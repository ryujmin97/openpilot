# HANDOFF

Worker: Claude (세션 13)
Date: 2026-09-13
Repository: ryujmin97/openpilot
Code Branch: carrot-ryu (base commit: 4f4f8a8 -- 이 위에 13차 커밋 1개
  추가 예정/완료. 정확한 새 HEAD 해시는 스크립트 실행 후 다음 세션이
  GitHub에서 확인)
Note Branch: carrot-ryu-note (13차 devnotes 반영, 이 커밋)
carrot-ms 마지막 검토/동기화 커밋(메시지 기준): 7차 세션과 동일, 신규 커밋
없음 (WIP_SYNC.md 참고, 13차에서도 재확인하지 않음)

작업:
사용자가 실제 화면 사진을 공유하며 온로드 좌측 상단 시계 표시가
"23:32:34"가 아닌 "3:32:34"로 보인다고 보고 (맨 앞 "2" 누락)

완료:
- 원인 규명: hud_renderer.py의 _draw_date_time()에서 시계 텍스트(HH:MM:SS,
  font_size=100)를 align="center_bottom"으로 그릴 때 x=rect.x+170(고정)을
  기준으로 절반 폭만큼 왼쪽으로 당겨 그리는데(text_draw.py
  get_text_draw_pos), 8자 텍스트 폭이 넓어 draw_x가 화면 좌측 경계를
  넘어(음수) 첫 글자가 잘림. 12차의 초 단위 표시 추가(%H:%M -> %H:%M:%S)로
  발생한 회귀로 추정
- 수정: measure_text_cached로 시계 텍스트 실측 폭을 구해 좌측 여백
  (UI_CONFIG.border_size)을 보장하도록 x를 동적 보정하는 로직 추가.
  _draw_date_time() 한 곳만 수정(10절 최소 변경 원칙)
- 검증: 반영 직전 GitHub의 hud_renderer.py 최신본을 다시 받아 그 위에서
  diff 생성 -> 별도 clone 시뮬레이션에서 git apply --check/git apply 성공
  확인 -> py_compile 통과 확인(Claude 샌드박스 python, 사용자 PC 환경과
  무관 -- 12차 HANDOFF 주의사항 참고)
- 9절 방식(diff/git apply)으로 반영 스크립트 작성, 사용자에게 전달
  (폰 Termux 환경이라 PowerShell 대신 bash 스크립트로 전달)

미완료 / 다음 세션 우선순위:
1. **실주행 재검증 필요** -- 13차(시계 잘림 수정) + 12차(스크린샷 버튼,
   시계 초단위) + 8~10차(route 감속 근본수정, RES 인게이지 안전장치) 모두
   실차 미검증
2. 13차 반영이 실제로 스크립트 실행을 통해 GitHub에 push 됐는지 확인
   (사용자 실행 로그 확인 또는 GitHub API/raw로 재확인 필요 -- 이 세션은
   스크립트만 만들고 실행은 못함, 5/16절 원칙)
3. 11차가 계획했던 스크린샷 backend/frontend(kind 구분, 이미지 뷰어) 변경
   여전히 미반영
4. AutoRoadSpeedLimitOffset(기본값 -1) / SpeedFromPCM 실제 설정값 미확인
5. carrot-ms가 추가한 "모델 셀렉터" 코드는 아직 분석하지 않음
6. TurnSpeedControlMode=2 / EnableSpeedTF=0 / DisableDM=2 등 사용자 의도 확인

검증: 정적 분석 + 문법 검증(py_compile) + diff 적용 재현 테스트까지만 확인.
실차 검증 미실시.

주의사항:
- git diff는 반드시 --no-pager 또는 GIT_PAGER=cat과 함께 사용
- Termux bash heredoc(<< 'EOF')은 마지막 줄 뒤 개행이 자연히 보존됨
  (PowerShell here-string과 달리 별도 보정 불필요)
- Claude는 web_fetch로 ryujmin97/openpilot의 raw 파일에 직접 접근 못함 --
  bash_tool로 raw.githubusercontent.com/api.github.com에 curl 가능
  (api.github.com은 미인증 rate limit에 자주 걸림 -- raw.githubusercontent.com
  위주로 조회할 것). hud_renderer.py 등 코드 파일의 실제 경로는 최상위에
  `openpilot/` 서브폴더가 있음(예: openpilot/selfdrive/ui/onroad/...) --
  4/9절 확인 시 이 경로 기준으로 조회할 것
- 이번 세션(13차)은 사용자가 폰(Termux)만 사용 중이라고 밝힘. 이후 세션에서
  반영 수단을 물을 때는 기본으로 Termux bash 스크립트를 우선 준비할 것

다음 작업 후보:
1. 13차 실제 GitHub 반영 여부 확인(사용자 스크립트 실행 로그 또는 재조회)
2. 실주행 재검증 (13차 신규 1건 + 12차 2건 + 8~10차 기존 2건 모두)
3. 스크린샷 backend/frontend(kind 구분, 이미지 뷰어) 추가 여부 결정 및 반영
4. AutoRoadSpeedLimitOffset/SpeedFromPCM 실제 설정값 확인
5. (선택) carrot-ms의 model_selector 코드 분석
