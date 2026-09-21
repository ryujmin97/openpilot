Worker: Claude (123차, Claude Sonnet 5)
Date: 2026-09-22
Repository: ryujmin97/openpilot
Code Branch: carrot-ryu (`a0f4c5a5fb932be1525311d2ed61f5382a4bd6d2`, 123차 C그룹 dead code 삭제 커밋, 부모 `2efdd2e2`. 사용자 실행 후 GitHub에서 직접 재확인함. 실차 검증 미실시)
Note Branch: carrot-ryu-note (이 스크립트 반영 전 base `24bab81ee4e8c1fa15b1fa90215c19b846ea0d22`. 반영 후 HEAD는 다음 세션이 git ls-remote로 확인)
carrot-ms 마지막 검토/동기화 체크포인트: `4bb4b510`(116차, camera_sync 스케윅 허용오차 10ms->20ms) 반영 완료. 이번 세션도 carrot-ms 신규 커밋 확인/동기화 작업 없음.

작업:
1. DEAD_CODE_REVIEW C그룹(cluster 계열) 삭제 스크립트 작성/검증(대상 함수 18개 + 미사용 import 1줄, -327줄).
2. 사용자 첫 실행이 clone 단계 schannel early EOF로 중단(push 없음) -> v2(clone `--depth 1` + 최대 3회 재시도)로 교체. devnotes v1의 후행 쉼표 파싱 오류(4057행)와 본문 "12개"(실제 18개) 오기를 실행 전에 발견해 정정.
3. 사용자가 v2 두 개 실행 후 GitHub 직접 재확인: carrot-ryu `a0f4c5a5`(부모 `2efdd2e2`, 3개 파일 +0/-327, blob 3/3 일치, 삭제 18개 이름 HEAD 전체 참조 0건), carrot-ryu-note `24bab81e`(4개 파일 blob 4/4 일치).
4. DEAD_CODE_REVIEW/CURRENT_STATUS 상태 갱신, 지침 9절 자가검증 체크리스트 8번(pwsh 구문 검증)·9번(로컬 bare 저장소 일반/CRLF 실행) 추가(19절, 사용자 승인).

완료:
1. 119차 A/B/C 4차 배치 전체 종결(A `b98620e8`, B `2efdd2e2`, C `a0f4c5a5`).
2. devnotes 정리와 지침 8·9번 추가안 작성(실행/push 대기).

미완료(다음 세션 최우선):
1. 이 스크립트(`123cha_cleanup_devnotes_instructions_carrot_ryu_note.ps1`) 실행/push 확인 -- carrot-ryu-note에 커밋 2개(devnotes 정리, 지침 9절 8·9번). 16절: 로그만으로 완료 단정 금지, GitHub SHA 고정 조회로 재확인.
2. CURRENT_STATUS.md 97~114차 구간 상세 catch-up(122차부터 이월)과 115~123차 항목 이식.
3. C그룹(123차) 포함 실차 배포/검증 -- 115~121차는 사용자가 실차 확인(122차 기록), 123차 C그룹은 미확인. 사용자 확인 후.
4. pytest를 실제 CI 조건(conftest 포함)으로 실행한 적이 없음(120차 `--noconftest`만, 123차는 py_compile/pyflakes/`git grep`만) -- 이월.
5. (사용자 결정 대기) 9절 스크립트 구조에 clone 재시도(`--depth 1`, 최대 3회) 표준화 여부.

검증: GitHub SHA 고정 조회 + blob hash 대조 + `git grep -w` + pwsh 파서/로컬 bare 저장소 시뮬레이션(일반/CRLF). 실차 검증: 미실시.

주의사항:
- 이 스크립트의 pre-image 해시 가드는 carrot-ryu-note `24bab81e` 기준(5개 파일)이다. 그 사이 다른 세션이 이 파일들을 건드렸다면 commit/push 이전에 안전 중단된다(15절/18절 -- 에러 메시지를 그대로 Claude에게 전달, 강제 진행 금지).
- 이미 실행 완료된 v2 두 개(`123cha_item_c_group_dead_code_carrot_ryu-v2.ps1`, `123cha_devnotes_carrot_ryu_note-v2.ps1`)와 대체된 v1 두 개는 다시 실행하지 않는다(실행해도 pre-image 가드에서 중단되지만 혼동 방지).
- 새 8·9번 검증은 Linux 샌드박스의 pwsh 7.x 기준이며 Windows PowerShell 5.1 실행을 대신하지 않는다. pwsh가 없으면 GitHub 릴리스 tarball(`releases/download/vX.Y.Z/powershell-X.Y.Z-linux-x64.tar.gz`)을 직접 받는다(`api.github.com`은 rate limit으로 실패할 수 있음).

다음 작업 후보:
1. 이 스크립트 실행/push 확인(1순위).
2. CURRENT_STATUS.md 97~114차 catch-up.
3. 115~123차 dead code 실차 배포/검증 일괄 확인(사용자 판단 대기).
4. 남은 dead code 후보 추가 배치 여부 -- 119차 조사에서 제외/보류한 것(테스트에서만 참조되는 10개, 고아 상수 67개/미사용 import)은 사용자 승인 후에만.
