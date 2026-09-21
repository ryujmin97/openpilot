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
| 신규(120차) A그룹 완전 고아: `live_runtime`(broker/contract/normalize/snapshot) + `carrot_man.py`/`carrot_serv.py` + dashcam/services 헬퍼 | def 29개(broker.py의 msgpack 인코딩 경로/`hello_*`/`debug_stats`, `build_live_hello`, `safe_chain`/`pick_first`, `calculate_angle`/`receive_*`, `_update_system_time`, `segment_creation_key`/`service_fields`/`current_upload_metadata`/`has_running_job`/`is_known_action`/`get_device_network`/`run_cmd_debug`/`_clear_drive_content_catalog_cache`/`finish_job`/`last_map_at` 등) | 30개 이름 모두 저장소 전체 참조 0곳(삭제 후 재확인) | 제거 완료(120차, carrot-ryu `b98620e8`, 부모 `df7da7d5`, 17개 파일 +1/-302, 실차 검증 미실시) |
| 신규(121차) B그룹: `desire_lib/blinker_manager.py` 파일 통째 + 고아 def 6개 | `blinker_manager.py`(106줄), `lane_planner_2.py`(`max_abs`/`calculate_plan_yaw_and_yaw_rate`), `model_selector/jobs.py`(`list_recent`), `model_selector/manifest.py`(`onnx_filenames`), `radar_motion/predictor.py`(`path_exit_probability`/`_radar_path`) | 7개 이름(`blinker_manager` 포함) 모두 저장소 전체 참조 0곳(코드 스크립트 7단계 `git grep`으로 삭제 후 재확인) | 제거 완료(121차, carrot-ryu `2efdd2e2`, 부모 `b98620e8`, 5개 파일 +0/-167, 실차 검증 미실시) |

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

## 119차 -- 4차 배치 후보 조사 (A/B/C 그룹, 삭제 전 조사 단계)

- 대상 커밋 기준: carrot-ryu `df7da7d5`(118차 HEAD, 이번 세션은 코드 변경 없음).
- 방법: first-party 범위(selfdrive/carrot, controls/lib, carrot/model_selector, tools/carrot_route_vault) 정의를 AST로 추출하고, 코드/문자열/비-py 파일/테스트로 구분해 참조를 토큰 단위로 센 뒤, 죽은 함수에서만 호출되는 함수까지 연쇄로 추적. 최종 후보는 저장소 전체 `grep -w`로 재확인(11절).
- 후보 규모: def 52개(연쇄 8개 포함) + 파일 통째 1개(`controls/lib/desire_lib/blinker_manager.py`, 어디서도 import되지 않음). 22개 파일, 본문 합계 약 630줄.
- A그룹(완전 고아, 위험도 최저): `server/live_runtime/broker.py`(`_coerce_payload_bytes`/`_encode_transport_value`/`_encode_msgpack_payload`/`hello_meta`/`hello_payload_bytes`/`_encode_snapshot`/`_encode_payload`/`debug_stats`, 연쇄로 `_load_msgpack`/`msgpack` 전역/`last_payload_*` 속성/`contract.py`의 `build_live_hello`/`LIVE_ENCODING_MSGPACK`도 고아화), `server/live_runtime/normalize.py`(`safe_chain`/`pick_first`), `server/live_runtime/snapshot.py`(`_service_alive_map`/`_alive_subset`), `carrot_man.py`(`calculate_angle`/`receive_fixed_length_data`/`receive_double`/`receive_float`), `carrot_serv.py`(`_update_system_time`, 호출부 주석 처리됨), dashcam/services 잔여 헬퍼(`segment_creation_key`/`service_fields`/`current_upload_metadata`/`has_running_job`/`is_known_action`/`get_device_network`/`run_cmd_debug`/`_clear_drive_content_catalog_cache`/`finish_job`(gdrive_upload)/`last_map_at`).
- B그룹: `controls/lib/desire_lib/blinker_manager.py`(파일 통째), `controls/lib/lane_planner_2.py`(`max_abs`/`calculate_plan_yaw_and_yaw_rate`), `carrot/model_selector`(`jobs.py`의 `list_recent`, `manifest.py`의 `onnx_filenames`), `radar_motion/predictor.py`(`path_exit_probability`/`_radar_path`).
- C그룹(가장 큼, 약 300줄): `cluster/cluster_renderer.py`(`rectangles_overlap`/`label_rect_inside_bounds`/`render_to_file`/`_world_label_bounds`/`_draw_drive_status_box`/`_draw_follow_gap_status`/`_draw_follow_vehicle_icon`), `cluster/cluster_scene.py`(`lane_marking_segments_for_marking`/`dashed_centerline_segments`/`model_line_points_for_render`/`corner_radar_common_lateral_speed_mps`/`detected_vehicle_is_rear_corner_summary`/`radar_point_is_outside_road_edges`/`translate_vec3_x`/`translate_vehicle_box_x`/`translate_radar_marker_x`), `cluster/main.py`(`route_state_has_cutin`/`route_state_cutin_candidates`).
- 제외(오탐/보류): `apply_deadzone`(opendbc `gm/carcontroller.py`가 사용, 1차 스캔이 opendbc 제외 범위였던 탓에 오탐), `.vendor/` 외부 라이브러리, 프레임워크 오버라이드(`do_POST`/`do_DELETE`/`handle_starttag`), `_ingest_*`(동적 호출), 테스트에서만 참조되는 10개(보류, 특히 `_draw_navi_traffic_light_panel`은 `test_cluster_navi.py`의 회귀 가드), 고아 상수 67개/미사용 import 46개/참조 없는 params 키 10개(이번 배치 범위 아님).
- 검증(시험 삭제, 반영 아님): 52 def + `blinker_manager.py` 삭제 시험본이 22개 파일 모두 py_compile 통과, pyflakes 정의되지않은이름 경고 전후 동일(2건), 새 미사용 import 5건 발견(추가 정리 필요: `cluster_scene.py`의 `statistics.median`, `dashcam/upload.py`의 `HAS_PARAMS`/`Params`, `broker.py`의 `json`/`build_live_hello`). pytest 실패/에러 목록(36건) 삭제 전후 동일(통과 개수는 컴파일 의존성 부재로 비교 못함).
- 상태: 조사 완료, 삭제 미실시. 사용자가 A → B → C 순서로 배치별 승인 후 진행하기로 결정(119차, WIP.md 참고). 각 배치 삭제 직전 11절(codeload tarball 재확인)을 다시 수행한다.

