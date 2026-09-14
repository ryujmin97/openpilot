# HANDOFF

Worker: Claude (세션 20)
Date: 2026-09-14
Repository: ryujmin97/openpilot
Code Branch: carrot-ryu (base: 17차 2869149 -> 18차 반영 실패(patch 파일만 커밋) -> 19차 a44f1580(routes.py/test_web_upload.py 반영 + patch 파일 정리) -> 20차 ad055dd4(gdrive_upload.py test_connection 추가), 실제 HEAD = ad055dd4, raw.githubusercontent.com으로 3개 파일 직접 재조회하여 확인 완료)
Note Branch: carrot-ryu-note (이 커밋으로 18~20차 devnotes 및 PROJECT_INSTRUCTIONS 반영)
carrot-ms 마지막 검토/동기화 커밋(메시지 기준): 7차 세션과 동일, 신규 커밋 없음 (WIP_SYNC.md 참고, 이번 세션에서도 재확인하지 않음)

작업:
16차 HANDOFF 미완료 우선순위 1번(api_dashcam_upload_test 연결 테스트 버튼을 Google Drive 기준으로 갱신) 착수 및 완료.

완료:
- gdrive_upload.py: test_connection() 추가 (access_token 갱신 + 대상 폴더 조회 왕복으로 실제 연동 확인)
- routes.py: api_dashcam_upload_test를 gdrive_upload.test_connection() 기준으로 교체, 옛 web_upload import/upload 모듈 참조 제거
- test_web_upload.py: 관련 테스트 3개로 교체(라우트 유일성, 연결 성공, 연결 실패)
- 반영 과정에서 diff(git apply)가 에러 없이 "성공"으로 보고했으나 실제로는 미반영되는 사례 발견(18차) -> 문자열 블록 치환 방식으로 전환하여 성공(19~20차, 도중 Claude의 anchor 오타로 한 번 안전 중단 -> 정정 후 최종 성공)
- 사용자 승인 하에 9절을 문자열 치환 우선으로 개정, PROJECT_INSTRUCTIONS_carrot-ryu.md 전체 교체 반영(이 커밋에 포함)
- carrot-ryu-note의 PROJECT_INSTRUCTIONS_carrot-ryu.md가 이미 12차 버전까지 앞서 있었는데 이번 세션이 9차 버전을 붙여넣은 채로 시작된 것을 발견, 이번 반영으로 최신화

미완료 / 다음 세션 우선순위:
1. 프론트엔드 이식: web/src/features/logs/의 upload_progress.js, upload_summary.js, dashcam.js에 Drive 연결 버튼/Client ID·Secret 입력/인증 코드 표시 UI 추가 (15차부터 이월)
2. devnotes/PARAMS_REGISTRY.md에 신규 파라미터 3개 등록: CarrotGDriveClientId, CarrotGDriveClientSecret, CarrotGDriveRefreshToken (15차부터 이월, 아직 미착수)
3. docs/carrot_web_upload.md 갱신 (Drive 기준으로) (15차부터 이월)
4. run_upload_segments() 설계 변경 두 가지가 실사용에 문제 없는지 재확인 (16차부터 이월)
5. 실주행 재검증 여전히 미실시 (8~20차 코드 변경 전부 이월)
6. carrot-ms 모델 셀렉터 코드 분석 착수 (6차 이후 계속 미착수)

검증: 정적 분석 + 실제 GitHub carrot-ryu에 반영 완료 확인(raw.githubusercontent.com으로 ad055dd4 시점 3개 파일 직접 재조회, test_connection 정의/routes.py import·함수 교체 확인). 실제 Google Drive 계정 업로드 테스트, 실차 검증 전부 미실시.

주의사항:
- diff(git apply)가 18차에서 에러 없이 "적용 완료"로 보고했지만 실제로는 반영되지 않고 임시 patch 파일만 잘못 커밋되는, 17차(corrupt patch로 안전 중단)보다 더 나쁜 형태의 실패였음. 9절이 문자열 블록 치환 우선으로 개정되었으니 다음 세션부터는 이 방식을 기본으로 사용할 것.
- 문자열 블록 치환도 Claude가 anchor 텍스트를 정확히 옮기지 못하면(20차 직전 사례, dict[str, Any] vs dict[str, dict[str, Any]]) 매치 0회로 안전하게 중단됨 -- 이 경우 GitHub 최신 원본을 바이트 단위로 다시 대조해서 정정할 것.
- 스크립트에서 Push-Location/Pop-Location 대신 git -C $TempDir 방식을 사용하는 것이 새 표준(18차 폴더 잠금/삭제 실패와 연관 추정).
- 다음 세션은 반드시 carrot-ryu-note의 PROJECT_INSTRUCTIONS_carrot-ryu.md를 GitHub에서 최우선 조회할 것(채팅에 붙여넣어진 사본을 신뢰하지 말 것 -- 이번 세션에서 실제로 9차 vs 12차 버전 차이가 있었음).

다음 작업 후보:
1. 프론트엔드(Drive 연결 UI) 이식
2. PARAMS_REGISTRY.md / docs/carrot_web_upload.md 갱신
3. carrot-ms 모델 셀렉터 코드 분석 착수