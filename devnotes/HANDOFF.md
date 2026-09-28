Worker: Claude (199cha 세션, Claude Sonnet 5). 198cha 이후 같은 흐름의 새 세션. 사용자가 붙여준 직전 세션 채팅 기록(남은 12건 분류, devnotes 기록 전에 끊김)을 재현 없이 devnotes에만 기록(devnotes 1회 push, 코드 변경 없음).
Date: 2026-09-28
Repository: ryujmin97/openpilot
Code Branch: carrot-ryu (base commit df0da457b3bc527a994cb77fae50126567ee3b3f = 198cha test_following_distance 기대값 교체 커밋, 테스트 전용. 199cha에서 코드 변경 없음.)
Note Branch: carrot-ryu-note (base commit 3fdfeae72bc076f03ccb3760caf093453475c4bb = 198cha devnotes. 199cha devnotes는 이 커밋 위에 push.)
carrot-ms 마지막 검토 체크포인트: 735a9a4 -> 4445c29 (194cha 판정 완료, 195cha~199cha에서는 점검하지 않음. 다음 점검은 4445c29 이후 신규 커밋부터.)

작업:
1. 4절 0단계(지침 문서 v2를 브랜치 URL과 SHA 고정 URL 양쪽으로 조회, 50696 바이트 동일) + HANDOFF.md/WIP.md 최상단 조회.
2. GitHub 상태 재확인(16절): ls-remote로 carrot-ryu df0da457, carrot-ryu-note 3fdfeae 확인. 직전 채팅 기록의 분류 결과가 저장소에 없음을 확인.
3. 그 분류 결과(test_cruise_speed 8건, test_longitudinal 서브테스트 7건, ACC forceDecel 무시)를 WIP.md 199cha에 기록. 사용자가 선택한 방식은 "재현 없이 지난 세션 기록만 근거". 샌드박스 재실행과 코드 재조회는 하지 않았다.
4. WIP.md 199cha 회차, 이 HANDOFF.md 갱신(devnotes 1회 push). WIP_SYNC.md 변경 없음.

완료:
1. 198cha까지의 코드/devnotes 반영 상태 확인(코드 df0da457, devnotes 3fdfeae).
2. 남은 12건 분류 결과를 devnotes에 기록(채팅 기록 기반, 이 세션 미재현). 핵심 요약:
   - test_cruise_speed 8건: speed=35 조합 전부. 원인은 CruiseEcoControl 기본값 2(설정속도 +2 km/h, 35 m/s -> 약 35.556 m/s). 기록상 eco=0 스크래치에서 16건 통과. 테스트 기대(스톡)와 carrot 기본값의 불일치로 기록됨.
   - test_longitudinal 서브테스트 7건: ACC force_decel 무시 2, allow_throttle 3(업스트림이 스톡 기능을 꺼둠), resume from a stop 1, cut-in(force_decel) 1과 cruising while disabled(e2e, force_decel) 1(원인 미확정).
   - 기록상 가장 중요: long_mpc.py 468행이 ACC에서 플래너의 v_cruise를 버려 force_decel의 v_cruise=0.0이 사라짐(업스트림 carrot-ms 097826b에도 같은 줄). 코드 변경은 없음.
3. 실차 검증: 미실시(12절). 코드/테스트 변경 없음.

