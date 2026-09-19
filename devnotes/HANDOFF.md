Worker: Claude (97차, Claude Sonnet 5)
Date: 2026-09-19
Repository: ryujmin97/openpilot
Code Branch: carrot-ryu (base: `25f21d406d23bfb79ad45a67890cc39e3ad9e67b`, 변경 없음 -- 이번 세션 코드 변경 없음)
Note Branch: carrot-ryu-note (base: `13b49d34dcb55f44f7c8d847d4c0224a5cd08493`, 96차 devnotes push 확인됨. 이번 devnotes 반영(WIP.md/HANDOFF.md/toolkit)은 실행/push 대기 -- 반영 후 HEAD는 다음 세션이 git ls-remote로 확인)
carrot-ms 마지막 검토/동기화 체크포인트: `e324f6735d3606800045ed6b28f41e79b17e5498`(변경 없음, 이번 세션 git ls-remote로 재확인) -- 93차와 동일.

작업:
4절 0단계로 지침 문서(v2, `13b49d3`)/HANDOFF.md/CURRENT_STATUS.md 확인 -> 사용자가 올린 rlog 9개 세그먼트+스크린샷으로 "선행차 감속에 과민 반응" 원인 분석(코드/지침 변경 없음) -> toolkit 등록.

완료:
1. carrot-ryu `25f21d4`, carrot-ms `e324f67` 재확인(변경 없음).
2. 로그가 carrot-ryu-v1(`9ccf1206`)에서 기록된 것임을 확인하고, 그 커밋의 cereal 스키마로 파싱 환경을 구성. 현행 carrot-ryu와 long_mpc.py 차이(SafeFollowState 제거, TF 리드 예외 제거, desired_distance 표시 전용화)를 정리.
3. 원인 분해: desiredDistance 공식의 리드 현재속도 즉시 반영 + aLeadTau≈0에 의한 리드 감속 장기 투사. 사건별 비중이 다름(32/33은 혼합, 123/124 t≈54는 투사 지배). 이전 대화의 "(B) 기여 미미" 정정은 근거 부족으로 재정정.
4. casadi MPC 복제본으로 폐루프 what-if(v_lead 저역통과/투사 감쇠/투사 없음). 상세 수치는 WIP.md 97차.
5. toolkit/lead_decel/ 5개 스크립트 등록(README/CHANGELOG 포함), 처음부터 재실행해 수치 재현 확인.

미완료(다음 세션 최우선):
1. 게이팅 설계·검증: 리드 감속 이벤트 26건 전체에 후보(거리 여유·TTC 기반 투사 페이드, v_lead 저역통과)를 적용해 과민 사례는 줄고 정당한 강한 감속(37/38 t≈54.5)은 유지되는지 확인. 위험거리 임계값 정의는 사용자 결정 필요.
2. 후보가 서면 현행 carrot-ryu(`25f21d4`) 기준으로 코드 설계(10절) -> 9절 절차로 반영. 지금까지는 코드 변경 없음.
3. 항목1·2 및 carrot-ms 4건, 화면녹화 탭 사진 업로드 UI(22·23·26)/Drive 파이프라인(5~10·12·17·18·20·21)/녹화 버튼 깜빡임(28) 실차 검증 이월(96차와 동일).

검증: 분석은 정적 분석/오프라인 시뮬레이션이며 실차 검증: 미실시. MPC 복제본은 acados 실물이 아니고 로그 accels 대비 RMSE 약 0.22 m/s², 강한 감속 사례는 과소 재현(-2.75 대 -3.70). toolkit 스크립트는 py_compile 통과 및 정리본 end-to-end 재실행으로 수치 재현 확인. 이번 devnotes 반영 스크립트는 pwsh 7(Linux)로 구문 파싱, 로컬 bare 저장소 대상 전체 실행, 음성 테스트로 검증 -- Windows PowerShell 5.1 실행 검증은 아님.

주의사항:
- carrot-ryu(코드)는 이번 세션에서 전혀 건드리지 않았으며 25f21d4 그대로임.
- 분석에 쓴 로그는 carrot-ryu-v1 기록분이라 현행 코드가 기록할 tFollow/desiredDistance와 다름(WIP.md 97차). 현행 코드의 desiredDistance는 표시 전용이라 그 값에 rate-limit을 거는 안은 제어에 영향이 없음.
- 분석 원본 zip(drive-download-20260919T035223Z-1-001.zip)은 Git에 없음(13절). 재개 시 사용자가 다시 올려야 함. 환경 재구성 절차는 toolkit/README.md.
- FINDINGS.md는 혼합 개행(상단 889줄 CRLF, 890행 이후 LF, 핵심 발견 45 참고)이므로 LF 정규화 후 전체 재작성 금지, 개행 보존 삽입만 사용. WIP.md/CURRENT_STATUS.md/HANDOFF.md는 LF, BOM 없음(WIP.md는 끝 개행 없음, CURRENT_STATUS.md/HANDOFF.md는 끝 개행 있음). 이번 세션은 FINDINGS.md/CURRENT_STATUS.md를 수정하지 않음.
- 스크립트 전달 시 9절 체크리스트 1~7번을 명령 출력과 함께 응답에 포함할 것. 앵커는 기억이 아니라 최신 SHA 원본에서 복사.
- 사용자가 "완료"만 보고하고 로그를 주지 않은 경우에도 완료로 가정하지 말고 GitHub에서 직접 재확인(16절).
- 콘솔에 스크립트를 직접 붙여넣으면 한글이 깨질 수 있으므로 .ps1 파일 저장 후 실행(95차 사고 참고, WIP.md 95차).

다음 작업 후보:
1. 세션 시작 시 carrot-ms에 `e324f67` 이후 신규 커밋이 있는지 확인(2절).
2. 리드 감속 게이팅 설계·이벤트 26건 검증(위 미완료 1) -- 원본 zip 재업로드 필요.
3. 항목1·2 + carrot-ms 4건 실주행(이동 중) 검증, 남은 항목(22·23·26·5~10·12·17·18·20·21·28) 실차 검증.
