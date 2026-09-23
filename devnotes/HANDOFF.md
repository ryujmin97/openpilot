Worker: Claude (151cha, Claude Sonnet 5)
Date: 2026-09-24
Repository: ryujmin97/openpilot
Code Branch: carrot-ryu (base: c0a01658f109f5fb52b98f56c4ff5e6dcde42159, 147차 코드 push 완료 상태 유지 -- 이번 세션 코드 변경 없음)
Note Branch: carrot-ryu-note (이 스크립트 반영 전 base: 150차 devnotes push 완료 상태, `2c1d7a7436fcf5fbcea1c248548199cc7230f784`)
carrot-ms 마지막 검토/동기화 체크포인트: `3756e6d5`(130차, 139차 세션 재확인 -- 신규 커밋 없음. 140~151차는 재점검 없음)

작업:
1. 세션 시작 4절 0단계로 지침 문서(v2, commit `2c1d7a7`) 조회, 150차 devnotes push(`2c1d7a7`) GitHub 직접 재조회로 확인.
2. 사용자 업로드 실차 rlog 4세그먼트(route `00000446--6455a5f5c4--70/71/92/93`)를 `route_extract.py`(113차 계속 toolkit)로 분석 -- xTurn=4(분기)/xTurn=6(톨게이트) 케이스 식별.
3. 114차 이월 항목("xTurn=6 톨게이트 케이스 로그 미확보") 해소.
4. 분기(xTurn=4) 접근 구간에서 desiredSpeed 자체가 급격히 요동치는 현상 신규 발견, 코드 대조로 114차 변경분은 원인이 아님을 확정, 근본 원인은 route_speed_raw(carrot_navi_route() 곡률 계산) 쪽으로 범위를 좁힘(미확정).

완료:
1. xTurn=6 톨게이트 케이스 로그 확보 및 1차 분석 완료(대체로 정상, 재개입 직후 짧은 flicker만 존재). WIP.md 151차 참고.
2. 분기(xTurn=4) desiredSpeed flicker 현상 발견 및 1차 원인 범위 확정(114차 무관, route_speed_raw 쪽으로 좁힘). WIP.md 151차 참고.

미완료(다음 세션 최우선 순으로):
1. **분기점 desiredSpeed flicker 원인 확정(신규, 최우선)** -- `carrot_navi_route()`(carrot_man.py)에 곡률 배열/경로 샘플 포인트 진단 로그를 추가해 다음 실차 또는 재분석으로 원인 확정 필요.
2. 147차 코드가 탑재된 디바이스의 실주행 로그 검증(148/149/150/151차 이월) -- 이번 세션 로그도 147차 코드 반영 전 상태(`8e8b0d1a`)라 여전히 해소 안 됨.
3. "선행차가 설정 차간거리(m~1.25) 근처에서 급제동" 시나리오는 로그에 없어 정량 미검증(148/149/150차 이월, 변동 없음).
4. 148차 v1 `2>&1` 재발(핵심 발견 53/55와 동일 패턴 3회째)의 FINDINGS.md 정식 등록 여부 결정(148차 이월).
5. 110차 GATE_M 관련 추가 실차 사례(변동 없음).
6. 이전 이월: diff/블록 추출 스크립트(임시, 147차 코드 반영용) toolkit 미등록.

검증:
- 로그 분석: `route_extract.py` 재사용 + carrot_serv.py/carrot_man.py 코드 대조로 114차 변경분(MAP_TURN_GUIDE_FACTOR)이 flicker 원인이 아님을 확정.
- 실차: 미실시(코드 변경 자체가 없었음, 로그도 147차 코드 반영 전 상태).

주의사항:
- 분기점 flicker의 근본 원인(route_speed_raw/carrot_navi_route() 쪽)은 코드 구조 대조로 범위만 좁힌 것이며, 실제 메커니즘(예: 경로 폴리라인 꼭짓점, GPS 위치 샘플링 흔들림)은 확정되지 않았다(11절: 추측만으로 원인 확정 금지).
- 이 devnotes 반영 스크립트(151차)의 실행/push 확인이 필요하다.

다음 작업:
1. 이 devnotes 반영 스크립트 실행/push 확인.
2. carrot_navi_route() 진단 로그 추가 여부 사용자 결정.
3. 147차 탑재 디바이스 실주행 로그가 생기면 미완료 2번 수행.
