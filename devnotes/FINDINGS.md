# FINDINGS


## 2026-09-15 (38차) -- raw.githubusercontent.com 브랜치-head 캐시 지연 재현(핵심 발견 21 재확인) 및 실기기 검증 상세 근거

**배경**: 37차 코드/devnotes push 직후, carrot-ryu-note 브랜치-head raw URL(`raw.githubusercontent.com/.../carrot-ryu-note/devnotes/HANDOFF.md`)로 HANDOFF.md/CURRENT_STATUS.md를 재조회했더니 37차 이전(36차) 내용이 그대로 반환됨. commit-pinned raw URL(`raw.githubusercontent.com/.../4b28547/devnotes/HANDOFF.md`)로 같은 파일을 다시 조회하자 37차 내용이 정상 확인됨 -- 33차에서 발견된 캐시 지연 현상(핵심 발견 21)이 이번에도 동일하게 재현됨. commit diff 엔드포인트는 두 경우 모두 정확했음. 향후에도 push 직후 devnotes 재조회 시에는 commit-pinned raw URL 또는 commit diff 엔드포인트를 우선 사용할 것.

**실기기 검증 상세 근거(38차)**: 사용자 제보 스크린샷 9장을 이미지별로 대조.
- 이미지1(온로드 HUD 14:47:37): 경로안내 박스 정상 표시, 도착 텍스트-회전아이콘 겹침 없음(34차 목표 1 달성 확인). 도로명 "대덕대로989번길"은 박스 바깥쪽 하단에 IP 주소와 같은 줄로 표시 -- 34차 WIP 기록("박스 안쪽, 신호과속과 같은 줄")과 정확히 일치하는지는 신호과속 배지 부재로 판단 보류.
- 이미지2~4(대시캠 탭 로그 전송 플로우): "로그 전송" 확인 다이얼로그 라벨이 "구글 드라이브"로 정상 표시(36차 라벨 버그 수정 확인), 전송 결과 "완료 1/1" 정상.
- 이미지5(화면녹화 탭): "화면녹화 기록이 없습니다" -- 36차 업로드 UI(체크박스 등) 테스트 대상 부재, 스크린샷(.png) "사진" 스트립만 존재.
- 이미지6(도구 탭): Git Commands/User System 메뉴 -- 이번 검증 항목과 직접 관련 없음(참고용으로 함께 제출된 것으로 보임).
- 이미지7(화면녹화 탭 햄버거 메뉴): "로그 메뉴"에 정렬 옵션만 존재, "최근 로그 업로드" 섹션 없음 -- 36차 탭 분기 수정 확인.
- 이미지8(구글드라이브 앱 내 드라이브): "CarrotWeb Logs" 폴더 1개만 존재.
- 이미지9(CarrotWeb Logs 폴더 내부): 파일 3개(HYUNDAI_GENESIS_541384... 14:52, tmux_HYUNDAI_GENESIS_... 14:50, tmux_HYUNDAI_GENESIS_... 14:48) -- 모두 같은 폴더에 위치. 다만 시간 간격(수 분)으로 인해 37차 락이 방어 대상으로 삼는 "거의 동시 호출" 레이스의 직접 재현은 아니며, tmux 항목 2건은 carrot_man.py의 send_tmux_web()(37차 FINDINGS에서 언급된 별도 프로세스 경로)에서 발생한 것으로 추정됨 -- 즉 이번 관찰은 오히려 "락이 보호하지 못하는 프로세스 경계를 넘나드는 호출들도 결과적으로 폴더가 겹치지 않았다"는 정황이며, 동시성 레이스 자체를 테스트한 것은 아님(원인 확정 아님, 추정).
## 2026-09-15 (37차) -- Drive 폴더 2개 생성(핵심 발견 23 증상 4) 원인 확정: _ensure_folder() TOCTOU 레이스 컨디션

**배경**: 35차에서 사용자가 Google Drive "내 드라이브"에 "CarrotWeb Logs" 폴더가 2개 생성된 것을 스크린샷으로 제보(증상 4). 당시 코드 조사로 `_ensure_folder()`의 300초 캐시와 이름검색/자동생성 흐름을 확인했으나, "300초 이상 간격" 또는 "Drive Files.list의 eventual consistency 지연" 중 어느 쪽이 실제 원인인지는 호출 시각을 알 수 없어 확정하지 못하고 "우선순위 낮음, 미확정"으로 이월했음.

**원인 확정**: `gdrive_upload.py`(294~331행, 37차 수정 전 기준) `_ensure_folder()`의 순서는 다음과 같음.
```
① cache_age/cached_id 확인 -> 캐시 유효하면 즉시 반환
② (캐시 미스) Drive Files.list(name='CarrotWeb Logs')로 검색  <- 여기서 API 왕복 대기
③ 검색 결과 없으면 Files.create()로 새 폴더 생성            <- 여기서도 API 왕복 대기
④ 생성/검색된 id를 _folder_verified_cache에 기록
```
①~④ 사이에 어떤 형태의 락(lock)도 없음. 즉 두 호출이 ①을 거의 동시에 통과하면(둘 다 캐시 미스), 첫 호출이 아직 ②~③의 API 왕복(보통 수백ms)을 끝내지 못한 상태에서 두 번째 호출도 ②를 실행하게 되고, 이 시점엔 아직 폴더가 존재하지 않으므로 두 호출 모두 files.list에서 빈 배열을 받아 각자 ③에서 폴더를 생성함. 즉 300초 캐시 만료나 Drive API의 eventual consistency와는 무관하게, **캐시가 채워지기 전의 좁은 레이스 윈도우**만으로 재현 가능한 결정론적 버그임.

**두 호출이 실제로 어떻게 겹쳤는가**: 35차 증상 1(대시캠 탭 개별/그룹 전송)과 증상 3(햄버거 메뉴 "최근 로그 업로드")은 둘 다 `server/features/dashcam/upload_jobs.py`의 `run_upload_segments()`를 거쳐 `gdrive_upload.upload_file_resumable()` -> `_ensure_folder()`를 호출하며, 각 요청은 `asyncio.create_task(run_job(job))`(upload_jobs.py:315)로 서로 독립된 백그라운드 job이 됨. 두 UI 요소(대시캠 탭 전송 버튼, 전역 햄버거 메뉴)는 서로를 비활성화하지 않으므로, 사용자가 짧은 시간 안에 둘 다 눌렀다면(35차 세션에서 여러 증상을 연달아 테스트하던 정황과 부합) 두 job이 겹쳐 실행되며 위 레이스가 그대로 발생할 수 있음.

**재현 및 수정 검증(목 테스트)**: 실제 aiohttp/Drive API 없이, `session.get`/`session.post`를 50ms 지연 후 응답하는 가짜 객체로 교체하고 `asyncio.gather`로 `_ensure_folder()`를 동시에 2번 호출하는 스크립트를 작성해 실행함.
- 수정 전 코드(GitHub 현재 버전, commit 0835b059 기준): 폴더 생성 API가 2번 호출됨(`create_calls: ['CarrotWeb Logs', 'CarrotWeb Logs']`) -- 버그 재현 성공.
- 수정 후 코드(37차, `_folder_lock` 추가): 폴더 생성 API가 1번만 호출되고(`create_calls: ['CarrotWeb Logs']`), 두 호출 모두 동일한 folder_id를 반환함 -- 수정 확인.
이 테스트는 aiohttp/openpilot.common.params 등 외부 의존성을 최소 스텁으로 대체한 것으로, 실제 Google Drive API나 실기기 환경을 사용하지 않았다는 한계가 있음(정적/목 검증 수준, 실차 검증 아님).

**수정**: `gdrive_upload.py`에 모듈 레벨 `_folder_lock = asyncio.Lock()`을 추가하고, `_ensure_folder()`의 캐시확인~검색~생성~캐시기록 전체를 `async with _folder_lock:`으로 감쌈(문자열 블록 치환, 20차 기본 방식).

**남은 한계(의도적으로 범위 밖, 사용자 승인)**: `carrot_man.py`의 `send_tmux_web()`(945행)은 웹서버(`server/app.py`)와 별도 프로세스에서 `asyncio.run()`으로 실행됨. 프로세스가 다르면 `_folder_lock`과 `_folder_verified_cache` 모두 프로세스별로 독립된 메모리이므로, 이번 수정으로는 "웹서버 쪽 업로드"와 "carrot_man.py의 tmux 진단정보 전송"이 우연히 겹치는 교차 프로세스 레이스까지는 막지 못함. 근본 해결책은 최초 생성된 folder_id를 `CarrotGDriveFolderId` 같은 신규 Params 키에 영구 저장해 두 프로세스가 공유하는 방식(22차에 등록한 Client ID/Secret/RefreshToken과 동일 패턴)이며, 사용자와 논의 후 이번 세션에서는 최소 수정(인프로세스 락)만 반영하기로 확정함. 근본 수정이 필요해지면(예: 실기기에서 폴더가 다시 중복 생성되는 사례가 재현되면) 이 옵션을 재검토할 것.

**교훈**: "추정, 미확정"으로 이월했던 항목도 실제 코드의 동시성 구조(락 유무, 호출 경로가 별도 asyncio task로 갈라지는지)를 직접 추적하면 결정론적으로 확정할 수 있는 경우가 있음. 특히 Google API의 "eventual consistency"처럼 외부 요인으로 돌리기 쉬운 증상일수록, 자체 코드에 동시성 제어가 있는지부터 먼저 확인할 가치가 있음.
## 2026-09-15 (35차) -- Drive 업로드 관련 실기기 이슈 3건 원인 특정 + 화면녹화 탭 신규 스펙 확정

**배경**: 32차(drive.file+폴더자동생성)가 실기기에서 실제로 동작해 Drive 연결 자체는 성공했다고 사용자가 확인함(핵심 발견 20 이후 첫 실기기 결과). 다만 사용자가 스크린샷 3장 + Drive 폴더 중복 스크린샷으로 예상 밖의 동작 4가지를 제보.

**증상 1 (당근서버 라벨)**: 대시캠 탭에서 로그 전송(1세그먼트/10.8MB, 5세그먼트/51.5MB) 다이얼로그에 "당근서버"라는 라벨이 표시됨. 사용자 확인: 실제 전송을 누르면 Drive로 정상 전송됨(기능은 정상, 표시만 오류).

**원인 1**: `web/src/features/logs/dashcam.js` `dashcamUploadConfirmHtml()`(1260~1293행) 중 targetLabel 결정 로직(1277~1279행)이 `"toss"` 케이스만 분기하고 `"gdrive"` 분기가 없어 else로 떨어져 `web_log_upload_target_carrot`("당근서버")를 반환함. `web/js/translations/ko.js` 580~582행에 `web_log_upload_target_carrot`/`_toss`/`_gdrive` 세 키가 모두 이미 정의돼 있어(578~582행), gdrive 분기 추가만으로 해결 가능. en.js에도 대응 키 존재 확인(다국어 영향 없음).

**증상 2 (화면녹화 탭에 선택/전송 버튼 없음)**: 사용자가 화면녹화 탭 화면을 보고 직접 확인, "화면녹화 화면에서는 선택과 전송 버튼이 없음"이라고 제보.

