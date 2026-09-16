# WIP

## 49차 (코드 완료, push 대기) -- 스크린샷 버튼 무반응 진단 로그 추가 + 버튼 위치 사용자 요청 반영

사용자가 실기기 스크린샷 2장(정상 캡처 예시, 실제 로그탭 화면 -- 목록에 사진 0건/영상 3건)을 제공하며 "스크린샷 버튼이 안 눌러지고 로그탭에 저장되지 않음" 제보 + "사진캡쳐버튼을 참고 사진의 빨간색 동그라미 위치로 이동" 요청.

**증거**: 로그탭 스크린샷에서 목록의 항목 3개가 전부 MP4(화면녹화)이고 JPG(사진)가 하나도 없음 -- 스크린샷 저장이 실제로 0건이라는 뜻이라 제보와 일치.

**코드 조사**: click 처리 로직(`Widget._process_mouse_events`), `capture_onroad_screenshot()`(47차 버전), pyray 바인딩(`uv.lock`에 고정된 `comma-deps-raylib==6.0.0.1.post101`을 sandbox에 실제 설치해 `load_image_from_screen`/`export_image` 존재 확인) 어디에서도 명백한 버그를 못 찾음. 11절 원칙(추측만으로 원인을 확정하지 않음)에 따라, 원인 확정 대신 다음 실차 테스트에서 원인이 드러나도록 진단 로그를 추가:
1. `screenshot_capture.py`: 3개 실패 분기(캡처 크기 이상/`export_image` 실패/파일 생성 실패)와 예외 처리에 `cloudlog.warning`/`cloudlog.exception` 추가.
2. `screenshot_button.py`: `_on_click`에 `cloudlog.debug("ScreenshotButton clicked")` 추가 -- 클릭 자체가 콜백까지 도달하는지, 캡처만 실패하는지 다음 실차 테스트에서 구분 가능.

**버튼 위치 변경**: `hud_renderer.py`에서 스크린샷(카메라) 버튼을 화면 중앙(기존 자리, `anchor_x`로 명명)에서 좌측으로 버튼 한 칸(140px 폭 + 30px 간격 = 170px) 이동. record 버튼 위치는 `anchor_x` 기준 수식이 이전과 동일해 절대 위치 그대로 유지.

**검증**: `py_compile`/`ast.parse` 3개 파일 모두 통과. Replace-Block 방식으로 `hud_renderer.py` 변경 전 블록이 파일 전체에서 정확히 1회 매치함을 Python으로 확인(9절). `cloudlog.debug/warning/exception`이 `SwagLogger`(`logging.Logger` 서브클래스)의 표준 메서드임을 `common/logging_extra.py` 소스로 확인(추측 아님, 11절).

**실차 검증**: 미실시 -- 이번 세션은 "원인 확정"이 아니라 "다음 테스트에서 원인이 보이게 만드는" 진단 단계(11절). 버튼 위치 변경도 실기기 확인 전.

상세: FINDINGS.md 2026-09-16(49차) 항목, 핵심 발견 34. HANDOFF.md 49차 참고.

## 48차 (검증 완료) — 47차 push 확인 + 36차/39차/37차 이월 항목 실기기 검증

사용자가 "체크포인트"를 요청. 4절 0단계(`git ls-remote`로 carrot-ryu-note SHA 고정 조회)부터 시작.

- `git ls-remote`로 carrot-ryu HEAD를 확인한 결과 `41fd34a7458d663d27e16d96fbeb2c6bcb20c1b5`(47차 스크린샷 DPI/JPG 수정)로 이미 push돼 있음을 확인. GitHub commit API로 커밋 메시지("47cha: fix screenshot DPI-scale portrait bug, save as jpg")와 변경 파일(`openpilot/selfdrive/ui/onroad/screenshot_capture.py` 1개)을 확인하고, raw.githubusercontent.com(SHA 고정)으로 파일 실제 내용을 재조회해 `rl.load_image_from_screen()` + `.jpg` export가 계획대로 반영됐음을 재확인. 47차 HANDOFF 미완료 1번이 세션 사이에 해소됨.
- 사용자가 제공한 실기기 스크린샷 7장(로그 전송 확인창 2장, HUD 디바이스 직접촬영 1장, 로그탭 화면녹화/사진 목록 2장, 구글드라이브 폴더·파일 목록 2장)으로 아래 이월 항목들을 실기기 검증:
  1. Issue 1(당근서버 라벨 오표시, 36차): 로그 전송 확인창에 "구글 드라이브"로 정확히 표시됨 -- 정상 확인.
  2. Issue 3(햄버거 메뉴 탭 무관 업로드, 36차): 화면녹화/로그 탭에서 탭 전용 선택-전송 UI(체크박스 + "선택 전송")가 정상 동작 -- 정상 확인.
  3. 39차/46차에서 미확인이던 "선택 전송" 버튼의 실제 전송 성공 여부: 사진/영상 3개 항목 체크 후 전송하는 흐름을 확인했고, 구글드라이브 "CarrotWeb Logs" 폴더에 해당 타임스탬프 mp4 파일(`20260916-111847.mp4` 등)이 실제로 존재함을 확인 -- 전송 성공까지 실증됨. (단, "선택 다운로드" 버튼 동작은 이번에도 확인 안 됨, 이월.)
  4. Issue 4(Drive 폴더 중복생성, 37차 락 수정): 구글드라이브 루트에 "CarrotWeb Logs" 폴더가 1개만 존재함을 재확인 -- 정상.
  5. 27차 HUD 경로안내 박스: 디바이스 화면 직접촬영 사진에서 레이아웃(교차로/회전아이콘/route=/도착거리/ETA/도로명)이 정상임을 재확인.
- 코드 변경 없음(전부 검증/문서화 세션). devnotes(WIP.md/CURRENT_STATUS.md/HANDOFF.md)만 갱신.
- 다음 세션 최우선 이월: 47차 스크린샷 수정 자체의 실차 검증(스크린샷 버튼을 실제로 눌러 가로 2160x1080 JPG로 저장되는지, 용량, 목록 표시 확인) -- 아직 확인 안 됨.

## 47차 (코드 완료, push 대기) -- 스크린샷 캡처 세로 뒤바뀜/과대용량 원인수정

사용자가 정상 캡처 예시(가로 2160x1080)와 실제 저장된 사진(세로 1080x2160, 상단 대부분 검정, 용량도 4배가량 큼) 두 장을 제공하며 버그 제보.

1. **원인**: `screenshot_capture.py`의 `rl.take_screenshot()`이 raylib 내부에서 `render 크기 * GetWindowScaleDPI()`로 캡처 크기를 계산하는데, 이 기기에서 DPI 스케일이 비등방으로 나와 가로/세로가 뒤바뀐 채 저장됨. 제공받은 두 이미지의 실제 픽셀 크기(2160x1080 vs 1080x2160)를 직접 확인해 실증.
2. **수정**: `rl.load_image_from_screen()`으로 교체(DPI 배율 계산 없이 논리적 화면 크기로 프레임버퍼를 그대로 읽음 -- 영상 녹화 파이프라인이 이미 쓰고 있는 "DPI 우회" 방식과 동일 원리, 46차에서 실차 검증된 접근).
3. **겸사겸사**: 저장 포맷을 PNG -> JPG로 전환(사진 용량 축소). `SCREEN_RECORDING_PHOTO_EXTS`에 `.jpg`/`.jpeg`가 이미 등록돼 있어 백엔드/프론트엔드 추가 수정 불필요함을 코드 조사로 확인.
4. `py_compile` 통과 + sandbox에 pyray를 별도 설치해 `export_image`의 JPG 저장 자체가 정상 동작함을 headless로 확인(실제 화면 렌더 검증은 아님).
5. carrot-ryu(코드, 전면 교체 방식) + carrot-ryu-note(devnotes) 반영 스크립트 작성, 둘 다 실행 대기. 실차 검증은 다음 세션 최우선 이월.

상세: FINDINGS.md 2026-09-16(47차) 항목, 핵심 발견 33. HANDOFF.md 47차 참고.

## 46차 (완료 -- HEAD 99b49a1 실기기 검증 4건, 최우선 이월 항목 전부 해소) -- 45차 배포분 실기기 검증

사용자가 제공한 스크린샷 2장(도구 탭 git pull 로그, 로그 탭 사진목록 화면)과 영상 1개(20260916-095343.mp4, 온로드 화면 4초 분량)로 HANDOFF.md 최우선 이월 1~4번을 전부 실기기 검증 완료.

1. **carrot-ryu HEAD(99b49a1) 실기기 배포 확인**: 도구 탭 로그에 실제 git pull 출력이 캡처됨 -- "Updating e2f356198..99b49a113", "Fast-forward", 변경 파일 ".../carrot/web/generated/asset-manifest.json"(2줄)/".../selfdrive/carrot/web/js/generated/logs.js"(32줄) 정확히 일치, 이어서 reboot 실행까지 로그로 확인. 45차 최종본이 실기기에 실제로 반영/재부팅됐음이 최초로 실증됨(45차-정정까지는 "미실시"였음).
2. **사진 목록 크래시 해소 확인(44/45차 formatLogBytes)**: 재부팅 후 로그 탭 스크린샷에서 사진 목록이 정상 렌더되고, 파일 크기가 "2.2 MB"/"2.3 MB"로 정확히 포맷되어 나옴(formatLogBytes가 실제로 호출/동작하는 증거). 체크박스/다운로드/전송 아이콘 정상.
3. **delete_all_videos 스크린샷 폴더 포함 확인(44차)**: 사용자가 실기기에서 전체 삭제 시 사진까지 삭제됨을 확인(사용자 보고).
4. **로그탭 새로고침 아이콘 확인(41차)**: 에러 없이 동작하며, 실제로 목록이 갱신됨을 사용자가 확인(사용자 보고). 41차 이월 항목 완료.
5. **녹화 버튼 깜빡임 확인(44차 3번, 정량 분석)**: 영상을 6fps(24프레임)로 추출, 버튼 좌표(원본 해상도 2160x1080 기준 x:1212-1288, y:912-988)를 색상 필터로 특정한 뒤 프레임별 평균 RGB를 측정. 밝은 상태(R≈193, 평균밝기≈99)와 어두운 상태(R≈33, 평균밝기≈34)가 프레임마다 규칙적으로 교대됨을 확인 -- 이전 세션(1.8초 영상, 정지 프레임 육안 비교)에서는 판단 불가였던 것을, 버튼 영역 크롭+수치 비교로 명확히 실증함(핵심 발견 32 참고).

이로써 HANDOFF.md의 "최우선" 이월 항목(1~4번)이 전부 해소됨. 남은 이월 항목(37차 락 동시성 재현, 34차 도로명-신호과속 같은 줄 배치, 28~30차 레이아웃 정밀 재검증, 나머지 코드 변경 전부 실차 재검증, tools.js 실기기 확인, 데드코드/테스트 정리, docs 갱신, carrot-ms 모델 셀렉터 분석, 핵심 발견 31 재발방지 제안 채택 여부)은 계속 이월.

검증: 실기기 스크린샷 2장 + 실기기 촬영 영상 1개(사용자 제공) 근거. 코드 변경 없음(devnotes만 갱신).

## 핵심 발견 31 (45차-정정) -- carrot-ryu-note에 반영된 45차 devnotes가 최종본이 아닌 중간 초안이었음 (코드는 최종본대로 정상 반영/검증됨)

바로 아래 "45차" WIP 항목(및 FINDINGS/HANDOFF의 45차 기록)은 실제로 이번 세션에서 push된 것이 맞지만, Linux sandbox 재빌드로 전환하기 *이전* 단계 -- 즉 사용자 PC에서 `npm install && node build.mjs`를 직접 실행하려던 1차 시도(`45cha_rebuild_bundle_carrot_ryu.ps1`, 예상 밖 diff ~25개 파일로 안전 중단됨) 시점 기준의 중간 초안 내용이다.

실제로는 그 이후 Linux sandbox 빌드로 전환한 최종 스크립트(`45cha_apply_bundle_carrot_ryu.ps1`)가 별도로 만들어져 carrot-ryu에 정상 push/검증까지 완료됐다(commit `99b49a113e48ddaeebf83074b04e42d417a88612`, `js/generated/logs.js` sha256 `9236a3838ecae5b81ef147c03a3b26f87ff1e15d738a159b4905b530acc49cbd` 일치, `node --test` 737/737 통과, 커밋 메시지에 CRLF/npm allow-scripts 가설 기각 및 esbuild 플랫폼 비결정성 결론까지 정확히 기록됨).

문제는 같은 세션에서 devnotes 반영용으로 준비했던 최종 스크립트(파일명 `45cha_devnotes_carrot_ryu_note.ps1`)가 아니라, 그보다 먼저 만들어졌던 동일 파일명의 중간 초안이 사용자 PC에서 실행되어 push됐다는 점이다. 두 버전의 커밋 메시지("bundle-not-rebuilt root cause + rebuild fix" vs 최종본의 "carrotweb 번들 재빌드 크로스플랫폼 비결정성 진단/우회 기록")와 HANDOFF.md Worker 라인이 서로 완전히 다름을 직접 바이트 비교로 확인했다.

원인 추정(직접 재현은 못 함): 한 세션 안에서 devnotes 스크립트를 같은 파일명으로 두 번(중간 초안 -> 최종본) 전달했고, 사용자 PC의 Downloads 폴더에 이미 이전 버전이 남아있어 최종본이 다른 이름으로 저장됐거나, 재실행 시 이전 로컬 파일이 그대로 실행됐을 가능성이 높다.

