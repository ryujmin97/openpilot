# HANDOFF

Worker: Claude (53차 -- 52차 push 확인 + 스크린샷 캡처 근본 재설계 방향 합의, 코드 변경 없음)
Date: 2026-09-16
Repository: ryujmin97/openpilot
Code Branch: carrot-ryu (base: `e4816edc2488fbd21f7241a44733aaf5d2113fbd`, 52차 캡처 위치 재수정. 이번 세션은 코드 변경 없음 -- carrot-ryu는 세션 시작 시와 동일)
Note Branch: carrot-ryu-note (base: `57062bb146744d003db080b44a83390bff59aede`, 52차 시점 devnotes. 이 커밋으로 devnotes 갱신)
carrot-ms 마지막 검토/동기화 커밋(메시지 기준): 7차 체크포인트 이후 신규 23건 확인, WIP_SYNC.md 40차 체크포인트 반영 스크립트 실행 여부 미확인(계속 이월)

작업:
지침 문서 4절 0단계(git ls-remote SHA 고정)로 시작, 체크포인트에서 carrot-ryu HEAD가 이미 `e4816edc`(52차)임을 확인 -- 52차 반영 스크립트가 세션 사이에 이미 실행/push 완료돼 있었음(devnotes에는 "push 대기"로 남아있던 괴리, 16절/핵심 발견 27과 동일 패턴). 이어서 52차 수정 이후에도 실기기 스크린샷에서 border 관련 HUD(차량명/시계/LD·LT·SR/laneless/git branch/IP)가 여전히 빠진다는 전제 하에, 화면녹화(정상)와 스크린샷(계속 실패)의 구조적 차이를 코드로 분석하고 근본 재설계 방향에 합의.

완료:
1. `git ls-remote`로 carrot-ryu HEAD(`e4816edc`) 확인 + GitHub API로 커밋 메시지("52cha: move screenshot capture trigger to end of AugmentedRoadView frame...")를 대조해 52차가 실제로 push 완료됐음을 실증.
2. carrot-ryu-note HEAD(`57062bb1`)는 세션 시작 전후로 변화 없음(체크포인트 중 HANDOFF 본문 안의 "이전 base" 참조 텍스트를 현재 HEAD로 순간 오인했다가, 재확인으로 착오였음을 세션 내에서 스스로 정정).
3. `application.py` 코드를 직접 확인해 화면녹화와 스크린샷의 구조적 차이를 확정:
   - 녹화 중에는 위젯 트리를 화면에 직접 그리지 않고 오프스크린 render texture에 그린 뒤(`begin_texture_mode()`~`end_texture_mode()`), `end_texture_mode()` 호출 뒤(그 프레임 내용이 텍스처에 확실히 다 쓰인 시점)에 `rl.load_image_from_texture()`로 읽는다 -- 순서가 구조적으로 보장됨.
   - 스크린샷은 녹화 중이 아닐 때 render texture 자체가 없는 상태에서, 위젯 렌더 콜백 한가운데(51·52차가 호출 위치를 옮겨도 여전히 프레임이 완성되기 전)에 `rl.load_image_from_screen()`으로 화면을 직접 읽어 raylib 배치 플러시 타이밍에 구조적으로 취약함.
4. 해결 방향 합의: "스크린샷 버튼을 누르면 녹화 로직으로 딱 1프레임만 임시 render texture에 떠서 이미지로 저장"(사용자 제안). 구체 설계:
   1. `GuiApplication`에 스크린샷 pending 플래그 추가.
   2. 렌더 루프 시작 시, pending 스크린샷이 있고 현재 녹화 중이 아니어서 `self._render_texture`가 없으면, 기존 `_ensure_render_texture_for_recording()`과 같은 패턴으로 그 프레임만 임시 render texture 생성 -- 자동으로 녹화와 동일한 `begin_texture_mode()` 경로를 타게 됨.
   3. `end_texture_mode()` 직후(녹화가 프레임을 추출하는 지점과 정확히 동일한 위치)에서 pending 스크린샷이 있으면 `rl.load_image_from_texture()`로 해당 프레임을 가져와 기존 480p 다운스케일+`export_image` 로직을 그대로 재사용해 저장.
   4. 이미 녹화 중일 때 스크린샷 버튼을 누른 경우는 별도 텍스처 생성 없이 같은 프레임을 한 번 더 추출.
   5. 스크린샷 때문에 임시로 만든 render texture는, 녹화 중이 아니라면 캡처 직후(다음 프레임 시작 전) `unload_render_texture()`로 정리 -- 평소엔 화면에 직접 그리는 기존 경로 유지, 스크린샷 순간에만 텍스처 경로로 잠깐 전환.
