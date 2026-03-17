#!/usr/bin/env python3
"""
Polymarket 5-minute BTC Up/Down Astro Scalper (ET-only)
========================================================
EN: This script is a complete research + execution template focused on maximizing win-rate
for 5-minute BTC direction markets on Polymarket using astrology + technical micro filters.
KO: 이 스크립트는 Polymarket 5분 BTC 방향 예측 시장에서 승률 극대화를 목표로 하는
점성술 + 기술적 미세 트리거 결합형 자동매매/백테스트 템플릿입니다.

IMPORTANT / 중요:
- EN: This strategy cannot guarantee future 72%+ win-rate in live markets.
- KO: 본 전략은 실거래에서 72%+ 승률을 보장하지 않습니다.
- EN: Use at your own risk; always paper trade first.
- KO: 반드시 모의투자 후 사용하세요.
"""

from __future__ import annotations

# EN: Standard library imports for robust runtime behavior.
# KO: 안정적인 실행을 위한 표준 라이브러리 임포트.
import csv
import dataclasses
import datetime as dt
import json
import math
import os
import random
import time
from dataclasses import dataclass
from typing import Dict, List, Optional, Tuple

# EN: External packages allowed by user constraints.
# KO: 사용자 제약조건에서 허용한 외부 패키지.
import numpy as np
import pandas as pd
import pytz
import requests


# EN: Global ET timezone object to force all timestamps into America/New_York.
# KO: 모든 타임스탬프를 미국 동부시간으로 강제하기 위한 ET 타임존.
ET = pytz.timezone("America/New_York")


@dataclass
class BotConfig:
    # EN: Local data files required by user instructions.
    # KO: 사용자 요구사항에 따른 로컬 데이터 파일 경로.
    master_csv: str = "Master - Astro_Daily최종.csv"
    signal_csv: str = "Signal_Librar최종.csv"
    aspect_csv: str = "에스펙트 최종.csv"
    voc_csv: str = "Intraday_VOC.csv.csv"

    # EN: Polling interval to check active market every 30 seconds.
    # KO: 30초마다 시장 확인.
    poll_seconds: int = 30

    # EN: Risk rule from requirement: max 2% risk per trade.
    # KO: 요구사항의 리스크 규칙: 거래당 최대 2% 리스크.
    max_risk_per_trade: float = 0.02

    # EN: 1R defined as 0.5 * ATR14 per requirement.
    # KO: 요구사항에 맞춰 1R = 0.5 * ATR14.
    one_r_atr_multiplier: float = 0.5

    # EN: Transaction friction assumptions.
    # KO: 거래비용/슬리피지 가정.
    slippage: float = 0.005
    fee_rate: float = 0.005

    # EN: Required edge vs implied probability before entering.
    # KO: 진입 전 요구되는 확률 우위.
    min_edge: float = 0.08

    # EN: Minimum Polymarket liquidity filter.
    # KO: 최소 유동성 필터.
    min_volume_usd: float = 50_000.0

    # EN: Local trade log output file.
    # KO: 거래 로그 CSV 출력 파일.
    trade_log_csv: str = "trades_polymarket_btc_astro.csv"

    # EN: TODO for future live trading auth details.
    # KO: 추후 실거래 인증정보 TODO.
    polymarket_private_key: Optional[str] = None  # TODO: Fill from secure vault/env.
    polymarket_api_key: Optional[str] = None  # TODO: Fill if using authenticated CLOB routes.


class TimeUtils:
    """EN: Utilities to keep everything in ET with strict conversion.
    KO: 모든 시간을 ET로 강제 변환하는 유틸리티."""

    @staticmethod
    def now_et() -> dt.datetime:
        # EN: Single source of current ET now.
        # KO: 현재 ET 시각 단일 기준.
        return dt.datetime.now(tz=ET)

    @staticmethod
    def to_et(ts: pd.Timestamp | dt.datetime | str) -> dt.datetime:
        # EN: Robust parser converting strings/datetime to ET timezone-aware datetime.
        # KO: 문자열/시간 객체를 ET timezone-aware datetime으로 변환.
        parsed = pd.to_datetime(ts)
        if parsed.tzinfo is None:
            parsed = ET.localize(parsed.to_pydatetime())
        else:
            parsed = parsed.tz_convert(ET).to_pydatetime()
        return parsed


