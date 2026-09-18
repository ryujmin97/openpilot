Worker: Claude (85차 계속3, 새 세션에서 v2 스크립트 독립 재검증)
Date: 2026-09-18
Repository: ryujmin97/openpilot
Code Branch: carrot-ryu (base: `132d85bdfa493cb1d440b574dfd33e8220c2ad6c`, 84차2 BOM 제거 커밋까지 push 확인됨. 이번 세션은 그 위에서 항목 22+23+26 재검증, 반영 스크립트 실행/push 대기)
Note Branch: carrot-ryu-note (base: `fa038e080aacb74f4a26ded007509f0f809118d9`, 84차2 devnotes push 확인됨. 이번 세션은 그 위에서 HANDOFF/CURRENT_STATUS 정정 + WIP.md 85차 항목 추가, 반영 스크립트 실행/push 대기)
carrot-ms 마지막 검토/동기화 커밋(메시지 기준): `706efb47b81cf9cb02888ee536a156d8f1fc1d91`(61차 20절 리셋 베이스, 변경 없음).

작업:
세션 시작 체크포인트(`git ls-remote`)에서 carrot-ryu/carrot-ryu-note 두 브랜치 모두 이미 `132d85b`/`fa038e0`
(84차2, BOM 제거)로 push 완료돼 있음을 확인했다. HANDOFF.md(84차2 작성분)에는 이 push가 "미완료"로 남아
있었던 괴리(4절/16절)를 발견 -- 이번 파일로 바로잡는다. 이어서 사용자 요청으로 항목 22(39차,
`797fca2e`)/23(40차-fix, `bdde8326`)/26(44차 일부, `e2f35619`)의 화면녹화 탭 사진 업로드 UI +
content_shift_y + import 버그 2건을 현재 베이스(`132d85b`) 위에서 독립적으로 재적용/재검증했다.

완료:
1. 4절/16절 원칙대로 carrot-ryu/carrot-ryu-note 실제 GitHub 최신 상태를 `git ls-remote`+`git clone`으로
   확인, HANDOFF.md의 stale "미완료" 표기를 발견/정정.
2. 항목 22(`797fca2e`) 원본 patch를 `github.com/.../commit/797fca2e.patch`로 조회, 12개 파일 중
   11개는 `git apply` 1회 매치로 정상 적용. `routes.py` 1개는 파일 끝 컨텍스트 차이로 `git apply` 실패해
   Replace-Block으로 수동 삽입(`api_screenrecord_photo_upload` 함수 + 라우트 등록) -- 사용자가 채팅에
   첨부한 `routes.py`와 byte-exact 일치 확인.
3. 항목 23(`bdde8326`)의 `formatRelativeEpoch` import 누락 수정, 항목 26(`e2f35619`)의
   `formatLogBytes` import 누락 수정을 screenshots.js에 순서대로 이어 적용.
4. `npm install && node build.mjs`로 생성 번들 3종 재생성, `py_compile`(routes.py/hud_renderer.py)
   통과, `node --check` 통과, `npm test` 746/747 통과(유일 실패는 무관한 기존 `ar_projection_golden`
   환경 이슈).
5. 반영 스크립트 2개 작성: `85cha_item22_23_26_carrot_ryu.ps1`(코드, carrot-ryu), 이 스크립트는 신선한
   별도 clone에 대해 로직을 Python으로 시뮬레이션 재현해 검증본과 diff 없음까지 확인. 9절 "전달 전 필수
   자가검증 체크리스트" 전 항목(BOM/`core.autocrlf`/임시폴더/`Get-PythonCmd`+EOF공급/WriteAllText 무BOM/
   anchor 결과 재확인) 통과했다고 기록됐으나, 아래 [85차 계속]에서 이 중 CRLF 정규화 항목이 실제로는
   코드에 없었음이 드러남.
6. devnotes 반영 스크립트 `85cha_devnotes_carrot_ryu_note.ps1`(carrot-ryu-note) 작성: HANDOFF.md(이 파일,
   전체교체) + CURRENT_STATUS.md(전체교체, 항목 22/23/26 상태 갱신 + 85차 기록) + WIP.md(최상단 85차 항목
   삽입, anchor `# WIP\n\n## 84차 계속2` 1회 매치 + 결과 재확인).