**원인 2**: `web/src/features/logs/screenrecord.js`(영상 목록, 285줄 전체)와 `screenshots.js`(사진 스트립, 107줄 전체)를 각각 전체 검토한 결과 selection state, 체크박스 마크업, 업로드 호출이 코드에 전혀 존재하지 않음(재생/다운로드 관련 액션만 `data-action="play-screenrecord"`, `data-action="download-screenrecord"`, `data-action="view-screenshot"`). `server/features/screenrecord/routes.py`도 `register()`에 등록된 엔드포인트가 videos/thumbnail/video/download/photos/photo류의 조회·다운로드뿐, 업로드 엔드포인트 없음. 즉 버그가 아니라 애초에 미구현.

**증상 3 (화면녹화 탭에서 햄버거 메뉴로 "전송"을 눌렀는데 대시캠 로그가 감)**: 사용자가 화면녹화 탭에서 상단 우측 햄버거(줄 3개) 버튼을 누르면 전송 메뉴가 뜬다고 제보. 그런데 실제 전송된 내용은 이미지1·2에서 확인된 것처럼 qcamera/rlog(대시캠 세그먼트 구성 파일)였음 -- 화면녹화 영상 파일이 아님.

**원인 3**: `runtime.js`의 `logsMenuButton`/`openLogsMenu()`/`logsMenuChoices()`(112~178행)는 대시캠/화면녹화 탭이 아니라 로그 페이지 전체에 걸쳐 있는 전역 버튼이며, 탭 상태를 전혀 참조하지 않음. 메뉴의 "최근 로그 업로드(2/5/10)" 항목은 `LOGS_MENU_UPLOAD` 액션으로 `dashcam.js`의 `uploadRecentDashcamSegments(count)`(1770~1787행)를 호출하고, 이 함수는 `/api/dashcam/recent`로 대시캠 세그먼트만 가져와 `uploadDashcamSegments()`로 넘김 -- 화면녹화 탭에서 열었는지 여부와 무관하게 항상 대시캠 로그만 업로드함. 사용자가 화면녹화 탭에서 이 메뉴로 "전송"한 것이 실제로는 최근 대시캠 로그 업로드였던 것으로 설명됨.

**증상 4 (Drive에 "CarrotWeb Logs" 폴더 2개 생성)**: 사용자가 Google Drive "내 드라이브"에서 동일한 이름의 폴더가 2개 생성된 것을 스크린샷으로 확인.

**원인 4 (추정, 미확정)**: `gdrive_upload.py`의 `_ensure_folder()`(294~331행)는 이름으로 Drive에 질의해 있으면 재사용, 없으면 생성하며, 결과를 인메모리 `_folder_verified_cache`에 300초간만 캐싱함(298~301행). 증상 1(대시캠 탭 개별/그룹 전송)과 증상 3(햄버거 메뉴 "최근 로그 업로드")이 서로 다른 시점에 각각 이 함수를 호출했을 것으로 보이며, (a) 두 호출 사이 300초 이상 간격이 있었거나 (b) Drive Files.list API가 방금 생성된 폴더를 검색 결과에 즉시 반영하지 못하는 잘 알려진 지연(eventual consistency)에 걸렸을 가능성이 유력함. 다만 코드 조사만으로는 실제 호출 시각을 알 수 없어 확정 불가 -- 우선순위 낮음으로 이월(기능 동작 자체에는 지장 없고, 사용자가 Drive에서 폴더 하나를 수동 정리 가능).

**사용자 확정 스펙 (다음 세션 최우선 작업)**: 화면녹화 탭에 (1) 영상목록을 실제로 노출하고, (2) 각 항목 파일명(저장시간 포함) 앞 체크박스 + 뒤 다운로드/전송 버튼, (3) 목록 상단 전체선택 버튼 + 다운로드/전송 버튼을 신규 구현. `dashcam.js`의 기존 선택 UI/업로드 확인 다이얼로그 패턴을 그대로 재사용하는 방향으로 설계할 것(증상 1의 targetLabel 버그도 이 참에 함께 수정 권장). 백엔드에는 화면녹화 업로드 엔드포인트가 없으므로 `gdrive_upload.py`의 `upload_file_resumable()`을 재사용해 신규 추가 필요.

**교훈**: 32차 이후 처음으로 실기기 검증 결과가 들어왔는데, 정적 코드 리뷰만으로 예측했던 것과 달리 UI 요소(햄버거 메뉴)가 탭 경계를 넘어 다른 데이터를 조작하는 설계상 허점이 실사용 중 자연스럽게 드러남. 향후 유사한 "탭별 격리"가 필요한 UI를 검토할 때는 전역 컨트롤(페이지 상단 고정 버튼 등)이 실제로 활성 탭을 인지하는지 별도로 확인할 것.
## 2026-09-15 (34차) -- 세션 시작 시 확인한 회차(32차)와 실제 최신 회차(33차) 사이 불일치 재확인

**증상**: 세션 시작 시 4절 절차로 HANDOFF/CURRENT_STATUS를 조회했을 때는 32차(c704371a)까지만 반영된 상태였으나, 사용자가 실제 실행한 push 로그(`789667f7..9fdefb3d`)를 보니 부모 커밋이 `789667f7`로, 그 사이 다른 경로에서 33차(ko.js 문구 수정)가 이미 진행되어 있었음.

**원인**: 사용자가 반영 스크립트를 실행하는 시점까지 시간차가 있고, 그 사이 다른 세션/경로에서 병행 작업이 있었던 것으로 추정. 스크립트 자체는 실행 시점에 항상 최신 브랜치를 clone하므로(6절), 코드 자체는 최신 위에 정상적으로 쌓였고 충돌도 없었음 -- 다만 Claude가 작업 도중 사용하던 세션 번호 라벨(`[33차]`, 코드 주석/커밋 메시지)이 실제 순서와 어긋나게 됨.

**영향**: 코드 로직/반영 자체에는 문제 없음(정상적으로 33차 위에 34차 커밋이 쌓임). devnotes 회차 번호 표기만 실제 순서(34차)로 바로잡아 기록. 이미 커밋된 코드 주석의 `[33차]` 표기는 과거 기록이므로 임의로 재작성하지 않음(18절 원칙과 동일하게 취급).

**교훈**: Base Commit 원칙(6절)에서 "스크립트 작성과 실행 사이 시간차 동안 다른 경로로 파일이 바뀔 수 있다"고 이미 경고하고 있던 상황이 실제로 재현됨. 코드 파일처럼 내용이 겹치는 변경뿐 아니라, devnotes 회차 번호 같은 "순서" 자체도 이 시간차의 영향을 받을 수 있음이 확인됨. 반영 완료 로그를 받으면, 커밋 해시 앞부분(`OLD..NEW`)의 OLD가 세션 시작 시 확인했던 HEAD와 다를 경우 그 사이 무엇이 반영됐는지 먼저 확인하는 절차를 권장.
## 2026-09-15 (33차) -- raw.githubusercontent.com이 쿼리스트링 캐시버스터를 무시하고 이전 내용을 반환하는 현상 관찰

**증상**: 33차 ko.js 수정 커밋(`789667f7`)이 GitHub에 정상 push된 것을 `git push` 로그와 `github.com/.../commit/<sha>.diff`로 확인했음에도, 같은 파일을 `raw.githubusercontent.com/.../carrot-ryu/.../ko.js?nocache=<timestamp>` 형태로 재조회하면 한동안 여전히 수정 전 텍스트("데스크톱 앱 유형")가 반환됨.

**추정 원인**: `raw.githubusercontent.com`은 Fastly CDN을 경유하며, 커밋 반영 직후 일정 시간 동안 이전 응답을 계속 서빙하는 것으로 보임. 20차·22차 세션에서도 유사하게 "이전 버전이 캐시되어 있었다"는 사례가 있었으나, 이번엔 `nocache` 쿼리스트링을 붙였음에도 재현됨 -- 즉 쿼리스트링 캐시버스터가 이 CDN에는 효과가 없거나 제한적임을 시사.

**임시 대응(이번 세션)**: `github.com/<owner>/<repo>/commit/<sha>.diff` 엔드포인트(git 커밋 자체를 직접 반영하므로 캐시 지연이 없는 것으로 관찰됨)로 교차 검증해 실제 반영을 확정함. `api.github.com` contents API도 대안이 될 수 있으나 이번 세션 중 비인증 rate limit(60/시간)에 걸려 사용 불가했음.

**제안(19절 절차 대상, 아직 미승인)**: 16절/20절의 "raw.githubusercontent.com 재조회로 확인" 절차에 "즉시 재조회 시 캐시로 이전 내용이 보일 수 있으므로, 그 경우 `github.com/.../commit/<sha>.diff`로 교차 검증 후 판단할 것 -- 캐시된 이전 내용만 보고 곧바로 '미반영'으로 단정하지 않는다"는 단서 추가를 다음 세션에 사용자에게 제안할 수 있음. 이번 세션에서는 코드 변경이 아니므로 제안만 기록하고 문서 자체는 수정하지 않음.
## 2026-09-15 (32차) -- drive.file 스코프 + 폴더 자동생성 복귀로 31차 근본 원인(핵심 발견 19) 우회 반영

**배경**: 31차(핵심 발견 19)에서 Google Device Authorization Grant가 전체 drive 스코프를 정책적으로 차단한다는 근본 원인이 확인되어, 사용자에게 3가지 대안(① drive.file+폴더자동생성 복귀, ② Authorization Code Flow 전면 재설계, ③ Drive 대체)을 제시하고 결정을 기다리는 상태로 세션이 종료됨.

**진행**: 커밋 `c704371a`(메시지에 `31cha device-flow block fix`로 명시)로 대안 ①이 선택·반영됨을 이번 세션에서 GitHub 커밋 로그/diff 직접 조회로 확인함. `gdrive_upload.py`의 스코프를 `drive` -> `drive.file`로 좁히고, 고정 `DRIVE_FOLDER_ID` 접근 방식을 c3-ms-dev 원본과 동일한 "이름으로 폴더 검색, 없으면 자동생성"(`_ensure_folder`) 방식으로 되돌림.

**미해결/주의**:
1. 이 변경 자체가 실제로 device flow에서 정상 동작하는지(31차에서 겪은 `Invalid device flow scope` 에러가 실제로 사라지는지)는 아직 실기기로 검증되지 않음 -- drive.file 스코프가 device flow에서 허용된다는 것은 외부 사례 기반 추정이었지 이 프로젝트에서 직접 확인된 사실은 아님(31차 FINDINGS 단서 참고).
2. 기존에 사용자가 미리 만들어둔 폴더(구 DRIVE_FOLDER_ID)는 더 이상 쓰이지 않고, 앱이 "CarrotWeb Logs"라는 새 폴더를 자동으로 만들게 되므로, 기존 폴더에 쌓여있던 파일과 새 폴더가 분리됨(필요시 사용자가 수동으로 옮겨야 함 -- devnotes에는 이 이관에 대한 언급이나 조치가 없음, 다음 세션에서 사용자에게 안내 필요).
3. 이번 커밋에 대한 세션별 WIP/HANDOFF 기록이 남아있지 않아, 실제로 어떤 경로(세션/스크립트/직접 웹 편집)로 이 커밋이 만들어졌는지는 devnotes만으로는 알 수 없음 -- 다음에 유사한 "기록 없는 반영"이 발견되면 16절 원칙대로 우선 GitHub 실제 상태를 기준으로 진행.
## 2026-09-15 (31차) -- Google Drive 연동(15차~) 설계가 Device Authorization Grant의 스코프 제약과 근본적으로 충돌함

