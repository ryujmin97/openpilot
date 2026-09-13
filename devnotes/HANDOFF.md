# HANDOFF

Worker: Claude (세션 11)
Date: 2026-09-13
Repository: ryujmin97/openpilot
Code Branch: carrot-ryu (base commit: 10차 RES/+ 인게이지 안전장치 = e1e587b, 그 위에
  내용 없는 빈 커밋 2c33603 "token test" 존재)
Note Branch: carrot-ryu-note (11차 devnotes 반영, 이 커밋)
carrot-ms 마지막 검토/동기화 커밋(메시지 기준): 7차 세션과 동일, 신규 커밋 없음
(WIP_SYNC.md 참고, 이번 세션에서도 재확인하지 않음)

작업:
완료:
- 온로드 시계 초 단위 표시 (hud_renderer.py)
- 더블탭 캡쳐 스크린샷 + carrotweb 로그탭 연동 (augmented_road_view.py 신규
  더블탭 판정, screenshot_capture.py 신규 파일, config.py/catalog.py 백엔드 확장,
  screenrecord.js/runtime.js 프론트엔드 확장 + 로그탭 번들 재빌드)
- Claude 샌드박스에서 GitHub 최신 코드 기준 미리 패치 적용, py_compile/node --check/
  npm run build 통과 확인
- 9절 방식(PowerShell 스크립트, git apply + 신규 파일 생성 + npm run build)로 반영
  스크립트 작성해 전달 (11차 세션 중간에 Termux/PowerShell 착오 + .NET 현재디렉터리
  이슈로 두 차례 재작성)
- WIP.md에 11차 항목 기록 (이 파일과 함께)

미완료 / 다음 세션 우선순위:
1. **실주행 재검증 필요** — 이번 11차(시계 초단위, 더블탭 캡쳐) + 8~10차(route
   감속 근본수정, RES 인게이지 안전장치) 모두 실제 콤마 디바이스 주행으로 확인 안 됨
2. `AutoRoadSpeedLimitOffset`(기본값 -1) / `SpeedFromPCM` 실제 설정값 미확인
   (10차부터 이어지는 항목)
3. carrot-ms가 추가한 "모델 셀렉터" 코드는 아직 분석하지 않음
4. TurnSpeedControlMode=2 / EnableSpeedTF=0 / DisableDM=2 등 사용자 의도 확인
   (오래된 보류 항목, 일부는 안전 관련)
5. (신규, 낮은 우선순위) rl.take_screenshot()이 절대경로를 그대로 지원하는지는
   기존 사용례(상대경로 사용)만으로 추정했고 실기기에서 직접 확인되지 않음 —
   실주행 검증 시 스크린샷 파일이 실제로 지정 폴더에 생성되는지 함께 확인
6. (신규, 참고) PowerShell에서 Set-Location으로 이동해도 [System.IO.File] 계열
   .NET API는 프로세스의 실제 CurrentDirectory를 따르지 않아 상대경로가 예상과
   다른 곳으로 풀릴 수 있음 확인 — 앞으로 반영 스크립트는 항상 $Tmp 기준
   절대경로(Join-Path)로 파일을 써야 함 (9절에 반영 검토)

검증: 정적 분석 + 문법 검증(py_compile/node --check) + 프론트엔드 빌드(npm run
build) 성공까지만 확인. 실차 검증 미실시.

주의사항:
- git diff는 반드시 --no-pager 또는 GIT_PAGER=cat과 함께 사용 (9차에서 확인된
  이슈, 계속 유효)
- carrot-ryu HEAD에 "token test"라는 빈 커밋(변경 내용 없음, 아마 사용자의 git
  인증 테스트용)이 10차 커밋 위에 하나 더 있음을 확인 — 코드/devnotes에는 영향 없음
- 사용자는 PC(PowerShell) 환경에서 작업 중임을 이번 세션에 재확인
- PowerShell 스크립트에서 파일 쓰기는 상대경로 대신 항상 $Tmp 기준 절대경로 사용

다음 작업 후보:
1. 실주행 재검증 (11차 신규 2건 + 8~10차 기존 2건 모두)
2. AutoRoadSpeedLimitOffset/SpeedFromPCM 실제 설정값 확인
3. (선택) carrot-ms의 model_selector 코드 분석