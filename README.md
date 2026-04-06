# LLM Multifactor Trading Agent (Read-only)

이 저장소는 **LLM 기반 멀티팩터 트레이딩 분석 시스템**의 모노레포 초안입니다.
핵심 원칙은 아래와 같습니다.

- 자동매매 미구현 (read-only 분석 시스템)
- LLM은 설명/리포팅 레이어 전용
- 데이터 freshness/confidence 없이는 결과를 제공하지 않음
- stale 데이터는 경고 후 차단

## Monorepo 구조

```bash
apps/
  web/                    # Next.js dashboard + thin API route (/api/report)
services/                 # External runtime targets (NOT vercel)
  ingestion/
  signal-engine/
  risk-engine/
  report-worker/
backtests/                # External runtime batch jobs
docs/
```

## 로컬 실행 방법

### 1) 환경변수 준비
```bash
cp .env.example .env
```

기본값은 mock mode:
- `REPORT_PROVIDER_MODE=mock`

### 2) 의존성 설치
```bash
npm install
```

### 3) 웹 실행
```bash
npm run dev:web
```

브라우저: `http://localhost:3000`

### 4) 동작 확인
- 심볼 입력(BTC 등) -> `분석 요청`
- JSON 응답 확인
- `freshness`, `confidence`, `no_trade` 표시 확인

## Vercel 배포 방법 (apps/web)

> 원칙: Vercel에는 `apps/web`만 올립니다.

1. Vercel에서 저장소 Import
2. Project Root를 `apps/web`로 지정(권장)
3. Environment Variables 설정
4. Deploy

### Vercel 필수 환경변수
- `REPORT_PROVIDER_MODE` (`mock` or `production`)
- `MAX_FRESHNESS_SECONDS` (예: 120)
- `REPORT_API_URL` (production 모드에서 필수)
- `REPORT_API_TOKEN` (production 모드에서 권장)

### 선택 환경변수
- `NEXT_PUBLIC_APP_NAME`
- `NEXT_PUBLIC_APP_ENV`

## 별도 런타임 배포 대상 설명 (Vercel 금지 대상)

아래 컴포넌트는 Vercel Function에 올리지 않습니다.

- `services/ingestion`
- `services/report-worker`
- `services/signal-engine`
- `services/risk-engine`
- `backtests`
- scheduled jobs / cron / background workers

권장 대상: Railway/Fly/Render/ECS/K8s

## 환경변수 설명

`.env.example` 참고:

- 공통
  - `APP_ENV`
  - `REPORT_PROVIDER_MODE`
  - `MAX_FRESHNESS_SECONDS`
- 웹(Vercel)
  - `REPORT_API_URL`
  - `REPORT_API_TOKEN`
- 외부 런타임
  - `POSTGRES_URL`, `REDIS_URL`, `EVENT_QUEUE_URL`
  - provider API keys (`EXCHANGE_API_KEY`, `NEWS_API_KEY`, ...)

## 운영 시 주의사항

1. stale data 차단 정책 유지 (`freshness` 기준).
2. freshness timestamp 누락 시 결과 미표시.
3. neutral 레짐에서는 강제 매매 아이디어 금지(`no_trade=true`).
4. 자동매매 adapter 연결 금지(현 단계).
5. mock/prod 모드 전환 시 runbook 기반 점검.

## 문서

- PRD: `docs/llm-multifactor-trading-agent-prd-v1.md`
- 배포 순서: `docs/deployment-order.md`
- 운영 체크리스트: `docs/operations-checklist.md`
- 프로덕션 아키텍처: `docs/production-architecture.md`
