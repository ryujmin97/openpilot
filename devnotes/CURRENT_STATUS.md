# CURRENT STATUS

- 프로젝트: CARROT-RYU (제네시스 DH 2015)
- 베이스 브랜치: carrot-ms (happymaj11r/openpilot). ryujmin97/openpilot에는 더 이상
  carrot-ms/carrot-wip을 미러링하지 않음 (7차 세션에서 삭제 완료, 필요 시 외부 저장소
  직접 조회)
- carrot-ryu 최신 commit: 02015190f58a4380a433ee0130e6374455dddc2e
  (carrot-ms HEAD와 완전히 동일, 7차 세션(2026-09-13) 확인 기준. 8차 세션은 재확인 안 함)
- carrot-ms 동기화 상태: 6차 세션 이후 carrot-ms에 신규 커밋(rebase) 없음 확인
  (7차, 2026-09-13). 8차 세션에서는 동기화 재점검 없음
- 참고: carrot-wip(ajouatom/openpilot) HEAD는 bb0e18bb8c09422fcd50dcf25c17e0d5c75072b1로
  계속 진행 중이나, carrot-ms가 아직 이를 따라 rebase하지 않아 직접 비교 대상 아님
  (2절 원칙)
- 상태: 코드 변경 없음. 종방향(가감속) 코드 분석 1단계는 완료, 8차에서 그 중 route
  감속 체인을 실주행 로그로 실증
- 핵심 발견 1: 현대·기아·제네시스는 종방향 PID 게인(Kp/Ki/Kf)이 코드에 고정되어
  LongTuningKpV/KiV/Kf 설정값이 실제로는 무시됨. 조절 가능한 종방향 노브는
  LongActuatorDelay / VEgoStopping / StoppingAccel 뿐
- 핵심 발견 2 (안전 관련, 확인 필요): DisableDM=2는 운전자 모니터링을 완전히 끄고
  Carrot Vision WebRTC 원격 스트리밍을 켜는 설정. 사용자 의도 확인 필요.
- 핵심 발견 3: LateralTorqueCustom=0이라 저장된 LateralTorqueKf 등 6개 값은 미적용,
  실제로는 opendbc 실측 기본값(LAT_ACCEL_FACTOR≈2.78, FRICTION≈0.098)으로 조향
  토크 계산 중.
- 핵심 발견 4 (안전 관련, 확인 필요): route(경로) 기반 커브 감속이 이 차량에서
  실제로 켜져 있음(TurnSpeedControlMode=2). 폰 내비 앱(APN) 연동 실제 연결 여부는
  미확인.
- 핵심 발견 5: T_FOLLOW/TFollowGap, traffic_stop(E2E 정지신호), curve_speed(비전
  커브) 체인 모두 실제 MPC obstacle/v_cruise까지 연결되어 물리적 가감속 명령을
  만들어냄을 확인.
- 핵심 발견 6 (8차, 실주행 로그로 확인): route 감속(핵심 발견 4)이 고속도로
  분기점에서 실제로 오검출 발생 — 3점 곡률 계산에 스파이크 제거 필터가 없어 조기
  과감속 후 원복되는 현상이 실주행 로그(route 000003fb--8470375f65--21)로 확인됨.
  대응 방향(설정 완화 vs 코드 수정) 미결정, 다음 세션 최우선 항목
- ⚠ 미확인: carrot-ms가 추가한 "모델 셀렉터" 관련 코드(carrot/model_selector 등)는
  아직 전혀 분석하지 않음
- 다음 작업: ①route 감속 오검출 대응 방향 결정 및 조치(최우선), ②모델 셀렉터
  코드 분석, ③콤마 디바이스 실차 장착 → 추가 route 로그 수집, ④TurnSpeedControlMode/
  DisableDM 등 사용자 의도 확인
- 보류 확인 항목: TurnSpeedControlMode=2 / EnableSpeedTF=0 / LeadAccelResponse=0이
  사용자 의도인지, DisableDM=2 의도 여부, LateralTorqueCustom=0 이유, route 감속
  오검출 대응 방향(신규, 8차)