**증상**: 실기기에서 "웹 설정 > 로그 업로드" 화면의 Google Drive 연결(Device Authorization Grant, gdrive_upload.py)이 클라이언트 ID/보안 비밀번호를 올바르게 입력하고 클라이언트 유형(TV 및 제한된 입력이 있는 기기)과 동의 화면 스코프 등록까지 정상인 상태에서도 "Invalid device flow scope: https://www.googleapis.com/auth/drive" 에러로 항상 실패함.

**조사 경과**: (1) 클라이언트 ID 형식 문제 -> 배제(재입력 후에도 동일), (2) UI 안내 문구(ko.js)가 요구 클라이언트 유형("데스크톱 앱 유형")을 실제 요구사항("TV 및 제한된 입력이 있는 기기")과 다르게 안내하는 버그 발견했으나 -> 사용자가 이미 올바른 유형으로 발급받아 적용했다고 확인되어 배제, (3) 동의 화면 스코프 미등록 -> 사용자 확인으로 배제.

**확정 원인**: 코드 조사가 아닌 외부 사례 조사로 확인됨 -- Google은 OAuth 2.0 Device Authorization Grant(RFC 8628, "TV 및 제한된 입력이 있는 기기" 흐름)에서 전체 Google Drive 스코프(https://www.googleapis.com/auth/drive)의 사용을 수년 전부터 정책적으로 차단하고 있음. 이는 클라이언트 유형/동의 화면 설정과 무관하게 Google 인증서버 단에서 스코프 자체를 거부하는 것으로, 사용자 측 설정으로는 우회 불가능함. (Calendar 등 다른 API 스코프는 동일 device flow에서 정상 동작하는 것으로 보아, Drive 전체 스코프 특유의 제약으로 판단. 다만 Google 공식 문서에서 이 제약을 명시적으로 문서화한 출처는 못 찾았고, 다수의 독립적인 개발자 보고 사례로 확인한 것임 -- 완전히 공식적으로 확정된 사실은 아니라는 점은 유의.)

**설계 충돌**: gdrive_upload.py(15차)는 c3-ms-dev 원본의 drive.file(비민감) 스코프 + _ensure_folder()(폴더 자동 생성) 방식을, "이미 만들어둔 고정 폴더(DRIVE_FOLDER_ID)에 ID로 바로 접근"하기 위해 의도적으로 전체 drive 스코프 + _verify_folder()(존재 확인만) 방식으로 변경했음(코드 주석에 사유 명시). 이 변경이 이번에 확인된 Google의 device flow 스코프 제약과 정면으로 충돌하는 조합이었던 것으로 보이며, 15차 시점에는 이 제약이 검증되지 않은 채 설계에 반영된 것으로 추정됨.

**미해결(다음 세션 결정 필요)**: 사용자에게 3가지 대안 제시함 --
1. drive.file 스코프 + 폴더 자동 생성 방식(c3-ms-dev 원본)으로 복귀. Device flow 유지 가능성 높으나 실제 검증 안 됨. 기존에 미리 만들어둔 폴더 재사용 불가(앱이 새 폴더를 만들게 됨).
2. Device flow를 버리고 표준 Authorization Code Flow(콤마 기기 자체 웹서버가 redirect URI를 로컬 네트워크로 수신하는 구조)로 전면 재설계 -- 작업량 큼, LAN IP/포트 고정 문제 등 새 이슈 예상.
3. Google Drive 자체를 다른 저장 수단으로 대체.
사용자 결정 대기 중.

**부가 발견(별도 수정 필요, 이번 세션 미수정)**: web/js/translations/ko.js의 web_gdrive_client_id_desc 문구가 "Google Cloud OAuth 클라이언트 ID (데스크톱 앱 유형)"으로 돼 있으나, 실제 필요한 유형은 "TV 및 제한된 입력이 있는 기기"임(gdrive_upload.py 주석과 불일치). 이번 에러의 직접 원인은 아니었으나(사용자가 이미 올바른 유형으로 발급받음), 다른 사용자/향후 재시도 시 혼란을 줄 수 있는 명백한 버그이므로 다음 세션에서 문구 수정 필요.

## 2026-09-15 (30차) — HANDOFF.md 미반영 기록과 실제 GitHub 상태 불일치

**증상**: 29차 세션이 작성한 HANDOFF.md에는 "사용자가 코드 반영 스크립트를 아직 실행하지 않음 — 실행 전까지 이 레이아웃 변경은 GitHub에 반영된 것이 아님"이라고 명시돼 있었음. 그런데 30차 세션 시작 시 4절 절차(0~3번)를 따라 carrot-ryu 최신 커밋을 직접 조회한 결과, 29차 커밋(67a8e10)뿐 아니라 그 이후의 30차 커밋(34bb41bc)까지 이미 GitHub에 push돼 있는 상태였음. CURRENT_STATUS.md 역시 27차(5f5e49d0) 기준에서 갱신되지 않은 채 남아 있었음.

**원인 추정**: 29차 세션이 스크립트 전달까지만 하고 세션이 종료된 뒤, 사용자가 실제로 스크립트를 실행해 반영을 완료했으나, 그 반영 사실이 별도로 devnotes(HANDOFF/CURRENT_STATUS)에 기록되지 않은 채 다음 세션이 곧바로 이어서 코드를 추가로 수정(30차 커밋)한 것으로 보임 — 즉 "코드 반영"과 "devnotes 갱신"이 서로 다른 시점/세션에 이루어지면서 devnotes 갱신이 누락된 채 다음 작업이 진행된 사례.

**핵심 발견 13(24차)과의 관계**: 24차에서 이미 "devnotes 기록 누락"과 "실제 미반영" 두 상태를 구분해야 한다는 원칙이 문서화됐으나, 이번 사례는 그와 유사하되 조금 다른 변종 — devnotes가 "미반영"이라고 잘못 기록한 상태에서, 실제로는 반영이 됐을 뿐 아니라 그 위에 한 세션치 작업(30차)이 이미 더 진행돼 있던 경우. 단순히 "반영 여부"만 확인해서는 부족하고, HEAD 자체가 devnotes에 기록된 것보다 더 앞서 있을 수 있다는 점까지 확인해야 함을 보여줌.

**재발 방지**: 이미 문서화된 4절 0~3번 절차(이 지침 문서 → HANDOFF.md → CURRENT_STATUS.md → carrot-ryu 최신 commit 확인)를 매 세션 빠짐없이 순서대로 밟는 것 자체가 재발 방지책 — 특히 3번(carrot-ryu 최신 commit 확인)을 건너뛰지 않는 것이 이번처럼 devnotes 기록과 실제 GitHub 상태가 어긋난 경우를 조기에 잡아낼 수 있는 유일한 방법. 이번 건은 기존 규칙을 정상적으로 따른 결과(30차 세션이 3번 단계를 밟아 스스로 발견함) 조기에 잡힌 사례이므로, 별도의 새 규칙 추가는 필요 없다고 판단함(19절 절차 대상 아님).

## 2026-09-14 (26차) — Google Drive 연결 UI 미노출: 정적 코드 리뷰와 실기기 스크린샷이 모순됨(원인 미확정)

**증상**: 실기기 "웹 설정 > 로그 업로드"에서 업로드 서버를 "구글 드라이브"로 선택해도 Client ID/Secret 입력란(web-gdrive-connect 컴포넌트, 23차 추가)이 보이지 않고, 대신 "당근서버 주소"/"토스서버 주소" 입력란(web-upload 컴포넌트의 carrot/toss 전용 필드)이 계속 보임.

**정적 코드 리뷰 결과(carrot-ryu HEAD d338afb7 기준)**:
- schema.js의 log_upload 그룹에 web-upload / web-gdrive-connect 두 항목 모두 정상 등록.
- components.js의 web-gdrive-connect는 isVisible을 별도 정의하지 않아, WebSettingsComponents.isVisible()의 기본 폴백 로직 `(component.settingKeys || []).every(...)` 가 적용됨. settingKeys가 undefined이므로 빈 배열의 every()는 항상 true -> 이 컴포넌트는 이론상 항상 visible이어야 함.
- web-upload 컴포넌트 내부의 "당근서버 주소"/"토스서버 주소" 필드는 각각 `target === "carrot"` / `target === "toss"` 일 때만 hidden 속성이 풀리도록 구현돼 있음. 즉 target이 "gdrive"이면 이 두 필드는 코드상 반드시 숨겨져야 함.
- web/js/generated/tools.js(배포용 esbuild 번들)를 소스와 직접 대조한 결과, 위 로직이 토씨 하나 다르지 않게 동일하게 반영돼 있었음(문자열 치환/축약 없이 로직 그대로 minify됨). web/css/generated/tools.css에도 .web-gdrive-settings 관련 셀렉터가 전부 포함, 숨김 규칙 없음.

**모순**: 실기기 스크린샷은 "구글 드라이브"가 선택된 상태에서 (a) carrot/toss 필드가 보이고 (b) gdrive 전용 필드가 안 보이는, 코드와 정반대의 상태를 보여줌. 즉 정적 코드 리뷰만으로는 원인을 찾지 못함.

**가설(미검증)**:
1. 실기기 브라우저가 최신 tools.js/tools.css를 서빙받지 못하고 캐시된 구버전을 쓰고 있을 가능성 (Samsung Browser 캐시)
2. scons 빌드 과정에서 이번 코드 변경분에 대해 esbuild 번들 재생성이 실제로는 안 됐을 가능성 (과거 devnotes에 기록된 것과 유사한 유형의 문제)
3. (낮은 가능성) 서버 쪽이 별도의 오래된 정적 파일 경로를 서빙하고 있을 가능성

**검증 방법(다음 세션에서 실기기로 수행 필요)**:
- 콤마 기기 터미널 탭에서 실제 서빙되는 tools.js 파일 내용에 "web-gdrive-connect" 문자열이 존재하는지 직접 grep
- 브라우저 강제 새로고침(캐시 무시) 또는 시크릿 모드로 재접속해 동일 현상 재현 여부 확인
- (선택) tools.js 파일의 수정시각/해시가 carrot-ryu HEAD(d338afb7) 반영 이후인지 확인

**부가 발견(코드 위치 미조사)**: 화면녹화 탭의 세그먼트 "전송" 다이얼로그가 업로드 서버를 "구글 드라이브"로 선택한 상태에서도 라벨을 "당근서버"로 표시함. 실제 업로드는 gdrive로 라우팅되는 것으로 보이나(최종적으로 "Google Drive가 연결되어 있지 않습니다" 에러 발생) 라벨 텍스트가 하드코딩됐을 가능성. 다음 세션에서 조사 필요.

## [2026-09-14] web_upload.py/dashcam upload.py 데드코드 및 test_web_upload.py 낡은 테스트 의심 (25차)

### 배경
- LOG_UPLOAD_TARGETS "gdrive" 누락 버그(24차 계속2 발견) 수정을 진행하면서, 사용자가 "관련 죽은 코드도 같이 삭제"를 요청해 조사함.

### 조사 1: 처음 보고를 정정 -- web_upload.py의 UPLOAD_TARGETS/selected_upload_settings()는 살아있는 코드
- `web_upload.py`: `UPLOAD_TARGETS = {"carrot", "toss"}`, `selected_upload_settings()`는 "gdrive"를 모르고 무조건 "carrot"으로 되돌리는 것은 맞으나, 이 함수는 `carrot_man.py`의 `_tmux_toss_only()`(958줄 `send_tmux_carrot_logs`, 1054줄 `send_tmux_discord`에서 호출)가 실제로 사용 중. `_tmux_toss_only()`는 "target이 toss인지"만 판별하는데, "gdrive"가 "carrot"으로 잘못 되돌려져도 결과적으로 "toss가 아니다"는 결론은 동일해 현재 시점 실사용 동작 버그는 없음. 하지만 함수 자체는 삭제 대상이 아님.

### 조사 2: 진짜 죽은 코드 3개 확인 (프로덕션 호출자 없음, grep으로 저장소 전체 재확인)
- `web_upload.py`의 `tmux_web_target()`: `send_tmux_web()`이 17차에 Google Drive 직접 업로드로 재작성되면서 더 이상 호출하지 않음. 현재 `server/tests/test_web_upload.py`에서만 참조(489, 503, 508, 514번째 줄).
- `server/features/dashcam/upload.py`의 `resolve_upload_target()`, `upload_target_settings()`: 같은 파일 안에서도, 다른 어떤 파일에서도 프로덕션 코드가 호출하지 않음. `server/tests/test_web_upload.py`에서 `resolve_upload_target`을 최소 6곳(397, 467, 702, 747, 767, 786번째 줄)에서 monkeypatch로만 참조.
- 이 3개 함수를 지우면 `web_upload.py`의 `os` 관련 상수(DEFAULT_TMUX_WEB_UPLOAD_URL)와 `dashcam/upload.py`의 `selected_upload_settings`/`read_web_settings` import 2개도 함께 미사용이 되어 정리 대상.

### 조사 3: test_web_upload.py 자체가 16차 전환 이전 기준으로 낡아있을 가능성 (미확정, 실행 검증 못함)
- `resolve_upload_target`을 monkeypatch하는 테스트 중 397번째 줄 부근의 `test_dashcam_upload_completion_notifies_web_server_and_discord`가 `upload_jobs.upload_folder_to_web`, `upload_jobs.send_web_upload_complete`도 함께 monkeypatch함.
- 그런데 `upload_jobs.py`를 직접 확인한 결과 이 두 함수는 더 이상 존재하지 않음 -- 16차에서 세그먼트 업로드를 "세그먼트/파일별 개별 HTTP 업로드"에서 "선택된 세그먼트를 zip으로 묶어 `gdrive_upload.upload_file_resumable()`로 단일 업로드"로 전면 재작성하면서 제거된 것으로 보임(`upload_jobs.py`의 `run_upload_segments()` 함수 docstring에 "기존에는... upload_folder_to_web... 통지했다"라고 과거형으로 명시되어 있음).
- `monkeypatch.setattr(obj, name, value)`은 기본적으로 `obj`에 `name` 속성이 실존해야 성립하므로(그렇지 않으면 AttributeError), 이 테스트는 16차 이후 실행하면 이미 실패했을 가능성이 높음. 다만 이번 세션에서는 pytest를 실제로 돌려보지 못해(openpilot 전체 런타임 의존성 없이 이 테스트 파일만 단독 실행이 어려움) 확정하지 못함 -- "가능성 높음"으로만 기록.
- 이 발견이 사실이라면, `resolve_upload_target` 등 3개 함수를 단순 삭제하는 작업이 "16차 전환 이후 갱신되지 않고 방치된 테스트 뭉치 전체 정리"로 범위가 커질 수 있음.

### 결론 및 다음 조치 (사용자 결정, 미착수)
- 사용자와 협의 결과, 이번 세션은 확실한 버그(LOG_UPLOAD_TARGETS)만 수정하고, 데드코드 3개 삭제 + test_web_upload.py 정리는 다음 세션으로 이월하기로 결정.
- 다음 세션 시작 시 권장 순서: (1) test_web_upload.py를 실제로 실행해(또는 최소한 관련 픽스처/모듈 임포트만이라도) 몇 개 테스트가 실제로 깨져 있는지 먼저 정량적으로 확인 -> (2) 16차 이후 낡아진 테스트 목록 확정 -> (3) 데드코드 3개 삭제 + 대응 테스트 삭제/갱신을 한 번에 진행.

## [2026-09-14] Google Drive 연결 UI Client ID/Secret 입력란 미노출 문제 조사 (24차 계속2)

### 배경
- 23차(commit 272834b8)에서 web_settings에 Google Drive 연결 UI(web-gdrive-connect 컴포넌트)를 추가했으나, 사용자 실기기에서 "업로드 서버" 드롭다운은 "구글 드라이브"로 바뀌는데 그 아래 Client ID/Secret 입력란과 연결 버튼이 보이지 않는다고 보고됨(WIP.md 23~24차 참고).

### 조사 1: 캐싱 가설 기각
- server/features/static.py를 확인한 결과, index.html은 매 요청마다 Cache-Control: no-cache, no-store, must-revalidate로 서빙되고, 정적 자산(js/css)의 src/href는 요청마다 실제 파일 콘텐츠 해시(?v=<sha256>)로 재작성됨(_rewrite_index_asset_urls/_fingerprinted_asset_url). 브라우저 캐시가 낡은 번들을 계속 쓸 수 있는 구조가 아니며, 서비스 워커도 존재하지 않음(grep 결과 없음). 캐싱 가설은 기각.

### 조사 2: 렌더링 로직 자체는 정상 (Node.js 시뮬레이션으로 검증)
- schema.js: log_upload 그룹에 web_upload, web_gdrive_connect 두 항목이 정상 등록되어 있음(commit 272834b8 diff로 확인).
- components.js: "web-gdrive-connect" 컴포넌트는 settingKeys가 비어 있어 isVisible이 항상 true. 드롭다운 선택값(target)과 무관하게 항상 렌더링되는 별도 행으로 구현되어 있음(web-upload의 필드처럼 target별 조건부 hidden이 아님).
- 실제 소스 파일(schema.js/state.js/components.js/render.js)을 그대로 Node.js 환경에 복사해 renderWebSettingsDialogHtml()을 직접 실행한 결과:
  - "web-gdrive-settings" 포함: true
  - "web-upload-settings" 포함: true
  - data-gdrive-field="client_id" input 포함: true
  → 렌더링 함수 자체는 Client ID/Secret 입력란을 포함한 HTML을 정상적으로 생성함. 컴포넌트 등록/가시성 로직에는 문제가 없음이 실증됨.

### 조사 3: 발견한 확실한 버그 -- 백엔드가 "gdrive"를 유효한 값으로 모름
- server/services/web_settings.py: `LOG_UPLOAD_TARGETS = {"carrot", "toss"}` (20번째 줄), `_Field("log_upload_target", "enum", "carrot", choices=LOG_UPLOAD_TARGETS)`.
- 23차에서 프론트엔드 드롭다운에 value="gdrive" 옵션을 추가했으나, 백엔드 enum choices 목록은 갱신되지 않음.
- 영향: 사용자가 "구글 드라이브"를 선택해 저장을 시도하면, 백엔드가 "gdrive"를 무효한 enum 값으로 취급해 저장을 거부하거나 기본값("carrot")으로 되돌릴 가능성이 높음(state.js의 normalizeWebSettingValue도 동일하게 WEB_SPEC_BY_KEY의 choices를 기준으로 판단하므로 프론트엔드에서도 같은 문제가 재현됨). 이는 web-gdrive-connect 행의 렌더링과는 무관한 별개의 확실한 버그.
- 수정 방향(미적용, 사용자 승인 대기): LOG_UPLOAD_TARGETS에 "gdrive" 추가.

### 결론 및 남은 가설 (미확정)
- "Client ID/Secret 입력란이 안 보인다"는 증상은 코드 레벨 렌더링 버그로는 재현되지 않음.
- .web-settings-group__body{overflow:auto}로 스크롤 가능한 구조이므로, 실기기 화면에서 "업로드 서버" 드롭다운 아래로 스크롤하지 않아 못 봤을 가능성이 유력한 가설로 남음(미검증 -- 실기기에서 스크롤 확인 필요).
- LOG_UPLOAD_TARGETS 버그는 별개로 반드시 수정이 필요하며, 사용자 승인 후 반영 예정.

## [2026-09-14] Google Drive 연동 파라미터 미등록으로 인한 UnknownKeyName 실패 (22차)

### 배경
- HANDOFF 다음 작업 후보 "PARAMS_REGISTRY.md 파라미터 3종 등록"을 진행하기 위해 gdrive_upload.py(15~20차에 걸쳐 작성)의 실제 파라미터 이름을 GitHub에서 직접 조회함.

### 원인
- gdrive_upload.py는 PARAM_CLIENT_ID="CarrotGDriveClientId", PARAM_CLIENT_SECRET="CarrotGDriveClientSecret", PARAM_REFRESH_TOKEN="CarrotGDriveRefreshToken" 3개 Params 키를 사용.
- openpilot/common/params_keys.h에는 이 3개가 전혀 등록되어 있지 않았음(다른 모든 Carrot* 파라미터는 예외 없이 이 파일에 등록되어 있음, {PERSISTENT, ...} 형태).
- openpilot/common/params_pyx.pyx의 get()/put()은 호출 시 check_key()를 거치며, params_keys.h에 없는 키면 UnknownKeyName 예외를 던짐(101-102줄).
- gdrive_upload.py의 api_gdrive_device()(Drive 연결 시작 API, "연결" 버튼이 호출)는 client_id/secret을 저장하는 첫 단계(_params().put(PARAM_CLIENT_ID, client_id))에서 이 예외를 try/except로 받아 HTTP 500을 반환하도록 되어 있음. 즉 사용자가 로그탭 설정에서 "연결"을 눌러 client_id를 입력하는 순간부터 항상 실패하는 상태였음.
- api_gdrive_callback()(디바이스 코드 인증 완료 후 refresh_token 저장)도 동일하게 _params().put(PARAM_REFRESH_TOKEN, refresh_token)에서 실패하도록 되어 있어, 설령 앞 단계를 우회하더라도 최종 인증 완료 단계에서도 실패했을 것으로 추정.
- 15차부터 20차까지 6개 세션에 걸쳐 만들어진 Drive 연동 기능이 실제 기기 연결 테스트를 한 번도 거치지 않아(devnotes에 이미 "실차 검증 미실시"로 기록되어 있었음) 이 버그가 드러나지 않고 있었음.

### 적용한 수정
- openpilot/common/params_keys.h에 다른 Carrot* 파라미터와 동일한 패턴으로 3줄 추가:
  {"CarrotGDriveClientId", {PERSISTENT, STRING}},
  {"CarrotGDriveClientSecret", {PERSISTENT, STRING}},
  {"CarrotGDriveRefreshToken", {PERSISTENT, STRING}},
- 위치: 기존 CarrotExceptionDiscordWebhookUrl 줄과 CwebPushRecoveryBoot 줄 사이.
- carrot-ryu commit 48c2e081.

### 검증
- 문자열 블록 치환 스크립트 실행 로그: git commit/push 정상 완료 확인.
- raw.githubusercontent.com으로 commit 48c2e081 시점의 params_keys.h를 직접 재조회하여 3줄이 의도한 위치에 정확히 들어간 것을 확인(정적 검증 완료).
- ⚠ 미검증: 실제 Google Cloud Console에서 OAuth 클라이언트를 발급하고 콤마 기기에서 "연결"을 눌러 device flow 전체(디바이스 코드 발급 -> 사용자 인증 -> refresh_token 저장 -> 실제 업로드)가 끝까지 동작하는지는 여전히 미실시. params_keys.h 수정으로 최소한 "저장 시 예외 발생" 문제는 해소되었으나, 그 외 OAuth 흐름 자체(스코프, 리다이렉트 등)의 정합성은 정적 분석 수준으로만 확인됨.## [2026-09-13] 온로드 좌측 상단 시계 좌측 화면 경계 잘림 버그 원인규명 및 수정 (13차)

### 배경
- 사용자가 실제 화면 사진을 공유. 좌측 상단 시계가 "23:32:34" 대신
  "3:32:34"로 표시되어 맨 앞 "2"가 잘려 보임을 보고

### 원인
- openpilot/selfdrive/ui/onroad/hud_renderer.py `_draw_date_time()`:
  시계 텍스트(HH:MM:SS, 8자, font_size=100)를 align="center_bottom"으로
  그리며 고정 x=rect.x+170을 기준으로 삼음
- text_draw.py `get_text_draw_pos()`: center_bottom 정렬은
  draw_x = x - 텍스트폭*0.5로 계산 -> 8자 텍스트의 절반 폭이 170px을
  넘어 draw_x가 음수(화면 좌측 밖)가 됨
- 12차에서 시계 표시가 %H:%M(5자)에서 %H:%M:%S(8자)로 늘어나며 발생한
  회귀로 추정 (5자일 때는 절반 폭이 170px보다 작아 문제가 드러나지 않았을
  가능성)

### 적용한 수정
- measure_text_cached로 시계 텍스트 실측 폭을 구해, 왼쪽 여백
  (UI_CONFIG.border_size)을 보장하도록 x를 max(기존x, 최소x)로 보정
- _draw_date_time() 한 곳만 수정, 다른 로직/파일은 건드리지 않음
- 검증: git apply --check 통과, py_compile 통과(Claude 샌드박스).
  실차 검증은 미실시

## [2026-09-13] route 감속 오검출 근본수정 적용 — carrot_navi_route()에 3-샘플 median 스파이크 필터 (8차 발견에 대한 조치, carrot-ryu commit 2dbe492)

### 배경
- 8차 세션에서 실주행 로그(route 000003fb--8470375f65--21)로 확인한 route 커브 감속
  오검출(고속도로 분기점 조기 과감속 후 원복)에 대해, 사용자가 대응 방향으로
  "②근본수정(스파이크 제거 필터 추가)"을 선택.

### 적용한 수정
- 파일: openpilot/selfdrive/carrot/carrot_man.py, carrot_navi_route() 함수
- 기존: 3점(약 40m 간격) 곡률을 계산하자마자 바로 그 곡률값으로 목표속도(speed)를
  산출 → 폴리라인 노이즈로 곡률이 한 지점에서만 튀어도 그대로 급감속 목표로 반영됨.
- 변경: 곡률(curvature) 계산을 먼저 전부 끝낸 뒤, 그 리스트에 3-샘플 슬라이딩
  median 필터를 적용하고, 그 필터링된 곡률로만 목표속도를 산출하도록 구조 변경.
  같은 아이디어가 이미 비전 커브 쪽(curve_speed.py의 curve_speed() 함수, 
  "A three-node median rejects isolated yaw spikes" 주석 부분)에 적용되어 있어
  이를 route 쪽에도 동일하게 적용한 것.
- 최소 변경 원칙(10절)에 따라 함수 내 한 블록(원본 13줄 → 26줄)만 교체, 다른 로직은
  건드리지 않음.

### 검증 (실차 검증 아님 — 정적/합성 검증만)
- python3 -m py_compile로 문법 검증 통과 (Claude 샌드박스 및 실제 push된 commit
  2dbe492 기준 모두 확인).
- 합성 곡률 시퀀스([0.005, 0.006, 0.005, 0.007, 0.08, 0.006, ...] 형태로 index 4에
  고의로 스파이크 삽입)로 필터 동작 검증: 단발성 스파이크(0.08)가 주변 median으로
  완전히 치환되어 사라지고, 나머지 정상 구간 값은 그대로 유지됨을 확인.
- ⚠ 8차 로그(000003fb--8470375f65--21)는 실제 route 폴리라인 좌표 자체를 갖고
  있지 않아, 이번 수정이 "그 실제 사고 구간"에서 어떻게 동작했을지 재생(replay)
  검증은 하지 못함. 즉 이 수정이 8차에서 관찰된 증상을 실제로 없애는지는 아직
  실주행으로만 확인 가능.

### 실차 검증
- 미실시. 콤마 디바이스에 이 코드가 올라가 동일/유사 구간을 재주행하기 전까지는
  "고쳐졌다"고 단정하지 않음. 다음 실주행 시 동일 분기점 통과 시 desiredSource=
  "route" 전환 시점의 desiredSpeed 급락 여부를 rlog로 재확인 필요.

## [2026-09-13] route(경로) 커브 감속 오검출 — 실주행 로그로 최초 확인 (고속도로 분기점 조기 과감속 후 원복)

### 배경
- 사용자가 실제 콤마 디바이스로 주행 중 채증한 로그(qcamera.ts/qlog.zst/rlog.zst, route
  000003fb--8470375f65--21) 업로드.
- 증상: 고속도로 거의 직선 구간에서 좌로 약간 굽은 분기점 접근 시, 미리감속이 과하게
  걸렸다가 다시 원복되는 느낌.

### 확인된 사실 (rlog 파싱 결과, pycapnp + carrot-wip 스키마로 직접 복호화)
- t=47.3s경 carrotMan.desiredSource가 "route"로 전환되며 desiredSpeed가 67km/h로 급락.
  이 시점 xDistToTurn(분기점까지 거리)은 아직 499m로, 실제 커브와는 거리가 먼 시점.
- 시스템이 실제로 aTarget 최대 -2.0m/s²까지 감속 명령을 걸어 vEgo가 약 12초간
  96km/h→69km/h로 실제 감소함 (carControl.actuators.accel까지 물리적으로 전달됨,
  표시용 아님).
- 운전자가 t=52.1~59.6s(약 7.5초) 동안 gasPressed=True로 가속페달 개입, 69~72km/h
  유지하며 시스템 감속에 저항.
- t=54.8~57.9s 사이 route/vturn 소스 자체가 재계산되어 desiredSpeed가 115~121km/h로
  회복됨 → 최초 67km/h 목표는 실제보다 훨씬 급한 커브로 오검출된 일시적 값이었음이
  로그상 확인됨.

### 원인 (기존 5차/5차계속 정적 분석과 연결)
- carrot_man.py의 carrot_navi_route()가 내비 폴리라인 3점(40m 간격) 곡률로
  route_speed를 산출하는데, curve_speed.py(비전 버전)에 있는 median 스파이크 제거
  필터가 없음(5차 계속 분석에서 이미 지적된 구조적 리스크).
- 고속도로 분기점 부근은 폴리라인 정점 밀도/기하가 국소적으로 흐트러지기 쉬운
  지점이라 이 3점 곡률 계산이 순간적으로 실제보다 훨씬 급한 커브로 오검출 →
  route_speed가 스파이크성으로 급락 → 차가 그 구간을 지나며 리샘플링 윈도우 이동 →
  오검출 해소 → desiredSpeed가 다시 정상 수준으로 복귀. 이게 "미리 과감속 후 원복"
  체감의 정체.
- ⚠ 이번 로그는 실제 route(경로) 폴리라인 좌표 자체를 갖고 있지 않아(carrotMan/
  carState 메시지만으로 재구성), 폴리라인 기하가 실제로 어떻게 틀어져 있었는지
  위성지도 등으로 직접 대조 확인하지는 못함. 메커니즘은 신호 패턴(거리/소스/속도
  궤적)으로 강하게 뒷받침되나 100% 확진은 아님.

### 결론
- 5차 계속 분석에서 "설계상 위험 요소로 존재한다"고 정적으로만 지적했던 route 감속
  오검출 리스크가, 이번 실주행 로그로 실제 발생을 최초로 확인함.
- 버그라기보다는 필터 부재로 인한 설계상 취약점의 실제 발현 사례.

### 대응 옵션 (미결정, 사용자 선택 필요)
1. 임시완화: TurnSpeedControlMode 2→1(비전만)로 낮춰 route 소스 비활성화
2. 근본수정: carrot_navi_route()에 median/스파이크 제거 필터 추가, 또는 프레임 간
   route_speed 하락률에 clamp 적용
3. 곡률 계산 샘플 간격(현재 40m) 확대로 노이즈 민감도 완화

### 실차 검증
- 실주행 로그(rlog) 1건으로 현상 자체는 확인됨. 다만 원인 메커니즘 중 "폴리라인 기하
  왜곡" 부분은 위성지도 등 외부 자료 대조까지는 하지 못했으므로 100% 확진은 아님.
  코드 수정/최종 조치는 아직 미실시.

### 분석 근거 파일 / 데이터
- 업로드 route: 000003fb--8470375f65--21 (qcamera.ts, qlog.zst, rlog.zst)
- 파싱 도구: pycapnp + carrot-wip(ajouatom/openpilot) cereal/log.capnp, custom.capnp 스키마
- openpilot/selfdrive/carrot/carrot_man.py (carrot_navi_route, calculate_curvature)
- openpilot/selfdrive/carrot/carrot_serv.py (update_navi, speed_n_sources)
- carrot-ryu HEAD: 02015190f58a4380a433ee0130e6374455dddc2e (변경 없음, 분석만 수행)

## [2026-09-12] minSteerSpeed 60km/h 제한 — SMDPS 장착 차량용 해제 토글 확인

### 배경
- CAR.HYUNDAI_GENESIS (제네시스 DH 2015-16 / G80 2017) 플랫폼 설정에
  minSteerSpeed=60km/h가 하드코딩되어 있음.
  (opendbc_repo/opendbc/car/hyundai/values.py, HYUNDAI_GENESIS 블록)
- 사용자 차량은 SMDPS(조향모터) 개조로 저속 조향 개입이 물리적으로 가능한 상태.

### 확인된 사실
- opendbc_repo/opendbc/car/interfaces.py (get_params 함수)에 다음 로직 존재:
  ```
  if Params().get_bool("DisableMinSteerSpeed"):
      ret.minSteerSpeed = 0.
  ```
- 이 Params 키는 carrot-wip 자체에 이미 구현된 기능이며, 콤마 디바이스 설정 UI에도
  노출되어 있음 (openpilot/selfdrive/carrot_settings.json, 1877번째 줄 부근):
  - name: DisableMinSteerSpeed
  - title(한글): "저속조향제한해제"
  - descr: "저속조향이 안되는 차량 제한해제(SMDPS장착차량): 1"
  - 값 범위: 0(기본, 끔) ~ 1(켬)
- params_keys.h에도 PERSISTENT INT 파라미터로 등록되어 있어 재부팅 후에도 유지됨.

### 결론
- 코드 수정 불필요. 콤마 디바이스 설정에서
  "시작(START)" 그룹 → "저속조향제한해제"를 1로 설정하면
  minSteerSpeed가 런타임에 0으로 강제되어 저속 조향 제한이 해제됨.
- carrot-ryu는 carrot-wip과 동일한 상태이므로 이 기능을 그대로 사용 가능.

### 실차 검증
- 미실시. 콤마 디바이스 설정 변경 후 실제 저속 구간(60km/h 이하)에서
  조향 개입 여부와 안정성을 직접 확인 필요.

### 분석 근거 커밋
- carrot-wip HEAD: bb0e18bb8c09422fcd50dcf25c17e0d5c75072b1 (2026-09-12)

## [2026-09-12] 종방향 PID 게인(LongTuningKpV/KiV/Kf)이 현대·기아·제네시스에서 고정됨 — 설정값은 실제로 미적용

### 배경
- PARAMS_REGISTRY.md에 기록된 사용자 현재값: LongTuningKpV=100, LongTuningKiV=0, LongTuningKf=100
  (스케일 적용 시 Kp=1.0, Ki=0.0, Kf=1.0)
- "종방향 제어(가감속) 로직 분석" 요청에 따라 openpilot/selfdrive/controls/lib/longcontrol.py 확인.

### 확인된 사실
- carrot-wip 커밋 a26b108d "safety: fix Hyundai longitudinal PID gains" (2026-09-04, ajouatom)에서
  현대/기아/제네시스(opendbc brand == "hyundai") 차량은 PID 게인을 다음처럼 코드에 고정함:
  - HYUNDAI_LONGITUDINAL_KP = 1.0
  - HYUNDAI_LONGITUDINAL_KI = 0.0
  - HYUNDAI_LONGITUDINAL_KF = 1.0
- `LongControl.__init__`에서 `self.hyundai_fixed_longitudinal_tuning = CP.brand == "hyundai"`이면
  즉시 `_apply_hyundai_longitudinal_tuning()`으로 위 고정값을 self.pid에 적용.
- 주기 갱신 함수 `_refresh_longitudinal_tuning()`도 동일 분기라서, Params에 저장된
  LongTuningKpV/KiV/Kf 값을 아예 읽지 않고 무시함(Hyundai 계열 한정).
  → 즉, 콤마 디바이스 설정 화면에서 이 세 값을 바꿔도 제네시스 DH 2015 실차 제어에는 반영되지 않음.
- 같은 커밋에서 문서(docs/user/ko/cruise-gap.md, settings.md)와 UI 스키마
  (carrot/server/features·services/settings.py, carrot_settings.json)도 함께 갱신되어,
  현대·기아·제네시스에서는 이 3개 항목이 설정 화면에서 숨겨지도록 의도됨.
  → "31개 항목" → "전체 31개, 현대·기아·제네시스 28개"로 문서 수정된 것이 그 근거.
- 반면 `LongActuatorDelay`, `VEgoStopping`, `StoppingAccel`은 이 고정 로직과 무관하게
  계속 Params에서 읽어 실제로 적용됨 (longitudinal_planner.py, longcontrol.py 확인).
  - 사용자 현재값: LongActuatorDelay=20(→0.2s), VEgoStopping=5(→0.05m/s), StoppingAccel=-10(→-0.1m/s²)
  - 단, `LongControl.__init__`에는 `CP.brand=="hyundai"`이고 StoppingAccel==0.0일 때만
    -50(→-0.5)으로 강제 복원하는 별도 안전장치가 있음(e79bfd5d). 사용자 값이 -10이라 이 복원은 발동 안 함.

### 결론
- 이 동작은 버그가 아니라 carrot-wip 유지보수자가 의도적으로 반영한 안전 고정값이며,
  문서에도 명시되어 있음. carrot-ryu는 carrot-wip과 코드 동일하므로 그대로 적용됨.
- 사용자가 실제로 조절 가능한 종방향 "반응성/지연" 관련 노브는 현재
  LongActuatorDelay / VEgoStopping / StoppingAccel 뿐이며, PID 게인 자체는 조절 불가.
- 최종 액추에이터 클램프는 opendbc/car/hyundai/values.py의 CarControllerParams
  (ACCEL_MIN=-4.0, ACCEL_MAX=2.5 m/s²)로, 전 Hyundai 계열 공통이며 제네시스 전용 값은 없음.

### 실차 검증
- 미실시. 코드/문서 정적 분석 기준.

### 분석 근거 커밋
- a26b108d (2026-09-04, "safety: fix Hyundai longitudinal PID gains") — 이번 발견의 핵심 커밋
- e79bfd5d (StoppingAccel 0일 때 -0.5 복원 로직)
- carrot-wip/carrot-ryu HEAD: bb0e18bb8c09422fcd50dcf25c17e0d5c75072b1 (2026-09-12, 변경 없음)

## [2026-09-12] DisableDM=2 의미 확인 — 운전자 모니터링 완전 OFF + Carrot Vision WebRTC 활성화

### 배경
- PARAMS_REGISTRY.md에 DisableDM=2가 기본값(0)이 아닌 채로 확인되었으나 의미 미확인 상태였음.

### 확인된 사실 (openpilot/selfdrive/carrot_settings.json 설명 문구 기준)
- descr: "1.DisableDM, 2: +EnableWebRTC, reboot required"
- 즉 값의 의미: 0=기본(DM 켜짐), 1=DM 비활성화만, 2=DM 비활성화 + Carrot Vision(WebRTC 원격 스트리밍) 활성화(재부팅 필요)

### 코드 레벨 동작 (DisableDM=1과 2 공통, DM 비활성화 부분)
- system/manager/process_config.py `enable_dm()`: `DisableDM == 0`일 때만 dmonitoringd(운전자 카메라 모니터링 프로세스) 실행
  → 1이든 2든 운전자 모니터링 프로세스 자체가 아예 뜨지 않음.
- selfdrive/selfdrived/selfdrived.py 245행: `DisableDM == 0`일 때만 졸음/주의분산 lockout, 경고(driverDistracted1~3 등) 로직 수행
  → 1/2에서는 이 안전 경고·개입 잠금 로직이 전부 스킵됨.
- selfdrive/controls/controlsd.py 426행: `DisableDM == 0`일 때만 AlertLevel.three(3단계 경고) 시 forceDecel(강제 감속) 적용
  → 1/2에서는 운전자 부주의로 인한 강제 감속도 발생하지 않음.

### DisableDM=2 전용 동작 (WebRTC)
- system/manager/process_config.py `enable_webrtc()`: `DisableDM == 2 and not ClusterHud`일 때
  carrot_vision_encoderd(도로 카메라 WebRTC 인코더) 프로세스가 활성화됨 (Carrot Vision 원격 시청 기능).
- ClusterHud==1이면(계기판 클러스터가 로드 카메라를 직접 사용 중) 충돌 방지를 위해 WebRTC는 비활성화됨.

### 결론
- 사용자의 DisableDM=2 설정은 "운전자 모니터링(졸음/주의분산 감지, 관련 경고·강제감속)을 완전히 끄고,
  대신 Carrot Vision을 통한 원격 화면 시청 기능을 켠 상태"를 의미함.
- 이는 안전과 직결되는 설정이며, 사용자가 의도적으로 설정한 것인지(예: DM 카메라 미장착/오작동, 또는
  의도적 비활성화) carrot-wip 자체의 결함은 아니고 사용자 선택의 문제임.
- carrot/server/features/intro/presets.py의 3개 기본 프리셋은 모두 `DisableDM: 0`(DM 켜짐)을 기본값으로
  두고 있어, 현재 값(2)은 사용자가 프리셋에서 벗어나 직접 변경한 상태로 보임.

### 실차 검증
- 미실시. 코드/설정 문구 기준 정적 분석. 사용자에게 이 설정이 의도된 것인지 확인 필요.

## [2026-09-12] LateralTorqueCustom=0 확인 — 저장된 LateralTorque* 값은 미적용, 실제로는 기본 튜닝 사용 중

### 배경
- PARAMS_REGISTRY.md에 LateralTorqueKf=100, Friction=30, AccelFactor=2500, KiV=10, KpV=100, Kd=0이
  기록되어 있었으나 LateralTorqueCustom=0이라 "비활성 상태로 보임"이라는 잠정 메모만 있었음.

### 확인된 사실 (openpilot/selfdrive/controls/lib/latcontrol_torque.py)
- `update()`에서 매 10프레임마다 `LateralTorqueCustom` 값을 확인:
  - `> 0`이면 저장된 LateralTorqueKpV/KiV/Kf/Kd/AccelFactor/Friction 값을 읽어 PID와 torque_params에 적용.
  - `== 0`(현재 상태)이면 이 분기를 타지 않으므로 저장된 LateralTorque* 값은 전혀 읽히지도, 적용되지도 않음.
  - (0으로 막 전환된 프레임에서 1회 한정으로 기본값 복원 로직은 있으나, 이후에는 그냥 기존 기본값 유지)
- 실제 적용되는 기본 토크 튜닝은 `CarInterfaceBase.configure_torque_tune()`
  (opendbc_repo/opendbc/car/interfaces.py)이 `opendbc/car/torque_data/params.toml`에서
  차종별 실측 계수를 읽어 설정:
  - HYUNDAI_GENESIS 실측값: LAT_ACCEL_FACTOR=2.7807965280270794, FRICTION=0.0984484465421171
  - kp=1.0, kf=1.0, ki=0.1은 전 차종 공통 하드코딩값 (params.toml과 무관)
  - latAccelOffset=0.0 고정

### 결론
- 사용자가 저장해 둔 LateralTorqueKf=100 등 값은 "커스텀 토크 테이블을 쓰겠다"는 스위치
  (LateralTorqueCustom)를 켜지 않아 실제로는 전혀 사용되지 않고 있음.
- 현재 제네시스 DH 2015는 opendbc가 실측해 둔 기본 torque_data(LAT_ACCEL_FACTOR≈2.78, FRICTION≈0.098)로
  조향 토크가 계산되는 중.
- 이는 버그가 아니라 "커스텀 토크 끔" 상태의 정상 동작이며, 저장된 값 자체가 잘못된 것도 아님
  (켜기만 하면 그 값들이 그대로 적용됨). 사용자가 커스텀 토크 튜닝을 실제로 원한다면
  LateralTorqueCustom을 1 이상으로 바꿔야 함.

### 실차 검증
- 미실시. 코드 정적 분석 기준.

### 분석 근거 파일
- openpilot/selfdrive/selfdrived/selfdrived.py, openpilot/selfdrive/controls/controlsd.py,
  openpilot/system/manager/process_config.py, openpilot/selfdrive/carrot_settings.json (DisableDM)
- openpilot/selfdrive/controls/lib/latcontrol_torque.py, opendbc_repo/opendbc/car/interfaces.py,
  opendbc_repo/opendbc/car/torque_data/params.toml (LateralTorqueCustom)
- carrot-wip/carrot-ryu HEAD: bb0e18bb8c09422fcd50dcf25c17e0d5c75072b1 (2026-09-12, 변경 없음)

## [2026-09-12] route(경로) 기반 커브 감속 체인 확인 — 실제 감속 명령까지 연결됨, 이 차량은 활성화 상태

### 배경
- "route 감속 관련 코드 분석" 요청. carrot-serv.py의 speed_n_sources에 "route"라는
  소스 이름이 있는 것을 확인하고 그 전체 체인을 추적함.

### 확인된 사실 (호출 체인)
1. carrot_man.py: carrot_navi_route() — 외부 내비 앱이 보내준 경로 폴리라인(self.navi_points,
   최대 256포인트, carrotNavi 브리지로 수신)에서 현재 위치 기준 300m 구간을 5m 간격 리샘플링 →
   3점(40m 간격)으로 곡률 계산 → 곡률→속도 룩업테이블(V_CURVE_LOOKUP_BP/VALS) 적용 →
   autoNaviSpeedDecelRate로 역순 가속도 제한 감속 프로파일 생성 → route_speed 산출
2. carrot_serv.py: update_navi() — route_speed에 mapTurnSpeedFactor 곱하고
   autoCurveSpeedLowerLimit로 하한 적용. TurnSpeedControlMode가 2/3/4일 때만
   speed_n_sources에 ("route", route_speed) 추가. 다른 소스(과속카메라 sdi, 방지턱,
   스쿨존, 비전커브 vturn, 도로제한속도 road)와 함께 최솟값을 desiredSpeed로 선택 →
   carrotMan 메시지로 publish
3. carrot_functions.py: CarrotPlanner._update_carrot_man() (451행) —
   v_cruise_kph = min(v_cruise_kph, carrot_man.desiredSpeed)
4. longitudinal_planner.py (126~130행) — self.v_cruise_kph = carrot.update(sm, v_cruise_kph, mode) →
   v_cruise로 변환되어 LongitudinalMpc의 v_cruise 상한 파라미터로 전달 → MPC가 이 상한에 맞춰
   실제 가/감속 궤적(jerk 제한 포함)을 계산 → actuator로 전달
- controlsd.py의 hudControl.setSpeed는 이 체인과 별개의 표시 전용 값이며, 실제 감속은
  4번 체인(carrot.update → longitudinal_planner → MPC)을 통해 일어남.

### 활성화 전제조건 (모두 만족해야 발동)
- TurnSpeedControlMode = 2 이상 (0: 미사용, 1: 비전만, 2: 비전+경로(TBT, ±500m 이내만),
  3/4: 경로 항상). carrot_settings.json 상 기본값은 1(비전만)이라 route 소스 기본 비활성.
- MapTurnSpeedFactor 설명에 "APN 연결시에만"이라 명시 — 폰 내비 앱이 carrotNavi 브리지로
  경로 폴리라인을 실시간 전송해야 함(navi_points_active, navd_active).
- is_onroad, SHAPELY_AVAILABLE(shapely 라이브러리)도 필요. 하나라도 빠지면
  carrot_navi_route()가 (300, 무제한)을 반환해 사실상 미작동.

### 이 차량(제네시스 DH 2015)의 실제 설정 — 활성화 상태로 확인됨
- params_snapshots/2026-09-12_params_backup-4.json 확인 결과 TurnSpeedControlMode=2
  (기본값 1이 아님) → 이 차량은 route 감속이 켜져 있는 상태.
- MapTurnSpeedFactor=100(반영비율 100%), AutoCurveSpeedLowerLimit=20(하한 20km/h),
  AutoNaviSpeedDecelRate=60(0.60 m/s² 감속률)
- ⚠ DisableDM=2와 같은 패턴: "설정은 켜져 있는데 사용자가 의도한 것인지 아직 확인 안 됨".
  폰 내비 앱 연동(APN) 자체가 실제로 붙어있는지도 미확인.

### 잠재 리스크 (정적 분석 기준)
- 곡률을 GPS 폴리라인 좌표로만 계산 — 내비 앱이 주는 폴리라인의 점 밀도/정확도에
  전적으로 의존. curve_speed.py(비전 버전)에는 있는 3노드 median 스파이크 제거 필터가
  이 route 버전(carrot_navi_route)에는 없어, GPS 노이즈로 인한 곡률 오검출 가능성 있음.
- GPS 위치/heading(bearing) 오차가 gps_to_relative_xy 변환에 그대로 전파됨.

### 결론
- 코드 자체는 완결된 파이프라인이고 실제 감속 명령까지 이어지는 것은 확인됨. 다만
  "코드가 있다 = 실차에서 항상 안전하게 작동한다"는 아니며, 외부 내비 앱 연동 안정성과
  GPS 폴리라인 품질에 성패가 좌우됨.
- 버그로 보이는 부분은 없음(설계상 위험 요소는 존재).

### 실차 검증
- 미실시. 정적 코드/설정값 분석 기준.

### 분석 근거 파일
- openpilot/selfdrive/carrot/carrot_man.py (carrot_navi_route, calculate_curvature)
- openpilot/selfdrive/carrot/carrot_serv.py (update_navi, speed_n_sources)
- openpilot/selfdrive/carrot/carrot_functions.py (_update_carrot_man)
- openpilot/selfdrive/carrot/carrot_navi_control.py (parse_carrot_navi_control, NaviRouteControl)
- openpilot/selfdrive/controls/lib/longitudinal_planner.py (v_cruise_kph 계산부)
- openpilot/selfdrive/controls/controlsd.py (setSpeed, hudControl 표시부)
- openpilot/selfdrive/carrot_settings.json (TurnSpeedControlMode, MapTurnSpeedFactor 설명)
- carrot-wip/carrot-ryu HEAD: bb0e18bb8c09422fcd50dcf25c17e0d5c75072b1 (변경 없음)

## [2026-09-12] T_FOLLOW/TFollowGap(차간거리) 체인 확인 — MPC 리드차 장애물 제약에 직접 반영됨

### 배경
- "종방향 코드 계속 분석" 요청으로 t_follow.py(22줄, 헬퍼 함수만 존재)에서 시작해
  실제 호출부(carrot_functions.py, long_mpc.py)까지 추적함.

### 확인된 사실 (계산 체인, carrot_functions.py)
1. _get_base_t_follow() — personality(aggressive/standard/relaxed/moreRelaxed) 4단계별
   TFollowGap1~4 값 선택. EnableSpeedTF<0이면 속도 구간별 보간으로 대체 가능(고정 브레이크포인트
   [0,30,60,90]/[0,40,80,120]/[0,50,100,150] 중 EnableSpeedTF값(-1/-2/-3)으로 선택)
2. _apply_speed_t_follow_scale() — EnableSpeedTF>0이면 저속에서 차간거리를 줄였다가
   고속으로 갈수록 원복(반대 방향 스케일링)
3. _apply_decel_hold_and_boost_t_follow() — 감속(a_ego≤-0.2) 중엔 여유거리를 즉시 늘리고
   (TFollowDecelBoost 비율, a_ego=-2.5일 때 최대 0.5초 추가), 해제 시엔 서서히만
   줄여(0.10×dt/frame) 널뛰기 방지
4. _clip_t_follow() — [0.3초, tf_max]로 클립. tf_max는 myTFollowFactor(주행모드)로 확장 가능
5. ramp_t_follow() — 거리를 늘리는 쪽만 램프(0.30 또는 0.60초/초, decel_extra 여부에 따라),
   줄이는 쪽은 즉시 반영
6. get_T_FOLLOW()에 leadAccelResponse>=4 레벨 예외 있음: 추적 중인 선행차가 양의 가속
   중이면(gap이 벌어지는 중) 속도기반 스케일을 건너뛰고 설정된 tf_base를 그대로 유지
   (gap이 벌어지는데 차간거리를 괜히 좁히지 않기 위함)
- long_mpc.py 421행: t_follow = carrot.get_T_FOLLOW(...) → desired_follow_distance() →
  MPC의 리드차 장애물 거리 제약(obstacle constraint)에 직접 반영 → 실제 추종거리/
  가감속 명령으로 이어짐 (route 감속과 마찬가지로 표시용이 아니라 실동작 경로).
- 상태 변수(_tf_decel_extra, _tf_base_last 등) 초기화 확인: __init__에서 안전하게
  초기화되어 있고 getattr fallback도 첫 프레임에서 크래시 나지 않음. 정적으로 버그
  발견되지 않음.

### 이 차량의 실제 설정값 (params_backup-4.json)
- TFollowGap1~4: 110/120/140/160 (1.10/1.20/1.40/1.60초) — openpilot 표준 범위 내, 이상 없음
- EnableSpeedTF: 0 → 속도기반 보정 미사용, personality 고정값만 사용 중
- LeadAccelResponse: 0 → 레벨4-5 예외(선행차 가속중 설정값 유지) 비활성 상태
- DynamicTFollowLC: 100(=1.0) → 차선변경시 차간거리 배율 변화 없음
- TFollowDecelBoost: 10(=0.10) → 감속시 여유거리 보정 약하게(최대 0.05초)
- (PARAMS_REGISTRY.md의 기존 "TFollowGap5 미확인" 메모는 정정: 코드상 TFollowGap1~4까지만
  존재하며 5번째 항목은 없음)

### 결론
- T_FOLLOW 체인은 정적으로 문제없이 설계되어 있고, 실제 추종거리 제어에 반영됨.
- 이 차량은 속도기반 보정(EnableSpeedTF)과 레벨4-5 예외(LeadAccelResponse)를 모두 끈
  "가장 단순한" personality 고정값 모드로 운용 중 — 의도적 설정인지, 아니면 시험해보지
  않은 기본값인지는 사용자 확인 필요.

### 실차 검증
- 미실시. 정적 코드/설정값 분석 기준.

### 분석 근거 파일
- openpilot/selfdrive/carrot/t_follow.py
- openpilot/selfdrive/carrot/carrot_functions.py (_get_base_t_follow ~ get_T_FOLLOW, 189~328행)
- openpilot/selfdrive/controls/lib/longitudinal_mpc_lib/long_mpc.py (t_follow 사용부, 405~470행)
- openpilot/selfdrive/carrot_settings.json (TFollowGap1~4 설명/범위)
- carrot-wip/carrot-ryu HEAD: bb0e18bb8c09422fcd50dcf25c17e0d5c75072b1 (변경 없음)

## [2026-09-12] traffic_stop.py(E2E 정지신호 감속) 체인 확인 — 순수 비전모델 휴리스틱, HD맵/신호색상 인식 없음

### 배경
- 종방향 분석 계속 진행: t_follow.py 다음으로 traffic_stop.py(정지선/신호 감속) 추적.

### 확인된 사실 (호출 체인)
- carrot_functions.py: check_model_stopping() — 주행모델이 예측한 미래 경로(x,y,v)만으로
  정지신호 여부 추론. 속도구간별 다른 임계값(1km/h 미만: model_x<20&&model_v<10 /
  82km/h 미만: model_x<d_rel-3, 속도별 거리상한 120~150m, model_v<3 or <v[0]*0.7, |y[-1]|<5m /
  82km/h 이상: 감지 안 함). stopSignCount/startSignCount 프레임 누적으로 trafficState(red/green/off) 결정
- XState 상태머신(e2eCruise→e2ePrepare→e2eStop→e2eStopped) — 가스/브레이크, 레이더 리드,
  trafficState에 따라 전이. is_traffic_stop_entry_allowed()로 조향각 50도 이상(회전 중)이면
  새 정지 진입 억제
- actual_stop_distance: 속도 높을수록 먼 거리 추정치를 np.interp로 깎아 보정. 빨간불 지속시
  comfort_brake를 매 프레임 0.9배씩 부드럽게 조임
- TrafficStopModelLeadMatcher(traffic_stop.py): 정차 상태에서 레이더 리드가 없을 때 모델이
  본 정차 선두차량 위치를 5프레임 연속(확률≥0.90, 거리 4~80m, 정지선과 gap 0~3m, 속도≤2m/s,
  x/y/v 표준편차 임계값 이내) 검증 후에만 obstacle로 확정 — median 필터 + confirm frame으로
  방어적으로 설계됨
- long_mpc.py(469~475행): get_traffic_stop_distance_adjust()/get_traffic_stop_obstacle_distance()로
  stop_x를 MPC obstacle(x2)로 변환, x_obstacles에 포함되어 acados MPC가 실제 감속 궤적 계산.
  50m~순항거리 구간에서 신호 obstacle을 점진적으로 노출해 급제동 방지하는 스무딩 포함

### 이 차량의 실제 설정
- TrafficLightDetectMode=2 (기본값, "정지+출발 모두 감지" — 별도 조작 없이 이미 실도로에서
  작동 중이었을 가능성 높음)
- StopDistanceCarrot=700 (7.00m), TrafficStopDistanceAdjust=0 (코드 초기값 2.5m을
  사용자가 0으로 재설정)

### 결론
- 실제 MPC까지 연결되는 진짜 감속 경로이고 방어 로직(median 필터, confirm frame, isfinite,
  std 임계값)도 탄탄함.
- 구조적 리스크: HD맵/신호등 색상 인식이 전혀 없는 순수 E2E 휴리스틱이라 주행모델의 예측
  정확도에 전적으로 의존. 회전교차로, 임시신호, 공사구간 등 모델이 학습 못한 상황에서
  놓치거나 오검출할 수 있음(버그가 아니라 이 접근 방식 자체의 근본적 한계).

### 실차 검증
- 미실시. 정적 코드/설정값 분석 기준.

### 분석 근거 파일
- openpilot/selfdrive/carrot/traffic_stop.py (TrafficStopModelLeadMatcher, get_traffic_stop_*)
- openpilot/selfdrive/carrot/carrot_functions.py (check_model_stopping, XState 상태머신, 340~680행)
- openpilot/selfdrive/controls/lib/longitudinal_mpc_lib/long_mpc.py (440~490행, x2 obstacle 반영부)
- openpilot/selfdrive/carrot_settings.json (TrafficLightDetectMode 설명)
- carrot-wip/carrot-ryu HEAD: bb0e18bb8c09422fcd50dcf25c17e0d5c75072b1 (변경 없음)

## [2026-09-12] curve_speed.py(비전 커브 감속) 확인 — 물리식 기반, 외부 의존성 없어 route 버전보다 견고

### 배경
- 종방향 분석 계속: curve_speed.py(비전 버전) 및 route 버전과의 차이 비교.

### 확인된 사실
- carrot_man.py: carrot_curve_speed() → vturn_speed() → curve_speed.py의 curve_speed() 함수 호출.
  입력은 sm['modelV2'](주행모델 예측 경로/속도/각속도)와 carState.vEgo/aEgo/vCluRatio 뿐 —
  외부 내비 앱(APN) 연동 불필요, 항상 동작 가능.
- curve_speed() 계산: 곡률=yaw_rate/velocity를 경로 각 지점에서 계산 → 3점 median 필터로
  순간 yaw 스파이크 제거(route 버전엔 없는 필터) → curve_ms=sqrt(횡가속도_예산/곡률)
  (원운동 물리공식, 룩업테이블 아님) → 감속 반응시간(액추에이터 지연 1.0초+저크 해소시간)과
  감속도(1.0 m/s²)를 감안한 거리기반 역산으로 approach_ms 산출 → 최대 180m(or v_ego*6s)
  전방 중 가장 타이트한 제약(최솟값) 선택
- VisionCurveSpeed.update(): 속도를 줄이는 쪽은 즉시 반영, 늘리는(제약 해제) 쪽은
  0.35초 대기 후 초당 7.2km/h로만 서서히 반영 — 커브 탈출 시 급가속 방지
- vturn_speed는 carrot_serv.py의 speed_n_sources에 "vturn" 소스로 포함되어 route/sdi 등과
  함께 desiredSpeed 최솟값 계산에 참여(5차 route 감속 체인 항목 참고)

### 이 차량의 실제 설정
- AutoCurveSpeedFactor=80 (기본 100%보다 낮음. 설정 설명상 "값을 높이면 허용 횡가속도가
  낮아져 목표속도가 낮아짐" → 80%는 기본보다 느슨하게, 즉 커브를 더 빠른 속도로
  통과하도록 설정된 상태). AutoCurveSpeedLowerLimit=20 (route 버전과 공유)

### route(경로) 버전과 비교
| 항목 | route(경로) | curve_speed(비전) |
|---|---|---|
| 데이터 소스 | 폰 내비 앱 GPS 폴리라인 | 주행모델 예측 경로만 |
| 외부 의존성 | APN 연결 필수 | 없음(항상 동작) |
| 스파이크 필터 | 없음 | 3노드 median 있음 |
| 신뢰도(정적 분석 기준) | 내비 앱 연동 상태에 좌우 | 상대적으로 견고 |

### 결론
- 물리식 기반으로 설계가 탄탄하고 외부 의존성이 없어 route 버전보다 작동 신뢰도가 높음.
- 다만 결국 주행모델이 예측한 미래 경로/yaw에 의존하므로, 모델의 원거리 커브 인지 정확도가
  이 기능 전체의 성패를 좌우함(E2E 모델 의존 시스템 공통 한계).

### 실차 검증
- 미실시. 정적 코드/설정값 분석 기준.

### 분석 근거 파일
- openpilot/selfdrive/carrot/curve_speed.py (curve_speed, VisionCurveSpeed)
- openpilot/selfdrive/carrot/carrot_man.py (carrot_curve_speed, vturn_speed)
- openpilot/selfdrive/carrot/carrot_serv.py (speed_n_sources "vturn" 항목, 5차 항목과 공유)
- openpilot/selfdrive/carrot_settings.json (AutoCurveSpeedFactor 설명)
- carrot-wip/carrot-ryu HEAD: bb0e18bb8c09422fcd50dcf25c17e0d5c75072b1 (변경 없음)

## [2026-09-12] longitudinal MPC 코스트 함수 확인 + 종방향 전체 체계 종합 — 종방향 코드 분석 1단계 마무리

### 배경
- 종방향 분석 마지막 항목: long_mpc.py의 코스트 함수(set_weights) 및 jerk_factor 연동 확인,
  이후 지금까지(4차~5차) 분석한 종방향 6개 축을 종합.

### 확인된 사실
- set_weights()는 stock openpilot의 acados 기반 MPC 프레임워크(gen_long_ocp) 그대로이며,
  carrot 고유 로직이 아님. 코스트 항목: X_EGO_OBSTACLE_COST, X_EGO_COST, V_EGO_COST,
  A_EGO_COST, a_change_cost(감가속 변화 억제), jerk_factor×J_EGO_COST(저크 억제).
  carrot은 이 프레임워크에 입력값(t_follow, v_cruise, stop_x, jerk_factor)만 주입하는 구조.
- jerk_factor는 carrot_functions.py에서 personality(4단계)/myDrivingMode에 연동되어
  0.5~1.0 사이로 결정 → 낮을수록 저크 비용↓ → 가감속 변화가 더 급격해짐(반응성↑ 승차감↓).
  이 차량은 EnableSpeedTF=0(else 분기)이라 personality=standard 기준
  myDrivingMode≠Safe면 jerk_factor=0.7.
- TFollowGap1~4(1.10/1.20/1.40/1.60초) 순서가 personality aggressive/standard/relaxed/
  moreRelaxed와 jerk_factor 배정(0.5/0.7/1.0/1.0)이 서로 일관되게 짝지어져 있음을 확인
  (설계 일관성 양호).

### 종방향 전체 체계 종합 (4차~5차 통합)
```
[LongControl PID] -- 현대차는 Kp=1.0/Ki=0.0/Kf=1.0 고정 (설정값 무시, 4차)
        |
[v_cruise 상한] <- min(route 감속, curve_speed 비전 감속, sdi카메라, 도로제한속도) -> carrotMan.desiredSpeed
        |
        v
[longitudinal MPC] <- t_follow(TFollowGap 체인) -> 리드차 obstacle
                   <- stop_dist(traffic_stop 체인) -> 정지선 obstacle(x2)
                   <- jerk_factor/a_change_cost -> 코스트 웨이트
        |
        v
   실제 가/감속 궤적(a_target) -> LongControl -> 액추에이터
```

### 결론 (종방향 코드 분석 1단계 마무리)
- route/vturn/T_FOLLOW/traffic_stop 4개 커스텀 입력 체인 모두 표시용이 아니라 실제로
  MPC까지 연결되어 물리적 가/감속 명령을 만들어내는 것을 코드 레벨에서 확인함.
- MPC 자체(acados 프레임워크)는 stock openpilot 그대로라 신뢰도가 높고, carrot의
  커스텀 입력 생성부도 전반적으로 방어적으로(isfinite, median 필터, confirm frame,
  클립/램프) 작성되어 있어 정적 분석 기준 버그는 발견되지 않음.
- 구조적 리스크 2가지: ①route 감속은 폰 내비 앱(APN) 연동 안정성에 좌우, ②traffic_stop은
  HD맵/신호색상 인식 없이 순수 E2E 모델 휴리스틱이라 모델 성능에 전적으로 의존.
- 실차 검증은 전혀 미실시. 지금까지 결론은 모두 정적 코드 분석 기준이며, 실제 동작 일치
  여부는 실차주행 로그로만 확인 가능 — 다음 단계(실차주행 → 로그분석)로 넘어가기로
  사용자와 합의됨.

### 실차 검증
- 미실시. 정적 코드/설정값 분석 기준. 다음 단계는 실차주행 후 로그분석.

### 분석 근거 파일
- openpilot/selfdrive/controls/lib/longitudinal_mpc_lib/long_mpc.py (get_jerk_factor,
  get_a_change_cost, set_weights, 60~343행)
- openpilot/selfdrive/carrot/carrot_functions.py (jerk_factor 결정부, 220~263행)
- carrot-wip/carrot-ryu HEAD: bb0e18bb8c09422fcd50dcf25c17e0d5c75072b1 (변경 없음)