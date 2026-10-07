Worker: Claude (262cha, Claude Sonnet 5.5). 코드 변경 없음, devnotes만 다룬 세션. 사용자가 "Carrot-ms 분석"을 요청해 2절 절차로 carrot-ms 0a67f68 이후 신규 8건을 점검했고, 판정안(제외 8건, 반영 후보 0건)을 "제외승인 기록"으로 확정했다.
Date: 2026-10-07
Repository: ryujmin97/openpilot
Code Branch: carrot-ryu (base commit 1326f21149cf99a890c95adf5e599bbdf16177da = 259cha 시점 HEAD, 비전 앞차 해제 대역 1.5 m + 3프레임 홀드, 부모 670f72c, 이 세션이 `git ls-remote`로 HEAD가 그대로임을 확인했다. 이 세션은 코드를 바꾸지 않았다).
Note Branch: carrot-ryu-note (base commit 966319e5ddbd6a3a450f33497432762de2920839 = 261cha devnotes(HANDOFF 슬림화), 이 세션이 `git ls-remote`로 확인했다. 이 세션의 devnotes 1회 push(262cha)가 그 위에 올라간다).
Archive Branches: carrot-ryu-v1 (6df4268eb31442be4d8abd92817111f7b26b1bf4, 불변), carrot-ryu-v2 (3ddf849ea3f3392c16d363d9edea6a1bc8eab041, 212cha 생성, 불변). 둘 다 이 세션의 `git ls-remote`로 SHA 일치를 확인했다. carrot-ryu-v3는 아직 없고 보존 시점은 사용자가 정한다(20절).
carrot-ms 마지막 검토 체크포인트: 0a67f68 -> 9fe7fa5 (262차: 신규 8건 8b65fb9, a85912d, b4b2ded, 679e633, b72237d, 30ee43d, 22af6b2, 9fe7fa5를 모두 제외로 확정, carrot-ryu 반영 없음, 사유는 WIP_SYNC.md 262차). 다음 점검은 9fe7fa5 이후 신규 커밋이 생겼을 때이며 `git cat-file -t 9fe7fa5`로 존재부터 확인한다(carrot-ms는 재생성되므로).

