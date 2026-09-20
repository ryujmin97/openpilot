Worker: Claude (113차 계속, Claude Sonnet 5)
Date: 2026-09-20
Repository: ryujmin97/openpilot
Code Branch: carrot-ryu (base `c7b5a010c70aa67a2155ba520c3bd7cc31feea9e`, 113차 route 배율 변경 반영 확인 -- 부모 `a430d114`. 이번 계속 회차는 코드 변경 없음)
Note Branch: carrot-ryu-note (base `d6eb0fd25593c0cd78336e0607b39704fff11967`, 113차 FINDINGS/WIP/HANDOFF 반영 확인 -- 부모 `7b0372f8`. 이 스크립트로 반영되는 113차 계속의 HEAD는 다음 세션이 git ls-remote로 확인)
carrot-ms 마지막 검토/동기화 체크포인트: `a23a77b1aa8b007d6b22bb19f2a1992b84d9b7d4`(111차 확정, 이번 세션 변경 없음)

작업:
113차 반영을 SHA 고정 조회로 재확인한 뒤(carrot_serv.py/테스트가 만든 파일과 바이트 동일), 재업로드된 rlog(세그먼트 155)로 46~50초 급제동의 원인을 규명하고 새 route 배율을 같은 로그에 산술 재계산했다. route_extract.py를 toolkit에 등록했다.

완료:
1. 113차 두 스크립트(carrot-ryu `c7b5a010`, carrot-ryu-note `d6eb0fd2`) 반영 확인.
2. 46~50초 급제동 = 46.00s 운전자 브레이크(pedalPressed/userDisable, selfdriveState disabled, longActive False, accel 0). 시스템 출력이 아님(FINDINGS.md 113차 계속).
3. 새 배율(1.05, 200~300m) 산술 재계산: 목표가 vEgo 아래로 처음 내려가는 시점 약 205m(38.1s), 계속 아래에 머무는 시점 약 149m(40.06s), 41~44초 목표 약 101.1 vs vEgo 106.6~109.2, vturn 인수(44.2s)보다 각각 약 6.1초/4.1초 빠름. 플래너 응답 미검증.
4. toolkit `route_decel/route_extract.py`(extract/show/replay) 등록, README.md/CHANGELOG.md 갱신.

미완료(다음 세션 최우선):
1. 사용자가 체감한 "급감속" 구간이 46~50초(운전자 제동)인지 44.2~46초(시스템 감속)인지 확인하고, 46.00s에 브레이크를 밟은 이유를 사용자에게 확인.
2. 실차 배포(디바이스 pull) 시점 -- 사용자 확인 후. 배포 후 분기/톨게이트 앞 감속 개시 지점과 체감 확인. 약하면 MAP_TURN_GUIDE_FACTOR 1.0 검토.
3. 다른 분기·톨게이트 로그 1~2건으로 원시값 대 vturn 비교.
4. (이월) 110차 GATE_M 0.8/1.0 실차 관찰(swaglog lead_gate g/m), 견고성 스윕 재개, vE 기준 need-cap 재설계/TTC 변화율(선택, 보류). CURRENT_STATUS.md는 이번에도 갱신하지 않음.
5. carrot-ms 다음 신규 커밋 여부는 필요 시 가벼운 git ls-remote 점검.

검증: 로그 파싱 + 코드 정독(longitudinal_planner reset_state) + 산술 재계산. 코드 수정 없음, 실차 검증: 미실시(이번 세션 전체).

주의사항:
- (110차 이월) GATE_M 0.8/1.0 관련 주의사항은 111차 HANDOFF.md와 동일하게 유효 -- 되돌리려면 `git revert a430d11`.
- 113차 route 배율 변경은 안내 종류가 분기(3/4)·톨게이트(6)일 때만 작동한다. 되돌리려면 `git revert c7b5a01`(carrot-ryu) 또는 MAP_TURN_GUIDE_FACTOR를 MapTurnSpeedFactor 이상으로.
- 재계산은 설계에 쓴 같은 로그 기준(표본 밖 검증 없음)이다. 업로드된 rlog/zip은 13절에 따라 커밋하지 않았고 세션 종료와 함께 사라짐.

다음 작업 후보:
1. 체감 구간 확인 -> 실차 배포 후 분기/톨게이트 앞 관찰 -> 필요 시 상수 조정.
2. 다른 분기·톨게이트 로그 비교(route_extract.py replay 사용).
3. carrot-ms 후속 신규 커밋 발생 시 2절 재점검, AGNOS 안정판 여부 확인.
4. (선택) 견고성 스윕 재개, vE 기준 need-cap 재설계 또는 TTC 변화율 후보.
