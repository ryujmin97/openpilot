# LAST ANALYZED

carrot-wip commit: bb0e18bb8c09422fcd50dcf25c17e0d5c75072b1 (2026-09-12)
분석 범위 (4차 — 종방향 PID 게인):
  openpilot/selfdrive/controls/lib/longcontrol.py
  openpilot/selfdrive/controls/lib/longitudinal_planner.py (LongActuatorDelay/VEgoStopping 사용부)
  opendbc_repo/opendbc/car/hyundai/interface.py (종방향 공통 설정부)
  opendbc_repo/opendbc/car/hyundai/values.py (CarControllerParams ACCEL_MIN/MAX)
  관련 커밋: a26b108d, e79bfd5d (longcontrol.py 변경 이력)

분석 범위 (3차 이전, 유지):
  opendbc_repo/opendbc/car/hyundai/values.py (HYUNDAI_GENESIS),
  opendbc_repo/opendbc/car/interfaces.py (minSteerSpeed 처리),
  openpilot/selfdrive/carrot_settings.json (DisableMinSteerSpeed UI)

다음 분석 후보:
- DisableDM=2, LateralTorqueCustom 관련 코드 (보류 상태, 사용자 요청 시 재개)
- TFollowGap / 차간거리 로직 (longitudinal_mpc, t_follow.py)
- 곡선 감속(curve_speed.py), 정지선 감속(traffic_stop.py) 등 carrot 전용 종방향 모듈