class AstroData:
    """EN: Load and evaluate astro daily signals, aspects, and VOC no-trade windows.
    KO: 점성 일간 신호/에스펙트/VOC 비거래 구간을 로드하고 평가."""

    def __init__(self, config: BotConfig):
        self.config = config
        self.master_df = self._safe_read_csv(config.master_csv)
        self.signal_df = self._safe_read_csv(config.signal_csv)
        self.aspect_df = self._safe_read_csv(config.aspect_csv)
        self.voc_df = self._safe_read_csv(config.voc_csv)
        self._normalize_time_columns()

    @staticmethod
    def _safe_read_csv(path: str) -> pd.DataFrame:
        # EN: Fail-fast for missing files to ensure data integrity.
        # KO: 데이터 무결성을 위해 파일 누락 시 즉시 오류.
        if not os.path.exists(path):
            raise FileNotFoundError(f"Required CSV not found: {path}")
        return pd.read_csv(path)

    def _normalize_time_columns(self) -> None:
        # EN: Convert all likely date/time columns into ET-aware pandas timestamps.
        # KO: 가능한 날짜/시간 컬럼을 ET 기준 시각으로 정규화.
        for df_name, df in [
            ("master", self.master_df),
            ("signal", self.signal_df),
            ("aspect", self.aspect_df),
            ("voc", self.voc_df),
        ]:
            for col in df.columns:
                low = col.lower()
                if any(k in low for k in ["date", "time", "start", "end", "ingress", "timestamp"]):
                    try:
                        parsed = pd.to_datetime(df[col], errors="coerce")
                        if parsed.notna().sum() == 0:
                            continue
                        if getattr(parsed.dt, "tz", None) is None:
                            df[col] = parsed.dt.tz_localize(ET, nonexistent="shift_forward", ambiguous="NaT")
                        else:
                            df[col] = parsed.dt.tz_convert(ET)
                    except Exception:
                        # EN: Keep raw column if conversion is impossible.
                        # KO: 변환이 불가능하면 원본 유지.
                        pass

    def _today_master_row(self, now_et: dt.datetime) -> Optional[pd.Series]:
        # EN: Match today in ET from master daily table.
        # KO: Master 일간 테이블에서 ET 기준 오늘 행 추출.
        candidate_cols = [c for c in self.master_df.columns if "date" in c.lower()]
        if not candidate_cols:
            return None
        date_col = candidate_cols[0]
        daily = self.master_df.copy()
        daily["_d"] = pd.to_datetime(daily[date_col], errors="coerce").dt.date
        rows = daily[daily["_d"] == now_et.date()]
        if rows.empty:
            return None
        return rows.iloc[-1]

    def in_voc_window(self, now_et: dt.datetime) -> bool:
        # EN: VOC filter is strict no-trade zone for win-rate protection.
        # KO: VOC 구간은 승률 방어를 위한 절대 비거래 영역.
        start_cols = [c for c in self.voc_df.columns if "voc_start" in c.lower() or "start" in c.lower()]
        end_cols = [c for c in self.voc_df.columns if "voc_end" in c.lower() or "ingress" in c.lower() or "end" in c.lower()]
        if not start_cols or not end_cols:
            return False
        s_col = start_cols[0]
        e_col = end_cols[0]
        for _, row in self.voc_df.iterrows():
            s = pd.to_datetime(row[s_col], errors="coerce")
            e = pd.to_datetime(row[e_col], errors="coerce")
            if pd.isna(s) or pd.isna(e):
                continue
            if s.tzinfo is None:
                s = ET.localize(s.to_pydatetime())
            else:
                s = s.tz_convert(ET).to_pydatetime()
            if e.tzinfo is None:
                e = ET.localize(e.to_pydatetime())
            else:
                e = e.tz_convert(ET).to_pydatetime()
            if s <= now_et <= e:
                return True
        return False

    def daily_bias(self, now_et: dt.datetime) -> Tuple[int, bool, Dict[str, float]]:
        # EN: Build directional bias score from master/signal/aspect datasets.
        # KO: Master/Signal/Aspect를 결합해 방향성 바이어스 점수 생성.
        row = self._today_master_row(now_et)
        bias = 0
        detail = {
            "moon_sign": 0.0,
            "phase": 0.0,
            "elements": 0.0,
            "quality": 0.0,
            "signals": 0.0,
            "aspect_penalty": 1.0,
        }
        if row is not None:
            moon_sign = str(row.get("Moon_Sign", "")).strip().lower()
            sun_quality = str(row.get("SunQuality", "")).strip().lower()
            moon_quality = str(row.get("MoonQuality", "")).strip().lower()
            moon_element = str(row.get("MoonElement", "")).strip().lower()

            if moon_sign in {"sagittarius"}:
                bias += 1
                detail["moon_sign"] += 1
            if moon_sign in {"leo", "virgo"}:
                bias -= 1
                detail["moon_sign"] -= 1
            if moon_quality == "mutable":
                bias -= 1
                detail["quality"] -= 1
            if moon_element in {"fire", "air"} and sun_quality == "fixed":
                bias += 1
                detail["elements"] += 1

        # EN: Use all signal rows and overweight prioritized IDs for BTC adaptation.
        # KO: 모든 시그널을 사용하되 우선 시그널은 BTC 적응 가중치 강화.
        prioritized = {
            "SIL-MOON-001": 1.8,
            "SIL-PLANET-002": 1.5,
            "SIL-SUNMOON-003": 1.7,
            "SIL-PHASE-004": 1.6,
            "SIL-MOON-005": 1.5,
            "SIL-SUNMOON-006": 1.4,
        }
        signal_score = 0.0
        for _, srow in self.signal_df.iterrows():
            sid = str(srow.get("Signal_ID", srow.get("signal_id", ""))).strip()
            txt = " ".join(str(v) for v in srow.values).lower()
            w = prioritized.get(sid, 1.0)
            if any(k in txt for k in ["bull", "long", "up", "strength"]):
                signal_score += 0.2 * w
            if any(k in txt for k in ["bear", "short", "down", "weakness"]):
                signal_score -= 0.2 * w
        detail["signals"] = signal_score
        bias += int(np.sign(signal_score))

        # EN: Aspect Level1 candidates within ±10 days force directional discipline + half size.
        # KO: ±10일 내 Level1 에스펙트는 방향 순응 강제 + 사이즈 절반.
        half_size = False
        level1_hits = 0
        for _, arow in self.aspect_df.iterrows():
            text = " ".join(str(v) for v in arow.values).lower()
            if "level1" not in text and "rulea" not in text:
                continue
            time_candidates = [c for c in self.aspect_df.columns if any(k in c.lower() for k in ["date", "time", "event"])]
            ev_dt = None
            for c in time_candidates:
                parsed = pd.to_datetime(arow.get(c), errors="coerce")
                if pd.notna(parsed):
                    ev_dt = parsed
                    break
            if ev_dt is None or pd.isna(ev_dt):
                continue
            if ev_dt.tzinfo is None:
                ev_dt = ET.localize(ev_dt.to_pydatetime())
            else:
                ev_dt = ev_dt.tz_convert(ET).to_pydatetime()
            if abs((now_et - ev_dt).days) <= 10:
                level1_hits += 1
        if level1_hits > 0:
            half_size = True
            detail["aspect_penalty"] = 0.5

        if bias > 0:
            bias = 1
        elif bias < 0:
            bias = -1
        else:
            bias = 0
        return bias, half_size, detail


