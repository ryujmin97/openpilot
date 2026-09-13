# CURRENT STATUS

- 프로젝트: CARROT-RYU (제네시스 DH 2015)
- 베이스 브랜치: carrot-ms (happymaj11r/openpilot). ryujmin97/openpilot에는 더 이상
  carrot-ms/carrot-wip을 미러링하지 않음 (7차 세션에서 삭제 완료)
- carrot-ryu: 10차 반영(RES/+ 인게이지 속도 안전장치) 스크립트 실행 완료 시
  최신 상태(8~9차 route 감속 근본수정 2dbe492 + 10차 안전장치)
- carrot-ms 동기화 상태: 6차 세션 이후 신규 커밋(rebase) 없음 확인 (7차). 8~10차
  세션에서는 동기화 재점검 없음
- 참고: carrot-wip(ajouatom/openpilot) HEAD는 bb0e18bb8c09422fcd50dcf25c17e0d5c75072b1로
  계속 진행 중이나, carrot-ms가 아직 rebase하지 않아 직접 비교 대상 아님
- 상태: 코드 수정 2건 - ①route 감속 오검출 근본수정(GitHub 반영됨, 실차 재검증 대기),
  ②RES/+ 인게이지 속도 안전장치(이 스크립트로 반영, 실차 재검증 대기)
- 핵심 발견 1: 현대·기아·제네시스는 종방향 PID 게인(Kp/Ki/Kf)이 코드에 고정되어
  LongTuningKpV/KiV/Kf 설정값이 실제로는 무시됨
- 핵심 발견 2 (안전 관련, 확인 필요): DisableDM=2는 운전자 모니터링을 완전히 끄고
  Carrot Vision WebRTC 원격 스트리밍을 켜는 설정. 사용자 의도 확인 필요.
- 핵심 발견 3: LateralTorqueCustom=0이라 opendbc 실측 기본값으로 조향 토크 계산 중
- 핵심 발견 4 (안전 관련, 확인 필요): route 기반 커브 감속이 실제로 켜져 있음
  (TurnSpeedControlMode=2)
- 핵심 발견 5: T_FOLLOW/traffic_stop/curve_speed 체인 모두 실제 MPC까지 연결됨
- 핵심 발견 6 (8~9차): route 감속 고속도로 분기점 오검출을 median 필터로 근본수정
  (2dbe492). 실차 재검증 대기
- 핵심 발견 7 (10차, 사용자 제보): 출발 가속 중 +RES 인게이지 시 설정속도가
  현재속도보다 낮게 잡혀 급감속 발생하는 경우 있음. 인게이지 속도가 항상 현재속도
  이상이 되도록 안전장치 추가. 정확한 트리거 조건(AutoRoadSpeedLimitOffset/
  SpeedFromPCM 실제값)은 미확인으로 완전히 특정 못함
- ⚠ 미확인: carrot-ms 모델 셀렉터 코드 미분석
- 다음 작업: ①route 감속 수정 + 인게이지 안전장치 모두 실주행 재검증, ②모델 셀렉터
  코드 분석, ③AutoRoadSpeedLimitOffset/SpeedFromPCM 등 사용자 의도 확인
- 보류 확인 항목: TurnSpeedControlMode=2 / EnableSpeedTF=0 / LeadAccelResponse=0 /
  DisableDM=2 / LateralTorqueCustom=0 / AutoRoadSpeedLimitOffset / SpeedFromPCM
