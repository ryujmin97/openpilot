Worker: Claude (125차, Claude Sonnet 5)
Date: 2026-09-22
Repository: ryujmin97/openpilot
Code Branch: carrot-ryu (`a0f4c5a5fb932be1525311d2ed61f5382a4bd6d2`, 123차 C그룹 dead code 삭제. 이번 세션 코드 변경 없음)
Note Branch: carrot-ryu-note (이 스크립트 반영 전 base `3f4882f671b69a7b6d338f1ad3e0fe04d0fe0526`, 124차 catch-up. 반영 후 HEAD는 다음 세션이 git ls-remote로 확인)
carrot-ms 마지막 검토/동기화 체크포인트: `e324f67`(93~95차). 이번 세션도 carrot-ms 신규 커밋 확인/동기화 작업 없음 -- 여전히 최우선 이월.

작업:
1. 124차에서 도구 호출 한도로 중단됐던 pytest CI 환경 구성을 이어받아 완료: acados OCP 솔버(`long_mpc.py`) 코드생성 -- `ACADOS_SOURCE_DIR`/`ACADOS_PYTHON_INTERFACE_PATH`/`TERA_PATH` 환경변수를 acados wheel(comma-deps-acados) 실제 설치 경로로 지정해 해결 -- 및 gcc 링크/Cython 컴파일까지 전부 완료.
2. conftest.py가 import하는 `msgq.ipc_pyx`도 동일 방식(Cython/C++ Extension)으로 컴파일.
3. 목표 테스트(`test_lead_gate_margin.py`, `test_map_turn_guide_factor.py`)를 실제 `pyproject.toml` addopts(pytest-cpp/randomly/xdist/asyncio 전부 로드) 조건으로 실행 -- 23/23 통과.
4. 범위를 `openpilot/selfdrive/controls/tests/`+`openpilot/selfdrive/carrot/tests/` 전체로 넓혀 실행(1928 passed/59 failed/85 errors), 실패/에러 표본을 확인해 대부분 샌드박스 환경 한계(pyray 미설치/OpenCV·ONNX 버전 불일치/일부 opendbc 차량 DBC 미생성)임을 확정, `test_latcontrol.py::test_saturation`의 시그니처 불일치(TypeError) 1건은 원인 미조사인 채로 발견 기록.
5. 전체 재현 절차를 `devnotes/toolkit/pytest_ci_setup.sh`로 등록, 완전 재초기화된 컨테이너에서 스크립트만으로 동일 결과가 재현됨을 재확인.

완료:
1. HANDOFF.md 124차 미완료 4번("pytest를 실제 CI 조건으로 실행한 적이 없음")을 해소 -- 목표 테스트 23/23 통과, 재사용 스크립트 등록까지 완료.
2. WIP.md 125차 신규 항목, toolkit/README.md 125차 섹션, toolkit/pytest_ci_setup.sh 신규 파일, CURRENT_STATUS.md 125차 항목 추가.

미완료(다음 세션 최우선):
1. 이 스크립트(`125cha_pytest_ci_devnotes.ps1`) 실행/push 확인 -- GitHub SHA 고정 조회로 재확인(16절).
2. carrot-ms 신규 커밋 확인(2절) -- 93~95차 체크포인트(`e324f67`) 이후 여전히 미확인, 여러 세션째 이월 중.
3. `test_latcontrol.py::test_saturation`의 `LatControlPID/Torque/Angle(CP, CI, DT_CTRL)` 3-인자 호출 vs 실제 `(CP, CI)` 2-인자 생성자 불일치 -- `git log -p`로 `latcontrol*.py`/`test_latcontrol.py` 변경 이력 대조해 언제부터/왜 어긋났는지 확인 필요(11절: 아직 추측 단계, 회귀인지 원래부터 stale이었는지 불명).
4. 110차 GATE_M 0.8/1.0, 114차 MAP_TURN_GUIDE_FACTOR 1.00 -- 둘 다 실차 미검증.
5. CURRENT_STATUS.md 97~114차 구간 상세 catch-up -- 여러 세션째 이월 중(122차부터).
6. (선택, 낮은 우선순위) opendbc 일부 차량 DBC 생성 단계를 `pytest_ci_setup.sh`에 추가하면 `test_latcontrol.py`/`test_longitudinal_gap_recovery.py`의 opendbc 파생 실패를 더 줄일 수 있음 -- 이번 세션 범위 밖으로 보류.

검증: 실제 pytest 실행(23/23 목표 테스트, 확장 실행 1928/59/85), 완전 재초기화 컨테이너에서 스크립트 재현으로 이중 확인. 실차 검증: 해당 없음(코드 변경 없음, 정적 테스트 인프라 작업).

주의사항:
- 코드 변경 없음(devnotes + toolkit 스크립트만).
- pytest_ci_setup.sh는 Claude 샌드박스 전용이며 콤마 디바이스/사용자 PC와 무관.
- `test_latcontrol.py` 발견 사항은 "테스트가 깨져있다"는 사실만 확정된 것이고, 프로덕션 코드(`latcontrol_*.py`)의 실제 동작 결함인지는 별개 -- 혼동 주의.

다음 작업 후보:
1. carrot-ms 신규 커밋 확인(2절) 착수.
2. test_latcontrol.py 시그니처 불일치 원인 조사.
3. 110차/114차 실차 관찰 항목.
