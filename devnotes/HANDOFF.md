Worker: Claude (116차, Claude Sonnet 5)
Date: 2026-09-21
Repository: ryujmin97/openpilot
Code Branch: carrot-ryu (base `0e1bef52eb36eb01d683898be4561c243083c160`, 116차 camera_sync 반영 스크립트 전달, 사용자 실행 대기)
Note Branch: carrot-ryu-note (base `133cbbd38930698fd8275b97b05a76334178f2ea`, 이 스크립트로 116차 devnotes 반영. 이 후속 스크립트 반영 후 HEAD는 다음 세션이 git ls-remote로 확인)
carrot-ms 마지막 검토/동기화 체크포인트: 4bb4b510(camera_sync 스큐 허용오차 10ms→20ms) 적용 승인, 반영 스크립트 전달(WIP_SYNC.md 116차). 111차 확정 체크포인트는 `a23a77b1`, 115차에는 4bb4b510을 후보로만 기록했었다.

작업:
1. HANDOFF 우선순위 2번(carrot-ms `4bb4b510` 분석) 수행: diff 확인, 현재 carrot-ryu 대응 코드 확인, DH2015+C3X 실행 경로 확인, 10ms 실패 사례/20ms 완화 영향 분석 -- 적용 권장으로 판정, 사용자 승인 받음.
2. `camera_sync.py`/`test_camera_sync.py` Replace-Block 스크립트 작성 및 사전 검증(앵커 1회 매치, carrot-ms 실제 결과와 byte-exact 동일, py_compile/pyflakes 0건, pytest 15건 통과).

완료:
1. `4bb4b510` 분석 및 적용 판정(콤마 C3X 기기 공통 버그 수정, DH 전용 아님), 사용자 승인.
2. 반영 스크립트 2개(코드/devnotes) 작성 및 샌드박스 검증. 코드 스크립트는 전달한 `.ps1` 파일에서 실제로 추출한 앵커 문자열로 재시뮬레이션까지 완료.

미완료(다음 세션 최우선):
1. 사용자가 두 스크립트 실행 -- push 로그 확인 후 GitHub에서 SHA 고정으로 재확인 필요(16절). "완료" 로그만으로 반영된 것으로 간주하지 않는다.
2. 실차 배포(디바이스 pull) 시점 -- dead code 1차 배치(115차) + camera_sync 변경(116차)을 함께/개별 배포할지 포함해 사용자 확인 후.
3. dead code 후속 배치: C10/C15(VW MEB, 5개 파일) -- 별도 세션. 추적은 devnotes/DEAD_CODE_REVIEW.md.
4. (이월) 114차 MAP_TURN_GUIDE_FACTOR 1.00 실차 관찰, 110차 GATE_M 0.8/1.0 관찰, 견고성 스윕 재개(선택). CURRENT_STATUS.md는 이번에도 갱신하지 않았다.

검증: 샌드박스 정적/단위 검증만(py_compile, pyflakes, pytest 15건 -- 기존 5건 + 신규 10건). 실차 검증: 미실시(이번 세션 전체).

주의사항:
- `camera_sync.py` 변경은 SOF 페어링 허용오차만 10ms -> 20ms로 완화하고, 리샌크 루프/타임아웃 등 그 외 로직은 그대로다. 되돌리려면 이번 커밋을 `git revert`.
- carrot-ms/carrot-wip 쪽 commit 메시지에도 "vehicle validation remains outstanding"으로 명시돼 있어, 우리 쪽 실차 검증 필요성과는 별개다.
- `test_turn_accel.py`의 `parse_model` 목이 4튜플로 바뀐 115차 변경 사항은 이번 세션과 무관하게 그대로 유지된다.

다음 작업 후보:
1. push 확인 후 실차 배포 여부 결정 및 관찰.
2. dead code 2차 배치(VW MEB 별도 세션) 후보 검증.
3. carrot-ms 후속 신규 커밋 발생 시 2절(폐지된 필터 없이 전체 개별 분석) 재점검.
4. 114차/110차 이월 실차 관찰 항목.