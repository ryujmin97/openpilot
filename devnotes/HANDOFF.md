Worker: Claude (109차, Claude Sonnet 5)
Date: 2026-09-20
Repository: ryujmin97/openpilot
Code Branch: carrot-ryu (HEAD `67b0aa933df429245fa6aa814c0438b1ca68c23d`, 105차 margin 하이브리드 게이트 반영 상태, 109차 코드 변경 없음)
Note Branch: carrot-ryu-note (base: `f00fe3dbac3b660f8403142ab6c92ee7cb2eb818`, 108차 계속2 devnotes 반영을 git ls-remote/SHA 고정 조회로 확인. 이번 109차 devnotes 반영은 실행/push 대기 -- 반영 후 HEAD는 다음 세션이 git ls-remote로 확인)
carrot-ms 마지막 검토/동기화 체크포인트: `e324f6735d3606800045ed6b28f41e79b17e5498`(93차 확정, 이번 세션도 2절 신규 커밋 확인 안 함 -- 계속 이월. 세션 중 채팅에 "carrot-ms에 신규 커밋 20개, 495caf5까지"라는 언급이 있었으나 이번 세션에서 GitHub API로 직접 검증하지 않아 devnotes에 반영하지 않았다 -- 다음 세션에서 직접 재확인 필요)

작업:
108차 계속2 이후 이어진(저장소 미기록) 채팅에서 시작된 필요 감속 기반 명령 상한(need-cap) 후보를 이번 세션에서 검증 완료했다. d_target=HFLOOR×vL 구조가 리드 급감속 시 캡을 역방향으로 풀어버리는 결함을 확인해 이 형태는 폐기했다. 상세는 WIP.md 109차.

완료:
1. 지침 v2/HANDOFF/ls-remote 확인(carrot-ryu 67b0aa9, carrot-ryu-note f00fe3d), 108차 계속2 devnotes 반영 확인.
2. 재업로드된 seg 113/146 로그로 환경 재구성, ego2.pkl 재추출(행 수 직전과 동일), closedloop_jlim.py/closedloop_ncap.py(NCAP=0) 베이스라인이 108차 계속2 수치와 정확히 일치함을 확인.
3. closedloop_ncap.py event 모드: hfloor 1.0~1.5/margin 0.4~0.8에서 seg113 -1.05~-1.68, seg146 -0.71~-1.21로 완화 확인(표는 WIP.md 109차).
4. closedloop_ncap.py stress 모드(합성: 94km/h 정속, 앞차 -5m/s² 지속, gap0 60/70/80): hfloor 1.2~3.0 전 구간에서 baseline(무제한 -4.0)보다 나쁨. hfloor=3.0(event 완화 0 지점)에서도 gap0=80 케이스가 baseline 생존(+2.05)에서 충돌(-0.89)로 전환.
5. 트레이스 분석으로 근본 원인 확인: d_target=HFLOOR×vL이 리드 감속 중 vL 감소를 따라 같이 줄어들어 avail이 다시 양수가 되고 cap이 풀림(위험 증가와 반대 방향 피드백).
6. event/stress 모드 bound 보정(a_min_used=min(a_min_eff,a_pl))을 stress에도 적용(채팅 지적, 코드에 반영). 재실행 결과 수치 변화 없음(원인은 아니었음).
7. toolkit closedloop_ncap.py 등록 + README/CHANGELOG.

