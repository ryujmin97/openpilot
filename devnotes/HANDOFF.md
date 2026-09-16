# HANDOFF

Worker: Claude (52차 -- 스크린샷에서 차량명/시계/디버그/laneless/IP 등이 여전히 빠지는 원인 확정 + 캡처 위치 재수정)
Date: 2026-09-16
Repository: ryujmin97/openpilot
Code Branch: carrot-ryu (base: `258817e0ee30ae8fcf875823e18168ceb1e04448`, 51차 스크린샷 타이밍 수정 + 480p 다운스케일 스크립트가 이미 실행/push 완료된 상태에서 시작. 이번 세션 변경: hud_renderer.py/augmented_road_view.py/screenshot_button.py 3개 파일 -- 반영 스크립트 실행 대기)
Note Branch: carrot-ryu-note (base: `f9df022707b208618580fd2456fa2166026910c3`, 51차. 이 커밋으로 devnotes 갱신)
carrot-ms 마지막 검토/동기화 커밋(메시지 기준): 7차 체크포인트 이후 신규 23건 확인, WIP_SYNC.md 40차 체크포인트 반영 스크립트 실행 여부 미확인(계속 이월)

작업:
사용자가 51차 반영 스크립트 실행 후 실기기 사진 2장(1: 스크린샷 캡처 결과물, 2: 실기기 화면 직접 촬영)을 제공하며 처음에는 "오른쪽 HUD의 내용이 완전히 표시되지 않음"이라고 제보했다가, 곧바로 "화면의 오른쪽이 아니라 실제 화면 전체"라고 정정. 지침 문서 4절 0단계(git ls-remote SHA 고정)부터 시작, HANDOFF.md 확인 후 진행.

완료:
1. git ls-remote로 carrot-ryu HEAD가 `258817e0ee30ae8fcf875823e18168ceb1e04448`임을 확인 -- 사용자가 51차 스크립트를 이미 실행해 push까지 완료했음을 실증.
2. 사용자 제공 사진 2장을 항목별로 대조: 스크린샷(사진1)에는 hud_renderer.py가 그리는 CPU/MEM/VOLT 박스, 우측 "교차로" 경로안내 박스, 플롯 디버그("1.Accel (Y:a_ego, G:a_target, O:a_out)" + 0.00/0.00 그래프)는 실기기 사진(사진2)과 동일하게 정상 포함돼 있음을 확인. 반면 실기기 사진에만 있고 스크린샷에는 없는 요소를 특정: 좌상단 "HYUNDAI_GENESIS(CAMERA SCC)" 차량명, 좌상단 큰 시계("14:31:33"/"09-16(수)"), 우상단 "LD[100%,0.19], LT[100%,ON](3.46/0.07), SR(15.7,0.0)" 디버그 텍스트, 하단 "laneless | 1.8m | 3.2m | 2.3m" 상태 텍스트, 우측 하단 IP 주소("10.173.240.171").
3. 위 5개 요소가 전부 augmented_road_view.py의 `_draw_border_carrot()` 한 메서드에서 그려짐을 코드로 확인(`top_left`=차량명(carrot_param_cache.py의 CarName/HyundaiCameraSCC/NNFFModelName 조합), `top_right`=LD/LT/SR(liveDelay/liveTorqueParameters/liveParameters), `bottom`=laneless 상태(lateralPlan.latDebugText), `bottom_left`=git branch, `bottom_right`=IP(params_memory의 NetworkAddress)).
4. AugmentedRoadView._render()의 실제 호출 순서를 코드로 직접 확인: 카메라뷰 -> model_renderer -> **self._hud_renderer.render(rect)** -> alert_renderer.render() -> driver_state_renderer.render() -> end_scissor_mode() -> **self._draw_border_carrot(rect)**. 51차가 옮긴 캡처 호출(consume_pending_capture -> capture_onroad_screenshot)은 hud_renderer.render() *안에서* 실행되므로, 이 시점엔 alert/driver-state 오버레이와 _draw_border_carrot()의 모든 텍스트(차량명/LD·LT·SR/laneless/git branch/IP)가 아직 그려지기 전임을 확정(11절: 코드 근거로 확정, 추측 아님). 51차는 HudRenderer *내부*의 그리기 순서(date_time/tpms 등을 캡처보다 먼저)만 고쳤을 뿐, 캡처가 hud_renderer.render() 안에 있다는 더 바깥쪽 구조 문제는 그대로 남아 있었음.
5. hud_renderer.py: `_render()` 끝의 `if self._screenshot_button.consume_pending_capture(): capture_onroad_screenshot()` 블록을 제거하고, 대신 대기 플래그만 소비해 반환하는 공개 메서드 `consume_pending_screenshot_capture()`를 추가. 더 이상 쓰지 않는 `capture_onroad_screenshot` import도 제거.
6. augmented_road_view.py: `capture_onroad_screenshot` import 추가, `_render()`에서 `self._draw_border_carrot(rect)` 호출 *다음*(= 이 프레임에서 그려지는 모든 것이 끝난 시점)에 `if self._hud_renderer.consume_pending_screenshot_capture(): capture_onroad_screenshot()`를 추가.
7. screenshot_button.py: 클래스 docstring에 52차 변경 사유(캡처 소비 주체가 HudRenderer에서 AugmentedRoadView로 이동)를 추가해, 코드만 봐도 현재 구조를 알 수 있게 유지(18절).
8. 세 파일 모두 실제 GitHub 최신 코드(`git clone`)를 기준으로 Replace-Block 앵커 5곳이 정확히 1회씩 매치됨을 파이썬으로 직접 검증 후 교체, `py_compile` 통과 확인.

