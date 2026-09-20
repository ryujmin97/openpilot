Worker: Claude (115차 계속, Claude Sonnet 5)
Date: 2026-09-21
Repository: ryujmin97/openpilot
Code Branch: carrot-ryu (base `0e1bef52eb36eb01d683898be4561c243083c160`, 115차 dead code 1차 배치 반영 확인. 부모 `fa75aeab` = 114차 MAP_TURN_GUIDE_FACTOR 1.00)
Note Branch: carrot-ryu-note (base `d10d23828a2852439c1854ff1ac6992142f1e3f0`, 115차 devnotes 반영 확인. 이 후속 스크립트 반영 후 HEAD는 다음 세션이 git ls-remote로 확인)
carrot-ms 마지막 검토/동기화 체크포인트: 신규 1건 `4bb4b510`(carrot-wip `d2973b3f` cherry-pick)은 후보로만 기록, 반영 보류(WIP_SYNC.md 115차). 111차 확정 체크포인트는 `a23a77b1`.

작업:
1. 지침 2절 필터 폐지(2번 항목 carrot-wip 배타 필터, 7번 항목 모델셀렉터 무관 커밋 기본 제외) 반영 확인. 앞으로 carrot-ms 신규 커밋은 전부 개별 분석한다.
2. dead code 1차 배치(C01/C12/C16/C06 계산부) 삭제 반영 확인: carrot-ryu `0e1bef52`, 3개 파일 +5/-49, `allowThrottle` 메시지 필드는 유지.

완료:
1. 세션 시작 확인: 지침 v2 조회, HANDOFF.md 확인, 브랜치 HEAD 확인.
2. 지침 변경 2건 push 확인(note `2358da1c`, `fdaaf452`).
3. dead code 1차 배치 코드 push를 codeload tarball로 확인(작업본과 바이트 동일, 삭제 대상 이름 잔존 0, allowThrottle 발행 유지). devnotes push(note `d10d2382`)도 SHA 고정 raw로 확인.
4. 이 후속 스크립트로 WIP.md 115차 계속, DEAD_CODE_REVIEW.md 상태 칸, HANDOFF.md를 최신화.

미완료(다음 세션 최우선):
1. 실차 배포(디바이스 pull) 시점 -- 사용자 확인 후. 배포 후 첫 주행에서 플래너 예외 로그(swaglog)가 없는지 확인.
2. dead code 후속 배치: C10/C15(VW MEB, 5개 파일)는 별도 세션. 추적은 devnotes/DEAD_CODE_REVIEW.md.
3. carrot-ms `4bb4b510` 반영 여부 사용자 판단 대기.
4. (이월) 114차 MAP_TURN_GUIDE_FACTOR 1.00 실차 관찰(급감속 구간이 운전자 제동인지 시스템 감속인지 확인, 46.00s 브레이크 사유), 110차 GATE_M 0.8/1.0 관찰, 견고성 스윕 재개(선택). CURRENT_STATUS.md는 이번에도 갱신하지 않음.

검증: 샌드박스 정적/단위 검증(py_compile, pyflakes, test_turn_accel 24건 통과 -- 원본 24, 수정본 24)과 GitHub push 내용 대조. `test_longitudinal.py`(네이티브 MPC 필요)와 전체 테스트 스위트는 실행하지 못했다. 실차 검증: 미실시(이번 세션 전체).

주의사항:
- dead code 삭제는 동작 변화가 없다는 정적 분석 결과일 뿐 실차나 통합 테스트로 확인한 것이 아니다. 되돌리려면 `git revert 0e1bef52`(carrot-ryu).
- `test_turn_accel.py`의 `parse_model` 목이 4튜플로 바뀌었다. `longitudinal_planner.py`의 `parse_model()` 반환 형태에 다시 손댈 때는 이 목도 함께 확인해야 한다.
- 지침 16절/1절의 "모델셀렉터" 문구는 아직 그대로다(범위 밖).

다음 작업 후보:
1. 실차 배포 여부 결정, 배포 후 관찰.
2. dead code 2차 배치(VW MEB 별도 세션) 후보 검증.
3. carrot-ms 후속 신규 커밋 발생 시 2절(폐지된 필터 없이 전체 개별 분석) 재점검.
4. 114차 이월 실차 관찰 항목.
