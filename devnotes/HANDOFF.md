Worker: Claude (175cha, Claude Sonnet 5)
Date: 2026-09-27
Repository: ryujmin97/openpilot
Code Branch: carrot-ryu (반영 완료 HEAD: d751e15ec0d5ab28022d28d7de4a6be9022b125d, 175차 -- 1ae25ef 반영 완료, GitHub 직접 재확인함, parent dcf43ead29d1f296f6861ba90710d88fb9564576)
Note Branch: carrot-ryu-note (이 스크립트 반영 전 HEAD: 38833bb497326f90ed91257daf1ae08efd8bc45e, 174차 상태)
carrot-ms 마지막 검토·동기화 체크포인트: 087fdca74f0e2c90b7c6b216e913736961ef8c15 (172차와 동일, 변동 없음 -- 이번 세션도 신규 커밋 재점검 아님)

작업:
1. 세션 시작 시 지침 문서(v2, 38833bb) 재확인, 174차 HANDOFF 다음 작업 1번(중간 우선순위 4건)을 이어받음.
2. `1ae25ef`(radar path normals 안정화) 상세 대조: carrot-ms 원본 5개 파일 중 Kia Carnival 전용 조사 문서 2개 제외, 실제 반영 대상 3개 파일(+125)로 확정.
3. `git apply --check` 재현 -- `predictor.py`만 실패, 원인은 121차 dead-code batch B의 `_radar_path` 제거(WIP_SYNC.md 기존 "161~162차 영역" 추정 메모는 부정확했음을 재분석으로 정정).
4. `_terminal_path_tangent` 신규 함수 + `_project_to_model_path_cached` 보정 로직을 `_radar_path` 의존 없이 블록치환으로 수동 이식(anchor 1회 매치 확인).
5. `py_compile` 통과, 신규 pytest 5개(순수 기하 로직) 컨테이너 직접 실행 전부 통과, 기존 회귀 테스트 무변화 확인. 컨트롤러 레벨 테스트 1개는 cereal Cython 빌드 환경 부재로 미실행(6번 이월과 동일 제약).
6. 로컬 bare 저장소로 스크립트 전체(clone->apply->블록치환->py_compile/json 검증->commit->push) 실행 검증 -- `git add -A`가 `py_compile`의 `__pycache__/*.pyc`까지 커밋에 포함시키는 버그를 발견해 대상 3개 파일 명시적 add로 수정 후 재실행, `3 files changed, 125 insertions(+)`로 의도한 결과만 커밋됨을 확인.
7. 사용자가 Termux에서 스크립트(`175cha_code_carrot_ryu.sh`)를 실행("push됨") 보고 후, 이를 그대로 신뢰하지 않고 `git ls-remote` + 로컬 shallow clone으로 carrot-ryu를 직접 재조회 -- HEAD `d751e15`, parent `dcf43ea`, stat `3 files changed, 125 insertions(+)`로 시뮬레이션/원본과 정확히 일치함을 확인(16절).
8. 남은 중간 우선순위 3건(`0006296`/`c84b175`/`dcffb7f`)의 patch를 happymaj11r/openpilot에서 확보하고 1차 관련성 triage 수행.
9. `0006296`(크루즈 코스팅 마진)을 carrot-ryu 현재 HEAD(`d751e15`)에 `git apply --check` -- 16개 파일 중 13개 통과, `longitudinal_planner.py`는 carrot-ryu의 `cutin_predecel_limit`/`force_slow_decel`/`accel_limits_turns` 커스텀 로직으로 인해 컨텍스트 불일치 확인(수동 병합 필요). `test_ci_check.py`/`test_generate.py`도 carrot-ryu 자체 확장 목록으로 불일치.
10. 사용자 판단에 따라 이번 세션은 devnotes(175차) 정리로 마무리, 나머지 3건 상세 병합은 다음 세션(176차)으로 이월.

완료:
1. 중간 우선순위 4건 중 1건(`1ae25ef`) carrot-ryu 반영 완료 -- GitHub 직접 재확인: `d751e15`, parent `dcf43ea`, `3 files changed, 125 insertions(+)`.
2. 남은 3건(`0006296`/`c84b175`/`dcffb7f`) patch 확보 및 1차 관련성 triage 완료.

미완료:
1. `0006296`(크루즈 코스팅 마진) `longitudinal_planner.py` 수동 병합 -- 미착수, 앵커 불일치만 확인됨(176차 후보).
2. `c84b175`(CPU 스케줄링), `dcffb7f`(카메라 SOF) 상세 대조 -- 미착수.
3. 저위험 소규모 9건(Carrot Web UI 3건, 로그/안내 2건, AGNOS 업데이트 2건, navi 감속 2건) -- 미착수(172차부터 이월).
4. 핵심 발견 68 실차 검증 -- 계속 이월(171차부터).
5. 163차(게이트 완전 제거) 실주행 검증 -- 계속 이월.
6. xTurn=6(톨게이트) 로그 확보 -- 여전히 미확보(114차부터 이월).
7. pytest CI 환경(conftest.py 포함 실제 실행) -- 이번 세션도 시도하지 않음(환경 제약 지속, 124차부터 이월).
8. 110차 GATE_M 0.8/1.0, 114차 MAP_TURN_GUIDE_FACTOR=1.00 실차 미검증(이월).
9. WIP_SYNC.md에 1ae25ef 원인 재분석 정정 반영 -- 미착수.

검증:
- `1ae25ef`: `git apply --check` 재현(2/3 파일 통과, predictor.py만 원인 재분석), 블록치환 anchor 1회 확인, `py_compile` 통과, 신규 pytest 5개 컨테이너 실행 전부 통과, 로컬 bare 저장소 clone->apply->commit->push 시뮬레이션 numstat 일치, 사용자 실행 후 GitHub 직접 재조회로 실제 push(`d751e15`) 확인.
- `0006296`: `git apply --check`로 13/16 파일 통과 확인, 나머지 3개 파일은 컨텍스트 불일치 원인까지 특정(코드 변경은 아직 없음).
- pytest 실제 실행(컨트롤러 레벨): 미실시(환경 제약, 이월 7번과 동일).
- 실차 검증: 미실시(12절).

주의사항:
- WIP_SYNC.md의 1ae25ef 관련 기존 메모("161~162차 영역"으로 원인 추정)가 부정확했음을 이번 세션 재분석으로 확인함. 실제 원인은 121차 dead-code batch B의 `_radar_path` 제거이며, WIP_SYNC.md 갱신이 아직 반영되지 않았으니 다음 세션에서 정정 필요.
- `git add -A` 방식은 `py_compile` 부산물(`__pycache__/*.pyc`)까지 커밋에 끼워넣을 수 있음을 175차에서 확인 -- 반영 스크립트 템플릿은 대상 파일 명시적 `git add`를 기본값으로 유지할 것.
- `0006296`은 13/16 파일이 깨끗이 적용되지만 핵심 종방향 제어 파일(`longitudinal_planner.py`)은 carrot-ryu 자체 커스텀 로직(`cutin_predecel_limit` 등) 때문에 수동 병합이 필요하며, 1ae25ef보다 작업량이 클 것으로 예상됨.

다음 작업:
1. `0006296`(크루즈 코스팅 마진) `longitudinal_planner.py` 수동 병합 상세 설계(176차 후보).
2. 이어서 `c84b175`(CPU 스케줄링), `dcffb7f`(카메라 SOF) 순차 검토.
3. WIP_SYNC.md에 `1ae25ef` 원인 재분석 정정 반영.
4. 저위험 소규모 9건, 핵심 발견 68 실차 검증 등 계속 이월.
