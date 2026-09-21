Worker: Claude (126차, Claude Sonnet 5)
Date: 2026-09-22
Repository: ryujmin97/openpilot
Code Branch: carrot-ryu (`a0f4c5a5fb932be1525311d2ed61f5382a4bd6d2`, 123차 C그룹 dead code 삭제. 이번 세션 코드 변경 없음)
Note Branch: carrot-ryu-note (이 스크립트 반영 전 base `1412328...`(125차 devnotes push 확인 완료). 반영 후 HEAD는 다음 세션이 git ls-remote로 확인)
carrot-ms 마지막 검토/동기화 체크포인트: `e324f67`(93~95차). 이번 세션도 carrot-ms 신규 커밋 확인/동기화 작업 없음 -- 여러 세션째 최우선 이월 중.

작업:
1. 125차 미완료 3번(`test_latcontrol.py::test_saturation`의 `TypeError` 원인/도입 시점 조사)을 이어받아 완료.
2. carrot-ryu(`a0f4c5a5f`)를 blobless partial clone해 대상 5개 파일(`controls/tests/test_latcontrol.py`, `controls/lib/latcontrol.py`/`latcontrol_pid.py`/`latcontrol_torque.py`/`latcontrol_angle.py`, `controls/lib/tests/test_latcontrol.py`)의 `git log --oneline` 확인 -- 전부 61차 리셋의 단일 스쿼시 커밋 이후 carrot-ryu 자체 이력에서 수정된 적 없음을 확인.
3. happymaj11r/openpilot(carrot-ms, `3756e6d`)와 ajouatom/openpilot(carrot-wip, `3d93b7e`)에서 동일 5개 파일을 직접 raw 조회해 carrot-ryu와 byte 단위 대조 -- 전부 동일함을 확인.
4. 원인 확정: 이 `TypeError`(3-인자 호출 vs 실제 2-인자 생성자)는 carrot-ryu의 61차 리셋이나 그 이후 반영 과정에서 생긴 회귀가 아니라, carrot-wip 원본 자체에 이미 존재하던 깨진 테스트가 carrot-ms를 거쳐 변경 없이 상속된 것.
5. 부수 발견: `controls/lib/tests/test_latcontrol.py`라는 별도의 중복 테스트 파일이 옛날 opendbc 4-튜플 인터페이스 API를 사용해 그 나름대로 깨져 있음을 확인(이것도 원본에 동일 존재).

완료:
1. HANDOFF.md 125차 미완료 3번("`test_latcontrol.py` 시그니처 불일치 원인/도입 시점 확인 필요")을 원인 확정으로 해소 -- carrot-ryu 회귀가 아니라 원본(carrot-wip/carrot-ms)부터 존재하던 문제로 결론.
2. WIP.md 126차 신규 항목, FINDINGS.md 핵심 발견 49, CURRENT_STATUS.md 126차 항목 추가.

미완료(다음 세션 최우선):
1. 이 스크립트(`126cha_test_latcontrol_root_cause_devnotes.ps1`) 실행/push 확인 -- GitHub SHA 고정 조회로 재확인(16절).
2. carrot-ms 신규 커밋 확인(2절) -- 93~95차 체크포인트(`e324f67`) 이후 여전히 미확인, 여러 세션째 이월 중(최우선).
3. `test_latcontrol.py` 두 파일(원인이 확정된 상태) 자체를 carrot-ryu 로컬에서 고칠지 여부 -- 이번 세션에서는 원인 확정만 하고 수정은 보류했다. 고치기로 하면: (a) `controls/tests/test_latcontrol.py`는 생성자 호출을 2-인자로 맞추거나 DBC 미생성 차량(HONDA/TOYOTA/NISSAN)까지 함께 걸리는 문제라 opendbc DBC 생성 단계 보강과 같이 볼지 판단 필요, (b) `controls/lib/tests/test_latcontrol.py`는 죽은 중복 파일로 보여 DEAD_CODE_REVIEW 대상으로 편입할지 검토 가능. 실차 로직과 무관해 우선순위 낮음.
4. 110차 GATE_M 0.8/1.0, 114차 MAP_TURN_GUIDE_FACTOR 1.00 -- 둘 다 실차 미검증.
5. CURRENT_STATUS.md 97~114차 구간 상세 catch-up -- 여러 세션째 이월 중(122차부터).
6. (선택, 낮은 우선순위) opendbc 일부 차량 DBC 생성 단계를 `pytest_ci_setup.sh`에 추가하면 `test_latcontrol.py`/`test_longitudinal_gap_recovery.py`의 opendbc 파생 실패를 더 줄일 수 있음.

검증: carrot-ryu/carrot-ms/carrot-wip 3개 저장소 직접 조회(blobless partial clone + raw 조회) 및 5개 파일 byte 단위 대조로 원인 확정(11절: 추측 아님, 원본 확인). 실차 검증: 해당 없음(코드 변경 없음, 정적 테스트 인프라 원인 조사).

주의사항:
- 코드 변경 없음(devnotes만).
- 이번 조사로 "carrot-ryu 회귀 여부"는 명확히 해소됐지만, 테스트 파일 자체를 고칠지는 아직 미결정 상태 -- 실차와 무관한 낮은 우선순위 항목으로 다음 세션 이월.
- carrot-ms 동기화(2절) 미확인이 이제 여러 세션째 가장 오래 이월된 항목이므로 다음 세션은 이것부터 착수 권장.

다음 작업 후보:
1. carrot-ms 신규 커밋 확인(2절) 착수 -- 최우선 권장.
2. `test_latcontrol.py` 두 파일 수정 여부 결정 및 반영(사용자 승인 시).
3. 110차/114차 실차 관찰 항목.
