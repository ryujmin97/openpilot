Worker: Claude (193cha-cont 세션, Claude Sonnet 5). 193cha 세션에서 이어짐(사용자가 후속 선택을 "너의 판단대로"로 위임).
Date: 2026-09-28
Repository: ryujmin97/openpilot
Code Branch: carrot-ryu (base commit 99754dc847c5d0353a3535a46bbeadaaf055846b = 193cha-cont tests-only 커밋. 부모 f6768af86b74f737e50159e476ec43ef837287bd.)
Note Branch: carrot-ryu-note (base commit 6ee1ce7b26a1932838771d43137db9a570314e80, 193cha devnotes. 193cha-cont devnotes는 이 커밋 위에 push.)
carrot-ms 마지막 검토 체크포인트: 3441183 -> 735a9a4 (192cha에서 신규 74건 전수 판정 완료, 전부 제외. 193cha/193cha-cont에서 재점검 안 함.)

작업:
1. (a') 중 gap_recovery 28건만 코드 push: test_longitudinal_gap_recovery.py의 log 스텁에 LongitudinalPersonality relaxed=2/moreRelaxed=3 추가 (99754dc8, 1줄, 테스트만). 5절 순차 전달 후 GitHub 직접 재확인 완료(부모/변경량/blob/BOM/CR).
2. following_distance 18건과 dashcam_replay 1건은 스크래치 클론에서 원인만 조사, 저장소 변경 없음.
3. author 이메일 깨짐 사고 원인 확정 및 스크립트 결함(전역 이메일 미설정 시 null 오류) 수정.
4. WIP.md 193cha 계속 회차 기록, 이 HANDOFF.md 갱신.

완료:
1. gap_recovery 28건 해소: 해당 파일 28 failed/50 passed -> 78 passed (샌드박스). controls/tests 전체 재실행에서 새 실패 없음.
2. 코드 스크립트 v2가 사용자 PC(py -3, Python 3.12.7)에서 끝까지 실행되어 99754dc8 push 성공. GitHub에서 직접 확인.
3. author 이메일 사고 원인 확정: 전역 git user.email에 자리표시자 문자열이 들어 있었고 PS 5.1 인코딩 변환으로 6ee1ce7b 커밋 author만 깨짐(히스토리는 그대로 둠).

미완료:
1. pytest 후속: (a'') following_distance 18건 하네스 갱신(코드 세션, 아래 주의사항의 연쇄 문제 참고), (b') dashcam_replay 1건 원인 확정(코드/테스트 중 어느 쪽이 나중에 바뀌었는지), (c) pytest_ci_setup.sh에 pytest-mock 추가(toolkit 변경이라 승인 필요, plannerd_clock 54 errors 해소가 확인된 상태).
2. (이월) 핵심 발견 68 실차 검증, 163차 게이트 실주행 검증, xTurn=6 로그 확보, 102ms wide-camera BOOT_TS gap(진단 WARN 로그 대기).
3. (이월) 110차 GATE_M 0.8/1.0, 114차 MAP_TURN_GUIDE_FACTOR=1.00 실차 검증.

검증:
- pytest는 샌드박스 단위 테스트이며 실차 검증이 아님. 실차 검증: 미실시(12절).
- 이번 세션 최종 상태에서 controls+carrot tests 전체를 다시 돌리지는 않았다. 마지막 전체 실행(gap_recovery 수정만 적용, pytest-mock 설치 상태)은 28 failed / 2196 passed / 31 errors. 이번 세션 재실행은 controls/tests만: 21 failed / 626 passed / 57 errors(pytest-mock 없어 plannerd_clock 54 errors 포함).
- 게이트를 완전 개방(g=1)으로 고정한 스텁이라 preview_release/cutout 테스트는 147차 게이트 동작을 검증하지 않음(193cha에서 이월).
- xiaoge_vision 22건과 ImportError 수집 에러 9건의 원인은 192cha 분류 유지, 미재확인.

주의사항:
- following_distance 18건은 plant.py에 carrot 인자만 넣어서는 안 풀린다. 스크래치에서 확인한 연쇄: (1) 테스트 Params의 MyDrivingMode가 0이라 DrivingMode(0) ValueError(params_keys.h 기본값 3, 유효값 1~4), (2) sm이 dict라 all_checks 없음, (3) carrot_man_input이 sm.seen 요구, (4) 그 뒤 6건은 modelV2 경로 리스트가 비어 check_model_stopping의 y[-1]에서 ZeroDivisionError, 12건은 단언 실패(시뮬 91.1 vs 기대 67.25 등)로 하네스 미비인지 실제 동작 차이인지 미확정. 시작 전에 WIP.md 193cha 계속 회차를 읽을 것.
- 최근 코드/devnotes 커밋의 author 이메일은 자리표시자 `여기에_깃허브_가입이메일@example.com`이고 6ee1ce7b만 깨진 문자열이다(기능 영향 없음, --force 금지라 그대로). 스크립트는 전역 git user.email이 ASCII 이메일 형식일 때만 사용하고 아니면 자리표시자로 폴백한다. 전역 값이 미설정이어도 죽지 않도록 `((@(& git config --global user.email) -join "")).Trim()` 형태를 쓴다(toolkit 템플릿에는 아직 미반영).
- carrot-ryu에는 openpilot/common/stopping_params.py가 없다(VEgoStopping은 get_float * 0.01 직접 사용, 최소값 1). carrot-ms 후속 커밋이 get_stopping_speed에 의존하면 이 차이를 먼저 확인할 것.
- pytest 재실행은 toolkit/pytest_ci_setup.sh부터(세션마다 파일시스템 초기화). 백그라운드 실행은 `setsid nohup ... < /dev/null`로 분리해야 컴파일 중 조용히 죽지 않는다. 이 스크립트는 pytest-mock을 설치하지 않는다.
- 다음 코드 변경 세션은 5절 순차 전달(코드 스크립트 먼저 -> 확인 -> devnotes)을 따른다.

다음 작업:
1. pytest 후속(위 미완료 1의 a''/b'/c 중 사용자 선택) 또는 이월 항목(실차 검증들).
2. 다음 carrot-ms 점검은 체크포인트 735a9a4 이후 신규 커밋부터.
