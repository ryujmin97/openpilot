# HANDOFF

Worker: Claude (51차 -- 스크린샷 캡처 타이밍 버그(시계/온도 HUD 누락) 수정 + 480p 다운스케일, Termux 전달)
Date: 2026-09-16
Repository: ryujmin97/openpilot
Code Branch: carrot-ryu (base: `08c7e9ae79641c56e67c426ef156267d1e0bb0cc`, 50차 PNG 롤백 스크립트가 이미 실행/push 완료된 상태에서 시작. 이번 세션 변경: screenshot_button.py/hud_renderer.py/screenshot_capture.py 3개 파일 -- 반영 스크립트 실행 대기)
Note Branch: carrot-ryu-note (base: `a3732fc8e163eb10fbf0c85769bc238249bf460f`, 50차. 이 커밋으로 devnotes 갱신)
carrot-ms 마지막 검토/동기화 커밋(메시지 기준): 7차 체크포인트 이후 신규 23건 확인, WIP_SYNC.md 40차 체크포인트 반영 스크립트 실행 여부 미확인(계속 이월)

작업:
사용자가 실기기 사진 2장(1: 시계/온도 HUD 없이 배경 카메라 화면만 담긴 스크린샷 결과물, 2: carrotweb 로그탭에 screenshot_2... 파일 두 개(4.9MB/4.6MB)가 실제로 목록에 잡힌 화면)을 제공하며 "캡쳐는 되는데 시간, 온도 등 UI 컨텐츠는 안나옴. 480p로 해상도도 낮춰서 코딩. 폰 termux 명령어로"라고 요청. 지침 문서 4절 0단계(git ls-remote SHA 고정)부터 시작, HANDOFF.md/CURRENT_STATUS.md 확인 후 진행.

완료:
1. git ls-remote로 carrot-ryu HEAD가 08c7e9ae79641c56e67c426ef156267d1e0bb0cc임을 확인 -- 사용자가 50차 PNG 롤백 스크립트를 이미 실행해 push까지 완료했음을 실증(50차 미완료 1,2번 해소: PNG export 성공 확정, JPG export 미지원 가설 확정).
2. 사용자 제공 로그탭 스크린샷의 파일 용량(4.9MB/4.6MB, PNG 특성과 일치)으로 50차 실차 검증(PNG export 성공)을 정황적으로 재확인.
3. hud_renderer.py의 _render() 호출 순서를 코드로 직접 확인: self._screenshot_button.render(...)가 self._draw_date_time(rect) / self._draw_tpms(rect) / self._draw_egpu_badge(rect) / self._draw_cruise_speed_animation(rect)보다 먼저 실행됨을 확정. 기존 ScreenshotButton._on_click()은 클릭 즉시 capture_onroad_screenshot()(내부에서 rl.load_image_from_screen()으로 그 순간의 프레임버퍼를 읽음)을 호출하는 구조라, 아직 그려지지 않은 시계/온도 등 HUD가 캡처에서 빠지는 것이 코드상 필연적임을 실증(사용자 제공 사진 1이 HUD 없이 배경만 나온 것과 정확히 일치, 11절 근거).
4. screenshot_button.py: _on_click()이 즉시 캡처하지 않고 _pending_capture 플래그만 세우도록 변경, consume_pending_capture() 메서드 추가(호출자가 한 번만 소비).
5. hud_renderer.py: import에 capture_onroad_screenshot 추가, _render() 끝(_draw_cruise_speed_animation(rect) 다음)에서 self._screenshot_button.consume_pending_capture()가 True면 그 시점에 capture_onroad_screenshot()을 호출하도록 이동 -- 이 프레임의 모든 HUD를 그린 뒤 캡처하므로 시계/온도가 포함되어야 한다.
6. screenshot_capture.py: 저장 직전 rl.image_resize()로 세로 480px(MAX_SCREENSHOT_HEIGHT) 기준 비율 유지 다운스케일 추가. 도크스트링에 47~50차 배경(과거 기록)은 그대로 두고 51차 변경 사유만 추가(18절, 과거 기록 보존).
7. 세 파일에 대해 Python으로 직접 시뮬레이션: screenshot_button.py/screenshot_capture.py는 전체 교체(소규모 파일, 9절), hud_renderer.py는 Replace-Block 앵커 2곳(import 1곳, _render() 끝 1곳) 모두 정확히 1회 매치 확인.
8. 사용자가 이번 세션에서 Termux 사용을 명시적으로 요청(9절 "Termux는 사용자가 명시할 때만") -- 기본 PowerShell 대신 bash(Termux) 스크립트로 작성해 전달(코드: 51cha_code_carrot_ryu.sh, devnotes: 51cha_devnotes_carrot_ryu_note.sh, 9절 원칙에 따라 분리).

