# CURRENT STATUS

- 프로젝트: CARROT-RYU (제네시스 DH 2015)
- 베이스 브랜치: carrot-ms (happymaj11r/openpilot). ryujmin97/openpilot에는
  더 이상 carrot-ms/carrot-wip을 미러링하지 않음 (7차 세션에서 삭제 완료)
- carrot-ryu: 12차까지 HEAD = 4f4f8a8. 13차는 hud_renderer.py
  _draw_date_time() 1개 함수만 수정(온로드 시계 좌측 화면 경계 잘림 버그
  수정). 정확한 13차 커밋 해시는 다음 세션에서 GitHub 확인 필요(스크립트
  실행 후 push된 경우에 한함)
- carrot-ryu HEAD 근처에 "token test"라는 내용 없는 빈 커밋(2c33603)이
  10차 위에 있음 확인 (아마 사용자의 git 인증 테스트, 코드/devnotes에
  영향 없음)
- carrot-ms 동기화 상태: 6차 세션 이후 신규 커밋(rebase) 없음 확인 (7차).
  8~13차 세션에서는 동기화 재점검 없음
- 참고: carrot-wip(ajouatom/openpilot)은 계속 진행 중이나, carrot-ms가
  아직 rebase하지 않아 직접 비교 대상 아님
- 상태: 코드 수정 4건 -- route 감속 오검출 근본수정(GitHub 반영됨, 실차
  재검증 대기), RES/+ 인게이지 속도 안전장치(GitHub 반영됨, 실차 재검증
  대기), 온로드 시계 초단위 표시 + 스크린샷 버튼(12차, GitHub 반영됨,
  실차 재검증 대기), 온로드 시계 좌측 화면 경계 잘림 수정(13차, 스크립트
  전달 완료, 사용자 실행/push 확인 필요)
- 핵심 발견 1~8(12차까지, 요약):
  1. 현대기아/제네시스 종방향 PID 게인 코드 고정(LongTuningKpV/KiV/Kf 무시)
  2. (안전, 확인 필요) DisableDM=2는 DM 끄고 Carrot Vision WebRTC 원격
     스트리밍 켬
  3. LateralTorqueCustom=0이라 opendbc 실측 기본값 사용 중
  4. (안전, 확인 필요) route 기반 커브 감속 실제 켜짐(TurnSpeedControlMode=2)
  5. T_FOLLOW/traffic_stop/curve_speed 체인 모두 MPC까지 연결됨
  6. (8~9차) route 감속 고속도로 분기점 오검출 median 필터로 근본수정
     (2dbe492), 실차 재검증 대기
  7. (10차) 출발 가속 중 +RES 인게이지 급감속 -> 안전장치 추가, 정확한
     트리거 조건 미확인
  8. (12차) 스크린샷 backend/frontend(kind 구분) 변경 아직 미반영
- 핵심 발견 9 (13차): 온로드 좌측 상단 시계가 HH:MM:SS(8자, font_size=100)로
  center_bottom 정렬되며 고정 x(rect.x+170) 기준으로는 텍스트 절반 폭이
  화면 좌측 경계를 넘어가 첫 글자가 잘리는 버그. 12차 초 단위 표시 추가로
  발생한 회귀로 추정. 텍스트 실측 폭 기반 x 보정으로 수정
- ⚠ 미확인: carrot-ms 모델 셀렉터 코드 미분석
- 다음 작업: 13차 포함 코드 수정 4건 전부 실주행 재검증, 스크린샷
  backend/frontend 추가 여부 결정, 모델 셀렉터 코드 분석,
  AutoRoadSpeedLimitOffset/SpeedFromPCM 등 사용자 의도 확인
- 보류 확인 항목: TurnSpeedControlMode=2 / EnableSpeedTF=0 /
  LeadAccelResponse=0 / DisableDM=2 / LateralTorqueCustom=0 /
  AutoRoadSpeedLimitOffset / SpeedFromPCM
