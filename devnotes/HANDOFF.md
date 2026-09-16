# HANDOFF

Worker: Claude (54차 -- render-texture 재사용 스크린샷 캡처 재설계 구현, push/반영 검증 완료)
Date: 2026-09-16
Repository: ryujmin97/openpilot
Code Branch: carrot-ryu (base: `e4816edc2488fbd21f7241a44733aaf5d2113fbd`, 52차. 이번 세션 push 후: `e047beb3da61b6727a3ce82b8f18c1605fd55381`)
Note Branch: carrot-ryu-note (base: `340d30ed38f98c0b3a2296e0c3771b41bf1e7d0b`, 53차 시점 devnotes. 이 커밋으로 devnotes 갱신)
carrot-ms 마지막 검토/동기화 커밋(메시지 기준): 7차 체크포인트 이후 신규 23건 확인, WIP_SYNC.md 40차 체크포인트 반영 스크립트 실행 여부 미확인(계속 이월, 이번 세션 미착수)

작업:
53차에서 설계만 합의됐던 render-texture 재사용 스크린샷 캡처 재설계를 실제 코드로 구현. 반영 스크립트 작성 직전 carrot-ryu 최신 원본(HEAD `e4816edc`)을 다시 조회해 그 위에서 Replace-Block anchor를 구성(6절). 최초 반영 스크립트 실행 시 py_compile 검증에서 콘솔 출력 없이 조용히 중단되는 문제가 발생해 원인을 Windows PC의 `python3` 명령 문제로 진단/수정하고 재실행, 최종 push 및 전체 검증까지 완료.

완료:
1. `application.py`(공통 파일, `openpilot/system/ui/lib/`)에 `request_temp_capture(callback)` 신규 메서드를 3개 지점(Replace-Block)에 추가:
   - `__init__` 끝: `_temp_capture_pending`/`_temp_capture_callback`/`_temp_capture_owns_texture` 초기화 + `request_temp_capture()` 메서드 정의.
   - 렌더 루프 시작 지점: pending 캡처가 있고 `self._render_texture`가 없으면 기존 `_ensure_render_texture_for_recording()`으로 그 프레임만 임시 render texture 생성.
   - `end_texture_mode()` 이후, 녹화 프레임 추출과 동일한 지점: `rl.load_image_from_texture()`로 추출 -> 콜백 호출 -> 임시로 만든 texture라면 즉시 해제.
   - selfdrive 코드 import 없이 제네릭 유지(기존 레이어링 규칙, 10절 최소변경 원칙과 별개로 레이어 분리 원칙은 그대로 준수).
2. `openpilot/selfdrive/ui/onroad/screenshot_capture.py` 전체 재작성: `capture_onroad_screenshot()` -> `save_screenshot_image(image: rl.Image)`. 화면을 직접 읽지 않고, 이미 캡처된 이미지를 받아 480p(세로기준, 51차) 다운스케일 + PNG(50차 롤백 상태) export만 담당하도록 책임 축소.
3. `openpilot/selfdrive/ui/onroad/screenshot_button.py` 전체 재작성: `_on_click()`이 `gui_app.request_temp_capture(self._on_frame_captured)`만 호출하도록 단순화, pending 플래그/consume 로직 완전 제거.
4. `openpilot/selfdrive/ui/onroad/hud_renderer.py`에서 `consume_pending_screenshot_capture()` 제거(Replace-Block 1곳).
5. `openpilot/selfdrive/ui/onroad/augmented_road_view.py`에서 51·52차가 추가했던 `capture_onroad_screenshot` import 및 프레임 끝 호출부 원복(Replace-Block 2곳).
6. **진단**: 최초 반영 스크립트(`54cha_code_carrot_ryu.ps1`) 실행 시 6개 Replace-Block/전체교체는 전부 "OK"로 성공했으나, py_compile 검증 단계에서 어떤 에러 텍스트도 없이 `[중단] py_compile 실패: application.py`로 종료(commit/push 안 됨 -- 스크립트 방어 로직은 의도대로 정상 동작). Linux sandbox에서 동일한 3개 Replace-Block을 그대로 재현해 `python3 -m py_compile` 실행 -> **정상 통과(exit 0)**. `Callable`도 파일에 이미 `from collections.abc import Callable, Iterable`로 import돼 있음을 확인 -- 반영된 코드 자체에는 결함이 없음을 확정(11절).
7. **원인 확정(핵심 발견 37)**: Windows PC의 `python3` 명령으로 추정. python.org 설치본은 보통 `python.exe`/`py.exe`(런처)만 PATH에 등록하고 `python3.exe`는 없는 경우가 흔한데, 이 상태에서 `python3`를 호출하면 Windows 10/11의 앱 실행 별칭(Microsoft Store 유도 스텁)이 가로채 콘솔 출력 없이 조용히 실패 -- 로그에 파이썬 에러가 전혀 안 찍힌 정황과 정확히 일치.
8. **수정**: 반영 스크립트에 `Get-PythonCmd` 함수 추가 -- `py -3` -> `python3` -> `python` 순으로 실제 `--version` 출력이 나오는 후보를 자동탐지해 py_compile 호출에 사용. 나머지 5개 파일 반영 내용은 원본과 100% 동일. 9절 버전표시 규칙에 따라 파일명 `54cha_code_carrot_ryu-v2.ps1`로 재전달.
9. 사용자가 v2 스크립트 실행 -> `(python 실행 파일 감지: ...)` 로그와 함께 py_compile 전체 통과 -> `git push` 로그(`e4816edc..e047beb3 carrot-ryu -> carrot-ryu`)로 커밋/push 성공 확인.
10. **push 후 검증(6절/16절 시퀀스)**: `git ls-remote`로 실제 HEAD가 `e047beb3`임을 재확인 -> commit-SHA 고정 raw URL로 5개 파일 전체 재조회 -> 5개 파일 전부 `python3 -m py_compile` 재통과 -> grep으로 핵심 마커 확인: `application.py`의 `request_temp_capture`/`_temp_capture_pending`/`_temp_capture_owns_texture` 존재, `screenshot_capture.py`의 `save_screenshot_image` 존재, `screenshot_button.py`의 `gui_app.request_temp_capture()` 호출 존재, `hud_renderer.py`의 `consume_pending_screenshot_capture` 0건(완전 제거), `augmented_road_view.py`의 `capture_onroad_screenshot` 0건(완전 제거) -- 실제 반영 내용이 설계·의도와 정확히 일치함을 실증.
11. devnotes(WIP.md/HANDOFF.md/CURRENT_STATUS.md) 갱신, 핵심 발견 37 신규 기록.