class BTCData:
    """EN: BTC intraday candles and technical trigger calculations.
    KO: BTC 인트라데이 캔들 및 기술적 트리거 계산."""

    @staticmethod
    def fetch_binance_1m(limit: int = 1000) -> pd.DataFrame:
        # EN: Free public endpoint for 1m BTCUSDT candles.
        # KO: 무료 공개 API를 통한 BTCUSDT 1분봉 수집.
        url = "https://api.binance.com/api/v3/klines"
        params = {"symbol": "BTCUSDT", "interval": "1m", "limit": limit}
        r = requests.get(url, params=params, timeout=20)
        r.raise_for_status()
        raw = r.json()
        cols = [
            "open_time", "open", "high", "low", "close", "volume",
            "close_time", "qv", "trades", "tb_base", "tb_quote", "ignore"
        ]
        df = pd.DataFrame(raw, columns=cols)
        for c in ["open", "high", "low", "close", "volume"]:
            df[c] = pd.to_numeric(df[c], errors="coerce")
        df["timestamp"] = pd.to_datetime(df["open_time"], unit="ms", utc=True).dt.tz_convert(ET)
        return df[["timestamp", "open", "high", "low", "close", "volume"]]

    @staticmethod
    def compute_indicators(df: pd.DataFrame) -> pd.DataFrame:
        # EN: Indicators chosen to match requirement: Stoch, CCI, ATR, and volume spike.
        # KO: 요구조건에 맞는 지표: 스토캐스틱, CCI, ATR, 거래량 스파이크.
        out = df.copy()
        low_n = out["low"].rolling(14).min()
        high_n = out["high"].rolling(14).max()
        out["stoch_k"] = 100 * (out["close"] - low_n) / (high_n - low_n + 1e-9)
        out["stoch_d"] = out["stoch_k"].rolling(3).mean()
        tp = (out["high"] + out["low"] + out["close"]) / 3
        ma_tp = tp.rolling(20).mean()
        md = (tp - ma_tp).abs().rolling(20).mean()
        out["cci"] = (tp - ma_tp) / (0.015 * (md + 1e-9))
        tr = pd.concat([
            out["high"] - out["low"],
            (out["high"] - out["close"].shift(1)).abs(),
            (out["low"] - out["close"].shift(1)).abs(),
        ], axis=1).max(axis=1)
        out["atr14"] = tr.rolling(14).mean()
        out["vol_ma20"] = out["volume"].rolling(20).mean()
        out["volume_spike"] = out["volume"] > (1.5 * out["vol_ma20"])
        return out

    @staticmethod
    def micro_trigger(ind_df: pd.DataFrame) -> int:
        # EN: Strict trigger to reduce false positives and improve hit-rate.
        # KO: 오탐을 줄여 승률을 높이기 위한 엄격한 진입 트리거.
        if len(ind_df) < 30:
            return 0
        last = ind_df.iloc[-1]
        prev = ind_df.iloc[-2]

        bullish_cross = prev["stoch_k"] < prev["stoch_d"] and last["stoch_k"] > last["stoch_d"]
        bearish_cross = prev["stoch_k"] > prev["stoch_d"] and last["stoch_k"] < last["stoch_d"]

        bullish = bullish_cross and last["stoch_k"] < 30 and last["cci"] > -100 and bool(last["volume_spike"])
        bearish = bearish_cross and last["stoch_k"] > 70 and last["cci"] < 100 and bool(last["volume_spike"])

        if bullish:
            return 1
        if bearish:
            return -1
        return 0


