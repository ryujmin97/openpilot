Worker: Claude (128차, Claude Sonnet 5)
Date: 2026-09-22
Repository: ryujmin97/openpilot
Code Branch: carrot-ryu (base `b3ac7c95fcf9db39800ec8e873e73e7def37a177`, 127차 test_latcontrol.py 수정/삭제, push 확인 완료. 이번 세션은 코드 변경 없음)
Note Branch: carrot-ryu-note (이 스크립트 반영 전 base `ff34025bee37cceabada4af716b4c7e93d8838b1`, 127차 push 확인 완료. 반영 후 HEAD는 다음 세션이 git ls-remote로 확인)
carrot-ms 마지막 검토/동기화 체크포인트: `3756e6d5`(128차, 이번 세션에서 갱신 -- 직전 체크포인트는 `4bb4b510`, 116차)

작업:
1. HANDOFF.md 127차 미완료 2번(carrot-ms 신규 커밋 확인, 2절)을 착수. WIP_SYNC.md 재확인 결과 실제로는 116차에 이미 e324f67보다 훨씬 뒤(4bb4b510)까지 진행돼 있었음을 파악(127차 HANDOFF.md 표기만 뒤처져 있었을 뿐).
2. `git ls-remote`로 carrot-ms(happymaj11r/openpilot) 현재 HEAD가 `3756e6d5`임을 확인, `4bb4b510`과 `git merge-base --is-ancestor`로 비조상관계(rebase 발생)를 확인.
3. 해시 체인 추적이 불가능해져 2절 원칙대로 커밋 메시지 기준 비교로 전환: 양쪽 HEAD에서 커밋 로그(400/410개)를 얕은 clone으로 확보해 제목 문자열 기준 `comm`으로 대조, 신규 10건 확인(OLD-only 0건으로 비교 신뢰성 확보).
4. 10건 전부 개별 diff를 직접 열어 대조(11절): CAN FD 전용 4건, 테스트/무관 브랜드 1건, VW MEB 전용 1건을 코드 근거로 제외 확정. 클러스터 기능 관련 2건은 사용자에게 사용 여부를 확인해 "미사용·계획없음"으로 제외 확정.
5. 남은 2건(`9f8619b1` 레이더 CAN 전처리 분리 리팩터, `3756e6d5` core5 배치 트라이얼) 검토 -- 사용자와 논의해 `9f8619b1`은 규모/충돌위험으로 다음 세션 후보로 이월 승인받음. `3756e6d5`는 추가로 "검토해봐" 요청을 받아 diff를 끝까지 열어본 결과, 신규 회귀테스트가 `radarcan.py`(9f8619b1이 만드는 파일, 현재 carrot-ryu에는 부재를 raw 404로 확인)를 전제로 검증한다는 구조적 종속을 발견 -- 독립 반영 불가로 판단, `9f8619b1`과 함께 다음 세션으로 이월.
6. WIP_SYNC.md(128차 체크포인트, 이어붙이기형)/WIP.md(128차, 이어붙이기형)/CURRENT_STATUS.md(128차 항목 추가, 교체형) 작성.

완료:
1. carrot-ms 신규 10건 전수 분류: 7건 제외 확정(CAN FD 전용 4 + 테스트/무관 브랜드 1 + VW 전용 1 + 클러스터 2) + 2건 후보 이월(9f8619b1, 3756e6d5).
2. 두 후보 항목 간 구조적 종속관계(3756e6d5가 9f8619b1의 radarcan.py를 전제)를 코드 대조로 확인, WIP_SYNC.md/WIP.md에 기록.
3. devnotes 3개 파일(WIP_SYNC.md/WIP.md/CURRENT_STATUS.md) 128차 항목 작성 완료.

미완료(다음 세션 최우선):
1. 이 devnotes 반영 스크립트(`128cha_devnotes_carrot_ryu_note.ps1`) 실행/push 확인 -- GitHub SHA 고정 조회로 재확인(16절).
2. `9f8619b1`(레이더 CAN 전처리 분리) 상세 반영 검토 착수 -- card.py/radar_motion/predictor.py/radar_motion/controller.py/radard_dpath.py가 carrot-ryu 기존 커스텀과 충돌하는지 파일별 diff 대조부터.
3. 2번 결론에 따라 `3756e6d5`(core5 배치 트라이얼) 반영 여부 재논의 -- 9f8619b1을 반영하지 않으면 자동 보류, 반영해도 DH2015+C3 재현 근거가 없다는 점을 다시 확인 필요.
4. 110차 GATE_M 0.8/1.0, 114차 MAP_TURN_GUIDE_FACTOR 1.00 -- 둘 다 실차 미검증(127차부터 이월).
5. CURRENT_STATUS.md 97~114차 구간 상세 catch-up -- 여러 세션째 이월 중(122차부터).

검증: carrot-ms 신규 10건 전부 GitHub에서 diff를 직접 열어 대조(11절: 추측 아님). `git merge-base --is-ancestor`로 rebase 실증, `git hash-object`+raw HTTP 404 조회로 `radarcan.py` 부재 실증. 코드 변경 없음(순수 분석/기록 세션, 9절 코드 검증 절차 해당 없음). 실차 검증: 해당 없음(12절 무관, 반영된 코드 없음).

주의사항:
- 이번 세션은 코드 변경이 전혀 없다(carrot-ryu HEAD 불변). devnotes(carrot-ryu-note)만 갱신.
- `9f8619b1`/`3756e6d5` 두 항목은 서로 독립적으로 판단할 수 없다 -- 다음 세션은 반드시 9f8619b1부터 먼저 결론 내고 그 결과에 따라 3756e6d5를 재논의할 것.
- carrot-ms는 이번에도 rebase가 실제로 발생했다(0절 경고 재확인) -- 다음 세션에서도 해시 체인이 아니라 커밋 메시지 기준 비교를 유지할 것.

다음 작업 후보:
1. `9f8619b1` 레이더 CAN 전처리 분리 -- carrot-ryu 커스텀과의 충돌 상세 대조부터 착수(최우선 권장).
2. `3756e6d5` core5 배치 트라이얼 재논의(1번 결과에 종속).
3. 110차/114차 실차 관찰 항목.
4. CURRENT_STATUS.md 97~114차 구간 catch-up.
