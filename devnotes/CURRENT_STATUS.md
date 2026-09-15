# CURRENT STATUS

- 프로젝트: CARROT-RYU (제네시스 DH 2015)
- 베이스 브랜치: carrot-ms (happymaj11r/openpilot). ryujmin97/openpilot에는 carrot-ms/carrot-wip을 미러링하지 않음(7차 세션에서 삭제 완료)
- carrot-ryu HEAD: `4f81ab7585847c71beb01ee8c5ee50d720f72b61` (42차: 온로드 원형 녹화 버튼) -- `git ls-remote` + commit patch로 43차 세션에서 직접 재확인. 41차(로그탭 새로고침 아이콘)와 42차(녹화 버튼)까지 모두 반영됨을 파일 내용으로도 재확인(index.html의 #logsRefreshButton, hud_renderer.py의 RecordButton 배선).
- carrot-ryu HEAD 근처에 "token test"라는 내용 없는 빈 커밋(2c33603, 10차 위)이 있음(사용자의 git 인증 테스트로 추정, 코드/devnotes 영향 없음)
- carrot-ms 동기화 상태: 6차 세션 이후 신규 커밋(rebase) 없음 확인(7차). 8차~38차 세션에서는 동기화 재점검 없음
- 참고: carrot-wip(ajouatom/openpilot)은 계속 진행 중이나, carrot-ms가 아직 rebase하지 않아 직접 비교 대상 아님
- PROJECT_INSTRUCTIONS_carrot-ryu.md는 27차 버전(9절 core.autocrlf=false clone 기본화 + PowerShell 실행정책 우회 -Force)이 최신. 43차 devnotes에는 22차로 잘못 기록돼 있었음 -- 44차에서 재조회해 정정.
- **[31차]** Google Drive 연동(15차) 설계가 Google의 Device Authorization Grant 스코프 제약(전체 drive 스코프 구조적 차단)과 근본적으로 충돌함을 확인. 3가지 대안 제시, 결정 대기 상태로 세션 종료.
- **[32차]** 31차 대안 중 (a) drive.file 스코프+폴더 자동생성 복귀가 커밋 c704371a로 반영됨을 확인(세션 기록 없이 반영된 것을 사후 diff로 정리). 실기기 연결 테스트는 아직 미실시.
- **[33차]** 32차 HANDOFF 미완료 3번(ko.js 문구 버그)을 commit 789667f7로 수정. raw.githubusercontent.com 캐시 지연 현상 관찰(FINDINGS 33차).
- **[34차]** 사용자 제보 UI 문제 2건(도착 텍스트-초록박스 겹침, 도로명 박스 밖 벗어남) 수정, commit 9fdefb3d. 세션 번호 라벨과 devnotes 회차 사이 불일치 발견/정정(FINDINGS 34차).
- **[35차]** 32차 Drive 연동 반영 후 처음으로 실기기 검증 결과 확인 -- 사용자가 Drive 연결 자체는 성공했다고 확인함. 다만 실기기 스크린샷으로 예상 밖 동작 3건(당근서버 라벨 오표시, 화면녹화 탭 업로드 기능 전무, 햄버거 메뉴가 탭 무관 대시캠 전용) + Drive 폴더 2개 생성(원인 추정)을 코드 조사로 확인. 사용자가 화면녹화 탭 업로드 기능 신규 스펙을 확정(체크박스/전체선택/다운로드/전송 버튼). 코드 변경은 다음 세션으로 이월. 상세: FINDINGS.md 2026-09-15(35차) 항목.
- **[36차]** 35차에서 확정된 화면녹화 탭 업로드 스펙(체크박스/전체선택/다운로드/전송)을 구현. 함께 "당근서버" 라벨 오표시 버그(dashcam.js targetLabel gdrive 케이스 누락) 수정, 햄버거 메뉴 "최근 로그 업로드"를 화면녹화 탭에서 숨기도록 수정(사용자 확정, 대시캠 탭은 그대로 유지). npm install && node build.mjs로 생성 번들 재생성 + npm test 737/737 pass 확인. 실기기 검증은 다음 세션 이월. 상세: HANDOFF.md 36차 참고.
- **[37차]** 36차 이월 1번(실기기 검증)보다 2번(Drive 폴더 2개 생성 원인 조사)을 사용자 요청으로 먼저 진행. gdrive_upload.py의 _ensure_folder()가 캐시확인/검색/생성/캐시기록을 락 없이 수행하는 TOCTOU 레이스임을 확정(35차 핵심 발견 23 증상 4의 "추정, 미확정"을 확정으로 전환). 모듈 레벨 asyncio.Lock을 추가해 최소 수정으로 해결. 목 기반 동시성 테스트로 수정 전 재현/수정 후 해소를 모두 확인(실기기 검증은 아님). carrot_man.py의 별도 프로세스 경로까지는 이 락으로 보호되지 않는다는 한계를 사용자와 확인 후 범위 밖으로 확정. 상세: FINDINGS.md 2026-09-15(37차) 항목.
- **[38차 신규]** 사용자가 제공한 실기기 스크린샷 9장으로 36차 변경사항과 34차 UI를 1차 실기기 검증(코드 변경 없음, devnotes만 갱신). 당근서버 라벨 버그 수정, 햄버거 메뉴 화면녹화 탭 분기, 34차 도착 텍스트 겹침 해소, Drive 폴더 단일화 정황은 확인됨. 화면녹화 탭 업로드 UI 자체 동작(녹화본 부재로 미확인), 37차 락의 실제 동시성 재현(수 분 간격 업로드라 직접 증거 아님), 34차 도로명-신호과속 같은 줄 배치(신호과속 배지 미출현으로 판단 보류)는 이월. push 직후 raw.githubusercontent.com 브랜치-head 캐시 지연이 재현됨(핵심 발견 21과 동일 패턴, 아래 핵심 발견 25 참고). 상세: FINDINGS.md 2026-09-15(38차) 항목.
- **[39차 신규]** 38차에서 미확인이던 "화면녹화 탭 업로드 UI"의 실제 의도가 녹화본이 아닌 온로드 캡쳐 사진이었음을 확인, 사진 목록에 체크박스/다운로드/전송(행별 + 상단 전체선택 툴바) UI 신규 구현. 34차 이월분인 경로안내 박스 상하 여백 불균형도 `content_shift_y` 상수로 함께 수정. py_compile/node --check/build/npm test(737/737) 전부 통과, 별도 세션에서 스크립트 로직을 독립적으로 재현해 재검증까지 완료. 이 재검증 과정에서 이전 세션이 만든 반영 스크립트의 9절·18절 필수 규칙 위반 3건(core.autocrlf=false 누락, .ps1 UTF-8 BOM 누락, 임시폴더 미삭제)을 발견해 수정. 실기기 검증은 다음 세션 이월. 상세: HANDOFF.md 39차 참고.
- **[40차 계속]** 39cha-fix push(`bdde8326`)를 `git ls-remote`+commit patch로 직접 재확인. 이어서 사용자 제공 실기기 스크린샷으로 27차 이후 이월되던 경로안내 박스 상하 여백 항목을 처음으로 실차 검증(12절) -- "교차로" 제목/회전아이콘/895m/도착거리/ETA/도로명 순서와 여백 모두 정상 확인. 사진 업로드 UI 자체의 정상 동작은 이 스크린샷에 없어 여전히 미확인, 다음 세션 최우선 이월.
- **[41차]** carrotweb 로그탭에 새로고침 아이콘 추가(대시캠/화면녹화 탭바와 hamburger 메뉴 사이). index.html/style.css/runtime.js 수정 + npm install && npm run build로 생성 번들 3종 재생성, node --check/npm test(32개) 통과까지 확인. **43차에서 실제 push 반영을 재확인함(commit da6ad815, index.html에 #logsRefreshButton 존재 확인).** 실기기 검증은 아직 미실시.
- **[42차]** 온로드 화면(디바이스 UI)에 스크린샷 버튼 옆 원형 녹화 버튼 추가(record_button.py 신규 + hud_renderer.py 5곳 수정). 41차와 세션 번호가 겹쳐(같은 시기 다른 세션이 각자 41차로 준비) 42차로 재번호. **43차에서 실제 push 반영을 재확인함(commit 4f81ab75, hud_renderer.py의 RecordButton 배선 확인).** 실기기 검증은 아직 미실시.
- **[43차 신규]** 지침 문서(27차) 및 레포 전체를 재확인하는 과정에서, 다른 세션이 이미 41~42차를 push 완료했음에도 HANDOFF.md/CURRENT_STATUS.md 텍스트에는 "push 미실시"로 남아있던 devnotes-실제상태 괴리(16절 사례)를 발견하고 이 파일들을 42차 기준으로 바로잡음(코드 변경 없음, devnotes만 갱신).
- **[44차 신규]** 사용자가 제공한 42차 녹화 버튼/41차 새로고침 아이콘 실기기 검증 스크린샷을 근거로 버그 3건을 코드 조사 후 수정: (1) `screenshots.js`의 `formatLogBytes` import 누락으로 사진 목록 렌더가 통째로 중단되던 문제(39cha-fix와 같은 파일의 두번째 미스), (2) `delete_all_videos`가 스크린샷 폴더는 안 지우던 문제(`SCREEN_RECORDING_DIRS` 기준으로 통일), (3) 녹화 버튼이 색만 바뀌고 깜빡이지 않던 것을 `_blink_timer` 재사용으로 개선. 반영 스크립트 작성 후 실제 저장소 경로가 `selfdrive/...`가 아니라 `openpilot/selfdrive/...`(레포 루트에 `openpilot` 서브디렉터리가 한 겹 더 있음)임을 실제 `git clone` 리허설로 재확인, 스크립트 경로를 수정해 반영 스크립트 실행 대기.
- **[45차 신규]** 사용자가 44차 스크립트 실행 후에도 사진 목록 크래시가 재현된다고 제보. carrot-ryu HEAD(e2f35619, 44차)를 직접 조회해 소스(screenshots.js)는 정확했지만 같이 커밋된 생성 번들(js/generated/logs.js)에 ormatLogBytes 함수 정의가 빠져 원문 그대로 미해석 참조로 남아있었음을 확인. 
pm install && node build.mjs를 직접 실행해 재현하고, 변경 diff가 js/generated/logs.js/generated/asset-manifest.json 2개 파일로 한정됨을 확인(
ode --test 737/737 통과). 반영 스크립트(45cha_rebuild_bundle_carrot_ryu.ps1)는 문자열 치환이 아니라 사용자 PC에서 실제 빌드를 실행하는 방식으로 작성, 실행 대기. 상세: FINDINGS.md 2026-09-16(45차) 항목, 핵심 발견 30.

## 코드 수정 현황 (실차 재검증 전부 미실시)
1. route 감속 오검출 근본수정(9차, 2dbe492) -- GitHub 반영됨
2. RES/+ 인게이지 속도 안전장치(10차, e1e587b) -- GitHub 반영됨
3. 온로드 시계 초단위 표시 + 스크린샷 버튼(12차, 684b30d) -- GitHub 반영됨
4. 온로드 시계 좌측 화면 경계 잘림 수정(13차, 2adced8) -- GitHub 반영됨
5. gdrive_upload.py 신규 추가(15차, 183bef9) -- Drive OAuth device flow + resumable 업로드 백엔드, GitHub 반영됨
6. 대시캠 업로드(로그탭 "전송") zip+Drive 전환(16차, dae901c 본편 + cc734e1 hotfix) -- GitHub 반영됨
7. send_tmux_web() Drive 업로드 전환(17차, commit 2869149) -- GitHub 반영됨
8. dashcam 업로드 연결 테스트 버튼(api_dashcam_upload_test)을 Google Drive 기준으로 전환(18~20차, commit ad055dd4) -- GitHub 반영됨
9. params_keys.h에 CarrotGDriveClientId/Secret/RefreshToken 등록(22차, commit 48c2e081) -- GitHub 반영됨
10. web settings log_upload에 Google Drive 계정 연결 UI 추가(23차, commit 272834b) -- GitHub 반영됨. 실기기에서 Client ID/Secret 입력란이 계속 안 보이는 문제 진행 중(26차까지 원인 미확정, 핵심 발견 16 참고).
11. 화면녹화 탭 스크린샷(.png) "사진" 스트립 추가(24차, commit a7a912c1) -- GitHub 반영됨
12. LOG_UPLOAD_TARGETS "gdrive" 누락 수정(25차, commit d338afb7) -- GitHub 반영됨
13. 우측하단 경로안내 박스 475x495 확대 + route=숫자 디버그 분리 표시 + 도착정보 2줄 표기(27차, commit 5f5e49d0) -- GitHub 반영됨. 40차 계속 실기기 검증: 상하 여백 균등 배치 확인됨(스크린샷, 12절 최초 실차 검증).
14. 경로안내 박스 높이 축소(495→400) + 도착/ETA를 route= 아래 우측끝맞춤으로, 회전아이콘 좌측 배치(28차, commit cc73f629) -- GitHub 반영됨
15. 경로안내 박스 제목 위치/도착·ETA 박스경계 끝맞춤/신호과속 배지를 회전아이콘 박스 바로 아래로 이동(29차, commit 67a8e10) -- GitHub 반영됨
16. 경로안내 박스 route= 크기/위치 조정, 도착·ETA를 pad 인셋 + route= 아래 상단기준으로 재조정(30차, commit 34bb41bc) -- GitHub 반영됨, 반영 후 GitHub 재조회로 확인 완료
17. Google Drive drive.file 스코프+폴더 자동생성 복귀(32차, commit c704371a) -- GitHub 반영 확인됨(diff 직접 조회). 35차에서 사용자가 실기기 연결 성공 확인함.
18. ko.js gdrive 클라이언트 유형 안내 문구 수정(33차, commit 789667f7) -- GitHub 반영 확인됨(commit diff로 검증), 실기기 검증 대기(우선순위 낮음)
19. 경로안내 박스 도착 텍스트 크기(40->32)/도로명 위치(박스 안쪽, 신호과속과 같은 줄) 수정(34차, commit 9fdefb3d) -- GitHub 반영 확인됨(commit diff + raw 재조회 + py_compile). 38차 실기기 검증: 도착 텍스트 겹침 해소는 확인됨, 도로명-신호과속 같은 줄 배치는 신호과속 배지 미출현 구간이라 판단 보류(재검증 필요).
20. 화면녹화 탭 업로드 UI 신규 구현 + 당근서버 라벨/햄버거 메뉴 버그 수정(36차, commit 0835b059) -- GitHub 반영 확인됨(push 로그). 38차 실기기 검증: 당근서버 라벨 수정과 햄버거 메뉴 탭 분기는 확인됨, 업로드 UI(체크박스/전체선택 등) 자체 동작은 녹화본 부재로 미확인.
21. gdrive_upload.py _ensure_folder() Drive 폴더 중복생성 레이스컨디션 수정(37차, 커밋 해시는 스크립트 실행 로그의 git push 출력 참고) -- 반영 여부 GitHub API/commit diff로 재확인 완료, 목 테스트로 검증. 38차 실기기 검증: Drive 폴더 1개만 생성됨을 확인했으나 시간 간격이 있는 업로드라 동시성 레이스의 직접 재현은 아님(정황상 일치 수준).
22. 화면녹화 탭 사진 업로드 UI 신규 구현(체크박스/전체선택/다운로드/전송) + 경로안내 박스 상하 여백 통일(content_shift_y)(39차, commit 797fca2e) -- GitHub 반영 확인됨. 경로안내 박스 여백은 40차 계속에서 실기기 검증 완료(스크린샷). 사진 업로드 UI 자체 동작은 여전히 실기기 검증 대기.
23. screenshots.js formatRelativeEpoch import 누락 수정(39cha-fix, 40차, commit bdde8326) -- GitHub 반영 확인됨(`git ls-remote` + commit patch). 39차 사진 업로드 UI 크래시의 실제 원인 수정, 실기기 검증(에러 해소 여부)은 다음 세션 이월.
24. carrotweb 로그탭 새로고침 아이콘 추가(41차, commit da6ad815) -- GitHub 반영 확인됨(43차, `git ls-remote` + commit patch + index.html 파일 내용 직접 재조회). 실기기 검증 대기.
25. 온로드 화면에 원형 녹화 버튼 추가(42차, commit 4f81ab75) -- GitHub 반영 확인됨(43차, 동일 방식). 실기기 검증 대기(버튼 위치/점등·소등/실제 녹화 파일 생성).
26. screenshots.js formatLogBytes import 누락 수정(44차, 커밋 해시는 반영 스크립트 실행 로그 참고) -- 사진 목록 렌더 크래시 근본수정, 반영 스크립트 실행 대기.
27. delete_all_videos를 SCREEN_RECORDING_DIRS 전체 기준으로 확장(44차) -- 스크린샷 폴더 미삭제 문제 수정, 반영 스크립트 실행 대기.
28. record_button.py에 set_blink_phase() 추가 + hud_renderer.py _blink_timer 배선(44차) -- 녹화 중 깜빡임 효과 추가, 반영 스크립트 실행 대기.
29. js/generated/logs.js, generated/asset-manifest.json 번들 재생성(45차) -- 44차 소스 수정이 반영 안 된 채 커밋됐던 생성 번들을 
pm install && node build.mjs로 다시 생성, GitHub 반영은 스크립트 실행 대기.

## 핵심 발견 1~8 (12차까지, 요약)
1. 현대기아/제네시스 종방향 PID 게인 코드 고정(LongTuningKpV/KiV/Kf 무시)
2. (안전, 확인 필요) DisableDM=2는 DM 끄고 Carrot Vision WebRTC 원격 스트리밍 켬
3. LateralTorqueCustom=0이라 opendbc 실측 기본값 사용 중
4. (안전, 확인 필요) route 기반 커브 감속 실제 켜짐(TurnSpeedControlMode=2)
5. T_FOLLOW/traffic_stop/curve_speed 체인 모두 MPC까지 연결됨
6. (8~9차) route 감속 고속도로 분기점 오검출 median 필터로 근본수정(2dbe492), 실차 재검증 대기
7. (10차) 출발 가속 중 +RES 인게이지 급감속 -> 안전장치 추가, 정확한 트리거 조건 미확인
8. (12차) 스크린샷 backend/frontend(kind 구분) 변경 -- 24차에서 실제 구현 완료(GitHub 반영 확인)

## 핵심 발견 9 (13차)
온로드 좌측 상단 시계가 HH:MM:SS(8자, font_size=100)로 center_bottom 정렬되며 고정 x(rect.x+170) 기준으로는 텍스트 실측 폭 기반 x 보정으로 수정.

## 핵심 발견 10 (15~23차) -- 대시캠/tmux 업로드 및 연결 테스트를 Carrot/Toss에서 Google Drive로 전환
- 배경: 기존 Carrot/Toss 업로드 서버(shind0.synology.me, op.wjcloud.kr)를 사용자 개인 Google Drive로 대체하기로 결정.
- gdrive_upload.py: OAuth2 Device Authorization Grant + resumable 업로드(8MB 청크). 15차 시점은 고정 DRIVE_FOLDER_ID 사용, 32차에서 drive.file+폴더 자동생성으로 재변경(핵심 발견 20 참고).
- 프론트엔드 연결 UI(23차): 실기기에서 드롭다운은 바뀌었으나 입력란이 안 보이는 문제 계속 진행 중(26차, 핵심 발견 16).
- 미완료: docs/carrot_web_upload.md 미갱신, 입력란 미노출 원인 조사(진행 중), 화면녹화 전송 다이얼로그 라벨 불일치 조사(26차 발견, 35차에서 원인 특정 -- 핵심 발견 23 참고).

## 핵심 발견 11 (17~20차) -- diff(git apply) 방식의 실전 한계, 결국 예외적 보조로 격하
17~18차에서 diff/git apply가 두 차례 실전 문제(corrupt patch, 조용한 미반영)를 일으켜 19~20차에 문자열 블록 치환(Replace-Block)으로 전환. 22, 24, 25, 27~30, 34, 37차에서도 동일 방식으로 정상 반영/검증 확인.

## 핵심 발견 12 (22차) -- Google Drive 연동 파라미터 3종이 params_keys.h에 미등록되어 실전에서 항상 실패했을 버그
gdrive_upload.py(15차)가 사용하는 CarrotGDriveClientId/Secret/RefreshToken이 params_keys.h에 미등록되어 Drive "연결" 버튼을 누르는 순간부터 항상 UnknownKeyName -> HTTP 500으로 실패했음. 22차에서 수정(commit 48c2e081). 상세: FINDINGS.md 2026-09-14(22차) 항목.

## 핵심 발견 13 (24차) -- devnotes 기록 누락과 미반영 작업을 "이어서 진행" 요청 시 구분해야 함
23차는 코드가 실제 GitHub에 반영되어 있었지만 devnotes만 누락된 경우였고, 24차는 세션 도중 사용자가 스크립트를 실행해 실제로 반영 완료됨(commit a7a912c1). "GitHub의 현재 상태를 먼저 직접 확인"(3절/16절)하지 않으면 두 상태를 구분할 수 없다는 것이 실증됨.

## 핵심 발견 14 (24차 계속2) -- Google Drive 연결 UI 입력란 미노출: 백엔드 LOG_UPLOAD_TARGETS에 "gdrive" 누락
25차에서 수정 완료(commit d338afb7). 다만 이 수정 이후에도(26차 실기기 검증) 입력란 미노출 현상은 그대로 재현됨 -> LOG_UPLOAD_TARGETS는 원인이 아니었거나, 원인 중 일부만 해결한 것으로 보임(핵심 발견 16).

## 핵심 발견 15 (25차) -- web_upload.py/dashcam upload.py 데드코드 3개 + test_web_upload.py 낡은 테스트 의심
tmux_web_target()/resolve_upload_target()/upload_target_settings()는 프로덕션 호출자가 없는 진짜 죽은 코드로 확인됨. 25차에서는 보류, 이월.

## 핵심 발견 16 (26차) -- Google Drive 연결 UI 미노출: 정적 코드 리뷰와 실기기 스크린샷이 모순됨(원인 미확정)
25차에서 LOG_UPLOAD_TARGETS 백엔드 버그를 고쳤음에도, 실기기 스크린샷에서는 여전히 입력란이 안 보임. 정적 코드 리뷰 결과 코드 자체에서는 원인을 못 찾음 -> 실기기가 최신 tools.js/tools.css 번들을 실제로 서빙/로드하고 있는지 의심(브라우저 캐시 또는 esbuild 재생성 누락 가능성). 실기기 디버깅은 다음 세션 이월. 화면녹화 전송 다이얼로그 "당근서버" 라벨 하드코딩 불일치도 발견(코드 위치 미조사, 35차에서 원인 특정 -- 핵심 발견 23 참고).

## 핵심 발견 17 (27차) -- Windows Git core.autocrlf로 인한 문자열 블록 치환(Replace-Block) 실패
git clone에 --config core.autocrlf=false 옵션 추가 + CRLF->LF 정규화 안전장치로 해결. 지침 문서 27차에서 9절 기본 규칙으로 정식 반영됨.

## 핵심 발견 18 (30차) -- HANDOFF.md 미반영 기록과 실제 GitHub 상태 불일치
29차 HANDOFF.md가 "미반영"으로 기록했던 레이아웃 변경(29차)이 실제로는 반영돼 있었고, 그 위에 30차 커밋까지 추가로 진행돼 있었음. "코드 반영"과 "devnotes 갱신"이 서로 다른 세션에서 이루어지며 갱신이 누락된 사례. 4절 0~3번 절차를 빠짐없이 따른 결과 이번 세션에서 스스로 발견/정정됨. 상세: FINDINGS.md 2026-09-15(30차) 항목.

## 핵심 발견 19 (31차) -- Google Drive 연동 설계가 Device Authorization Grant의 스코프 제약과 근본적으로 충돌
Google은 OAuth Device Authorization Grant(기기 인증 흐름)에서 전체 Drive 스코프(auth/drive)를 클라이언트 유형/동의 화면 설정과 무관하게 정책적으로 차단하고 있음(다수 독립 개발자 사례로 확인, Google 공식 문서 명시 출처는 못 찾음). gdrive_upload.py(15차)가 고정 폴더 ID 접근을 위해 의도적으로 넓힌 전체 drive 스코프가 바로 이 제약과 충돌하는 조합이었음. drive.file+폴더자동생성 복귀 / 표준 Authorization Code Flow 전면 재설계 / Drive 자체 대체, 3가지 대안을 사용자에게 제시하고 결정 대기 중이었음 -> 32차에서 첫 번째 대안 반영됨(핵심 발견 20).

## 핵심 발견 20 (32차) -- 31차 근본 원인을 drive.file+폴더자동생성 복귀로 우회 반영, 실기기 검증 전
31차 핵심 발견 19의 3가지 대안 중 (a) drive.file 스코프+폴더 자동생성(c3-ms-dev 원본) 복귀가 커밋 c704371a로 반영됨을 이번 세션에서 diff 직접 조회로 확인. gdrive_upload.py의 DRIVE_SCOPE을 drive.file로 좁히고 _verify_folder()를 _ensure_folder()(이름 검색/자동생성)로 교체. 35차에서 실기기 연결 성공이 확인됨(핵심 발견 23 참고).

## 핵심 발견 21 (33차) -- raw.githubusercontent.com 캐시 지연으로 커밋 직후 재조회 시 이전 내용이 보일 수 있음
쿼리스트링 캐시버스터(`?nocache=<timestamp>`)를 붙여도 raw.githubusercontent.com이 한동안 이전 내용을 반환하는 현상이 33차에서 재현됨. github.com commit diff 엔드포인트(`/commit/<sha>.diff`)는 지연 없이 정확했음. 다음 세션에서 "재조회했는데 반영이 안 보인다"는 이유만으로 곧바로 "미반영"으로 단정하지 말고, commit diff로 교차 검증할 것. 38차에서 동일 현상 재현(핵심 발견 25 참고). 상세: FINDINGS.md 2026-09-15(33차) 항목.

## 핵심 발견 22 (34차) -- 세션 시작 시 인지한 회차와 실제 최신 회차 사이 시간차로 인한 번호 불일치
34차 세션은 32차까지만 인지한 상태로 시작해 코드 주석/커밋 메시지에 [33차]로 표기했으나, 그 사이 다른 경로에서 33차(ko.js, 789667f7)가 이미 진행돼 있었음(push 로그의 부모 커밋으로 확인). 코드 자체는 스크립트가 실행 시점에 항상 최신을 clone하므로(6절) 정상적으로 33차 위에 쌓였고 충돌도 없었음 -- 다만 세션 라벨과 devnotes 회차 번호가 어긋남. 코드에 이미 커밋된 [33차] 주석은 과거 기록이므로 재작성하지 않고, devnotes 회차만 실제 순서(34차)로 정정 기록. 상세: FINDINGS.md 2026-09-15(34차) 항목.

## 핵심 발견 23 (35차) -- Drive 업로드 관련 실기기 이슈 3건 원인 특정 + 화면녹화 탭 신규 스펙 확정
32차 Drive 연동 반영 후 처음으로 실기기 검증 결과가 들어옴(연결 성공 확인). 다만 사용자 제보 스크린샷으로 예상 밖 동작 3건을 코드 조사로 특정: (1) dashcam.js targetLabel 분기에 gdrive 케이스 누락으로 "당근서버" 라벨 오표시(실제 전송은 정상), (2) screenrecord.js/screenshots.js에 업로드 기능 자체가 미구현, (3) 전역 햄버거 메뉴("최근 로그 업로드")가 탭 상태를 무시하고 항상 대시캠 세그먼트만 업로드 -- 화면녹화 탭에서 "전송"을 눌러도 화면녹화 영상이 아닌 대시캠 로그가 전송됨. Drive 폴더 2개 생성은 (1)·(3)이 각각 별도로 _ensure_folder() 호출한 타이밍 문제로 추정(당시 미확정 -> 37차에서 TOCTOU 레이스로 확정, 핵심 발견 24 참고). 사용자가 화면녹화 탭에 체크박스/전체선택/다운로드/전송 UI를 신규 구현하는 스펙을 확정, 다음 세션 최우선 작업으로 이월(36차에서 구현 완료). 상세: FINDINGS.md 2026-09-15(35차) 항목.

## 핵심 발견 24 (37차) -- Drive 폴더 2개 생성(핵심 발견 23 증상 4) 원인 확정: _ensure_folder() TOCTOU 레이스 컨디션
gdrive_upload.py의 _ensure_folder()가 캐시확인/이름검색/생성/캐시기록을 락 없이 수행해, 대시캠 탭 전송과 햄버거 메뉴 "최근 로그 업로드"처럼 서로 다른 asyncio task가 거의 동시에 호출하면 첫 호출의 Drive API 왕복이 끝나기 전에 둘 다 캐시 미스로 판단해 폴더를 중복 생성할 수 있음을 확정(300초 캐시 만료가 아니라 캐시가 채워지기 전의 좁은 레이스 윈도우 문제). 모듈 레벨 asyncio.Lock으로 최소 수정(37차, 인프로세스 한정). carrot_man.py의 send_tmux_web()은 별도 프로세스라 이 락으로 보호되지 않는 한계가 남아있으며, 근본 해결(Params 영구저장)은 사용자 승인 하에 범위 밖으로 확정. 목 기반 동시성 테스트로 수정 전 재현/수정 후 해소 모두 확인(실기기 검증 아님). 상세: FINDINGS.md 2026-09-15(37차) 항목.

## 핵심 발견 25 (38차) -- raw.githubusercontent.com 브랜치-head 캐시 지연 재현 + 36차/37차/34차 실기기 검증 1차 결과
37차 push 직후 브랜치-head raw URL로 HANDOFF.md/CURRENT_STATUS.md를 재조회했더니 36차(이전) 내용이 그대로 반환됨 -- commit-pinned raw URL(`/{sha}/...`)로 재조회하자 37차 내용이 정상 확인됨(핵심 발견 21과 동일 패턴 재현). 이와 별개로 사용자가 제공한 실기기 스크린샷 9장으로 36차 당근서버 라벨 버그 수정/햄버거 메뉴 탭 분기, 34차 도착 텍스트 겹침 해소, Drive 폴더 단일화 정황을 확인했으나, 화면녹화 탭 업로드 UI 자체 동작(녹화본 부재)과 37차 락의 실제 동시성 재현(시간 간격 있는 업로드라 직접 증거 아님), 34차 도로명-신호과속 같은 줄 배치(신호과속 배지 미출현)는 판단을 보류하고 이월함. 상세: FINDINGS.md 2026-09-15(38차) 항목.

## 핵심 발견 26 (39차) -- 다른 세션이 만든 반영 스크립트도 실행 전 9절·18절 필수 규칙 위반 여부를 재검증해야 함
39차 코드 작업(사진 업로드 UI, 경로안내 박스 여백) 자체는 직전 세션에서 정적 검증까지 마쳤으나, 무료 사용량 한도로 carrot-ryu 반영 스크립트(.ps1) 전달 전에 세션이 종료됨. 이어받은 세션에서 그 스크립트를 실행하기 전 재검증한 결과, 9절·18절에 이미 문서화된 필수 규칙 3건이 지켜지지 않은 상태였음을 발견: (1) `git clone`에 `--config core.autocrlf=false`(27차) 누락, (2) 한글 포함 `.ps1` 파일 자체의 UTF-8 BOM(21차) 누락, (3) 스크립트 종료 시 임시 폴더를 삭제하지 않고 사용자에게 수동 삭제를 안내(18절 금지 항목). 스크립트의 문자열 치환(anchor) 로직 자체는 GitHub 최신 클론에 대해 파이썬으로 재현했을 때 17곳 모두 정확히 1회 매치로 문제없었음. 즉 "코드 변경 내용"은 정확했으나 "전달 형식"이 규칙을 어긴 경우로, 22차 핵심 발견(지침 문서 미조회)과 유사하게 "직전 세션이 규칙을 몰라서"가 아니라 "규칙 준수 여부를 전달 직전에 재확인하지 않아서" 발생한 사례. 세 가지 위반을 모두 수정한 뒤 최종 스크립트를 전달함.

## 핵심 발견 27 (43차) -- devnotes 텍스트가 실제 push 완료 상태를 반영하지 못한 채로 세션이 종료된 사례
41차·42차 세션은 코드/devnotes 스크립트를 만들어 전달한 뒤, 사용자가 실행해 실제로 GitHub에 push까지 완료됐음(carrot-ryu commit da6ad815, 4f81ab75; carrot-ryu-note commit 8bbc7c82)에도, HANDOFF.md/WIP.md 본문 텍스트 자체는 "push 미실시"/"실행 여부 확인 필요"로 남아있었음 -- devnotes를 push하는 시점과 코드 push 확인 시점 사이에 세션이 종료되며 문서 갱신이 누락된 것으로 추정. 43차에서 4절 0~3번 절차(지침 재조회 -> HANDOFF -> CURRENT_STATUS -> git ls-remote)를 처음부터 다시 수행하는 과정에서 `git ls-remote` + commit patch + 파일 내용 직접 재조회로 실제 반영 사실을 확인하고 문서를 바로잡음. 핵심 발견 18(30차)과 유사한 패턴이 반복됨 -- "코드 반영"과 "devnotes 갱신"이 다른 시점/세션에서 이루어질 수 있으므로, 매 세션 시작 시 devnotes 텍스트만으로 상태를 단정하지 말고 GitHub 실제 커밋을 항상 재확인해야 함(16절).

## 핵심 발견 28 (44차) -- 사진 목록 미표시와 delete_all_videos 범위 누락, 두 버그의 공통 패턴: 코드 재사용 시 참조 대상 목록이 갱신 안 됨
(1) `screenshots.js`가 `formatLogBytes()`를 쓰면서 39cha-fix(40차) 때 고친 `formatRelativeEpoch`처럼 import를 안 해놔서, 사진 행을 그리는 순간 ReferenceError로 목록 렌더 전체가 중단됨(39cha-fix가 그때 이 파일의 다른 누락 import까지는 점검하지 않았던 사각지대). (2) `delete_all_videos`(dispatcher.py 비동기/동기 두 구현)는 `/data/media/0/videos` 하나만 하드코딩돼 있었는데, 스크린샷은 별도 폴더(`SCREEN_RECORDING_DIRS[1]`, `/data/media/0/screenrecord`)에 저장되도록 설계돼 있어 삭제 범위에서 누락됨. 두 버그 모두 "실제 데이터가 있는 곳/실제로 필요한 참조"가 원래 구현 시점 이후 넓어졌는데 관련 코드(import 목록, 하드코딩된 경로)가 함께 갱신되지 않은 동일 패턴. 앞으로 같은 파일/기능을 다시 건드릴 때는 그 파일이 실제로 참조·순회하는 대상 목록(import 대상, 폴더 목록 등)이 현재 설계와 일치하는지 먼저 grep으로 교차 확인할 것.

## 핵심 발견 29 (44차) -- 반영 스크립트의 상대경로 가정이 실제 레포 구조(레포 루트에 openpilot 서브디렉터리)와 어긋났던 사례
44차에서 만든 코드 반영 스크립트의 Replace-Block 대상 경로를 처음에 `selfdrive/carrot/...` 식으로 레포 루트 기준으로 작성했으나, ryujmin97/openpilot 레포는 루트에 `carrot`(툴킹 관련)과 `openpilot`(실제 콤마 openpilot 코드, `selfdrive`가 이 안에 있음) 두 서브디렉터리가 공존하는 구조라, 실제로는 `openpilot/selfdrive/carrot/...`가 맞는 경로였음. `git clone` 리허설(임시 폴더에 실제 clone 후 대상 파일 존재 확인)로 스크립트 실행 전에 발견/수정함 -- 만약 그대로 전달됐다면 Replace-Block이 `FileNotFoundException`으로 즉시 중단됐을 것(9절의 "1회 매치 아니면 중단" 방어선 이전 단계에서 실패하므로 데이터 손상 위험은 없었으나, 사용자가 원인 모를 에러를 마주쳤을 것). 앞으로 새로운 코드 반영 스크립트를 만들 때는 anchor 매치 카운트뿐 아니라 대상 경로 자체도 실제 `git clone` 결과로 먼저 확인할 것(6절과 연계, 특히 세션 사이 로컬 작업 디렉터리가 초기화되는 이 환경에서는 이전 세션이 사용한 상대경로 표기를 그대로 재사용하지 말 것).

## 핵심 발견 30 (45차) -- 소스 수정 완료와 생성 번들 반영 완료는 별개다
44차에서 screenshots.js 소스의 누락 import를 정확히 고쳤음에도, 그 위에서 
pm install && node build.mjs로 생성 번들을 재생성하는 단계를 건너뛰어 예전(깨진) 번들이 그대로 커밋됨. 기기는 커밋된 번들을 그대로 서빙하므로 소스만 맞고 번들이 어긋나면 실기기 효과가 없음. 
pm install && node build.mjs를 직접 실행해 재현/해결, 변경 diff는 js/generated/logs.js/generated/asset-manifest.json 2개 파일로 한정, 
ode --test 737/737 통과 확인. 앞으로 js/css 소스 변경 시 생성 산출물까지 diff로 함께 확인/커밋할 것. 상세: FINDINGS.md 2026-09-16(45차) 항목.

- 미확인: carrot-ms 모델 셀렉터 코드 미분석
- 다음 작업: 45차 반영 스크립트 실행 확인(최우선) + 44차 3건(사진목록/전체삭제/녹화버튼 깜빡임) 실기기 재검증 + 3건(사진목록/전체삭제/녹화버튼 깜빡임) 실기기 재검증, 41차 로그탭 새로고침 아이콘 실기기 검증, 37차 락 수정 동시성 재현 검증(의도적으로 동시에 두 업로드 시도), 34차 도로명-신호과속 같은 줄 배치 확인(신호과속 구간에서), 28~30차 레이아웃 정밀 재검증, 실기기 터미널로 배포된 tools.js 내용 확인해 번들 최신 여부 검증, test_web_upload.py 실제 실행해 낡은 테스트 범위 확정, 데드코드 3개 삭제 + 대응 테스트 정리, docs 갱신, 코드 수정 28건 전부 실주행 재검증, carrot-ms 신규 커밋 cherry-pick 검토 착수(WIP_SYNC.md 참고)
- 보류 확인 항목: TurnSpeedControlMode=2 / EnableSpeedTF=0 / LeadAccelResponse=0 / DisableDM=2 / LateralTorqueCustom=0 / AutoRoadSpeedLimitOffset / SpeedFromPCM