Worker: Claude (180cha, Claude Sonnet 5)
Date: 2026-09-27
Repository: ryujmin97/openpilot
Code Branch: carrot-ryu (검증 완료 HEAD: 67f41f87fec16ca5626f550c213b4b03eba53c0e, parent c70dad323746a265be3b68939721e69845d5e9ff (dcffb7f cherry-pick), parent 005f1202 (179차), push 완료 및 GitHub 직접 재확인 완료)
Note Branch: carrot-ryu-note (이 스크립트 실행 직전 HEAD: 6ed55774a175facb47c0d8d0747362db54cff265, 179차 devnotes 반영 이후 상태)
carrot-ms 마지막 검토·동기화 체크포인트: 087fdca74f0e2c90b7c6b216e913736961ef8c15 (172차와 동일, 변동 없음)

작업:
1. 세션 시작 시 4절 절차대로 지침 문서(0단계, 커밋 6ed5577)와 HANDOFF.md 확인.
2. GitHub 실제 carrot-ryu HEAD(c70dad323)가 HANDOFF.md 기록(005f1202, 179차)보다 앞서 있음을 발견 -- 16절 해당 괴리로 사용자에게 보고.
3. c70dad323 diff를 원본 happymaj11r dcffb7f(ajouatom 7bdd374e cherry-pick)와 직접 대조해 내용 확인 -- 카메라 startup phase(staggered_sof=false) 수정 + SOF 타이밍 진단 로직 + 문서.
4. 원본 대비 .github/workflows/tests.yaml, AGENTS.md 2개 파일이 cherry-pick에서 빠져있음을 발견해 사용자에게 확인 -> 추가 반영 결정.
5. 두 파일에 대한 Termux 반영 스크립트 작성, 로컬 bare mirror dry-run 검증 후 전달.
6. 사용자 실행 로그 확인 후 GitHub 직접 재확인(16절) -- 67f41f87.
7. 180차 devnotes(WIP.md/WIP_SYNC.md 이어붙이기 + HANDOFF.md 교체) 작성.

완료:
1. dcffb7f cherry-pick 전체(카메라 startup phase 수정 + SOF 진단 + 문서) devnotes 소급 기록.
2. .github/workflows/tests.yaml(진단 테스트 CI 스텝), AGENTS.md(이슈 요약 메모) 추가 반영 및 push, GitHub 직접 재확인 완료.
3. WIP_SYNC.md 이월 항목 dcffb7f 해소 기록.
4. 180차 devnotes(WIP.md/WIP_SYNC.md/HANDOFF.md) 작성 및 carrot-ryu-note 반영.

미완료:
1. c84b175(CPU 스케쥴링) 상세 대조 -- 미착수, 계속 이월.
2. log.capnp @62/@63 필드 타입(UInt8 vs Int32) 정합성 재확인 -- 계속 이월.
3. 저위험 소규모 9건, 핵심 발견 68 실차 검증, 163차 게이트 실주행 검증, xTurn=6 로그 확보 -- 계속 이월.
4. pytest CI 환경(conftest.py 포함 실제 cereal 실행) -- 여전히 미실행.
5. docs/camera_sof_gap_20260923.md의 102ms wide-camera BOOT_TS gap 자체 -- 이번 수정 대상 아님, 신규 진단 로그로 향후 관측 필요.

검증:
- 코드(180차): c70dad323/67f41f87 두 커밋 모두 SHA 고정 raw/git show 조회로 실제 내용을 upstream 원본과 직접 대조해 확인. 67f41f87는 전달 전 로컬 bare mirror dry-run(anchor 단일매치, 삽입 결과 확인)까지 거침.
- 실차 검증: 미실시(12절) -- 다음 실주행에서 카메라 부팅이 raw frame 41 fallback 없이 정상 동기화되는지 확인 필요.

주의사항:
- 이번 괴리(코드 push 완료, devnotes 미기록 상태로 세션 종료)가 재발하지 않도록, 17절 "세션 종료 전 devnotes 기록" 원칙을 특히 코드 반영 직후 세션이 끝날 가능성이 있는 경우 더 엄격히 적용할 필요.
- .github/workflows/tests.yaml은 carrot-ryu 자체 CI 스텝 구성이 upstream과 이미 다르므로(json11/acados 등 carrot-ryu 고유 테스트), 향후 upstream CI 변경을 반영할 때마다 앵커 위치를 매번 재확인해야 함.

다음 작업:
1. c84b175(CPU 스케쥴링) 상세 대조 착수.
2. log.capnp @62/@63 필드 타입 정합성 재확인.
3. 저위험 9건/68번 실차 검증 등 장기 이월 항목 순차적 해소 검토.
4. 실차 배포 후 카메라 startup(180차)과 CruiseCoastingPercent(179차) 정상 동작 확인.