5. 이 설계는 51·52차보다 범위가 넓어(공통 파일 `application.py` 포함) 사용자에게 진행 여부를 확인, 사용자가 다음 세션에 구현하기로 결정 -- 이번 세션은 코드 변경 없이 설계 합의까지만 진행.
6. devnotes(WIP.md/HANDOFF.md/CURRENT_STATUS.md) 갱신 -- 52차 push 확인 사실과 53차 설계 합의 내용을 반영. WIP.md의 기존 "52차 (코드 완료, push 대기)" 표기는 규칙상(7절, 기존 회차 수정 금지) 그대로 두고, 53차 새 회차에서 실제 상태를 정정 기록.

미완료 (다음 세션 이월):
1. [최우선, 신규] 53차에서 합의된 render-texture 재사용 스크린샷 재설계를 실제 코드로 구현: `application.py`, `hud_renderer.py`, `screenshot_button.py`, `screenshot_capture.py` 대상. 51·52차가 수정한 `augmented_road_view.py`의 캡처 호출부는 이번 재설계로 되돌릴 예정.
2. [이월] 52차 캡처 위치 수정(border HUD 포함 여부) 실차 검증 -- 다만 위 재설계로 대체될 가능성이 높아 우선순위는 1번 다음.
3. [이월, 51차] 시계/온도 HUD 포함 여부, 480p 다운스케일(rl.image_resize) 실제 동작 여부(파일 용량/해상도) 미확인.
4. [이월, 50차] 저장 확장자 `.jpg`->`.png` 롤백 실차 검증으로 JPG export 미지원 가설 확정/기각.
5. [이월, 47차] 가로/세로 방향(2160x1080 비율 유지 여부) 재확인.
6. [이월, 37차] 락 수정의 실제 동시성 재현 검증(의도적으로 거의 동시에 두 업로드 시도).
7. [이월, 34차] 도로명-신호과속 같은 줄 배치 확인(신호과속 배지가 나타나는 구간에서).
8. [이월] 28~30차 레이아웃 정밀 재검증.
9. [이월] "선택 다운로드" 버튼 실제 동작(다운로드 성공 여부) 여전히 미확인.
10. [이월] test_web_upload.py 실제 실행해 낡은 테스트 수 확인 -> 데드코드 3개 삭제/갱신.
11. [이월] docs/carrot_web_upload.md 갱신(Drive 기준).
12. [이월] carrot-ms 모델 셀렉터 코드 분석 착수. WIP_SYNC.md 40차 체크포인트 반영 확인 필요.

검증: 이번 세션은 코드 변경이 없어 py_compile 등 정적 검증 대상 없음. **실차 검증: 미실시**(설계 논의만 진행됨).

주의사항:
- 52차는 이미 push 완료된 상태였으나 devnotes(HANDOFF/CURRENT_STATUS)에는 "실행 대기"로 남아있었음(16절/핵심 발견 27과 동일 패턴) -- 이번 세션에서 바로잡음.
- 다음 세션은 위 render-texture 재사용 설계 그대로 구현에 착수. 세션 라벨은 "53차 계속" 또는 "54차" 중 세션 시작 시 실제 GitHub 최신 상태(다른 경로로 이미 반영된 것이 없는지)를 먼저 확인한 뒤 정한다(16절/핵심 발견 22와 동일 원칙).
- 이번 재설계는 application.py(공통 파일)를 건드리므로, 반영 스크립트 작성 전 최신 원본을 다시 조회해 anchor를 구성할 것(6절).

다음 작업 후보:
1. render-texture 재사용 스크린샷 재설계 구현(application.py/hud_renderer.py/screenshot_button.py/screenshot_capture.py, augmented_road_view.py 캡처 호출부 원복) -- 최우선
2. 52차 캡처 위치 수정 실차 검증(재설계 구현과 함께 또는 그 이후)
3. 51차 480p 다운스케일 실차 검증(이월)
4. 50차 PNG 롤백 실차 검증(이월)
5. 47차 DPI 수정(가로/세로 방향) 재검증(이월)
