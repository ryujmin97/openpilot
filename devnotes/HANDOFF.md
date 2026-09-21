Worker: Claude (123차, Claude Sonnet 5)
Date: 2026-09-21
Repository: ryujmin97/openpilot
Code Branch: carrot-ryu (`2efdd2e25b42c78ea94f7366424fde695a13b15a`, 121차 B그룹 삭제 커밋. 이번 세션 코드 변경 없음 -- 삭제 스크립트는 작성만 하고 실행/push는 사용자 대기)
Note Branch: carrot-ryu-note (이 스크립트 반영 전 base `48533191bcdbeb95bee54de9244c9c7378e40e59`, 122차 devnotes. 반영 후 HEAD는 다음 세션이 git ls-remote로 확인)
carrot-ms 마지막 검토/동기화 체크포인트: `4bb4b510`(116차, camera_sync 스케윅 허용오차 10ms->20ms) 반영 완료. 이번 세션은 carrot-ms 신규 커밋 확인/동기화 작업 없음(122차와 동일).

작업:
1. 119차 승인된 A→B→C 순서의 마지막 단계 C그룹(cluster 계열) 착수 전 11절 재확인(codeload tarball, 대상 커밋 `2efdd2e2`) -- 대상 함수 18개 여전히 정의 1곳 + (그룹 내부 상호호출 제외) 외부 참조 0곳 확인.
2. AST(`ast.parse`)로 함수 경계를 산출해 cluster_renderer.py/cluster_scene.py/main.py에서 대상 18개 함수 + 미사용 import 1줄(`from statistics import median`) 삭제(-327줄).
3. py_compile 3개 통과, pyflakes 경고 삭제 전/후 완전 동일(무관 기존 경고 1건만 잔존) 확인.
4. 독립적인 새 `git clone`에서 반영 스크립트 로직(pre-image 블롭 해시 가드 -> base64 파일쓰기 -> post-image 블롭 해시+BOM 확인 -> py_compile -> commit) 전체를 처음부터 재현, commit diff가 예상(+0/-327, 3개 파일)과 정확히 일치함을 확인.
5. 반영 스크립트(`123cha_item_c_group_dead_code_carrot_ryu.ps1`) 작성, 9절 "전달 전 필수 자가검증 체크리스트" 전항목 통과.
6. devnotes 4개 파일(WIP.md/HANDOFF.md/CURRENT_STATUS.md/DEAD_CODE_REVIEW.md) 갱신.

완료:
1. C그룹 삭제 스크립트 작성/자가검증 완료(실행/push는 대기).
2. devnotes 4개 파일 갱신.

미완료(다음 세션 최우선):
1. 코드 스크립트(`123cha_item_c_group_dead_code_carrot_ryu.ps1`) 실행 -> push 확인 (16절: 로그만으로 완료 단정 금지, GitHub API/raw 직접 재확인 필수).
2. push 확인되면 DEAD_CODE_REVIEW.md의 C그룹 행/123차 섹션 상태를 "제거 완료"로 갱신 -- 이로써 119차 A/B/C 4차 배치 전체 종결.
3. CURRENT_STATUS.md 97~114차 구간 상세 catch-up (122차부터 이월, 이번 세션도 착수하지 않음).
4. C그룹 포함 115~121차 dead code 전체의 실차 배포/검증(사용자 확인 후).

검증: devnotes 조회(GitHub SHA 고정) + codeload tarball 11절 재확인 + py_compile/pyflakes + 독립 clone에서 스크립트 로직 재현(9절/16절). 실차 검증: 미실시(코드 자체가 아직 GitHub에 반영되지 않음).

주의사항:
- 실행할 스크립트는 `-v2` 두 개뿐이다: `123cha_item_c_group_dead_code_carrot_ryu-v2.ps1`, `123cha_devnotes_carrot_ryu_note-v2.ps1`. 같은 이름의 v1 두 개는 실행하지 말 것 -- 코드 v1은 git clone 재시도가 없어 사용자 PC에서 schannel early EOF로 한 번 실패했고, devnotes v1은 4057행 후행 쉼표로 PowerShell 파싱 오류가 난다(WIP.md 123차 "사용자 첫 실행 결과" 참고). 코드 v1 첫 실행은 clone 단계에서 끊겨 push되지 않았다.
- 코드는 아직 GitHub에 반영되지 않았다 -- carrot-ryu HEAD는 여전히 `2efdd2e2`(121차)다. 사용자가 스크립트를 실행/push하기 전까지 "제거 완료"로 간주하지 말 것.
- 이 세션에 준비한 스크립트의 pre/post 블롭 해시 가드는 대상 커밋이 `2efdd2e2`일 때만 유효하다. 스크립트 실행 시점에 만약 다른 세션이 먼저 이 3개 파일을 건드렸다면 pre-image 해시 불일치로 스크립트가 commit/push 이전에 안전하게 중단된다(15절/18절 안전장치 -- 에러 메시지를 그대로 Claude에게 전달할 것, 강제 진행 금지).
- 9절 자가검증 체크리스트 항목 7(전달할 .ps1에서 앵커/치환 문자열을 추출해 SHA 고정 원본에 시뮬레이션)을 base64 전체교체 방식에 맞게 적용: .ps1 파일 안의 base64 문자열을 직접 추출/디코드해 (a) 결과 바이트가 사전 준비한 수정본과 완전히 동일한지, (b) git blob 해시가 스크립트에 박아 둔 Post 해시와 일치하는지 확인했다.

다음 작업 후보:
1. 123차 스크립트 실행/push 확인(1순위).
2. CURRENT_STATUS.md 97~114차 구간 catch-up.
3. 119차 A/B/C 배치 전체 + 115~121차 dead code 실차 배포/검증 일괄 확인(사용자 판단 대기).
