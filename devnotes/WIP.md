# WIP

## 10차 (완료 — 코드 수정) — RES/+ 인게이지 시 설정속도가 현재속도보다 낮아지는 문제 안전장치 추가

- 사용자 제보: 출발 후 가속 중(예: 약 50km/h) 핸들 +RES 버튼으로 크루즈 인게이지 시,
  설정속도가 현재속도보다 낮게(예: 약 30km/h) 잡혀 급감속이 발생하는 경우가 있다는
  실사용 증상 보고 (실주행 로그 없이 사용자 설명 기반, 아직 rlog로 재현 확인 전)
- 코드 확인(carrot-ryu 2dbe492 기준, selfdrive/car/cruise.py):
  - `_update_cruise_buttons()`의 accelCruise 인게이지 분기(`_cruise_ready or not
    CC.enabled or CS.cruiseState.standstill`)에서, `_v_cruise_kph_at_brake`(브레이크
    시점에 저장해두는 "재개용" 속도) 또는 아직 초기화되지 않은 v_cruise_kph 값이
    현재속도(v_ego_kph_set)보다 낮은 채로 그대로 인게이지 속도로 채택될 수 있는
    경로 존재
  - `_v_cruise_kph_at_brake`는 브레이크 재개 목적 외에 `_auto_speed_up()`의 도로제한
    속도 동기화 로직(`AutoRoadSpeedLimitOffset > 0`일 때, 매 프레임 CC.enabled 여부와
    무관하게 `nRoadLimitSpeed + offset`으로 덮어씀, 726번 줄 부근)에서도 값이 채워질
    수 있어, 최초 인게이지 시점에 도로제한속도 기반의 낮은 값이 남아있을 가능성 있음
    (단, `AutoRoadSpeedLimitOffset` 기본값은 -1이라 사용자가 이 옵션을 켠 경우에만
    해당 경로가 열림 - PARAMS_REGISTRY에 이 값 미기록이라 이 차량 설정은 미확인)
  - `SpeedFromPCM`이 1이 아닌 기본 설정(0 등)에서는 openpilot 자체 v_cruise_kph 로직이
    쓰이므로 위 경로가 실제로 영향을 줄 수 있음(1이면 순정 SCC 값을 그대로 씀 - 이
    경우 문제가 있다면 순정 ECU 쪽 이슈이므로 이번 코드수정 대상 아님)
- 수정: 최소 변경 원칙에 따라 인게이지 분기 마지막에 안전장치(floor)만 추가.
  계산된 인게이지 속도가 "현재속도 + ENGAGE_SPEED_MARGIN_KPH(2km/h)"보다 낮으면
  "현재속도 + 2km/h"로 올림. 브레이크 후 저장된 속도가 현재속도보다 높은 정상적인
  재개(예: 커브에서 감속 후 RES로 이전 설정속도로 복귀) 케이스는 그대로 유지됨
  (그 값이 floor보다 크므로 영향 없음)
- 검증:
  - 문법검증(py_compile) 통과
  - 기존 `test_carrot_cruise_buttons.py`의 인게이지 관련 테스트 4건
    (`test_accel_restores_at_least_brake_speed_while_cruise_is_off` 2건,
    `test_accel_keeps_initialized_speed_without_brake_snapshot_while_cruise_is_off`,
    "브레이크 후 더 높은 속도로 정상 재개" 신규 케이스)을 동일 로직으로 재현한
    standalone 합성 스크립트로 결과 일치 확인 (샌드박스에 cereal/capnp 빌드가 없어
    pytest 자체 실행은 9차와 동일하게 불가)
  - 사용자가 보고한 "50km/h 주행 중 RES → 30km/h로 급감속" 시나리오를 동일 로직으로
    재현 → 수정 후 52km/h(현재속도+2)로 인게이지됨을 합성 테스트로 확인
- 실차 검증: 미실시. 다음 세션/실주행에서 동일 상황(출발 가속 중 RES 인게이지) 재현
  시 급감속이 사라졌는지 확인 필요
- 관련 없는 리팩터링 없음, 파일 1개(cruise.py)만 수정, 12줄 추가


## 9차 (완료 — 코드 수정) — route 커브 오검출 근본수정: median 스파이크 필터 추가