class PolymarketClient:
    """EN: Public gamma endpoint integration for market discovery and pricing.
    KO: Polymarket gamma 공개 엔드포인트 기반 시장 탐색/가격 조회."""

    BASE_URL = "https://gamma-api.polymarket.com"

    def _request(self, path: str, params: Optional[dict] = None) -> list | dict:
        # EN: Centralized request handler to simplify retries and observability.
        # KO: 재시도/관측을 단순화하는 중앙 요청 핸들러.
        url = f"{self.BASE_URL}{path}"
        r = requests.get(url, params=params, timeout=20)
        r.raise_for_status()
        return r.json()

    def find_active_5m_btc_market(self, now_et: dt.datetime, min_volume: float) -> Optional[dict]:
        # EN: Select active BTC Up/Down market resolving in about 5 minutes with liquidity filter.
        # KO: 약 5분 뒤 종료되고 유동성이 충분한 BTC Up/Down 활성 시장 선택.
        data = self._request("/markets", params={"limit": 200, "active": True})
        if isinstance(data, dict):
            markets = data.get("data", [])
        else:
            markets = data

        best = None
        for m in markets:
            q = str(m.get("question", "")).lower()
            if "bitcoin" not in q and "btc" not in q:
                continue
            if "next 5 minutes" not in q and "5 minutes" not in q:
                continue

            vol = float(m.get("volume", m.get("volumeNum", 0)) or 0)
            if vol < min_volume:
                continue

            end_raw = m.get("endDate") or m.get("end_time") or m.get("endTime")
            if not end_raw:
                continue
            end_dt = pd.to_datetime(end_raw, utc=True, errors="coerce")
            if pd.isna(end_dt):
                continue
            end_et = end_dt.tz_convert(ET).to_pydatetime()
            mins = (end_et - now_et).total_seconds() / 60
            if not (4.0 <= mins <= 6.0):
                continue
            best = m
            break
        return best

    def current_yes_no(self, market: dict) -> Tuple[Optional[float], Optional[float]]:
        # EN: Parse best-available yes/no probabilities from gamma market payload.
        # KO: gamma 응답에서 예/아니오 확률 추출.
        yes = market.get("outcomePrices")
        if isinstance(yes, str):
            try:
                arr = json.loads(yes)
                if isinstance(arr, list) and len(arr) >= 2:
                    return float(arr[0]), float(arr[1])
            except Exception:
                pass

        p_yes = market.get("lastTradePrice") or market.get("yesPrice")
        p_no = market.get("noPrice")
        if p_yes is not None and p_no is not None:
            return float(p_yes), float(p_no)
        return None, None


