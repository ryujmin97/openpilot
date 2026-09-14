# HANDOFF

Worker: Claude (devnotes 동기화 세션 — 코드 변경 없음, 기존 28~30차 코드 반영 확인 및 devnotes 정리만 수행)
Date: 2026-09-15
Repository: ryujmin97/openpilot
Code Branch: carrot-ryu (HEAD: 34bb41bc, 30차까지 반영 확인 완료)
Note Branch: carrot-ryu-note (이 커밋으로 devnotes 동기화 반영)
carrot-ms 마지막 검토/동기화 커밋(메시지 기준): 7차 세션과 동일, 신규 커밋 없음 (이번 세션에서도 재확인하지 않음)

작업:
사용자 요청으로 지침 문서(27차) 확인 후 4절 절차(HANDOFF.md → CURRENT_STATUS.md → carrot-ryu 최신 commit)를 진행하던 중, HANDOFF.md(29차 작성)가 "사용자 미실행"으로 기록한 레이아웃 변경이 실제로는 GitHub에 반영(29차, commit 67a8e10)돼 있을 뿐 아니라 그 이후 30차 커밋(34bb41bc)까지 이미 push되어 있는 것을 발견함. 사용자에게 확인 요청 후 "맞다"는 답변을 받아, 28~30차 커밋 3건의 diff를 직접 조회해 WIP.md에 누락된 회차 기록(28, 29, 30차)을 추가하고, HANDOFF.md/CURRENT_STATUS.md를 실제 HEAD(34bb41bc) 기준으로 갱신하며, 이 불일치 자체를 FINDINGS.md에 신규 항목으로 기록함.

완료:
- carrot-ryu 커밋 로그(atom 피드) 및 28~30차 커밋 3건(.patch)을 직접 조회해 diff 내용 확인.
- WIP.md에 28차/29차/30차 회차 요약 3건 추가(기존 27차 이하 내용은 그대로 보존).
- FINDINGS.md에 "HANDOFF.md 미반영 기록과 실제 GitHub 상태 불일치" 신규 항목 추가.
- HANDOFF.md/CURRENT_STATUS.md를 34bb41bc(30차) 기준으로 갱신.
- 사용자에게 30차 코드 기준 경로안내 박스 레이아웃을 SVG 목업(개략도)으로 렌더링해 전달함(실제 기기 픽셀/폰트와는 다름, 대화 이해를 돕기 위한 참고용).

미완료 (다음 세션 최우선, 29차 HANDOFF에서 이월):
1. 28~30차 레이아웃 변경(교차로 위치, ETA 끝맞춤 재변경, route= 크기/위치, 신호과속 위치)은 사진 한 장 + 사용자 구두 요청만으로 추정한 좌표이며 실차 화면으로 재확인되지 않음(12절 원칙) — 실기기 스크린샷으로 재검증 필요. 특히 route=/도착/ETA가 회전 아이콘 초록박스와 세로로 겹치지 않는지 확인 필요.
2. 실차 재검증(8~30차 코드 변경 전부 이월, 12절 원칙)
3. 실기기에서 직접 디버깅: 배포된 tools.js에 "web-gdrive-connect" 문자열 실제 존재 여부, 브라우저 강제새로고침/시크릿모드 재현 여부 (26차부터 이월)
4. 화면녹화 전송 다이얼로그 "당근서버" 라벨 하드코딩 여부 코드 조사 (26차 발견, 미착수)
5. test_web_upload.py 실제 실행(또는 최소 import/픽스처 점검)해 낡은 테스트 수 확인 -> 데드코드 3개(tmux_web_target, resolve_upload_target, upload_target_settings) + 대응 테스트 삭제/갱신 (25차부터 이월)
6. 실제 Google Cloud Console OAuth 클라이언트 발급 + 콤마 기기 Drive 연결 테스트(device flow 전체) (15차부터 이월)
7. docs/carrot_web_upload.md 갱신 (Drive 기준) (15차부터 이월)
8. run_upload_segments() 설계 변경 두 가지 실사용 문제 없는지 재확인 (16차부터 이월)
9. carrot-ms 모델 셀렉터 코드 분석 착수 (6차 이후 계속 미착수)

검증: 이번 세션은 devnotes(문서) 반영만 수행하고 코드 파일은 건드리지 않음. carrot-ryu 코드는 사용자가 이미 실행/반영한 28~30차 스크립트 결과를 GitHub에서 커밋 로그와 파일 내용(raw.githubusercontent.com)으로 재조회해 확인한 것뿐임. 실차 검증: 미실시(12절 원칙).

주의사항:
- 이번 세션에서 확인된 절차 실패 사례(29차 HANDOFF의 "미실행" 기록이 실제와 달랐던 것)는 FINDINGS.md에 상세 기록함 — 다음 세션은 특히 4절 3번(carrot-ryu 최신 commit 확인)을 절대 건너뛰지 말 것.
- "신호과속" 배지 위치는 29차부터 초록박스 "내부"가 아니라 초록박스 바로 "아래(붙임)"로 구현되어 있음 — 30차에서도 이 방식 유지됨.
- HANDOFF.md/CURRENT_STATUS.md는 "항상 최신 1개 버전만 유지"하는 교체형 파일이므로, 이번에 전체 교체함(9절).

다음 작업 후보:
1. 실기기 스크린샷으로 28~30차 레이아웃(교차로 위치/ETA 끝맞춤/route= 위치/신호과속 위치) 재확인, 필요 시 좌표 미세조정
2. 실기기 터미널로 배포된 tools.js 내용 확인 (26차부터 이월, 원인 규명의 핵심)
3. carrot-ms 모델 셀렉터 코드 분석 착수
4. test_web_upload.py 실행/데드코드 정리 착수
