# LAST ANALYZED

분석 범위 (8차 — 실주행 로그 분석, route 감속 오검출 확인):
  route 000003fb--8470375f65--21 (rlog.zst, qlog.zst, qcamera.ts) — carrotMan/carState/
    carControl/longitudinalPlan 메시지 파싱 및 시계열 대조 (5차 정적분석 대상이었던
    carrot_navi_route/update_navi 체인의 실주행 검증)
  openpilot/selfdrive/carrot/carrot_man.py (carrot_navi_route, calculate_curvature) — 재확인
  openpilot/selfdrive/carrot/carrot_serv.py (update_navi, speed_n_sources) — 재확인

carrot-wip commit: bb0e18bb8c09422fcd50dcf25c17e0d5c75072b1 (2026-09-12)
분석 범위 (5차 계속 — traffic_stop / curve_speed / MPC 코스트 함수, 종방향 1단계 마무리):
  openpilot/selfdrive/carrot/traffic_stop.py (TrafficStopModelLeadMatcher, get_traffic_stop_*)
  openpilot/selfdrive/carrot/curve_speed.py (curve_speed, VisionCurveSpeed)
  openpilot/selfdrive/carrot/carrot_functions.py (check_model_stopping, XState 상태머신,
    jerk_factor 결정부)
  openpilot/selfdrive/carrot/carrot_man.py (carrot_curve_speed, vturn_speed)
  openpilot/selfdrive/controls/lib/longitudinal_mpc_lib/long_mpc.py (get_jerk_factor,
    get_a_change_cost, set_weights, x2 obstacle 반영부)
  openpilot/selfdrive/carrot_settings.json (TrafficLightDetectMode, AutoCurveSpeedFactor 등)

분석 범위 (5차 — route 감속 체인 + T_FOLLOW/TFollowGap):
  openpilot/selfdrive/carrot/carrot_man.py (carrot_navi_route, calculate_curvature)
  openpilot/selfdrive/carrot/carrot_serv.py (update_navi, speed_n_sources)
  openpilot/selfdrive/carrot/carrot_functions.py (_update_carrot_man, _get_base_t_follow ~ get_T_FOLLOW)
  openpilot/selfdrive/carrot/carrot_navi_control.py (parse_carrot_navi_control)
  openpilot/selfdrive/carrot/t_follow.py
  openpilot/selfdrive/controls/lib/longitudinal_planner.py (v_cruise_kph 계산부)
  openpilot/selfdrive/controls/lib/longitudinal_mpc_lib/long_mpc.py (t_follow 사용부)
  openpilot/selfdrive/controls/controlsd.py (setSpeed/hudControl 표시부, carrotMan 소비부)
  openpilot/selfdrive/carrot_settings.json (TurnSpeedControlMode, MapTurnSpeedFactor, TFollowGap1~4 등)
  devnotes/params_snapshots/2026-09-12_params_backup-4.json (실제 저장값 대조)

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
- ✅ 종방향(가감속) 코드 분석 1단계 완료: route/vturn 감속, T_FOLLOW, traffic_stop,
  MPC 코스트 함수까지 전체 체인 추적 완료
- 다음 단계: 실차주행(콤마 디바이스 실장착) → route 로그 생성 → 로그분석으로 코드 분석과
  실제 거동 일치 여부 검증
- (그 외 보류 항목: TurnSpeedControlMode/EnableSpeedTF 등 사용자 의도 확인, DisableDM=2 확인)
- (완료됨: DisableDM=2, LateralTorqueCustom — 4차 계속 / route 감속 체인, T_FOLLOW — 5차 /
  traffic_stop, curve_speed, MPC 코스트 함수 — 5차 계속 참고)