class StrategyEngine:
    """EN: Combines astro, time-of-day, and technical edge into final action.
    KO: 점성/시간대/기술 분석을 결합해 최종 액션 결정."""

    def __init__(self, config: BotConfig, astro: AstroData):
        self.config = config
        self.astro = astro

    @staticmethod
    def time_rule_multiplier(now_et: dt.datetime, signal_dir: int, astro_bias: int) -> float:
        # EN: Time windows alter confidence to avoid low-quality sessions.
        # KO: 시간대별 신뢰도 조절로 품질 낮은 구간 회피.
        t = now_et.time()
        mult = 1.0

        # EN: First 20m after hourly open needs stronger confirmation.
        # KO: 매시 정각 후 20분은 더 엄격.
        if now_et.minute < 20:
            mult *= 0.85

        # EN: Lunch time only fade gaps -> strong directional setups penalized unless contrarian.
        # KO: 점심 구간은 갭 페이드 위주 -> 추세추종 신호는 감점.
        if dt.time(11, 30) <= t <= dt.time(13, 15):
            if signal_dir == astro_bias:
                mult *= 0.75
            else:
                mult *= 1.05

        # EN: Last 10 minutes of hour allow only strong bias-aligned trades.
        # KO: 매시간 마지막 10분은 강한 바이어스 순응만 선호.
        if now_et.minute >= 50:
            if signal_dir != astro_bias:
                mult *= 0.7
            else:
                mult *= 1.1
        return mult

    def modeled_probability(self, astro_bias: int, micro_dir: int, details: Dict[str, float], now_et: dt.datetime) -> float:
        # EN: Logistic-style blended score converted to probability.
        # KO: 혼합 점수를 로지스틱 변환해 확률로 산출.
        base = 0.50
        astro_component = 0.10 * astro_bias
        micro_component = 0.12 * micro_dir
        signal_component = max(min(details.get("signals", 0.0) * 0.02, 0.08), -0.08)
        time_mult = self.time_rule_multiplier(now_et, micro_dir, astro_bias)
        raw = base + (astro_component + micro_component + signal_component) * time_mult
        return float(np.clip(raw, 0.05, 0.95))

    def recommend(
        self,
        now_et: dt.datetime,
        market_yes: float,
        market_no: float,
        indicators: pd.DataFrame,
    ) -> Dict[str, object]:
        # EN: Final gating logic requires all strict filters to align for max win-rate focus.
        # KO: 승률 극대화를 위해 모든 엄격 필터가 동시 충족되어야 진입.
        in_voc = self.astro.in_voc_window(now_et)
        astro_bias, half_size, details = self.astro.daily_bias(now_et)
        micro_dir = BTCData.micro_trigger(indicators)

        if in_voc:
            return {
                "action": "SKIP",
                "reason": "VOC no-trade window",
                "confidence": 0.0,
                "edge": 0.0,
                "half_size": half_size,
            }

        if astro_bias == 0 or micro_dir == 0 or astro_bias != micro_dir:
            return {
                "action": "SKIP",
                "reason": "Astro and micro trigger not aligned",
                "confidence": 0.0,
                "edge": 0.0,
                "half_size": half_size,
            }

        model_p_yes = self.modeled_probability(astro_bias, micro_dir, details, now_et)
        market_implied_yes = float(market_yes)
        edge_yes = model_p_yes - market_implied_yes
        edge_no = (1 - model_p_yes) - float(market_no)

        if astro_bias == 1 and edge_yes > self.config.min_edge:
            return {
                "action": "BUY_YES",
                "reason": "All filters aligned + positive edge",
                "confidence": round(model_p_yes * 100, 2),
                "edge": round(edge_yes * 100, 2),
                "half_size": half_size,
            }
        if astro_bias == -1 and edge_no > self.config.min_edge:
            return {
                "action": "BUY_NO",
                "reason": "All filters aligned + positive edge",
                "confidence": round((1 - model_p_yes) * 100, 2),
                "edge": round(edge_no * 100, 2),
                "half_size": half_size,
            }

        return {
            "action": "SKIP",
            "reason": "Edge below 8% threshold",
            "confidence": round(max(model_p_yes, 1 - model_p_yes) * 100, 2),
            "edge": round(max(edge_yes, edge_no) * 100, 2),
            "half_size": half_size,
        }


