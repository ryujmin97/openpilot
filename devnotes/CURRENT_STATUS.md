# CURRENT STATUS

- 프로젝트: CARROT-RYU (제네시스 DH 2015)
- 베이스 브랜치: carrot-ms (happymaj11r/openpilot). ryujmin97/openpilot에는 carrot-ms/carrot-wip을 미러링하지 않음(7차 세션에서 삭제 완료)
- carrot-ryu HEAD: 36차 커밋(이 값은 코드 반영 스크립트 실행 로그의 git push 출력 참고, 다음 세션에서 GitHub API로 정확한 해시 재확인 필요) -- 화면녹화 탭 업로드 UI + 라벨/메뉴 버그 3건 수정
- carrot-ryu HEAD 근처에 "token test"라는 내용 없는 빈 커밋(2c33603, 10차 위)이 있음(사용자의 git 인증 테스트로 추정, 코드/devnotes 영향 없음)
- carrot-ms 동기화 상태: 6차 세션 이후 신규 커밋(rebase) 없음 확인(7차). 8차~35차 세션에서는 동기화 재점검 없음
- 참고: carrot-wip(ajouatom/openpilot)은 계속 진행 중이나, carrot-ms가 아직 rebase하지 않아 직접 비교 대상 아님
- PROJECT_INSTRUCTIONS_carrot-ryu.md는 22차 버전(4절 0번 단계 보고 의무 추가)이 최신.
- **[31차]** Google Drive 연동(15차) 설계가 Google의 Device Authorization Grant 스코프 제약(전체 drive 스코프 구조적 차단)과 근본적으로 충돌함을 확인. 3가지 대안 제시, 결정 대기 상태로 세션 종료.
- **[32차]** 31차 대안 중 (a) drive.file 스코프+폴더 자동생성 복귀가 커밋 c704371a로 반영됨을 확인(세션 기록 없이 반영된 것을 사후 diff로 정리). 실기기 연결 테스트는 아직 미실시.
- **[33차]** 32차 HANDOFF 미완료 3번(ko.js 문구 버그)을 commit 789667f7로 수정. raw.githubusercontent.com 캐시 지연 현상 관찰(FINDINGS 33차).
- **[34차]** 사용자 제보 UI 문제 2건(도착 텍스트-초록박스 겹침, 도로명 박스 밖 벗어남) 수정, commit 9fdefb3d. 세션 번호 라벨과 devnotes 회차 사이 불일치 발견/정정(FINDINGS 34차).
- **[36차 신규]** 35차에서 확정된 화면녹화 탭 업로드 스펙(체크박스/전체선택/다운로드/전송)을 구현. 함께 "당근서버" 라벨 오표시 버그(dashcam.js targetLabel gdrive 케이스 누락) 수정, 햄버거 메뉴 "최근 로그 업로드"를 화면녹화 탭에서 숨기도록 수정(사용자 확정, 대시캠 탭은 그대로 유지). npm install && node build.mjs로 생성 번들 재생성 + npm test 737/737 pass 확인(직전 세션에서 중단됐던 빌드 검증 완료). 실기기 검증은 다음 세션 이월. 상세: FINDINGS.md 2026-09-15(36차) 항목(있는 경우) 또는 HANDOFF.md 36차 참고.- **[35차 신규]** 32차 Drive 연동 반영 후 처음으로 실기기 검증 결과 확인 -- 사용자가 Drive 연결 자체는 성공했다고 확인함. 다만 실기기 스크린샷으로 예상 밖 동작 3건(당근서버 라벨 오표시, 화면녹화 탭 업로드 기능 전무, 햄버거 메뉴가 탭 무관 대시캠 전용) + Drive 폴더 2개 생성(원인 추정)을 코드 조사로 확인. 사용자가 화면녹화 탭 업로드 기능 신규 스펙을 확정(체크박스/전체선택/다운로드/전송 버튼). 코드 변경은 다음 세션으로 이월. 상세: FINDINGS.md 2026-09-15(35차) 항목.

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
13. 우측하단 경로안내 박스 475x495 확대 + route=숫자 디버그 분리 표시 + 도착정보 2줄 표기(27차, commit 5f5e49d0) -- GitHub 반영됨
14. 경로안내 박스 높이 축소(495→400) + 도착/ETA를 route= 아래 우측끝맞춤으로, 회전아이콘 좌측 배치(28차, commit cc73f629) -- GitHub 반영됨
15. 경로안내 박스 제목 위치/도착·ETA 박스경계 끝맞춤/신호과속 배지를 회전아이콘 박스 바로 아래로 이동(29차, commit 67a8e10) -- GitHub 반영됨
16. 경로안내 박스 route= 크기/위치 조정, 도착·ETA를 pad 인셋 + route= 아래 상단기준으로 재조정(30차, commit 34bb41bc) -- GitHub 반영됨, 반영 후 GitHub 재조회로 확인 완료
17. Google Drive drive.file 스코프+폴더 자동생성 복귀(32차, commit c704371a) -- GitHub 반영 확인됨(diff 직접 조회). **35차에서 사용자가 실기기 연결 성공 확인함.**
18. ko.js gdrive 클라이언트 유형 안내 문구 수정(33차, commit 789667f7) -- GitHub 반영 확인됨(commit diff로 검증), 실기기 검증 대기(우선순위 낮음)
19. 경로안내 박스 도착 텍스트 크기(40->32)/도로명 위치(박스 안쪽, 신호과속과 같은 줄) 수정(34차, commit 9fdefb3d) -- GitHub 반영 확인됨(commit diff + raw 재조회 + py_compile), 실기기 검증 대기

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
17~18차에서 diff/git apply가 두 차례 실전 문제(corrupt patch, 조용한 미반영)를 일으켜 19~20차에 문자열 블록 치환(Replace-Block)으로 전환. 22, 24, 25, 27~30, 34차에서도 동일 방식으로 정상 반영/검증 확인.

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
쿼리스트링 캐시버스터(`?nocache=<timestamp>`)를 붙여도 raw.githubusercontent.com이 한동안 이전 내용을 반환하는 현상이 33차에서 재현됨. github.com commit diff 엔드포인트(`/commit/<sha>.diff`)는 지연 없이 정확했음. 다음 세션에서 "재조회했는데 반영이 안 보인다"는 이유만으로 곧바로 "미반영"으로 단정하지 말고, commit diff로 교차 검증할 것. 상세: FINDINGS.md 2026-09-15(33차) 항목.