미완료 (다음 세션 이월):
1. [최우선] 실차 검증 -- 스크린샷 버튼을 눌러 border HUD(차량명/시계/LD·LT·SR/laneless/git branch/IP) 전부가 결과 이미지에 포함되는지, 480p 다운스케일과 PNG 저장이 정상 동작하는지 확인. 구조가 완전히 바뀌었으므로 49~52차/47차/51차의 개별 이월 항목(HUD 누락, DPI/방향, JPG export 실패, 480p)은 전부 이번 한 번의 실차 테스트로 함께 흡수해 확인.
2. [이월] 핵심 발견 31 재발 방지 제안(스크립트 파일명 버전 표시 규칙화) 및 이번 핵심 발견 37의 `Get-PythonCmd` 방식을 지침 문서 9절에 정식 규칙으로 채택할지 사용자 확인(19절 절차 -- 변경 이유/기존 규칙/변경안/승인/반영 순서).
3. [이월, 37차] 락 수정의 실제 동시성 재현 검증(의도적으로 거의 동시에 두 업로드 시도).
4. [이월, 34차] 도로명-신호과속 같은 줄 배치 확인(신호과속 배지가 나타나는 구간에서).
5. [이월] 28~30차 레이아웃 정밀 재검증.
6. [이월] "선택 다운로드" 버튼 실제 동작(다운로드 성공 여부) 여전히 미확인.
7. [이월] test_web_upload.py 실제 실행해 낡은 테스트 수 확인 -> 데드코드 3개 삭제/갱신.
8. [이월] docs/carrot_web_upload.md 갱신(Drive 기준).
9. [이월] carrot-ms 모델 셀렉터 코드 분석 착수. WIP_SYNC.md 40차 체크포인트 반영 확인 필요.

검증: 5개 파일 전부 `python3 -m py_compile` 통과(스크립트 내장 검증 1회 + push 후 SHA고정 재조회본 재검증 1회, 총 2회). grep으로 핵심 마커(추가/제거 대상) 존재 여부 전부 의도와 일치 확인. **실차 검증: 미실시**.

주의사항:
- Windows PC 환경에서 `python3` 명령이 항상 보장되지 않는다는 것이 이번 세션에서 처음 확인됨(핵심 발견 37) -- 앞으로 py_compile을 포함하는 반영 스크립트는 `Get-PythonCmd` 같은 자동탐지 방식을 기본으로 쓰는 것을 권장. 다만 지침 문서 9절 자체를 바꾸려면 19절 절차(사용자 승인)가 먼저 필요해 이번엔 스크립트 레벨에서만 대응.
- 이번 재설계로 51·52차가 만들었던 `augmented_road_view.py`의 캡처 호출부는 완전히 원복됐으므로, 그 두 회차의 코드 변경 이력은 "현재 코드에는 반영돼 있지 않은 과거 시도"로 이해할 것(devnotes 기록 자체는 7절 규칙상 수정하지 않고 그대로 둠).
- 다음 세션은 실차 검증 결과에 따라 갈림: border HUD가 전부 포함되면 49~52차 계열 이월 항목은 전부 해소로 정리, 일부라도 빠지면 이번 재설계의 어느 지점(임시 texture 생성 타이밍, 콜백 실행 시점 등)이 원인인지 `application.py`의 render() 루프를 다시 코드로 대조할 것.

다음 작업 후보:
1. render-texture 재사용 스크린샷 재설계 실차 검증 -- 최우선
2. 핵심 발견 37(Get-PythonCmd) 지침 문서 9절 정식 반영 여부 사용자 확인
3. 37차 락 수정 동시성 재현 검증(이월)
4. 34차 도로명-신호과속 같은 줄 배치 확인(이월)
5. 28~30차 레이아웃 정밀 재검증(이월)
