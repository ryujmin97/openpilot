Worker: Claude (170cha, Claude Sonnet 5)
Date: 2026-09-26
Repository: ryujmin97/openpilot
Code Branch: carrot-ryu (base: 7cd03aebca3bd882e2e05cbcde199a7c78fa9f04, 169차 push 확인됨 -- 170차 코드 반영은 실행/push 대기)
Note Branch: carrot-ryu-note (이 스크립트 반영 전 base: be0ae4b6ff50ae6f3ba5342d3502122a7588e17a, 168차 devnotes까지만 기록돼 있었음)
carrot-ms 마지막 검토·동기화 체크포인트: `3756e6d5`(130차, 139차 재확인) -- 신규 커밋 없음. 140~170차는 재점검 없음.

작업:
1. 세션 시작 4절 0단계(git ls-remote)로 carrot-ryu-note HEAD가 여전히 be0ae4b6(168차, HANDOFF/WIP/FINDINGS 모두 168차 "실행/push 대기" 상태)임을 확인. 반면 carrot-ryu(코드) HEAD는 이미 `7cd03aeb`(169차, "route freeze expiry(핵심 발견 67) + gas override timeout")까지 push 완료돼 있어, devnotes가 코드보다 최소 한 세션(169차) 뒤처진 상태를 발견(16절 해당). 169차 자체의 devnotes 정식 캐치업은 이번 세션 범위로 다루지 않고 다음 세션 최우선으로 이월(아래 미완료 3번), 코드 내용은 GitHub 직접 조회(raw SHA고정 + git hash-object)로 실측 확인.
2. 사용자와 이어진 논의(route 목표속도 오탐 원인 -- carrot_serv.py의 update_navi()가 카메라 표지판 인식(CS.speedLimit)을 디바운스 없이 nRoadLimitSpeed에 덮어써, carrot_man.py의 route freeze 폴백(핵심 발견 59/67)이 오탐 소스가 될 수 있음)를 바탕으로, 폴백값을 nRoadLimitSpeed에서 vCruise(운전자 설정속도)로 전환하는 수정 진행(핵심 발견 68). 사용자가 범위를 ②(route fallback, carrot_man.py)로 명시적으로 한정 -- carrot_serv.py의 ③ AutoRoadSpeedLimitOffset 후보 로직(1385~1392행)은 미변경.
3. 사용자가 Termux 사용을 명시(51/55/168차와 동일 패턴) -- 반영 스크립트를 bash로 작성.
4. 수정(carrot_man.py, +9/-4) 적용 후 py_compile 통과, pre/post-image blob hash 가드(`52510d16...` → `455b6a55...`), 로컬 bare 저장소(Linux) dry-run end-to-end(clone → pre-hash guard → anchor 1회 매치 치환 → post-hash guard → py_compile → commit → push) 성공, push된 커밋 numstat(+9/-4) 및 blob hash 재확인까지 완료.

완료:
1. carrot-ryu: 핵심 발견 68 수정(carrot_man.py, +9/-4) 로컬 dry-run 검증 완료. 실제 push는 사용자 실행 대기.
2. carrot-ryu-note: 이 스크립트 자체가 WIP.md 170차 / FINDINGS.md 핵심 발견 68 / HANDOFF.md 갱신 반영 수단(교체형 파일이라 이 문구는 반영 스크립트 실행 이후 시점 기준).

미완료:
1. `170cha_code_carrot_ryu.sh` 실행/push 확인 -- 다음 세션 최우선.
2. push 확인 후 GitHub raw(SHA고정)로 blob hash(`455b6a55...`) 재조회해 실제 반영 재확인 필요(16절).
3. **169차 devnotes 캐치업 미완료** -- carrot-ryu HEAD `7cd03aeb`(169차, 커밋 메시지 "169cha: route freeze expiry(핵심 발견 67) + gas override timeout", 부모 `3a17435d`)의 devnotes(WIP.md/FINDINGS.md/HANDOFF.md)가 아직 정식 기록되지 않음. 다음 세션에서 이 커밋 diff를 조회해 정식 devnotes 작성 필요.
4. 핵심 발견 68 수정의 실차 검증(다음 실주행 로그로 route 정보 부족/freeze 만료 구간의 desiredSpeed가 vCruise 설정값과 일치하는지 재확인).
5. 163차(게이트 완전 제거) 자체의 실주행 검증 -- 이번 세션에도 미포함.
6. xTurn=6(톨게이트) 로그 확보 -- 여전히 미확보(114차부터 이월).

검증:
- 핵심 발견 68 수정: py_compile 통과, anchor 1회 매치, pre/post-image blob hash 가드(byte-exact), 로컬 bare 저장소(Linux) dry-run end-to-end 성공(bash -n 구문 검사 포함, push된 커밋 numstat/blob hash 재확인). Termux(사용자 실제 환경, Android) 실행은 아직 없음. 실차 검증: 미실시.

주의사항:
- 169차 devnotes가 아직 기록되지 않은 채로 170차가 먼저 기록되는 순서 역전이 발생했다. 다음 세션은 4절 0단계 직후 이 갭부터 인지하고, 169차 정식 devnotes부터 작성한 뒤 이어갈 것(16절, WIP.md/FINDINGS.md 회차 번호 자체는 발생 순서와 무관하게 기록 시점 기준으로 계속 이어 붙이면 됨 -- 7절/19절의 "기존 기록 삭제/재배치 금지" 원칙상 170차를 169차보다 앞에 두는 소급 재배치는 하지 않는다).
- carrot_serv.py의 ③ AutoRoadSpeedLimitOffset 후보 로직(1385~1392행)은 이번 수정과 무관하게 그대로 유지됨 -- 향후 세션에서 "route fallback도 vCruise로 바뀌었으니 이것도 바뀐 줄" 혼동하지 않도록 명시.

다음 작업:
1. `170cha_code_carrot_ryu.sh` / `170cha_devnotes_carrot_ryu_note.sh` 실행/push 확인.
2. 169차 정식 devnotes 캐치업(WIP.md/FINDINGS.md에 169차 핵심 발견 67 항목 신규 작성, 커밋 `7cd03aeb` diff 기준).
3. 핵심 발견 68 수정 실차 검증.
