Worker: Claude (116차 계속, Claude Sonnet 5)
Date: 2026-09-21
Repository: ryujmin97/openpilot
Code Branch: carrot-ryu (base `62ae74dcd0aad4bc09c2409e45d7c9861351b401`, 116차 camera_sync 반영 확인. 부모 `0e1bef52` = 115차 dead code 1차 배치)
Note Branch: carrot-ryu-note (base `03ba2f7f8e8602d197ec750c4acbef91ce39691f`, 116차 devnotes 반영 확인. 이 후속 스크립트 반영 후 HEAD는 다음 세션이 git ls-remote로 확인)
carrot-ms 마지막 검토/동기화 체크포인트: `4bb4b510`(camera_sync 스큐 허용오차 10ms→20ms) 반영 완료(WIP_SYNC.md 116차). 111차 확정 체크포인트는 `a23a77b1`.

작업:
1. carrot-ms `4bb4b510` 적용(camera_sync.py MAX_CAMERA_SKEW_NS 도입 + 임계값 교체, test_camera_sync.py 회귀 테스트 4종 추가) 반영 확인.

완료:
1. 세션 시작 확인: 지침 v2 조회, HANDOFF.md 확인, 브랜치 HEAD 확인.
2. camera_sync 스큐 완화 push를 raw.githubusercontent.com(SHA 고정)으로 확인(사전 시뮬레이션 결과와 byte-exact 동일, 파일 개수/이름 일치). devnotes push도 동일 방식으로 확인.
3. 이 후속 스크립트로 WIP.md 116차 계속, HANDOFF.md를 최신화.

미완료(다음 세션 최우선):
1. 실차 배포(디바이스 pull) 시점 -- 사용자 확인 후. 배포 후 swaglog로 플래너 예외/카메라 페어링 이상 여부 확인.
2. dead code 후속 배치: C10/C15(VW MEB, 5개 파일)는 별도 세션. 추적은 devnotes/DEAD_CODE_REVIEW.md.
3. (이월) 114차 MAP_TURN_GUIDE_FACTOR 1.00 실차 관찰(급감속 구간이 운전자 제동인지 시스템 감속인지 확인), 110차 GATE_M 0.8/1.0 관찰, 견고성 스윕 재개(선택). CURRENT_STATUS.md는 이번에도 갱신하지 않았다.

검증: 샌드박스 정적/단위 검증(py_compile, pyflakes, test_camera_sync.py 15건 통과)과 GitHub push 내용 대조(raw 조회, byte-exact 확인). 실차 검증: 미실시(이번 세션 전체).

주의사항:
- camera_sync 스큐 완화는 동작 변화가 카메라 SOF 페어링 허용오차 10ms->20ms뿐이라는 정적 분석/upstream 테스트 결과이며 실차나 통합 테스트로 확인한 것은 아니다. 되돌리려면 `git revert 62ae74dc`(carrot-ryu).
- 115차 dead code 삭제(`0e1bef52`)와 116차 camera_sync 변경(`62ae74dc`)이 모두 미배포 상태로 누적돼 있다. 디바이스 배포 시 두 변경이 한 번에 반영됨을 인지해야 한다.

다음 작업 후보:
1. 실차 배포 여부 결정, 배포 후 관찰(플래너 예외 + 카메라 페어링).
2. dead code 2차 배치(VW MEB 별도 세션) 후보 검증.
3. carrot-ms 후속 신규 커밋 발생 시 2절(폐지된 필터 없이 전체 개별 분석) 재점검.
4. 114차/110차 이월 실차 관찰 항목.