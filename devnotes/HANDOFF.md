Worker: Claude (199cha 계속2 세션, Claude Sonnet 5). 사용자가 HANDOFF 다음 작업 (a)를 선택해 plant.py가 vEgoCluster를 발행하도록 하는 테스트 전용 코드 변경(carrot-ryu bef8edf)을 5절 순차 전달로 반영하고 GitHub에서 재확인한 뒤, 이 devnotes(WIP.md 199cha 계속2 + 이 HANDOFF.md)를 기록했다.
Date: 2026-09-28
Repository: ryujmin97/openpilot
Code Branch: carrot-ryu (base commit bef8edfcc8f113c7e0e534b2904352d2a5331f2f = 199cha plant.py vEgoCluster 발행 커밋, 테스트 전용, 부모 df0da457. 이 세션의 코드 변경은 이것 하나.)
Note Branch: carrot-ryu-note (base commit 04f9790ad20e129aef93c38b48d9d6f0c591ebfb = 199cha 계속 devnotes. 199cha 계속2 devnotes는 이 커밋 위에 push.)
carrot-ms 마지막 검토 체크포인트: 735a9a4 -> 4445c29 (194cha 판정 완료, 195cha~199cha에서는 점검하지 않음. 다음 점검은 4445c29 이후 신규 커밋부터.)

작업:
1. 4절 0단계: 지침 문서 v2를 브랜치 URL과 SHA 고정 URL(04f9790)로 조회, cmp 일치(50696 바이트).
2. 코드 반영 스크립트(199cha_code_plant_vegocluster_v1.ps1)를 사용자가 실행해 carrot-ryu bef8edf push. 이 세션에서 GitHub를 직접 재확인(git ls-remote, blobless bare clone의 git log/show --numstat/ls-tree/diff; api.github.com은 rate limit으로 실패).
3. WIP.md 199cha 계속2 회차와 이 HANDOFF.md 갱신(devnotes push). WIP_SYNC.md 변경 없음.

완료:
1. plant.py에 `car_state.carState.vEgoCluster = float(self.speed)`와 주석 1줄 추가(+2/-0, blob 824098d -> f238ce1, mode 100755 유지). 테스트 하네스만 바뀌고 실행 코드 변경 없음. 커밋 bef8edf의 부모는 df0da457, author ryujmin97 <ryujmin97@gmail.com>.
2. 샌드박스 측정(코드 스크립트 작성 시 실행, 이번 확인 단계에서는 재실행하지 않음): test_cruise_speed 8 failed/13 passed -> 21 passed, test_following_distance 18 passed(변화 없음), test_longitudinal 서브테스트 실패 7건(변화 없음, 이 수정과 무관). 이 Plant를 쓰는 테스트는 이 3개 파일뿐.
3. 남은 12건 분류 중 test_cruise_speed 8건 해소. 남은 것은 test_longitudinal 서브테스트 7건(미완료 1번 참고).
4. 실차 검증: 미실시(12절).

