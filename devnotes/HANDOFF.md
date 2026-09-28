Worker: Claude (198cha 세션, Claude Sonnet 5). 197cha 이후 같은 흐름의 새 세션이며, 사용자가 붙여준 코드 push 로그(f075028..df0da45, DONE)로 시작해 코드 반영을 확인하고 테스트를 재현한 뒤 devnotes만 기록(devnotes 1회 push).
Date: 2026-09-28
Repository: ryujmin97/openpilot
Code Branch: carrot-ryu (base commit df0da457b3bc527a994cb77fae50126567ee3b3f = 198cha test_following_distance 기대값 교체 커밋, 테스트 전용. 부모 f075028fee5d5c0277a4c3c557606a9e6ccd2ee3 = 195cha plant.py 하네스 커밋.)
Note Branch: carrot-ryu-note (base commit 39d39b75b74a5acab0d0da4e21cf1a379ecc586a = 197cha devnotes. 198cha devnotes는 이 커밋 위에 push.)
carrot-ms 마지막 검토 체크포인트: 735a9a4 -> 4445c29 (194cha 판정 완료, 195cha~198cha에서는 점검하지 않음. 다음 점검은 4445c29 이후 신규 커밋부터.)

작업:
1. 4절 0단계(지침 문서 v2를 브랜치 URL과 SHA 고정 URL 양쪽으로 조회, 50696 바이트 동일) + HANDOFF.md 조회.
2. 사용자가 전달한 코드 push 로그(f075028..df0da45)를 GitHub에서 직접 재확인(16절): ls-remote HEAD df0da457, blobless bare clone으로 부모 f075028f, author ryujmin97, 변경 1파일 test_following_distance.py(+32/-4), 커밋 메시지 확인.
3. df0da45의 diff를 직접 읽음(RecordingPlant로 마지막 스텝의 t_follow/comfort_brake/stop_distance를 기록해 기대값 계산에 사용).
4. toolkit/pytest_ci_setup.sh로 샌드박스 환경을 구성해 df0da45에서 test_following_distance.py 재실행.
5. WIP.md 198cha 회차, 이 HANDOFF.md 갱신(devnotes 1회 push). 코드 변경 없음(이 세션이 만든 코드 변경 없음), WIP_SYNC.md 변경 없음.

완료:
1. 198cha 코드 커밋 df0da45 반영 확인: test_following_distance의 기대값을 스톡 상수 대신 시뮬레이션에서 플래너(carrot)가 실제로 쓴 T/comfort_brake/stop_distance로 계산한다(get_safe_obstacle_distance(v_lead, t_follow, comfort_brake, stop_distance) - get_stopped_equivalence_factor(v_lead)). 허용오차는 변경 없음. 실행 코드 변경 없음(테스트 전용).
2. 재현: df0da45에서 following_distance 18 passed in 52.90s(-n 4, -p no:randomly). 197cha 기록의 같은 조건 기준선은 17 passed / 1 failed(TestFollowingDistance_10)였으므로 197cha 미완료 1번(following_distance 처리 방침)은 옵션 (i)로 해소됐다. 이번에 부모 f075028에서 기준선을 다시 돌리지는 않았다(197cha 기록 인용).
3. 실차 검증: 미실시(12절). 테스트 전용 변경.