미완료:
1. (사용자 결정 대기, 기록 수치는 미재현) 남은 12건 처리 방침: (a) test_cruise_speed에 eco=0을 넣고 allow_throttle 테스트는 알려진 차이로 처리하는 테스트 전용 수정, (b) ACC forceDecel 무시(long_mpc.py 468행) 코드 수정 검토(안전 관련 동작이라 별도 세션과 명시적 승인 필요, 10절), (c) 무엇이든 바꾸기 전에 기록 수치를 샌드박스에서 재현.
2. 원인 미확정: cut-in(force_decel) 1건, cruising while disabled(e2e, force_decel) 1건, resume from a stop의 출발 지연, eco가 +2 지점으로 수렴하는 이유(종료 조건이 코드에 있는데도).
3. (판단만, 코드 변경 없음) comfort_brake 2.4와 정지등가 항 상수 2.5 불일치를 의도로 볼지. 실주행 영향: 60 km/h 약 +2.3 m, 100 km/h 약 +6.4 m, 35 m/s +10.2 m(계산, 실차 미검증), stop_distance -0.5 m. 198cha의 기대값은 플래너 실제 값을 따르므로 이 불일치를 테스트가 검출하지 않는다. 필요하면 실차에서 정상상태 추종 거리를 로그로 확인하는 항목으로 이월.
4. v=0 정상상태 gap이 desired(5.502)보다 약 1.06 m 작은 현상(4.43~4.48) 원인 미조사. 정지 제어 쪽 별개 요인으로 추정, 테스트는 통과.
5. carrot/server/tests 7건 원인 확인(6건 aiohttp NotAppKeyWarning 에러 취급 -- 샌드박스 aiohttp 버전 문제일 수 있으나 프로젝트 핀 미조회, 1건 test_web_upload.py:215 소스 문자열 단언), 기준선 실행 범위 포함 여부 미확인. 넓은 회귀 현재 수치도 미확인(198cha와 같음).
6. (b') dashcam_replay 1건 원인 확정(코드/테스트 중 어느 쪽이 나중에 바뀌었는지), (c) pytest_ci_setup.sh에 pytest-mock 추가(toolkit 변경이라 승인 필요; pytest-mock이 없으면 plannerd_clock 계열이 errors로 나옴(193cha 계속 기록: 54건)), (v) 197cha 측정 스크립트(Plant 서브클래스 프로브)를 toolkit에 넣을지(승인 필요; 198cha 테스트의 RecordingPlant와 같은 아이디어라 재사용 가능성을 함께 검토).
7. (이월) 핵심 발견 68 실차 검증, 163차 게이트 실주행 검증, xTurn=6 로그 확보, 102ms wide-camera BOOT_TS gap(진단 WARN 로그 대기).
8. (이월) 110차 GATE_M 0.8/1.0, 114차 MAP_TURN_GUIDE_FACTOR=1.00 실차 검증.
9. (이월) f992f9c LFS 전환 재검토: 디바이스에서 LFS pull 실패나 계정 LFS 한도 문제가 확인되면 별도 코드 세션 + 사용자 승인으로 판단.

검증:
- 이 세션은 테스트를 실행하지 않았다. 남은 12건 분류의 모든 수치(eco 측정값, 16 passed 13.15s, force_decel 25.555/7.87/0.73 m/s, 서브테스트 7건에서 5건 등)는 직전 채팅 기록의 인용이며 이 세션에서 재현·재조회하지 않았다. 실차 검증: 미실시(12절).
- 198cha에서 재현한 following_distance 18 passed(HEAD df0da457)는 그대로 유효하다(코드 변경 없음). 넓은 회귀는 재집계하지 않았다.
- 게이트를 완전 개방(g=1)으로 고정한 스텁이라 preview_release/cutout 테스트는 147차 게이트 동작을 검증하지 않음(193차에서 이월). e2e 모드의 T 결정 경로, 주행 모드별 comfort_brake(Safe 0.9배), SpeedTFFactor/myTFollowFactor/decel boost 경로, 디바이스에서 사용자가 바꾼 파라미터는 미측정.
- 세부는 WIP.md 199cha(분류 결과와 한계), 198cha, 197cha 참고.

주의사항:
- 199cha 분류 수치(eco=2/eco=0 측정, force_decel 스크래치 실험)는 재현되지 않은 채팅 기록 기반이다. 이 값을 근거로 코드/테스트를 바꾸기 전에 샌드박스에서 먼저 재현할 것(toolkit/pytest_ci_setup.sh부터). force_decel(ACC에서 v_cruise 덮어쓰기)은 안전 관련 동작이므로 코드 수정은 별도 세션 + 명시적 승인.
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
1. 사용자가 선택: (a) 테스트 전용 수정(test_cruise_speed eco=0, allow_throttle 알려진 차이 처리), (b) ACC forceDecel 코드 수정 검토(승인 필요), (c) 분류 수치 샌드박스 재현, (d) carrot-ms 점검(체크포인트 4445c29 이후 신규 커밋부터), (e) comfort_brake 2.4 vs 2.5 의도 판단, (f) 이월 항목(실차 검증들), (g) (b')/(c)/(v).
2. 코드 변경이 나오면 5절 순차 전달(코드 스크립트 먼저 -> 확인 -> devnotes 1회).
