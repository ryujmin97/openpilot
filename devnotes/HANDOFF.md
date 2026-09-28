Worker: Claude (194cha 세션, Claude Sonnet 5). 193cha-cont 이후 새 세션이며 사용자가 후속 선택을 "너의 판단대로"로 위임.
Date: 2026-09-28
Repository: ryujmin97/openpilot
Code Branch: carrot-ryu (base commit 99754dc847c5d0353a3535a46bbeadaaf055846b = 193cha-cont tests-only 커밋, 이번 세션 변동 없음)
Note Branch: carrot-ryu-note (base commit 82ed7712c0f0cae3d2aac029c8a050149968e99a = 193cha-cont devnotes. 194cha devnotes는 이 커밋 위에 push.)
carrot-ms 마지막 검토 체크포인트: 735a9a4 -> 4445c29 (194cha에서 신규 11건 판정 완료: Jetson 9건 + fc7ee88 제외, f992f9c 보류.)

작업:
1. 4절 0단계(지침 문서 SHA 고정 조회) + HANDOFF.md 확인.
2. carrot-ms 점검(2절): 735a9a4..4445c29 신규 11건 전수 판정. api.github.com이 rate limit이라 blobless bare clone + git log/diff-tree로 대체.
3. WIP.md 194cha 회차, WIP_SYNC.md 194차 체크포인트, 이 HANDOFF.md 갱신(devnotes 1회 push).

완료:
1. Jetson 설치기 계열 9건 제외(이 차량에 없는 하드웨어).
2. fc7ee88(C3 UI little core 공유) 제외: carrot-ryu에 display_scheduling.py가 없고 ui.py 구조가 다름.
3. f992f9c(LFS -> 일반 blob 전환) 보류: carrot-ryu는 LFS 설정/포인터 상태 그대로. 자세한 사유와 재검토 조건은 WIP_SYNC.md 194차.
4. 코드 변경 없음, 실차 검증: 미실시(12절).

미완료:
1. pytest 후속: (a'') following_distance 18건 하네스 갱신(코드 세션, 아래 주의사항의 연쇄 문제 참고), (b') dashcam_replay 1건 원인 확정(코드/테스트 중 어느 쪽이 나중에 바뀌었는지), (c) pytest_ci_setup.sh에 pytest-mock 추가(toolkit 변경이라 승인 필요, plannerd_clock 54 errors 해소가 확인된 상태).
2. (이월) 핵심 발견 68 실차 검증, 163차 게이트 실주행 검증, xTurn=6 로그 확보, 102ms wide-camera BOOT_TS gap(진단 WARN 로그 대기).
3. (이월) 110차 GATE_M 0.8/1.0, 114차 MAP_TURN_GUIDE_FACTOR=1.00 실차 검증.
4. (신규) f992f9c LFS 전환 재검토: 디바이스에서 LFS pull 실패나 계정 LFS 한도 문제가 확인되면 별도 코드 세션 + 사용자 승인으로 판단.

검증:
- 이번 세션은 코드 변경이 없고 pytest도 재실행하지 않았다. 마지막 전체 실행 수치(193cha-cont): controls+carrot tests 28 failed / 2196 passed / 31 errors(gap_recovery 수정 전 기준 아님, 수정만 적용된 상태), controls/tests만 21 failed / 626 passed / 57 errors(pytest-mock 없어 plannerd_clock 54 errors 포함). 실차 검증: 미실시(12절).
- 게이트를 완전 개방(g=1)으로 고정한 스텁이라 preview_release/cutout 테스트는 147차 게이트 동작을 검증하지 않음(193차에서 이월).
- xiaoge_vision 22건과 ImportError 수집 에러 9건의 원인은 192cha 분류 유지, 미재확인.
- carrot-ms 판정은 정적 확인(변경 파일 목록/핵심 diff/carrot-ryu 파일 존재). Jetson 9건은 라인 단위로 읽지 않음.

주의사항:
- following_distance 18건은 plant.py에 carrot 인자만 넣어서는 안 풀린다. 스크래치에서 확인한 연쇄: (1) 테스트 Params의 MyDrivingMode가 0이라 DrivingMode(0) ValueError(params_keys.h 기본값 3, 유효값 1~4), (2) sm이 dict라 all_checks 없음, (3) carrot_man_input이 sm.seen 요구, (4) 그 뒤 6건은 modelV2 경로 리스트가 비어 check_model_stopping의 y[-1]에서 ZeroDivisionError, 12건은 단언 실패(시뮬 91.1 vs 기대 67.25 등)로 하네스 미비인지 실제 동작 차이인지 미확정. 시작 전에 WIP.md 193cha 계속 회차를 읽을 것.
- 전역 git user.email은 ryujmin97@gmail.com으로 설정됨(사용자 확인). 이 회차 스크립트 로그에 `commit author: ryujmin97 <ryujmin97@gmail.com>`이 나오는지 확인. 기존 커밋 99754dc8/82ed7712 등의 author는 자리표시자이고 6ee1ce7b만 깨진 문자열(기능 영향 없음, --force 금지라 그대로). 스크립트는 전역 값이 ASCII 이메일 형식이 아니거나 미설정이면 ryujmin97@users.noreply.github.com으로 폴백한다(미설정이어도 죽지 않는 `((@(& git config --global user.email) -join "")).Trim()` 형태 사용, toolkit 템플릿에는 아직 미반영).
- carrot-ryu에는 openpilot/common/stopping_params.py와 openpilot/common/display_scheduling.py가 없다(VEgoStopping은 get_float * 0.01 직접 사용, 최소값 1). carrot-ms 후속 커밋이 get_stopping_speed나 DisplayScheduler에 의존하면 이 차이를 먼저 확인할 것. carrot-ryu는 .gitattributes가 LFS 설정이고 driving_supercombo.onnx/updater/lane.onnx는 LFS 포인터다.
- pytest 재실행은 toolkit/pytest_ci_setup.sh부터(세션마다 파일시스템 초기화). 백그라운드 실행은 `setsid nohup ... < /dev/null`로 분리해야 컴파일 중 조용히 죽지 않는다. 이 스크립트는 pytest-mock을 설치하지 않는다.
- api.github.com은 rate limit이 자주 걸린다. git ls-remote / blobless bare clone / raw(SHA 고정)로 대체할 것.
- 다음 코드 변경 세션은 5절 순차 전달(코드 스크립트 먼저 -> 확인 -> devnotes)을 따른다.

다음 작업:
1. pytest 후속(위 미완료 1의 a''/b'/c 중 사용자 선택) 또는 이월 항목(실차 검증들).
2. 다음 carrot-ms 점검은 체크포인트 4445c29 이후 신규 커밋부터.