미완료:
1. (판단만, 코드 변경 없음) comfort_brake 2.4와 정지등가 항 상수 2.5 불일치를 의도로 볼지. 실주행 영향: 60 km/h 약 +2.3 m, 100 km/h 약 +6.4 m, 35 m/s +10.2 m(계산, 실차 미검증), stop_distance -0.5 m. 198cha의 기대값은 플래너 실제 값을 따르므로 이 불일치를 테스트가 검출하지 않는다. 필요하면 실차에서 정상상태 추종 거리를 로그로 확인하는 항목으로 이월.
2. v=0 정상상태 gap이 desired(5.502)보다 약 1.06 m 작은 현상(4.43~4.48) 원인 미조사. 정지 제어 쪽 별개 요인으로 추정, 테스트는 통과.
3. 남은 12건 분류(197cha 기준, 이번에 넓은 회귀를 재집계하지 않아 현재 수치는 미확인): test_cruise_speed 8건(TestCruiseSpeed_1,3,...,15 홀수 인덱스; "Did not reach 35 m/s" 8 + "35.55x == 35.0 ± 0.01" 8), test_longitudinal 서브테스트 7건(cruising at 25 m/s while disabled 2, slow to 5m/s ... pitch +0.1 3, approach slower cut-in car 1, resume from a stop 1). 스톡 플래너 기대인지 하네스 부족인지 미확인.
4. carrot/server/tests 7건 원인 확인(6건 aiohttp NotAppKeyWarning 에러 취급 -- 샌드박스 aiohttp 버전 문제일 수 있으나 프로젝트 핀 미조회, 1건 test_web_upload.py:215 소스 문자열 단언), 기준선 실행 범위 포함 여부 미확인.
5. (b') dashcam_replay 1건 원인 확정(코드/테스트 중 어느 쪽이 나중에 바뀌었는지), (c) pytest_ci_setup.sh에 pytest-mock 추가(toolkit 변경이라 승인 필요; pytest-mock이 없으면 plannerd_clock 계열이 errors로 나옴(193cha 계속 기록: 54건)), (v) 197cha 측정 스크립트(Plant 서브클래스 프로브)를 toolkit에 넣을지(승인 필요; 198cha 테스트의 RecordingPlant와 같은 아이디어라 재사용 가능성을 함께 검토).
6. (이월) 핵심 발견 68 실차 검증, 163차 게이트 실주행 검증, xTurn=6 로그 확보, 102ms wide-camera BOOT_TS gap(진단 WARN 로그 대기).
7. (이월) 110차 GATE_M 0.8/1.0, 114차 MAP_TURN_GUIDE_FACTOR=1.00 실차 검증.
8. (이월) f992f9c LFS 전환 재검토: 디바이스에서 LFS pull 실패나 계정 LFS 한도 문제가 확인되면 별도 코드 세션 + 사용자 승인으로 판단.

검증:
- 이번 세션 테스트는 샌드박스(Ubuntu 24, Python 3.12, xdist `-n 4`, -p no:randomly)에서 HEAD df0da457로 test_following_distance.py 18건만 실행했다. 실차 검증: 미실시(12절).
- 넓은 회귀(다른 테스트 파일들)는 이번에 재집계하지 않았다. 197cha까지의 분류(xiaoge_vision 22건, ImportError 수집 에러 9건 등)는 192cha 분류를 유지하며 재확인하지 않았다.
- 게이트를 완전 개방(g=1)으로 고정한 스텁이라 preview_release/cutout 테스트는 147차 게이트 동작을 검증하지 않음(193차에서 이월).
- e2e 모드의 T 결정 경로, 주행 모드별 comfort_brake(Safe 0.9배), SpeedTFFactor/myTFollowFactor/decel boost 경로, 디바이스에서 사용자가 바꾼 파라미터는 미측정(197cha와 동일).
- 세부는 WIP.md 198cha(변경 내용, 재현 명령), 197cha(편차 원인 공식·표), 196cha 참고.

주의사항:
- 시작 전에 WIP.md 197cha 회차(원인, 공식, 표), 필요하면 196cha(T_FOLLOW 매핑, 18건 표), 195cha, 193cha 계속 회차도 읽을 것.
- Plant.__init__은 Params()에 params_keys.h 기본값을 put한다(값이 없는 키만). pytest 안에서는 conftest의 OpenpilotPrefix로 격리되지만, pytest 밖에서 Plant를 돌리면 기본 Params 경로(Path.home()/.comma/params/d, 디바이스는 /data/params/d)에 실제로 쓴다. pytest 밖에서 돌릴 때는 `with OpenpilotPrefix():`(openpilot.common.prefix)로 감쌀 것: msgq 경로(안 감싸면 IpcError: Messaging failure with radarState)와 Params가 함께 격리된다.
- pytest 실행 옵션: pyproject.toml addopts에 `-n auto --dist=loadgroup`이 있으므로 `-p no:xdist`는 쓰지 말 것(사용법 오류로 종료). xdist는 `-n 0`으로 끄고 병렬은 `-n 4`. 요약 줄을 grep으로 걸러 볼 때 결과가 비면 tail로 에러부터 확인할 것(197cha에서 옵션 오류가 grep에 가려져 2회 헛실행).
- 소요 시간: 환경 구성 1분 남짓(백그라운드), following_distance 18건 약 53초(-n 4), 프로브 1회(v 하나, 3 personality) 약 8초.
- 전역 git user.email은 ryujmin97@gmail.com(사용자 확인, f075028f, df0da45, b788ac1에 반영 확인). 기존 커밋 99754dc8/82ed7712 등의 author는 자리표시자이고 6ee1ce7b만 깨진 문자열(기능 영향 없음, --force 금지라 그대로). 스크립트는 전역 값이 ASCII 이메일 형식이 아니거나 미설정이면 ryujmin97@users.noreply.github.com으로 폴백한다(미설정이어도 죽지 않는 ((@(& git config --global user.email) -join "")).Trim() 형태 사용, toolkit 템플릿에는 아직 미반영).
- carrot-ryu에는 openpilot/common/stopping_params.py와 openpilot/common/display_scheduling.py가 없다(VEgoStopping은 get_float * 0.01 직접 사용, 최소값 1). carrot-ms 후속 커밋이 get_stopping_speed나 DisplayScheduler에 의존하면 이 차이를 먼저 확인할 것. carrot-ryu는 .gitattributes가 LFS 설정이고 driving_supercombo.onnx/updater/lane.onnx는 LFS 포인터다. 노트 브랜치(carrot-ryu-note)에는 .gitattributes가 없다(단 FINDINGS.md는 LF/CRLF 혼재라 `* text eol=crlf` 같은 강제 정규화 조건에서는 devnotes 스크립트의 "변경 파일 2개" 검사가 안전 중단한다).
- pytest 재실행은 toolkit/pytest_ci_setup.sh부터(세션마다 파일시스템 초기화). 백그라운드 실행은 setsid nohup ... < /dev/null 로 분리해야 컴파일 중 조용히 죽지 않는다. 이 스크립트는 pytest-mock을 설치하지 않는다(필요하면 pip install pytest-mock를 샌드박스에서 별도로).
- api.github.com은 rate limit이 자주 걸린다. git ls-remote / blobless bare clone / raw(SHA 고정)로 대체할 것. pwsh 설치 버전 조회도 curl -sIL https://github.com/PowerShell/PowerShell/releases/latest 의 Location 헤더 방식이 이번에도 rate limit 없이 동작(v7.6.6). carrot-ms 원본 raw 경로는 `openpilot/selfdrive/...` 접두가 붙는다(`selfdrive/...`만 쓰면 404).
- 다음 코드 변경 세션은 5절 순차 전달(코드 스크립트 먼저 -> 확인 -> devnotes)을 따른다.

다음 작업:
1. 사용자가 선택: (a) 남은 12건 분류(미완료 3, 넓은 회귀 재집계 포함), (b) carrot-ms 점검(체크포인트 4445c29 이후 신규 커밋부터), (c) 미완료 1(comfort_brake 2.4 vs 2.5 의도 판단), (d) 이월 항목(실차 검증들), (e) (b')/(c)/(v).
2. 코드 변경이 나오면 5절 순차 전달(코드 스크립트 먼저 -> 확인 -> devnotes 1회).
