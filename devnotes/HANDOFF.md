Worker: Claude (120차, Claude Sonnet 5)
Date: 2026-09-21
Repository: ryujmin97/openpilot
Code Branch: carrot-ryu (이 세션 시작 시 HEAD `df7da7d5`, 118차 web_upload.py/upload.py 삭제가 최신. 120차 A그룹 삭제 코드 스크립트는 **실행/push 대기** -- 다음 세션은 git ls-remote로 HEAD를 확인해 `df7da7d5`이면 미실행, 아니면 A그룹 커밋 여부를 확인)
Note Branch: carrot-ryu-note (이 스크립트 반영 전 base `e69b3c56eb7e8df1d419500be73225b3fbd1058f`. 반영 후 HEAD는 다음 세션이 git ls-remote로 확인)
carrot-ms 마지막 검토/동기화 체크포인트: `4bb4b510`(116차, camera_sync 스큐 허용오차 10ms->20ms) 반영 완료. 111차 확정 체크포인트는 `a23a77b1`. 이번 세션은 carrot-ms 동기화 작업 없음.

작업:
1. DEAD_CODE_REVIEW A그룹(17개 파일, def 29개, 순 +1/-302줄) 삭제 코드 스크립트 작성/검증(`120cha_deadcode_batchA_code_carrot_ryu-v1.ps1`).
2. WIP.md 120차 항목, DEAD_CODE_REVIEW.md 표 행 + 120차 섹션, HANDOFF.md 갱신(이 스크립트 `120cha_notes_carrot_ryu_note-v1.ps1`).

완료:
1. 세션 시작 확인: 지침 v2 조회(SHA 고정, 커밋 `e69b3c5`), HANDOFF.md(119차)/CURRENT_STATUS.md/DEAD_CODE_REVIEW.md 확인, 브랜치 HEAD 재확인(carrot-ryu `df7da7d5`, carrot-ryu-note `e69b3c56`, 기록과 일치, 16절).
2. 샌드박스 초기화로 중간 편집본이 사라졌으나, 같은 SHA tarball로 편집을 재현 가능한 스크립트(`apply_A.py`)로 다시 만들어 동일 범위를 재적용(WIP.md 120차 참고).
3. 검증: tarball 17개 blob == GitHub blob, py_compile 17개 통과, pyflakes 원본과 동일(19건, 신규 0), 삭제 대상 30개 이름 잔여 참조 0건, pytest 삭제 전/후 863 passed/11 failed/25 collection errors 동일(FAILED/ERROR 36건 목록 동일, `--noconftest -o addopts="" --continue-on-collection-errors`).
4. 코드 스크립트를 pwsh 7.4.6(Linux)로 구문 파싱 + 로컬 bare 저장소 실행(일반/CRLF 체크아웃 재현 양성 2회, 사전 blob 불일치 음성 1회) 검증. 9절 체크리스트: BOM 포함(비ASCII 있음), `core.autocrlf=false` clone, finally 임시폴더 삭제, `Get-PythonCmd` + stdin EOF, 전체 재작성은 WriteAllText(UTF8 no BOM) + BOM 재확인, 앵커는 전달할 .ps1에서 추출한 쌍이 곧 검증에 쓴 쌍이며 사후 blob 해시로 결과까지 확인.

미완료(다음 세션 최우선):
1. 코드 스크립트 `120cha_deadcode_batchA_code_carrot_ryu-v1.ps1` 사용자 실행/push 확인. 확인 시 carrot-ryu 새 HEAD의 부모가 `df7da7d5`인지, 변경 파일 17개/+1/-302인지, 각 파일 결과 blob이 스크립트 `Post` 값과 일치하는지 SHA 고정 조회(16절). 실행되지 않았거나 실패했으면 사용자 로그를 받아 원인부터 확인.
2. B그룹(`blinker_manager.py` 파일 통째, `lane_planner_2.py`, `carrot/model_selector`의 `list_recent`/`onnx_filenames`, `radar_motion/predictor.py`) -> C그룹(cluster 계열, 약 300줄) 순차 진행. 각 배치 착수 전 11절 재확인, 사용자 승인은 A -> B -> C 순차로 이미 받음(119차).
3. 실차 배포(디바이스 pull) 시점 -- 115차(`0e1bef52`)/116차(`62ae74dc`)/117차(`22b101f6`)/118차(`df7da7d5`) 4건 미배포 누적에 A그룹(실행되면)이 추가됨, 계속 이월.
4. (이월) 114차 MAP_TURN_GUIDE_FACTOR 1.00 실차 관찰, 110차 GATE_M 0.8/1.0 관찰. CURRENT_STATUS.md는 이번에도 갱신하지 않았다.
5. pytest는 conftest(`params_pyx` 컴파일 산출물 필요) 없이 `--noconftest`로만 실행했으므로 실제 CI 조건의 pytest 실행은 여전히 미실시.

검증: 샌드박스 정적 검증만(py_compile/pyflakes/grep/pytest --noconftest 삭제 전후 비교, pwsh 7.4.6 Linux에서 스크립트 로컬 실행). Windows PowerShell 5.1에서의 스크립트 실행은 미확인. 실차 검증: 미실시(이번 세션은 dead code 삭제 준비, 12절 무관).

주의사항:
- 코드 스크립트 실행 전에는 A그룹이 삭제되지 않은 상태이며 DEAD_CODE_REVIEW.md도 "스크립트 준비, 실행/push 대기"로 기록돼 있다. 스크립트가 사전 blob 불일치나 앵커 매치 오류로 중단하면 아무것도 push되지 않는다(강제 진행 금지, 15절).
- 샌드박스는 세션 중에도 초기화될 수 있다(이번 세션에서 실제 발생). 중간 결과는 스크립트/문서로 바로 남길 것.
- 되돌릴 코드 커밋은 아직 없음(코드는 `df7da7d5` 그대로). 실행 후에는 새 커밋 1개를 revert하면 A그룹이 복구된다.

다음 작업 후보:
1. 코드 스크립트 실행/push 확인 -> B그룹 조사 결과 재확인 후 삭제 스크립트 작성.
2. 실차 배포 여부 결정, 배포 후 관찰(controlsd/플래너 예외 + 카메라 페어링 + 대시캠 업로드 + 로그탭 업로드 경로).
3. C그룹 착수(가장 큼, 각 배치 착수 전 11절 재확인).
4. 114차/110차 이월 실차 관찰 항목.
