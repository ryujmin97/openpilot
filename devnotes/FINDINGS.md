# FINDINGS

## [2026-09-13] route(경로) 커브 감속 오검출 — 실주행 로그로 최초 확인 (고속도로 분기점 조기 과감속 후 원복)

### 배경
- 사용자가 실제 콤마 디바이스로 주행 중 채증한 로그(qcamera.ts/qlog.zst/rlog.zst, route
  000003fb--8470375f65--21) 업로드.
- 증상: 고속도로 거의 직선 구간에서 좌로 약간 굽은 분기점 접근 시, 미리감속이 과하게
  걸렸다가 다시 원복되는 느낌.

### 확인된 사실 (rlog 파싱 결과, pycapnp + carrot-wip 스키마로 직접 복호화)
- t=47.3s경 carrotMan.desiredSource가 "route"로 전환되며 desiredSpeed가 67km/h로 급락.
  이 시점 xDistToTurn(분기점까지 거리)은 아직 499m로, 실제 커브와는 거리가 먼 시점.
- 시스템이 실제로 aTarget 최대 -2.0m/s²까지 감속 명령을 걸어 vEgo가 약 12초간
  96km/h→69km/h로 실제 감소함 (carControl.actuators.accel까지 물리적으로 전달됨,
  표시용 아님).
- 운전자가 t=52.1~59.6s(약 7.5초) 동안 gasPressed=True로 가속페달 개입, 69~72km/h
  유지하며 시스템 감속에 저항.
- t=54.8~57.9s 사이 route/vturn 소스 자체가 재계산되어 desiredSpeed가 115~121km/h로
  회복됨 → 최초 67km/h 목표는 실제보다 훨씬 급한 커브로 오검출된 일시적 값이었음이
  로그상 확인됨.

### 원인 (기존 5차/5차계속 정적 분석과 연결)
- carrot_man.py의 carrot_navi_route()가 내비 폴리라인 3점(40m 간격) 곡률로
  route_speed를 산출하는데, curve_speed.py(비전 버전)에 있는 median 스파이크 제거
  필터가 없음(5차 계속 분석에서 이미 지적된 구조적 리스크).
- 고속도로 분기점 부근은 폴리라인 정점 밀도/기하가 국소적으로 흐트러지기 쉬운
  지점이라 이 3점 곡률 계산이 순간적으로 실제보다 훨씬 급한 커브로 오검출 →
  route_speed가 스파이크성으로 급락 → 차가 그 구간을 지나며 리샘플링 윈도우 이동 →
  오검출 해소 → desiredSpeed가 다시 정상 수준으로 복귀. 이게 "미리 과감속 후 원복"
  체감의 정체.
- ⚠ 이번 로그는 실제 route(경로) 폴리라인 좌표 자체를 갖고 있지 않아(carrotMan/
  carState 메시지만으로 재구성), 폴리라인 기하가 실제로 어떻게 틀어져 있었는지
  위성지도 등으로 직접 대조 확인하지는 못함. 메커니즘은 신호 패턴(거리/소스/속도
  궤적)으로 강하게 뒷받침되나 100% 확진은 아님.

### 결론
- 5차 계속 분석에서 "설계상 위험 요소로 존재한다"고 정적으로만 지적했던 route 감속
  오검출 리스크가, 이번 실주행 로그로 실제 발생을 최초로 확인함.
- 버그라기보다는 필터 부재로 인한 설계상 취약점의 실제 발현 사례.

### 대응 옵션 (미결정, 사용자 선택 필요)
1. 임시완화: TurnSpeedControlMode 2→1(비전만)로 낮춰 route 소스 비활성화
2. 근본수정: carrot_navi_route()에 median/스파이크 제거 필터 추가, 또는 프레임 간
   route_speed 하락률에 clamp 적용
3. 곡률 계산 샘플 간격(현재 40m) 확대로 노이즈 민감도 완화

### 실차 검증
- 실주행 로그(rlog) 1건으로 현상 자체는 확인됨. 다만 원인 메커니즘 중 "폴리라인 기하
  왜곡" 부분은 위성지도 등 외부 자료 대조까지는 하지 못했으므로 100% 확진은 아님.
  코드 수정/최종 조치는 아직 미실시.

### 분석 근거 파일 / 데이터
- 업로드 route: 000003fb--8470375f65--21 (qcamera.ts, qlog.zst, rlog.zst)
- 파싱 도구: pycapnp + carrot-wip(ajouatom/openpilot) cereal/log.capnp, custom.capnp 스키마
- openpilot/selfdrive/carrot/carrot_man.py (carrot_navi_route, calculate_curvature)
- openpilot/selfdrive/carrot/carrot_serv.py (update_navi, speed_n_sources)
- carrot-ryu HEAD: 02015190f58a4380a433ee0130e6374455dddc2e (변경 없음, 분석만 수행)

## [2026-09-12] minSteerSpeed 60km/h 제한 — SMDPS 장착 차량용 해제 토글 확인

