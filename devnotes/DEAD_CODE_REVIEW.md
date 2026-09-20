# DEAD CODE REVIEW

carrot-ryu의 dead code(호출/참조되지 않는 코드) 정리 추적 문서. 이어쌓기형: 새 배치는 표 아래에 회차 항목으로 추가하고, 기존 항목은 상태 칸만 갱신한다.

**원칙**: (1) 후보는 carrot-ryu 전체를 codeload tarball로 받아 심볼 단위 grep으로 참조 0건을 확정한 뒤에만 삭제한다(추측 금지, 11절). (2) 삭제 diff를 `py_compile`과 기존 테스트로 확인한다. (3) 사용자가 스크립트를 실행해 push하기 전에는 "제거 완료"로 쓰지 않는다. (4) 지침 10절 "최소 변경 원칙"과 방향이 반대(코드를 줄이는 이니셔티브)이므로 배치마다 사용자 승인을 받는다. (5) carrot-ms와의 차이가 늘어나는 점을 감안한다(20절 리셋 시 재이식 대상이 됨).

후보 번호(C01 등)는 ChatGPT 분석 세션에서 붙은 것이다. 그 분석의 전체 목록은 이 저장소에 없고, 아래는 Claude 세션에서 다시 검증한 후보만 적었다.

| 후보 | 위치 | repo 전체 참조 | 상태 |
|---|---|---|---|
| C01 `get_jerk_factor()` | long_mpc.py | 자기 파일의 주석 1곳뿐, 호출 0곳 | 1차 배치 삭제 스크립트 전달(115차, 실행 대기) |
| C12 `prev_accel_clip` | longitudinal_planner.py | 초기화 1곳 + 주석 블록뿐, 읽는 곳 0곳 | 1차 배치 삭제 스크립트 전달(115차, 실행 대기) |
| C16 `get_max_accel()` + `A_CRUISE_MAX_VALS/BP` | longitudinal_planner.py | 자기 파일의 주석 1곳뿐. `A_CRUISE_MAX_BP_CARROT`(carrot_functions.py)는 별개 상수 | 1차 배치 삭제 스크립트 전달(115차, 실행 대기) |
| C06 throttle/coast 계산부 | longitudinal_planner.py | 계산부는 `self.allow_throttle = True` 상수 때문에 실행되지 않음. 메시지 필드 `allowThrottle`은 UI 2곳과 클러스터 리플레이가 읽음 | 계산부만 1차 배치에서 삭제(필드와 `self.allow_throttle = True`는 유지). 스크립트 전달(115차, 실행 대기) |
| C10/C15 VW MEB(`is_volkswagen_meb`/`is_vw_meb`) | drive_helpers.py 정의 + cruise.py, controlsd.py, steer_ratio.py, longitudinal_planner.py, test_controlsd.py | 5개 파일에서 사용 중. `CP.brand == "volkswagen"`이 DH2015에서 항상 False라 각 분기는 죽은 경로이나 제거 범위가 큼 | 보류 -- 별도 세션 |

## 115차 -- 1차 배치 (C01 + C12 + C16 + C06 계산부)

- 대상 커밋 기준: carrot-ryu `fa75aeab`. 삭제 3개 파일(long_mpc.py, longitudinal_planner.py, test_turn_accel.py의 `parse_model` 목 반환값 5튜플 -> 4튜플).
- 검증과 동작 변화 없음 근거는 WIP.md 115차 참고. 실차 검증: 미실시.
- 상태: 코드 스크립트 `115cha_deadcode_batch1_code_carrot_ryu-v1.ps1` 전달, 사용자 실행 대기.
