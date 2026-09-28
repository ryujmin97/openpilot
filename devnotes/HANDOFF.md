Worker: Claude (205cha 세션, Claude Sonnet 5.5). 사용자가 미완료 15번 검토(blended 감속 하한 vs ACC)와 comfort_brake 2.5 통일을 지시했다. 15번은 코드 읽기와 샌드박스 프로브로 검토했고(코드 변경 없음, ACCEL_MIN 유지 권고), comfort_brake는 코드 스크립트를 작성해 사용자가 실행했으며(carrot-ryu 058391e), 5절 순서대로 GitHub 재확인 뒤 이 devnotes를 기록했다(실차 미실시). 직전 204cha 세션(Claude Sonnet 5.5)은 99012c3(blended forceDecel)을 독립 검증했다.
Date: 2026-09-29
Repository: ryujmin97/openpilot
Code Branch: carrot-ryu (base commit 058391e6a3b4a1d3ac5b2eee0e4d9a4bb2f7d044 = 205cha comfortBrake 2.4 -> 2.5 통일 커밋, 부모 99012c363cc4177e93e4b250b06bf3898ee6bba9 = 204cha blended forceDecel 수정 커밋, 그 부모 0a1a9fc5da304cef25de23eabbff678d68aa396a = 202cha ACC forceDecel 수정 커밋. 이 세션이 만든 코드 변경은 058391e 하나.)
Note Branch: carrot-ryu-note (base commit 66375ec121286b88a5e599b263a41eef57cb2133 = 204cha devnotes. 205cha devnotes는 이 커밋 위에 push.)
carrot-ms 마지막 검토 체크포인트: 4445c29 -> c771c4e (201차 판정 완료: 948b139 이식, 4770067 제외, DM2 계열 8건 보류, jetlink 12건 + a482d02 제외). 다음 점검은 c771c4e 이후 신규 커밋부터이며, 세션 시점 HEAD인 c36f6e7(Hyundai CAN-FD 조향 터치 감지)은 아직 판정하지 않았다.

작업(205cha, 이 세션):
1. 4절 0단계: 지침 문서 v2를 브랜치 URL로 읽은 뒤 note 66375ec SHA 고정본으로 재조회, 일치(변경 없음) 확인. carrot-ryu HEAD 99012c3가 HANDOFF base와 일치.
2. 미완료 15번 검토(코드 변경 없음): ACC(약 520행)와 blended(약 547행) 감속 하한 코드, autoNaviSpeedDecelRate(기본 1.2, 범위 0.5~3.0)와 ACCEL_MIN(-4.0), forceDecel/reset_state 발생 조건을 읽고, 샌드박스 프로브로 하한별(-4.0/-3.0/-1.2/-0.5) 결과를 측정. 결론: 앞차 없으면 하한이 걸리지 않아 결과가 같고, 정지한 앞차가 있으면 -1.2로 맞출 때 제동 권한을 잃으므로 ACCEL_MIN 유지를 권고(WIP.md 205cha 1번).
3. comfort_brake 2.5 통일: 코드 스크립트 205cha_code_comfort_brake_2p5_v1.ps1을 작성/사전 검증해 전달, 사용자 실행 후 carrot-ryu 058391e push를 GitHub로 재확인(WIP.md 205cha 2~3번).
4. WIP.md 205cha와 이 HANDOFF.md를 기록(devnotes push).

작업(204cha, 이전 세션 이월):
1. 4절 0단계: 지침 문서 v2를 note 80b9ce9 SHA 고정으로 조회, 브랜치 URL 본과 일치(변경 없음) 확인. carrot-ryu HEAD 99012c3가 HANDOFF base(0a1a9fc)보다 1커밋 앞선 것을 16절대로 대조.
2. carrot-ryu 99012c3(long_mpc.py, blended 모드 forceDecel, +4/-0)를 GitHub 독립 bare clone과 독립 샌드박스로 검증(numstat/blob/CR/BOM/py_compile, pytest 7개 파일 신/구 비교). WIP.md 204cha와 이 HANDOFF.md를 기록.

