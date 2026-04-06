import { NextRequest, NextResponse } from "next/server";
import { getMockReport } from "@/lib/providers/mock";
import { fetchUpstreamReport } from "@/lib/providers/upstream";
import type { AnalysisResponse } from "@/lib/types";

const MAX_FRESHNESS_SECONDS = Number(process.env.MAX_FRESHNESS_SECONDS ?? "120");
const MODE = process.env.REPORT_PROVIDER_MODE ?? "mock";

function withFreshnessGuard(report: AnalysisResponse): AnalysisResponse {
  const nowMs = Date.now();
  const tsMs = new Date(report.freshness_timestamp).getTime();
  const freshnessSec = Number.isFinite(tsMs) ? Math.max(0, Math.floor((nowMs - tsMs) / 1000)) : Number.MAX_SAFE_INTEGER;

  const stale = freshnessSec > MAX_FRESHNESS_SECONDS || !report.freshness_timestamp;

  return {
    ...report,
    freshness_sec: freshnessSec,
    stale,
    risk_notes: stale ? [...report.risk_notes, "stale data warning"] : report.risk_notes
  };
}

export async function GET(req: NextRequest) {
  const symbol = (req.nextUrl.searchParams.get("symbol") ?? "BTC").trim().toUpperCase();
  if (!symbol) {
    return NextResponse.json({ error: "symbol is required" }, { status: 400 });
  }

  try {
    const baseReport = MODE === "production" ? await fetchUpstreamReport(symbol) : getMockReport(symbol);
    const report = withFreshnessGuard(baseReport);

    if (!report.freshness_timestamp) {
      return NextResponse.json({ error: "freshness_timestamp is required" }, { status: 422 });
    }

    if (report.stale) {
      return NextResponse.json(
        {
          error: "data is stale",
          stale: true,
          freshness_timestamp: report.freshness_timestamp,
          freshness_sec: report.freshness_sec,
          report
        },
        { status: 409 }
      );
    }

    return NextResponse.json(report, { status: 200 });
  } catch (error) {
    return NextResponse.json(
      { error: error instanceof Error ? error.message : "unknown report error" },
      { status: 500 }
    );
  }
}
