export type Bias = "bullish" | "bearish" | "neutral";

export type AnalysisResponse = {
  symbol: string;
  bias: Bias;
  freshness_timestamp: string;
  freshness_sec: number;
  confidence_score: number;
  stale: boolean;
  no_trade: boolean;
  evidence_list: string[];
  risk_notes: string[];
  payload: Record<string, unknown>;
};
