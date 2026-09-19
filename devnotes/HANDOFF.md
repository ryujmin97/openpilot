Worker: Claude (100차, Claude Sonnet 5)
Date: 2026-09-20
Repository: ryujmin97/openpilot
Code Branch: carrot-ryu (base: `f87083ec420c1aa28cf059fcba758e3d660bc4d6`, 99차 게이트 반영 이미 push 완료 -- 이번 세션은 테스트 하네스 수정 2줄+4줄 반영 스크립트만 작성/전달, 실행/push 대기)
Note Branch: carrot-ryu-note (base: `044a1d11377f7918cb644b09658558c2a87f5d3f`, 이번 devnotes 반영도 실행/push 대기 -- 반영 후 HEAD는 다음 세션이 git ls-remote로 확인)
carrot-ms 마지막 검토/동기화 체크포인트: `e324f6735d3606800045ed6b28f41e79b17e5498`(변경 없음, 이번 세션 git ls-remote로 재확인) -- 93차와 동일.

작업:
99차에서 반영한 B안(G2T) 리드 감속 게이팅(long_mpc.py, `f87083e`)이 실제로 push까지 완료돼 있음을 재확인하고, 업로드된 실차 로그(9/18, 패치 이전 코드로 기록)로 패치된 코드를 재생 검증. 그 과정에서 게이트 코드 자체는 정상이지만 기존 테스트 39개(2개 파일)가 테스트 하네스 문제로 실패하는 회귀를 발견해, 하네스만 최소 수정.

