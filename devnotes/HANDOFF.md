# HANDOFF

Worker: Claude (세션 10)
Date: 2026-09-13
Repository: ryujmin97/openpilot
Code Branch: carrot-ryu (base commit: 10차 RES/+ 인게이지 속도 안전장치 반영 스크립트 실행 직후 커밋)
Note Branch: carrot-ryu-note (10차 devnotes 반영, 이 커밋)
carrot-ms 마지막 검토/동기화 커밋(메시지 기준): 7차 세션과 동일, 신규 커밋 없음
(WIP_SYNC.md 참고, 이번 세션에서는 재확인하지 않음)

작업:
완료:
- 사용자 제보(출발 가속 중 +RES 인게이지 시 설정속도가 현재속도보다 낮게 잡혀
  급감속 발생) 코드 확인. selfdrive/car/cruise.py의 accelCruise 인게이지 분기에서
  _v_cruise_kph_at_brake(브레이크 재개용 저장 속도, _auto_speed_up의 도로제한속도
  동기화 로직에서도 재사용/덮어쓰기됨) 또는 미초기화 v_cruise_kph가 현재속도보다
  낮은 채로 인게이지 속도로 채택될 수 있는 경로 확인
- 최소 변경으로 인게이지 분기 끝에 안전장치(floor) 추가: 인게이지 속도가
  "현재속도 + 2km/h(ENGAGE_SPEED_MARGIN_KPH)"보다 낮으면 올림. 정상적인
  "브레이크 후 더 높은 속도로 재개" 케이스는 영향 없음
- Claude 샌드박스에서 GitHub 최신 코드(carrot-ryu 2dbe492) 기준으로 미리 패치
  적용, 문법검증(py_compile) 통과, 기존 테스트 4건 + 사용자 시나리오 1건을
  standalone 합성 스크립트로 재현하여 결과 확인 (cereal/capnp 미빌드로 pytest
  자체 실행은 불가, 9차와 동일한 한계)
- 9절 방식(Termux 스크립트, head/tail 기반 라인 삽입)으로 반영 스크립트 작성해 전달
- WIP.md에 10차 항목 기록 (이 파일)

미완료 / 다음 세션 우선순위:
1. **실주행 재검증 필요** — 이번 수정과 8~9차의 route 감속 근본수정(2dbe492) 모두
   실제 콤마 디바이스 주행으로 확인 안 됨. 다음 실주행에서 "출발 가속 중 RES 인게이지"
   상황을 재현해 급감속이 사라졌는지 확인 필요
2. `AutoRoadSpeedLimitOffset`(기본값 -1) / `SpeedFromPCM` 이 차량의 실제 설정값이
   PARAMS_REGISTRY.md에 없어 미확인 — 이번 버그의 정확한 발생 조건을 완전히
   특정하지 못했음
3. carrot-ms가 추가한 "모델 셀렉터" 코드는 아직 분석하지 않음
4. TurnSpeedControlMode=2 / EnableSpeedTF=0 / DisableDM=2 등 사용자 의도 확인
   (오래된 보류 항목, 일부는 안전 관련)

검증: 정적 분석 + 문법 검증 + 기존 테스트 로직을 재현한 합성 스크립트로만 검증.
실차 검증 미실시.

주의사항:
- 사용자가 폰(Termux)에서 작업 중. 이번 세션부터 코드 반영 스크립트는 sed 대신
  head/tail 기반 라인 삽입 방식 사용(Termux의 sed/awk 구현이 GNU sed와 다를 수
  있어 더 안전한 방식으로 변경)
- git diff는 반드시 --no-pager 또는 GIT_PAGER=cat과 함께 사용 (9차에서 확인된 이슈)

다음 작업 후보:
1. 실주행 재검증 (이번 건 + 8~9차 route 감속 수정 모두)
2. AutoRoadSpeedLimitOffset/SpeedFromPCM 실제 설정값 확인
3. (선택) carrot-ms의 model_selector 코드 분석
