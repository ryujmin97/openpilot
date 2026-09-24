Worker: Claude (153cha, Claude Sonnet 5)
Date: 2026-09-24
Repository: ryujmin97/openpilot
Code Branch: carrot-ryu (HEAD: 44bfd33d6ad3bb4c0470386a6ac6e98bdad37fc2, 152차 상태 유지 -- 153차 코드는 아직 실행/push 전, 반영 스크립트 준비 완료)
Note Branch: carrot-ryu-note (이 스크립트 반영 전 base: 152차 devnotes push 완료 상태, `26fa4b18c3258b11cee13017e42f5a18b86a63b8`)
carrot-ms 마지막 검토/동기화 체크포인트: `3756e6d5`(130차, 139차 세션 재확인 -- 신규 커밋 없음. 140~153차는 재점검 없음)

작업:
1. 세션 시작 4절 0단계로 지침 문서(v2, commit `26fa4b1`) 조회, HANDOFF.md/CURRENT_STATUS.md(152차, 동일 커밋) 확인 후 carrot-ryu HEAD(`44bfd33d`, 152차, 변경 없음)와 문서 기록 일치 재확인.
2. 사용자가 제공한 seg70(rlog `00000446--6455a5f5c4--70`) 분기 구간 desiredSpeed flicker에 대해, `carrot_man.py`의 `get_path_after_distance()`를 코드로 분석해 "첫 세그먼트가 이미 distance_m(300m)을 넘는 경우" 처리 누락을 근본 원인으로 확정.
3. `get_path_after_distance()`에 첫 세그먼트 안에서 바로 보간·반환하는 분기를 추가하는 수정 구현.
4. 합성 좌표 스윕으로 수정 전/후 안정성 차이를 재현 검증.
5. 전달용 `153cha_code_carrot_ryu.ps1`을 작성해, 로컬 bare mirror(carrot-ryu 현재 HEAD) 대상으로 일반/Windows CRLF 재현 두 모드 clone-to-push 전 과정 dry-run으로 검증(9절 자가검증 체크리스트 전항목).
6. dry-run 중 발견한 스크립트 자체 버그(`Get-PythonCmd` 반환값의 PowerShell 자동 스칼라 축약) 수정.

완료:
1. 근본 원인 확정: `get_path_after_distance()`가 closest_point->next_point 첫 세그먼트 거리가 distance_m 이상이면 무조건 next_point를 append한 뒤 `remaining_distance = distance_m - total_distance`를 음수로 만들어, 진행방향과 반대인 가짜 보간점을 만드는 구조적 버그(route 폴리라인 정점 간격이 300m보다 성긴 분기/램프 구간에서만 발현, 곡률 계산이 GPS 위치 변화에 매우 민감해져 20Hz마다 desiredSpeed가 요동).
2. 수정 구현: 첫 세그먼트 거리가 distance_m 이상이면 그 세그먼트 안에서 바로 보간해 즉시 반환하는 분기 추가(음수 ratio 원천 차단). `openpilot/selfdrive/carrot/carrot_man.py` 1개 파일, 24줄 블록(+21/-3). Pre-image blob hash `29fde460f43b89b8195d0b0ca70c28939761c944`(carrot-ryu 현재 HEAD와 일치 확인), post-image blob hash `eb8a53c4c1e8900cf35ddb06ff41c85b16d606c2`.
3. 합성 좌표 검증: p6->p7=400m(>300m) 세그먼트에서 차량을 5m 간격으로 0~80m 스윕 -- OLD는 5m 이동만으로 반환 경로 마지막 점이 -87.9m 튀는 불연속 발생 후 계속 흔들림, NEW는 전 구간 편차 0.0m로 완전 안정.
4. 반영 스크립트(`153cha_code_carrot_ryu.ps1`) 작성 -- `devnotes/toolkit/replace_block_template.ps1`의 `Invoke-ReplaceBlock`/`Invoke-Git` 재사용(14절), pre/post-image blob hash guard 포함.
5. pwsh 7.4.6 파서 구문 오류 0건, `.ps1` 자체 UTF-8 BOM 포함 확인(9절 체크리스트 1·8번).
6. 로컬 bare mirror(carrot-ryu HEAD `44bfd33d`) 대상 clone->pre-hash guard->Replace-Block->py_compile->post-hash guard->commit->push 전 과정을, 일반 체크아웃 모드와 Windows CRLF 체크아웃 재현 모드(`GIT_CONFIG_KEY_0=core.eol GIT_CONFIG_VALUE_0=crlf`) 둘 다로 실제 실행 -- 두 모드 모두 diff(`1 file changed, 21 insertions(+), 3 deletions(-)`)와 결과 blob이 byte-exact 일치(9절 체크리스트 9번).
7. dry-run 1차 시도에서 발견한 스크립트 버그(`Get-PythonCmd`가 반환하는 원소 1개 배열이 PowerShell 성공 스트림에서 스칼라 문자열로 자동 축약되어, 뒤이은 배열 슬라이싱이 문자 단위 인덱싱으로 오동작 -> `python3`이 개별 문자로 쪼개져 `py_compile` 호출 실패)을 `@(Get-PythonCmd)` + `$PyExtraArgs` 분리로 수정, 재검증까지 완료.