**[85차 계속]** 사용자가 `85cha_item22_23_26_carrot_ryu.ps1`을 실행한 결과, 로그(특히 `git commit`/
`git push` 부분)를 사용자가 전달해 16절 원칙대로 확인한 결과 첫 Replace-Block 호출(`content_shift_y-decl`,
hud_renderer.py)에서 `Anchor match count != 1: got 0`으로 push 전에 안전하게 중단됐음을 확인
(commit/push 없음, 15절/18절 안전장치 정상 동작). 원인을 재현/규명: `git ls-remote`로 carrot-ryu HEAD가
`132d85b`(스크립트 실행 시점과 동일 베이스)임을 재확인 -> 그 SHA의 `hud_renderer.py`를 raw로 재조회해
스크립트의 `$old_hud_0` 앵커와 Python으로 바이트 단위 대조한 결과 정확히 1회 매치(앵커/베이스 자체는
문제 없음) -> 저장소 루트 `.gitattributes`에 여전히 `* text=auto`가 있음을 확인(63차에서 이미 규명된,
Windows Git 환경에서 `core.autocrlf=false`를 clone 시 줘도 체크아웃 시 CRLF로 변환될 수 있는 바로 그
조건) -> `Invoke-ReplaceBlock` 함수를 코드로 직접 읽어 63차 이후 9절에 명문화된 "매칭 전 CRLF->LF 정규화
병행"이 실제로는 빠져 있었음을 확인(HANDOFF.md/WIP.md에는 "9절 체크리스트 전항목 통과"로 기록됐었으나
그 항목의 실제 코드 구현이 누락됐던 것 -- 핵심 발견 44). `Invoke-ReplaceBlock`에 CRLF 정규화를 추가한
`85cha_item22_23_26_carrot_ryu_v2.ps1`로 교체, 신선한 독립 clone에 대해 12개 Replace-Block 앵커
(hud_renderer.py 5곳 + index.html 1곳 + en/ko/zh.js 각 2곳) 전부 1회 매치 + `py_compile`(hud_renderer.py)
+ `node --check`(en/ko/zh.js) 재통과를 Python 시뮬레이션으로 재확인.

미완료(다음 세션 최우선):
1. 사용자가 v2 스크립트(`85cha_item22_23_26_carrot_ryu_v2.ps1`)를 실행해 carrot-ryu에 push할 것 --
   v1(`85cha_item22_23_26_carrot_ryu.ps1`)은 실행하지 말 것(이미 실행 시도 -> 안전 중단됨, 다시 실행해도
   같은 이유로 다시 중단될 뿐임). devnotes 스크립트(`85cha_devnotes_carrot_ryu_note.ps1`)는 이 HANDOFF.md/
   CURRENT_STATUS.md 정정 내용(핵심 발견 44 포함)이 반영된 버전으로 다음 세션에서 갱신해 전달할 것 --
   원래 버전은 이번 실패/수정 경위가 빠져 있어 그대로 실행하면 devnotes가 실제 경위와 어긋나게 됨.
2. v2 push 확인되면 항목 22/23/26(사진 업로드 UI 체크박스/전체선택/다운로드/전송 동작 + content_shift_y
   여백)의 실차 검증 -- 이 프로젝트 역사상 이 경로는 한 번도 실차로 확인된 적 없음(12절).
3. 84차 sdi_descr 배지 실차 검증도 여전히 이월 상태(카메라/POI 근처 실주행에서 배지 안에 텍스트가 제대로
   들어오는지 확인).
4. (낮은 우선순위, 사용자 결정 대기) 제목(`tbt_main_text`)/도로명(`road_name_text`)도 동일한
   `get_text_draw_pos()` `left_bottom` 미구현 버그의 영향을 받고 있음 -- 근본 수정 여부 판단 필요.

검증: `git ls-remote`+`git clone`으로 두 브랜치 실제 HEAD 확인, 원본 커밋 patch 3개 직접 조회 후 재적용,
`py_compile`/`node --check`/`npm test`(746/747) 통과, 반영 스크립트 자체도 별도 clone 시뮬레이션으로
재검증. v1 실행 실패 이후 원인 규명 + v2 수정 + 재시뮬레이션 검증까지 완료(핵심 발견 44). 실차 검증:
미실시(이번 세션은 항목 22/23/26 코드 변경 자체가 아직 push되지 않음).