### 배경
- CAR.HYUNDAI_GENESIS (제네시스 DH 2015-16 / G80 2017) 플랫폼 설정에
  minSteerSpeed=60km/h가 하드코딩되어 있음.
  (opendbc_repo/opendbc/car/hyundai/values.py, HYUNDAI_GENESIS 블록)
- 사용자 차량은 SMDPS(조향모터) 개조로 저속 조향 개입이 물리적으로 가능한 상태.

### 확인된 사실
- opendbc_repo/opendbc/car/interfaces.py (get_params 함수)에 다음 로직 존재:
  ```
  if Params().get_bool("DisableMinSteerSpeed"):
      ret.minSteerSpeed = 0.
  ```
- 이 Params 키는 carrot-wip 자체에 이미 구현된 기능이며, 콤마 디바이스 설정 UI에도
  노출되어 있음 (openpilot/selfdrive/carrot_settings.json, 1877번째 줄 부근):
  - name: DisableMinSteerSpeed
  - title(한글): "저속조향제한해제"
  - descr: "저속조향이 안되는 차량 제한해제(SMDPS장착차량): 1"
  - 값 범위: 0(기본, 끔) ~ 1(켬)
- params_keys.h에도 PERSISTENT INT 파라미터로 등록되어 있어 재부팅 후에도 유지됨.

### 결론
- 코드 수정 불필요. 콤마 디바이스 설정에서
  "시작(START)" 그룹 → "저속조향제한해제"를 1로 설정하면
  minSteerSpeed가 런타임에 0으로 강제되어 저속 조향 제한이 해제됨.
- carrot-ryu는 carrot-wip과 동일한 상태이므로 이 기능을 그대로 사용 가능.

### 실차 검증
- 미실시. 콤마 디바이스 설정 변경 후 실제 저속 구간(60km/h 이하)에서
  조향 개입 여부와 안정성을 직접 확인 필요.

### 분석 근거 커밋
- carrot-wip HEAD: bb0e18bb8c09422fcd50dcf25c17e0d5c75072b1 (2026-09-12)

## [2026-09-12] 종방향 PID 게인(LongTuningKpV/KiV/Kf)이 현대·기아·제네시스에서 고정됨 — 설정값은 실제로 미적용

### 배경
- PARAMS_REGISTRY.md에 기록된 사용자 현재값: LongTuningKpV=100, LongTuningKiV=0, LongTuningKf=100
  (스케일 적용 시 Kp=1.0, Ki=0.0, Kf=1.0)
- "종방향 제어(가감속) 로직 분석" 요청에 따라 openpilot/selfdrive/controls/lib/longcontrol.py 확인.

### 확인된 사실
- carrot-wip 커밋 a26b108d "safety: fix Hyundai longitudinal PID gains" (2026-09-04, ajouatom)에서
  현대/기아/제네시스(opendbc brand == "hyundai") 차량은 PID 게인을 다음처럼 코드에 고정함:
  - HYUNDAI_LONGITUDINAL_KP = 1.0
  - HYUNDAI_LONGITUDINAL_KI = 0.0
  - HYUNDAI_LONGITUDINAL_KF = 1.0
- `LongControl.__init__`에서 `self.hyundai_fixed_longitudinal_tuning = CP.brand == "hyundai"`이면
  즉시 `_apply_hyundai_longitudinal_tuning()`으로 위 고정값을 self.pid에 적용.
- 주기 갱신 함수 `_refresh_longitudinal_tuning()`도 동일 분기라서, Params에 저장된
  LongTuningKpV/KiV/Kf 값을 아예 읽지 않고 무시함(Hyundai 계열 한정).
  → 즉, 콤마 디바이스 설정 화면에서 이 세 값을 바꿔도 제네시스 DH 2015 실차 제어에는 반영되지 않음.
- 같은 커밋에서 문서(docs/user/ko/cruise-gap.md, settings.md)와 UI 스키마
  (carrot/server/features·services/settings.py, carrot_settings.json)도 함께 갱신되어,
  현대·기아·제네시스에서는 이 3개 항목이 설정 화면에서 숨겨지도록 의도됨.
  → "31개 항목" → "전체 31개, 현대·기아·제네시스 28개"로 문서 수정된 것이 그 근거.
- 반면 `LongActuatorDelay`, `VEgoStopping`, `StoppingAccel`은 이 고정 로직과 무관하게
  계속 Params에서 읽어 실제로 적용됨 (longitudinal_planner.py, longcontrol.py 확인).
  - 사용자 현재값: LongActuatorDelay=20(→0.2s), VEgoStopping=5(→0.05m/s), StoppingAccel=-10(→-0.1m/s²)
  - 단, `LongControl.__init__`에는 `CP.brand=="hyundai"`이고 StoppingAccel==0.0일 때만
    -50(→-0.5)으로 강제 복원하는 별도 안전장치가 있음(e79bfd5d). 사용자 값이 -10이라 이 복원은 발동 안 함.