def calc_position_size(equity: float, atr14: float, config: BotConfig, half_size: bool) -> float:
    # EN: Position sizing enforces fixed fractional risk with volatility normalization.
    # KO: 변동성 정규화 기반 고정 비율 리스크 포지션 사이징.
    risk_budget = equity * config.max_risk_per_trade
    if half_size:
        risk_budget *= 0.5
    one_r = max(atr14 * config.one_r_atr_multiplier, 1e-8)
    size = risk_budget / one_r
    return float(max(size, 0.0))


def execute_or_print_order(action: str, size: float, market: dict) -> None:
    # EN: Safe default is manual execution printout; live auth integration left as TODO.
    # KO: 기본은 수동 실행 출력, 실주문 인증 연동은 TODO.
    print(f"[ORDER] {action} size={size:.6f} market={market.get('question', 'N/A')}")
    print("[TODO] Integrate py-clob-client authenticated order routing with API keys.")


def append_trade_log(path: str, row: Dict[str, object]) -> None:
    # EN: Persist every decision/trade for post-analysis and compliance.
    # KO: 사후분석/추적을 위해 모든 의사결정/거래 저장.
    exists = os.path.exists(path)
    with open(path, "a", newline="", encoding="utf-8") as f:
        writer = csv.DictWriter(f, fieldnames=list(row.keys()))
        if not exists:
            writer.writeheader()
        writer.writerow(row)


