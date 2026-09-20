Worker: Claude (105차, Claude Sonnet 5)
Date: 2026-09-20
Repository: ryujmin97/openpilot
Code Branch: carrot-ryu (base: `f78e51e0bfe01e14ce70cc7eafc3323c5981a8a7`. 이번 105차 코드 변경은 반영 스크립트 `105cha_carrot_ryu_margin_gate.ps1` 실행/push 대기 -- 반영 후 HEAD는 다음 세션이 git ls-remote로 확인)
Note Branch: carrot-ryu-note (base: `fd995bd619d45ac755bda3cf6f789674a07540d8`, 103차 devnotes push 완료를 git ls-remote로 확인. 이번 105차 devnotes 반영은 실행/push 대기)
carrot-ms 마지막 검토/동기화 체크포인트: `e324f6735d3606800045ed6b28f41e79b17e5498`(93차 확정, 이번 세션도 2절 신규 커밋 확인 안 함 -- 계속 이월)

작업:
사용자 결정("검증은 나중에 하고 우선 코드 적용한 후 실차검증으로 수정")에 따라 리드 감속 게이트를 margin_ratio 하이브리드로 carrot-ryu `long_mpc.py`에 적용하는 코드/테스트/반영 스크립트를 작성했다.

완료:
1. 지침 문서 v2 전체 조회(SHA 고정본 == 브랜치 URL 조회본), HANDOFF/WIP 최상단 확인, 두 브랜치 HEAD 재확인.
2. `long_mpc.py`: `GATE_H_LO/HI`(1.5/2.2s) 게이트를 `margin_ratio`(m = (gap + 정지환산거리(vLead)) / (0.8 * 쾌적거리(vEgo, tFollow, cb, sd)))로 교체, `GATE_M_LO/HI = 1.0/1.2`, TTC 6/12s 성분은 `max()` 결합(하이브리드), 나머지 상수(`GATE_TAU_G=1.0`, `GATE_TAU_TARGET=1.5`) 동일. `process_lead()` 시그니처는 유지하고 `update()`가 `self._gate_ctx`로 tFollow/comfort_brake/stop_distance를 전달. `lead_gate` swaglog에 `m=` 추가.
3. 신규 단위 테스트 `test_lead_gate_margin.py` 8개(샌드박스 8 passed), 기존 `test_cutout_mpc_integration.py` 17 passed(수정 전후 동일).
4. 반영 스크립트를 PowerShell 7.4.6로 로컬 베어 저장소에 끝까지 드라이런(푸시 결과 == 작업본 바이트 일치, 임시 폴더 정리 확인).

미완료(다음 세션 최우선):
1. 두 반영 스크립트(코드/devnotes) 실행 로그 확인 -> GitHub SHA 고정 조회로 실제 반영 재확인(16절).
2. 실차 배포(디바이스 git pull은 사용자 확인 후) 및 swaglog `lead_gate`(g, m) 관찰 -> 튜닝(WIP 105차 "튜닝 가이드").
3. 104차 기록 부재 확인: 업로드된 `margin_gate_eval.py` docstring이 104차를 명시하지만 devnotes에 104차 회차가 없다. 사용자에게 104차 내용/결과 확인.
4. `margin_gate_eval.py`(+ `gate_replay.py`/`full_gate_stats.py`/`leadtwo_probe.py`)의 devnotes/toolkit/lead_decel/ 정식 등록 여부 사용자 확인(14절, 세션 리셋마다 복구 비용 반복).
5. CURRENT_STATUS.md에 99차 게이트 항목이 없음(이번 세션은 수정 안 함) -- 정리 필요.
6. carrot-ms 신규 커밋 확인(2절), 화면녹화 탭 사진 업로드 UI(항목 22·23·26)/Drive 파이프라인/녹화 버튼 깜빡임(28) 실차 검증 이월.
7. (보류) idx 14~25 재생, 하이브리드 폐루프 평가, gap_offset 스트레스(-10,-20).

검증: 정적 분석/샌드박스 단위 테스트이며 실차 검증: 미실시. 이번 하이브리드 조합의 폐루프 재생 검증도 미실시.

주의사항:
- 103차 재생에서 margin 단독(1.0/1.2)은 idx8에서 base와 동일(-2.75)해 기존 B(-2.31)보다 못했다. 하이브리드가 이를 보완하는지는 재생하지 않았으므로, 위험 상황 감속 억제가 기존 B보다 나쁠 수 있다. 문제 시 105차 코드 커밋을 `git revert`하면 `f78e51e`(B안)로 복귀.
- 정상 추종 평형 m=1.25(GATE_M_HI=1.2는 여유 0.05). tFollow가 동적으로 커지거나 실제 gap이 평형보다 짧은 구간에서 g가 올라갈 수 있다 -- 로그로 확인.
- GitHub API는 rate limit에 자주 걸린다 -- `git ls-remote`/`git clone`(--depth 1)을 우선 사용.
- HANDOFF의 "push 대기" 표기를 실제 상태와 대조 없이 믿지 않는다(16절).

다음 작업 후보:
1. 반영 확인 -> 실차 lead_gate 로그 관찰/튜닝.
2. 104차 기록 확인, toolkit 등록 여부 확인.
3. carrot-ms 신규 커밋 확인(2절).
