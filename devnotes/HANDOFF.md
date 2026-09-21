Worker: Claude (120차 계속, Claude Sonnet 5)
Date: 2026-09-21
Repository: ryujmin97/openpilot
Code Branch: carrot-ryu (`b98620e8e5c02e8985a0a89daab1ef002e8674c3`, 120차 A그룹 삭제 커밋. 부모 `df7da7d5`. GitHub에서 확인 완료)
Note Branch: carrot-ryu-note (이 스크립트 반영 전 base `d70389a27ef514466abf85cf838471fd5e3b17a4`. 반영 후 HEAD는 다음 세션이 git ls-remote로 확인)
carrot-ms 마지막 검토/동기화 체크포인트: `4bb4b510`(116차, camera_sync 스큐 허용오차 10ms->20ms) 반영 완료. 111차 확정 체크포인트는 `a23a77b1`. 이번 세션은 carrot-ms 동기화 작업 없음.

작업:
1. DEAD_CODE_REVIEW 4차 배치 A그룹(17개 파일, def 29개, 순 +1/-302줄) 삭제 스크립트 작성/검증 -> 사용자 실행 -> GitHub 재확인.
2. devnotes 갱신 2회(120차 스크립트 준비 기록 `d70389a2`, 120차 계속 A그룹 완료 정정 -- 이 스크립트).

완료:
1. A그룹 제거 완료: carrot-ryu `b98620e8`. 부모 `df7da7d5`, 17개 파일 부모 blob == 스크립트 `Pre`, 결과 blob == `Post` 전부 일치, 변경 파일 목록 일치(GitHub blobless fetch + `git ls-tree`, 16절). 검증 방법과 삭제 내용은 WIP.md 120차 참고.
2. 노트 `d70389a2`: 3개 파일 SHA-256이 스크립트 사후 값과 일치. 그 3개 파일의 "실행/push 대기" 표기는 이 스크립트로 정정.
3. 사용자 PC에서 두 스크립트가 실행됨(Windows PowerShell 버전, 실행 로그 원문은 미수령).

미완료(다음 세션 최우선):
1. B그룹(`controls/lib/desire_lib/blinker_manager.py` 파일 통째, `controls/lib/lane_planner_2.py`의 `max_abs`/`calculate_plan_yaw_and_yaw_rate`, `carrot/model_selector`의 `jobs.py list_recent`/`manifest.py onnx_filenames`, `radar_motion/predictor.py`의 `path_exit_probability`/`_radar_path`) 삭제 스크립트 작성. 착수 전 11절 재확인(codeload tarball, 대상 커밋은 `b98620e8`). 사용자 승인은 A -> B -> C 순차로 이미 받음(119차).
2. C그룹(cluster 계열, 약 300줄) -- B그룹 이후.
3. 실차 배포(디바이스 pull) 시점 -- 115차(`0e1bef52`)/116차(`62ae74dc`)/117차(`22b101f6`)/118차(`df7da7d5`)/120차 A그룹(`b98620e8`) 5건 미배포 누적, 계속 이월.
4. (이월) 114차 MAP_TURN_GUIDE_FACTOR 1.00 실차 관찰, 110차 GATE_M 0.8/1.0 관찰. CURRENT_STATUS.md는 이번에도 갱신하지 않았다.
5. pytest는 conftest(`params_pyx` 컴파일 산출물 필요) 없이 `--noconftest`로만 실행했으므로 실제 CI 조건의 pytest 실행은 여전히 미실시.

검증: 샌드박스 정적 검증(py_compile/pyflakes/grep/pytest --noconftest 삭제 전후 비교) + GitHub 대조. 실차 검증: 미실시(12절 무관, 삭제 대상은 전부 참조 0곳이라 동작 변화 없을 것으로 정적 분석했을 뿐).

주의사항:
- 문제가 생기면 carrot-ryu `b98620e8` 커밋 1개를 revert하면 A그룹이 복구된다(코드 커밋은 이것 하나).
- B그룹의 `blinker_manager.py`는 파일 통째 삭제라 A그룹처럼 Replace-Block이 아니라 `git rm` 경로가 필요하고, 삭제 후 py_compile/import 가드가 다르다. 스크립트 구조는 이 점을 반영해 새로 짤 것.
- 샌드박스는 세션 중에도 초기화될 수 있다(120차에 실제 발생). 중간 결과는 스크립트/문서로 바로 남길 것.

다음 작업 후보:
1. B그룹 삭제 스크립트 작성(1순위, 승인 완료).
2. 실차 배포 여부 결정, 배포 후 관찰(controlsd/플래너 예외 + 카메라 페어링 + 대시캠 업로드 + 로그탭 업로드 경로 + live_runtime `/api/live_runtime`).
3. C그룹 착수, 114차/110차 이월 실차 관찰 항목.
