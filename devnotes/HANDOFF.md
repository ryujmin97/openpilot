Worker: Claude (121차, Claude Sonnet 5)
Date: 2026-09-21
Repository: ryujmin97/openpilot
Code Branch: carrot-ryu (`2efdd2e25b42c78ea94f7366424fde695a13b15a`, 121차 B그룹 삭제 커밋. 부모 `b98620e8`. GitHub에서 확인 완료)
Note Branch: carrot-ryu-note (이 스크립트 반영 전 base `0d1daba55c6cbeba5e0bb17cba587b2396b41752`. 반영 후 HEAD는 다음 세션이 git ls-remote로 확인)
carrot-ms 마지막 검토/동기화 체크포인트: `4bb4b510`(116차, camera_sync 스큐 허용오차 10ms->20ms) 반영 완료. 111차 확정 체크포인트는 `a23a77b1`. 이번 세션은 carrot-ms 동기화 작업 없음.

작업:
1. DEAD_CODE_REVIEW 4차 배치 B그룹(5개 파일, `blinker_manager.py` 통째 + 고아 def 6개, 순 +0/-167줄) 삭제 스크립트 작성/검증 -> 사용자 실행 -> GitHub 재확인.
2. v1 스크립트 두 차례 실패 대응(git 실행 불가 창, CRLF checkout 앵커 0회 매치) -> v2 작성/재현 검증.
3. devnotes 갱신(이 스크립트): WIP.md 121차, DEAD_CODE_REVIEW.md B그룹, FINDINGS.md 핵심 발견 48, HANDOFF.md.

완료:
1. B그룹 제거 완료: carrot-ryu `2efdd2e2`. 부모 `b98620e8`, 5개 파일 +0/-167, 4개 파일 결과 blob == 스크립트 `Post`, `blinker_manager.py` HEAD에서 삭제(GitHub blobless fetch + `git ls-tree`, SHA 고정 raw, 16절). 사용자 PC(Windows PowerShell 5.1) 실행 로그가 1~8단계 전부 통과.
2. v1 사고 원인 확정: 3단계 중단은 `.gitattributes` `* text=auto` 때문에 Windows 작업 트리가 CRLF인데 앵커가 LF였던 것(핵심 발견 46/44 재발, FINDINGS.md 핵심 발견 48). 샌드박스에서 `core.eol=crlf`로 재현하고 v2로 통과 확인. 첫 실행의 "git 실행 불가 창"은 새 PowerShell 창으로 해소됐으나 원인 미확정.

미완료(다음 세션 최우선):
1. C그룹(cluster 계열, 약 300줄: `cluster_renderer.py`/`cluster_scene.py`/`main.py`) 삭제 스크립트 작성. 착수 전 11절 재확인(codeload tarball, 대상 커밋 `2efdd2e2`). `cluster_scene.py`의 `statistics.median` 미사용 import도 이 배치 소관. 사용자 승인은 A -> B -> C 순차로 이미 받음(119차).
2. 실차 배포(디바이스 pull) 시점 -- 115차(`0e1bef52`)/116차(`62ae74dc`)/117차(`22b101f6`)/118차(`df7da7d5`)/120차 A그룹(`b98620e8`)/121차 B그룹(`2efdd2e2`) 6건 미배포 누적, 계속 이월.
3. (이월) 114차 MAP_TURN_GUIDE_FACTOR 1.00 실차 관찰, 110차 GATE_M 0.8/1.0 관찰. CURRENT_STATUS.md는 이번에도 갱신하지 않았다.
4. pytest는 conftest(`params_pyx` 컴파일 산출물 필요) 없이 `--noconftest`로만 실행했으므로 실제 CI 조건의 pytest 실행은 여전히 미실시.
5. (제안, 사용자 승인 대기) 9절 체크리스트에 "`core.eol=crlf` 재현 양성 실행" 항목 추가(FINDINGS.md 핵심 발견 48, 19절 절차).

검증: 샌드박스 재현(pwsh 7.4.6 Linux, `core.eol=crlf`, 로컬 bare) + 사용자 PC 실행 로그 + GitHub 직접 재조회. 실차 검증: 미실시(삭제 대상은 전부 참조 0곳이라 동작 변화 없을 것으로 정적 분석했을 뿐).

주의사항:
- 문제가 생기면 carrot-ryu `2efdd2e2` 커밋 1개를 revert하면 B그룹이 복구된다(이번 코드 커밋은 이것 하나).
- 코드 저장소를 대상으로 하는 새 스크립트는 반드시 `core.eol=crlf`를 준 환경에서 양성 실행해 본다(핵심 발견 48). `git hash-object <경로>` 가드는 EOL 불일치를 잡지 못한다.
- 사용자 PowerShell 창에서 `git`이 출력 없이 창만 떴다 사라지면 그 창을 닫고 새 관리자 PowerShell을 연다(v2 스크립트는 `git --version` 출력이 없으면 중단한다).
- devnotes 파일 EOL이 파일마다 다르다: FINDINGS.md는 앞부분 CRLF/끝부분 일부 LF 혼재, WIP_SYNC.md는 CRLF, 나머지는 LF. 전체 파일을 재작성하지 말고 앵커 삽입으로만 고칠 것.
- 샌드박스는 세션 중에도 초기화될 수 있다(120차에 실제 발생). 중간 결과는 스크립트/문서로 바로 남길 것.

다음 작업 후보:
1. C그룹 삭제 스크립트 작성(1순위, 승인 완료).
2. 실차 배포 여부 결정, 배포 후 관찰(controlsd/플래너 예외 + 카메라 페어링 + 대시캠 업로드 + 로그탭 업로드 경로 + live_runtime `/api/live_runtime`).
3. 114차/110차 이월 실차 관찰 항목.