작업(203cha, 이전 세션 이월):
1. 4절 0단계: 지침 문서 v2를 note c5d501d SHA 고정으로 조회, 브랜치 URL 본과 일치(변경 없음) 확인.
2. 202cha 세션 샌드박스(체크아웃 0a1a9fc)를 재사용해, 남은 서브테스트 실패 5건을 Plant 직접 호출 프로브로 프레임 단위 재현. disabled+blended 1건은 reset_state 스크래치 실험(원복 확인)으로 근본 원인을 구조적으로 확정. WIP.md 203cha와 이 HANDOFF.md를 기록.

작업(202cha, 이전 세션 이월):
1. (완료) 4절 0단계: 지침 문서 v2를 note fa8bbd2 SHA 고정으로 조회, 브랜치 URL 본과 일치 확인.
2. (완료) carrot-ryu 0a1a9fc(long_mpc.py 468행, ACC forceDecel) push를 GitHub로 재확인하고, 독립 clone/샌드박스에서 diff, CR/BOM, py_compile, 종방향 관련 pytest 7개 파일 신/구 비교를 수행, WIP.md 202cha와 이 HANDOFF.md를 기록.

작업(201cha, 직전 세션 이월):
1. (완료) 4절 0단계: 지침 문서 v2를 note eb76575 SHA 고정으로 조회, 브랜치 URL 본과 일치 확인.
2. carrot-ms 4445c29..c771c4e 신규 23건의 변경 파일을 조회하고 carrot-ryu에 관련 파일이 있는지 확인해 판정(WIP_SYNC.md 201차).
3. 948b139 이식 코드 스크립트(201cha_code_radar_stopping_lead_948b139_v1.ps1)를 사용자가 실행해 carrot-ryu 69eaf32 push. 이 세션에서 GitHub를 직접 재확인(git ls-remote, 독립 clone의 git show --numstat/blob/CR/py_compile/JSON).
4. WIP.md 201cha, WIP_SYNC.md 201차 체크포인트, 이 HANDOFF.md 갱신(devnotes push).