### 결론
- 이 동작은 버그가 아니라 carrot-wip 유지보수자가 의도적으로 반영한 안전 고정값이며,
  문서에도 명시되어 있음. carrot-ryu는 carrot-wip과 코드 동일하므로 그대로 적용됨.
- 사용자가 실제로 조절 가능한 종방향 "반응성/지연" 관련 노브는 현재
  LongActuatorDelay / VEgoStopping / StoppingAccel 뿐이며, PID 게인 자체는 조절 불가.
- 최종 액추에이터 클램프는 opendbc/car/hyundai/values.py의 CarControllerParams
  (ACCEL_MIN=-4.0, ACCEL_MAX=2.5 m/s²)로, 전 Hyundai 계열 공통이며 제네시스 전용 값은 없음.

### 실차 검증
- 미실시. 코드/문서 정적 분석 기준.

### 분석 근거 커밋
- a26b108d (2026-09-04, "safety: fix Hyundai longitudinal PID gains") — 이번 발견의 핵심 커밋
- e79bfd5d (StoppingAccel 0일 때 -0.5 복원 로직)
- carrot-wip/carrot-ryu HEAD: bb0e18bb8c09422fcd50dcf25c17e0d5c75072b1 (2026-09-12, 변경 없음)

## [2026-09-12] DisableDM=2 의미 확인 — 운전자 모니터링 완전 OFF + Carrot Vision WebRTC 활성화

### 배경
- PARAMS_REGISTRY.md에 DisableDM=2가 기본값(0)이 아닌 채로 확인되었으나 의미 미확인 상태였음.

### 확인된 사실 (openpilot/selfdrive/carrot_settings.json 설명 문구 기준)
- descr: "1.DisableDM, 2: +EnableWebRTC, reboot required"
- 즉 값의 의미: 0=기본(DM 켜짐), 1=DM 비활성화만, 2=DM 비활성화 + Carrot Vision(WebRTC 원격 스트리밍) 활성화(재부팅 필요)

### 코드 레벨 동작 (DisableDM=1과 2 공통, DM 비활성화 부분)
- system/manager/process_config.py `enable_dm()`: `DisableDM == 0`일 때만 dmonitoringd(운전자 카메라 모니터링 프로세스) 실행
  → 1이든 2든 운전자 모니터링 프로세스 자체가 아예 뜨지 않음.
- selfdrive/selfdrived/selfdrived.py 245행: `DisableDM == 0`일 때만 졸음/주의분산 lockout, 경고(driverDistracted1~3 등) 로직 수행
  → 1/2에서는 이 안전 경고·개입 잠금 로직이 전부 스킵됨.
- selfdrive/controls/controlsd.py 426행: `DisableDM == 0`일 때만 AlertLevel.three(3단계 경고) 시 forceDecel(강제 감속) 적용
  → 1/2에서는 운전자 부주의로 인한 강제 감속도 발생하지 않음.

### DisableDM=2 전용 동작 (WebRTC)
- system/manager/process_config.py `enable_webrtc()`: `DisableDM == 2 and not ClusterHud`일 때
  carrot_vision_encoderd(도로 카메라 WebRTC 인코더) 프로세스가 활성화됨 (Carrot Vision 원격 시청 기능).
- ClusterHud==1이면(계기판 클러스터가 로드 카메라를 직접 사용 중) 충돌 방지를 위해 WebRTC는 비활성화됨.

### 결론
- 사용자의 DisableDM=2 설정은 "운전자 모니터링(졸음/주의분산 감지, 관련 경고·강제감속)을 완전히 끄고,
  대신 Carrot Vision을 통한 원격 화면 시청 기능을 켠 상태"를 의미함.
- 이는 안전과 직결되는 설정이며, 사용자가 의도적으로 설정한 것인지(예: DM 카메라 미장착/오작동, 또는
  의도적 비활성화) carrot-wip 자체의 결함은 아니고 사용자 선택의 문제임.
- carrot/server/features/intro/presets.py의 3개 기본 프리셋은 모두 `DisableDM: 0`(DM 켜짐)을 기본값으로
  두고 있어, 현재 값(2)은 사용자가 프리셋에서 벗어나 직접 변경한 상태로 보임.

### 실차 검증
- 미실시. 코드/설정 문구 기준 정적 분석. 사용자에게 이 설정이 의도된 것인지 확인 필요.

## [2026-09-12] LateralTorqueCustom=0 확인 — 저장된 LateralTorque* 값은 미적용, 실제로는 기본 튜닝 사용 중

### 배경
- PARAMS_REGISTRY.md에 LateralTorqueKf=100, Friction=30, AccelFactor=2500, KiV=10, KpV=100, Kd=0이
  기록되어 있었으나 LateralTorqueCustom=0이라 "비활성 상태로 보임"이라는 잠정 메모만 있었음.