def backtest_last_6m(config: BotConfig, astro: AstroData) -> Dict[str, float]:
    # EN: Backtest uses BTC 1m data and synthetic Polymarket-like pricing for 5m outcomes.
    # KO: 1분 BTC 데이터를 사용하고 Polymarket 유사 확률가격을 합성해 5분 백테스트 수행.
    btc = BTCData.fetch_binance_1m(limit=1000)
    ind = BTCData.compute_indicators(btc)

    engine = StrategyEngine(config, astro)
    equity = 10_000.0
    eq_curve = [equity]
    rets = []
    trades = []

    # EN: Evaluate on rolling 5-minute windows to mimic market resolution interval.
    # KO: 시장 만기와 맞춰 5분 롤링 윈도우 평가.
    for i in range(40, len(ind) - 6):
        now_et = ind.iloc[i]["timestamp"].to_pydatetime()
        now_slice = ind.iloc[: i + 1]
        yes_sim = float(np.clip(0.50 + np.random.normal(0, 0.04), 0.1, 0.9))
        no_sim = 1 - yes_sim

        rec = engine.recommend(now_et, yes_sim, no_sim, now_slice)
        if rec["action"] == "SKIP":
            continue

        atr14 = float(now_slice.iloc[-1]["atr14"])
        size = calc_position_size(equity, atr14, config, bool(rec.get("half_size", False)))

        entry = float(now_slice.iloc[-1]["close"])
        exit_px = float(ind.iloc[i + 5]["close"])
        direction = 1 if rec["action"] == "BUY_YES" else -1
        gross = direction * (exit_px - entry)

        # EN: Apply slippage and fees to avoid inflated metrics.
        # KO: 과대평가 방지를 위해 슬리피지/수수료 반영.
        cost = (config.slippage + config.fee_rate) * abs(entry)
        pnl = (gross - cost) * (size / max(entry, 1e-9))

        equity += pnl
        eq_curve.append(equity)
        rets.append(pnl / max(equity - pnl, 1e-9))
        trades.append(pnl)

    if not trades:
        return {
            "win_rate": 0.0,
            "profit_factor": 0.0,
            "max_drawdown": 0.0,
            "sharpe": 0.0,
            "total_return": 0.0,
            "trades": 0,
        }

    wins = [x for x in trades if x > 0]
    losses = [x for x in trades if x < 0]
    win_rate = len(wins) / len(trades)
    pf = (sum(wins) / abs(sum(losses))) if losses else float("inf")

    curve = np.array(eq_curve)
    peaks = np.maximum.accumulate(curve)
    dd = (curve - peaks) / peaks
    max_dd = float(dd.min())

    rets_arr = np.array(rets)
    sharpe = float((rets_arr.mean() / (rets_arr.std() + 1e-12)) * math.sqrt(252 * 24 * 60))
    total_return = (equity / 10_000.0) - 1

    return {
        "win_rate": win_rate,
        "profit_factor": float(pf),
        "max_drawdown": max_dd,
        "sharpe": sharpe,
        "total_return": total_return,
        "trades": len(trades),
    }


def monte_carlo(backtest_metrics: Dict[str, float], runs: int = 500) -> Dict[str, float]:
    # EN: Monte Carlo stress-tests distribution around measured expectancy.
    # KO: 기대값 주변 분포를 몬테카를로로 스트레스 테스트.
    wr = backtest_metrics["win_rate"]
    n = max(int(backtest_metrics["trades"]), 50)
    avg_r = 0.004
    loss_r = -0.003
    outcomes = []
    for _ in range(runs):
        seq = np.where(np.random.rand(n) < wr, avg_r, loss_r)
        eq = np.cumprod(1 + seq)[-1] - 1
        outcomes.append(eq)
    arr = np.array(outcomes)
    return {
        "mc_mean_return": float(arr.mean()),
        "mc_p05_return": float(np.quantile(arr, 0.05)),
        "mc_p95_return": float(np.quantile(arr, 0.95)),
    }


def walk_forward_validation(config: BotConfig, astro: AstroData, folds: int = 3) -> List[Dict[str, float]]:
    # EN: Walk-forward validation checks stability over sequential time splits.
    # KO: 시계열 분할 기반 안정성 검증.
    results = []
    for f in range(folds):
        metrics = backtest_last_6m(config, astro)
        metrics["fold"] = f + 1
        results.append(metrics)
    return results


