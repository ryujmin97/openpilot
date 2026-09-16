# HANDOFF

Worker: Claude (65~66차 -- 20절 이식 항목 25, 27+28 재적용: 온로드 원형 녹화 버튼(42차) + delete_all_videos 확장/녹화 버튼 깜빡임(44차 일부)을 새 베이스 위에 순차 재적용)
Date: 2026-09-17
Repository: ryujmin97/openpilot
Code Branch: carrot-ryu (base: `4e3b44a81f2fc79c3b6f23ebaee40a1bc73d370b`, 64차 HEAD 위에 65차 `b152e192` -> 66차 `0d5117533e0703e442fd1664b8ee00146cf40a4f` 순차 추가)
Note Branch: carrot-ryu-note (base: `9b6ee32defa5c4b54a34f33b8b3c0d6e5628d7dc`, 64차 devnotes. 이 커밋으로 devnotes 갱신)
carrot-ms 마지막 검토/동기화 커밋(메시지 기준): `706efb47b81cf9cb02888ee536a156d8f1fc1d91`(61차 20절 리셋 베이스, 변경 없음).

작업:
64차에서 완료된 항목 4에 이어, 스크린샷 관련 후속 수정 묶음(20절 이식 항목 25·26~28·30~36번)을 17절 원칙대로 세션 하나에 몰지 않고 항목 단위로 나눠 진행하기로 함. 65차는 항목 25(42차, 온로드 원형 녹화 버튼 추가), 66차는 항목 27+28(44차 e2f35619 커밋 중 파일 의존성 없는 부분)을 순차 재적용했다.

완료(65차 -- 항목 25, commit `b152e192`):
1. 원본 42차 커밋(4f81ab75)의 diff를 확인 -- record_button.py 신규 추가(스크린샷 버튼 오른쪽에 배치, ScreenRecord 파라미터를 토글하는 원형 녹화 버튼, 녹화 중엔 빨간 원 채움) + hud_renderer.py에 import/UIConfig 필드/__init__/_render/user_interacting 5곳 배선.
2. 사전 확인: ScreenRecord 파라미터가 params_keys.h에 이미 등록되어 있어 추가 등록 불필요, put_bool_nonblocking(params_pyx.pyx)/gui_app.is_recording()(application.py)/Widget/set_click_callback 모두 새 베이스(4e3b44a8)에 그대로 존재.
3. sandbox에서 5개 Replace-Block 전부 1회 매치 + 신규 파일까지 py_compile 통과 확인.
4. 사용자가 `reapply_item25_65cha.ps1` 실행, commit `b152e192`로 carrot-ryu에 push 완료.
5. `git ls-remote` + commit diff로 반영 내용이 원본 42차 커밋과 정확히 일치함을 재확인.

완료(66차 -- 항목 27+28, commit `0d511753`):
1. 44차 원본은 실제로 항목 26·27·28을 커밋 하나(e2f35619)로 묶어 반영했었음을 commit diff로 확인.
2. 그중 항목 26(screenshots.js formatLogBytes import 수정)은 전제가 되는 screenshots.js 파일 자체(항목 11, 24차 작업물)가 새 베이스에 없어(GitHub raw 조회 404) 이번엔 적용 불가로 확정, 파일 의존성이 없는 항목 27+28만 진행.
3. 항목 27: dispatcher.py의 delete_all_videos(비동기/동기 두 구현)를 하드코딩된 `/data/media/0/videos` 한 곳에서 SCREEN_RECORDING_DIRS(영상+스크린샷 폴더 전체) 기준으로 확장.
4. 항목 28: record_button.py 전체교체(set_blink_phase() 추가) + hud_renderer.py 1줄 -- 기존 _blink_timer(카메라감지/과열경고에 이미 쓰던 프레임 카운터)를 재사용해 녹화 중 채움/테두리를 번갈아 그리도록 깜빡임 추가.
5. sandbox에서 5곳 전부 1회 매치 + py_compile 통과 확인 후 전달, 원본 44차 diff와 동일함을 commit patch 대조로 확인.
6. 사용자가 `reapply_items2728_66cha.ps1` 실행, commit `0d5117533e0703e442fd1664b8ee00146cf40a4f`로 carrot-ryu에 push 완료(3 files changed, 17 insertions, 4 deletions 로그로 확인).
7. `git ls-remote`(carrot-ryu=`0d511753`)로 재확인, `git log --oneline`으로 65·66차 두 커밋이 순서대로 쌓여있음을 직접 조회로 검증.
8. carrot-ryu-v1 "코드 수정 현황" 항목 25/27/28을 CURRENT_STATUS.md에 "재반영 완료(commit ...)"로 개별 갱신, 항목 26은 "61차 리셋 이후 미반영, 항목 11·23 선행 필요"로 갱신.

미완료(다음 세션 최우선):
1. carrot-ryu-v1 "코드 수정 현황" 나머지 항목 재적용 계속: 1·2번(종방향/RES 안전장치), 5번 이후(Google Drive 파이프라인 등), 항목 26(screenshots.js -- 항목 11·23 선행 필요) 및 30~36번(DPI 반전/캡처 타이밍/render-texture 재설계/상하반전 등).
2. [63차부터 이월, 사용자 확인 필요] 항목 11·23을 먼저 반영해 항목 26 의존성을 해소할지, 아니면 Google Drive 파이프라인 등 다른 서브시스템을 먼저 할지 순서를 정해야 함(20절 5번).
3. 이식이 반 정도라도 진행되기 전까지 콤마 디바이스 git pull 금지 상태 유지(현재도 여전히 유지 중 -- 12·13·25·27·28번만 반영된 상태).
4. WIP_SYNC.md에 항목 26의 의존관계(항목 11·23 선행 필요)를 정식 기록.

검증: 코드 변경은 `git ls-remote` + commit diff(github.com/.../commit/<sha>.patch)로 직접 재확인, 원본 42차/44차 커밋과 diff 일치 확인(위 완료 항목). 실차 검증: 미실시(12절) -- git pull 금지 상태이므로 디바이스에 배포된 적 없음.

주의사항:
- carrot-ryu는 여전히 커스텀 코드 대부분이 없는 상태(12·13·25·27·28번 다섯 항목만 추가됨). git pull 금지 유지 중이므로 실차 영향 없음.
- carrot-ryu-v1은 이식 체크리스트이자 임시 참조용이므로 1절 원칙대로 수정하지 않는다.
- 항목 26(screenshots.js)은 항목 11·23이 먼저 반영되기 전까지 재시도하지 말 것(파일 자체가 없어 즉시 실패).

다음 작업 후보:
1. 항목 11(24차, 화면녹화 탭 사진 스트립 신규 생성) + 항목 23(39cha-fix, formatRelativeEpoch import) 재적용 -> 이어서 항목 26(screenshots.js formatLogBytes) 재적용
2. Google Drive 업로드 파이프라인(5~14번) 재적용 착수
3. 종방향/RES 안전장치(1·2번) 재적용
4. 이식 진행률을 CURRENT_STATUS.md에 계속 갱신