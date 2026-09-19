Worker: Claude (98차, Claude Sonnet 5)
Date: 2026-09-19
Repository: ryujmin97/openpilot
Code Branch: carrot-ryu (base: `25f21d406d23bfb79ad45a67890cc39e3ad9e67b`, 변경 없음 -- 이번 세션 코드 변경 없음)
Note Branch: carrot-ryu-note (base: `4644f6df68ed5c4d843adab3d7e7c598d65924f2`, 97차 devnotes push는 git log와 변경 파일로 확인됨. 이번 devnotes 반영(WIP.md/HANDOFF.md/toolkit)은 실행/push 대기 -- 반영 후 HEAD는 다음 세션이 git ls-remote로 확인)
carrot-ms 마지막 검토/동기화 체크포인트: `e324f6735d3606800045ed6b28f41e79b17e5498`(변경 없음, 이번 세션 git ls-remote로 재확인) -- 93차와 동일.

작업:
4절 0단계로 지침 문서(v2, `4644f6d`)/HANDOFF.md/CURRENT_STATUS.md 확인 -> 사용자가 zip 재업로드 -> 97차 toolkit 재실행으로 수치 재현 -> 리드 감속 이벤트 26건에 게이팅 후보를 복제 폐루프와 초기 거리 스트레스로 평가 -> 사용자가 B안(G2T) 선택 -> devnotes 기록(코드/지침 변경 없음). devnotes 반영 직전 세션이 중단돼 스크립트 3개와 반영 스크립트가 유실되었고, 새 세션에서 같은 zip으로 환경을 복원해 다시 작성/재검증했다.

완료:
1. carrot-ryu `25f21d4`, carrot-ms `e324f67` 재확인(변경 없음). HANDOFF의 Note base 표기(97차 push 전 값)를 `4644f6d`로 정정.
2. 97차 폐루프 수치 재현(baseline -2.15, lpf1.0 -1.79, tau1.5 -1.85, noproj -1.96)과 이벤트 26건 재현.
3. 게이팅 후보 평가 결과는 WIP.md 98차. 과민 반응은 #5(32/33 t≈86)·#22(123/124 t≈54)·#8(37/38 t≈54.5)에 집중, 나머지 8건은 영향 미미, #19~21은 끼어들기로 추정되어 평가 대상 아님(#18은 끼어들기 이전의 약한 감속이라 별도 평가 안 함).
4. 결정(사용자): B안(G2T) = 투사 감쇠(aLeadTau->1.5)만 게이팅, 시간차 h_lo 1.5 s / h_hi 2.2 s, TTC t_lo 6 s / t_hi 12 s. 복제 폐루프에서 #5 -2.10->-1.92, #8 -2.75->-2.31, #22 -2.05->-1.21(최소 시간차 2.2 s대 -> 1.93~1.98 s). 초기 거리 -20 m 스트레스에서는 #8이 현행과 동일(-3.34)로 복원.
5. toolkit/lead_decel/에 events.py, needed_decel.py, gating_eval.py 등록(README/CHANGELOG 포함).

미완료(다음 세션 최우선):
1. B안의 코드 설계(10절): 현행 carrot-ryu(`25f21d4`)의 long_mpc.py를 먼저 읽고 게이트 삽입 위치와 최소 변경안을 설계 -> 사용자 승인 -> 9절 절차로 반영. 지금까지 코드 변경 없음. 설계 때 확인할 것: (a) 게이트 입력(dRel, vLead, vEgo)을 long_mpc에서 얻는 방법, (b) 현행 tFollow가 로그(v1 기록, 1.6 등)와 다른 점이 B안 결과에 주는 영향 -- 임계값이 절대 시간차(1.5~2.2 s)라 tFollow가 1.1 정도로 짧은 설정에서는 평상시 g가 중간값이 됨(123/124 t≈8~30 로그에서 시간차 약 1.7 s). 복제본에 현행 tFollow 값을 넣어 재확인할지 결정, (c) 새 Params 키를 쓰면 params_keys.h에 같은 커밋에서 등록(10절), 임계값을 Params로 노출할지는 사용자 결정, (d) 게이트 값을 로그에 남겨 실차 검증에 쓸지.
2. B안 및 carrot-ms 4건, 화면녹화 탭 사진 업로드 UI(22·23·26)/Drive 파이프라인(5~10·12·17·18·20·21)/녹화 버튼 깜빡임(28) 실차 검증 이월(97차와 동일).

