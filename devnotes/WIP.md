# WIP

## 17차 (완료 -- 코드 반영, GitHub push 완료) -- send_tmux_web() Google Drive 업로드 전환

- 배경: 16차 HANDOFF 미완료 우선순위 1번. tmux 진단 전송(온로드 자동 진단, CAN
  에러, 예외 상황, tmux_send 명령)의 "carrot/toss 선택 전송" 경로가 아직 옛
  Carrot/Toss HTTP 업로드(session 발급 -> multipart POST)를 쓰고 있었음.
- carrot_man.py의 send_tmux_web()을 tmux.log[+toggle_values.json]+metadata.json을
  zip으로 묶어 gdrive_upload.upload_file_resumable()로 업로드하는 방식으로 전면
  재작성.
  - metadata.json에 기존 payload(_tmux_upload_payload: tmux_why, car_name,
    git_branch 등)를 그대로 담아, Carrot/Toss 서버가 받던 진단 필드가 유실되지
    않도록 함(Drive는 별도 DB가 없으므로 파일로 동봉).
  - 파일명: tmux_{car_name}_{tmux_why}_{timestamp}.zip (영숫자/-/_ 외 문자는
    _ 치환)
  - 압축 방식은 ZIP_DEFLATED 선택(16차 대시캠 zip은 이미 압축된 h265/zstd라
    ZIP_STORED였지만, tmux.log/json은 텍스트라 DEFLATE 이득이 있고 콤마 기기
    CPU 부담도 미미함).
  - 동기 메서드(send_tmux_web)에서 비동기 gdrive_upload.upload_file_resumable()을
    호출해야 해서, 파일 내 기존 관례(carrot_navi_http_server 호출부의
    asyncio.run() 패턴)를 그대로 따라 asyncio.run()으로 브릿지.
  - 반환값 계약(web_response.ok / .status_code, 실패 시 None)은 호출부
    (1255/1285/1318/1319행 등)가 그대로 재사용하므로 변경하지 않음 --
    성공 시 SimpleNamespace(ok=True, status_code=200, drive_result=...)를
    반환, 실패 시 기존과 동일하게 예외를 잡아 None 반환.
  - send_tmux_carrot_logs()(Discord carrot_logs 포럼용 독립 고정 전송)는 이번
    변경과 무관하며 손대지 않음(HANDOFF 지침대로).
  - import 정리: create_web_upload_session_sync, tmux_web_target은 이 함수에서만
    쓰였는데 더 이상 필요 없어 import 목록에서 제거(10절 최소 변경 원칙 -- 직접
    관련된 dead import 제거만, 그 외 리팩터링 없음). read_web_settings/
    selected_upload_settings는 _tmux_toss_only()가 계속 사용하므로 유지.

- ⚠ [중요 교훈] diff(git apply) 방식 최초 실전 시도가 실패함:
  - 9차 세션에서 도입한 "파일은 크지만 변경 범위가 작은 경우 unified diff 사용"
    원칙에 따라 처음에 diff/git apply 스크립트를 전달했으나, 사용자 실행 시
    `error: corrupt patch at ...patch:101`로 git apply --check 단계에서 실패.
  - 원인 추정: git diff의 컨텍스트 공백 줄(빈 줄, 들여쓰기 공백)이 채팅
    복사/붙여넣기 과정에서 손상됨(트레일링 공백 유실 등). PowerShell here-string
    자체의 CRLF/LF 정규화로는 해결되지 않는 종류의 손상.
  - 대응: 15/18절 원칙대로 git apply 실패 시 스크립트가 즉시 중단되어 carrot-ryu에
    어떤 손상도 남기지 않음(HEAD는 cc734e18 그대로 유지됨을 GitHub API로 재확인).
    강제 적용(--3way/--reject 등)은 시도하지 않음.
  - 최종 해결: diff 대신 "문자열 치환(find & replace) 방식"으로 전환. 변경 전/후
    블록을 통째로 here-string으로 담고, 치환 전 `[regex]::Matches(...).Count -eq 1`로
    "정확히 1회만 매치"하는지 검증한 뒤에만 치환 실행(매치 0회/2회 이상이면 아무
    것도 바꾸지 않고 중단) -- 이 방식이 diff보다 채팅 복사 손상에 훨씬 강함.
  - 문자열 치환 스크립트로 재시도 -> 3개 블록 모두 1회 매치 확인 -> 치환 ->
    py_compile 통과 -> commit/push 성공(commit 2869149, GitHub API/git ls-remote로
    재확인 완료).
  - [다음 세션부터 반영할 원칙 제안, 19절 절차로 사용자 승인 필요]: 9절의 diff
    옵션을 "1순위"가 아니라 "문자열 치환으로 처리하기 어려운 경우(같은 텍스트가
    여러 곳에 나타나 유일 매치를 만들 수 없는 대규모/분산 변경)의 대안"으로
    재조정하는 것을 고려. 문자열 치환은 (a) 유일 매치 검증이 가능해 채팅 복사
    손상에 강하고 (b) git apply의 컨텍스트 줄 민감도 문제가 없음. 아직 문서
    변경은 하지 않았고, 다음 세션에 사용자 승인받아 9절을 수정할지 결정.
- 반영 방식: 문자열 치환(위 사유로 diff에서 전환) -- import 블록 2곳 + 함수 본문
  1곳, 총 3개 블록. 실제 carrot-ryu clone에서 각 블록 유일 매치(count=1) 확인 +
  치환 후 py_compile 통과 확인 후 commit/push.
- 검증: 정적 분석 + 실제 GitHub carrot-ryu에 반영 후 최신 HEAD(2869149)를
  git ls-remote로 재확인 완료. 실제 Google Drive 업로드 테스트, 실차 검증은
  미실시.
- 미완료: PARAMS_REGISTRY.md에 Drive 파라미터 3종 아직 미등록(15차부터 이월,
  16차 HANDOFF 우선순위 4). CURRENT_STATUS.md가 13차 시점에서 갱신이 멈춰 있던
  것을 17차에서 16~17차분까지 소급 반영.
## 16차 (완료 -- 코드 반영 + hotfix) -- upload_jobs.py zip+Drive 재작성 + app.py 연결 + 반영 스크립트 버그 3종 발견/수정

- 배경: 15차에서 만든 gdrive_upload.py가 아직 아무 데서도 호출되지 않는
  상태였음(15차 HANDOFF 우선순위 1a/1c). 이번 세션에서 실제로 연결.
- 1) gdrive_upload.py: upload_file_resumable()에 progress_cb(sent, total)
  콜백 파라미터 추가. 호출자가 자체 진행률/취소 체계를 가질 때 바이트 단위
  진행률을 전달받기 위함. 콜백에서 예외를 던지면 그대로 전파되어 업로드 중단.
- 2) server/features/dashcam/upload_jobs.py: run_upload_segments() 전면
  재작성. 세그먼트별 개별 스트리밍 업로드(Carrot/Toss 대상) -> 세그먼트
  파일들을 zip(무압축 ZIP_STORED)으로 묶어 gdrive_upload.upload_file_resumable()
  로 단일 업로드하는 방식으로 전환. job/progress/취소/Discord 알림 골격은
  유지, 내부 구현만 교체(10절 최소 변경 원칙).
  - 설계 변경: 성공/실패 판정이 "세그먼트별" -> "zip 전체 단위"로 바뀜.
    Discord 알림을 target 무관 항상 시도하도록 변경(기존엔 carrot일 때만).
- 3) server/app.py: gdrive_upload.register(app) 앱 진입점 연결
  (15차 HANDOFF 우선순위 1c 완료).
- 4) server/services/dashcam_upload_report.py: gdrive 대상일 때
  "Open & Analyze" 구간 링크 생성 스킵 (이번 세션에 새로 발견).
