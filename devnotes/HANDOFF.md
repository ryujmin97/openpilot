Worker: Claude (191cha, Claude Sonnet 5)
Date: 2026-09-28
Repository: ryujmin97/openpilot
Code Branch: carrot-ryu (base commit 6ed56f0d64df0612e3993e247d03fc199903569e, 변동 없음 — 191cha는 코드 변경 없음.)
Note Branch: carrot-ryu-note (base commit caec97bbaeea6f225e0f6e259116131028e56d7e, 190차 devnotes push 완료 확인. 191cha devnotes는 이 커밋 위에 push.)
carrot-ms 마지막 검토 체크포인트: 087fdca74f0e2c90b7c6b216e913736961ef8c15 -> 3441183(변동 없음, 188cha에서 확정, 191cha에서 변동 없음)

작업:
1. 사용자가 5절(작업 흐름) 문제 제기: 코드 push + devnotes push 이후, devnotes에
   "완료 확인"을 반영하려고 다시 한번 push해야 하는 구조가 불합리하다는 지적.
2. 19절 절차대로 원인 설명(동시 전달 방식 때문에 devnotes 작성 시점에 코드 push
   결과를 알 수 없어 재작성이 필요했음) → 변경안(순차 전달: 코드 스크립트 먼저 →
   실행/확인 → 그 다음 devnotes 스크립트 작성) 제시 → 사용자 승인.
3. PROJECT_INSTRUCTIONS_carrot-ryu.md 5절을 순차 전달 방식으로 교체(절 번호/제목
   유지, 18절의 절 번호 재배치 금지 원칙 준수).
4. WIP.md에 191cha 회차 기록 추가.
5. 이 HANDOFF.md 갱신.

완료:
1. 5절 개정(19절 절차 완료: 이유 → 기존규칙 → 변경안 → 승인 → 변경 → GitHub 저장).
2. WIP.md 191cha 기록.

미완료:
1. (이월) 핵심 발견 68 실차 검증, 163차 게이트 실주행 검증, xTurn=6 로그 확보,
   pytest CI 환경(conftest.py 포함 실제 cereal 실행), 102ms wide-camera BOOT_TS
   gap.
2. (이월) carrot-ms 정기 동기화 점검(2절) — 다음 세션에서 필요 여부 판단.

검증:
- 개정된 5절 텍스트를 세션 응답에서 사용자에게 먼저 보여주고 승인받은 뒤에만
  반영 스크립트를 작성함(19절).
- 실차 검증: 미실시(12절, 191cha는 코드 변경 없음).

주의사항:
- 다음 세션부터 코드 변경이 있는 작업은 5절 신규 절차(코드 스크립트 단독 전달 →
  실행/확인 → devnotes 스크립트 전달)를 따를 것. 코드+devnotes 스크립트를 동시에
  만들지 않는다.
- devnotes만 다루는 세션(이번처럼)은 기존과 동일하게 devnotes 스크립트 1개만
  전달하면 된다 — 신규 절차는 코드 변경이 있는 세션에만 적용된다.

다음 작업:
1. carrot-ms 정기 동기화 점검(2절) 필요 여부 판단.
2. 이월 항목(실차 검증들) 중 우선순위 있는 것부터 진행.
3. 다음에 코드 변경이 발생하는 세션에서 신규 5절 절차(순차 전달)를 실제로
   적용해보고, 문제가 없는지 확인.
