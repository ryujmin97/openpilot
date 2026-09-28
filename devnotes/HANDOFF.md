Worker: Claude (197cha 세션, Claude Sonnet 5). 196cha 이후 같은 흐름의 새 세션이며 사용자가 후속 선택을 "너의 판단대로"로 위임한 뒤, 코드는 건드리지 않고 devnotes만 먼저 기록하도록 선택.
Date: 2026-09-28
Repository: ryujmin97/openpilot
Code Branch: carrot-ryu (base commit f075028fee5d5c0277a4c3c557606a9e6ccd2ee3 = 195cha plant.py 테스트 하네스 커밋. 196cha, 197cha에서 코드 변경 없음.)
Note Branch: carrot-ryu-note (base commit b788ac1855442bdaa2f86acc763a0dde5abca63d = 196cha devnotes. 197cha devnotes는 이 커밋 위에 push.)
carrot-ms 마지막 검토 체크포인트: 735a9a4 -> 4445c29 (194cha 판정 완료, 195cha/196cha/197cha에서는 점검하지 않음. 다음 점검은 4445c29 이후 신규 커밋부터. 197cha는 원인 조사용으로 carrot-ms HEAD 87f8bed의 두 파일 일부를 조회했을 뿐 동기화 검토가 아님.)

작업:
1. 4절 0단계(지침 문서 v2 조회) + 196cha devnotes 반영을 GitHub에서 직접 재확인(HEAD b788ac18, 부모 5f99b1f, 변경 2파일, blob 일치).
2. 196cha 스크립트 재검증(9절 체크리스트 재실행): BOM/파서/bare 시뮬 (a)(b) 통과, 더 강한 CRLF 재현에서는 FINDINGS.md 혼재 개행 때문에 안전 중단(push 없음).
3. 196cha 미완료 2번(미설명 편차 원인 조사) 수행: toolkit/pytest_ci_setup.sh로 환경 구성 후 Plant 서브클래스로 t_follow/comfort_brake/stop_distance/desired distance를 실측.
4. 업스트림 carrot-ms 대응 줄 대조, 기대값 교체 스크래치 실험(저장소 미반영, 삭제).
5. WIP.md 197cha 회차, 이 HANDOFF.md 갱신(devnotes 1회 push). 코드 변경 없음, WIP_SYNC.md 변경 없음.

완료:
1. 미설명 편차 원인 확정(측정): 비-e2e 정상상태 gap = T_carrot*v_ego + stop_distance(5.5) + v_ego^2/(2*carrot_cb 2.4) - v_lead^2/(2*2.5). 앞차 정지등가 항 get_stopped_equivalence_factor가 모듈 상수 COMFORT_BRAKE(2.5)를 쓰고 carrot.comfort_brake는 2.4라 v_lead=v_ego일 때 v^2*0.008333이 남는다(v=10 +0.833, v=35 +10.208). stop_distance 5.5(StopDistanceCarrot 기본 550)는 -0.5. v=10 순 편차 +0.333, v=35 약 +9.8은 196cha 관측과 정확히 일치. 시뮬 gap은 플래너 base_desired_distances와 0.001 m 안에서 일치(v=10, v=35).
2. 업스트림 carrot-ms(HEAD 87f8bed)의 long_mpc.py, carrot_functions.py에도 같은 구조(comfortBrake 2.4 vs 상수 2.5)가 있다(해당 줄만 대조). carrot-ryu가 만든 편차가 아니라 물려받은 구조로 보인다.
3. 스크래치 실험: 기대값을 get_safe_obstacle_distance(v, T, 2.4, 5.5) - get_stopped_equivalence_factor(v)(T aggressive 1.10 / standard 1.20 / relaxed 1.40)로 바꾸면 following_distance 18 passed. 같은 조건 원본은 1 failed / 17 passed(기준선 재현). 스크래치 삭제, 저장소 미변경.
4. 196cha 기록 보완: "기대값을 carrot T로 바꾸면 v=35 실패"는 T만 바꾸고 상수를 그대로 둘 때의 계산이며, comfort_brake/stop_distance까지 반영하면 통과한다. 196cha 본문은 수정하지 않았다(7절).
5. `-p no:xdist` 출력이 비었던 원인 확정: pyproject.toml addopts의 `-n auto --dist=loadgroup`과 충돌해 사용법 오류로 종료. xdist는 `-n 0`으로 끈다(동작 확인).
6. 실차 검증: 미실시(12절). 코드 변경 없음.

