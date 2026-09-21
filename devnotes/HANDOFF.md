Worker: Claude (118차, Claude Sonnet 5)
Date: 2026-09-21
Repository: ryujmin97/openpilot
Code Branch: carrot-ryu (base `df7da7d5`, 118차 web_upload.py/upload.py 구 웹 업로드 경로(3차 배치) 삭제 반영 확인. 부모 `22b101f6` = 117차 VW MEB 삭제)
Note Branch: carrot-ryu-note (이 스크립트 반영 전 base `e0ba99b1fcfb7355924e3712830624ff8739d472`. 반영 후 HEAD는 다음 세션이 git ls-remote로 확인)
carrot-ms 마지막 검토/동기화 체크포인트: `4bb4b510`(camera_sync 스큐 허용오차 10ms->20ms) 반영 완료(WIP_SYNC.md 116차). 111차 확정 체크포인트는 `a23a77b1`. 이번 세션은 carrot-ms 동기화 작업 없음.

작업:
1. DEAD_CODE_REVIEW.md 3차 배치(web_upload.py/server/features/dashcam/upload.py 구 웹 업로드 경로) 삭제: web_upload.py 7개 함수/그룹 + upload.py 2개 함수(총 9개 심볼) 및 관련 테스트 17개 제거. 3개 파일 +5/-814.

완료:
1. 세션 시작 확인: 지침 v2 조회(SHA 고정), HANDOFF.md(117차) 확인, 브랜치 HEAD 확인(HANDOFF 기록과 일치, 16절).
2. 사용자가 채팅에 붙여넣은 "3차 배치" 분석 초안이 이번 세션에서 검증된 것이 아니고 DEAD_CODE_REVIEW.md에도 기록이 없음을 확인 -> 재검증 필요성을 사용자에게 보고 후 승인받아 tarball+grep으로 직접 재검증(11절).
3. 재검증 중 초안의 오차 2건 발견 및 정정(api_url() 생존->사망 재분류, 영향 테스트 11->17개 재계산). 자세한 내용은 WIP.md 118차, DEAD_CODE_REVIEW.md 118차 항목 참고.
4. 코드 스크립트(`118cha_web_upload_dead_code_code_carrot_ryu-v1.ps1`) 준비: 9개 심볼 + 17개 테스트 + 헬퍼 클래스 3개 삭제, 전면 재작성 방식(9절), py_compile 통과, 전달 전 자가검증 체크리스트(BOM 없음/core.eol=lf/finally cleanup/byte-exact 시뮬레이션) 전부 통과.
5. 코드 스크립트 v1 실행·push 완료(carrot-ryu `df7da7d5`, 3개 파일 +5/-814). 로그로만 판단하지 않고 `git ls-remote`, 커밋 `.patch`, SHA 고정 tarball grep(삭제 심볼 잔여 참조 0건, opendbc_repo 제외), AST import 검사, py_compile로 재확인(16절).
6. 노트 스크립트 v1이 WIP.md 앵커 확인에서 안전 중단(아무것도 push되지 않음) -> 원인 둘(.ps1 CRLF, 큰따옴표 앵커 안 백틱 소실) 확인 후 v2로 대체. 이 v2 스크립트로 WIP.md 118차, HANDOFF.md, DEAD_CODE_REVIEW.md(118차 항목)를 갱신.

미완료(다음 세션 최우선):
1. 실차 배포(디바이스 pull) 시점 -- 사용자 확인 후. 115차 dead code 1차 배치(`0e1bef52`), 116차 camera_sync(`62ae74dc`), 117차 VW MEB 삭제(`22b101f6`), 118차 웹 업로드 경로 삭제(`df7da7d5`)가 모두 미배포로 누적돼 있어 한 번에 반영된다. 배포 후 swaglog로 controlsd/플래너 예외와 카메라 페어링 이상 여부, 그리고 대시캠 업로드(Google Drive) 정상 동작 여부 확인.
2. (이월) 114차 MAP_TURN_GUIDE_FACTOR 1.00 실차 관찰, 110차 GATE_M 0.8/1.0 관찰, 견고성 스윕 재개(선택). CURRENT_STATUS.md는 이번에도 갱신하지 않았다.
3. 117차부터 이월된 CRLF 사고 교훈을 FINDINGS.md에 기록할지 결정(핵심 발견 번호 체계 확인 필요) -- 이번 118차에서도 아직 미기록.
4. pytest 자체 실행 미실시 상태가 누적 중(conftest.py/컴파일 의존성 부재). 필요하면 사용자 실제 디바이스나 별도 환경에서 실행해 재확인하는 방안을 고려.

검증: 샌드박스 정적 검증만(ast.parse + py_compile 3파일 전부 통과, 삭제 심볼 잔여 참조 0건 재grep, .ps1 here-string 추출 내용과 원본 byte-exact 일치). pytest 실행은 미실시(11절/12절, 이전 세션들과 동일한 한계). 실차 검증: 미실시(이번 세션 전체).

주의사항:
- 채팅에 붙여넣어진 이전 세션 요약/분석은 이번 세션에서 검증된 것으로 간주하지 않는다(3절). 이번 세션에서 실제로 DEAD_CODE_REVIEW.md에 기록이 없는 "3차 배치" 주장을 발견해 재검증했고, 그 결과 오차 2건(api_url 생존 오분류, 테스트 개수 11->17)을 잡아냈다 -- 향후 세션도 동일하게 채팅 사본을 곧바로 신뢰하지 말 것.
- `.ps1`을 CRLF로 만들면 여러 줄 문자열/here-string에 `\r\n`이 들어가 LF 파일과의 비교·치환이 실패하거나 개행이 섞인다. 또 큰따옴표 문자열 안의 백틱은 이스케이프라 `` `22b101f6` `` 같은 마크다운 코드 표기가 사라진다. 여러 줄 앵커/본문은 작은따옴표 here-string(`@'...'@`)을 쓰고, 스크립트는 LF로 생성하며, 스크립트 안에서 `\r\n`을 정규화한다. FINDINGS.md 기록 여부는 아직 미결정.
- upload_jobs.py의 [15차->16차 전환] docstring은 의도적으로 유지(10절 최소 변경 원칙, 역사적 설명일 뿐 호출 아님).
- 되돌리려면 `git revert df7da7d5`(carrot-ryu).

다음 작업 후보:
1. 실차 배포 여부 결정, 배포 후 관찰(controlsd/플래너 예외 + 카메라 페어링 + 대시캠 업로드).
2. carrot-ms 후속 신규 커밋 발생 시 2절(폐지된 필터 없이 전체 개별 분석) 재점검.
3. 114차/110차 이월 실차 관찰 항목.
4. dead code 추가 후보 발굴이 필요하면 DEAD_CODE_REVIEW.md 원칙(심볼 단위 grep으로 참조 0건 확정, 배치마다 사용자 승인)대로 새 배치 -- 단, 채팅에 붙여넣어진 과거 분석은 그 자체로 검증된 것으로 취급하지 말고 이번 세션처럼 재확인부터 시작한다.