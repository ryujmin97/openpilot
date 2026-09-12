# CURRENT STATUS

- 프로젝트: CARROT-RYU (제네시스 DH 2015)
- ⚠ 베이스 브랜치 변경됨: carrot-wip → carrot-ms (happymaj11r/openpilot, 콤마 주행모델
  선택 기능 포함, carrot-wip 기반으로 매번 재생성/rebase됨). 프로젝트 지침 문서의
  "베이스 브랜치" 항목을 이 사실에 맞춰 갱신해야 함 (6차 WIP 참고, 수정 문구 HANDOFF 참고)
- carrot-ryu 최신 commit: 02015190f58a4380a433ee0130e6374455dddc2e
  ("Recover evil-merge resolutions from carrot-wip PR #516 and PR #517", carrot-ms HEAD와 동일)
- carrot-wip 직접 동기화는 더 이상 하지 않음 — carrot-ms를 통해 간접 반영됨
- carrot-ms 동기화 방식: histor가 매번 재작성(rebase)되어 fast-forward 불가. carrot-ms가
  업데이트될 때마다 carrot-ms/carrot-wip 커밋 메시지를 비교해 "모델 셀렉터 관련 커밋"만
  선별 반영 필요 (2절 동기화 원칙의 carrot-ms용 확장 적용 필요, 아직 미정)
- 상태: 코드 변경 없음(베이스 전환만 수행). 종방향(가감속) 코드 분석 1단계는 완료된 상태이며
  carrot-wip 기반 분석이라 carrot-ms에도 대부분 그대로 유효한 것으로 판단
- 핵심 발견 1: 현대·기아·제네시스는 종방향 PID 게인(Kp/Ki/Kf)이 코드에 고정되어
  LongTuningKpV/KiV/Kf 설정값이 실제로는 무시됨. 조절 가능한 종방향 노브는
  LongActuatorDelay / VEgoStopping / StoppingAccel 뿐
- 핵심 발견 2 (안전 관련, 확인 필요): DisableDM=2는 운전자 모니터링을 완전히 끄고
  Carrot Vision WebRTC 원격 스트리밍을 켜는 설정. 사용자 의도 확인 필요.
- 핵심 발견 3: LateralTorqueCustom=0이라 저장된 LateralTorqueKf 등 6개 값은 미적용,
  실제로는 opendbc 실측 기본값(LAT_ACCEL_FACTOR≈2.78, FRICTION≈0.098)으로 조향 토크 계산 중.
- 핵심 발견 4 (안전 관련, 확인 필요): route(경로) 기반 커브 감속이 이 차량에서 실제로
  켜져 있음(TurnSpeedControlMode=2). 폰 내비 앱(APN) 연동 실제 연결 여부는 미확인.
- 핵심 발견 5: T_FOLLOW/TFollowGap, traffic_stop(E2E 정지신호), curve_speed(비전 커브)
  체인 모두 실제 MPC obstacle/v_cruise까지 연결되어 물리적 가감속 명령을 만들어냄을 확인.
- ⚠ 미확인: carrot-ms가 추가한 "모델 셀렉터" 관련 코드(carrot/model_selector 등)는
  아직 전혀 분석하지 않음 — 다음 분석 후보
- 다음 작업: ①모델 셀렉터 코드 분석(신규), ②실차주행(콤마 디바이스 실장착) → route 로그
  수집 → 로그분석, ③사용자 프로젝트 지침 문서에 베이스 브랜치 변경 반영
- 보류 확인 항목: TurnSpeedControlMode=2 / EnableSpeedTF=0 / LeadAccelResponse=0이
  사용자 의도인지, DisableDM=2 의도 여부, LateralTorqueCustom=0 이유
