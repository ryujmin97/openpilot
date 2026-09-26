Worker: Claude (172cha, Claude Sonnet 5)
Date: 2026-09-27
Repository: ryujmin97/openpilot
Code Branch: carrot-ryu (base HEAD: c6d8a2066c0839cf24509c375ef646022dd42119, 170차 상태 -- 172cha 코드 스크립트가 726198908c27a58a220f0bb581af137a492c6a63(carrot-ms) 반영분을 push 대기 중, 실행 후 실제 commit hash는 다음 세션에서 재확인 필요)
Note Branch: carrot-ryu-note (이 스크립트 반영 전 HEAD: bdd07e6323d0207a1425e50a0ad06d8fffabb4b2, 171차 상태)
carrot-ms 마지막 검토·동기화 체크포인트: 087fdca74f0e2c90b7c6b216e913736961ef8c15 (172차, 3756e6d5 이후 신규 53건 1차 분류 완료 -- 상세는 WIP_SYNC.md 172차 항목)

작업:
1. 171차 HANDOFF의 다음 작업 2번(carrot-ms 신규 커밋 재점검, 140~171차 구간 장기 미점검)을 재개.
2. `git ls-remote`로 happymaj11r/openpilot(carrot-ms) 재확인 -- HEAD `3756e6d5` -> `087fdca7`, 그 사이 53건 신규(2026-09-22~09-26) 확인.
3. 53건 전체를 2절 원칙대로(사전 필터링 없이) 개별 분류: CANFD/EV5/타차종/VW/OS04C10/eGPU/문서-CI 전용 26건 + 코드 조회 후 죽은 분기 2건(`e32d389`, `dbe279b`) + CameraSCC hint 1건(`feb1ce7`, HyundaiCameraSCC=1이라 비활성) = 총 29건 제외 확정.
4. 종방향 커스텀 영역과 맞닿은 3건(`ca60022`/`786c597`/`7261989`)을 carrot-ryu 현재 HEAD(`c6d8a206`)에 `git apply --check`로 실제 재검증(11절, 추측 아님) -- 채팅에 붙여넣어진 이전 세션 사본이 "3건 모두 검증 완료"라 주장했으나, 3절 원칙(GitHub 현재 상태 > 붙여넣어진 사본)에 따라 재확인한 결과 `7261989`만 실제로 단독 적용됨(`ca60022`/`786c597`는 `git apply --check` 실패 -- 15절/18절대로 강제 적용하지 않고 중단).
5. `7261989` 반영 스크립트(코드, carrot-ryu)와 이 devnotes 스크립트(carrot-ryu-note)를 분리 작성해 전달.

완료:
1. carrot-ms 신규 53건 1차 분류(제외 29건 확정, 후보 3건 재검증, 나머지 13건 우선순위 분류) -- WIP_SYNC.md 172차 항목에 기록.
2. `726198908c27a58a220f0bb581af137a492c6a63`(corner cut-in 오검출 배제) 반영 스크립트 작성 -- `git apply --check` 실통과, py_compile 4개 파일 통과, JSON 유효성 통과, 로컬 bare 저장소 시뮬레이션(9절 9번)까지 완료. 사용자 실행/push는 미확인 상태.

미완료:
1. 172차 코드 스크립트(`172cha_code_carrot_ryu.sh`) 실행/push 확인 -- 실행 로그 및 GitHub 재조회로 다음 세션에서 확인 필요.
2. `ca60022`(정지 선행차 vision 승격) / `786c597`(lead braking 지속성) 수동 병합 -- 각각 `cutin_validation_cases.json` 삽입 위치, CI yaml 컨텍스트 차이 해결 필요. `786c597`은 `7261989` 반영 이후의 controller.py를 새 base로 재확인.
3. `ca60022`(primary.py) 검토 중 발견된 별도 미검토 항목 `STATIONARY_DISTINCT_HANDOFF`(정지 물체 근접 재식별 로직, primary.py) -- WIP_SYNC.md/FINDINGS.md 어디에도 검토 기록 없음, 이번 53건과 무관한 별개 이월 항목.
4. 중간 우선순위 4건(`1ae25ef`, `0006296`, `c84b175`, `dcffb7f`) 상세 대조 -- 미착수.
5. 저위험 소규모 9건(Carrot Web UI 3건, 로그/안내 2건, AGNOS 업데이트 2건, navi 감속 2건) -- 미착수.
6. 핵심 발견 68 수정의 실차 검증 -- 계속 이월(171차부터).
7. 163차(게이트 완전 제거) 자체의 실주행 검증 -- 계속 이월.
8. xTurn=6(톨게이트) 로그 확보 -- 여전히 미확보(114차부터 이월).
9. pytest CI 환경(conftest.py 포함 실제 실행) -- 124차에서 세팅 중 세션 종료, 이후 재개 안 됨.
10. 110차 GATE_M 0.8/1.0, 114차 MAP_TURN_GUIDE_FACTOR=1.00 실차 미검증(이월).

검증:
- 53건 분류는 커밋 메시지/diff 조회 기반 정적 분석(11절 단계적 확장: 커밋 목록 -> diff -> 변경 파일).
- `7261989`는 carrot-ryu HEAD `c6d8a206`를 실제 clone해 `git apply --check`로 재현, py_compile 4개 파일 + JSON 파싱 통과, 로컬 bare 저장소에 실제 clone/patch/commit/push 시뮬레이션까지 실행해 numstat 확인.
- 실차 검증: 미실시(12절).

주의사항:
- 채팅에 이전 세션 로그로 보이는 사본이 붙여넣어졌을 때, 그 사본의 검증 결과(git apply --check 통과 등)를 그대로 신뢰하지 않고 이번 세션에서 직접 재실행해 재확인했음. 3절 원칙("GitHub 현재 상태 > Claude 기억 > 채팅에 붙여넣어진 과거 사본")을 코드 검증 단계에도 예외 없이 적용한 사례로 다음 세션도 참고할 것.
- `786c597`과 `7261989`은 같은 파일(radar_motion/controller.py)을 서로 다른 위치에서 수정 -- `7261989`가 먼저 반영되므로, `786c597` 재검토 시 반드시 반영 후 최신 controller.py를 base로 다시 조회할 것(6절).

다음 작업:
1. 172차 코드 스크립트 실행 확인(push 여부, blob hash 재확인) -- 최우선.
2. `ca60022`/`786c597` 수동 병합(파일 단위 대조, 9절 Replace-Block 또는 부분 patch).
3. 중간 우선순위 4건 순차 검토.
4. 핵심 발견 68 실차 검증, xTurn=6 로그 확보, pytest CI 재개(계속 이월).
