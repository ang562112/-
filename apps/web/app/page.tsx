"use client";

import { useState } from "react";
import type { AnalysisResponse } from "@/lib/types";

type ApiState = {
  loading: boolean;
  error: string | null;
  staleWarning: string | null;
  report: AnalysisResponse | null;
};

export default function HomePage() {
  const [symbol, setSymbol] = useState("BTC");
  const [state, setState] = useState<ApiState>({
    loading: false,
    error: null,
    staleWarning: null,
    report: null
  });

  async function onAnalyze() {
    setState({ loading: true, error: null, staleWarning: null, report: null });

    try {
      const res = await fetch(`/api/report?symbol=${encodeURIComponent(symbol)}`, { cache: "no-store" });
      const data = await res.json();

      if (!res.ok) {
        if (res.status === 409) {
          setState({
            loading: false,
            error: "Stale data: fresh 데이터 확보 전 결과를 표시하지 않습니다.",
            staleWarning: `freshness=${data.freshness_sec}s, threshold 초과`,
            report: null
          });
          return;
        }

        throw new Error(data.error ?? "analysis request failed");
      }

      setState({ loading: false, error: null, staleWarning: null, report: data as AnalysisResponse });
    } catch (error) {
      setState({
        loading: false,
        error: error instanceof Error ? error.message : "unknown error",
        staleWarning: null,
        report: null
      });
    }
  }

  return (
    <main>
      <h1>LLM Multifactor Read-only Dashboard</h1>
      <p>심볼 입력 후 분석 요청(JSON). freshness/confidence 필수.</p>

      <div className="card" style={{ display: "flex", gap: "0.5rem" }}>
        <input value={symbol} onChange={(e) => setSymbol(e.target.value.toUpperCase())} placeholder="BTC" />
        <button onClick={onAnalyze} disabled={state.loading}>
          {state.loading ? "Analyzing..." : "분석 요청"}
        </button>
      </div>

      {state.error ? (
        <div className="card bad">
          <strong>오류:</strong> {state.error}
          {state.staleWarning ? <p className="warn">{state.staleWarning}</p> : null}
        </div>
      ) : null}

      {state.report ? (
        <div className="card">
          <p><strong>symbol:</strong> {state.report.symbol}</p>
          <p><strong>bias:</strong> {state.report.bias}</p>
          <p><strong>freshness:</strong> <span className={state.report.stale ? "warn" : "ok"}>{state.report.freshness_sec}s</span></p>
          <p><strong>confidence:</strong> {state.report.confidence_score}</p>
          <p><strong>no_trade:</strong> {String(state.report.no_trade)}</p>
          <h3>JSON response</h3>
          <pre>{JSON.stringify(state.report, null, 2)}</pre>
        </div>
      ) : null}
    </main>
  );
}