- **반영 과정에서 스크립트 버그 3종을 실전에서 발견/수정함** (전부 Claude
  샌드박스 리허설로는 못 잡았던, 사용자 실제 Windows PC 환경에서만
  드러난 문제들 -- 앞으로 반영 스크립트 작성 시 반드시 유의할 것):
  a) **CRLF 정규화 누락**: Windows git의 core.autocrlf로 로컬 체크아웃 시
     .py 파일이 CRLF로 변환됨. PowerShell 문자열 치환 코드가 LF(`` `n ``)
     기준으로 .Contains()/.Replace()를 했다가 실패 -> 이후 파일을 읽을 때
     항상 CRLF/CR을 LF로 정규화하는 Read-Utf8Lf 헬퍼를 표준으로 채택.
  b) **상대경로 vs 프로세스 작업 디렉터리 불일치**: PowerShell의
     Push-Location/Set-Location으로 "현재 위치"를 옮겨도 .NET
     [System.IO.File]::WriteAllText 같은 API는 그 위치를 따라가지 않고
     실제 프로세스 작업 디렉터리(예: C:\WINDOWS\system32)를 기준으로
     상대경로를 해석함 -> 이후 모든 파일 I/O 경로는 $TempDir 기준
     절대경로(Join-Path)로 고정하는 것을 표준으로 채택.
  c) **PowerShell here-string(`@' ... '@`) 끝 개행 소실**: 닫는 줄(`'@`)
     바로 앞의 개행이 문자열에 포함되지 않아, 줄바꿈을 포함해야 하는
     교체 텍스트 끝에 개행이 누락됨 -> dashcam_upload_report.py에
     `else []  if runs:` 처럼 두 줄이 한 줄로 붙는 문법 오류가 실제로
     **한 번 GitHub에 push된 채로 남아있었음**(commit dae901ce). hotfix
     커밋(cc734e18)으로 즉시 수정. 앞으로 here-string으로 만드는 교체
     텍스트는 항상 명시적으로 끝에 개행이 있는지 눈으로 재확인할 것.
  d) (버그는 아니지만 함께 발견) **py_compile 실패가 스크립트를 멈추지
     못함**: `python -m py_compile`이 SyntaxError로 실패(exit code != 0)
     했는데도 PowerShell이 이를 종료 오류로 인식하지 못해 그대로
     commit/push까지 진행됨(외부 프로세스의 비정상 exit code는
     $ErrorActionPreference="Stop"의 대상이 아님) -> 이후 `$LASTEXITCODE`
     를 명시적으로 확인해 0이 아니면 throw하도록 표준화.
- 결과: dae901ce(문법 오류 포함, 실사용 불가 상태로 짧게 존재)
  -> cc734e18(hotfix, 정상)까지 push 완료 확인. GitHub 실제 파일(4개)을
  codeload tarball로 재조회해 py_compile 전부 통과 재확인함(16절 원칙:
  스크립트 출력만 믿지 않고 GitHub 실제 상태로 재검증).
- 반영: 9절 방식. 1차 스크립트(diff 2개 + 문자열치환 2개) 실행 중
  app.py 단계에서 CRLF 문제로 1차 실패 -> 수정판 실행 중 상대경로 문제로
  2차 실패 -> 수정판2로 4개 파일 반영 성공(dae901ce)하되
  dashcam_upload_report.py에 here-string 개행 버그로 인한 문법 오류
  포함된 채 push됨 -> hotfix 스크립트로 해당 한 줄만 수정해 push(cc734e18)
- 실차 검증: 미실시(정적 분석 + mock 시뮬레이션만. 실제 Google Drive
  계정/토큰 업로드 테스트 없음. carrot-ryu가 콤마 디바이스에 설치되어
  실제로 대시캠 업로드 버튼을 눌러봐야 최종 검증됨)

## 15차 (진행 중 -- Carrotweb 구글드라이브 전환 범위 확정 + gdrive_upload.py 신규 모듈) -- web_upload.py Carrot/Toss -> Drive 2단계

- 배경: 14차에서 설계 방향(zip 압축 후 Drive 업로드)까지는 정리했으나
  tmux 진단/Discord 웹훅 처리 여부가 미결이었음. 이번 세션에서 사용자와
  범위를 재확인
- 1단계 - carrot-ryu 실제 구조 재확인 (codeload tarball, 리포 루트 밑에
  `openpilot/` 서브폴더가 한 겹 더 있음 확인 -- 이후 스크립트의 파일
  경로는 모두 `openpilot/selfdrive/carrot/...` 기준):
  - `selfdrive/carrot/web_upload.py`(333줄): Carrot/Toss HTTP 업로드 +
    tmux/carrot_logs 진단 전송 함수가 **한 파일에 공존**
  - `server/features/dashcam/upload_jobs.py`(663줄): 세그먼트별 동시
    스트리밍 업로드, 바이트 단위 진행률 추적
  - `server/features/dashcam/upload.py`: `resolve_upload_target()`,
    `discord_webhook_url()`/`send_discord_webhook()`(대시캠 업로드 완료
    알림용, tmux/carrot_logs 포럼과는 별개의 또 다른 Discord 웹훅임)
- 2단계 - **중요 구조 발견**: `log_upload_target`(carrot/toss) 설정
  하나가 서로 다른 두 시스템에서 공유되고 있었음
  1. 로그탭 "전송" 버튼(대시캠 세그먼트 업로드,
     `upload_jobs.py` -> `upload.resolve_upload_target()`)
  2. tmux 진단 전송 중 "선택 전송"(`carrot_man.py` ->
     `send_tmux_web()` -> `selected_upload_settings()`)
  - 반면 `send_tmux_carrot_logs()`(Discord `carrot_logs` 포럼용)는 대상
    URL이 `tmux.carrotpilot.app`으로 고정이고 `log_upload_target`은
    "Toss 전용이면 이 전송을 건너뛴다"는 `_tmux_toss_only()` 체크에만
    쓰임 -- 완전히 별개는 아니지만 대상 자체는 공유하지 않음
  - `web_settings.py`의 `LOG_UPLOAD_TARGETS = {"carrot","toss"}`,
    `log_upload_target` enum 필드가 이 모든 것의 공통 데이터 소스
- 3단계 - 사용자와 범위 확정 (2번의 확인 질문 거침):
  - 로그탭 "전송" 버튼(대시캠 업로드) -> Drive: 기존 확정 유지
  - tmux 진단 중 "carrot/toss 선택 전송"(`send_tmux_web()`) -> **이번에
    Drive로 추가 확정**
  - tmux 진단 중 "Discord carrot_logs 포럼용 고정 전송"
    (`send_tmux_carrot_logs()`) -> **그대로 유지** (Drive로 바꾸지 않음,
    Discord 봇이 소비하는 고정 엔드포인트라 구조가 다름)
  - `log_upload_target`/`LOG_UPLOAD_TARGETS`/`web_settings.py` 스키마
    자체는 건드리지 않기로 함(`_tmux_toss_only()`가 계속 이 값을 참조
    하므로) -- 다만 대시캠 업로드와 `send_tmux_web()`이 모두 Drive로
    이관되면 `log_upload_target`은 "carrot_logs 포럼 스킵 여부" 판단
    외에는 실질적으로 안 쓰이게 됨(설계상 다소 어색하지만 최소 변경
    원칙에 따라 이번엔 그대로 둠 -- 정리 필요성은 다음 세션 이월)
- 4단계 - c3-ms-dev의 `server/gdrive.py`(511줄, OAuth Device
  Authorization Grant + resumable 업로드) 재확인:
  - codeload로 다시 받아보니 **원본(폴더 이름 자동검색, drive.file
    스코프) 상태**였음 -- 14차에서 언급된 "폴더 ID 고정 + 전체 스코프"
    치환은 사용자 로컬(C:\dev\ryu)에서만 확인됐고 c3-ms-dev 원격 브랜치
    에는 반영 안 된 것으로 추정(다음 세션에서 재확인 필요, 우선순위는
    낮음 -- carrot-ryu 포팅에는 영향 없음)
  - carrot-ryu 이식본은 이 원본을 기준으로, 처음부터 폴더 ID 고정
    (`DRIVE_FOLDER_ID`) + `drive`(전체) 스코프로 직접 작성함
