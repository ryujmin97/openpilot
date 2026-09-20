Worker: Claude (102차, Claude Sonnet 5)
Date: 2026-09-20
Repository: ryujmin97/openpilot
Code Branch: carrot-ryu (base: `f78e51e0bfe01e14ce70cc7eafc3323c5981a8a7`, 100차 테스트 하네스 수정까지 push 완료. 이번 세션도 코드 변경 없음, git ls-remote로 재확인)
Note Branch: carrot-ryu-note (base: `c2d9d8dddf873679b44eaed0fe6247a1790ddd11`, 101차 devnotes push 완료를 SHA 고정 raw 바이트 대조로 확인. 이번 102차 devnotes 반영은 실행/push 대기 -- 반영 후 HEAD는 다음 세션이 git ls-remote로 확인)
carrot-ms 마지막 검토/동기화 체크포인트: `e324f6735d3606800045ed6b28f41e79b17e5498`(변경 없음, 101차에서 git ls-remote로 재확인) -- 93차와 동일.

작업:
분석 전용 세션(코드/지침 변경 없음). 101차에서 leadTwo를 "검증용 로그 확보 필요"로만 기록했으나, 사용자가 "제네시스 DH는 레이더 트랙이 안 돼서 leadTwo가 없는 것 아닌가"라고 지적했다. 이 가설을 업로드 로그(9/18, carrot-ryu-v1 `9ccf1206`)와 carrot-ryu `f78e51e` 코드로 확인했다.

완료:
1. 101차 push 확인: `b10177b`..`c2d9d8d`는 HANDOFF.md/WIP.md 2개만 변경, 지침 문서 무변경, 두 파일이 101차 페이로드와 바이트 단위로 일치.
2. 로그 집계: `liveTracks` 10,799개 중 포인트 1개 10,796건(0개 3건), `trackId`는 0(SCC11 단일 타깃)뿐. leadOne 활성 10,770개 중 `radar=True` 10,664개, leadTwo 활성 0개. `carParams`: `radarUnavailable=False`, `HYUNDAI_GENESIS`, `openpilotLongitudinalControl=True`.
3. 코드 확인(읽기 기반): hyundai `radar_interface.py`는 SCC11에서 단일 포인트(`SCC_TID=0`)를 만들고, leadTwo는 `select_dpath_lead_two`와 SCC 전용 경로에서 전방 객체 목록/코너 레이더 포인트의 독립적 지지를 요구한다. 포인트가 SCC 하나뿐이면 조건을 채울 수 없다.
4. 결론: 이 차량·현재 레이더 구성에서는 leadTwo가 구조적으로 나오지 않을 가능성이 높아, leadTwo 게이트(`lead_index=1`)의 실주행 노출은 사실상 없다고 본다. 101차의 "leadTwo 검증용 로그 확보" 항목은 우선순위를 낮춘다(101차 기록은 불변이라 102차 WIP에서 정정).

미완료(다음 세션 최우선):
1. 사용자가 `102cha_devnotes_carrot_ryu_note.ps1` 실행 → push. 다음 세션은 `git ls-remote`로 carrot-ryu-note HEAD 변경 확인 → WIP.md 최상단이 102차이고 HANDOFF.md가 이 문서와 일치하는지 SHA 고정 raw로 재확인(16절).
2. 임계값(`GATE_H_HI` 2.2 s 등) 재검토 여부 판단(101차에서 이월). 정속 headway(2.24 s)와의 겹침, 감속 리드 표본의 88.3%가 g<0.5인 점(WIP.md 101차). 사용자 결정은 아직 "기록만 하고 이월"이며, 조정안 설계나 다른 드라이브 로그(정체·급감속) 추가 검증은 하지 않았다.
3. `gate_replay.py`(100차), `full_gate_stats.py`(101차), `leadtwo_probe.py`(102차)를 `devnotes/toolkit/lead_decel/`에 정식 등록할지 사용자 확인(14절). 현재는 샌드박스에만 있어 세션이 끊기면 사라진다.
4. 실차 배포 후 swaglog에서 `lead_gate` 태그 관찰(99차부터 이월) -- 특히 tFollow 짧은 구간에서 g가 평상시에도 자주 내려가는지.
5. (낮은 우선순위) leadTwo: 이 구성에서는 구조적으로 나오지 않을 가능성이 높다. raw 레이더 트랙 등 다른 구성이 제네시스 DH에서 가능한지는 확인하지 않았다. 필요해질 때 사용자에게 확인.
6. carrot-ms 4건, 화면녹화 탭 사진 업로드 UI(항목 22·23·26)/Drive 파이프라인(5~10·12·17·18·20·21)/녹화 버튼 깜빡임(28) 실차 검증 이월(97~101차와 동일, 계속 이월 중).

검증: 정적 분석/로그 재생 통계이며 실차 검증: 미실시. 로그는 v1 코드(`9ccf1206`)로 기록됐고 읽은 코드는 `f78e51e`라서 그 사이 leadTwo 로직이 바뀌었을 수 있다. `modelV2.leadsV3`의 1번 항목 확률(평균 0.993)의 의미(두 번째 리드인지 시간대별 가설인지)는 확인하지 못해 결론에서 제외했다.

주의사항:
- HANDOFF.md의 "push 대기" 표기를 실제 상태와 대조 없이 그대로 믿지 않는다(16절).
- g<1 비율만으로 게이트 개입 정도를 판단하지 않는다(WIP.md 101차). 투사 리드 속도 변화량을 함께 본다.
- 사용자의 현장 지식(차량 특성)은 가설로 남기지 말고 로그·코드로 먼저 확인해 기록에 반영한다. 이번에 leadTwo 지적이 101차 기록에서 누락됐었다.
- `process_lead()` 시그니처나 `long_mpc.py` 모듈 상수를 또 바꾸면 `test_cutout_mpc_integration.py`/`test_longitudinal_gap_recovery.py` 하네스(ast exec 방식)가 다시 깨질 수 있다(100차). 반영 스크립트 작성 시 두 파일도 함께 점검한다.

다음 작업 후보:
1. 102cha devnotes 스크립트 실행 확인 → push 재확인.
2. 임계값 재검토 논의(정속 headway와 `GATE_H_HI`의 겹침): 조정안 설계, 또는 다른 드라이브 로그로 추가 검증.
3. toolkit 등록 여부 확인 후 등록.
4. 실차 배포 후 lead_gate 로그 관찰, 필요시 임계값/tFollow 연동 재설계(99차부터 이월).
5. carrot-ms 4건 + Drive/화면녹화 관련 이월 항목 실차 검증.
