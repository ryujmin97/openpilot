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
- TFollowGap1~4: 110 / 120 / 140 / 160 (=1.10/1.20/1.40/1.60초, openpilot 표준 범위 내,
  정정: 코드상 Gap1~4까지만 존재, Gap5 항목 없음. FINDINGS 2026-09-12 T_FOLLOW 체인 참고)
- EnableSpeedTF: 0 ← 속도기반 차간거리 보정 미사용, personality 고정값만 사용 중
- LeadAccelResponse: 0 ← 레벨4-5 예외(선행차 가속중 설정 유지) 비활성
- DynamicTFollowLC: 100(=1.0) ← 차선변경시 차간거리 배율 변화 없음
- TFollowDecelBoost: 10(=0.10) ← 감속시 여유거리 보정 약하게(최대 0.05초)

**감속제어 (커브/route/카메라) — route 감속 체인, FINDINGS 2026-09-12 참고**
- TurnSpeedControlMode: 2 ← 기본값(1, 비전만)이 아님. "비전+경로(TBT)" 모드로 실제
  route 감속이 활성화된 상태. ⚠ 사용자 의도 여부 확인 필요 (DisableDM=2와 동일 패턴)
- MapTurnSpeedFactor: 100 ← 경로 감속 반영비율 100%(조정 없음)
- AutoCurveSpeedLowerLimit: 20 ← 커브/경로 감속 하한 20km/h
- AutoNaviSpeedDecelRate: 60(=0.60 m/s²) ← 카메라/커브/경로 공통 감속률
- AutoCurveSpeedFactor: 80 ← 기본값(100)보다 낮음. "높이면 목표속도가 낮아진다"는 설명
  기준, 80%는 기본보다 느슨하게(커브를 더 빠른 속도로 통과)로 설정된 상태 (curve_speed.py
  비전 버전, FINDINGS 참고)

**정지신호 감속(traffic_stop.py) — FINDINGS 2026-09-12 참고**
- TrafficLightDetectMode: 2 ← 기본값("정지+출발 모두 감지"). 별도 조작 없이 이미
  실도로에서 작동 중이었을 가능성 높음
- StopDistanceCarrot: 700(=7.00m) ← 정지선/장애물 정지거리
- TrafficStopDistanceAdjust: 0(=0.00m) ← 코드 초기값 2.5m을 사용자가 0으로 재설정

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
- TurnSpeedControlMode=2(route 감속 활성화)가 사용자 의도인지, 폰 내비 앱(APN) 연동이
  실제로 붙어있는 상태인지 확인 필요 (FINDINGS 2026-09-12 route 감속 체인 참고)
- EnableSpeedTF=0 / LeadAccelResponse=0이 의도적 설정인지, 아니면 시험해보지 않은
  기본값 방치인지 확인 필요
- ✅ 종방향(가감속) 코드 분석 1단계 완료(4차~5차 계속): LongControl PID, route/vturn 감속,
  T_FOLLOW, traffic_stop, MPC 코스트 함수까지 전체 체인 추적 완료. FINDINGS 2026-09-12
  "종방향 전체 체계 종합" 참고
- 다음 단계: 실차주행 → route 로그 생성 → 로그분석으로 코드 분석과 실제 거동 일치 여부 검증