### 확인된 사실 (openpilot/selfdrive/controls/lib/latcontrol_torque.py)
- `update()`에서 매 10프레임마다 `LateralTorqueCustom` 값을 확인:
  - `> 0`이면 저장된 LateralTorqueKpV/KiV/Kf/Kd/AccelFactor/Friction 값을 읽어 PID와 torque_params에 적용.
  - `== 0`(현재 상태)이면 이 분기를 타지 않으므로 저장된 LateralTorque* 값은 전혀 읽히지도, 적용되지도 않음.
  - (0으로 막 전환된 프레임에서 1회 한정으로 기본값 복원 로직은 있으나, 이후에는 그냥 기존 기본값 유지)
- 실제 적용되는 기본 토크 튜닝은 `CarInterfaceBase.configure_torque_tune()`
  (opendbc_repo/opendbc/car/interfaces.py)이 `opendbc/car/torque_data/params.toml`에서
  차종별 실측 계수를 읽어 설정:
  - HYUNDAI_GENESIS 실측값: LAT_ACCEL_FACTOR=2.7807965280270794, FRICTION=0.0984484465421171
  - kp=1.0, kf=1.0, ki=0.1은 전 차종 공통 하드코딩값 (params.toml과 무관)
  - latAccelOffset=0.0 고정

### 결론
- 사용자가 저장해 둔 LateralTorqueKf=100 등 값은 "커스텀 토크 테이블을 쓰겠다"는 스위치
  (LateralTorqueCustom)를 켜지 않아 실제로는 전혀 사용되지 않고 있음.
- 현재 제네시스 DH 2015는 opendbc가 실측해 둔 기본 torque_data(LAT_ACCEL_FACTOR≈2.78, FRICTION≈0.098)로
  조향 토크가 계산되는 중.
- 이는 버그가 아니라 "커스텀 토크 끔" 상태의 정상 동작이며, 저장된 값 자체가 잘못된 것도 아님
  (켜기만 하면 그 값들이 그대로 적용됨). 사용자가 커스텀 토크 튜닝을 실제로 원한다면
  LateralTorqueCustom을 1 이상으로 바꿔야 함.

### 실차 검증
- 미실시. 코드 정적 분석 기준.

### 분석 근거 파일
- openpilot/selfdrive/selfdrived/selfdrived.py, openpilot/selfdrive/controls/controlsd.py,
  openpilot/system/manager/process_config.py, openpilot/selfdrive/carrot_settings.json (DisableDM)
- openpilot/selfdrive/controls/lib/latcontrol_torque.py, opendbc_repo/opendbc/car/interfaces.py,
  opendbc_repo/opendbc/car/torque_data/params.toml (LateralTorqueCustom)
- carrot-wip/carrot-ryu HEAD: bb0e18bb8c09422fcd50dcf25c17e0d5c75072b1 (2026-09-12, 변경 없음)

## [2026-09-12] route(경로) 기반 커브 감속 체인 확인 — 실제 감속 명령까지 연결됨, 이 차량은 활성화 상태

### 배경
- "route 감속 관련 코드 분석" 요청. carrot-serv.py의 speed_n_sources에 "route"라는
  소스 이름이 있는 것을 확인하고 그 전체 체인을 추적함.

### 확인된 사실 (호출 체인)
1. carrot_man.py: carrot_navi_route() — 외부 내비 앱이 보내준 경로 폴리라인(self.navi_points,
   최대 256포인트, carrotNavi 브리지로 수신)에서 현재 위치 기준 300m 구간을 5m 간격 리샘플링 →
   3점(40m 간격)으로 곡률 계산 → 곡률→속도 룩업테이블(V_CURVE_LOOKUP_BP/VALS) 적용 →
   autoNaviSpeedDecelRate로 역순 가속도 제한 감속 프로파일 생성 → route_speed 산출
2. carrot_serv.py: update_navi() — route_speed에 mapTurnSpeedFactor 곱하고
   autoCurveSpeedLowerLimit로 하한 적용. TurnSpeedControlMode가 2/3/4일 때만
   speed_n_sources에 ("route", route_speed) 추가. 다른 소스(과속카메라 sdi, 방지턱,
   스쿨존, 비전커브 vturn, 도로제한속도 road)와 함께 최솟값을 desiredSpeed로 선택 →
   carrotMan 메시지로 publish
3. carrot_functions.py: CarrotPlanner._update_carrot_man() (451행) —
   v_cruise_kph = min(v_cruise_kph, carrot_man.desiredSpeed)
4. longitudinal_planner.py (126~130행) — self.v_cruise_kph = carrot.update(sm, v_cruise_kph, mode) →
   v_cruise로 변환되어 LongitudinalMpc의 v_cruise 상한 파라미터로 전달 → MPC가 이 상한에 맞춰
   실제 가/감속 궤적(jerk 제한 포함)을 계산 → actuator로 전달
- controlsd.py의 hudControl.setSpeed는 이 체인과 별개의 표시 전용 값이며, 실제 감속은
  4번 체인(carrot.update → longitudinal_planner → MPC)을 통해 일어남.

