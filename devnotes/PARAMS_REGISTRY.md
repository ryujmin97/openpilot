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
- LateralTorqueKf: 100    ⚠ LateralTorqueCustom=0이라 미적용 (FINDINGS 2026-09-12 참고)
- LateralTorqueFriction: 30   ⚠ 위와 동일, 미적용
- LateralTorqueAccelFactor: 2500   ⚠ 위와 동일, 미적용
- LateralTorqueKiV: 10   ⚠ 위와 동일, 미적용
- LateralTorqueKpV: 100   ⚠ 위와 동일, 미적용
- LateralTorqueKd: 0   ⚠ 위와 동일, 미적용
- LateralTorqueCustom: 0 (확인됨: 이 값이 0이면 위 6개 값은 전혀 읽히지 않음.
  실제로는 opendbc torque_data/params.toml의 HYUNDAI_GENESIS 실측값
  LAT_ACCEL_FACTOR≈2.7808, FRICTION≈0.0984로 조향 토크가 계산됨)

**종방향(가감속) 튜닝**
- LongPitch: True
- LongActuatorDelay: 20 ← 실제 적용됨 (longitudinal_planner.py)
- LongTuningKpV: 100  ⚠ 현대·기아·제네시스는 코드에서 고정(Kp=1.0)되어 이 값 무시됨 (FINDINGS 2026-09-12 참고)
- LongTuningKiV: 0    ⚠ 위와 동일, 고정(Ki=0.0)되어 무시됨
- LongTuningKf: 100   ⚠ 위와 동일, 고정(Kf=1.0)되어 무시됨
- StoppingAccel: -10 ← 실제 적용됨 (고정 로직 대상 아님)
- VEgoStopping: 5 ← 실제 적용됨
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
- DisableDM: 2  ← 기본값(0)이 아님. 확인됨(FINDINGS 2026-09-12): 운전자 모니터링(졸음/주의분산 감지,
  경고, 강제감속) 완전 OFF + Carrot Vision WebRTC 원격 스트리밍 활성화. 안전 관련 설정이므로
  사용자 의도 여부 재확인 필요.

### 실차 검증
- 이 값들은 사용자가 실제로 디바이스에 적용해 사용 중인 값 (실주행 반영 상태로 추정).
- 다만 Claude가 직접 실차 검증한 것은 아니며, 사용자 제공 백업 파일 기준으로만 기록.

### TODO / 다음 분석 후보
- DisableDM=2의 정확한 의미와 왜 이 값으로 설정했는지 확인
- LateralTorqueCustom=0인데 LateralTorque* 값들이 커스텀되어 있는 이유 확인
  (커스텀 토크 테이블이 실제로 적용되는 조건 확인 필요)
