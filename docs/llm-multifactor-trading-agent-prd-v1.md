# LLM 기반 멀티팩터 트레이딩 에이전트 — 1차 기획 문서 (v1.1)

## A. 한 줄 요약
멀티소스(마켓·마이크로스트럭처·파생·온체인·거시·지정학·뉴스·이벤트 캘린더) 데이터를 정량 시그널/리스크 엔진으로 계산하고, LLM은 **설명/리포트 전용**으로 분리한 read-only 우선 시스템을 설계한다.

---

## B. 내가 만들 시스템의 핵심 정의
**핵심 정의**
- 입력: 코인명/티커(BTC, ETH, SOL 등).
- 출력: (1) 시황 기반 전망, (2) 강세/약세/중립 시나리오, (3) 근거/리스크/신선도, (4) 구조화된 TP/SL/invalidation/보유기간/신뢰도.

**반드시 지킬 원칙**
- Phase 1~2는 read-only/paper 중심, 자동매매 전제 금지.
- LLM 단독 예측 금지(LLM은 설명/요약/리포팅 전용).
- 점성술/천문 데이터는 experimental flag로 격리, 핵심 의사결정 경로에서 제외.
- 모든 출력에 freshness/confidence/evidence/source를 포함.
- neutral bias면 억지로 매매 아이디어 생성 금지(“No-Trade” 허용).

---

## C. 1차 PRD

### 1) 문제 정의
- 단일 지표/단일 뉴스는 레짐 전환 국면에서 오판이 잦다.
- 시장 데이터·파생 과열·온체인 흐름·지정학 충격이 분절되어 있어 일관된 의사결정이 어렵다.
- TP/SL가 규칙 기반이 아니면 재현성, 검증 가능성, 리스크 통제가 약해진다.

### 2) 사용자 시나리오
- 트레이더: 티커 입력 후 24h~2w 관점의 구조화 시나리오와 TP/SL 조회.
- 리서처: 지정학/정책 이벤트가 위험자산에 주는 market impact factor 추적.
- PM: 전략 버전별 walk-forward와 레짐별 성능/드로우다운 점검.

### 3) 핵심 기능
- 멀티소스 ingestion + 공통 스키마 normalization + feature store 구축.
- 6개 시그널 엔진 점수화(Trend/Momentum/Volatility/Liquidity-Derivatives/Macro-Geopolitical/Experimental Astrology).
- 리스크 엔진의 룰 기반 TP/SL/invalidation/horizon 산출.
- LLM 리포터의 근거 중심 설명(JSON + markdown 동시 출력).
- source freshness/confidence/evidence/revision 메타데이터 노출.

### 4) 비핵심 기능
- 초저지연 자동 주문 집행.
- 개인화 포트폴리오 최적화.
- 멀티브로커 스마트 라우팅.

### 5) 성공 지표
- 데이터 신선도 SLA 준수율 >95%.
- 스키마 유효성(JSON schema pass) 100%.
- 백테스트 walk-forward expectancy >0, MaxDD 제한 준수.
- 중립 레짐에서 No-Trade 권고 정확도(불필요 진입 억제율) 추적.

### 6) 주요 리스크
- 데이터 지연/결측/스키마 변경.
- 파생 과열 신호의 과최적화.
- 뉴스/소셜 노이즈에 의한 과민반응.
- LLM 환각/과장 해석.

### 7) MVP 범위
- 자산: BTC/ETH/SOL + DXY/US10Y/VIX/CL/Gold/Silver/Nasdaq proxy.
- 기능: read-only 분석 + 구조화 TP/SL + 백테스트 리포트.
- 제외: 실주문 execution(Phase 4까지 유예).

---

## D. 시스템 아키텍처 초안

### 1) Ingestion Layer
- 거래소(WebSocket/REST): OHLCV, order book, trade tape, derivatives.
- 온체인/거래소 플로우: inflow/outflow, whale, stablecoin mint/burn, bridge flow.
- 거시/크로스에셋: DXY, US10Y, VIX, CL, Gold, Silver, Nasdaq proxy.
- 뉴스/지정학/캘린더: RSS/API/structured events.
- 표준 메타데이터 부착: `source,timestamp,latency,freshness,confidence,symbol_mapping,exchange,timeframe,revision_flag`.

