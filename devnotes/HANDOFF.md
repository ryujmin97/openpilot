# HANDOFF

Worker: Claude (세션 7)
Date: 2026-09-13
Repository: ryujmin97/openpilot
Code Branch: carrot-ryu (base commit: 02015190f58a4380a433ee0130e6374455dddc2e, carrot-ms HEAD와 동일)
Note Branch: carrot-ryu-note (7차 devnotes 반영)
carrot-ms 마지막 검토/동기화 커밋(메시지 기준): 신규 커밋 없음 확인 (2026-09-13 점검,
WIP_SYNC.md 참고) — carrot-ryu가 이미 carrot-ms HEAD와 완전히 동일한 상태

작업:
완료:
- ryujmin97/openpilot에 남아있던 carrot-ms, carrot-wip 미러 브랜치를 사용자가 GitHub 웹
  UI로 직접 삭제 → 문서화된 브랜치 구성(carrot-ryu, carrot-ryu-note 두 개만 존재)과
  일치하는 상태로 정리됨
- carrot-ms(happymaj11r/openpilot) 신규 커밋 동기화 검토: git ls-remote로 carrot-ryu
  HEAD와 carrot-ms HEAD 비교 → 완전히 동일함 확인, 반영 대상 커밋 0건
- WIP_SYNC.md를 carrot-ms 체크포인트 방식으로 갱신
- WIP.md에 7차 회차 추가

미완료 / 다음 세션 우선순위:
1. carrot-ms가 추가한 "모델 셀렉터" 코드(carrot/model_selector, web(models) 등) 자체는
   아직 분석하지 않음
2. TurnSpeedControlMode=2 / EnableSpeedTF=0 / DisableDM=2 등 사용자 의도 확인
   (오래된 보류 항목, 일부는 안전 관련)
3. 실차주행 전혀 안 함 (콤마 디바이스 실장착/실주행 로그 없음)
4. carrot-wip(ajouatom/openpilot)이 carrot-ms보다 앞서 진행 중(HEAD bb0e18b...) —
   carrot-ms가 다음에 rebase되는 시점에 다시 동기화 검토 필요

검증: 실차 검증 미실시. 이번 세션은 순수 브랜치 정리 + 동기화 점검 작업(코드 변경 없음)

주의사항:
- carrot-ms는 현재(2026-09-13 기준) 6차 세션 때와 동일한 HEAD를 유지 중 — 아직
  rebase되지 않음. 다음에 carrot-ms HEAD가 바뀌면 그때 carrot-wip과 비교해 모델 셀렉터
  관련 커밋만 선별해야 함(2절)
- ryujmin97/openpilot에는 더 이상 carrot-ms/carrot-wip을 미러링하지 않기로 확정됨.
  필요할 때마다 외부 저장소(happymaj11r/openpilot, ajouatom/openpilot)를 git
  ls-remote / API로 직접 조회

다음 작업 후보:
1. (선택) carrot-ms의 model_selector 코드 분석
2. TurnSpeedControlMode/EnableSpeedTF/DisableDM 등 사용자 의도 확인
3. 콤마 디바이스 실차주행 → route 로그 수집 → 로그분석
