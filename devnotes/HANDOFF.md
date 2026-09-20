Worker: Claude (114차, Claude Sonnet 5)
Date: 2026-09-20
Repository: ryujmin97/openpilot
Code Branch: carrot-ryu (base `c7b5a010c70aa67a2155ba520c3bd7cc31feea9e`, 113차 route 배율 변경. 114차 변경은 스크립트 실행 후 반영되며 그 HEAD는 다음 세션이 git ls-remote로 확인)
Note Branch: carrot-ryu-note (base `d75d879fd5c7dbe15d4395878cee7cdab6166795`, 113차 계속 반영 확인. 114차 devnotes의 HEAD는 다음 세션이 git ls-remote로 확인)
carrot-ms 마지막 검토/동기화 체크포인트: `a23a77b1aa8b007d6b22bb19f2a1992b84d9b7d4`(111차 확정, 이번 세션 변경 없음)

작업:
사용자 결정으로 MAP_TURN_GUIDE_FACTOR(분기·톨게이트 안내 지점 200m 이내 route 반영비율)를 1.05에서 1.00으로 바꾸는 코드 변경을 작성했다(carrot_serv.py 88행 한 줄). 코드/devnotes 스크립트 두 개를 전달했다.

완료:
1. 세션 시작 확인: 지침 v2 SHA 고정 조회(note `d75d879f`), HANDOFF.md 확인, carrot-ryu HEAD `c7b5a010` 유지 확인.
2. 113차 계속 devnotes 반영 확인(note `d75d879f`).
3. carrot_serv.py MAP_TURN_GUIDE_FACTOR 1.05 -> 1.00 코드 작성. py_compile, 단위 테스트 15건, 함수 직접 실행(250m 1.175 / 200m 이내 1.0 / 안내 종류 1은 1.35)로 확인.

미완료(다음 세션 최우선):
1. 두 스크립트(`114cha_guide_factor_1p00_code.ps1`, `114cha_guide_factor_1p00_devnotes.ps1`) 실행 결과 확인. 사용자가 push 로그를 전달하기 전까지는 GitHub 반영으로 간주하지 않는다. 다음 세션은 git ls-remote로 두 브랜치 HEAD와 carrot_serv.py 88행을 확인.
2. 체감한 급감속 구간이 46~50초(운전자 제동)인지 44.2~46초(시스템 감속)인지 확인하고, 46.00s에 브레이크를 밟은 이유를 사용자에게 확인.
3. 실차 배포(디바이스 pull) 시점 -- 사용자 확인 후. 배포 후 분기/톨게이트 앞 감속 개시 지점과 체감 확인. 너무 세면 MAP_TURN_GUIDE_FACTOR를 1.05 쪽으로 되돌리는 것을 검토.
4. 다른 분기·톨게이트 로그 1~2건으로 원시값 대 vturn 비교(toolkit `route_decel/route_extract.py replay`).
5. (이월) 110차 GATE_M 0.8/1.0 실차 관찰(swaglog lead_gate g/m), 견고성 스윕 재개, vE 기준 need-cap 재설계/TTC 변화율(선택, 보류). CURRENT_STATUS.md는 이번에도 갱신하지 않음.

검증: py_compile, 단위 테스트 15건(샌드박스; 테스트는 상수를 소스에서 읽어 값에 무관하게 통과하므로 값 변경 자체는 함수 직접 실행으로 확인), 반영 스크립트 로컬 시뮬레이션 실행. 실차 검증: 미실시(이번 세션 전체).

주의사항:
- (110차 이월) GATE_M 0.8/1.0 관련 주의사항은 111차 HANDOFF.md와 동일하게 유효 -- 되돌리려면 `git revert a430d11`.
- route 배율 변경은 안내 종류가 분기(3/4)·톨게이트(6)일 때만 작동한다. 배율 1.00은 원시값 그대로라 여유가 없다: 113차 계속 기록의 로그에서 안내 지점 205~149m 구간 원시값이 요동했으므로, 감속이 더 이르고 강해질 수 있다(예상, 미검증). 되돌리려면 `git revert <114차 코드 커밋>`(carrot-ryu) 또는 상수를 1.05로.
- 1.00으로 낮춘 근거는 113차 계속 FINDINGS에 후보로 적힌 수치(목표 약 96.3)뿐이며, 이번 세션에는 로그가 없어 재계산하지 못했다. 사용자가 이 값을 고른 이유는 별도로 언급하지 않았다.

다음 작업 후보:
1. 스크립트 반영 확인 -> 실차 배포 후 분기/톨게이트 앞 관찰 -> 필요 시 상수 조정(값은 carrot_serv.py 상단 상수 4개).
2. 다른 분기·톨게이트 로그 비교(route_extract.py replay 사용).
3. carrot-ms 후속 신규 커밋 발생 시 2절 재점검, AGNOS 안정판 여부 확인.
4. (선택) 견고성 스윕 재개, vE 기준 need-cap 재설계 또는 TTC 변화율 후보.
