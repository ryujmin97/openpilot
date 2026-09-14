# HANDOFF

Worker: Claude (세션 17)
Date: 2026-09-14
Repository: ryujmin97/openpilot
Code Branch: carrot-ryu (base: cc734e18 [16차 hotfix] -> 17차 send_tmux_web()
  변경 반영 완료, 실제 HEAD = 2869149af68742de2d4454f47a0e0ca0aa999a83,
  git ls-remote로 확인 완료)
Note Branch: carrot-ryu-note (이 커밋으로 17차 devnotes 반영)
carrot-ms 마지막 검토/동기화 커밋(메시지 기준): 7차 세션과 동일, 신규 커밋
없음 (WIP_SYNC.md 참고, 17차에서도 재확인하지 않음)

작업:
16차 HANDOFF 미완료 우선순위 1번 착수 및 완료. carrot_man.py의
send_tmux_web()을 Carrot/Toss 선택 전송에서 Google Drive 직접 업로드로
재작성.

완료:
- carrot_man.py: send_tmux_web() 전면 재작성 (tmux.log+toggle_values.json+
  metadata.json을 zip으로 묶어 gdrive_upload.upload_file_resumable() 호출).
  import 정리(create_web_upload_session_sync, tmux_web_target 제거,
  gdrive_upload/shutil/tempfile/zipfile/SimpleNamespace 추가).
- 반영 방식: diff(git apply) 최초 시도 실패(`corrupt patch`, 채팅 복사 중
  컨텍스트 공백 손상 추정) -> 문자열 치환(find & replace, 유일 매치 검증)
  방식으로 전환하여 성공. GitHub carrot-ryu에 실제 push 완료(commit
  2869149, git ls-remote로 재확인).
- CURRENT_STATUS.md를 13차 시점에서 16~17차 기준으로 갱신(아래 CURRENT_STATUS
  본문 참고).

미완료 / 다음 세션 우선순위:
1. api_dashcam_upload_test(연결 테스트 버튼, routes.py) -- 여전히 옛
   Carrot/Toss 헬스체크(check_web_upload_health)를 가리킴, Drive 기준으로
   갱신 필요 (15차부터 이월)
2. 프론트엔드 이식: web/src/features/logs/의 upload_progress.js,
   upload_summary.js, dashcam.js에 Drive 연결 버튼/Client ID·Secret 입력/
   인증 코드 표시 UI 추가 (15차부터 이월)
3. devnotes/PARAMS_REGISTRY.md에 신규 파라미터 3개 등록:
   CarrotGDriveClientId, CarrotGDriveClientSecret, CarrotGDriveRefreshToken
   (15차부터 이월, 아직 미착수)
4. docs/carrot_web_upload.md 갱신 (Drive 기준으로) (15차부터 이월)
5. run_upload_segments() 설계 변경 두 가지가 실사용에 문제 없는지 재확인
   (16차부터 이월: 성공/실패 판정 세그먼트별->zip 단위, Discord 알림 항상
   시도로 변경)
6. 실주행 재검증 여전히 미실시 (8~17차 코드 변경 전부 이월)
7. [사용자 승인 필요, 19절 절차] 9절의 diff(git apply) 우선순위 재검토 제안:
   diff는 채팅 복사 과정에서 컨텍스트 공백이 손상되어 실패할 수 있음이
   17차에서 실제로 확인됨. "부분 변경 시 문자열 치환을 우선 시도하고, 같은
   텍스트가 여러 곳에 나타나 유일 매치가 안 되는 경우에만 diff를 대안으로
   쓰는" 방향으로 9절을 수정할지 다음 세션에서 사용자에게 확인.

검증: 정적 분석 + 실제 GitHub carrot-ryu에 반영 완료 확인(git ls-remote로
HEAD 2869149 확인). 실제 Google Drive 계정/토큰을 통한 업로드 테스트, 실차
검증은 미실시.

주의사항:
- 17차에서 diff(git apply) 방식이 실전에서 처음으로 실패한 사례가 나왔음
  (`corrupt patch`). 원인은 채팅으로 diff를 전달하는 과정에서 컨텍스트 공백
  줄이 손상된 것으로 추정. git apply --check 단계에서 안전하게 중단되어
  carrot-ryu에는 아무 영향 없었음(15/18절 원칙 정상 작동).
- 문자열 치환으로 재작업할 때는 반드시 "치환 전 블록이 파일 내에 정확히
  1회만 존재하는지" 확인 후 치환하는 패턴을 유지할 것 (여러 곳에 매치되면
  중단하고 보고).
- send_tmux_web()의 반환값 계약(.ok/.status_code 또는 None)은 유지했으므로
  carrot_cmd_zmq() 등 호출부는 수정하지 않음 -- 만약 다음 세션에서 이 계약이
  깨지는 변경을 하게 되면 호출부 3곳(1255/1285/1318행 부근)도 함께 확인할 것.
- 다음 세션 시작 시 9절 diff 우선순위 재검토 여부를 사용자에게 먼저 물어볼 것
  (19절 절차: 사유 -> 기존 규칙 -> 변경안 -> 승인 -> 변경 -> 저장).

다음 작업 후보:
1. api_dashcam_upload_test Drive 기준으로 갱신
2. 프론트엔드(Drive 연결 UI) 이식
3. PARAMS_REGISTRY.md / docs/carrot_web_upload.md 갱신