- 8차에서 실주행 로그로 확인한 route 감속 오검출에 대해, 사용자가 근본수정(옵션 ②)
  선택
- carrot_man.py의 carrot_navi_route()를 수정: 3점 곡률을 먼저 전부 계산한 뒤,
  3-샘플 슬라이딩 median 필터를 적용하고 그 결과로만 목표속도 산출하도록 구조 변경
  (비전 커브 curve_speed.py에 이미 있던 median 필터 방식을 route 쪽에도 동일 적용)
- 최소 변경(함수 내 한 블록만 교체), Claude 샌드박스에서 GitHub 최신 코드로 미리
  패치 적용/문법검증/diff 검증 후 스크립트로 전달 → 사용자가 Termux에서 실행,
  carrot-ryu 브랜치에 반영 완료 (commit 0201519..2dbe492)
- 스크립트 실행 중 두 가지 이슈 발생 및 해결: ①heredoc 안 한글 텍스트가 Termux
  붙여넣기 과정에서 줄바꿈이 깨져 히어독이 안 닫힌 문제(재시도로 해결, 실제 반영
  안 된 상태에서 중단됐던 것 확인) ②git diff가 less 페이저를 띄우며 화면이 꼬여
  셸까지 깨진 문제(GIT_PAGER=cat, --no-pager diff --stat로 해결). 두 이슈 모두
  코드/devnotes에 실제 손상 없이 안전하게 재시도로 해결됨
- 합성 테스트로 필터가 단발성 곡률 스파이크를 제거하면서 정상 커브는 유지함을 확인
- 실차 검증: 미실시. 다음 실주행에서 동일 분기점 재통과 시 rlog로 재확인 필요

## 8차 (완료 — 실주행 로그 분석) — route 감속 오검출 최초 실증

- 사용자가 실제 콤마 디바이스 주행 로그(route 000003fb--8470375f65--21, rlog/qlog/
  qcamera)를 업로드. 증상: 고속도로 좌커브 분기점 접근 시 route기반 감속이 미리
  과하게 걸렸다가 다시 원복되는 느낌
- pycapnp + carrot-wip cereal 스키마로 rlog.zst를 직접 복호화하여 carrotMan/carState/
  carControl/longitudinalPlan 타임라인 재구성, 문제 구간(t=47~59s) 정밀 분석
- 확인: t=47.3s경 desiredSource="route"로 desiredSpeed가 67km/h로 급락(당시 분기점
  까지 아직 499m). 실제 감속 명령까지 이어져 vEgo 96→69km/h 하락. 운전자가 7.5초간
  가스 개입. 이후 t=54.8~57.9s에 route 소스가 115~121km/h로 자체 재계산되며 복귀
- 원인: carrot_navi_route()의 3점(40m) 곡률 계산에 스파이크 제거 필터가 없어, 분기점
  폴리라인 기하 국소 왜곡을 실제보다 급한 커브로 오검출한 것으로 추정(5차계속 정적
  분석에서 이미 지적된 리스크의 실제 발현). 다만 폴리라인 기하 자체는 직접 대조 못함
- FINDINGS.md에 상세 기록. 코드 수정은 아직 하지 않음(대응 옵션 3가지 제시, 사용자
  판단 대기)
- 실차 검증: 현상 자체는 실주행 로그로 확인. 원인 메커니즘 일부(폴리라인 기하)는
  미확진

## 7차 (완료 — 웹 UI 전환 마무리 + carrot-ms 동기화 점검) — 브랜치 정리 및 신규 커밋 없음 확인

- ryujmin97/openpilot에 실제로 남아있던 carrot-ms, carrot-wip 브랜치(각각
  happymaj11r/openpilot, ajouatom/openpilot의 완전한 복사본)를 사용자가 GitHub 웹 UI에서
  직접 삭제 완료. 이제 ryujmin97/openpilot에는 carrot-ryu, carrot-ryu-note 두 브랜치만
  존재하여 문서화된 브랜치 구성과 일치하는 상태로 정리됨 (지침 16절 항목 해소)
- carrot-ms(happymaj11r/openpilot) 신규 커밋 동기화 검토 진행: git ls-remote로 확인한 결과
  carrot-ryu HEAD와 carrot-ms HEAD가 정확히 일치(02015190f58a4380a433ee0130e6374455dddc2e)
  → 6차 세션 이후 carrot-ms에 새로운 rebase/커밋이 전혀 없음. 반영 대상 커밋 0건
