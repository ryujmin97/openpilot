Worker: Claude (111차, Claude Sonnet 5)
Date: 2026-09-20
Repository: ryujmin97/openpilot
Code Branch: carrot-ryu (base `a430d114f17e8b9579392071f7828324cc8bb329`, 110차 GATE_M_LO/HI 0.8/1.0. 이번 세션 코드 변경 없음 -- SHA 고정 조회 + 격리 pytest로 110차 반영을 독립 재검증만 수행)
Note Branch: carrot-ryu-note (base `bf20985ed47844ed7fa5af3865e6dac314f8c38f`, 110차 devnotes. 이번 111차 devnotes 반영은 실행/push 대기 -- 반영 후 HEAD는 다음 세션이 git ls-remote로 확인)
carrot-ms 마지막 검토/동기화 체크포인트: `a23a77b1aa8b007d6b22bb19f2a1992b84d9b7d4`(111차 확정, e324f67 이후 신규 21건 전수 분류 -- 전부 반영 보류)

작업:
110차 코드/devnotes 반영(a430d11/bf20985)을 SHA 고정 조회 + 격리 pytest로 독립 재검증(문제 없음 확인). 이어서 2절 carrot-ms 동기화 점검을 수행해 e324f67(93/95차 체크포인트) 이후 신규 21건(happymaj11r 대비 carrot-wip에 없는 고유 커밋, merge-base로 확인)을 전수 분류. 블루투스 리모컨/Cinque v3(14건), World Model 실험 문서(2건, 코드 변경 없음), Hyundai CAN FD 전용 리드표시 보정(1건, DH는 LEGACY라 무관), C3 eGPU 이미지/워프 검증(4건, eGPU 미보유) 전부 사용자 확인 후 제외 확정. AGNOS 19.8-carrot-bt1(블루투스 리모컨용 트라이얼 빌드, 검증 미완료)도 동일 사유로 제외. 상세는 WIP.md 111차, WIP_SYNC.md 111차 체크포인트.

완료:
1. 110차 반영 재검증 완료 -- carrot-ryu `a430d11`이 `67b0aa9` 위에 커밋 1개, long_mpc.py 70행 `GATE_M_LO, GATE_M_HI = 0.8, 1.0` 확인, BOM 없음, 격리 pytest 8 passed. carrot-ryu-note `bf20985`이 `abcda6c` 위에 커밋 1개, WIP.md/HANDOFF.md 110차 표기 일치. 브랜치 구성(carrot-ryu/carrot-ryu-note/carrot-ryu-v1) 1절과 일치.
2. carrot-ms 2절 점검 완료: 체크포인트 e324f67 -> a23a77b 갱신, 신규 21건 전수 분류/제외 확정, WIP_SYNC.md 기록.

미완료(다음 세션 최우선):
1. 이 devnotes 반영 스크립트(carrot-ryu-note) 실행 로그 확인 -> SHA 고정 조회로 재확인(16절).
2. 실차 배포(디바이스 pull) 시점 -- 사용자 확인 후. 배포 후 swaglog lead_gate의 g/m 관찰(110차 GATE_M 0.8/1.0).
3. 견고성 스윕 재개(94 km/h -3, 60 km/h -5, 110 km/h -5, 94 km/h -7, g0=0; 이전 채팅에서 72건 중 6건만 완료, 결과 미확인)와 g0=0에서 0.9/1.1·none 결과표 -- 선택.
4. (선택, 보류) vE 기준 need-cap 재설계, TTC 변화율 후보. 104차 기록 부재, CURRENT_STATUS.md 99차 게이트 항목 정리, 화면녹화 탭/Drive 파이프라인 실차 검증 -- 계속 이월. CURRENT_STATUS.md는 이번 세션도 갱신하지 않음.
5. carrot-ms 다음 신규 커밋 여부는 필요 시 가벼운 git ls-remote 점검(체크포인트는 a23a77b로 최신화됨). AGNOS가 안정판(비-bt1)으로 나오면 재검토.

검증: 정적 조회만 수행(git ls-remote/clone/rev-list/merge-base/diff, 격리 pytest). 코드 변경 없음, 실차 검증: 해당 없음(이번 세션은 코드 변경이 없음). 110차 GATE_M 0.8/1.0 자체의 실차 검증은 여전히 미실시.

주의사항:
- (110차 이월) GATE_M 0.8/1.0의 완화폭은 복제본 기준이며 실차 -4.0의 약 10% 수준이고, 복제본 폐루프가 강한 리드 감속에서 실차보다 약함(seg 113 -2.6 vs -4.0)이라 실제 효과 크기는 불확실. 급제동 표본은 seg 113 1건. 위험 상황 감속이 늦게 느껴지면 0.9/1.1 또는 1.0/1.2로 먼저 검토, 되돌리려면 `git revert a430d11`(105차 값 1.0/1.2로 복귀). 105차 게이트 커밋 자체를 revert하면 `f78e51e`.
- carrot-ms의 AGNOS_VERSION이 19.8-carrot-bt1로 바뀐 것은 기록만 해두었고 반영하지 않음 -- 블루투스 리모컨용 트라이얼 빌드이며 디바이스 OS 이미지 전체 교체라는 점에서 안정판이 나올 때까지 보류.
- 채팅에 붙여넣어진 외부 분석은 3절 원칙대로 항상 재검증할 것(과거 109차에 존재하지 않는 SHA를 언급한 리뷰 코멘트 사례 있었음).

다음 작업 후보:
1. 반영 확인 -> 실차 배포 후 lead_gate 로그 관찰 -> 필요 시 GATE_M 상수 조정(0.9/1.1 또는 복귀).
2. carrot-ms 후속 신규 커밋 발생 시 2절 재점검, AGNOS 안정판 여부 확인.
3. (선택) 견고성 스윕 재개, vE 기준 need-cap 재설계 또는 TTC 변화율 후보.