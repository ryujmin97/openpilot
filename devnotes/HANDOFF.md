# HANDOFF

Worker: Claude (세션 12)
Date: 2026-09-13
Repository: ryujmin97/openpilot
Code Branch: carrot-ryu (base commit: 4f4f8a8 -- 12차 스크린샷 버튼+시계초단위
  반영 및 오커밋 파일(hud_renderer.diff) 정리 완료)
Note Branch: carrot-ryu-note (12차 devnotes 반영, 이 커밋)
carrot-ms 마지막 검토/동기화 커밋(메시지 기준): 7차 세션과 동일, 신규 커밋 없음
(WIP_SYNC.md 참고, 이번 세션에서도 재확인하지 않음)

작업:
완료:
- (11차부터 이어진) 온로드 시계 초단위 표시를 hud_renderer.py에 실제로 반영 완료
- 더블탭 대신 온로드 화면 중앙 하단 스크린샷 버튼(ScreenshotButton) 신규 추가
  및 hud_renderer.py 연동
- screenshot_capture.py 신규 파일 반영
- 9절 스크립트 방식(diff apply + 신규 파일 생성)으로 실제 GitHub push 완료,
  GitHub raw로 재확인
- 반영 과정에서 발생한 diff 적용 실패(corrupt patch, patch does not apply)
  원인 규명 및 스크립트 개선(Write-Utf8NoBom에 끝 개행 보장 로직 추가,
  core.autocrlf=false 명시)
- 잘못 커밋된 hud_renderer.diff 파일 정리(후속 커밋)

미완료 / 다음 세션 우선순위:
1. **실주행 재검증 필요** -- 12차(스크린샷 버튼, 시계 초단위) + 8~10차(route
   감속 근본수정, RES 인게이지 안전장치) 모두 실차 미검증
2. 11차가 계획했던 backend(config.py/catalog.py의 이미지 kind 구분)와
   frontend(screenrecord.js/runtime.js의 이미지 뷰어) 변경이 12차에는 빠짐 --
   스크린샷 파일이 carrotweb 로그탭에서 정상적으로 정지 이미지로 표시되는지
   미확인. 필요 시 다음 세션에서 추가 반영
3. 반영 스크립트의 python 감지 로직(Get-Command python)이 Windows Store
   더미 python.exe를 걸러내지 못하는 문제 -- `python --version` 결과에
   "Python 3" 포함 여부로 판정하도록 개선 필요 (9절 개정 후보, 사용자 승인 필요)
4. AutoRoadSpeedLimitOffset(기본값 -1) / SpeedFromPCM 실제 설정값 미확인
   (10차부터 이어지는 항목)
5. carrot-ms가 추가한 "모델 셀렉터" 코드는 아직 분석하지 않음
6. TurnSpeedControlMode=2 / EnableSpeedTF=0 / DisableDM=2 등 사용자 의도 확인
   (오래된 보류 항목, 일부는 안전 관련)

검증: 정적 분석 + 문법 검증(py_compile, Claude 샌드박스에서 실제 Python으로
확인) + diff 적용 실제 재현 테스트(LF/CRLF/BOM 조합)까지만 확인. 실차 검증
미실시.

주의사항:
- git diff는 반드시 --no-pager 또는 GIT_PAGER=cat과 함께 사용 (9차부터 계속
  유효)
- PowerShell here-string(@'...'@)은 마지막 줄 뒤 개행을 보존하지 않음 --
  [System.IO.File]::WriteAllText 등으로 파일을 쓸 때는 반드시 끝에 개행을
  붙여야 함(특히 diff/patch 파일에서 치명적, "corrupt patch" 원인). 향후
  스크립트의 Write-Utf8NoBom 헬퍼에는 이미 반영됨
- 이 사용자 PC에는 실제 Python이 설치되어 있지 않고 Windows App Execution
  Alias 더미 python.exe만 있음 -- `Get-Command python`만으로는 이를 걸러내지
  못하므로 스크립트의 py_compile 단계 결과가 실패로 나와도 실제 문법 오류가
  아닐 수 있음(9절 개정 후보)
- raw.githubusercontent.com은 CDN 캐시(최대 5분, cache-control max-age=300)가
  있어 push 직후 삭제/수정 확인 시 잠깐 이전 내용이 보일 수 있음(x-cache: HIT
  헤더로 판별 가능)
- Claude는 web_fetch 도구로는 ryujmin97/openpilot의 raw 파일에 직접 접근하지
  못했음(검색 결과에 없는 URL 제약) -- 대신 bash_tool의 네트워크 허용
  도메인(raw.githubusercontent.com, api.github.com 등)을 통해 curl로 직접
  조회/검증 가능함을 이번 세션에 확인. 앞으로 GitHub 파일 조회/검증은 이
  방법을 우선 사용

다음 작업 후보:
1. 실주행 재검증 (12차 신규 2건 + 8~10차 기존 2건 모두)
2. 스크린샷 backend/frontend(kind 구분, 이미지 뷰어) 추가 여부 결정 및 반영
3. AutoRoadSpeedLimitOffset/SpeedFromPCM 실제 설정값 확인
4. (선택) carrot-ms의 model_selector 코드 분석
5. (선택) 반영 스크립트 py_compile 감지 로직 개선(9절 개정, 사용자 승인 필요)
