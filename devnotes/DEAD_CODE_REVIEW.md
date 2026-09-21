# DEAD CODE REVIEW

carrot-ryu의 dead code(호출/참조되지 않는 코드) 정리 추적 문서. 이어쌓기형: 새 배치는 표 아래에 회차 항목으로 추가하고, 기존 항목은 상태 칸만 갱신한다.

**원칙**: (1) 후보는 carrot-ryu 전체를 codeload tarball로 받아 심볼 단위 grep으로 참조 0건을 확정한 뒤에만 삭제한다(추측 금지, 11절). (2) 삭제 diff를 `py_compile`과 기존 테스트로 확인한다. (3) 사용자가 스크립트를 실행해 push하기 전에는 "제거 완료"로 쓰지 않는다. (4) 지침 10절 "최소 변경 원칙"과 방향이 반대(코드를 줄이는 이니셔티브)이므로 배치마다 사용자 승인을 받는다. (5) carrot-ms와의 차이가 늘어나는 점을 감안한다(20절 리셋 시 재이식 대상이 됨).

후보 번호(C01 등)는 ChatGPT 분석 세션에서 붙은 것이다. 그 분석의 전체 목록은 이 저장소에 없고, 아래는 Claude 세션에서 다시 검증한 후보만 적었다.

| 후보 | 위치 | repo 전체 참조 | 상태 |
|---|---|---|---|
| C01 `get_jerk_factor()` | long_mpc.py | 자기 파일의 주석 1곳뿐, 호출 0곳 | 제거 완료(115차, carrot-ryu `0e1bef52`, 실차 검증 미실시) |
| C12 `prev_accel_clip` | longitudinal_planner.py | 초기화 1곳 + 주석 블록뿐, 읽는 곳 0곳 | 제거 완료(115차, carrot-ryu `0e1bef52`, 실차 검증 미실시) |
| C16 `get_max_accel()` + `A_CRUISE_MAX_VALS/BP` | longitudinal_planner.py | 자기 파일의 주석 1곳뿐. `A_CRUISE_MAX_BP_CARROT`(carrot_functions.py)는 별개 상수 | 제거 완료(115차, carrot-ryu `0e1bef52`, 실차 검증 미실시) |
| C06 throttle/coast 계산부 | longitudinal_planner.py | 계산부는 `self.allow_throttle = True` 상수 때문에 실행되지 않음. 메시지 필드 `allowThrottle`은 UI 2곳과 클러스터 리플레이가 읽음 | 계산부만 1차 배치에서 삭제(필드와 `self.allow_throttle = True`는 유지). 제거 완료(115차, carrot-ryu `0e1bef52`, 실차 검증 미실시) |
| C10/C15 VW MEB(`is_volkswagen_meb`/`is_vw_meb`) | drive_helpers.py 정의 + cruise.py, controlsd.py, steer_ratio.py, longitudinal_planner.py, test_controlsd.py | 5개 파일에서 사용 중. `CP.brand == "volkswagen"`이 DH2015에서 항상 False라 각 분기는 죽은 경로이나 제거 범위가 큼 | 제거 완료(117차, carrot-ryu `22b101f6`, 7개 파일 +9/-153, 실차 검증 미실시) |
| 신규(118차) `web_upload.py`/`server/.../upload.py` 구 웹 업로드 경로 | web_upload.py(`create_web_upload_session`/`_sync`, `upload_folder_to_web`, `send_web_upload_complete`, `check_web_upload_health`, `tmux_web_target`, `_session_payload`/`_session_token`, `api_url`) + `server/features/dashcam/upload.py`(`resolve_upload_target`, `upload_target_settings`) | 9개 심볼 모두 프로덕션 참조 0곳(테스트만 참조, `check_web_upload_health`는 테스트도 0곳으로 완전 고아) | 제거 완료(118차, carrot-ryu `df7da7d5`, 3개 파일 +5/-814, 실차 검증 미실시) |

## 115차 -- 1차 배치 (C01 + C12 + C16 + C06 계산부)

- 대상 커밋 기준: carrot-ryu `fa75aeab`. 삭제 3개 파일(long_mpc.py, longitudinal_planner.py, test_turn_accel.py의 `parse_model` 목 반환값 5튜플 -> 4튜플).
- 검증과 동작 변화 없음 근거는 WIP.md 115차 참고. 실차 검증: 미실시.
- 상태: 코드 스크립트 `115cha_deadcode_batch1_code_carrot_ryu-v1.ps1` 실행·push 완료 확인(carrot-ryu `0e1bef52`, 부모 `fa75aeab`, 3개 파일 +5/-49). 실차 검증: 미실시. 실차 배포 시점은 사용자 확인 후.