## 120차 -- 4차 배치 A그룹 삭제 스크립트 (조사는 119차 참고)

- 대상 커밋 기준: carrot-ryu `df7da7d5`(118차 HEAD). 변경 17개 파일, def 29개 삭제, 순 +1/-302줄. 삭제 내용은 WIP.md 120차 참고.
- 119차 조사 대비 확정 사항: 119차 A그룹 목록의 연쇄 항목(`_load_msgpack`/`msgpack` 전역, `last_payload_*` 속성, `contract.py`의 `build_live_hello`/`LIVE_ENCODING_MSGPACK`)까지 포함해 삭제한다. 삭제로 미사용이 되는 import는 `broker.py`(`json`/`importlib`/`LIVE_ENCODING_MSGPACK`/`build_live_hello`), `contract.py`(`typing.Iterable`), `live_runtime/__init__.py`(재수출 2개), `dashcam/upload.py`(`HAS_PARAMS`/`Params`)를 함께 정리했다. 연쇄 고아 후보(`_prune_jobs`, `_touch_job`, `route_creation_key`, `_update_alive_map`)는 다른 호출부가 남아 유지.
- 검증: tarball blob이 GitHub blob과 일치, `py_compile` 17개 통과, pyflakes 경고 원본과 동일(19건, 신규 0), 삭제 대상 30개 이름 잔여 참조 0건, pytest(`--noconftest`) 삭제 전/후 863 passed/11 failed/25 collection errors로 실패 목록 동일. 실차 검증: 미실시.
- 상태: 코드 스크립트 `120cha_deadcode_batchA_code_carrot_ryu-v1.ps1` 실행·push 완료 확인(carrot-ryu `b98620e8`, 부모 `df7da7d5`, 17개 파일 +1/-302, 각 파일 결과 blob이 스크립트 `Post` 값과 일치). 실차 검증: 미실시. 실차 배포 시점은 사용자 확인 후. B그룹은 착수 전 11절(codeload tarball 재확인)을 다시 수행한다.

## 121차 -- 4차 배치 B그룹 삭제 (조사는 119차 참고)

- 대상 커밋 기준: carrot-ryu `b98620e8`(120차 A그룹 HEAD). 변경 5개 파일(`blinker_manager.py` 삭제, `lane_planner_2.py`/`jobs.py`/`manifest.py`/`predictor.py` 편집), 순 +0/-167줄. 삭제 내용은 WIP.md 121차 참고.
- 119차 조사 대비: 범위 변화 없음. `blinker_manager.py`는 파일 통째라 코드 스크립트가 Replace-Block이 아니라 `git rm`을 쓰고, `py_compile`은 편집한 4개 파일에만 적용했다.
- 검증: 삭제 후 7개 이름 잔여 참조 0건(`git grep`, 사용자 PC 실행 로그 7단계), `py_compile` 4개 통과(Windows PowerShell 5.1, `py -3`), 4개 파일의 사전/사후 blob이 스크립트 `Pre`/`Post`와 일치(push 후 GitHub 재조회로도 확인). 테스트 통과 수치(388 passed, 10 passed)는 앞 세션 채팅 사본에 적힌 것으로 이 세션에서 재현하지 않았다. 실차 검증: 미실시.
- 사고: 코드 스크립트 v1은 Windows CRLF checkout 때문에 3단계에서 안전 중단(commit/push 없음, 핵심 발견 48). v2(`121cha_deadcode_batchB_code_carrot_ryu-v2.ps1`)로 실행·push 완료.
- 상태: 코드 스크립트 v2 실행·push 완료 확인(carrot-ryu `2efdd2e2`, 부모 `b98620e8`, 5개 파일 +0/-167, 4개 파일 결과 blob이 스크립트 `Post` 값과 일치, `blinker_manager.py`는 HEAD에서 삭제 확인). 실차 검증: 미실시. 실차 배포 시점은 사용자 확인 후. C그룹은 착수 전 11절(codeload tarball 재확인, 대상 커밋 `2efdd2e2`)을 다시 수행한다.
