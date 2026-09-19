Worker: Claude (96차, Claude Sonnet 5)
Date: 2026-09-19
Repository: ryujmin97/openpilot
Code Branch: carrot-ryu (base: `25f21d406d23bfb79ad45a67890cc39e3ad9e67b`, 변경 없음 -- 이번 세션 코드 변경 없음)
Note Branch: carrot-ryu-note (base: `913b6f17ce66517fd772af8c50b034be914d9308`, 96차 1차분(PROJECT_INSTRUCTIONS 9절 체크리스트 7번 추가, 부모 `ac45f91`) push 완료·SHA 고정 raw 재검증됨. 이번 devnotes 반영(WIP.md/CURRENT_STATUS.md/HANDOFF.md)은 실행/push 대기)
carrot-ms 마지막 검토/동기화 체크포인트: `e324f6735d3606800045ed6b28f41e79b17e5498`(변경 없음, 이번 세션 git ls-remote로 happymaj11r/openpilot 재확인) -- 93차와 동일.

작업:
4절 0단계로 지침 문서(v2, `ac45f91`)/HANDOFF.md/CURRENT_STATUS.md 확인 -> 2절 carrot-ms 신규 커밋 확인(없음) -> 19절 절차로 지침 문서 9절 체크리스트 7번(앵커 시뮬레이션) 추가 -> 반영 확인.

완료:
1. carrot-ryu `25f21d4`(변경 없음)와 carrot-ms `e324f67`(신규 커밋 없음)을 git ls-remote로 재확인.
2. 95차 HANDOFF의 note base(`5e67047`)/"push 대기" 표기와 실제 HEAD(`ac45f91`)의 시차를 클론으로 확인(16절): `ac45f91`이 이미 그 3개 파일을 반영한 커밋이었고 반영 누락은 없었음. 이번 HANDOFF에서 base를 정정.
3. PROJECT_INSTRUCTIONS_carrot-ryu.md 9절 체크리스트에 7번 추가(변경 이유->변경안->사용자 승인->`96cha_pi_checklist7_v1.ps1`). 사용자의 "완료" 보고 후 GitHub에서 직접 재확인: carrot-ryu-note `913b6f1`(부모 `ac45f91`), 변경 파일 1개 +4/-0, SHA 고정 raw가 사전 계산한 기대 결과(SHA-256 `83bf4294200da038678ce67266696eda40b20585748769f29bd080fa7ff84618`)와 바이트 동일, BOM 없음. 실행 로그는 전달되지 않았음.
4. 샌드박스에서 pwsh 7.6.6(GitHub 릴리스 tarball)을 받아 전달 스크립트를 실제 실행 검증하는 방법을 도입(상세: WIP.md 96차).

미완료(다음 세션 최우선):
1. 항목1·2 및 carrot-ms 4건(카메라 페어링/커브 탈출 지연 등 종방향 관련)의 실주행(이동 중) 검증 -- 사용자가 주행 후 결과나 로그를 주면 이어서 봄.
2. route 로그(qcamera.ts+rlog.zst, route 00000436--2edd613f1e--8): 사용자가 "실차 검증에 필요하면 쓰라고 준 것"이라고 답함(별도 분석 요청 아님). 필요해지면 그때 재업로드를 요청하며, 현재 샌드박스에 없고 openpilot cereal 스키마 파싱 환경도 없어 그 구성부터 필요함.
3. 화면녹화 탭 사진 업로드 UI(22·23·26)/Drive 파이프라인(5~10·12·17·18·20·21)/녹화 버튼 깜빡임(28) 실차 검증 이월.

검증: 지침 문서 변경은 SHA 고정 raw + `git clone --depth 3`로 재확인(변경 파일 1개, +4/-0, 바이트 동일). 전달 스크립트(`96cha_pi_checklist7_v1.ps1`)는 pwsh 7.6.6(Linux)으로 구문 파싱(오류 0), 로컬 bare 저장소 대상 전체 실행, 음성 테스트 2건(앵커 오기입/원본 SHA 불일치 -> 모두 push 없이 중단)을 거침 -- Windows PowerShell 5.1 실행 검증은 아님. 이번 devnotes 스크립트도 같은 방식으로 검증. 코드 변경 없어 py_compile 등 정적 검증은 해당 없음. 실차 검증 대상 아님(12절 무관).

주의사항:
- carrot-ryu(코드)는 이번 세션에서 전혀 건드리지 않았으며 93차 상태(25f21d4) 그대로임.
- "코드 수정 현황"의 항목별 "실차 검증: 미실시" 개별 줄은 아직 고치지 않았고(95차 신규 bullet에 결과 요약), 필요시 항목 13~19/30~36 줄에도 개별 반영 검토.
- FINDINGS.md는 혼합 개행(상단 889줄 CRLF, 890행 이후 LF, 핵심 발견 45 참고)이므로 LF 정규화 후 전체 재작성 금지, 개행 보존 삽입만 사용. WIP.md/CURRENT_STATUS.md/HANDOFF.md는 LF, BOM 없음(WIP.md는 끝 개행 없음, CURRENT_STATUS.md/HANDOFF.md는 끝 개행 있음).
- 스크립트 전달 시 9절 체크리스트 1~7번(특히 이번에 추가된 7번: 전달할 .ps1에서 앵커를 추출해 SHA 고정 원본에 시뮬레이션)을 명령 출력과 함께 응답에 포함할 것. 앵커는 기억이 아니라 최신 SHA 원본에서 복사.
- 사용자가 "완료"만 보고하고 로그를 주지 않은 경우에도 완료로 가정하지 말고 GitHub에서 직접 재확인(16절).
- 콘솔에 스크립트를 직접 붙여넣으면 한글이 깨질 수 있으므로 .ps1 파일 저장 후 실행(95차 사고 참고, WIP.md 95차).

다음 작업 후보:
1. 세션 시작 시 carrot-ms에 `e324f67` 이후 신규 커밋이 있는지 확인(2절).
2. 항목1·2 + carrot-ms 4건 실주행(이동 중) 검증.
3. 남은 항목(22·23·26·5~10·12·17·18·20·21·28) 실차 검증.
