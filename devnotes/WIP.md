# WIP

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
