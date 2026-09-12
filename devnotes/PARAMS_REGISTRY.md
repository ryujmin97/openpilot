# PARAMS REGISTRY

## 현재 적용 파라미터 베이스라인 스냅샷
- 파일: devnotes/params_snapshots/2026-09-12_params_backup-4.json
- 출처: 사용자가 콤마 디바이스에서 export한 params_backup-4.json
- 기록일: 2026-09-12
- 차량 확인: CarSelected3 = "Hyundai Genesis 2015-16" (제네시스 DH 2015 일치 확인)

### 확인된 주요 커스텀 값 (기본값 아닌 것 위주)

**저속조향 (SMDPS 관련)**
- DisableMinSteerSpeed: 1  ← FINDINGS.md 2026-09-12 항목에서 확인한 설정, 실제 적용 중
- AlwaysLateral: 1
- CustomSteerMax: 409
- LatSuspendAngleDeg: 45

**조향 토크 튜닝 (LateralTorque*)**
- LateralTorqueKf: 100
- LateralTorqueFriction: 30
- LateralTorqueAccelFactor: 2500
- LateralTorqueKiV: 10
- LateralTorqueKpV: 100
- LateralTorqueKd: 0
- LateralTorqueCustom: 0 (커스텀 토크 테이블 자체는 비활성 상태로 보임 — 확인 필요)

**종방향(가감속) 튜닝**
- LongPitch: True
- LongActuatorDelay: 20
- LongTuningKpV: 100
- LongTuningKiV: 0
- LongTuningKf: 100
- StoppingAccel: -10
- VEgoStopping: 5
- SteerActuatorDelay: 0

**크루즈 속도/추종거리 프로파일**
- CruiseSpeed1~5: 50 / 70 / 90 / 100 / 120
- CruiseMaxVals0~6: 130 / 125 / 80 / 60 / 50 / 45 / 40
- TFollowGap1~5: 110 / 120 / 140 / 160 (Gap4 기준, Gap5 값 미포함 확인 필요)

**차량/카메라 인식 관련**
- HyundaiCameraSCC: 1
- CanfdHDA2: 0 (DH는 CAN 차량이므로 정상)
- IsLdwsCar: 0

**Driver Monitoring**
- DisableDM: 2  ← 기본값(0)이 아님. 의미와 근거는 아직 미확인 (다음 분석 대상 후보)

### 실차 검증
- 이 값들은 사용자가 실제로 디바이스에 적용해 사용 중인 값 (실주행 반영 상태로 추정).
- 다만 Claude가 직접 실차 검증한 것은 아니며, 사용자 제공 백업 파일 기준으로만 기록.

### TODO / 다음 분석 후보
- DisableDM=2의 정확한 의미와 왜 이 값으로 설정했는지 확인
- LateralTorqueCustom=0인데 LateralTorque* 값들이 커스텀되어 있는 이유 확인
  (커스텀 토크 테이블이 실제로 적용되는 조건 확인 필요)