- 5단계 - 신규 모듈 `openpilot/selfdrive/carrot/gdrive_upload.py` 작성
  (Claude 샌드박스에서 py_compile 통과 확인, 사용자 PC 환경 기준 검증은
  아직):
  - OAuth Device Flow 엔드포인트(status/device/token/disconnect) +
    `upload_file_resumable()`(8MB 청크 resumable PUT) + job 진행률 추적
    -- c3-ms-dev와 동일 패턴
  - `_ensure_folder()`(이름 검색/자동생성) 대신 `_verify_folder()`(고정
    ID 존재/휴지통/타입 검증만, 신규 생성 안 함)로 교체
  - 위치를 `selfdrive/carrot/gdrive_upload.py`에 둔 이유: `web_upload.py`
    와 같은 레벨에 둬야 `carrot_man.py`(server/ 밖에 위치)와
    `server/features/dashcam/upload_jobs.py`(server/ 안에 위치) 양쪽에서
    같은 상대 경로 부담 없이 import 가능
  - `register(app)`은 인증/상태조회/job조회 엔드포인트만 등록. 실제
    "업로드 시작"(zip 압축, tmux 로그 전송)은 각 호출부가
    `upload_file_resumable()`을 직접 호출하는 방식으로 다음 세션에 연결
    예정(아직 미연결)
  - 반영: 9절 방식(신규 파일, PowerShell 스크립트) `apply_15_gdrive_module.ps1`
    로 carrot-ryu 브랜치에 전달함
- 실차 검증: 미실시(신규 모듈 작성 + 문법 검증만, 실제 업로드 동작
  테스트 없음. `upload_jobs.py`/`carrot_man.py`와 아직 연결 전이라 단독
  실행도 불가능한 상태)

## 13차 (완료 — 온로드 시계 좌측 화면 경계 잘림 버그 수정) — hud_renderer.py _draw_date_time() x좌표 보정

- 배경: 사용자가 실제 화면 사진(2026-09-13 23:32:34 촬영)을 공유, 좌측 상단
  시계가 "23:32:34"가 아니라 "3:32:34"로 보여 맨 앞 "2"가 잘림을 보고
- 원인 분석 (코드 레벨):
  - openpilot/selfdrive/ui/onroad/hud_renderer.py의 _draw_date_time()에서
    시계 텍스트(HH:MM:SS, font_size=100)를 align="center_bottom"으로 그리는데,
    기준 x가 rect.x+170(고정값)
  - text_draw.py의 get_text_draw_pos()는 center_bottom일 때
    draw_x = x - text_size.x*0.5 로 계산 -> 텍스트 폭이 넓을수록 draw_x가
    더 왼쪽으로 밀림
  - 8자 "HH:MM:SS" 폭이 넓어 draw_x가 음수(화면 밖)로 계산되어 좌측 첫 글자
    (시 10의 자리)가 잘림 (사진 현상과 일치)
  - 12차에서 시계 캐시 키에 tm_sec을 추가하며 "%H:%M"(5자) -> "%H:%M:%S"(8자)
    로 표시 자릿수가 늘어난 것이 이 clipping을 유발한 회귀로 추정
- 수정: measure_text_cached로 시계 텍스트 실측 폭을 구해, 좌측 여백
  (UI_CONFIG.border_size=30)을 보장하도록 x를 동적으로 보정(clamp)하는 로직
  추가. 날짜 텍스트(MM-DD(요일))는 동일 x를 재사용해 시계와 세로 정렬 유지
- 파일: openpilot/selfdrive/ui/onroad/hud_renderer.py, _draw_date_time()만
  수정(10절 최소 변경 원칙)
- 반영 방식: 9절 diff(git apply) 방식. 반영 직전 GitHub 최신
  hud_renderer.py를 다시 조회해 그 위에서 diff 생성, 별도 clone
  시뮬레이션에서 git apply --check/git apply 성공 + py_compile 통과 확인
  (Claude 샌드박스, 사용자 PC python 환경과 무관)
- 실차 검증: 미실시(정적 분석 + 코드 시뮬레이션만)

## 12차 (완료 — 코드 반영 + 반영 프로세스 디버깅) — 더블탭 대신 화면 중앙 하단 스크린샷 버튼 + 온로드 시계 초단위 표시(재반영)

- 배경: 11차에서 설계했던 "더블탭으로 스크린샷" + "시계 초단위 표시"가 실제로는
  GitHub에 반영되지 못한 채(패치 적용 실패 반복) 이번 12차까지 넘어옴. 이번
  세션에서 설계를 바꿔 실제로 반영을 완료함.
- 설계 변경: 더블탭 제스처(augmented_road_view.py 수정) 대신, 온로드 화면 중앙
  하단에 항상 보이는 버튼(ScreenshotButton, 지름 140px 원형 카메라 아이콘)을
  새로 추가하는 방식으로 재설계. 기존 단일 탭(사이드바 토글)과 겹치지 않도록
  명시적 탭 대상만 사용.
  - 신규 파일: selfdrive/ui/onroad/screenshot_button.py (버튼 위젯, pyray로
    원형 카메라 아이콘 직접 그림)
  - 신규 파일: selfdrive/ui/onroad/screenshot_capture.py (11차와 동일한 로직 —
    take_screenshot()으로 cwd에 저장 후 SCREEN_RECORDING_DIRS[1]로 이동)
  - hud_renderer.py: ScreenshotButton import, __init__에서 인스턴스 생성,
    _render 하단 중앙에 배치, user_interacting()에 버튼 눌림 상태 포함
  - hud_renderer.py: 11차 계획대로 시계 캐시 키에 tm_sec 추가,
    "%H:%M" -> "%H:%M:%S"
  - 이번 회차에서는 augmented_road_view.py 더블탭 판정 코드는 적용하지 않음
    (설계 변경으로 불필요) — 11차 WIP 기록의 더블탭 관련 서술은 이번 재설계로
    대체됨
  - 11차가 계획했던 backend(config.py의 SCREEN_RECORDING_IMAGE_EXTS,
    catalog.py의 kind 구분)와 frontend(screenrecord.js/runtime.js의 이미지
    뷰어 액션) 변경은 이번 12차에 포함되지 않음 — 스크린샷 파일은 폴더에
    저장되지만, carrotweb 로그탭에서 정지 이미지로 정상 표시/재생될지는
    미확인 상태로 남음(다음 세션 후보)
- 반영 프로세스 디버깅(참고용, 앞으로 비슷한 실수 방지):
  1. 최초 diff에 PowerShell Set-Content -NoNewline으로 diff 파일 끝 개행이
     빠져 "corrupt patch" 발생 -> -NoNewline 제거로 1차 수정
  2. 그 다음 "patch does not apply" 발생 -> 처음엔 core.autocrlf 체크아웃
     변환을 원인으로 추정했으나, Claude 샌드박스에서 실제 GitHub 최신
     hud_renderer.py를 직접 받아(raw.githubusercontent.com이 네트워크 허용
     도메인이라 컨테이너에서 바로 curl 접근 가능함을 확인) LF/CRLF/BOM 각각
     재현 테스트했지만 모두 정상 적용됨 -> 이 진단은 근거 부족으로 폐기
  3. BOM 회피를 위해 Set-Content를 [System.IO.File]::WriteAllText 기반
     헬퍼로 바꿨다가, PowerShell here-string이 마지막 줄 개행을 보존하지
     않는 특성 때문에 diff 파일에 "corrupt patch"가 재발 -> 헬퍼에 "끝에
     개행 없으면 추가" 로직을 넣어 최종 해결(샌드박스에서 재현/수정 모두 검증)
  4. py_compile 단계에서 원인불명 실패 -> 실제로는 이 PC에 진짜 Python이
     없고 Windows "App Execution Alias" 더미 python.exe만 있어서 발생.
     Claude 샌드박스의 실제 Python으로 3개 파일 모두 문법 검증 완료(정상)로
     대체 확인. 스크립트의 python 감지 로직(Get-Command python)이 이 더미를
     걸러내지 못하는 문제는 아직 미수정(다음 세션 후보)
  5. 반영 스크립트의 git add -A 범위에 diff 파일 자체(hud_renderer.diff)가
     포함되어 carrot-ryu에 잘못 커밋됨 -> git rm으로 후속 커밋(4f4f8a8)에서
     제거, GitHub raw로 삭제 확인(단, raw.githubusercontent.com CDN 캐시로
     약 5분간 이전 내용이 잠깐 더 보일 수 있음 확인)
