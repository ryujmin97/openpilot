Worker: Claude (145cha, Claude Sonnet 5)
Date: 2026-09-23
Repository: ryujmin97/openpilot
Code Branch: carrot-ryu (HEAD: 139차 push 완료 상태 그대로 유지, `8e8b0d1a1569295a69a9817e378eef2ad861d79b` -- 145차도 코드 변경 없음)
Note Branch: carrot-ryu-note (이 스크립트 반영 전 base: 144차 devnotes push 완료 상태, `10c1f685ea8508651535fa6e572115b95f064f55`)
carrot-ms 마지막 검토/동기화 체크포인트: `3756e6d5`(130차, 139차 세션 재확인 -- 신규 커밋 없음. 140~145차는 재점검 없음)

작업:
1. 사용자가 "고속도로 앞차 추종 정속주행 시 앞차의 (가)속도 변화에 내차가 출렁인다, 위험하지 않다고 판단되면 반응요소를 무시하게 하는 게 어떤가"라는 개선 아이디어를 제기.
2. 사용자가 제공한 실주행 rlog 3세그먼트(`00000446--6455a5f5c4--29/30/31`, 각 ~60s 연속구간, 총 180s)로 조사 착수.
3. `git ls-remote`로 carrot-ryu(`8e8b0d1a`)/carrot-ryu-note(`10c1f68`) 현재 HEAD 확인.
4. rlog 3개 모두 `initData.gitCommit`이 현재 carrot-ryu HEAD와 일치, `dirty=False`임을 pycapnp로 직접 디코딩해 확인(3절/16절).
5. 그 커밋 기준 `openpilot/cereal/*.capnp` + `opendbc_repo/opendbc/car/car.capnp`를 새로 sparse-checkout, pycapnp 패키지 내장 `include/c++.capnp`까지 준비해 스키마 디렉터리 구성.
6. 세션 로컬 추출 스크립트(toolkit 미등록)로 `carState`/`carControl`/`longitudinalPlan`(리드 프리뷰 진단 필드 포함)/`radarState.leadOne`을 20Hz 병합, `gapMargin`(dRel-desiredDistance) 등 파생값 계산.
7. `openpilot/selfdrive/controls/lib/longitudinal_preview.py` + `longitudinal_planner.py` + `long_mpc.py`를 GitHub에서 직접 조회해 감속 프리뷰(`get_lead_preview_request`)와 양의 리드가속 응답(`get_lead_accel_mpc_request`) 두 메커니즘의 게이팅 구조를 대조.
8. WIP.md 145차 신설(최상단) / CURRENT_STATUS.md 145차 요약 한 줄 삽입(`## 코드 수정 현황` 헤더 직전) / HANDOFF.md(이 파일) 전체 갱신을 devnotes 반영 스크립트로 작성해 전달.

