Worker: Claude (155cha, Claude Sonnet 5)
Date: 2026-09-24
Repository: ryujmin97/openpilot
Code Branch: carrot-ryu (HEAD: f23d05fef4690a01af27e108f98cc01992f11869, 153차 코드 -- 155차 코드 수정은 반영 스크립트 `155cha_code-v2.ps1` 실행/push 대기 중, GitHub 미반영)
Note Branch: carrot-ryu-note (이 스크립트 반영 전 base: 154차 devnotes push 완료 상태, `ffd9922a1426884884b36ea91c8b744a7059013e`)
carrot-ms 마지막 검토/동기화 체크포인트: `3756e6d5`(130차, 139차 세션 재확인 -- 신규 커밋 없음. 140~155차는 재점검 없음)

작업:
1. 세션 시작 4절 0단계로 지침 문서(v2) 조회 후 HANDOFF.md(154차 기록)와 GitHub 실제 상태(carrot-ryu `f23d05f`, carrot-ryu-note `ffd9922`)가 일치함을 확인. 이 회차는 사용량 한도로 중단된 155차 초안 세션의 이어받기이며, 그 초안은 GitHub에 아무것도 push되지 않았으므로(HEAD 변동 없음) 원본을 SHA 고정으로 다시 받아 처음부터 재수행.
2. 로그탭 대시캠 "선택 전송" ENOSPC(Errno 28) 원인 분석 결과 반영: zip 스테이징이 `tempfile` 기본 경로(`/tmp` tmpfs 150M)라 선택 세그먼트 합계(38세그먼트 약 460M)가 넘으면 실패 -- 상세 WIP.md 155차/FINDINGS.md 핵심 발견 56.
3. 코드 수정(carrot-ryu, 최소 변경): `config.py`에 `DASHCAM_UPLOAD_TMP_DIR`(`/data/carrot/tmp/dashcam_upload`) 추가, `upload_jobs.py`의 `mkdtemp`에 `dir=` 지정. 용량 사전체크 방어 코드는 사용자가 선택하지 않아 미포함.
4. `selfdrive/carrot/**/*.py`의 다른 tmp 사용처 grep -- 대용량 스테이징은 이 한 곳뿐(정적 grep).

완료:
1. 코드 반영 스크립트 `155cha_code-v2.ps1` 작성 + 9절 체크리스트 검증(BOM/autocrlf 옵션/finally 정리/py_compile/pwsh 파서 0 errors/앵커 1회 매치/로컬 bare 저장소 일반+CRLF 재현 두 모드 blob byte-exact 동일). 사용자 실행/push 전이라 GitHub 반영은 미확인.
2. devnotes(WIP.md 155차/FINDINGS.md 핵심 발견 56/HANDOFF.md/CURRENT_STATUS.md) 작성.

미완료(다음 세션 최우선 순으로):
1. **155차 코드 push 확인**: 세션 시작 시 `git ls-remote`로 carrot-ryu HEAD가 `f23d05f`에서 바뀌었는지(=`155cha: dashcam upload zip tmp dir ...` 커밋 존재) 확인하고, 안 바뀌었으면 사용자가 아직 스크립트를 실행하지 않은 것(반영으로 가정 금지).
2. **실기기 검증 미실시**: 반영·배포(git pull) 후 로그탭 38세그먼트 전체 "선택 전송"이 완주하는지, `/data/carrot/tmp/dashcam_upload`가 생성되고 종료 후 비워지는지 확인.
3. 강제 종료/전원 차단 시 `/data/carrot/tmp/dashcam_upload/carrot_dashcam_*` 잔존 zip(수백 MB)이 재부팅으로 안 지워지는 문제 -- 시작 시 정리 로직 추가 여부 결정(이월).
4. (선택) `build_zip()` 직전 `shutil.disk_usage`로 필요 용량 vs 여유를 비교하는 조기 실패 방어 코드(이번에는 미포함).
5. **실차 검증 여전히 미실시** -- `f23d05f`(153차) 이후 코드가 탑재된 디바이스의 분기(xTurn=4)/톨게이트(xTurn=6) 실주행 로그 필요(154차 이월).
6. 152차·153차·155차 코드의 디바이스 배포(git pull) 여부 확인(151~155차 이월).
7. 분기/톨게이트 통과 직후(xDist<0) 구간 요동에 152차 게이트(TurnSpeedControlMode==2)가 적용되는지 확인(154차 이월).
8. 잔여 비트리거 급변(세그먼트당 10~25건)의 원인 분석 미착수(154차 이월).
9. 147차 코드 탑재 디바이스 실주행 로그 검증, "선행차가 설정 차간거리 근처에서 급제동" 시나리오 정량 미검증, 148차 v1 `2>&1` 재발의 FINDINGS.md 정식 등록 여부 결정, 147차 임시 diff/블록 추출 스크립트 toolkit 미등록(모두 이전 이월, 변동 없음).

검증:
- 155차 코드: 정적 분석 + py_compile + 로컬 bare 저장소 시뮬레이션(pwsh 7.5.4, 리눅스)만 수행. Windows PowerShell 5.1 실행, 실기기, 실차 검증은 모두 미실시.
- 원인 수치(`/tmp` 150M, `/data` 71G, route 합계 약 460M)는 사용자가 전달한 이전 세션 분석 인용이며 이 컨테이너에서 원문 출력을 재확인하지 못함.

주의사항:
- carrot-ryu 코드는 `155cha_code-v2.ps1` 실행 전까지 `f23d05f` 그대로다. 파일명의 `-v2`는 중단된 초안 세션의 로컬 파일과 이름이 겹치지 않게 하려는 것.
- devnotes 반영 스크립트는 코드와 별도 브랜치(carrot-ryu-note)용이며 서로 독립적으로 실행 가능하다.
- 잔존 임시 파일 주의: `/data`는 재부팅해도 비워지지 않는다(핵심 발견 56 일반화 2).

다음 작업:
1. 155차 코드 push 여부 확인 → 실기기 배포 후 "선택 전송" 재현 테스트.
2. 잔존 zip 정리 로직 필요 여부 결정.
3. 153차 이월 항목(분기/톨게이트 실주행 로그 검증)으로 복귀.