Worker: Claude (112차, Claude Sonnet 5)
Date: 2026-09-20
Repository: ryujmin97/openpilot
Code Branch: carrot-ryu (base `a430d114f17e8b9579392071f7828324cc8bb329`, 110차 GATE_M_LO/HI 0.8/1.0. 이번 세션도 코드 변경 없음)
Note Branch: carrot-ryu-note (base `c4d442615e00b0152459e4305f2c33b59a6f0582`, 112차 FINDINGS.md 반영 완료 -- SHA 고정 조회 + `git clone --depth 2`로 재검증함. 이 스크립트로 반영되는 WIP.md/HANDOFF.md 자체의 HEAD는 다음 세션이 git ls-remote로 확인)
carrot-ms 마지막 검토/동기화 체크포인트: `a23a77b1aa8b007d6b22bb19f2a1992b84d9b7d4`(111차 확정, 이번 세션 변경 없음)

작업:
사용자가 업로드한 실주행 rlog(제네시스 DH, 세그먼트 00000438--9c260778c7--155)를 바탕으로 "라우트 감속이 130km/h에서 멈췄다가 뒤늦게 급감속" 제보를 분석. capnp schema를 로그 기록 커밋(carrot-ryu `a430d114`, 110차 상태) 기준으로 구성해 parse_route.py(신규, 1회성)로 carState/carrotMan을 파싱, carrot_navi_route()의 역산 로직을 Python으로 재현해 v_ego 미반영 구조를 확인. FINDINGS.md에 112차 항목 기록·반영 완료(SHA 고정 조회 + git clone --depth 2로 재검증). 코드 변경 없음.

완료:
1. rlog 파싱/분석: t=41.2~43.9초 동안 desiredSpeed 130km/h 고정, vEgo만 계속 증가하다 t=44.2초 vturn 전환 시 급락하는 패턴을 로그로 재현.
2. 원인 확인: carrot_navi_route() 역산 시뮬레이션 결과 v_ego(100/120/145km/h)를 무엇으로 바꿔도 출력 동일 -- route 목표속도가 도로 곡률 형상 + 고정 감속상수(AutoNaviSpeedDecelRate)만으로 정해지는 구조임을 확인.
3. FINDINGS.md 112차 항목 반영: carrot-ryu-note `58e88c7` -> `c4d4426`(devnotes/FINDINGS.md 14줄 순수 추가, 다른 파일 미변경). SHA 고정 raw 조회 + `git clone --depth 2`로 커밋 메시지/부모/BOM 없음/95차 항목 보존 재확인함.
4. WIP.md 112차 항목 + 이 HANDOFF.md 반영(이 스크립트의 실행 결과는 다음 세션이 SHA 고정 조회로 재확인).

미완료(다음 세션 최우선):
1. (111차부터 이월) 실차 배포(디바이스 pull) 시점 -- 사용자 확인 후. 배포 후 swaglog lead_gate의 g/m 관찰(110차 GATE_M 0.8/1.0).
2. 라우트 감속 정체/급감속 수정 착수 여부 결정 -- FINDINGS.md 112차의 두 방향성 후보(v_ego 기준 캡핑 / route↔vturn 전환 rate limit) 중 택일. route 폴리라인 원본 곡률 배열을 확보할 수 있는 로그가 있으면 2.7초 정체가 알고리즘 구조만의 문제인지 GPS 갱신주기(약 1Hz) 요인이 섞인 것인지 추가 분리 조사.
3. 견고성 스윕 재개(94 km/h -3, 60 km/h -5, 110 km/h -5, 94 km/h -7, g0=0; 72건 중 6건만 완료, 결과 미확인)와 g0=0 결과표 -- 선택.
4. (선택, 보류) vE 기준 need-cap 재설계, TTC 변화율 후보. CURRENT_STATUS.md 99차 게이트 항목 정리, 화면녹화 탭/Drive 파이프라인 실차 검증 -- 계속 이월. CURRENT_STATUS.md는 112차도 갱신하지 않음.
5. carrot-ms 다음 신규 커밋 여부는 필요 시 가벼운 git ls-remote 점검(체크포인트는 a23a77b로 최신, 변경 없음).

검증: 정적 분석 + 실주행 로그 파싱 + carrot_navi_route() 역산 로직 Python 재현 시뮬레이션. 코드 수정 없음, 실차 검증: 미실시(이번 세션 전체).

주의사항:
- (110차 이월) GATE_M 0.8/1.0 관련 주의사항은 111차 HANDOFF.md와 동일하게 유효 -- 되돌리려면 `git revert a430d11`(105차 값 1.0/1.2로 복귀).
- 업로드된 route 로그(zip)는 13절 원칙에 따라 커밋하지 않았고 세션 종료와 함께 사라짐 -- 같은 증상을 다시 분석하려면 사용자가 로그를 재업로드해야 함.
- 이번 분석은 route 폴리라인 원본 좌표/곡률 배열 없이 carrotMan 디버그 필드(desiredSpeed/Source, route= 문자열)만으로 역추적한 결과이므로, 2.7초 정체의 GPS 갱신주기 기여분은 분리하지 못함(FINDINGS.md 112차 "한계" 참고).

다음 작업 후보:
1. 반영 확인 -> 실차 배포 후 lead_gate 로그 관찰 -> 필요 시 GATE_M 상수 조정(0.9/1.1 또는 복귀).
2. 라우트 감속 수정 방향(v_ego 캡핑 vs 전환 rate limit) 결정 후 코드 작업 착수.
3. carrot-ms 후속 신규 커밋 발생 시 2절 재점검, AGNOS 안정판 여부 확인.
4. (선택) 견고성 스윕 재개, vE 기준 need-cap 재설계 또는 TTC 변화율 후보.