부가 확인: 검증 과정에서 `git clone --depth 1` 뒤 `git show --stat HEAD`를 실행하면 부모 커밋이 로컬에 없어 빈 트리 대비 diff로 처리되어(grafted root 취급) devnotes 폴더의 무관한 파일들까지 대량으로 나열되는 착시가 있었다 -- 이는 실제 이상 징후가 아니라 shallow clone의 부작용이며, `--depth 5` 이상(부모 포함)으로 다시 확인해 배제했다.

재발 방지 제안(승인 시 지침 문서에 규칙으로 추가 검토): 한 세션 안에서 같은 대상에 대해 스크립트를 다시 만들 때는 파일명에 버전 표시(-v2, -final 등)를 붙여 Downloads 폴더의 이전 로컬 파일과 절대 겹치지 않게 한다.

부가 수정: 이번 검증 중 WIP.md 파일 맨 앞에 있어야 할 "# WIP" 타이틀 헤더가 실제로는 없는 상태임을 발견(FINDINGS.md는 "# FINDINGS" 헤더가 정상적으로 파일 맨 앞에 있는 것과 대조됨 -- 언제부터 이랬는지는 확인 못 함, 과거 어느 세션의 스크립트가 anchor 매칭에 실패한 채로 다른 위치에 텍스트를 삽입했을 가능성). 과거 devnotes 반영 스크립트들이 "# WIP`n`n" 앵커로 매칭했던 것은 사실 파일 맨 앞이 아니라 본문 중 이 앵커 기법 자체를 설명하는 텍스트(과거 세션 기록) 안의 우연한 일치였을 가능성이 있음 -- 다만 그 경우에도 매치 수가 정확히 1이었으므로 항목이 엉뚱한 위치에 삽입되지는 않았을 것으로 추정(직접 재현 확인은 못 함). 이 커밋에서 "# WIP" 헤더를 파일 맨 앞에 복원함.

## 45차 -- 44차 소스 수정은 맞았으나 생성 번들(js/generated/logs.js)이 재생성되지 않아 크래시가 실기기에 그대로 남아있던 문제 발견/수정

사용자가 44차 스크립트 실행 후에도 실기기에서 `formatLogBytes is not defined`가 그대로 재현된다고 제보. GitHub의 carrot-ryu HEAD(commit e2f35619, 44차)를 직접 조회해 보니 `screenshots.js` 소스에는 `formatLogBytes` import가 정상적으로 추가돼 있었지만, 같이 커밋된 `js/generated/logs.js` 번들 안에는 `formatLogBytes` 함수 정의가 없고 호출부만 미해석 외부 참조로 그대로 남아있음을 확인(esbuild가 번들링/이름축약을 못 하고 원문 그대로 남겨둔 상태 -- 정상적으로 번들되면 다른 로컬 함수들처럼 짧은 이름으로 축약되어 원문에 `formatLogBytes` 리터럴이 아예 남지 않아야 함). 즉 44차 세션이 소스 파일은 정확히 고쳤지만, 그 위에서 `npm install && node build.mjs`를 실행해 생성 번들을 다시 만드는 단계를 건너뛴 채 예전(깨진) 번들 그대로 커밋한 것이 원인.

동일 소스로 직접 `npm install && node build.mjs`를 실행해 재현: 재생성된 번들에서는 `formatLogBytes` 호출부가 로컬 함수와 정상적으로 결합/축약되어(리터럴 `formatLogBytes` 문자열이 0회로 사라짐, 축약된 다른 로컬 함수들과 동일 패턴), `node --test tests/**/*.test.mjs` 737/737 통과 확인. 재생성 전후 diff는 `js/generated/logs.js`와 `generated/asset-manifest.json`(해시값 한 줄) 딱 2개 파일로 한정됨 -- 수동 코드 수정은 없고 순수 빌드 재실행 결과.

반영 스크립트(`45cha_rebuild_bundle_carrot_ryu.ps1`)는 이번엔 Replace-Block 문자열 치환이 아니라, 사용자 PC에서 `git clone`(임시 폴더) 후 그 자리에서 실제로 `npm install && node build.mjs`를 실행하고 변경된 생성 파일만 커밋/push하는 방식으로 작성함(9절 "코드 파일" 유형 중 신규/전면 재작성에 해당하되, Claude가 완성 파일을 만들어 전달하는 대신 빌드 과정 자체를 스크립트가 재현하도록 함 -- 100KB 넘는 압축 번들을 문자열로 스크립트에 박아넣는 것보다 안전하고, 진짜 소스인 build.mjs/esbuild 결과를 그대로 신뢰할 수 있음). 스크립트는 빌드 후 `git status`로 변경 파일 목록을 확인해 `js/generated/`, `css/generated/`, `generated/asset-manifest.json` 범위 밖의 변경이 섞이면 커밋하지 않고 중단하도록 방어장치를 넣음(15절 강제 진행 금지 원칙).

미완료: 스크립트 사용자 실행 대기 -> 실행 후 push 반영을 `git ls-remote`+commit patch로 재확인, 이어서 사진 목록 렌더가 실제로 크래시 없이 뜨는지 실기기 재검증(44차 미완료 항목 1~2번과 동일 검증이 이제야 가능).

# WIP

## 44차 (진행 중 -- 실기기 버그 3건 수정 + 반영 스크립트 경로 오류 사전 발견/수정) -- 사진목록 크래시/전체삭제 범위/녹화버튼 깜빡임

사용자가 제공한 42차 녹화 버튼·41차 새로고침 아이콘 실기기 검증 스크린샷(녹화 시작/종료, 화면녹화 파일 생성/전송 성공)을 검토하던 중 신규 버그 발견 및 요청 2건이 추가됨:

1. **사진 목록 크래시**: 화면녹화 탭에서 파일을 체크박스로 선택하는 순간 `formatLogBytes is not defined` 토스트 발생. 코드 조사 결과 `selfdrive/carrot/web/src/features/logs/screenshots.js`가 `formatLogBytes()`를 62번째 줄(개별 항목 크기)과 162번째 줄(선택 합계 크기)에서 쓰면서 `./runtime.js` import문에는 누락돼 있었음(39cha-fix, 40차에서 같은 파일의 `formatRelativeEpoch` 누락은 고쳤으나 `formatLogBytes` 누락은 그때 못 잡음). `dashcam.js`/`screenrecord.js`는 정상적으로 import 중. 수정: import문에 `formatLogBytes` 한 항목 추가.
2. **사용자 요청**: 도구탭 "delete all videos"를 누르면 영상과 사진(캡쳐 스크린샷)까지 함께 삭제되게 해달라. 코드 조사 결과 `dispatcher.py`의 `delete_all_videos` 액션이 비동기(682번째 줄)/동기(1164번째 줄) 두 곳 모두 `/data/media/0/videos` 폴더 하나만 하드코딩돼 있었음. 반면 캡쳐 사진(.png)은 `screenshot_capture.py`에서 `SCREEN_RECORDING_DIRS[1]`(`/data/media/0/screenrecord`)에 저장됨 -- 영상/사진이 서로 다른 폴더라 기존 로직은 사진 폴더를 건드리지 않았음. 수정: 두 곳 모두 `config.py`에 이미 정의된 `SCREEN_RECORDING_DIRS`(영상+사진 후보 폴더 7개 전체, `catalog.py`가 실제 목록 조회에 쓰는 것과 동일한 소스) 기준으로 변경.
3. **녹화 버튼 깜빡임 없음**: 사용자 설명("평상시 흰색테두리, 누르면 빨간색으로 채워짐, 깜빡이지는 않음, 다시 누르면 흰 테두리로 복귀")을 코드로 재확인한 결과 정확히 그대로 구현돼 있었고(42차), 깜빡임 로직 자체가 없어 "실제 녹화 중"이라는 느낌이 안 드는 것이 원인이었음. `hud_renderer.py`가 카메라 감지/CPU·메모리 과열 경고에 이미 쓰고 있는 `_blink_timer` 프레임 카운터를 재사용해, `record_button.py`에 `set_blink_phase()`를 추가하고 녹화 중일 때만 채움/테두리를 번갈아 그리도록 수정(녹화 안 할 때는 42차와 동일하게 유지).

3건 모두 최신 GitHub 재조회 후 Replace-Block 앵커 1회 매치 확인, py_compile/`node --check` 통과.

**[중요, 세션 재개 시 발견]** 이 세션은 이전 세션(스크립트까지 완성한 상태)을 이어받아 시작했으나, 이 환경의 로컬 작업 디렉터리가 세션 사이 초기화되는 특성상 이전 세션이 검증에 썼던 경로 가정을 그대로 신뢰하지 않고 `git clone` 전체 리허설로 처음부터 재검증함. 그 결과 **이전 세션이 작성한 Replace-Block 대상 경로가 `selfdrive/...`로 돼 있었는데, 실제 ryujmin97/openpilot 레포는 루트에 `openpilot` 서브디렉터리가 한 겹 더 있어 정확한 경로는 `openpilot/selfdrive/...`임을 발견**(핵심 발견 29 참고). 만약 그대로 전달됐다면 사용자가 스크립트를 실행하는 순간 `FileNotFoundException`으로 실패했을 것 -- 경로를 수정한 뒤 앵커 매치(전부 1회)와 `py_compile`/`node --check`를 다시 통과시키고, 최종적으로 실제 `git clone`으로 대상 파일 존재까지 확인함.

수정 파일: `openpilot/selfdrive/carrot/web/src/features/logs/screenshots.js`, `openpilot/selfdrive/carrot/server/features/tools/dispatcher.py`, `openpilot/selfdrive/ui/onroad/hud_renderer.py`, `openpilot/selfdrive/ui/onroad/record_button.py`(전체 교체).

미완료: carrot-ryu 반영 스크립트(`44cha_carrot_ryu_fixes.ps1`) 사용자 실행 대기. 실행 후 3건 모두 실기기 재검증 필요(사진 목록이 크래시 없이 뜨는지, delete all videos가 사진까지 지우는지, 녹화 중 버튼이 실제로 깜빡이는지).



## 43차 (완료 -- devnotes/실제 상태 괴리 확인 + HANDOFF·CURRENT_STATUS 42차 기준 정리)

사용자가 "지침을 전체 읽고 다시" + "레포도 다시 읽고" 요청 -> 4절 0~3번 절차(지침 문서 -> HANDOFF -> CURRENT_STATUS -> carrot-ryu 최신 commit)를 처음부터 재수행. 그 과정에서 이 대화가 몰랐던 41차(로그탭 새로고침 아이콘)·42차(온로드 원형 녹화 버튼)가 다른 세션에 의해 이미 push 완료돼 있음을 발견했으나, HANDOFF.md/WIP.md 본문은 여전히 "push 미실시"로 남아있는 괴리를 확인(16절 사례, 핵심 발견 27로 CURRENT_STATUS.md에 기록).

검증 방법: `git ls-remote`로 carrot-ryu(`4f81ab75`)·carrot-ryu-note(`8bbc7c82`) HEAD 확인 -> commit patch로 메시지/변경 파일 확인 -> raw.githubusercontent.com으로 실제 파일 내용까지 재조회(index.html의 `#logsRefreshButton`, hud_renderer.py의 `RecordButton` 배선 5곳) -- 텍스트 문구가 아니라 실제 파일 내용으로 반영을 확인함.

반영: CURRENT_STATUS.md(carrot-ryu HEAD 줄, 41차/42차 bullet, 코드 수정 현황 24~25번, 다음 작업 순서, 핵심 발견 27)와 HANDOFF.md(전체)를 42차 기준으로 바로잡음. 코드 변경은 없음, devnotes만 갱신.

교훈: 코드 push와 devnotes push가 시간차를 두고 이루어지는 세션 구조상, devnotes 스크립트 작성 시점의 "미확인" 문구가 이후 실제로 반영된 뒤에도 갱신되지 않은 채 남을 수 있음. 다음 세션은 devnotes 텍스트를 그대로 믿지 말고 항상 `git ls-remote`부터 재확인할 것.

## 42차 (코드 작성 완료 -- 반영 스크립트 실행 대기 -- 온로드 화면에 원형 녹화(Record) 버튼 추가)

사용자 요청: 온로드 화면의 스크린샷 캡쳐 버튼 옆에 동그라미 모양 녹화 버튼을 추가. 한 번 누르면 빨간색으로 점등(녹화 중), 다시 누르면 빨간색이 꺼지고 투명 원(대기 중)으로 표시.

기존 화면녹화 기능(carrotweb Home 탭 `btnRecordToggle` + carrotMan `RECORD` 명령)은 이미 `ScreenRecord` bool param + `layouts/main.py`의 `_handle_carrot_record_cmd`로 구현돼 있었으나, 온로드 UI(디바이스 화면) 자체에는 트리거 버튼이 없었음. 이번 회차는 그 세 번째 트리거로 온로드 UI에 버튼을 추가.

구현:
- 신규 파일 `openpilot/selfdrive/ui/onroad/record_button.py`: `ScreenshotButton`과 동일한 스타일(검정 반투명 배경 원)의 `RecordButton` 위젯. 클릭 시 `ui_state.params.get_bool("ScreenRecord")`를 읽어 반전값을 `put_bool_nonblocking`으로 씀(carrotweb `car.js`의 `toggleRecord()`와 동일한 패턴). 그리기 상태는 로컬 토글 플래그가 아니라 매 프레임 `gui_app.is_recording()`을 직접 읽어 반영 -- carrotweb/carrotMan 등 다른 경로로 녹화 상태가 바뀌어도 항상 실제 상태와 일치.
  - 녹화 중: 안쪽에 빨간 원(`rl.draw_circle`, 사용자 요청의 "빨간색 점등")
  - 대기 중: 안쪽에 흰색 원 테두리만(`rl.draw_circle_lines`, 사용자 요청의 "투명 원")
