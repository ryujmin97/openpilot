Worker: Claude (101차, Claude Sonnet 5)
Date: 2026-09-20
Repository: ryujmin97/openpilot
Code Branch: carrot-ryu (base: `f78e51e0bfe01e14ce70cc7eafc3323c5981a8a7`, 100차 테스트 하네스 수정까지 push 완료를 이번 세션에서 git 직접 조회로 확인. 이번 세션은 코드 변경 없음)
Note Branch: carrot-ryu-note (base: `b10177ba7df7e2eabcaaa97a9f65826527a89129`, 이번 101차 devnotes 반영은 실행/push 대기 -- 반영 후 HEAD는 다음 세션이 git ls-remote로 확인)
carrot-ms 마지막 검토/동기화 체크포인트: `e324f6735d3606800045ed6b28f41e79b17e5498`(변경 없음, 이번 세션 git ls-remote로 재확인) -- 93차와 동일.

작업:
분석 전용 세션(코드/지침 변경 없음). 100차 이월 항목 중 (3) 거리 -10/-20 m 스트레스 재검증(반영본 상수 기준)과 (4) 주행 전체 게이트 노출 통계 + leadTwo 확인을 업로드된 실차 로그(9/18, carrot-ryu-v1 `9ccf1206`, 9개 세그먼트)로 수행했다. 같은 분석을 시작했던 이전 대화가 devnotes 반영 전에 끊겨 있어, 채팅에 붙여넣어진 사본을 근거로 쓰지 않고 로그로 재현한 뒤 기록했다.

완료:
1. 세션 시작 확인(4절 0단계): carrot-ryu-note `b10177b`, carrot-ryu `f78e51e`, carrot-ms `e324f67`. 지침 문서(v2)는 SHA 고정본과 브랜치 URL 사본이 동일. 100차 HANDOFF의 "push 대기" 표기는 이미 오래된 정보였음을 blobless clone(`git log`/`git diff`)으로 확인 -- carrot-ryu `f87083e`..`f78e51e`는 테스트 2개(+5/-1)뿐이며 100차 설계와 일치, carrot-ryu-note는 `044a1d1`..`b10177b`에서 HANDOFF.md/WIP.md만 변경. (GitHub API는 rate limit으로 사용 못 함.)
2. toolkit/lead_decel(SHA 고정본)로 26개 이벤트 재추출(97~98차와 동일), 게이트 상수·식을 `f78e51e` long_mpc.py에서 직접 대조(H 1.5~2.2 s, TTC 6~12 s, 하강 시정수 1 s, 약화 목표 tau 1.5, 적용 대상은 `aLeadTau`뿐).
3. 스트레스 재검증(#5/#8/#22 x 0/-10/-20 m, 현행 vs B=G2T): 98차 수치와 일치. #5/#8은 -20 m에서 g가 1에 도달해 현행과 동일(설계대로), #22는 -20 m에서도 -2.58 → -2.11. 표는 WIP.md 101차 참고.
4. 전체 주행 게이트 노출: leadOne 유효 10,770개, h 중앙값 2.24 s(`GATE_H_HI` 2.2 s와 겹침), g<1 98.1%, g 평균 0.135. 다만 g<1 비율은 사실상 "h≥1.5 s인 비율"(h<1.5 s가 1.9%)과 같아 "상시 개입"의 근거가 아니다. 투사 리드 속도가 실제로 달라지는 표본은 |dV|>0.5 m/s가 5.9%이고, 그중 약 75%가 리드 감속 순간, 약 21%가 리드 가속 순간이다(감속 리드 표본의 88.3%가 g<0.5). 이 해석 정정은 WIP.md 101차에 있다.
5. leadTwo: 9개 세그먼트 전체에서 활성 0건 -- 게이트 동작 검증 불가, 여전히 미확인.
6. 100차 WIP의 "g 평균이 낮아 게이트가 대부분 열려 있었다" 문장은 용어가 뒤섞인 표현임을 101차 WIP에서 정정(g=1이 현행 동작, g<1이 투사 약화).

미완료(다음 세션 최우선):
1. 사용자가 `101cha_devnotes_carrot_ryu_note.ps1` 실행 → push. 다음 세션은 `git ls-remote`로 carrot-ryu-note HEAD 변경 확인 → WIP.md 최상단이 101차이고 HANDOFF.md가 이 문서와 일치하는지 SHA 고정 raw로 재확인(16절).
2. 임계값(`GATE_H_HI` 2.2 s 등) 재검토 여부 판단. 이번 회차 사용자 결정은 "기록만 하고 다음 세션 판단으로 이월"이며, 조정안 설계와 다른 드라이브 로그(정체·급감속) 추가 검증은 아직 하지 않았다.
3. leadTwo 게이트 동작을 검증할 수 있는 로그(리드 2대가 동시에 잡히는 구간) 확보.
4. `gate_replay.py`(100차)와 `full_gate_stats.py`(101차)를 `devnotes/toolkit/lead_decel/`에 정식 등록할지 사용자 확인(14절). 현재는 샌드박스에만 있어 세션이 끊기면 사라진다.
5. 실차 배포 후 swaglog에서 `lead_gate` 태그 관찰(99차부터 이월) -- 특히 tFollow 짧은 구간에서 g가 평상시에도 자주 내려가는지.
6. carrot-ms 4건, 화면녹화 탭 사진 업로드 UI(항목 22·23·26)/Drive 파이프라인(5~10·12·17·18·20·21)/녹화 버튼 깜빡임(28) 실차 검증 이월(97~100차와 동일, 계속 이월 중).

검증: 정적 분석/오프라인 시뮬레이션(로그 재생 통계 + casadi/IPOPT 복제본 폐루프)이며 실차 검증: 미실시. 복제본은 acados 실물이 아니라 강한 감속을 과소 재현하는 기존 한계(97~98차)가 동일하게 적용된다. 로그는 패치 이전 코드(v1)로 기록된 단일 고속도로 드라이브(약 18분)라, 패치된 코드로 주행할 때의 headway 분포와 다를 수 있다.

주의사항:
- HANDOFF.md의 "push 대기" 표기를 실제 상태와 대조 없이 그대로 믿지 않는다(16절) -- 100차 표기가 이번에도 오래된 정보였다.
- g<1 비율만으로 게이트 개입 정도를 판단하지 않는다. 게이트는 `aLeadTau`만 바꾸므로 `aLeadK≈0` 구간에서는 g가 낮아도 투사가 변하지 않는다. 판단에는 투사 리드 속도 변화량(WIP.md 101차)을 함께 본다.
- `process_lead()` 시그니처나 `long_mpc.py` 모듈 상수를 또 바꾸면 `test_cutout_mpc_integration.py`/`test_longitudinal_gap_recovery.py` 하네스(ast exec 방식)가 다시 깨질 수 있다(100차). 반영 스크립트 작성 시 두 파일도 함께 점검한다.
- 이 회차의 devnotes는 채팅 사본이 아니라 GitHub 최신 상태(SHA 고정)와 업로드 로그 재계산을 근거로 작성했다.

다음 작업 후보:
1. 101cha devnotes 스크립트 실행 확인 → push 재확인.
2. 임계값 재검토 논의(정속 headway와 `GATE_H_HI`의 겹침) 또는 다른 드라이브 로그로 추가 검증.
3. 실차 배포 후 lead_gate 로그 관찰, 필요시 임계값/tFollow 연동 재설계(99차부터 이월).
4. carrot-ms 4건 + Drive/화면녹화 관련 이월 항목 실차 검증.
