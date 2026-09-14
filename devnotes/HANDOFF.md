# HANDOFF

Worker: Claude (세션 22)
Date: 2026-09-14
Repository: ryujmin97/openpilot
Code Branch: carrot-ryu (base: 20차 ad055dd4 -> 22차 48c2e081(params_keys.h에 CarrotGDrive* 3종 등록), 실제 HEAD = 48c2e081, raw.githubusercontent.com으로 직접 재조회하여 확인 완료)
Note Branch: carrot-ryu-note (이 커밋으로 21차 소급 기록 + 22차 devnotes 반영, base: 21da1364)
carrot-ms 마지막 검토/동기화 커밋(메시지 기준): 7차 세션과 동일, 신규 커밋 없음 (WIP_SYNC.md 참고, 이번 세션에서도 재확인하지 않음)

작업:
HANDOFF 다음 작업 후보 2번(PARAMS_REGISTRY.md 파라미터 3종 등록)을 진행하던 중, gdrive_upload.py가 사용하는 3개 파라미터(CarrotGDriveClientId/Secret/RefreshToken)가 openpilot/common/params_keys.h에 전혀 등록되지 않은 버그를 발견 -> 사용자 승인 하에 범위를 확대하여 코드 수정까지 완료.

완료:
- (버그 발견) gdrive_upload.py가 사용하는 CarrotGDriveClientId/CarrotGDriveClientSecret/CarrotGDriveRefreshToken이 params_keys.h에 미등록 -> Params.get()/.put() 호출 시 UnknownKeyName 예외 -> Drive "연결" 버튼을 누르는 순간부터 15~20차 내내 항상 실패했을 버그를 정적 분석으로 확인 (FINDINGS.md 2026-09-14 참고)
- params_keys.h에 3줄 추가({PERSISTENT, STRING}, 다른 Carrot* 파라미터와 동일 패턴), 문자열 블록 치환 방식으로 반영, carrot-ryu commit 48c2e081, raw.githubusercontent.com으로 반영 내용 직접 재확인 완료
- PARAMS_REGISTRY.md에 3개 파라미터(이름/타입/용도) + 버그 경위 등록
- 21차 devnotes 누락 발견 및 소급 기록(WIP.md에 21차 회차 추가) — 21차는 PROJECT_INSTRUCTIONS_carrot-ryu.md만 갱신한 세션(carrot-ryu-note commit 21da1364)이었음을 확인

미완료 / 다음 세션 우선순위:
1. 프론트엔드 이식: web/src/features/logs/의 upload_progress.js, upload_summary.js, dashcam.js에 Drive 연결 버튼/Client ID·Secret 입력/인증 코드 표시 UI 추가 (15차부터 이월)
2. docs/carrot_web_upload.md 갱신 (Drive 기준으로) (15차부터 이월)
3. run_upload_segments() 설계 변경 두 가지가 실사용에 문제 없는지 재확인 (16차부터 이월)
4. 실제 Google Cloud Console에서 OAuth 클라이언트 발급 + 콤마 기기에서 실제 Drive 연결 테스트(device flow 전체) — params_keys.h 수정으로 최소한 저장 단계 예외는 해소됐으나, 그 외 흐름 전체는 여전히 미검증 (15차부터 이월, 이번 세션에서 원인 하나 제거됨)
5. 실주행 재검증 여전히 미실시 (8~22차 코드 변경 전부 이월)
6. carrot-ms 모델 셀렉터 코드 분석 착수 (6차 이후 계속 미착수)

검증: 정적 분석 + 실제 GitHub carrot-ryu에 반영 완료 확인(raw.githubusercontent.com으로 48c2e081 시점 params_keys.h 직접 재조회, 3줄이 의도한 위치에 정확히 존재함을 확인). 실제 Google Drive 계정 연결 테스트, 실차 검증 전부 미실시.

주의사항:
- 이번 발견은 "가벼운 문서 작업"으로 시작했다가 실제 코드 버그로 이어진 사례. 앞으로 PARAMS_REGISTRY.md처럼 가벼워 보이는 devnotes 작업도, 대상 코드의 실제 파라미터 이름을 조회하는 과정에서 params_keys.h 등록 여부를 함께 확인하는 습관을 들일 것.
- 21차처럼 "지침 문서만 갱신되고 WIP/HANDOFF/CURRENT_STATUS는 갱신 안 되는" 상황이 재발하지 않도록, 지침 문서(PROJECT_INSTRUCTIONS_carrot-ryu.md) 변경이 있는 세션은 항상 WIP.md에도 최소 한 줄이라도 회차 기록을 남길 것.
- 여전히 diff/git apply는 예외적 보조 수단으로만 사용, 문자열 블록 치환이 기본(20절 원칙 유지, 이번에도 정상 작동).

다음 작업 후보:
1. 실제 Drive 연결 테스트 (Google Cloud Console 클라이언트 발급 필요, 사용자 액션 필요)
2. 프론트엔드(Drive 연결 UI) 이식
3. docs/carrot_web_upload.md 갱신
4. carrot-ms 모델 셀렉터 코드 분석 착수