## 핵심 발견 22 (34차) -- 세션 시작 시 인지한 회차와 실제 최신 회차 사이 시간차로 인한 번호 불일치
34차 세션은 32차까지만 인지한 상태로 시작해 코드 주석/커밋 메시지에 [33차]로 표기했으나, 그 사이 다른 경로에서 33차(ko.js, 789667f7)가 이미 진행돼 있었음(push 로그의 부모 커밋으로 확인). 코드 자체는 스크립트가 실행 시점에 항상 최신을 clone하므로(6절) 정상적으로 33차 위에 쌓였고 충돌도 없었음 -- 다만 세션 라벨과 devnotes 회차 번호가 어긋남. 코드에 이미 커밋된 [33차] 주석은 과거 기록이므로 재작성하지 않고, devnotes 회차만 실제 순서(34차)로 정정 기록. 상세: FINDINGS.md 2026-09-15(34차) 항목.

## 핵심 발견 23 (35차) -- Drive 업로드 관련 실기기 이슈 3건 원인 특정 + 화면녹화 탭 신규 스펙 확정
32차 Drive 연동 반영 후 처음으로 실기기 검증 결과가 들어옴(연결 성공 확인). 다만 사용자 제보 스크린샷으로 예상 밖 동작 3건을 코드 조사로 특정: (1) dashcam.js targetLabel 분기에 gdrive 케이스 누락으로 "당근서버" 라벨 오표시(실제 전송은 정상), (2) screenrecord.js/screenshots.js에 업로드 기능 자체가 미구현, (3) 전역 햄버거 메뉴("최근 로그 업로드")가 탭 상태를 무시하고 항상 대시캠 세그먼트만 업로드 -- 화면녹화 탭에서 "전송"을 눌러도 화면녹화 영상이 아닌 대시캠 로그가 전송됨. Drive 폴더 2개 생성은 (1)·(3)이 각각 별도로 _ensure_folder() 호출한 타이밍 문제로 추정(미확정). 사용자가 화면녹화 탭에 체크박스/전체선택/다운로드/전송 UI를 신규 구현하는 스펙을 확정, 다음 세션 최우선 작업으로 이월. 상세: FINDINGS.md 2026-09-15(35차) 항목.

- 미확인: carrot-ms 모델 셀렉터 코드 미분석
- 다음 작업: (최우선) 화면녹화 탭 업로드 기능 프론트엔드+백엔드 신규 구현, 당근서버 라벨 버그 수정, 햄버거 메뉴 화면녹화 탭 처리 방향 결정, 34차 UI 변경 실기기 확인, 28~30차 레이아웃 실기기 재검증, 실기기 터미널로 배포된 tools.js 내용 확인해 번들 최신 여부 검증, test_web_upload.py 실제 실행해 낡은 테스트 범위 확정, 데드코드 3개 삭제 + 대응 테스트 정리, docs 갱신, 코드 수정 19건 전부 실주행 재검증, 모델 셀렉터 코드 분석
- 보류 확인 항목: TurnSpeedControlMode=2 / EnableSpeedTF=0 / LeadAccelResponse=0 / DisableDM=2 / LateralTorqueCustom=0 / AutoRoadSpeedLimitOffset / SpeedFromPCM
