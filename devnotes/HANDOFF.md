Worker: Claude (106차, Claude Sonnet 5)
Date: 2026-09-20
Repository: ryujmin97/openpilot
Code Branch: carrot-ryu (HEAD `67b0aa933df429245fa6aa814c0438b1ca68c23d`, 105차 margin 하이브리드 게이트 반영 완료, 이번 106차 코드 변경 없음)
Note Branch: carrot-ryu-note (base: `91e5956ba02bd24307061db5a07d708933ef27d8`. 106차 devnotes 반영은 실행/push 대기 -- 반영 후 HEAD는 다음 세션이 git ls-remote로 확인)
carrot-ms 마지막 검토/동기화 체크포인트: `e324f6735d3606800045ed6b28f41e79b17e5498`(93차 확정, 이번 세션도 2절 신규 커밋 확인 안 함 -- 계속 이월)

작업:
105차 코드로 주행한 실차 로그(route 00000438--9c260778c7, seg 21~25)를 확인하고, 이벤트 16건 중 6건을 base/B(98차 채택)/M105(105차 실제 게이트)로 폐루프 재생 비교했다. 상세는 WIP.md 106차.

완료:
1. 105차 코드/devnotes push 완료를 GitHub에서 재확인. lead_gate swaglog 291건에서 이상값 없음(g 평균 0.089, m 1.01~1.92).
2. 폐루프 재생(54회): M105의 base 대비 평균 완화 +0.004 m/s², B는 +0.051(idx8 +0.30, idx9 +0.08). **103차 우려(margin 계열이 idx8에서 B만큼 완화 못함)가 오늘 로그에서도 재현됨** -- 세션 앞부분 요약("의도대로 동작, 우려 재현 안 됨")은 방향을 잘못 읽은 것이라 WIP 106차에서 정정했다.
3. `gating_eval_105.py` 신규 + `merge_lead_series.py` CLI 인자 추가, toolkit README 갱신(반영 스크립트에 포함).

미완료(다음 세션 최우선):
1. 106차 devnotes 반영 스크립트 실행 로그 확인 -> SHA 고정 조회로 재확인(16절).
2. 사용자 결정: M105 게이트를 튜닝할지(WIP 106차 "튜닝 후보" a/b/c) 또는 실차 관찰을 더 할지. 튜닝 시 `gating_eval_105.py`의 M105 dict로 재생 후 코드 반영.
3. 104차 기록 부재 확인(margin_gate_eval.py docstring이 104차를 명시하나 devnotes에 없음) 및 `margin_gate_eval.py`/`gate_replay.py`/`full_gate_stats.py`/`leadtwo_probe.py` toolkit 등록 여부.
4. idx 0,1,3,4,10~15 재생(이번엔 6건만), 다른 route 로그로 교차 확인.
5. CURRENT_STATUS.md에 99차 게이트 항목 없음 -- 정리 필요.
6. carrot-ms 신규 커밋 확인(2절), 화면녹화 탭/Drive 파이프라인/녹화 버튼 깜빡임 실차 검증 이월. 실차 배포(디바이스 git pull)는 사용자 확인 후.

검증: 복제본(mpc_replica, acados 아님) 재생이며 실차 검증: 미실시. 실차 주관 평가 "앞차 반응 좋음"은 수치 검증이 아니다.

주의사항:
- 재생 창 이벤트 6건x오프셋 3이라 표본이 작다. idx8/9는 minHw 2 s 이상 비위험 이벤트여서 "안전 문제"가 아니라 "불필요한 제동 미완화" 문제다.
- 문제 시 105차 코드 커밋을 `git revert`하면 `f78e51e`(B안)로 복귀.
- GitHub API는 rate limit에 자주 걸린다 -- `git ls-remote`/`git clone`(--depth 1) 우선.
- toolkit 재생 환경은 세션마다 초기화된다: 스키마는 로그를 기록한 커밋(105차 로그는 `67b0aa9`)의 cereal + opendbc car.capnp로 구성.

다음 작업 후보:
1. 반영 확인 -> 튜닝 여부 결정 -> 필요 시 재생 -> 코드 반영.
2. 104차/toolkit 등록 여부 확인. 3. carrot-ms 신규 커밋 확인(2절).
