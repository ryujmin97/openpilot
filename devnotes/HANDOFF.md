# HANDOFF

Worker: Claude (세션 27)
Date: 2026-09-15
Repository: ryujmin97/openpilot
Code Branch: carrot-ryu (HEAD: 5f5e49d0, 27차 반영)
Note Branch: carrot-ryu-note (이 커밋으로 27차 devnotes 반영)
carrot-ms 마지막 검토/동기화 커밋(메시지 기준): 7차 세션과 동일, 신규 커밋 없음 (27차에서도 재확인하지 않음)

작업:
사용자가 실기기 스크린샷(20260913_183642.jpg)을 제공하며, 우측하단 경로안내 박스를 좌측하단 디버그 박스(475x495)와 동일 크기로 키우고, "도착:" 표기 순서를 거리->시간 2줄로 바꾸고, "route=숫자" 디버그 값이 신호과속 배지와 겹치거나 사라지지 않게 해달라고 요청. 원인은 carrot_serv.py의 debugText("route=...")가 도로명(szPosRoadName)에 공백으로 이어붙어 들어오는데, 기존 hud_renderer.py가 신호과속/도로명 중 하나만 그리는 if/elif 구조였기 때문(원인 확정).

완료:
- selfdrive/ui/onroad/hud_renderer.py 수정(carrot-ryu, commit 5f5e49d0):
  - import re 추가
  - _format_eta_text() -> _format_eta_time_text()로 이름 변경, "도착:" 라벨 제거(2번째 줄 전용)
  - _split_road_name_debug() 신규 헬퍼 추가 -- 정규식으로 도로명과 route=숫자를 분리
  - _draw_turn_info_hud() 레이아웃 전면 재구성: 박스 475x495, 상단(제목+route=숫자 우측끝맞춤) / 중단(회전아이콘+거리) / 중하단(도착 2줄, 글자크기 40) / 하단(신호과속 또는 도로명 배지)
- 문자열 블록 치환(Replace-Block) 3곳 모두 반영 전 정확히 1회 매치 확인 후 진행, ast.parse 문법 검증 통과
- 반영 후 raw.githubusercontent.com으로 carrot-ryu HEAD(5f5e49d0) 재조회해 의도한 변경만 반영됐는지 직접 재확인 완료(diff 1곳, 의도한 주석 라벨 변경뿐)
- 실행 중 발생한 Windows Git core.autocrlf 관련 실패(1차 시도, import-re 블록 0회 매치) -- commit/push 이전 단계에서 안전하게 중단됐고 임시 폴더도 정상 삭제됨을 확인. git clone에 --config core.autocrlf=false 추가 + CRLF->LF 정규화 안전장치로 재작성한 스크립트로 재실행해 정상 반영(2차 시도 성공)
- 변경 후 UI 레이아웃을 설명하는 SVG 목업을 사용자에게 렌더링해 전달(실제 기기 픽셀/폰트와는 다른 개략도임을 명시)

미완료 / 다음 세션 우선순위:
1. 실차 재검증(27차 경로안내 박스 변경분 포함, 8~27차 코드 변경 전부 이월)
2. 실기기에서 직접 디버깅: 터미널 탭으로 배포된 tools.js에 "web-gdrive-connect" 문자열이 실제로 있는지 확인, 브라우저 강제새로고침/시크릿모드로 재현 여부 확인 (26차부터 이월)
3. 화면녹화 전송 다이얼로그의 "당근서버" 라벨 하드코딩 여부 코드 조사 (26차 발견, 미착수)
4. test_web_upload.py를 실제로 실행(또는 최소 import/픽스처 점검)해 낡은 테스트가 몇 개나 있는지 정량 확인 -> 데드코드 3개(tmux_web_target, resolve_upload_target, upload_target_settings) + 대응 테스트 삭제/갱신 (25차부터 이월)
5. 실제 Google Cloud Console에서 OAuth 클라이언트 발급 + 콤마 기기에서 실제 Drive 연결 테스트(device flow 전체) (15차부터 이월)
6. docs/carrot_web_upload.md 갱신 (Drive 기준으로) (15차부터 이월)
7. run_upload_segments() 설계 변경 두 가지가 실사용에 문제 없는지 재확인 (16차부터 이월)
8. carrot-ms 모델 셀렉터 코드 분석 착수 (6차 이후 계속 미착수)

검증: 코드 파일(hud_renderer.py)은 raw.githubusercontent.com으로 carrot-ryu HEAD(5f5e49d0)를 직접 재조회해 의도한 diff만 있는지 확인함(20차 원칙). ast.parse 문법 검증 통과. 실차 재현/디버깅은 미실시(12절 원칙, 정적 코드 변경 단계).

주의사항:
- 이번 세션에서 Windows Git core.autocrlf로 인한 문자열 블록 치환 실패 사례가 실제로 재현됨(1차 시도). git clone --config core.autocrlf=false 옵션 + CRLF->LF 정규화 안전장치가 이 문제를 해결했으므로, 앞으로 이 저장소 대상 PowerShell 반영 스크립트에는 기본적으로 이 옵션을 포함시킬 것(9절 갱신 필요 여부는 다음 세션에서 사용자와 논의).
- 26차에서 발견된 Google Drive 연결 UI 미노출/화면녹화 라벨 불일치 건은 이번 세션에서 다루지 않았으며 그대로 이월됨.

다음 작업 후보:
1. 이번 세션 9절에 "clone 시 --config core.autocrlf=false 기본 포함" 규칙 추가 여부 사용자와 논의 후 반영 (19절 절차)
2. 실기기 터미널로 배포된 tools.js 내용 확인 (26차부터 이월, 원인 규명의 핵심)
3. 화면녹화 전송 다이얼로그 라벨 하드코딩 조사
4. test_web_upload.py 실행 가능 여부 확인 -> 데드코드 3개 + 테스트 정리
5. carrot-ms 모델 셀렉터 코드 분석 착수