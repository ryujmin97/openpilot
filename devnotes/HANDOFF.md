# HANDOFF

Worker: Claude (세션 28)
Date: 2026-09-15
Repository: ryujmin97/openpilot
Code Branch: carrot-ryu (HEAD: cc73f629, 28차 반영)
Note Branch: carrot-ryu-note (이 커밋으로 28차 devnotes 반영)
carrot-ms 마지막 검토/동기화 커밋(메시지 기준): 7차 세션과 동일, 신규 커밋 없음 (28차에서도 재확인하지 않음)

작업:
사용자가 27차에서 반영한 경로안내 박스(475x495) 레이아웃에 대해 세 가지 구체적인 조정을 요청함 — (1) 박스 크기를 475x400으로 축소 (2) "도착:" 거리/시간 텍스트를 route=숫자 바로 아래(한 줄 띄고)로 이동 (3) 회전 아이콘 초록박스를 세로 중앙/가로 좌측끝맞춤으로 재배치하고 다른 글자 영역과 겹치지 않게 처리. 이번 세션에서는 실기기 스크린샷 없이 사용자가 준 텍스트 스펙만으로 좌표를 계산/조정함.

완료:
- selfdrive/ui/onroad/hud_renderer.py `_draw_turn_info_hud()` 수정(carrot-ryu, commit cc73f629):
  - box_h: 495 -> 400
  - "도착: {거리}" / eta_time_text를 `_draw_text_left_bottom`(좌측끝맞춤) 대신 `draw_text_ui_style(align="right_bottom")`로 변경, route=숫자 아래(box_y+150 / box_y+195)에 우측끝맞춤·동일 열로 배치
  - 회전 아이콘 초록박스: bx = box_x+pad+80(좌측 끝이 pad에 맞춰짐), by = box_y+190, 오프셋 -95/+115(높이 210, 기존 -90/+140·높이230에서 축소)로 박스 세로 정중앙(200)에 오도록 계산. 위쪽 제목/route 줄(~79까지)과 아래쪽 신호과속/도로명 배지(~315부터)와 겹치지 않음을 좌표 계산으로 확인
  - 회전까지 남은 거리(dist_text) 오프셋도 by+110 -> by+95로, 축소된 초록박스 크기에 맞춰 조정
- 문자열 블록 치환(Replace-Block) 2곳 모두 반영 전 정확히 1회 매치 확인. `git clone --config core.autocrlf=false` 사용(27차 규칙 적용)
- 반영 스크립트 작성 전 로컬에서 py_compile 통과 확인, Replace-Block 매칭 로직도 Python으로 사전 시뮬레이션해 old 블록이 carrot-ryu HEAD(당시 5f5e49d0) 원본과 각각 정확히 1회 매치되고 치환 결과가 로컬 검증본과 동일함을 확인 후 스크립트 전달
- 사용자가 스크립트를 실행해 push 성공(HEAD: 5f5e49d0 -> cc73f629). 이후 carrot-ryu를 다시 clone해 실제 반영된 파일을 로컬 검증본과 diff — 완전 동일(0 diff) 확인, 원격 HEAD 파일 기준 py_compile 재검증도 통과(20차 원칙)
- 변경 전/후 레이아웃 및 하단 배지(신호과속)/도로명 두 가지 표시 케이스를 SVG 목업으로 렌더링해 사용자에게 전달(실제 기기 폰트/픽셀과 다른 개략도임을 명시)

미완료 / 다음 세션 우선순위:
1. 실차 재검증(27~28차 경로안내 박스 변경분 포함, 8~28차 코드 변경 전부 이월)
2. 실기기에서 직접 디버깅: 터미널 탭으로 배포된 tools.js에 "web-gdrive-connect" 문자열이 실제로 있는지 확인, 브라우저 강제새로고침/시크릿모드로 재현 여부 확인 (26차부터 이월)
3. 화면녹화 전송 다이얼로그의 "당근서버" 라벨 하드코딩 여부 코드 조사 (26차 발견, 미착수)
4. test_web_upload.py를 실제로 실행(또는 최소 import/픽스처 점검)해 낡은 테스트가 몇 개나 있는지 정량 확인 -> 데드코드 3개(tmux_web_target, resolve_upload_target, upload_target_settings) + 대응 테스트 삭제/갱신 (25차부터 이월)
5. 실제 Google Cloud Console에서 OAuth 클라이언트 발급 + 콤마 기기에서 실제 Drive 연결 테스트(device flow 전체) (15차부터 이월)
6. docs/carrot_web_upload.md 갱신 (Drive 기준으로) (15차부터 이월)
7. run_upload_segments() 설계 변경 두 가지가 실사용에 문제 없는지 재확인 (16차부터 이월)
8. carrot-ms 모델 셀렉터 코드 분석 착수 (6차 이후 계속 미착수)
9. WIP.md에 28차 회차 요약 추가 필요 여부 — 이번 세션은 사용자 요청 범위가 HANDOFF.md로 한정되어 WIP.md는 갱신하지 않음(다음 세션에서 필요 시 추가)

검증: 코드 파일(hud_renderer.py)은 사용자 push 로그 확인 후 carrot-ryu HEAD(cc73f629)를 직접 clone해 로컬 검증본과 diff 0, py_compile 재검증 통과 확인함(20차 원칙). 실차 재현/디버깅은 미실시(12절 원칙, 정적 코드 변경 단계).

주의사항:
- 이번 세션은 실기기 스크린샷 없이 사용자의 텍스트 스펙(박스 크기, "route=숫자 아래 한 줄 띄고", "세로 중앙/가로 좌측끝맞춤")만으로 좌표를 계산했다. 좌표 간격(예: route= 아래 "한 줄" 간격, 초록박스 높이 210)은 합리적 근사치이며 실제 폰트 메트릭 기준으로 정밀 검증된 값은 아님 — 실차/실기기에서 시각적으로 재확인 필요.
- 26차에서 발견된 Google Drive 연결 UI 미노출/화면녹화 라벨 불일치 건은 이번 세션에서도 다루지 않았으며 그대로 이월됨.

다음 작업 후보:
1. 실기기 터미널로 배포된 tools.js 내용 확인 (26차부터 이월, 원인 규명의 핵심)
2. 화면녹화 전송 다이얼로그 라벨 하드코딩 조사
3. test_web_upload.py 실행 가능 여부 확인 -> 데드코드 3개 + 테스트 정리
4. carrot-ms 모델 셀렉터 코드 분석 착수
5. (선택) WIP.md에 28차 회차 기록 추가
