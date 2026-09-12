# FINDINGS

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
