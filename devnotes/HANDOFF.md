Worker: Claude (193cha 사후 확인/기록 세션, Claude Sonnet 5). 코드 커밋 f6768af8의 작성 세션/도구는 이 세션에서 확인하지 못했고 GitHub 조회로 사후 확인함.
Date: 2026-09-28
Repository: ryujmin97/openpilot
Code Branch: carrot-ryu (base commit f6768af86b74f737e50159e476ec43ef837287bd = 193cha tests-only 커밋. 부모 6ed56f0d. 이 세션은 코드 변경 없음.)
Note Branch: carrot-ryu-note (base commit bfa53c81f5095a228b581378a1249362f473c81f, 192cha-cont. 193cha devnotes는 이 커밋 위에 push.)
carrot-ms 마지막 검토 체크포인트: 3441183 -> 735a9a4 (192cha에서 신규 74건 전수 판정 완료, 전부 제외. 193cha에서 재점검 안 함.)

작업:
1. carrot-ryu HEAD가 HANDOFF 기록(6ed56f0d)과 달라 GitHub에서 직접 확인(16절): f6768af8은 tests 5파일 +16/-8, 스텁/픽스처만 갱신하고 단언은 불변.
2. f6768af8 기준 pytest를 192cha와 같은 조건으로 재실행하고 남은 실패를 예외 메시지로 분류.
3. 후속 (c)의 전제(pytest-mock 추가)를 샌드박스에서만 확인.
4. WIP.md 193cha 회차 기록, 이 HANDOFF.md 갱신.

완료:
1. pytest: 2114 passed / 56 failed / 85 errors (192cha: 2011/159/85). 수정한 5파일은 실패 0건이고 감소분 103이 파일별 집계와 일치.
2. 남은 56 failed 전건 분류: gap_recovery 28(`moreRelaxed` 스텁 누락) + following_distance 18(`update()`에 `carrot` 인자 누락) = 하네스 노후 46건, pyray 없음 4 + 생성 DBC 부재 3 + OpenCV ONNX 2 = 샌드박스 한계 9건, dashcam_replay 1(원인 미조사).
3. pytest-mock 설치 시 test_plannerd_clock 54건 전부 통과(파일 단위 확인).

미완료:
1. pytest 후속: (a') gap_recovery 28 + following_distance 18 하네스 갱신(코드 세션), (b') dashcam_replay 1건 조사, (c) pytest_ci_setup.sh에 pytest-mock 추가(54 errors 해소 확인됨, toolkit 변경이라 승인 필요).
2. (이월) 핵심 발견 68 실차 검증, 163차 게이트 실주행 검증, xTurn=6 로그 확보, 102ms wide-camera BOOT_TS gap(진단 WARN 로그 대기).
3. (이월) 110차 GATE_M 0.8/1.0, 114차 MAP_TURN_GUIDE_FACTOR=1.00 실차 검증.

검증:
- pytest는 샌드박스 단위 테스트이며 실차 검증이 아님. 실차 검증: 미실시(12절).
- 이 세션은 f6768af8의 전체 diff를 직접 읽었으나, 커밋 작성 세션의 실행 로그는 보지 못함.
- 미재확인: xiaoge_vision 22건과 ImportError 수집 에러 9건의 원인(192cha 분류 유지). pytest-mock 추가 후 전체 재실행은 하지 않음(2168/56/31은 산술 추정).
- 게이트를 완전 개방(g=1)으로 고정한 스텁이라 preview_release/cutout 테스트는 147차 게이트 동작을 검증하지 않음.

주의사항:
- 최근 코드/devnotes 커밋의 author 이메일이 `여기에_깃허브_가입이메일@example.com` 자리표시자다(기능 영향 없음). 193cha devnotes 스크립트는 전역 git 설정 user.email이 있으면 그것을 쓰고, 없으면 자리표시자로 폴백한다.
- carrot-ryu에는 openpilot/common/stopping_params.py가 없다(VEgoStopping은 get_float * 0.01 직접 사용, 최소값 1). carrot-ms 후속 커밋이 get_stopping_speed에 의존하면 이 차이를 먼저 확인할 것.
- pytest 재실행은 toolkit/pytest_ci_setup.sh부터(세션마다 파일시스템 초기화). 백그라운드 실행은 `setsid nohup ... < /dev/null`로 분리해야 컴파일 중 조용히 죽지 않는다.
- 다음 코드 변경 세션은 5절 순차 전달(코드 스크립트 먼저 -> 확인 -> devnotes)을 따른다.

다음 작업:
1. pytest 후속(위 미완료 1의 a'/b'/c 중 사용자 선택) 또는 이월 항목(실차 검증들).
2. 다음 carrot-ms 점검은 체크포인트 735a9a4 이후 신규 커밋부터.