미완료(다음 세션 최우선):
1. 109차 devnotes 반영 스크립트 실행 로그 확인 -> SHA 고정 조회로 재확인(16절).
2. 사용자 결정: long_mpc.py의 GATE_M_LO/HI를 0.8/1.0으로 변경할지(이월, 이번 세션으로 need-cap 대체안이 종결되어 다음 세션 최우선). 복제본 기준 완화 seg113 약 0.43, seg146 약 0.33 m/s².
3. carrot-ms 신규 커밋 확인(2절) — 이번 세션 채팅에서 "20개 커밋, 495caf5까지"라는 언급이 있었으나 직접 GitHub API로 검증하지 않았다. 다음 세션에서 e324f67 이후 신규 커밋을 happymaj11r/ajouatom 비교로 직접 재확인 필요.
4. (선택, 보류) d_target을 vE 기준으로 바꾼 새 안전거리 설계 — 이번 세션에서는 새 설계로 보고 시도하지 않았다. 시도하려면 그 안전거리 정의의 근거부터 세우고 event+stress 처음부터 재검증 필요.
5. (선택, 보류) TTC 변화율(dTTC/dt) 기반 보정항 — need-cap의 단순 수정판이 아니라 별도 연구 주제.
6. 104차 기록 부재 확인, CURRENT_STATUS.md 99차 게이트 항목 정리, 화면녹화 탭/Drive 파이프라인 실차 검증 — 계속 이월.

검증: 정적 분석/로그 대조/복제본(casadi/IPOPT, acados 아님) 재생 + 합성 stress이며, 수정 코드의 실차 검증: 미실시. stress는 이 세션에서 정의한 합성 시나리오다.

주의사항:
- 이번 세션 중 채팅에 등장한 리뷰 코멘트 문서 하나는 지침 문서 커밋으로 실제 존재하지 않는 SHA(`363a715`)를 언급했다. 3절 원칙에 따라 GitHub 상태로 직접 재검증하지 않은 주장은 신뢰하지 않았고, 코드로 재확인 가능한 지적(bound 충돌 가능성)만 채택해 검증했다. 다음 세션도 채팅에 붙여넣어진 외부 분석은 항상 재검증할 것.
- stress 모드는 자차/리드 정속 94km/h, 초기 gap 60/70/80 m, 앞차 -5m/s² 지속 감속이라는 하나의 시나리오만 시험했다. 다른 속도/gap/감속도 조합에서는 결론이 달라질 수 있다(미시험).
- 급정거 표본은 seg 113 1건이다. 앞차가 이후 재가속한 이벤트라 앞차가 계속 제동하는 경우는 결론 불가.
- 복제본 단발(open-loop) 해는 실제 상태를 주면 실차와 잘 맞지만, 폐루프 복제본은 강한 리드 감속에서 실차보다 약하다(seg 113 명령 -2.6 vs -4.0). 폐루프 복제본 수치를 실차 효과 크기로 읽지 말 것.
- TF_FLOOR 변형 코드는 저장소에 없다(미등록, 108차 계속2부터 이월).
- 기존 toolkit(mpc_replica.py 등)의 기본값은 a_min -3.5, cb 2.47/sd 11.6이다. 새 도구(openloop108/closedloop108/closedloop_jlim/closedloop_ncap)만 보정값(-4.0, 2.4/7.0)을 쓴다.
- 급제동 시 운전자 핸들 개입(steerOverride)이 있었다. 개입 의도는 로그로 확인 불가.
- 문제 시 105차 코드 커밋을 `git revert`하면 `f78e51e`(B안)로 복귀.
- raw aEgo에는 수십 ms짜리 센서 스파이크가 있다. 실제 제동 판단은 accelCmd/0.5 s 중앙값으로 한다.
- GitHub API는 rate limit에 자주 걸린다 -- `git ls-remote`/`git clone`(--depth 1)/codeload tarball 우선. 백그라운드 실행은 `setsid nohup ... < /dev/null`을 써야 호출이 끝나도 살아 있다.
- toolkit 재생 환경은 세션마다 초기화된다: 스키마는 로그를 기록한 커밋(105차 로그는 `67b0aa9`)의 cereal + opendbc car.capnp로 구성. 새 도구는 폴더 배치(`../toolkit`, `../schema`, `../segs`, `out/ego2.pkl`)를 가정한다.

다음 작업 후보:
1. GATE_M_LO/HI 0.8/1.0 결정 -> 필요 시 코드 반영 스크립트(9절 Replace-Block + 정적 검증, 실차 배포는 사용자 확인 후).
2. carrot-ms 신규 커밋 직접 재확인(2절).
3. (선택) vE 기준 need-cap 재설계 또는 TTC 변화율 후보를 새 세션에서 시작.