## 117차 -- 2차 배치 (C10/C15 VW MEB)

- 대상 커밋 기준: carrot-ryu `62ae74dc`. 삭제 7개 파일(drive_helpers.py, cruise.py, controlsd.py, longitudinal_planner.py, steer_ratio.py, test_steer_ratio.py, test_controlsd.py). 후보 표에 적힌 5개 파일 외에 test_steer_ratio.py(`is_vw_meb` 인자 전달 4곳)와 삭제 후 고아가 된 `atc_turn_speed`(controlsd.py)가 추가로 확인돼 함께 정리했다.
- 유지: opendbc_repo의 VW 코드, `car.capnp`의 HUD 필드(스키마). 검증과 동작 변화 없음 근거는 WIP.md 117차 참고. 실차 검증: 미실시.
- 상태: 코드 스크립트 `117cha_vw_meb_dead_code_v2.ps1` 실행·push 완료 확인(carrot-ryu `22b101f6`, 부모 `62ae74dc`, 7개 파일 +9/-153). v1은 CRLF checkout 때문에 치환 전 안전 중단(WIP.md 117차 참고). 실차 검증: 미실시. 실차 배포 시점은 사용자 확인 후.

## 118차 -- 3차 배치 (web_upload.py/upload.py 구 웹 업로드 경로)

- 대상 커밋 기준: carrot-ryu `22b101f6`(117차 HEAD). 변경 3개 파일(web_upload.py, server/features/dashcam/upload.py, server/tests/test_web_upload.py).
- 배경: 16차(Google Drive 전환)에서 `run_upload_segments()`가 세그먼트별 개별 HTTP PUT 방식(Carrot/Toss 서버)에서 zip 단일 파일 `gdrive_upload.upload_file_resumable()` 방식으로 바뀌었으나, 옛 경로의 함수들이 삭제되지 않고 남아 있었다(docstring에는 "[15차->16차 전환]"으로 대체됐다고 적혀 있었음).
- web_upload.py: `create_web_upload_session()`/`create_web_upload_session_sync()`, `upload_folder_to_web()`, `send_web_upload_complete()`, `check_web_upload_health()`, `tmux_web_target()`, `_session_payload()`/`_session_token()`, `api_url()` 삭제. `api_url()`은 채팅 초안의 최초 후보 목록에는 "생존"으로 잘못 분류돼 있었으나, 위 함수들이 모두 사라지면 유일한 호출자가 없어져 함께 고아가 됨을 재검증 중 확인해 배치에 포함시켰다.
- server/features/dashcam/upload.py: `resolve_upload_target()`, `upload_target_settings()` 삭제(완전 고아, 테스트도 없었음). 이 둘만 쓰던 `selected_upload_settings` import와 `read_web_settings` import도 함께 정리.
- 테스트: server/tests/test_web_upload.py에서 위 심볼을 참조하던 테스트 함수 17개와 `FakeResponse`/`FakeRequestContext`/`FakeSession` 헬퍼 클래스 삭제(채팅 초안은 11개로 추산했으나 함수 단위로 다시 세어 17개로 정정, `api_url` 전용 테스트 1개 포함). 삭제 대상 사이에 끼어 있던 무관한 catalog 테스트(`test_dashcam_upload_summary_*` 3개)는 그대로 유지.
- 유지(생존 확인): `carrot_logs_web_target()`/`post_tmux_web()`/`selected_upload_settings()`/`web_upload_settings()`/`toss_upload_settings()`는 carrot_man.py(로그탭 업로드, 별개 기능)에서 실제로 사용 중.
- 검증 방법: carrot-ryu `22b101f6`을 codeload tarball로 받아 후보 심볼마다 저장소 전체 grep으로 참조 0건 확정(11절). py_compile 3파일 통과. pytest 자체 실행은 샌드박스에 conftest.py/컴파일 의존성이 없어 미실시(정적 grep 근거만). 실차 검증: 미실시.
- 상태: 코드 스크립트 `118cha_web_upload_dead_code_code_carrot_ryu-v1.ps1` 실행·push 완료 확인(carrot-ryu `df7da7d5`, 부모 `22b101f6`, 3개 파일 +5/-814). 실차 검증: 미실시. 실차 배포 시점은 사용자 확인 후.
