# CURRENT STATUS

- 프로젝트: CARROT-RYU (제네시스 DH 2015)
- 상태: 코드 변경 없음, 종방향(가감속) 코드 분석 진행 중 (5차 완료)
- carrot-ryu 최신 commit: bb0e18bb8c09422fcd50dcf25c17e0d5c75072b1 (carrot-wip과 동일)
- carrot-wip 마지막 동기화 commit: bb0e18bb8c09422fcd50dcf25c17e0d5c75072b1 (분기 시점 기준, 신규 커밋 없음 확인)
- 진행 방향(사용자 결정): 종방향 코드 분석을 먼저 마무리 → 콤마 디바이스로 실차주행 →
  route 로그 생성 → 로그분석으로 코드 분석과 실제 거동 일치 여부 검증
- 핵심 발견 1: 현대·기아·제네시스는 종방향 PID 게인(Kp/Ki/Kf)이 코드에 고정되어
  LongTuningKpV/KiV/Kf 설정값이 실제로는 무시됨. 조절 가능한 종방향 노브는
  LongActuatorDelay / VEgoStopping / StoppingAccel 뿐
- 핵심 발견 2 (안전 관련, 확인 필요): DisableDM=2는 운전자 모니터링(졸음/주의분산 감지·경고·
  강제감속)을 완전히 끄고 Carrot Vision WebRTC 원격 스트리밍을 켜는 설정. 사용자 의도 확인 필요.
- 핵심 발견 3: LateralTorqueCustom=0이라 저장된 LateralTorqueKf 등 6개 값은 전혀 적용되지 않고,
  실제로는 opendbc 실측 기본값(HYUNDAI_GENESIS: LAT_ACCEL_FACTOR≈2.78, FRICTION≈0.098)으로 조향 토크 계산 중.
- 핵심 발견 4 (안전 관련, 확인 필요): route(경로) 기반 커브 감속이 이 차량에서 실제로
  켜져 있음(TurnSpeedControlMode=2). GPS 폴리라인 기반 곡률 계산 → MPC v_cruise 상한까지
  실제 감속 명령으로 이어지는 체인 확인. 폰 내비 앱(APN) 연동 실제 연결 여부는 미확인.
- 핵심 발견 5: T_FOLLOW/TFollowGap(차간거리) 체인도 MPC 리드차 장애물 제약에 직접 반영됨을
  확인. 이 차량은 EnableSpeedTF=0, LeadAccelResponse=0으로 가장 단순한 personality 고정값
  모드(TFollowGap1~4=1.10/1.20/1.40/1.60초, 표준 범위)로 운용 중. 정적 버그 없음.
- 다음 분석 후보: traffic_stop.py(정지선), curve_speed.py(비전 커브), longitudinal MPC 코스트 함수
- 그 이후: 실차주행 → 로그분석 단계로 전환
