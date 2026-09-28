Worker: Claude (195cha 세션, Claude Sonnet 5). 194cha 이후 새 세션이며 사용자가 후속 선택을 "너의 판단대로"로 위임.
Date: 2026-09-28
Repository: ryujmin97/openpilot
Code Branch: carrot-ryu (base commit f075028fee5d5c0277a4c3c557606a9e6ccd2ee3 = 195cha plant.py 테스트 하네스 커밋, 부모 99754dc847c5d0353a3535a46bbeadaaf055846b)
Note Branch: carrot-ryu-note (base commit 4114b5fd4365a4c8a73d24b8d1a931680fcef631 = 194cha devnotes. 195cha devnotes는 이 커밋 위에 push.)
carrot-ms 마지막 검토 체크포인트: 735a9a4 -> 4445c29 (194cha 판정 완료, 195cha에서는 점검하지 않음. 다음 점검은 4445c29 이후 신규 커밋부터.)

작업:
1. 4절 0단계(지침 문서 SHA 고정 조회 4114b5fd) + HANDOFF.md 확인.
2. (a'') following_distance 18건 하네스 갱신 착수: plant.py 코드 push(f075028f) -> GitHub 직접 재확인(16절) -> 이 devnotes.
3. WIP.md 195cha 회차, 이 HANDOFF.md 갱신(devnotes 1회 push). WIP_SYNC.md는 변경 없음.

완료:
1. 코드 반영: f075028f, plant.py 1파일 +27/-3, blob 81a4144c... -> 824098da.... 내용은 FakeSubMaster(seen/alive/valid/logMonoTime/all_checks), Params 기본값 put 후 CarrotPlanner() 생성, modelV2.position y/z/t 채우기, planner.update(sm, self.carrot) 호출. 테스트 하네스뿐이며 주행 코드 변경 없음.
2. GitHub 재확인: HEAD/부모/author(ryujmin97 <ryujmin97@gmail.com>)/numstat/blob/LF/BOM 없음/py_compile 통과, update 시그니처 일치, MyDrivingMode 기본값 3. 전역 git 이메일 설정이 실제 커밋에 반영된 것을 이번에 처음 확인.
3. 실차 검증: 미실시(12절).

미완료:
1. pytest 재실행 미실시(이번 세션의 판단): following_distance 18건이 풀렸는지 미확인. 다음 코드 세션의 첫 작업은 toolkit/pytest_ci_setup.sh로 환경을 만들고 following_distance 테스트를 돌려 남은 실패를 분류하는 것. 남은 12건 단언 실패(시뮬 91.1 vs 기대 67.25 등)가 하네스 미비인지 실제 동작 차이인지 확정 필요.
2. (b') dashcam_replay 1건 원인 확정(코드/테스트 중 어느 쪽이 나중에 바뀌었는지), (c) pytest_ci_setup.sh에 pytest-mock 추가(toolkit 변경이라 승인 필요, plannerd_clock 54 errors 해소가 확인된 상태).
3. (이월) 핵심 발견 68 실차 검증, 163차 게이트 실주행 검증, xTurn=6 로그 확보, 102ms wide-camera BOOT_TS gap(진단 WARN 로그 대기).
4. (이월) 110차 GATE_M 0.8/1.0, 114차 MAP_TURN_GUIDE_FACTOR=1.00 실차 검증.
5. (이월) f992f9c LFS 전환 재검토: 디바이스에서 LFS pull 실패나 계정 LFS 한도 문제가 확인되면 별도 코드 세션 + 사용자 승인으로 판단.

검증:
- 이번 세션은 pytest를 재실행하지 않았다. 마지막 전체 실행 수치(193cha-cont, plant.py 변경 전): controls+carrot tests 28 failed / 2196 passed / 31 errors, controls/tests만 21 failed / 626 passed / 57 errors(pytest-mock 없어 plannerd_clock 54 errors 포함). 실차 검증: 미실시(12절).
- 코드 push는 정적 확인만 했다(blob/diff/py_compile/시그니처). 전달 시점의 pwsh 시뮬레이션은 Linux pwsh 7.6.6 기준이며 Windows PowerShell 5.1 실행은 사용자 로그로만 확인.
- 게이트를 완전 개방(g=1)으로 고정한 스텁이라 preview_release/cutout 테스트는 147차 게이트 동작을 검증하지 않음(193차에서 이월).
- xiaoge_vision 22건과 ImportError 수집 에러 9건의 원인은 192cha 분류 유지, 미재확인.

주의사항:
- plant.py의 Plant.__init__은 Params()에 params_keys.h 기본값을 put한다(값이 없는 키만). 테스트 환경의 Params 경로에 실제로 쓰므로, 격리 없이 디바이스/개발 PC에서 실행하면 그곳 Params가 채워질 수 있다. Params 경로 격리 여부는 조회하지 않음.
- Plant를 쓰는 다른 longitudinal_maneuvers 계열 테스트가 이 변경(CarrotPlanner 연결)으로 영향받는지 조회하지 않음. pytest 재실행 때 함께 확인할 것.
- 시작 전에 WIP.md 195cha 회차와 193cha 계속 회차를 읽을 것(following_distance 연쇄 조사 내용).
- 전역 git user.email은 ryujmin97@gmail.com(사용자 확인, f075028f에 반영 확인). 기존 커밋 99754dc8/82ed7712 등의 author는 자리표시자이고 6ee1ce7b만 깨진 문자열(기능 영향 없음, --force 금지라 그대로). 스크립트는 전역 값이 ASCII 이메일 형식이 아니거나 미설정이면 ryujmin97@users.noreply.github.com으로 폴백한다(미설정이어도 죽지 않는 ((@(& git config --global user.email) -join "")).Trim() 형태 사용, toolkit 템플릿에는 아직 미반영).
- carrot-ryu에는 openpilot/common/stopping_params.py와 openpilot/common/display_scheduling.py가 없다(VEgoStopping은 get_float * 0.01 직접 사용, 최소값 1). carrot-ms 후속 커밋이 get_stopping_speed나 DisplayScheduler에 의존하면 이 차이를 먼저 확인할 것. carrot-ryu는 .gitattributes가 LFS 설정이고 driving_supercombo.onnx/updater/lane.onnx는 LFS 포인터다.
- pytest 재실행은 toolkit/pytest_ci_setup.sh부터(세션마다 파일시스템 초기화). 백그라운드 실행은 setsid nohup ... < /dev/null 로 분리해야 컴파일 중 조용히 죽지 않는다. 이 스크립트는 pytest-mock을 설치하지 않는다.
- api.github.com은 rate limit이 자주 걸린다(195cha에서도 재현). git ls-remote / blobless bare clone / raw(SHA 고정)로 대체할 것.
- 다음 코드 변경 세션은 5절 순차 전달(코드 스크립트 먼저 -> 확인 -> devnotes)을 따른다.

다음 작업:
1. pytest 재실행으로 following_distance 결과 확정(위 미완료 1) 후, 남은 실패에 따라 (a'') 후속 또는 (b')/(c) 중 사용자 선택. 또는 이월 항목(실차 검증들).
2. 다음 carrot-ms 점검은 체크포인트 4445c29 이후 신규 커밋부터.
