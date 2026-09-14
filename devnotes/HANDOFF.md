# HANDOFF

Worker: Claude (세션 16)
Date: 2026-09-14
Repository: ryujmin97/openpilot
Code Branch: carrot-ryu (HEAD: cc734e18a90d55365bf2e8b98993142496d20959 --
  16차 본편(dae901ce) + hotfix(cc734e18) 모두 push 완료 확인, GitHub 실제
  파일 재조회로 4개 파일 py_compile 통과 재검증함)
Note Branch: carrot-ryu-note (이 커밋으로 16차 devnotes 반영)
carrot-ms 마지막 검토/동기화 커밋(메시지 기준): 7차 세션과 동일, 신규 커밋
없음 (WIP_SYNC.md 참고, 16차에서도 재확인하지 않음 -- 순수 Drive 전환
코드 작업만 진행)

작업:
15차에서 만든 gdrive_upload.py를 실제로 호출부에 연결. 대시캠 업로드
(로그탭 "전송" 버튼)를 zip 압축 + Google Drive resumable 업로드 방식으로
전면 전환. 반영 과정에서 발생한 스크립트 버그(CRLF/상대경로/here-string
개행/py_compile exit code)를 실전에서 발견하고 수정.

완료:
- gdrive_upload.py: progress_cb 콜백 파라미터 추가
- server/features/dashcam/upload_jobs.py: run_upload_segments() zip+Drive
  방식으로 재작성
- server/app.py: gdrive_upload.register(app) 앱 진입점 연결
- server/services/dashcam_upload_report.py: gdrive 대상일 때
  Open&Analyze 링크 스킵
- 4개 파일 모두 carrot-ryu에 push 완료 및 GitHub 재조회로 컴파일 검증 완료
- 반영 스크립트의 버그 3종(CRLF 정규화 누락, 상대경로/작업디렉터리 불일치,
  here-string 개행 소실) + 검증 누락 1종(py_compile exit code 미확인)을
  실전에서 발견하고 표준 처리 방식 확립 (WIP.md 16차 항목에 상세 기록)

미완료 / 다음 세션 우선순위:
1. **carrot_man.py의 send_tmux_web() 재작성** (15차부터 이월) -- tmux
   진단 중 "carrot/toss 선택 전송"을 gdrive_upload.upload_file_resumable()
   직접 호출로 교체. send_tmux_carrot_logs()(Discord carrot_logs 포럼용
   고정 전송)는 손대지 않음
2. api_dashcam_upload_test(연결 테스트 버튼, routes.py) -- 여전히 옛
   Carrot/Toss 헬스체크(check_web_upload_health)를 가리킴, Drive 기준으로
   갱신 필요 (15차부터 이월)
3. 프론트엔드 이식: web/src/features/logs/의 upload_progress.js,
   upload_summary.js, dashcam.js에 Drive 연결 버튼/Client ID·Secret 입력/
   인증 코드 표시 UI 추가 (15차부터 이월)
4. devnotes/PARAMS_REGISTRY.md에 신규 파라미터 3개 등록:
   CarrotGDriveClientId, CarrotGDriveClientSecret, CarrotGDriveRefreshToken
   (15차부터 이월, 아직 미착수)
5. docs/carrot_web_upload.md 갱신 (Drive 기준으로) (15차부터 이월)
6. run_upload_segments() 설계 변경 두 가지가 실사용에 문제 없는지 재확인:
   - 성공/실패 판정이 "세그먼트별" -> "zip 전체 단위"로 바뀐 것
   - Discord 알림이 target 무관 항상 시도로 바뀐 것
7. 실주행 재검증 여전히 미실시 (8~16차 코드 변경 전부 이월)
8. (참고용, 조치 불필요) 이번 세션에서 표준화한 반영 스크립트 패턴
   (Read-Utf8Lf, 절대경로 고정, here-string 끝 개행 확인, py_compile
   $LASTEXITCODE 확인)을 앞으로 모든 반영 스크립트에 기본 적용할 것

검증: 정적 분석 + Claude 샌드박스 mock 시뮬레이션 + 실제 사용자 PC에서의
스크립트 실행(3회 시행착오 끝에 성공) + GitHub 실제 파일 재조회를 통한
최종 컴파일 검증까지 완료. 실제 Google Drive 계정/토큰 업로드 테스트,
실차 검증은 미실시.

주의사항:
- 앞으로 문자열 치환/here-string으로 새 텍스트를 만들 때는 끝에 개행이
  있는지 반드시 눈으로 재확인할 것 (이번 세션 hotfix의 근본 원인)
- 반영 스크립트에서 python 등 외부 프로세스를 호출해 검증할 때는
  $LASTEXITCODE를 반드시 확인할 것 (PowerShell은 외부 프로세스의 실패를
  자동으로 터미네이팅 에러로 처리하지 않음)
- carrot_man.py의 send_tmux_web()은 아직 옛 Carrot/Toss 분기 그대로임 --
  대시캠 업로드만 Drive로 바뀌고 tmux 선택 전송은 아직 안 바뀐 "과도기"
  상태

다음 작업 후보:
1. carrot_man.py의 send_tmux_web() Drive 재작성
2. api_dashcam_upload_test Drive 기준으로 갱신
3. 프론트엔드(Drive 연결 UI) 이식
4. PARAMS_REGISTRY.md / docs/carrot_web_upload.md 갱신
