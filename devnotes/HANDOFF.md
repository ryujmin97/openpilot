Worker: Claude (108차, Claude Sonnet 5)
Date: 2026-09-20
Repository: ryujmin97/openpilot
Code Branch: carrot-ryu (HEAD `67b0aa933df429245fa6aa814c0438b1ca68c23d`, 105차 margin 하이브리드 게이트 반영 상태, 108차 코드 변경 없음)
Note Branch: carrot-ryu-note (base: `73a28c19f7c3e7d27e7c400f39d20647112dd5b8`, 107차 devnotes push 완료를 git ls-remote/clone으로 확인. 이번 108차 devnotes 반영은 실행/push 대기 -- 반영 후 HEAD는 다음 세션이 git ls-remote로 확인)
carrot-ms 마지막 검토/동기화 체크포인트: `e324f6735d3606800045ed6b28f41e79b17e5498`(93차 확정, 이번 세션도 2절 신규 커밋 확인 안 함 -- 계속 이월)

작업:
사용자가 올린 새 로그(route 00000438--9c260778c7 seg 113, 146; 105차 코드 67b0aa9로 기록)로 자차 급정거를 확인했다. 이전 seg 21~25와 다른 구간이라 새 표본이다. 상세는 WIP.md 108차.

완료:
1. 107차 devnotes 반영 검증: 73a28c1(부모 5b13e02), numstat/BOM/CR/py_compile 확인.
2. 급정거 실측(seg 113): aEgo 최소 -4.10(0.5 s 중앙값 -3.58), accelCmd -4.00(ACCEL_MIN, 0.67 s 유지), aTarget -4.25. 시간차 최소 1.97 s, TTC 최소 9.3 s의 비위험 상황이며 사후 필요 감속은 0.33~1.39 m/s². 앞차가 92 -> 71 km/h로 감속(aLeadK 최소 -6.98) 후 재가속. 운전자가 t=4.8~8.2 s 핸들 개입(overriding steerOverride).
3. 게이트 상태: g가 t≈4.4 s부터 1.0(완전 개방), m 1.01, aLeadTau 0.25 -> 0.03. preview는 원인 아님(aTarget - aTargetBase 약 0.08).
4. 복제본 재생: seg 113 aEmin base -2.71 / B -2.19 / M105 -2.69 / M0.9-1.1 -2.59 / M0.8-1.0 -2.22, seg 146 idx1은 -1.51 / -1.04 / -1.44 / -1.13 / -1.01. gap 오프셋 -10/-20에서는 후보 간 차이가 거의 없음.
5. 복제본이 강한 리드 감속 이벤트에서 실차보다 약함: seg 113 약 0.9~1.3, seg 146 약 0.5 m/s² 낮음. 107차의 정합성(평균 0.14)은 온화한 이벤트 16건 기준이다.

미완료(다음 세션 최우선):
1. 108차 devnotes 반영 스크립트 실행 로그 확인 -> SHA 고정 조회로 재확인(16절).
2. 사용자 결정: `long_mpc.py`의 `GATE_M_LO/HI`를 0.8/1.0으로 변경할지. 이번 로그는 완화 방향을 지지하나 복제본 기준 효과 약 0.4~0.5 m/s²로 작고, 변경해도 사후 필요값보다 크게 제동한다. 변경 시 코드 반영 스크립트(9절 Replace-Block + 정적 검증), 실차 배포는 사용자 확인 후.
3. 급정거 원인 추가 조사(결정 전 후보): 복제본이 실차 -4.0을 재현하지 못하는 이유 확인(복제본에 빠진 실제 planner 요소 규명), 필요하면 aLeadK/aLeadTau 투사가 원인인지 복제본 what-if로 확인. 아직 시작하지 않음.
4. 다른 route(103차 이벤트 26건 셋) 교차 확인, gap 오프셋 -10/-20 확장 재생(seg 21~25의 미재생 10건 포함).
5. 104차 기록 부재 확인(margin_gate_eval.py docstring이 104차를 명시하나 devnotes에 없음) 및 `margin_gate_eval.py`/`gate_replay.py`/`full_gate_stats.py`/`leadtwo_probe.py` toolkit 등록 여부.
6. CURRENT_STATUS.md에 99차 게이트 항목 없음 -- 정리 필요.
7. carrot-ms 신규 커밋 확인(2절), 화면녹화 탭/Drive 파이프라인/녹화 버튼 깜빡임 실차 검증 이월.

검증: 복제본(mpc_replica, acados 아님) 재생 + 로그 대조이며, 수정 코드(M0.8/1.0)의 실차 검증: 미실시. 실차 로그 항목은 105차 코드로 주행한 기록을 읽은 것이다.

주의사항:
- 급정거 표본은 seg 113 1건이다. 앞차가 이후 재가속한 이벤트라 앞차가 계속 제동하는 경우는 결론 불가.
- 복제본은 aLeadK -7 수준의 강한 리드 감속에서 실차 accelCmd보다 약하게 나온다(seg 113 M105 -2.69 vs 실차 -3.58/-4.00). 이 범위의 복제본 수치를 실차 효과 크기로 읽지 말 것.
- 급제동 시 운전자 핸들 개입(steerOverride)이 있었다. 개입 의도는 로그로 확인 불가.
- 문제 시 105차 코드 커밋을 `git revert`하면 `f78e51e`(B안)로 복귀.
- raw aEgo에는 수십 ms짜리 센서 스파이크가 있다. 실제 제동 판단은 accelCmd/0.5 s 중앙값으로 한다.
- GitHub API는 rate limit에 자주 걸린다 -- `git ls-remote`/`git clone`(--depth 1) 우선.
- toolkit 재생 환경은 세션마다 초기화된다: 스키마는 로그를 기록한 커밋(105차 로그는 `67b0aa9`)의 cereal + opendbc car.capnp로 구성. toolkit 스크립트는 폴더 배치(`../schema`, `../segs`)를 고정 가정한다(각 파일 docstring). 서로 떨어진 seg는 폴더를 나눠 각각 처리한다(merge_lead_series.py main=<n>-<n>).

다음 작업 후보:
1. 반영 확인 -> 복제본 불일치 원인 조사 -> GATE_M_LO/HI 결정 -> 필요 시 코드 반영 스크립트.
2. 다른 route 교차 확인 / 104차·toolkit 등록 여부 / carrot-ms 신규 커밋 확인(2절).
