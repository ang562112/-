import type { AnalysisResponse } from "../types";

export function getMockReport(symbol: string): AnalysisResponse {
  const now = new Date();
  return {
    symbol,
    bias: "neutral",
    freshness_timestamp: now.toISOString(),
    freshness_sec: 4,
    confidence_score: 0.61,
    stale: false,
    no_trade: true,
    evidence_list: [
      "trend_engine:+0.10",
      "liquidity_derivatives:-0.08",
      "macro_regime:mixed"
    ],
    risk_notes: [
      "neutral regime",
      "no forced trade",
      "read-only report"
    ],
    payload: {
      entry_zone: null,
      stop_loss: null,
      tp1: null,
      tp2: null,
      tp3: null,
      invalidation_condition: ["regime shift required"],
      holding_horizon: "intraday"
    }
  };
}
