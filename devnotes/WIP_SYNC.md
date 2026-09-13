# WIP SYNC

carrot-ms → carrot-ryu 동기화 이력 (carrot-ms는 매번 rebase되어 commit hash가 바뀌므로,
hash가 아닌 "커밋 메시지/내용 기준"으로 추적. 2절 참고)

## 체크포인트: 2026-09-13 (7차)

- carrot-ryu HEAD: 02015190f58a4380a433ee0130e6374455dddc2e
- carrot-ms(happymaj11r/openpilot) HEAD: 02015190f58a4380a433ee0130e6374455dddc2e
  → carrot-ryu와 완전히 동일
- 결론: 6차 세션에서 carrot-ryu를 carrot-ms HEAD로 전면 재생성한 이후,
  carrot-ms에 새로운 커밋(rebase)이 전혀 없음. 이번 점검 시점 기준 반영 대상 커밋 0건
- 참고: carrot-wip(ajouatom/openpilot) HEAD는 bb0e18bb8c09422fcd50dcf25c17e0d5c75072b1로
  6차 시점 이후에도 계속 진행 중. 그러나 carrot-ms가 아직 이를 따라 rebase하지 않았으므로,
  지침 2절 원칙대로 carrot-wip을 직접 비교/반영 대상으로 삼지 않음
  (carrot-ms가 다음에 rebase될 때 다시 검토)
- 다음 확인 시점: 사용자가 요청하거나, 시간이 좀 지난 뒤 carrot-ms HEAD가 바뀌었는지부터
  재확인 (git ls-remote로 HEAD hash만 비교하면 되므로 가벼운 점검)

## (6차 이전 이력 - 참고용)

6차 세션에서는 carrot-wip 대비 carrot-ms에만 있는 커밋 117개(모델 셀렉터 관련 약 58개,
무관한 것 약 59개)를 확인했으나, 선별 cherry-pick 대신 carrot-ryu 자체를 carrot-ms
HEAD(0201519...)로 전면 재생성하는 방식으로 처리함(당시 carrot-ryu에 사용자 코드가 없어
안전하게 가능했음). 따라서 그 시점까지의 carrot-ms 커밋은 모두 반영된 것으로 간주하며,
이 파일은 그 이후부터 발생하는 "신규 커밋"만 추적하는 목적으로 사용한다.
