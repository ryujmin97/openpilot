Worker: Claude (108차 계속2, Claude Sonnet 5)
Date: 2026-09-20
Repository: ryujmin97/openpilot
Code Branch: carrot-ryu (HEAD `67b0aa933df429245fa6aa814c0438b1ca68c23d`, 105차 margin 하이브리드 게이트 반영 상태, 108차/108차 계속/108차 계속2 코드 변경 없음)
Note Branch: carrot-ryu-note (base: `bb5883f2aa5ccb46bf0a447b27462c9dee011edb`, 108차 계속 devnotes 반영을 git ls-remote/SHA 고정 조회로 확인. 이번 108차 계속2 devnotes 반영은 실행/push 대기 -- 반영 후 HEAD는 다음 세션이 git ls-remote로 확인)
carrot-ms 마지막 검토/동기화 체크포인트: `e324f6735d3606800045ed6b28f41e79b17e5498`(93차 확정, 이번 세션도 2절 신규 커밋 확인 안 함 -- 계속 이월)

작업:
108차 급정거(route 00000438--9c260778c7 seg 113, 146; 105차 코드 67b0aa9로 기록) 완화책 탐색. 현행 게이트(M105)가 이 이벤트에서 무효라는 108차 계속 결과를 이어받아 대체 후보를 검증했다: tFollow 하한(TF_FLOOR)과 출력단 저크 제한(J_MAX). 상세는 WIP.md 108차 계속2.

완료:
1. 지침 v2/HANDOFF/ls-remote 확인(carrot-ryu 67b0aa9, carrot-ryu-note bb5883f), 108차 계속 devnotes 반영 확인.
2. 직전 채팅(저장소 미기록)의 후보 4개 결과를 WIP.md 108차 계속2에 옮겨 기록: TF_FLOOR 1.6 -> 0.4에서 seg 113 -2.58 -> -2.29, seg 146 -1.40 -> -1.06(완화 0.29~0.34)이지만 TF_FLOOR 1.2만으로 gap0=60 m 경계 스트레스가 충돌(minGap -0.21)로 넘어감. 1~3번 후보(상승 지연/임계값 완화/tau 하한)의 수치는 자료에 없어 미기록. 이 수치들은 이번 세션에서 재현하지 않았다.
3. 출력단 저크 제한(J_MAX 999~4) 재생: 게이트 M105에서 seg 113 -2.59/-2.65, seg 146 -1.42/-1.45로 J_MAX 6 이상은 완전 무효(복제본 최대 강화 저크가 seg 113 -4.66, seg 146 -1.70 m/s³뿐), J_MAX 4도 -2.66. 피크 감속을 깎지 못한다.
4. 초기화된 환경을 로그 커밋 67b0aa9 스키마로 재구성해 ego2.pkl 재추출(행 수가 직전과 동일).
5. toolkit `closedloop_jlim.py` 등록 + README/CHANGELOG.

미완료(다음 세션 최우선):
1. 108차 계속2 devnotes 반영 스크립트 실행 로그 확인 -> SHA 고정 조회로 재확인(16절).
2. 사용자 결정: `long_mpc.py`의 `GATE_M_LO/HI`를 0.8/1.0으로 변경할지(이월). 복제본 기준 완화 seg 113 약 0.43, seg 146 약 0.33 m/s²이며, 이번에 검증한 대체안(tFollow 하한/출력 저크)은 무효이거나 안전 여유를 크게 깎아 채택 근거가 약하다. 폐루프 복제본이 실차보다 약해 효과 크기는 불확실. 변경 시 코드 반영 스크립트(9절 Replace-Block + 정적 검증), 실차 배포는 사용자 확인 후.
3. 사용자 선택(제안 단계, 미시험): 필요 감속(TTC/차간거리) 기반 명령 상한을 새 후보로 시험할지. 사후 필요 감속 0.33~1.39 m/s²(h1.0~1.8)인데 명령이 -4.0까지 갔다는 점이 근거이며, 앞차가 계속 제동하는 경계 스트레스 테스트(gating_eval_105.py stress 계열)가 필수다.
4. 폐루프 복제본이 약한 원인 추가 조사(선택): 램프 구간 첫 스텝 편향 0.06~0.24와 a_change 증폭 가설 확인, seg 113 온화 구간(10~14 s) RMSE 0.155 원인 미확인.
5. params_backup.json이 로그 당시 값인지 확인(다음 로그 zip과 함께 Params 백업). 다른 route(103차 이벤트 26건 셋) 교차 확인, gap 오프셋 -10/-20 확장 재생.
6. 104차 기록 부재 확인(margin_gate_eval.py docstring이 104차를 명시하나 devnotes에 없음) 및 `margin_gate_eval.py`/`gate_replay.py`/`full_gate_stats.py`/`leadtwo_probe.py` toolkit 등록 여부.
7. CURRENT_STATUS.md에 99차 게이트 항목 없음 -- 정리 필요.
8. carrot-ms 신규 커밋 확인(2절), 화면녹화 탭/Drive 파이프라인/녹화 버튼 깜빡임 실차 검증 이월.