- 검증: Claude 샌드박스에서 실제 GitHub 최신 파일 기준 diff 적용 성공 확인,
  py_compile 통과(3개 파일) 확인. GitHub push 후 raw.githubusercontent.com으로
  반영 내용 재확인(ScreenshotButton import/사용, second_key 로직 모두 확인됨)
- 실차 검증: 미실시
- carrot-ryu HEAD: 12차 완료 후 4f4f8a8 (684b30d에서 hud_renderer.diff
  오커밋 제거)

## 11李?(?꾨즺 ??肄붾뱶 ?섏젙) ???붾툝??罹≪퀜 ?ㅽ겕由곗꺑 + ?⑤줈???쒓퀎 珥덈떒???쒖떆

- ?ъ슜???붿껌 1: ?⑤줈???붾㈃ 醫뚯긽???쒓퀎媛 遺??⑥쐞濡쒕쭔 媛깆떊?섏뼱 珥??⑥쐞 ?쒖떆媛 ?꾩슂
  - 肄붾뱶 ?꾩튂: selfdrive/ui/onroad/hud_renderer.py??_refresh_date_time_text()
  - ?먯씤: 罹먯떆 ?ㅺ? tm_min源뚯?留??ъ슜??媛숈? 遺??덉뿉?쒕뒗 媛깆떊??嫄대꼫?
  - ?섏젙: 罹먯떆 ?ㅼ뿉 tm_sec 異붽?, ?щ㎎ "%H:%M"  "%H:%M:%S"濡?蹂寃?(18:36:02 ?뺤떇, 留ㅼ큹 媛깆떊)