이 파일은 8절대로 "최신 1개 버전만" 유지한다. 201cha~260cha의 작업/완료/미완료/검증/주의사항/다음 작업 전체 이력은 커밋 f58764b의 같은 경로에 그대로 있다: `git show f58764bd94f0e7fdc5b0c9e9f2028a85726894fa:devnotes/HANDOFF.md` 또는 SHA 고정 raw URL(https://raw.githubusercontent.com/ryujmin97/openpilot/f58764bd94f0e7fdc5b0c9e9f2028a85726894fa/devnotes/HANDOFF.md). 회차별 상세는 원래 WIP.md(불변)가 갖고 있으므로 여기에 다시 쌓지 않는다. 아래 "미완료/주의사항"은 이전 HANDOFF에서 옮긴 것이며 이 세션이 내용을 재검증하지는 않았다(번호는 이전 HANDOFF의 미완료 번호로, 상세가 필요하면 위 커밋에서 해당 번호를 읽는다).

작업(262cha, 이 구간):
1. 4절 0단계: 지침 문서 v2를 브랜치 URL로 받아 읽고 `git ls-remote`(note 966319e, carrot-ryu 1326f21)와 SHA 고정본 비교로 두 사본이 바이트 동일(49,277바이트)함을 확인했다. 이어서 HANDOFF.md를 SHA 고정으로 읽었다.
2. carrot-ms(happymaj11r) HEAD 9fe7fa5. 체크포인트 0a67f68이 commit이고 HEAD의 조상임을 확인했다(rebase 없음). `0a67f68..HEAD` 8건 전부 ajouatom(2026-10-06~07), Jetson/Jetlink 계열이다. 8건 전체 `--numstat`과 비 Jetlink 파일 diff(`hud_renderer.py` 2개, `hardwared.py`, `params_keys.h`, `alerts_offroad.json`, `jetlink_status.py`)를 읽었고, carrot-ryu 1326f21의 파일 5,449개 중 jetlink/jetson 경로는 0개였다.
3. 판정안(제외 8건, 반영 후보 0건)을 사용자가 "제외승인 기록"으로 확정했다. WIP_SYNC.md 262차와 WIP.md 262cha 항목을 추가하고 이 파일을 갱신하는 devnotes 스크립트 1개(`262cha_ms_sync_record.sh`, Termux bash)만 쓴다(코드 변경 없음, 5절 devnotes 1회 push).

완료(최근 구간, 상세는 WIP.md):
- 262cha: carrot-ms 0a67f68..9fe7fa5 신규 8건(Jetson/Jetlink 계열)을 모두 제외로 확정, carrot-ryu 반영 없음(정적 확인, 실차 검증 미실시). 261cha: HANDOFF.md를 8절의 최신 1개 버전으로 슬림화(코드 변경 없음).
- 260cha: 1326f21 규칙이 크루즈 작동 중 새로 만드는 프레임 측정(route 478 세그먼트 1~10, 8,309프레임에서 새 present 0개)과 끊김 유지(G) 대 채움(A) 플래너 시뮬레이션(route 492-4). 재생/시뮬레이션만이며 실차 검증은 미실시.
- 259cha: 1326f21 재검증(route 492 세그먼트 4에서 끊김 10 -> 0, pytest 447 passed).
- 이전 구간의 반영 커밋 요약(carrot-ryu): 1326f21(비전 앞차 해제 대역 1.5 m + 3프레임 홀드), 670f72c(carrot-ms 47d35da 간격 헤드룸 유지 거리 대역), `J_EGO_COST` 12.0 반영(246cha, 두 테스트의 하드코딩 보정은 0a1ad62), f9ffbc2(`JerkCostEgo` 설정, 코드 기본 12, 상한 20), b3e16c5(SCC 모드 -1 비전 앞차 허용, 기기값 0이라 현재 비작동), 11d7e89/0f08f08/76b182a(UI 네이티브 배치와 plot 경량화), 8cdb515(SCC 앞차 비전 거리 완화), 99012c3(disabled+blended force_decel 미감속 수정).

미완료(번호는 이전 HANDOFF 기준, 실차 항목은 모두 "실차 검증: 미실시"):
- 48번 (a) 실기기에서 1326f21의 비전 단독 앞차 장면 확인. (b) 옆 차선 오감속 빈도는 이 로그로 판정 불가: 크루즈 작동 중 비전 단독 앞차가 1.0~1.5 m 경계에 걸리는 장면(옆 차선에 차가 많은 도로) 로그가 필요. (c) G가 A보다 과대하게 나온 원인은 미규명(끊김 뒤 실제 플래너의 lead 유지 로직 읽기, 채운 프레임에 비전 원시값 넣어 `jerk_sim/run_gap.py` 재실행은 선택지).
- 45번, 47번 (a) `JerkCostEgo` 20(기기 설정값) 유지/12/8 결정은 미결정. 256cha 시뮬레이션에서 J=20은 FCW의 주원인은 아니지만 감속을 늦추는 증폭 요인이었다. 20이 의도한 값인지도 알 수 없다.
- 46번 (a), 255cha 정지 앞차 근처 풀림: 크루즈 활성 상태에서 앞차가 정지하는 장면 로그가 없어 검증 불가(기록 커밋 670f72c 이상 필요). 47번 (b): 차량 SCC 레이더가 정차 버스를 경고 시점까지 보고하지 않은 이유는 로그로 알 수 없음(`EnableRadarTracks` 0 대 -1과는 무관함은 257cha에 확인).
- 44번 `test_leads.py::test_radar_fault` 실패: 원인은 `openpilot/selfdrive/test/process_replay/migration.py` 306행의 옛 이름 `CANFD_LKA_STEER_MSG`(carrot-ms는 `CANFD_LKA_STEERING`). 알려진 실패로 두거나 한 줄 수정 코드 세션(승인 필요), 수정 미결정.
- 22~28번 고속 앞차 추종/램프: 8cdb515 실차 확인(급감 사라졌는지, 끼어들기 반응 지연 없는지), SCC<->비전 전환 후속(8 m 규칙은 대부분 비전이 옳았음, 거리 비례 완화안은 표본 부족으로 승인 전), 진출 램프 600 m와 유지 300 m 실차 확인, 진입 램프 조건은 미해결(내비를 켠 채 진입/진출 램프를 지나는 rlog 필요).
- 실차 확인 이월: 3번 comfort_brake 2.5 통일 뒤 정상상태 추종 거리와 승차감, 4번 v=0 정상상태 gap이 desired보다 약 1.06 m 작은 현상(재주행 로그의 정지 장면에서 간격만 확인), 10번 948b139 이식(held_stopping_front), 13번 202cha(v_cruise=0일 때 ACC 감속 반영), 15번 (a), 7번 핵심 발견 68 실차 검증/163차 게이트/xTurn=6 로그/102ms wide-camera BOOT_TS gap, 8번 110차 GATE_M 0.8/1.0과 114차 MAP_TURN_GUIDE_FACTOR=1.00.
- 29, 33~41번 UI 프레임 저하와 네이티브 UI: 이 기기의 fps 저하는 원래 수준일 가능성이 크다는 비교(227cha 계속2)까지만 했다. 남은 것은 76b182a 효과 확인(35번), 기기 `_draw_native*.so` 빌드 근거(241cha: `.so` 존재까지 확인, scons 빌드 로그와 ARM 빌드 성공 자체의 증거는 없음, 38번), 11d7e89 검증 공백(40번 (a)(c)(d)), plot 모드를 고정한 같은 조건 로그로 네이티브 효과 비교(41번 (b)). 상세는 이전 HANDOFF의 해당 번호.
- 30번 b3e16c5(SCC 모드 -1 비전 앞차 허용): 기기 `EnableRadarTracks`는 0이고 사용자가 0으로 계속 쓸 예정이라 보류. -1로 바꿀 때만 -1 실주행 로그 확인.
- 9번 f992f9c LFS 전환 재검토(디바이스 LFS pull 실패나 계정 한도 문제가 확인될 때만), 12번 4770067(부팅 실패 자동 Git 복구) 보류(사용자가 원할 때만), 19번 carrot-ryu-v3 보존 시점은 사용자가 정한다.
- 42, 43번 `J_EGO_COST` 12.0 반영 뒤 실차 로그로 앞차 감속 거동 확인(새 로그 zip 필요).

종결(재조사 불필요, 근거는 WIP.md 해당 회차): 1, 2번(test_longitudinal 서브테스트 실패, 226cha 사용자 승인으로 조사 없이 종결), 5번(carrot/server/tests 7건, 코드 변경 없이 종결 유지), 16~18번(HUD 위치 확인, DATE_TIME_X_SHIFT 110 현행 유지), 19번 옛 재생성 방침(폐지), DM2 계열 제외 확정(217cha), 카메라 접근 정책 "표시속도 기준 유지"(244cha 사용자 결정, 바꾸려면 새 결정과 안전성 검토와 승인), a2139b7 제외(CAN-FD 차량을 다루게 되면 재검토).

검증:
- 이 세션 검증: 이전 HANDOFF.md 구조 분석(작업 블록 68개, 줄/글자 수), `git ls-remote`로 브랜치 SHA 4개, note HEAD f58764b의 부모/작성자/시각/numstat. 코드 변경이 없으므로 pytest나 실차 검증은 해당 없음.
- 위 "미완료/주의사항"의 이전 세션 서술은 옮긴 것이며 이 세션이 다시 확인하지 않았다. 실차 검증은 이 구간 전체에서 미실시다.

주의사항:
- 샌드박스(bash_tool): `cut -c`는 바이트 단위라 한글 줄을 자르면 도구 출력 전체가 사라지니 파이썬 슬라이스를 쓴다. `sh`는 dash라 `<( )`와 `$'\r'`이 안 되니 bash 스크립트로 실행하고 CR 개수는 `tr -cd '\r' | wc -c`로 센다. 한 명령은 300초 제한이라 pytest나 큰 clone은 `setsid nohup ... < /dev/null &`로 분리한다. `pkill -f "git clone"`은 자기 셸까지 죽이니 쓰지 않는다.
- `toolkit/pytest_ci_setup.sh`는 `/home/claude/repo`를 지우고 carrot-ryu 최신으로 새로 만든다(약 100초~5분). 돌린 뒤 `git rev-parse HEAD`가 기록 커밋과 같은지 먼저 확인한다. pytest는 `-n 0`(xdist 끔) 또는 `-n 4`, `-p no:xdist`는 쓰지 않는다, 기준선 비교에 `-x`를 쓰지 않는다. 저장소 파일을 임시로 고쳤으면 `git checkout`으로 되돌리고 `git status`로 확인한다.
- api.github.com은 rate limit이 자주 걸린다(이 세션도 걸림). `git ls-remote`, blobless clone, SHA 고정 raw로 대체한다. pwsh 버전은 `curl -sIL https://github.com/PowerShell/PowerShell/releases/latest`의 Location 헤더로 얻는다(이번에 v7.6.6).
- 로그 분석: 각 세그먼트 rlog 맨 앞 initData는 logMonoTime이 route 시작 시각이라 t0로 쓰면 안 된다(약 540초 어긋남). `log.capnp`는 `/car.capnp`를 import하니 pycapnp imports에 `opendbc_repo/opendbc/car`를 넣는다. `runtimeTiming`은 logMessage 안 JSON 문자열이다. carrotMan의 desiredSpeed/xSpdLimit와 cruiseTarget은 표시(클러스터) 속도 기준이고 carState.vEgo는 실속도라 vCluRatio(약 0.93)만큼 다르니 같은 기준끼리 비교한다.
- 파일 수정 시각만으로 최신성을 판단하지 않는다(내용은 `grep -c` 등으로 직접 확인). 붙여넣어진 확인 결과 글의 수치는 틀릴 수 있으니 기록 전에 GitHub에서 같은 값을 다시 얻는다(3절).
- carrot-ryu 고유 차이(carrot-ms 동기화 시 먼저 대조): `long_mpc.py` 43행 `J_EGO_COST = 12.0`은 upstream 06639e5의 20과 다른 의도된 값이다(시뮬레이터 근거뿐, 실차 검증 없음). `set_weights`에 `j_ego_cost` 인자(5~20 clip)가 있다. `application.py`에 54cha 일회성 캡처(`_temp_capture_*`)가 있다. `lateral_planner.py` blob 8f800a4가 53d88ef판과 `deque` import 한 줄만 다르다. carrot-ryu에는 dm2/dm2d/dm2_context, tools/jetlink와 jetlink_status, startup_recovery, hyundai steering_touch/steering_handover, openpilot/common/reboot.py, impact_dashcam/impact_detector, stopping_params, display_scheduling, lane_model_speed가 없다. 후속 carrot-ms 커밋이 이들에 의존하면 먼저 이 차이를 본다.
- HUD 그리는 곳: 하단 좌측 브랜치/모델 문구는 우측 상단(CPU 글자 아래)에 `ui/onroad/augmented_road_view.py`의 `_draw_border_carrot`로 그린다. `HudRenderer._hud_top_right`는 `_draw_set_speed_carrot`가 매 프레임 설정하니 `_draw_carrot_speed_panel`/`_draw_carrot_device_state` 호출 순서를 바꾸기 전에 확인한다.
- 스크립트 작성: PowerShell 래퍼 함수를 `Git`처럼 명령과 대소문자만 다른 이름으로 만들면 무한 재귀로 죽는다(`Invoke-G`/`Invoke-Git`을 쓴다). 스크립트 안 `python -m py_compile`은 저장소 안에 `__pycache__`를 만들어 `git add -A`에 섞이니 `cfile=`을 저장소 밖으로 주고 커밋 전에 `git diff --cached --name-only`로 파일 수를 본다. 스크립트 안의 git 명령은 항상 `-C <clone 경로>`로 대상 저장소를 명시한다(9절 10번). 사용자 PC git 이메일이 기록(ryujmin97@gmail.com)과 다르게 보인 적이 있다(058391e Author ryujmin@naver.com, 기능 영향 없음, `--force` 금지).
- carrot-ryu-v1/v2는 불변이다. 여기에 새 작업이나 devnotes를 얹지 않는다. 폐지된 "carrot-ryu 재생성" 언급을 옛 기록에서 보면 무시한다(219cha).
- 코드 변경이 나오면 5절 순차 전달(코드 스크립트 먼저 -> GitHub 직접 확인 -> devnotes 1회).

다음 작업:
- 사용자가 고를 수 있는 것: (1) 1326f21의 옆 차선 오감속 판정용 로그 확보(크루즈 작동 중 비전 단독 앞차, 옆 차선에 차가 많은 도로)와 `radar_gate/release_replay.py`/`margin_scan.py` 재생(코드 변경 없음), (2) `JerkCostEgo` 20 유지/12/8 결정(CarrotWeb 설정, 코드 변경 없음), (3) 정지 앞차 접근과 내비를 켠 램프 주행 재주행 로그 확보, (4) `test_radar_fault` 처리 결정, (5) carrot-ms 9fe7fa5 이후 신규 커밋 점검, (6) carrot-ryu-v3 보존 시점 지정.
- 코드 변경이 나오면 사용자 승인 후 5절 순차 전달(코드 스크립트 먼저 -> 확인 -> devnotes 1회)을 따른다.
