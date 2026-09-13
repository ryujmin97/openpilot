# CURRENT STATUS

- 프로젝트: CARROT-RYU (제네시스 DH 2015)
- 베이스 브랜치: carrot-ms (happymaj11r/openpilot). ryujmin97/openpilot에는
  더 이상 carrot-ms/carrot-wip을 미러링하지 않음 (7차 세션에서 삭제 완료)
- carrot-ryu: 12차 반영 완료. HEAD = 4f4f8a8 (8~9차 route 감속 근본수정
  2dbe492 + 10차 RES 인게이지 안전장치 e1e587b + 12차 스크린샷 버튼/시계
  초단위 684b30d + 오커밋 정리 4f4f8a8). 11차는 설계만 있었고 실제 반영은
  12차에서 재설계되어 완료됨(WIP.md 12차 항목 참고)
- carrot-ryu HEAD에 "token test"라는 내용 없는 빈 커밋(2c33603)이 10차 위에
  하나 더 있음 확인 (아마 사용자의 git 인증 테스트, 코드/devnotes에 영향 없음)
- carrot-ms 동기화 상태: 6차 세션 이후 신규 커밋(rebase) 없음 확인 (7차).
  8~12차 세션에서는 동기화 재점검 없음
- 참고: carrot-wip(ajouatom/openpilot) HEAD는
  bb0e18bb8c09422fcd50dcf25c17e0d5c75072b1로 계속 진행 중이나, carrot-ms가
  아직 rebase하지 않아 직접 비교 대상 아님
- 상태: 코드 수정 3건 -- route 감속 오검출 근본수정(GitHub 반영됨, 실차
  재검증 대기), RES/+ 인게이지 속도 안전장치(GitHub 반영됨, 실차 재검증
  대기), 온로드 시계 초단위 표시 + 스크린샷 버튼(12차, GitHub 반영됨, 실차
  재검증 대기)
- 핵심 발견 1: 현대기아/제네시스는 종방향 PID 게인(Kp/Ki/Kf)이 코드에
  고정되어 LongTuningKpV/KiV/Kf 설정값이 실제로는 무시됨
- 핵심 발견 2 (안전 관련, 확인 필요): DisableDM=2는 운전자 모니터링을 완전히
  끄고 Carrot Vision WebRTC 원격 스트리밍을 켜는 설정. 사용자 의도 확인 필요.
- 핵심 발견 3: LateralTorqueCustom=0이라 opendbc 실측 기본값으로 조향 토크
  계산 중
- 핵심 발견 4 (안전 관련, 확인 필요): route 기반 커브 감속이 실제로 켜져
  있음 (TurnSpeedControlMode=2)
- 핵심 발견 5: T_FOLLOW/traffic_stop/curve_speed 체인 모두 실제 MPC까지
  연결됨
- 핵심 발견 6 (8~9차): route 감속 고속도로 분기점 오검출을 median 필터로
  근본수정 (2dbe492). 실차 재검증 대기
- 핵심 발견 7 (10차): 출발 가속 중 +RES 인게이지 시 설정속도가 현재속도보다
  낮게 잡혀 급감속 발생하는 경우 있음 -> 안전장치 추가. 정확한 트리거
  조건(AutoRoadSpeedLimitOffset/SpeedFromPCM 실제값) 미확인
- 핵심 발견 8 (12차): 스크린샷은 carrotweb이 이미 스캔 중인 화면녹화 폴더에
  저장하는 방식이나, 정지 이미지/영상 구분(kind)을 위한 backend/frontend
  변경은 아직 미반영 -- carrotweb 로그탭에서 정상 표시되는지 미확인
- ⚠ 미확인: carrot-ms 모델 셀렉터 코드 미분석
- 다음 작업: route 감속 수정 + 인게이지 안전장치 + 12차 신규 2건 모두 실주행
  재검증, 스크린샷 backend/frontend 추가 여부 결정, 모델 셀렉터 코드 분석,
  AutoRoadSpeedLimitOffset/SpeedFromPCM 등 사용자 의도 확인
- 보류 확인 항목: TurnSpeedControlMode=2 / EnableSpeedTF=0 /
  LeadAccelResponse=0 / DisableDM=2 / LateralTorqueCustom=0 /
  AutoRoadSpeedLimitOffset / SpeedFromPCM
