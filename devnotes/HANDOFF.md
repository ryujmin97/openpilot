Worker: Claude (146cha, Claude Sonnet 5)
Date: 2026-09-23
Repository: ryujmin97/openpilot
Code Branch: carrot-ryu (HEAD: 139차 push 완료 상태 그대로 유지, `8e8b0d1a1569295a69a9817e378eef2ad861d79b` -- 146차도 코드 변경 없음)
Note Branch: carrot-ryu-note (이 스크립트 반영 전 base: 145차 devnotes push 완료 상태, `773355cbec039f2c76c1c056521dfc6a51a01993`)
carrot-ms 마지막 검토/동기화 체크포인트: `3756e6d5`(130차, 139차 세션 재확인 -- 신규 커밋 없음. 140~146차는 재점검 없음)

작업:
1. 145차가 이월한 두 항목(감속 프리뷰 게이팅 임계값 설계, offline replay 사전검증)을 이어서 착수.
2. 사용자가 145차와 동일 route 3세그먼트(`00000446--6455a5f5c4--29/30/31`, 총 180s)를 재업로드, `initData.gitCommit`이 현재 HEAD와 일치함을 재확인(3절/16절).
3. 해당 커밋 기준 cereal/car 스키마를 새로 구성해 carState/radarState.leadOne/longitudinalPlan/selfdriveState를 20Hz 병합하는 세션 로컬 스크립트(`extract.py`/`analyze.py`, toolkit 미등록) 작성/실행.
4. 로그의 `desiredDistance`/`tFollow`로 기존 GATE_M(`_gate_raw()`) 게이트와 동일한 공식으로 `margin_ratio`를 재구성, 이를 감속 프리뷰 신호(`lead_accel_signal`)에 곱하는 후보를 순수 오프라인으로 시뮬레이션.
5. 재구성 baseline offset_s vs 로그의 `leadPreviewSeconds` 대조 -- 차이 원인이 버그가 아니라 `rate_limit_preview()` 램프 유무 때문임을 코드 대조로 확인(11절).
6. GATE_M 동일 임계값(0.8/1.0) 적용 결과 + 완화 밴드 4종(1.0/1.3, 1.2/1.6, 1.3/1.8, 1.4/2.0) 스윕 결과 비교.
7. 사용자와 설계 방향 논의: "설정 차간거리 유지 + 위험하지 않으면 앞차 반응 무시"라는 목표를 margin_ratio 공식에 대수적으로 대입해, gap=desiredDistance일 때 항상 m=1.25(=1/LEAD_DANGER_FACTOR)가 됨을 도출, 이를 프리뷰 게이트의 설계 기준선으로 확정. 전환 방식(1.25 부근 좁은 fade, TTC 유지)에 합의.
8. WIP.md 146차 신설(최상단) / CURRENT_STATUS.md 146차 요약 한 줄 삽입(`## 코드 수정 현황` 헤더 직전) / HANDOFF.md(이 파일) 전체 갱신을 반영 스크립트로 작성해 전달.