주의사항:
- HANDOFF.md의 "push 미완료" 표기가 실제 push 완료 상태를 못 따라간 패턴(핵심 발견 27/38)이 84차2에서도
  재발함 -- 세션 시작 시 4절 0단계(git ls-remote)를 반드시 먼저 수행해 devnotes 텍스트보다 GitHub 실제
  상태를 우선할 것.
- 직전 세션(84차 계속2)이 채팅에 남긴 "sandbox 검증 완료" 기록은 실제로는 GitHub에 반영되지 않은 상태였음
  -- 3절 원칙(GitHub 현재 상태 > 채팅에 붙여넣어진 과거 사본)대로 이번 세션은 그 기록을 그대로 신뢰하지
  않고 현재 베이스 위에서 원본 커밋부터 처음부터 재현/재검증했다. 결과는 일치했으나, 앞으로도 세션 간
  채팅 사본은 참고만 하고 GitHub/원본 커밋 기준으로 항상 재검증할 것.
- **[85차 계속, 핵심 발견 44]** "9절 체크리스트 전항목 통과"라는 서술을 그대로 믿지 말 것 -- 실제로
  Invoke-ReplaceBlock에 CRLF 정규화 코드가 있는지, py_compile 호출부에 EOF 선공급이 있는지 등은 스크립트
  파일을 직접 읽어 대조해야 한다. 서술과 코드가 어긋난 채로 "통과"가 기록될 수 있음이 이번에 실증됐다.

다음 작업 후보:
1. v2 코드 스크립트 실행/push 확인, devnotes 스크립트도 정정본으로 갱신해 실행/push 확인.
2. 실차에서 사진 업로드 UI(항목 22/23/26) + content_shift_y 여백 확인.
3. 84차 sdi_descr 배지 실차 검증.
4. 제목/도로명 `left_bottom` 근본 수정 여부 사용자 판단.


**[85차 계속3, 새 세션]** 세션 시작 체크포인트(`git ls-remote`)로 carrot-ryu/carrot-ryu-note가 여전히
`132d85b`/`fa038e0`(84차2)임을 재확인 -- 즉 위 85차/85차 계속 작업(item22/23/26 재검증, v1 실패,
핵심 발견 44, v2 스크립트)은 전부 GitHub에 아직 반영되지 않은 채팅 사본 상태였다(3절 원칙). 이를 그대로
믿지 않고, 신선한 별도 clone(현재 `132d85b`)에 `85cha_item22_23_26_carrot_ryu_v2.ps1`의 로직(base64
전체교체 7개 + CRLF 정규화 Replace-Block 12곳)을 Python으로 처음부터 재시뮬레이션했다: 12개 앵커 전부
1회 매치, `py_compile`(routes.py/hud_renderer.py)·`node --check`(screenshots.js/runtime.js/en·ko·zh.js/
생성번들 logs.js) 전부 통과, `content_shift_y`/`screenshotsToolbarWrap` 치환 결과도 재확인했다. 이어서
9절 "전달 전 필수 자가검증 체크리스트" 6항목을 `.ps1` 파일 자체를 직접 읽어 대조(핵심 발견 44의 교훈 그대로
적용): (a) `.ps1` 첫 3바이트 `EF BB BF`(BOM 있음, 정상), (b) `core.autocrlf=false` 포함, (c) `finally`
블록 `Remove-Item -Recurse -Force` 존재, (d) `Get-PythonCmd` + 모든 Python 외부호출 `"" | &` EOF 선공급
패턴 존재, (e) 전체재작성부 `WriteAllText(..., UTF8Encoding($false))` 사용, (f) 쓰기 후 BOM 검사 루프
존재 -- 6개 모두 실제 코드에 있음을 확인(서술만 믿지 않고 grep으로 직접 대조). 결론: v2 스크립트는
수정 없이 그대로 사용 가능. devnotes 반영 스크립트(`85cha_devnotes_carrot_ryu_note.ps1`)를 이 세션에서
새로 작성해 함께 전달한다.
