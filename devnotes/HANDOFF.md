Worker: Claude (271cha, Claude Sonnet 5.5). 사용자가 현재 기기 설정값이라며 올린 `params_backup.json`으로 `JerkCostEgo`(12), `AlwaysLateral`(1), `EnableRadarTracks`(0), `TurnSpeedControlMode`(2)를 확인했다(코드 변경 없음, 설정값 읽기만, 실차 검증 미실시). 나머지 내용은 이전 HANDOFF에서 옮긴 것이다.
Date: 2026-10-12
Repository: ryujmin97/openpilot
Code Branch: carrot-ryu (현재 HEAD = base commit 760905a(270cha에서 `git ls-remote`로 다시 확인), 8212379 이식 커밋. 부모 110cff9 = 267cha 반영 커밋). 269cha에서 GitHub로 직접 확인했다: 변경 10개 파일 +415/-4(신규 3: `longitudinal_braking_gap.py`, `test_longitudinal_braking_gap.py`, `test_radar_closing_range.py`), 트리 파일 수 5,454 -> 5,457, 신규 파일 모드 100644, diff 안 CR 0.
Note Branch: carrot-ryu-note (이 교체 직전 base 95126c8. 이 HANDOFF 교체는 그 위에 올라간다).
Archive Branches: carrot-ryu-v1 (6df4268eb31442be4d8abd92817111f7b26b1bf4, 불변), carrot-ryu-v2 (3ddf849ea3f3392c16d363d9edea6a1bc8eab041, 212cha 생성, 불변). carrot-ryu-v3는 아직 없고 보존 시점은 사용자가 정한다(20절).
carrot-ms 마지막 검토 체크포인트: b7dd150 (270차: 28d2386..b7dd150 신규 3건 점검, 전부 제외 확정. 268차의 `4896f0d`와 제외안 27건도 270차에 제외로 확정되어 확정 대기 항목은 없다. 후보 `8212379`는 269차에 전체 이식, carrot-ryu 760905a). 다음 점검은 b7dd150 이후 신규 커밋이 생겼을 때이며, `git cat-file -t b7dd150`로 존재부터 확인한다(carrot-ms는 재생성되므로).

