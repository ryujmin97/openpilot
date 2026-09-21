Worker: Claude (117차, Claude Sonnet 5)
Date: 2026-09-21
Repository: ryujmin97/openpilot
Code Branch: carrot-ryu (base `22b101f623bd6ce07fa4ed1a655144058d3530dc`, 117차 VW MEB dead code 삭제 반영 확인. 부모 `62ae74dc` = 116차 camera_sync)
Note Branch: carrot-ryu-note (이 스크립트 반영 전 base `ccbef14d551e35f98985737f925fed40d51ec103`. 반영 후 HEAD는 다음 세션이 git ls-remote로 확인)
carrot-ms 마지막 검토/동기화 체크포인트: `4bb4b510`(camera_sync 스큐 허용오차 10ms→20ms) 반영 완료(WIP_SYNC.md 116차). 111차 확정 체크포인트는 `a23a77b1`. 이번 세션은 carrot-ms 동기화 작업 없음.

작업:
1. DEAD_CODE_REVIEW.md 후보 C10/C15(VW MEB) 삭제: `is_volkswagen_meb`/`is_vw_meb` 정의와 모든 사용처(drive_helpers, cruise, controlsd, longitudinal_planner, steer_ratio, 테스트 2개)를 제거. 7개 파일 +9/-153.

완료:
1. 세션 시작 확인: 지침 v2 조회(SHA 고정), HANDOFF.md 확인, 브랜치 HEAD 확인(HANDOFF 기록과 일치).
2. 반영 스크립트 v1이 CRLF checkout(`.gitattributes`의 `text=auto`) 때문에 치환 전 안전 중단 -> `core.eol=lf`와 `git diff --numstat` 검증을 추가한 v2로 반영. push 로그와 별개로 `git ls-remote`, 커밋 `.patch`, SHA 고정 raw(7개 파일 byte-exact)로 재확인.
3. 이 후속 스크립트로 WIP.md 117차, HANDOFF.md, DEAD_CODE_REVIEW.md(C10/C15 상태, 117차 항목)를 갱신.

미완료(다음 세션 최우선):
1. 실차 배포(디바이스 pull) 시점 -- 사용자 확인 후. 115차 dead code 1차 배치(`0e1bef52`), 116차 camera_sync(`62ae74dc`), 117차 VW MEB 삭제(`22b101f6`)가 모두 미배포로 누적돼 있어 한 번에 반영된다. 배포 후 swaglog로 controlsd/플래너 예외와 카메라 페어링 이상 여부 확인.
2. (이월) 114차 MAP_TURN_GUIDE_FACTOR 1.00 실차 관찰(급감속 구간이 운전자 제동인지 시스템 감속인지 확인), 110차 GATE_M 0.8/1.0 관찰, 견고성 스윕 재개(선택). CURRENT_STATUS.md는 이번에도 갱신하지 않았다.
3. 이번 CRLF 사고 교훈을 FINDINGS.md에 기록할지 결정(핵심 발견 번호 체계 확인 필요).

검증: 샌드박스 정적/단위 검증(py_compile 7파일, pyflakes 새 경고 없음, test_steer_ratio+test_controlsd 51->50건 통과(삭제한 VW 전용 테스트 1건 차이), controls/car 전체 실패 28건은 원본과 동일한 환경 문제)과 GitHub push 내용 대조(raw 조회 byte-exact). cruise.py 관련 테스트(test_cruise_speed 등)는 샌드박스에서 수집 불가라 cruise.py 변경은 정적 검증까지만 했다. 실차 검증: 미실시(이번 세션 전체).

주의사항:
- Windows에서 carrot-ryu를 clone해 텍스트를 치환하는 스크립트는 `.gitattributes`의 `* text=auto` 때문에 `core.autocrlf=false`만으로는 CRLF로 checkout된다. `--config core.eol=lf`를 함께 지정하고, 샌드박스의 `grep -c $'\r'`은 CR을 세지 못하므로 python 등으로 바이트 단위 확인.
- 동작 변화는 없다는 결론은 제네시스(hyundai)에서 `is_vw_meb`가 항상 False라는 코드 분석 기준이며 실차로 확인한 것이 아니다. 되돌리려면 `git revert 22b101f6`(carrot-ryu).
- opendbc_repo의 VW 코드와 `car.capnp`의 HUD 필드(`naviEventType` 등)는 의도적으로 남겼다.

다음 작업 후보:
1. 실차 배포 여부 결정, 배포 후 관찰(controlsd/플래너 예외 + 카메라 페어링).
2. carrot-ms 후속 신규 커밋 발생 시 2절(폐지된 필터 없이 전체 개별 분석) 재점검.
3. 114차/110차 이월 실차 관찰 항목.
4. dead code 추가 후보 발굴이 필요하면 DEAD_CODE_REVIEW.md 원칙(심볼 단위 grep으로 참조 0건 확정, 배치마다 사용자 승인)대로 새 배치.