검증: 복제본(casadi/IPOPT, acados 아님) 재생 + 로그 대조이며, 수정 코드의 실차 검증: 미실시. 실차 로그 항목은 105차 코드로 주행한 기록을 읽은 것이다. 4번 후보(TF_FLOOR) 수치는 직전 채팅 출력을 옮긴 것으로 재현하지 않았다.

주의사항:
- 급정거 표본은 seg 113 1건이다. 앞차가 이후 재가속한 이벤트라 앞차가 계속 제동하는 경우는 결론 불가.
- 복제본 단발(open-loop) 해는 실제 상태를 주면 실차와 잘 맞지만, 폐루프 복제본은 강한 리드 감속에서 실차보다 약하다(seg 113 명령 -2.6 vs -4.0). 폐루프 복제본 수치를 실차 효과 크기로 읽지 말 것. 출력 저크 제한 무효 결과도 이 한계 안에서의 결과다.
- TF_FLOOR 변형 코드는 저장소/이번 세션 자료에 없다(미등록). tf가 d_comf 목표와 충돌 회피 하드 제약 두 곳에 쓰인다는 설명과 TFollowDecelBoost가 반대 방향 안전장치라는 설명은 직전 채팅 것이고 코드로 재확인하지 않았다.
- 기존 toolkit(mpc_replica.py 등)의 기본값은 a_min -3.5, cb 2.47/sd 11.6이다. 새 도구(openloop108/closedloop108/closedloop_jlim)만 보정값(-4.0, 2.4/7.0)을 쓴다. 기존 도구 결과를 인용할 때 이 차이를 감안할 것.
- 급제동 시 운전자 핸들 개입(steerOverride)이 있었다. 개입 의도는 로그로 확인 불가.
- 문제 시 105차 코드 커밋을 `git revert`하면 `f78e51e`(B안)로 복귀.
- raw aEgo에는 수십 ms짜리 센서 스파이크가 있다. 실제 제동 판단은 accelCmd/0.5 s 중앙값으로 한다.
- GitHub API는 rate limit에 자주 걸린다 -- `git ls-remote`/`git clone`(--depth 1)/codeload tarball 우선. 백그라운드 실행은 `setsid nohup ... < /dev/null`을 써야 호출이 끝나도 살아 있다(그냥 `&`는 종료됨). 복제본 재생은 CPU 1코어라 병렬로 돌려도 총시간은 같다(7 J_MAX x 2 seg 약 5분).
- toolkit 재생 환경은 세션마다 초기화된다: 스키마는 로그를 기록한 커밋(105차 로그는 `67b0aa9`)의 cereal + opendbc car.capnp로 구성. 새 도구는 폴더 배치(`../toolkit`, `../schema`, `../segs`, `out/ego2.pkl`)를 가정한다.

다음 작업 후보:
1. 반영 확인 -> GATE_M_LO/HI 결정 -> 필요 시 코드 반영 스크립트.
2. 필요 감속 기반 명령 상한 후보 시험(경계 스트레스 포함) 또는 새 로그 zip + Params 백업으로 표본 확대.
3. 다른 route 교차 확인 / 104차·toolkit 등록 여부 / carrot-ms 신규 커밋 확인(2절).