- `hud_renderer.py` 5곳 수정(문자열 블록 치환): import 추가, `UIConfig`에 `record_button_size`/`record_button_gap` 필드 추가, `__init__`에 `RecordButton` 인스턴스 생성, `_render()`에서 스크린샷 버튼 오른쪽(간격 30px)에 배치해 렌더, `user_interacting()`에 눌림 상태 포함(사이드바 토글 오탭 방지, 27차 이전 더블탭 제스처 폐기 사유와 동일 원칙).

참고 조사 (반영 안 함): 사용자가 `ryujmin97/openpilot`의 `c3-ms-dev` 브랜치(폐기 프로젝트, 코드 참조용으로만 유지)에 이 기능이 있는지 확인 요청 -> Qt 기반 구형 UI(`selfdrive/ui/qt/screenrecorder/`, OMX 하드웨어 인코더)로 지금 carrot-ryu의 pyray 기반 UI와 프레임워크 자체가 달라 이식 대상 아님, 사용자도 "신경 안 써도 됨"으로 확인. `c3-ms-dev`는 1절이 문서화한 브랜치 구성(carrot-ryu/carrot-ryu-note)에 없는 브랜치이나, 사용자 확인으로 조치 불필요 처리.

세션 번호 관련 주의: 이 회차를 준비하던 중 원래 "41차"로 라벨링했으나, 세션 종료 시점에 다른 세션이 이미 "41차"(carrotweb 로그탭 새로고침 아이콘, commit `da6ad815`)를 실제로 push 완료한 것을 `git ls-remote` 재확인으로 발견해 "42차"로 재번호. 코드 자체(record_button.py/hud_renderer.py)는 그 41차 커밋과 겹치는 파일이 없어 영향 없음(41차 커밋 파일: index.html/style.css/runtime.js/생성 번들, 이번 42차 파일: record_button.py/hud_renderer.py).

검증: `py_compile` 통과(2개 파일). 반영 스크립트의 5개 anchor 블록 모두 GitHub 실제 최신 `hud_renderer.py`(41차 커밋 `da6ad815` 기준, 41차가 이 파일을 건드리지 않아 27차 세션 시점 내용과 바이트 단위로 동일함을 diff로 확인) 대비 정확히 1회씩만 매치함을 Python으로 재현해 확인, 치환 결과가 Claude가 로컬에서 직접 작성한 최종본과 바이트 단위로 동일함을 diff로 확인(6절, 9절, 20절). **실기기 검증은 미실시** -- 반영 스크립트 실행 자체가 이번 세션에서 아직 안 됨(12절 원칙: 사용자가 실행해 push하기 전까지 미반영으로 간주).

미완료 (다음 세션 이월):
1. [최우선] `push_carrot_ryu_42cha.ps1` 실행 여부 확인 -- `git ls-remote` + commit patch로 실제 push 재확인 필요.
2. 실기기에서 버튼 위치(스크린샷 버튼 오른쪽, 간격 30px)가 화면 밖으로 벗어나지 않는지, 버튼을 눌렀을 때 실제로 빨간 원 점등/소등이 정상 동작하는지 확인.
3. 41차(logs 탭 새로고침 아이콘) 실기기 검증도 여전히 미실시 상태로 남아있음(아래 HANDOFF.md 이월 목록 참고).

## 41차 (완료 -- 코드 작성/빌드/테스트, push 및 실기기 검증은 다음 세션 이월) -- carrotweb 로그탭 새로고침 아이콘 추가

사용자 요청: 로그탭에서 대시캠/화면녹화 탭바(`#logsTabs`)와 hamburger 메뉴(`#logsMenu`) 사이에 새로고침 아이콘 버튼을 추가하고, 누르면 현재 화면 내용이 새로고침되도록.

완료:
- `index.html`: `#logsTabs`와 `#logsMenu` 사이에 `#logsRefreshButton`(원형 화살표 SVG) 마크업 삽입. Replace-Block anchor 1회 매치 확인.
- `style.css`: `.logs-refresh`/`.logs-refresh__button`/`.logs-refresh-icon` 추가(기존 `.logs-menu__button`과 동일한 `--menu-trigger-size` 박스 크기 공유), 클릭 시 0.6s 회전 애니메이션(`is-spinning` 클래스), 저해상도(<=620px) 미디어쿼리의 `min-height: 38px` 규칙에도 `.logs-refresh__button` 함께 반영.
- `runtime.js`: `refreshActiveLogsTab()`(활성 탭이 화면녹화면 `loadScreenrecordVideos()`+`loadScreenshots()`, 대시캠이면 `loadDashcamRoutes()`를 모두 non-silent 기본 옵션으로 재호출 -- 즉 목록을 처음부터 다시 조회) + `bindLogsRefresh()`(클릭 중 버튼 disable, `is-spinning` 토글) 추가, `bindLogsPage()` 초기화부에 `bindLogsRefresh()` 호출 삽입.
- 빌드 산출물 재생성: `npm install && npm run build`(`node build.mjs`)로 `js/generated/logs.js`/`css/generated/logs.css`/`generated/asset-manifest.json` 3종을 함께 갱신 -- 소스만 바꾸고 번들을 안 바꾸면 실기기에는 반영되지 않으므로 필수(9절).

검증:
- 5개 Replace-Block anchor(index.html 1, style.css 2, runtime.js 2) 모두 carrot-ryu 최신 clone(`bdde8326` 기준) 대상 파이썬 재현으로 정확히 1회 매치 확인.
- `node --check`로 `runtime.js`/`js/generated/logs.js` 문법 확인(PASS).
- `npm test`(logs_tabbar_contract 4개 포함, 로그/대시캠/화면녹화/스크린샷 관련 32개) 전부 pass.
- 별도의 신선한 clone에 동일 Replace-Block 로직과 `npm install && npm run build`를 처음부터 재현해, 스크립트로 전달할 최종 파일이 최초 작업본과 바이트 단위로 동일함을 확인(39차 핵심 발견 26 이후 습관).
- **carrot-ryu push 자체는 이 세션 종료 시점까지 사용자가 아직 실행하지 않음 -- 다음 세션은 반드시 GitHub에서 실제 반영 여부부터 재확인할 것(5절/16절).**

미완료 (다음 세션 이월):
1. [신규, 최우선] `add_logs_refresh_button_41cha.ps1` 실행(push) 여부 GitHub에서 직접 재확인 -- carrot-ryu HEAD가 41차 커밋으로 갱신됐는지 `git ls-remote`+commit patch로 확인.
2. [신규] 새로고침 아이콘 실기기 검증: 위치(탭바-hamburger 사이)가 의도대로 보이는지, 클릭 시 회전 애니메이션과 실제 목록 재조회(대시캠/화면녹화 각각)가 정상 동작하는지.
3. [이월] 사진 업로드 UI(체크박스/전체선택/다운로드/전송)가 `bdde8326`(39cha-fix) 반영 후 에러 없이 정상 렌더링되는지 실기기 재확인.
4. [이월] 화면녹화 탭 "영상" 업로드 UI(36차 구현분) 자체 동작 검증 -- 실제 화면녹화 파일 확보 후 재검증 필요.
5. [이월] 37차 락 수정의 실제 동시성(거의 동시 호출) 재현 검증.
6. [이월] 34차 도로명-신호과속 같은 줄 배치 확인(신호과속 배지가 나타나는 구간에서).
7. [이월] 28~30차 레이아웃 정밀 재검증(육안 확인만 완료).
8. [이월] 실차 재검증(8~41차 코드 변경 전부, 12절 원칙) -- 계속 이월.
9. [이월] 실기기에서 직접 디버깅: 배포된 tools.js에 "web-gdrive-connect" 문자열 실제 존재 여부.
10. [이월] test_web_upload.py 실제 실행해 낡은 테스트 수 확인 -> 데드코드 3개 + 대응 테스트 삭제/갱신.
11. [이월] docs/carrot_web_upload.md 갱신(Drive 기준).
12. [이월] run_upload_segments() 설계 변경 실사용 문제 없는지 재확인.
13. [이월] carrot-ms 모델 셀렉터 코드 분석 착수(6차 이후 계속 미착수).

교훈: 이번 요청은 코드 변경 자체는 작았지만(마크업 1곳, CSS 2곳, JS 2곳) esbuild 번들(`js/generated/logs.js`, 110KB+)을 텍스트로 직접 전달하는 대신 스크립트가 clone 직후 `npm install && npm run build`를 실행해 번들을 그 자리에서 재생성하도록 구성함 -- 39차(`.gitignore` 주석: "device serves this source tree directly and does not run Node at startup")에서 확인된 대로 생성 번들은 커밋되어야 하지만, 전달 스크립트 자체가 무겁게 그 내용을 내장할 필요는 없다는 것이 이번에 실증됨. 향후 esbuild 번들이 걸리는 변경은 이 패턴(소스만 Replace-Block, 번들은 스크립트 내 `npm run build`로 생성 후 커밋)을 기본으로 고려할 것.

## 40차 계속2 (완료 -- devnotes 반영 스크립트 here-string 종료 버그로 인한 조용한 실패 수정)

직전 "40차 계속" 반영 스크립트를 실행한 뒤 `git ls-remote` + commit patch로 재확인하는 과정(16절)에서, `HANDOFF.md`가 완전히 빈 파일(0바이트)로 덮어써졌고 `CURRENT_STATUS.md`는 전혀 갱신되지 않은 채 옛 내용 그대로 남아있음을 발견.

원인: PowerShell here-string(`@'...'@`)은 종료 마커 `'@`가 반드시 줄 맨 앞에 와야 인식되는데, `CURRENT_STATUS.md` 내용을 담은 here-string이 줄바꿈 없이 끝나 `'@`가 이전 줄 텍스트 끝에 바로 붙어버림. PowerShell이 이를 종료로 인식하지 못해, 그 뒤에 이어지는 실제 스크립트 코드(`[System.IO.File]::WriteAllText($StatusPath, ...)` 호출부터 `$HandoffNew = @'` 변수 대입, HANDOFF.md 전체 내용, 그다음 here-string의 정상 종료 마커까지)를 전부 "문자열 리터럴"로 통째로 삼켜버림. 그 결과 (1) `CURRENT_STATUS.md`를 실제로 쓰는 코드 자체가 문자열 안에 파묻혀 실행되지 않아 파일이 그대로 남았고, (2) `$HandoffNew` 변수가 끝내 정의되지 않은 채(`$null`) `HANDOFF.md`에 써져 빈 파일이 됨. 에러 없이 `git commit`/`git push`까지 정상 진행되어 "Push complete"로 보고됨 -- 18절이 경계해온 "조용한 실패" 패턴의 새로운 변종.

수정: devnotes 반영 스크립트를 생성할 때 here-string에 담기는 모든 내용 블록이 줄바꿈으로 끝나도록 보장하는 절차를 추가(내용 끝에 개행이 없으면 자동 추가). 이번 세션에서 이 방식으로 재생성한 스크립트로 `HANDOFF.md`를 복구하고 `CURRENT_STATUS.md`를 실제로 갱신함.

교훈: 9절의 anchor 1회매치 검증처럼, here-string으로 파일 전체를 교체하는 "전체 교체형" 작업도 실행 전에 "내용이 줄바꿈으로 끝나는지"를 기계적으로 검증할 필요가 있음. 이 문제는 anchor 매칭 문제(20차 핵심 발견)나 인코딩 문제(21차)와는 다른, PowerShell here-string 구문 자체의 함정이라 별도로 기록.

## 40차 계속 (완료 -- 경로안내 박스 상하 여백 실기기 검증 + 39cha-fix push 재확인)

직전 40차 HANDOFF.md가 "fix_carrot_ryu_39cha.ps1 미실행"으로 남겨뒀던 1순위 미완료 항목을 이번 세션에서 재확인: `git ls-remote`로 carrot-ryu HEAD가 `bdde832654a6...`임을 확인하고, `github.com/.../commit/bdde8326....patch`로 커밋 메시지("39cha-fix: import missing formatRelativeEpoch in screenshots.js")와 변경 파일(screenshots.js/logs.js/asset-manifest.json)을 직접 조회해 실제 반영을 확인(16절, API rate limit로 REST 엔드포인트가 막혀 ls-remote+patch 조합으로 우회).

이어서 사용자가 제공한 실기기 스크린샷(제네시스 DH 2015, 20:14:25 캡처)으로 27차 이후 계속 이월되던 "우측하단 경로안내 박스 상하 여백" 항목을 처음으로 실기기에서 확인. "교차로"(제목) → 회전아이콘/895m → "도착: 286.1km" → "193.6분(23:28)" → "용산2로" 순서가 27차 설계대로 나타났고, 34차 `content_shift_y=20` 적용 이후 상단/하단 여백이 균등하게 보임(12절, 이 항목의 첫 실차 검증 사례).

미확인: 사진 업로드 UI(체크박스/전체선택/다운로드/전송) 자체 동작은 이 스크린샷에 나타나지 않아 별도 확인 필요(39cha-fix가 실제로 크래시를 해소했는지도 미확인, 다음 세션 최우선 이월).

## 40차 (완료 -- 39차 사진 업로드 UI 실기기 크래시 원인 규명 및 수정: formatRelativeEpoch import 누락)

사용자가 39차 코드 반영 후 실기기에서 "구현안됨"(체크박스/툴바 없이 예전 가로 썸네일만 보임)이라고 보고. 우선 GitHub carrot-ryu HEAD를 확인해 39차 커밋(`797fca2e`)이 정상 push됐음을 확인했고, 사용자가 디바이스에서 `git rev-parse HEAD`/`git status`/`git branch --show-current`를 직접 실행한 결과도 `797fca2e`·clean·`carrot-ryu`로 일치 -- 즉 코드 반영 자체는 문제 없었음. 사용자가 화면을 다시 캡처해 보낸 스크린샷에서 실제 에러 토스트 `formatRelativeEpoch is not defined`를 확인하며 진짜 원인을 특정.