- 참고로 carrot-wip(ajouatom/openpilot)은 HEAD가 bb0e18bb8c09422fcd50dcf25c17e0d5c75072b1로
  계속 진행 중이나, carrot-ms가 아직 이를 따라 rebase하지 않아 지침 2절 원칙대로 직접 비교
  대상으로 삼지 않음
- WIP_SYNC.md를 carrot-ms 기준 체크포인트 방식으로 갱신(이번 점검 결과 기록)
- 코드 변경 없음 (브랜치 정리 + 점검만 수행), carrot-ryu는 여전히 carrot-ms와 동일
- 실차 검증: 해당 없음 (인프라 점검 작업)

## 6차 (완료 — 베이스 브랜치 전환) — carrot-wip → carrot-ms 로 변경

- 사용자가 happymaj11r/openpilot 저장소의 carrot-ms 브랜치(콤마 주행모델 선택 기능,
  carrot-wip 기반으로 매번 재생성/rebase됨)를 확인 요청
- git merge-base로 확인한 결과 carrot-wip과 carrot-ms는 공통 조상 커밋이 없음(히스토리
  공유 안 함) — carrot-ms는 carrot-wip이 업데이트될 때마다 그 위에 모델선택 기능을 다시
  얹어 통째로 재작성(rebase/force-push)하는 방식으로 판단됨
- 전체 히스토리 비교 결과 carrot-wip에 없고 carrot-ms에만 있는 커밋 117개 확인.
  이 중 모델 셀렉터 관련 키워드로 필터링한 것 약 58개, 나머지 약 59개는 클러스터(계기판)
  HUD, PC 시뮬레이터 지원, 로그 업로드 서버(토스/당근) 선택 기능 등 이 프로젝트와 무관한
  기능으로 판단됨. 선별 이식(cherry-pick)은 다단계 작업이 될 것으로 예상됨
- 사용자 결정: 선별 이식 대신, carrot-ryu 브랜치 자체의 베이스를 carrot-wip에서
  carrot-ms로 전면 전환하기로 결정 (당시 carrot-ryu에 사용자 코드가 전혀 없어 안전하게
  가능한 시점이었음)
- 실행: carrot-ryu(origin) 브랜치 삭제 후 happymaj11r/carrot-ms 기준으로 재생성.
  carrot-ryu HEAD가 carrot-ms HEAD(02015190f58a4380a433ee0130e6374455dddc2e,
  "Recover evil-merge resolutions from carrot-wip PR #516 and PR #517")와 일치함을 확인
- carrot-ryu-note는 그대로 유지 (기존 종방향 분석 내용은 carrot-wip 기반 코드 분석이라
  carrot-ms에도 대부분 그대로 유효함 — 코드가 크게 갈라지지 않는 한 재분석 불필요)
- 프로젝트 지침 문서(PROJECT_INSTRUCTIONS)의 "베이스 브랜치" 항목을 carrot-wip →
  carrot-ms로 수정하는 문구를 사용자에게 전달함 (문서 자체는 저장소 밖에서 사용자가
  보관하는 것으로 파악되어 Claude가 직접 수정하지 않음)
- ⚠ 향후 영향: carrot-ms는 매번 히스토리가 재작성되므로, carrot-wip처럼 fast-forward
  동기화가 불가능함. carrot-ms가 업데이트될 때마다 carrot-ms와 carrot-wip의 커밋 메시지를
  비교해 "모델 셀렉터 관련 커밋"만 선별 반영하는 방식이 필요함 (2절 동기화 원칙의 확장 적용
  필요 — 다음 세션에서 WIP_SYNC.md 구조를 carrot-ms용으로도 확장할지 검토 필요)
- 코드 변경 없음 (브랜치 베이스 전환만 수행, carrot-ryu는 여전히 carrot-ms와 동일)
- 실차 검증: 해당 없음 (인프라 변경 작업)

## 5차 계속 (완료 — traffic_stop / curve_speed / MPC 코스트 함수 분석) — 종방향 코드 분석 1단계 마무리

- 같은 세션에서 이어서 traffic_stop.py(정지선/신호 감속) → curve_speed.py(비전 커브 감속) →
  longitudinal MPC 코스트 함수(set_weights, jerk_factor) 순으로 분석 진행
