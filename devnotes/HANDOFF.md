# HANDOFF

Worker: Claude (31차 -- Google Drive OAuth 연결 실패 원인 조사, 코드 변경 없음)
Date: 2026-09-15
Repository: ryujmin97/openpilot
Code Branch: carrot-ryu (HEAD: 34bb41bc, 30차와 동일, 이번 세션 코드 변경 없음)
Note Branch: carrot-ryu-note (이 커밋으로 devnotes 갱신)
carrot-ms 마지막 검토/동기화 커밋(메시지 기준): 7차 세션과 동일, 신규 커밋 없음 (이번 세션에서도 재확인하지 않음)

작업:
사용자가 실기기에서 Google Drive 연결(Device Authorization Grant)을 시도하다 겪은 3단계 에러를 순서대로 조사함. 최종적으로 Google이 Device Authorization Grant에서 전체 Drive 스코프를 구조적으로 차단하고 있다는 근본 원인을 외부 사례로 확인, gdrive_upload.py(15차) 설계와의 충돌을 확인함. 코드 수정은 진행하지 않고 devnotes에 조사 경과와 대안을 기록, 사용자 결정을 요청하며 세션을 체크포인트함.

완료:
- OAuth 클라이언트 ID 형식 문제, UI 안내 문구(클라이언트 유형) 불일치, 동의 화면 스코프 미등록 등 1~3차 가설을 순서대로 조사/배제.
- Google Device Authorization Grant가 전체 Drive 스코프를 정책적으로 차단한다는 근본 원인 확인(웹 검색, 다수 독립 사례).
- gdrive_upload.py의 스코프 확장 설계(15차)가 이 제약과 충돌함을 코드 주석과 대조해 확인.
- WIP.md에 31차 회차 기록 추가, FINDINGS.md에 신규 항목 추가, HANDOFF.md/CURRENT_STATUS.md 갱신(이번 커밋).

미완료 (다음 세션 최우선, 이월):
1. [신규, 최우선] Google Drive 연동 방식 재설계 방향 결정 필요 -- (a) drive.file 스코프+폴더 자동생성 방식 복귀, (b) 표준 Authorization Code Flow로 전면 재설계, (c) Drive 자체를 다른 저장 수단으로 대체. 사용자 결정 후 착수.
2. [신규] ko.js의 web_gdrive_client_id_desc 문구("데스크톱 앱 유형" -> "TV 및 제한된 입력이 있는 기기 유형")를 실제 요구사항에 맞게 수정 -- 이번 에러의 직접 원인은 아니었으나 명백한 버그.
3. 28~30차 레이아웃 변경 실기기 재검증 (29차부터 이월)
4. 실차 재검증(8~30차 코드 변경 전부 이월, 12절 원칙)
5. 실기기에서 직접 디버깅: 배포된 tools.js에 "web-gdrive-connect" 문자열 실제 존재 여부, 브라우저 강제새로고침/시크릿모드 재현 여부 (26차부터 이월)
6. 화면녹화 전송 다이얼로그 "당근서버" 라벨 하드코딩 여부 코드 조사 (26차 발견, 미착수)
7. test_web_upload.py 실제 실행(또는 최소 import/픽스처 점검)해 낡은 테스트 수 확인 -> 데드코드 3개 + 대응 테스트 삭제/갱신 (25차부터 이월)
8. docs/carrot_web_upload.md 갱신 (Drive 기준) (15차부터 이월)
9. run_upload_segments() 설계 변경 두 가지 실사용 문제 없는지 재확인 (16차부터 이월)
10. carrot-ms 모델 셀렉터 코드 분석 착수 (6차 이후 계속 미착수)

검증: 이번 세션은 코드 파일을 전혀 건드리지 않음(조사/devnotes만). 실차 검증: 미실시(12절 원칙, 해당 없음 -- 코드 변경 없음).

주의사항:
- 다음 세션은 반드시 먼저 사용자에게 Drive 연동 재설계 방향(미완료 1번)을 확인한 뒤 착수할 것.
- gdrive_upload.py의 "필요 사전 준비" 안내(파일 상단 docstring)는 이번 조사로 드러난 device flow 스코프 제약을 반영하고 있지 않으므로, 재설계 방향이 정해지면 이 docstring도 함께 갱신 필요.

다음 작업 후보:
1. Google Drive 연동 재설계 방향 결정 및 착수(가장 시급)
2. ko.js 클라이언트 유형 안내 문구 수정
3. 28~30차 레이아웃 실기기 재확인
4. carrot-ms 모델 셀렉터 코드 분석 착수