원인: 39차에서 신규 작성된 `screenshots.js`가 `runtime.js`의 `formatRelativeEpoch`를 import하지 않음(같은 패턴을 쓰는 `dashcam.js`/`screenrecord.js`는 정상 import). 사진 행 렌더링 중 `ReferenceError`가 발생해 목록 전체가 비어버리고 에러 토스트만 노출되는 것이 실제 증상이었음 -- 디바이스/캐시/빌드 반영 문제가 아니라 순수 코드 버그.

수정: `screenshots.js` import문에 `formatRelativeEpoch` 1개 식별자만 추가(1줄 변경). 이 저장소를 별도로 shallow clone해 로컬에서 직접 수정 → `npm install` → `node build.mjs`로 재빌드 → `py_compile`(hud_renderer.py, routes.py) 통과, `node --check` 통과, `npm test` 737/737 통과 확인. 재빌드로 `js/generated/logs.js`(esbuild가 import 추가로 인해 파일 전역의 축약 식별자를 재배정 -- 문자열 블록 치환이 아닌 전체 교체로 처리) 및 `generated/asset-manifest.json`(logs.runtime 해시 1줄만 변경, anchor 치환)이 함께 변경됨.

반영: `screenshots.js`/`asset-manifest.json`은 1줄 anchor 치환(카운트=1 검증 포함), `logs.js`는 전체 교체 방식의 PowerShell 스크립트(`fix_carrot_ryu_39cha.ps1`, UTF-8 BOM, `--config core.autocrlf=false`, 임시폴더 자동삭제 포함)로 준비해 사용자에게 전달. **이번 세션 종료 시점까지 사용자가 스크립트를 실행하지 않았으므로, 다음 세션은 carrot-ryu 최신 commit이 이 수정 커밋으로 갱신됐는지 반드시 재확인할 것(16절 원칙).**

교훈: "코드/디바이스 반영 문제로 보이는 증상"이 실제로는 반영과 무관한 순수 JS 런타임 에러일 수 있음 -- 반영 상태(git HEAD/status)를 아무리 정밀하게 검증해도 실제 브라우저 에러 메시지를 직접 확인하기 전까지는 근본 원인을 알 수 없었음. 다음부터 "화면이 예전 그대로다"류 보고를 받으면, 반영 상태 확인과 별개로 최대한 빨리 실제 에러 화면 캡처를 요청하는 것이 효율적.


## 39차 (완료 -- 코드 반영, 실기기 검증은 다음 세션 이월) -- 화면녹화 탭 사진 업로드 UI 신규 구현 + 경로안내 박스 상하 여백 통일

사용자가 38차 미확인 항목("화면녹화 탭 업로드 UI 자체 동작")의 의도를 정정: 녹화본이 아니라 화면캡쳐 사진 업로드를 원했던 것. 사진 목록에 체크박스(앞)/다운로드+전송 버튼(뒤), 목록 상단에 전체선택/다운로드/전송 툴바를 신규 요청. 추가로 34차에서 이월됐던 경로안내 박스 상하 여백 불균형(제목 위 여백은 넉넉한데 하단 배지가 경계에 닿음)도 함께 요청.

완료:
- `screenshots.js` 전면 재작성 -- 기존 썸네일 전용 가로 스트립(클릭 시 원본 열기만 가능)을 `screenrecord.js`(영상 목록) 컨벤션과 동일한 세로 행(row) 목록으로 교체. 행별 체크박스(`select-screenshot`) + 다운로드/전송 버튼, 선택 상태(Set) 관리, 전체선택/선택다운로드/선택전송 툴바, 업로드 확인/결과 다이얼로그, 다운로드는 `<a download>` 순차 클릭 방식(팝업 차단 회피, screenrecord와 동일 패턴).
- `runtime.js` -- `screenshots.js` import 확장(downloadScreenshots/uploadScreenshots/screenshotsSelectedPhotos/toggleScreenshotSelectAll/toggleScreenshotSelection 추가), 사진 목록 click/change 위임에 download-screenshot/upload-screenshot/select-screenshot 핸들러 추가, 신규 `screenshotsToolbar` click 위임(전체선택/선택다운로드/선택전송) 추가.
- `index.html` -- `screenshotsToolbarWrap`/`screenshotsToolbar` 마크업 추가(screenrecordToolbar와 동일 구조, `dashcam-selection-row` 클래스 재사용).
- `style.css` -- `.screenrecord-photos`를 가로 썸네일 스트립(overflow-x)에서 세로 행 리스트(overflow-y, flex-column)로 전환, `.screenrecord-photos-wrap`에 `max-height: 46vh` + 내부 스크롤 적용(사진이 많아도 영상 목록을 화면 밖으로 밀어내지 않도록), 이제 안 쓰는 `.screenrecord-photo`/`.screenrecord-photo:hover`/`.screenrecord-photo img`(구 썸네일 버튼) 규칙 삭제.
- `js/translations/{ko,en,zh}.js` -- `screenshot_upload`, `no_selected_photos` 2개 키 추가(3개 언어).
- `server/features/screenrecord/routes.py` -- `POST /api/screenrecord/photo/upload` 신규 엔드포인트 추가. 기존 `api_screenrecord_upload()`(영상용)를 `find_photo()` 기준으로 그대로 미러링(동기, 파일별 순차, job/폴링 없음). 라우터에 등록.
- `openpilot/selfdrive/ui/onroad/hud_renderer.py` -- `_draw_turn_info_hud()`에 `content_shift_y = 20` 상수 도입, 제목/route=숫자/도착 거리·시간/회전아이콘(따라서 신호과속·도로명 배지까지 연쇄) 기준 y좌표 4곳에서 이 값을 일괄로 뺌. 요소 간 상대 간격(95/175/190 등)은 그대로 유지한 채 절대 기준선만 위로 이동. 실기기에서 여백이 여전히 안 맞으면 이 상수 하나만 조정하면 되도록 주석에 명시.

검증:
- `python3 -m py_compile`(hud_renderer.py, routes.py) 통과.
- `node --check`(runtime.js, screenshots.js, ko/en/zh.js) 통과.
- `npm install && node build.mjs`로 생성 번들(`js/generated/logs.js`, `css/generated/logs.css`, `generated/asset-manifest.json`) 재생성 확인.
- `npm test` 737/737 통과.
- 반영 전 사전 검증: 코드 반영 스크립트를 별도 클론(HEAD `c01d9ec`, 37차와 동일)에 대해 Python으로 anchor 로직을 재현해 시뮬레이션 실행, 문자열 anchor 17곳 모두 정확히 1회 매치 확인 후 실제로 적용 → py_compile/node --check/build/npm test까지 전부 재확인(9절 사전 dry-run, 새 세션에서 재검증).
- 실차/실기기 검증: 미실시(12절 원칙) -- 사진 업로드 UI 자체 동작(선택/전송/다운로드)과 경로안내 박스 여백 실측은 다음 세션 이월.

주의사항:
- `.screenrecord-photo`(단수, 구 썸네일 버튼) 클래스는 완전히 삭제됨. 사진 행은 이제 `.screenrecord-row`(영상 목록과 공유)를 그대로 재사용하므로 별도 CSS 스타일링이 필요 없었음.
- `content_shift_y`는 `_draw_turn_info_hud()` 지역 상수이며 Params 등 외부 설정이 아님 -- 실기기에서 상하 여백을 추가로 조정하려면 코드 값(현재 20)을 바꿔야 함.


## 38차 (완료 -- 36차/37차/34차 실기기 검증 1차 진행, 일부 확인/일부 이월) -- 사용자 제보 스크린샷 9장 분석

사용자가 실기기 스크린샷 9장(온로드 HUD 1장, 대시캠 탭 로그 전송 플로우 3장, 화면녹화 탭/도구 탭/햄버거 메뉴 3장, 구글드라이브 앱 2장)을 제공. 37차 HANDOFF 미완료 1번(36차 변경사항 실기기 검증)과 4번(34차 UI 실기기 재확인)을 함께 검증. 코드 변경 없음, devnotes만 갱신.

확인됨:
- 당근서버 라벨 오표시 버그(36차 dashcam.js 수정) -- 대시캠 탭 세그먼트 메뉴의 "로그 전송" 확인 다이얼로그가 "구글 드라이브"로 정상 표시됨. 실제 전송도 "전송 완료 1/1"(qcamera 1개+rlog 1개, 11.2MB)로 성공.
- 햄버거 메뉴 화면녹화 탭 분기(36차 runtime.js 수정) -- 화면녹화 탭에서 우측상단 메뉴를 열면 "로그 메뉴"에 정렬 옵션만 있고 "최근 로그 업로드" 섹션이 없음. 35차 증상 3(탭 무관 대시캠 전용 업로드) 해소 확인.
- Drive 폴더 단일화 -- 내 드라이브에 "CarrotWeb Logs" 폴더가 1개만 존재, 그 안에 이번 세션 업로드 3건(대시캠 로그 전송 1건 14:52, tmux로 추정되는 항목 2건 14:48/14:50)이 모두 같은 폴더로 들어감.
- 34차 UI(도착 텍스트 40->32 축소) -- 경로안내 박스에서 회전아이콘 초록박스와 "도착: 3.0km / 6.7분(14:54)" 텍스트가 겹치지 않음, 육안상 정상.

미확인/이월(근거 포함):
- 화면녹화 탭 업로드 UI(체크박스/전체선택/다운로드/전송) 자체 동작 -- 실제 화면녹화 파일이 없어("화면녹화 기록이 없습니다") 테스트 대상 부재, 사진 스트립만 존재. 녹화본이 생긴 뒤 재검증 필요.
- 37차 락 수정의 실기기 동시성 재현 -- 업로드 3건이 14:48/14:50/14:52로 수 분 간격이 있어 "거의 동시 호출" 레이스 조건을 재현한 테스트가 아님. 폴더 1개만 생성된 것은 정황상 문제없어 보이나, 락이 실제로 레이스를 막았다는 확정적 증거로 보고하지 않음(12절 원칙).
- 34차 도로명-신호과속 같은 줄 배치 -- 스크린샷 촬영 시점에 신호과속 배지가 화면에 없어(과속/신호 구간 아님) 같은 줄 비교 불가. 도로명("대덕대로989번길")은 경로안내 박스 바깥쪽 하단(IP 주소와 같은 줄)에 표시되고 있어, WIP 34차에 기록된 "박스 안쪽" 목표와 실제로 일치하는지 신호과속 배지가 뜨는 구간에서 추가 확인 필요.
- 28~30차 레이아웃 -- 확인한 스크린샷 범위에서는 특별한 깨짐/겹침 없음(육안 확인 수준, 좌표 단위 정밀 검증 아님).

부가 발견: 37차 push 직후 raw.githubusercontent.com 브랜치-head 조회에서 캐시 지연이 재현됨(핵심 발견 21, 33차와 동일 패턴) -- commit-pinned raw URL(`/{sha}/...`)로 우회해 실제 최신 내용 확인. 상세: FINDINGS.md 2026-09-15(38차) 항목.
## 37차 (완료 -- gdrive_upload.py Drive 폴더 중복생성 레이스컨디션 수정) -- 35차 핵심발견23 증상4 근본조치

35차에서 "추정, 미확정"으로 이월됐던 Drive 폴더 2개 생성 문제(핵심 발견 23 증상 4)의 원인을 코드 조사로 확정하고 최소 수정으로 고침. 화면녹화 탭 실기기 검증(36차 이월 1번)은 이번 세션에서 다루지 않음(사용자가 2번 항목부터 진행하기로 결정).

원인: gdrive_upload.py의 _ensure_folder()가 "캐시확인 -> 이름으로 검색 -> 없으면 생성 -> 캐시기록" 순서를 락 없이 수행함(TOCTOU 레이스). 같은 프로세스(웹서버) 안에서 대시캠 탭 전송과 햄버거 메뉴 "최근 로그 업로드"처럼 서로 다른 업로드 job이 거의 동시에 이 함수를 호출하면, 첫 호출의 Drive API 왕복(수백ms)이 끝나기 전에 두 번째 호출도 캐시 미스로 판단해 files.list가 둘 다 빈 결과를 받고 둘 다 새 폴더를 생성함.

수정: gdrive_upload.py에 모듈 레벨 `_folder_lock = asyncio.Lock()` 추가, `_ensure_folder()` 본문 전체(캐시확인~생성~캐시기록)를 이 락으로 감쌈. 문자열 블록 치환 3곳(import 추가, 전역 상태 변수 추가, 함수 본문 교체), 각각 파일 내 정확히 1회 매치 확인 후 반영.

검증:
- `python3 -m py_compile` 통과.
- 목(mock) 기반 동시성 테스트 직접 작성해 실행: aiohttp 세션을 50ms 지연이 있는 가짜 객체로 교체하고 `asyncio.gather`로 `_ensure_folder()`를 동시에 2번 호출. **수정 전** 코드로는 실제로 폴더 생성 API가 2번 호출되는 것을 재현 확인(버그 재현 성공). **수정 후** 코드로는 1번만 호출되고 두 호출 모두 같은 folder_id를 반환함을 확인(수정 확인). 이 테스트 스크립트는 이번 세션의 1회성 검증 산출물이며 toolkit에 저장하지 않음.
- 실기기 검증: 미실시(로컬 코드 조사 + 목 테스트만 진행, 실제 Drive API 대상 동시성 재현은 하지 않음. 12절 원칙에 따라 실차 검증으로 표기하지 않음).