- traffic_stop.py: 주행모델 예측(x,y,v)만으로 정지신호 판단하는 순수 E2E 휴리스틱 확인.
  XState 상태머신, TrafficStopModelLeadMatcher(5프레임 confirm)까지 확인. HD맵/신호색상
  인식 없음 — 모델 성능 의존 리스크 있음. long_mpc.py의 x2 obstacle까지 실제 연결됨 확인.
  이 차량 설정: TrafficLightDetectMode=2(기본값, 이미 활성 상태)
- curve_speed.py(비전): route 버전과 달리 외부 내비 앱 불필요, 순수 modelV2 기반. 곡률=
  yaw_rate/velocity를 3점 median 필터링 후 물리공식(v=sqrt(횡가속도예산/곡률))으로 계산 —
  route 버전보다 견고함. 이 차량 AutoCurveSpeedFactor=80(기본보다 느슨하게 설정됨) 확인
- longitudinal MPC 코스트 함수: stock openpilot acados 프레임워크 그대로, carrot은 입력값만
  주입. jerk_factor가 personality/myDrivingMode에 연동(0.5~1.0)됨을 확인, TFollowGap
  선택과 일관되게 설계되어 있음을 확인
- 종방향 전체 체계(LongControl PID → v_cruise 상한 → MPC obstacle/코스트 → 액추에이터)
  종합 다이어그램으로 FINDINGS.md에 정리
- 종방향 코드 분석 1단계(4차~5차)를 여기서 마무리하기로 결정. 다음 단계는 실차주행 →
  route 로그 생성 → 로그분석
- FINDINGS.md, PARAMS_REGISTRY.md, LAST_ANALYZED.md, CURRENT_STATUS.md, HANDOFF.md 갱신
- 코드 변경 없음 (분석/기록만), carrot-ryu는 carrot-wip과 여전히 동일
- 실차 검증: 미실시

## 5차 (완료 — route 감속 체인 + T_FOLLOW/TFollowGap 체인 분석) — 종방향 감속 로직 계속

- 사용자 방향: "종방향 관련 코드부터 분석 → 실차주행 → 로그분석" 순서로 진행하기로 결정
- route(경로) 기반 커브 감속 체인 전체 추적:
  carrot_man.py(carrot_navi_route, GPS 폴리라인→곡률→속도) → carrot_serv.py(update_navi,
  speed_n_sources 최솟값 선택) → carrot_functions.py(_update_carrot_man, v_cruise_kph 갱신) →
  longitudinal_planner.py → MPC v_cruise 상한 → 실제 감속 명령까지 이어짐을 확인 (표시 전용이 아님)
- 활성화 전제조건 확인: TurnSpeedControlMode>=2 필요(기본값은 1=비전만), 폰 내비 앱의
  APN 연결로 경로 폴리라인 수신 필요, shapely 라이브러리 필요
- ⚠ 이 차량의 실제 저장값은 TurnSpeedControlMode=2로, route 감속이 켜져 있는 상태임을
  params_backup-4.json에서 확인 (DisableDM=2처럼 "설정은 켜져있는데 의도 미확인" 패턴)
- T_FOLLOW/TFollowGap(차간거리) 체인 전체 추적:
  t_follow.py(헬퍼) → carrot_functions.py(_get_base_t_follow ~ get_T_FOLLOW, personality별
  기본값/속도보정/감속시 여유거리 boost&hold/클립/램프) → long_mpc.py(t_follow →
  desired_follow_distance → MPC 리드차 장애물 제약)로 실제 추종거리 제어에 반영됨을 확인
- 이 차량은 EnableSpeedTF=0, LeadAccelResponse=0으로 가장 단순한 personality 고정값
  모드로 운용 중임을 확인 (TFollowGap1~4=110/120/140/160, 표준 범위 내 이상 없음)
- 정적 분석 기준 버그는 발견되지 않음(상태 변수 초기화, 클립/램프 로직 모두 안전하게 작성됨)
- FINDINGS.md, PARAMS_REGISTRY.md, LAST_ANALYZED.md 갱신
- 코드 변경 없음 (분석/기록만), carrot-ryu는 carrot-wip과 여전히 동일
- 실차 검증: 미실시

