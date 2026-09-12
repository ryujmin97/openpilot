# HANDOFF

Worker: Claude (세션 4)
Date: 2026-09-12
Repository: ryujmin97/openpilot
Code Branch: carrot-ryu (base commit: bb0e18bb8c09422fcd50dcf25c17e0d5c75072b1, carrot-wip과 동일, 코드 변경 없음)
Note Branch: carrot-ryu-note (4차 devnotes 반영)
carrot-wip 마지막 동기화 commit: bb0e18bb8c09422fcd50dcf25c17e0d5c75072b1 (신규 커밋 없음 확인, 동기화 불필요)

작업:
완료:
- 종방향 제어(가감속) 로직 분석 (longcontrol.py, longitudinal_planner.py, hyundai interface.py/values.py)
- 핵심 발견: 현대·기아·제네시스 종방향 PID 게인(Kp/Ki/Kf)이 커밋 a26b108d(2026-09-04)에서
  코드 레벨로 고정됨(1.0/0.0/1.0). 사용자의 LongTuningKpV/KiV/Kf=100/0/100 설정은 실제로 무시됨.
- 실제 적용되는 종방향 노브: LongActuatorDelay(현재 20→0.2s), VEgoStopping(5→0.05m/s),
  StoppingAccel(-10→-0.1m/s²) 3가지뿐임을 확인
- ACCEL_MIN/MAX(-4.0/2.5 m/s²)는 제네시스 전용값 없이 Hyundai 계열 공통값임을 확인
- FINDINGS.md / PARAMS_REGISTRY.md / LAST_ANALYZED.md / WIP.md(4차) 갱신

미완료:
- DisableDM=2 의미/근거 미확인 (이번 세션에서 사용자가 보류 지정)
- LateralTorqueCustom=0인데 LateralTorque* 값들이 커스텀된 이유 미확인 (보류)
- TFollowGap / 차간거리(t_follow.py), 곡선감속(curve_speed.py), 정지선(traffic_stop.py) 등
  carrot 전용 종방향 모듈은 아직 분석 안 함
- 종방향 MPC(longitudinal_mpc_lib) 코스트 함수 분석 안 함

검증: 실차 검증 미실시 (정적 코드/문서 분석 기준)

주의사항:
- 이번 발견은 버그가 아니라 carrot-wip이 문서화한 의도된 안전 고정값임 (docs/user/ko/cruise-gap.md,
  settings.md에 명시됨). carrot-ryu에 임의로 "게인을 되살리는" 패치를 하지 말 것 — 사용자 승인 필요.
- carrot-ryu는 여전히 carrot-wip과 코드 동일 (분기 이후 실제 코드 수정 아직 없음)
- carrot-wip에 신규 커밋 없음을 이번 세션에서 재확인함 (동기화 작업 불필요)

다음 작업 후보:
- DisableDM=2 / LateralTorqueCustom 분석 재개
- TFollowGap 등 차간거리 로직 분석
- 또는 사용자가 원하는 다른 항목