미완료:
1. (사용자 승인/선택 필요) following_distance 남은 1건(TestFollowingDistance_10) 처리 방침: (i) test_following_distance.py 기대값을 실제 플래너 값으로 교체(테스트 전용 코드 변경, carrot-ryu; 하드코딩 대신 CarrotPlanner/Params에서 읽는 방식을 먼저 검토), (ii) 알려진 차이로 문서화, (iii) 그대로 둠. 5절 순차 전달(코드 스크립트 -> 확인 -> devnotes) 적용.
2. (판단만, 코드 변경 없음) comfort_brake 2.4와 정지등가 항 상수 2.5 불일치를 의도로 볼지. 실주행 영향: 60 km/h 약 +2.3 m, 100 km/h 약 +6.4 m, 35 m/s +10.2 m(계산, 실차 미검증), stop_distance -0.5 m. 필요하면 실차에서 정상상태 추종 거리를 로그로 확인하는 항목으로 이월.
3. v=0 정상상태 gap이 desired(5.502)보다 약 1.06 m 작은 현상(4.43~4.48) 원인 미조사. 정지 제어 쪽 별개 요인으로 추정, 테스트는 통과.
4. 남은 12건 분류: test_cruise_speed 8건(TestCruiseSpeed_1,3,...,15 홀수 인덱스; "Did not reach 35 m/s" 8 + "35.55x == 35.0 ± 0.01" 8), test_longitudinal 서브테스트 7건(cruising at 25 m/s while disabled 2, slow to 5m/s ... pitch +0.1 3, approach slower cut-in car 1, resume from a stop 1). 스톡 플래너 기대인지 하네스 부족인지 미확인.
5. carrot/server/tests 7건 원인 확인(6건 aiohttp NotAppKeyWarning 에러 취급 -- 샌드박스 aiohttp 버전 문제일 수 있으나 프로젝트 핀 미조회, 1건 test_web_upload.py:215 소스 문자열 단언), 기준선 실행 범위 포함 여부 미확인.
6. (b') dashcam_replay 1건 원인 확정(코드/테스트 중 어느 쪽이 나중에 바뀌었는지), (c) pytest_ci_setup.sh에 pytest-mock 추가(toolkit 변경이라 승인 필요; pytest-mock이 없으면 plannerd_clock 계열이 errors로 나옴(193cha 계속 기록: 54건)), (v) 이번 측정 스크립트(Plant 서브클래스 프로브)를 toolkit에 넣을지(승인 필요).
7. (이월) 핵심 발견 68 실차 검증, 163차 게이트 실주행 검증, xTurn=6 로그 확보, 102ms wide-camera BOOT_TS gap(진단 WARN 로그 대기).
8. (이월) 110차 GATE_M 0.8/1.0, 114차 MAP_TURN_GUIDE_FACTOR=1.00 실차 검증.
9. (이월) f992f9c LFS 전환 재검토: 디바이스에서 LFS pull 실패나 계정 LFS 한도 문제가 확인되면 별도 코드 세션 + 사용자 승인으로 판단.

검증:
- 이번 세션 시뮬레이션은 모두 샌드박스(Ubuntu 24, Python 3.12.3, xdist `-n 4`, -p no:randomly)에서 HEAD f075028f로 실행했다. 실차 검증: 미실시(12절).
- 측정 범위: 비-e2e, personality 0/1/2 x v=0/10/35, t_end 100 s, Plant Params 기본값. e2e 모드의 T/편차, 주행 모드별 comfort_brake(Safe 0.9배), SpeedTFFactor/myTFollowFactor/decel boost 경로, 디바이스에서 사용자가 바꾼 파라미터는 미측정.
- 세부 표와 공식, 업스트림 줄 번호, 스크래치 실험은 WIP.md 197cha 참고. Plant A/B 통제 실험, 넓은 회귀 파일별 집계, following_distance 18건 표(스톡 T 기대)는 WIP.md 196cha 참고.
- 게이트를 완전 개방(g=1)으로 고정한 스텁이라 preview_release/cutout 테스트는 147차 게이트 동작을 검증하지 않음(193차에서 이월).
- xiaoge_vision 22건과 ImportError 수집 에러 9건의 원인은 192cha 분류 유지, 미재확인. test_latcontrol_torque_buffer의 ImportError(LAT_ACCEL_REQUEST_BUFFER_SECONDS 없음)는 환경이 아니라 코드/테스트 불일치처럼 보이나 192cha 분류와 대조하지 않았다.

주의사항:
- 시작 전에 WIP.md 197cha 회차(원인, 공식, 표), 필요하면 196cha(T_FOLLOW 매핑, 18건 표), 195cha, 193cha 계속 회차도 읽을 것.
- Plant.__init__은 Params()에 params_keys.h 기본값을 put한다(값이 없는 키만). pytest 안에서는 conftest의 OpenpilotPrefix로 격리되지만, pytest 밖에서 Plant를 돌리면 기본 Params 경로(Path.home()/.comma/params/d, 디바이스는 /data/params/d)에 실제로 쓴다. pytest 밖에서 돌릴 때는 `with OpenpilotPrefix():`(openpilot.common.prefix)로 감쌀 것: msgq 경로(안 감싸면 IpcError: Messaging failure with radarState)와 Params가 함께 격리된다.
- pytest 실행 옵션: pyproject.toml addopts에 `-n auto --dist=loadgroup`이 있으므로 `-p no:xdist`는 쓰지 말 것(사용법 오류로 종료). xdist는 `-n 0`으로 끄고 병렬은 `-n 4`. 요약 줄을 grep으로 걸러 볼 때 결과가 비면 tail로 에러부터 확인할 것(197cha에서 옵션 오류가 grep에 가려져 2회 헛실행).
- 소요 시간: 환경 구성 1분 남짓(백그라운드), following_distance 18건 약 53초(-n 4), 프로브 1회(v 하나, 3 personality) 약 8초.
- 전역 git user.email은 ryujmin97@gmail.com(사용자 확인, f075028f와 b788ac1에 반영 확인). 기존 커밋 99754dc8/82ed7712 등의 author는 자리표시자이고 6ee1ce7b만 깨진 문자열(기능 영향 없음, --force 금지라 그대로). 스크립트는 전역 값이 ASCII 이메일 형식이 아니거나 미설정이면 ryujmin97@users.noreply.github.com으로 폴백한다(미설정이어도 죽지 않는 ((@(& git config --global user.email) -join "")).Trim() 형태 사용, toolkit 템플릿에는 아직 미반영).
- carrot-ryu에는 openpilot/common/stopping_params.py와 openpilot/common/display_scheduling.py가 없다(VEgoStopping은 get_float * 0.01 직접 사용, 최소값 1). carrot-ms 후속 커밋이 get_stopping_speed나 DisplayScheduler에 의존하면 이 차이를 먼저 확인할 것. carrot-ryu는 .gitattributes가 LFS 설정이고 driving_supercombo.onnx/updater/lane.onnx는 LFS 포인터다. 노트 브랜치(carrot-ryu-note)에는 .gitattributes가 없다(단 FINDINGS.md는 LF/CRLF 혼재라 `* text eol=crlf` 같은 강제 정규화 조건에서는 devnotes 스크립트의 "변경 파일 2개" 검사가 안전 중단한다).
- pytest 재실행은 toolkit/pytest_ci_setup.sh부터(세션마다 파일시스템 초기화). 백그라운드 실행은 setsid nohup ... < /dev/null 로 분리해야 컴파일 중 조용히 죽지 않는다. 이 스크립트는 pytest-mock을 설치하지 않는다(필요하면 pip install pytest-mock를 샌드박스에서 별도로).
- api.github.com은 rate limit이 자주 걸린다. git ls-remote / blobless bare clone / raw(SHA 고정)로 대체할 것. pwsh 설치 버전 조회도 curl -sIL https://github.com/PowerShell/PowerShell/releases/latest 의 Location 헤더 방식이 이번에도 rate limit 없이 동작(v7.6.6). carrot-ms 원본 raw 경로는 `openpilot/selfdrive/...` 접두가 붙는다(`selfdrive/...`만 쓰면 404).
- 다음 코드 변경 세션은 5절 순차 전달(코드 스크립트 먼저 -> 확인 -> devnotes)을 따른다.

다음 작업:
1. 미완료 1(following_distance 처리 방침)을 사용자에게 확인. 코드 변경이면 테스트 파일만 바꾸는 최소 변경으로, 값을 하드코딩하지 않고 CarrotPlanner/Params에서 읽는 방식을 먼저 검토한 뒤 5절 순차 전달.
2. 남은 12건 분류(미완료 4)는 1과 독립적으로 가능.
3. 또는 이월 항목(실차 검증들), carrot-ms 점검(체크포인트 4445c29 이후 신규 커밋부터), (b')/(c)/(v) 중 사용자 선택.