미완료(다음 세션 최우선 순으로):
1. **153차 코드 스크립트 실행/push 확인** -- 정적/dry-run 검증만 완료, 실제 GitHub push는 아직.
2. **153차 devnotes 반영 스크립트 실행/push 확인**.
3. seg71/92/93에서도 동일 패턴(첫 세그먼트가 300m를 넘는 경우)이 실제로 나타나는지 rlog 재생으로 교차검증(이번 세션은 seg70 기반 원인 분석 + 합성 좌표 검증만 수행, 151차부터 이어지는 이월).
4. push 후 분기(xTurn=4)/톨게이트(xTurn=6) 재실차 로그로 desiredSpeed flicker 실제 감소 여부 검증(정적 분석/합성 좌표 검증만 완료, 실차 검증: 미실시).
5. 152차 코드(TBT desiredSpeed atc 제거 + route 게이트 300m)의 디바이스 배포(git pull) 여부 여전히 미확인(151/152차 이월).
6. 147차 코드가 탑재된 디바이스의 실주행 로그 검증(148~152차 이월).
7. "선행차가 설정 차간거리(m~1.25) 근처에서 급제동" 시나리오 정량 미검증(148~150차 이월).
8. 148차 v1 `2>&1` 재발(핵심 발견 53/55와 동일 패턴 3회째)의 FINDINGS.md 정식 등록 여부 결정(148차 이월).
9. 이전 이월: diff/블록 추출 스크립트(임시, 147차 코드 반영용) toolkit 미등록.

검증:
- 코드: SHA 고정 원본(carrot-ryu 현재 HEAD `44bfd33d`) 대비 py_compile 통과, 합성 좌표 재현(수정 전/후 안정성 차이 실증), 전달용 `.ps1` 스크립트 자체의 로컬 bare mirror 대상 clone-to-push 전 과정 dry-run(일반/Windows CRLF 재현 두 모드 byte-exact 일치)까지 완료.
- 실차: 미실시(이 수정 자체가 아직 GitHub에 push되지 않았고, 디바이스 배포/실주행 기록도 없음).

주의사항:
- 152차 코드(atc 제거 + route 게이트 300m)와 153차 코드(get_path_after_distance 첫 세그먼트 보간)는 서로 다른 파일(carrot_serv.py vs carrot_man.py)의 독립적인 수정이며 충돌 없음.
- 153차 수정은 "route 폴리라인 정점 간격이 300m보다 성긴 구간에서 발생하는 진행방향 역행 보간점" 문제만 고친 것이며, 다른 종류의 곡률 불안정 요인(예: GPS 노이즈 자체, 폴리라인 정점 밀도가 촘촘한 구간의 다른 문제)까지 해소한다고 단정하지 않는다 -- 재실차 검증에서 flicker가 남아있다면 11절 원칙대로 추가 분석이 필요하다.
- `153cha_code_carrot_ryu.ps1`은 아직 사용자가 실행한 적이 없다(dry-run은 Claude 샌드박스의 로컬 bare mirror 대상으로만 수행됨, Windows PowerShell 5.1 실제 실행은 아님).

다음 작업:
1. 153차 코드/devnotes 반영 스크립트 실행/push 확인.
2. seg71/92/93 교차검증, push 후 분기/톨게이트 재실차 로그 검증.
