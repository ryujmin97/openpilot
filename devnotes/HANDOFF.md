Worker: Claude (177cha, Claude Sonnet 5)
Date: 2026-09-27
Repository: ryujmin97/openpilot
Code Branch: carrot-ryu (검증 완료 HEAD: 5161837541d07ece15707a2ae6e3458d02befed3, parent d751e15 175차, push 완료 및 GitHub 직접 재확인 완료)
Note Branch: carrot-ryu-note (이 스크립트 실행 로그의 clone 직후 HEAD 참고 -- 176차 devnotes 반영 이후 상태)
carrot-ms 마지막 검토·동기화 체크포인트: 087fdca74f0e2c90b7c6b216e913736961ef8c15 (172차와 동일, 변동 없음)

작업:
1. 176차 HANDOFF 다음 작업 1번(반영 스크립트 작성)을 이어받음.
2. 5개 파일(cruise_coasting.py 신규, longcontrol.py 전체교체, longitudinal_planner.py 앵커치환 6곳, log.capnp, params_keys.h) 대상 Termux bash 반영 스크립트 작성.
3. cereal/log.capnp에 cruiseCoastingTarget @62 :Float32 / cruiseCoastingPercent @63 :Int32 신규 추가, params_keys.h에 CruiseCoastingPercent(PERSISTENT, INT, "0") 신규 추가 -- 176차 devnotes의 "git apply --check 클린 통과" 기록이 실제 반영이 아니라 dry-run이었음을 확인한 뒤, 코드 사용처 기준으로 최소 재구성해 추가.
4. 로컬 bare 저장소로 스크립트 전체(clone→base drift guard→파일작성→py_compile→commit→push) 실제 실행 검증, 재실행 시 base drift guard 정상 중단도 확인.
5. 사용자 Termux 실행("완료" 보고) 후 그대로 신뢰하지 않고 git ls-remote + SHA고정 raw 조회로 직접 재확인.

완료:
1. 0006296 핵심 코드 5개 파일 carrot-ryu 반영 및 push 완료.
2. GitHub 직접 재확인 완료(HEAD 5161837, parent d751e15, 5개 파일 내용 일치).
3. 이 devnotes(177차) 기록을 carrot-ryu-note에 반영(이 스크립트로 실행).

미완료:
1. test_cruise_coasting.py 복원 반영.
2. carrot_settings.json UI 노출, test_settings_schema.py(설정 개수 183→184 불일치 재확인 포함).
3. log.capnp @62/@63 필드가 원본 0006296 patch 번호와 실제 일치하는지 -- 남은 patch 조각(1번) 반영 시 확인 필요.
4. c84b175(CPU 스케줄링), dcffb7f(카메라 SOF) 상세 대조 -- 미착수, 계속 이월.
5. 저위험 소규모 9건, 핵심 발견 68 실차 검증, 163차 게이트 실주행 검증, xTurn=6 로그 확보 -- 계속 이월.
6. pytest CI 환경(conftest.py 포함 실제 cereal 실행) -- 여전히 미실행(환경 제약 지속).

검증:
- 코드 반영 스크립트: 로컬 bare 저장소 시뮬레이션(실제 clone→적용→py_compile→commit→push) 통과, push된 커밋을 재-clone해 5개 파일 내용 재확인.
- GitHub 재확인: git ls-remote(carrot-ryu HEAD 5161837) + SHA고정 raw 조회(5개 파일 각각) 일치 확인.
- 실차 검증: 미실시(12절).

주의사항:
- log.capnp/params_keys.h는 원본 0006296 patch diff 그대로가 아니라 코드 사용처 기반 재구성임 -- 원본 patch를 나중에 다시 열어 필드 번호/설정 그룹이 다르면 그때 정합성 재확인 필요.
- test_ci_check.py/test_generate.py는 여전히 반영 범위 밖(176차와 동일 이유).

다음 작업:
1. test_cruise_coasting.py 복원 및 반영 스크립트 작성(기존 make_cp() 픽스처 보정 포함, 176차에서 이미 확인된 내용).
2. carrot_settings.json/test_settings_schema.py 반영 검토(183→184 설정 개수 불일치 먼저 재확인).
3. c84b175, dcffb7f 순차 검토 착수.
