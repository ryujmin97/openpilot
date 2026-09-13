# HANDOFF

Worker: Claude (세션 8)
Date: 2026-09-13
Repository: ryujmin97/openpilot
Code Branch: carrot-ryu (base commit: 02015190f58a4380a433ee0130e6374455dddc2e, 변경 없음)
Note Branch: carrot-ryu-note (8차 devnotes 반영)
carrot-ms 마지막 검토/동기화 커밋(메시지 기준): 7차 세션과 동일, 신규 커밋 없음
(WIP_SYNC.md 참고, 이번 세션에서는 재확인하지 않음)

작업:
완료:
- 사용자가 업로드한 실주행 로그(route 000003fb--8470375f65--21: rlog.zst/qlog.zst/
  qcamera.ts)를 pycapnp + carrot-wip cereal 스키마로 직접 파싱하여 분석
- 증상(고속도로 좌커브 분기점 접근 시 route 기반 감속이 미리 과하게 걸렸다가 원복되는
  느낌)의 원인을 로그로 확인: carrot_navi_route()의 3점 곡률 계산이 분기점 부근에서
  실제보다 급한 커브로 순간 오검출 → 조기 과감속 → 재계산되며 정상 속도로 복귀
- FINDINGS.md / WIP.md / LAST_ANALYZED.md 에 상세 기록

미완료 / 다음 세션 우선순위:
1. **route 감속 오검출 대응 방향 결정 필요** (FINDINGS.md 2026-09-13 항목 참고) —
   ①TurnSpeedControlMode 1로 낮춰 route 비활성화(임시완화) vs ②carrot_navi_route()에
   스파이크 제거 필터/하락률 clamp 추가(근본수정) vs ③곡률 계산 샘플 간격 확대.
   사용자 선택 후 진행
2. carrot-ms가 추가한 "모델 셀렉터" 코드(carrot/model_selector, web(models) 등) 자체는
   아직 분석하지 않음
3. TurnSpeedControlMode=2 / EnableSpeedTF=0 / DisableDM=2 등 사용자 의도 확인
   (오래된 보류 항목, 일부는 안전 관련)
4. 콤마 디바이스 실차 장착/실주행은 아직 진행 중 아님. 단, 이번 세션에서 사용자가
   확보한 route 1건은 분석 완료
5. carrot-wip(ajouatom/openpilot)이 carrot-ms보다 앞서 진행 중(7차 시점 HEAD
   bb0e18b...) — carrot-ms가 다음에 rebase되는 시점에 다시 동기화 검토 필요

검증: 실차 검증 — 증상 자체는 실주행 로그로 확인됨. 원인 메커니즘 중 폴리라인 기하
왜곡 부분은 위성지도 등 대조까지는 하지 못해 100% 확진은 아님. 코드 수정/조치는
아직 미실시.

주의사항:
- 이번 세션은 로그 분석만 수행, carrot-ryu 코드 변경 없음 (base commit 7차와 동일)
- route 감속 오검출 대응 방향(위 미완료 1번)을 정하기 전까지는 관련 코드를 임의로
  수정하지 않음
- carrot-ms는 7차 세션 점검 시점(2026-09-13) 기준 HEAD 변동 없음. 이번 세션에서는
  재점검하지 않았으므로 다음 세션에서 다시 확인 권장

다음 작업 후보:
1. route 감속 대응 방향 결정 → 코드 수정 진행 (사용자 선택에 따라)
2. (선택) carrot-ms의 model_selector 코드 분석
3. TurnSpeedControlMode/EnableSpeedTF/DisableDM 등 사용자 의도 확인
