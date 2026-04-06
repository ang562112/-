# Deployment Order (Read-only System)

## 0) Principle
- Vercel: `apps/web` + thin API route only.
- External runtime: ingestion, signal-engine, risk-engine, report-worker, backtests, cron.

## 1) External Runtime First
1. Deploy `services/signal-engine`.
2. Deploy `services/risk-engine`.
3. Deploy `services/report-worker` (expose `/report?symbol=` read-only endpoint).
4. Deploy ingestion + scheduler + queues.
5. Verify report-worker returns `freshness_timestamp` + `confidence_score`.

## 2) Configure Vercel Project
1. Import monorepo to Vercel.
2. Set **Root Directory** to `apps/web` (recommended) OR keep root + use scripts.
3. Add env vars:
   - `REPORT_PROVIDER_MODE`
   - `REPORT_API_URL`
   - `REPORT_API_TOKEN`
   - `MAX_FRESHNESS_SECONDS`
4. Deploy Preview, then Production.

## 3) Validation
- Request `/api/report?symbol=BTC`.
- If stale data, UI must show warning and hide actionable output.
- If freshness missing, endpoint must reject.

## 4) Rollout
- Start with `REPORT_PROVIDER_MODE=mock`.
- Switch to `production` only after external runtime health checks pass.