- ?ъ슜???붿껌 2: ?⑤줈???붾㈃???붾툝??븯硫??ㅽ겕由곗꺑??李띿뼱 carrotweb 濡쒓렇??쓽
  "?붾㈃?뱁솕" 紐⑸줉?먯꽌 諛붾줈 蹂댁씠寃??섍퀬 ?띠쓬
  - ?붾툝???먯젙: selfdrive/ui/onroad/augmented_road_view.py??_handle_mouse_press()??    0.4珥?0px ?대궡 ?ы꺆?대㈃ ?붾툝??쑝濡?蹂대뒗 ?먯젙 濡쒖쭅 異붽?(_check_double_tap_screenshot).
    湲곗〈 ?⑥씪 ???대┃(?ъ씠?쒕컮 ?좉?)怨?HUD ?명꽣?숈뀡 以?臾댁떆 ?숈옉? 洹몃?濡??좎?
  - 罹≪퀜: ???뚯씪 selfdrive/ui/onroad/screenshot_capture.py 異붽?. pyray??    take_screenshot()?쇰줈 PNG ??? ????꾩튂??SCREEN_RECORDING_DIRS[1]
    (/data/media/0/screenrecord) ??carrotweb???대? ?ㅼ틪 以묒씤 ?대뜑??蹂꾨룄 諛섏쁺 ?놁씠
    ?먮룞 ?몄텧
  - 諛깆뿏??selfdrive/carrot/server/): config.py??SCREEN_RECORDING_IMAGE_EXTS
    (.png/.jpg/.jpeg) 異붽??섍퀬 SCREEN_RECORDING_EXTS???⑹궛. catalog.py??    build_videos()媛 kind="image"/"video" 援щ텇媛믪쓣 ?대젮二쇰룄濡??섍퀬, ?뺤? ?대?吏??    thumbnail_path()?먯꽌 ffmpeg -ss ?먯깋 ?놁씠 諛붾줈 由ъ궗?댁쫰留??섎룄濡?遺꾧린
  - ?꾨줎?몄뿏??selfdrive/carrot/web/): screenrecord.js?먯꽌 kind==="image"???됱?
    data-action??"view-screenrecord-image"濡?諛붽퓭 鍮꾨뵒???뚮젅?댁뼱 ???????뿉??    ?먮낯 ?대?吏媛 ?대━?꾨줉 ?섍퀬, runtime.js???대떦 ?≪뀡 ?몃뱾??異붽?. npm run build濡?    js/generated/logs.js(諛?asset-manifest.json ?댁떆) ?щ퉴??- 寃利? Claude ?뚮뱶諛뺤뒪?먯꽌 GitHub 理쒖떊 肄붾뱶(carrot-ryu, 10李?諛섏쁺 吏곹썑 = e1e587b,
  洹??꾩쓽 ?댁슜 ?녿뒗 鍮?而ㅻ컠 2c33603 "token test" ?ы븿) 湲곗??쇰줈 誘몃━ ?⑥튂 ?곸슜 
  py_compile ?듦낵(?섏젙 Python ?뚯씪 5媛?, node --check ?듦낵(JS ?뚯씪 2媛?, npm run
  build濡?濡쒓렇??踰덈뱾 ?щ퉴???뺤긽 ?꾨즺(esbuild ?먮윭 ?놁쓬)源뚯? ?뺤씤. cereal/capnp
  誘몃퉴?쒕줈 UI ?먯껜 援щ룞/pytest ?ㅽ뻾? ?대쾲?먮룄 遺덇?(9~10李⑥? ?숈씪???쒓퀎)
- ?ㅼ감 寃利? 誘몄떎?? ?ㅼ쓬 ?ㅼ＜?됱뿉???쒓퀎媛 珥??⑥쐞濡?留ㅼ큹 媛깆떊?섎뒗吏, ?⑤줈??  ?붾㈃ ?붾툝?????ㅽ겕由곗꺑??李랁? carrotweb 濡쒓렇??> ?붾㈃?뱁솕 紐⑸줉???대?吏濡??④퀬
  ??븯硫?????뿉???먮낯 ?대?吏媛 ?대━?붿? ?뺤씤 ?꾩슂
- 愿???녿뒗 由ы뙥?곕쭅 ?놁쓬. ?뚯씪 6媛??섏젙(hud_renderer.py, augmented_road_view.py,
  config.py, catalog.py, screenrecord.js, runtime.js) + ?뚯씪 1媛??좉퇋
  (screenshot_capture.py) + 鍮뚮뱶 ?곗텧臾?2媛?js/generated/logs.js,
  generated/asset-manifest.json)

## 10李?(?꾨즺 ??肄붾뱶 ?섏젙) ??RES/+ ?멸쾶?댁? ???ㅼ젙?띾룄媛 ?꾩옱?띾룄蹂대떎 ??븘吏??臾몄젣 ?덉쟾?μ튂 異붽?

- ?ъ슜???쒕낫: 異쒕컻 ??媛??以??? ??50km/h) ?몃뱾 +RES 踰꾪듉?쇰줈 ?щ（利??멸쾶?댁? ??
  ?ㅼ젙?띾룄媛 ?꾩옱?띾룄蹂대떎 ??쾶(?? ??30km/h) ?≫? 湲됯컧?띿씠 諛쒖깮?섎뒗 寃쎌슦媛 ?덈떎??  ?ㅼ궗??利앹긽 蹂닿퀬 (?ㅼ＜??濡쒓렇 ?놁씠 ?ъ슜???ㅻ챸 湲곕컲, ?꾩쭅 rlog濡??ы쁽 ?뺤씤 ??
- 肄붾뱶 ?뺤씤(carrot-ryu 2dbe492 湲곗?, selfdrive/car/cruise.py):
  - `_update_cruise_buttons()`??accelCruise ?멸쾶?댁? 遺꾧린(`_cruise_ready or not
    CC.enabled or CS.cruiseState.standstill`)?먯꽌, `_v_cruise_kph_at_brake`(釉뚮젅?댄겕
    ?쒖젏????ν빐?먮뒗 "?ш컻?? ?띾룄) ?먮뒗 ?꾩쭅 珥덇린?붾릺吏 ?딆? v_cruise_kph 媛믪씠
    ?꾩옱?띾룄(v_ego_kph_set)蹂대떎 ??? 梨꾨줈 洹몃?濡??멸쾶?댁? ?띾룄濡?梨꾪깮?????덈뒗
    寃쎈줈 議댁옱
  - `_v_cruise_kph_at_brake`??釉뚮젅?댄겕 ?ш컻 紐⑹쟻 ?몄뿉 `_auto_speed_up()`???꾨줈?쒗븳
    ?띾룄 ?숆린??濡쒖쭅(`AutoRoadSpeedLimitOffset > 0`???? 留??꾨젅??CC.enabled ?щ??
    臾닿??섍쾶 `nRoadLimitSpeed + offset`?쇰줈 ??뼱?, 726踰?以?遺洹??먯꽌??媛믪씠 梨꾩썙吏?    ???덉뼱, 理쒖큹 ?멸쾶?댁? ?쒖젏???꾨줈?쒗븳?띾룄 湲곕컲????? 媛믪씠 ?⑥븘?덉쓣 媛?μ꽦 ?덉쓬
    (?? `AutoRoadSpeedLimitOffset` 湲곕낯媛믪? -1?대씪 ?ъ슜?먭? ???듭뀡??耳?寃쎌슦?먮쭔
    ?대떦 寃쎈줈媛 ?대┝ - PARAMS_REGISTRY????媛?誘멸린濡앹씠????李⑤웾 ?ㅼ젙? 誘명솗??
  - `SpeedFromPCM`??1???꾨땶 湲곕낯 ?ㅼ젙(0 ???먯꽌??openpilot ?먯껜 v_cruise_kph 濡쒖쭅??    ?곗씠誘濡???寃쎈줈媛 ?ㅼ젣濡??곹뼢??以????덉쓬(1?대㈃ ?쒖젙 SCC 媛믪쓣 洹몃?濡?? - ??    寃쎌슦 臾몄젣媛 ?덈떎硫??쒖젙 ECU 履??댁뒋?대?濡??대쾲 肄붾뱶?섏젙 ????꾨떂)
- ?섏젙: 理쒖냼 蹂寃??먯튃???곕씪 ?멸쾶?댁? 遺꾧린 留덉?留됱뿉 ?덉쟾?μ튂(floor)留?異붽?.
  怨꾩궛???멸쾶?댁? ?띾룄媛 "?꾩옱?띾룄 + ENGAGE_SPEED_MARGIN_KPH(2km/h)"蹂대떎 ??쑝硫?  "?꾩옱?띾룄 + 2km/h"濡??щ┝. 釉뚮젅?댄겕 ????λ맂 ?띾룄媛 ?꾩옱?띾룄蹂대떎 ?믪? ?뺤긽?곸씤
  ?ш컻(?? 而ㅻ툕?먯꽌 媛먯냽 ??RES濡??댁쟾 ?ㅼ젙?띾룄濡?蹂듦?) 耳?댁뒪??洹몃?濡??좎???  (洹?媛믪씠 floor蹂대떎 ?щ?濡??곹뼢 ?놁쓬)
- 寃利?
  - 臾몃쾿寃利?py_compile) ?듦낵
  - 湲곗〈 `test_carrot_cruise_buttons.py`???멸쾶?댁? 愿???뚯뒪??4嫄?    (`test_accel_restores_at_least_brake_speed_while_cruise_is_off` 2嫄?
    `test_accel_keeps_initialized_speed_without_brake_snapshot_while_cruise_is_off`,
    "釉뚮젅?댄겕 ?????믪? ?띾룄濡??뺤긽 ?ш컻" ?좉퇋 耳?댁뒪)???숈씪 濡쒖쭅?쇰줈 ?ы쁽??    standalone ?⑹꽦 ?ㅽ겕由쏀듃濡?寃곌낵 ?쇱튂 ?뺤씤 (?뚮뱶諛뺤뒪??cereal/capnp 鍮뚮뱶媛 ?놁뼱
    pytest ?먯껜 ?ㅽ뻾? 9李⑥? ?숈씪?섍쾶 遺덇?)
  - ?ъ슜?먭? 蹂닿퀬??"50km/h 二쇳뻾 以?RES ??30km/h濡?湲됯컧?? ?쒕굹由ъ삤瑜??숈씪 濡쒖쭅?쇰줈
    ?ы쁽 ???섏젙 ??52km/h(?꾩옱?띾룄+2)濡??멸쾶?댁??⑥쓣 ?⑹꽦 ?뚯뒪?몃줈 ?뺤씤
- ?ㅼ감 寃利? 誘몄떎?? ?ㅼ쓬 ?몄뀡/?ㅼ＜?됱뿉???숈씪 ?곹솴(異쒕컻 媛??以?RES ?멸쾶?댁?) ?ы쁽
  ??湲됯컧?띿씠 ?щ씪議뚮뒗吏 ?뺤씤 ?꾩슂
- 愿???녿뒗 由ы뙥?곕쭅 ?놁쓬, ?뚯씪 1媛?cruise.py)留??섏젙, 12以?異붽?


## 9李?(?꾨즺 ??肄붾뱶 ?섏젙) ??route 而ㅻ툕 ?ㅺ?異?洹쇰낯?섏젙: median ?ㅽ뙆?댄겕 ?꾪꽣 異붽?

- 8李⑥뿉???ㅼ＜??濡쒓렇濡??뺤씤??route 媛먯냽 ?ㅺ?異쒖뿉 ??? ?ъ슜?먭? 洹쇰낯?섏젙(?듭뀡 ??
  ?좏깮
- carrot_man.py??carrot_navi_route()瑜??섏젙: 3??怨〓쪧??癒쇱? ?꾨? 怨꾩궛????
  3-?섑뵆 ?щ씪?대뵫 median ?꾪꽣瑜??곸슜?섍퀬 洹?寃곌낵濡쒕쭔 紐⑺몴?띾룄 ?곗텧?섎룄濡?援ъ“ 蹂寃?  (鍮꾩쟾 而ㅻ툕 curve_speed.py???대? ?덈뜕 median ?꾪꽣 諛⑹떇??route 履쎌뿉???숈씪 ?곸슜)
- 理쒖냼 蹂寃??⑥닔 ????釉붾줉留?援먯껜), Claude ?뚮뱶諛뺤뒪?먯꽌 GitHub 理쒖떊 肄붾뱶濡?誘몃━
  ?⑥튂 ?곸슜/臾몃쾿寃利?diff 寃利????ㅽ겕由쏀듃濡??꾨떖 ???ъ슜?먭? Termux?먯꽌 ?ㅽ뻾,
  carrot-ryu 釉뚮옖移섏뿉 諛섏쁺 ?꾨즺 (commit 0201519..2dbe492)
- ?ㅽ겕由쏀듃 ?ㅽ뻾 以???媛吏 ?댁뒋 諛쒖깮 諛??닿껐: ?쟦eredoc ???쒓? ?띿뒪?멸? Termux
  遺숈뿬?ｊ린 怨쇱젙?먯꽌 以꾨컮轅덉씠 源⑥졇 ?덉뼱?낆씠 ???ロ엺 臾몄젣(?ъ떆?꾨줈 ?닿껐, ?ㅼ젣 諛섏쁺
  ?????곹깭?먯꽌 以묐떒?먮뜕 寃??뺤씤) ?죊it diff媛 less ?섏씠?瑜??꾩슦硫??붾㈃??瑗ъ뿬
  ?멸퉴吏 源⑥쭊 臾몄젣(GIT_PAGER=cat, --no-pager diff --stat濡??닿껐). ???댁뒋 紐⑤몢
  肄붾뱶/devnotes???ㅼ젣 ?먯긽 ?놁씠 ?덉쟾?섍쾶 ?ъ떆?꾨줈 ?닿껐??- ?⑹꽦 ?뚯뒪?몃줈 ?꾪꽣媛 ?⑤컻??怨〓쪧 ?ㅽ뙆?댄겕瑜??쒓굅?섎㈃???뺤긽 而ㅻ툕???좎??⑥쓣 ?뺤씤
- ?ㅼ감 寃利? 誘몄떎?? ?ㅼ쓬 ?ㅼ＜?됱뿉???숈씪 遺꾧린???ы넻怨???rlog濡??ы솗???꾩슂

## 8李?(?꾨즺 ???ㅼ＜??濡쒓렇 遺꾩꽍) ??route 媛먯냽 ?ㅺ?異?理쒖큹 ?ㅼ쬆

- ?ъ슜?먭? ?ㅼ젣 肄ㅻ쭏 ?붾컮?댁뒪 二쇳뻾 濡쒓렇(route 000003fb--8470375f65--21, rlog/qlog/
  qcamera)瑜??낅줈?? 利앹긽: 怨좎냽?꾨줈 醫뚯빱釉?遺꾧린???묎렐 ??route湲곕컲 媛먯냽??誘몃━
  怨쇳븯寃?嫄몃졇?ㅺ? ?ㅼ떆 ?먮났?섎뒗 ?먮굦
- pycapnp + carrot-wip cereal ?ㅽ궎留덈줈 rlog.zst瑜?吏곸젒 蹂듯샇?뷀븯??carrotMan/carState/
  carControl/longitudinalPlan ??꾨씪???ш뎄?? 臾몄젣 援ш컙(t=47~59s) ?뺣? 遺꾩꽍
- ?뺤씤: t=47.3s寃?desiredSource="route"濡?desiredSpeed媛 67km/h濡?湲됰씫(?뱀떆 遺꾧린??  源뚯? ?꾩쭅 499m). ?ㅼ젣 媛먯냽 紐낅졊源뚯? ?댁뼱??vEgo 96??9km/h ?섎씫. ?댁쟾?먭? 7.5珥덇컙
  媛??媛쒖엯. ?댄썑 t=54.8~57.9s??route ?뚯뒪媛 115~121km/h濡??먯껜 ?ш퀎?곕릺硫?蹂듦?
- ?먯씤: carrot_navi_route()??3??40m) 怨〓쪧 怨꾩궛???ㅽ뙆?댄겕 ?쒓굅 ?꾪꽣媛 ?놁뼱, 遺꾧린??  ?대━?쇱씤 湲고븯 援?냼 ?쒓끝???ㅼ젣蹂대떎 湲됲븳 而ㅻ툕濡??ㅺ?異쒗븳 寃껋쑝濡?異붿젙(5李④퀎???뺤쟻
  遺꾩꽍?먯꽌 ?대? 吏?곷맂 由ъ뒪?ъ쓽 ?ㅼ젣 諛쒗쁽). ?ㅻ쭔 ?대━?쇱씤 湲고븯 ?먯껜??吏곸젒 ?議?紐삵븿
- FINDINGS.md???곸꽭 湲곕줉. 肄붾뱶 ?섏젙? ?꾩쭅 ?섏? ?딆쓬(????듭뀡 3媛吏 ?쒖떆, ?ъ슜??  ?먮떒 ?湲?
- ?ㅼ감 寃利? ?꾩긽 ?먯껜???ㅼ＜??濡쒓렇濡??뺤씤. ?먯씤 硫붿빱?덉쬁 ?쇰?(?대━?쇱씤 湲고븯)??  誘명솗吏?
## 7李?(?꾨즺 ????UI ?꾪솚 留덈Т由?+ carrot-ms ?숆린???먭?) ??釉뚮옖移??뺣━ 諛??좉퇋 而ㅻ컠 ?놁쓬 ?뺤씤

- ryujmin97/openpilot???ㅼ젣濡??⑥븘?덈뜕 carrot-ms, carrot-wip 釉뚮옖移?媛곴컖
  happymaj11r/openpilot, ajouatom/openpilot???꾩쟾??蹂듭궗蹂?瑜??ъ슜?먭? GitHub ??UI?먯꽌
  吏곸젒 ??젣 ?꾨즺. ?댁젣 ryujmin97/openpilot?먮뒗 carrot-ryu, carrot-ryu-note ??釉뚮옖移섎쭔
  議댁옱?섏뿬 臾몄꽌?붾맂 釉뚮옖移?援ъ꽦怨??쇱튂?섎뒗 ?곹깭濡??뺣━??(吏移?16????ぉ ?댁냼)
- carrot-ms(happymaj11r/openpilot) ?좉퇋 而ㅻ컠 ?숆린??寃??吏꾪뻾: git ls-remote濡??뺤씤??寃곌낵
  carrot-ryu HEAD? carrot-ms HEAD媛 ?뺥솗???쇱튂(02015190f58a4380a433ee0130e6374455dddc2e)
  ??6李??몄뀡 ?댄썑 carrot-ms???덈줈??rebase/而ㅻ컠???꾪? ?놁쓬. 諛섏쁺 ???而ㅻ컠 0嫄?- 李멸퀬濡?carrot-wip(ajouatom/openpilot)? HEAD媛 bb0e18bb8c09422fcd50dcf25c17e0d5c75072b1濡?  怨꾩냽 吏꾪뻾 以묒씠?? carrot-ms媛 ?꾩쭅 ?대? ?곕씪 rebase?섏? ?딆븘 吏移?2???먯튃?濡?吏곸젒 鍮꾧탳
  ??곸쑝濡??쇱? ?딆쓬
- WIP_SYNC.md瑜?carrot-ms 湲곗? 泥댄겕?ъ씤??諛⑹떇?쇰줈 媛깆떊(?대쾲 ?먭? 寃곌낵 湲곕줉)
- 肄붾뱶 蹂寃??놁쓬 (釉뚮옖移??뺣━ + ?먭?留??섑뻾), carrot-ryu???ъ쟾??carrot-ms? ?숈씪
- ?ㅼ감 寃利? ?대떦 ?놁쓬 (?명봽???먭? ?묒뾽)

## 6李?(?꾨즺 ??踰좎씠??釉뚮옖移??꾪솚) ??carrot-wip ??carrot-ms 濡?蹂寃?
- ?ъ슜?먭? happymaj11r/openpilot ??μ냼??carrot-ms 釉뚮옖移?肄ㅻ쭏 二쇳뻾紐⑤뜽 ?좏깮 湲곕뒫,
  carrot-wip 湲곕컲?쇰줈 留ㅻ쾲 ?ъ깮??rebase??瑜??뺤씤 ?붿껌
- git merge-base濡??뺤씤??寃곌낵 carrot-wip怨?carrot-ms??怨듯넻 議곗긽 而ㅻ컠???놁쓬(?덉뒪?좊━
  怨듭쑀 ???? ??carrot-ms??carrot-wip???낅뜲?댄듃???뚮쭏??洹??꾩뿉 紐⑤뜽?좏깮 湲곕뒫???ㅼ떆
  ?뱀뼱 ?듭㎏濡??ъ옉??rebase/force-push)?섎뒗 諛⑹떇?쇰줈 ?먮떒??- ?꾩껜 ?덉뒪?좊━ 鍮꾧탳 寃곌낵 carrot-wip???녾퀬 carrot-ms?먮쭔 ?덈뒗 而ㅻ컠 117媛??뺤씤.
  ??以?紐⑤뜽 ??됲꽣 愿???ㅼ썙?쒕줈 ?꾪꽣留곹븳 寃???58媛? ?섎㉧吏 ??59媛쒕뒗 ?대윭?ㅽ꽣(怨꾧린??
  HUD, PC ?쒕??덉씠??吏?? 濡쒓렇 ?낅줈???쒕쾭(?좎뒪/?밴렐) ?좏깮 湲곕뒫 ?????꾨줈?앺듃? 臾닿???  湲곕뒫?쇰줈 ?먮떒?? ?좊퀎 ?댁떇(cherry-pick)? ?ㅻ떒怨??묒뾽????寃껋쑝濡??덉긽??- ?ъ슜??寃곗젙: ?좊퀎 ?댁떇 ??? carrot-ryu 釉뚮옖移??먯껜??踰좎씠?ㅻ? carrot-wip?먯꽌
  carrot-ms濡??꾨㈃ ?꾪솚?섍린濡?寃곗젙 (?뱀떆 carrot-ryu???ъ슜??肄붾뱶媛 ?꾪? ?놁뼱 ?덉쟾?섍쾶
  媛?ν븳 ?쒖젏?댁뿀??
- ?ㅽ뻾: carrot-ryu(origin) 釉뚮옖移???젣 ??happymaj11r/carrot-ms 湲곗??쇰줈 ?ъ깮??
  carrot-ryu HEAD媛 carrot-ms HEAD(02015190f58a4380a433ee0130e6374455dddc2e,
  "Recover evil-merge resolutions from carrot-wip PR #516 and PR #517")? ?쇱튂?⑥쓣 ?뺤씤
- carrot-ryu-note??洹몃?濡??좎? (湲곗〈 醫낅갑??遺꾩꽍 ?댁슜? carrot-wip 湲곕컲 肄붾뱶 遺꾩꽍?대씪
  carrot-ms?먮룄 ?遺遺?洹몃?濡??좏슚????肄붾뱶媛 ?ш쾶 媛덈씪吏吏 ?딅뒗 ???щ텇??遺덊븘??
- ?꾨줈?앺듃 吏移?臾몄꽌(PROJECT_INSTRUCTIONS)??"踰좎씠??釉뚮옖移? ??ぉ??carrot-wip ??  carrot-ms濡??섏젙?섎뒗 臾멸뎄瑜??ъ슜?먯뿉寃??꾨떖??(臾몄꽌 ?먯껜????μ냼 諛뽰뿉???ъ슜?먭?
  蹂닿??섎뒗 寃껋쑝濡??뚯븙?섏뼱 Claude媛 吏곸젒 ?섏젙?섏? ?딆쓬)
- ???ν썑 ?곹뼢: carrot-ms??留ㅻ쾲 ?덉뒪?좊━媛 ?ъ옉?깅릺誘濡? carrot-wip泥섎읆 fast-forward
  ?숆린?붽? 遺덇??ν븿. carrot-ms媛 ?낅뜲?댄듃???뚮쭏??carrot-ms? carrot-wip??而ㅻ컠 硫붿떆吏瑜?  鍮꾧탳??"紐⑤뜽 ??됲꽣 愿??而ㅻ컠"留??좊퀎 諛섏쁺?섎뒗 諛⑹떇???꾩슂??(2???숆린???먯튃???뺤옣 ?곸슜
  ?꾩슂 ???ㅼ쓬 ?몄뀡?먯꽌 WIP_SYNC.md 援ъ“瑜?carrot-ms?⑹쑝濡쒕룄 ?뺤옣?좎? 寃???꾩슂)
- 肄붾뱶 蹂寃??놁쓬 (釉뚮옖移?踰좎씠???꾪솚留??섑뻾, carrot-ryu???ъ쟾??carrot-ms? ?숈씪)
- ?ㅼ감 寃利? ?대떦 ?놁쓬 (?명봽??蹂寃??묒뾽)

## 5李?怨꾩냽 (?꾨즺 ??traffic_stop / curve_speed / MPC 肄붿뒪???⑥닔 遺꾩꽍) ??醫낅갑??肄붾뱶 遺꾩꽍 1?④퀎 留덈Т由?
- 媛숈? ?몄뀡?먯꽌 ?댁뼱??traffic_stop.py(?뺤????좏샇 媛먯냽) ??curve_speed.py(鍮꾩쟾 而ㅻ툕 媛먯냽) ??  longitudinal MPC 肄붿뒪???⑥닔(set_weights, jerk_factor) ?쒖쑝濡?遺꾩꽍 吏꾪뻾
- traffic_stop.py: 二쇳뻾紐⑤뜽 ?덉륫(x,y,v)留뚯쑝濡??뺤??좏샇 ?먮떒?섎뒗 ?쒖닔 E2E ?대━?ㅽ떛 ?뺤씤.
  XState ?곹깭癒몄떊, TrafficStopModelLeadMatcher(5?꾨젅??confirm)源뚯? ?뺤씤. HD留??좏샇?됱긽
  ?몄떇 ?놁쓬 ??紐⑤뜽 ?깅뒫 ?섏〈 由ъ뒪???덉쓬. long_mpc.py??x2 obstacle源뚯? ?ㅼ젣 ?곌껐???뺤씤.
  ??李⑤웾 ?ㅼ젙: TrafficLightDetectMode=2(湲곕낯媛? ?대? ?쒖꽦 ?곹깭)
- curve_speed.py(鍮꾩쟾): route 踰꾩쟾怨??щ━ ?몃? ?대퉬 ??遺덊븘?? ?쒖닔 modelV2 湲곕컲. 怨〓쪧=
  yaw_rate/velocity瑜?3??median ?꾪꽣留???臾쇰━怨듭떇(v=sqrt(?↔??띾룄?덉궛/怨〓쪧))?쇰줈 怨꾩궛 ??  route 踰꾩쟾蹂대떎 寃ш퀬?? ??李⑤웾 AutoCurveSpeedFactor=80(湲곕낯蹂대떎 ?먯뒯?섍쾶 ?ㅼ젙?? ?뺤씤
- longitudinal MPC 肄붿뒪???⑥닔: stock openpilot acados ?꾨젅?꾩썙??洹몃?濡? carrot? ?낅젰媛믩쭔
  二쇱엯. jerk_factor媛 personality/myDrivingMode???곕룞(0.5~1.0)?⑥쓣 ?뺤씤, TFollowGap
  ?좏깮怨??쇨??섍쾶 ?ㅺ퀎?섏뼱 ?덉쓬???뺤씤
- 醫낅갑???꾩껜 泥닿퀎(LongControl PID ??v_cruise ?곹븳 ??MPC obstacle/肄붿뒪?????≪텛?먯씠??
  醫낇빀 ?ㅼ씠?닿렇?⑥쑝濡?FINDINGS.md???뺣━
- 醫낅갑??肄붾뱶 遺꾩꽍 1?④퀎(4李?5李?瑜??ш린??留덈Т由ы븯湲곕줈 寃곗젙. ?ㅼ쓬 ?④퀎???ㅼ감二쇳뻾 ??  route 濡쒓렇 ?앹꽦 ??濡쒓렇遺꾩꽍
- FINDINGS.md, PARAMS_REGISTRY.md, LAST_ANALYZED.md, CURRENT_STATUS.md, HANDOFF.md 媛깆떊
- 肄붾뱶 蹂寃??놁쓬 (遺꾩꽍/湲곕줉留?, carrot-ryu??carrot-wip怨??ъ쟾???숈씪
- ?ㅼ감 寃利? 誘몄떎??
## 5李?(?꾨즺 ??route 媛먯냽 泥댁씤 + T_FOLLOW/TFollowGap 泥댁씤 遺꾩꽍) ??醫낅갑??媛먯냽 濡쒖쭅 怨꾩냽

- ?ъ슜??諛⑺뼢: "醫낅갑??愿??肄붾뱶遺??遺꾩꽍 ???ㅼ감二쇳뻾 ??濡쒓렇遺꾩꽍" ?쒖꽌濡?吏꾪뻾?섍린濡?寃곗젙
- route(寃쎈줈) 湲곕컲 而ㅻ툕 媛먯냽 泥댁씤 ?꾩껜 異붿쟻:
  carrot_man.py(carrot_navi_route, GPS ?대━?쇱씤?믨끝瑜졻넂?띾룄) ??carrot_serv.py(update_navi,
  speed_n_sources 理쒖넖媛??좏깮) ??carrot_functions.py(_update_carrot_man, v_cruise_kph 媛깆떊) ??  longitudinal_planner.py ??MPC v_cruise ?곹븳 ???ㅼ젣 媛먯냽 紐낅졊源뚯? ?댁뼱吏먯쓣 ?뺤씤 (?쒖떆 ?꾩슜???꾨떂)
- ?쒖꽦???꾩젣議곌굔 ?뺤씤: TurnSpeedControlMode>=2 ?꾩슂(湲곕낯媛믪? 1=鍮꾩쟾留?, ???대퉬 ?깆쓽
  APN ?곌껐濡?寃쎈줈 ?대━?쇱씤 ?섏떊 ?꾩슂, shapely ?쇱씠釉뚮윭由??꾩슂
- ????李⑤웾???ㅼ젣 ??κ컪? TurnSpeedControlMode=2濡? route 媛먯냽??耳쒖졇 ?덈뒗 ?곹깭?꾩쓣
  params_backup-4.json?먯꽌 ?뺤씤 (DisableDM=2泥섎읆 "?ㅼ젙? 耳쒖졇?덈뒗???섎룄 誘명솗?? ?⑦꽩)
- T_FOLLOW/TFollowGap(李④컙嫄곕━) 泥댁씤 ?꾩껜 異붿쟻:
  t_follow.py(?ы띁) ??carrot_functions.py(_get_base_t_follow ~ get_T_FOLLOW, personality蹂?  湲곕낯媛??띾룄蹂댁젙/媛먯냽???ъ쑀嫄곕━ boost&hold/?대┰/?⑦봽) ??long_mpc.py(t_follow ??  desired_follow_distance ??MPC 由щ뱶李??μ븷臾??쒖빟)濡??ㅼ젣 異붿쥌嫄곕━ ?쒖뼱??諛섏쁺?⑥쓣 ?뺤씤
- ??李⑤웾? EnableSpeedTF=0, LeadAccelResponse=0?쇰줈 媛???⑥닚??personality 怨좎젙媛?  紐⑤뱶濡??댁슜 以묒엫???뺤씤 (TFollowGap1~4=110/120/140/160, ?쒖? 踰붿쐞 ???댁긽 ?놁쓬)
- ?뺤쟻 遺꾩꽍 湲곗? 踰꾧렇??諛쒓껄?섏? ?딆쓬(?곹깭 蹂??珥덇린?? ?대┰/?⑦봽 濡쒖쭅 紐⑤몢 ?덉쟾?섍쾶 ?묒꽦??
- FINDINGS.md, PARAMS_REGISTRY.md, LAST_ANALYZED.md 媛깆떊
- 肄붾뱶 蹂寃??놁쓬 (遺꾩꽍/湲곕줉留?, carrot-ryu??carrot-wip怨??ъ쟾???숈씪
- ?ㅼ감 寃利? 誘몄떎??
## 4李?怨꾩냽 (?꾨즺 ??DisableDM / LateralTorqueCustom 遺꾩꽍) ??蹂대쪟?덈뜕 ????ぉ ?뺤씤

- 媛숈? ?몄뀡?먯꽌 ?댁뼱??"DisableDM=2 / LateralTorqueCustom" 蹂대쪟 ??ぉ 遺꾩꽍 吏꾪뻾
- DisableDM=2 ?뺤씤: carrot_settings.json ?ㅻ챸("1.DisableDM, 2: +EnableWebRTC")怨?  process_config.py/selfdrived.py/controlsd.py 肄붾뱶濡??섎? ?뺤젙
  ???댁쟾??紐⑤땲?곕쭅(議몄쓬/二쇱쓽遺꾩궛 媛먯?쨌寃쎄퀬쨌媛뺤젣媛먯냽) ?꾩쟾 OFF + Carrot Vision WebRTC ?쒖꽦??  ???덉쟾 愿???ㅼ젙?대씪 ?ъ슜?먯뿉寃??섎룄 ?щ? ?ы솗???꾩슂 (?ㅼ쓬 ?몄뀡 ?먮뒗 吏湲??뺤씤)
- LateralTorqueCustom=0 ?뺤씤: latcontrol_torque.py 遺꾧린 援ъ“??0?대㈃ ??λ맂
  LateralTorqueKf/Friction/AccelFactor/KiV/KpV/Kd 媛믪씠 ?꾪? ?쏀엳吏 ?딆쓬.
  ?ㅼ젣濡쒕뒗 opendbc torque_data/params.toml??HYUNDAI_GENESIS ?ㅼ륫媛?  (LAT_ACCEL_FACTOR??.7808, FRICTION??.0984)濡?議고뼢 ?좏겕 怨꾩궛 以묒엫???뺤씤
- FINDINGS.md, PARAMS_REGISTRY.md 媛깆떊
- 肄붾뱶 蹂寃??놁쓬 (遺꾩꽍/湲곕줉留?
- ?ㅼ감 寃利? 誘몄떎??
## 4李?(?꾨즺 ??醫낅갑??PID 寃뚯씤 怨좎젙 ?뺤씤) ??LongTuningKpV/KiV/Kf 臾댄슚??諛쒓껄

- ?ъ슜???붿껌?쇰줈 "醫낅갑???쒖뼱(媛媛먯냽) 濡쒖쭅 遺꾩꽍" 李⑹닔
  (DisableDM=2 / LateralTorqueCustom ??ぉ? ?대쾲 ?몄뀡?먯꽌 蹂대쪟)
- longcontrol.py 遺꾩꽍 以? 而ㅻ컠 a26b108d(2026-09-04)?먯꽌 ?꾨?쨌湲곗븘쨌?쒕꽕?쒖뒪 李⑤웾??  醫낅갑??PID 寃뚯씤(Kp/Ki/Kf)??肄붾뱶??怨좎젙(1.0/0.0/1.0)?섏뼱 ?덉쓬???뺤씤
- ?ъ슜?먭? 蹂댁쑀??LongTuningKpV=100/KiV=0/Kf=100 ?ㅼ젙媛믪? ?쒕꽕?쒖뒪 DH 2015?먯꽌
  ?ㅼ젣濡쒕뒗 ?쏀엳吏 ?딄퀬 臾댁떆??(臾몄꽌?먮룄 紐낆떆???섎룄???숈옉, 踰꾧렇 ?꾨떂)
- ?ㅼ젣 ?곸슜?섎뒗 醫낅갑???몃툕??LongActuatorDelay / VEgoStopping / StoppingAccel 肉먯엫???뺤씤
- ACCEL_MIN/MAX(-4.0/2.5 m/s짼)???쒕꽕?쒖뒪 ?꾩슜 媛??놁씠 Hyundai 怨꾩뿴 怨듯넻媛믪엫???뺤씤
- FINDINGS.md, PARAMS_REGISTRY.md, LAST_ANALYZED.md??諛섏쁺
- 肄붾뱶 蹂寃??놁쓬 (遺꾩꽍/湲곕줉留?, carrot-ryu??carrot-wip怨??ъ쟾???숈씪
- ?ㅼ감 寃利? 誘몄떎??
## 3李?(?꾨즺 ???뚮씪誘명꽣 踰좎씠?ㅻ씪??湲곕줉) ???꾩옱 ?곸슜 ?ㅼ젙媛??ㅻ깄??
- ?ъ슜?먭? 肄ㅻ쭏 ?붾컮?댁뒪?먯꽌 export??params_backup-4.json ?섎졊
- CarSelected3="Hyundai Genesis 2015-16"濡?李⑤웾 留ㅼ묶 ?뺤씤
- DisableMinSteerSpeed=1???ㅼ젣濡??곸슜?섏뼱 ?덉쓬???뺤씤 (2李?FINDINGS? ?쇱튂)
- ?먮낯 ?뚯씪??devnotes/params_snapshots/2026-09-12_params_backup-4.json?쇰줈 蹂닿?
- PARAMS_REGISTRY.md??二쇱슂 而ㅼ뒪? 媛?議고뼢 ?좏겕, 醫낅갑???쒕떇, ?щ（利??꾨줈?뚯씪 ?? ?붿빟 湲곕줉
- DisableDM=2, LateralTorqueCustom=0 ???섎? 誘명솗????ぉ???ㅼ쓬 遺꾩꽍 ?꾨낫濡??깅줉
- ?ㅼ감 寃利? ?대떦 ?놁쓬 (湲곕줉 ?묒뾽)

## 2李?(?꾨즺 ????띿“???쒗븳 遺꾩꽍) ??minSteerSpeed / SMDPS

- CAR.HYUNDAI_GENESIS minSteerSpeed=60km/h ?섎뱶肄붾뵫 ?뺤씤
- DisableMinSteerSpeed Params ?좉???carrot-wip???대? 援ы쁽?섏뼱 ?덉쓬???뺤씤
  (interfaces.py + carrot_settings.json UI ?몄텧)
- 肄붾뱶 ?섏젙 ?놁씠 ?ㅼ젙媛?蹂寃쎈쭔?쇰줈 ?닿껐 媛???먮떒
- ?ㅼ감 寃利? 誘몄떎??
## 1李?(?꾨즺 ??釉뚮옖移??명똿) ???꾨줈?앺듃 援ъ“ 珥덇린??
- carrot-wip: ?먮낯 李멸퀬 釉뚮옖移??뺤씤
- carrot-ryu: carrot-wip?먯꽌 遺꾧린?섏뿬 ?앹꽦
- carrot-ryu-note: orphan 釉뚮옖移섎줈 ?앹꽦, devnotes ?대뜑 援ъ“ ?명똿
- ?ㅼ감 寃利? 誘몄떎??