### 활성화 전제조건 (모두 만족해야 발동)
- TurnSpeedControlMode = 2 이상 (0: 미사용, 1: 비전만, 2: 비전+경로(TBT, ±500m 이내만),
  3/4: 경로 항상). carrot_settings.json 상 기본값은 1(비전만)이라 route 소스 기본 비활성.
- MapTurnSpeedFactor 설명에 "APN 연결시에만"이라 명시 — 폰 내비 앱이 carrotNavi 브리지로
  경로 폴리라인을 실시간 전송해야 함(navi_points_active, navd_active).
- is_onroad, SHAPELY_AVAILABLE(shapely 라이브러리)도 필요. 하나라도 빠지면
  carrot_navi_route()가 (300, 무제한)을 반환해 사실상 미작동.

### 이 차량(제네시스 DH 2015)의 실제 설정 — 활성화 상태로 확인됨
- params_snapshots/2026-09-12_params_backup-4.json 확인 결과 TurnSpeedControlMode=2
  (기본값 1이 아님) → 이 차량은 route 감속이 켜져 있는 상태.
- MapTurnSpeedFactor=100(반영비율 100%), AutoCurveSpeedLowerLimit=20(하한 20km/h),
  AutoNaviSpeedDecelRate=60(0.60 m/s² 감속률)
- ⚠ DisableDM=2와 같은 패턴: "설정은 켜져 있는데 사용자가 의도한 것인지 아직 확인 안 됨".
  폰 내비 앱 연동(APN) 자체가 실제로 붙어있는지도 미확인.

### 잠재 리스크 (정적 분석 기준)
- 곡률을 GPS 폴리라인 좌표로만 계산 — 내비 앱이 주는 폴리라인의 점 밀도/정확도에
  전적으로 의존. curve_speed.py(비전 버전)에는 있는 3노드 median 스파이크 제거 필터가
  이 route 버전(carrot_navi_route)에는 없어, GPS 노이즈로 인한 곡률 오검출 가능성 있음.
- GPS 위치/heading(bearing) 오차가 gps_to_relative_xy 변환에 그대로 전파됨.

### 결론
- 코드 자체는 완결된 파이프라인이고 실제 감속 명령까지 이어지는 것은 확인됨. 다만
  "코드가 있다 = 실차에서 항상 안전하게 작동한다"는 아니며, 외부 내비 앱 연동 안정성과
  GPS 폴리라인 품질에 성패가 좌우됨.
- 버그로 보이는 부분은 없음(설계상 위험 요소는 존재).

### 실차 검증
- 미실시. 정적 코드/설정값 분석 기준.

### 분석 근거 파일
- openpilot/selfdrive/carrot/carrot_man.py (carrot_navi_route, calculate_curvature)
- openpilot/selfdrive/carrot/carrot_serv.py (update_navi, speed_n_sources)
- openpilot/selfdrive/carrot/carrot_functions.py (_update_carrot_man)
- openpilot/selfdrive/carrot/carrot_navi_control.py (parse_carrot_navi_control, NaviRouteControl)
- openpilot/selfdrive/controls/lib/longitudinal_planner.py (v_cruise_kph 계산부)
- openpilot/selfdrive/controls/controlsd.py (setSpeed, hudControl 표시부)
- openpilot/selfdrive/carrot_settings.json (TurnSpeedControlMode, MapTurnSpeedFactor 설명)
- carrot-wip/carrot-ryu HEAD: bb0e18bb8c09422fcd50dcf25c17e0d5c75072b1 (변경 없음)

## [2026-09-12] T_FOLLOW/TFollowGap(차간거리) 체인 확인 — MPC 리드차 장애물 제약에 직접 반영됨

### 배경
- "종방향 코드 계속 분석" 요청으로 t_follow.py(22줄, 헬퍼 함수만 존재)에서 시작해
  실제 호출부(carrot_functions.py, long_mpc.py)까지 추적함.

### 확인된 사실 (계산 체인, carrot_functions.py)
1. _get_base_t_follow() — personality(aggressive/standard/relaxed/moreRelaxed) 4단계별
   TFollowGap1~4 값 선택. EnableSpeedTF<0이면 속도 구간별 보간으로 대체 가능(고정 브레이크포인트
   [0,30,60,90]/[0,40,80,120]/[0,50,100,150] 중 EnableSpeedTF값(-1/-2/-3)으로 선택)
2. _apply_speed_t_follow_scale() — EnableSpeedTF>0이면 저속에서 차간거리를 줄였다가
   고속으로 갈수록 원복(반대 방향 스케일링)
3. _apply_decel_hold_and_boost_t_follow() — 감속(a_ego≤-0.2) 중엔 여유거리를 즉시 늘리고
   (TFollowDecelBoost 비율, a_ego=-2.5일 때 최대 0.5초 추가), 해제 시엔 서서히만
   줄여(0.10×dt/frame) 널뛰기 방지
4. _clip_t_follow() — [0.3초, tf_max]로 클립. tf_max는 myTFollowFactor(주행모드)로 확장 가능
5. ramp_t_follow() — 거리를 늘리는 쪽만 램프(0.30 또는 0.60초/초, decel_extra 여부에 따라),
   줄이는 쪽은 즉시 반영
