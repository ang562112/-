# 운영 체크리스트 (Read-only)

- [ ] 자동매매 기능 비활성화(실주문 adapter 미연결).
- [ ] `REPORT_PROVIDER_MODE`가 의도한 값인지 확인(mock/production).
- [ ] `freshness_timestamp` 누락 시 응답 차단되는지 확인.
- [ ] stale data(`freshness_sec > MAX_FRESHNESS_SECONDS`) 경고 노출 확인.
- [ ] `confidence_score` 표시 확인.
- [ ] evidence/risk notes 포함 여부 확인.
- [ ] report-worker auth token 검증 확인.
- [ ] ingestion/scheduler가 Vercel이 아닌 외부 런타임에서 실행 중인지 확인.
- [ ] 장애 시 mock 모드 전환 절차(runbook) 준비.
- [ ] 릴리즈 전 smoke test: BTC/ETH/SOL 각각 `/api/report` 호출.
