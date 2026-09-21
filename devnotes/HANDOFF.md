Worker: Claude (122차, Claude Sonnet 5)
Date: 2026-09-21
Repository: ryujmin97/openpilot
Code Branch: carrot-ryu (`2efdd2e25b42c78ea94f7366424fde695a13b15a`, 121차 B그룹 삭제 커밋. 이번 세션 코드 변경 없음)
Note Branch: carrot-ryu-note (이 스크립트 반영 전 base `6f978201139131acf76eb98e6e935e6912e144d2`, 121차 devnotes. 반영 후 HEAD는 다음 세션이 git ls-remote로 확인)
carrot-ms 마지막 검토/동기화 체크포인트: `4bb4b510`(116차, camera_sync 스케윅 허용오차 10ms->20ms) 반영 완료. 111차 확정 체크포인트는 `a23a77b1`. 이번 세션은 carrot-ms 신규 커밋 확인/동기화 작업 없음(121차와 동일).

작업:
1. CURRENT_STATUS.md가 96차 이후 갱신되지 않고 있었음을 발견(16절) -- 97~121차 사이 갭이 존재함을 명시적으로 기록(세부 재구성은 다음 세션 이월).
2. 사용자가 제공한 디바이스 git pull 로그(`fa75aeab7`->`2efdd2e2`, 115/116/117/118/120/121cha 6건)와 "실차 검증 이상없이 작동" 확인을 근거로, 121차 미완료 2번(실차 배포 이월)을 해소 처리.
3. devnotes 3개 파일(WIP.md/HANDOFF.md/CURRENT_STATUS.md) 갱신.

완료:
1. 115~121차 dead code cleanup 6개 커밋의 실차 배포 + 실차 주행 확인(사용자 보고 기준, 총괄 수준)을 devnotes에 기록.
2. CURRENT_STATUS.md 동기화 갭(96차 이후 미갱신)을 발견/명시(코드 변경 아님).

미완료(다음 세션 최우선):
1. DEAD_CODE_REVIEW C그룹(cluster 계열, `cluster_renderer.py`/`cluster_scene.py`/`main.py`, 약 300줄 + `cluster_scene.py`의 `statistics.median` 미사용 import) 삭제 스크립트 작성 -- 사용자 승인 완료(119차), A->B->C 순서 중 마지막 단계. 착수 전 11절대로 codeload tarball로 대상 커밋(`2efdd2e2`) 최신 상태 재확인.
2. CURRENT_STATUS.md의 97~114차 구간 상세 catch-up(현재는 갭 존재만 기록, 세부 내용 미보강) -- 필요 시 WIP.md 97~114차를 순서대로 조회해 채울 것.
3. (이월) 114차 MAP_TURN_GUIDE_FACTOR 1.00 실차 관찰, 110차 GATE_M 0.8/1.0 관찰 -- 계속 이월.
4. pytest는 여전히 `--noconftest`로만 실행돼 실제 CI 조건 pytest 실행이 미실시(121차와 동일 이월).
5. (제안, 사용자 승인 대기, 121차 이월) 9절 체크리스트에 "`core.eol=crlf` 재현 양성 실행" 항목 추가.

검증: devnotes 조회(GitHub SHA 고정) + 사용자 제공 디바이스 스크린샷/보고. 실차 검증: 115~121cha 6건 - 사용자 실차 주행 확인(이상 없음, 총괄 보고 수준. 세부 기능별 재검증은 아님).

주의사항:
- 코드 변경 없는 세션이므로 revert 대상 없음.
- CURRENT_STATUS.md는 96차 이후 실제로 갱신되지 않았던 것으로 확인됨 -- 앞으로 이 파일을 "최신"으로 가정하지 말고 HANDOFF.md/WIP.md와 교차 확인할 것(16절 사례로 편입).

다음 작업 후보:
1. C그룹 삭제 스크립트 작성(1순위, 승인 완료).
2. CURRENT_STATUS.md 97~114차 구간 catch-up.
3. 114차/110차 이월 실차 관찰 항목.