6. get_T_FOLLOW()에 leadAccelResponse>=4 레벨 예외 있음: 추적 중인 선행차가 양의 가속
   중이면(gap이 벌어지는 중) 속도기반 스케일을 건너뛰고 설정된 tf_base를 그대로 유지
   (gap이 벌어지는데 차간거리를 괜히 좁히지 않기 위함)
- long_mpc.py 421행: t_follow = carrot.get_T_FOLLOW(...) → desired_follow_distance() →
  MPC의 리드차 장애물 거리 제약(obstacle constraint)에 직접 반영 → 실제 추종거리/
  가감속 명령으로 이어짐 (route 감속과 마찬가지로 표시용이 아니라 실동작 경로).
- 상태 변수(_tf_decel_extra, _tf_base_last 등) 초기화 확인: __init__에서 안전하게
  초기화되어 있고 getattr fallback도 첫 프레임에서 크래시 나지 않음. 정적으로 버그
  발견되지 않음.

### 이 차량의 실제 설정값 (params_backup-4.json)
- TFollowGap1~4: 110/120/140/160 (1.10/1.20/1.40/1.60초) — openpilot 표준 범위 내, 이상 없음
- EnableSpeedTF: 0 → 속도기반 보정 미사용, personality 고정값만 사용 중
- LeadAccelResponse: 0 → 레벨4-5 예외(선행차 가속중 설정값 유지) 비활성 상태
- DynamicTFollowLC: 100(=1.0) → 차선변경시 차간거리 배율 변화 없음
- TFollowDecelBoost: 10(=0.10) → 감속시 여유거리 보정 약하게(최대 0.05초)
- (PARAMS_REGISTRY.md의 기존 "TFollowGap5 미확인" 메모는 정정: 코드상 TFollowGap1~4까지만
  존재하며 5번째 항목은 없음)

### 결론
- T_FOLLOW 체인은 정적으로 문제없이 설계되어 있고, 실제 추종거리 제어에 반영됨.
- 이 차량은 속도기반 보정(EnableSpeedTF)과 레벨4-5 예외(LeadAccelResponse)를 모두 끈
  "가장 단순한" personality 고정값 모드로 운용 중 — 의도적 설정인지, 아니면 시험해보지
  않은 기본값인지는 사용자 확인 필요.

### 실차 검증
- 미실시. 정적 코드/설정값 분석 기준.

### 분석 근거 파일
- openpilot/selfdrive/carrot/t_follow.py
- openpilot/selfdrive/carrot/carrot_functions.py (_get_base_t_follow ~ get_T_FOLLOW, 189~328행)
- openpilot/selfdrive/controls/lib/longitudinal_mpc_lib/long_mpc.py (t_follow 사용부, 405~470행)
- openpilot/selfdrive/carrot_settings.json (TFollowGap1~4 설명/범위)
- carrot-wip/carrot-ryu HEAD: bb0e18bb8c09422fcd50dcf25c17e0d5c75072b1 (변경 없음)

## [2026-09-12] traffic_stop.py(E2E 정지신호 감속) 체인 확인 — 순수 비전모델 휴리스틱, HD맵/신호색상 인식 없음

### 배경
- 종방향 분석 계속 진행: t_follow.py 다음으로 traffic_stop.py(정지선/신호 감속) 추적.

### 확인된 사실 (호출 체인)
- carrot_functions.py: check_model_stopping() — 주행모델이 예측한 미래 경로(x,y,v)만으로
  정지신호 여부 추론. 속도구간별 다른 임계값(1km/h 미만: model_x<20&&model_v<10 /
  82km/h 미만: model_x<d_rel-3, 속도별 거리상한 120~150m, model_v<3 or <v[0]*0.7, |y[-1]|<5m /
  82km/h 이상: 감지 안 함). stopSignCount/startSignCount 프레임 누적으로 trafficState(red/green/off) 결정
- XState 상태머신(e2eCruise→e2ePrepare→e2eStop→e2eStopped) — 가스/브레이크, 레이더 리드,
  trafficState에 따라 전이. is_traffic_stop_entry_allowed()로 조향각 50도 이상(회전 중)이면
  새 정지 진입 억제
- actual_stop_distance: 속도 높을수록 먼 거리 추정치를 np.interp로 깎아 보정. 빨간불 지속시
  comfort_brake를 매 프레임 0.9배씩 부드럽게 조임
- TrafficStopModelLeadMatcher(traffic_stop.py): 정차 상태에서 레이더 리드가 없을 때 모델이
  본 정차 선두차량 위치를 5프레임 연속(확률≥0.90, 거리 4~80m, 정지선과 gap 0~3m, 속도≤2m/s,
  x/y/v 표준편차 임계값 이내) 검증 후에만 obstacle로 확정 — median 필터 + confirm frame으로
  방어적으로 설계됨
