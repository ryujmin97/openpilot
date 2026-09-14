# HANDOFF

Worker: Claude (세션 25)
Date: 2026-09-14
Repository: ryujmin97/openpilot
Code Branch: carrot-ryu (HEAD: d338afb7, 25차 LOG_UPLOAD_TARGETS "gdrive" 누락 수정 반영 완료. base: a7a912c1(24차) -> d338afb7(25차))
Note Branch: carrot-ryu-note (이 커밋으로 25차 devnotes 반영, base: 92ad0b3(24차 계속2))
carrot-ms 마지막 검토/동기화 커밋(메시지 기준): 7차 세션과 동일, 신규 커밋 없음 (이번 세션에서도 재확인하지 않음)

작업:
24차 계속2에서 발견한 LOG_UPLOAD_TARGETS "gdrive" 누락 버그를 사용자 승인 후 문자열 치환으로 수정, GitHub push 및 raw.githubusercontent.com 직접 재조회로 반영 확인. 이어서 사용자가 요청한 "관련 데드코드 삭제"를 조사하다 범위가 예상보다 커짐을 발견(데드코드 3개는 확인했으나, 그중 하나를 지우려면 test_web_upload.py의 이미 깨져있을 가능성이 높은 낡은 테스트까지 함께 정리해야 함) -> 사용자와 협의해 이번 세션은 버그 수정까지만 반영하고 데드코드/테스트 정리는 다음 세션으로 이월하기로 결정.

완료:
- LOG_UPLOAD_TARGETS에 "gdrive" 추가(server/services/web_settings.py), GitHub 반영 확인(commit d338afb7)
- web_upload.py `UPLOAD_TARGETS`/`selected_upload_settings()`가 실제로는 carrot_man.py의 `_tmux_toss_only()`가 쓰는 살아있는 코드임을 확인(이전 세션 보고 정정)
- 진짜 데드코드 3개 확인: web_upload.py의 `tmux_web_target()`, dashcam/upload.py의 `resolve_upload_target()`/`upload_target_settings()` (프로덕션 호출자 없음, 테스트에서만 참조)
- test_web_upload.py 조사 중, `test_dashcam_upload_completion_notifies_web_server_and_discord`가 16차에 이미 제거된 `upload_jobs.upload_folder_to_web`/`send_web_upload_complete`를 monkeypatch하고 있어 이미 깨져 있을 가능성이 높은 낡은 테스트임을 발견(직접 실행 검증은 못함)

미완료 / 다음 세션 우선순위:
1. test_web_upload.py를 실제로 실행(또는 최소 import/픽스처 점검)해 낡은 테스트가 몇 개나 있는지 정량 확인 -> 데드코드 3개(tmux_web_target, resolve_upload_target, upload_target_settings) + 대응 테스트 삭제/갱신 한 번에 진행
2. 실기기에서 web-settings 다이얼로그를 열어 "업로드 서버" 드롭다운 아래로 스크롤 시 Client ID/Secret 입력란이 실제로 보이는지 확인 (스크롤 가설 검증, 24차 계속2부터 이월)
3. 실제 Google Cloud Console에서 OAuth 클라이언트 발급 + 콤마 기기에서 실제 Drive 연결 테스트(device flow 전체) (15차부터 이월)
4. docs/carrot_web_upload.md 갱신 (Drive 기준으로) (15차부터 이월)
5. run_upload_segments() 설계 변경 두 가지가 실사용에 문제 없는지 재확인 (16차부터 이월)
6. 실주행 재검증 여전히 미실시 (8~25차 코드 변경 전부 이월)
7. carrot-ms 모델 셀렉터 코드 분석 착수 (6차 이후 계속 미착수)

검증: LOG_UPLOAD_TARGETS 수정은 raw.githubusercontent.com으로 실제 파일 내용 직접 재확인 완료(5절/16절/20절 원칙). 데드코드/낡은 테스트 관련 내용은 grep 기반 정적 조사만 했고, 실제 pytest 실행 검증은 하지 못함(FINDINGS.md 참고). 실차 검증, 실제 Drive 연결 테스트는 여전히 미실시.

주의사항:
- "죽은 코드 삭제" 요청이 실제로는 더 큰 작업(낡은 테스트 뭉치 정리)과 얽혀 있을 수 있다는 점을 발견 -- 10절(최소 변경)/17절(세션 크기 관리) 원칙에 따라 범위를 분리해 이월함. 다음 세션에서 이 작업을 시작할 때는 반드시 먼저 test_web_upload.py 실행 가능 여부부터 확인할 것.
- 처음 보고했던 "web_upload.py의 UPLOAD_TARGETS도 죽은 코드"라는 판단은 틀렸음(정정: `_tmux_toss_only()`가 실사용). 다음 세션에서 데드코드 삭제 시 이 정정 내용을 다시 확인할 것(FINDINGS.md 참고).

다음 작업 후보:
1. test_web_upload.py 실행 가능 여부 확인 -> 낡은 테스트 범위 확정 -> 데드코드 3개 + 테스트 정리
2. 실기기 스크롤 확인
3. 실제 Drive 연결 테스트 (Google Cloud Console 클라이언트 발급 필요, 사용자 액션 필요)
4. docs/carrot_web_upload.md 갱신
5. carrot-ms 모델 셀렉터 코드 분석 착수