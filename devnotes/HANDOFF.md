Worker: Claude (107차, Claude Sonnet 5)
Date: 2026-09-20
Repository: ryujmin97/openpilot
Code Branch: carrot-ryu (HEAD `67b0aa933df429245fa6aa814c0438b1ca68c23d`, 105차 margin 하이브리드 게이트 반영 상태, 107차 코드 변경 없음)
Note Branch: carrot-ryu-note (base: `5b13e02b43e6a9bc926a3f6a92ae5c80191b4272`, 106차 계속 devnotes push 완료를 git ls-remote로 확인. 이번 107차 devnotes 반영은 실행/push 대기 -- 반영 후 HEAD는 다음 세션이 git ls-remote로 확인)
carrot-ms 마지막 검토/동기화 체크포인트: `e324f6735d3606800045ed6b28f41e79b17e5498`(93차 확정, 이번 세션도 2절 신규 커밋 확인 안 함 -- 계속 이월)

작업:
106차 계속의 결정 대기 항목에 대해 사용자가 올린 로그(route 00000438--9c260778c7 seg 21~25)로 실차 로그 확인을 진행했다. 이 로그는 106차에서 분석한 것과 같은 주행분이다(이벤트 16건, lead_gate 291건 일치). 상세는 WIP.md 107차.

완료:
1. 자차 실제 급감속 확인(105차 코드 주행 기록): 0.5 s 평균 aEgo < -1.0 구간은 idx8(t=155.3~158.6 s) 1건. 최대 aEgo -1.81, accelCmd -1.68, 시간차 h 2.19~2.55 s인 비위험 상황. 게이트 g가 제동 정점에서 0.96까지 풀림(m 1.24 -> 1.01). t=98.5 s의 -1.65는 0.05 s 센서 스파이크(실제 제동 아님).
2. 복제본-실차 정합성: 16건 전부 M105 재생 vs 실차 aEgo(0.5 s 중앙값). 평균 |차이| 0.143, 최대 0.34, 평균 RMSE 0.203 m/s².
3. 미재생 10건(idx 0,1,3,4,10~15, gap 오프셋 0)을 base/B/M105/M0.9-1.1/M0.8-1.0으로 재생: 후보 간 평균 차이 작음(dAEmin B +0.026 / M105 +0.016 / M0.9-1.1 +0.022 / M0.8-1.0 +0.023). 후보 차이는 idx8/9에서 나옴.
4. toolkit 등록: ego_extract.py, ego_episodes.py, replay_ext.py, real_vs_replay.py (lead_decel/).

미완료(다음 세션 최우선):
1. 107차 devnotes 반영 스크립트 실행 로그 확인 -> SHA 고정 조회로 재확인(16절).
2. 사용자 결정: `long_mpc.py`의 `GATE_M_LO/HI`를 0.8/1.0으로 변경할지(WIP 107차 "결정 대기"). 변경 시 코드 반영 스크립트(9절 Replace-Block + 정적 검증) 작성, 실차 배포(디바이스 git pull)는 사용자 확인 후. 변경하지 않으면 실차 관찰 계속.
3. 다른 route(103차 이벤트 26건 셋) 교차 확인, gap 오프셋 -10/-20 확장 재생(미재생 10건은 오프셋 0만 함).
4. 104차 기록 부재 확인(margin_gate_eval.py docstring이 104차를 명시하나 devnotes에 없음) 및 `margin_gate_eval.py`/`gate_replay.py`/`full_gate_stats.py`/`leadtwo_probe.py` toolkit 등록 여부.
5. CURRENT_STATUS.md에 99차 게이트 항목 없음 -- 정리 필요.
6. carrot-ms 신규 커밋 확인(2절), 화면녹화 탭/Drive 파이프라인/녹화 버튼 깜빡임 실차 검증 이월.

검증: 복제본(mpc_replica, acados 아님) 재생 + 로그 대조이며, 수정 코드(M0.8/1.0)의 실차 검증: 미실시. 실차 로그 항목은 105차 코드로 주행한 기록을 읽은 것이다.

주의사항:
- 이번 로그는 106차와 같은 주행분이라 독립 표본이 늘지 않았다. 근거 사례는 idx8/9 위주이고 위험 이벤트는 없다(근접/극단 구간 반응은 결론 불가, 복제본 스트레스에서만 확인).
- idx8/9는 시간차 2 s 이상의 비위험 이벤트여서 "안전 문제"가 아니라 "불필요한 제동 미완화" 문제다.
- 문제 시 105차 코드 커밋을 `git revert`하면 `f78e51e`(B안)로 복귀.
- raw aEgo에는 수십 ms짜리 센서 스파이크가 있다(예: t=98.5 s). 실제 제동 판단은 accelCmd/이동평균으로 한다.
- GitHub API는 rate limit에 자주 걸린다 -- `git ls-remote`/`git clone`(--depth 1) 우선.
- toolkit 재생 환경은 세션마다 초기화된다: 스키마는 로그를 기록한 커밋(105차 로그는 `67b0aa9`)의 cereal + opendbc car.capnp로 구성. 새 toolkit 스크립트는 폴더 배치(`../schema`, `../segs`)를 고정 가정한다(각 파일 docstring).

다음 작업 후보:
1. 반영 확인 -> GATE_M_LO/HI 결정 -> 필요 시 코드 반영 스크립트.
2. 다른 route 교차 확인 / 104차·toolkit 등록 여부 / carrot-ms 신규 커밋 확인(2절).