- long_mpc.py(469~475행): get_traffic_stop_distance_adjust()/get_traffic_stop_obstacle_distance()로
  stop_x를 MPC obstacle(x2)로 변환, x_obstacles에 포함되어 acados MPC가 실제 감속 궤적 계산.
  50m~순항거리 구간에서 신호 obstacle을 점진적으로 노출해 급제동 방지하는 스무딩 포함

### 이 차량의 실제 설정
- TrafficLightDetectMode=2 (기본값, "정지+출발 모두 감지" — 별도 조작 없이 이미 실도로에서
  작동 중이었을 가능성 높음)
- StopDistanceCarrot=700 (7.00m), TrafficStopDistanceAdjust=0 (코드 초기값 2.5m을
  사용자가 0으로 재설정)

### 결론
- 실제 MPC까지 연결되는 진짜 감속 경로이고 방어 로직(median 필터, confirm frame, isfinite,
  std 임계값)도 탄탄함.
- 구조적 리스크: HD맵/신호등 색상 인식이 전혀 없는 순수 E2E 휴리스틱이라 주행모델의 예측
  정확도에 전적으로 의존. 회전교차로, 임시신호, 공사구간 등 모델이 학습 못한 상황에서
  놓치거나 오검출할 수 있음(버그가 아니라 이 접근 방식 자체의 근본적 한계).

### 실차 검증
- 미실시. 정적 코드/설정값 분석 기준.

### 분석 근거 파일
- openpilot/selfdrive/carrot/traffic_stop.py (TrafficStopModelLeadMatcher, get_traffic_stop_*)
- openpilot/selfdrive/carrot/carrot_functions.py (check_model_stopping, XState 상태머신, 340~680행)
- openpilot/selfdrive/controls/lib/longitudinal_mpc_lib/long_mpc.py (440~490행, x2 obstacle 반영부)
- openpilot/selfdrive/carrot_settings.json (TrafficLightDetectMode 설명)
- carrot-wip/carrot-ryu HEAD: bb0e18bb8c09422fcd50dcf25c17e0d5c75072b1 (변경 없음)

## [2026-09-12] curve_speed.py(비전 커브 감속) 확인 — 물리식 기반, 외부 의존성 없어 route 버전보다 견고

### 배경
- 종방향 분석 계속: curve_speed.py(비전 버전) 및 route 버전과의 차이 비교.

### 확인된 사실
- carrot_man.py: carrot_curve_speed() → vturn_speed() → curve_speed.py의 curve_speed() 함수 호출.
  입력은 sm['modelV2'](주행모델 예측 경로/속도/각속도)와 carState.vEgo/aEgo/vCluRatio 뿐 —
  외부 내비 앱(APN) 연동 불필요, 항상 동작 가능.
- curve_speed() 계산: 곡률=yaw_rate/velocity를 경로 각 지점에서 계산 → 3점 median 필터로
  순간 yaw 스파이크 제거(route 버전엔 없는 필터) → curve_ms=sqrt(횡가속도_예산/곡률)
  (원운동 물리공식, 룩업테이블 아님) → 감속 반응시간(액추에이터 지연 1.0초+저크 해소시간)과
  감속도(1.0 m/s²)를 감안한 거리기반 역산으로 approach_ms 산출 → 최대 180m(or v_ego*6s)
  전방 중 가장 타이트한 제약(최솟값) 선택
- VisionCurveSpeed.update(): 속도를 줄이는 쪽은 즉시 반영, 늘리는(제약 해제) 쪽은
  0.35초 대기 후 초당 7.2km/h로만 서서히 반영 — 커브 탈출 시 급가속 방지
- vturn_speed는 carrot_serv.py의 speed_n_sources에 "vturn" 소스로 포함되어 route/sdi 등과
  함께 desiredSpeed 최솟값 계산에 참여(5차 route 감속 체인 항목 참고)

### 이 차량의 실제 설정
- AutoCurveSpeedFactor=80 (기본 100%보다 낮음. 설정 설명상 "값을 높이면 허용 횡가속도가
  낮아져 목표속도가 낮아짐" → 80%는 기본보다 느슨하게, 즉 커브를 더 빠른 속도로
  통과하도록 설정된 상태). AutoCurveSpeedLowerLimit=20 (route 버전과 공유)

### route(경로) 버전과 비교
| 항목 | route(경로) | curve_speed(비전) |
|---|---|---|
| 데이터 소스 | 폰 내비 앱 GPS 폴리라인 | 주행모델 예측 경로만 |
| 외부 의존성 | APN 연결 필수 | 없음(항상 동작) |
| 스파이크 필터 | 없음 | 3노드 median 있음 |
| 신뢰도(정적 분석 기준) | 내비 앱 연동 상태에 좌우 | 상대적으로 견고 |

### 결론
- 물리식 기반으로 설계가 탄탄하고 외부 의존성이 없어 route 버전보다 작동 신뢰도가 높음.
- 다만 결국 주행모델이 예측한 미래 경로/yaw에 의존하므로, 모델의 원거리 커브 인지 정확도가
  이 기능 전체의 성패를 좌우함(E2E 모델 의존 시스템 공통 한계).