알려진 한계(그대로 이월, FINDINGS 37차 참고): 이 락은 프로세스 내부에서만 유효함. `carrot_man.py`의 `send_tmux_web()`은 웹서버(`server/app.py`)와 별도 프로세스로 실행되므로, 그쪽에서 발생하는 tmux 진단정보 전송과 웹서버 쪽 대시캠/화면녹화 업로드가 우연히 겹치는 경우까지는 이번 수정으로 막지 못함. 근본 해결안(폴더 id를 Params에 영구 저장)은 사용자와 논의 후 이번 세션에서는 범위 밖으로 확정(31차 발견 이후 두 번째로 "최소수정 vs 근본수정" 중 최소수정을 선택한 사례).
## 36차 (완료 -- 화면녹화 탭 업로드 UI 구현 + 버그 수정 3건) -- 35차 스펙 반영

35차에서 확정된 스펙(화면녹화 탭 체크박스/전체선택/다운로드/전송)을 구현하고, 함께 발견됐던 버그 2건과 UX 문제 1건을 같이 수정함.

완료:
- screenrecord.js: 선택 상태(Set), 행별 체크박스 + 전송 버튼, 상단 툴바(전체선택/선택다운로드/선택전송), 업로드 확인/결과 다이얼로그, 동기 순차 업로드(개별 파일, 사용자 확정 스펙), <a download> 순차 클릭 방식 다운로드(팝업 차단 회피), 새로고침 시 사라진 파일 선택 자동 정리.
- runtime.js: 체크박스 change/전송 버튼 click 위임, 신규 screenrecordToolbar 클릭 위임(전체선택/선택다운로드/선택전송).
- index.html: screenrecordToolbarWrap/screenrecordToolbar 마크업 추가.
- style.css: .screenrecord-toolbar-wrap 패딩 규칙 추가(체크박스/버튼은 기존 클래스 재사용).
- server/features/screenrecord/routes.py: POST /api/screenrecord/upload 신규 -- gdrive_upload.upload_file_resumable()을 파일별 순차 호출, job/폴링 없이 결과 배열 반환.
- js/translations/{ko,en,zh}.js: download_selected/screenrecord_upload/no_selected_recordings 3개 키 추가.
- dashcam.js: "당근서버" 라벨 오표시 버그 수정 -- dashcamUploadConfirmHtml() targetLabel 분기에 gdrive 케이스 추가(35차 원인 특정, 이번 세션에 수정).
- runtime.js logsMenuChoices(): 햄버거 메뉴 "최근 로그 업로드" 항목을 화면녹화 탭에서 숨김 처리(사용자 확정 -- 대시캠 탭에서는 그대로 유지). "항상 대시캠 세그먼트만 업로드"하는 설계 문제(35차 발견)에 대한 사용자 결정 반영.
- npm install && node build.mjs로 esbuild 번들(js/generated/logs.js, css/generated/logs.css, generated/asset-manifest.json) 재생성 확인, npm test 737/737 통과 확인(이전 세션에서 중단됐던 빌드 검증을 이번 세션에서 완료).

검증: 정적 문법 검사(node --check) + 빌드(node build.mjs) + 전체 테스트(npm test, 737/737 pass) 통과. 실차 검증: 미실시.

