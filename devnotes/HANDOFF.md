Worker: Claude (156cha, Claude Sonnet 5)
Date: 2026-09-24
Repository: ryujmin97/openpilot
Code Branch: carrot-ryu (HEAD: 9ff1242e4ba1da3f491ef0a7de563647919aff63, 155차 코드 그대로 -- 이번 156차 반영 스크립트는 실행/push 대기, 아직 GitHub 미반영)
Note Branch: carrot-ryu-note (이 스크립트 반영 전 base: 61e87b9360320626afb333dce47a71a4f32391dd, 155차 계속2 devnotes push 완료 상태)
carrot-ms 마지막 검토/동기화 체크포인트: `3756e6d5`(130차, 139차 세션 재확인 -- 신규 커밋 없음. 140~156차는 재점검 없음)

작업:
1. HANDOFF.md(155차 계속2) 미완료 2번(강제 종료/전원 차단 시 `/data/carrot/tmp/dashcam_upload/carrot_dashcam_*` 잔존 zip이 재부팅으로 안 지워지는 문제)의 A안(작업 시작 시, 실행 중 작업이 없을 때 무활동 만료 시간보다 오래된 `carrot_dashcam_*` 삭제)을 9절 절차대로 반영. `openpilot/selfdrive/carrot/server/features/dashcam/upload_jobs.py`에 `cleanup_stale_upload_tmp_dirs()` 신규 함수를 추가하고, `create_job()`이 `running_job() is None`일 때(=현재 실행 중인 업로드 작업이 없을 때)만 이를 호출하도록 배선(+33줄, 10절 최소 변경 -- 정상 종료 경로인 `run_upload_segments()`의 `finally: shutil.rmtree(tmp_dir)`는 그대로 둠).

완료:
1. 위 A안 코드 작성 및 9절 자가검증 체크리스트 전항목 통과: 독립 함수 단위 테스트(임시 디렉터리에 `carrot_dashcam_*` 접두사 폴더 2개(30분 이상 지난 것/최근 것) + 접두사 다른 폴더 1개를 만들어, 오래된 것만 삭제되고 나머지는 보존됨을 확인), `py_compile` 통과, BOM 없음, `.ps1` 자체는 UTF-8 BOM 포함, `pwsh 7.4.6` 파서 구문 오류 0건, 실제 GitHub `carrot-ryu`(HEAD `9ff1242e`)를 직접 clone해 pre-image/post-image blob hash 가드(`fb534605` -> `e5914f28`) + anchor 1회 매치 + 치환 결과 재확인 + commit(`1 file changed, 33 insertions(+)`)까지 일반/Windows CRLF 재현 두 모드 모두 동일 결과로 dry-run(9절 항목 9, push 단계는 이 샌드박스에 GitHub 쓰기 인증정보가 없어 의도대로 거부됨). `-C` 플래그 전 지점 사용(10절).

미완료(다음 세션 최우선 순으로):
1. **156차 코드/devnotes 반영 스크립트 실행/push 확인** -- 사용자가 두 스크립트(`156cha_code_carrot_ryu.ps1`, `156cha_devnotes_carrot_ryu_note.ps1`)를 실행해야 이번 세션 작업이 실제 반영된다.
2. **156차 A안의 실기기 검증 자체가 아직 없음** -- 정상 종료 경로(기존 `finally: shutil.rmtree`)는 155차에서 이미 확인됐으나, 이번에 추가한 "다음 전송 시작 시 잔존물 정리" 경로는 강제 종료/전원 차단을 실제로 재현한 뒤 그 다음 업로드를 시작해야 검증 가능(다음 세션 또는 사용자 실기기 테스트 이월).
3. 주행 실차 검증 여전히 미실시 -- 153차 수정(`get_path_after_distance()`) 실주행 검증(분기 xTurn=4 / 톨게이트 xTurn=6 구간, 154차 이월).
4. (선택) zip 내용 무결성 확인(Drive에서 내려받아 열기), 두 번째 zip(497.5MB)이 첫 번째(459.4MB)보다 큰 이유 확인.
5. (선택) `build_zip()` 직전 `shutil.disk_usage`로 필요 용량 vs 여유를 비교하는 조기 실패 방어 코드(미포함 상태 유지).
6. 분기/톨게이트 통과 직후(xDist<0) 구간 요동에 152차 게이트(TurnSpeedControlMode==2)가 적용되는지 확인(154차 이월).
7. 잔여 비트리거 급변(세그먼트당 10~25건)의 원인 분석 미착수(154차 이월).
8. 147차 코드 탑재 디바이스 실주행 로그 검증, "선행차가 설정 차간거리 근처에서 급제동" 시나리오 정량 미검증, 148차 v1 `2>&1` 재발의 FINDINGS.md 정식 등록 여부 결정, 147차 임시 diff/블록 추출 스크립트 toolkit 미등록(모두 이전 이월, 변동 없음).

검증:
- 156차 코드: 정적 분석 + 독립 함수 단위 테스트(샌드박스, 실제 `upload_jobs.py`가 아닌 동일 로직 발췌본으로 검증 -- import 체인이 무거워 전체 모듈 import는 하지 않음) + `py_compile` + 로컬(실제 GitHub 저장소 대상) clone-to-commit 시뮬레이션(일반/Windows CRLF 재현 두 모드) + `pwsh` 파서 0 errors. 실기기/주행 실차 검증은 미실시.

주의사항:
- 이번 156차는 코드 변경 스크립트가 아직 사용자 PC에서 실행되지 않았다 -- 위 carrot-ryu HEAD는 `9ff1242e` 그대로다.
- `cleanup_stale_upload_tmp_dirs()`는 `create_job()`(=로그탭에서 새 업로드를 시작하는 시점) 진입 시에만 호출된다. 따라서 전원 차단 이후 대시캠 업로드 기능을 한 번도 다시 쓰지 않으면 잔존 zip이 계속 `/data`에 남아있을 수 있다(설계상 트레이드오프, 추천안 A 자체가 그렇게 명시돼 있었음 -- B안(서버 기동 시 전체 청소)이나 C안(수동 삭제)은 이번에 채택되지 않음).
- `/data`는 재부팅해도 비워지지 않는다(FINDINGS 핵심 발견 56 일반화 2).

다음 작업:
1. 사용자가 156차 코드/devnotes 스크립트 2개를 실행 -> push 확인.
2. 강제 종료/전원 차단을 실제로 재현한 뒤 다음 업로드 시작 시 잔존 zip이 정리되는지 실기기 검증.
3. 사용자가 주는 실주행 로그로 153차 수정 실차 검증(분기/톨게이트).