미완료:
1. (사용자 결정 대기) test_longitudinal 서브테스트 7건 처리 방침: ACC forceDecel 무시로 설명된 2건(순항 disabled ACC, allow_throttle ACC force_decel)은 long_mpc.py 468행 코드 수정 검토(안전 관련 동작이라 별도 세션과 명시적 승인 필요, 10절; 실주행 controlsd 경로 영향 확인 필요). ACC cut-in + force_decel 1건은 그 패치 후에도 20 s 종료 시점 speed 0.12/a=-0.029로 판정 여유 차이. allow_throttle force_decel=False 2건과 resume from a stop 1건은 알려진 차이/추가 조사.
2. 원인 미확정: e2e 순항 disabled + force_decel(reset_state 가설), ACC cut-in + force_decel의 20 s 판정 여유, resume from a stop의 출발 지연(t=10.15 s 리드 출발 후 a=-0.0066이 3스텝, t=12.6 s에 a=0.273; 199cha 채팅 기록, 재조사 안 함).
3. (판단만, 코드 변경 없음) comfort_brake 2.4와 정지등가 항 상수 2.5 불일치를 의도로 볼지. 실주행 영향: 60 km/h 약 +2.3 m, 100 km/h 약 +6.4 m, 35 m/s +10.2 m(계산, 실차 미검증), stop_distance -0.5 m. 198cha의 기대값은 플래너 실제 값을 따르므로 이 불일치를 테스트가 검출하지 않는다. 필요하면 실차에서 정상상태 추종 거리를 로그로 확인하는 항목으로 이월.
4. v=0 정상상태 gap이 desired(5.502)보다 약 1.06 m 작은 현상(4.43~4.48) 원인 미조사. 정지 제어 쪽 별개 요인으로 추정, 테스트는 통과.
5. carrot/server/tests 7건 원인 확인(6건 aiohttp NotAppKeyWarning 에러 취급 -- 샌드박스 aiohttp 버전 문제일 수 있으나 프로젝트 핀 미조회, 1건 test_web_upload.py:215 소스 문자열 단언), 기준선 실행 범위 포함 여부 미확인. 넓은 회귀 현재 수치도 미확인(198cha와 같음).
6. (b') dashcam_replay 1건 원인 확정(코드/테스트 중 어느 쪽이 나중에 바뀌었는지), (c) pytest_ci_setup.sh에 pytest-mock 추가(toolkit 변경이라 승인 필요; pytest-mock이 없으면 plannerd_clock 계열이 errors로 나옴(193cha 계속 기록: 54건)), (v) 197cha 측정 스크립트(Plant 서브클래스 프로브)를 toolkit에 넣을지(승인 필요; 198cha 테스트의 RecordingPlant와 같은 아이디어라 재사용 가능성을 함께 검토).
7. (이월) 핵심 발견 68 실차 검증, 163차 게이트 실주행 검증, xTurn=6 로그 확보, 102ms wide-camera BOOT_TS gap(진단 WARN 로그 대기).
8. (이월) 110차 GATE_M 0.8/1.0, 114차 MAP_TURN_GUIDE_FACTOR=1.00 실차 검증.
9. (이월) f992f9c LFS 전환 재검토: 디바이스에서 LFS pull 실패나 계정 LFS 한도 문제가 확인되면 별도 코드 세션 + 사용자 승인으로 판단.

검증:
- 이번 회차의 테스트 수치는 샌드박스(Ubuntu 24, Python 3.12) 값이다(코드 스크립트 작성 시 측정). 사용자 PC(Windows)에서 pytest는 돌리지 않았고 GitHub 재확인은 코드 diff/blob/부모 기준이다. 실차 검증: 미실시(12절).
- 직전 회차(199cha 계속)의 재현 수치와 한계(게이트 완전 개방 스텁, e2e T 결정 경로, 주행 모드별 comfort_brake, 사용자 파라미터 미측정 등)는 그대로 유효하다. 넓은 회귀 재집계는 하지 않았다.
- 세부는 WIP.md 199cha 계속2, 199cha 계속, 199cha, 198cha 참고.

주의사항:
- 199cha 계속의 재현 수치는 샌드박스 하네스 값이다(toolkit/pytest_ci_setup.sh로 구성, 정확한 수치는 -n 0). 재현 스크래치는 untracked 임시 테스트 파일로 만들고, 저장소 파일을 임시로 고친 뒤에는 반드시 `git checkout <파일>`로 되돌린 다음 `git status`로 확인할 것(`openpilot/cereal/gen/`는 환경 구성 산출물). 코드 변경(특히 force_decel, long_mpc.py 468행)은 별도 승인이 필요하다(10절).
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
1. 사용자가 선택: (b) ACC forceDecel 코드 수정 검토(승인 필요), (c) 미확정 원인 조사(e2e disabled force_decel, resume from a stop, allow_throttle force_decel=False 2건), (d) carrot-ms 점검(체크포인트 4445c29 이후 신규 커밋부터), (e) comfort_brake 2.4 vs 2.5 의도 판단, (f) 이월 항목(실차 검증들), (g) (b')/(c)/(v).
2. 코드 변경이 나오면 5절 순차 전달(코드 스크립트 먼저 -> 확인 -> devnotes 1회).
