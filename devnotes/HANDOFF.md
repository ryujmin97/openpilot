Worker: Claude (119차, Claude Sonnet 5)
Date: 2026-09-21
Repository: ryujmin97/openpilot
Code Branch: carrot-ryu (base `df7da7d5`, 이번 세션은 코드 변경 없음. 118차 web_upload.py/upload.py 구 웹 업로드 경로 삭제가 최신)
Note Branch: carrot-ryu-note (이 스크립트 반영 전 base `6da523938629962eca4dcceaf291f46a299c0b58`. 반영 후 HEAD는 다음 세션이 git ls-remote로 확인)
carrot-ms 마지막 검토/동기화 체크포인트: `4bb4b510`(116차, camera_sync 스큐 허용오차 10ms->20ms) 반영 완료. 111차 확정 체크포인트는 `a23a77b1`. 이번 세션은 carrot-ms 동기화 작업 없음.

작업:
1. FINDINGS.md에 핵심 발견 46(117차 checkout CRLF, `.gitattributes` text=auto 원인)/47(118차 .ps1 CRLF+큰따옴표 백틱 이스케이프) 기록.
2. DEAD_CODE_REVIEW.md에 4차 배치 후보(A/B/C 그룹, def 52개+파일 1개) 조사 결과 기록.
3. WIP.md 119차 항목 추가.

완료:
1. 세션 시작 확인: 지침 v2 조회(SHA 고정, 커밋 `6da5239`), HANDOFF.md(118차) 확인, 브랜치 HEAD 재확인(carrot-ryu `df7da7d5`, carrot-ryu-note `6da52393`, HANDOFF 기록과 일치, 16절).
2. 핵심 발견 46/47을 pwsh 7.4.6 직접 설치 실측 + Linux `git clone --config core.eol` 비교로 검증 후 FINDINGS.md 최상단에 기록(개행 보존 삽입, CRLF).
3. carrot-ryu `df7da7d5` tarball 기반 AST 참조 분석으로 first-party 범위 dead code 후보 52 def + 파일 1개(`blinker_manager.py`) 확정, 저장소 전체 grep으로 재확인, 시험 삭제로 py_compile/pyflakes/pytest(실패목록 동일성) 검증.
4. DEAD_CODE_REVIEW.md에 4차 배치 후보(A/B/C)와 근거를 이어붙여 기록.
5. WIP.md 119차 항목 추가.
6. 노트 스크립트(`119cha_notes_carrot_ryu_note-v1.ps1`) 준비: 9절 전달 전 자가검증 체크리스트 통과(BOM 없음, core.eol=lf clone, finally cleanup, 앵커 SHA 고정 원본 시뮬레이션 매치 1회 + 치환 결과 텍스트 확인, HANDOFF는 전체교체, FINDINGS/WIP/DEAD_CODE_REVIEW는 이어붙이기 방식).

미완료(다음 세션 최우선):
1. DEAD_CODE_REVIEW A그룹(live_runtime `broker.py`/`normalize.py`/`snapshot.py` + `carrot_man.py`/`carrot_serv.py` + dashcam/services 잔여 헬퍼) 삭제 스크립트 작성/반영 -- 사용자가 A→B→C 순차 진행을 승인함(119차). 삭제 직전 11절 재확인 필요.
2. 실차 배포(디바이스 pull) 시점 -- 115차(`0e1bef52`)/116차(`62ae74dc`)/117차(`22b101f6`)/118차(`df7da7d5`) 4건 미배포 누적, 계속 이월.
3. (이월) 114차 MAP_TURN_GUIDE_FACTOR 1.00 실차 관찰, 110차 GATE_M 0.8/1.0 관찰. CURRENT_STATUS.md는 이번에도 갱신하지 않았다.
4. pytest 자체 실행 미실시 상태 누적(conftest.py/컴파일 의존성 부재, 이번 세션은 삭제 전/후 시험본 비교만 가능했음).

검증: 샌드박스 정적/실측 검증만. 핵심 발견 46/47은 Linux git clone 옵션 비교 + pwsh 7.4.6 직접 설치 실측(Windows PowerShell 5.1에서 재현한 것은 아님). dead code 후보는 AST 참조분석 + 저장소 전체 grep -w 재확인 + 시험 삭제 py_compile/pyflakes/pytest 실패목록 동일성 확인. 실차 검증: 미실시(이번 세션은 devnotes/조사 작업, 12절 무관).

주의사항:
- FINDINGS.md는 상단 CRLF/하단 LF 혼합 개행 파일이라(95차 부수 발견 2) 이번에도 개행 보존 삽입 방식(맨 위에 CRLF로 새 항목만 삽입)만 사용했다.
- DEAD_CODE_REVIEW A/B/C 그룹은 조사 결과일 뿐 아직 삭제되지 않았다. 삭제 스크립트는 그룹별 사용자 승인 후 별도 세션에서 작성한다.
- 되돌릴 코드 커밋 없음(이번 세션은 note 커밋만 발생, carrot-ryu 코드는 `df7da7d5` 그대로).

다음 작업 후보:
1. A그룹 삭제 스크립트 작성(1순위, 승인 완료).
2. 실차 배포 여부 결정, 배포 후 관찰(controlsd/플래너 예외 + 카메라 페어링 + 대시캠 업로드).
3. B그룹 → C그룹 순으로, 각 배치 착수 전 11절 재확인.
4. 114차/110차 이월 실차 관찰 항목.