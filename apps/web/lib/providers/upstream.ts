import type { AnalysisResponse } from "../types";

export async function fetchUpstreamReport(symbol: string): Promise<AnalysisResponse> {
  const baseUrl = process.env.REPORT_API_URL;

  if (!baseUrl) {
    throw new Error("REPORT_API_URL is required in production mode.");
  }

  const response = await fetch(`${baseUrl.replace(/\/$/, "")}/report?symbol=${encodeURIComponent(symbol)}`, {
    method: "GET",
    headers: {
      Authorization: `Bearer ${process.env.REPORT_API_TOKEN ?? ""}`
    },
    cache: "no-store"
  });

  if (!response.ok) {
    throw new Error(`Upstream report failed: ${response.status}`);
  }

  return (await response.json()) as AnalysisResponse;
}