미완료 (다음 세션 이월):
1. [최우선, 신규] 이번 세션에서 전달한 스크립트 2개(carrot-ryu 코드, carrot-ryu-note devnotes)의 Termux 실행 결과(git push 로그) 확인.
2. [최우선, 신규] 실기기에서 스크린샷 버튼을 눌러 (a) 시계/온도 등 HUD가 이제 캡처 결과물에 실제로 포함되는지, (b) 저장된 파일이 480p 근처(세로 480px)로 줄었는지 두 가지를 함께 실차 검증 -- rl.image_resize()가 이 raylib 빌드(comma-deps-raylib==6.0.0.1.post101)에서 실제로 정상 동작하는지도 이번이 최초 검증.
3. [이월, 47차] 가로/세로 방향(2160x1080 비율 유지 여부)도 480p 리사이즈 후 함께 재확인.
4. [이월, 37차] 락 수정의 실제 동시성 재현 검증(의도적으로 거의 동시에 두 업로드 시도).
5. [이월, 34차] 도로명-신호과속 같은 줄 배치 확인(신호과속 배지가 나타나는 구간에서).
6. [이월] 28~30차 레이아웃 정밀 재검증.
7. [이월] "선택 다운로드" 버튼 실제 동작(다운로드 성공 여부) 여전히 미확인.
8. [이월] 실기기 터미널로 배포된 tools.js에 "web-gdrive-connect" 문자열 실제 존재 여부 확인(핵심 발견 16).
9. [이월] test_web_upload.py 실제 실행해 낡은 테스트 수 확인 -> 데드코드 3개 삭제/갱신.
10. [이월] docs/carrot_web_upload.md 갱신(Drive 기준).
11. [이월] carrot-ms 모델 셀렉터 코드 분석 착수. WIP_SYNC.md 40차 체크포인트 반영 확인 필요.

검증: 스크립트 자체에 py_compile 통과 확인 포함, hud_renderer.py Replace-Block 매치 카운트 2곳 모두 1회씩 확인(스크립트 실행 시 Python으로 직접 검증, 1회가 아니면 아무것도 쓰지 않고 중단). **실차 검증: 미실시** -- 다음 세션 최우선(시계/온도 포함 여부, 480p 리사이즈 실제 동작 여부).

주의사항:
- 코드(carrot-ryu)와 devnotes(carrot-ryu-note) 반영 스크립트를 분리해서 전달함 -- 섞어서 실행하지 말 것.
- 이번 전달 형식은 PowerShell이 아니라 Termux(bash)다 -- 사용자가 이번 세션에서 명시적으로 요청했기 때문(9절). PowerShell 전용 규칙(core.autocrlf, .ps1 UTF-8 BOM 등)은 이번 스크립트에는 해당 사항이 없으나, 대신 bash set -euo pipefail과 파이썬 앵커 1회 매치 검증으로 동일한 수준의 안전장치를 적용함.
- rl.image_resize() 호출이 이 raylib 빌드에서 예상과 다르게 동작하더라도, 함수 전체가 이미 try/except로 감싸여 있어 실패 시 조용히 스크린샷 저장만 실패하고 주행에는 영향이 없다(12절, 코드 자체 안전장치이며 실차 검증은 아님).
- 51차 변경은 "시계/온도 HUD가 캡처에 포함된다"를 아직 확정한 것이 아니라, 코드 조사로 원인을 특정하고 그 원인을 제거하는 수정을 반영한 것이다(11절). 다음 세션은 실차 결과를 먼저 확인한 뒤 판단할 것.

다음 작업 후보:
1. 51차 변경 실차 검증(시계/온도 HUD 포함 여부, 480p 리사이즈 동작 여부) -- 최우선
2. 47차 DPI 수정(가로/세로 방향) 480p 리사이즈 후 재검증(이월)
3. 37차 락 동시성 재현 검증(의도적 동시 업로드 2회 시도)
4. 34차 도로명-신호과속 같은 줄 배치 확인(신호과속 구간 실주행 필요)
