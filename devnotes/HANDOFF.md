# HANDOFF

Worker: Claude (55차 -- 54차 render-texture 스크린샷의 상하반전 버그 원인 확정/수정, 반영 스크립트 실행 대기)
Date: 2026-09-16
Repository: ryujmin97/openpilot
Code Branch: carrot-ryu (base: `e047beb3da61b6727a3ce82b8f18c1605fd55381`, 54차)
Note Branch: carrot-ryu-note (base: `340d30ed38f98c0b3a2296e0c3771b41bf1e7d0b`, 53차 시점 devnotes. 이 커밋으로 devnotes 갱신)
carrot-ms 마지막 검토/동기화 커밋(메시지 기준): 7차 체크포인트 이후 신규 23건 확인, WIP_SYNC.md 40차 체크포인트 반영 스크립트 실행 여부 미확인(계속 이월, 이번 세션 미착수)

작업:
사용자가 54차 반영분(render-texture 재사용 스크린샷 캡처)을 실기기에서 테스트한 스크린샷을 제공, 480p 다운스케일/PNG 저장 자체는 정상 동작했으나 이미지가 상하반전(사용자 보고: "화면이 상하좌우 뒤바뀜")으로 저장된다고 제보. application.py를 코드로 조사해 원인을 추측 없이 확정(11절)한 뒤 최소 수정 반영.

완료:
1. **원인 확정**: `application.py`의 영상 녹화 경로 2곳(카메라 스트림 인코딩, 화면 인코딩)이 모두 ffmpeg에 `"-vf", "vflip,format=yuv420p"`를 걸고 있음을 확인 -- 이는 OpenGL render texture(`rl.load_render_texture()`)를 `rl.load_image_from_texture()`로 읽으면 픽셀이 아래->위(OpenGL 텍스처 좌표계) 순서로 나오기 때문에, 영상 파이프라인이 이미 이 문제를 알고 보정하고 있었다는 뜻. 54차가 스크린샷 캡처를 `rl.load_image_from_screen()`(화면 그대로, 보정 불필요)에서 `rl.load_image_from_texture()`(render texture, 보정 필요)로 바꾸면서, 영상 경로에 있던 이 vflip 보정을 스크린샷 경로(`screenshot_capture.py`)에는 옮겨오지 않았던 것이 근본 원인.
2. `openpilot/selfdrive/ui/onroad/screenshot_capture.py`의 `save_screenshot_image()` 맨 앞(유효성 검사 직후, 리사이즈/export 전)에 `rl.image_flip_vertical(image)` 한 줄 추가(Replace-Block 1곳, anchor 1회 매치 확인, 6절에 따라 반영 스크립트 작성 직전 GitHub 최신본 재조회 후 구성).
3. 다른 4개 파일(application.py, screenshot_button.py, hud_renderer.py, augmented_road_view.py)은 이번 버그와 무관해 손대지 않음(10절 최소변경 원칙).

미완료 (다음 세션 이월):
1. [최우선] 반영 스크립트(`55cha_code_carrot_ryu_termux.sh`) 실행 및 실차 검증 -- 스크린샷이 정상 방향(상하 정상)으로 저장되는지 확인. border HUD 포함 여부/480p/PNG는 54차에서 이미 확인됐으므로 이번엔 방향만 확인하면 됨.
2. [이월] 핵심 발견 31 재발 방지 제안(스크립트 파일명 버전 표시 규칙화) 및 핵심 발견 37의 `Get-PythonCmd` 방식을 지침 문서 9절에 정식 규칙으로 채택할지 사용자 확인(19절 절차).
3. [이월, 37차] 락 수정의 실제 동시성 재현 검증(의도적으로 거의 동시에 두 업로드 시도).
4. [이월, 34차] 도로명-신호과속 같은 줄 배치 확인(신호과속 배지가 나타나는 구간에서).
5. [이월] 28~30차 레이아웃 정밀 재검증.
6. [이월] "선택 다운로드" 버튼 실제 동작(다운로드 성공 여부) 여전히 미확인.
7. [이월] test_web_upload.py 실제 실행해 낡은 테스트 수 확인 -> 데드코드 3개 삭제/갱신.
8. [이월] docs/carrot_web_upload.md 갱신(Drive 기준).
9. [이월] carrot-ms 모델 셀렉터 코드 분석 착수. WIP_SYNC.md 40차 체크포인트 반영 확인 필요.

검증: 새 anchor 문자열이 GitHub 최신본(commit `e047beb3`)에서 정확히 1회 매치됨을 사전 확인(Python `str.count()`). 코드 자체(raylib `rl.image_flip_vertical` 존재 여부)는 이 세션에서 실제 실행 검증하지 못함(9절 py_compile은 구문 오류만 잡고 raylib 바인딩 존재 여부는 잡지 못하므로, 스크립트 실행 로그에서 확인 필요). **실차 검증: 미실시**.

주의사항:
- 이 버그는 raylib/OpenGL의 일반적인 텍스처 좌표계 특성(텍스처 원점이 좌하단)에서 오는 것으로, 54차 이후 render texture를 읽는 경로라면 항상 재발할 수 있는 클래스의 문제. 앞으로 `rl.load_image_from_texture()`를 새로 쓰는 코드가 있으면 이 vflip 보정이 필요한지 먼저 확인할 것.
- 사용자가 이번에도 Termux 환경임을 명시(51차와 동일 패턴) -- PowerShell이 아닌 bash 스크립트로 전달함(0절 기본값은 PowerShell이지만 사용자가 명시하면 Termux로 전환).
- rl.image_flip_vertical()이 pyray 바인딩에 실제로 존재하는지는 raylib 공식 API(ImageFlipVertical)에 대응하는 이름 규칙(다른 곳에서 이미 쓰이는 rl.image_flip_horizontal과 동일 패턴)으로 추정한 것이며, 사용자 PC/폰에 설치된 실제 pyray 버전에서 AttributeError가 나면 즉시 보고받아야 함(11절, 확정 아님으로 표기).

다음 작업 후보:
1. 55차 반영 스크립트 실행 + 스크린샷 방향 실차 검증 -- 최우선
2. 핵심 발견 37(Get-PythonCmd)/핵심 발견 31 지침 문서 9절 정식 반영 여부 사용자 확인
3. 37차 락 수정 동시성 재현 검증(이월)
4. 34차 도로명-신호과속 같은 줄 배치 확인(이월)
5. 28~30차 레이아웃 정밀 재검증(이월)
