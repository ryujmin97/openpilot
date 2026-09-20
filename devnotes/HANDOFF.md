Worker: Claude (113차, Claude Sonnet 5)
Date: 2026-09-20
Repository: ryujmin97/openpilot
Code Branch: carrot-ryu (base `a430d114f17e8b9579392071f7828324cc8bb329`, 110차 GATE_M_LO/HI 0.8/1.0. 113차 코드 변경은 반영 스크립트 전달만 했고 사용자 실행 전까지 GitHub에는 없음)
Note Branch: carrot-ryu-note (base `7b0372f86322ff404ab5600580c4ddb597a52dae`, 세션 시작 시점 HEAD. 이 스크립트로 반영되는 FINDINGS/WIP/HANDOFF 113차의 HEAD는 다음 세션이 git ls-remote로 확인)
carrot-ms 마지막 검토/동기화 체크포인트: `a23a77b1aa8b007d6b22bb19f2a1992b84d9b7d4`(111차 확정, 이번 세션 변경 없음)

작업:
재업로드된 실주행 rlog(세그먼트 155)와 현재 코드를 대조해 112차의 "route가 v_ego를 반영하지 않는다" 진단을 정정하고(FINDINGS.md 113차), 사용자 결정에 따라 분기(xTurnInfo 3/4)·톨게이트(6) 안내 지점 200~300m 구간에서만 route 반영비율(MapTurnSpeedFactor)을 낮추는 코드를 작성했다.

완료:
1. 원인 정정: 130km/h 정체 = 원시값 96.3 x 배율 1.35(기기 설정 135). 130->97 급락 = route가 아니라 vturn 전환. 코드는 v_ego를 이미 사용. (직전 대화의 로그 분석 결과를 옮겨 적은 것이며 이 세션에는 로그 파일이 없었음)
2. carrot_serv.py에 `map_turn_speed_factor()`와 상수 4개 추가, update_navi()의 route 배율 곱셈을 이 함수로 교체(새 Params 키 없음). 신규 테스트 test_map_turn_guide_factor.py.
3. 반영 스크립트 2개 전달: `113cha_route_guide_factor_code.ps1`(carrot-ryu), `113cha_route_guide_factor_devnotes.ps1`(carrot-ryu-note: FINDINGS 113차, WIP 113차, 이 HANDOFF).

미완료(다음 세션 최우선):
1. 두 스크립트의 실행/push 여부 확인(git ls-remote + 필요 시 SHA 고정 raw). 코드 스크립트가 아직 실행되지 않았다면 carrot-ryu는 여전히 `a430d114`.
2. 46~50s 급제동 원인 소스 규명(로그 필요: 사용자가 로그를 다시 올려야 함).
3. 실차 배포(디바이스 pull) 시점 -- 사용자 확인 후. 배포 후 분기/톨게이트 앞 감속 개시 거리와 체감 확인, 1.05/200/300 조정 여부 결정. 배포 후 swaglog lead_gate의 g/m 관찰(110차 GATE_M 0.8/1.0)도 이월.
4. (선택, 보류) 견고성 스윕 재개, vE 기준 need-cap 재설계, TTC 변화율 후보. CURRENT_STATUS.md는 113차도 갱신하지 않음.
5. carrot-ms 다음 신규 커밋 여부는 필요 시 가벼운 git ls-remote 점검.

검증: 정적 분석 + 단위 테스트 15건(샌드박스, ast 기반) + 반영 스크립트 로컬 저장소 시뮬레이션. 실차 검증: 미실시(이번 세션 전체).

주의사항:
- (110차 이월) GATE_M 0.8/1.0 관련 주의사항은 111차 HANDOFF.md와 동일하게 유효 -- 되돌리려면 `git revert a430d11`.
- 이번 변경은 안내 종류가 분기·톨게이트일 때만 작동한다. 일반 굽이/좌우회전(xTurnInfo 1/2), 로터리(5)는 기존 배율(기기 135) 그대로다.
- 근거가 분기 1건(+톨게이트 1건)이라 1.05, 200m, 300m는 초기값이다. route= 표시값은 이제 배율 적용값이며 원시값은 xTurnInfo/xDistToTurn으로 배율을 재계산해 되돌린다.
- 업로드된 route 로그(zip)는 13절 원칙에 따라 커밋하지 않았고 세션 종료와 함께 사라짐.

다음 작업 후보:
1. 반영 확인 -> 실차 배포 후 분기/톨게이트 앞 route 목표가 vEgo 아래로 내려가는 거리 관찰 -> 상수 조정.
2. 46~50s 급제동 원인 소스 규명(로그 재업로드 필요).
3. carrot-ms 후속 신규 커밋 발생 시 2절 재점검, AGNOS 안정판 여부 확인.
4. (선택) 견고성 스윕 재개, vE 기준 need-cap 재설계 또는 TTC 변화율 후보.