### 2) Normalization Layer
- 심볼 매핑(BTCUSDT/BTC-USD/BTC).
- 이벤트 타입 표준화(news/event/macro/onchain/deriv).
- 시계열 정렬(UTC), missing/outlier flags.

### 3) Feature Store
- Online: Redis (저지연 조회).
- Offline: PostgreSQL + Parquet(백테스트/재현).
- feature versioning + data lineage + revision log.

### 4) Signal Engine
- 6개 엔진 점수([-1,+1]) + data quality penalty + regime adjustment.
- 최종 ensemble score + bias 분류(bullish/bearish/neutral).

### 5) LLM Reasoning/Report Layer
- 입력은 오직 구조화 신호/리스크 결과.
- 자유 추정 TP/SL 금지.
- 출력: JSON 스키마 + 설명 텍스트 + evidence list.

### 6) Risk Engine
- ATR + market structure + microstructure/derivatives 과열 기반 SL/TP 계산.
- 이벤트 리스크 시 보수적 조정(TP 축소, SL 강화, 포지션 축소).
- neutral/no-trade 정책 강제.

### 7) Execution Adapter
- Phase 1~2: mock only(read-only).
- Phase 3: paper trading adapter.
- Phase 4: Minara/브로커/거래소 실연동 후보.

### 8) Backtest Engine
- walk-forward + regime-based + long/short 분리.
- 거래 비용/슬리피지/펀딩 반영.
- feature ablation 자동화(geopolitics/astrology on/off).

### 9) Monitoring/Logging Layer
- freshness 지표, 데이터 drift, 신호 drift, 실패율.
- 감사로그(입력 스냅샷/출력/전략 버전/룰 버전).

---

## E. 데이터 소스 설계

> 각 항목: 목적 / 업데이트 주기 / 예상 지연 / 저장 방식 / feature 후보 / TP·SL 연결

### 1) Crypto market data + Market microstructure
- 목적: 가격 방향성과 체결/유동성 미세구조 파악.
- 업데이트: tick~1m.
- 지연: 100ms~3s.
- 저장: trade tape + L2 snapshot + 1m/5m/1h 집계.
- feature 후보:
  - OHLCV, VWAP deviation, volume profile
  - **order book imbalance, bid/ask spread, market depth**
  - **taker buy/sell ratio, large trade detector, CVD(가능 시)**
- TP/SL 연결:
  - 스프레드 확대/깊이 얕음 → entry 보수화, SL 타이트닝.
  - order book imbalance 급변 + large trade 편향 → 단기 TP 조정.

### 2) Derivatives / leverage complex
- 목적: 레버리지 과열, squeeze 리스크 정량화.
- 업데이트: 1m~5m.
- 지연: 수초.
- 저장: perp/futures snapshot + liquidation event log.
- feature 후보:
  - **funding rate, open interest, OI delta**
  - **basis, perp premium**
  - **liquidation, long/short ratio**
  - **estimated leverage ratio**
  - **top trader positioning(가능한 거래소에 한정)**
- TP/SL 연결:
  - funding 과열 + OI 급증 + basis 왜곡 시 역추세 리스크 가산.
  - 청산 밀집 레벨 근접 시 TP 분할 비중 확대, invalidation 강화.

### 3) On-chain / Exchange flow
- 목적: 수급/유동성 레짐 확인.
- 업데이트: 1m~1h.
- 지연: 수초~수분.
- 저장: 체인/거래소별 metric 테이블.
- feature 후보:
  - **exchange inflow/outflow, whale movement**
  - **stablecoin mint/burn**
  - **bridge flow, TVL, DEX volume**
  - **unlock schedule, staking inflow/outflow**
- TP/SL 연결:
  - 거래소 inflow 급증(매도 압력) 시 bearish 시나리오 가중.
  - unlock/스테이킹 유출 이벤트 구간에서 SL 보수화.

### 4) Macro / Cross-asset
- 목적: risk-on/off 레짐 및 크로스자산 충격 파악.
- 업데이트: 실시간~일간.
- 지연: 초~일.
- 저장: 시계열 + 발표 캘린더.
- feature 후보:
  - **DXY, US10Y, VIX, CL, gold, silver, Nasdaq proxy**
  - 상관구조 붕괴 지표, 리스크센티먼트 지수.
