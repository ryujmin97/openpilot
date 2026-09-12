# CURRENT STATUS

- 프로젝트: CARROT-RYU (제네시스 DH 2015)
- 상태: 코드 변경 없음. 종방향(가감속) 코드 분석 1단계 완료(5차 계속), 실차주행 단계로 전환 예정
- carrot-ryu 최신 commit: bb0e18bb8c09422fcd50dcf25c17e0d5c75072b1 (carrot-wip과 동일)
- carrot-wip 마지막 동기화 commit: bb0e18bb8c09422fcd50dcf25c17e0d5c75072b1 (분기 시점 기준, 신규 커밋 없음 확인)
- 진행 방향(사용자 결정): 종방향 코드 분석 완료 → 콤마 디바이스로 실차주행 → route 로그 생성
  → 로그분석으로 코드 분석과 실제 거동 일치 여부 검증 (다음 세션의 핵심 작업)
- 핵심 발견 1: 현대·기아·제네시스는 종방향 PID 게인(Kp/Ki/Kf)이 코드에 고정되어
  LongTuningKpV/KiV/Kf 설정값이 실제로는 무시됨. 조절 가능한 종방향 노브는
  LongActuatorDelay / VEgoStopping / StoppingAccel 뿐
- 핵심 발견 2 (안전 관련, 확인 필요): DisableDM=2는 운전자 모니터링을 완전히 끄고
  Carrot Vision WebRTC 원격 스트리밍을 켜는 설정. 사용자 의도 확인 필요.
- 핵심 발견 3: LateralTorqueCustom=0이라 저장된 LateralTorqueKf 등 6개 값은 미적용,
  실제로는 opendbc 실측 기본값(LAT_ACCEL_FACTOR≈2.78, FRICTION≈0.098)으로 조향 토크 계산 중.
- 핵심 발견 4 (안전 관련, 확인 필요): route(경로) 기반 커브 감속이 이 차량에서 실제로
  켜져 있음(TurnSpeedControlMode=2). 폰 내비 앱(APN) 연동 실제 연결 여부는 미확인.
- 핵심 발견 5: T_FOLLOW/TFollowGap 체인, traffic_stop(E2E 정지신호) 체인, curve_speed(비전
  커브) 체인 모두 실제 MPC obstacle/v_cruise까지 연결되어 물리적 가감속 명령을 만들어냄을
  코드 레벨에서 확인. MPC 자체는 stock openpilot 프레임워크라 신뢰도 높음.
- 핵심 발견 6 (구조적 리스크, 정적 분석 기준): ①route 감속은 폰 내비 앱 연동 안정성에 좌우,
  ②traffic_stop은 HD맵/신호색상 인식 없이 순수 E2E 모델 휴리스틱이라 모델 성능에 전적 의존.
- ✅ 종방향 코드 분석 1단계(4차~5차 계속) 완료: LongControl PID → v_cruise 상한(route/vturn)
  → MPC(T_FOLLOW/traffic_stop obstacle, 코스트 함수) → 액추에이터까지 전체 체인 추적 완료.
- 다음 작업: 실차주행(콤마 디바이스 실장착) → route 로그 수집 → 로그분석
- 보류 확인 항목: TurnSpeedControlMode=2 / EnableSpeedTF=0 / LeadAccelResponse=0이
  사용자 의도인지, DisableDM=2 의도 여부, LateralTorqueCustom=0 이유
