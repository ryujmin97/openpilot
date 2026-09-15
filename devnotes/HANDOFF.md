# HANDOFF

Worker: Claude (32차 devnotes 정리 세션 -- 코드 변경 없음, 이미 GitHub에 반영된 32차 커밋을 devnotes에 반영)
Date: 2026-09-15
Repository: ryujmin97/openpilot
Code Branch: carrot-ryu (HEAD: c704371a, 32차 "gdrive drive.file scope + folder auto-create revert")
Note Branch: carrot-ryu-note (이 커밋으로 devnotes 갱신)
carrot-ms 마지막 검토/동기화 커밋(메시지 기준): 7차 세션과 동일, 신규 커밋 없음 (이번 세션에서도 재확인하지 않음)

작업:
세션 시작 시 4절 절차로 carrot-ryu 최신 커밋을 확인한 결과, 31차 HANDOFF.md에는 기록되지 않았던 32차 커밋(c704371a, drive.file 스코프+폴더 자동생성 복귀)이 이미 GitHub에 반영돼 있음을 발견(16절 상황). github.com commit diff를 직접 조회해 실제 변경 내용을 확인하고, WIP.md/FINDINGS.md/HANDOFF.md/CURRENT_STATUS.md를 이 32차 상태 기준으로 갱신함. 코드 자체는 이번 세션에서 수정하지 않음.

완료:
- 32차 커밋(c704371a) 내용을 diff로 직접 확인·devnotes에 기록(WIP.md 32차 항목, FINDINGS.md 2026-09-15(32차) 항목).
- CURRENT_STATUS.md/HANDOFF.md를 실제 GitHub 상태(HEAD c704371a) 기준으로 갱신(이번 커밋).

미완료 (다음 세션 최우선, 이월):
1. [갱신, 최우선] 32차 변경(drive.file 스코프+폴더 자동생성) 실기기 연결 테스트 필요 -- 31차에서 겪은 Invalid device flow scope 에러가 실제로 해소됐는지, 새 폴더("CarrotWeb Logs")가 정상 자동생성/재사용되는지 확인되지 않음.
2. [신규, FINDINGS 32차 참고] 기존에 사용자가 미리 만들어둔 폴더(구 DRIVE_FOLDER_ID)에 있던 파일과, 32차 이후 앱이 자동생성하는 새 폴더("CarrotWeb Logs")가 분리됨 -- 기존 파일 이관 필요 여부 사용자에게 확인 필요.
3. [이월] ko.js의 web_gdrive_client_id_desc 문구("데스크톱 앱 유형" -> "TV 및 제한된 입력이 있는 기기 유형") 수정 -- 31차부터 이월, 아직 미수정.
4. 28~30차 레이아웃 변경 실기기 재검증 (29차부터 이월)
5. 실차 재검증(8~32차 코드 변경 전부 이월, 12절 원칙)
6. 실기기에서 직접 디버깅: 배포된 tools.js에 "web-gdrive-connect" 문자열 실제 존재 여부, 브라우저 강제새로고침/시크릿모드 재현 여부 (26차부터 이월)
7. 화면녹화 전송 다이얼로그 "당근서버" 라벨 하드코딩 여부 코드 조사 (26차 발견, 미착수)
8. test_web_upload.py 실제 실행(또는 최소 import/픽스처 점검)해 낡은 테스트 수 확인 -> 데드코드 3개 + 대응 테스트 삭제/갱신 (25차부터 이월)
9. docs/carrot_web_upload.md 갱신 (Drive 기준) (15차부터 이월)
10. run_upload_segments() 설계 변경 두 가지 실사용 문제 없는지 재확인 (16차부터 이월)
11. carrot-ms 모델 셀렉터 코드 분석 착수 (6차 이후 계속 미착수)

검증: 이번 세션은 코드 파일을 전혀 건드리지 않음(devnotes 정리만). 실차 검증: 미실시(12절 원칙, 해당 없음 -- 코드 변경 없음). 32차 코드 변경(다른 경로로 이미 반영됨) 자체도 실기기 검증 미실시 상태.

주의사항:
- 32차 커밋을 실제로 어떤 경로로 반영했는지 devnotes에는 기록이 없음(16절 상황) -- 다음에도 유사하게 "기록 없는 반영"이 발견되면 GitHub 실제 상태를 우선 기준으로 삼을 것.
- 다음 세션은 반드시 먼저 사용자에게 32차 변경의 실기기 연결 테스트 결과를 확인한 뒤, 통과하면 미완료 3번(ko.js 문구), 실패하면 재설계 방향을 다시 논의할 것.

다음 작업 후보:
1. 32차 변경 실기기 Drive 연결 테스트 결과 확인(최우선, 사용자 액션 필요)
2. ko.js 클라이언트 유형 안내 문구 수정
3. 28~30차 레이아웃 실기기 재확인
4. carrot-ms 모델 셀렉터 코드 분석 착수