- TP/SL 연결:
  - VIX↑ + DXY↑ + Nasdaq 약세 동시 발생 시 long TP 축소/SL 강화.

### 5) Geopolitics / Structured events
- 목적: 지정학 이벤트를 구조화된 market impact factor로 변환.
- 업데이트: 분~시간.
- 지연: 분 단위.
- 저장: event table(event_id, type, region, severity, confidence, half-life).
- feature 후보:
  - **war/conflict escalation, sanctions**
  - **shipping disruption, aviation closure**
  - **energy supply shock, election/regulatory shock**
  - impact_direction, impact_intensity, affected_assets.
- TP/SL 연결:
  - impact_intensity 높을수록 TP 폭 보수화/SL 강화.
  - 이벤트 유효기간(half-life) 내 신규진입 필터링.

### 6) News / sentiment (structured)
- 목적: 뉴스 흐름을 단순 요약이 아니라 이벤트 변수로 사용.
- 업데이트: 분 단위.
- 지연: 1~10분.
- 저장: 원문 + 구조화 필드 + 임베딩.
- feature 후보(필수 필드):
  - **headline, event_type, impact_direction, impact_intensity, half-life, related_assets**
  - novelty score, source reliability score.
- TP/SL 연결:
  - 하방 충격 뉴스 출현 시 bearish 확률/SL 강화.

### 7) Crypto event calendar
- 목적: 예정 이벤트 리스크 사전 반영.
- 업데이트: 시간~일간.
- 지연: 낮음(사전 일정).
- 저장: calendar table + revision history.
- feature 후보:
  - **token unlock, listing/delisting, governance vote**
  - **ETF/SEC/policy event**
  - **mainnet/TGE/airdrop, major protocol announcement**
- TP/SL 연결:
  - 이벤트 D-1~D+1 윈도우에서 보수적 리스크 모드 전환.

### 8) Options data (optional)
- 목적: 변동성 기대치/꼬리리스크 파악(선택적).
- 업데이트: 1m~1h.
- 지연: 소스 의존.
- 저장: 옵션 체인 스냅샷.
- feature 후보:
  - **IV, skew, put/call, DVOL(가능 시)**
- TP/SL 연결:
  - IV 급등/스큐 왜곡 시 변동성 버퍼 확대.

### 9) Astrology / Ephemeris (experimental only)
- 목적: 연구용 주기성 가설 검증.
- 업데이트: 시간~일간.
- 지연: 낮음.
- 저장: 실험용 분리 스키마.
- feature 후보:
  - **moon phase, planetary aspect, retrograde 여부**
  - `experimental_flag=true` 강제.
- TP/SL 연결:
  - 핵심 엔진에 직접 반영 금지.
  - ablation 성과 입증 전 운영 가중치 0 고정.

### 10) 공통 데이터 메타데이터 스키마(모든 소스 필수)
```json
{
  "source": "binance_ws",
  "timestamp": "2026-04-06T05:40:00Z",
  "latency_ms": 420,
  "freshness_sec": 5,
  "confidence": 0.93,
  "symbol_mapping": "BTCUSDT->BTC",
  "exchange": "BINANCE",
  "timeframe": "1m",
  "revision_flag": false
}
```

---

## F. 시그널 프레임워크 설계 (6개 엔진)

### 공통 규칙
- 점수: 각 엔진 [-1,+1], 최종 점수는 가중합 + 리스크 보정.
- 결측치: 최근값 대체 제한 + 품질 패널티 + confidence 하향.
- 신호 강도: `|score| × data_quality × regime_confidence`.
- neutral 조건: 최종점수 절대값이 임계치 미만이면 No-Trade.

### 1) Trend engine
- 입력 데이터: 멀티타임프레임 OHLCV.
- 주요 지표: EMA(20/50/200), ADX, HH/HL 구조.
- 점수화 방식: 추세 정렬 + ADX 임계치.
- 신호 강도: 타임프레임 동조성 가중.
- 결측치 처리: 상위 TF 보간, 품질 낮으면 감점.
- 리스크 보정: 횡보 레짐에서 레버리지/신뢰도 하향.

### 2) Momentum engine
- 입력 데이터: 수익률/거래량/가속도.
- 주요 지표: RSI, ROC, volume surge, divergence.
- 점수화 방식: 추세방향 모멘텀 vs 과열 반전 위험 동시 반영.
- 신호 강도: 모멘텀 지속시간 + 가속도.
- 결측치 처리: 롤링 중앙값 대체.
- 리스크 보정: 이벤트 윈도우에서 과열 감점.