이 파일은 8절대로 "최신 1개 버전만" 유지한다. 201cha~262cha의 작업/완료/미완료/검증/주의사항/다음 작업 전체 이력은 커밋 f58764b의 같은 경로에 그대로 있다: `git show f58764bd94f0e7fdc5b0c9e9f2028a85726894fa:devnotes/HANDOFF.md` 또는 SHA 고정 raw URL(https://raw.githubusercontent.com/ryujmin97/openpilot/f58764bd94f0e7fdc5b0c9e9f2028a85726894fa/devnotes/HANDOFF.md). 회차별 상세는 WIP.md(불변)가 갖고 있으므로 여기에 다시 쌓지 않는다. 아래 "미완료/주의사항"은 이전 HANDOFF에서 옮긴 것이며, 옮길 때 번호는 그대로 두었다. 상세가 필요하면 위 커밋에서 해당 번호를 읽는다.

작업(271cha, 이 구간, 코드 변경 없음):
1. 4절 0단계(지침 v2, note 95126c8, 브랜치 URL본과 SHA본 md5 일치)와 HANDOFF를 읽었다. 앞 세션 270cha devnotes push(95126c8)를 GitHub에서 직접 확인했다(부모 034226d, WIP.md +27/-0, WIP_SYNC.md +14/-0, HANDOFF.md +19/-10, BOM 없음, carrot-ryu는 760905a 그대로).
2. 사용자가 현재 기기 설정값이라며 올린 `params_backup.json`(파일 안에 저장 시각 없음)에서 다음을 확인했다: `JerkCostEgo`=12, `AlwaysLateral`=1, `EnableRadarTracks`=0, `TurnSpeedControlMode`=2, `HyundaiCameraSCC`=1(참고).
3. 의미: `JerkCostEgo` 12는 270cha 결정과 코드(기본값, `J_EGO_COST = 12.0`)와 일치해 CarrotWeb에서 바꿀 일이 없다. `AlwaysLateral` 1이라 353cc8e의 시동 직후 조향 게이트 경로가 해당된다. `EnableRadarTracks` 0이라 760905a의 레이더 `closing_range` 매칭과 b3e16c5는 작동하지 않는다(269cha 분석과 같음). `TurnSpeedControlMode` 2는 266cha의 회피안(2 -> 1)이 적용되지 않았다는 뜻이고, 110cff9가 코드로 고쳤으므로 값을 바꿀 필요는 없다.
4. devnotes(WIP.md 271cha, 이 HANDOFF)를 PowerShell 스크립트로 기록했다. carrot-ms 점검이 없어 WIP_SYNC.md는 바꾸지 않았다.

작업(270cha, 이전 구간, 코드 변경 없음):
1. 4절 0단계(지침 v2, note 034226d, 브랜치 URL본과 SHA본 바이트 일치)와 HANDOFF를 읽었다. 사용자가 `JerkCostEgo` 12 유지로 결정했다(코드 기본값 12와 같아 코드 변경 없음. HANDOFF 기록상 기기 설정값은 20이었으므로 기기 값이 20이면 CarrotWeb에서 12로 바꿔야 한다. 기기 값은 확인하지 않았다).
2. 268차의 `4896f0d`(한글 자모 글리프 추가, 글자 깨짐 증상이 있을 때만 필요)는 사용자가 제외로 확정했다.
3. carrot-ms를 다시 조회해 28d2386..b7dd150 신규 3건(`cc34d6a`, `d9c226f`, `b7dd150`, 모두 신호등 정지 준비 실험)을 점검했다. carrot-ryu에 전제 코드(`signal_assist` 등)가 없고 `cc34d6a`는 종방향 가속도 경로를 바꾸는 실험이라 제외안을 냈고, 사용자가 신규 3건과 이전 것(268차 제외안 27건)을 모두 제외로 확정했다. 상세는 WIP.md 270cha와 WIP_SYNC 270차.
4. devnotes(WIP.md 270cha, WIP_SYNC.md 270차, 이 HANDOFF)를 PowerShell 스크립트로 기록했다.

작업(269cha, 이전 구간, 코드 변경 없음):
1. 4절 0단계(지침 v2, note 2627042, 브랜치 URL본과 SHA본 md5 일치)와 HANDOFF를 읽었다. 앞 세션은 `8212379` 이식(760905a)과 오프라인 시뮬레이션 검증까지 마친 뒤 사용량 한도로 중단돼 devnotes는 기록되지 않았고, 샌드박스가 초기화돼 하네스가 사라졌다.
2. 앞 세션 기록에서 하네스를 복원해 `devnotes/toolkit/cl_sim/`로 정리했다(`cl_sim.py`, `scen.py`, `sweep.py`, `relief.py`, `fuzz.py`, `fuzz_summary.py`, `fallback.py`, `prep_base.sh`). `pytest_ci_setup.sh`로 환경을 다시 만들고(760905a), 복원본으로 sweep 30행, relief 15행, fallback 3행, fuzz 160케이스를 다시 돌렸다. 모두 앞 세션 수치와 일치했다.
3. GitHub에서 760905a(부모 110cff9, 10개 파일 +415/-4, 트리 5,457)를 직접 확인했고, 테스트를 다시 돌렸다: 관련 4개 파일 164건 통과, `carrot/tests`+`controls/tests` 전체 9 failed/24 errors/2,625 passed(실패 33건의 파일별 개수가 앞 세션 기준선과 같음).
4. SCC 앞차: `SCC_TID = 0`이고 컨트롤러 단위 실험에서 `EnableRadarTracks` -1/0/3 모두 `radarTrackId=0`, `radar=True`. `closing_range` 매칭은 frontRadar에서 모드 1/2/3에서만 성립, 0/-1에서는 비작동. 상세는 WIP.md 269cha.
5. devnotes(WIP.md 269cha, WIP_SYNC.md 269차, toolkit README/CHANGELOG/cl_sim, 이 HANDOFF)를 PowerShell 스크립트로 기록했다.

작업(268cha, 이전 구간, 코드 변경 없음):
1. 4절 0단계(지침 v2, note 3ddb894, 브랜치 URL본과 SHA본 md5 일치)와 HANDOFF를 읽고 carrot-ms 0e7f299..28d2386 신규 29건을 점검했다. blobless bare clone으로 받았고, 후보와 공용 경로는 diff 본문을 읽었다.
2. 판정안: 후보 `8212379`(부분), 선택 `4896f0d`, 제외안 27건(신호등 인식 보조 24, eGPU/MDM 2, CAN-FD 1). 사용자는 "우선 기록"으로 답했고 반영/제외 확정은 아직 없다. 상세는 WIP.md 268cha와 WIP_SYNC 268차 표.
3. `8212379`: 앞차 제동 시 간격 유지(`long_mpc.py` + 신규 `longitudinal_braking_gap.py`)는 모드와 무관하게 내 차에 작동하고, 레이더 `closing_range` 매칭은 `EnableRadarTracks=0`에서 작동하지 않는다. `apply --check`로 carrot-ryu 적용 가능성을 확인했다(테스트 `test_cutout_mpc_integration.py`는 hunk 충돌, `test_radar_corroboration.py`는 carrot-ryu에 없음). 커밋 메시지가 실차/acados 검증 없음을 명시한다. 옵션은 보류 / long_mpc 쪽만 / 전체이고, 제안 의견은 실차 로그 확보 전까지 보류다.
4. devnotes(WIP.md 268cha, WIP_SYNC.md 268차, 이 HANDOFF)를 기록했다. 사용자가 PowerShell 스크립트로 받았다.

작업(267cha, 이전 구간):
1. 4절 0단계(지침 v2, note 637392e)와 HANDOFF를 읽었다. 사용자가 266cha 선택지에서 "1+2번으로 진행"을 골랐고 반영 스크립트는 Termux로 받았다.
2. `carrot_man.py`를 고쳤다: `ROUTE_PATH_MIN_POINTS` 대신 `ROUTE_PATH_COVER_MARGIN_M = 5.0`과 `route_path_covers_lookahead()`(경로 점 사이 거리 합 >= 전방 탐색거리 - 5 m)로 충분 판정, freeze 만료 시 `navi_route_speed_filt = None`. 신규 테스트 `tests/test_carrot_route_sufficient.py` 9건을 함께 넣었다.
3. 샌드박스에서 새 테스트와 변이 확인(옛 판정 복원 시 2건, filt 지움 제거 시 1건 실패), `carrot/tests` 전체 원본 대비 비교(5 failed/22 errors로 동일), Termux 스크립트 시뮬레이션(일반, CRLF, 중단 3종, 실제 GitHub DRY_RUN)을 했다. 사용자가 스크립트를 실행했고 GitHub에서 직접 재확인했다(carrot-ryu 110cff9).
4. devnotes(WIP.md 267cha, FINDINGS 핵심 발견 74, 이 HANDOFF)를 기록했다. 상세는 WIP.md 267cha.

작업(266cha, 이전 구간, 코드 변경 없음):
1. 4절 0단계(지침 v2, note 72961a8)와 HANDOFF를 읽고, 사용자가 올린 route 00000497 세그먼트 121, 122 rlog와 params_backup.json으로 route 목표속도 고정 현상을 분석했다(기록 커밋 353cc8e, toolkit route_extract.py 재사용).
2. 결론: `carrot_navi_route()`의 `route_info_sufficient = len(path) >= ROUTE_PATH_MIN_POINTS(4)`가 직선 고속도로(꼭짓점 간격 중앙값 437 m)에서 거의 항상 "부족"이 되고, freeze가 만료돼도 `navi_route_speed_filt`가 지워지지 않아 점이 충분해지는 순간 낡은 값 기준 +1 km/h/사이클 슬루가 걸린다. 121에서 51.36초에 route 162 -> 83 급락 후 105.9(원시 78.4)까지 램프, 122의 7.6초에 162로 풀림. 급락 직전 filt는 원시 약 60.5로 역산.
3. 해결안(승인 대기): (1) 충분 판정을 경로가 덮는 길이(약 295 m 이상)로 교체, (2) freeze 만료 시 filt = None, (3) 코드 없는 회피 `TurnSpeedControlMode` 2 -> 1(미검증). 상세와 재생 수치는 WIP.md 266cha, FINDINGS 핵심 발견 73.
4. 사용자가 "먼저 기록, termux"로 답해 devnotes만 먼저 기록했다(이 HANDOFF 교체 포함). 코드 반영은 사용자의 다음 지시를 기다린다.

작업(265cha, 그 이전 구간):
1. 4절 0단계(지침 v2, note eb821ce)와 HANDOFF를 읽고 carrot-ms a0698918..0e7f299 신규 23건을 점검했다. 사용자가 "1번 진행. 나머지 제외 확정"으로 답했다(이식 3건, 제외 20건).
2. 시동 직후 조향 차단(`LateralStartupGate`)을 carrot-ryu에 이식했다(353cc8e). Termux bash 스크립트로 반영했다(사전/사후 blob 해시 검증, 로컬 bare 시뮬레이션). 반영 뒤 GitHub에서 직접 재확인했다.
3. 20건의 제외 사유는 WIP_SYNC 265차 표, 이식 상세는 WIP.md 265cha를 본다.

작업(264cha, 더 이전 구간):
1. 사용자가 "d14303d5 코드 진행"으로 승인했다. 반영 전에 carrot-ryu 기준 앵커를 확인했다: `selfdrived.py` 529행 `timed_out = self.sm.frame * DT_CTRL > 6.` 한 곳에만 매치되고, 바로 앞 줄은 `all_valid = CS.canValid and self.sm.all_checks()`다. selfdrived/tests 6개 파일에는 6초 기준을 고정하는 테스트가 없다.
2. Termux 반영 스크립트로 `selfdrived.py`의 한 줄을 주석 1줄과 `> 10.`으로 교체하고 push했다(d082d92). push 전에 스크립트가 3회 중단됐고 원격은 그때마다 변경되지 않았다. 처음 두 번은 파일 모드 문제로 잘못 진단했다. 세 번째 실행의 진단 출력으로 실제 원인을 찾았다: `--no-checkout` clone 뒤 인덱스가 비어 있어 나머지 파일이 전부 "삭제"로 보였다. 파일 여러 개가 있는 시뮬레이션에서 재현한 뒤 clone 직후 `git reset --quiet`로 인덱스를 HEAD에 맞춰 해결했다.
3. devnotes 기록 스크립트로 WIP.md에 264cha, WIP_SYNC.md에 264차 블록을 최상단에 추가했다(note 3a3937e). 두 파일 모두 기존 내용은 삭제되지 않았다.
4. 이 HANDOFF를 교체했다(교체형).

완료(최근 구간, 상세는 WIP.md와 WIP_SYNC.md):
- 271cha: 사용자가 올린 기기 `params_backup.json`으로 `JerkCostEgo`=12, `AlwaysLateral`=1, `EnableRadarTracks`=0, `TurnSpeedControlMode`=2 확인(코드 변경 없음, 설정값 읽기만, 실차 검증 미실시). 270cha devnotes push(95126c8) GitHub 재확인.
- 270cha: carrot-ms 28d2386..b7dd150 신규 3건(신호등 정지 준비 실험) 점검과 제외 확정, 268차 `4896f0d`와 제외안 27건 제외 확정(코드 변경 없음, 정적 분석, 실차 미실시). `JerkCostEgo` 12 유지 결정 기록. WIP_SYNC 270차에 확정 기록, 점검 체크포인트 b7dd150.
- 269cha: carrot-ms `8212379` carrot-ryu 이식(760905a) GitHub 재확인, 전체 테스트 재실행, 실제 acados 폐루프 시뮬레이션(고정 30행, 무작위 160, 완화 경로 15, 폴백 강제 3) 재실행과 `toolkit/cl_sim/` 등록. 오프라인뿐이며 실차 검증은 미실시. WIP_SYNC 269차에 `8212379` 반영 확정을 기록.
- 268cha: carrot-ms 0e7f299..28d2386 신규 29건 점검 판정안 기록(코드 변경 없음, 정적 분석, 실차 미실시). 270cha에 `4896f0d`와 제외안 27건이 제외로 확정됐다.
- 267cha: carrot-ryu route 낡은 filt 수정 반영(110cff9: 충분 판정을 경로 길이 기준으로, 만료 시 filt 지움, 테스트 9건 신규; 정적 분석과 단위 테스트, 실차 미실시). devnotes 기록.
- 266cha: route 낡은 filt 현상 분석 기록(코드 변경 없음, 정적 분석과 로그 재생, 실차 검증 미실시).
- 265cha: carrot-ryu 시동 직후 조향 차단 이식(`lateral_readiness.py` 신규, `controlsd.py`/`card.py`/`carrot_settings.json` 수정, 테스트 4파일; 353cc8e, 정적 검증, 실차 미실시). 265차(WIP_SYNC): carrot-ms a0698918..0e7f299 신규 23건 점검, 이식 3건, 제외 20건 확정.
- 264cha: carrot-ryu d14303d5 selfdrived 온라인 초기화 대기 6초 -> 10초 반영(d082d92, 정적 검증, 실차 미실시). devnotes 기록 3a3937e.
- 263차(WIP_SYNC): carrot-ms 9fe7fa5..a0698918 신규 31건 점검, 제외 30건 확정, 후보 d14303d5 유지. 제외 30건의 분류는 WIP_SYNC 263차 표를 본다(Jetlink/Jetson 13, eGPU 3, CAN-FD 3, 클러스터/C4 2, Tesla 2, Xiaoge 4, 공용 경로 검토 후 제외 2(a0698918, 673d5e74), 기록 문서 1).
- 262cha: carrot-ms 0a67f68..9fe7fa5 신규 8건(Jetson/Jetlink 계열)을 모두 제외로 확정, carrot-ryu 반영 없음(정적 확인, 실차 검증 미실시).
- 261cha: HANDOFF.md를 8절의 최신 1개 버전으로 슬림화(코드 변경 없음).
- 260cha: 1326f21 규칙이 크루즈 작동 중 새로 만드는 프레임 측정(route 478 세그먼트 1~10, 8,309프레임에서 새 present 0개)과 끊김 유지(G) 대 채움(A) 플래너 시뮬레이션(route 492-4). 재생/시뮬레이션만이며 실차 검증은 미실시.
- 259cha: 1326f21 재검증(route 492 세그먼트 4에서 끊김 10 -> 0, pytest 447 passed).
- 이전 구간의 반영 커밋 요약(carrot-ryu): d082d92(selfdrived 온라인 초기화 대기 10초, 264cha), 1326f21(비전 앞차 해제 대역 1.5 m + 3프레임 홀드), 670f72c(carrot-ms 47d35da 간격 헤드룸 유지 거리 대역), `J_EGO_COST` 12.0 반영(246cha, 두 테스트의 하드코딩 보정은 0a1ad62), f9ffbc2(`JerkCostEgo` 설정, 코드 기본 12, 상한 20), b3e16c5(SCC 모드 -1 비전 앞차 허용, 기기값 0이라 현재 비작동), 11d7e89/0f08f08/76b182a(UI 네이티브 배치와 plot 경량화), 8cdb515(SCC 앞차 비전 거리 완화), 99012c3(disabled+blended force_decel 미감속 수정).

미완료(번호는 이전 HANDOFF 기준. 실차 항목은 모두 "실차 검증: 미실시"):
- 신규(269cha) 760905a 실차 확인(8212379 이식, 전부 "실차 검증: 미실시"): (a) 앞차와 함께 감속하는 장면(앞차 제동 때 간격 유지)에서 간격이 기준선(110cff9)보다 크게 유지되는지, 제동이 너무 일찍/강하게 걸리지 않는지(시뮬레이션은 최대 제동 차이 -0.03~+0.06 m/s², 최소 간격 중앙 +0.39 m). (b) 근거리에서 앞차가 완만하게 감속할 때 편안함 완화(`comfort_relief`)가 약 1초 켜지는지와 승차감(시뮬레이션은 최소 TTC가 0.5~0.9 s 줄고 최대 제동이 0.06~0.07 m/s² 더 세졌다). (c) 완화가 켜질 때 조건부 추가 solve 1회가 C3 CPU/플래너 시간에 주는 부하(재지 않았다). (d) 기기 `EnableRadarTracks`는 271cha에 params_backup.json에서 0으로 확인했다(0이라 레이더 `closing_range` 절반은 작동하지 않는 것이 맞다). (e) SCC 앞차에서 `radarTrackId=0`으로 이식 코드가 실제로 작동하는지 실제 SCC 스트림이 들어간 로그로 확인(컨트롤러 단위 실험에서만 확인). `toolkit/cl_sim`은 합성 시나리오용이라 실로그 재생에는 쓸 수 없다(실로그 재생 도구 `gap_replay/`는 gap_recovery용이라 이식 코드에는 그대로 맞지 않을 수 있다).
- 신규(268cha) carrot-ms 판정은 모두 확정됐다(남은 것 없음): `8212379`는 269차에 전체 이식, `4896f0d`와 제외안 27건은 270차에 제외로 확정, 신규 3건(28d2386..b7dd150)도 270차에 제외 확정. WIP_SYNC 270차에 기록했다.
- 신규(267cha) 110cff9 실차 확인: 같은 구간(직선 고속도로, 내비 경로 활성) 재주행 로그에서 (a) 직선 구간 route 목표속도가 상한으로 유지되고 낡은 값에서 +1 km/h/사이클로 올라가는 구간이 사라졌는지, (b) 진출 램프(안내 600 m 구간)에서 route 곡률 감속이 새로 켜져 너무 일찍/강하게 걸리지 않는지(1번이 고속도로에서 route 곡률 감속을 실제로 켜므로 동작이 바뀐다), (c) 경로 끝이나 내비 종료 근처에서 freeze 유지와 만료 동작을 확인한다. 266cha 재생 수치(충분 4.1% -> 99.7%)는 295 m 기준이고 이 구현(300 m - 5 m)으로 다시 돌리지 않았다. 낡은 값 60.5가 처음 저장된 순간은 여전히 미확정이다(세그먼트 120 rlog가 있으면 확인; 만료 시 filt를 지우므로 출처와 무관하게 이번 증상은 막지만 만료 전 다른 경로의 낡은 값 문제는 범위 밖). 이번 세션에 올라온 로그 zip 2개(`HYUNDAI_GENESIS_541384155f4f8ca5_20261011_170556.zip`, `..._173000.zip`)는 분석하지 않았다.
- 기기 `AlwaysLateral`(353cc8e 확인 (a)): 271cha에 사용자가 현재 기기 설정값이라며 올린 params_backup.json에서 1로 확인했다. 시동 직후 조향 게이트 경로가 해당된다(확인 (b)(c)는 주행 로그가 필요).
- 신규(265cha) 353cc8e 실차 확인: (a) 기기의 `AlwaysLateral` 값은 271cha에 1로 확인했다(켜져 있어 시동 직후 경로가 해당된다). (b) 시동 직후 첫 조향이 부드러운지, 게이트가 너무 늦게 열려 조향 시작이 지연되지 않는지 주행 로그로 확인(carControl.latActive 시작 시각과 modelV2/liveParameters 첫 수신 시각 비교). (c) 정상 주행 중 게이트가 다시 막지 않는지(한 번 통과하면 재무장 없음이 설계). 변경은 d082d92 이전 동작과 달리 시동 직후 수 초간 조향이 늦게 시작될 수 있다.
- 신규(264cha) d082d92 실차 확인: 정상 시동에서 온라인 초기화가 이전보다 늦어지거나 이상이 생기지 않는지, 시동 시간이 실제로 줄었는지 주행 로그로 확인한다. 이 변경은 타임아웃 한 줄뿐이라 로직 자체는 1326f21과 같다. 아래 1326f21 기준 항목은 d082d92에서도 그대로 유효하다.
- 48번 (a) 실기기에서 1326f21의 비전 단독 앞차 장면 확인. (b) 옆 차선 오감속 빈도는 이 로그로 판정 불가: 크루즈 작동 중 비전 단독 앞차가 1.0~1.5 m 경계에 걸리는 장면(옆 차선에 차가 많은 도로) 로그가 필요. (c) G가 A보다 과대하게 나온 원인은 미규명(끊김 뒤 실제 플래너의 lead 유지 로직 읽기, 채운 프레임에 비전 원시값 넣어 `jerk_sim/run_gap.py` 재실행은 선택지).
- 45번, 47번 (a) `JerkCostEgo`: 270cha에 사용자가 12 유지로 결정했다(코드 기본값과 `J_EGO_COST = 12.0`이 이미 12라 코드 변경 없음). 기기 값은 271cha에 params_backup.json에서 12로 확인했다(CarrotWeb에서 바꿀 일 없음. 이전 HANDOFF의 20 기록은 이미 바뀐 상태이며 바뀐 시점은 알 수 없다). 참고: 256cha 시뮬레이션에서 J=20은 FCW의 주원인은 아니지만 감속을 늦추는 증폭 요인이었다. 12가 실차에서 어떤지는 실차 검증 미실시.
- 46번 (a), 255cha 정지 앞차 근처 풀림: 크루즈 활성 상태에서 앞차가 정지하는 장면 로그가 없어 검증 불가(기록 커밋 670f72c 이상 필요). 47번 (b): 차량 SCC 레이더가 정차 버스를 경고 시점까지 보고하지 않은 이유는 로그로 알 수 없음(`EnableRadarTracks` 0 대 -1과는 무관함은 257cha에 확인).
- 44번 `test_leads.py::test_radar_fault` 실패: 원인은 `openpilot/selfdrive/test/process_replay/migration.py` 306행의 옛 이름 `CANFD_LKA_STEER_MSG`(carrot-ms는 `CANFD_LKA_STEERING`). 알려진 실패로 두거나 한 줄 수정 코드 세션(승인 필요)으로 처리하는데, 수정 여부는 미결정.
- 22~28번 고속 앞차 추종/램프: 8cdb515 실차 확인(급감 사라졌는지, 끼어들기 반응 지연 없는지), SCC<->비전 전환 후속(8 m 규칙은 대부분 비전이 옳았음, 거리 비례 완화안은 표본 부족으로 승인 전), 진출 램프 600 m와 유지 300 m 실차 확인, 진입 램프 조건은 미해결(내비를 켠 채 진입/진출 램프를 지나는 rlog 필요).
- 실차 확인 이월: 3번 comfort_brake 2.5 통일 뒤 정상상태 추종 거리와 승차감, 4번 v=0 정상상태 gap이 desired보다 약 1.06 m 작은 현상(재주행 로그의 정지 장면에서 간격만 확인), 10번 948b139 이식(held_stopping_front), 13번 202cha(v_cruise=0일 때 ACC 감속 반영), 15번 (a), 7번 핵심 발견 68 실차 검증/163차 게이트/xTurn=6 로그/102ms wide-camera BOOT_TS gap, 8번 110차 GATE_M 0.8/1.0과 114차 MAP_TURN_GUIDE_FACTOR=1.00.
- 29, 33~41번 UI 프레임 저하와 네이티브 UI: 이 기기의 fps 저하는 원래 수준일 가능성이 크다는 비교(227cha 계속2)까지만 했다. 남은 것은 76b182a 효과 확인(35번), 기기 `_draw_native*.so` 빌드 근거(241cha: `.so` 존재까지 확인, scons 빌드 로그와 ARM 빌드 성공 자체의 증거는 없음, 38번), 11d7e89 검증 공백(40번 (a)(c)(d)), plot 모드를 고정한 같은 조건 로그로 네이티브 효과 비교(41번 (b)). 상세는 이전 HANDOFF의 해당 번호.
- 30번 b3e16c5(SCC 모드 -1 비전 앞차 허용): 기기 `EnableRadarTracks`는 0이고(271cha params_backup.json에서 재확인) 사용자가 0으로 계속 쓸 예정이라 보류. -1로 바꿀 때만 -1 실주행 로그 확인.
- 9번 f992f9c LFS 전환 재검토(디바이스 LFS pull 실패나 계정 한도 문제가 확인될 때만), 12번 4770067(부팅 실패 자동 Git 복구) 보류(사용자가 원할 때만), 19번 carrot-ryu-v3 보존 시점은 사용자가 정한다.
- 42, 43번 `J_EGO_COST` 12.0 반영 뒤 실차 로그로 앞차 감속 거동 확인(새 로그 zip 필요).

종결(재조사 불필요, 근거는 WIP.md 해당 회차):
- 1, 2번(test_longitudinal 서브테스트 실패, 226cha 사용자 승인으로 조사 없이 종결), 5번(carrot/server/tests 7건, 코드 변경 없이 종결 유지), 16~18번(HUD 위치 확인, DATE_TIME_X_SHIFT 110 현행 유지), 19번 옛 재생성 방침(폐지), DM2 계열 제외 확정(217cha), 카메라 접근 정책 "표시속도 기준 유지"(244cha 사용자 결정, 바꾸려면 새 결정과 안전성 검토와 승인), a2139b7 제외(CAN-FD 차량을 다루게 되면 재검토).
- carrot-ms 263차 제외 중 재검토 조건이 있는 것: a0698918(camerad poll 구조 변경, 실물 재연결·점화 사이클 검증 미완, 공용 카메라 코드)은 실차 근거가 있을 때만 다시 본다. 673d5e74(운전자 카메라 사용 불가 배너 제거, 안전 알림 변경)는 사용자 승인 없이는 반영하지 않는다. Xiaoge 4건(12e01eb5, 986b4979, 1c9351b5, 4a2115dc)은 내 차량에서 Xiaoge를 쓰는지 확인한 뒤 재점검한다.

검증:
- 271cha 검증: GitHub에서 note 95126c8의 부모(034226d), 변경 파일 3개(HANDOFF.md +19/-10, WIP.md +27/-0, WIP_SYNC.md +14/-0), 세 파일의 첫 3바이트(BOM 없음), WIP.md 최상단 270cha 블록, carrot-ryu 760905a를 `git ls-remote`와 blobless bare clone으로 확인했다. 기기 설정값은 사용자가 업로드한 params_backup.json 파일에서 읽었다(파일 안에 저장 시각이 없어 "현재 값"은 사용자 진술에 따른 것이고, 기기에서 직접 읽은 것이 아니며, 위 5개 키 외에는 비교하지 않았다). 설정값 읽기만이며 실차 검증은 미실시다.
- 270cha 검증: carrot-ms HEAD `b7dd150`(`git ls-remote`), `git cat-file -t 28d2386` = commit, `merge-base --is-ancestor 28d2386 HEAD` 성공, `28d2386..HEAD` 3건을 확인했다. 변경 파일은 `show --stat`으로 읽었다(`cc34d6a` 11개 +573/-4, `d9c226f` 5개 +177/-27, `b7dd150` 4개 +118/-11). `cc34d6a`의 공용 경로 diff(`longitudinal_planner.py` +28, `carrot_functions.py`, `model_renderer.py`, `cluster_renderer.py`, `signal_tracking_shadow.py`, `test_signal_start_guard.py`, AGENTS.md)는 본문을 읽었다. carrot-ryu 760905a의 `carrot_functions.py`/`longitudinal_planner.py`에서 `signal_assist`/`start_guard`/`apply_signal_start_guard` 0건, signal 계열 파일 없음을 blobless bare clone의 `ls-tree`와 `git show`로 확인했다. 한계: `signal_stop_prepare*.py`, 테스트, docs 본문과 `d9c226f`/`b7dd150` diff 본문은 읽지 않았다. 정적 확인이며 실차 검증은 미실시다.
- 269cha 검증: GitHub에서 carrot-ryu 760905a의 부모(110cff9), 변경 10개 파일 +415/-4, 트리 5,454 -> 5,457, 신규 3개 모드 100644, diff 내 CR 0을 확인했다. 샌드박스(`pytest_ci_setup.sh`, HEAD 760905a): 관련 4개 파일 164건 통과, `carrot/tests`+`controls/tests` 전체 9 failed/24 errors/2,625 passed/4 skipped(앞 세션이 잰 기준선 110cff9의 9 failed/24 errors/2,597 passed와 실패 파일별 개수 동일, 기준선은 이 세션에서 다시 돌리지 않음). 실제 acados 폐루프 시뮬레이션(HEAD 대 110cff9): 고정 30행에서 HEAD 최소 간격이 기준선 이상, crash 값 불일치 0, 무작위 160케이스에서 간격 악화 최악 -0.44 m(0.5 m 초과 악화 0건), TTC 1 s 초과 악화 0건, FCW 차이 0건, 솔버 비정상 0건. 편안함 완화 경로 15케이스와 폴백 강제 발동 3케이스도 이상 없음. 한계: 레이더 이상적, 앞차 1대, 자차 응답 미보정. 실차 검증은 미실시다.
- 267cha 검증: GitHub에서 carrot-ryu 110cff9의 부모(353cc8e), 변경 2개(M carrot_man.py 30/8, A test 162/0)의 blob 해시 일치, 트리 5,454개, 모드 100644, CR 0, carrot_man.py 내용이 샌드박스 새 파일과 일치함을 확인했다. 샌드박스 pytest: 새 테스트 9건 + lookahead/bridge 관련 19건 통과, `selfdrive/carrot/tests` 전체는 원본과 같은 5 failed/22 errors(목록 diff 동일, 새 실패 없음). 변이 확인 2종으로 새 테스트가 옛 동작을 잡음을 확인했다. 실차 검증은 미실시다.
- 265cha 검증: GitHub에서 carrot-ryu 353cc8e의 부모(d082d92), 변경 파일 8개(M4/A4)의 blob 해시 일치, 트리 5,453개, 파일 모드 유지, CR 0을 확인했다. 전체 체크아웃 pytest: 신규·관련 155건 통과, `controls/car/selfdrived` 테스트 통과 870 -> 975, 실패 8건은 d082d92 기준선과 동일(새 실패 없음). 실차 검증은 미실시다.
- 264cha 검증: GitHub에서 carrot-ryu d082d92 raw 내용(기대값과 일치, CR 없음), 두 커밋 사이 변경 파일 1개(+2/-1), 트리 파일 수 5,449개 동일, 파일 모드 100755를 확인했다. note 3a3937e에서 WIP.md의 264cha와 WIP_SYNC.md의 264차 블록을 확인했다. pytest는 돌리지 않았다. 실차 검증은 미실시다.
- 이전 검증 기록은 WIP.md 해당 회차를 본다.

주의사항:
- 스크립트 시뮬레이션(265cha): `--no-checkout` clone에는 없는 폴더가 있으니 신규 파일을 쓰기 전에 `mkdir -p`를 한다. 샌드박스의 `/bin/sh`는 `${N:0:7}`를 못 쓰니 `bash`로 실행한다. 시뮬레이션 push에는 `GIT_AUTHOR_*`/`GIT_COMMITTER_*` 환경변수가 필요하다. 파일을 글롭(`test_lateral_*.py`)으로 옮길 때 기존 파일이 같이 딸려가지 않게 이름을 명시한다.
- carrot-ryu 고유 차이 추가(265cha): `controls/lib/lateral_readiness.py`(carrot-ms HEAD본), `controlsd.py`의 `lateral_startup`/`lateral_started`, `card.py`의 이중 가드와 SubMaster 4개 서비스가 있다. carrot-ms가 이 게이트를 바꾸면 따로 대조한다. Hyundai CAN-FD `carcontroller.py`의 `steering_template_ready`는 이식하지 않았다.
- 부분 clone(--no-checkout)의 인덱스는 비어 있다(264cha). 파일 하나만 checkout하면 나머지 파일이 전부 삭제로 보인다. clone 직후 `git reset --quiet`로 인덱스를 HEAD에 맞춘다. 파일이 한 개뿐인 시뮬레이션은 이 문제를 재현하지 못했으니, 부분 clone 스크립트는 파일이 여러 개인 저장소로 검증한다.
- 실패 진단 순서(264cha): 파일 모드나 권한을 추측으로 고치지 말고, 먼저 `git diff --cached --summary` 전체 출력을 본다. 264cha에서 모드 원인을 두 번 잘못 짚었다.
- Termux용 bash 스크립트에는 BOM을 넣지 않는다(shebang이 깨진다). BOM은 Windows `.ps1`에만 붙인다.
- anchor가 줄의 일부만 같을 때는 줄 전체 일치(`=`)가 아니라 접두 일치(`case ... in "$ANCHOR"*)`)로 검사한다(263차 devnotes 스크립트에서 발견).
- 샌드박스(bash_tool): `cut -c`는 바이트 단위라 한글 줄을 자르면 도구 출력 전체가 사라지니 파이썬 슬라이스를 쓴다. `sh`는 dash라 `<( )`와 `$'\r'`이 안 되니 bash 스크립트로 실행하고 CR 개수는 `tr -cd '\r' | wc -c`로 센다. 한 명령은 300초 제한이라 pytest나 큰 clone은 `setsid nohup ... < /dev/null &`로 분리한다. `pkill -f "git clone"`은 자기 셸까지 죽이니 쓰지 않는다.
- `toolkit/pytest_ci_setup.sh`는 `/home/claude/repo`를 지우고 carrot-ryu 최신으로 새로 만든다(약 100초~5분). 돌린 뒤 `git rev-parse HEAD`가 기록 커밋과 같은지 먼저 확인한다. pytest는 `-n 0`(xdist 끔) 또는 `-n 4`, `-p no:xdist`는 쓰지 않는다, 기준선 비교에 `-x`를 쓰지 않는다. 저장소 파일을 임시로 고쳤으면 `git checkout`으로 되돌리고 `git status`로 확인한다.
- api.github.com은 rate limit이 자주 걸린다(이 세션도 걸림). `git ls-remote`, blobless clone, SHA 고정 raw로 대체한다. pwsh 버전은 `curl -sIL https://github.com/PowerShell/PowerShell/releases/latest`의 Location 헤더로 얻는다(269cha에 v7.6.6). 270cha에는 이 `releases/latest` 요청이 403으로 막혀 재시도하지 않고, 알고 있던 v7.6.6의 `releases/download/v7.6.6/powershell-7.6.6-linux-x64.tar.gz`를 직접 받아 설치했다(성공).
- 로그 분석: 각 세그먼트 rlog 맨 앞 initData는 logMonoTime이 route 시작 시각이라 t0로 쓰면 안 된다(약 540초 어긋남). `log.capnp`는 `/car.capnp`를 import하니 pycapnp imports에 `opendbc_repo/opendbc/car`를 넣는다. `runtimeTiming`은 logMessage 안 JSON 문자열이다. carrotMan의 desiredSpeed/xSpdLimit와 cruiseTarget은 표시(클러스터) 속도 기준이고 carState.vEgo는 실속도라 vCluRatio(약 0.93)만큼 다르니 같은 기준끼리 비교한다.
- 파일 수정 시각만으로 최신성을 판단하지 않는다(내용은 `grep -c` 등으로 직접 확인). 붙여넣어진 확인 결과 글의 수치는 틀릴 수 있으니 기록 전에 GitHub에서 같은 값을 다시 얻는다(3절).
- 폐루프 시뮬레이션(269cha): `toolkit/cl_sim/` 사용법은 toolkit README 269차 추가. 순서는 `pytest_ci_setup.sh`(약 3~4분) -> `git -C /home/claude/repo fetch --depth 2 origin carrot-ryu` -> `prep_base.sh HEAD~1` -> `cd <작업 폴더>; python3 <cl_sim 경로>/sweep.py`. 쓰고 나면 `long_mpc_base110.py`를 지운다(`git status` 확인). fuzz 160은 약 7분이라 `setsid nohup ... < /dev/null &`로 분리하고, 전체 pytest(`-n 4`)도 약 2~3분이다. 샌드박스 초기화로 `/home/claude`가 사라지므로 세션마다 환경부터 다시 만든다.
- carrot-ryu 고유 차이 추가(270cha): 신호등 인식 보조 계열(`signal_assist`, `signal_start_guard`, `signal_stop_prepare`, `signal_tracking_shadow`, `XState.e2eStopPrepare` 등)이 carrot-ryu에는 통째로 없다. carrot-ms 후속 커밋이 이 계열이면 전제 코드 부재로 같은 분류(263~270차 제외 이력)로 보고, 이식하려면 계열 전체가 필요하다는 점과 종방향 경로 변경이라는 점을 먼저 본다.
- carrot-ryu 고유 차이 추가(269cha): `long_mpc.py`에 거리 기억(`braking_gap_states`)과 편안함 완화(`comfort_path_has_reserve`, 조건부 추가 solve)가 있고 `longitudinal_braking_gap.py`가 신규다. 레이더 `closing_range` 매칭(`primary.py` `_match_closing_range`, `controller.py` 거리 veto 면제)은 코드에 있지만 `EnableRadarTracks` 0/-1에서는 작동하지 않는다. carrot-ms가 이 부분을 바꾸거나 carrot-wip 910bd82를 다시 손보면 따로 대조한다. 업스트림의 `docs/longitudinal_approach_20261011.md`와 `test_radar_corroboration.py`는 가져오지 않았다.
- carrot-ms 점검 도구(268cha): blobless clone(`--filter=blob:none`)에서 `git grep <rev>`는 모든 blob을 내려받아 300초 제한에 걸린다. 파일은 `git show <rev>:<path>` 또는 `git cat-file blob`로 읽고, 패치 적용성은 carrot-ryu 파일만 모은 임시 저장소에서 `git apply --check -v`로 본다.
- carrot-ryu 고유 차이 추가(267cha): `carrot_man.py`의 route 충분 판정이 길이 기준(`route_path_covers_lookahead`, `ROUTE_PATH_COVER_MARGIN_M`)이고 freeze 만료 시 `navi_route_speed_filt`를 지운다. carrot-ms는 점 개수(`ROUTE_PATH_MIN_POINTS`) 기준일 수 있으니 carrot-ms가 `carrot_navi_route()`의 해당 부분을 바꾸면 따로 대조한다.
- 스크립트 작성(267cha, Termux bash): `--depth 1 --filter=blob:none --no-checkout` clone 뒤 `git reset --quiet`, 파일은 체크아웃하지 않고 `git cat-file blob HEAD:<경로>`로 원본 바이트를 읽어 bash 문자열로 1회 매치 치환(`${C%%"$old"*}`/`${C#*"$old"}` 방식, `shopt -u patsub_replacement`), 사전/사후 blob 해시와 numstat를 검사한 뒤 push한다. 이 방식은 CRLF 체크아웃 설정과 무관하다. 시뮬레이션은 로컬 bare에 `uploadpack.allowFilter`/`allowAnySHA1InWant`를 켜고 `file://`로 clone한다. 샌드박스 도구 셸은 `sh`라 `${PIPESTATUS[0]}`가 안 되니 `bash -c`로 감싼다. `carrot_navi_route()`를 직접 돌리는 테스트는 shapely가 필요하다(샌드박스에는 `pip install shapely --break-system-packages`; 없으면 테스트가 건너뛴다). FINDINGS.md는 줄바꿈이 CRLF와 LF가 섞여 있고 최상단 줄들은 CRLF라, 삽입 블록은 CRLF로 넣는다(WIP.md, HANDOFF.md는 LF).
- carrot-ryu 고유 차이(carrot-ms 동기화 시 먼저 대조): `long_mpc.py` 43행 `J_EGO_COST = 12.0`은 upstream 06639e5의 20과 다른 의도된 값이다(시뮬레이터 근거뿐, 실차 검증 없음). `set_weights`에 `j_ego_cost` 인자(5~20 clip)가 있다. `selfdrived.py` 529행은 d082d92에서 upstream d14303d5와 같은 `> 10.`이며, 그 커밋의 modeld 계측은 이식하지 않았다. `application.py`에 54cha 일회성 캡처(`_temp_capture_*`)가 있다. `lateral_planner.py` blob 8f800a4가 53d88ef판과 `deque` import 한 줄만 다르다. carrot-ryu에는 dm2/dm2d/dm2_context, tools/jetlink와 jetlink_status, startup_recovery, hyundai steering_touch/steering_handover, openpilot/common/reboot.py, impact_dashcam/impact_detector, stopping_params, display_scheduling, lane_model_speed가 없다. 후속 carrot-ms 커밋이 이들에 의존하면 먼저 이 차이를 본다.
- HUD 그리는 곳: 하단 좌측 브랜치/모델 문구는 우측 상단(CPU 글자 아래)에 `ui/onroad/augmented_road_view.py`의 `_draw_border_carrot`로 그린다. `HudRenderer._hud_top_right`는 `_draw_set_speed_carrot`가 매 프레임 설정하니 `_draw_carrot_speed_panel`/`_draw_carrot_device_state` 호출 순서를 바꾸기 전에 확인한다.
- 스크립트 작성: PowerShell 래퍼 함수를 `Git`처럼 명령과 대소문자만 다른 이름으로 만들면 무한 재귀로 죽는다(`Invoke-G`/`Invoke-Git`을 쓴다). 스크립트 안 `python -m py_compile`은 저장소 안에 `__pycache__`를 만들어 `git add -A`에 섞이니 `cfile=`을 저장소 밖으로 주고 커밋 전에 `git diff --cached --name-only`로 파일 수를 본다. 스크립트 안의 git 명령은 항상 `-C <clone 경로>`로 대상 저장소를 명시한다(9절 10번). 사용자 PC git 이메일이 기록(ryujmin97@gmail.com)과 다르게 보인 적이 있다(058391e Author ryujmin@naver.com, 기능 영향 없음, `--force` 금지).
- carrot-ryu-v1/v2는 불변이다. 여기에 새 작업이나 devnotes를 얹지 않는다. 폐지된 "carrot-ryu 재생성" 언급을 옛 기록에서 보면 무시한다(219cha).
- 코드 변경이 나오면 5절 순차 전달(코드 스크립트 먼저 -> GitHub 직접 확인 -> devnotes 1회)을 따른다.

다음 작업:
- route 낡은 filt 수정은 110cff9로 반영됐다(위 신규 267cha 항목). 다음은 사용자가 고른다. 새 로그가 있으면 직선 고속도로 route 상한 유지와 진출 램프 감속 과다 여부를 먼저 본다.
- 사용자가 고를 수 있는 것: (1) 1326f21의 옆 차선 오감속 판정용 로그 확보(크루즈 작동 중 비전 단독 앞차, 옆 차선에 차가 많은 도로)와 `radar_gate/release_replay.py`/`margin_scan.py` 재생(코드 변경 없음), (2) 완료(271cha): 기기 `JerkCostEgo` 값 12 확인(결정은 12 유지, 270cha, 코드 변경 없음), (3) 정지 앞차 접근과 내비를 켠 램프 주행 재주행 로그 확보, (4) `test_radar_fault` 처리 결정, (5) carrot-ms b7dd150 이후 신규 커밋 점검(체크포인트 존재 확인부터; 268차 판정은 270차에 모두 확정), (11) 760905a 실차 확인용 주행 로그 확보(앞차와 함께 감속하는 장면, 위 신규 269cha 항목), (9) 353cc8e 시동 직후 로그 확보(기기 `AlwaysLateral`=1은 271cha에 확인), (6) carrot-ryu-v3 보존 시점 지정, (7) d082d92 실차 확인용 주행 로그 확보, (8) Xiaoge 사용 여부 확인(답에 따라 제외 4건 재점검), (10) 110cff9 실차 확인용 재주행 로그 확보(위 신규 267cha 항목).
- 코드 변경이 나오면 사용자 승인 후 5절 순차 전달(코드 스크립트 먼저 -> 확인 -> devnotes 1회)을 따른다.