완료:
1. (203cha) test_longitudinal 남은 서브테스트 실패 5건 원인 조사(코드 변경 없음): (a) disabled+blended(e2e=True, force_decel=True) - reset_state가 매 프레임 True로 고정돼 blended 모드에서만 force_decel 감속을 막는 것을 스크래치 실험으로 확정(강제 False 시 20 s간 25->7.87 m/s 감속, ACC 모드는 원본 그대로도 0.376 m/s까지 정지). (b) cut-in force_decel: 20 s 종료 speed=0.1208/a=-0.0283로 199cha 기록과 일치, margin이 좁아 통과하지 못함(구조적 가설). (c) resume from a stop: t=10.15~10.25 3프레임(0.15초) 동안 a가 -0.0066~-0.0015로 남아있다가 t=10.30부터 양전환, t=12.6 a=0.273(199cha 기록과 일치, 지연시간 0.15초로 정량화). (d) allow_throttle force_decel=False 2건: 종료 speed 20.00/20.00으로 전혀 감속하지 않음(기존 원인 그대로, 변동 없음). 5건 모두 202cha 이후 pass/fail 변화 없음(9 failed 그대로).
2. (202cha) carrot-ryu 0a1a9fc: 비 blended(ACC) 모드에서 long_mpc.py 468행이 `min(v_cruise, carrot.v_cruise)`를 쓰도록 변경(+3/-1, 1파일). 플래너가 forceDecel 때 넘기는 v_cruise=0.0이 ACC에서도 MPC에 반영된다. 독립 검증: test_longitudinal 서브테스트 실패 7건 -> 5건(사라진 2건은 ACC 모드 force_decel 2건: cruising 25 m/s while disabled, allow_throttle=False pitch +0.1), 나머지 6개 파일 통과(전체 9 failed / 277 passed / 53 subtests passed, 이전판 기준선은 test_longitudinal만 11 failed / 51 subtests passed). 안전 관련 동작이며 실차 검증: 미실시(12절).
3. (201cha) primary.py에 held_stopping_front 추가(+23/-2), test_radar_motion_predictor.py +78(테스트 16건), cutin_validation_cases.json +15(Sonata 1건), docs/sonata_stopping_lead_continuity_20260928.md 신규 +93. 확정된 전방 레이더 리드(같은 식별자, 위치 연속, v_lead >= -1.0 m/s)를 정지까지 후보로 유지한다. 종방향 표적 선택에 영향을 준다.
4. (201cha) 업스트림과 다른 점: 14e2cfa(radar_track_state == 1 거부)가 carrot-ryu에 없어 primary.py 두 hunk를 한 블록으로 합쳤고, 업스트림 릴리스 테스트의 tentative 케이스는 이식하지 않았다. DH2015는 일반 CAN이라 상태값이 항상 0이라 실제 영향 없음.
5. (201cha) 샌드박스 측정(코드 스크립트 작성 시 실행, 이번 확인 단계에서는 재실행하지 않음): test_radar_motion_predictor.py 420 -> 436 통과, 새 테스트를 옛 코드에 적용하면 정지 유지 테스트 3건 실패, 관련 11개 파일 수정 전후 모두 4 failed / 271 passed(test_radar_lead_simulator.py 4건, 이번 변경과 무관).
6. (201cha) carrot-ms 23건 판정(WIP_SYNC.md 201차 참고): 이식 1, 제외 1(4770067), 보류 8(DM2), 제외 13(jetlink 12 + a482d02).
7. 실차 검증: 미실시(12절).
8. (204cha) carrot-ryu 99012c3: blended 모드에서 `reset_state and v_cruise == 0`이면 `self.params[:,0] = ACCEL_MIN`(long_mpc.py 약 544행, +4/-0, 1파일). 203cha가 확정한 disabled+blended forceDecel 미감속 원인의 수정이다. 독립 검증: blob f087a48 -> f4f81e2, CR 0/BOM 없음/py_compile 통과, pytest 7개 파일 신판 7 failed / 278 passed / 54 subtests passed(기준선 test_longitudinal만 9 failed / 53 subtests passed). 신/구 차이는 `cruising at 25 m/s while disabled`(e2e=True, force_decel=True) 서브테스트와 그 부모 1건이 사라진 것뿐, 나머지 6개 파일 통과. 안전 관련 동작이며 실차 검증: 미실시(12절).
9. (205cha) carrot-ryu 058391e: `carrot_functions.py` 103행 CarrotPlanner `comfortBrake` 기본값 2.4 -> 2.5(+1/-1)와 테스트 픽스처 `test_longitudinal_gap_recovery.py` 64행 `comfort_brake=2.4` -> 2.5(+1/-1). long_mpc.py 상수 COMFORT_BRAKE=2.5(정지등가 항)와 같아진다. 정상상태 추종 거리의 v^2/(2*cb) 항이 줄어 60 km/h 약 -2.3 m, 100 km/h 약 -6.4 m, 35 m/s 약 -10.2 m(계산, 실차 미검증). 모드 계수(Safe 0.9 -> 2.25)와 정지 표지판 분기 min(mode, cb*0.9)(2.16 -> 2.25)도 함께 바뀐다. 테스트: 7개 파일 신/구 모두 7 failed / 278 passed / 54 subtests passed, 실패 목록 동일(모두 test_longitudinal.py). 안전 관련 동작이며 실차 검증: 미실시(12절).
10. (205cha) 미완료 15번 검토 결과(코드 변경 없음): blended 하한을 -autoNaviSpeedDecelRate로 맞추지 않고 ACCEL_MIN(-4.0)을 유지하는 것을 권고. 앞차 없음: -4.0/-3.0/-1.2 모두 min a=-0.587(하한이 걸리지 않음). 정지 앞차(25 m/s 접근, 60 m): -4.0은 정지(최소 간격 +1.47 m), -1.2는 앞차를 지나감(-90.77 m). ACC는 source == 'cruise'일 때만 그 하한을 쓰므로 조건이 다르다. 사용자가 이의를 제기하지 않으면 이 부분은 종결.