### 실차 검증
- 미실시. 정적 코드/설정값 분석 기준.

### 분석 근거 파일
- openpilot/selfdrive/carrot/curve_speed.py (curve_speed, VisionCurveSpeed)
- openpilot/selfdrive/carrot/carrot_man.py (carrot_curve_speed, vturn_speed)
- openpilot/selfdrive/carrot/carrot_serv.py (speed_n_sources "vturn" 항목, 5차 항목과 공유)
- openpilot/selfdrive/carrot_settings.json (AutoCurveSpeedFactor 설명)
- carrot-wip/carrot-ryu HEAD: bb0e18bb8c09422fcd50dcf25c17e0d5c75072b1 (변경 없음)

## [2026-09-12] longitudinal MPC 코스트 함수 확인 + 종방향 전체 체계 종합 — 종방향 코드 분석 1단계 마무리

### 배경
- 종방향 분석 마지막 항목: long_mpc.py의 코스트 함수(set_weights) 및 jerk_factor 연동 확인,
  이후 지금까지(4차~5차) 분석한 종방향 6개 축을 종합.

### 확인된 사실
- set_weights()는 stock openpilot의 acados 기반 MPC 프레임워크(gen_long_ocp) 그대로이며,
  carrot 고유 로직이 아님. 코스트 항목: X_EGO_OBSTACLE_COST, X_EGO_COST, V_EGO_COST,
  A_EGO_COST, a_change_cost(감가속 변화 억제), jerk_factor×J_EGO_COST(저크 억제).
  carrot은 이 프레임워크에 입력값(t_follow, v_cruise, stop_x, jerk_factor)만 주입하는 구조.
- jerk_factor는 carrot_functions.py에서 personality(4단계)/myDrivingMode에 연동되어
  0.5~1.0 사이로 결정 → 낮을수록 저크 비용↓ → 가감속 변화가 더 급격해짐(반응성↑ 승차감↓).
  이 차량은 EnableSpeedTF=0(else 분기)이라 personality=standard 기준
  myDrivingMode≠Safe면 jerk_factor=0.7.
- TFollowGap1~4(1.10/1.20/1.40/1.60초) 순서가 personality aggressive/standard/relaxed/
  moreRelaxed와 jerk_factor 배정(0.5/0.7/1.0/1.0)이 서로 일관되게 짝지어져 있음을 확인
  (설계 일관성 양호).

### 종방향 전체 체계 종합 (4차~5차 통합)
```
[LongControl PID] -- 현대차는 Kp=1.0/Ki=0.0/Kf=1.0 고정 (설정값 무시, 4차)
        |
[v_cruise 상한] <- min(route 감속, curve_speed 비전 감속, sdi카메라, 도로제한속도) -> carrotMan.desiredSpeed
        |
        v
[longitudinal MPC] <- t_follow(TFollowGap 체인) -> 리드차 obstacle
                   <- stop_dist(traffic_stop 체인) -> 정지선 obstacle(x2)
                   <- jerk_factor/a_change_cost -> 코스트 웨이트
        |
        v
   실제 가/감속 궤적(a_target) -> LongControl -> 액추에이터
```

### 결론 (종방향 코드 분석 1단계 마무리)
- route/vturn/T_FOLLOW/traffic_stop 4개 커스텀 입력 체인 모두 표시용이 아니라 실제로
  MPC까지 연결되어 물리적 가/감속 명령을 만들어내는 것을 코드 레벨에서 확인함.
- MPC 자체(acados 프레임워크)는 stock openpilot 그대로라 신뢰도가 높고, carrot의
  커스텀 입력 생성부도 전반적으로 방어적으로(isfinite, median 필터, confirm frame,
  클립/램프) 작성되어 있어 정적 분석 기준 버그는 발견되지 않음.
- 구조적 리스크 2가지: ①route 감속은 폰 내비 앱(APN) 연동 안정성에 좌우, ②traffic_stop은
  HD맵/신호색상 인식 없이 순수 E2E 모델 휴리스틱이라 모델 성능에 전적으로 의존.
- 실차 검증은 전혀 미실시. 지금까지 결론은 모두 정적 코드 분석 기준이며, 실제 동작 일치
  여부는 실차주행 로그로만 확인 가능 — 다음 단계(실차주행 → 로그분석)로 넘어가기로
  사용자와 합의됨.

### 실차 검증
- 미실시. 정적 코드/설정값 분석 기준. 다음 단계는 실차주행 후 로그분석.

### 분석 근거 파일
- openpilot/selfdrive/controls/lib/longitudinal_mpc_lib/long_mpc.py (get_jerk_factor,
  get_a_change_cost, set_weights, 60~343행)
- openpilot/selfdrive/carrot/carrot_functions.py (jerk_factor 결정부, 220~263행)
- carrot-wip/carrot-ryu HEAD: bb0e18bb8c09422fcd50dcf25c17e0d5c75072b1 (변경 없음)
