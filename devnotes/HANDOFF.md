Worker: Claude (181차, Claude Sonnet 5)
Date: 2026-09-27
Repository: ryujmin97/openpilot
Code Branch: carrot-ryu (HEAD: 67f41f87fec16ca5626f550c213b4b03eba53c0e, 180차 이후 변동 없음 -- 이번 세션은 코드 변경 없음)
Note Branch: carrot-ryu-note (이 스크립트 실행 직전 HEAD: 619a338b691243d30b6cd16e11754fecc09b21ef, 180차 devnotes 반영 이후 상태)
carrot-ms 마지막 검토·동기화 체크포인트: 087fdca74f0e2c90b7c6b216e913736961ef8c15 (172차와 동일, 변동 없음)

작업:
1. 세션 시작 시 4절 절차대로 지침 문서(0단계, 커밋 619a338b) 및 HANDOFF.md 확인 -- 코드/노트 브랜치 HEAD 모두 기록과 일치, 괴리 없음.
2. 180차 HANDOFF.md 미완료 1순위 c84b175(happymaj11r/openpilot, ajouatom a60f554a7dfb3a229be6fa7ae6715be5c3ae14da cherry-pick, "cores 6/7 저우선순위 배치") GitHub API로 전체 diff(26개 파일, +453/-544) 확보 후 상세 대조.
3. 신규 DisplayScheduler(core6=UI, core7=클러스터 HUD 저우선순위 공유) 구조가 carrot-ryu의 기존 코어 격리 정책(core5=UI+radard, core6=카메라 단독, core7=modeld+plannerd+dmonitoringmodeld 전용)과 구조적으로 충돌함을 확인.
4. 사용자에게 이점/실익 설명 및 카롯 클러스터 HUD/eGPU 사용 여부 확인 -> 미사용 확인, 제외 결정.
5. 181차 devnotes(WIP.md/WIP_SYNC.md 이어붙이기 + HANDOFF.md 교체) 작성.

완료:
1. c84b175 상세 대조 및 구조적 불일치 확인.
2. c84b175 반영 대상에서 완전 제외 확정(WIP_SYNC.md 이월 항목 종결).
3. 181차 devnotes(WIP.md/WIP_SYNC.md/HANDOFF.md) 작성.

미완료:
1. log.capnp @62/@63 필드 타입(UInt8 vs Int32) 정합성 재확인 -- 계속 이월, 다음 세션 1순위.
2. 저위험 소규모 9건, 핵심 발견 68 실차 검증, 163차 게이트 실주행 검증, xTurn=6 로그 확보 -- 계속 이월.
3. pytest CI 환경(conftest.py 포함 실제 cereal 실행) -- 여전히 미실행.
4. docs/camera_sof_gap_20260923.md의 102ms wide-camera BOOT_TS gap 자체 -- 180차에서 이월, 신규 진단 로그로 향후 관측 필요.

검증:
- 이번 세션은 코드 변경 없음(분석 및 devnotes 기록만) -- carrot-ryu HEAD 67f41f87 그대로.
- 실차 검증: 해당 없음(분석 세션).

주의사항:
- c84b175/dcffb7f 두 개별 커밋 이월 항목이 모두 종결됨. 172차 체크포인트에 기록된 "장기 이월 53건 1차 분류" 중 남은 항목은 저위험 9건 + 실차 검증류뿐.
- carrot-ryu의 코어 배치(core5=UI+radard, core6=카메라, core7=모델 스택)는 carrot-ms 최신 기준과 이미 크게 갈라져 있음 -- 향후 carrot-ms에서 코어/스케줄링 관련 신규 커밋이 또 나오면 이번과 같은 구조적 충돌 검토가 반복될 가능성 높음(20절 버전 리셋 시점 판단에 참고할 만한 근거).

다음 작업:
1. log.capnp @62/@63 필드 타입 정합성 재확인 착수(다음 세션 1순위).
2. 저위험 9건/68번 실차 검증 등 장기 이월 항목 순차적 해소 검토.
3. 실차 배포 후 카메라 startup(180차)과 CruiseCoastingPercent(179차) 정상 동작 확인.