## 4차 계속 (완료 — DisableDM / LateralTorqueCustom 분석) — 보류했던 두 항목 확인

- 같은 세션에서 이어서 "DisableDM=2 / LateralTorqueCustom" 보류 항목 분석 진행
- DisableDM=2 확인: carrot_settings.json 설명("1.DisableDM, 2: +EnableWebRTC")과
  process_config.py/selfdrived.py/controlsd.py 코드로 의미 확정
  → 운전자 모니터링(졸음/주의분산 감지·경고·강제감속) 완전 OFF + Carrot Vision WebRTC 활성화
  → 안전 관련 설정이라 사용자에게 의도 여부 재확인 필요 (다음 세션 또는 지금 확인)
- LateralTorqueCustom=0 확인: latcontrol_torque.py 분기 구조상 0이면 저장된
  LateralTorqueKf/Friction/AccelFactor/KiV/KpV/Kd 값이 전혀 읽히지 않음.
  실제로는 opendbc torque_data/params.toml의 HYUNDAI_GENESIS 실측값
  (LAT_ACCEL_FACTOR≈2.7808, FRICTION≈0.0984)로 조향 토크 계산 중임을 확인
- FINDINGS.md, PARAMS_REGISTRY.md 갱신
- 코드 변경 없음 (분석/기록만)
- 실차 검증: 미실시

## 4차 (완료 — 종방향 PID 게인 고정 확인) — LongTuningKpV/KiV/Kf 무효화 발견

- 사용자 요청으로 "종방향 제어(가감속) 로직 분석" 착수
  (DisableDM=2 / LateralTorqueCustom 항목은 이번 세션에서 보류)
- longcontrol.py 분석 중, 커밋 a26b108d(2026-09-04)에서 현대·기아·제네시스 차량의
  종방향 PID 게인(Kp/Ki/Kf)이 코드에 고정(1.0/0.0/1.0)되어 있음을 확인
- 사용자가 보유한 LongTuningKpV=100/KiV=0/Kf=100 설정값은 제네시스 DH 2015에서
  실제로는 읽히지 않고 무시됨 (문서에도 명시된 의도된 동작, 버그 아님)
- 실제 적용되는 종방향 노브는 LongActuatorDelay / VEgoStopping / StoppingAccel 뿐임을 확인
- ACCEL_MIN/MAX(-4.0/2.5 m/s²)는 제네시스 전용 값 없이 Hyundai 계열 공통값임을 확인
- FINDINGS.md, PARAMS_REGISTRY.md, LAST_ANALYZED.md에 반영
- 코드 변경 없음 (분석/기록만), carrot-ryu는 carrot-wip과 여전히 동일
- 실차 검증: 미실시

## 3차 (완료 — 파라미터 베이스라인 기록) — 현재 적용 설정값 스냅샷

- 사용자가 콤마 디바이스에서 export한 params_backup-4.json 수령
- CarSelected3="Hyundai Genesis 2015-16"로 차량 매칭 확인
- DisableMinSteerSpeed=1이 실제로 적용되어 있음을 확인 (2차 FINDINGS와 일치)
- 원본 파일을 devnotes/params_snapshots/2026-09-12_params_backup-4.json으로 보관
- PARAMS_REGISTRY.md에 주요 커스텀 값(조향 토크, 종방향 튜닝, 크루즈 프로파일 등) 요약 기록
- DisableDM=2, LateralTorqueCustom=0 등 의미 미확인 항목을 다음 분석 후보로 등록
- 실차 검증: 해당 없음 (기록 작업)

## 2차 (완료 — 저속조향 제한 분석) — minSteerSpeed / SMDPS

- CAR.HYUNDAI_GENESIS minSteerSpeed=60km/h 하드코딩 확인
- DisableMinSteerSpeed Params 토글이 carrot-wip에 이미 구현되어 있음을 확인
  (interfaces.py + carrot_settings.json UI 노출)
- 코드 수정 없이 설정값 변경만으로 해결 가능 판단
- 실차 검증: 미실시

## 1차 (완료 — 브랜치 세팅) — 프로젝트 구조 초기화

- carrot-wip: 원본 참고 브랜치 확인
- carrot-ryu: carrot-wip에서 분기하여 생성
- carrot-ryu-note: orphan 브랜치로 생성, devnotes 폴더 구조 세팅
- 실차 검증: 미실시
