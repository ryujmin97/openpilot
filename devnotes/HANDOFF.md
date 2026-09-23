Worker: Claude (149cha, Claude Sonnet 5)
Date: 2026-09-24
Repository: ryujmin97/openpilot
Code Branch: carrot-ryu (base: c0a01658f109f5fb52b98f56c4ff5e6dcde42159, 147차 코드 push 완료 확인 -- 이번 세션 코드 변경 없음)
Note Branch: carrot-ryu-note (이 스크립트 반영 전 base: 148차 devnotes push 완료 상태, `ce81555521006c651675206c62036da7656b3920`)
carrot-ms 마지막 검토/동기화 체크포인트: `3756e6d5`(130차, 139차 세션 재확인 -- 신규 커밋 없음. 140~149차는 재점검 없음)

작업:
1. 세션 시작 4절 0단계로 지침 문서(v2, commit `77fc181`) 조회, 148차 devnotes push(`ce81555`, 부모 `77fc181`, +37/-35) GitHub 직접 재조회로 확인.
2. 148차 v1 스크립트 실행 실패(`2>&1`+`param()` 재도입 -> 5.1 `NativeCommandError`, 아무것도 push 안 됨) 원인 분석 -> toolkit 정식 `Invoke-Git` 그대로 쓴 v2 작성/재검증, 사용자 재실행 성공.
3. 사용자 업로드 rlog 5세그먼트(route 443 seg 5/6, route 446 seg 29/30/31; 전부 gitCommit `8e8b0d1a`, dirty=False)로 147차 감속 프리뷰 게이트(1.05/1.25 + TTC 6/12) 재생 검증. 실제 코드(`_gate_raw`, `longitudinal_preview.py`)를 SHA 고정 원본에서 import해 재구현 없이 재생.
4. 재생 도구 `lead_decel/replay_gate147.py`, `extract_radar_flag.py`를 toolkit에 등록(README/CHANGELOG 갱신).

완료:
1. 146~148차 이월 "위험 시나리오 재생 검증" 수행(open-loop, 로그 재생). 재생 신뢰도: 기록 커밋 코드 체인이 로그 leadPreviewSeconds를 mean|err| 0.0005(443)/0.0065(446) s로 재현, aTargetBase 재구성 mean 0.002~0.003 m/s². 결과: m<=1.05 표본 100% g=1, TTC<=8 s 접근 97.2% g=1(min 0.81), 위험 이벤트 2건에서 출력 a_target 제동 약화 최대 0.088 m/s²(0.15 s), 프리뷰 최대 도달 지연 약 1.0 s(이벤트 2, 선행차 감속 후 정지). 446: 활성 80.6->15.8%, RMS -91.3%.
2. comfort_brake=2.4/stop_distance=7.0을 swaglog lead_gate에서 역산(m 오차 mean 0.006).
3. fade 밴드 스윕 자료 확보(WIP.md 149차 표).
4. 147차 이월 "검증용 스크립트 정식 등록 여부" -- 재생 도구 2종 등록으로 해소(diff/블록 추출 스크립트는 별개, 미완료 7번).
5. 148차 HANDOFF 미완료 6번(replace_block_template.ps1에 Invoke-Git 반영)은 144차에 이미 완료돼 있음을 SHA 고정 원본(`77fc181`)의 파일/README/CHANGELOG로 확인(미완료에서 제거).

미완료(다음 세션 최우선 순으로):
1. **147차 코드가 탑재된 디바이스의 실주행 로그 검증(신규 최우선)** -- 이번 재생은 로그 기록 시점에 147차 코드가 없었으므로 시뮬레이션일 뿐이다. 같은 도구(`replay_gate147.py`, ego_extract2.py + extract_radar_flag.py)로 실제 leadPreviewSeconds/게이트 거동을 비교할 것. 실차 검증 미실시.
2. fade 밴드 폭(1.05/1.25) 확정 -- 사용자 결정 필요. 스윕은 WIP.md 149차 표 참고(위험 완전개방 구간은 밴드와 무관, 차이는 onset 지연 vs 정속 추종 억제량).
3. "선행차가 설정 차간거리(m~1.25) 근처에서 급제동" 시나리오는 로그에 없어 정량 미검증(g가 TTC/m 악화에 따라 올라가는 onset 지연 문제) -- 해당 로그 확보 시 검증.
4. 148차 v1 `2>&1` 재발(핵심 발견 53/55와 동일 패턴 3회째)의 FINDINGS.md 정식 등록 여부 결정.
5. 114차 계열 이월 항목(변동 없음): xTurn=6(톨게이트) 케이스 로그 미확보, 디바이스 MapTurnSpeedFactor(base) 실측값 미확인.
6. 110차 GATE_M 관련 추가 실차 사례(변동 없음).
7. 이전 이월: diff/블록 추출 스크립트(임시, 147차 코드 반영용) toolkit 미등록.

검증:
- 정적/재생: 위 "완료 1" 참고(로그 재생, open-loop). pytest 등 코드 테스트는 코드 변경 없어 해당 없음.
- 실차: 미실시.

주의사항:
- 재생 결과는 로그 기록 커밋(8e8b0d1a) 위의 시뮬레이션이다. 147차 코드가 실차에서 이렇게 동작한다는 증거가 아니다(12절).
- 업로드 참고자료(margin_ratio 1.052~1.507, RMS 84.9%, 82.9%)는 이번 재생과 일치하지 않는다(WIP.md 149차 대조 참고). 참고자료 수치는 근거로 쓰지 말 것.
- 이 devnotes 반영 스크립트(149차)의 실행/push 확인이 필요하다.

다음 작업:
1. 이 devnotes 반영 스크립트 실행/push 확인.
2. 사용자 결정: fade 밴드 폭 유지/조정, 148차 재발 FINDINGS 등록 여부.
3. 147차 탑재 디바이스 실주행 로그가 생기면 미완료 1번 수행.