### 3) Volatility engine
- 입력 데이터: 고빈도 수익률.
- 주요 지표: ATR, realized vol, vol-of-vol.
- 점수화 방식: 압축/확장 레짐 점수.
- 신호 강도: 변동성 체인지포인트 가중.
- 결측치 처리: 신호 약화 + confidence 하향.
- 리스크 보정: 고변동에서 포지션/TP/SL 자동 조정.

### 4) Liquidity/derivatives engine
- 입력 데이터: 오더북+파생+체결.
- 주요 지표:
  - **order book imbalance, spread, depth, taker ratio, large trade, CVD**
  - **funding, OI, OI delta, basis, perp premium, liquidation, long/short, estimated leverage ratio, top trader positioning(가능 시)**
- 점수화 방식: 유동성 취약 + 레버리지 과열 + squeeze 확률 합성.
- 신호 강도: 다중 경고 동시발생 시 비선형 증폭.
- 결측치 처리: 해당 요소 가중치 0 및 confidence 페널티.
- 리스크 보정: 과열 상태에서 TP 보수화/SL 강화.

### 5) Macro/geopolitical regime engine
- 입력 데이터: DXY/US10Y/VIX/CL/금/은/Nasdaq + structured events.
- 주요 지표: risk-on/off index, event impact factor.
- 점수화 방식: 이벤트 `impact_direction × impact_intensity × half-life`.
- 신호 강도: 이벤트 신선도/신뢰도/자산민감도 가중.
- 결측치 처리: stale event 감쇠.
- 리스크 보정: conflict/sanctions shock 시 신규진입 제한.

### 6) Experimental astrology engine
- 입력 데이터: moon phase, planetary aspect, retrograde.
- 주요 지표: 주기 dummy + 시차 피처.
- 점수화 방식: 연구용 점수만 산출.
- 신호 강도: 통계적 유의성 있을 때만 연구 리포트 반영.
- 결측치 처리: 무시.
- 리스크 보정: 운영 경로 영향 0(핵심 엔진 제외).

---

## G. TP/SL 설계 원칙 (구조화)

### 1) 표준 출력 형식
```json
{
  "bias": "bullish|bearish|neutral",
  "entry_zone": {"low": 0, "high": 0, "method": "breakout|pullback|value_area"},
  "stop_loss": {"price": 0, "rule": "max(structure_break, k*ATR)", "type": "hard|trailing"},
  "tp1": {"price": 0, "rr": 1.0},
  "tp2": {"price": 0, "rr": 2.0},
  "tp3": {"price": 0, "rr": 3.0},
  "invalidation_condition": ["4h_close_below_structure", "derivatives_overheat_flip"],
  "holding_horizon": "intraday|1-3d|1-2w",
  "confidence_score": 0.0,
  "evidence_list": ["liquidity_deriv:+0.55", "macro_regime:risk_off"],
  "freshness_timestamp": "2026-04-06T05:40:00Z",
  "risk_notes": ["event_risk_active"],
  "no_trade": false
}
```

### 2) 계산 규칙
- bias 결정: ensemble score + 레짐 필터.
- neutral 임계값 내에서는 `no_trade=true`로 반환(강제 매매 아이디어 금지).
- SL: 구조 이탈 + ATR 기준의 최대값 사용.
- TP: 1R/2R/3R + 오더북 유동성 벽/청산 클러스터 반영.
- 파생 과열(funding/OI/basis/ELR 급등) 시 TP 폭 축소 + SL 보수화.
- 이벤트 리스크(news/geopolitics/calendar) 발생 시 TP·SL 모두 보수적 조정.

### 3) 스타일별 차등
- Spot: 상대적으로 넓은 SL, 긴 horizon 허용.
- Perp: funding/청산/레버리지 반영하여 SL 더 엄격.
- Swing: 거시/이벤트 영향 비중 확대.
- Intraday: microstructure(스프레드/깊이/taker ratio/CVD) 비중 확대.

---

## H. 백테스트/평가 설계

