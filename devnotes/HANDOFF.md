# HANDOFF

Worker: Claude (33차 -- ko.js 문구 수정 반영, devnotes 갱신)
Date: 2026-09-15
Repository: ryujmin97/openpilot
Code Branch: carrot-ryu (HEAD: 789667f7, 33차 "fix ko.js gdrive client id type desc")
Note Branch: carrot-ryu-note (이 커밋으로 devnotes 갱신)
carrot-ms 마지막 검토/동기화 커밋(메시지 기준): 7차 세션과 동일, 신규 커밋 없음 (이번 세션에서도 재확인하지 않음)

작업:
32차 HANDOFF.md 미완료 3번(ko.js의 web_gdrive_client_id_desc 문구 버그, 31차부터 이월)을 소규모 문자열 치환으로 수정하고 GitHub에 반영. 반영 직후 raw.githubusercontent.com 캐시 지연으로 재조회 시 이전 내용이 보이는 현상을 겪어, github.com commit diff 엔드포인트로 교차 검증해 실제 반영을 확정함. WIP.md/FINDINGS.md/HANDOFF.md/CURRENT_STATUS.md를 33차 상태로 갱신.

완료:
- ko.js web_gdrive_client_id_desc 문구 수정(commit 789667f7), "데스크톱 앱 유형" -> "TV 및 제한된 입력이 있는 기기 유형".
- WIP.md 33차 항목, FINDINGS.md 2026-09-15(33차) raw.githubusercontent.com 캐시 지연 현상 기록.
- HANDOFF.md/CURRENT_STATUS.md 33차 기준 갱신(이번 커밋).

미완료 (다음 세션 최우선, 이월):
1. [최우선, 이월] 32차 Drive 연결(drive.file 스코프+폴더 자동생성) 실기기 연결 테스트 -- 여전히 미실시.
2. [이월] 기존 폴더(구 DRIVE_FOLDER_ID)와 32차 이후 자동생성되는 새 폴더("CarrotWeb Logs") 파일 이관 필요 여부 사용자 확인 필요.
3. 28~30차 레이아웃 변경 실기기 재검증 (29차부터 이월)
4. 실차 재검증(8~33차 코드 변경 전부 이월, 12절 원칙)
5. 실기기에서 직접 디버깅: 배포된 tools.js에 "web-gdrive-connect" 문자열 실제 존재 여부 (26차부터 이월)
6. 화면녹화 전송 다이얼로그 "당근서버" 라벨 하드코딩 여부 코드 조사 (26차 발견, 미착수)
7. test_web_upload.py 실제 실행해 낡은 테스트 수 확인 -> 데드코드 3개 + 대응 테스트 삭제/갱신 (25차부터 이월)
8. docs/carrot_web_upload.md 갱신 (Drive 기준) (15차부터 이월)
9. run_upload_segments() 설계 변경 실사용 문제 없는지 재확인 (16차부터 이월)
10. carrot-ms 모델 셀렉터 코드 분석 착수 (6차 이후 계속 미착수)
11. [신규, FINDINGS 33차 참고] 16절/20절에 raw.githubusercontent.com 캐시 지연 관련 단서 추가 여부 -- 사용자 승인 필요(19절 절차 대상).

검증: 코드 변경은 텍스트 문구 1줄뿐(정적 안내 문구, 로직 영향 없음). 실차/실기기 검증: 미실시.

주의사항:
- raw.githubusercontent.com이 쿼리스트링 캐시버스터를 붙여도 한동안 이전 내용을 반환하는 사례가 이번에 재현됨(FINDINGS 33차). 다음 세션에서 "재조회했는데 반영이 안 된 것처럼 보이면" 곧바로 "미반영"으로 단정하지 말고, 먼저 github.com commit diff 엔드포인트로 교차 검증할 것.

다음 작업 후보:
1. 32차 Drive 연결 실기기 테스트 결과 확인(최우선, 사용자 액션 필요)
2. 28~30차 레이아웃 실기기 재확인
3. carrot-ms 모델 셀렉터 코드 분석 착수
4. (선택) 16절/20절에 raw.githubusercontent.com 캐시 지연 단서 추가할지 사용자에게 확인