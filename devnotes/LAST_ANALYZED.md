# LAST ANALYZED

carrot-wip commit: bb0e18bb8c09422fcd50dcf25c17e0d5c75072b1 (2026-09-12)
분석 범위 (4차 계속 — DisableDM / LateralTorqueCustom):
  openpilot/selfdrive/selfdrived/selfdrived.py (DisableDM 사용부, 245행)
  openpilot/selfdrive/controls/controlsd.py (DisableDM 사용부, 426행)
  openpilot/system/manager/process_config.py (enable_dm, enable_webrtc)
  openpilot/selfdrive/carrot_settings.json (DisableDM 설명 문구)
  openpilot/selfdrive/controls/lib/latcontrol_torque.py (LateralTorqueCustom 분기)
  opendbc_repo/opendbc/car/interfaces.py (configure_torque_tune)
  opendbc_repo/opendbc/car/torque_data/params.toml (HYUNDAI_GENESIS 실측 토크 계수)

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
- TFollowGap / 차간거리 로직 (longitudinal_mpc, t_follow.py)
- 곡선 감속(curve_speed.py), 정지선 감속(traffic_stop.py) 등 carrot 전용 종방향 모듈
- (완료됨: DisableDM=2, LateralTorqueCustom — 4차 계속 참고)
