# CURRENT STATUS

- 프로젝트: CARROT-RYU (제네시스 DH 2015)
- 베이스 브랜치: carrot-ms (happymaj11r/openpilot). ryujmin97/openpilot에는 carrot-ms/carrot-wip을 미러링하지 않음(7차 세션에서 삭제 완료)
- carrot-ryu HEAD: `a0f4c5a5fb932be1525311d2ed61f5382a4bd6d2` (123차 C그룹 dead code 삭제, 부모 `2efdd2e2`(121차); 97~121차 커밋 체인은 이 파일에 아직 catch-up되지 않았고 WIP.md 115~121차/DEAD_CODE_REVIEW.md 참고. 아래 괄호 안은 93차 시점 기록: `25f21d406d23bfb79ad45a67890cc39e3ad9e67b` (93차, carrot-ms 557e6f6a 재적용 -- 부모 `9eced40`(92차, ec95363a), 그 부모 `f1e920d`(91차 계속2, 4d1a3ded), 그 부모 `260565f`(90차, b4f751f4). 4건 모두 GitHub push 확인 완료. carrot-ryu-v1(`9ccf1206a034c5fb5e5f35201553f9fc4e5237e5`)에 원래 36개 항목 전체가 보존됨. 실기기 배포/검증은 미실시(git pull 금지 유지 중). **36개 항목(1~36) 전부 GitHub 반영 확인 완료.**
- 61차 리셋 이전 HEAD 이력(9ccf1206 등, 45차~59차의 개별 커밋들)은 carrot-ryu-v1 브랜치에 스냅샷으로 남아있으며, 20절 원칙에 따라 앞으로 수정하지 않음.
- carrot-ms 동기화 상태: 6차 세션 이후 신규 커밋(rebase) 없음 확인(7차). 8차~38차 세션에서는 동기화 재점검 없음
- 참고: carrot-wip(ajouatom/openpilot)은 계속 진행 중이나, carrot-ms가 아직 rebase하지 않아 직접 비교 대상 아님
- PROJECT_INSTRUCTIONS_carrot-ryu.md는 v2가 최신(v1 1~27차의 회차별 규칙을 절 번호(0~19) 그대로 유지한 채 정리/재구성, 상세 변경 사유는 이 파일 자체의 GitHub 커밋 메시지로 이전). 46차 세션에서 반영(commit `8f8209fe82de96acd2c5f7b90765aa3dc70d3012`) -- 직전 45차-정정 세션에서 "45차 세션에서 반영"으로 잘못 표기돼 있던 것을 커밋 메시지 대조로 정정.
- **[69차, devnotes 정정만 · 코드 변경 없음]** 68차에서 항목 22(39차) 착수를 준비하던 중, 항목 22의 routes.py 변경이 항목 20(36차, `0835b059`)에 바로 이어붙는 전제이고, 항목 20 자체가 Google Drive 파이프라인 전체(항목 5~10·12·17·18·21)에 의존한다는 것을 diff 대조로 발견했다. 실제 `carrot-ryu` 코드를 독립적으로 clone해 재확인한 결과, `gdrive_upload.py` 파일이 저장소 어디에도 없고 `routes.py`에는 업로드용 POST 엔드포인트가 하나도 없음(GET만 존재)을 확인했다. 원인: 아래 "코드 수정 현황" 항목 5~10·12·17·18·20·21(및 이에 의존하는 22·23·24)이 61차(20절 리셋) 이전 carrot-ryu 기준 "GitHub 반영됨" 표기가 그대로 남아있었던 것 -- 62차 안내문이 "재적용될 때마다 개별 갱신하라"고 미리 경고했던 바로 그 상황이 방치돼 있었다(63~68차에서는 hud_renderer.py 관련 항목(3·4·11·13~16·19·25·27·28)만 개별 재확인/재적용됐고, Drive 관련 항목은 그 사이 아무도 재확인하지 않음). 즉 항목 22를 지금 적용해도 전제인 항목 20(및 20이 의존하는 5~10·12·17·18·21)이 새 베이스에 없어 반드시 다시 막힌다. 이번 세션은 코드 변경 없이 아래 해당 항목 표기만 정정했다(16절). 다음 세션 최우선: 5→6→7→8→9→10→12→17→18→20→21 순서(파일 스코프 대조로 서로 겹치지 않음 확인, 순서 변경 없이 확정)로 재적용, 이후 22→23→26.
- **[70~74차]** 항목 5(15차, `183bef9`, gdrive_upload.py 신규)→6(16차, `dae901c`+`cc734e1`, 대시캠/tmux 업로드 Drive zip 전환)→7(17차, `2869149`, send_tmux_web() Drive 전환)→8(18~20차, `ad055dd4`, 업로드 연결테스트 버튼 Drive 전환)→9(22차, `48c2e081`, params_keys.h Drive 3키 등록) 순서로 새 베이스(`2088c546`) 위에 순차 재적용, 각 commit(`017072dd`/`4b6c8f84`/`75c7c316`/`bc021ed9`/`7a1555ed`)까지 push 완료. devnotes(HANDOFF.md/WIP.md)는 이 다섯 세션 동안 갱신되지 못한 채 세션이 끊겨 69차 상태로 남아있었음 -- 75차에서 `git ls-remote`+GitHub compare API로 발견/사후 동기화(핵심 발견 27/38과 동일 패턴, 상세는 75차 항목 및 WIP.md 참고).
- **[76차, devnotes 정정만 · 코드 변경 없음]** 세션 시작 체크포인트(`git ls-remote`)에서 carrot-ryu HEAD가 `c9a03b5`로, HANDOFF.md(75차)에 기록된 base(`7a1555ed`)와 다름을 발견(4절/16절). GitHub compare API로 `7a1555ed`..`c9a03b5` 사이를 조회한 결과 정확히 2개 커밋: `61bfcd44`(AR projection golden fixture 갱신, Drive 작업과 무관) + `c9a03b5`("75cha: web settings Google Drive 계정 연결 UI 재적용", 항목 10, 번들 재생성 포함). 변경 파일 9개(base.css/components.js/schema.js 전체교체 + en.js/ko.js/zh.js anchor삽입 + tools.css/tools.js/asset-manifest.json 생성번들)가 HANDOFF.md 75차에 기록된 예상과 정확히 일치함을 확인. 결론: 사용자가 이미 `75cha_item10_web_settings_gdrive.ps1`을 실행해 push까지 완료했고, HANDOFF.md의 "실행 대기" 표기만 뒤처져 있던 것(핵심 발견 27/38과 동일 패턴). 코드 변경 없이 이 파일과 HANDOFF.md의 표기만 정정. 다음 세션 최우선: 항목 12(25차, commit `d338afb7`, `LOG_UPLOAD_TARGETS`에 "gdrive" 누락 수정)부터 이어서.
- **[77차]** 세션 시작 체크포인트(`git ls-remote`)로 carrot-ryu `c9a03b5`/carrot-ryu-note `102131e` 확인, 지침 문서(v2, 커밋 `102131e`)/HANDOFF.md/CURRENT_STATUS.md 재확인 후 이어받음. 항목 12(25차, commit `d338afb7`, `LOG_UPLOAD_TARGETS`에 "gdrive" 누락 수정) 착수: 원본 커밋 patch를 `github.com/.../commit/d338afb7.patch`로 직접 조회한 결과 `openpilot/selfdrive/carrot/server/services/web_settings.py` 한 파일, 한 줄 변경 (`LOG_UPLOAD_TARGETS = {"carrot", "toss"}` -> `{"carrot", "toss", "gdrive"}`). 새 베이스(`c9a03b5`)의 해당 파일 blob hash(`f41e1bb4b4a31b380b33968d41781a98101b2661`)가 원본 커밋의 pre-image blob hash와 완전히 일치함을 `git hash-object`로 확인 -- 그 사이 다른 세션이 이 파일을 건드리지 않았음을 실증(byte-exact 재적용 가능). anchor 매치 1회 확인. 반영 스크립트(`77cha_item12_log_upload_targets.ps1`) 작성/전달, 사용자 실행 후 commit `27d81a4`로 push 완료를 GitHub compare API로 재확인(원본 25차 diff와 완전히 동일). devnotes 반영 스크립트(`77cha_devnotes_carrot_ryu_note.ps1`)는 최초 실행 시 WIP.md 상단 anchor 검증 로직이 파일 중간의 기존 "# WIP" 헤더 중복(기지 이슈)까지 세면서 2회 매치로 잘못 중단됨 -- StartsWith 방식으로 고친 -v2로 재전달해 해결, push 완료(`f76209d`) 확인. 실차 검증: 미실시.
- **[78차]** 사용자가 올린 첫 파일이 채팅에서 설명한 "항목 17 스크립트"와 다른 파일(실제로는 이미
  push 완료된 77차-fix devnotes 정정 스크립트)임을 `git log` 대조로 발견(16절), 재업로드받은 실제
  항목 17 스크립트(`77cha_item17_gdrive_file_scope.ps1`, 챗지피티 작성)를 반영 전 원본 커밋
  (`c704371a`, 32차)의 부모 SHA/pre-image blob hash 일치 여부부터 독립 재현으로 먼저 검증(9절).
  실행 과정에서 버그 3건을 사용자 실행 로그로 실증하며 순차 수정: (1) 8자리 축약 SHA로는 GitHub이
  `git fetch`를 거부함 -- 40자리 전체 SHA로 교체, (2) `git diff | Out-File -Encoding ascii`가
  PowerShell 파이프라인 캡처 과정에서 patch를 손상시킴(`patch fragment without header`) --
  `git diff --output=<file>`로 교체, (3) `$Diff` 배열에 대한 `-notmatch` 검사가 PowerShell의
  배열 매치 시맨틱("전체가 매치 안 하면 참"이 아니라 "매치 안 하는 원소들의 배열 반환") 때문에
  항상 거짓 실패로 중단됨 -- 이미 읽어둔 스칼라 문자열 `$PatchText`로 교체. (4) `py_compile`
  검증은 핵심 발견 37과 동일한 Windows 앱 실행 별칭 문제가 재발해 `Get-PythonCmd` 함수를 재적용.
  v2~v5까지 9절 버전표시 규칙대로 순차 전달, 최종 v5 실행으로 carrot-ryu commit `c197cd4e`(32차
  "restore drive.file scope and auto-create Drive folder")로 push 완료. push 후 독립 clone으로
  새 HEAD의 대상 파일 blob hash가 원본 32차 커밋 결과 blob과 byte-exact 일치함을 재확인(16절).
  이전 대화(코드 push까지는 동일 작업)에서 devnotes 3개 파일 반영이 HANDOFF.md 작성 전에 끊겨
  push되지 못했음을 이번 세션 시작 시 `git ls-remote`(carrot-ryu-note가 여전히 `227bde4`, 77차-fix)
  로 확인 -- 76차/77차와 동일한 "코드 push는 됐는데 devnotes만 뒤처짐" 패턴(핵심 발견 27/38)의
  재발이자, devnotes 자체가 세션 종료로 아예 반영되지 못한 새로운 변형. 이번 세션에서 처음부터
  다시 확인/재작성해 CURRENT_STATUS.md/WIP.md/HANDOFF.md 3개 파일을 완성, 한 번에 push했다.
  실차 검증: 미실시. 상세: 핵심 발견 39. HANDOFF.md 78차 참고.
- **[79차]** 항목 18(33차, commit `789667f7`, ko.js gdrive 클라이언트 유형 안내 문구 수정: "데스크톱
  앱 유형" -> "TV 및 제한된 입력이 있는 기기 유형") 착수. 원본 커밋을 `.patch` 엔드포인트로 조회(API
  rate limit 회피), sparse-checkout으로 `web/` 구조를 확인해 이 파일이 `index.html`에서 직접
  `<script>`로 로드되고 build.mjs 번들 대상이 아님을 확인(npm 빌드 불필요). anchor 1회 매치를
  sandbox에서 사전 시뮬레이션 후 스크립트 전달. 최초 전달본(v1)이 실행 중 anchor 0회 매치로 안전하게
  중단됨 -- 스크립트(.ps1) 자체가 UTF-8 BOM 없이 생성되어 PowerShell 5.1이 CP949로 잘못 해석,
  스크립트 내부 한글 anchor 문자열이 로드 시점에 이미 깨져 있었던 것(9절 필수 규칙에 이미 명시된
  이슈의 재발이나 이번엔 Claude가 스크립트 생성 시 직접 저지름; 15절/18절의 강제진행 금지 안전장치는
  정상 동작해 대상 파일 손상 없음). BOM 포함 `-v2`로 재생성해 해결, carrot-ryu commit
  `a959576f6973b44d878617399241cd35c47bf1bd`로 push 완료. push 후 GitHub compare API + raw
  조회(SHA고정)로 변경 파일 1개·원본 33차 diff와 완전 일치·byte-exact를 재확인(16절). 실차 검증:
  미실시. 다음 세션 최우선: 항목 20(36차, commit `0835b059`) -- 재적용 순서 10번.
- **[75차]** 위 74차까지의 devnotes 공백을 사후 동기화하고, 이어서 재적용 순서 6번째인 항목 10(23차, commit `272834b`, web settings log_upload에 Google Drive 계정 연결 UI 추가)을 착수. base.css/components.js/schema.js는 pre-image hash가 현재 베이스와 정확히 일치해 전체교체, en.js/ko.js/zh.js는 다른 세션들이 추가한 번역 키와 공존하도록 anchor 기반 15개 키 삽입으로 처리. 독립 `git clone`에 실제 적용 + `npm install && node build.mjs`로 생성 번들 3종 재생성까지 확인, 변경 파일이 원본 커밋과 정확히 같은 9개임을 `git status`로 확인, `node --check` + `node --test`(747/747) 전부 통과. 반영 스크립트 (`75cha_item10_web_settings_gdrive.ps1`) 작성 및 임베드 데이터 GitHub 최신 상태 대비 round-trip 재검증까지 완료, 실행 대기. 상세: HANDOFF.md 75차 참고.
- **[68차]** 세션 시작 체크포인트(`git ls-remote`)로 carrot-ryu(`81754ea3`)/carrot-ryu-note(`8cfa5b92`)가 직전 세션 보고와 일치함을 확인. 사용자와 협의해 항목 22(39차) 착수 전 항목 13~16(27~30차, 경로안내 박스 조정)을 먼저 재적용하기로 결정, 착수 중 항목 19(34차/33cha)까지 선행 필요함을 추가로 발견(위 26번 참고). hud_renderer.py 한 파일에 13→14→15→16→19를 순서대로 적용 -- 각 단계 anchor 1회 매치 확인, 최종 결과에 항목 22(`797fca2e`)의 hud_renderer.py 부분 diff가 정상적으로 붙는 것까지 별도 검증(9절/16절). `py_compile` 통과. `_format_eta_text`가 `_format_eta_time_text`로 이름이 바뀌는 부분(항목13)의 유일 호출부도 같은 블록 안에서 함께 치환됨을 확인해 dangling 참조 없음. 반영 스크립트 실행 대기, 항목 22 본편(스크린샷 업로드 UI + 번들 재생성)은 push 확인 후 이어서 진행.
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
- **[45차-정정]** 45차 devnotes(carrot-ryu-note commit `0b0d322`)가 실제로는 핵심 발견 30의 최종 결론(esbuild 플랫폼 비결정성 -> Linux sandbox 빌드) 이전, "사용자 PC 재빌드가 아직 실패하지 않았던" 중간 초안 내용으로 push됐던 것을 재확인 절차 중 발견. carrot-ryu 코드(commit `99b49a1`)는 커밋 메시지 전문/sha256 비교로 최종본대로 정상 반영/검증됐음을 확인, devnotes만 중간 초안 상태였던 것으로 결론(핵심 발견 31). 원인은 한 세션 내 동일 파일명(`45cha_devnotes_carrot_ryu_note.ps1`) 스크립트 재전달로 인한 사용자 PC 측 파일명 충돌 가능성이 유력(직접 재현은 못 함). 부수적으로 `git clone --depth 1` + `git show --stat`이 grafted root 취급되어 무관한 파일이 대량 나열되는 착시도 확인/배제. 이 커밋으로 HANDOFF.md/CURRENT_STATUS.md를 실제 최종 상태로 재동기화.
- **[46차]** 사용자가 제공한 실기기 스크린샷 2장(도구 탭 git pull/reboot 로그, 로그 탭 사진목록)과 실기기 촬영 영상 1개(20260916-095343.mp4)로 직전 HANDOFF "최우선" 이월 1~4번을 전부 실기기 검증 완료: (1) carrot-ryu HEAD(99b49a1) 실기기 배포/재부팅 확인, (2) 사진 목록 크래시 해소 확인, (3) delete_all_videos 스크린샷 포함 삭제 확인, (4) 로그탭 새로고침 목록 갱신 확인. 추가로 녹화 버튼 깜빡임을 영상 프레임 정량 분석(6fps, 버튼 영역 평균 RGB)으로 실증(핵심 발견 32). 코드 변경 없음, devnotes만 갱신. 상세: HANDOFF.md 46차 참고.
- **[47차 신규]** 사용자가 실기기 스크린샷 버튼으로 찍은 사진이 세로(1080x2160, 상단 대부분 검정) 이미지로 저장되고 용량도 과도하게 크다고 제보. 원인 조사 결과 `screenshot_capture.py`가 쓰던 `rl.take_screenshot()`이 raylib 내부적으로 `render 크기 * GetWindowScaleDPI()`로 캡처 크기를 계산하는데(rcore.c), 이 기기에서 DPI 스케일이 비등방(가로/세로 배율이 다름)으로 나와 가로 2160x세로 1080이어야 할 캡처가 세로 1080x가로 2160으로 뒤집혀 저장됨을 확인. 같은 프레임버퍼를 읽되 DPI 배율 계산이 없는 `rl.load_image_from_screen()`(영상 녹화 파이프라인이 `rl.load_image_from_texture()`로 동일하게 DPI 우회 방식을 쓰는 것과 동일한 원리)으로 교체해 해결. 겸사겸사 저장 포맷을 PNG(무손실)에서 JPG로 변경 -- `SCREEN_RECORDING_PHOTO_EXTS`(carrot/server/config.py)에 ".jpg"/".jpeg"가 이미 등록돼 있어 백엔드/프론트엔드 추가 수정 없이 바로 인식/목록/썸네일/서빙됨을 코드 조사로 확인. 실차 검증: 미실시(스크립트 실행 대기). 상세: FINDINGS.md 2026-09-16(47차) 항목, 핵심 발견 33.
- **[48차 신규]** 사용자 요청("체크포인트")으로 지침 문서 4절 0단계(git ls-remote SHA 고정)부터 세션 시작. carrot-ryu HEAD가 이미 `41fd34a7`(47차 스크린샷 수정)로 push돼 있음을 확인 -- 47차 최우선 이월 1번이 세션 사이에 사용자 실행으로 해소돼 있었음. 이어서 사용자가 제공한 실기기 스크린샷 7장(로그 전송 확인창 2장, HUD 디바이스 직접촬영 1장, 로그탭 화면녹화 목록 2장, 구글드라이브 폴더/파일 목록 2장)으로 이전 세션들의 이월 항목을 실기기 검증: (1) Issue 1(당근서버 라벨, 36차) 정상, (2) Issue 3(햄버거 메뉴 탭 무관 업로드, 36차) 정상, (3) 39차/46차에서 미확인이던 "선택 전송" 버튼의 실제 전송 성공 여부 -- 구글드라이브에 방금 업로드된 타임스탬프 mp4 파일 존재로 실증, (4) Issue 4(Drive 폴더 중복, 37차 락) 폴더 1개만 존재 재확인, (5) 27차 HUD 경로안내 박스 레이아웃 재확인. 코드 변경 없음, devnotes만 갱신. 상세: HANDOFF.md 48차 참고.
- **[49차 신규]** 사용자가 실기기 스크린샷 2장(정상 캡처 예시, 실제 로그탭 화면 -- 사진 0건/영상 3건)을 제공하며 "스크린샷 버튼이 안 눌러지고 로그탭에 저장되지 않음" 제보 + 스크린샷 버튼을 참고 사진의 빨간 원 위치로 이동해달라는 요청. 로그탭 목록에 JPG가 0건임을 확인해 제보를 실증. 클릭 처리 경로(Widget._process_mouse_events)와 capture_onroad_screenshot()(47차 버전), pyray 바인딩(comma-deps-raylib==6.0.0.1.post101, sandbox 실제 설치로 API 존재 확인) 조사 결과 명백한 버그는 못 찾음(11절 원칙에 따라 원인을 추측으로 확정하지 않음). 대신 screenshot_capture.py의 3개 실패 분기 + 예외 처리, screenshot_button.py의 _on_click 진입 지점에 cloudlog.debug/warning/exception 진단 로그를 추가해 다음 실차 테스트에서 원인이 드러나도록 함. 참고 사진 픽셀 분석으로 hud_renderer.py의 스크린샷 버튼 위치를 화면 중앙(anchor_x)에서 좌측 170px(버튼폭 140+간격 30) 이동, record 버튼은 수식상 이전과 동일 위치 유지. py_compile/ast.parse 통과 + hud_renderer.py Replace-Block 매치 카운트 1 확인. 실차 검증: 미실시(진단 로그 확인 및 버튼 위치 확인 모두 다음 세션 최우선). 상세: FINDINGS.md 2026-09-16(49차) 항목, 핵심 발견 34. HANDOFF.md 49차 참고.
- **[50차 신규]** 49차 반영 스크립트가 실제로 실행된 것을 사용자 제공 실기기 로그(위젯 실행 로그: `git pull` 41fd34a74..dfdbfff9a Fast-forward, `reboot`)로 확인, carrot-ryu HEAD가 `dfdbfff9a7df48aac869b1417ea6398dd6768f32`임을 `git ls-remote`로 재확인. 사용자가 제공한 `swaglog` grep 결과(49차 진단 로그 반영 전/후 두 구간)를 분석: git pull 이후 매 실패마다 `screenshot_button.py:28 _on_click`에서 `capture_onroad_screenshot: export_image failed for ...` 경고가 raylib의 `Failed to export image` 경고와 함께 찍힘 -- 이는 클릭이 `_on_click()` -> `capture_onroad_screenshot()`까지 정상 전달되고 `load_image_from_screen()`도 성공했음을 뜻하므로(11절, 실제 로그 근거로 확정), 49차 최우선 이월 2번 중 (a) 클릭 전달 문제 가설은 배제됨. 반면 `rl.export_image()` 자체가 raylib 레벨에서 매번 실패하는 것이 확정 원인이며, git pull 이전(commit `41fd34a7`, 47차) 구간에도 동일한 raylib 경고가 이미 있었다는 점, 46차까지(PNG 저장)는 방향은 틀렸어도 저장 자체는 성공했다는 점을 근거로 "이 기기의 raylib 빌드(comma-deps-raylib==6.0.0.1.post101)가 JPG export를 지원하지 않는다"를 유력 가설로 제시(단, 11절 원칙상 확정 아님 -- DPI 수정과 확장자 변경이 같은 커밋에 같이 들어가 변수 미분리 상태). 변수를 분리하기 위해 저장 확장자만 `.jpg` -> `.png`로 되돌리는 최소 변경(`load_image_from_screen()` DPI 수정은 유지)을 반영, 사용자가 스크린샷 버튼 위치는 의도한 대로 됐다고 확인함(49차 미완료 3번 해소). 코드 변경 1개 파일(`screenshot_capture.py`), 반영 스크립트 실행 대기. 실차 검증: 미실시. 상세: FINDINGS.md 2026-09-16(50차) 항목, 핵심 발견 35. HANDOFF.md 50차 참고.
- **[51차 신규]** 사용자가 50차 PNG 롤백 실차 결과 사진 2장(HUD 없는 순수 배경 스크린샷, carrotweb 로그탭에 파일이 실제로 잡힌 화면)을 제공하며 시계/온도 HUD 누락과 480p 다운스케일을 요청. hud_renderer.py _render()에서 스크린샷 버튼 render()가 _draw_date_time/_draw_tpms/_draw_egpu_badge/_draw_cruise_speed_animation보다 먼저 호출되는 구조적 타이밍 문제를 확정, 캡처를 프레임 끝으로 미루도록 수정(screenshot_button.py + hud_renderer.py) + screenshot_capture.py에 480p 다운스케일(rl.image_resize) 추가. 사용자가 Termux 사용을 명시해 PowerShell 대신 bash 스크립트로 전달(9절). 실차 검증은 다음 세션 최우선. 상세: FINDINGS.md 2026-09-16(51차) 항목, 핵심 발견 36. HANDOFF.md 51차 참고.
- **[52차]** 51차 480p/캡처타이밍 수정 실차 검증 중 사용자가 "오른쪽 HUD가 안 나온다"고 제보했다가 곧 "화면 전체가 다 안 나온다"로 정정. augmented_road_view.py의 실제 호출 순서를 코드로 확인해, 51차가 옮긴 캡처 호출이 여전히 HudRenderer._render() *안에서* 실행되고 있어 alert/driver-state 오버레이와 _draw_border_carrot()(차량명/시계/LD·LT·SR/laneless/git branch/IP를 그리는 곳)보다 앞서 실행됨을 확정. 캡처 호출을 AugmentedRoadView._render()의 맨 끝(_draw_border_carrot() 다음)으로 옮기고, HudRenderer는 대기 플래그를 소비만 하는 공개 메서드(consume_pending_screenshot_capture())를 노출하도록 hud_renderer.py/augmented_road_view.py/screenshot_button.py 3개 파일 수정. 실차 검증은 다음 세션 최우선으로 이월. 상세: HANDOFF.md 52차 참고.
- **[53차, 설계 논의만·코드 변경 없음]** 세션 시작 체크포인트(git ls-remote)로 carrot-ryu HEAD가 이미 `e4816edc`(52차)임을 확인 -- 52차 반영 스크립트가 실제로 이미 실행/push 완료된 상태였음(devnotes에는 그 사이 "push 대기"로 남아있던 괴리, 16절/핵심 발견 27과 동일 패턴, 이번 세션에서 CURRENT_STATUS.md/HANDOFF.md를 바로잡음). 52차 반영 이후에도 실기기 스크린샷에서 border 관련 HUD가 여전히 빠진다는 것을 전제로, 화면녹화(정상 동작)와 스크린샷(계속 실패)의 구조적 차이를 application.py 코드로 대조: 녹화는 오프스크린 render texture에 그린 뒤 end_texture_mode() 직후 load_image_from_texture()로 안전하게 추출하지만, 스크린샷은 render texture가 없는 상태에서 위젯 렌더 콜백 도중 load_image_from_screen()으로 직접 읽어 raylib 배치 플러시 타이밍에 구조적으로 취약함을 확정. 해결 방향으로 "스크린샷 버튼을 누르면 녹화 로직으로 딱 1프레임만 임시 render texture에 떠서 이미지로 저장"(사용자 제안)에 합의: GuiApplication에 스크린샷 pending 플래그 추가 -> 렌더 루프 시작 시 녹화 중이 아니면 기존 _ensure_render_texture_for_recording() 패턴으로 그 프레임만 임시 render texture 생성 -> end_texture_mode() 직후(녹화 추출 지점과 동일 위치)에서 load_image_from_texture()로 캡처 후 기존 480p 다운스케일/export_image 로직 재사용 -> 캡처 직후 임시 텍스처는 unload_render_texture()로 정리(녹화 중이면 별도 텍스처 없이 같은 프레임 재사용). application.py까지 건드리는 범위라 사용자에게 진행 여부를 물었고, 사용자가 다음 세션에 구현하기로 결정 -- 이번 세션은 코드 변경 없이 설계 합의까지만 진행(51·52차의 augmented_road_view.py 캡처 호출부는 다음 세션 구현 시 되돌릴 예정). 실차 검증: 미실시(코드 변경 자체가 없었음). 상세: HANDOFF.md 53차 참고.
- **[54차]** 53차에서 합의된 render-texture 재사용 설계를 코드로 구현. application.py에 request_temp_capture(callback) 신규 메서드(초기화부/렌더루프 시작 시 임시 render texture 생성/end_texture_mode() 직후 추출·콜백호출, 3개 Replace-Block, selfdrive import 없이 제네릭 레이어링 유지) 추가, screenshot_capture.py를 save_screenshot_image(image)로 전체 재작성(캡처된 rl.Image를 받아 480p 다운스케일+PNG export만 담당), screenshot_button.py를 gui_app.request_temp_capture() 호출 방식으로 전체 재작성, hud_renderer.py의 consume_pending_screenshot_capture() 제거, augmented_road_view.py의 51·52차 캡처 호출부 원복 -- 총 5개 파일. 반영 스크립트 최초 실행 시 py_compile 검증 단계에서 콘솔 출력 없이 조용히 중단(commit/push 안 됨, 안전장치는 정상 동작): Linux에서 동일 Replace-Block 3곳을 재현해 py_compile이 실제로는 정상 통과함을 확인해 코드 결함이 아님을 확정. 원인은 Windows PC의 `python3` 명령이 앱 실행 별칭(Microsoft Store 스텁)으로 가로채져 콘솔 출력 없이 실패하는 것으로 추정(핵심 발견 37) -- `py -3`/`python3`/`python` 순으로 실제 동작하는 명령을 자동탐지하는 `Get-PythonCmd` 함수를 추가한 -v2 스크립트(9절 버전표시 규칙)로 재전달, 사용자가 실행해 commit `e4816edc..e047beb3` push 성공. push 후 `git ls-remote`+SHA고정 raw URL로 5개 파일 전체 재조회, py_compile 5개 전부 재통과, grep으로 `request_temp_capture`/`save_screenshot_image` 존재 및 `consume_pending_screenshot_capture`/`capture_onroad_screenshot` 0건(완전 제거)까지 확인해 실제 반영 내용이 설계와 정확히 일치함을 실증(6절/16절 검증 시퀀스). 실차 검증: 미실시(다음 세션 최우선 -- border HUD 전부 포함 여부, 480p 다운스케일, PNG 저장 모두 이 재설계로 한 번에 재검증). 상세: HANDOFF.md 54차 참고.

- **[55차]** 54차 render-texture 재사용 스크린샷 재설계 실차 검증 결과, 480p 다운스케일/PNG 저장 자체는 정상 동작했으나 결과 이미지가 상하반전(사용자 보고: "화면이 상하좌우 뒤바뀜")으로 저장됨을 확인. application.py를 코드로 조사해 원인 확정: rl.load_image_from_texture()가 OpenGL render texture의 아래->위 픽셀 순서를 그대로 반환하는데, 영상 녹화 경로(같은 application.py)는 이미 ffmpeg "-vf vflip"으로 이를 보정하고 있었던 반면 screenshot_capture.py의 save_screenshot_image()에는 이 보정이 빠져 있었음(11절: 코드 대조로 확정, 추측 아님). save_screenshot_image() 맨 앞에 rl.image_flip_vertical(image) 한 줄만 추가하는 최소 수정(Replace-Block 1곳, anchor 1회 매치 확인). 사용자가 Termux 사용 환경이라 51차와 동일하게 bash 스크립트로 전달(9절). 실차 검증은 다음 세션 최우선.

- **[56차, 코드 변경 없음]** 사용자가 실기기 스크린샷 버튼으로 촬영한 이미지 1장(HYUNDAI_GENESIS(CAMERA SCC) 온로드 HUD, 16:59:49 09-16(수))을 제공하며 "정상됨" 확인. 55차 rl.image_flip_vertical() 수정 이후 상하반전 없이 정방향으로 저장됨을 실차 검증(12절) -- 이미지에 차량명/시계/날짜/LD·LT·SR/laneless/git branch/IP 등 border HUD 요소와 CPU·MEM·DISK, 속도/기어/LIMIT까지 전부 정상 포함돼 있어 54차 render-texture 재설계 항목(border HUD 누락/480p/PNG)도 함께 재확인됨. 49~55차에 걸쳐 순차 수정해온 스크린샷 관련 이슈(HUD 누락 -> DPI 반전 -> 캡처 타이밍 -> 상하반전)가 이 확인으로 전부 해소됨. 코드 변경 없음, devnotes만 갱신.

- **[57차, 설계 논의만·코드 변경 없음]** 사용자 요청으로 "carrot-ms 모델 셀렉터 코드 분석 착수" 시작. 41개 모델셀렉터 전용 커밋(carrot-ms에만 있고 carrot-wip에는 없는 117건 중 필터링)을 조사했으나, `git merge-base --is-ancestor`로 전수 검증한 결과 전부 6~7차 체크포인트 기준점(`02015190f5`, 2026-09-12)의 조상 커밋이어서 이미 carrot-ryu에 반영돼 있음을 확인(carrot-wip/carrot-ms를 각각 blob 없이 bare clone 후 커밋 메시지 집합 비교, api.github.com rate limit 회피). carrot-ryu의 `carrot/model_selector/` 21개 파일이 fork 이후 무수정 상태이고, README 명시 upstream 최소침습 지점 6곳(process_config.py/manager.py/modeld/helpers.py/carrot/server/app.py/web/index.html/ui/mici/layouts/home.py) 및 params_keys.h의 DrivingModelName/PendingModelName 등록까지 전부 정상 배선됨을 직접 확인. 사용자가 이 결과를 바탕으로 범위를 재설정: 모델셀렉터에 국한하지 않고, **carrot-ryu 브랜치 생성(fork point `02015190f5`) 이후 carrot-ms에 새로 쌓인 커밋 전체**(현재 25건, WIP_SYNC.md 57차 체크포인트 참고)를 대상으로 (1) 우리 차량(제네시스 DH 2015)에 불필요한 것 제외, (2) 필요한 것만 선별, (3) carrot-ryu 자체 커스텀 코드와 충돌/상충 여부 분석하는 방향으로 다음 세션 작업을 설계하기로 함(이번 세션은 설계 방향 합의까지만, 실제 분석은 다음 세션). 부수적으로 항목 36(55차 `image_flip_vertical` 수정)이 "반영 스크립트 실행 대기"로 남아있었으나 실제로는 carrot-ryu HEAD가 이미 `9ccf1206`(커밋메시지 `55cha: flip render-texture screenshot vertically`)로 push 완료돼 있음을 `git ls-remote`로 확인(16절/핵심 발견 27과 동일 패턴, 다음 세션에서 정식 반영 표기 정정 필요).
- **[59차, 설계 합의·저장소 정리]** 사용자 제안으로 carrot-ms 신규 커밋 선별 반영(2절)
  방식의 누적 부담을 완화하기 위한 "carrot-ryu-vN 아카이브 + 재생성" 정책을 논의/합의
  (PROJECT_INSTRUCTIONS_carrot-ryu.md 20절 신설). carrot-ryu는 디바이스 배포 브랜치명으로
  계속 고정하고, 재생성 시점마다 직전 상태를 carrot-ryu-vN으로 스냅샷 보관한 뒤 carrot-ms
  최신 베이스로 carrot-ryu를 재구성하고 vN의 커스텀 코드(이 파일의 "코드 수정 현황" 번호
  리스트)를 체크리스트 삼아 이식하는 방식. 이번 세션에서 첫 적용으로 (1) 지침 1절과
  어긋나던 정체불명 브랜치 `c3-ms-dev` 삭제, (2) 현재 carrot-ryu(commit `9ccf1206`) 스냅샷을
  `carrot-ryu-v1`으로 생성(반영 스크립트 실행 대기). 실제 carrot-ms 베이스 재생성과 v1 코드
  이식은 규모가 커(36개 항목, 서로 무관한 여러 서브시스템) 다음 세션들로 이월(17절).
- **[60차, devnotes 오염 발견/복구]** 세션 시작 SHA 고정 조회 중 devnotes/HANDOFF.md(59차분)에
  WIP_SYNC.md 전체 내용이 PowerShell 히어스트링 조각과 함께 잘못 이어붙어 있고, 실제
  devnotes/WIP_SYNC.md는 0바이트로 커밋되어 있음을 발견(59차 또는 이전 반영 스크립트의
  히어스트링 종료 처리 오류로 추정). HANDOFF.md 안에 남아있던 원문을 바이트 단위로 정확히
  추출해 내용 손실 없이 복구, HANDOFF.md/WIP_SYNC.md를 각각 정상 상태로 재작성(코드 변경
  없음, 반영 스크립트 실행 대기). 20절 리셋 착수 여부는 이번 세션에서 재확정 안 됨.
- **[61차, 20절 실제 리셋 실행]** 사용자 승인으로 carrot-ryu를 carrot-ms 현재 HEAD(`706efb47`)로
  재생성(force-push). carrot-ryu-v1(`9ccf1206`)은 변경 없이 보존. 이 시점부터 carrot-ryu에는
  커스텀 코드가 전혀 없으며, devnotes 61차 갱신은 무료 사용량 소진으로 다음 세션으로 이월됨.
- **[62차, devnotes 사후 동기화]** 세션 시작 재확인 중 코드 브랜치(이미 706efb47로 리셋됨)와
  devnotes(여전히 60차 상태)가 서로 다른 시점을 가리키는 것을 16절 원칙대로 발견, 사용자 확인
  후 devnotes 네 파일을 실제 코드 상태에 맞춰 사후 동기화(코드 변경 없음). 다음 세션부터 v1의
  "코드 수정 현황" 36개 항목을 서브시스템 단위로 하나씩 재적용 예정(20절 5번, 17절).
- **[63차]** carrot-ryu-v1 "코드 수정 현황" 항목 3(온로드 시계 초단위 표시 + 스크린샷 버튼,
  12차 684b30d 원본)을 새 베이스(706efb47) 위에 재적용, commit `429f105e`로 push 완료. 착수
  스크립트(reapply_12cha.ps1)가 hud_renderer.py 5번 Replace-Block에서 CRLF/LF 불일치로 중단된
  것을, 저장소 루트 `.gitattributes`의 `* text=auto`(일부 Windows Git 환경에서
  core.autocrlf=false를 줘도 체크아웃 시 CRLF로 변환될 수 있음, GitHub 원본 blob 자체는 LF)로
  원인 확정하고, Replace-Block에 매칭 전 CRLF->LF 정규화(9절 기존 원칙)를 추가한
  reapply_12cha-v2.ps1로 재시도해 해결. `git ls-remote` + commit diff(API rate limit 회피)로
  반영 내용이 의도한 3개 파일과 정확히 일치함을 확인. 12차 원본 그대로이며, 이후 세션들에서
  누적된 스크린샷 후속 수정(25·26~28·30~36번: DPI/캡처 타이밍/render-texture 재설계/상하반전
  등)은 아직 미반영 -- 다음 세션 이후 순서 확정 필요. 실차 검증: 미실시(git pull 금지 상태 유지
  중).
- **[64차]** carrot-ryu-v1 "코드 수정 현황" 항목 4(온로드 시계 좌측 화면 경계 잘림 수정, 13차
  2adced8 원본)를 새 베이스(429f105e) 위에 재적용, commit `4e3b44a8`로 push 완료. 원본 커밋이
  hud_renderer.py `_draw_date_time` 한 곳만 건드리는 작은 diff였고, 12차 재적용(63차) 이후에도
  해당 함수가 원본 base(`0e9c84a51e`)와 동일하게 남아있어 Replace-Block으로 그대로 재적용.
  치환 결과 blob이 원본 13차 커밋의 결과 blob(`d7e8d7b6a5`)과 완전히 일치함을 diff로 확인(바이트
  단위 재현). 실차 검증: 미실시(git pull 금지 상태 유지 중).

- **[65차]** carrot-ryu-v1 "코드 수정 현황" 항목 25(온로드 화면 원형 녹화버튼 추가, 42차
4f81ab75 원본)를 새 베이스(`4e3b44a8`, 64차 위) 위에 재적용, commit `b152e192`로 push 완료.
record_button.py 신규 추가(스크린샷 버튼 오른쪽에 배치, ScreenRecord 파라미터를 토글하는 원형
녹화 버튼, 녹화 중엔 빨간 원 채움) + hud_renderer.py에 import/UIConfig 필드/__init__/_render/
user_interacting 5곳 배선. ScreenRecord 파라미터는 params_keys.h에 이미 등록되어 있어 추가
등록 불필요, put_bool_nonblocking(params_pyx.pyx)/gui_app.is_recording()(application.py)/
Widget/set_click_callback 모두 새 베이스에 그대로 존재함을 확인. 원본 42차 커밋과 동일한
diff임을 git ls-remote + commit diff로 재확인. 실차 검증: 미실시(git pull 금지 상태 유지 중).

- **[66차]** carrot-ryu-v1 "코드 수정 현황" 항목 27+28(44차 e2f35619 커밋 일부)을 새
베이스(`b152e192`, 65차 위) 위에 재적용, commit `0d511753`으로 push 완료. 44차 원본은
사실 항목 26·27·28을 커밋 하나(e2f35619)로 묶어 반영했었으나, 그중 항목 26(screenshots.js의
formatLogBytes import 수정)은 전제가 되는 screenshots.js 파일 자체(항목 11, 24차 작업물)가
아직 새 베이스에 없어서(GitHub에서 404 확인) 이번엔 적용 불가, 파일 의존성이 없는 항목
27+28만 먼저 반영: (27) dispatcher.py의 "전체 영상 삭제"가 하드코딩된
/data/media/0/videos 한 곳만 지우던 것을 이미 존재하는 SCREEN_RECORDING_DIRS(영상+스크린샷
폴더 전체) 기준으로 확장(비동기/동기 경로 두 곳 모두), (28) record_button.py 전체교체 +
hud_renderer.py 1줄 -- 녹화 중 버튼이 계속 채워진 채로만 있던 것을 기존 _blink_timer(카메라감지/
과열경고에 이미 쓰던 프레임 카운터)를 재사용해 채움/테두리를 번갈아 그리도록 깜빡임 추가.
원본 44차 diff와 동일함을 git ls-remote + commit diff로 확인. 남은 항목 26(screenshots.js)은
항목 11(24차, 화면녹화 탭 사진 스트립 신규 생성)과 항목 23(39cha-fix, formatRelativeEpoch
import)까지 먼저 반영된 뒤에 이어서 처리해야 함 -- WIP_SYNC.md에 이 의존관계 기록 필요(다음
세션 이월). 실차 검증: 미실시(git pull 금지 상태 유지 중).

- **[67차]** 66차 HANDOFF 미완료 1번(항목 11+23 -> 26 의존관계 해소) 순서를 사용자가 확정: "항목 11만 우선 적용(22/23/26은 이월)". carrot-ryu-v1 "코드 수정 현황" 항목 11(24차, 화면녹화 탭 사진 스트립 신규 생성, commit `a7a912c1`)을 새 베이스(`0d511753`, 66차 위) 위에 재적용 -- 원본 commit patch를 github.com/.../commit/a7a912c1.patch로 직접 조회해 9개 소스 파일(config.py/catalog.py/routes.py/index.html/en.js/ko.js/zh.js/runtime.js/style.css) 수정 + screenshots.js 신규 파일 내용을 확인하고, 독립적인 실제 `git clone`(carrot-ryu)에 적용해 anchor 전부 1회 매치, 그 자리에서 `npm install && node build.mjs`로 생성 번들(logs.css/asset-manifest.json/logs.js)까지 재생성, `node --check`(runtime.js/screenshots.js/generated logs.js) + `python3 -m py_compile`(config.py/catalog.py/routes.py) + `node --test`(747/747) 전부 통과 확인(핵심 발견 30 재발 방지 -- 소스만 고치고 번들 재생성을 빠뜨리지 않도록 스크립트 자체가 npm install && node build.mjs를 실행). py/routes.py 3개 파일과 screenshots.js/style.css는 원본 24차 결과와 바이트 단위로 완전히 동일함을 diff로 확인, index.html/en.js/ko.js/zh.js/runtime.js는 그 사이 다른 세션들의 변경(Google Drive UI, 설정 검색 등)과 정상 공존하며 병합됨을 확인. 반영 스크립트(`reapply_item11_67cha.ps1`) 전달, 실행 대기. 부수적으로 이 파일 최상단 carrot-ryu HEAD 표기가 61차 커밋으로 오래 방치돼 있던 것을 16절에 따라 발견/정정(코드 변경 아님).
- **[81차, devnotes 정정만 · 코드 변경 없음]** 세션 시작 체크포인트(`git ls-remote`)에서 carrot-ryu
  HEAD가 이미 `1bd10a7c790aea4a08c605502379a5da88f96aad`로, HANDOFF.md(80차)에 기록된 base
  (`a959576f`, "실행 대기")와 다름을 발견(4절/16절). GitHub `.diff` 엔드포인트(api.github.com
  rate limit 회피)로 `a959576f`..`1bd10a7c` 구간을 조회한 결과 정확히 1개 커밋(`1bd10a7c`,
  커밋 메시지 "36cha: screenrecord tab upload/download UI + gdrive label fix + tab-aware
  hamburger menu")이며, 변경 파일 12개(routes.py `api_screenrecord_upload` 신규 엔드포인트 +
  생성 번들 3종 + 소스 8개)가 80차 HANDOFF.md에 기록된 항목 20(36차, `0835b059`) 재적용 내용과
  정확히 일치함을 확인. 결론: 사용자가 이미 `80cha_item20_screenrecord_upload.ps1`을 실행해
  push까지 완료했고, HANDOFF.md/CURRENT_STATUS.md의 "실행 대기"/"push 미실시" 표기만 뒤처져
  있었던 것(핵심 발견 27/38과 동일 패턴). 코드 변경 없이 이 파일과 HANDOFF.md의 표기만 정정.
  다음 세션 최우선: 항목 21(37차, `_ensure_folder()` TOCTOU 레이스 수정, asyncio.Lock) 재적용부터
  착수.
- **[82차, 코드 push 대기 · v4로 py_compile 원인 수정]** 항목 21(37차, gdrive_upload.py
  _ensure_folder() Drive 폴더 중복생성 레이스컨디션 수정, asyncio.Lock)을 새 베이스
  (carrot-ryu `1bd10a7c`) 위에 재적용 -- carrot-ryu-v1(`9ccf1206`)과 실제 `git clone`
  대조로 차이가 정확히 37차 수정 하나임을 확인, 문자열 블록 치환 3곳 anchor 전부 1회
  매치, 결과가 carrot-ryu-v1과 byte-exact 일치(diff/md5), `python3 -m py_compile` 통과
  까지 확인(9절/16절). 최초 반영 스크립트(v3)는 실제 사용자 PC 실행 시 [5/6]
  py_compile 검증 단계에서 진단 출력 없이 실패 -- 리눅스 재현으로 코드/치환 로직
  자체는 문제 없음을 재확정하고, 원인을 핵심 발견 37(54차)과 동일한 Windows
  App Execution Alias 문제로 특정. `Get-PythonCmd`를 "py -3" 최우선 + 실제
  `--version` 실행 결과로 후보를 검증하도록 강화하고 py_compile 출력을 항상
  콘솔에 표시하도록 한 v4로 교체(anchor/치환 로직 자체는 v3와 동일, 변경 없음).
  js/css 소스 변경 없어 번들 재생성/params_keys.h 등록 불필요. 반영 스크립트
  (`82cha_item21_gdrive_folder_lock_v4.ps1`) 전달, 실행 대기. 다음 세션 최우선:
  push 확인(83차에서 완료 확인, 아래 [83차] 항목 참고). Google Drive 파이프라인 이식(항목
  5~10·12·17·18·20·21)이 전부 완료되었으므로, 이어서 항목 22(39차, `797fca2e`) 본편
  착수 -> 항목 23(39cha-fix) -> 항목 26(44차) 순서로 진행. 실차 검증: 미실시(git
  pull 금지 상태 유지 중).
- **[83차, devnotes 정정만 · 코드 변경 없음]** 세션 시작 체크포인트(`git ls-remote`)에서 carrot-ryu
  HEAD가 이미 `435d0b58e6fc3a1012d659f379770fb48654e01f`로, HANDOFF.md(82차)에 기록된 base
  (`1bd10a7c`, "push 대기")와 다름을 발견(4절/16절). GitHub compare `.diff` 엔드포인트
  (api.github.com rate limit 회피)로 `1bd10a7c`..`435d0b58` 구간을 조회한 결과 정확히 1개
  커밋("82cha: item21 (37cha) reapply - gdrive_upload.py _ensure_folder() TOCTOU...")이며,
  변경 파일이 gdrive_upload.py 1개뿐이고 diff 내용(import asyncio 추가 + 모듈 레벨
  _folder_lock 추가 + _ensure_folder() 전체를 락으로 감싸는 것)이 82차 HANDOFF.md에 기록된
  항목 21(37차) 재적용 내용과 정확히 일치함을 확인. 결론: 사용자가 이미
  `82cha_item21_gdrive_folder_lock_v4.ps1`을 실행해 push까지 완료했고, HANDOFF.md/
  CURRENT_STATUS.md의 "push 대기" 표기만 뒤처져 있었던 것(핵심 발견 27/38과 동일 패턴).
  이 push로 Google Drive 파이프라인(항목 5~10·12·17·18·20·21) 이식이 전부 완료됨. 코드
  변경 없이 이 파일과 HANDOFF.md의 표기만 정정. 다음 세션 최우선: 항목 22(39차, `797fca2e`,
  화면녹화 탭 사진 업로드 UI 신규 구현) 본편 착수.
- **[84차]** 사용자 제보(실기기 스크린샷, 2026-09-17)로 경로안내 박스의 "교통정보 수집지점"(sdi_descr) 배지 문구가 초록 배지 밖으로 밀려 보이는 버그 확인. FINDINGS.md 38차/HANDOFF.md 40차 기록을 재검토한 결과 이 sdi_descr 분기는 실차로 한 번도 제대로 검증된 적이 없었음(그동안은 도로명 분기만 캡처됨)을 확인. 근본 원인은 `text_draw.py`의 `get_text_draw_pos()`에 `align="left_bottom"` 분기 자체가 없어 `_draw_text_left_bottom()`(제목/신호과속·교통정보 배지/도로명 3곳에서 사용)이 `left_top`처럼 동작하는 것으로 확정(carrot-ryu/v1 양쪽에 동일하게 존재). 사용자 요청으로 공용 함수는 건드리지 않고 `_draw_turn_info_hud()`의 `if info["sdi_descr"]:` 블록만 범위를 한정해 배지 안에 세로 중앙 정렬되도록 수정 + 글자크기 90% 축소(제목/도로명은 동일 버그가 남아있는 채로 의도적으로 미수정). 반영 스크립트(`84cha_item_sdi_badge_fix.ps1`) 작성/전달, 실행 대기. 실차 검증: 미실시(이 코드 경로 자체가 프로젝트 역사상 처음 검증 대상). **[84차 계속2]** 사용자가 v2 스크립트 실행 후 push 완료(carrot-ryu `a461c7e`/carrot-ryu-note `b174937`) -- 재확인 과정에서 4개 파일에 의도치 않은 BOM 삽입(핵심 발견 41) + WIP.md "# WIP" 헤더 소실(핵심 발견 42)을 발견해 즉시 보정 커밋으로 수정, 지침 문서 9절에 재발방지 체크리스트를 실제로 반영함.

- **[85차]** 세션 시작 체크포인트(`git ls-remote`)로 carrot-ryu HEAD가 이미 `132d85b`(84차2 BOM 제거 커밋)로 push 완료돼 있음을 확인 -- HANDOFF.md(84차2)에는 이 push가 "미완료/사용자 실행 대기"로 남아있던 괴리(16절/핵심 발견 27·38과 동일 패턴)를 발견, 이 파일들을 84차2 push-확인 기준으로 바로잡는다. 이어서 사용자 요청으로 항목 22(39차, `797fca2e`, 화면녹화 탭 사진 업로드 UI + content_shift_y)·항목 23(40차-fix, `bdde8326`, screenshots.js formatRelativeEpoch import 누락)·항목 26(44차, `e2f35619`, screenshots.js formatLogBytes import 누락)을 현재 베이스(`132d85b`) 위에서 처음부터 독립 재검증했다: 원본 커밋 patch 3개를 `github.com/.../commit/<sha>.patch`로 직접 조회 -> 12개 파일 중 11개는 `git apply` 1회 매치로 정상 적용, `routes.py` 1개만 파일 끝 컨텍스트 줄 차이로 수동 삽입(코드 내용 자체는 patch와 동일) -> `bdde8326`/`e2f35619`의 screenshots.js import 수정 순서대로 이어 적용 -> `npm install && node build.mjs`로 생성 번들 3종(`js/generated/logs.js`, `css/generated/logs.css`, `generated/asset-manifest.json`) 재생성 -> `py_compile`(routes.py/hud_renderer.py) 통과, `node --check` 통과, `npm test` 746/747 통과(유일 실패는 기존에도 알려진 무관한 `ar_projection_golden` 환경 이슈, 69차 이전부터 반복 확인된 사항). 최종 변경 12개 파일(routes.py/screenshots.js/runtime.js/style.css/생성번들 3종/index.html/en·ko·zh.js/hud_renderer.py)의 diff 통계가 직전 세션(84차 계속2, sandbox 검증 중 세션 종료로 미전달)이 남긴 기록과 완전히 일치함을 확인해 독립 재검증 결과가 이전 세션의 sandbox 결론과 같음을 실증(11절). 반영 스크립트 `85cha_item22_23_26_carrot_ryu.ps1`(코드, base64 전체교체 7개 파일 + Replace-Block 5곳)을 9절 자가검증 체크리스트 전항목(BOM/`core.autocrlf`/임시폴더/`Get-PythonCmd`+EOF공급/전체재작성 WriteAllText 무BOM/anchor 결과 재확인) 통과 후 전달, 신선한 별도 clone으로 스크립트 로직 자체도 시뮬레이션 재현해 `verify_clone`(git apply 기반) 결과와 바이트 단위 diff 없음까지 확인(핵심 발견 42 원칙 적용). **[85차, 사용자 실행 결과]** 사용자가 이 스크립트를 실행한 결과 첫 Replace-Block(`content_shift_y-decl`)에서 anchor 0회 매치로 push 전에 안전하게 중단됨(핵심 발견 44). 원인은 63차와 동일한 `.gitattributes` `* text=auto` CRLF 문제이며, 이번 `Invoke-ReplaceBlock`에 9절이 이미 요구하던 CRLF 정규화가 실제로는 빠져 있었던 것으로 확인됐다. `Invoke-ReplaceBlock`에 CRLF->LF 정규화를 추가한 `85cha_item22_23_26_carrot_ryu_v2.ps1`로 교체, 신선한 clone에 대해 12개 Replace-Block 앵커 전부 1회 매치 + `py_compile`/`node --check` 재통과를 재확인했다. **v1(`85cha_item22_23_26_carrot_ryu.ps1`)은 실행하지 말 것 -- v2만 실행.** 실행/push 대기. 실차 검증: 미실시(코드 변경 자체가 아직 push되지 않음, 항목 22/23/26 모두 이 프로젝트 역사상 실차 검증된 적 없는 경로).
- **[88차, devnotes 정정만 · 코드 변경 없음]** 세션 시작 체크포인트(`git ls-remote`)로 carrot-ryu HEAD가 `0923f83`, carrot-ryu-note HEAD가 `50e7f67`임을 확인 -- 87차가 준비했던 반영 스크립트 2개(`87cha_items30_36_carrot_ryu.ps1`/`87cha_devnotes_carrot_ryu_note.ps1`) 모두 사용자가 이미 실행/push까지 완료한 상태였음을 발견(16절, 핵심 발견 27/38과 동일 패턴 -- HANDOFF.md/CURRENT_STATUS.md에는 "실행/push 대기"로 남아있었음). GitHub commit API로 `0923f83`(parent `ba929b5f2`, 86차 베이스와 일치)의 변경 파일 4개(hud_renderer.py/screenshot_button.py/screenshot_capture.py/application.py)가 87차 기록과 정확히 일치함을 확인, `50e7f67`(parent `15cdf6e2e`)이 87차가 준비한 devnotes 3개 파일(CURRENT_STATUS.md/HANDOFF.md/WIP.md) 갱신임을 확인. **이로써 carrot-ryu-v1 "코드 수정 현황" 36개 항목(1~36) 전부가 20절 리셋 이후 새 베이스 위에서 GitHub 반영 확인 완료됨.** 코드 변경 없이 이 파일 최상단 HEAD 줄 + 항목 30~36 일곱 곳의 "실행/push 대기" 표기만 88차 기준으로 정정했다. 실차 검증: 미실시(다음 세션 최우선 -- 36개 항목 전부가 이 시점부터 처음으로 "새 베이스 기준 실차 재검증" 대상이 됨).
- **[91차, devnotes 사후 동기화만 · 코드 변경 없음]** 세션 시작 체크포인트(`git ls-remote`)로 carrot-ryu HEAD가 `260565f`(90차, "reapply carrot-ms b4f751f4 - camera pair sync, curve release confirm window, path_geometry extraction"), carrot-ryu-note HEAD가 `b7013c6`(89차)임을 확인 -- HANDOFF.md(89차)의 코드 base(`0923f83`)와 달라 16절에 따라 조사했고, 90차가 코드 push까지만 마치고 devnotes를 반영하지 못한 채 끊긴 것으로 판단했다(핵심 발견 27/38과 동일 패턴). carrot-ms b4f751f4와 260565f의 패치를 index 줄 제외하고 대조해 15개 파일 660줄이 동일함(carrot_man.py 헝크 헤더 줄번호 1줄만 다름)을 확인했고, 변경 .py 11개 py_compile 통과, 단위 테스트 47개 통과(샌드박스). 89차 검토대상 4건 중 b4f751f4만 반영 완료이며 4d1a3ded/ec95363a/557e6f6a는 미반영·미승인. carrot-ms HEAD는 `e324f67`로 89차 체크포인트 대비 1건 추가(분류 이월, WIP_SYNC.md 91차 참고). 실차 검증: 미실시(36개 항목 + b4f751f4 재적용분 전부).
- **[91차 계속, carrot-ms 4d1a3ded 반영 스크립트 준비 · 실행/push 대기]** carrot-ryu-note `b55388c`(91차 devnotes) push를 GitHub에서 재확인한 뒤, 남은 3건의 처리 순서를 사용자가 위임해 4d1a3ded를 먼저 골랐다. 근거: check_contracts.py `modeld-mirror` 계약이 carrot-ryu 260565f에서 FAIL(90차가 modeld.py를 바꿨는데 upstream_baseline/modeld.py.baseline과 carrot_modeld.py 미러가 그대로)이고 carrot-ms 4d1a3ded 시점에는 PASS. 대상 두 파일(carrot/model_selector/carrot_modeld.py, upstream_baseline/modeld.py.baseline)의 pre-image blob이 carrot-ryu와 동일해 충돌 없이 적용 가능. 코드 반영 스크립트 `91cha2_4d1a3ded_carrot_ryu.ps1`과 이 devnotes 스크립트를 같은 응답에서 전달(새 원칙: 코드 변경 시 devnotes 동시 진행). 코드 push 확인 전이므로 위 carrot-ryu HEAD는 `260565f` 그대로다. WIP_SYNC.md 널바이트 1개 정정 포함. 실차 검증: 미실시.
- **[91차 계속2, carrot-ms 4d1a3ded 반영 완료 확인]** 사용자 실행 로그(`260565f..f1e920d`)를 `git ls-remote`+별도 clone으로 재검증: 부모 `260565f`, 변경 파일 정확히 2개, 결과 blob이 carrot-ms `4d1a3ded`의 post-image와 byte 일치. `check_contracts.py`를 새 HEAD에서 재실행해 `modeld-mirror`가 PASS로 전환됐음을 확인(나머지 FAIL 4건은 tinygrad_repo 부재로 인한 샌드박스 한계, 반영 전후 동일). 89차 검토대상 4건 중 `b4f751f4`/`4d1a3ded` 반영 완료, 남은 `ec95363a`/`557e6f6a`와 `e324f67` 분류는 다음 세션으로. 실차 검증: 미실시.
- **[92차, carrot-ms ec95363a 상세 대조 완료 · 반영 스크립트 준비, 실행/push 대기]** 89차 검토대상 잔여 2건 중 ec95363a("Batch lane dash geometry and separate UI CPU work from render waits", 8개 파일 +185/-39)를 먼저 착수. 대상 파일 중 기존 파일 6개(augmented_road_view.py/model_renderer.py/road_markings.py 수정 + 테스트 3개 수정: test_carrot_model_renderer.py/test_carrot_model_renderer_lane_visibility.py/test_ui_debug_hud_schema.py)의 현재 carrot-ryu(`f1e920d`) blob이 원본 ec95363a 커밋의 pre-image blob과 전부 byte-exact 일치함을 `git hash-object`로 확인, 신규 파일 2개(render_diagnostics.py/test_render_diagnostics.py)는 아직 없음을 확인(충돌 없는 순수 신규 생성). 90차(carrot-ms b4f751f4)가 model_renderer.py를 이미 건드렸으나 ec95363a보다 시간상 먼저이고 현재 blob이 ec95363a pre-image와 정확히 일치해 체인 순서 충돌 없음을 확인(4d1a3ded는 carrot_modeld.py/upstream_baseline만 건드려 무관). `openpilot/common/runtime_diagnostics.py`(RuntimeDiagnostics.record)가 이미 존재하고 render_diagnostics.py와 API가 호환됨을 확인. 별도 blobless/sparse clone에서 `git apply --check`로 8개 파일 전부 충돌 없이 적용됨을 검증, 적용 후 8개 파일 `py_compile` 전부 통과, hud_renderer.py 계열의 구 스크린샷 API(`consume_pending_screenshot_capture`/`capture_onroad_screenshot`) 잔여 참조가 augmented_road_view.py에 없음도 grep으로 재확인(52~54차 재설계와 충돌 없음). pytest 실행은 샌드박스에 `params_pyx` 등 컴파일 의존성이 없어 미실시(11절, 과거 세션들이 Windows/Linux 환경에서 실행하던 것과 동일한 제약). 반영 스크립트(`92cha_item_ec95363a_carrot_ryu.ps1`, 8개 파일 base64 전체교체)를 9절 자가검증 체크리스트(BOM 없음/`core.autocrlf=false`/임시폴더 자동삭제/`Get-PythonCmd`+EOF공급) 통과 후 전달, 실행/push 대기. 실차 검증: 미실시(이 코드 경로 자체가 프로젝트 역사상 처음 검증 대상). 다음: push 확인 후 557e6f6a(precompiled_worker.py 1파일 +3/-1) 착수, 이후 e324f67 필요 여부 판단.
- **[93차, carrot-ms 557e6f6a 상세 대조 완료 · 반영 스크립트 준비, 실행/push 대기 / ec95363a push 확인]** 세션 시작 시 carrot-ryu HEAD가 `9eced40`으로 HANDOFF(92차) base `f1e920d`와 다름을 확인(16절): `9eced40`은 92차 ec95363a 반영 커밋으로, 부모 `f1e920d`, 변경 파일 8개 +185/-39, 8개 결과 blob이 원본 patch post-image와 전부 일치함을 blobless clone으로 재검증했다(ec95363a 반영 완료 확정). 이어 89차 검토대상 마지막 건 557e6f6a("Identify model artifact and input size in worker diagnostics", `openpilot/selfdrive/modeld/precompiled_worker.py` 1파일 +3/-1, `diagnostics.record` context에 format/camera_width/camera_height/input_bytes/model_sha256 추가)에 착수: 현재 carrot-ryu blob `1c2e2a3b5e`가 원본 pre-image와 byte-exact 일치, 신규 참조 값이 전부 정의·존재함(`manifest['format']`은 `validate_catalog`가 강제하는 값이며 installed.json이 그 dict를 그대로 저장) 확인, `test_precompiled_runner.py`의 worker 직접 실행 테스트는 checksum 실패 경로라 영향 없음(코드 읽기, 미실행), 별도 sparse clone에서 `git apply --check`/적용/`py_compile` 통과, 결과 blob `d04b52ce89`가 원본 post-image와 일치. 반영 스크립트(`93cha_item_557e6f6a_carrot_ryu.ps1`, base64 전체교체+pre-image blob 가드+post 검증)를 9절 체크리스트 통과 후 전달, 실행/push 대기. 샌드박스에 PowerShell이 없어 스크립트 구문 실행은 미검증. pytest 미실시, 실차 검증: 미실시. 다음: push 확인 후 e324f67 필요 여부 판단(DH 2015가 정지 lead 인계 경로를 타는지).
- **[93차 계속, carrot-ms 557e6f6a 반영 완료 확인 · e324f67 제외 확정 · 89차 검토대상 4건 종결]** 사용자가 두 스크립트 실행 완료를 알려와 로그 없이 GitHub에서 직접 재확인: carrot-ryu `25f21d4`(부모 `9eced40`, 변경 파일 1개 +3/-1, 결과 blob `d04b52ce89e5`가 원본 post-image와 일치), carrot-ryu-note `bd69ab0`(변경 4개 파일 sha256이 사전 계산값과 전부 일치). 이어 e324f67("Require clear persistent vision for distinct stopped-lead handoff", primary.py + 테스트 2파일 +112/-2)을 분석: 새 분기는 붙잡은 정지 점과 더 가까운 점, 서로 다른 레이더 점 두 개가 있어야 하는데, 이 차량 설정(사용자 제공 params_backup-1.json: HyundaiCameraSCC=1, EnableRadarTracks=0, EnableCornerRadar=0)에서는 `radar_interface`가 트랙/코너 파서를 쓰지 않고 SCC 고정 ID 점 하나만 발행하므로 발동할 수 없다. 사용자 승인으로 제외 확정(코드 변경 없음, 재검토 트리거: EnableRadarTracks>0 또는 EnableCornerRadar 활성화). 분석 중 "radarUnavailable=True" 추론은 HyundaiCameraSCC=1(CAMERA_SCC 플래그로 radarUnavailable=False)이라 정정했으나 결론은 유지. 61차 리셋 이후 carrot-ms 16건 전부 분류 종결(반영 4건 + 제외 12건). 한계: params 백업과 현재 장치 값의 일치는 미확인, 정적 분석. pytest 미실시, 실차 검증: 미실시. 다음: 다음 세션 시작 시 carrot-ms 신규 커밋 확인 후, 없으면 36개 항목 + 재적용분 실차 검증 준비.
- **[94차, devnotes 정리만 · 코드 변경 없음]** 직전 세션(93차 계속) HANDOFF 미완료 3번(WIP.md 맨 끝 mojibake 처리 여부, `# WIP` 헤더 중복 정리 여부)을 처리. `# WIP` 헤더가 파일에 2회(1번째 줄 정상 제목, 961번째 줄 44차 항목 앞 스트레이 중복) 등장함을 확인해 중복 줄 1개만 제거(실제 회차 내용 변경 없음). mojibake 구간(11차~1차, 11개 회차, 구 라인 1612~1814)은 역변환(문자열을 CP949로 재인코딩 후 UTF-8로 재디코딩)을 시도한 결과 160곳 이상에서 인코딩 자체가 실패(문자가 이미 제어문자 `\x80` 등으로 치환된 상태)함을 확인, 단일 인코딩 사고가 아니라 여러 단계가 겹친 손상이며 byte-exact 복구가 불가능함을 확정(추측 아님, 실제 역변환 시도로 확인). 사용자에게 (a)그대로 둠 (b)안내 문구만 추가(원문 보존) (c)삭제 3가지를 제시했고 사용자가 위임 -- 7절 "기존 기록 임의 삭제 금지" 원칙에 따라 (c)는 배제하고 (b) 채택: 11차 헤더 직전에 손상 사실과 대체 참고처(`PROJECT_INSTRUCTIONS_carrot-ryu.md`의 핵심 발견 1~8, `CURRENT_STATUS.md`)를 안내하는 문단만 신규 추가, 원문(mojibake 텍스트) 자체는 한 글자도 수정/삭제하지 않음. 코드 변경 없음, WIP.md만 전체교체(9절 "이번만 예외" -- 편집 지점이 파일 중간 두 곳이라 87차와 동일하게 전체교체 적용). 실행/push 대기. 실차 검증: 해당 없음.
- **[95차]** carrot-ms 신규 커밋 확인(2절): git ls-remote로 happymaj11r/openpilot HEAD가 여전히 e324f67임을 재확인(93차 체크포인트와 동일, 신규 없음). 이어 20절 7항 절차대로 사용자가 디바이스 현재 상태(carrot-ryu-v1, commit c81aef07)를 확인, 도구 탭 "브랜치 변경"(브랜치 목록에서 carrot-ryu 재선택 -> 자동 재체크아웃/재빌드)으로 origin/carrot-ryu 전환을 승인·실행함. 61차 force reset으로 히스토리가 갈라져 있어 일반 git pull(fast-forward)로는 애초에 받아질 수 없는 상태였고, "브랜치 변경"(재체크아웃) 방식이 정확히 이 문제를 우회한다는 점을 사용자가 지적/확인. 사용자가 제공한 전후 tmux 로그 2건(16:30:51/16:38:30)의 metadata.json+tmux.log 부팅 로그로 실제 배포를 독립 재확인: 전(tmux1) git_branch: carrot-ryu-v1, git_commit: c81aef07... -> 후(tmux2) git_branch: carrot-ryu, git_commit: 25f21d406d23bfb79ad45a67890cc39e3ad9e67b(93차 최종 HEAD와 일치), 온로드 프로세스 부팅 로그 "Carrot GitBranch = carrot-ryu, '...2026-09-19 14:54:13 +0900'"로 재확인(11절: 실제 부팅 로그 근거, 추정 아님).
- **[95차 계속, 최초 실차 UI 검증]** 사용자가 제공한 온로드 스크린샷 1장(2026-09-19 16:49:06, 스크린샷 버튼으로 직접 촬영, 정차/주차장 상태)으로 실차 검증(12절): (1) 항목 30~36(screenshot capture 체인, render-texture 재설계) 전부 정상 확인 -- 이미지 실측 960x480(항목33 480p 세로기준 다운스케일 일치, PIL로 직접 측정), PNG 포맷(항목32), 상하반전 없음(항목36), border HUD 요소(차량명 HYUNDAI_GENESIS(CAMERA SCC)/시계 16:49:06 09-19(토)/LD·LT·SR/laneless/carrot-ryu 브랜치명/IP 10.105.201.171) 전부 캡처에 포함(항목34·35 캡처 타이밍 재설계로 해소된 문제) -- 이 체인 전체의 프로젝트 역사상 첫 실차 확인. (2) 항목 13~19(우측하단 경로안내 박스) 정상 확인 -- "교차로" 제목/회전아이콘/123m/route=114.0/도착 409.9km/284.8분(21:33)/과속방지턱 배지가 박스 안에 겹침·overflow 없이 표시됨(27차 이후 이월되던 레이아웃 항목들의 재적용본 첫 확인). (3) CPU/MEM/VOLT 패널, 원형 녹화 버튼(항목25) 존재 확인(단, 깜빡임 동작(항목28)은 정지 이미지라 판단 불가). 미확인/이월: 항목1·2(종방향 안전장치)와 carrot-ms 4건(b4f751f4 등, 실제 주행 중 동작), Drive 업로드 파이프라인(5~10·12·17·18·20·21), 화면녹화 탭 사진 업로드 UI(22·23·26) -- 이번 스크린샷은 정차 상태 1장뿐이라 종방향 제어/실주행 관련 검증은 아직 없음. 사용자가 추가로 대용량 route 로그(qcamera.ts+rlog.zst, route 00000436--2edd613f1e--8)를 업로드했으나 openpilot cereal 스키마 파싱 환경이 샌드박스에 없어 이번 세션에서는 심층 분석 보류(사용자에게 원하는 확인 항목 문의 예정).
- **[96차, 지침 문서 갱신 · 코드 변경 없음]** 세션 시작 체크포인트로 지침 문서(v2, 커밋 `ac45f91`)/HANDOFF.md/CURRENT_STATUS.md를 확인하고 carrot-ryu `25f21d4`(변경 없음)/carrot-ms `e324f67`(신규 커밋 없음, 2절)을 재확인했다. 95차 HANDOFF의 note base(`5e67047`)/"push 대기" 표기가 실제 HEAD(`ac45f91`, 그 3개 파일이 이미 반영됨)와 시차가 있었음을 클론으로 확인(16절, 반영 누락 아님). 19절 절차(변경 이유->변경안->사용자 승인->스크립트)로 PROJECT_INSTRUCTIONS_carrot-ryu.md 9절 체크리스트에 7번(전달할 .ps1에서 앵커/치환 문자열을 추출해 SHA 고정 원본에 시뮬레이션)을 추가 -- carrot-ryu-note `913b6f1`(부모 `ac45f91`, 변경 파일 1개 +4/-0). 사용자의 "완료" 보고 후 SHA 고정 raw가 사전 계산한 기대 결과(SHA-256 `83bf4294...`)와 바이트 동일함을 GitHub에서 직접 재확인(16절). 지침 문서는 v2 유지, 9절 본문에 한 항목이 추가됐을 뿐이다. 전달 스크립트 검증에 샌드박스 pwsh 7.6.6(GitHub 릴리스, Linux)을 처음 사용했다(구문 파싱 + 로컬 bare 저장소 전체 실행 + 음성 테스트 2건) -- 사용자 PC의 Windows PowerShell 5.1 검증은 아니다. 코드/실차 검증 대상 아님(12절 무관).

- **[97~114차, 종방향 리드 감속 게이팅 + 라우트 커브 감속 튜닝(catch-up, 122차 HANDOFF 이월분)]** 이 구간은 96차(지침 문서 갱신) 이후 122차가 이 파일 갱신을 재개하기 전까지 방치돼 있던 18개 세션이다. 아래는 124차에서 WIP.md 97~114차 원문을 순서대로 다시 읽어 구성한 요약이며, 각 항목의 세부 수치/표/재현 방법은 WIP.md 해당 회차 원문이 원본이다(이 요약은 축약이므로 상충 시 WIP.md를 따른다).
  - **97~99차(분석->설계->구현)**: 선행차 감속 과민 반응(#5/#8/#22 등 26건 이벤트) 로그 분석(97차, toolkit `lead_decel/` 5개 신규 등록) -> MPC 복제본(casadi/IPOPT, acados 아님) what-if로 게이팅 후보 비교, B안(G2T: 투사 감쇠만, 시간차 1.5~2.2s / TTC 6~12s) 채택(98차, 사용자 승인, 코드 변경 없음) -> `long_mpc.py`에 `GATE_H_LO/HI`/`GATE_T_LO/HI`/`_gate_raw()`/`process_lead(self, lead, lead_index)` 구현(99차, 반영 스크립트 실행/push 대기). 전 구간 실차 검증: 미실시.
  - **100차**: 99차 반영(carrot-ryu `f87083e`) push 확인. 반영 후 기존 테스트 2개 파일에서 39개 회귀 실패 발견(하네스가 새 `process_lead` 시그니처/`GATE_*` 상수를 몰라서) -- 프로덕션 코드는 무변경, 테스트 파일 2개만 최소 수정해 95개 전부 통과 확인. 반영 스크립트 실행/push 대기.
  - **101차**: 100차 반영(`f87083e`) push 확인(16절, HANDOFF 표기 정정). 스트레스 재검증(-10/-20m) + 전체 주행(leadOne 10,770표본) 게이트 노출 통계: g<1 비율 98.1%이지만 투사가 실제로 바뀌는 표본(|dV|>0.5m/s)은 5.9%뿐임을 확인해 "상시 개입"이라는 표면적 해석을 정정. leadTwo 활성 0건 발견(원인은 102차로 이월). 코드 변경 없음.
  - **102차**: leadTwo 0건의 원인 확정 -- 이 차량(제네시스 DH, `HyundaiCameraSCC` 등)의 레이더 구성이 SCC 단일 타깃 포인트만 주는 구조라 leadTwo가 구조적으로 나오지 않을 가능성이 높음(로그+코드 대조). leadTwo 게이트 검증 우선순위를 낮춤. 코드 변경 없음.
  - **103차**: `margin_ratio`(gap 여유 비율) 기반 게이트 후보 스윕 진행 중 토큰 한도로 중단. 넓은 밴드(1.0/1.2)는 평상시 무반응(g==0 90%) 달성에는 좋았으나, 게이트를 만든 근거 사례(idx5/idx8)에서 base 대비 개선이 없거나 오히려 소폭 악화 -- margin_ratio 단독은 TTC가 하던 "조기 감지" 역할을 대신하지 못한다는 잠정 결론(하이브리드 필요 시사). idx14~25 스윕은 미완료. 코드 변경 없음.
  - **104차**: WIP.md에 기록이 없음(105차가 "104차 세션이 있었을 수 있으나 devnotes 미반영으로 추정"이라고 언급, 확인되지 않음 -- 16절 사례로 기록만 하고 105차로 번호를 이어감).
  - **105차**: 사용자 결정("검증은 나중에, 우선 코드부터")으로 재생 검증을 생략하고 게이트를 margin_ratio+TTC 하이브리드(`GATE_M_LO/HI`=1.0/1.2, 기존 TTC 성분과 `max()` 결합)로 교체하는 코드 반영(`long_mpc.py`, 신규 테스트 `test_lead_gate_margin.py` 8개). 커밋은 `67b0aa9`로 이후 회차(106~110차)에서 "105차 코드"로 지칭된다. 위험 명시: 103차 근거사례(idx8)에서 margin 단독은 기존 B안보다 완화 효과가 작았고 이 하이브리드 조합 자체는 재생 검증된 적 없음.
  - **106차(+계속)**: 105차(`67b0aa9`) push 확인. 실차 로그(swaglog `lead_gate` 291건)와 base/B/M105(105차 게이트) 폐루프 재생 비교(`gating_eval_105.py` 신규 등록) -- 해석 정정: M105는 idx8/9(비위험, 시간차 2.2s 이상)에서 B안만큼 완화하지 못해 103차의 우려가 실제로 재현됨(원인: margin 계산에 리드 정지환산거리가 들어가 리드가 느려지면 gap이 커도 m이 내려감). 106차 계속에서 margin 임계값 하향(0.8/1.0 등) 스윕 -- M0.8/1.0이 idx8/9에서 B 수준 완화를 내지만 근접 극단 스트레스(-20m)에서는 게이트가 덜 열리는 방향(주의 필요). 사용자 결정 대기, 코드 변경 없음.
  - **107차**: 105차 코드(`67b0aa9`) 그대로 주행한 실차 로그(동일 route seg 21~25) 재확인 -- 자차 급감속 1건(idx8, aEgo 0.5s 중앙값 -1.59, accelCmd -1.68) 실측: 시간차 2.2s 이상인 비위험 상황인데도 게이트 g가 0.96까지 열려 강하게 제동. 복제본-실차 정합성 16건 평균 |오차| 0.143 m/s². 미재생이던 10건 후보(base/B/M105/M0.9-1.1/M0.8-1.0) 비교. toolkit 4개(`ego_extract.py` 등) 신규 등록. 코드 변경 없음.
  - **108차(+계속·계속2)**: 신규 로그(seg 113/146)에서 자차 급정거 실측 -- accelCmd가 하한 `ACCEL_MIN`(-4.0)까지 도달(seg113), 시간차 2s/TTC 9s 이상인데도 극심 제동. 복제본이 강한 리드 감속(aLeadK -6.7)에서는 실차보다 훨씬 약하게 나와(정합성 깨짐) M0.8/1.0 재생 완화폭이 seg113 약 0.43·seg146 약 0.33 m/s²로 작게 나옴(108차). 계속 세션에서 ACCEL_MIN/실제 Params/플래너 x0·게이트를 실제 값으로 재구성한 결과 단발 해는 실차 궤적과 RMSE 0.02~0.09로 일치하지만 폐루프는 여전히 실차보다 약함(seg113 -2.16~-2.59 vs 실차 -4.0) -- 원인 가설: a_change_cost로 인한 첫 스텝 편향의 누적(acados 실물 부재로 미확인). 계속2에서 게이트 완화 대체 후보 2건 검증: TF_FLOOR(tFollow 하한)는 하드 안전거리 제약 자체를 낮춰 stress에서 gap0=60m 케이스가 생존->충돌로 전환(가장 위험), 출력단 저크 제한(J_MAX)은 이 이벤트의 실제 저크가 이미 작아 무효. toolkit 6개 신규 등록(`ego_extract2.py`/`openloop108.py`/`closedloop108.py`/`closedloop_jlim.py` 등). 전 구간 코드 변경 없음.
  - **109차**: 필요 감속 기반 명령 상한("need-cap", `d_target=HFLOOR*vLead` 구조) 후보를 새로 설계해 검증한 결과, 리드가 급감속하면 vLead가 줄어 d_target도 같이 줄고 avail(gap-d_target)이 커져 오히려 캡이 풀리는 **역방향 피드백 결함**을 확정 -- 이 형태의 need-cap은 폐기. toolkit `closedloop_ncap.py` 등록. 코드 변경 없음. 다음 최우선으로 "GATE_M_LO/HI를 0.8/1.0으로 바꿀지" 결정이 이월됨.
  - **110차**: GATE_M_LO/HI를 1.0/1.2 -> 0.8/1.0으로 낮추는 코드 반영(`long_mpc.py` + `test_lead_gate_margin.py` 4개를 상수 무관 형태로 수정). 이전(저장소 미기록) 채팅에서 재구성된 event/stress 수치를 이번 세션이 그대로 인용(재실행 없음) -- 0.8/1.0은 M105 대비 완화(seg113 +0.43, seg146 +0.33 m/s²)되고 stress 비용은 작음(경계 약 1m)이나, 완화폭이 실차 -4.0의 약 10%뿐이고 복제본이 실차보다 약해 실제 효과는 불확실하다는 한계가 명시됨. 반영 스크립트 실행/push 대기, 실차 검증 미실시.
  - **111차**: 110차 반영(`a430d11`) 재검증(격리 pytest 8 passed, BOM 없음 확인). carrot-ms 2절 정기 점검(`e324f67`->`a23a77b`, 신규 21건) 수행 -- 전부 사용자 승인 하에 반영 보류 확정(블루투스 리모컨 관련 14건은 해당 리모컨 미보유, World Model 실험 기록 2건은 문서만이라 반영할 코드 없음, Hyundai CAN FD 전용 리드 표시 보정 1건은 이 차량이 CAN FD가 아님, eGPU 이미지 검증 4건은 eGPU 미보유). 코드 변경 없음.
  - **112차**: 사용자 제보("라우트 감속이 130km/h에서 정체하다 뒤늦게 급감속됨")를 실주행 rlog(seg 155)로 분석 -- `carrot_navi_route()`의 역산(backward integration) 로직을 Python으로 재현한 결과 route 목표속도 계산이 **v_ego를 입력으로 쓰지 않는 구조적 문제**를 확인(도로 형상+고정 상수만으로 정해지는 순수 물리적 상한선). 코드 변경 없음, FINDINGS.md 기록.
  - **113차(+계속)**: 112차 진단을 재업로드 로그로 정정 -- route가 130에서 멈춘 것은 v_ego 미반영이 아니라 원시값 96.3에 기기 배율 1.35가 곱해진 결과이고, 130->97 급락은 route가 아니라 vturn(비전 커브 인식) 전환이었음. 분기(3/4)·톨게이트(6) 안내 지점 200~300m 이내에서만 route 반영비율(MapTurnSpeedFactor)을 완화하는 `map_turn_speed_factor()` 함수 + 4개 상수(`MAP_TURN_GUIDE_FACTOR=1.05` 등)를 `carrot_serv.py`에 추가(반영 스크립트 실행/push 대기, 113차). 계속 세션에서 반영 확인(`c7b5a010`) + 사용자가 체감했던 46~50초 급제동은 시스템이 아니라 **운전자 브레이크**(selfdriveState disabled)로 확정(44.8~46.0초는 시스템이 vturn으로 감속 중이었음). `route_extract.py` toolkit 신규 등록.
  - **114차**: 113차 기록의 근거(같은 구간에서 배율 1.0으로 낮추면 목표 약 96.3, vEgo보다 10~13km/h 낮음)를 사용자가 채택해 `MAP_TURN_GUIDE_FACTOR`를 1.05 -> 1.00으로 한 줄 변경(`carrot_serv.py`). 함수/다른 상수/Params 키는 변경 없음. 반영 스크립트 실행/push 대기, 실차 검증 미실시. 이월 항목: 체감 급감속 구간이 46~50초(운전자 제동, 113차계속에서 확정)인지 44.2~46초(시스템)인지 재확인, 다른 분기/톨게이트 로그로 원시값 대 vturn 비교, 110차 GATE_M 0.8/1.0 실차 관찰.
  - **catch-up 시점(124차) 현재 GitHub 상태와의 관계**: 97~114차는 전부 `carrot-ryu` `2efdd2e2`(121차, dead code 배치B) 이전 커밋 체인(`67b0aa9`~`c7b5a010`~그 이후) 위에서 진행됐고, 115차부터는 별도로 dead-code 정리(1~4차 배치)가 이어졌다(WIP.md 115차 이후 및 이 파일 122차 참고). 즉 97~114차의 종방향 게이팅/라우트 커브 변경들은 현재 HEAD(`a0f4c5a5f`)에 **누적 반영되어 있으나, 이 구간 전체(97~114차 코드 변경분)가 실차에서 개별 검증된 적은 없다** -- 110차 GATE_M 0.8/1.0과 114차 MAP_TURN_GUIDE_FACTOR 1.00은 특히 실차 미검증 상태로 남아있다(다음 세션 우선 후보).

- **[122차, devnotes 동기화 · 코드 변경 없음]** 이 파일이 96차 이후 갱신되지 않고 있었음을 발견(16절) -- 97~121차 사이 실제 진행된 작업(115~121차 dead code cleanup 6개 커밋: 115cha 데드코드 배치1/116cha 카메라 SOF 페어링 skew tolerance 10ms->20ms(carrot-ms 4bb4b510 cherry-pick)/117cha VW MEB(ID.4/ID.5) 데드코드 제거/118cha 레거시 web-upload 경로 제거/120cha 데드코드 배치A(29개 고아 def)/121cha 데드코드 배치B(blinker_manager.py 통째+고아 def 6개) 등, 상세는 WIP.md 115~121차 참고)이 이 파일에는 반영되지 않은 채 방치돼 있었다. 97~114차 구간의 상세 내용은 이번 세션에서 개별 조회하지 않아 재구성하지 않았고(11절: 추측 금지), 갭 존재 자체와 최신 확인 가능한 사실만 우선 기록한다. 이어서 사용자가 디바이스 도구 탭 git pull 로그(`fa75aeab7`->`2efdd2e2`, 6개 커밋 fast-forward, 35개 파일 +71/-1486)와 함께 "실차 검증 이상없이 작동"을 확인해와, 115~121차 6개 커밋의 실차 배포+주행 확인을 사용자 보고 기준으로 기록한다(12절: 총괄 수준 확인이며 개별 기능 단위 재검증은 아님). 코드 변경 없음. 다음 세션 최우선: DEAD_CODE_REVIEW C그룹(cluster 계열) 착수, CURRENT_STATUS.md 97~114차 구간 catch-up.

- **[123차, C그룹 삭제 스크립트 준비 · 실행/push 대기]** 119차 승인된 A->B->C 순서의 마지막 단계인 DEAD_CODE_REVIEW C그룹(cluster 계열, 약 300줄) 착수 전 11절(codeload tarball 재확인, 대상 커밋 `2efdd2e2`)을 수행: `cluster_renderer.py`/`cluster_scene.py`/`main.py`의 대상 함수 18개가 여전히 정의 1곳 + (그룹 내부 상호호출 제외) 외부 참조 0곳임을 저장소 전체 grep으로 재확인하고, `cluster_scene.py`의 `corner_radar_common_lateral_speed_mps` 삭제로 함께 고아가 되는 `from statistics import median` import도 확인했다(119차 예고분). AST로 함수 경계(데코레이터 포함 시작줄/끝줄)를 정확히 산출해 3개 파일에서 삭제(cluster_renderer.py -109/cluster_scene.py -194/main.py -24, 합계 -327줄, 최상위 함수는 앞뒤 2줄·메서드는 1줄 공백 규칙 유지 확인), py_compile 3개 통과·pyflakes 경고 삭제 전후 완전 동일(무관한 기존 경고 1건만 잔존, 줄 번호만 이동)까지 확인. 독립 clone에서 스크립트 로직(pre-image blob hash 가드 -> base64 파일쓰기 -> post-image blob hash+BOM 확인 -> py_compile -> commit) 전체를 처음부터 재현해 commit diff가 예상과 정확히 일치함을 확인(9절/16절 -- Linux 샌드박스 재현이며 Windows PowerShell 5.1 실제 실행은 아님). 코드 반영 스크립트(`123cha_item_c_group_dead_code_carrot_ryu.ps1`)를 9절 "전달 전 필수 자가검증 체크리스트" 통과 후 작성/전달, 실행/push 대기. 이로써 119차 A/B/C 3개 그룹 전부 스크립트가 준비됨(A·B는 이미 push 완료, C는 이번 세션 스크립트가 마지막). 실차 검증: 미실시. 상세: DEAD_CODE_REVIEW.md 123차, HANDOFF.md 123차 참고.

- **[123차 계속, C그룹 삭제 반영 확인 · 119차 A/B/C 4차 배치 종결 · devnotes 정리 · 지침 9절 8·9번 추가 -- 스크립트 준비, 실행/push 대기]** 사용자가 v2 스크립트 2개 실행 완료를 알려와 로그 없이 GitHub에서 직접 재확인했다(16절): carrot-ryu `a0f4c5a5`(부모 `2efdd2e2`, 3개 파일 +0/-327, 결과 blob 3개가 스크립트 `Post` 값과 일치, 삭제한 18개 이름 HEAD 전체 잔여 참조 0건), carrot-ryu-note `24bab81e`(부모 `4853319`, 4개 파일 blob 4개 일치). 사용자 첫 실행(v1)은 clone 단계 schannel early EOF로 push 없이 중단됐고(임시 폴더 정리, 변경 없음) v2(`--depth 1` + 최대 3회 재시도)로 성공했다. devnotes v1은 4057행 후행 쉼표 파싱 오류가 있어(pwsh 파서로 실행 전 발견) v2에서 제거하고 본문 "12개"를 실제 삭제 수 18개로 정정했다. 이로써 119차 A/B/C 4차 배치가 전부 push 완료됐다(120차 A `b98620e8`, 121차 B `2efdd2e2`, 123차 C `a0f4c5a5`). 지침 9절 자가검증 체크리스트에 8번(전달 전 pwsh 구문 검증)·9번(로컬 bare 저장소 일반/CRLF 두 모드 실행)을 19절 절차(사용자 승인)로 추가했다 -- 이 스크립트의 2번째 커밋. 실차 검증: C그룹 미실시(115~121차는 122차 기록 참고). 이 파일의 97~121차 구간 catch-up은 여전히 미완료. 상세: WIP.md 123차 계속, HANDOFF.md 참고.

- **[125차]** pytest를 실제 CI 조건(conftest.py 포함)으로 최초 실행. acados OCP 솔버 코드생성/컴파일(`long_mpc.py`)과 `msgq.ipc_pyx` 컴파일까지 전부 해결해, 목표였던 105~110차 margin_ratio 게이트(`test_lead_gate_margin.py`) + 113~114차 route 커브 감속(`test_map_turn_guide_factor.py`) 23/23 전부 통과 확인(pytest-cpp/randomly/xdist/asyncio 로드된 실제 `pyproject.toml` 조건). 범위를 넓힌 `controls/tests/`+`carrot/tests/` 전체 실행(1928 passed/59 failed/85 errors)에서 실패 대부분은 이 샌드박스의 구조적 한계(`pyray` 미설치, OpenCV/ONNX 버전 불일치, 일부 opendbc 차량 DBC 미생성)로 확인됐으나, `test_latcontrol.py::test_saturation`이 `LatControlPID/Torque/Angle`을 인자 3개(`CP, CI, DT_CTRL`)로 호출하는데 실제 생성자는 전부 `(CP, CI)`만 받아 `TypeError`가 나는 것을 코드 대조로 확정(원인/도입 시점은 미조사, 다음 세션 이월). 재현 절차를 `devnotes/toolkit/pytest_ci_setup.sh`로 등록, 완전 재초기화된 컨테이너에서 그 스크립트 하나로 동일 결과가 재현됨을 확인. 상세: WIP.md 125차.

## 코드 수정 현황 (실차 재검증 전부 미실시)

> **[62차, 20절 리셋 이후 상태 안내]** 아래 목록은 61차 리셋 시점 기준 "이식 체크리스트"다.
> carrot-ryu가 carrot-ms 현재 베이스(706efb47)로 통째로 교체되면서, 아래 각 항목은 리셋 시점
> 기준 전부 carrot-ryu에 반영되어 있지 않다(carrot-ryu-v1에만 과거 상태로 보존). 각 항목이
> 새 베이스 위에 실제로 재적용될 때마다 그 세션에서 해당 줄을 "재반영 완료(commit ...)"로
> 개별 갱신할 것 -- 아래 "GitHub 반영됨" 표기는 61차 리셋 이전 carrot-ryu 기준 과거 기록이다.

1. route 감속 오검출 근본수정(9차, 2dbe492) -- GitHub 반영됨
2. RES/+ 인게이지 속도 안전장치(10차, e1e587b) -- GitHub 반영됨
3. 온로드 시계 초단위 표시 + 스크린샷 버튼(12차, 684b30d 원본) -- [63차] 새 베이스(706efb47) 위에
   재반영 완료(commit `429f105e`, git ls-remote + commit diff로 확인). 12차 원본 버전 그대로이며,
   25·26~28·30~36번(스크린샷 관련 후속 수정: DPI/타이밍/render-texture 재설계/상하반전 등)은
   아직 미반영. 실차 검증: 미실시(git pull 금지 상태 유지 중).
4. 온로드 시계 좌측 화면 경계 잘림 수정(13차, 2adced8 원본) -- [64차] 새 베이스(429f105e) 위에
   재반영 완료(commit `4e3b44a8`, git ls-remote + commit diff로 확인, 원본과 결과 blob까지
   완전 일치). 실차 검증: 미실시(git pull 금지 상태 유지 중).
5. gdrive_upload.py 신규 추가(15차, 183bef9) -- Drive OAuth device flow + resumable 업로드 백엔드. **[70차]** 새 베이스(2088c546) 위에 byte-exact 재적용 완료, commit `017072dd`로 push(75차에서 git ls-remote+compare API로 재확인). 실차 검증: 미실시.
6. 대시캠 업로드(로그탭 "전송") zip+Drive 전환(16차, dae901c 본편 + cc734e1 hotfix) -- **[71차]** 새 베이스(017072dd) 위에 byte-exact 재적용 완료, commit `4b6c8f84`로 push(75차에서 재확인). 실차 검증: 미실시.
7. send_tmux_web() Drive 업로드 전환(17차, commit 2869149) -- **[72차]** 새 베이스(4b6c8f84) 위에 3-block replace로 재적용 완료, commit `75c7c316`으로 push(75차에서 재확인). 실차 검증: 미실시.
8. dashcam 업로드 연결 테스트 버튼(api_dashcam_upload_test)을 Google Drive 기준으로 전환(18~20차, commit ad055dd4) -- **[73차]** 새 베이스(75c7c316) 위에 byte-exact 재적용 완료(18~20차 원본은 a44f1580+ad055dd4), commit `bc021ed9`로 push(75차에서 재확인). 실차 검증: 미실시.
9. params_keys.h에 CarrotGDriveClientId/Secret/RefreshToken 등록(22차, commit 48c2e081) -- **[74차]** 새 베이스(bc021ed9) 위에 재적용 완료(3개 파라미터 정확히 삽입, SHA 고정 raw 조회로 검증), commit `7a1555ed`로 push(75차에서 재확인). 실차 검증: 미실시.
10. web settings log_upload에 Google Drive 계정 연결 UI 추가(23차, commit 272834b) -- [75차] 새 베이스(7a1555ed) 위에 재적용(base.css/components.js/schema.js 전체교체 hash일치 + en.js/ko.js/zh.js anchor삽입 hash일치 + 생성번들 3종 재생성, node --test 747/747 통과) -- **[76차]** 반영 스크립트(`75cha_item10_web_settings_gdrive.ps1`) 실행/push 완료를 commit `c9a03b5`로 확인(4절/16절). 실기기 입력란 미노출 이슈(26차, 핵심 발견 16)는 리셋 이전 기록이라 재검증 필요(실차 검증: 미실시).
11. 화면녹화 탭 스크린샷(.png) "사진" 스트립 추가(24차, commit a7a912c1) -- [67차] 새 베이스(0d511753) 위에
    재적용 완료, commit `63addc2e`로 push까지 `git ls-remote`로 확인(5절/16절). 같은 커미트에 실수로 같이
    커밋된 반영 스크립트 헬퍼(`apply_item11_67cha.py`)는 [67차-fix]에서 `cleanup_stray_67cha.ps1`로 제거하고
    commit `81754ea3`로 push, 독립 `git clone`으로 파일 부재 + 코드 정상 유지 재확인 완료(16절). 실차 검증: 미실시.
12. LOG_UPLOAD_TARGETS "gdrive" 누락 수정(25차, commit d338afb7) -- **[77차]** 새 베이스(`c9a03b5`) 위에 byte-exact 재적용 완료, commit `27d81a4`로 push(GitHub compare API로 원본 25차 diff와 완전히 동일함을 재확인). 실차 검증: 미실시.
13. 우측하단 경로안내 박스 475x495 확대 + route=숫자 디버그 분리 표시 + 도착정보 2줄 표기(27차, commit 5f5e49d0) -- [68차] 새 베이스(81754ea3) 위에 재적용(anchor 1회 매치, py_compile 통과), 반영 스크립트 실행 대기. 40차 계속 실기기 검증(리셋 이전 기록): 상하 여백 균등 배치 확인됨(스크린샷, 12절 최초 실차 검증) -- 재검증 필요.
14. 경로안내 박스 높이 축소(495→400) + 도착/ETA를 route= 아래 우측끝맞춤으로, 회전아이콘 좌측 배치(28차, commit cc73f629) -- [68차] 항목 13 위에 이어서 재적용(anchor 1회 매치, py_compile 통과), 반영 스크립트 실행 대기
15. 경로안내 박스 제목 위치/도착·ETA 박스경계 끝맞춤/신호과속 배지를 회전아이콘 박스 바로 아래로 이동(29차, commit 67a8e10) -- [68차] 항목 14 위에 이어서 재적용(anchor 1회 매치, py_compile 통과), 반영 스크립트 실행 대기
16. 경로안내 박스 route= 크기/위치 조정, 도착·ETA를 pad 인셋 + route= 아래 상단기준으로 재조정(30차, commit 34bb41bc) -- [68차] 항목 15 위에 이어서 재적용(anchor 1회 매치, py_compile 통과), 반영 스크립트 실행 대기. 항목 22(39차) diff의 hud_renderer.py 부분이 이 상태를 전제로 함을 확인(20절 이식 순서 근거).
17. Google Drive drive.file 스코프+폴더 자동생성 복귀(32차, commit c704371a) -- **[78차]** 새 베이스
    (`27d81a4`) 위에 재적용 완료, commit `c197cd4e627c6f266e6f5529d152d1984a47fcd6`로 push. 독립
    clone으로 결과 파일 blob hash(`e6a5832f`)가 원본 32차 커밋 결과와 완전히 일치함을 확인(byte-exact,
    16절). 35차 실기기 연결 성공 기록은 리셋 이전 상태 기준이라 이번 재적용본은 재검증 필요(실차 검증:
    미실시).
18. ko.js gdrive 클라이언트 유형 안내 문구 수정(33차, commit 789667f7) -- **[79차]** 새 베이스(`c197cd4e`) 위에 재적용 완료, push, GitHub compare API + raw 조회로 byte-exact 확인(새 HEAD `a959576f`). 재적용 순서 9번 완료 -- 다음은 항목 20(순서 10번).
19. 경로안내 박스 도착 텍스트 크기(40->32)/도로명 위치(박스 안쪽, 신호과속과 같은 줄) 수정(34차, 실제 commit 메시지는 "33cha", commit `9fdefb3d`) -- [68차] 항목 16 위에 이어서 재적용(anchor 1회 매치, py_compile 통과), 반영 스크립트 실행 대기. **68차에서 신규 확인**: 항목 22(39차, `797fca2e`)의 hud_renderer.py 부분이 13→14→15→16뿐 아니라 이 19번(comment "eta_size(40)는...")까지 전제로 하는 체인임을 diff 대조로 확정 -- CURRENT_STATUS 목록 순서(13~16, 17~18 Drive, 19)만 보면 안 보이던 의존관계라 다음 세션(또는 이번 세션 이어서) 항목 22 착수 전 필수 선행 항목으로 기록. 38차 실기기 검증(리셋 이전 기록): 도착 텍스트 겹침 해소는 확인됨, 도로명-신호과속 같은 줄 배치는 신호과속 배지 미출현 구간이라 판단 보류 -- 재검증 필요.
20. 화면녹화 탭 업로드 UI 신규 구현 + 당근서버 라벨/햄버거 메뉴 버그 수정(36차, commit 0835b059) -- **[80차/81차]** 새 베이스(`a959576f`) 위에 byte-exact 재적용 완료, commit `1bd10a7c`로 push(81차에서 GitHub `.diff` 엔드포인트로 원본 36차 diff와 파일 목록·커밋 메시지 일치 재확인). 재적용 순서 10번 완료 -- 다음은 항목 21(순서 11번, 마지막). 38차/48차 실기기 검증 기록은 리셋 이전 상태 기준이라 재적용 후 처음부터 재검증 필요.
21. gdrive_upload.py _ensure_folder() Drive 폴더 중복생성 레이스컨디션 수정(37차) -- **[82차/83차]**
    새 베이스(`1bd10a7c`) 위에 재적용 완료, commit `435d0b58`로 push(83차에서 GitHub compare
    `.diff`로 원본 37차 수정(asyncio import + _folder_lock 추가 + _ensure_folder() 전체를
    락으로 감싸는 것) 하나뿐임을 재확인). 재적용 순서 11번(마지막) 완료 -- Google Drive
    파이프라인 이식(항목 5~10·12·17·18·20·21) 전부 완료.
22. 화면녹화 탭 사진 업로드 UI 신규 구현(체크박스/전체선택/다운로드/전송) + 경로안내 박스 상하 여백 통일(content_shift_y)(39차, commit 797fca2e) -- **[69차 정정]** 61차 리셋 이후 미반영 확인됨(전제인 항목 5~10·12·17·18·20·21 전부 없음). content_shift_y 부분은 68차에서 13~16+19 재적용 완료로 anchor 조건 충족, 나머지(routes.py/screenshots.js 등)는 항목 20까지 재적용된 뒤에야 착수 가능. 46차/48차 실기기 검증 기록은 리셋 이전 상태 기준. **[85차]** 현재 베이스(`132d85b`) 위에서 독립 재검증 완료(`py_compile`/`npm test` 746/747 통과), 반영 스크립트 v1 실행 시 anchor 0회 매치로 안전 중단(핵심 발견 44) -> CRLF 정규화 추가한 v2로 교체, 재검증 완료, v2 실행/push 대기. **[86차 확인]** v2 스크립트가 실제로는 이미 실행/push 완료돼 있었음을 `git ls-remote`+GitHub compare `.diff`로 재확인(commit `c74c0ac`, 변경 파일 12개가 예상과 정확히 일치). 항목 22 이식 완료. 실차 검증: 미실시.
23. screenshots.js formatRelativeEpoch import 누락 수정(39cha-fix, 40차, commit bdde8326) -- **[69차 정정]** 61차 리셋 이후 미반영 확인됨(전제인 항목 22의 screenshots.js가 아직 없음). **[85차]** 항목 22와 함께 현재 베이스 위에서 재검증 완료, v2 반영 스크립트 실행/push 대기(핵심 발견 44 참고). **[86차 확인]** commit `c74c0ac`로 push 완료 확인(screenshots.js에 `formatRelativeEpoch` import 실제 존재 재확인). 항목 23 이식 완료. 실차 검증: 미실시.
24. carrotweb 로그탭 새로고침 아이콘 추가(41차, commit da6ad815) -- 이 항목은 index.html/style.css/runtime.js 새로고침 버튼 자체로, Drive 파이프라인과 무관. **[69차 확인]** hud_renderer.py 계열과 별개 서브시스템이라 61차 리셋 영향 여부는 미확인(다음 세션에서 index.html의 #logsRefreshButton 존재 여부로 재확인 필요, 우선순위는 5~21보다 낮음). **[86차]** grep으로 index.html에 `#logsRefreshButton` 0건임을 확인해 새 베이스(`c74c0ac`)에 미반영임을 확정. 원본 41차 patch(index.html/runtime.js/style.css, 총 3곳 5개 치환)를 Claude 샌드박스에서 독립 `git clone`에 적용 -> anchor 전부 1회 매치, `npm install && node build.mjs`로 생성 번들 재생성, 변경 파일 6개·라인 증감이 원본 41차 커밋과 정확히 일치함을 확인, `node --check`/`node --test`(746/747) 통과. v1 반영 스크립트가 사용자 PC의 node/npm 부재로 막혀, 동일 빌드 결과를 base64 전체교체로 담은 v2(`86cha_item24_logs_refresh_carrot_ryu_v2.ps1`)로 교체해 전달, 실행/push 대기.
25. 온로드 화면에 원형 녹화 버튼 추가(42차, commit 4f81ab75) -- [65차] 새 베이스(4e3b44a8) 위에
    재반영 완료(commit `b152e192`, git ls-remote + commit diff로 확인). 42차 원본 그대로이며,
    깜빡임 효과(44차 항목 28)는 [66차]에서 별도 재적용. 실차 검증: 미실시(git pull 금지 상태 유지 중).
26. screenshots.js formatLogBytes import 누락 수정(44차) -- 사진 목록 렌더 크래시 근본수정. 61차
    리셋 이후 아직 미반영: 전제 조건이 "항목 11 -> 22 -> 23" 순서로 셋 다 필요함을 66차에서 확정.
    [67차/67차-fix]에서 항목 11 반영 + stray 파일 정리까지 완료(commit `81754ea3`까지 검증됨).
    [68차]에서 항목 22 착수를 위해 diff를 대조하다, 항목 22의 hud_renderer.py 부분(content_shift_y)이
    실제로는 항목 13~16(경로안내 박스 조정)뿐 아니라 항목 19(34차/33cha, `9fdefb3d`)까지 새 베이스에
    먼저 있어야 하는 체인임을 추가로 확인(13~16만으로는 anchor 불일치, 19까지 필요). 13→14→15→16→19를
    이번 세션에서 순서대로 재적용(반영 스크립트 실행 대기, 아래 각 항목 줄 참고). 이 다섯 개가 push
    확인되면 항목 22(체크박스/전체선택/업로드/다운로드 툴바 + content_shift_y)와 항목 23(39cha-fix,
    formatRelativeEpoch import)을 이어서 착수. 다음 세션(또는 이 세션 이어서) 최우선. **[85차]** 항목 11(67차)·13~16+19(68차)·22·23(85차)이 모두 현재 베이스 위에 갖춰진 것을 전제로 항목 26(formatLogBytes import)까지 함께 재검증 완료, v2 반영 스크립트 실행/push 대기(핵심 발견 44 참고). **[86차 확인]** commit `c74c0ac`로 push 완료 확인(screenshots.js에 `formatLogBytes` import 실제 존재 재확인). 항목 26 이식 완료. 실차 검증: 미실시.
27. delete_all_videos를 SCREEN_RECORDING_DIRS 전체 기준으로 확장(44차) -- [66차] 새 베이스
    (b152e192) 위에 재반영 완료(commit `0d511753`, git ls-remote + commit diff로 확인, 원본
    44차 diff와 일치). 실차 검증: 미실시(git pull 금지 상태 유지 중).
28. record_button.py에 set_blink_phase() 추가 + hud_renderer.py _blink_timer 배선(44차) -- [66차]
    새 베이스(b152e192) 위에 재반영 완료(commit `0d511753`, git ls-remote + commit diff로 확인,
    원본 44차 diff와 일치). 실차 검증: 미실시(git pull 금지 상태 유지 중).
29. js/generated/logs.js, generated/asset-manifest.json 번들 재생성(45차, commit `99b49a1`) -- 44차 소스 수정이 반영 안 된 채 커밋됐던 생성 번들을 Claude가 Linux sandbox에서 npm install && node build.mjs로 재생성, sha256/`node --test` 737/737로 검증 완료. GitHub 반영 확인됨(45차-정정 세션에서 커밋 메시지 전문 대조로 재검증). **46차에서 실기기 배포까지 확인됨**: 도구 탭 로그에서 실제 `git pull`(`e2f356198..99b49a113`, Fast-forward) + `reboot` 실행을 확인, 이어서 크래시 해소(26번)까지 실증됨.
30. screenshot_capture.py의 `rl.take_screenshot()` -> `rl.load_image_from_screen()` 교체 + 저장 포맷 PNG -> JPG 전환(47차, commit `41fd34a7`) -- DPI 스케일 버그로 인한 세로 뒤바뀜/과대 용량 수정. 48차에서 git ls-remote + commit API + raw 조회(SHA 고정)로 GitHub 반영 확인됨. 실차 검증(스크린샷 버튼을 실제로 눌러본 결과물 확인): 미실시. **[87차]** 새 베이스(`ba929b5`) 위에, 항목 30~36 전체를 carrot-ryu-v1(`9ccf1206`) 아카이브의 56차 최종본 기준으로 한 번에 재적용(개별 중간 단계가 아니라 최종 결과물 그대로) -- screenshot_capture.py/screenshot_button.py 전체교체, hud_renderer.py는 49차 버튼위치 이동만 Replace-Block 2곳으로 반영(84차 sdi_descr 배지 수정은 보존), application.py는 신규 반영(54차 request_temp_capture()). 독립 clone 2회(최초 검증 + 완전히 별개의 재현 clone)에서 py_compile 4개 전부 통과, application.py는 v1과 byte-exact 일치, 잔여 참조(구 API) 0건 확인. 반영 스크립트(`87cha_items30_36_carrot_ryu.ps1`) 작성/9절 체크리스트 통과. **[88차]** commit `0923f8396dacbb61a23e1c394751d8014ddddf5f`로 push 확인됨(GitHub commit API 재확인). 실차 검증: 미실시.
31. screenshot_capture.py/screenshot_button.py에 진단 로그(cloudlog.debug/warning/exception) 추가 + hud_renderer.py 스크린샷 버튼 위치를 화면 중앙에서 좌측 170px로 이동(49차, 반영 스크립트 실행 대기) -- 스크린샷 버튼 무반응/미저장 제보의 원인을 다음 실차 테스트에서 특정하기 위한 진단 단계. GitHub 반영 여부는 다음 세션에서 확인 필요. 실차 검증: 미실시. **[87차]** 새 베이스(`ba929b5`) 위에, 항목 30~36 전체를 carrot-ryu-v1(`9ccf1206`) 아카이브의 56차 최종본 기준으로 한 번에 재적용(개별 중간 단계가 아니라 최종 결과물 그대로) -- screenshot_capture.py/screenshot_button.py 전체교체, hud_renderer.py는 49차 버튼위치 이동만 Replace-Block 2곳으로 반영(84차 sdi_descr 배지 수정은 보존), application.py는 신규 반영(54차 request_temp_capture()). 독립 clone 2회(최초 검증 + 완전히 별개의 재현 clone)에서 py_compile 4개 전부 통과, application.py는 v1과 byte-exact 일치, 잔여 참조(구 API) 0건 확인. 반영 스크립트(`87cha_items30_36_carrot_ryu.ps1`) 작성/9절 체크리스트 통과. **[88차]** commit `0923f8396dacbb61a23e1c394751d8014ddddf5f`로 push 확인됨(GitHub commit API 재확인). 실차 검증: 미실시.
32. screenshot_capture.py 저장 확장자 `.jpg` -> `.png` 롤백(50차, 반영 스크립트 실행 대기) -- 49차 진단 로그로 클릭 전달/`load_image_from_screen()` 문제가 아니라 `rl.export_image()` 자체가 raylib 레벨에서 실패한다는 것을 확정한 뒤, JPG export 미지원 가설을 검증하기 위한 변수 분리 테스트. `load_image_from_screen()` DPI 수정은 그대로 유지. 실차 검증: 미실시(다음 세션 최우선 -- PNG로도 실패하면 가설 기각, 성공하면 JPG export 문제로 확정). **[87차]** 새 베이스(`ba929b5`) 위에, 항목 30~36 전체를 carrot-ryu-v1(`9ccf1206`) 아카이브의 56차 최종본 기준으로 한 번에 재적용(개별 중간 단계가 아니라 최종 결과물 그대로) -- screenshot_capture.py/screenshot_button.py 전체교체, hud_renderer.py는 49차 버튼위치 이동만 Replace-Block 2곳으로 반영(84차 sdi_descr 배지 수정은 보존), application.py는 신규 반영(54차 request_temp_capture()). 독립 clone 2회(최초 검증 + 완전히 별개의 재현 clone)에서 py_compile 4개 전부 통과, application.py는 v1과 byte-exact 일치, 잔여 참조(구 API) 0건 확인. 반영 스크립트(`87cha_items30_36_carrot_ryu.ps1`) 작성/9절 체크리스트 통과. **[88차]** commit `0923f8396dacbb61a23e1c394751d8014ddddf5f`로 push 확인됨(GitHub commit API 재확인). 실차 검증: 미실시.
33. screenshot_button.py의 _on_click()이 클릭 즉시 캡처를 실행하던 것을 pending 플래그로 미루고, hud_renderer.py _render() 끝(모든 HUD를 그린 뒤)에서 소비하도록 변경 + screenshot_capture.py에 480p(세로 기준) 다운스케일(rl.image_resize) 추가(51차, 반영 스크립트 실행 대기) -- 스크린샷에 시계/온도 HUD가 빠지던 원인(캡처가 같은 프레임의 나머지 HUD보다 먼저 실행됨)을 코드로 확정하고 수정. 실차 검증: 미실시(다음 세션 최우선 -- 시계/온도 포함 여부, 480p 리사이즈 동작 여부). **[87차]** 새 베이스(`ba929b5`) 위에, 항목 30~36 전체를 carrot-ryu-v1(`9ccf1206`) 아카이브의 56차 최종본 기준으로 한 번에 재적용(개별 중간 단계가 아니라 최종 결과물 그대로) -- screenshot_capture.py/screenshot_button.py 전체교체, hud_renderer.py는 49차 버튼위치 이동만 Replace-Block 2곳으로 반영(84차 sdi_descr 배지 수정은 보존), application.py는 신규 반영(54차 request_temp_capture()). 독립 clone 2회(최초 검증 + 완전히 별개의 재현 clone)에서 py_compile 4개 전부 통과, application.py는 v1과 byte-exact 일치, 잔여 참조(구 API) 0건 확인. 반영 스크립트(`87cha_items30_36_carrot_ryu.ps1`) 작성/9절 체크리스트 통과. **[88차]** commit `0923f8396dacbb61a23e1c394751d8014ddddf5f`로 push 확인됨(GitHub commit API 재확인). 실차 검증: 미실시.
34. hud_renderer.py의 캡처 호출을 AugmentedRoadView._render() 끝(_draw_border_carrot() 다음)으로 재이동 + HudRenderer에 consume_pending_screenshot_capture() 공개 메서드 추가(52차, commit `e4816edc`) -- GitHub 반영 확인됨(git ls-remote + commit 메시지 대조, 53차). 캡처 시점이 border 텍스트(차량명/LD·LT·SR/laneless/git branch/IP)보다 앞서던 문제를 수정. 실차 검증: 미실시. 53차에서 이 수정으로도 문제가 남는다는 전제 하에 render-texture 재사용 방식으로 더 근본적인 재설계가 합의됐고(코드 미반영), 구현 시 이 52차 변경분(및 51·52차의 augmented_road_view.py 캡처 호출부)은 되돌릴 예정. **[87차]** 새 베이스(`ba929b5`) 위에, 항목 30~36 전체를 carrot-ryu-v1(`9ccf1206`) 아카이브의 56차 최종본 기준으로 한 번에 재적용(개별 중간 단계가 아니라 최종 결과물 그대로) -- screenshot_capture.py/screenshot_button.py 전체교체, hud_renderer.py는 49차 버튼위치 이동만 Replace-Block 2곳으로 반영(84차 sdi_descr 배지 수정은 보존), application.py는 신규 반영(54차 request_temp_capture()). 독립 clone 2회(최초 검증 + 완전히 별개의 재현 clone)에서 py_compile 4개 전부 통과, application.py는 v1과 byte-exact 일치, 잔여 참조(구 API) 0건 확인. 반영 스크립트(`87cha_items30_36_carrot_ryu.ps1`) 작성/9절 체크리스트 통과. **[88차]** commit `0923f8396dacbb61a23e1c394751d8014ddddf5f`로 push 확인됨(GitHub commit API 재확인). 실차 검증: 미실시.
35. application.py에 request_temp_capture(callback) 추가 + screenshot_capture.py/screenshot_button.py 전체 재작성 + hud_renderer.py/augmented_road_view.py에서 51·52차 캡처 호출 경로 제거, render-texture 재사용 방식으로 스크린샷 캡처 근본 재설계(54차, commit `e047beb3`) -- GitHub 반영 확인됨(git ls-remote + SHA고정 raw 재조회 + py_compile 5개 + grep 마커 확인). 녹화가 이미 쓰던 render texture 추출 경로(begin_texture_mode~end_texture_mode~load_image_from_texture)를 스크린샷에도 그대로 재사용해, 49~52차에 걸쳐 하나씩 고치던 HUD 누락/DPI/타이밍 문제 전체를 구조적으로 해소하려는 시도. 저장 확장자는 .png 유지(50차 롤백 상태 그대로), 480p 다운스케일(51차)도 그대로 유지. 실차 검증: 미실시(다음 세션 최우선). **[87차]** 새 베이스(`ba929b5`) 위에, 항목 30~36 전체를 carrot-ryu-v1(`9ccf1206`) 아카이브의 56차 최종본 기준으로 한 번에 재적용(개별 중간 단계가 아니라 최종 결과물 그대로) -- screenshot_capture.py/screenshot_button.py 전체교체, hud_renderer.py는 49차 버튼위치 이동만 Replace-Block 2곳으로 반영(84차 sdi_descr 배지 수정은 보존), application.py는 신규 반영(54차 request_temp_capture()). 독립 clone 2회(최초 검증 + 완전히 별개의 재현 clone)에서 py_compile 4개 전부 통과, application.py는 v1과 byte-exact 일치, 잔여 참조(구 API) 0건 확인. 반영 스크립트(`87cha_items30_36_carrot_ryu.ps1`) 작성/9절 체크리스트 통과. **[88차]** commit `0923f8396dacbb61a23e1c394751d8014ddddf5f`로 push 확인됨(GitHub commit API 재확인). 실차 검증: 미실시.
36. screenshot_capture.py의 save_screenshot_image()에 rl.image_flip_vertical(image) 추가(55차, 반영 스크립트 실행 대기) -- 54차 render-texture 재사용 방식으로 캡처가 OpenGL 텍스처 픽셀 순서상 상하반전된 채 저장되던 문제 수정. 영상 녹화 경로(ffmpeg vflip)와 동등한 보정을 스크린샷 경로에 적용. 실차 검증: 미실시(다음 세션 최우선 -- 상하반전 해소 여부만 확인하면 됨(56차 실차검증 완료 -- 아래 [56차] 항목 참고), border HUD/480p/PNG는 54차에서 이미 확인). **[87차]** 새 베이스(`ba929b5`) 위에, 항목 30~36 전체를 carrot-ryu-v1(`9ccf1206`) 아카이브의 56차 최종본 기준으로 한 번에 재적용(개별 중간 단계가 아니라 최종 결과물 그대로) -- screenshot_capture.py/screenshot_button.py 전체교체, hud_renderer.py는 49차 버튼위치 이동만 Replace-Block 2곳으로 반영(84차 sdi_descr 배지 수정은 보존), application.py는 신규 반영(54차 request_temp_capture()). 독립 clone 2회(최초 검증 + 완전히 별개의 재현 clone)에서 py_compile 4개 전부 통과, application.py는 v1과 byte-exact 일치, 잔여 참조(구 API) 0건 확인. 반영 스크립트(`87cha_items30_36_carrot_ryu.ps1`) 작성/9절 체크리스트 통과. **[88차]** commit `0923f8396dacbb61a23e1c394751d8014ddddf5f`로 push 확인됨(GitHub commit API 재확인). 실차 검증: 미실시.

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
39차 코드 작업(사진 업로드 UI, 경로안내 박스 여백) 자체는 직전 세션에서 정적 검증까지 마쳤으나, 무료 사용량 한도로 carrot-ryu 반영 스크립트(.ps1) 전달 전에 세션이 종료됨. 이어받은 세션에서 그 스크립트를 실행하기 전 재검증한 결과, 9절·18절에 이미 문서화된 필수 규칙 3건이 지켜지지 않은 상태였음을 발견: (1) `git clone`에 `--config core.autocrlf=false`(27차) 누락, (2) 한글 포함 `.ps1` 파일 자체의 UTF-8 BOM(21차) 누락, (3) 스크립트 종료 시 임시 폴더를 삭제하지 않고 사용자에게 수동 삭제를 안내(18절 금지 항목). 스크립트의 문자열 치환(anchor) 로직 자체는 GitHub 최신 클론에 대해 파이썬으로 재현했을 때 17곳 모두 정확히 1회 매치로 문제없었음. 즉 "코드 변경 내용"은 정확했으나 "전달 형식"이 규칙을 어긴 경우로, 22차 핵심 발견(지침 문서 미조회)과 유사하게 "직전 세션이 규칙을 몰라서"가 아니라 "규칙 준수 여부를 전달 직전에 재확인하지 않아서" 발생한 사례. 세 가지 위반을 모두 수정한 뒤 최종 스크립트를 전달함. **[84차 재확인]** 이 중 (1) BOM((21차)) 항목이 84차에서 세 번째로 재발함을 확인 -- 서술형 규칙만으로는 재발을 막지 못한다고 판단해, 19절 절차로 사용자 승인을 받아 9절에 "전달 전 필수 자가검증 체크리스트"(BOM/`core.autocrlf`/임시폴더/`Get-PythonCmd`를 py_compile과 동급의, 실행하고 결과를 보고해야 하는 검증 단계로 승격)를 정식 반영함.

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

## 핵심 발견 35 (50차) -- 스크린샷 export_image 실패의 원인이 클릭 전달이 아니라 JPG export 자체일 가능성 확정적으로 좁힘
49차에서 추가한 진단 로그(`_on_click` 진입 로그, `capture_onroad_screenshot` 3개 실패분기 로그)를 실차 반영(commit `dfdbfff9`) 후 확보한 swaglog로 분석. `_on_click` 프레임에서 export_image 실패 경고가 매번 함께 찍힌다는 사실로 클릭 콜백 도달과 `load_image_from_screen()` 성공까지는 실증됨(추측 아님, 로그 근거). 실패는 오직 `rl.export_image()` 호출 지점뿐이며, 이 실패가 47차(git pull 이전)에도 이미 있었던 점과 46차까지 PNG는 저장에 성공했던 점을 근거로 JPG export 미지원을 유력 가설로 제시, 확장자만 되돌리는 변수 분리 테스트를 다음 실차 검증으로 예정. 상세: FINDINGS.md 2026-09-16(50차) 항목.

## 핵심 발견 36 (51차) -- 스크린샷에 시계/온도 HUD가 빠지는 원인: 캡처가 같은 프레임의 나머지 HUD보다 먼저 실행됨
hud_renderer.py의 HudRenderer._render()는 screenshot_button.render()(클릭 처리 포함)를 _draw_date_time()/_draw_tpms()/_draw_egpu_badge()/_draw_cruise_speed_animation()보다 먼저 호출한다. ScreenshotButton._on_click()이 클릭 즉시 capture_onroad_screenshot()(rl.load_image_from_screen()으로 그 순간의 프레임버퍼를 읽음)을 호출하던 기존 구조에서는, 아직 그려지지 않은 시계/온도/eGPU 배지/크루즈 애니메이션이 캡처에서 항상 빠지는 것이 코드상 필연적임을 확정(50차 핵심 발견 35의 export_image 실패와는 별개의 새로운 원인). _on_click()이 pending 플래그만 세우고 _render() 끝에서 그 플래그를 소비해 캡처를 실행하도록 변경. 같은 세션에서 요청된 480p(세로 기준) 다운스케일(rl.image_resize)도 screenshot_capture.py에 함께 반영. 실차 검증은 다음 세션 최우선. 상세: FINDINGS.md 2026-09-16(51차) 항목.

## 핵심 발견 37 (54차) -- Windows PC의 `python3` 명령이 반영 스크립트 내 정적 검증을 콘솔 출력 없이 조용히 실패시킬 수 있음
54차 반영 스크립트가 py_compile 검증 단계에서 어떤 에러 텍스트도 출력하지 않은 채 `[중단] py_compile 실패`로만 끝남. Linux sandbox에서 동일한 Replace-Block 3곳을 그대로 재현해 `python3 -m py_compile`을 돌려보니 정상 통과(exit 0)해 코드 자체는 문제가 없음을 먼저 확정(11절: 추측 대신 재현으로 확인). 유력 원인은 Windows 10/11의 앱 실행 별칭(App Execution Alias) -- python.org 설치본은 보통 `python.exe`/`py.exe`(런처)만 PATH에 등록하고 `python3.exe`는 없는 경우가 흔한데, 이 이름으로 호출하면 Microsoft Store 유도용 스텁이 콘솔 출력 없이 대신 실행돼 반환값만 비정상으로 끝남. 반영 스크립트에 `py -3` -> `python3` -> `python` 순으로 실제 버전 출력이 나오는 후보를 찾아 사용하는 `Get-PythonCmd` 함수를 추가(9절 검증 규칙과 별개로, 검증 자체가 이 PC에서 실행 가능한지부터 확인하는 방어 계층)해 해결. 사용자 PC의 Python 실행 환경(python3/py/python 중 무엇이 실제 동작하는지)은 세션마다 다를 수 있으므로, 앞으로 py_compile을 포함하는 반영 스크립트는 이 자동탐지 방식을 기본으로 채택 제안(19절 절차대로 사용자 승인 시 지침 문서 9절에도 정식 반영 검토). **[84차, 채택 완료]** 82차에서 이 방식이 v3->v4 사이에서 또 한 번 빠졌던 재발(같은 세션 안에서도 "개별 스크립트마다 매번 재적용돼야 하는 방어 로직"이었음)을 계기로, 19절 절차로 사용자 승인 받아 9절 "전달 전 필수 자가검증 체크리스트"에 기본값으로 정식 반영함(더 이상 "필요할 때만 추가"가 아님).

## 핵심 발견 38 (69차) -- "코드 수정 현황"의 stale "GitHub 반영됨" 표기가 20절 리셋 이후에도 장기간 방치될 수 있음
62차 안내문이 "61차 리셋 이후 각 항목은 실제로 재적용될 때마다 개별 갱신하라"고 미리 경고했음에도, 항목 5~10·12·17·18·20·21(Google Drive 파이프라인 전체)은 68차까지 7개 세션 동안 아무도 재확인하지 않아 리셋 이전 "GitHub 반영됨" 표기가 그대로 남아있었다. 그 사이 63~68차는 hud_renderer.py 계열(항목 3·4·11·13~16·19·25·27·28)만 순서대로 재적용하며 CURRENT_STATUS 목록을 위에서부터 훑지 않고 "다음 필요한 항목"만 골라 처리해온 것이 원인으로 추정된다. 69차에서 항목 22(39차) 착수 전 의존관계를 역추적하다 우연히 발견했고, 독립 `git clone`으로 `gdrive_upload.py` 부재 + routes.py POST 엔드포인트 부재를 직접 확인해 실증했다(16절, 11절). 앞으로 새 항목을 재적용하기 전에는 그 항목이 서브시스템 경계를 넘어 의존하는 다른 항목(예: 22가 20에, 20이 5~10·12·17·18·21에 의존)까지 먼저 "GitHub 반영됨" 표기만 믿지 말고 실제 코드 존재 여부를 확인할 것.


## 핵심 발견 39 (78차) -- 다른 AI가 만든 반영 스크립트의 구조적 버그 3종 + devnotes 미반영
채팅이 끊기면 코드는 push되어도 devnotes는 통째로 유실될 수 있음
챗지피티가 작성한 항목 17 반영 스크립트를 실행하며 서로 다른 layer의 버그 3건이 연쇄로 드러났다.
(1) `git fetch origin <8자리 축약 SHA>`는 GitHub 서버가 ref로 인식하지 못해 거부한다(`couldn't
find remote ref`) -- reachable 여부와 무관하게 40자리 전체 SHA가 필요함을 독립 재현으로 확정.
(2) `git diff ... | Out-File -Encoding ascii`처럼 PowerShell 파이프라인(성공 스트림)으로 git의
표준출력을 캡처해 파일에 쓰면, 비ASCII(한글 주석 등)가 많이 섞인 긴 diff에서 patch가 손상돼
`git apply --check`가 `patch fragment without header`로 실패할 수 있다(원인은 파이프라인
캡처/재인코딩 과정으로 추정, 정확한 메커니즘은 미확정). git 자체가 파이프라인을 거치지 않고 파일에
직접 쓰는 `git diff --output=<file>` 옵션으로 완전히 우회됨을 독립 재현으로 확인 -- 앞으로 patch를
파일로 뽑아야 하는 스크립트는 `Out-File`/`>` 대신 이 방식을 기본으로 삼을 것.
(3) PowerShell의 `-match`/`-notmatch`는 좌변이 배열이면 "전체가 조건을 만족하는가"의 불리언이
아니라 "조건을 만족하는(또는 만족하지 않는) 개별 원소들의 배열"을 반환한다. `$Diff = git ... diff`
처럼 여러 줄짜리 명령 출력을 변수에 담으면 PowerShell이 자동으로 줄 단위 문자열 배열로 저장하므로,
`if ($Diff -notmatch 'X')`는 "X를 포함하는 줄이 하나도 없으면 참"이 아니라 "X를 포함하지 않는
줄들의 배열이 비어있지 않으면 참"으로 동작해, 대부분의 실전 diff에서 매치되는 줄이 1~2줄뿐이어도
거의 항상 거짓 실패(오탐)로 중단된다. 이번 사례는 실제로 패치가 정상 적용된 뒤에도(4~6/8단계 전부
성공) 이 검증 단계에서만 계속 실패했다 -- 스칼라 문자열(이미 파일로 읽어둔 patch 원문 등)로 검사
대상을 통일하면 해결된다. 앞으로 diff/patch 텍스트에 대한 문자열 포함 여부 검사는 배열이 아니라
반드시 단일 문자열 변수에 대해 수행할 것.
(4) 별개로, 항목 17 코드 push까지 마친 이전 대화가 devnotes(CURRENT_STATUS.md/WIP.md/HANDOFF.md)
3개 파일 편집 도중, HANDOFF.md 작성 전에 끊겨 devnotes가 전혀 push되지 못한 채 남았다. 대화가
끊기면 로컬(컨테이너) 파일 편집 내용은 전부 사라지고 GitHub에 실제로 push된 것만 남으므로, 코드
push 확인 직후 devnotes 3개 파일도 가능한 한 바로 이어서 완성해 같은 세션 안에서 push까지 끝내는
것이 안전하다(76차/77차의 "코드는 됐는데 devnotes만 뒤처짐" 패턴, 핵심 발견 27/38과 연결되는
동일 계열 위험 -- 이번엔 지연이 아니라 완전 유실 직전까지 갔다는 점이 다름). 다음 세션 시작 시
`git ls-remote`로 carrot-ryu-note HEAD가 예상과 다르면(코드 HEAD는 최신인데 devnotes HEAD가
뒤처져 있으면) 곧바로 이 패턴을 의심하고 devnotes 재작성부터 시작할 것.

## 핵심 발견 40 (84차) -- 실차 검증 기록이 실제로는 다른 if/elif 분기를 봤을 수 있음 + get_text_draw_pos() align="left_bottom" 미구현
경로안내 박스의 `if sdi_descr: ... elif road_name: ...` 구조에서, 38차/40차의 "실차 검증 정상" 기록은 사실 도로명(elif) 분기만 캡처한 것이었고 sdi_descr(신호과속/교통정보 수집지점 등) 분기는 프로젝트 전체 역사상 한 번도 실제로 확인된 적이 없었음(38차 FINDINGS가 "신호과속 배지 부재로 판단 보류"라고 이미 명시했었으나 이후 세션들에서 40차의 "여백 모두 정상 확인"이 sdi_descr까지 포함하는 것으로 오인/누락됨). 실제로 sdi_descr 분기에는 진짜 버그가 있었음: `openpilot/system/ui/lib/text_draw.py`의 `get_text_draw_pos()`는 `center_bottom`/`center_top`/`left_top`/`right_top`/`left_center`/`center`/`right_center` 7개 정렬만 처리하고 `left_bottom`은 처리하지 않아, `align="left_bottom"`으로 호출하면 함수 맨 위 기본값(`draw_y = y + y_offset`)이 그대로 적용되어 사실상 `left_top`처럼 동작함. `hud_renderer.py`의 `_draw_text_left_bottom()`(제목/신호과속·교통정보 배지/도로명 3곳에서 사용)이 전부 이 경로를 타므로, 세 곳 모두 텍스트가 의도보다 자기 글자 높이만큼 아래로 밀려 그려짐 -- 다만 배지처럼 별도 사각형과 텍스트 크기를 맞춰 비교하는 요소에서만 육안으로 뚜렷하게 드러남(제목/도로명은 배경이 큰 박스라 어긋나도 눈에 덜 띔). 84차에서 사용자 요청으로 sdi_descr 블록만 범위를 한정해 개별 보정(공용 함수는 미수정) -- 제목/도로명 쪽 근본 수정 여부는 다음 세션 사용자 판단 대기. 앞으로 `if/elif`로 갈리는 UI 요소를 실차 검증할 때는 "어느 분기가 표시된 화면이었는지"까지 기록에 명시할 것.

## 핵심 발견 41 (84차 계속2) -- Windows PowerShell 5.1의 `Set-Content -Encoding UTF8`은 원본에 BOM이 없어도 항상 BOM을 새로 붙인다
84차 반영 스크립트가 `hud_renderer.py`/`WIP.md`/`CURRENT_STATUS.md`/`HANDOFF.md` 4개 파일을 전체 재작성할 때 전부 `Set-Content -Path ... -Encoding UTF8`을 사용했는데, push 후 GitHub 원본을 재조회해보니 네 파일 모두 맨 앞에 `EF BB BF`(UTF-8 BOM)가 새로 삽입돼 있었다. 원본 파일들은 모두 BOM 없는 상태였으므로, 이는 `-Encoding UTF8` 자체가 Windows PowerShell 5.1에서 항상 BOM을 붙이는 동작(PowerShell 7/Core의 `UTF8NoBOM`과 달리 5.1에는 그런 옵션이 없음)이기 때문임을 확인했다. 지침 문서 9절의 기존 문구가 "`Set-Content -Encoding UTF8` 또는 BOM 없는 UTF-8을 사용한다"처럼 둘을 사실상 같은 것으로 서술해 놓은 것 자체가 틀린 전제였다. `hud_renderer.py`는 Python이 파일 맨 앞 UTF-8 BOM을 자동으로 건너뛰므로 `py_compile`이 정상 통과해 이번에도 걸러지지 않았다(11절: 정적 검증 통과가 "결과물이 규칙을 100% 지켰다"는 뜻은 아님). 수정: 대상 파일을 전체 재작성하는 모든 쓰기는 `[System.IO.File]::WriteAllText($Path, $Content, (New-Object System.Text.UTF8Encoding($false)))`만 사용하고, 쓴 뒤 대상 파일 첫 3바이트가 BOM이 아닌지 확인하는 것을 9절 "전달 전 필수 자가검증 체크리스트"에 정식 반영(19절 절차, 사용자 승인 완료). 보정 스크립트로 네 파일 모두 BOM 제거.

## 핵심 발견 42 (84차 계속2) -- anchor 매치 횟수(1회)만 확인하고 치환 *결과*를 다시 보지 않으면, 의도한 헤더가 통째로 삭제돼도 못 잡는다
84차 devnotes 반영 스크립트의 `WIP.md` 갱신 로직이 anchor를 `"# WIP\n\n## 83차"`로 잡고 이를 `"[새 84차 항목]\n\n## 83차"`로 치환했는데, 새 콘텐츠 쪽에 `"# WIP"`를 다시 넣지 않아 파일 최상단 제목 줄이 통째로 사라진 채 push됐다. anchor가 정확히 1회 매치된다는 것은 "그 자리에서 치환이 일어났다"만 보증하지, "치환 결과가 의도와 같다"는 것은 보증하지 않는다는 것을 보여준 사례(기존에 알려진 "`# WIP` 헤더 *중복*" 이슈와는 반대로 이번엔 "소실"). 수정: anchor 매치 횟수 확인에 더해, 치환 *결과* 텍스트(특히 파일 맨 앞/헤더 줄)를 다시 눈으로 또는 diff로 확인하는 절차를 9절 체크리스트에 추가(19절 절차, 사용자 승인 완료). 보정 스크립트로 `"# WIP"` 헤더 복원.

## 핵심 발견 43 (84차 계속2, 사용자 실행 중 발견) -- Python 버전/컴파일 외부 호출이 인터랙티브 REPL로 빠져 스크립트가 무한 대기할 수 있음
`84cha2_hud_renderer_bom_fix.ps1` 실행 중 `py_compile` 검증 단계에서 스크립트가 Python 인터랙티브 셸(`>>>`)에 빠져 멈춤(사용자가 `Ctrl+C`로 중단, `git commit`/`push` 이전이라 반영 사고 없음). 정확한 원인은 미확정(추정: 배열 스플래팅으로 외부 exe 호출 시 인자 조합 문제)이나, 재발 방지로 Python 외부 호출 전부에 표준입력 EOF를 미리 공급(`"" | & $Cmd @Args`)하도록 9절 체크리스트 항목 4에 추가 반영, 종료 코드와 실제 출력을 항상 응답에 남기도록 강화. 상세: WIP.md 84차 계속2 항목.

## 핵심 발견 44 (85차, 사용자 실행 중 발견) -- 63차와 동일한 `.gitattributes` `* text=auto` CRLF 문제가 Invoke-ReplaceBlock에 정규화 누락으로 재발
사용자가 `85cha_item22_23_26_carrot_ryu.ps1`을 실행한 결과, 첫 Replace-Block 호출(`content_shift_y-decl`, hud_renderer.py)에서 `Anchor match count != 1: got 0`으로 안전하게 중단됨(`git commit`/`push` 이전이라 반영 사고 없음 -- 15절/18절 안전장치 정상 동작). 다음 세션에서 원인을 재현/확정: (1) `git ls-remote`로 carrot-ryu HEAD가 `132d85b`(스크립트가 실행됐을 때와 동일한 베이스)임을 확인, (2) 그 SHA의 `hud_renderer.py`를 raw로 재조회해 스크립트의 `$old_hud_0` 앵커 텍스트와 Python으로 바이트 단위 대조한 결과 정확히 1회 매치함을 확인(즉 앵커 자체나 베이스 불일치 문제가 아님), (3) 저장소 루트 `.gitattributes`에 여전히 `* text=auto`가 있음을 확인 -- 63차에서 이미 "일부 Windows Git 환경은 `core.autocrlf=false`를 clone 시 줘도 `text=auto` 때문에 체크아웃 시 CRLF로 변환될 수 있다"고 규명됐던 바로 그 조건, (4) 그런데 이번 스크립트의 `Invoke-ReplaceBlock` 함수를 코드로 직접 읽어보니 63차 이후 9절에 이미 명문화된 "매칭 전 CRLF->LF 정규화 병행" 절차가 실제로는 빠져 있었음(HANDOFF.md/WIP.md에는 "9절 체크리스트 전항목 통과"로 기록돼 있었으나, 그 체크리스트 항목 중 CRLF 정규화는 실제 함수 코드에 없었던 것 -- 서술만 확인하고 코드 자체를 다시 읽어 대조하지 않으면 이런 누락이 "통과"로 잘못 보고될 수 있음을 보여준 사례). Linux sandbox는 checkout 시 CRLF로 변환되지 않아 이 사이드는 재현되지 않았지만(원인 조건인 `.gitattributes`는 동일하게 존재), Windows 쪽에서 체크아웃 시 CRLF로 변환됐다면 LF 기준으로 작성된 `$Old` 문자열과 바이트 단위로 어긋나 0회 매치가 되는 것과 정확히 일치하는 실패 양상이다. 수정: `Invoke-ReplaceBlock`에 파일 내용과 `$Old`/`$New`를 모두 `-replace "`` `r`` `n", "`` `n"`로 정규화한 뒤 매칭/치환/재확인하도록 추가(63차와 동일한 패턴, 9절 원칙을 실제 코드로 재적용)한 `85cha_item22_23_26_carrot_ryu_v2.ps1`로 교체, 신선한 독립 clone에 대해 12개 Replace-Block 앵커 전부 1회 매치 + `py_compile`/`node --check` 통과를 Python 시뮬레이션으로 재확인했다. 앞으로 "9절 체크리스트 통과"를 기록할 때는 체크리스트 항목의 서술만 대조하지 말고, 그 항목이 실제로 구현하려는 코드(예: CRLF 정규화 로직 자체)가 스크립트 안에 문자 그대로 존재하는지 직접 읽어 확인할 것.

- 미확인: carrot-ms 모델 셀렉터 코드 미분석
- 다음 작업: [신규] 56차에서 55차 스크린샷 상하반전 수정 실차검증 완료 -- 다음 우선순위는 사용자 확인 필요. 후보: 37차 락 수정 동시성 재현 검증(의도적으로 동시에 두 업로드 시도), 34차 도로명-신호과속 같은 줄 배치 확인(신호과속 구간에서), 28~30차 레이아웃 정밀 재검증, 실기기 터미널로 배포된 tools.js 내용 확인해 번들 최신 여부 검증, test_web_upload.py 실제 실행해 낡은 테스트 범위 확정, 데드코드 3개 삭제 + 대응 테스트 정리, docs 갱신, 46차까지 확인된 것을 제외한 나머지 코드 변경 전부 실주행 재검증, carrot-ms 신규 커밋 cherry-pick 검토 착수(WIP_SYNC.md 참고), 핵심 발견 31 재발 방지 제안(스크립트 파일명 버전 표시 규칙화) 채택 여부 확인, WIP.md "# WIP" 헤더 중복 정리(낮은 우선순위)
- 보류 확인 항목: TurnSpeedControlMode=2 / EnableSpeedTF=0 / LeadAccelResponse=0 / DisableDM=2 / LateralTorqueCustom=0 / AutoRoadSpeedLimitOffset / SpeedFromPCM
- **[80차]** 항목 20(36차, commit `0835b059`, 화면녹화 탭 업로드 UI 신규 구현 + 당근서버 라벨/햄버거 메뉴 버그 수정) 구현 완료. 원본 커밋(`0835b059`) patch 전체 조회 후 현재 베이스(`a959576f`)의 대상 9개 소스 파일 blob hash가 원본 diff pre-image와 정확히 일치함을 확인해 anchor 유효성을 사전 확정, Replace-Block으로 전체 적용(routes.py 신규 POST 엔드포인트 `api_screenrecord_upload` 포함) 후 `npm install && node build.mjs`로 생성 번들 재생성까지 포함해 변경 파일이 원본 커밋과 정확히 같은 12개임을 확인. 추출한 소스 전용 diff를 완전히 독립된 두 번째 clone에 재적용해 12개 파일 전부의 blob hash가 byte-exact 일치함을 검증(9절/16절). `node --test` 747개 중 746개 통과, 유일 실패(`ar_projection_golden.test.mjs`)는 무수정 base clone에서도 동일하게 재현되는 기존 환경 문제로 이번 변경과 무관함을 별도 무수정 clone으로 재확인. 반영 스크립트(`80cha_item20_screenrecord_upload.ps1`) 작성/전달, 실행 대기(push 미실시). 실차 검증: 미실시.


- **[85차 계속3, 새 세션]** `git ls-remote`로 GitHub가 여전히 84차2 상태(`132d85b`/`fa038e0`)임을 재확인 --
  85차/85차 계속(item22/23/26 재검증, v1 anchor 0회 매치 실패, 핵심 발견 44 CRLF 정규화 누락 발견, v2
  스크립트 작성)이 전부 아직 push되지 않은 채팅 사본이었음을 재확인(3절). 신선한 별도 clone에서
  `85cha_item22_23_26_carrot_ryu_v2.ps1`의 로직을 처음부터 독립 재시뮬레이션(base64 전체교체 7개 +
  CRLF 정규화 Replace-Block 12곳 전부 1회 매치, `py_compile`/`node --check` 전부 통과) + 9절 체크리스트
  6항목을 스크립트 파일 자체 grep으로 직접 대조해 전부 확인. v2 스크립트는 그대로 사용 가능, devnotes
  반영 스크립트를 이 세션에서 신규 작성해 함께 전달. 실행/push는 여전히 대기 중.

- **[87차]** 세션 시작 체크포인트(`git ls-remote`)로 carrot-ryu(`ba929b5`)/carrot-ryu-note(`15cdf6e`)가 86차
  상태 그대로임을 확인(86차 이후 추가 push 없음). 위 "carrot-ryu HEAD" 최상단 줄이 82차/83차 기준으로 오래
  방치돼 있던 것을 16절에 따라 발견/정정(코드 변경 아님). 이어서 마지막 남은 이식 항목 30~36(스크린샷 캡처
  체인 7건, 47~56차)을 새 베이스(`ba929b5`) 위에 착수 -- carrot-ryu-v1(`9ccf1206`) 아카이브의 56차 최종본을
  기준으로 screenshot_capture.py/screenshot_button.py 전체교체, hud_renderer.py는 84차 sdi_descr 배지 수정을
  보존하며 49차 버튼위치 이동만 Replace-Block으로 좁혀 반영, application.py는 신규 반영(54차
  request_temp_capture() render-texture 재사용 재설계). 독립 clone에서 py_compile 4개 통과, application.py는
  v1과 byte-exact 일치, 구 API(`capture_onroad_screenshot`/`consume_pending_screenshot_capture`) 잔여 참조
  0건까지 확인 후, 완전히 별개의 두 번째 clone에 스크립트 페이로드를 재현해 동일 결과를 재확인(9절/16절,
  핵심 발견 42 원칙). 반영 스크립트(`87cha_items30_36_carrot_ryu.ps1`) 작성, 9절 "전달 전 필수 자가검증
  체크리스트" 전항목(비ASCII 0건/`core.autocrlf=false`/임시폴더 자동삭제/`Get-PythonCmd`+EOF공급) 통과 확인.
  이로써 36개 항목 전부에 대해 최소 1회 재적용 스크립트가 작성됨(항목 22/23/24/26은 이미 push 완료, 30~36은
  이번 세션 스크립트로 실행/push 대기).

  별개로, devnotes 갱신을 준비하며 WIP.md를 raw로 재조회하는 과정에서 이 파일에 실제 null byte(`\x00`) 손상
  1건이 있었음을 처음 발견했다 -- 57차 항목 본문 중 "carrot-ryu fork point(`\x00`2015190f5, ...)" 자리의
  숫자 `0`이 널바이트로 바뀌어 있었고, 같은 해시가 파일 다른 곳에는 `02015190f5`로 정상 표기돼 있어 원본
  문자를 바이트 단위로 확정해 `0`으로 복원했다(그 외 null byte 없음을 전수 확인). devnotes 반영 스크립트에
  WIP.md 전체교체(9절 "이번만 예외" 명시, 평소엔 최상단 anchor 삽입만 하는 이어붙이기형이지만 이번엔 중간
  손상 수정이 함께 필요해 예외 적용)로 이 수정 + 87차 신규 항목을 함께 반영. 파일 맨 끝(1차 세션 기록)에
  이미 존재하던 별개의 인코딩 깨짐(mojibake로 추정, null byte와 무관 -- 내 수정 이전부터 있었음을 원본과
  대조해 확인)은 이번 세션에서 손대지 않고 그대로 둠(7절 "임의 축소/삭제 금지" 원칙, 다음 세션에서 필요시
  사용자 판단 요청). 기존에 알려진 "`# WIP` 헤더 중복"(789번째 줄) 이슈도 "다음 작업" 목록에 낮은 우선순위로
  이미 기록돼 있어 이번에는 손대지 않음.

  실행/push 대기(코드 스크립트 + devnotes 스크립트 모두). 실차 검증: 미실시.
