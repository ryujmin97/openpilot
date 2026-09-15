# WIP SYNC

carrot-ms → carrot-ryu 동기화 이력 (carrot-ms는 매번 rebase되어 commit hash가 바뀌므로,
hash가 아닌 "커밋 메시지/내용 기준"으로 추적. 2절 참고)

## 체크포인트: 2026-09-15 (40차)

- carrot-ryu HEAD: bdde832654a6bbf2e3e598ea7937e61a153832a8 (39cha-fix, "40차 계속2" devnotes 세션 기준 최신)
- carrot-ms(happymaj11r/openpilot) HEAD: c5f6e95b8ee1d7daaf62acbfbe920e4ee22d4c8b (2026-09-15)
- 7차 체크포인트(커밋 메시지 "Recover evil-merge resolutions from carrot-wip PR #516 and PR #517", 당시 hash 0201519...)가 현재 carrot-ms 히스토리에 그대로 남아있어, `git log 0201519..HEAD`로 구간 diff를 직접 확인함(2절: hash가 아닌 커밋 메시지 내용 기준 추적). 신규 커밋 23건 발생(rebase로 예전 hash는 무효, 이 diff는 07차 체크포인트 커밋이 아직 히스토리에 남아있어 우연히 가능했던 것으로, 다음에 또 rebase되면 이 방식도 안 통할 수 있음 -- 그때는 메시지 텍스트로 개별 대조 필요).
- 분류: 종방향 튠 다수(7건: lead acceleration/tau/gap response 관련), 파라미터 기본값 변경 2건(SpeedFromPCM, 내비 감속), 현대차 클러스터 2건, **모델 셀렉터/Cinque v2 eGPU 3건**(11번 on-the-horizon 항목과 직결 -- "Consolidate Carrot development on carrot-wip with Cinque v2", "Use Cinque v2 eGPU model from comma PR 38823", "Record Cinque v2 delivery verification and documentation scope"), 설정 리네이밍 1건("Rename lead response setting to following responsiveness" -- 우리 커스텀 UI 한국어 문자열과 충돌 가능성 있어 확인 필요), 의존성/빌드 2건(json11/Catch2, acados), 테스트/CI 2건, 네비게이션 1건("Prefer external navigation exclusively while connected"), 기타 1건(sensord update).
- 결론: 7차 이후 carrot-ryu가 자체 커스텀 코드(39~40차 등)를 계속 쌓아왔으므로, 6차 때처럼 carrot-ryu를 carrot-ms HEAD로 전면 재생성하는 방식은 이제 쓸 수 없음. 23건 중 어떤 것을 cherry-pick할지 선별 검토가 필요하나, 이번 세션에서는 체크포인트 기록까지만 하고 개별 커밋 diff 분석/cherry-pick 판단은 다음 세션으로 이월.
- 다음 확인 시점: 위 23건 중 어느 것을 반영할지 사용자와 함께 검토를 시작할 때, 또는 시간이 지나 carrot-ms HEAD가 또 바뀌었는지 가벼운 `git ls-remote` 점검할 때.

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
