# HANDOFF

Worker: Claude (61차 -- 20절 실제 리셋 실행: carrot-ryu를 carrot-ms 현재 HEAD(706efb47)로 재생성. 코드 브랜치 대규모 변경(이전 커스텀 36개 항목 현재 carrot-ryu에 없음, v1에만 보존). 이번 62차 세션에서 devnotes를 그에 맞게 사후 동기화)
Date: 2026-09-17
Repository: ryujmin97/openpilot
Code Branch: carrot-ryu (base: `706efb47b81cf9cb02888ee536a156d8f1fc1d91`, happymaj11r/openpilot carrot-ms 현재 HEAD를 그대로 force-push로 반영. 이전 HEAD `9ccf1206a034c5fb5e5f35201553f9fc4e5237e5`는 carrot-ryu-v1에만 남아있음)
Note Branch: carrot-ryu-note (base: `ff9d0e77f53a0c6e87c10f3e5fc8051e4e9047b4`, 60차 시점 devnotes. 이 커밋으로 devnotes 갱신)
carrot-ms 마지막 검토/동기화 커밋(메시지 기준): `706efb47b81cf9cb02888ee536a156d8f1fc1d91`(20절 리셋의 실제 반영 대상이자 새 베이스).

작업:
직전 세션(61차)에서 사용자 승인을 받아 20절 절차의 실제 첫 적용을 실행, carrot-ryu를 carrot-ms 현재 HEAD(706efb47)로 force-push해 재생성했다. push는 성공적으로 완료됐고 `git ls-remote`로도 확인됐으나, 그 직후 devnotes(HANDOFF/WIP_SYNC/WIP/CURRENT_STATUS) 61차 갱신 스크립트를 준비하던 중 무료 사용량이 소진되어 스크립트를 사용자에게 전달·실행하지 못한 채 세션이 끊겼다. 이번 세션(62차) 시작 시 4절 0단계 절차에 따라 재확인하는 과정에서, 코드 브랜치(carrot-ryu=706efb47)와 devnotes(당시 여전히 60차, ff9d0e77)가 서로 다른 시점을 가리키는 괴리를 16절 원칙에 따라 직접 발견·보고했고, 사용자 확인 후 devnotes를 코드 브랜치의 실제 상태에 맞춰 사후 동기화한다.

완료 (직전 61차 세션에서 실행, 이번 세션에서 결과 재확인):
1. carrot-ryu HEAD 변화 확인: force-push로 706efb47(carrot-ms와 동일)로 재생성됨. carrot-ryu-v1 = 9ccf1206으로 변경 없이 보존됨. 이번 세션에서 git ls-remote로 직접 재확인 완료.

완료 (이번 62차 세션):
1. 세션 시작 시 코드/devnotes 브랜치 간 시점 불일치(코드는 61차 반영됨, devnotes는 60차 그대로)를 발견해 사용자에게 보고, 진행 승인 받음.
2. devnotes(HANDOFF/WIP_SYNC/WIP/CURRENT_STATUS) 61차분을 코드 브랜치의 실제 반영 결과에 맞춰 재구성(이 문서 포함) -- 새 carrot-ryu HEAD 반영, CURRENT_STATUS.md 상단 HEAD 줄 갱신, "코드 수정 현황" 섹션에 리셋으로 전부 미반영 상태임을 명시하는 안내 추가.

미완료 (다음 세션 최우선):
0. [최우선] carrot-ryu-v1의 "코드 수정 현황" 36개 항목을 새 베이스(706efb47) 위에 하나씩 재적용(20절 5번, 9절 기존 워크플로/Replace-Block이나 전체교체). git cherry-pick을 기본 수단으로 삼지 않음(베이스 구조 자체가 크게 바뀌어 충돌 위험 높음). 규모가 크므로 도메인/서브시스템 단위로 나누어 여러 세션에 걸쳐 진행(17절).
0-1. 이식 순서를 사용자와 확정 필요: 서브시스템별(온로드 HUD 레이아웃 / 스크린샷첩리 / Google Drive 업로드 / 종방향 튜닝 / 현대 CAN 커스텀 등)로 묶을지, 이전 작업 후보 순서(아래)대로 하나씩 가는지.
0-2. 이식이 반 정도라도 진행되기 전까지는 콤마 디바이스 git pull 금지 상태 유지(현재 carrot-ryu는 커스텀 코드 전혀 없는 순수 carrot-ms 상태).
1. [이월, 20절 이식 대상] 온로드 시계 초단위 표시 + 스크린샷 버튼(12차, 684b30d 기준).
2. [이월] 온로드 시계 좌측 화면 경계 잘림 수정(13차).
3. [이월] Google Drive 업로드 전체 파이프라인(15~23차: gdrive_upload.py, 대시캠 zip 전환, params_keys.h 등록, 웹 설정 UI).
4. [이월] 화면녹화 탭 스크린샷(.png) 사진 스트립 및 관련 후속 수정들(24차~).
5. [이월] 종방향 gap/lead-response 자체 재설계(MPC costs 통합 등).
6. [이월] 나머지 항목들은 CURRENT_STATUS.md "코드 수정 현황" 전체 목록(1~36번) 참고 -- 각 항목이 새 베이스에 재적용될 때마다 해당 세션의 devnotes에서 개별적으로 "재반영 완료(commit ...)"로 갱신해야 함.
7. [59차에서 이월] 기존 2절 개별 선별 반영 이월분(종방향 클러스터 A/Hyundai CAN B/eGPU C 등)은 20절 리셋으로 흡수된 것으로 간주(carrot-ms 최신 베이스에 이미 포함됨). 별도 반영 필요 없음.

검증: 코드 변경은 브랜치 단위 교체로, `git ls-remote`로 carrot-ryu HEAD가 706efb47(carrot-ms와 동일)임을 이번 세션에서 직접 재확인. 실차 검증은 미실시(12절) -- 새 베이스는 아직 디바이스에 배포된 적 없음.

주의사항:
- 현재 carrot-ryu는 캐럿리 이름 기준으로는 실주행 대상이지만, 실제로는 지금까지의 커스텀 코드가 전혀 없는 상태다. 디바이스가 이 상태를 pull하면 기존 기능(온로드 HUD, 스크린샷, Drive 업로드 등)이 모두 사라진다.
- carrot-ryu-v1은 이식 체크리스트이자 임시 참조용이므로 1절 원칙대로 수정하지 않는다.
- carrot-ms는 앞으로도 수시로 rebase될 수 있으므로, 이식 작업 중에는 carrot-ms를 다시 베이스로 삼는 친션 잔업을 대부분 하지 않고 706efb47 위에서만 진행하는 것이 안전하다(베이스가 또 바뀌면 새 리셋이 필요해질 수 있음, 문제된 경우 사용자와 먼저 상의).
- 앞으로 한 스크립트에 여러 교체형 devnotes 파일을 히어스트링으로 함께 담을 때는 각 변수의 여는 줄(`$Var = @'`)과 닫는 줄(`'@`, 줄 시작)이 정확히 1:1로 대응하는지 반드시 재확인한다(60차에서 실제 오염 사례 있었음).

다음 작업 후보:
1. 온로드 시계 초단위/스크린샷 버튼부터 순차 재적용 착수
2. Google Drive 업로드 파이프라인 재적용
3. 종방향 gap/lead-response 자체 재설계 재적용
4. 이식 진행률을 CURRENT_STATUS.md에 계속 갱신