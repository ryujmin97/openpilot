Worker: Claude (155cha 계속, Claude Sonnet 5)
Date: 2026-09-24
Repository: ryujmin97/openpilot
Code Branch: carrot-ryu (HEAD: 9ff1242e4ba1da3f491ef0a7de563647919aff63, 155차 코드 -- upload_jobs zip 스테이징 /data 하위 이동, push 완료 확인. 이번 계속 회차 코드 변경 없음)
Note Branch: carrot-ryu-note (이 스크립트 반영 전 base: 155차 devnotes push 완료 상태, `5c02b08139b63c9d49d57e42f1e8f553c0944d68`)
carrot-ms 마지막 검토/동기화 체크포인트: `3756e6d5`(130차, 139차 세션 재확인 -- 신규 커밋 없음. 140~155차는 재점검 없음)

작업:
1. 사용자가 155차 코드/devnotes 반영 스크립트를 실행했다고 알려와, GitHub를 SHA 고정으로 직접 조회해 push 완료를 확정(16절): carrot-ryu `9ff1242e`(부모 `f23d05f`, +5/+7-1, blob hash가 시뮬레이션 예측과 일치), carrot-ryu-note `5c02b081`.
2. 사용자가 기기에서 git pull을 마치고 로그탭 대시캠 전체선택 "선택 전송"을 재실행한 결과("정상 진행됨")를 WIP.md 155차 계속/CURRENT_STATUS.md에 기록. 직전 HANDOFF의 "155차 코드 push 대기" 문구를 바로잡음.

완료:
1. 155차(로그탭 선택 전송 ENOSPC/Errno 28) 코드+devnotes push 완료 확정.
2. 실기기 검증: 사용자 보고 기준 전체선택 선택 전송이 정상 진행돼 ENOSPC 재발 없음(정차 상태 기능 확인, 주행 검증 아님).

미완료(다음 세션 최우선 순으로):
1. 155차 잔여 확인(사용자 보고에 없던 것): Drive 업로드가 끝까지 완료됐는지, 전송 후 `/data/carrot/tmp/dashcam_upload`가 비워졌는지(`ls`로 확인), 기기가 pull한 커밋 SHA.
2. 강제 종료/전원 차단 시 `/data/carrot/tmp/dashcam_upload/carrot_dashcam_*` 잔존 zip(수백 MB)이 재부팅으로 안 지워지는 문제 -- 시작 시 정리 로직 추가 여부 결정(155차 이월).
3. (선택) `build_zip()` 직전 `shutil.disk_usage`로 필요 용량 vs 여유를 비교하는 조기 실패 방어 코드(미포함 상태 유지).
4. **주행 실차 검증 여전히 미실시** -- 기기에 152·153차 코드가 탑재됐는지(사용자가 carrot-ryu 최신을 pull했으므로 가능성 높으나 SHA 미확인) 확인 후, 분기(xTurn=4)/톨게이트(xTurn=6) 실주행 로그로 153차 수정 검증(154차 이월).
5. 분기/톨게이트 통과 직후(xDist<0) 구간 요동에 152차 게이트(TurnSpeedControlMode==2)가 적용되는지 확인(154차 이월).
6. 잔여 비트리거 급변(세그먼트당 10~25건)의 원인 분석 미착수(154차 이월).
7. 147차 코드 탑재 디바이스 실주행 로그 검증, "선행차가 설정 차간거리 근처에서 급제동" 시나리오 정량 미검증, 148차 v1 `2>&1` 재발의 FINDINGS.md 정식 등록 여부 결정, 147차 임시 diff/블록 추출 스크립트 toolkit 미등록(모두 이전 이월, 변동 없음).

검증:
- 155차 코드: 정적 분석 + py_compile + 로컬 bare 저장소 시뮬레이션에 더해, 사용자 보고 기준 실기기 전체선택 선택 전송 정상 진행(Drive 완주/임시 폴더 정리는 미확인). 주행 실차 검증은 미실시.
- 원인 수치(`/tmp` 150M, `/data` 71G, route 합계 약 460M)는 사용자가 전달한 이전 세션 분석 인용이며 이 세션 컨테이너에서 원문 출력을 재확인하지 못함(WIP 155차 참고).

주의사항:
- 이번 계속 회차는 devnotes만 변경, carrot-ryu 코드 변경 없음(코드 HEAD는 155차 `9ff1242e` 그대로).
- `/data`는 재부팅해도 비워지지 않는다(FINDINGS 핵심 발견 56 일반화 2) -- 잔존 zip 정리 로직은 아직 없다.

다음 작업:
1. 155차 잔여 확인 3건(Drive 완주/임시 폴더 정리/pull SHA) 사용자에게 확인.
2. 잔존 zip 정리 로직 필요 여부 결정.
3. 153차 이월 항목(분기/톨게이트 주행 로그 검증)으로 복귀.