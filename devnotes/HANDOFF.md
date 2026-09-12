# HANDOFF

Worker: Claude (세션 6)
Date: 2026-09-12
Repository: ryujmin97/openpilot (+ 외부 참고: happymaj11r/openpilot)
Code Branch: carrot-ryu (base commit: 02015190f58a4380a433ee0130e6374455dddc2e, carrot-ms HEAD와 동일)
Note Branch: carrot-ryu-note (6차 devnotes 반영)
carrot-wip 동기화: 더 이상 직접 하지 않음. carrot-ms를 통해 간접 반영 (아래 참고)

⚠⚠ 중요 — 다음 세션 시작 시 반드시 확인 ⚠⚠
- 이 세션에서 carrot-ryu의 베이스 브랜치가 carrot-wip → carrot-ms 로 전환되었습니다.
- carrot-ms는 https://github.com/happymaj11r/openpilot 의 브랜치이며, carrot-wip을 기반으로
  콤마 주행모델 선택 기능을 얹어 carrot-wip이 업데이트될 때마다 통째로 재생성(rebase)됩니다.
- 사용자님이 보관 중인 "PROJECT_INSTRUCTIONS_carrot-ryu.md" 문서의 "0. 프로젝트 목표" 중
  "베이스 브랜치: carrot-wip" 항목을 아래 문구로 교체해서 다음 세션부터 사용해주세요:

  베이스 브랜치: carrot-ms (외부 저장소 happymaj11r/openpilot의 브랜치. carrot-wip을
  기반으로 콤마 주행모델 선택 기능을 얹어, carrot-wip이 업데이트될 때마다 통째로
  재생성(rebase)됨. 직접 수정하지 않음. carrot-wip은 이 브랜치를 통해 간접적으로만
  반영됨. ⚠ 히스토리가 매번 재작성되므로 carrot-wip처럼 fast-forward 동기화가 불가능 —
  새 버전이 나올 때마다 carrot-ms와 carrot-wip의 커밋 메시지를 비교해 "모델 셀렉터 관련
  커밋"만 선별 반영 필요.

작업:
완료:
- happymaj11r/openpilot의 carrot-ms 브랜치 존재 및 성격 확인
  (git merge-base 결과 carrot-wip과 공통 조상 없음 → 매번 rebase되는 방식으로 판단)
- 전체 히스토리 비교: carrot-wip에 없고 carrot-ms에만 있는 커밋 117개 확인.
  키워드 필터링 결과 모델 셀렉터 관련 약 58개, 무관한 것(클러스터 HUD, PC 시뮬레이터,
  토스/당근 업로드 등) 약 59개로 추정
- 사용자 결정: 선별 cherry-pick 대신 carrot-ryu 베이스 자체를 carrot-ms로 전면 전환
- carrot-ryu(origin) 삭제 후 happymaj11r/carrot-ms 기준 재생성 완료, HEAD 일치 확인됨
  (02015190f58a4380a433ee0130e6374455dddc2e)
- 이 프로젝트(Claude 대화)와 carrot-ryu-note의 기존 devnotes는 삭제하지 않고 유지하기로
  결정 (carrot-wip 기반 분석 내용이 carrot-ms에도 대부분 유효하다고 판단)

미완료 / 다음 세션 우선순위:
1. carrot-ms가 추가한 "모델 셀렉터" 코드(carrot/model_selector, web(models) 등) 자체는
   아직 전혀 분석하지 않음 — 필요하면 신규 분석 대상
2. carrot-ms 동기화 원칙을 devnotes에 어떻게 반영할지 미정 (기존 WIP_SYNC.md는
   carrot-wip 전용으로 설계됨 — carrot-ms용 별도 섹션/파일이 필요할 수 있음)
3. TurnSpeedControlMode=2 / EnableSpeedTF=0 / DisableDM=2 등 사용자 의도 확인 (오래된 보류 항목)
4. 실차주행 전혀 안 함 (콤마 디바이스 실장착/실주행 로그 없음)

검증: 실차 검증 미실시. 이번 세션은 순수 브랜치 인프라 전환 작업(코드 변경 없음)

주의사항:
- carrot-ryu 브랜치를 삭제 후 재생성했습니다 (당시 사용자 코드가 전혀 없어 안전했음).
  이후로는 carrot-ryu에 실제 코드가 쌓이면 이런 삭제+재생성 방식을 다시 쓸 수 없습니다
  (force push 금지 원칙과 동일한 이유로, 데이터 손실 위험 있음).
- carrot-ms는 매번 히스토리가 재작성(rebase/force-push)되는 브랜치이므로, 앞으로
  carrot-ryu에 커스텀 커밋을 쌓은 뒤 carrot-ms를 다시 따라가려면 매번 자신의 커밋들을
  새 carrot-ms 위에 직접 rebase해야 하는 번거로움이 있을 수 있음을 사용자에게 이미 안내함.
- 기존 종방향 분석 내용(FINDINGS.md, PARAMS_REGISTRY.md)은 carrot-wip 기준 코드 분석이라
  carrot-ms에도 코드가 크게 다르지 않다면 유효하지만, 100% 확인된 것은 아님 — 필요시
  재검증 권장.

다음 작업 후보:
1. (선택) carrot-ms의 model_selector 코드 분석
2. TurnSpeedControlMode/EnableSpeedTF/DisableDM 등 사용자 의도 확인
3. 콤마 디바이스 실차주행 → route 로그 수집 → 로그분석
