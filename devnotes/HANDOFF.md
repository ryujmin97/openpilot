Worker: Claude (84차 계속2, devnotes/인코딩 보정만 · 84차 코드 로직 변경 없음)
Date: 2026-09-18
Repository: ryujmin97/openpilot
Code Branch: carrot-ryu (base: `a461c7ea5188b93487ea240728519771cf64eb7c`, 84차 sdi_descr 배지 수정 push 완료, 이번 세션은 그 위에서 BOM만 제거)
Note Branch: carrot-ryu-note (base: `b1749374ac0e1803465dc9bc8c70da9947b3d9ff`, 84차 devnotes push 완료, 이번 세션은 그 위에서 BOM 제거 + WIP.md 헤더 복원 + CURRENT_STATUS.md/PROJECT_INSTRUCTIONS 갱신)
carrot-ms 마지막 검토/동기화 커밋(메시지 기준): `706efb47b81cf9cb02888ee536a156d8f1fc1d91`(61차 20절 리셋 베이스, 변경 없음).

작업:
84차에서 전달한 v2 스크립트 실행 후 push가 완료됐음을 세션 시작 체크포인트(`git ls-remote`)로 확인.
4절/16절 원칙대로 push된 실제 내용을 raw(SHA고정)로 재조회하는 과정에서 두 가지 문제를 발견해 이번
세션에서 즉시 보정했다.

완료:
1. 4개 파일(`hud_renderer.py`/`WIP.md`/`CURRENT_STATUS.md`/`HANDOFF.md`) 전체 재작성에 쓰인
   `Set-Content -Encoding UTF8`이 Windows PowerShell 5.1에서 항상 BOM을 새로 붙인다는 것을 확인
   (원본은 전부 BOM 없는 상태였음). 4개 파일 모두 BOM(`EF BB BF`) 제거(핵심 발견 41).
2. `WIP.md`는 84차 반영 스크립트의 anchor 치환 로직 버그로 최상단 `# WIP` 제목 줄이 통째로
   사라진 채 push되어 있었음을 발견, 복원(핵심 발견 42).
3. `PROJECT_INSTRUCTIONS_carrot-ryu.md` 9절에 "전달 전 필수 자가검증 체크리스트"를 실제로 반영
   (직전 84차 세션에서 CURRENT_STATUS.md에는 "반영 완료"로 기록됐으나 실제 지침 문서 파일 자체에는
   반영되지 않았던 누락을 이번에 바로잡음 -- 핵심 발견 27/38과 같은 "기록과 실제 상태 불일치"
   패턴이 지침 문서 자신에도 발생했던 사례). 체크리스트 내용: (a) 대상 파일 전체 재작성 시
   `[System.IO.File]::WriteAllText(path, content, New-Object System.Text.UTF8Encoding($false))`만
   사용 + 쓴 뒤 첫 3바이트가 BOM이 아닌지 확인, (b) `.ps1` 자체의 BOM 필요 여부 확인, (c) `git clone`의
   `--config core.autocrlf=false` 포함 여부 확인, (d) 임시 폴더 자동 정리(`finally`) 여부 확인,
   (e) `Get-PythonCmd` 자동탐지 패턴을 py_compile 검증 시 기본값으로 사용, (f) anchor 매치 횟수뿐
   아니라 치환 *결과* 텍스트(특히 파일 맨 앞/헤더 줄)까지 재확인. 이 6가지 모두 py_compile과 동급의,
   "실행하고 결과를 응답에 보여줘야 하는" 검증 단계로 명문화.
4. CURRENT_STATUS.md에 핵심 발견 41/42 신규 삽입, 84차 bullet/핵심 발견 26/37에 재발·채택 각주 추가.

미완료(다음 세션 최우선):
1. 사용자가 이 devnotes 반영 스크립트(코드용 `84cha2_hud_renderer_bom_fix_v2.ps1`, devnotes용
   `84cha2_devnotes_bom_and_header_fix_v2.ps1`)를 실행해 push할 것(구버전 v1 두 파일은 실행하지 말 것).
2. push 확인되면 이번 세션에서 다룬 인코딩 보정과 별개로, 84차 sdi_descr 배지 수정 자체의 실차
   검증이 여전히 미실시 상태 -- 카메라/POI 근처 실주행에서 배지 안에 텍스트가 제대로 들어오는지
   확인할 것(12절, 프로젝트 역사상 이 코드 경로 최초 검증).
3. (낮은 우선순위, 사용자 결정 대기) 제목(`tbt_main_text`)/도로명(`road_name_text`)도 동일한
   `get_text_draw_pos()` `left_bottom` 미구현 버그의 영향을 받고 있음 -- 근본 수정 여부 판단 필요.
4. 항목 22(39차, `797fca2e`, 화면녹화 탭 사진 업로드 UI) 본편 착수는 이번에도 다루지 않음 -- 계속
   다음 우선순위 후보로 이월.

검증: 4개 파일 모두 `od -An -tx1 -N3`로 BOM 제거 확인, `hud_renderer.py` `py_compile` 재통과,
`WIP.md` 파일 맨 앞 `# WIP` 복원 확인, `PROJECT_INSTRUCTIONS_carrot-ryu.md` 9절 Replace-Block anchor
1회 매치 + 치환 결과 재확인(핵심 발견 42 원칙을 이 수정 자체에도 적용). 실차 검증: 이번 세션은
인코딩/문서 보정만이며 코드 로직 변경 없음 -- 84차 sdi_descr 실차 검증은 여전히 대기 중.

[사용자 실행 중 추가 발견] `84cha2_hud_renderer_bom_fix.ps1` 실행 중 `py_compile` 검증 단계에서
스크립트가 Python 인터랙티브 셸(`>>>`)에 빠져 무한 대기하는 문제가 실제로 발생(핵심 발견 43). 사용자가
`Ctrl+C`로 안전하게 중단(commit/push 이전이라 반영 사고 없음). Python 외부 호출부에 표준입력 EOF
선공급(`"" | & $Cmd @Args`)을 추가해 하드닝한 `84cha2_hud_renderer_bom_fix_v2.ps1`로 교체 전달함.

주의사항:
- 이번 사례(핵심 발견 41/42)는 "규칙이 문서에 서술돼 있어도 전달 직전 기계적 검증이 없으면
  반복된다"는 패턴(BOM(.ps1)/core.autocrlf/임시폴더/Get-PythonCmd와 동일 계열)이 대상 파일
  인코딩(BOM)과 치환 결과 검증에도 그대로 적용된 사례. 9절 체크리스트로 승격했으니 다음 세션부터는
  이 6가지 모두 결과 출력을 응답에 포함할 것.
- "CURRENT_STATUS.md에 반영 완료로 적었다"가 "실제 지침 문서 파일에 반영됐다"를 보증하지 않는다는
  것도 이번에 재확인됨 -- 지침 문서 자체를 수정하는 19절 절차를 완료했다고 기록할 때는, 그 직후
  반드시 지침 문서 파일을 raw로 다시 조회해 실제 반영 여부를 확인할 것.

다음 작업 후보:
1. 코드/devnotes 보정 스크립트 실행/push 확인.
2. 실차에서 sdi_descr 배지 표시 확인(84차 본 작업).
3. 항목 22(39차) 본편 착수.