완료:
1. carrot-ryu `f87083e`, carrot-ms `e324f67` 재확인(변경 없음). HANDOFF.md(99차분)의 "push 대기" 표기가 이미 오래된 정보였음을 `git diff 25f21d4 f87083e`로 확인(변경 파일 long_mpc.py 1개, 99차 설계와 diff 완전 일치) — 정정.
2. 게이트 코드(GATE_*/`_gate_raw`/`process_lead`) 단위검증 도구(`gate_replay.py`, toolkit 미등록 상태) 신규 작성: `_gate_raw` 산식 343점 일치, h<1.5s에서 패치본==기존 비트동일, 하강 1s LPF/상승 즉시, 리드소실 시 해당 인덱스만 리셋, cloudlog 레이트리밋, 극단 입력 안정성 — 전부 통과.
3. `gate_replay.py`로 26개 이벤트 폐루프 A/B: 기존↔98차 수치 재현 일치, 패치↔B안(G2T) 수치 ±0.01 이내 일치(#5/#8/#22 포함). tFollow 짧은 구간(#18~21)은 게이트가 사실상 열려 기존과 동일(안전 방향).
4. 회귀 발견: `test_cutout_mpc_integration.py` 12개, `test_longitudinal_gap_recovery.py` 27개, 합계 39개 실패(기존 `25f21d4`에서는 각각 17/78 전부 통과). 원인은 두 파일 다 `ast`로 production 코드를 직접 `exec`하는 하네스 구조상, (a) 가짜 `process_lead(l)`가 인자 1개만 받음, (b) stub 네임스페이스에 `GATE_*`/`time`/`cloudlog`가 없음 — 실행 코드(long_mpc.py) 자체의 문제 아님.
5. 두 파일에 최소 수정(각각 1~4줄) 설계, SHA 고정 원본(`f87083e`)에서 Replace-Block 앵커 유일 매치 확인, `py_compile` 통과, 실제 `pytest`로 95개 전부 통과 재확인(cereal/opendbc 스키마 포함 sparse clone에서 실행).
6. `test_following_distance.py`/`test_long_mpc_a_change_cost.py`는 `process_lead`/`GATE_` 심볼 미참조를 grep으로 확인(영향 낮음, 실제 실행은 opendbc.can 네이티브 빌드가 샌드박스에 없어 못 함).
7. 반영 스크립트(`100cha_test_fix_carrot_ryu.ps1`) 작성: Replace-Block 패턴, `Get-PythonCmd`+EOF 공급 후 `py_compile` 검증, 전체쓰기 WriteAllText(UTF8 무BOM)+BOM 최종확인, anchor 치환 결과 재확인, 임시폴더 자동삭제. 9절 체크리스트 1~7번 전부 명령 출력과 함께 수행(7번: 전달 파일에서 앵커 재추출 → SHA고정 원본 재시뮬레이션 → 1회 매치/py_compile/실제 pytest 95개 통과까지 재확인).

미완료(다음 세션 최우선):
1. 사용자가 `100cha_test_fix_carrot_ryu.ps1` 실행 → push. 다음 세션은 `git ls-remote`로 carrot-ryu HEAD 변경 확인 → GitHub API/raw로 변경 파일이 테스트 2개뿐이고 diff가 이 세션 설계와 일치하는지 재확인(16절).
2. devnotes 반영 스크립트(`100cha_devnotes_carrot_ryu_note.ps1`, WIP.md 최상단 삽입 + HANDOFF.md 전체교체) 실행/push 확인.
3. 거리 -10/-20 m 스트레스 시나리오를 `f87083e` 패치본 기준으로 재실행(98차는 후보 비교용, 이번엔 실제 반영본 검증용으로 필요).
4. 주행 전체(26개 이벤트 외 구간 포함) 게이트 노출 빈도(g<1 비율) 통계, leadTwo 쪽 게이트 동작 확인(지금까지 leadOne 기준만 확인됨).
5. `gate_replay.py`를 `devnotes/toolkit/lead_decel/`에 정식 등록할지 사용자 확인(14절, 이번 세션은 보류 지시받음).
6. 실차 배포 후 swaglog에서 `lead_gate` 태그 관찰(99차부터 이월) — 특히 tFollow 짧은 구간에서 g가 평상시에도 자주 내려가는지.
7. carrot-ms 4건, 화면녹화 탭 사진 업로드 UI(22·23·26)/Drive 파이프라인(5~10·12·17·18·20·21)/녹화 버튼 깜빡임(28) 실차 검증 이월(97~98차와 동일, 계속 이월 중).

검증: 정적 분석/오프라인 시뮬레이션(단위검증 + 26개 이벤트 폐루프 재생 + pytest 95개)이며 실차 검증: 미실시. `gate_replay.py`의 폐루프도 casadi/IPOPT 복제본(acados 실물 아님)이라 강한 감속을 과소 재현하는 기존 한계(97~98차)가 동일하게 적용된다. PowerShell 구문 자체의 실행 검증은 샌드박스에 pwsh가 없어 못 했다(수동 육안 검토만, Windows PowerShell 5.1 실행 검증도 아님).

주의사항:
- carrot-ryu의 게이트 코드(`f87083e`, long_mpc.py)는 정상이며 이번 세션에서 건드리지 않았다 — 이번 수정 대상은 기존 테스트 하네스 2개 파일뿐이다.
- 39개 회귀는 프로덕션 코드가 아니라 `ast.parse`+`exec` 방식 테스트 하네스의 stub 부족이 원인이다. 앞으로 `process_lead()` 시그니처나 `long_mpc.py` 모듈 상수를 또 바꾸면 같은 종류의 하네스 회귀가 재발할 수 있으니, 반영 스크립트 작성 시 이 두 테스트 파일의 하네스도 함께 점검하는 습관이 필요하다.
- `test_following_distance.py`/`test_long_mpc_a_change_cost.py`의 실제 실행 검증은 여전히 못 했다(cereal capnp 빌드는 됐으나 opendbc.can 네이티브 확장이 샌드박스에 없음). grep으로 낮은 위험만 확인한 상태다.
- `gate_replay.py`는 이번 세션 샌드박스에만 있고 toolkit에 등록되지 않았다 — 세션이 끊기면 사라진다(사용자가 나중에 등록하라고 지시했으므로 의도된 보류).
- HANDOFF.md의 "push 대기" 표기를 실제 상태와 대조 없이 그대로 믿지 않는다(16절) — 이번 세션에서 실제로 오래된 정보였음이 확인됨.

다음 작업 후보:
1. 99cha/100cha 스크립트들 실행 확인 → push 재확인.
2. 스트레스 시나리오(-10/-20 m) + 주행 전체 게이트 노출 통계 + leadTwo 분석 마무리.
3. 실차 배포 후 lead_gate 로그 관찰, 필요시 임계값/tFollow 연동 재설계 논의(99차부터 이월).
4. carrot-ms 4건 + Drive/화면녹화 관련 이월 항목 실차 검증.
