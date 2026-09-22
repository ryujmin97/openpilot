Worker: Claude (127차, Claude Sonnet 5)
Date: 2026-09-22
Repository: ryujmin97/openpilot
Code Branch: carrot-ryu (base `a0f4c5a5fb932be1525311d2ed61f5382a4bd6d2`, 123차 C그룹 dead code 삭제. 이 스크립트 반영 전 base. 반영 후 HEAD는 다음 세션이 git ls-remote로 확인)
Note Branch: carrot-ryu-note (이 스크립트 반영 전 base `fe98d2e00c2e76fc59e0d53e1d54a16fdce63bad`, 126차 push 확인 완료. 반영 후 HEAD는 다음 세션이 git ls-remote로 확인)
carrot-ms 마지막 검토/동기화 체크포인트: `e324f67`(93~95차). 이번 세션도 carrot-ms 신규 커밋 확인/동기화 작업 없음 -- 여러 세션째 최우선 이월 중.

작업:
1. 126차 미완료 2번(`test_latcontrol.py` 두 파일 처리 방향 결정)을 사용자에게 두 옵션(A: controls/tests/test_latcontrol.py 최소 수정, B: controls/lib/tests/test_latcontrol.py를 DEAD_CODE_REVIEW 대상으로 편입)으로 제시, 사용자가 "진행"으로 A+B 조합 승인.
2. 사용자가 이어서 "이 코드는 실차 로직과 관련없으면 삭제해도 되지 않아?"라고 재질문 -- controls/tests/test_latcontrol.py는 실제 조향 제어 프로덕션 코드(LatControlPID/Torque/Angle)를 검증하는 테스트이고 버그는 테스트 호출부에만 있다는 점을 근거로 삭제 대신 수정을 재제안, 승인받음. controls/lib/tests/ 쪽은 grep으로 무참조 orphan임을 재확인해 삭제 방향 유지.
3. `controls/tests/test_latcontrol.py` 수정: 생성자 `(CP, CI)` 2-인자, `update()` 마지막 두 인자를 실제 시그니처(`CC`, `curvature_limited`)에 맞게 재구성. 원본 인자값이 CC 인자 추가 이전부터 이미 논리적으로 모순(`curvature_limited`가 세 호출 모두 참 값 고정)이었음을 확인, `controlsd.py` 실제 호출부/주석/assert 3개를 근거로 3가지 포화 시나리오를 재구성. `DT_CTRL` 미사용 import 제거.
4. `controls/lib/tests/test_latcontrol.py` + `__init__.py` 삭제 (디렉터리 통째로 제거).
5. 별도 clone(`a0f4c5a5f`, GitHub 현재 HEAD와 drift 없음 확인)에서 pre-image blob hash 가드 -> WriteAllText(UTF8, BOM 없음) 전체 재작성 -> post-image blob hash 일치 확인 -> git rm 2개 -> `python3 -m py_compile` 통과 -> git status 최종 diff(3 files changed, 5 insertions(+), 52 deletions(-)) 확인.
6. 반영 스크립트(`127cha_item_test_latcontrol_carrot_ryu.ps1`)를 pwsh 7.4.6(GitHub 릴리스, Linux)으로 구문 검증(오류 0건) 후, 로컬 bare 저장소(`a0f4c5a5f` 스냅샷)를 대상으로 일반 체크아웃 + Windows CRLF 체크아웃 재현 두 모드 모두 처음부터 끝까지 실행, 두 모드 모두 동일한 결과(post-image blob hash `21b42b0b...` 일치)를 확인(9절 항목 9).

완료:
1. `test_latcontrol.py` 두 파일 처리 방향 결정 및 반영 스크립트 작성/검증 완료.
2. WIP.md 127차 신규 항목(최상단), CURRENT_STATUS.md 127차 항목 추가.

미완료(다음 세션 최우선):
1. 이 스크립트(`127cha_item_test_latcontrol_carrot_ryu.ps1`) 실행/push 확인 -- GitHub SHA 고정 조회로 재확인(16절). Windows PowerShell 5.1 실제 실행은 이번 세션에서 검증하지 못했음(Linux 샌드박스 pwsh 7.4.6 재현만 완료).
2. carrot-ms 신규 커밋 확인(2절) -- 93~95차 체크포인트(`e324f67`) 이후 여전히 미확인, 여러 세션째 이월 중(**최우선**).
3. 110차 GATE_M 0.8/1.0, 114차 MAP_TURN_GUIDE_FACTOR 1.00 -- 둘 다 실차 미검증.
4. CURRENT_STATUS.md 97~114차 구간 상세 catch-up -- 여러 세션째 이월 중(122차부터).

검증: 별도 clone에서 pre/post-image blob hash 가드 + `python3 -m py_compile` 통과 + git status diff 대조(11절: 추측 아님, 실제 재현). 반영 스크립트 자체도 pwsh 파서 구문 검증 + 로컬 bare 저장소 일반/CRLF 두 모드 실행 재현까지 완료(9절). 실차 검증: 해당 없음(테스트 파일만 변경, latcontrol_pid.py/latcontrol_torque.py/latcontrol_angle.py 등 프로덕션 조향 제어 코드는 무변경).

주의사항:
- 코드 변경은 테스트 파일 2개(1개 수정 + 1개 삭제 대상, 실제로는 삭제 파일 2개 + 수정 파일 1개, 총 3개 파일)에 한정. 프로덕션 latcontrol 코드는 건드리지 않음.
- Windows PowerShell 5.1 실제 실행 검증은 여전히 없음(Linux 샌드박스 pwsh 7.4.6 재현이 한계). 9절 항목 9의 명시된 한계 그대로.
- carrot-ms 동기화(2절) 미확인이 여러 세션째 가장 오래 이월된 항목이므로 다음 세션은 이것부터 착수 권장.

다음 작업 후보:
1. carrot-ms 신규 커밋 확인(2절) 착수 -- 최우선 권장.
2. 110차/114차 실차 관찰 항목.
3. CURRENT_STATUS.md 97~114차 구간 catch-up.