주의사항:
- 이 회차는 직전 세션(도구 호출 한도로 중단, carrot-ryu에 커밋된 적 없음)에서 로컬로만 작성됐던 코드를 이어받아, 새 세션에서 GitHub carrot-ryu(당시 HEAD 9fdefb3d) 위에 다시 clone하여 재검증(문법/빌드/테스트)까지 마친 뒤 반영한 것. 커밋 히스토리 불연속은 없음.
- 생성 번들(js/generated/*, css/generated/*, generated/asset-manifest.json)은 기기가 소스가 아닌 이 파일들을 직접 서빙하므로 소스와 함께 커밋이 필수 -- 코드 반영 스크립트가 npm install && node build.mjs를 실행해 자동 재생성 후 커밋함.

다음 세션 후보:
- Drive 폴더 2개 생성 원인 확정 조사(우선순위 낮음)
- 이번 세션 변경사항(화면녹화 업로드, 라벨 수정, 햄버거 메뉴) 실기기 검증
- 34차 UI 변경 실기기 재확인, 28~30차 레이아웃 실기기 재검증
- test_web_upload.py 실행 + 데드코드 3개 정리
- docs/carrot_web_upload.md 갱신
- carrot-ms 모델 셀렉터 코드 분석 착수

## 35차 (진행 중 -- 코드 변경 없음, 조사/스펙 확정만) -- 화면녹화 탭 업로드 기능 조사 및 신규 스펙 확정

- 사용자가 실기기 스크린샷 3장(대시캠 탭 "로그 전송" 다이얼로그 1세그먼트/10.8MB, 5세그먼트/51.5MB, 화면녹화 탭 "화면녹화 기록이 없습니다" 화면)과 Drive "내 드라이브"에 "CarrotWeb Logs" 폴더가 2개 생성된 스크린샷을 제보. 이를 바탕으로 32차 Drive 연동 이후 실기기 첫 검증 결과를 코드 조사로 분석함.
- **핵심 발견 1 (당근서버 라벨 오표시)**: `web/src/features/logs/dashcam.js`의 `dashcamUploadConfirmHtml()` 1277~1279행, targetLabel 분기가 `uploadTarget === "toss"` 여부만 검사하고 else는 무조건 `web_log_upload_target_carrot`("당근서버")을 반환 -- `"gdrive"` 케이스가 없음. 실제 업로드 자체는 `getWebSettingByKey("log_upload_target")`로 정상적으로 gdrive를 타는 것으로 보이나(1653~1661행), 확인 다이얼로그의 표시 라벨만 어긋남. ko.js에 `web_log_upload_target_gdrive: "구글 드라이브"` 키가 웹설정 드롭다운용으로 이미 존재해서, 매핑만 추가하면 되는 간단한 수정.
- **핵심 발견 2 (화면녹화 탭 업로드 기능 전무)**: `screenrecord.js`(영상 목록)와 `screenshots.js`(사진 스트립) 둘 다 조회/썸네일/재생/다운로드만 구현돼 있고, 선택 상태(selection state)나 업로드 호출이 코드에 전혀 없음. 서버 쪽 `server/features/screenrecord/routes.py`에도 조회/썸네일/다운로드 엔드포인트뿐 업로드 엔드포인트가 없음. 대시캠 탭(`dashcam.js`)에만 선택+전송 UI가 구현돼 있는 상태.
- **핵심 발견 3 (햄버거 메뉴가 탭 무관 대시캠 전용)**: 로그 페이지 상단 햄버거 버튼(`logsMenuButton`, `runtime.js`)은 대시캠/화면녹화 탭 구분 없이 페이지 전역에 떠 있음. 메뉴의 "최근 로그 업로드(2/5/10)" 항목은 `uploadRecentDashcamSegments()` -> `/api/dashcam/recent` -> `uploadDashcamSegments()`로 이어져 **무조건 대시캠 세그먼트(qcamera/rlog)만 업로드**함. 화면녹화 탭에서 열어도 화면녹화 영상과는 무관 -- 사용자가 제보한 "화면녹화에서 전송" 스크린샷(qcamera/rlog 카운트)이 이 경로로 설명됨.
- **Drive 폴더 2개 생성 (원인 추정, 미확정)**: `gdrive_upload.py`의 `_ensure_folder()`는 이름으로 폴더 검색 후 없으면 생성하며, 인메모리 캐시(`_folder_verified_cache`, 300초)만 사용. 핵심 발견 1의 개별 세그먼트 전송과 핵심 발견 3의 햄버거 메뉴 업로드가 각각 별도로 `_ensure_folder()`를 호출했고, 캐시 만료 또는 Drive 검색 인덱스의 생성 직후 지연(eventual consistency)으로 두 번째 호출이 방금 만든 폴더를 못 찾아 새로 만들었을 가능성이 유력. 코드 조사만으로 확정할 수 없어 미해결로 이월.
- **사용자 확정 스펙 (화면녹화 탭 신규 기능, 다음 세션 최우선)**:
  1. 영상목록 표시 (현재도 목록 렌더링 로직 자체는 있으나 선택/전송 UI가 전혀 없는 상태 -> 아래 UI를 추가)
  2. 각 항목: 파일명(저장 시간 포함) 앞에 체크박스, 뒤에 다운로드 버튼 + 전송 버튼
  3. 목록 상단: 전체선택 버튼, 그 옆에 다운로드 버튼 + 전송 버튼
- 이번 세션에서 진행 중이던 것: `dashcam.js`의 기존 선택 UI(체크박스 렌더링, 선택 상태 관리, 클릭 디스패치 구조, 업로드 확인 다이얼로그)를 화면녹화 탭에 동일 컨벤션으로 이식하기 위해 `index.js`/`web/src/shared/` 디렉터리 구조까지 확인하던 중 세션 종료 -- 코드 작성 전.
- 실차/실기기 검증: 해당없음(이번 세션은 코드 변경 없이 분석/스펙 확정만 진행, 12절 원칙).
## 34차 (완료 -- 코드 수정 1건 GitHub 반영 완료) -- 경로안내 박스 도착 텍스트 크기/도로명 위치 수정

- 사용자 요청 2건: (1) 도착 거리/시간 텍스트가 회전 아이콘 초록박스와 겹쳐 보임 -> 글자 크기를 40에서 32로 축소(arrival_size 변수 신규 도입, eta_size 자체는 다른 요소용으로 그대로 유지). (2) 일반도로 도로명 텍스트가 박스 아래 경계를 벗어나 보임 -> 신호과속 배지와 동일한 y좌표 계산식(회전 아이콘 초록박스 하단 by+115 기준)으로 이동해 박스 안쪽, 신호과속 문구와 같은 줄 위치로 조정.
- 변경 파일: `openpilot/selfdrive/ui/onroad/hud_renderer.py` 2곳, 문자열 블록 치환(Replace-Block, 9절)으로 반영. commit `9fdefb3d`(부모 `789667f7`, 33차 ko.js 수정 위에 쌓임).
- **[핵심 발견 22 참고] 세션 번호 충돌**: 이 세션은 시작 시점에 32차까지만 인지한 상태로 작업해 코드 주석/커밋 메시지에 `[33차]`로 표기했으나, 실제로는 그 사이 다른 경로로 33차(ko.js 문구 수정, commit 789667f7)가 이미 진행/기록돼 있었음. 코드에 이미 커밋된 `[33차]` 주석 문구는 과거 기록이므로 수정하지 않고(18절, 기존 기록 임의 수정 금지 원칙과 동일하게 취급), devnotes 상의 회차 번호만 실제 순서에 맞춰 34차로 기록함.
- 반영 전 검증: 문자열 anchor 블록 2곳 모두 push 직전 최신 GitHub 내용과 정확히 1회 매치 확인(사전 dry-run). 반영 후 검증: `github.com/.../commit/9fdefb3d.diff` 및 commit-pinned raw URL로 실제 내용 재조회, 두 블록 모두 정상 반영·`py_compile` 문법 검사 통과 확인.
- 실차/실기기 검증: 미실시(정적 레이아웃 변경, 12절 원칙).
## 33차 (완료 -- 코드 수정 1건 GitHub 반영 완료) -- ko.js Google Drive 클라이언트 유형 안내 문구 수정

- 32차 HANDOFF.md 미완료 3번(31차부터 이월된 버그): ko.js의 `web_gdrive_client_id_desc`가 "데스크톱 앱 유형"으로 안내하지만, gdrive_upload.py 주석/실제 요구사항은 "TV 및 제한된 입력이 있는 기기" 유형임을 수정.
- 변경 파일: `openpilot/selfdrive/carrot/web/js/translations/ko.js` 1곳(584번째 줄), commit `789667f7`(부모 `c704371a`, 32차).
- 반영 방식: 소규모 문자열 치환(9절), 치환 전 원본 라인이 파일 내 정확히 1회 매치되는지 확인 후 진행.
- **검증 관련 신규 관찰**: `github.com/.../commit/789667f7.diff`로는 즉시 정상 반영이 확인됐으나, `raw.githubusercontent.com`은 `?nocache=<timestamp>` 쿼리를 붙여도 한동안 수정 전 내용을 계속 반환함(캐시 지연). 상세: FINDINGS.md 2026-09-15(33차) 항목.
- 실차/실기기 검증: 미실시(UI 안내 문구 텍스트 변경, 우선순위는 낮음 -- 필요 시 다음 실기기 검증 때 함께 확인).
## 32차 (devnotes 사후 정리 -- 코드 반영은 이미 GitHub에 완료된 상태로 확인) -- Google Drive drive.file 스코프 + 폴더 자동생성 복귀

- 세션 시작 시 4절 0~3번 절차로 carrot-ryu 최신 커밋을 확인한 결과, `c704371a`(부모 `34bb41bc`, 메시지: `32cha: gdrive drive.file scope + folder auto-create revert (c3-ms-dev, 31cha device-flow block fix)`)가 이미 GitHub에 반영돼 있었음. 이 커밋에 대한 devnotes(WIP/HANDOFF/CURRENT_STATUS)는 남아있지 않아, 이번 세션에서 `github.com/.../commit/<sha>.diff`로 실제 변경 내용을 직접 조회해 사후 정리함(16절 상황, 24차·30차와 유사한 "코드 반영과 devnotes 갱신이 다른 시점에 이루어진" 사례).
- 이 커밋은 31차(FINDINGS 핵심 발견 19)에서 사용자에게 제시한 3가지 대안 중 **(a) drive.file 스코프 + 폴더 자동생성 방식(c3-ms-dev 원본)으로 복귀**를 선택해 반영한 것으로 보임.
- 변경 파일: `openpilot/selfdrive/carrot/gdrive_upload.py` 1개뿐(diff로 확인).
- 변경 내용:
  1. `DRIVE_SCOPE`: `.../auth/drive`(전체) -> `.../auth/drive.file`(비민감, 앱이 만든 파일만 접근).
  2. 고정 `DRIVE_FOLDER_ID` 상수 제거, `DRIVE_FOLDER_NAME = "CarrotWeb Logs"` 신설.
  3. `_verify_folder()`(ID로 존재/휴지통/타입만 확인) -> `_ensure_folder()`(이름으로 검색, 없으면 생성)로 교체.
  4. `_folder_verified_cache` 구조 변경: `{"ok": bool}` -> `{"id": str|None}`.
  5. `api_gdrive_status` 응답에서 `folder_id` 필드 제거(고정 ID 개념 자체가 없어짐).
  6. 파일 상단 docstring을 새 설계(31차 근거, drive.file 복귀 사유, 폴더 자동생성 동작)에 맞춰 갱신.
- 31차에서 확인된 "Device Authorization Grant가 전체 drive 스코프를 정책적으로 차단"하는 제약(핵심 발견 19)을 정면으로 우회하는 방향.
- 실차/실기기 검증: 미실시. 실제 Drive 연결 버튼을 눌러 새 폴더가 정상 생성/재사용되는지는 아직 확인되지 않음 -- 기존에 만들어둔 폴더(구 DRIVE_FOLDER_ID)는 이제 사용되지 않고, 앱이 "CarrotWeb Logs"라는 새 폴더를 자동 생성/검색하는 구조로 바뀌었으므로 반드시 실사용 테스트 필요.
## 31차 (진행 중 -- 코드 변경 없음, Google Drive 연동 설계 근본 제약 발견) -- OAuth 연결 실패 원인 조사: Device Flow가 Drive 스코프를 구조적으로 차단

- 사용자가 실기기에서 "웹 설정 > 로그 업로드" Google Drive 연결을 시도하며 스크린샷 3장 제공. 순서대로 (1) 클라이언트 ID에 "http://"가 붙은 값 입력 + "Google Drive가 연결되어 있지 않습니다"/OAuth client not found 화면, (2) 클라이언트 보안 비밀번호까지 입력 후 "The OAuth client was not found." 에러, (3) 정상 형식의 Client ID로 재시도 후 "Invalid device flow scope: https://www.googleapis.com/auth/drive" 에러.
- 1차 가설(클라이언트 ID 값 자체의 형식 문제) 확인 시도 -> 사용자가 이미 정상 형식으로 재입력했음에도 동일 계열 에러 지속.
- 2차 가설: ko.js 번역 문구(web_gdrive_client_id_desc, 23차 추가)가 "데스크톱 앱 유형"이라고 안내하지만, gdrive_upload.py 설계 주석(15차)은 "TV 및 제한된 입력이 있는 기기" 유형을 필수로 요구함 -> UI 문구가 실제 요구사항과 다른 버그로 확인. 다만 사용자는 이미 올바른 유형(TV/제한된 기기)으로 발급받아 적용했다고 확인 -> 이 불일치가 이번 에러의 직접 원인은 아님.
- 3차 가설: OAuth 동의 화면(Data Access)에 auth/drive 스코프가 실제 등록됐는지 확인 요청 -> 사용자 확인 결과 이미 등록돼 있음 -> 배제.
- 4차(확정): 웹 검색으로 독립된 다수 개발자 사례를 확인한 결과, Google이 OAuth Device Authorization Grant(기기 인증 흐름) 자체에서 전체 Drive 스코프(https://www.googleapis.com/auth/drive)를 수년째 구조적으로 차단하고 있음을 확인함(클라이언트 유형, 동의 화면 스코프 등록 여부와 무관하게 항상 거부됨). Calendar 등 다른 API 스코프는 동일 흐름에서 정상 동작하는 것으로 보아, Drive 전체 스코프 특유의 제약으로 판단.
- 설계 충돌 확인: gdrive_upload.py(15차)는 원래 drive.file(비민감) 스코프를 쓰다가, 사용자가 미리 만들어둔 고정 폴더(DRIVE_FOLDER_ID)에 ID로 직접 접근하기 위해 의도적으로 전체 drive 스코프로 넓혔음(주석에 명시). 이 설계 변경이 바로 device flow에서 차단되는 조합이었음 -> 현재 설계로는 애초에 성공할 수 없는 구조였던 것으로 확인됨.
- 사용자에게 3가지 대안 제시, 결정 대기 중(상세 내용은 FINDINGS.md 참고):
  1. drive.file 스코프로 되돌리고 폴더를 앱이 직접 생성하는 방식(c3-ms-dev 원본 _ensure_folder())으로 복귀 -- device flow 유지 가능성 높으나 미검증, 기존에 만들어둔 폴더는 사용 불가.
  2. Device flow를 포기하고 표준 Authorization Code Flow(콤마 기기 자체 웹서버가 redirect URI 수신)로 전면 재설계.
  3. Google Drive 대신 다른 저장 수단으로 전환.
- 이번 세션은 조사만 진행, 코드/carrot-ryu 커밋 없음. carrot-ryu HEAD는 30차와 동일(34bb41bc).

## 30차 (완료 — 코드 수정 1건 GitHub 반영 완료) — 경로안내 박스 route=/도착 텍스트 위치 재조정

- 사용자 요청: (1) "route=숫자" 글자 크기를 28→32로 키우고, 세로 위치를 회전 아이콘 초록박스 상단(box_y+95)과 텍스트 상단이 맞도록 이동. (2) "도착:"/ETA 텍스트가 박스 우측 경계(edge_x = box_x+box_w-6)를 넘어 삐져나오는 문제를 pad(24px)만큼 안쪽으로 들여 해결. (3) 위 변경에 맞춰 도착/ETA 텍스트를 route= 한 줄 아래(eta_top = box_y+175)에서 상단기준(right_top)으로 다시 배치.
- 적용한 수정(carrot-ryu, selfdrive/ui/onroad/hud_renderer.py만, commit 34bb41bc): route_debug_text 크기/좌표 수정, edge_x를 box_x+box_w-6에서 box_x+box_w-pad로 변경, eta_top 변수 신설(box_y+175), 도착/ETA 정렬을 right_bottom→right_top으로 변경.
- 반영 방식: 문자열 블록 치환(Replace-Block, 20차 원칙) 2곳, GitHub 최신(67a8e10, 29차) 대비 각각 정확히 1회 매치 확인 후 진행.
- 실차 검증: 미실시(정적 코드 변경 단계, 12절 원칙). 실기기 스크린샷으로 재확인 필요(HANDOFF.md 참고).

## 29차 (완료 — 코드 수정 1건 GitHub 반영 완료) — 경로안내 박스 제목/ETA/신호과속 배지 위치 조정

- 사용자가 실기기 사진 한 장을 제공하며 세 가지 레이아웃 조정 요청: (1) "교차로"(제목) 텍스트를 위로 이동(box_y+55 → box_y+38)해 회전 아이콘 초록박스와 겹치지 않게. (2) "도착:"/ETA 텍스트를 pad(24px) 인셋이 아니라 박스 우측 경계(box_x+box_w-6)에 거의 붙여(끝맞춤) 표시. (3) "신호과속" 배지를 박스 맨 아래 고정 위치(box_y+box_h-35, 다른 하단 상태줄과 겹쳐 보이던 위치)에서, 회전 아이콘 초록박스 바로 아래(by+115 기준, 배지 텍스트 실측 높이로 역산한 label_y)로 이동.
- 적용한 수정(carrot-ryu, selfdrive/ui/onroad/hud_renderer.py만, commit 67a8e10): 제목 y좌표 수정, edge_x 변수 신설, bx/by 계산을 if x_turn_info 블록 밖으로 이동(신호과속 배지 위치 계산에도 재사용하기 위함), 신호과속 label_y를 by+115 기준 역산 방식으로 변경.
- 반영 방식: 문자열 블록 치환(Replace-Block) 4곳, GitHub 최신(cc73f629, 28차) 대비 각각 정확히 1회 매치 확인 후 py_compile 통과 확인.
- **devnotes 절차 문제(중요, FINDINGS 참고)**: 이 회차의 HANDOFF.md는 "사용자가 스크립트를 아직 실행하지 않음(미반영)"으로 작성됐으나, 실제로는 사용자가 스크립트를 실행해 GitHub에 정상 반영된 상태였음. 다음 세션(30차) 시작 시 4절 절차에 따라 carrot-ryu 커밋 로그를 직접 재조회하며 발견함. 상세 원인/재발 방지는 FINDINGS.md "2026-09-15(30차) — HANDOFF.md 미반영 기록과 실제 GitHub 상태 불일치" 항목 참고.
- 실차 검증: 미실시(정적 코드 변경 단계, 12절 원칙).

## 28차 (완료 — 코드 수정 1건 GitHub 반영 완료) — 경로안내 박스 높이 축소 및 요소 재배치

- 사용자 요청: 27차에서 475x495로 확대했던 경로안내 박스의 높이를 495→400으로 축소하고, 그에 맞춰 "도착: 거리"/ETA 텍스트를 route=숫자 바로 아래(우측끝맞춤)로 옮기고, 회전 아이콘 초록박스를 박스 가로 중앙이 아니라 좌측(상단 제목과 동일한 pad 기준선)에, 세로는 박스 정중앙에 오도록 재배치.
- 적용한 수정(carrot-ryu, selfdrive/ui/onroad/hud_renderer.py만, commit cc73f629): box_h 495→400, 도착/ETA 텍스트를 좌측하단 정렬(_draw_text_left_bottom)에서 우측끝맞춤 상대좌표(draw_text_ui_style, align="right_bottom")로 이동, bx 계산을 박스 가로중앙(box_x+box_w//2)에서 좌측 pad 기준(box_x+pad+80)으로, by를 box_y+200에서 box_y+190으로, 초록박스 크기를 160x230→160x210으로 축소.
- 반영 방식: 문자열 블록 치환(Replace-Block) 3곳, GitHub 최신(5f5e49d0, 27차) 대비 각각 정확히 1회 매치 확인 후 py_compile 통과 확인.
- 실차 검증: 미실시(정적 코드 변경 단계, 12절 원칙).

## 27차 (완료 — 코드 수정 1건 GitHub 반영·재확인 완료) — 우측하단 경로안내 박스 크기/레이아웃 개편

- 사용자가 실기기 스크린샷(20260913_183642.jpg) 제공. 요청: 우측하단 경로안내 박스를 좌측하단 디버그 박스(475x495)와 동일 크기로, "도착: 2.4분(18:39) / 0.9km" 순서를 "도착: 0.9km" -> "2.4분(18:39)" 2줄로, 글자크기는 신호과속 라벨과 동일(40)로, 박스가 세로로 길어진 만큼 각 요소가 겹치지 않게 재배치, "route=숫자"는 신호과속이 떠도 겹치거나 사라지지 않도록 항상 우측끝맞춤으로 별도 표시.
- 원인 분석: 우측하단 박스는 _draw_turn_info_hud()(기존 790x300 고정). "route=숫자"는 carrot_serv.py의 self.debugText(f"route={{route_speed:.1f}}")가 carrotMan.szPosRoadName(도로명)에 공백으로 이어붙어 들어오는 값이며, 기존 코드는 if 신호과속(sdi_descr) / elif 도로명 구조라 신호과속이 뜨면 route= 값이 도로명과 함께 통째로 사라지는 구조였음(원인 확정, 스크린샷과 코드 대조로 확인).
- 적용한 수정(carrot-ryu, selfdrive/ui/onroad/hud_renderer.py만, 최소 변경, commit 5f5e49d0):
  1. import re 추가.
  2. _format_eta_text() -> _format_eta_time_text()로 이름 변경 + "도착:" 라벨 제거(거리 줄과 분리해 두 번째 줄 전용), _split_road_name_debug() 신규 헬퍼 추가(정규식 route=[-0-9.]+ 로 도로명과 route= 디버그 값을 분리).
  3. _draw_turn_info_hud() 레이아웃 재구성: 박스 475x495(좌하단 디버그 박스와 동일), 상단에 안내제목(좌)+route=숫자(우측끝맞춤, 항상 별도 줄), 중단에 회전아이콘+거리, 중하단에 "도착: 거리"/"N.N분(HH:MM)" 2줄(글자크기 40), 하단에 신호과속(또는 도로명) 배지 — 신호과속 배지와 route=숫자가 물리적으로 분리되어 있어 항상 함께 보임.
- 반영 방식: 문자열 블록 치환(Replace-Block, 20차 원칙) 3곳, 치환 전 GitHub 최신(d338afb7) 대비 정확히 1회 매치 확인 후 진행. Python 문법 검증(ast.parse) 통과.
- 실행 이슈 1건 발생 -> 해결: 최초 실행 시 Windows Git의 core.autocrlf로 clone된 파일이 CRLF로 변환되어 있어, LF 기준으로 만든 치환 블록이 import-re 단계에서 0회 매치로 실패 -> 15절/18절/20절 원칙대로 아무 것도 건드리지 않고 안전하게 중단(커밋/푸시 이전이라 carrot-ryu 영향 없음, 임시 폴더도 정상 삭제됨 확인). git clone에 --config core.autocrlf=false 추가 + 읽은 직후 CRLF->LF 정규화 안전장치를 넣어 재작성한 스크립트로 재실행, 정상 반영됨(d338afb7..5f5e49d0).
- 반영 후 재확인: raw.githubusercontent.com으로 carrot-ryu HEAD(5f5e49d0)의 hud_renderer.py를 직접 재조회해, 의도한 변경 외 차이가 없음(diff 1곳, 의도한 주석 라벨 변경)과 ast.parse 문법 통과를 확인함(16절/20절 원칙).
- 사용자에게 변경 후 UI 레이아웃을 설명하는 목업(SVG, 실제 기기 픽셀/폰트와는 다른 개략도)을 별도로 렌더링해 전달함.
- 실차 검증: 미실시(정적 코드 변경 단계, 12절 원칙).


## 26차 (진행 중 — 실기기 검증 결과와 정적 코드 리뷰 결과가 모순되어 원인 미확정, 실기기 디버깅 다음 세션으로 이월) — Google Drive 연결 UI 미노출 재조사

- 세션 시작: 지침 문서 22차 버전 확인 -> HANDOFF.md/CURRENT_STATUS.md(25차 상태, carrot-ryu HEAD d338afb7) 확인 후 진행.
- 사용자가 오늘(2026-09-14) 실기기에서 찍은 스크린샷 10장 제공(14:47~18:41). 내용: 웹 설정 > 로그 업로드에서 업로드 서버를 "구글 드라이브"로 선택한 화면, 화면녹화 세그먼트 전송 시도 및 결과.
- 관찰 1: "웹 설정 > 로그 업로드" 카드의 업로드 서버 드롭다운은 당근서버/토스서버/구글드라이브 3개 옵션이 정상 표시되고 구글드라이브가 선택돼 있음. 그런데 그 아래에는 23차에서 추가한 Client ID/Secret 입력란(web-gdrive-connect 컴포넌트) 대신 "당근서버 주소"/"토스서버 주소" 입력란이 그대로 보임.
- 관찰 2(신규 발견): 화면녹화 탭에서 세그먼트 "전송" 시도 시 다이얼로그 라벨이 "당근서버"로 표시됨(업로드 서버는 구글드라이브로 설정된 상태인데도). 최종적으로 "Google Drive가 연결되어 있지 않습니다" 에러가 뜸 -> 실제 라우팅은 gdrive로 가는 것으로 추정되나 다이얼로그 라벨 텍스트만 하드코딩된 "당근서버"를 쓰고 있는 것으로 보임(코드 위치는 아직 조사 안 함).
- carrot-ryu 최신(commit d338afb7) 소스를 codeload tarball로 직접 받아 정적 코드 리뷰 수행:
  - web/src/features/tools/web_settings/schema.js: log_upload 그룹에 web-upload, web-gdrive-connect 두 항목 모두 정상 존재.
  - web/src/features/tools/web_settings/components.js: web-gdrive-connect 컴포넌트가 Client ID/Secret 입력란을 포함해 정상 등록돼 있음. isVisible을 별도 정의하지 않아 기본값(빈 settingKeys -> every()가 vacuous true)이 적용되므로 이론상 항상 visible이어야 함.
  - web/js/generated/tools.js(esbuild 번들): 위 로직이 소스와 완전히 동일하게 반영돼 있음을 확인 -- 예전에 있었던 "esbuild 번들 재생성 누락" 유형 문제는 이번 소스/번들 비교로는 재현되지 않음.
  - web/css/generated/tools.css: .web-gdrive-settings 관련 셀렉터가 전부 정상 포함돼 있고 display:none 등 숨김 규칙 없음.
  - web-upload 컴포넌트의 당근서버/토스서버 주소 필드는 코드상 target === "carrot" / target === "toss" 일 때만 hidden이 해제되도록 짜여 있어, 스크린샷처럼 target이 "gdrive"인 상황에서는 두 필드가 반드시 숨겨져야 함. 그런데 스크린샷은 정반대(두 필드는 보이고 gdrive 전용 필드는 안 보임) -- 정적 코드 리뷰 결과와 실기기 스크린샷이 모순됨.
- 결론(미확정): 코드 자체에서는 문제를 찾지 못함. 실기기 브라우저가 최신 tools.js/tools.css 번들을 실제로 로드하고 있는지 의심됨(브라우저 캐시, 또는 scons 빌드 시 esbuild 재생성 누락 가능성). 사용자가 이번 세션 중에는 실기기 디버깅(터미널로 배포된 파일 내용 확인, 강제 새로고침/시크릿모드 재현 테스트)을 진행할 수 없어 다음 세션으로 이월.
- 이번 세션은 코드/devnotes 커밋 변경 없이 조사만 진행. carrot-ryu HEAD는 25차와 동일하게 d338afb7 유지.


## 25차 (완료 -- 코드 수정 1건 GitHub 반영 확인, 조사 1건 추가 발견) -- LOG_UPLOAD_TARGETS "gdrive" 누락 수정 + 데드코드/낡은 테스트 의심 발견

- 24차 계속2에서 발견한 확실한 버그(server/services/web_settings.py의 LOG_UPLOAD_TARGETS = {"carrot", "toss"}에 "gdrive" 누락)를 사용자 승인 후 수정. 문자열 치환(소규모 변경, 9절) 방식으로 anchor 1회 매치 검증 -> py_compile 검증 -> 스크립트 전달 -> 사용자 실행 -> commit d338afb7 push 확인 -> raw.githubusercontent.com으로 실제 파일 내용까지 직접 재조회해 `LOG_UPLOAD_TARGETS = {"carrot", "toss", "gdrive"}`로 반영됨을 확인(5절/16절).
- 수정 과정에서 사용자가 "관련 죽은 코드도 같이 삭제하면 안 되나" 요청 -> 조사 결과, 처음 보고했던 것과 달리 web_upload.py의 `UPLOAD_TARGETS`/`selected_upload_settings()`는 carrot_man.py의 `_tmux_toss_only()`(Discord/carrot_logs 진단 전송 시 "Toss 전용이면 스킵" 게이트, 958/1054줄에서 실제 호출)가 사용하는 **살아있는 코드**로 정정 확인됨. 반면 `web_upload.py`의 `tmux_web_target()`과 `server/features/dashcam/upload.py`의 `resolve_upload_target()`/`upload_target_settings()`는 프로덕션 호출자가 없고 테스트에서만 참조되는 **진짜 죽은 코드**로 확인됨.
- 이 3개 함수를 삭제하려고 `server/tests/test_web_upload.py`의 관련 테스트를 조사하던 중, `test_dashcam_upload_completion_notifies_web_server_and_discord`(397번째 줄 부근)가 `upload_jobs.upload_folder_to_web`/`upload_jobs.send_web_upload_complete`를 monkeypatch하는데, 이 두 함수는 **16차(대시캠 업로드를 세그먼트별 HTTP 업로드에서 zip+Google Drive 단일 업로드로 전환)에서 이미 제거되어 현재 upload_jobs.py에 존재하지 않음**을 발견. `monkeypatch.setattr`은 대상 속성이 실존해야 하므로 이 테스트는 16차 이후 갱신되지 않은 채 이미 깨져 있을 가능성이 높음(테스트 스위트를 직접 실행해 확인하지는 못함, openpilot 전체 런타임 의존성 없이는 이 파일만 단독 실행이 어려움).
- 범위가 예상보다 커서(데드코드 3개 삭제 -> 관련 테스트 삭제 -> "16차 전환 이후 방치된 낡은 테스트 뭉치" 가능성) 10절(최소 변경)·17절(세션 크기 관리) 원칙에 따라, 이번 세션에서는 확실한 버그 수정(LOG_UPLOAD_TARGETS)만 반영하고 데드코드 삭제/낡은 테스트 정리는 사용자 결정에 따라 다음 세션으로 이월.
- 상세: FINDINGS.md 2026-09-14 "web_upload.py/dashcam upload.py 데드코드 및 test_web_upload.py 낡은 테스트 의심" 항목 참고.
## 24차 계속2 (완료 -- 조사만, 코드 미수정) -- Google Drive 연결 UI 입력란 미노출 문제 조사 + 리포지토리 외부 변경 사항 확인

- HANDOFF 우선순위 1번(Drive UI 입력란 미노출)을 조사함. 캐싱 가설은 기각(index.html이 매 요청 no-cache로 서빙되고 정적 자산 URL이 콘텐츠 해시로 재작성됨을 코드로 확인, 서비스워커 없음).
- 실제 소스 파일(schema.js/state.js/components.js/render.js)을 Node.js 환경에 그대로 옮겨 renderWebSettingsDialogHtml()을 직접 실행하는 시뮬레이션으로, web-gdrive-connect 컴포넌트가 Client ID/Secret 입력란을 포함해 정상적으로 HTML을 생성함을 실증. 렌더링 로직 자체에는 버그 없음.
- 대신 server/services/web_settings.py의 LOG_UPLOAD_TARGETS = {"carrot", "toss"}에 "gdrive"가 빠져 있는 확실한 버그를 발견(23차에서 프론트엔드 드롭다운에만 옵션을 추가하고 백엔드 enum choices는 갱신 안 함). 아직 코드 수정은 하지 않음 -- 사용자 승인 대기.
- 입력란이 안 보이는 증상 자체는 .web-settings-group__body{overflow:auto} 구조상 스크롤 필요일 가능성이 유력한 가설로 남음(실기기 확인 필요, 미검증).
- 상세: FINDINGS.md 2026-09-14 "Google Drive 연결 UI Client ID/Secret 입력란 미노출 문제 조사" 항목 참고.
- [리포지토리 확인] 이번 체크포인트 전에 GitHub 상태를 먼저 재확인하다가, carrot-ryu-note에 이 세션의 스크립트가 아닌 다른 경로(작성자 "Ryu <ryu@example.com>", PowerShell 스크립트 커밋의 작성자 "ryujmin97"과 다름)로 커밋 2개(7d44f2f, c7b86a0)가 더 있었음을 발견. 7d44f2f가 PROJECT_INSTRUCTIONS_carrot-ryu.md를 실수로 9차 시점 구버전으로 덮어썼고, c7b86a0이 같은 작성자에 의해 22차(98fad93) 상태로 직접 복구됨. 이 세션이 만든 24차 devnotes 커밋(33fcfcc)은 이 두 커밋 사이에 위치하며 PROJECT_INSTRUCTIONS_carrot-ryu.md를 건드리지 않아 영향 없음. 현재 문서는 22차 상태로 정상.
## 24차 계속 (완료 -- GitHub push 확인됨) -- carrot_ryu_24cha_photos.ps1 실행 결과 검증

- 세션 초반에는 carrot-ryu HEAD가 여전히 272834b(23차)로, 24차 스크린샷 스트립 반영 스크립트가 실행되지 않은 상태였음(위 "24차" 항목 참고).
- 세션 도중 사용자가 carrot_ryu_24cha_photos.ps1을 실행: npm 실행 정책 문제(PowerShell 스크립트 차단)를 `Set-ExecutionPolicy -Scope Process -ExecutionPolicy Bypass`로 우회 후 정상 실행. clone -> 문자열 블록 치환 반영 -> commit -> push까지 로그가 끝까지 출력됨(임시 폴더 자동 삭제 포함).
- 5절/16절/20절 원칙에 따라 로그만으로 "완료"로 단정하지 않고, api.github.com 및 raw.githubusercontent.com으로 직접 재조회: carrot-ryu HEAD가 a7a912c1로 갱신되었고, 신규 파일 openpilot/selfdrive/carrot/web/src/features/logs/screenshots.js가 실제로 브랜치에 존재함을 확인.
- 결론: 24차(화면녹화 탭 스크린샷 "사진" 스트립) 코드는 GitHub에 정상 반영 완료(commit a7a912c1). devnotes(HANDOFF.md/CURRENT_STATUS.md)도 이 확인 결과에 맞춰 함께 갱신.
- 남은 작업은 위 "24차" 항목의 "미완료" 목록 중 코드 반영 자체가 아닌 나머지 항목(Drive UI 입력란 미노출 조사, 실제 Drive 연결 테스트, 실주행 재검증 등)으로 이월.
## 24차 (완료 — 코드 반영 스크립트 준비, GitHub push는 사용자 실행 대기) — 화면녹화 탭에 스크린샷(.png) "사진" 스트립 추가

- 배경: 실기기에서 온로드 캡처 버튼(screenshot_capture.py)으로 찍은 .png 스크린샷이 웹 로그탭 어디에도 보이지 않는다는 사용자 보고. server/features/screenrecord/catalog.py의 build_videos()가 SCREEN_RECORDING_EXTS(영상 확장자만)만 스캔해서 .png가 애초에 목록화되지 않는 것이 원인으로 확인됨.
- 사진을 영상 목록(screenrecord.js, 가상 스크롤 적용)에 억지로 섞지 않고, 별도의 작은 비가상화 가로 스트립(screenshots.js, 신규 파일)으로 분리 구현. 사진 개수가 영상 개수보다 훨씬 적을 것으로 예상되어 가상 스크롤의 복잡도를 들일 가치가 없다고 판단.
- 백엔드: config.py에 SCREEN_RECORDING_PHOTO_EXTS(.png/.jpg/.jpeg) 추가, catalog.py에 build_photos()/find_photo()/photo_thumbnail_path() 추가(build_videos() 로직과 의도적으로 코드 공유하지 않고 병행 구현 — 영상 목록 동작이 회귀하지 않도록), routes.py에 /api/screenrecord/photos, /api/screenrecord/photo/thumbnail/{id}, /api/screenrecord/photo/{id}, /api/screenrecord/photo/download/{id} 4개 라우트 추가.
- 프론트엔드: screenshots.js(신규) — loadScreenshots()/renderScreenshots()/openScreenshot() 구현. index.html에 screenrecordPhotosWrap/screenrecordPhotosTitle/screenrecordPhotos 마크업 추가, style.css에 가로 스크롤 스트립 스타일 추가, runtime.js에 import + 로드 훅 4곳 + 클릭 핸들러 바인딩 추가. en/ko/zh 번역 3종에 screenrecord_photos_title/screenrecord_photos_load_failed 키 추가.
- 검증: carrot-ryu 실제 HEAD(272834b, 23차)를 그대로 clone하여 반영 스크립트(문자열 블록 치환, Replace-Block 패턴)를 실제로 적용 -> `npm install && node build.mjs`로 실제 빌드 실행 -> `python -m py_compile`로 수정된 .py 3개 확인 -> `node --test tests/logs_tabbar_contract.test.mjs` 통과 확인. 별도의 독립 시뮬레이션(원본 파일에 동일 블록 치환을 파이썬으로 재현)으로 모든 소스 파일이 바이트 단위로 일치함을 재확인.
- 전달 방식: 9절 규칙대로 코드 파일 여러 곳의 부분 수정이므로 diff가 아닌 문자열 블록 치환(Replace-Block) 방식으로 스크립트 구성, `.ps1` 파일 자체는 21차 규칙대로 UTF-8 BOM 포함하여 생성(`carrot_ryu_24cha_photos.ps1`). js/generated/logs.js, css/generated/logs.css, generated/asset-manifest.json 등 빌드 산출물은 스크립트 안에 손으로 담지 않고, 스크립트가 실제 `node build.mjs`를 실행해 생성하도록 함(18~20차에서 확인된 "손으로 만든 빌드 산출물이 실제 빌드 결과와 달라지는" 위험 회피).
- 미완료: 사용자가 아직 이 스크립트를 실행하지 않은 상태(24차 세션 시작 시 carrot-ryu HEAD가 여전히 272834b/23차인 것으로 GitHub에서 직접 확인). 즉 이번 회차의 코드 변경은 스크립트 형태로만 준비되었고 실제 push는 다음 확인 필요.
- 별도 미해결 이슈(23차 관련, 사용자 실기기 보고): Google Drive 연결 UI의 드롭다운은 "구글 드라이브"로 바뀌었으나 그 아래 Client ID/Secret 입력란과 연결 버튼이 나타나지 않음. 브라우저가 js/generated/tools.js의 이전 캐시를 물고 있을 가능성(캐시 버스팅 부재)이 유력하나 사용자의 하드 리프레시/시크릿창 확인으로 아직 미검증. 다음 세션 우선순위로 이월.

## 23차 (완료 — 코드 반영, GitHub push 완료, devnotes만 소급 기록) — web settings log_upload에 Google Drive 계정 연결 UI 추가

- 배경: 15~22차에 걸쳐 만든 gdrive_upload.py 백엔드(OAuth device flow, params_keys.h 등록까지 완료)에 대응하는 프론트엔드 연결 UI가 없어 사용자가 실제로 Drive 계정을 연결할 방법이 없었음. HANDOFF 미완료 우선순위 1번(15차부터 이월)에 해당.
- carrot-ryu commit 272834b8("23cha: web settings log_upload에 Google Drive 계정 연결 UI 추가 (web-gdrive-connect)")로 이미 GitHub에 반영되어 있었음을 24차 세션 시작 시 발견(devnotes에는 22차까지만 기록되어 있어 16절 해당 괴리 사례).
- 변경 파일(commit 272834b8 기준, GitHub에서 직접 diff 조회로 확인): web/src/features/tools/web_settings/schema.js, web/src/features/tools/web_settings/components.js(174줄 추가, 연결 버튼/Client ID·Secret 입력/인증 코드 표시 UI 구현 추정), web/src/features/tools/styles/base.css(45줄 추가), web/js/translations/{en,ko,zh}.js(각 15줄, 관련 UI 텍스트), 그리고 이에 따른 생성 산출물(tools.js/tools.css/asset-manifest.json) 갱신.
- 24차 세션에서 실제 코드 내용을 상세 분석하지는 않음(이번 세션의 초점은 스크린샷 기능이었음) — 다음 세션에서 필요 시 components.js/schema.js 상세 리뷰.
- 검증: 실차 검증 미실시. 실제 Drive 연결 테스트(OAuth 인증 코드 입력까지)도 미실시. 사용자가 실기기에서 확인한 결과 드롭다운은 바뀌었으나 입력란이 안 보이는 문제가 있었음(24차 항목 참고, 원인 미확정).

## 22차 (완료 — Google Drive 파라미터 등록 버그 발견 및 수정) — params_keys.h 미등록 수정 + PARAMS_REGISTRY.md 정리

- 배경: HANDOFF 다음 작업 후보 중 "PARAMS_REGISTRY.md 파라미터 3종 등록"(가장 가벼운 작업으로 사용자 선택)을 진행하기 위해 gdrive_upload.py의 실제 파라미터 이름(PARAM_CLIENT_ID/PARAM_CLIENT_SECRET/PARAM_REFRESH_TOKEN = CarrotGDriveClientId/CarrotGDriveClientSecret/CarrotGDriveRefreshToken)을 GitHub에서 직접 조회하던 중, openpilot/common/params_keys.h에 이 3개가 전혀 등록되어 있지 않은 것을 발견함.
- 원인: openpilot Params 클래스는 get()/put() 호출 시 내부적으로 checkKey()를 거쳐 params_keys.h에 등록 안 된 키면 UnknownKeyName 예외를 던짐(params_pyx.pyx 101-102줄 확인). gdrive_upload.py의 api_gdrive_device()(Drive 연결 시작 API)는 client_id 저장 단계(_params().put(PARAM_CLIENT_ID, ...))에서 이 예외를 그대로 받아 HTTP 500을 반환하도록 되어 있어, 15차부터 만들어온 Drive 연동 기능 전체가 "연결" 버튼을 누르는 순간부터 실패하는 상태였음(실제 기기 연결 테스트를 아직 안 해봐서 지금까지 미발견 — FINDINGS.md 참고).
- 사용자에게 즉시 보고(11절/16절 원칙) 후 승인받아, 원래 "문서화만" 범위였던 이번 작업을 "코드 수정(params_keys.h) + 문서화(PARAMS_REGISTRY.md)"로 확대함.
- 수정: params_keys.h에 다른 모든 Carrot* 파라미터와 동일한 패턴({PERSISTENT, STRING})으로 3줄 추가. 문자열 블록 치환 방식(CarrotExceptionDiscordWebhookUrl 줄을 앵커로 사용) 적용, carrot-ryu commit 48c2e081.
- 최종 GitHub 반영 확인: raw.githubusercontent.com으로 commit 48c2e081 시점의 params_keys.h를 직접 재조회하여 3줄이 정확한 위치(CarrotExceptionDiscordWebhookUrl 다음, CwebPushRecoveryBoot 이전)에 들어간 것을 확인 완료.
- PARAMS_REGISTRY.md에 이 3개 파라미터(이름/타입/용도)와 버그 경위를 함께 등록.
- 미완료: 실제 기기에서 Drive 연결(OAuth device flow) 테스트 — params_keys.h 수정으로 UnknownKeyName 예외는 해소됐으나, 실제 Google Cloud Console 클라이언트 ID/Secret 발급 및 콤마 기기에서의 연결은 여전히 미실시.

## 21차 (완료 — 소급 기록, 22차 세션에서 devnotes 누락 발견 후 작성) — 반영 방식을 .ps1 파일 생성 + BOM 필수로 개정

- 배경: PROJECT_INSTRUCTIONS_carrot-ryu.md 자체에는 21차 변경사항이 이미 반영되어 있었으나(carrot-ryu-note commit 21da1364, "docs: PROJECT_INSTRUCTIONS_carrot-ryu.md 21차 갱신"), WIP.md/HANDOFF.md/CURRENT_STATUS.md에는 21차 회차 기록이 전혀 없었음. 22차 세션 시작 시 이 불일치를 발견(16절 해당 사례), 사용자 확인 결과 "21차는 실제 있었던 세션, devnotes 기록만 누락"으로 확인되어 이번 커밋에서 소급 기록함.
- 변경 1: 9절 기본 전달 방식을 "스크립트 전체를 채팅에 붙여넣기"에서 ".ps1 파일로 생성해 전달 + 실행 명령만 채팅에 별도 안내"로 전환. 사유: 대용량 교체형 파일(PROJECT_INSTRUCTIONS_carrot-ryu.md 등)을 채팅에 직접 붙여넣는 것이 파일 생성 도구로 전달하는 것보다 무료 사용량(토큰)을 훨씬 많이 쓰는 것이 실측으로 확인됨.
- 변경 2: 9절·18절에 ".ps1 스크립트 파일에 한글 등 비ASCII 문자가 있으면 반드시 UTF-8 BOM을 포함해 생성한다" 규칙 추가. 사유: BOM 없는 .ps1 파일을 Windows PowerShell 5.1이 시스템 코드페이지(CP949 등)로 잘못 읽어, 쓰기 시점 인코딩 지정과 무관하게 스크립트 내 한글 문자열 자체가 이미 손상된 채 커밋되는 사고가 실제 발생함. BOM 포함 스크립트로 재실행해 정상 복구 확인.
- 22차부터 전달하는 모든 .ps1 파일은 이 규칙(파일 생성 도구로 전달 + UTF-8 BOM 포함)을 따름(이번 22차 params_keys.h 수정 스크립트도 BOM 포함하여 정상 실행 확인됨).## 18~20차 (완료 — 코드 반영, GitHub push 완료) — api_dashcam_upload_test를 Google Drive 연결 테스트로 전환

- 배경: HANDOFF 미완료 우선순위 1번(15차부터 이월). dashcam 업로드 연결 테스트 버튼(`/api/dashcam/upload/test`, routes.py의 `api_dashcam_upload_test`)이 16~17차에서 이미 Drive로 전환된 실제 업로드 경로와 달리 여전히 옛 Carrot/Toss 헬스체크(`check_web_upload_health`)를 가리키고 있었음.
- gdrive_upload.py에 `test_connection()` 추가: `is_connected()`가 refresh_token 존재 여부만 보는 것과 달리, 실제 access_token 갱신 + 대상 폴더 조회까지 왕복해 Drive 연동이 실제로 동작하는지 확인.
- routes.py: `api_dashcam_upload_test`를 `gdrive_upload.test_connection()` 호출로 교체, 옛 `web_upload`(check_web_upload_health/create_web_upload_session) import 및 `upload` 모듈 참조 제거.
- test_web_upload.py: 옛 toss/carrot 대상 관련 테스트 2개를 제거하고, 라우트 유일성 1개 + Drive 연결 성공/실패 케이스 2개로 교체.
- ⚠ [중요 교훈] 18차에서 diff/`git apply` 시도가 조용히 실패함 — 스크립트는 에러 없이 "적용 완료"로 끝났으나, 실제로는 patch 파일만 carrot-ryu에 잘못 커밋되고 의도했던 코드 변경은 전혀 반영되지 않음(정확한 근본원인은 사용자 PC를 직접 디버깅할 수 없어 확정 불가, `Apply-Patch` 함수 내부의 반복적인 `Push-Location`/`Pop-Location`이 셸 위치 추적을 꼬이게 한 것으로 추정). 17차(`corrupt patch`로 안전 중단)보다 더 나쁜, 조용히 실패하는 양상이었음.
- 19차에서 방식을 전면 교체: diff 대신 **파일 전체 텍스트에서 블록을 통째로 찾아 `.Replace()`로 치환**(치환 전 블록이 정확히 1회만 존재하는지 검증 후 치환, 아니면 중단), `Push-Location` 대신 `git -C $TempDir`만 사용. 이 방식으로 routes.py/test_web_upload.py 반영 및 18차에서 잘못 커밋된 임시 patch 파일 3개 정리까지 정상 완료(commit a44f1580).
- 다만 19차에서 gdrive_upload.py 하나는 Claude가 anchor 문자열을 잘못 옮겨 적어(`dict[str, Any]` vs 실제 `dict[str, dict[str, Any]]`) 매치 0회로 안전하게 중단됨 — `Replace-Block`의 "정확히 1회 아니면 중단" 안전장치가 의도대로 작동한 사례로, carrot-ryu에는 영향 없었음. 20차에서 GitHub 최신 원본과 anchor를 바이트 단위로 재대조하여 정정, 정상 반영 완료(commit ad055dd4).
- 최종 GitHub 반영 확인: raw.githubusercontent.com으로 ad055dd4 시점의 3개 파일을 모두 직접 재조회하여 `test_connection()` 정의, routes.py import/함수 교체를 확인 완료.
- 사용자 승인 하에 9절을 "코드 파일 부분 수정은 문자열 블록 치환을 기본으로, diff/git apply는 예외적 보조 수단으로" 개정.
- ⚠ [별도 발견] 이번 세션은 채팅에 9차 버전의 PROJECT_INSTRUCTIONS_carrot-ryu.md를 붙여넣은 채로 시작됐으나, 실제 carrot-ryu-note의 GitHub 버전은 이미 12차까지 진행되어 있었음. 20차에서 GitHub 버전(12차) 위에 이번 변경을 반영해 정정.
- ⚠ [WIP.md 반영 후속] 이 회차 자체가 처음 만들어진 20차 devnotes 반영 스크립트에서 `Prepend-Top` 함수에 CRLF 정규화가 빠져 있어("# WIP" marker가 `\r\n` 파일과 불일치) 실패했고, HANDOFF.md/CURRENT_STATUS.md/PROJECT_INSTRUCTIONS만 먼저 commit 450a1cd로 반영됨. 이 회차는 그 직후 별도 후속 커밋으로 반영됨.

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