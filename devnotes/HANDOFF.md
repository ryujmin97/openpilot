Worker: Claude (196cha 세션, Claude Sonnet 5). 195cha 이후 새 세션이며 사용자가 후속 선택을 "너의 판단대로"로 위임.
Date: 2026-09-28
Repository: ryujmin97/openpilot
Code Branch: carrot-ryu (base commit f075028fee5d5c0277a4c3c557606a9e6ccd2ee3 = 195cha plant.py 테스트 하네스 커밋. 196cha에서 코드 변경 없음.)
Note Branch: carrot-ryu-note (base commit 5f99b1f85f98516fc1e2138830d48179f772a885 = 195cha devnotes. 196cha devnotes는 이 커밋 위에 push.)
carrot-ms 마지막 검토 체크포인트: 735a9a4 -> 4445c29 (194cha 판정 완료, 195cha/196cha에서는 점검하지 않음. 다음 점검은 4445c29 이후 신규 커밋부터.)

작업:
1. 4절 0단계(지침 문서 SHA 고정 조회 5f99b1f8, 브랜치 URL 사본과 cmp 동일) + HANDOFF.md 확인.
2. 195cha 미완료 1번 수행: toolkit/pytest_ci_setup.sh로 환경 구성(1분 남짓) 후 following_distance 재실행, 남은 실패의 원인 측정.
3. HANDOFF 주의사항 조회: Plant 하네스 변경이 다른 Plant 사용 테스트와 넓은 회귀에 준 영향, Params 격리.
4. WIP.md 196cha 회차, 이 HANDOFF.md 갱신(devnotes 1회 push). 코드 변경 없음, WIP_SYNC.md 변경 없음.

완료:
1. following_distance: 18건 실패 -> 17 통과 / 1 실패(TestFollowingDistance_10: e2e=False, relaxed, v=10, 시뮬 20.333 vs 기대 23.5 ± 2.85). 하네스 미비가 아니라 기대값과 플래너의 T_FOLLOW 정의 차이다: 테스트는 스톡 get_T_FOLLOW(1.75/1.45/1.25)로 기대값을 계산하고, 플래너는 carrot.get_T_FOLLOW(TFollowGap 기본 1.40/1.20/1.10)를 쓴다. 시뮬 중 mpc.t_follow 실측 수렴값이 1.40/1.20/1.10이었다(비-e2e만 측정).
2. 미설명 편차 발견: 비-e2e에서 시뮬 - (T_carrot*v + 6)이 personality와 무관하게 속도별로 일정(v=10 +0.333, v=35 약 +9.8). 정상상태 수렴은 확인(t_end 100/200/400 s). 원인 미확정. 이 편차가 carrot T 감소를 우연히 상쇄해 17건이 통과했을 가능성은 추론이며 실험으로 확인하지 않았다.
3. Plant 계열 다른 테스트(test_longitudinal.py, car/tests/test_cruise_speed.py): 195cha 이전(부모 plant.py)에는 74건이 TypeError('carrot' 인자 누락)로 실패, 195cha 이후 FAILED 줄 20 -> 12로 줄고 새로 실패한 테스트 없음(A 실패 집합 ⊂ B 실패 집합). 남은 12건은 분류 미실시.
4. 넓은 회귀(controls+carrot 전체 디렉터리): 18 failed / 2506 passed / 31 errors. 193cha 계속 기준선(28/2196/31)과 항목별 대조: following_distance 18->1, 나머지 기존 항목(radar_lead_simulator 4, latcontrol 3, xiaoge_inference 2, dashcam_replay 1, 에러 31) 동일. 기준선에 없던 항목: carrot/server/tests 7건(xiaoge_proxy 6, web_upload 1), 기준선 실행 범위 포함 여부 미확인.
5. Params 격리 확인: pytest 안은 conftest autouse fixture(OpenpilotPrefix)로 격리, pytest 밖 직접 실행은 기본 Params 경로에 기본값을 씀(샌드박스 /root/.comma/params/d에 207키).
6. 실차 검증: 미실시(12절). 코드 변경 없음.