완료:
1. rlog 3개(`--29/30/31`) `gitCommit`(`8e8b0d1a1...`)이 현재 HEAD와 일치, `dirty=False` 확인(3절/16절, 145차와 동일 route임을 재확인).
2. GATE_M 하이브리드 게이트(margin_ratio+TTC)와 동일한 공식으로 offline replay 시뮬레이션을 구성, baseline(게이트 없음) offset_s가 로그 `leadPreviewSeconds`와 다른 이유가 `rate_limit_preview()` 램프 유무임을 코드 대조로 확정(사안을 버그로 오판하지 않음, 11절).
3. GATE_M 임계값(0.8/1.0)을 프리뷰에 그대로 적용 시 이 180초 구간(margin_ratio 전부 1.0 초과) 전체에서 게이트가 항상 닫혀 활성비율 53.6%->0%, RMS 100% 감소함을 확인 -- 단, "이 구간에 위험 상황이 없었다"는 사실의 반영이라는 한계를 함께 기록.
4. 완화 밴드 4종 스윕 결과 (1.0,1.3)이 활성비율은 거의 유지(53.2%)하면서 RMS를 80.4% 감소시키는 가장 균형 잡힌 후보임을 확인.
5. margin_ratio 공식에 `gap=desiredDistance`를 대입하면 `SE(vLead)` 항이 상쇄되어 리드속도 무관하게 항상 `m=1/0.8=1.25`가 성립함을 대수적으로 도출 -- "설정 차간거리 유지 시 항상 margin_ratio=1.25"라는 기준선을 확정. (1.0,1.3) 밴드 상한이 이 값과 거의 겹치고, 이번 로그의 margin_ratio 평균(1.258)/중앙값(1.251)도 1.25 부근에 몰려있다는 것으로 상호 교차검증.
6. 기존 GATE_M(0.8~1.0)이 설정 차간거리(1.25)보다 훨씬 안쪽(약 64~80%)을 보는 MPC danger-zone 전용 게이트로, 프리뷰 목적과 다름을 사용자에게 설명/합의.
7. 전환 방식을 완전 이진이 아닌 1.25 기준선 주변 좁은 폭 fade로, TTC 성분은 유지하기로 사용자와 합의(코드 미반영).
8. WIP.md 146차 신설(최상단, LF 유지) / CURRENT_STATUS.md 146차 요약 한 줄 삽입(LF 유지, `## 코드 수정 현황` 헤더 직전) / HANDOFF.md(이 파일) 전체 갱신을 반영 스크립트로 작성.
9. 9절 체크리스트 중 이번 세션에서 실제로 수행한 항목: (6/7번) WIP.md/CURRENT_STATUS.md 앵커(`"# WIP\n\n## 145차"`, `"상세: WIP.md 145차 참고.\n\n## 코드 수정 현황"`)를 SHA 고정(`773355cbec03...`) 원본에 Python으로 사전 시뮬레이션해 각각 정확히 1회 매치 확인, 그 결과를 스크립트의 치환 문자열로 그대로 사용.

미완료(다음 세션 최우선, 기존 이월 항목 포함):
1. 이번(146차) devnotes 반영 스크립트 실행/push 확인(16절).
2. **핵심 미결정 사항** -- 1.25 기준선을 축으로 한 fade 밴드의 정확한 상/하한 폭을 로그 시뮬레이션(`analyze.py` 확장)으로 결정하지 못했다.
3. 위 게이팅 후보를 실제로 코드에 반영하기 전에, 위험 시나리오(142차 rlog 또는 97~110차 idx5/8/9 급감속 이벤트)로 재생 검증해 margin_ratio가 실제로 낮아지는 구간에서 게이트가 정상적으로 열리는지 확인 필요(11절, 코드 반영 전 증거 기반 원칙) -- 완료 전까지 코드 반영 착수하지 않음.
4. 이번 세션의 임시 스크립트(`extract.py`/`analyze.py`)를 `devnotes/toolkit/lead_decel/`에 정식 등록할지 결정 필요.
5. (9절 체크리스트 8/9번 계열) 이번 세션도 코드 변경이 없어 pwsh 파서 검증/로컬 bare 저장소 dry-run 대상 스크립트가 devnotes 반영 스크립트 1개뿐이며, Termux(bash) 환경 특성상 `bash -n` 문법 확인 + 로컬 bare 저장소 실행 검증을 (실행자가) 별도로 수행할 것을 전제로 함.
6. 114차 계열 이월 항목(변동 없음): xTurn=6(톨게이트) 케이스 로그 미확보, 디바이스 `MapTurnSpeedFactor`(base) 실측값 미확인.
7. 110차 GATE_M 관련 추가 실차 사례(변동 없음).
8. devnotes/toolkit/replace_block_template.ps1의 재사용 헬퍼에 Invoke-Git 패턴 반영(140차부터 이월, 아직 미착수, 146차도 코드 반영 스크립트가 아니라 해당 없음).
