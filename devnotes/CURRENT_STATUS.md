# CURRENT STATUS

- 프로젝트: CARROT-RYU (제네시스 DH 2015)
- 상태: 코드 변경 없음, 분석/기록 진행 중 (4차 + 4차 계속 완료)
- carrot-ryu 최신 commit: bb0e18bb8c09422fcd50dcf25c17e0d5c75072b1 (carrot-wip과 동일)
- carrot-wip 마지막 동기화 commit: bb0e18bb8c09422fcd50dcf25c17e0d5c75072b1 (분기 시점 기준, 신규 커밋 없음 확인)
- 핵심 발견 1: 현대·기아·제네시스는 종방향 PID 게인(Kp/Ki/Kf)이 코드에 고정되어
  LongTuningKpV/KiV/Kf 설정값이 실제로는 무시됨. 조절 가능한 종방향 노브는
  LongActuatorDelay / VEgoStopping / StoppingAccel 뿐 (FINDINGS.md 2026-09-12 참고)
- 핵심 발견 2 (안전 관련): DisableDM=2는 운전자 모니터링(졸음/주의분산 감지·경고·강제감속)을
  완전히 끄고 Carrot Vision WebRTC 원격 스트리밍을 켜는 설정임. 사용자에게 의도 여부 확인 필요.
- 핵심 발견 3: LateralTorqueCustom=0이라 저장된 LateralTorqueKf 등 6개 값은 전혀 적용되지 않고,
  실제로는 opendbc 실측 기본값(HYUNDAI_GENESIS: LAT_ACCEL_FACTOR≈2.78, FRICTION≈0.098)으로 조향 토크 계산 중.
- 다음 분석 후보: TFollowGap(차간거리), curve_speed.py, traffic_stop.py 등