미완료:
1. (사용자 승인/선택 필요) following_distance 남은 1건 처리 방침: (i) 기대값을 carrot T 기준으로 교체 -- 미설명 편차 때문에 비-e2e v=35(허용오차 약 5~6 m 대비 편차 9.8 m)가 실패로 바뀔 계산이라 편차 원인 조사가 선행돼야 함, (ii) 알려진 차이로 문서화, (iii) 그대로 둠.
2. 미설명 편차(v=35에서 약 +9.8 m, v=10 +0.333 m, v=0 약 -1.5 m) 원인 조사. 방법 후보: 시뮬 중 사이클별 desired distance vs 실제 gap을 기록해 MPC가 어떤 목표를 추종하는지 분해(e2e 모드 T도 미측정).
3. 남은 12건 분류: test_cruise_speed 8건(TestCruiseSpeed_1,3,...,15 홀수 인덱스; "Did not reach 35 m/s" 8 + "35.55x == 35.0 ± 0.01" 8), test_longitudinal 서브테스트 7건(cruising at 25 m/s while disabled 2, slow to 5m/s ... pitch +0.1 3, approach slower cut-in car 1, resume from a stop 1). 스톡 플래너 기대인지 하네스 부족인지 미확인.
4. carrot/server/tests 7건 원인 확인(6건 aiohttp NotAppKeyWarning 에러 취급 -- 샌드박스 aiohttp 버전 문제일 수 있으나 프로젝트 핀 미조회, 1건 test_web_upload.py:215 소스 문자열 단언).
5. (b') dashcam_replay 1건 원인 확정(코드/테스트 중 어느 쪽이 나중에 바뀌었는지), (c) pytest_ci_setup.sh에 pytest-mock 추가(toolkit 변경이라 승인 필요; 이번에도 샌드박스에서만 설치. pytest-mock이 없으면 plannerd_clock 계열이 errors로 나옴(193cha 계속 기록: 54건)).
6. (이월) 핵심 발견 68 실차 검증, 163차 게이트 실주행 검증, xTurn=6 로그 확보, 102ms wide-camera BOOT_TS gap(진단 WARN 로그 대기).
7. (이월) 110차 GATE_M 0.8/1.0, 114차 MAP_TURN_GUIDE_FACTOR=1.00 실차 검증.
8. (이월) f992f9c LFS 전환 재검토: 디바이스에서 LFS pull 실패나 계정 LFS 한도 문제가 확인되면 별도 코드 세션 + 사용자 승인으로 판단.

검증:
- 이번 세션 pytest는 모두 샌드박스(Ubuntu 24, Python 3.12.3, pytest-mock 설치, xdist 기본, -p no:randomly)에서 HEAD f075028f로 실행했다. 실차 검증: 미실시(12절).
- following_distance 18건 전체 표와 T_FOLLOW 실측, Plant 계열 A/B 통제 실험(plant.py 부모 blob 81a4144c vs HEAD 824098da, 실험 후 HEAD 버전 복원과 blob 확인), 넓은 회귀 파일별 집계는 WIP.md 196cha 참고.
- t_follow 실측은 비-e2e 6개 조합(relaxed/standard/aggressive x v=10,35)만이다. e2e 모드 T는 미측정.
- 게이트를 완전 개방(g=1)으로 고정한 스텁이라 preview_release/cutout 테스트는 147차 게이트 동작을 검증하지 않음(193차에서 이월).
- xiaoge_vision 22건과 ImportError 수집 에러 9건의 원인은 192cha 분류 유지, 미재확인. 이번 로그에서 test_latcontrol_torque_buffer의 ImportError(LAT_ACCEL_REQUEST_BUFFER_SECONDS 없음)는 환경이 아니라 코드/테스트 불일치처럼 보이나 192cha 분류와 대조하지 않았다.

주의사항:
- 시작 전에 WIP.md 196cha 회차(following_distance 결과, T_FOLLOW 원인, 미설명 편차)를 읽을 것. 필요하면 195cha, 193cha 계속 회차도.
- Plant.__init__은 Params()에 params_keys.h 기본값을 put한다(값이 없는 키만). pytest 안에서는 conftest의 OpenpilotPrefix로 격리되지만, pytest 밖(스크래치 스크립트 등)에서 Plant를 돌리면 기본 Params 경로(Path.home()/.comma/params/d, 디바이스는 /data/params/d)에 실제로 쓴다. pytest 밖에서 돌릴 때는 OPENPILOT_PREFIX를 지정할 것.
- 이번 세션에 pytest 재실행에 든 시간: 환경 구성 1분 남짓, following_distance 약 50초, 넓은 회귀 약 80초. 재실행 비용이 크다는 195cha의 우려는 해당하지 않았다.
- `-p no:xdist`를 넘긴 pytest 실행은 이번에 출력이 비어 결과를 얻지 못했다(원인 미확인). xdist를 끄려면 다른 방법을 확인해서 쓸 것.
- 전역 git user.email은 ryujmin97@gmail.com(사용자 확인, f075028f에 반영 확인). 기존 커밋 99754dc8/82ed7712 등의 author는 자리표시자이고 6ee1ce7b만 깨진 문자열(기능 영향 없음, --force 금지라 그대로). 스크립트는 전역 값이 ASCII 이메일 형식이 아니거나 미설정이면 ryujmin97@users.noreply.github.com으로 폴백한다(미설정이어도 죽지 않는 ((@(& git config --global user.email) -join "")).Trim() 형태 사용, toolkit 템플릿에는 아직 미반영).
- carrot-ryu에는 openpilot/common/stopping_params.py와 openpilot/common/display_scheduling.py가 없다(VEgoStopping은 get_float * 0.01 직접 사용, 최소값 1). carrot-ms 후속 커밋이 get_stopping_speed나 DisplayScheduler에 의존하면 이 차이를 먼저 확인할 것. carrot-ryu는 .gitattributes가 LFS 설정이고 driving_supercombo.onnx/updater/lane.onnx는 LFS 포인터다. 노트 브랜치(carrot-ryu-note)에는 .gitattributes가 없다.
- pytest 재실행은 toolkit/pytest_ci_setup.sh부터(세션마다 파일시스템 초기화). 백그라운드 실행은 setsid nohup ... < /dev/null 로 분리해야 컴파일 중 조용히 죽지 않는다. 이 스크립트는 pytest-mock을 설치하지 않는다(pip install pytest-mock를 샌드박스에서 별도로).
- api.github.com은 rate limit이 자주 걸린다. git ls-remote / blobless bare clone / raw(SHA 고정)로 대체할 것. pwsh 설치 버전 조회도 curl -sIL https://github.com/PowerShell/PowerShell/releases/latest 의 Location 헤더 방식이 이번에도 rate limit 없이 동작(v7.6.6).
- 다음 코드 변경 세션은 5절 순차 전달(코드 스크립트 먼저 -> 확인 -> devnotes)을 따른다.

다음 작업:
1. 위 미완료 1~3 중 사용자 선택. 판단 순서 제안: 미설명 편차 원인 조사(2)가 following_distance 처리 방침(1)의 선결 조건이다. 남은 12건 분류(3)는 독립적으로 가능.
2. 또는 이월 항목(실차 검증들), carrot-ms 점검(체크포인트 4445c29 이후 신규 커밋부터), (b')/(c) 중 사용자 선택.
