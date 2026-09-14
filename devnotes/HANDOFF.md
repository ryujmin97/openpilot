# HANDOFF

Worker: Claude (세션 26)
Date: 2026-09-14
Repository: ryujmin97/openpilot
Code Branch: carrot-ryu (HEAD: d338afb7, 변경 없음 -- 이번 세션은 조사만 진행)
Note Branch: carrot-ryu-note (이 커밋으로 26차 devnotes 반영)
carrot-ms 마지막 검토/동기화 커밋(메시지 기준): 7차 세션과 동일, 신규 커밋 없음 (이번 세션에서도 재확인하지 않음)

작업:
사용자가 실기기(콤마 C3)에서 오늘 찍은 스크린샷 10장(2026-09-14 14:47~18:41)을 제공. "웹 설정 > 로그 업로드"에서 업로드 서버를 구글 드라이브로 선택해도 Client ID/Secret 입력란이 안 보이고 당근서버/토스서버 주소 입력란이 계속 보이는 현상, 그리고 화면녹화 전송 다이얼로그 라벨 불일치를 확인. carrot-ryu 최신(d338afb7) 프론트엔드 소스를 codeload tarball로 받아 정적 코드 리뷰를 수행했으나, 코드 로직상으로는 이 현상이 재현되지 않아야 한다는 결론에 도달(모순).

완료:
- carrot-ryu HEAD(d338afb7) 기준 web-gdrive-connect 컴포넌트의 등록/가시성(isVisible)/렌더 로직 정적 리뷰 완료 -- 코드 자체에는 문제를 찾지 못함
- web/js/generated/tools.js(esbuild 번들)가 소스와 완전히 동일한 로직을 담고 있음을 직접 대조 확인 -- 번들 재생성 누락은 이번 소스/번들 비교로는 확인되지 않음
- web/css/generated/tools.css에 .web-gdrive-settings 관련 CSS 전부 정상 포함 확인
- web-upload 컴포넌트의 당근/토스 주소 필드가 target==="carrot"/"toss"일 때만 보이도록 구현돼 있다는 것을 코드로 확인 -- 스크린샷(target=gdrive인데 두 필드가 보임)과 모순됨을 발견
- FINDINGS.md에 상세 기록(2026-09-14 26차 항목)

미완료 / 다음 세션 우선순위:
1. 실기기에서 직접 디버깅: 터미널 탭으로 배포된 tools.js에 "web-gdrive-connect" 문자열이 실제로 있는지 확인, 브라우저 강제새로고침/시크릿모드로 재현 여부 확인 (이번 세션에서 사용자가 실기기 접근 불가로 이월)
2. 화면녹화 전송 다이얼로그의 "당근서버" 라벨 하드코딩 여부 코드 조사 (신규 발견, 미착수)
3. test_web_upload.py를 실제로 실행(또는 최소 import/픽스처 점검)해 낡은 테스트가 몇 개나 있는지 정량 확인 -> 데드코드 3개(tmux_web_target, resolve_upload_target, upload_target_settings) + 대응 테스트 삭제/갱신 (25차부터 이월)
4. 실제 Google Cloud Console에서 OAuth 클라이언트 발급 + 콤마 기기에서 실제 Drive 연결 테스트(device flow 전체) (15차부터 이월, 1번 해결 후 진행 가능)
5. docs/carrot_web_upload.md 갱신 (Drive 기준으로) (15차부터 이월)
6. run_upload_segments() 설계 변경 두 가지가 실사용에 문제 없는지 재확인 (16차부터 이월)
7. 실주행 재검증 여전히 미실시 (8~25차 코드 변경 전부 이월)
8. carrot-ms 모델 셀렉터 코드 분석 착수 (6차 이후 계속 미착수)

검증: 이번 세션은 코드 변경이 없었으므로 코드 반영 검증 대상 없음. 정적 코드 리뷰는 raw tarball(codeload.github.com)로 실제 GitHub 최신 내용을 직접 조회해 수행함(5절/16절/20절 원칙). 실기기 재현/디버깅은 미실시.

주의사항:
- 이번 세션에서 발견한 "코드 리뷰 결과 vs 실기기 스크린샷"의 모순은 반드시 실기기에서 직접 확인해야 해소 가능함. 코드를 임의로 더 고치지 말고(10절 최소 변경 원칙), 먼저 실기기에서 배포된 번들 내용을 확인하는 것이 우선.
- "당근서버" 라벨 하드코딩 의심 건은 아직 코드 위치조차 특정하지 못했으므로, 다음 세션에서 그레핑부터 시작할 것.

다음 작업 후보:
1. 실기기 터미널로 배포된 tools.js 내용 확인 (원인 규명의 핵심)
2. 화면녹화 전송 다이얼로그 라벨 하드코딩 조사
3. test_web_upload.py 실행 가능 여부 확인 -> 데드코드 3개 + 테스트 정리
4. 실제 Drive 연결 테스트 (Google Cloud Console 클라이언트 발급 필요)
5. carrot-ms 모델 셀렉터 코드 분석 착수