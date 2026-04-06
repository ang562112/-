# Sample Production Architecture

## Vercel (Frontend + Thin API)
- `apps/web`
  - UI dashboard
  - `/api/report` thin route (input validation + freshness guard + proxy)

## External Runtime (Railway/Fly/Render/K8s)
- `services/ingestion`: market/onchain/news/macro 수집
- `services/signal-engine`: 시그널 계산
- `services/risk-engine`: TP/SL/invalidation/no-trade 계산
- `services/report-worker`: read-only report API
- `backtests/`: 배치 백테스트 및 평가
- Scheduler/Cron/Queue workers

## Data Layer
- Postgres: normalized & historical data
- Redis: low-latency cache / queue

## Security
- Vercel -> report-worker 통신은 토큰 기반 인증
- read-only endpoint only