미완료:
1. test_longitudinal 서브테스트 실패 4건이 남음(204cha 기준, 203cha의 5건에서 disabled+blended가 해소됨): allow_throttle=False pitch +0.1(e2e=True와 e2e=False, force_decel=False 2건, 원인 기존과 동일), ACC cut-in + force_decel(203cha 재확인 speed=0.1208/a=-0.0283, 199cha와 일치), resume from a stop(e2e=False, 지연시간 0.15초/3프레임). 부모 포함 신판 7 failed(서브테스트 4 + 부모 3). 아래 2번 참고.
2. (204cha 갱신) e2e 순항 disabled + force_decel: 99012c3으로 수정됨(하네스에서 해당 서브테스트 통과 확인). 남은 것은 ACC cut-in + force_decel과 resume from a stop의 출발 지연으로, 둘 다 v=0 근처 가속도 스무딩과 하네스의 즉각적 급제동/양전환 요구 사이 불일치로 보인다는 가설까지만 세웠고(203cha), jerk_factor/a_change_cost 코스트 파라미터로 인과를 격리하지는 않았다.
3. (205cha 해결) comfort_brake는 2.5로 통일(058391e). 남은 것은 실차에서 정상상태 추종 거리를 로그로 확인하는 항목(60 km/h 약 2.3 m, 100 km/h 약 6.4 m 짧아짐, 계산, 실차 미검증)과 승차감/뒤차 관점 확인.
4. v=0 정상상태 gap이 desired(5.502)보다 약 1.06 m 작은 현상(4.43~4.48) 원인 미조사. 정지 제어 쪽 별개 요인으로 추정, 테스트는 통과.
5. carrot/server/tests 7건 원인 확인(6건 aiohttp NotAppKeyWarning 에러 취급 -- 샌드박스 aiohttp 버전 문제일 수 있으나 프로젝트 핀 미조회, 1건 test_web_upload.py:215 소스 문자열 단언), 기준선 실행 범위 포함 여부 미확인. 넓은 회귀 현재 수치도 미확인(198cha와 같음).
6. (b') dashcam_replay 1건 원인 확정(코드/테스트 중 어느 쪽이 나중에 바뀌었는지), (c) pytest_ci_setup.sh에 pytest-mock 추가(toolkit 변경이라 승인 필요; pytest-mock이 없으면 plannerd_clock 계열이 errors로 나옴(193cha 계속 기록: 54건)), (v) 197cha 측정 스크립트(Plant 서브클래스 프로브)를 toolkit에 넣을지(승인 필요; 198cha 테스트의 RecordingPlant와 같은 아이디어라 재사용 가능성을 함께 검토).
7. (이월) 핵심 발견 68 실차 검증, 163차 게이트 실주행 검증, xTurn=6 로그 확보, 102ms wide-camera BOOT_TS gap(진단 WARN 로그 대기).
8. (이월) 110차 GATE_M 0.8/1.0, 114차 MAP_TURN_GUIDE_FACTOR=1.00 실차 검증.
9. (이월) f992f9c LFS 전환 재검토: 디바이스에서 LFS pull 실패나 계정 LFS 한도 문제가 확인되면 별도 코드 세션 + 사용자 승인으로 판단.
10. (신규, 실차) 948b139 이식(held_stopping_front)의 실주행 확인: 정지하는 앞차(특히 정지 직전 v_lead가 0 부근이거나 약간 음수로 흔들리는 구간)를 정지까지 놓치지 않는지, 정지 후 재출발 시 표적이 정상적으로 풀리는지 로그로 확인. 확인 전까지 정적/샌드박스 단계.
11. (신규) c771c4e 이후 carrot-ms 신규 커밋 점검(세션 시점 HEAD c36f6e7부터, 미판정).
12. (신규, 보류 유지) DM2 계열 8건과 4770067(부팅 실패 자동 Git 복구)은 사용자가 원할 때만 별도 코드 세션 + 승인으로 재검토(WIP_SYNC.md 201차의 재검토 조건 참고).
13. (신규, 실차) 202cha 변경의 실주행 확인: DM alert 3 / softDisabling 등 플래너가 v_cruise=0.0을 넘기는 상황에서 ACC 모드일 때 감속 요구가 MPC와 실제 제동에 반영되는지 로그로 확인. 그 조건이 controlsd 경로에서 실제로 발생하는 경우와 carrot 쪽 vCluRatio 출처(플래너와 같은 carState.vCluRatio인지)는 202cha 세션에서 읽지 않았다. 확인 전까지 정적/샌드박스 단계.
14. (204cha 완료) disabled+blended force_decel 미감속 수정은 99012c3으로 반영됐다. 남은 것은 아래 15번의 실차/설계 확인이다.
15. (205cha 검토 완료, 실차/설계 확인만 남음) blended 하한(ACCEL_MIN -4.0)과 ACC 경로(-autoNaviSpeedDecelRate, source == 'cruise' 한정)의 차이는 코드 읽기와 프로브로 검토했고 ACCEL_MIN 유지를 권고한다(위 완료 10번, WIP.md 205cha 1번). 남은 것: (a) DM alert 3 / softDisabling에서 blended + reset_state True + v_cruise=0이 실제 발생하는지(LongControl 상태 전이와 로그, 202cha 확인 항목 13번과 같은 계열), (b) blended의 forceDecel 감속이 ACC보다 약한 점(blended 25 -> 약 8 m/s를 -0.87 m/s^2로, 정지하지 않음. ACC는 20 s 안에 거의 정지)을 의도로 볼지의 설계 판단(다음 작업 (i)). 코드 변경이 되면 안전 관련이라 별도 승인 필요(10절).

검증:
- (205cha) 코드 058391e 독립 검증(이 세션): `git ls-remote` HEAD 일치, 부모 99012c3, numstat 2파일 각 1/1, blob 2989b30 -> f7d1bfe(carrot_functions.py)와 34894be -> 1a9f682(test_longitudinal_gap_recovery.py)가 스크립트 기대값과 일치, CR 0개, py_compile 통과. pytest 7개 파일(-n 0 -p no:randomly, pytest-mock): 기준선 99012c3 7 failed / 278 passed / 54 subtests passed(108 s), 신판 같은 수치(109 s), SUBFAILED/FAILED 7줄 diff 없음. 15번 프로브: 하한 -4.0/-3.0/-1.2 앞차 없음 min a=-0.587 동일, 정지 앞차 60 m에서 -4.0 정지(+1.47 m)/-1.2 통과(-90.77 m). 코드 스크립트 사전 검증은 Linux pwsh 7.6.6 기준(파서 오류 0건, 앵커 시뮬레이션, bare 저장소 일반/CRLF 재현)이며 Windows PowerShell 5.1 실제 실행이 아니다(실제 실행은 사용자 PC, push 로그와 GitHub 재확인). 이번 devnotes 스크립트도 Linux pwsh 기준. 실차 검증: 미실시(12절).
- (204cha) carrot-ryu 99012c3 독립 검증(이 세션): `git ls-remote` HEAD 일치, 부모 0a1a9fc, numstat 1파일 +4/-0, blob f087a48 -> f4f81e2, CR 0개, BOM 없음(23 21 2f), py_compile 통과. pytest 7개 파일(-n 0 -p no:randomly, pytest-mock 설치) 신판: 7 failed / 278 passed / 54 subtests passed(111 s), 실패는 모두 test_longitudinal.py. long_mpc.py를 0a1a9fc판으로 임시 교체한 기준선(test_longitudinal만): 9 failed / 53 subtests passed(55 s). 신/구 차이는 `cruising at 25 m/s while disabled`(e2e=True, force_decel=True) 서브테스트와 그 부모가 사라진 것뿐이다. 임시 교체는 `git checkout`으로 원복했고 blob f4f81e2/빈 diff/HEAD 99012c3를 확인했다. 샌드박스(Ubuntu 24, Python 3.12) 값이며 넓은 회귀는 실행하지 않았다. 이번 devnotes 스크립트 사전 검증은 Linux pwsh 기준이며 Windows PowerShell 5.1 실제 실행이 아니다. 실차 검증: 미실시(12절).
- (203cha) 남은 서브테스트 5건 프레임 단위 재현(이 세션, 202cha 샌드박스 재사용): disabled+blended reset_state 스크래치 실험(강제 False 시 20 s간 a=-0.866으로 7.87 m/s까지 감속 확인, 실험 후 `git checkout`으로 원복하고 `git diff --stat` 빈 결과 확인 - 코드 변경 없음). cut-in force_decel 20 s 종료 speed=0.1208/a=-0.0283(199cha와 일치). resume from a stop t=10.15~10.25 a=-0.00665~-0.00153(3프레임, 0.15초), t=10.30부터 양전환, t=12.60 a=0.273(199cha와 일치). allow_throttle force_decel=False 2건 종료 speed 20.0048/20.0000(감속 없음, 기존과 동일). 코드 변경 없음, 실차 검증: 미실시(12절).
- (202cha) 코드 0a1a9fc 독립 검증(이 세션): `git ls-remote` HEAD 일치, 부모 69eaf32, numstat 1파일 +3/-1, blob 446c2ed -> f087a48, CR 0개, BOM 없음, py_compile 통과. pytest 7개 파일(-n 0, pytest-mock 설치): 9 failed / 277 passed / 53 subtests passed, 실패는 모두 test_longitudinal.py. long_mpc.py를 69eaf32판으로 임시 교체한 기준선(test_longitudinal만)은 11 failed / 51 subtests passed였고, 신/구 차이는 ACC 모드 force_decel 2건이 사라진 것뿐이다. 임시 교체는 `git checkout`으로 원복했다. 샌드박스(Ubuntu 24, Python 3.12.3) 값이며 넓은 회귀는 실행하지 않았다. 이번 devnotes 스크립트 사전 검증은 Linux pwsh 7.6.6 기준이며 Windows PowerShell 5.1 실제 실행이 아니다. 실차 검증: 미실시(12절).
- 코드 push 재확인(201cha, 독립 clone): HEAD 69eaf32 일치, 부모 bef8edf, --numstat 4파일이 위 수치와 일치, 4개 파일 CR 0개, py_compile과 JSON 파싱 통과. pytest는 이 세션 샌드박스에 없어 재실행하지 않았고, push된 blob과 코드 스크립트 기대 해시의 대조도 하지 않았다(스크립트가 이 세션에 없었음).
- 코드 스크립트의 사전 검증은 Linux PowerShell 7.6.6 기준(구문 오류 0건, bare 저장소 일반/CRLF 체크아웃 모두 통과)이며 Windows PowerShell 5.1 실제 실행이 아니다. 실제 실행은 사용자 PC에서 이뤄졌고 push 로그와 GitHub 재확인으로 결과를 확인했다.
- 테스트 수치는 샌드박스(Ubuntu 24, Python 3.12) 값이다. 이번 devnotes 스크립트도 Linux pwsh 시뮬레이션 기준이다. 실차 검증: 미실시(12절).
- 직전 회차(199cha 계속2)의 재현 수치와 한계는 그대로 유효하다. 세부는 WIP.md 201cha, 199cha 계속2, 199cha 계속, 199cha 참고.

주의사항:
- 199cha 계속의 재현 수치는 샌드박스 하네스 값이다(toolkit/pytest_ci_setup.sh로 구성, 정확한 수치는 -n 0). 재현 스크래치는 untracked 임시 테스트 파일로 만들고, 저장소 파일을 임시로 고친 뒤에는 반드시 `git checkout <파일>`로 되돌린 다음 `git status`로 확인할 것(`openpilot/cereal/gen/`는 환경 구성 산출물). 코드 변경(특히 force_decel 계열)은 별도 승인이 필요하다(10절). long_mpc.py 468행은 202cha(0a1a9fc)에서 이미 수정됐다.
- 시작 전에 WIP.md 197cha 회차(원인, 공식, 표), 필요하면 196cha(T_FOLLOW 매핑, 18건 표), 195cha, 193cha 계속 회차도 읽을 것.
- Plant.__init__은 Params()에 params_keys.h 기본값을 put한다(값이 없는 키만). pytest 안에서는 conftest의 OpenpilotPrefix로 격리되지만, pytest 밖에서 Plant를 돌리면 기본 Params 경로(Path.home()/.comma/params/d, 디바이스는 /data/params/d)에 실제로 쓴다. pytest 밖에서 돌릴 때는 `with OpenpilotPrefix():`(openpilot.common.prefix)로 감쌀 것: msgq 경로(안 감싸면 IpcError: Messaging failure with radarState)와 Params가 함께 격리된다.
- pytest 실행 옵션: pyproject.toml addopts에 `-n auto --dist=loadgroup`이 있으므로 `-p no:xdist`는 쓰지 말 것(사용법 오류로 종료). xdist는 `-n 0`으로 끄고 병렬은 `-n 4`. 요약 줄을 grep으로 걸러 볼 때 결과가 비면 tail로 에러부터 확인할 것(197cha에서 옵션 오류가 grep에 가려져 2회 헛실행).
- 소요 시간: 환경 구성 1분 남짓(백그라운드), following_distance 18건 약 53초(-n 4), 프로브 1회(v 하나, 3 personality) 약 8초.
- 전역 git user.email은 ryujmin97@gmail.com(사용자 확인, f075028f, df0da45, b788ac1에 반영 확인). 기존 커밋 99754dc8/82ed7712 등의 author는 자리표시자이고 6ee1ce7b만 깨진 문자열(기능 영향 없음, --force 금지라 그대로). 스크립트는 전역 값이 ASCII 이메일 형식이 아니거나 미설정이면 ryujmin97@users.noreply.github.com으로 폴백한다(미설정이어도 죽지 않는 ((@(& git config --global user.email) -join "")).Trim() 형태 사용, toolkit 템플릿에는 아직 미반영).
- carrot-ryu에는 openpilot/common/stopping_params.py와 openpilot/common/display_scheduling.py가 없다(VEgoStopping은 get_float * 0.01 직접 사용, 최소값 1). carrot-ms 후속 커밋이 get_stopping_speed나 DisplayScheduler에 의존하면 이 차이를 먼저 확인할 것. carrot-ryu는 .gitattributes가 LFS 설정이고 driving_supercombo.onnx/updater/lane.onnx는 LFS 포인터다. 노트 브랜치(carrot-ryu-note)에는 .gitattributes가 없다(단 FINDINGS.md는 LF/CRLF 혼재라 `* text eol=crlf` 같은 강제 정규화 조건에서는 devnotes 스크립트의 "변경 파일 2개" 검사가 안전 중단한다).
- pytest 재실행은 toolkit/pytest_ci_setup.sh부터(세션마다 파일시스템 초기화). 백그라운드 실행은 setsid nohup ... < /dev/null 로 분리해야 컴파일 중 조용히 죽지 않는다. 이 스크립트는 pytest-mock을 설치하지 않는다(필요하면 pip install pytest-mock를 샌드박스에서 별도로).
- api.github.com은 rate limit이 자주 걸린다. git ls-remote / blobless bare clone / raw(SHA 고정)로 대체할 것. pwsh 설치 버전 조회도 curl -sIL https://github.com/PowerShell/PowerShell/releases/latest 의 Location 헤더 방식이 이번에도 rate limit 없이 동작(v7.6.6). carrot-ms 원본 raw 경로는 `openpilot/selfdrive/...` 접두가 붙는다(`selfdrive/...`만 쓰면 404).
- 다음 코드 변경 세션은 5절 순차 전달(코드 스크립트 먼저 -> 확인 -> devnotes)을 따른다.
- 201cha 이식 코드는 carrot-ryu에 없는 14e2cfa(radar_track_state 거부)를 전제로 하지 않도록 합쳐 놓았다. 나중에 14e2cfa를 들이면 primary.py의 held_stopping_front 두 hunk와 tentative 케이스 테스트(WIP_SYNC.md 201차 참고)를 함께 재검토할 것.
- carrot-ryu에는 dm2.py/dm2d.py/dm2_context.py, tools/jetlink, startup_recovery.py, hyundai steering_touch.py가 없다(201cha clone 확인). carrot-ms 후속 커밋이 이들에 의존하면 이 차이를 먼저 확인할 것.
- 이 세션의 샌드박스 셸은 dash라 $'\r' 같은 bash 전용 인용이 해석되지 않는다. CR 개수는 tr -cd '\r' | wc -c로 센다(첫 CRLF 재현이 이 때문에 잘못된 0으로 나왔음).
- 이 세션 샌드박스에서 `cut -c`는 한글 UTF-8을 바이트 단위로 잘라 출력이 invalid UTF-8이 됐다. 한글 문서는 python 슬라이스로 읽을 것. pytest 재현에는 pip install pytest-mock이 필요했다(pytest_ci_setup.sh가 설치하지 않음). 기준선 비교/스크래치 패치는 대상 파일만 임시 교체하고 반드시 `git checkout <파일>`로 원복해 `git diff --stat`(또는 `git status`)으로 빈 결과를 확인할 것.
- (203cha) 202cha 세션의 샌드박스(/home/claude/repo, 체크아웃 0a1a9fc)는 세션 간 파일시스템이 남아있을 수도, 초기화됐을 수도 있다(이번엔 남아있었다). 있으면 재사용해 환경 구성(약 1분)을 건너뛸 수 있으니 먼저 `git rev-parse HEAD` 등으로 확인할 것.
- (204cha) 이 세션에서 99012c3을 만든 코드 스크립트와 그 사전 검증은 확인하지 못했다(이 세션에 없음). 커밋 주석의 "ACC mode lifts this for v_cruise == 0"은 방향만 같고 조건/값이 다르다(WIP.md 204cha 4번, 미완료 15번). 샌드박스가 남아 있다면 /home/claude/repo(체크아웃 99012c3)를 재사용할 수 있으나 세션 간 초기화될 수 있으니 `git rev-parse HEAD`로 먼저 확인할 것.
- (205cha) 샌드박스/도구 메모: 15번 프로브(probe_lb.py, probe_lb_lead.py)는 세션 로컬이라 저장소에 없다. long_mpc.py 임시 패치(환경변수 PROBE_LB)는 git checkout으로 원복하고 빈 diff를 확인했다. pytest 전체 비교에는 -x를 쓰지 말 것(첫 실패에서 멈춘다. 이번에 기준선을 -x로 돌려 재실행했다). 샌드박스 sh(dash)의 printf는 \xEF\xBB\xBF를 해석하지 못해 BOM이 글자로 들어가므로 BOM은 python으로 붙이고 od -An -tx1 -N3으로 확인할 것(이번에 그렇게 잡았다). 샌드박스에는 git-lfs가 없다.
- (205cha) 이번 코드 스크립트는 이전 것들과 달리 (a) 환경변수 GIT_LFS_SKIP_SMUDGE=1, (b) git add -A 대신 대상 2경로만 add, (c) 수정 전/후 blob 해시 가드를 넣었다. 이전 코드 스크립트가 같은 방식이었는지는 이 세션에서 확인하지 못했고 toolkit 템플릿에도 반영하지 않았다(필요하면 승인 후).
- (205cha) 058391e의 Author 이메일이 사용자 로그에서 ryujmin@naver.com로 표시됐다. 위 전역 user.email 기록(ryujmin97@gmail.com)과 다르다. 스크립트는 전역 설정이 ASCII 이메일 형식이면 그대로 쓰므로 사용자 PC 설정이 바뀌었거나 다른 값일 수 있다. 기능 영향 없고 --force 금지라 그대로다. 의도 확인이 필요하면 사용자에게 물을 것.

다음 작업:
1. 사용자가 선택: (d) carrot-ms 점검 계속(c771c4e 이후, c36f6e7부터), (b) 202cha/204cha/205cha 실차 확인 항목 정리(미완료 13, 15번과 comfort_brake 정상상태 추종 거리), (i) blended forceDecel의 감속이 ACC보다 약한 점(blended는 25 -> 약 8 m/s, ACC는 정지)을 의도로 볼지 설계 판단, (f) 이월 항목(실차 검증들, 미완료 10번 포함), (g) (b')/(c)/(v). 이전 목록의 (h) 미완료 15번 검토와 (e) comfort_brake 통일은 205cha에서 처리했다(15번은 유지 권고, 사용자 이의 없으면 종결).
2. 코드 변경이 나오면 5절 순차 전달(코드 스크립트 먼저 -> 확인 -> devnotes 1회).
