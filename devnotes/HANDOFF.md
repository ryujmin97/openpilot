Worker: Claude (110차, Claude Sonnet 5)
Date: 2026-09-20
Repository: ryujmin97/openpilot
Code Branch: carrot-ryu (base `67b0aa933df429245fa6aa814c0438b1ca68c23d`, 105차 margin 하이브리드 게이트. 110차 코드 변경(GATE_M_LO/HI 0.8/1.0 + 게이트 단위 테스트 밴드 무관화)은 반영 스크립트 실행/push 대기 -- 반영 후 HEAD는 다음 세션이 git ls-remote로 확인)
Note Branch: carrot-ryu-note (base: `abcda6c42bfc8ba2d352fa51da730e4e17d28569`, 109차 devnotes 반영을 git ls-remote/SHA 고정 조회로 확인. 이번 110차 devnotes 반영은 실행/push 대기 -- 반영 후 HEAD는 다음 세션이 git ls-remote로 확인)
carrot-ms 마지막 검토/동기화 체크포인트: `e324f6735d3606800045ed6b28f41e79b17e5498`(93차 확정, 이번 세션도 2절 신규 커밋 확인 안 함 -- 계속 이월. 109차 채팅에 "carrot-ms에 신규 커밋 20개, 495caf5까지"라는 언급이 있었으나 GitHub API로 직접 검증한 적 없음 -- 다음 세션에서 직접 재확인 필요)

작업:
109차에서 이월된 GATE_M_LO/HI 0.8/1.0 결정을 사용자가 "반영"으로 결정해(현행 유지/0.9-1.1 절충/0.8-1.0 중 선택), 코드 반영 스크립트와 devnotes 110차 기록을 작성했다. 결정 근거로 쓴 event/stress 재구성 결과는 별도 채팅(저장소 미기록)의 도구 출력이며 이번 세션에서 재실행하지 않았다. 상세는 WIP.md 110차.

완료:
1. 지침 v2/HANDOFF/ls-remote 확인(carrot-ryu 67b0aa9, carrot-ryu-note abcda6c), 109차 devnotes 반영 확인.
2. long_mpc.py `GATE_M_LO, GATE_M_HI` 1.0/1.2 -> 0.8/1.0 반영 스크립트 작성. 기존 test_lead_gate_margin.py가 1.0/1.2를 하드코딩해 상수만 바꾸면 4개 실패하므로, 4개 테스트를 코드 상수를 읽는 밴드 무관 형태로 수정. 샌드박스 격리 실행으로 변경 전 8 passed, 상수만 변경 4 failed, 수정 후 8 passed(0.8/1.0과 1.0/1.2 양쪽), py_compile OK.
3. 재구성 결과(g 궤적, seg 113/146 이벤트, stress g0=1/0)를 WIP.md 110차에 기록.

미완료(다음 세션 최우선):
1. 코드 반영 스크립트(carrot-ryu)와 devnotes 스크립트(carrot-ryu-note) 실행 로그 확인 -> SHA 고정 조회로 재확인(16절). 특히 carrot-ryu는 push 후 long_mpc.py 70행이 0.8/1.0인지 raw(SHA고정)로 확인.
2. 실차 배포(디바이스 pull) 시점 -- 사용자 확인 후. 배포 후 swaglog lead_gate의 g/m 관찰.
3. 견고성 스윕 재개(94 km/h -3, 60 km/h -5, 110 km/h -5, 94 km/h -7, g0=0; 이전 채팅에서 72건 중 6건만 완료, 결과 미확인)와 g0=0에서 0.9/1.1·none 결과표 -- 선택.
4. carrot-ms 신규 커밋 확인(2절) -- e324f67 이후를 happymaj11r/ajouatom 비교로 직접 재확인.
5. (선택, 보류) vE 기준 need-cap 재설계, TTC 변화율 후보. 104차 기록 부재, CURRENT_STATUS.md 99차 게이트 항목 정리, 화면녹화 탭/Drive 파이프라인 실차 검증 -- 계속 이월. CURRENT_STATUS.md는 이번 세션 갱신하지 않음.

검증: 정적 분석/로그 대조/복제본(casadi/IPOPT, acados 아님) 재생 + 합성 stress이며, 수정 코드(GATE 0.8/1.0)의 실차 검증: 미실시. PowerShell 반영 스크립트는 샌드박스에 pwsh가 없어 실행하지 못했다(Replace-Block 매치/치환 결과와 테스트는 Python으로 시뮬레이션).

주의사항:
- 완화폭은 복제본 기준 seg 113 +0.43, seg 146 +0.33 m/s²로 실차 -4.0의 약 10%이며, 복제본 폐루프는 강한 리드 감속에서 실차보다 약해(seg 113 -2.6 vs -4.0) 실제 효과 크기는 불확실하다. 급제동 표본은 seg 113 1건.
- seg 146에서 0.8/1.0의 g가 거의 열리지 않는다(오픈루프 최대 0.06). 106차 계속의 "좁은 밴드는 근접 구간 무반응 경향" 우려와 같은 방향이므로, 실차에서 위험 상황 감속이 늦게 느껴지면 0.9/1.1 또는 1.0/1.2로 되돌리는 것을 먼저 검토.
- stress는 합성 시나리오(94 km/h 정속, 앞차 -5 m/s² 지속, 자차 게이트 g0=1 시작이 기본, g0=0도 별도)만 시험했다. 다른 속도/감속도 조합은 미확인. 109차 stress "baseline"은 M105+캡 없음이지 게이트 없음이 아니다(none은 gap 60에서 -6.51).
- 채팅에 붙여넣어진 외부 분석은 3절 원칙대로 항상 재검증할 것(109차에 존재하지 않는 SHA `363a715`를 언급한 리뷰 코멘트가 있었다).
- TF_FLOOR 변형 코드는 저장소에 없다(미등록). 기존 toolkit(mpc_replica.py 등)의 기본값은 a_min -3.5, cb 2.47/sd 11.6이고, 새 도구(openloop108/closedloop108/closedloop_jlim/closedloop_ncap)만 보정값(-4.0, 2.4/7.0)을 쓴다.
- 급제동 시 운전자 핸들 개입(steerOverride)이 있었으나 의도는 로그로 확인 불가. raw aEgo에는 수십 ms짜리 센서 스파이크가 있어 실제 제동 판단은 accelCmd/0.5 s 중앙값으로 한다.
- 문제 시 이번 반영 커밋을 `git revert`하면 105차 값(1.0/1.2)으로 복귀. 105차 게이트 커밋 자체를 revert하면 `f78e51e`(B안).
- GitHub API는 rate limit에 자주 걸린다 -- `git ls-remote`/`git clone`(--depth 1)/codeload tarball 우선. 백그라운드 실행은 `setsid nohup ... < /dev/null`. toolkit 재생 환경은 세션마다 초기화되며 스키마는 로그 기록 커밋(105차 로그 `67b0aa9`)의 cereal + opendbc car.capnp로 구성, 새 도구는 폴더 배치(`../toolkit`, `../schema`, `../segs`, `out/ego2.pkl`)를 가정한다.

다음 작업 후보:
1. 반영 확인 -> 실차 배포 후 lead_gate 로그 관찰 -> 필요 시 GATE_M 상수 조정(0.9/1.1 또는 복귀).
2. carrot-ms 신규 커밋 직접 재확인(2절).
3. (선택) 견고성 스윕 재개, vE 기준 need-cap 재설계 또는 TTC 변화율 후보.
