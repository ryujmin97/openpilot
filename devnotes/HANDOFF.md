# HANDOFF

Worker: Claude (63차 -- 20절 이식 항목 3·4 재적용: 온로드 시계 초단위 표시 + 스크린샷 버튼(12차, 684b30d 원본)을 새 베이스(706efb47) 위에 재적용. 착수 스크립트가 CRLF/LF 불일치로 한 차례 중단됐다가 원인 확정 후 재시도로 반영 성공)
Date: 2026-09-17
Repository: ryujmin97/openpilot
Code Branch: carrot-ryu (base: `429f105e16853b5230d7eb7a082de2b817a3d8e9`, 62차 HEAD `706efb47b81cf9cb02888ee536a156d8f1fc1d91` 위에 12차 원본 재적용 커밋 추가)
Note Branch: carrot-ryu-note (base: `88411ef9cf7c1b3b72a5754b41c3484d510b9e8e`, 62차 devnotes. 이 커밋으로 devnotes 갱신)
carrot-ms 마지막 검토/동기화 커밋(메시지 기준): `706efb47b81cf9cb02888ee536a156d8f1fc1d91`(61차 20절 리셋 베이스, 변경 없음).

작업:
62차에서 확정된 다음 작업(20절 이식 항목 1번: 온로드 시계 초단위 표시 + 스크린샷 버튼, 12차 684b30d 기준)을 착수. 첫 반영 스크립트(reapply_12cha.ps1)가 hud_renderer.py의 5번 Replace-Block("render screenshot button", 여러 줄 anchor)에서 "expected 1 match, found 0"으로 중단됨(commit/push 이전 단계라 GitHub에는 아무 영향 없었음, 안전). 사용자가 제공한 진단 결과(Select-String, Contains 비교)로 원인을 확정: 저장소 루트 `.gitattributes`의 `* text=auto` 때문에, `git clone --config core.autocrlf=false`를 줘도 일부 Windows Git 환경에서는 체크아웃 시점에 CRLF로 변환될 수 있음(GitHub 원본 blob 자체는 LF임을 raw 조회로 직접 확인 -- 이 세션에서 재확인). 여러 줄에 걸친 anchor(5·6·7번)만 이 변환에 취약하고 한 줄짜리(1~4번)는 우연히 문제없이 통과했던 것. 지침 9절이 이미 명시한 "매칭 전 CRLF→LF 정규화 병행" 방어가 이 스크립트에는 누락돼 있던 것이 근본 원인.

완료:
1. Replace-Block 함수에 CRLF→LF 정규화 매칭/치환 로직을 추가(9절 기존 원칙을 실제로 구현), sandbox에서 새 베이스(706efb47) 파일에 대해 7개 블록 전부 + 신규 파일 2개(screenshot_button.py, screenshot_capture.py)를 재현해 정확히 1회 매치 + `py_compile` 통과를 사전에 확인.
2. 사전 검증으로 `ScreenshotButton`이 쓰는 `Widget.set_click_callback`/`is_pressed`(openpilot/system/ui/widgets/__init__.py)와 `SCREEN_RECORDING_DIRS[1]`("/data/media/0/screenrecord", openpilot/selfdrive/carrot/server/config.py)이 새 베이스에서도 그대로 존재함을 확인(12차 이후 이 API들은 바뀌지 않음).
3. 수정된 스크립트(reapply_12cha-v2.ps1, 이름에 버전 표시)를 사용자가 실행, commit `429f105e`로 carrot-ryu에 push 완료(로그: `706efb47..429f105e  carrot-ryu -> carrot-ryu`).
4. `git ls-remote`(carrot-ryu=429f105e)와 `github.com/.../commit/429f105e....diff`(API rate limit 회피, 핵심 발견 21/25와 동일 수단) 직접 조회로 실제 반영 내용이 의도한 3개 파일(hud_renderer.py 7곳 수정, screenshot_button.py/screenshot_capture.py 신규)과 정확히 일치함을 확인.
5. carrot-ryu-v1 "코드 수정 현황" 항목 3(온로드 시계 초단위+스크린샷 버튼)을 "재반영 완료(commit 429f105e)"로 CURRENT_STATUS.md에 개별 갱신(HANDOFF.md 62차 지침대로).

미완료(사소, 낮은 우선순위):
- diff 확인 중 screenshot_button.py/screenshot_capture.py 두 신규 파일 모두 파일 끝 개행이 없음("No newline at end of file")을 발견. 기능에는 영향 없음(Python 문법상 문제 없음, py_compile 통과 확인됨). 다음에 이 파일들을 다시 건드릴 때 함께 정리해도 무방.

미완료(다음 세션 최우선):
1. carrot-ryu-v1 "코드 수정 현황" 나머지 항목 재적용 계속: 1·2번(종방향/RES 안전장치), 4번(13차, 시계 좌측 경계 잘림), 5번 이후(Google Drive 파이프라인 등).
2. [사용자 확인 필요] 이번에 반영한 3번 항목은 12차 "원본" 그대로이고, 이후 세션들(25·26~28·30~36번)에서 스크린샷 관련해 누적된 후속 수정(DPI 반전/캡처 타이밍/render-texture 재설계/상하반전 등, 전부 carrot-ryu-v1에는 이미 실차검증까지 끝난 상태로 존재)이 아직 반영 안 됐다. 다음 세션에서 4번(13차)을 먼저 하고 그 다음 스크린샷 후속 수정들을 이어서 몰아 반영할지, 아니면 다른 서브시스템(Drive 등)을 먼저 할지 순서를 정해야 함(62차부터 이월된 미확정 사항, 20절 5번).
3. 이식이 반 정도라도 진행되기 전까지 콤마 디바이스 git pull 금지 상태 유지(현재도 여전히 유지 중 -- 12차 원본만 반영된 상태라 이후 세션 30~36번 수정 전까지는 스크린샷에 알려진 버그들이 그대로 있음).

검증: 코드 변경은 `git ls-remote` + commit diff로 직접 재확인(위 완료 4번). 실차 검증: 미실시(12절) -- git pull 금지 상태이므로 디바이스에 배포된 적 없음.

주의사항:
- carrot-ryu는 여전히 커스텀 코드 대부분이 없는 상태(이번에 3번 항목만 추가됨). 디바이스가 pull하면 스크린샷 기능은 12차 원본의 알려진 버그(DPI 스케일로 인한 세로 뒤바뀜, HUD 요소 누락 등, 47·49·51차에서 이미 발견/수정됐던 문제들)를 그대로 갖고 있는 상태다. git pull 금지 유지 중이므로 실차 영향 없음.
- carrot-ryu-v1은 이식 체크리스트이자 임시 참조용이므로 1절 원칙대로 수정하지 않는다.
- 저장소 루트 `.gitattributes`의 `* text=auto`로 인한 CRLF 체크아웃 변환 이슈는 앞으로도 여러 줄짜리 Replace-Block 대상 코드 반영 스크립트마다 재현될 수 있음 -- 다음부터 새 Replace-Block 함수를 작성할 때는 처음부터 CRLF→LF 정규화를 기본 포함할 것(9절에 이미 있던 원칙을 실제로 빠뜨리지 않도록 재확인).

다음 작업 후보:
1. 13차(시계 좌측 경계 잘림) 재적용
2. 스크린샷 후속 수정(25·26~28·30~36번) 몰아서 재적용 -- 또는 사용자가 다른 순서 지정
3. Google Drive 업로드 파이프라인(5~14번) 재적용 착수
4. 이식 진행률을 CURRENT_STATUS.md에 계속 갱신