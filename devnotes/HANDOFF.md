Worker: Claude (179cha, Claude Sonnet 5)
Date: 2026-09-27
Repository: ryujmin97/openpilot
Code Branch: carrot-ryu (검증 완료 HEAD: 005f1202b3bd1139ca97195e7cda716e70f35588, parent 107279570bc9110fc58b9937707f9ae448343c51 (178차), push 완료 및 GitHub 직접 재확인 완료)
Note Branch: carrot-ryu-note (이 스크립트 실행 직전 HEAD: 8477bb059ef54e7ccd812ccdce834073f7f6ecf3, 178차 devnotes 반영 이후 상태)
carrot-ms 마지막 검토·동기화 체크포인트: 087fdca74f0e2c90b7c6b216e913736961ef8c15 (172차와 동일, 변동 없음)

작업:
1. 세션 시작 시 4절 절차대로 지침 문서(0단계)와 HANDOFF.md 확인(22차 버전 지침 확인 보고 포함).
2. 178차 HANDOFF 다음 작업 1번 이어받음: carrot_settings.json UI 노출 + test_settings_schema.py 183→184 불일치 재확인.
3. happymaj11r/openpilot 0006296 커밋 원문을 직접 조회해 carrot_settings.json/params_keys.h/log.capnp/test_settings_schema.py diff 전체 확보, CruiseCoastingPercent 관련 부분과 RadarTrackFlip(무관 번들 설정) 부분을 구분.
4. carrot_settings.json에 CruiseCoastingPercent 그룹 멤버십/파라미터 정의 블록 추가, test_settings_schema.py에 가드 테스트 추가하는 Termux 스크립트 작성, 실제 GitHub 최신 HEAD로 프레시 clone해 편집 로직 dry-run 검증 후 전달.
5. 사용자 실행 로그(push 성공) 확인 후 GitHub 직접 재확인(16절).

완료:
1. carrot_settings.json에 CruiseCoastingPercent 노출(CRUISE_CARROT 그룹 멤버십 + 파라미터 정의, min0/max10/default0/percent).
2. test_settings_schema.py에 가드 테스트 추가(test_cruise_coasting_percent_is_exposed_in_carrot_cruise_group).
3. carrot-ryu push 및 GitHub 직접 재확인 완료(005f1202).
4. 179차 devnotes(WIP.md/WIP_SYNC.md 이어붙이기 + HANDOFF.md 교체) 작성 및 carrot-ryu-note 반영(이 스크립트로 실행).

미완료:
1. log.capnp @62/@63 필드가 원본 0006296 patch와 실제 일치하는지(타입 불일치 발견: 원본 UInt8 vs carrot-ryu Int32).
2. c84b175(CPU 스케쥴링), dcffb7f(카메라 SOF) 상세 대조 — 미착수.
3. 저위험 소규모 9건, 핵심 발견 68 실차 검증, 163차 게이트 실주행 검증, xTurn=6 로그 확보 — 계속 이월.
4. pytest CI 환경(conftest.py 포함 실제 cereal 실행) — 여전히 미실행(환경 제약 지속).

검증:
- 코드(179차): 스크립트 전달 전 실제 HEAD(1072795)로 dry-run 편집 검증(anchor 단일매치, JSON 유효성, py_compile 통과), 사용자 push 후 SHA 고정(005f1202) raw 조회로 두 파일 실제 내용 재확인. pytest는 환경 제약으로 미실행, 신규 assertion은 수동 재현으로 통과 확인.
- devnotes(179차): Termux bash 스크립트로 WIP.md/WIP_SYNC.md anchor 이어붙이기 + HANDOFF.md 전체 교체 → commit/push, 실행 로그와 GitHub 재조회로 반영 확인 예정(사용자 실행 후).
- 실차 검증: 미실시(12절).

주의사항:
- log.capnp 필드 타입(UInt8 vs Int32) 불일치는 현재 carrot-ryu 자체 동작에는 영향 없으나, 향후 0006296 원본 patch의 다른 부분(예: 다른 필드와의 상호작용)을 반영할 때 반드시 재확인 필요.
- 0006296 커밋은 여러 설정이 번들된 형태(예: RadarTrackFlip)라서, 향후 다른 upstream 커밋을 반영할 때도 컮밋 단위가 아니라 기능 단위로 재검토하는 습관이 필요함(10절 최소 변경 원칙과 연계).

다음 작업:
1. log.capnp @62/@63 필드 타입/번호 정합성을 원본 0006296 patch와 다시 대조(UInt8→Int32 변경이 실제 문제를 일으키는지 평가).
2. c84b175, dcffb7f 순차 검토 착수.
3. 저위험 9건/68번 실차 검증 등 장기 이월 항목 순차적 해소 검토.