### 필수 항목
1. Walk-forward validation.
2. Regime-based backtest(risk-on/off, high-vol, event windows).
3. Long/Short 분리 성능.
4. Win rate.
5. Expectancy.
6. Max drawdown.
7. Sharpe(또는 Sortino/Calmar).
8. TP/SL hit sequence 분석.
9. Feature importance.
10. Astrology engine on/off ablation.
11. Geopolitics feature on/off ablation.

### 추가 필수 평가
- Microstructure/derivatives feature on/off 비교.
- Event calendar feature on/off 비교.
- Neutral No-Trade 정책의 손실 회피 기여도.

---

## I. 구현 우선순위 (4단계)

### Phase 1: read-only 분석 에이전트
- 산출물: 시나리오 + evidence + freshness + confidence.
- 리스크: 데이터 결측/지연.
- 완료 조건: 스키마 통과 100%, stale 데이터 경고 동작.

### Phase 2: 구조화 TP/SL 제안
- 산출물: 룰 기반 TP/SL/invalidation/horizon + no-trade.
- 리스크: 과열/이벤트 구간 과최적화.
- 완료 조건: baseline 대비 expectancy 개선 + MDD 관리.

### Phase 3: paper trading/simulated execution
- 산출물: 모의 체결, 비용/슬리피지/펀딩 반영 성과.
- 리스크: 실거래 체결 괴리.
- 완료 조건: 4~8주 안정성 검증.

### Phase 4: 실제 execution adapter 연동
- 산출물: 브로커/거래소/Minara 어댑터 + 승인 워크플로.
- 리스크: 보안/키관리/컴플라이언스.
- 완료 조건: kill-switch/감사로그/롤백 테스트 통과.

---

## J. 개발 스택 제안 (MVP 중심)
- Frontend: Next.js + TypeScript.
- Backend: FastAPI(Python).
- DB: PostgreSQL(+Timescale optional).
- Cache: Redis.
- Queue/Scheduler: Celery(or RQ) + APScheduler.
- Vector store: 초기 optional(pgvector 필요 시만).
- Model orchestration: LangGraph 또는 경량 orchestrator.
- Backtesting: vectorbt/backtrader + pandas/polars.
- Observability: Prometheus + Grafana + OpenTelemetry.
- Secrets: Cloud Secret Manager(or Doppler).

---

## K. 저장소 구조 초안
```bash
apps/
  web/
services/
  api-gateway/
  ingestion/
  normalization/
  feature-store/
  signal-engine/
  risk-engine/
  llm-reporter/
  execution-adapter/
packages/
  schemas/
  data-contracts/
  clients/
  common/
research/
  notebooks/
  experiments/
backtests/
  configs/
  runs/
  reports/
infra/
  docker/
  terraform/
docs/
  prd/
  architecture/
  runbooks/
```

---

## L. 지금 당장 시작할 최소 MVP 태스크 10개
1. 공통 데이터 계약 정의(필수 메타데이터 9개 필드 포함).
2. microstructure 수집(order book imbalance/spread/depth/taker/large trade/CVD).
3. derivatives 수집(funding/OI/OI delta/basis/perp premium/liquidation/L-S/ELR/top trader 가능 여부).
4. on-chain/exchange-flow 수집(inflow/outflow/whale/stablecoin mint-burn/bridge/TVL/DEX volume/unlock/staking).
5. macro/cross-asset 수집(DXY/US10Y/VIX/CL/Gold/Silver/Nasdaq proxy).
6. structured geopolitics 이벤트 테이블 구축(impact direction/intensity/half-life).
7. news/sentiment 구조화 파이프라인(headline/event_type/impact/half-life/related_assets).
8. crypto event calendar 구축(unlock/listing/governance/ETF-SEC/mainnet-TGE-airdrop/protocol).
9. risk engine v0 구현(과열·이벤트 시 TP/SL 보수화 + neutral no-trade).
10. ablation 백테스트 자동화(astrology on/off, geopolitics on/off, microstructure on/off).

---

## 참고 자료 해석 메모
- Minara: 실행 레이어 후보(Phase 4 어댑터).
- WorldMonitor: 실시간 인텔리전스/데이터 집계 구조의 참고 모델.
- 이미지 브리프: lead-lag, 스테이지, 시장 폭 개념을 시그널과 대시보드 설계에 반영.
- 점성술 PDF: 현재 세션에서 파일 접근 불가로 확인되어, experimental schema만 반영.