검증: 분석은 정적 분석/오프라인 시뮬레이션이며 실차 검증: 미실시. MPC 복제본은 acados 실물이 아니고 강한 감속을 과소 재현한다(#8 실제 -3.70 대 복제 -2.75, 복제 baseline이 실제보다 약한 이벤트 8건, 예: #16 -0.32 대 -1.59). toolkit 스크립트 3개는 py_compile 통과, 재작성 후 재실행 수치가 WIP.md 98차 기록과 일치(WIP.md의 toolkit 등록 문단 참고). 이번 devnotes 반영 스크립트는 pwsh 7(Linux)로 실행 검증(로컬 bare 저장소 대상 전체 실행) -- Windows PowerShell 5.1 실행 검증은 아님.

주의사항:
- carrot-ryu(코드)는 이번 세션에서 전혀 건드리지 않았으며 25f21d4 그대로임.
- 분석에 쓴 로그는 carrot-ryu-v1 기록분이라 현행 코드가 기록할 tFollow/desiredDistance와 다름(WIP.md 97차). 현행 코드의 desiredDistance는 표시 전용이며 실제 레버는 솔버에 들어가는 장애물 궤적(투사)임.
- B안 평가의 한계: 결정적 사례 3건, 복제본 과소 재현, #5는 개선폭이 작음(WIP.md 98차 한계 참고).
- 분석 원본 zip(drive-download-20260919T035223Z-1-001.zip)은 Git에 없음(13절). 게이팅 재평가가 필요하면 사용자가 다시 올려야 함(코드 설계만 할 때는 불필요). 환경 재구성 절차는 toolkit/README.md.
- FINDINGS.md는 혼합 개행(상단 889줄 CRLF, 890행 이후 LF, 핵심 발견 45 참고)이므로 LF 정규화 후 전체 재작성 금지, 개행 보존 삽입만 사용. WIP.md/CURRENT_STATUS.md/HANDOFF.md는 LF, BOM 없음(WIP.md는 끝 개행 없음, CURRENT_STATUS.md/HANDOFF.md는 끝 개행 있음). 이번 세션은 FINDINGS.md/CURRENT_STATUS.md를 수정하지 않음.
- 스크립트 전달 시 9절 체크리스트 1~7번을 명령 출력과 함께 응답에 포함할 것. 앵커는 기억이 아니라 최신 SHA 원본에서 복사.
- 사용자가 "완료"만 보고하고 로그를 주지 않은 경우에도 완료로 가정하지 말고 GitHub에서 직접 재확인(16절).
- 콘솔에 스크립트를 직접 붙여넣으면 한글이 깨질 수 있으므로 .ps1 파일 저장 후 실행(95차 사고 참고, WIP.md 95차).
- 샌드박스에서 긴 계산을 백그라운드로 돌릴 때는 setsid nohup을 쓸 것(일반 nohup은 호출 종료 시 죽음). GitHub API는 rate limit에 걸릴 수 있으니 git clone/ls-remote를 우선.
- 반영 전에 세션이 끊기면 샌드박스의 미반영 산출물(스크립트 등)이 사라진다. 이번처럼 유실되면 zip으로 재구성해야 하므로, 세션이 한도에 가까우면 스크립트 작성 직후 바로 전달할 것(17절).

다음 작업 후보:
1. 세션 시작 시 carrot-ms에 `e324f67` 이후 신규 커밋이 있는지 확인(2절).
2. B안 코드 설계 -> 승인 -> 9절 절차로 반영(위 미완료 1).
3. B안 + carrot-ms 4건 실주행(이동 중) 검증, 남은 항목(22·23·26·5~10·12·17·18·20·21·28) 실차 검증.
