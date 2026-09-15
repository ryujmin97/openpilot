# HANDOFF

Worker: Claude (43차 -- devnotes/실제 상태 괴리 확인 + HANDOFF·CURRENT_STATUS 42차 기준 정리)
Date: 2026-09-16
Repository: ryujmin97/openpilot
Code Branch: carrot-ryu (base: 4f81ab7585847c71beb01ee8c5ee50d720f72b61, 42차 온로드 원형 녹화 버튼. 이번 세션 코드 변경 없음)
Note Branch: carrot-ryu-note (이 커밋으로 devnotes 갱신)
carrot-ms 마지막 검토/동기화 커밋(메시지 기준): 7차 체크포인트 이후 신규 23건 확인, WIP_SYNC.md에 40차 체크포인트로 기록 예정(사용자 실행 대기)

작업:
지침 재확인(사용자 요청)을 계기로 4절 0~3번 절차(지침 문서 -> HANDOFF -> CURRENT_STATUS -> carrot-ryu 최신 commit)를 처음부터 다시 수행. 그 과정에서 이 대화가 인지하지 못했던 41차(로그탭 새로고침 아이콘)·42차(온로드 원형 녹화 버튼) 작업이 다른 세션에 의해 이미 GitHub에 push 완료돼 있음을 발견. 다만 HANDOFF.md/WIP.md 본문 텍스트는 여전히 "push 미실시"/"확인 필요"로 남아있어 devnotes와 실제 상태 사이 괴리가 있었음(16절 사례, 핵심 발견 27로 기록). git ls-remote + commit patch + 파일 내용(index.html의 #logsRefreshButton, hud_renderer.py의 RecordButton 배선) 직접 재조회로 실제 반영을 확인한 뒤, HANDOFF.md/CURRENT_STATUS.md를 42차 기준으로 바로잡음.

완료:
- carrot-ryu HEAD 재확인: `4f81ab7585847c71beb01ee8c5ee50d720f72b61`(42차: add onroad record button). commit patch로 메시지·변경 파일(hud_renderer.py) 확인.
- carrot-ryu-note HEAD 재확인: `8bbc7c82639941e6ef213167d1b2118e3c449dc0`(42차 devnotes: onroad record button). commit patch로 변경 파일(HANDOFF.md/WIP.md) 확인.
- 41차 반영 파일 내용 직접 재조회: `openpilot/selfdrive/carrot/web/index.html`에 `#logsRefreshButton` 존재 확인.
- 42차 반영 파일 내용 직접 재조회: `openpilot/selfdrive/ui/onroad/record_button.py` 존재(HTTP 200) + `hud_renderer.py`에 `RecordButton` import/필드/인스턴스화/렌더 배치/`user_interacting()` 포함 5곳 전부 확인.
- CURRENT_STATUS.md: carrot-ryu HEAD 줄을 42차 기준으로 정정, 41차 bullet의 "push 미실시" 문구 정정, 42차 bullet 신규 추가, 43차(이번 세션) bullet 추가, 코드 수정 현황에 24번(41차) 문구 정정 + 25번(42차) 신규 추가, "다음 작업" 목록 최우선 순서 재정렬, 핵심 발견 27(devnotes-실제상태 괴리) 신규 추가.
- HANDOFF.md: 이 파일 자체를 43차 기준으로 전체 교체.

미완료 (다음 세션 이월):
1. [최우선] 42차 원형 녹화 버튼 실기기 검증 -- 스크린샷 버튼 오른쪽(간격 30px) 위치가 화면 밖으로 벗어나지 않는지, 클릭 시 실제 빨간 원 점등/소등이 정상 동작하는지, 실제 녹화 파일이 생성되는지.
2. [이월, 41차] 로그탭 새로고침 아이콘 실기기 검증(위치, 클릭 반응, 회전 애니메이션, 대시캠/화면녹화 각 탭에서 실제 목록 재조회 여부).
3. [이월] 사진 업로드 UI(체크박스/전체선택/다운로드/전송)가 `bdde8326`(39cha-fix) 반영 후 에러 없이 정상 렌더링되는지 실기기 재확인.
4. [이월] 화면녹화 탭 "영상" 업로드 UI(36차) 실기기 검증 -- 42차로 녹화 버튼이 생겼으니 다음 세션에 직접 녹화본 확보 가능.
5. [이월] 37차 락 수정의 실제 동시성(거의 동시 호출) 재현 검증.
6. [이월] 34차 도로명-신호과속 같은 줄 배치 확인(신호과속 배지가 나타나는 구간에서).
7. [이월] 28~30차 레이아웃 정밀 재검증(육안 확인만 완료).
8. [이월] 실차 재검증(8~42차 코드 변경 전부, 12절 원칙) -- 계속 이월.
9. [이월] 실기기에서 직접 디버깅: 배포된 tools.js에 "web-gdrive-connect" 문자열 실제 존재 여부.
10. [이월] test_web_upload.py 실제 실행해 낡은 테스트 수 확인 -> 데드코드 3개 + 대응 테스트 삭제/갱신.
11. [이월] docs/carrot_web_upload.md 갱신(Drive 기준).
12. [이월] run_upload_segments() 설계 변경 실사용 문제 없는지 재확인.
13. [이월] carrot-ms 모델 셀렉터 코드 분석 착수(6차 이후 계속 미착수). 40차 체크포인트(7차 이후 신규 23건, 그중 Cinque v2 eGPU 3건)가 WIP_SYNC.md 반영 스크립트 실행 대기 중.
14. [이월] `devnotes_40cha_wipsync_checkpoint.ps1` 실행 여부 확인 -- 아직 반영 안 됐다면 재전달 필요.

검증: `git ls-remote` + commit patch + raw.githubusercontent.com 파일 내용 직접 재조회로 41차·42차 실제 반영을 확인(16절). 이번 세션은 devnotes 텍스트만 정정, 코드 변경 없음. **실차 검증은 전부 미실시**(12절) -- 특히 42차 녹화 버튼과 41차 새로고침 아이콘은 코드 반영만 확인됐을 뿐 실기기에서 한 번도 확인된 적 없음.

주의사항:
- **devnotes-실제상태 괴리 재발 방지**: 코드 스크립트와 devnotes 스크립트를 순차로 전달/실행하는 세션에서는, devnotes 스크립트를 만드는 시점에 코드 push가 아직 미확인이었더라도 이후 실제로 push됐을 수 있다. 다음 세션은 HANDOFF.md/WIP.md 문구를 그대로 믿지 말고 항상 `git ls-remote`로 최신 HEAD부터 재확인할 것(4절 0~3번, 16절).
- 42차 record_button.py는 screenshot_button.py와 동일하게 독립 클릭 콜백을 갖는 위젯이라 사이드바 토글(단일 탭) 영역과 겹치지 않도록 `user_interacting()`에 포함돼 있으나, 실기기에서 버튼 판정 영역이 실제로 안 겹치는지는 미검증.
- 41차/42차는 서로 다른 파일(index.html/style.css/runtime.js vs record_button.py/hud_renderer.py)이라 충돌 없이 둘 다 반영됨.
- WIP_SYNC.md 40차 체크포인트(carrot-ms 신규 23건, Cinque v2 eGPU 3건 포함) 반영 스크립트가 아직 실행 확인이 안 된 상태로 남아있을 수 있음 -- 다음 세션 확인 필요.

다음 작업 후보:
1. 42차 원형 녹화 버튼 실기기 검증(최우선)
2. 41차 로그탭 새로고침 아이콘 실기기 검증
3. 사진 업로드 UI(39cha-fix) 실기기 검증
4. 화면녹화 탭 "영상" 업로드 UI 실기기 검증(녹화본 확보 후)
5. WIP_SYNC.md 40차 체크포인트 반영 확인 + carrot-ms 신규 23건 중 모델 셀렉터 3건 cherry-pick 검토 착수
6. 37차 락 수정 동시성 재현 검증