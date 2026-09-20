Worker: Claude (115차, Claude Sonnet 5)
Date: 2026-09-21
Repository: ryujmin97/openpilot
Code Branch: carrot-ryu (base `fa75aeab7b63233db4c4942021675f0536ee7160`, 114차 MAP_TURN_GUIDE_FACTOR 1.00 반영 확인. 115차 dead code 1차 배치는 스크립트 실행 후 반영되며 그 HEAD는 다음 세션이 git ls-remote로 확인)
Note Branch: carrot-ryu-note (base `fdaaf452d61d42752844f6a8161f887597398b59`, 115차 지침 2절 2번·7번 폐지 반영 확인. 이 세션의 devnotes 스크립트 반영 후 HEAD는 다음 세션이 git ls-remote로 확인)
carrot-ms 마지막 검토/동기화 체크포인트: 신규 1건 `4bb4b510`(carrot-wip `d2973b3f` cherry-pick)은 후보로만 기록, 반영 보류(WIP_SYNC.md 115차). 111차 확정 체크포인트는 `a23a77b1`.

작업:
1. 지침 2절 필터 폐지를 반영 확인했다. 2번 항목(carrot-wip 배타 필터, note `2358da1c`)과 7번 항목("모델셀렉터와 무관한 커밋 기본 제외", note `fdaaf452`). 앞으로 carrot-ms 신규 커밋은 전부 개별 분석한다.
2. dead code 1차 배치(C01 get_jerk_factor, C12 prev_accel_clip, C16 get_max_accel/A_CRUISE_MAX_*, C06 throttle/coast 계산부)의 삭제 코드와 반영 스크립트를 만들었다. `allowThrottle` 메시지 필드는 유지한다.

완료:
1. 세션 시작 확인: 지침 v2 조회(note `50283ef1`), HANDOFF.md 확인, 브랜치 HEAD 확인.
2. 지침 변경 2건의 push를 SHA 고정 raw와 diff로 확인(PROJECT_INSTRUCTIONS LF, WIP_SYNC CRLF 개행 유지, BOM 없음).
3. dead code 후보를 carrot-ryu `fa75aeab` tarball grep으로 재검증하고 삭제 diff 작성(3개 파일 9개 블록). py_compile, pyflakes(원본/수정본 모두 0건), test_turn_accel 24건 통과(원본 24, 수정본 24), 스크립트 앵커 시뮬레이션(매치 1회, 작업 트리와 바이트 동일)까지 확인.

미완료(다음 세션 최우선):
1. 두 스크립트 실행 결과 확인: 코드 `115cha_deadcode_batch1_code_carrot_ryu-v1.ps1`(carrot-ryu), devnotes `115cha_deadcode_batch1_devnotes_carrot_ryu_note-v1.ps1`(carrot-ryu-note). 사용자가 push 로그를 전달하기 전까지는 GitHub 반영으로 간주하지 않는다. 다음 세션은 git ls-remote로 두 브랜치 HEAD와 longitudinal_planner.py 삭제 반영(SHA 고정 raw)을 확인.
2. 코드 반영 후 실차 배포(디바이스 pull) 시점은 사용자 확인 후.
3. dead code 후속 배치: C10/C15(VW MEB, 5개 파일)는 별도 세션. 추적은 devnotes/DEAD_CODE_REVIEW.md.
4. carrot-ms `4bb4b510` 반영 여부 사용자 판단 대기.
5. (이월) 114차 MAP_TURN_GUIDE_FACTOR 1.00 실차 관찰(급감속 구간이 운전자 제동인지 시스템 감속인지 확인, 46.00s 브레이크 사유), 110차 GATE_M 0.8/1.0 관찰, 견고성 스윕 재개(선택). CURRENT_STATUS.md는 이번에도 갱신하지 않음.

검증: 위 3번의 샌드박스 정적/단위 검증. `test_longitudinal.py`(네이티브 MPC 필요)와 전체 테스트 스위트는 실행하지 못했다. 스크립트의 PowerShell 문법은 샌드박스에 pwsh가 없어 실행 검증하지 못했다. 실차 검증: 미실시(이번 세션 전체).

주의사항:
- dead code 삭제는 동작 변화가 없다는 정적 분석 결과일 뿐, 실차나 통합 테스트로 확인한 것이 아니다. 되돌리려면 `git revert <115차 코드 커밋>`.
- 코드 반영 전 스크립트가 carrot-ryu HEAD가 `fa75aeab`가 아니면 스스로 중단한다(그 사이 다른 push가 있었다는 뜻이므로 Claude에게 보고).
- `test_turn_accel.py`의 `parse_model` 목이 4튜플로 바뀐다. `longitudinal_planner.py`의 `parse_model()` 반환 형태에 다시 손댈 때는 이 목도 함께 확인해야 한다.
- 지침 16절/1절의 "모델셀렉터" 문구는 아직 그대로다(범위 밖).

다음 작업 후보:
1. 스크립트 반영 확인 -> 필요 시 DEAD_CODE_REVIEW.md 상태 칸을 "제거 완료"로 갱신.
2. dead code 2차 배치 후보 검증(C10/C15 VW MEB는 별도 세션).
3. carrot-ms 후속 신규 커밋 발생 시 2절(폐지된 필터 없이 전체 개별 분석) 재점검.
4. 114차 이월 실차 관찰 항목.
