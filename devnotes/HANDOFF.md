Worker: Claude (124차, Claude Sonnet 5)
Date: 2026-09-22
Repository: ryujmin97/openpilot
Code Branch: carrot-ryu (`a0f4c5a5fb932be1525311d2ed61f5382a4bd6d2`, 123차 C그룹 dead code 삭제 커밋. 이번 세션에서 사용자가 실차 배포/검증까지 완료했음을 확인. 코드 변경 없음)
Note Branch: carrot-ryu-note (이 스크립트 반영 전 base `6b66f163c917310f66768693b81ba3889fa81a11`. 반영 후 HEAD는 다음 세션이 git ls-remote로 확인)
carrot-ms 마지막 검토/동기화 체크포인트: `4bb4b510`(116차, camera_sync 스큐 허용오차 10ms->20ms) 반영 완료. 이번 세션도 carrot-ms 신규 커밋 확인/동기화 작업 없음.

작업:
1. 사용자가 제공한 실차 디바이스 위젯 로그(git reset --hard -> `2efdd2e25`, git pull -> `a0f4c5a5f` Fast-forward)로 123차 C그룹까지 배포됐음을 재확인, 재부팅 후 실차 주행 검증 완료(이상 없음)를 devnotes에 기록.
2. DEAD_CODE_REVIEW.md의 C그룹 상태 줄에 실차 검증 완료를 추가, WIP.md에 124차 항목 신설.

완료:
1. carrot-ryu `a0f4c5a5f`(부모 `2efdd2e25`, 3파일 +0/-327)이 GitHub HEAD와 일치함을 재확인(16절).
2. CURRENT_STATUS.md(122차)와 대조해 115~121차(이미 실차 확인)에 123차 C그룹을 더해 4차 배치(A/B/C) 전체가 실차 검증 완료로 종결됨을 확인.
3. devnotes 2개 파일(WIP.md 신규 항목 / DEAD_CODE_REVIEW.md 상태 정정) 갱신.

미완료(다음 세션 최우선):
1. 이 스크립트(`124cha_realvehicle_verified_carrot_ryu_note-v1.ps1`) 실행/push 확인 -- GitHub SHA 고정 조회로 재확인(16절).
2. CURRENT_STATUS.md 97~114차 구간 상세 catch-up(122차부터 이월)과 115~124차 항목 이식 -- 여러 세션째 이월 중.
3. carrot-ms 신규 커밋 확인(2절) -- 지난 체크포인트(93~95차, `e324f67`) 이후 재확인이 오래 방치됨.
4. pytest를 실제 CI 조건(conftest 포함)으로 실행한 적이 없음 -- 계속 이월.
5. 114차/110차 이월 실차 관찰 항목(MAP_TURN_GUIDE_FACTOR 1.00, GATE_M 0.8/1.0)은 여전히 미확인.

검증: GitHub 커밋 대조 + 사용자 실차 로그/판단. 실차 검증: 완료(4차 배치 A/B/C 전체, 사용자 확인).

주의사항:
- 코드 변경 없음(devnotes만).
- 이번 실차 확인은 삭제 대상 각각을 개별로 트리거한 것이 아니라 정상 주행 범위 내 이상 없음 확인이다. 사용성이 낮은 경로(예: `/api/live_runtime`, 클러스터 디스플레이)를 실제로 쓰는 경우라면 추가 관찰이 유효할 수 있다.

다음 작업 후보:
1. carrot-ms 신규 커밋 확인(2절) 착수.
2. CURRENT_STATUS.md catch-up.
3. 114차/110차 이월 관찰 항목, dead code 5차 배치 필요 여부는 사용자 판단 대기.
