Worker: Claude (108차 계속, Claude Sonnet 5)
Date: 2026-09-20
Repository: ryujmin97/openpilot
Code Branch: carrot-ryu (HEAD `67b0aa933df429245fa6aa814c0438b1ca68c23d`, 105차 margin 하이브리드 게이트 반영 상태, 108차/108차 계속 코드 변경 없음)
Note Branch: carrot-ryu-note (base: `3c24e76b2adf21b48df840b28308de31ddec8e32`, 108차 devnotes 반영을 git ls-remote/SHA 고정 조회로 확인. 이번 108차 계속 devnotes 반영은 실행/push 대기 -- 반영 후 HEAD는 다음 세션이 git ls-remote로 확인)
carrot-ms 마지막 검토/동기화 체크포인트: `e324f6735d3606800045ed6b28f41e79b17e5498`(93차 확정, 이번 세션도 2절 신규 커밋 확인 안 함 -- 계속 이월)

작업:
108차 급정거(route 00000438--9c260778c7 seg 113, 146; 105차 코드 67b0aa9로 기록)의 복제본 불일치 원인 조사. 복제본 설정을 코드/Params 기준으로 바로잡고 플래너 내부 상태를 로그에서 재구성해 재검증했다. 상세는 WIP.md 108차 계속.

완료:
1. 지침 v2/HANDOFF/ls-remote 확인(carrot-ryu 67b0aa9, carrot-ryu-note 3c24e76), 108차 devnotes 반영 확인.
2. 사실 확정: ACCEL_MIN은 67b0aa9에서 -4.0(toolkit 기본 -3.5는 낡음). params_backup.json 기준 stop_distance 7.0 m, comfortBrake 2.4(Normal), personality 3(tFollow 1.6), aChangeCost 200. 로그 accels는 CONTROL_N=17점(0~2.5 s) 재보간값.
3. 플래너 x0(v_desired_filter, a_desired)와 게이트 g를 로그에서 재구성했고 g는 swaglog와 일치.
4. open-loop 단발 재생 RMSE: seg 113 급정거 0.091, seg 146 0.035(레이더 1 cycle 지연 가정 0.019), seg 113 온화 구간 0.155. 계획 궤적은 실차처럼 -4.0에 닿는다.
5. 폐루프는 보정 후에도 실차보다 약함: seg 113 M105 -2.59/none -2.62/M0.9-1.1 -2.49/M0.8-1.0 -2.16 vs 실차 raw -4.05(accelCmd -4.00); seg 146 M105 -1.40/M0.8-1.0 -1.07 vs 실차 raw -1.92. 현행 게이트(M105)는 이 이벤트에서 억제 효과가 사실상 없다(none과 동일).
6. 직전 세션 채팅 요약 정정(WIP.md 참고): "a_min 오류/폐루프 방법론이 원인, 게이트 무관" 결론은 지지되지 않음.
7. toolkit 신규 3개(ego_extract2.py, openloop108.py, closedloop108.py) + README/CHANGELOG.

미완료(다음 세션 최우선):
1. 108차 계속 devnotes 반영 스크립트 실행 로그 확인 -> SHA 고정 조회로 재확인(16절).
2. 사용자 결정: `long_mpc.py`의 `GATE_M_LO/HI`를 0.8/1.0으로 변경할지. 보정 후에도 완화 방향(복제본 기준 seg 113 약 0.43, seg 146 약 0.33 m/s²)이며 현행 게이트가 이 이벤트에서 무효라는 근거가 추가됐으나, 복제본 폐루프가 실차보다 약해 효과 크기가 불확실하다. 변경 시 코드 반영 스크립트(9절 Replace-Block + 정적 검증), 실차 배포는 사용자 확인 후.
3. 폐루프 복제본이 약한 원인 추가 조사(선택): 램프 구간 첫 스텝 편향 0.06~0.24(복제본이 약함)와 a_change 증폭 가설 확인. acados 실물이 없으면 SQP_RTI 1회 반복 모사(반복 횟수 제한 QP) 정도가 한계. 온화 구간(seg 113 10~14 s) RMSE 0.155 원인도 미확인.
4. params_backup.json이 로그 당시 값인지 확인(다음 로그 zip과 함께 Params를 백업하면 확정 가능). 다른 route(103차 이벤트 26건 셋) 교차 확인, gap 오프셋 -10/-20 확장 재생.
5. 104차 기록 부재 확인(margin_gate_eval.py docstring이 104차를 명시하나 devnotes에 없음) 및 `margin_gate_eval.py`/`gate_replay.py`/`full_gate_stats.py`/`leadtwo_probe.py` toolkit 등록 여부.
6. CURRENT_STATUS.md에 99차 게이트 항목 없음 -- 정리 필요.
7. carrot-ms 신규 커밋 확인(2절), 화면녹화 탭/Drive 파이프라인/녹화 버튼 깜빡임 실차 검증 이월.

검증: 복제본(casadi/IPOPT, acados 아님) 재생 + 로그 대조이며, 수정 코드(M0.8/1.0)의 실차 검증: 미실시. 실차 로그 항목은 105차 코드로 주행한 기록을 읽은 것이다.

주의사항:
- 급정거 표본은 seg 113 1건이다. 앞차가 이후 재가속한 이벤트라 앞차가 계속 제동하는 경우는 결론 불가.
- 복제본 단발(open-loop) 해는 실제 상태를 주면 실차와 잘 맞지만, 폐루프 복제본은 강한 리드 감속에서 실차보다 약하다(seg 113 명령 -2.6 vs -4.0). 폐루프 복제본 수치를 실차 효과 크기로 읽지 말 것.
- 기존 toolkit(mpc_replica.py 등)의 기본값은 a_min -3.5, cb 2.47/sd 11.6이다. 새 도구(openloop108/closedloop108)만 보정값(-4.0, 2.4/7.0)을 쓴다. 기존 도구 결과를 인용할 때 이 차이를 감안할 것.
- 급제동 시 운전자 핸들 개입(steerOverride)이 있었다. 개입 의도는 로그로 확인 불가.
- 문제 시 105차 코드 커밋을 `git revert`하면 `f78e51e`(B안)로 복귀.
- raw aEgo에는 수십 ms짜리 센서 스파이크가 있다. 실제 제동 판단은 accelCmd/0.5 s 중앙값으로 한다.
- GitHub API는 rate limit에 자주 걸린다 -- `git ls-remote`/`git clone`(--depth 1)/codeload tarball 우선. 백그라운드 실행은 `setsid nohup ... < /dev/null`을 써야 호출이 끝나도 살아 있다(그냥 `&`는 종료됨).
- toolkit 재생 환경은 세션마다 초기화된다: 스키마는 로그를 기록한 커밋(105차 로그는 `67b0aa9`)의 cereal + opendbc car.capnp로 구성. 새 도구는 폴더 배치(`../toolkit`, `../schema`, `../segs`, `out/ego2.pkl`)를 가정한다.

다음 작업 후보:
1. 반영 확인 -> GATE_M_LO/HI 결정 -> 필요 시 코드 반영 스크립트.
2. 새 로그 zip을 받으면 Params 백업을 함께 받아 openloop108/closedloop108로 같은 검증 반복(표본 확대).
3. 다른 route 교차 확인 / 104차·toolkit 등록 여부 / carrot-ms 신규 커밋 확인(2절).