미완료 (다음 세션 이월):
1. [최우선, 신규] 이번 세션에서 전달한 스크립트 2개(carrot-ryu 코드, carrot-ryu-note devnotes)의 Termux 실행 결과(git push 로그) 확인.
2. [최우선, 신규] 실기기에서 스크린샷 버튼을 눌러 차량명/시계/LD·LT·SR/laneless/IP가 이번에는 전부 캡처 결과물에 포함되는지 실차 검증. 함께 alert(경고 알림)나 driver-state(운전자 모니터링) 오버레이가 떠 있는 상태에서 캡처했을 때도 정상 포함되는지 확인(이번 수정으로 이 두 렌더러도 캡처 이전에 그려지게 됨).
3. [이월, 51차] 480p(세로 기준) 다운스케일(rl.image_resize)이 실제로 동작하는지(파일 용량/해상도) 여전히 미확인 -- 51차부터 이월.
4. [이월, 47차] 가로/세로 방향(2160x1080 비율 유지 여부) 재확인.
5. [이월, 37차] 락 수정의 실제 동시성 재현 검증(의도적으로 거의 동시에 두 업로드 시도).
6. [이월, 34차] 도로명-신호과속 같은 줄 배치 확인(신호과속 배지가 나타나는 구간에서).
7. [이월] 28~30차 레이아웃 정밀 재검증.
8. [이월] "선택 다운로드" 버튼 실제 동작(다운로드 성공 여부) 여전히 미확인.
9. [이월] 실기기 터미널로 배포된 tools.js에 "web-gdrive-connect" 문자열 실제 존재 여부 확인(핵심 발견 16).
10. [이월] test_web_upload.py 실제 실행해 낡은 테스트 수 확인 -> 데드코드 3개 삭제/갱신.
11. [이월] docs/carrot_web_upload.md 갱신(Drive 기준).
12. [이월] carrot-ms 모델 셀렉터 코드 분석 착수. WIP_SYNC.md 40차 체크포인트 반영 확인 필요.
13. [신규, 낮은 우선순위] CURRENT_STATUS.md는 이번 세션에서 갱신하지 못함(세션 예산) -- 51차 기준 내용 그대로이므로 다음 세션에서 52차 반영 여부와 함께 갱신할 것(16절: devnotes-실제상태 괴리 방지).

검증: 세 파일에 대해 실제 GitHub 최신 코드 기준 anchor 5곳 모두 정확히 1회 매치 확인(스크립트 실행 시 파이썬으로 직접 검증, 1회가 아니면 아무것도 쓰지 않고 중단), py_compile 통과 확인. **실차 검증: 미실시** -- 다음 세션 최우선(차량명/시계/디버그/laneless/IP 포함 여부).

주의사항:
- 코드(carrot-ryu)와 devnotes(carrot-ryu-note) 반영 스크립트를 분리해서 전달함 -- 섞어서 실행하지 말 것.
- 사용자가 이번에도 Termux 사용을 요청 -- bash 스크립트로 전달(9절), core.autocrlf 관련 이슈 없음(파이썬 문자열 치환 + 1회 매치 검증으로 동일 수준 안전장치 적용).
- 51차는 "캡처가 HudRenderer 내부에서 date_time/tpms보다 먼저 실행된다"는 문제를 고쳤고, 52차는 "그 캡처 호출 자체가 AugmentedRoadView의 다른 렌더러(alert/driver-state)와 border 텍스트보다 더 앞서 실행된다"는, 한 단계 더 바깥쪽의 같은 계열 문제를 고친 것이다(11절: 두 번에 걸쳐 원인을 좁혀 나간 것이지, 51차가 틀렸던 것은 아님).
- 52차 변경은 "화면에 실제로 그려지는 모든 것이 캡처에 포함된다"를 아직 확정한 것이 아니라, 코드 조사로 남은 원인을 특정하고 그 원인을 제거하는 수정을 반영한 것이다(12절). 다음 세션은 실차 결과를 먼저 확인한 뒤 판단할 것.

다음 작업 후보:
1. 52차 변경 실차 검증(차량명/시계/디버그/laneless/IP 포함 여부, alert/driver-state 오버레이가 떠 있을 때도 정상 포함되는지) -- 최우선
2. 51차 480p 다운스케일 실차 검증(이월)
3. 47차 DPI 수정(가로/세로 방향) 재검증(이월)
4. 37차 락 동시성 재현 검증(의도적 동시 업로드 2회 시도)
5. 34차 도로명-신호과속 같은 줄 배치 확인(신호과속 구간 실주행 필요)