완료:
1. rlog 3개(`--29/30/31`) 모두 `initData.gitCommit`(`8e8b0d1a1569295a69a9817e378eef2ad861d79b`)이 현재 HEAD와 일치, `gitBranch=carrot-ryu`, `dirty=False` 확인(3절/16절).
2. 180초 병합 데이터에서 `longitudinalPlan.leadPreviewSeconds`(감속 프리뷰)가 전체 시간의 80.7% 활성임을 확인. `gapMargin`(dRel-desiredDistance) > 15m로 간격 여유가 충분한 구간(2144/17999 표본)만 봐도 활성 비율이 78.9%로 거의 차이가 없어, 간격 여유/위험도와 사실상 무관하게 반응하고 있음을 확인.
3. `leadPreviewAccel`(상대가속도 신호) 부호가 초당 약 2.9회 뒤집힘을 확인 -- 사용자가 체감한 "출렁임"과 빈도 상 부합.
4. `longitudinalPlan.aChangeCost`가 180초 내내 정확히 200.0으로 고정, 즉 반대 방향(양의 리드가속 응답)은 이 표본에서 전혀 발동하지 않았음을 확인.
5. 코드 조회로 `get_lead_preview_request()`(감속 프리뷰, `longitudinal_planner.py`에서 호출)는 `a_lead-a_ego`에 ±0.10 데드밴드 + `lead.status`/`radar`/`radarTrackId`/운전자 개입 외 게이팅이 없음을 확인. `get_lead_accel_mpc_request()`(양의 응답, `long_mpc.py:537`에서만 호출 -- grep으로 `longitudinal_planner.py`에는 해당 호출이 없음을 확인)는 `gap_margin`/`closing_speed_floor`/`prediction_horizon` 게이팅이 이미 있음을 확인. 감속 쪽만 위험도 게이팅이 빠진 비대칭 구조를 코드로 확정(11절).
6. 사용자 제안(위험 아니면 반응 무시)이 이 기존 비대칭을 감속 쪽에 대칭 적용하자는 것과 같은 방향임을 확인하고 사용자에게 근거와 함께 제시. 코드 반영에는 착수하지 않고(안전 관련 핵심 로직) 임계값 설계/사전 검증이 필요함을 명시.
7. WIP.md 145차 신설(최상단, LF 유지) / CURRENT_STATUS.md 145차 요약 한 줄 삽입(LF 유지, `## 코드 수정 현황` 헤더 직전) / HANDOFF.md(이 파일) 전체 갱신을 반영 스크립트로 작성.
8. 9절 체크리스트 중 이번 세션에서 실제로 수행한 항목: (6/7번) WIP.md/CURRENT_STATUS.md 앵커(`"# WIP\n\n## 144차"`, `"코드 변경 없음. 상세: WIP.md 144차 참고.\n\n## 코드 수정 현황"`)를 SHA 고정(`10c1f685...`) 원본에 Python으로 사전 시뮬레이션해 각각 정확히 1회 매치 확인, 그 결과를 스크립트의 치환 문자열로 그대로 사용.

미완료(다음 세션 최우선, 기존 이월 항목 포함):
1. 이번(145차) devnotes 반영 스크립트 실행/push 확인(16절).
2. **핵심 미결정 사항** -- 감속 프리뷰(`get_lead_preview_request`)에 `gap_margin`/`vRel` 기반 위험도 게이팅을 추가할지, 추가한다면 구체 임계값(간격 여유 몇 m부터 "안전"으로 볼지, closing speed 조건을 어떻게 잡을지)을 어떻게 설계할지 사용자와 방향을 확정하지 못했다. 코드 변경은 아직 착수하지 않음.
3. 위 게이팅을 실제로 설계/반영하기 전에, 이번에 확보한 3개 로그(180s)로 후보 게이팅 로직을 offline replay 재계산해 출렁임(leadPreviewAccel 부호 반전 빈도, previewEffect 크기)이 실제로 줄어드는지 사전 검증 필요(11절, 코드 반영 전 증거 기반 원칙) -- route_extract.py의 `replay` 모드처럼 재사용 가능한 형태로 만들지, 이번 세션의 1회성 스크립트를 그대로 확장할지도 결정 필요.
4. (9절 체크리스트 8/9번 계열) 이번 세션도 코드 변경이 없어 pwsh 파서 검증/로컬 bare 저장소 dry-run 대상 스크립트가 devnotes 반영 스크립트 1개뿐이며, Termux(bash) 환경 특성상 `bash -n` 문법 확인 + 로컬 bare 저장소 실행 검증을 (실행자가) 별도로 수행할 것을 전제로 함.
5. 114차 계열 이월 항목(변동 없음): xTurn=6(톨게이트) 케이스 로그 미확보, 디바이스 `MapTurnSpeedFactor`(base) 실측값 미확인.
6. 110차 GATE_M 관련 추가 실차 사례(변동 없음).
7. devnotes/toolkit/replace_block_template.ps1의 재사용 헬퍼에 Invoke-Git 패턴 반영(140차부터 이월, 아직 미착수, 145차도 코드 반영 스크립트가 아니라 해당 없음).