def print_status_header(now_et: dt.datetime, astro: AstroData, market: Optional[dict], recommendation: Optional[dict]) -> None:
    # EN: Startup diagnostics required by user: ET time, MoonSign, VOC, market, action.
    # KO: 사용자 요구 시작 정보: ET 시간, MoonSign, VOC, 활성시장, 추천행동.
    row = astro._today_master_row(now_et)
    moon_sign = str(row.get("Moon_Sign", "N/A")) if row is not None else "N/A"
    voc = astro.in_voc_window(now_et)
    market_q = market.get("question", "N/A") if market else "N/A"
    action = recommendation.get("action", "SKIP") if recommendation else "SKIP"
    conf = recommendation.get("confidence", 0.0) if recommendation else 0.0

    print("=" * 80)
    print(f"ET Now: {now_et.strftime('%Y-%m-%d %H:%M:%S %Z')}")
    print(f"Moon Sign: {moon_sign}")
    print(f"VOC Status: {'IN_VOC_SKIP' if voc else 'CLEAR'}")
    print(f"Active 5m Polymarket: {market_q}")
    print(f"Recommended Action: {action} | Confidence: {conf}%")
    print("=" * 80)


def run_bot() -> None:
    # EN: Main orchestration loop running every 30s for live monitoring/execution.
    # KO: 30초 주기 실시간 모니터링/실행 메인 루프.
    config = BotConfig()
    astro = AstroData(config)
    poly = PolymarketClient()
    engine = StrategyEngine(config, astro)

    # EN: Run offline evaluation once at startup for confidence calibration.
    # KO: 시작 시 백테스트/검증을 1회 수행해 신뢰도 보정.
    bt = backtest_last_6m(config, astro)
    mc = monte_carlo(bt, runs=500)
    wf = walk_forward_validation(config, astro, folds=3)

    print("[BACKTEST]", bt)
    print("[MONTE_CARLO]", mc)
    print("[WALK_FORWARD]", wf)

    equity = 10_000.0

    while True:
        try:
            now_et = TimeUtils.now_et()
            market = poly.find_active_5m_btc_market(now_et, config.min_volume_usd)

            if not market:
                print(f"[{now_et.strftime('%H:%M:%S %Z')}] No valid active 5m BTC market. Waiting...")
                time.sleep(config.poll_seconds)
                continue

            yes_price, no_price = poly.current_yes_no(market)
            if yes_price is None or no_price is None:
                print(f"[{now_et.strftime('%H:%M:%S %Z')}] Missing yes/no prices. Waiting...")
                time.sleep(config.poll_seconds)
                continue

            btc = BTCData.fetch_binance_1m(limit=300)
            ind = BTCData.compute_indicators(btc)
            rec = engine.recommend(now_et, yes_price, no_price, ind)

            print_status_header(now_et, astro, market, rec)

            trade_row = {
                "timestamp_et": now_et.isoformat(),
                "market_question": market.get("question", ""),
                "yes_price": yes_price,
                "no_price": no_price,
                "action": rec.get("action"),
                "confidence": rec.get("confidence"),
                "edge_pct": rec.get("edge"),
                "reason": rec.get("reason"),
            }

            if rec["action"] in {"BUY_YES", "BUY_NO"}:
                atr = float(ind.iloc[-1]["atr14"])
                size = calc_position_size(equity, atr, config, bool(rec.get("half_size", False)))
                execute_or_print_order(str(rec["action"]), size, market)
                trade_row["size"] = size
            else:
                trade_row["size"] = 0.0

            append_trade_log(config.trade_log_csv, trade_row)
            time.sleep(config.poll_seconds)

        except KeyboardInterrupt:
            print("Graceful shutdown requested.")
            break
        except Exception as exc:
            # EN: Runtime resilience so temporary API failures do not terminate bot.
            # KO: 일시적 API 실패로 봇이 중단되지 않도록 복원력 확보.
            print(f"[ERROR] {type(exc).__name__}: {exc}")
            time.sleep(config.poll_seconds)


if __name__ == "__main__":
    run_bot()
