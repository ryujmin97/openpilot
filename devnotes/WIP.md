# WIP

## 100차 (Claude) — 99차 게이트 반영 후 회귀 테스트 39개 실패 발견, 테스트 하네스만 수정(코드 변경 없음)

**세션 시작(4절 0단계)**: `git ls-remote`로 carrot-ryu-note HEAD `044a1d1`을 얻어 SHA 고정 raw로 지침 문서(v2)를 조회했다. HANDOFF.md(99차분)도 같은 SHA로 읽었다. carrot-ryu `f87083e`, carrot-ms `e324f67`(변경 없음) 확인.

**HANDOFF.md 정정(16절)**: 99차 HANDOFF.md는 "반영 스크립트 실행/push 대기"로 적혀 있었으나, 실제로는 코드(`f87083e`)·devnotes(`044a1d1`) 둘 다 이미 push 완료돼 있었다. `git diff 25f21d4 f87083e`로 변경 파일이 long_mpc.py 1개뿐이고 99차 설계(GATE_* 상수 / `_gate_raw()` / `process_lead(self, lead, lead_index)` / `reset()` 초기화 / 호출부 2곳)와 정확히 일치함을 재확인했다. 이번 HANDOFF에서 정정.

**업로드 로그(9/18 기록, carrot-ryu-v1 `9ccf1206`)로 패치된 코드(f87083e) 재생 검증**: toolkit/lead_decel(97~98차 등록) 절차로 환경을 복원해(스키마는 `9ccf1206` sparse-checkout) 26개 aLeadK<-1 이벤트를 다시 추출했다(97~98차와 동일). long_mpc.py의 게이트 코드(`GATE_*`/`_gate_raw`/`process_lead`)를 파일에서 그대로 추출해 스텁으로 실행하는 단위검증 도구(`gate_replay.py`, 신규)를 작성해 아래를 확인했다:
- `_gate_raw()`가 독립 명세(98차 `gating_eval.py`의 `gate_raw()`)와 343개 표본에서 완전히 일치(max|diff|=0).
- 시간차 1.5 s 미만(h<h_lo, g=1)에서는 패치본이 기존 코드와 비트 단위로 동일(300/300 표본).
- 하강은 1 s LPF, 상승은 즉시라는 설계대로 동작(LPF 20스텝 후 g=(1-dt/tau)^20 수치 일치).
- 리드가 사라지면 해당 인덱스만 g=1로 리셋되고 다른 인덱스는 유지됨, `status=False`(leadTwo)도 동일.
- `cloudlog.debug`는 g<1일 때만 초당 1회 이하로 호출됨, g=1이면 호출 없음.
- 극단 입력(정지/초근접/원거리)에서 예외·NaN 없음.

이 `gate_replay.py`로 26개 이벤트를 폐루프(97~98차 `mpc_replica`/`closed_loop` 방식 재사용) A/B 비교했다: 기존 코드 결과는 98차 수치와 일치하게 재현됐고, 패치 결과는 98차에 기록된 B안(G2T) 수치와 ±0.01 이내로 일치했다(예: #5 최대감속 -2.10→-1.91, #8 -2.75→-2.30, #22 -2.05→-1.21; 최소 시간차도 각각 개선). 123/124 구간의 tFollow 1.1~1.6대(#18~21)는 g가 0.7~1이라 게이트가 사실상 열려 있어 기존과 결과가 같았고(안전한 방향), tFollow 1.6 평상 추종 구간은 g 평균이 대체로 0.1~0.45로 게이트가 대부분 열려 있었다. #11은 구간 시작 아티팩트라 제외.

**회귀 발견(핵심)**: 99차 게이트 반영 후 기존 테스트 2개 파일에서 총 39개 실패를 발견했다 — `test_cutout_mpc_integration.py` 12개(기존 25f21d4에서는 17개 전부 통과), `test_longitudinal_gap_recovery.py` 27개(기존에는 78개 전부 통과). 두 파일 모두 `ast.parse`로 production `long_mpc.py`의 함수/클래스 노드를 뽑아 stub 네임스페이스에서 `exec`하는 방식(하네스가 소스를 직접 실행)이라, 원인은 실행 코드(long_mpc.py)가 아니라 하네스 자체였다:
1. `test_cutout_mpc_integration.py`의 가짜 `process_lead(l)`가 인자 1개만 받는데, `update()`가 이제 `process_lead(radarstate.leadOne, 0)`처럼 2개를 넘겨 `TypeError`.
2. `test_longitudinal_gap_recovery.py`의 stub 네임스페이스(`ns`)에 새로 참조된 `GATE_H_LO/HI`, `GATE_T_LO/HI`, `GATE_TAU_G`, `GATE_TAU_TARGET` 모듈 상수와 `time`, `cloudlog`가 없어 `NameError`.

**최소 수정(테스트 파일 2개, 프로덕션 코드 무변경)**: (a) `process_lead(l)` → `process_lead(l, lead_index=0)`. (b) `load_mpc_update()`의 `ns`에 `time`/`cloudlog`(no-op stub) 추가, `ast.parse` 결과에서 `GATE_`로 시작하는 모듈 레벨 `Assign` 노드를 함수/클래스 노드 앞에 추가로 포함하도록 한 줄 추가. 두 파일 다 SHA 고정 원본(`f87083e`)에서 Replace-Block 앵커 유일 매치(각 1회)를 확인했다.

**검증**: 두 파일을 패치해 `openpilot`(f87083e sparse clone, cereal/opendbc 스키마 포함)에서 `pytest`를 실제로 실행 — 95개 전부 통과(17+78). `py_compile` 통과. 반영 스크립트(`100cha_test_fix_carrot_ryu.ps1`)의 전달본에서 `$Old`/`$New` 3쌍을 정규식으로 추출해 SHA 고정 원본에 재시뮬레이션 → 전부 1회 매치, 재구성한 파일이 사전 설계본과 diff 없음, `py_compile` 재통과, 그 결과로 실제 pytest도 95개 통과까지 재확인했다(9절 체크리스트 7번). 체크리스트 1~6번도 스크립트 코드 자체에서 확인(BOM `EF BB BF`, 모든 `git clone`에 `core.autocrlf=false`, `finally`에 `Remove-Item -Recurse -Force`, `Get-PythonCmd`+EOF 공급, 전체쓰기는 `WriteAllText(...,UTF8Encoding($false))`만 사용 후 BOM 없음 확인, 치환 결과 재확인 로직 존재).

**영향받지 않는 것으로 확인**: `test_following_distance.py`, `test_long_mpc_a_change_cost.py`는 `process_lead`/`GATE_` 심볼을 참조하지 않음을 grep으로 확인(파일 내 매치 0건). 다만 이 두 파일은 `cereal`(capnp 네이티브 빌드)과 `opendbc.can`(C 확장) 전체 빌드가 필요해 이번 세션 샌드박스에서 직접 실행은 못 했다(pycapnp는 설치했으나 opendbc.can 네이티브 모듈이 없어 `ModuleNotFoundError`) — grep 결과로 낮은 위험만 확인했고 실제 실행 검증은 아니다.

**이번 세션에서 하지 못한 것(다음 세션 후보)**: (a) 거리 -10/-20 m 스트레스 시나리오를 f87083e 패치본으로 재실행(98차는 후보 비교용, 이번엔 실제 반영본 검증용으로 다시 필요). (b) 주행 전체(9개 세그먼트 전체, 26개 이벤트 외 구간)에서 게이트 노출 빈도(g<1 비율) 통계. (c) leadTwo 쪽 게이트 동작(98차 분석은 leadOne 기준)은 여전히 실차/시뮬 양쪽에서 확인된 적 없음. (d) `gate_replay.py`를 `devnotes/toolkit/lead_decel/`에 정식 등록(README/CHANGELOG 갱신, 14절) — 이번 세션은 사용자가 나중에 하라고 지시해 보류.

**한계**: (1) MPC는 casadi/IPOPT 복제본(acados 실물 아님), 강한 감속을 과소 재현한다(97~98차와 동일 한계). (2) 로그의 tFollow는 v1(`9ccf1206`) 기준이라 현재 carrot-ryu 설정과 다를 수 있다. (3) v1에만 있던 `SafeFollow` 관련 코드는 기록된 설정(`LeadAccelResponse=0`)에서 꺼져 있었다고 보고 이번 재현 검증에서 무시했다(97~98차와 동일 처리). (4) `cloudlog.debug`가 실제 콤마 디바이스의 swaglog에 정상적으로 남는지는 확인하지 못했다. **정적 분석/오프라인 시뮬레이션 단계이며 실차 검증: 미실시.**

**다음 세션 최우선**: (a) 사용자가 `100cha_test_fix_carrot_ryu.ps1` 실행 → push 확인(GitHub API/raw로 재확인, 16절). (b) 실차 배포 후 swaglog `lead_gate` 태그 관찰(99차부터 이월). (c) 위 "하지 못한 것" (a)(b)(c) 진행 여부 판단. (d) `gate_replay.py` toolkit 등록 여부 사용자 확인.


## 99차 (Claude) — B안(G2T) 리드 감속 게이팅 코드 설계/구현, long_mpc.py 반영 스크립트 작성(실행/push 대기)

**세션 시작(4절 0단계)**: `git ls-remote`로 carrot-ryu-note HEAD `d5cc1df`를 얻어 SHA 고정 raw로 지침 문서(v2)를 조회했다. HANDOFF.md/CURRENT_STATUS.md/WIP.md(98차)도 같은 SHA로 읽었다. carrot-ryu `25f21d4`, carrot-ms `e324f67` 모두 변경 없음(drift 없음).

**코드 조사**: `openpilot/selfdrive/controls/lib/longitudinal_mpc_lib/long_mpc.py`(base `25f21d4`)를 독립 `git clone`(shallow fetch)으로 읽었다. 게이트 입력(dRel/vLead/vEgo)은 `process_lead(self, lead)` 안에서 이미 접근 가능함을 확인 — `update()` 시그니처 변경 불필요. `process_lead()`가 `extrapolate_lead()`에 넘기는 `a_lead_tau`를 게이트로 대체하는 지점이 삽입 위치. `process_lead()`는 leadOne/leadTwo 양쪽에 호출되므로 리드별 게이트 상태(상승 즉시/하강 1 s LPF) 분리가 필요해 `lead_index` 인자를 추가했다. `process_lead()`가 이 파일 밖에서 호출되지 않음(외부 호출자 없음)을 `openpilot/selfdrive/controls` 전체 grep으로 확인해 시그니처 변경의 파급 범위가 없음을 검증했다.

**사용자 결정 3건**: (a) tFollow 절대시간차 문제(h_lo=1.5s가 짧은 tFollow 설정에서 평상시에도 g<1을 유발할 수 있는 한계) — B안 승인된 절대값 그대로 반영하고 실차 로그로 관찰하기로 함(임계값 자체 재설계는 19절 성격이라 보류). (b) 임계값(h_lo/h_hi/t_lo/t_hi)을 Params로 노출할지 — 코드 상수로 고정(10절 최소 변경, params_keys.h 등록 불필요). (c) 게이트 값을 실차 로그에 남길지 — `cloudlog.debug`로 g<1일 때만 초당 1회 경량 기록(기존 `self.last_cloudlog_t` 레이트리밋 패턴 재사용).

**최소 변경안(4개 블록, `long_mpc.py` 한 파일)**: (A) `STOP_DISTANCE` 아래 `GATE_H_LO/HI`, `GATE_T_LO/HI`, `GATE_TAU_G`, `GATE_TAU_TARGET` 모듈 상수 추가(B안 수치: h 1.5~2.2 s, TTC 6~12 s, 하강 시정수 1 s, 투사 목표 1.5). (B) `extrapolate_lead()` 뒤에 `_gate_raw(gap, v_ego, v_lead)` staticmethod 추가(98차 `gating_eval.py`의 `gate_raw()`와 동일한 시간차/TTC 게이트 산식), `process_lead(self, lead, lead_index)`로 시그니처 변경하고 실제 리드 분기 안에서 게이트 계산 → `a_lead_tau = g*a_lead_tau + (1-g)*GATE_TAU_TARGET`(G2T, 투사 감쇠만) → g<1일 때 `cloudlog.debug` 레이트리밋 기록. 가짜 리드 분기에서는 `self._gate_g[lead_index] = 1.0`로 중립 리셋. (C) `reset()`에 `self._gate_g = np.array([1.0, 1.0])`, `self._gate_last_cloudlog_t = 0.0` 초기화 추가. (D) `update()` 안 `process_lead()` 호출 2곳에 `lead_index`(0/1) 인자 추가.

**검증(샌드박스, 실차 아님)**: 4개 블록을 Python으로 원본(base `25f21d4`) 위에 순서대로 적용해 anchor 전부 1회 매치, `python3 -m py_compile` 통과를 확인했다. 반영 스크립트(`99cha_lead_gate_carrot_ryu.ps1`)를 Replace-Block 패턴(63차/85차의 CRLF→LF 정규화 포함)으로 작성하고, 9절 "전달 전 필수 자가검증 체크리스트" 1~6번(BOM 없음/`core.autocrlf=false`/임시폴더 자동삭제/`Get-PythonCmd`+EOF공급/전체쓰기 WriteAllText 무BOM+BOM 재확인/anchor 결과 재확인)을 스크립트 코드 자체로 통과시켰다. 7번(전달할 .ps1에서 앵커 문자열을 추출해 SHA 고정 원본에 재시뮬레이션)도 실제 전달 파일에서 `$Old`/`$New` 4쌍을 정규식으로 추출해 원본에 재적용 → anchor 전부 1회 매치, 결과가 사전 설계 시뮬레이션과 동일, `py_compile` 재통과까지 확인했다. 이 세션은 pwsh(Linux)가 샌드박스에 설치돼 있지 않아 PowerShell 구문 자체의 실행 검증은 못 했고(수동 육안 검토만), Windows PowerShell 5.1 실행 검증도 아니다.

**미결정/다음(다음 세션 최우선)**: (a) 사용자가 `99cha_lead_gate_carrot_ryu.ps1` 실행 → push 확인(GitHub API/raw로 재확인). (b) 실차 배포 후 swaglog에서 `lead_gate` 태그로 g 값이 정상 범위에서 움직이는지, 특히 tFollow가 짧은 구간(123/124류)에서 평상시 g가 지나치게 자주 1 밑으로 떨어지는지 관찰(위 사용자 결정 (a) 관련). (c) 가능하면 97~98차에서 다룬 #5/#8/#22류 재현 상황에서 실제 감속이 완화되는지 확인. (d) 12절: 정적 분석/설계 단계이며 실차 검증은 미실시.

## 98차 (Claude · 분석/설계 결정 · 코드/지침 변경 없음) — 리드 감속 게이팅 26건 평가, 후보 B안(G2T: 투사 감쇠만, 시간차 2.2→1.5 s / TTC 12→6 s) 채택

**세션 시작(4절 0단계)**: `git ls-remote`로 carrot-ryu-note HEAD `4644f6d`를 얻어 SHA 고정 raw로 지침 문서(v2)를 조회했다(브랜치 URL 조회본과 바이트 동일). HANDOFF.md/CURRENT_STATUS.md도 같은 SHA로 읽었다. carrot-ryu `25f21d4`, carrot-ms `e324f67` 모두 변경 없음. HANDOFF.md의 Note Branch base(`13b49d3`, "97차 반영 push 대기")는 push 이전 값이었고 실제로는 `4644f6d`("97cha: devnotes - ...")로 반영돼 있음을 git clone/git log와 그 커밋의 변경 파일(WIP.md/HANDOFF.md/toolkit 9개)로 확인했다(노트 브랜치 커밋 목록의 GitHub API 조회가 rate limit에 걸려 git clone으로 대체, 16절). 이번 HANDOFF에서 정정.

**환경 복원/재현**: 사용자가 zip(drive-download-20260919T035223Z-1-001.zip, Git에 없음, 13절)을 다시 올렸다. toolkit/README.md 절차로 환경을 복원했다(스키마는 로그 기록 커밋 carrot-ryu-v1 `9ccf1206`에서 sparse checkout — 20절 8항 예외, README에 명시된 절차). 97차 toolkit을 처음부터 재실행해 32/33 t=84~95 폐루프 수치가 97차와 일치함을 확인했다(baseline -2.15, lpf1.0 -1.79, lpf2.0 -1.46, tau1.5 -1.85, noproj -1.96, 실제 로그 -2.39). aLeadK<-1.0 이벤트도 연속 간격 2 s 초과 분리 기준으로 26건(32/33 6, 37/38 5, 39/40 7, 123/124 7, 34 1)으로 재현됐다.

**이벤트 분류**: (1) #19~21(123/124 t≈24~35)은 t≈23에서 dRel이 46→33→20 m로 바뀌고 vRel>0(앞차가 자차보다 빠름), 실제 자차 최대 감속 -0.9 이내, 실제 최소 시간차 0.67~1.35 s다. 새 선행차 끼어들기로 추정(영상은 확인하지 않음)하며, 이 구간의 aLeadK<-1은 새 리드 인식 직후의 값으로 보여(확인하지 못함) 감속 게이팅 평가 대상으로 보지 않았다. #18(123/124 t≈11)은 끼어들기 이전의 약한 감속(vRel -0.6, 실제 최대 감속 -0.73)이라 별도 평가하지 않았고, 이 구간은 tFollow가 1.10이라 정상 추종 시간차가 이미 약 1.7 s였다(dRel 46.7 m, vEgo 27.5 m/s). #11(39/40 t=0.2)은 구간 시작부라 minGap 0.0으로 나와 판단 불가(원인 미확인). (2) 대부분 이벤트에서 실제 최소 시간차(dRel/vEgo)는 2.0~2.5 s로 여유가 있었다. 과민 후보 #5(2.25 s)·#22(2.09 s)와 97차의 정당 대조 #8(2.09 s)은 시간차만으로는 구분되지 않는다(실제 최소 TTC[dRel/-vRel]: #8 9.6 s, #5 14.8 s, #22 17.7 s).

**사후 필요 감속(needed_decel.py)**: 리드 궤적을 미리 안다고 가정하고 시간차 하한 1.0/1.2/1.5/1.8 s를 지키는 최소 상수 감속(m/s², 지연 0.3 s, 이벤트 시작~+16 s). #5는 0.71/0.76/0.85/0.95(실제 -2.39), #8은 0.48/0.53/0.64/0.81(실제 -3.70), #22는 모두 0(실제 -2.39). #5·#8·#22와 #18~21을 제외한 나머지는 h1.5 기준 0.3 이하. 사후 정보라 실시간 제어기가 쓸 수 없는 이상화 값이다. 97차에서 #8을 "정당한 강한 감속"으로 둔 것은, 사후 기준으로는 그만큼의 감속이 필요하지 않았다는 점에서 "앞차가 언제 멈출지 실시간으로 알 수 없어 보수적 반응이 불가피했을 수 있는 대조 사례" 정도로 정정한다.

**게이팅 후보(gating_eval.py)**: 관측 가능한 값만 사용한다. 시간차 h=gap/vEgo, TTC=gap/(vEgo-vLead)(접근 중일 때). g_h=clip((h_hi-h)/(h_hi-h_lo),0,1), g_t=clip((ttc_hi-TTC)/(ttc_hi-ttc_lo),0,1), g=max(g_h,g_t), 상승은 즉시·하강은 시정수 1 s. g=1이면 현행(투사 그대로), g=0이면 약화. 약화 방식은 투사 감쇠(tau_used=g*aLeadTau+(1-g)*1.5)와 리드 속도 저역통과(1 s) 두 가지이고 단독/동시 적용을 비교했다. 임계값 세트: 1안 h 1.2→2.0 s, TTC 5→9 s / 2안 h 1.5→2.2 s, TTC 6→12 s / 3안 h 1.2→1.8 s(시간차만). 변형 이름: G1/G2/G3(감쇠+저역통과 동시), G1L/G2L(저역통과만), G1T/G2T(투사 감쇠만). 별칭 A=G1T, B=G2T. 복제 폐루프에 로그 리드를 외생 입력으로 재생하고(창: 이벤트 시작 -1 s ~ +9 s), 위험 상황에서 현행 감속이 복원되는지 보려고 초기 거리에 -10/-20 m를 더한 스트레스 시나리오도 돌렸다.

**결과(복제 폐루프, 각 칸은 최대 감속 m/s² / 최소 시간차 s, 거리 offset 0)**:

| 변형 | #5 (32/33 t≈86, 과민) | #8 (37/38 t≈54.5, 강한 감속) | #22 (123/124 t≈54, 과민) |
|---|---|---|---|
| 현행(base) | -2.10 / 2.15 | -2.75 / 2.08 | -2.05 / 2.21 |
| G1 (감쇠+저역통과) | -1.96 / 1.70 | -2.12 / 1.75 | -1.03 / 1.74 |
| G2 (감쇠+저역통과) | -2.09 / 1.82 | -2.34 / 1.86 | -1.05 / 1.79 |
| G3 (시간차만) | -1.84 / 1.58 | -1.76 / 1.57 | -1.03 / 1.74 |
| G1L (저역통과만) | -1.81 / 1.94 | -2.34 / 2.04 | -1.51 / 2.10 |
| G2L (저역통과만) | -2.00 / 1.99 | -2.54 / 2.05 | -1.52 / 2.10 |
| G1T = A안 (투사 감쇠만) | -1.83 / 1.93 | -2.17 / 1.89 | -1.20 / 1.98 |
| G2T = B안 (투사 감쇠만) | -1.92 / 1.96 | -2.31 / 1.93 | -1.21 / 1.98 |

스트레스(같은 리드 궤적, 초기 거리 -10 m / -20 m):

| 변형 | #5 -10m | #5 -20m | #8 -10m | #8 -20m | #22 -10m | #22 -20m |
|---|---|---|---|---|---|---|
| 현행 | -2.37 / 1.76 | -2.66 / 1.33 | -3.12 / 1.62 | -3.34 / 1.15 | -2.34 / 1.90 | -2.58 / 1.58 |
| G1T (A안) | -2.07 / 1.63 | -2.51 / 1.31 | -2.57 / 1.51 | -3.34 / 1.15 | -1.44 / 1.74 | -1.80 / 1.48 |
| G2T (B안) | -2.17 / 1.67 | -2.66 / 1.33 | -2.75 / 1.57 | -3.34 / 1.15 | -1.53 / 1.77 | -2.11 / 1.54 |

- 감쇠와 저역통과를 동시에 쓰면(G1/G2/G3) 감속은 더 줄지만 시간차 손실이 커서 효율이 나빴다. 단독 적용 쪽이 절충이 낫고, 그중 투사 감쇠만(G1T/G2T)이 #8·#22에서 감속 저감이 크다.
- #8을 -20 m(시간차 1.15 s)로 줄이면 G1T/G2T 모두 g가 1까지 올라 현행과 동일한 -3.34가 나왔다(G1/G2/G3는 이 시나리오를 돌리지 않음). B안(G2T)은 #5 -20 m에서도 현행과 동일(-2.66).
- 나머지 8건(#0·1·2·12·13·16·17·23, 복제 baseline이 -0.32~-0.99로 약함, base/G1T/G2T 비교): 최대 감속 차 0.15 m/s² 이하, 최소 시간차 손실 0.14 s 이하(재작성본 재실행 기준). 과민 반응은 #5·#8·#22에 집중돼 있다.
- 복제 baseline이 실제보다 약한 이벤트: #0 -0.48(실제 -1.19), #1 -0.61(-1.37), #2 -0.55(-1.37), #12 -0.70(-1.21), #13 -0.48(-1.21), #16 -0.32(-1.59), #17 -0.99(-1.59), #23 -0.70(-1.37). 원인은 확인하지 못했다(앞차 추종 외 감속 요인, 로그 코드 차이, 복제 오차 등 가능성만 있음). 과민 후보 3건은 실제 -2.39/-3.70/-2.39 대비 복제 -2.10/-2.75/-2.05.

**결정(사용자)**: B안(G2T) 채택 — 투사 감쇠(aLeadTau→1.5)만 게이팅, 임계값 시간차 h_lo 1.5 s / h_hi 2.2 s, TTC t_lo 6 s / t_hi 12 s. Claude가 제안한 근거: A안과 B안의 효과 차이가 작고(#22 -1.20 대 -1.21, #5 -1.83 대 -1.92, #8 -2.17 대 -2.31), 복제본이 강한 감속을 과소 재현하고 실차 검증이 없어 보수적으로 시작하는 편이 낫고, 이후 임계값만 바꿔 조정할 수 있다. 사용자가 승인한 것은 B안(후보와 임계값 세트)이며, g의 상승 즉시/하강 1 s, 투사 감쇠 목표 1.5는 복제 평가에서 쓴 설정이지 개별 승인된 설계값이 아니다. 사용자는 코드 설계보다 devnotes 저장을 먼저 하도록 지시했다.

**한계**: (1) 결정적 사례가 3건(#5·#8·#22)뿐이라 표본이 작다. (2) MPC 복제본은 casadi/IPOPT 근사이며 acados 실물이 아니고, 강한 감속을 과소 재현한다(위 표). (3) 액추에이터 1차 지연(0.35 s)·지령 시점 0.4 s는 가정값이고 리드는 로그 재생이다. (4) 로그는 v1(`9ccf1206`) 기록분이라 tFollow(1.6 등)가 현행 carrot-ryu와 다를 수 있다. (5) #5는 어느 안이든 감속 저감폭이 작아(현행 -2.10 → -1.9 안팎) 화면에서 본 -2.4 수준의 과민함이 게이팅만으로 크게 사라지지 않을 수 있다. (6) 임계값이 절대 시간차(1.5~2.2 s)라서 tFollow 설정에 따라 평상시 g가 달라진다: 123/124 t≈8~30은 tFollow 1.10이고 정상 추종 시간차가 약 1.7 s로 이 구간 안에 들어가 g가 중간값이 된다(이 구간은 게이팅 시뮬을 돌리지 않았다). **정적 분석/오프라인 시뮬레이션 단계이며 실차 검증: 미실시.**

**toolkit 등록(14절)**: `devnotes/toolkit/lead_decel/`에 events.py, needed_decel.py, gating_eval.py 3개와 README/CHANGELOG 항목을 추가했다(py_compile 통과). 이 스크립트들은 첫 작성분이 반영 전에 세션 중단으로 유실돼, 같은 zip으로 환경을 다시 구성해 다시 작성했다. 재작성본을 재실행해 위 기록 수치와 대조했다: 이벤트 표(26건, 실제 최대 감속/최소 시간차/TTC), 사후 필요 감속 표, 게이팅 평가(메인 3건x8변형, 스트레스 3건x2거리x3변형, 나머지 8건x3변형)가 기록과 일치했다(예외: 나머지 8건 중 #16의 복제 baseline이 첫 기록 -0.22였으나 재실행에서 -0.32가 나와 재실행 값으로 정정했고 원인은 확인하지 못했다. 나머지 8건의 개별 base/G1T/G2T 값은 첫 기록이 남아 있지 않아 baseline 값과 요약 범위만 대조했다). 창 정의: events.py 실제 지표 창은 이벤트 시작 -3 s ~ +11 s, 폐루프 시뮬 창은 -1 s ~ +9 s, needed_decel은 시작 ~ +16 s. 97차 스크립트 5개는 변경 없음. 폐루프 1회가 CPU 1코어 기준 약 10 s이고, 백그라운드 실행은 호출이 끝나면 죽는 환경이 있어 setsid nohup을 써야 했다(README 참고).

**미결정/다음**: (a) 현행 carrot-ryu `25f21d4`의 long_mpc.py를 먼저 읽고 B안 게이팅 삽입 위치·최소 변경안 설계(10절): 게이트 입력(dRel/vLead/vEgo)을 얻는 방법, 현행 tFollow가 로그와 다른 점의 영향(임계값이 절대 시간차라 tFollow 설정별 평상시 g 확인 포함), 새 Params 키를 쓴다면 params_keys.h 동시 등록, 임계값을 Params로 노출할지(사용자 결정), 게이트 값을 로그에 남길지. (b) 설계 승인 후 9절 절차로 반영. (c) 실차 검증(#5류 재현). 이번 세션은 코드 변경 없음.

## 97차 (분석 전용 · 코드/지침 변경 없음) — 선행차 감속 과민 반응 로그 분석: 원인 분해, MPC 복제본 what-if, toolkit 등록

**세션 시작(4절 0단계)**: `git ls-remote`로 carrot-ryu-note HEAD `13b49d3`을 얻어 SHA 고정 raw로 지침 문서(v2)를 조회했다(브랜치 URL 조회본과 바이트 동일). HANDOFF.md/CURRENT_STATUS.md도 같은 SHA로 읽었다. carrot-ryu `25f21d4`, carrot-ms `e324f67` 모두 변경 없음(drift 없음). 이번 세션은 코드/지침 변경 없이 로그 분석만 했다.

**분석 대상**: 사용자가 Drive에서 내려받아 올린 zip(원본은 커밋하지 않음, 13절)의 rlog 세그먼트 9개(route `0000042f--32975bbd0f`, seg 32·33·34·37·38·39·40·123·124), 스크린샷 5장(2026-09-18 12:17~13:49), tmux 로그. 문제 제기: "선행차와 거리 여유가 충분한데 선행차 감속에 자차가 -2.4 m/s²까지 과민하게 감속한다."

**로그 기록 코드 버전(중요)**: tmux metadata.json 기준 로그는 `carrot-ryu-v1`(`9ccf1206`)에서 기록됐다. 현행 carrot-ryu(`25f21d4`)의 `long_mpc.py`는 다음이 다르다: SafeFollowState 제거, get_T_FOLLOW의 리드 기반 예외 제거, `desired_distance`가 `displayed_follow_distance()`(표시 전용, 솔버 장애물은 바꾸지 않음)로 변경. `process_lead`/`extrapolate_lead`/`desired_follow_distance`/OCP 비용식은 동일하다. 따라서 결론은 현행 코드에도 적용되지만, 로그의 tFollow/desiredDistance 값은 현행 코드가 기록할 값과 다르고, "desiredDistance에 rate-limit" 안은 현행 코드에서는 표시값만 바꾸게 된다(실제 레버는 솔버에 들어가는 장애물 궤적).

**이전 진단의 재정정**: 이전 대화에서 넘어온 진단은 1차로 "aLeadK 무감쇠 투사(B)가 원인", 2차로 "(B)는 기여 미미, desiredDistance 공식이 v_lead를 즉시 반영하는 것이 진짜 원인"이라고 했다. 2차 정정의 근거인 로그의 `desiredDistance`는 현재 시각의 값일 뿐 MPC가 실제로 쓰는 미래 장애물 궤적(`x_lead_traj + v_lead_traj²/(2b)`)을 반영하지 않으므로 (B)를 배제할 근거가 못 됐다. 복제본 실험 결과 두 요인이 사건마다 다른 비중으로 섞여 있다(아래).

**메커니즘 확인**: (1) 로그로 역산하면 `desiredDistance ≈ tFollow·vEgo + (vEgo²-vLead²)/(2b) + s`에 b≈2.47, s≈11.6(n=9570, RMSE 1.55 m; 코드의 comfortBrake 2.4(×주행모드 계수)와 근접, 계수 값은 미확인). 리드 속도가 1 m/s 줄면 요구거리는 vLead/b(대략 8 m)만큼 커지는 반면 실제 dRel은 초당 약 1 m 줄 뿐이다. (2) 리드 감속 중 로그의 aLeadTau가 평시 1.5에서 0.00~0.05로 떨어져 있어(예: 32/33 t=87.5 s 0.04), `extrapolate_lead`는 리드가 투사 구간(10 s) 내내 거의 같은 감속을 유지한다고 가정한다. aLeadTau 갱신 규칙은 `radar_motion/controller.py`(lead_dynamics.a_lead_tau, conventional radard 모사)에 있으며 그 조건식 자체는 이번 세션에서 확인하지 못했다.

**정량 결과(복제 폐루프, 최대 감속 m/s²)**:

| 이벤트 | 실제 aEgo | 복제 baseline | v_lead 저역통과 1s | 투사 감쇠 τ=1.5 | 투사 없음 |
|---|---|---|---|---|---|
| 32/33 t≈86 (스샷) | -2.39 | -2.15 | -1.79 | -1.85 | -1.96 |
| 123/124 t≈54 | -2.39 | -2.06 | -1.52 | -1.21 | -1.18 |
| 37/38 t≈54.5 (대조: 정당한 강한 감속) | -3.70 | -2.75 | -2.27 | -2.08 | -2.06 |

- 최소 시간차(gap/vEgo, 복제): 32/33 baseline 2.13 s → 저역통과1s 1.90 / τ1.5 1.91 / 투사없음 1.65. 123/124 baseline 2.20 → 2.09 / 1.98 / 1.81. 37/38 baseline 2.08 → 2.04 / 1.87 / 1.61.
- 123/124 t≈54~58: 리드가 105→81 km/h로 약 3초 감속한 뒤 재가속(t=57.5 aLeadK +1.22). dRel은 60 m 아래로 내려가지 않았는데 자차는 102→85 km/h로 aEgo -2.3까지 감속. aLeadTau가 0.00~0.05인 구간이라 (B)가 지배적(-2.06 → -1.2). 이전 스캔(margin>8 & aLeadK<-1 기준)에서는 잡히지 않았다.
- 32/33: 투사를 빼도 -1.96이 남는다 → 나머지는 요구거리 공식이 리드 현재속도를 즉시 반영하는 구조. 사후(hindsight) 기준으로 리드 궤적을 안다고 가정하면 시간차 1.6 s 유지에 필요한 상수 감속은 onset 85.5~87.0 s에서 약 0.85~1.10 m/s²(시간차 1.2 s 기준 0.65~0.9)로, 실제 피크의 절반 이하다.
- 이벤트 스캔: aLeadK<-1.0 이벤트 26건(32/33 6, 37/38 5, 39/40 7, 123/124 7, 34 1). 자차 최대 감속은 37/38 t≈54.5(-3.70, 이미 근접 상태였던 정당한 반응), 32/33 t≈86(-2.39), 123/124 t≈54(-2.39), 나머지는 -1.6 이내.
- 어느 변형도 선택적이지 않다(대조 사례도 함께 약해짐). 대조 사례는 복제본이 실제를 과소 재현(-2.75 대 -3.70)하므로 안전 쪽 결론은 약하다. 위험거리 정의(고정 거리/TTC/desired 대비 비율)를 포함한 게이팅 설계가 핵심 과제.

**한계**: (1) MPC 복제본은 casadi/IPOPT 근사이며 acados 실물이 아니다: 로그 accels 궤적 대비 RMSE ≈0.22 m/s²(jerk_factor 1.0이 후보 0.05~1.0 중 최적), 피크 시점이 실제보다 늦고 강한 감속은 과소 재현. (2) 폐루프 액추에이터 모델(1차 지연 0.35 s, 지령 시점 0.4 s)은 가정값. (3) 리드는 로그를 외생 입력으로 재생. (4) 세그먼트 9개, 리드 이벤트 26건의 작은 표본. (5) 로그는 v1 코드 기록분. **정적 분석/오프라인 시뮬레이션 단계이며 실차 검증: 미실시.**

**toolkit 등록(14절)**: `devnotes/toolkit/lead_decel/`에 parse_lead_log.py, merge_lead_series.py, counterfactual.py, mpc_replica.py, closed_loop.py 5개와 README/CHANGELOG 항목을 추가했다. 샌드박스에서 정리본을 처음부터 다시 돌려 baseline -2.15 등 수치가 재현됨을 확인했다(py_compile 통과). 환경 구성은 toolkit/README.md 참고(pycapnp/zstandard/casadi, 로그를 기록한 커밋의 cereal 스키마).

**미결정/다음**: (a) 리드 감속 이벤트 26건 전체에 게이팅 후보(거리 여유·TTC 기반 투사 페이드 + v_lead 저역통과)를 돌려 "과민 사례는 줄고 대조 사례는 유지되는지" 검증, (b) 후보가 서면 현행 carrot-ryu 코드 기준으로 설계(10절, 실제 반영은 9절 절차), (c) 위험거리 임계값 정의는 사용자 결정 필요. 분석 원본 zip은 Git에 없으므로 재개 시 다시 업로드가 필요하다.

## 96차 (지침 문서 갱신 · 코드 변경 없음) — 9절 체크리스트 7번(앵커 시뮬레이션) 추가, 샌드박스 pwsh 실행 검증 도입

**세션 시작(4절 0단계)**: `git ls-remote`로 carrot-ryu-note HEAD `ac45f91`을 얻어 SHA 고정 raw로 지침 문서(v2)를 조회했다(브랜치 URL 조회본과 내용 동일). 이어 HANDOFF.md/CURRENT_STATUS.md를 같은 SHA로 읽었다. carrot-ryu HEAD `25f21d4`(HANDOFF와 일치, 변경 없음), carrot-ms(happymaj11r) HEAD `e324f6735d3606800045ed6b28f41e79b17e5498`(93차 체크포인트와 동일, 신규 커밋 없음, 2절).

**HANDOFF 표기 시차 확인(16절)**: 95차 HANDOFF.md는 Note Branch base를 `5e67047`, 계속분(WIP.md/FINDINGS.md/HANDOFF.md)을 "실행/push 대기"로 적었으나 실제 note HEAD는 `ac45f91`이었다. 클론해서 확인한 결과 `ac45f91`(95cha2)이 바로 그 3개 파일(WIP.md +22, FINDINGS.md +18, HANDOFF.md)이었다. HANDOFF.md가 push 전 상태로 작성된 채 그 push에 함께 실려서 생긴 표기상 시차이며 반영 누락은 아니었다.

**지침 문서 변경(19절 절차)**: 변경 이유(95차 v2 스크립트가 앵커 텍스트 오기입으로 `got 0` 중단 -- 기존 9절 체크리스트 1~6번은 앵커 텍스트 자체를 검증하지 않음, 핵심 발견 45) -> 변경안(9절 "전달 전 필수 자가검증 체크리스트"에 7번 추가) 제시 -> 사용자 승인 -> `96cha_pi_checklist7_v1.ps1` 전달 -> 사용자가 "완료"라고만 보고(실행 로그는 전달되지 않음). 완료로 가정하지 않고 GitHub에서 직접 재확인했다(16절): carrot-ryu-note HEAD `913b6f1`(부모 `ac45f91`), 변경 파일 1개(`devnotes/PROJECT_INSTRUCTIONS_carrot-ryu.md` +4/-0), SHA 고정 raw 파일의 SHA-256 `83bf4294200da038678ce67266696eda40b20585748769f29bd080fa7ff84618`이 사전 계산한 기대 결과와 바이트 단위로 동일, 첫 3바이트 `23 20 43`(BOM 없음), carrot-ryu는 `25f21d4` 그대로.

**검증 방식 변경**: 이전 세션 기록은 "샌드박스에는 PowerShell이 없어 Python으로 시뮬레이션"이었다. 이번 세션에서 샌드박스 허용 도메인(api.github.com, github.com)만으로 GitHub 릴리스의 PowerShell 7.6.6 linux-x64 tarball(약 76MB)을 받아 실행할 수 있음을 확인했다(`DOTNET_SYSTEM_GLOBALIZATION_INVARIANT=1` 지정). 이를 이용해 전달 스크립트를 (1) 구문 파싱(오류 0), (2) 원본 문서를 커밋한 로컬 bare 저장소를 `$RepoUrl`로 바꾼 테스트 사본에 대해 clone->치환->검증->commit->push 전체 실행(결과 파일이 기대 결과와 바이트 동일, 임시 폴더 잔존 0), (3) 음성 테스트 2건(앵커 공백 1개 오기입 -> `got 0`, 원본 SHA-256 불일치)으로 검증했고, 두 경우 모두 push 없이 중단됐다. 한계: Linux의 pwsh 7이지 사용자 PC의 Windows PowerShell 5.1이 아니다(5.1 고유의 콘솔 코드페이지/`Set-Content` 인코딩 동작은 재현하지 못한다). 샌드박스는 세션마다 초기화되므로 필요하면 매번 다시 받아야 한다.

**스크립트 설계 메모**: 대상 파일의 "변경 전 SHA-256"과 "기대 결과 SHA-256"을 미리 계산해 스크립트에 박아 넣고, 원본 해시 불일치/앵커 매치 != 1/결과 해시 불일치 중 하나라도 걸리면 commit 전에 중단하게 했다(1회 매치가 "의도한 결과"까지 보증하지 않는다는 핵심 발견 42와 같은 취지의 강화). git 호출은 종료 코드로만 판정하는 래퍼(`Invoke-Git`)로 감쌌다. Windows PowerShell 5.1에서 네이티브 stderr 진행 출력이 `$ErrorActionPreference='Stop'` 아래 예외가 되는 알려진 동작을 예방하려는 것이며, 이번 세션에서 5.1로 재현하지는 않았다.

**실차 검증**: 대상 아님(문서 변경, 12절 무관). 코드 변경 없음(carrot-ryu `25f21d4` 그대로).

## 95차 (devnotes 정리 + 디바이스 배포 확인 · 코드 변경 없음) — carrot-ryu `25f21d4` 디바이스 실배포 확인, 첫 실차 UI 검증, 반영 스크립트 사고 3회(모두 commit 전 안전 중단)

**carrot-ms 재확인(2절)**: `git ls-remote`로 happymaj11r/openpilot(carrot-ms) HEAD가 여전히 `e324f6735d3606800045ed6b28f41e79b17e5498`임을 확인했다(93차 체크포인트와 동일, 신규 커밋 없음).

**디바이스 배포(20절 7항)**: 사용자가 디바이스 현재 상태(carrot-ryu-v1, `c81aef07`)를 확인한 뒤, 도구 탭 "브랜치 변경"(브랜치 목록에서 carrot-ryu 재선택 -> 재체크아웃/재빌드)으로 origin/carrot-ryu로 전환했다. 61차 force reset으로 히스토리가 갈라져 있어 일반 git pull(fast-forward)로는 받을 수 없는 상태였다. 사용자가 올린 tmux 로그 2건(전/후)의 metadata.json git_commit과 부팅 로그 "Carrot GitBranch = ..."로 carrot-ryu-v1(`c81aef07`) -> carrot-ryu(`25f21d406d23bfb79ad45a67890cc39e3ad9e67b`, 93차 최종 HEAD와 일치) 전환을 재확인했다(11절).

**첫 실차 UI 검증(12절, 정차 상태 스크린샷 1장 기준)**: 항목 30~36(스크린샷 캡처 체인)과 항목 13~19(우측하단 경로안내 박스)가 정상임을 확인했다(상세: CURRENT_STATUS.md 95차 계속). 미확인/이월: 항목 1·2(종방향 안전장치), carrot-ms 4건(b4f751f4 등)의 실주행 동작, Drive 업로드 파이프라인, 화면녹화 탭 사진 업로드 UI(22·23·26), 녹화 버튼 깜빡임(28).

**route 로그**: 사용자가 올린 대용량 route 로그(qcamera.ts+rlog.zst, route 00000436--2edd613f1e--8)는 "실차 검증에 필요하면 쓰라고 준 것"이라고 사용자가 밝혔다(별도 분석 요청 아님). 샌드박스에 openpilot cereal 스키마 파싱 환경이 없어 심층 분석은 하지 않았고, 이 로그는 현재 세션 샌드박스에도 남아 있지 않다(필요 시 재업로드).

**반영 스크립트 사고(모두 commit/push 전 안전 중단, 반영 사고 없음)**:
1. 1차 시도(콘솔에 직접 붙여넣기): 한글 리터럴이 콘솔 코드페이지로 깨져 WIP_SYNC.md anchor 0회 매치로 중단 -> `.ps1` 파일 저장 + UTF-8 명시 읽기로 전환.
2. 직전 `.ps1`: `Set-Location` 후 상대경로 `WriteAllText`가 .NET 프로세스 작업 디렉터리(콘솔 시작 위치 `C:\WINDOWS\system32`) 기준으로 풀려 실패 -> 절대경로(`Join-Path $RepoRoot ...`)로 고친 `95cha_devnotes_v2.ps1`로 교체(9절 PowerShell 필수 규칙과 같은 사례).
3. `95cha_devnotes_v2.ps1`: CURRENT_STATUS.md anchor `$csOld`가 `반영 스크립트 실행/push 대기. ...`로 시작했으나 94차 항목의 실제 문구는 `...적용). 실행/push 대기. ...`라서 0회 매치로 중단. SHA 고정 원본(`f8d92c6`)으로 Linux에서 재현했다: 스크립트 앵커 0회 / 접두를 뺀 앵커 1회. 핵심 발견 44(CRLF 정규화 누락)와 증상은 같지만 원인은 앵커 텍스트 오기입임을 확정했다(이 스크립트는 CRLF 정규화가 이미 들어 있었고 Linux에서도 0회이므로). 상세: FINDINGS.md 핵심 발견 45.
   -> `95cha_devnotes_v3.ps1`: 앵커 정정, HANDOFF 마지막 개행 복원(핵심 발견 37), 치환 결과 검증(핵심 발견 42) 추가. 전달 전에 실제 .ps1에서 앵커를 추출해 SHA 고정 원본에 시뮬레이션하던 중, 새로 넣은 "맨 앞 200자 불변" 검사가 WIP_SYNC.md 앵커(약 128번째 바이트부터 시작)와 겹쳐 정상 치환도 오류로 중단시킬 결함을 발견해 100자로 수정했다.

**push 확인(16절)**: 사용자가 v3 실행 후 `f8d92c6..5e67047` push 성공 로그를 전달했다. 로그만으로 완료 처리하지 않고 재확인했다: carrot-ryu-note HEAD `5e67047d2114f20b765df9a558a45ace41cc8e5b`, 부모 `f8d92c6`, 변경 파일 정확히 3개(CURRENT_STATUS.md +2, HANDOFF.md +21/-19, WIP_SYNC.md +7). SHA 고정 raw로 조회한 결과 WIP_SYNC.md CRLF 238줄 전부 유지, CURRENT_STATUS.md/HANDOFF.md LF 유지, 3개 파일 BOM 없음, HANDOFF.md 마지막 개행 유지, 95차 bullet/체크포인트 각 1개를 확인했다. (커밋 API가 403(rate limit)이라 `git clone --depth 2`로 대체 확인.) carrot-ryu(코드)는 `25f21d4` 그대로다.

**이번 계속분**: WIP.md 95차 회차(이 항목), FINDINGS.md 핵심 발견 45, HANDOFF.md 갱신. 준비 중 FINDINGS.md가 혼합 개행(상단 889줄 CRLF, 890행 이후 LF)임을 발견해, 이 파일은 개행을 보존하는 삽입 방식으로 반영한다.

실차 검증: 위 첫 실차 UI 검증(정차 스크린샷 1장) 범위 외에는 미실시. 코드 변경 없음.

## 94차 (devnotes 정리만 · 코드 변경 없음) — WIP.md "# WIP" 헤더 중복 제거 + mojibake 구간 안내 추가

사용자 요청(직전 세션 HANDOFF "미완료" 3번, "WIP.md 파일 맨 끝의 mojibake 처리 여부, '# WIP' 헤더 중복 정리 여부")에 따라 두 건을 조사/처리했다.

1. **"# WIP" 헤더 중복**: 파일 전체에서 `# WIP`가 정확히 2회 등장함을 확인(1번째 줄 정상 제목, 961번째 줄은 44차 항목 바로 앞에 낀 스트레이 중복 — 과거 어느 세션의 반영 스크립트가 최상단 삽입 지점을 잘못 잡으며 끼어든 것으로 추정). 실제 회차 내용은 건드리지 않고 중복 헤더 줄 1개만 제거.
2. **mojibake 구간(11차~1차, 구 라인 1612~1814)**: 역변환(문자열을 CP949로 재인코딩 후 UTF-8로 재디코딩)을 시도한 결과 160곳 이상에서 인코딩 자체가 실패(문자가 이미 제어문자 `\x80` 등으로 치환된 상태)하고 나머지도 부분 복원에 그쳐, 단일 인코딩 사고가 아니라 여러 단계가 겹친 손상이며 byte-exact 복구가 불가능함을 확정함. 사용자에게 (a)그대로 둠 (b)안내 문구만 추가(원문 보존) (c)삭제, 3가지를 제시했고 사용자가 위임 -- 7절 "기존 기록 임의 삭제 금지" 원칙에 따라 (c)는 배제하고 (b)를 채택: 11차 헤더 직전에 손상 사실과 대체 참고처를 안내하는 문단만 추가, 원문(mojibake 텍스트) 자체는 한 글자도 수정/삭제하지 않았다.

실차 검증: 해당 없음(devnotes 텍스트 편집만).

## 93차 계속 — carrot-ms 557e6f6a 반영 완료 확인(carrot-ryu `25f21d4`), e324f67 제외 확정, 89차 검토대상 4건 종결

사용자가 코드/devnotes 두 스크립트 실행 완료를 알려왔다. 실행 로그는 전달되지 않아, 완료로 가정하지 않고 GitHub에서 직접 재확인했다(16절).

**push 확인**: carrot-ryu HEAD `25f21d406d23bfb79ad45a67890cc39e3ad9e67b`(2026-09-19 14:54:13 +0900, "93cha: reapply carrot-ms 557e6f6a - precompiled_worker diagnostics identify model artifact and input size"), 부모 `9eced40`, 변경 파일 정확히 1개(`openpilot/selfdrive/modeld/precompiled_worker.py`, +3/-1), 결과 blob `d04b52ce89e54698215cce8cf84bab62d5e846f7`가 원본 post-image와 일치. carrot-ryu-note HEAD `bd69ab0139874c7e36d6f58552923a291fc98a92`(14:56:57 +0900), 부모 `1f98304`, 변경 파일 4개(CURRENT_STATUS 2/1, HANDOFF 23/22, WIP 20/0, WIP_SYNC 13/0)이고 SHA 고정 raw로 조회한 4개 파일의 sha256이 스크립트에 내장한 사전 계산값과 전부 일치(WIP_SYNC.md의 CRLF 유지). 557e6f6a 반영 완료 확정.

**e324f67 분석**("Require clear persistent vision for distinct stopped-lead handoff", ajouatom 2026-09-19 08:22:02 +0900, carrot-wip `1130b074` cherry-pick, `radar_motion/primary.py` + `test_radar_motion_predictor.py` 2파일 +112/-2): 앞 레이더가 붙잡고 있는 정지 lead(held)를, 5 m를 넘게 더 가까운 다른 정지 물체로 갈아탈 수 있게 조건을 넓힌다(비전이 뚜렷하게 더 가까운 쪽을 지지하고 0.5 s 지속될 때만).
1. 호출 경로: `radard` 프로세스는 `process_config.py` 177행에서 `openpilot.selfdrive.carrot.radar.radard_dpath`로 뜨고, `DPathRadarController`(controller.py 480~481행)가 `VisionRadarMatcher` 2개를 만들며, 새 분기가 들어가는 `_stationary_closer_handoff_ready`는 primary.py 3672행에서 호출된다.
2. 새 분기는 붙잡은 정지 점(stationary)과 더 가까운 점(moving) 두 개의 서로 다른 레이더 점이 있어야 하고, 두 점의 거리 차(`stationary.d_rel - moving.d_rel`)가 양수여야 한다. 점이 하나뿐이면 성립할 수 없다.
3. 이 차량의 실제 설정(사용자가 올린 `params_backup-1.json`): `CarSelected3`="Hyundai Genesis 2015-16", `HyundaiCameraSCC`=1, `EnableRadarTracks`=0, `EnableCornerRadar`=0. opendbc상 DH 2015는 `HYUNDAI_GENESIS`(flags `CHECKSUM_6B | LEGACY`, `MANDO_RADAR` 플래그 없음 = `Bus.radar` DBC 없음).
4. `radar_interface.py`: `radar_tracks = EnableRadarTracks >= 1`이 False라 트랙 파서는 읽지 않고(`if self.radar_tracks and self.rcp_tracks`), 코너 오브젝트 파서도 `EnableCornerRadar=0`으로 꺼져 있다. 발행되는 것은 `_update_scc`뿐이며 이는 고정 ID(`SCC_TID`) 점 하나만 채운다. 따라서 이 설정에서는 서로 다른 레이더 점 2개가 존재하지 않아 새 분기가 발동할 수 없다(mode 2 SCC fallback도 `stationary_points=()`로 호출하나 이 장치는 mode 0).
5. 반영해도 이 차량에서 실행되지 않을 가능성이 높고, primary.py(3,885줄)에서 carrot-ms와의 차이만 늘어난다. 원저자의 검증(1,201프레임 차량 replay)은 다른 차량 데이터라 DH 근거가 아니다.

**분석 중 정정**: 분석 중간에 "EnableRadarTracks 기본값 0이면 `radarUnavailable=True`"라고 추론했으나, 실제 설정은 `HyundaiCameraSCC=1`이라 `CAMERA_SCC` 플래그가 켜져 interface.py 197~198행에 의해 `radarUnavailable=False`이다. 결론(레이더 트랙 미사용, SCC 단일 점)은 위 4번의 `radar_tracks=False`로 그대로 유지된다.

**결정**: 사용자 승인 "제외." -- e324f67 제외 확정. 반영 없음, 코드 변경 없음. 재검토 트리거: `EnableRadarTracks`를 0보다 크게 바꾸거나 `EnableCornerRadar`를 켜서 앞 레이더 트랙/코너 오브젝트를 실제로 쓰게 될 때.

**종결**: 89차 검토대상 4건(b4f751f4/4d1a3ded/ec95363a/557e6f6a) 반영 완료, 11건 + e324f67 = 12건 제외 확정으로 carrot-ms 61차 리셋 이후 16건 전부 분류 종결. carrot-ms HEAD는 `e324f67` 그대로(`git ls-remote` 재확인).

한계: `params_backup-1.json`은 백업 파일이라 백업 시점과 현재 장치 값이 같은지는 확인하지 못했다. 위 판단은 정적 코드 읽기이며 실차 검증: 미실시. pytest 미실시. 다음: 다음 세션 시작 시 carrot-ms에 `e324f67` 이후 신규 커밋이 있는지 확인(2절), 없으면 36개 항목 + 재적용분(b4f751f4/4d1a3ded/ec95363a/557e6f6a)의 실차 검증 준비(실기기 배포 여부는 20절 7항에 따라 사용자 판단).

## 93차 — carrot-ms 557e6f6a(precompiled_worker 진단 메타데이터) 상세 대조 완료, 반영 스크립트 준비(실행/push 대기) + ec95363a push 확인(carrot-ryu `9eced40`)

사용자가 세션 시작 지침(지침 문서 조회)에 이어 "557e6f6a 착수"로 이번 항목을 지정했다. 지침 문서(v2)를 브랜치 URL과 SHA 고정 URL(carrot-ryu-note `1f98304`) 양쪽으로 조회해 두 결과의 sha256이 동일함(`c57f27c3c2c916a0...`)을 확인한 뒤 진행했다. `git ls-remote`로 carrot-ryu HEAD가 `9eced40`(HANDOFF.md 92차에 기록된 base `f1e920d`와 다름), carrot-ryu-note HEAD가 `1f98304`임을 확인해 16절 절차로 재검증했다.

**ec95363a push 확인(16절)**: carrot-ryu `9eced40`(2026-09-19 14:32 +0900, "92cha: reapply carrot-ms ec95363a - batch lane dash geometry, separate UI CPU timing from render waits")의 부모가 `f1e920d`이고, `f1e920d..9eced40` 변경 파일이 정확히 8개(+185/-39, 원본 ec95363a와 동일 규모)임을 blobless clone으로 확인했다. 8개 파일 각각의 결과 blob이 원본 patch의 post-image 인덱스 해시와 전부 일치한다(augmented_road_view.py `64b9edc213`/model_renderer.py `887c628ed2`/render_diagnostics.py `0fd1e19b76`/road_markings.py `356e1b5c20`/test_carrot_model_renderer.py `4939c12528`/test_carrot_model_renderer_lane_visibility.py `aacc28093b`/test_render_diagnostics.py `790d59f921`/test_ui_debug_hud_schema.py `6f9a943cd1`). 이로써 ec95363a는 반영 완료로 확정. carrot-ms(happymaj11r) HEAD는 `e324f67` 그대로(신규 커밋 없음), ryujmin97/openpilot 브랜치 구성은 carrot-ryu/carrot-ryu-note/carrot-ryu-v1 3개로 문서와 일치한다.

**557e6f6a 원본**: `github.com/happymaj11r/openpilot/commit/557e6f6a.patch` 직접 조회. carrot-wip `2fd77be4`의 cherry-pick(ajouatom, 2026-09-18 16:47:40 +0900), 제목 "Identify model artifact and input size in worker diagnostics". 변경은 `openpilot/selfdrive/modeld/precompiled_worker.py` 1파일 +3/-1: 매 추론마다 `diagnostics.record(context=...)`에 넘기는 context에 기존 `gpu_arch` 외에 `format`/`camera_width`/`camera_height`/`input_bytes`/`model_sha256`을 추가한다. 원본 커밋 메시지는 타이밍 메타데이터 전용이며 설정/주행 동작 변경이 없다고 밝히고 있고, 코드상으로도 record 호출의 context 인자만 바뀐다(pipe 프로토콜/컴파일된 그래프 변경 없음).

**충돌/런타임 검증**:
1. carrot-ryu `9eced40`의 precompiled_worker.py를 SHA 고정 raw로 조회해 `git hash-object`를 계산: `1c2e2a3b5e6dbdfc4545b1595094bf5d81872ada`로 patch의 pre-image(`1c2e2a3b5e`)와 byte-exact 일치 -- 충돌 없음.
2. 패치가 새로 읽는 값의 존재 확인(KeyError/NameError 위험 점검): `width`/`height`는 main() 29행에서 argv로 정의, `input_bytes`는 66행에서 정의(record 호출 99행보다 앞), `manifest['pickle']['sha256']`는 worker 32행이 이미 사용 중, `manifest['format']`은 installed.json이 `precompiled_model.py`의 `validate_catalog`(`format == 'comma-run-model'` 강제)를 통과한 catalog dict 전체를 그대로 저장한 것(150~153행)이라 항상 존재한다.
3. 테스트 영향: `tests/test_precompiled_runner.py`의 worker 직접 실행 테스트(`test_worker_reports_real_checksum_failure_before_gpu_access`)는 최소 manifest(`{'pickle': {'sha256'}}`)로 checksum 검증 단계에서 실패하는 경로라 record 호출 지점에 도달하지 않아 영향 없음(코드 읽기로 확인, 실행은 미실시).
4. modeld.py 280행에 `usbgpu_pkl_path.name == 'model.pkl'` + installed.json 존재 조건 분기가 있음을 grep으로 확인했다(precompiled worker 경로용으로 보이나 호출 흐름 전체를 추적하지는 않았고, DH 2015 실주행이 이 경로를 타는지는 미확인).

**패치 적용/정적 검증(샌드박스)**: blobless/sparse clone(`openpilot/selfdrive/modeld`, `openpilot/common`)에서 `git apply --check` 통과 -> 적용 -> 변경 파일 정확히 1개(+3/-1), `python3 -m py_compile` 통과. 결과 blob `d04b52ce89e54698215cce8cf84bab62d5e846f7`가 patch post-image(`d04b52ce89`)와 일치, CR 0/BOM 없음(LF).

**반영 스크립트**: `93cha_item_557e6f6a_carrot_ryu.ps1` -- 파일 전체를 base64로 교체하되, 실행 시 clone한 파일의 blob이 pre-image와 다르면 아무것도 수정하지 않고 중단(이미 post-image면 무동작 종료). 쓴 뒤 post-image blob/`py_compile`/변경 파일 1개/numstat +3/-1을 모두 검증한 뒤에만 commit/push하고, push 후 `git ls-remote`로 원격 HEAD를 대조한다. 9절 체크리스트(BOM, `core.autocrlf=false`, finally 임시폴더 삭제, `Get-PythonCmd`+EOF 공급, WriteAllBytes+BOM 미삽입 확인, 결과 검증) 전 항목을 명령 출력으로 확인했고 payload 역디코드가 검증된 원본과 byte-exact 일치함도 재확인했다. 단 샌드박스에 PowerShell(pwsh)이 없어 스크립트의 PowerShell 구문 실행 자체는 검증하지 못했다(사용자 첫 실행이 최초 실행).

이번 항목도 새 원칙(2026-09-19, 91차 계속)에 따라 코드 스크립트와 이 devnotes 스크립트를 같은 응답에서 함께 전달한다. 실행/push 대기. pytest 미실시(이번 세션 미실행). 실차 검증: 미실시. 다음: 557e6f6a push 확인 -> e324f67 필요 여부 판단(DH 2015가 radar_motion 정지 lead 인계 경로를 실제로 타는지) -> 36개 항목+재적용분 실차 검증.

## 92차 — carrot-ms ec95363a(레인 대시/UI CPU 분리) 상세 대조 완료, 반영 스크립트 준비(실행/push 대기)

세션 시작 체크포인트(`git ls-remote`)로 carrot-ryu `f1e920d`/carrot-ryu-note `521f0eb`가 91차 계속2 기록과 일치함을 확인하고 이어받았다. HANDOFF.md 91차 계속2의 "다음 세션 최우선" 1번(ec95363a 상세 대조)에 착수.

**원본 커밋 조회**: `github.com/happymaj11r/openpilot/commit/ec95363a.patch`로 전체 patch(435줄)를 직접 조회(API rate limit 회피, 지침 0절 권고 방식). 커밋 메시지: "Batch lane dash geometry and separate UI CPU work from render waits" — 레인 대시(점선 차선) 보간/투영을 배치로 묶어 렌더 비용을 줄이고, UI 섹션별 renderTiming에 스레드 CPU 시간을 elapsed/스케줄러 대기와 분리해 기록. carrot-wip 커밋 `137c0331`의 cherry-pick.

**대상 파일 8개 분류**:
- 수정 3개: `openpilot/selfdrive/ui/onroad/augmented_road_view.py`(timing 계측 래핑), `openpilot/selfdrive/ui/onroad/model_renderer.py`(`project_lane_segments` 배치 투영 도입 + `_draw_carrot_overlays`에 timing 계측), `openpilot/selfdrive/ui/road_markings.py`(`lane_dash_segments` interp 배치화 + `project_lane_segments` 신규 함수)
- 신규 1개: `openpilot/selfdrive/ui/render_diagnostics.py`(`RenderDiagnostics` 클래스, `openpilot/common/runtime_diagnostics.py`의 `RuntimeDiagnostics` 사용)
- 테스트 수정 3개: `test_carrot_model_renderer.py`(params.calls 카운트를 `len(params.values)` 기준으로 일반화 — `CarrotTireTrajectory` 등 파라미터 개수 변화에 안전), `test_carrot_model_renderer_lane_visibility.py`(`project_lane_segments` 배치 투영이 기존 `_map_line_to_polygon` 결과와 동일함을 확인하는 테스트 2개 추가), `test_ui_debug_hud_schema.py`(AST 기반 uiDebug 렌더-라인 검사기가 `timing.call(name, target, ...)` 래핑을 인식하도록 `_is_attribute` 대상을 `node.args[1]`로 우회)
- 테스트 신규 1개: `test_render_diagnostics.py`(`RenderDiagnostics.start/call/finish` 단위 테스트)

**충돌/체인 검증**:
1. 기존 파일 6개의 현재 carrot-ryu(`f1e920d`) blob hash를 `raw.githubusercontent.com`(SHA 고정) + `git hash-object`로 직접 계산 -- 전부 patch의 pre-image 인덱스 해시와 정확히 일치(`b3f11ebec0`/`f4b2fb8a79`/`87ea3e9eee`/`8030571e7c`/`102b9986f5`/`fa5bd0cdba`). 신규 파일 2개는 HTTP 404로 아직 없음을 확인 -- 충돌 없는 순수 신규 생성.
2. 90차(carrot-ms `b4f751f4`, camera pair sync/curve release confirm window/path_geometry extraction)가 `model_renderer.py`를 이미 건드렸음을 그 원본 patch(`.diff` 파일 목록)로 확인했으나, 시간순으로 `b4f751f4`가 `ec95363a`보다 앞서고 현재 carrot-ryu의 `model_renderer.py` blob이 `ec95363a`의 pre-image와 정확히 일치하므로 체인 순서 충돌이 없음을 실증(1번 검증과 동일 결과가 이를 이미 증명함). `4d1a3ded`(91차 계속2)는 `carrot_modeld.py`/`upstream_baseline/modeld.py.baseline` 2개만 건드려 겹치지 않음.
3. `render_diagnostics.py`가 임포트하는 `openpilot.common.runtime_diagnostics.RuntimeDiagnostics`가 이미 저장소에 존재하고(`record(context=None, **values)` 시그니처), `RenderDiagnostics.finish()`가 호출하는 `runtime.record(work_ms=..., thread_cpu_ms=..., **self.values)` 형태와 호환됨을 소스로 직접 확인.

**패치 적용/정적 검증(샌드박스)**: `git clone --filter=blob:none --no-checkout --depth 1 --branch carrot-ryu`(sparse-checkout으로 `openpilot/selfdrive/ui`, `openpilot/common`만) 후 `git apply --check` -> 0회 에러(exit 0), `git apply`로 실제 적용해 정확히 8개 파일(수정 6 + 신규 2)만 변경됨을 `git status --short`로 확인. 8개 파일 전부 `python3 -m py_compile` 통과. hud_renderer.py 계열의 옛 스크린샷 API(`consume_pending_screenshot_capture`/`capture_onroad_screenshot`)가 patch 적용 후 `augmented_road_view.py`에 잔여 참조 0건임을 grep으로 재확인 -- 52~54차 render-texture 재설계(54차, 87차 재적용)로 이미 제거된 상태와 이번 패치가 서로 어긋나지 않음. pytest 실제 실행은 샌드박스에 `openpilot.common.params_pyx`(컴파일된 cython 확장) 등 빌드 의존성이 없어 conftest 로드 단계에서 막혀 미실시 -- 11절 원칙대로 "실행했다"고 보고하지 않고 미실시로 명시. 과거 세션들이 이 프로젝트의 pytest 스위트를 실제로 통과시킬 때는 Windows PC(node/npm 계열) 또는 별도 준비된 Linux sandbox(tinygrad_repo 등 포함)를 썼던 것과 동일한 환경 제약.

**반영 스크립트**: 위 검증을 그대로 반영해 8개 파일을 base64 전체교체(패치 적용 후 결과 파일 그대로, anchor 매칭 방식이 아니므로 CRLF/BOM 등 63차·85차류 재발 위험 자체가 없음)하는 `92cha_item_ec95363a_carrot_ryu.ps1` 작성. 9절 "전달 전 필수 자가검증 체크리스트" 전항목 확인: 스크립트 자체 UTF-8 BOM 포함(한글 주석 포함), `git clone`에 `--config core.autocrlf=false`, `finally` 블록에 임시폴더 `Remove-Item -Recurse -Force`(수동 삭제 요청 없음), `Get-PythonCmd`가 `py -3` -> `python3` -> `python` 순으로 실제 `--version` 확인 + 표준입력 EOF 공급(`"" | & ...`) 후 `py_compile` 검증, 대상 파일 쓰기 직후 첫 3바이트 BOM 아님 확인(`WriteAllBytes`로 원본 바이트 그대로 기록하므로 BOM 삽입 자체가 구조적으로 불가능). base64 페이로드를 Python으로 역디코드해 원본 8개 파일과 byte-exact 일치함을 재확인(핵심 발견 42 원칙, anchor가 아니라 전체교체이므로 "결과 재확인"이 곧 이 라운드트립 검증임).

실행/push 대기. 실차 검증: 미실시.

## 91차 계속2 — carrot-ms 4d1a3ded 반영 완료 확인(carrot-ryu `f1e920d`), check_contracts.py modeld-mirror PASS 재확인

사용자가 `91cha2_4d1a3ded_carrot_ryu.ps1` 실행 로그를 전달했다. clone 단계에서 화면이 멈춘 것처럼 보였던 것은 `--quiet` 옵션 때문에 진행률 표시가 안 나온 것으로 안내했고, 이후 사용자가 완료 로그(`260565f..f1e920d`, 로컬/원격 HEAD 일치)를 전달해 `git ls-remote`와 별도 clone(`git clone --filter=blob:none --no-checkout`)으로 16절 재검증을 수행했다.

확인 결과:
1. `git ls-remote`: carrot-ryu HEAD `f1e920d5c391d3ce44f647f29913a8b996a1a7c2`, carrot-ryu-note HEAD `34c5c9bb13af6e64edc793aaf0462f47e48d0cb0` (사용자 로그와 일치).
2. `f1e920d`의 부모는 `260565f` 그대로, 커밋 메시지는 스크립트에 지정한 그대로, 변경 파일 정확히 2개(carrot/model_selector/carrot_modeld.py, carrot/model_selector/upstream_baseline/modeld.py.baseline, +11/-80).
3. 두 파일의 결과 blob(`9a5a62c678b5f4ce5fef789e28e2a6ec3c870da1`, `2ebe83365471da975dfb005b986ead5b7baa0dad`)이 carrot-ms `4d1a3ded`의 post-image blob과 byte 단위 일치.
4. `check_contracts.py`를 새 HEAD(`f1e920d`)에 대해 재실행: `modeld-mirror`가 예상대로 PASS로 전환됨(반영 전 260565f에서는 FAIL). 나머지 FAIL 4건(script-paths/tinygrad-pickle-compat/compile-env-guards/wiring)은 샌드박스에 tinygrad_repo가 없는 환경 한계로, 반영 전후 동일해 무관함을 재확인.

이로써 89차 검토대상 4건 중 두 번째(`4d1a3ded`)가 반영 완료로 확정됐다. WIP_SYNC.md/CURRENT_STATUS.md/HANDOFF.md의 해당 표기를 정정하고, 남은 두 건(`ec95363a` -> `557e6f6a`, 커밋 발생 순서) 및 `e324f67` 분류 이월 항목으로 다음 세션을 이어간다. 이번 항목은 devnotes만 갱신하며 코드 변경은 없다.

실차 검증: 미실시(이번 항목은 GitHub 재확인과 샌드박스 계약 점검뿐).

## 91차 계속 — carrot-ms 4d1a3ded 반영 준비(model selector 미러 carrot_modeld.py + upstream_baseline), WIP_SYNC.md 널바이트 정정

사용자가 91차 devnotes 반영 스크립트 실행을 알려와 GitHub에서 재확인했다(4절/16절): carrot-ryu-note HEAD `b55388c`(부모 `b7013c6`, 변경 파일 4개), SHA 고정 raw 조회로 HANDOFF.md가 91차로 시작하고 WIP.md 최상단이 91차임을, WIP_SYNC.md가 CRLF 163줄/LF 혼입 0/91차 체크포인트 포함임을 확인했다. carrot-ryu는 `260565f` 그대로. 이 시점부터 새 원칙(사용자 지시, 2026-09-19): 코드 변경 시 devnotes 기록도 같은 세션에서 동시에 진행한다. 이번 항목부터 코드 반영 스크립트와 devnotes 스크립트를 같은 응답에서 함께 전달한다.

남은 3건의 처리 순서는 사용자가 Claude 판단에 위임했다("너가 합리적이라 생각하는것부터"). 커밋 발생 순서상 다음이자 90차 반영의 직접 후속인 4d1a3ded(model selector 미러를 공유 camera_sync에 맞춤)를 먼저 골랐다. 근거:
1. `carrot/model_selector/check_contracts.py`(표준 라이브러리만 사용)의 `modeld-mirror` 계약이 carrot-ryu 260565f에서 FAIL이다("마지막 미러 리뷰 이후 변경됨: modeld.py"). 90차가 modeld.py를 바꿨는데 upstream_baseline/modeld.py.baseline 스냅샷과 carrot_modeld.py 미러는 그대로이기 때문이다. 샌드박스에서 세 상태를 비교했다: carrot-ms b4f751f4(4d1a3ded 직전) FAIL, carrot-ms 4d1a3ded PASS, carrot-ryu 260565f FAIL. 나머지 FAIL 4건(script-paths/tinygrad-pickle-compat/compile-env-guards/wiring)은 샌드박스에 tinygrad_repo가 없어서이며 세 상태에서 동일하므로 무관하다.
2. 대상 두 파일(carrot/model_selector/carrot_modeld.py, carrot/model_selector/upstream_baseline/modeld.py.baseline)의 4d1a3ded 직전 blob이 carrot-ryu 260565f의 blob과 동일(각각 `1d9eb7ecc5409f7eca1bed94d8911fd13615325e`, `59ea2ab20b420acc54875cde6914600f2d07f882`)해서 충돌 없이 적용 가능하다.

4d1a3ded 내용(carrot-ms 커밋 메시지 기준): 미러의 자체 FrameMeta와 고정 25 ms 수신 루프를 제거하고 공유 `camera_sync.receive_camera_pair()`를 호출하도록 바꾼다(변경 파일 2개, +11/-80). 커밋이 의도적으로 포팅하지 않은 부분(precompiled_runner의 fused backend publish, dropped-frame 로그 문구 "advancing model history")은 미러에 적용되지 않고 미러의 기존 로그 문구가 유지된다. carrot_modeld.py 쪽 변경은 미러 경로에만 영향을 주며 modeld 본체는 90차에서 이미 같은 변경이 반영돼 있다. DH 2015에서 모델 셀렉터 미러 경로가 실제로 쓰이는지는 확인하지 못했다.

반영 방식: 9절 Replace-Block(carrot_modeld.py 3블록, modeld.py.baseline 4블록). 블록을 4d1a3ded 직전 blob에 순차 적용한 결과가 4d1a3ded의 blob(`9a5a62c678b5f4ce5fef789e28e2a6ec3c870da1` / `2ebe83365471da975dfb005b986ead5b7baa0dad`)과 byte 단위로 일치함을 사전에 확인했다. 반영 스크립트는 실행 시점에도 시작 blob 일치, 블록 1회 매치, 결과 blob 일치, py_compile 순으로 검증하고 하나라도 어긋나면 push 전에 중단한다. 스크립트: `91cha2_4d1a3ded_carrot_ryu.ps1`(carrot-ryu, 사용자 실행 대기), `91cha2_devnotes_carrot_ryu_note.ps1`(carrot-ryu-note, 이 기록).

부수: WIP_SYNC.md의 널바이트 1개를 정정했다(널바이트 + `2015190f58a4380a433ee0130e6374455dddc2e` -> `02015190f58a4380a433ee0130e6374455dddc2e`). 같은 해시가 이 파일의 다른 두 곳(6~7차 체크포인트의 carrot-ryu HEAD/carrot-ms HEAD 줄)에 앞자리 0를 포함한 정상 표기로 있는 것과 앞 회차의 WIP.md 정정 사례(87차)를 근거로 했다. 91차 체크포인트가 이 항목을 116행이라고 적은 것은 91차 체크포인트 13줄이 삽입되기 전 줄 번호다(삽입 후 129행).

실차 검증: 미실시(이번 코드 반영분은 반영 스크립트 실행/push 전이며, 그 후에도 36개 항목 및 b4f751f4/4d1a3ded 재적용분 전부 미실시). 상세: WIP_SYNC.md 91차 계속 체크포인트, HANDOFF.md 참고.

## 91차 — 90차 코드 push(carrot-ms b4f751f4 재적용, `260565f`) devnotes 사후 동기화 + 패치 대조/정적 검증, carrot-ms 신규 1건(e324f67) 발견

세션 시작 체크포인트(4절 0단계, `git ls-remote`)로 carrot-ryu-note `b7013c6`(89차 devnotes), carrot-ryu `260565f187a2d934f0e27464457eee63c8ec233a`를 확인했다. HANDOFF.md(89차)는 코드 브랜치를 `0923f83`(변경 없음)으로 기록하고 있어 두 브랜치가 서로 다른 시점을 가리키고 있었다(16절). 조회 결과 `260565f`는 부모가 `0923f83`인 커밋 1개("90cha: reapply carrot-ms b4f751f4 - camera pair sync, curve release confirm window, path_geometry extraction", 2026-09-19 13:06 +0900, 작성자 RYU)였고, WIP.md/HANDOFF.md/CURRENT_STATUS.md/WIP_SYNC.md 어디에도 "90차" 기록이 없었다. 90차 세션이 코드 push까지만 마치고 devnotes 반영 전에 끊긴 것으로 보인다(핵심 발견 27/38과 동일 패턴). 90차 세션 자체의 진행 경위(승인 대화, 당시 실행한 검증)는 devnotes에 남아 있지 않아 확인하지 못했다. 아래는 이번 세션이 GitHub 상태를 독립적으로 재검증한 내용이다. 사용자 승인('진행')을 받은 범위는 이 검증과 devnotes 사후 동기화까지이며, 남은 3건의 코드 반영은 승인 범위 밖이라 착수하지 않았다.

검증 (모두 정적/샌드박스 검증이며 실차 검증이 아니다):
1. 패치 대조: carrot-ms의 b4f751f4(happymaj11r/openpilot, `git clone --filter=blob:none`)와 carrot-ryu의 260565f를 각각 `git show`로 패치로 뽑아 index 줄을 제외하고 diff했다. 15개 파일(+307/-152) 660줄이 전부 동일하고, 차이는 carrot_man.py 헝크 헤더의 시작 줄번호 한 줄(carrot-ms 1457 / carrot-ryu 1481)뿐이다. 이는 carrot-ryu 파일에서 해당 위치가 24줄 뒤에 있다는 뜻일 뿐 변경 내용 자체는 동일하다.
2. py_compile: 변경된 .py 11개 전부 통과.
3. 단위 테스트(260565f 체크아웃, `pytest --noconftest -o addopts=""`, 샌드박스 python3.12): test_camera_sync 5 / test_path_geometry 8 / test_curve_speed 22 / test_precompiled_runner 12, 총 47개 전부 통과. 처음에는 sparse checkout에 openpilot/common이 빠져 test_precompiled_runner가 ModuleNotFoundError로 실패했으나, carrot-ms b4f751f4 원본에서도 동일하게 실패했고 openpilot/common을 추가하자 통과했다 -- 재적용 결함이 아니라 샌드박스 구성 문제였다.

결과: 89차 검토대상 4건 중 b4f751f4는 반영 완료(carrot-ryu `260565f`)로 확인했다. 나머지 3건(4d1a3ded / ec95363a / 557e6f6a)은 미반영이며 반영 승인 기록도 없다(18절 -- 승인 전 착수 금지).

부수 발견 2건:
(1) carrot-ms(happymaj11r/openpilot) HEAD가 89차 체크포인트(`f19d404a`)보다 1건 앞선 `e324f6735d3606800045ed6b28f41e79b17e5498`("Require clear persistent vision for distinct stopped-lead handoff", ajouatom, 2026-09-19 08:22 +0900)로 갱신돼 있다. 분류/반영 판단은 이월하며 상세는 WIP_SYNC.md 91차 체크포인트 참고.
(2) WIP_SYNC.md 116행(57차 항목 본문의 fork point 해시 자리)에 널바이트(\x00) 1개가 남아 있다. 87차가 WIP.md에서 정정한 것과 같은 유형으로 보이며 정상 표기는 `02015190f58a4380a433ee0130e6374455dddc2e`(40자리, 앞자리 0가 누락된 상태)다. 이번 세션 범위 밖이라 정정하지 않았고 사용자 결정을 기다린다.

실차 검증: 미실시(코드 변경 없음. 36개 항목 및 90차 b4f751f4 재적용분 전부 미실시). 상세: WIP_SYNC.md 91차 체크포인트, HANDOFF.md 91차 참고.
## 89차 — carrot-ms 신규 15건 전수 분석 (2절 동기화), 반영은 다음 세션 이월

88차에서 처음 발견된 carrot-ms 신규 13건(706efb47 대비)을 이어받아 전수 분석했다. 그 사이 carrot-ms가 다시 갱신되어 총 15건(추가 2건: 8e85a02 CCNC leadOne, f19d404a Hyundai CAN FD nearest lead)으로 늘어난 상태를 확인했다. api.github.com rate limit 소진으로 `git clone --filter=blob:none` partial clone으로 전환해 15건 전부의 diff를 직접 대조했다.

우리 차량(HYUNDAI_GENESIS, 제네시스 DH 2015-16)의 values.py 플래그(`CHECKSUM_6B | LEGACY`, CAN FD·RADAR_GROUP3 모두 아님)를 근거로 CAN FD 전용 7건(0beb200a/de6ee634/a6c8220/34cf65fb/5ae4a25/8e85a02/f19d404a)과 Radar Group3 전용 1건(ee8d4353)을 제외 확정했다. CI/문서/테스트픽스처뿐인 3건(845e725b/21b71f00/994683d5)도 제외.

남은 4건(b4f751f4 카메라 프레임 페어링+커브 리팩터, 4d1a3ded 모델셀렉터 미러 동기화, ec95363a UI 레인대시 배치, 557e6f6a 진단로그)은 대상 함수가 carrot-ryu에서 fork 이후 무수정임을 diff로 확인해 충돌위험이 낮다고 판단했으나, 사용자 요청으로 이번 세션은 코드 반영 없이 WIP_SYNC.md 체크포인트 기록까지만 진행했다. 실제 반영은 다음 세션에서 별도 승인 후 착수.

실차 검증: 미실시(이번 세션은 GitHub 조회/분석만, 코드 변경 없음). 상세: WIP_SYNC.md 2026-09-19(89차) 체크포인트 참고.
## 88차 — 87차 반영 스크립트 2개 push 확인 (devnotes 정정만, 코드 변경 없음) + carrot-ms 신규 13건 발견

세션 시작 체크포인트(4절 0단계, `git ls-remote`)로 carrot-ryu-note가 `50e7f67`(87차 devnotes 갱신)임을 확인. 이어서 carrot-ryu HEAD를 조회한 결과 `0923f8396dacbb61a23e1c394751d8014ddddf5f`로, HANDOFF.md(87차)에 "실행/push 대기"로 기록돼 있던 항목 30~36 반영 스크립트(`87cha_items30_36_carrot_ryu.ps1`)가 이미 사용자에 의해 실행/push까지 완료돼 있음을 16절에 따라 발견했다(핵심 발견 27/38과 동일 패턴). GitHub commit API로 `0923f83`의 부모가 `ba929b5f2`(86차 베이스)와 정확히 일치하고, 변경 파일 4개(hud_renderer.py/screenshot_button.py/screenshot_capture.py/application.py)가 87차 HANDOFF에 기록된 내용과 동일함을 재확인했다. devnotes 반영 스크립트(`87cha_devnotes_carrot_ryu_note.ps1`)도 이미 실행되어 `50e7f67`(부모 `15cdf6e2e`, 87차 베이스와 일치)로 push 완료돼 있었다.

**36개 항목(1~36) 전부가 20절 리셋 이후 새 베이스 위에서 GitHub 반영 확인 완료된 상태다.** 이번 세션은 코드 변경 없이 CURRENT_STATUS.md(최상단 HEAD 줄 + 항목 30~36 일곱 곳)와 HANDOFF.md, 이 WIP.md 표기만 88차 기준으로 정정한다.

부수적으로 carrot-ms(happymaj11r/openpilot) 동기화 상태도 점검했다: WIP_SYNC.md에 마지막 검토 완료로 기록된 지점(`706efb47`, 87차까지 "변경 없음"으로 유지)보다 carrot-ms 현재 HEAD(`994683d5`)가 GitHub compare API 기준 13개 커밋 앞서 있음을 확인했다. 신규 13건: `845e725`(fix tests) / `0beb200`(CAN FD stop request re-entry 실험) / `de6ee63`(CAN FD stopping merge resolution 복원) / `a6c8220`(CAN FD stop retry를 기본 off 설정 뒤로) / `21b71f0`(Cinque v3 실험 범위 기록) / `34cf65f`(CAN FD stop retry 설정 변경을 주행 중 적용) / `ee8d435`(Hyundai Group 3 레이더 객체 identity, CAN 슬롯 이동 대응) / `b4f751f`(카메라 cadence/커브 진입 복구/UI path cost) / `4d1a3ad`(model selector mirror를 공유 카메라 페어링에 적응) / `5ae4a25`(CAN FD 카메라 SCC HUD 객체에 leadOne 사용) / `ec95363`(lane dash geometry 배치 + UI CPU 작업 분리) / `557e6f6`(worker 진단에 모델 아티팩트/입력 크기 식별) / `994683d`(EV9 정지 상태 코너 phantom braking 회귀 대응). 이 중 CAN FD stop retry/stopping 4건(`0beb200`/`de6ee63`/`a6c8220`/`34cf65f`)과 Hyundai Group 3 레이더 1건(`ee8d435`)은 현대차 그룹 CAN 계열이라 제네시스 DH 2015와 관련성 후보로 보이고, model selector mirror 조정 1건(`4d1a3ad`)도 2절 동기화 대상 후보다. 나머지(카메라 cadence, lane dash, worker 진단, EV9 phantom braking, 테스트/실험 범위 기록 등)는 관련성 낮아 보이나 개별 diff 미확인. **이 13건의 개별 diff 분석/반영 판단/WIP_SYNC.md 체크포인트 기록은 이번 세션에서 진행하지 않았고 다음 세션 과제로 이월한다.**

실차 검증: 미실시(코드 변경 자체가 없음). 상세: HANDOFF.md 88차 참고.

## 87차 — 항목 30~36(스크린샷 캡처 체인 7건) 재적용 + WIP.md null byte 손상 발견/수정

세션 시작 체크포인트(`git ls-remote`)로 carrot-ryu(`ba929b5`)/carrot-ryu-note(`15cdf6e`)가 86차 상태 그대로임을
확인(4절/16절) -- 86차 이후 추가 push 없음. 이어서 남은 마지막 항목인 30~36(스크린샷 캡처 체인: DPI 스케일
버그 → 진단로그+버튼위치 → PNG 롤백 → 480p 다운스케일+캡처타이밍 → 캡처위치 재조정(border HUD) →
render-texture 재설계 → 상하반전, 47~56차 순서)을 새 베이스(`ba929b5`) 위에 착수했다.

carrot-ryu-v1(`9ccf1206`) 아카이브에서 이 체인의 최종 결과물(56차 시점 최종본)인
`screenshot_capture.py`/`screenshot_button.py`/`hud_renderer.py`/`system/ui/lib/application.py` 4개 파일을
가져와 현재 베이스와 대조했다. `screenshot_capture.py`/`screenshot_button.py`는 다른 세션이 그 사이 건드리지
않아 전체교체로 안전하게 적용 가능함을 확인. `hud_renderer.py`는 84차에서 추가된 sdi_descr 배지 위치 보정
(핵심 발견 40)이 v1 아카이브에는 없는 이후 변경이라, 전체교체 대신 49차 버튼위치 이동 부분만 Replace-Block
2곳으로 좁혀 적용해 84차 수정을 보존했다. `application.py`는 이 저장소에 처음 반영되는 파일(신규 추가,
54차 request_temp_capture() 렌더텍스처 재사용 방식)이라 v1과 완전히 동일하게 전체교체. `augmented_road_view.py`는
51·52차가 추가했던 캡처 호출부가 54차 재설계로 이미 다시 원복돼 있어(v1 기준) 이번 재적용에서 변경 없음(diff 0).

4개 파일 전부 독립 `git clone`에 적용 → `py_compile` 4개 전부 통과, `application.py`는 v1 아카이브와
byte-exact 일치(`diff` 무출력) 확인, 잔여 참조 점검(`capture_onroad_screenshot`/`consume_pending_screenshot_capture`
호출부 0건, `gui_app` 싱글턴 import 경로 확인)까지 완료(9절/16절). js/css 소스 변경 없어 번들 재생성/
`params_keys.h` 등록 불필요. 반영 스크립트(`87cha_items30_36_carrot_ryu.ps1`, base64 전체교체 4개 파일 +
`Get-PythonCmd` 자동탐지 + EOF 공급 + `core.autocrlf=false` + 임시폴더 자동삭제)를 9절 "전달 전 필수
자가검증 체크리스트" 전항목(비ASCII 0건/`core.autocrlf`/cleanup/`Get-PythonCmd`+EOF공급) 통과 후, 완전히
독립된 두 번째 clone에 페이로드를 재적용해 `py_compile` 재통과 + diff stat(4 files, +138/-20)이 최초
검증과 동일함을 재확인했다(핵심 발견 42 원칙 적용 -- 결과 자체를 다시 확인).

이 작업과 별개로, devnotes 갱신을 준비하며 `WIP.md`를 raw로 재조회하는 과정에서 실제 null byte(`\x00`) 손상
1건을 처음으로 발견했다: 57차 항목 본문 중 "carrot-ryu fork point(`\x00`2015190f5, ...)" 자리에 있어야 할
숫자 `0`이 널바이트로 바뀌어 있었다(같은 해시가 파일 다른 곳(606번째 줄 등)에는 `02015190f5`로 정상
표기돼 있어 원본 문자를 확정할 수 있었다). 정확한 손상 경위는 미확정이나(과거 세션의 문자열 치환/이스케이프
처리 과정에서 발생한 것으로 추정, 핵심 발견 41·42와 유사하게 "체크리스트 통과 기록과 실제 결과물이
달랐던" 사례로 보임), 이번 세션에서 바이트 단위로 위치를 특정해 `0`으로 복원했다(그 외 이 파일에 다른
null byte는 없음을 전수 확인). 기존에 알려져 있던 "`# WIP` 헤더 중복"(789번째 줄) 이슈는 지침 문서
"다음 작업" 목록에 "낮은 우선순위"로 이미 기록돼 있어 이번 세션에서는 손대지 않았다(임의 축소/삭제
금지 원칙, 7절).

**[9절 예외 사항 명시]** WIP.md는 원래 "이어붙이기형"(최상단 anchor 삽입만) 원칙 대상이지만, 이번엔 파일
중간의 null byte 손상을 같은 커밋에서 함께 고쳐야 해서 이번 회차에 한해 파일 전체를 base64로 담아
전체교체 방식으로 반영한다(9절의 "이번만 예외" 명시 원칙, 85차가 CURRENT_STATUS.md에 적용했던 것과 반대
방향의 동일 원칙 적용). 다음 회차부터는 다시 기존 방식(최상단 anchor 삽입)으로 돌아간다.

실행/push 대기(코드/devnotes 모두). 실차 검증: 미실시(항목 30~36 모두 이 프로젝트 역사상 새 베이스
위에서는 처음 재적용되는 경로).

## 86차 — 항목22/23/26 push 확인(c74c0ac) + 항목24(41차) 재적용(v1 실패 -> v2로 교체)

세션 시작 체크포인트(`git ls-remote`)로 carrot-ryu HEAD가 `132d85b`가 아니라 이미 `c74c0ac`로 바뀌어
있음을 확인 -- HANDOFF.md(85차 계속3)에는 v2 스크립트가 여전히 "실행/push 대기"로 남아있던 괴리(16절/
핵심 발견 27·38과 동일 패턴)를 발견했다. `132d85b`..`c74c0ac` GitHub compare `.diff`로 정확히 12개
파일(routes.py/screenshots.js/hud_renderer.py/생성번들 3종/index.html/en·ko·zh.js/runtime.js/style.css)이
변경돼 있고 screenshots.js에 `formatRelativeEpoch`/`formatLogBytes` import가 실제로 존재함을 확인해,
사용자가 이미 `85cha_item22_23_26_carrot_ryu_v2.ps1`을 실행해 push까지 완료했음을 확정했다(항목
22/23/26 이식 완료).

이어서 사용자 요청으로 항목 24(41차, commit `da6ad815`, carrotweb 로그탭 새로고침 아이콘)에 착수. 원본
커밋 patch(index.html/runtime.js/style.css/생성번들 3종, 6개 파일)를 조회하고, 현재 베이스(`c74c0ac`)의
세 소스 파일에 대해 anchor를 직접 대조(`bindLogsMenu`/`formatRelativeEpoch`/`bindLogsPage`/`.logs-menu`
등 주변 컨텍스트가 원본 41차 시점과 완전히 동일함을 확인) -> 독립 `git clone`에 Replace-Block 3곳
(index.html 1곳, runtime.js 2곳, style.css 2곳, 총 5개 치환) 적용, 전부 1회 매치 확인. `npm install &&
node build.mjs`로 생성 번들 3종 재생성 -> 변경 파일 6개·라인 증감(index.html +8, runtime.js +32,
style.css +30, logs.css/asset-manifest.json/logs.js)이 원본 41차 커밋과 정확히 일치함을 `git diff
--stat`으로 확인. `node --check`(runtime.js, 생성 logs.js) 통과, `node --test` 746/747 통과(유일 실패는
무관한 기존 `ar_projection_golden` 환경 이슈). 반영 스크립트(`86cha_item24_logs_refresh_carrot_ryu.ps1`)
전달, 실행/push 대기.

**[v1 실행 결과 -> v2로 교체]** 사용자가 v1을 실행한 결과 `[3/6] node --check` 단계에서 `node`가 이
PC에서 인식되지 않음을 확인(`node --version`, `where.exe node` 모두 실패 -- git commit/push 이전이라
반영 사고 없음, 15절/18절 안전장치 정상 동작). 45차~85차까지는 반영 스크립트가 사용자 PC에서
`npm install && node build.mjs`를 직접 실행하는 방식을 문제없이 써왔으나(overview.md에도 "Node.js는
로컬에 설치 확인됨"으로 기록돼 있었음), 이 세션에서 처음으로 그 전제가 깨진 것을 실증했다. 67차 등
과거 세션에서 쓰던 방식(소스 수정 + 번들 재생성 전체를 Claude 샌드박스에서 실행한 뒤 결과물을 base64로
담아 전달)으로 전환해, index.html/runtime.js/style.css Replace-Block 5곳 + `npm install && node
build.mjs`를 Claude 샌드박스(Linux)에서 실행/검증(anchor 전부 1회 매치, 변경 파일 6개, `node --check`/
`node --test` 746/747 통과 -- v1과 동일한 검증 결과)하고, 최종 결과 파일 6개를 base64 전체교체로 담은
`86cha_item24_logs_refresh_carrot_ryu_v2.ps1`로 교체했다. v2는 이 PC에서 node/npm을 전혀 실행하지
않는다. 페이로드를 완전히 독립된 두 번째 clone(`c74c0ac` 기준 fresh clone)에 적용해 6개 파일 전부
샌드박스 빌드 결과와 byte-exact 일치함을 재확인했다(9절/16절, 핵심 발견 42 원칙 -- anchor 매치뿐
아니라 치환 결과 자체를 재확인). **v1(`86cha_item24_logs_refresh_carrot_ryu.ps1`)은 이 PC에서 실행해도
같은 이유로 다시 막힐 뿐이니 실행하지 말 것 -- v2만 실행.** 실행/push 대기. 실차 검증: 미실시(이 코드
경로는 41차 이후 61차 리셋으로 한 번 사라졌다가 이번에 처음 재적용되는 것이라, push 확인 후 처음부터
재검증 필요).
## 85차 (+계속3) — 항목22(39차)+23(40차-fix)+26(44차) 재검증, v1 CRLF 실패 -> 핵심 발견 44 -> v2로 수정, 이번 세션에서 독립 재확인

세션 시작 체크포인트(`git ls-remote`)로 carrot-ryu HEAD가 이미 `132d85b`(84차2 BOM 제거 커밋)로 push
완료돼 있음을 확인했다. 사용자 요청으로 항목 22(39차, `797fca2e`, 화면녹화 탭 사진 업로드 UI +
content_shift_y)·항목 23(40차-fix, `bdde8326`, screenshots.js formatRelativeEpoch import 누락)·항목
26(44차 일부, `e2f35619`, screenshots.js formatLogBytes import 누락)을 현재 베이스(`132d85b`) 위에서
처음부터 재검증했다: 원본 커밋 patch 3개 직접 조회 -> 12개 파일 중 11개는 `git apply` 1회 매치, `routes.py`
1개는 파일 끝 컨텍스트 차이로 Replace-Block 수동 삽입 -> `npm install && node build.mjs`로 생성 번들 3종
재생성 -> `py_compile`/`node --check`/`npm test`(746/747, 유일 실패는 무관한 기존 `ar_projection_golden`
환경 이슈) 통과. 반영 스크립트 `85cha_item22_23_26_carrot_ryu.ps1`(v1) 작성/전달.

**[사용자 실행 결과]** 사용자가 v1을 실행한 결과 첫 Replace-Block(`content_shift_y-decl`)에서
`Anchor match count != 1: got 0`으로 안전하게 중단됨(commit/push 이전, 15절/18절 안전장치 정상 동작).
원인 규명: `.gitattributes`에 여전히 `* text=auto`가 있어(63차에서 이미 규명된 조건) Windows Git
환경에서 `core.autocrlf=false`를 clone 시 줘도 체크아웃 시 CRLF로 변환될 수 있는데, 이번
`Invoke-ReplaceBlock` 함수에는 9절이 이미 요구하던 "매칭 전 CRLF->LF 정규화"가 실제 코드에는 빠져
있었음을 확인(핵심 발견 44 -- "9절 체크리스트 통과"라는 서술만 믿지 말고 코드 자체를 직접 대조해야
한다는 교훈). `Invoke-ReplaceBlock`에 CRLF->LF 정규화를 추가한 `85cha_item22_23_26_carrot_ryu_v2.ps1`로
교체.

**[85차 계속3, 새 세션에서 독립 재확인]** 새 세션 시작 체크포인트에서 carrot-ryu/carrot-ryu-note가 여전히
`132d85b`/`fa038e0`임을 재확인 -- 위 작업 전체가 아직 GitHub에 반영되지 않은 채팅 사본이었음을 인지하고
(3절), 그 기록을 그대로 믿지 않고 신선한 별도 clone에서 v2 스크립트 로직을 처음부터 다시
재시뮬레이션(Python)했다: base64 전체교체 7개 파일 + CRLF 정규화 Replace-Block 12개 앵커 전부 1회 매치,
`py_compile`(routes.py/hud_renderer.py)·`node --check`(screenshots.js/runtime.js/en·ko·zh.js/생성번들
logs.js) 전부 통과, `content_shift_y`/`screenshotsToolbarWrap` 치환 결과도 재확인. 이어서 9절 "전달 전
필수 자가검증 체크리스트" 6항목을 `.ps1` 파일을 직접 `grep`으로 대조해 전부 확인(BOM 있음/
`core.autocrlf=false`/`finally` 임시폴더 삭제/`Get-PythonCmd`+EOF 선공급/`WriteAllText` 무BOM/쓰기 후
BOM 검사 루프). 결론: v2 스크립트는 수정 없이 그대로 사용 가능. devnotes 반영 스크립트
(`85cha_devnotes_carrot_ryu_note.ps1`)를 이 세션에서 새로 작성해 코드 스크립트(v2)와 함께 전달.

실행 순서: (1) `85cha_item22_23_26_carrot_ryu_v2.ps1`(carrot-ryu) 먼저 실행, (2)
`85cha_devnotes_carrot_ryu_note.ps1`(carrot-ryu-note) 실행. v1(`85cha_item22_23_26_carrot_ryu.ps1`)은
실행하지 말 것.

실차 검증: 미실시(항목 22/23/26 코드 변경 자체가 아직 push되지 않음, 이 프로젝트 역사상 이 경로들은 한
번도 실차 확인된 적 없음). push 확인되면 다음 세션 최우선으로 실차 검증 진행.

## 84차 계속2 (코드/devnotes push 완료 후 보정 대기) -- Set-Content -Encoding UTF8의 BOM 강제삽입 + WIP.md "# WIP" 헤더 소실 발견 및 수정

사용자가 84cha_item_sdi_badge_fix_v2.ps1/84cha_devnotes_carrot_ryu_note_v2.ps1를 실행해 carrot-ryu(`a461c7e`)/
carrot-ryu-note(`b174937`)에 각각 push 완료. 9절 체크리스트 승격 작업 착수 전 4절/16절 원칙대로
`git ls-remote`+GitHub raw(SHA고정)로 실제 반영 내용을 재확인하는 과정에서 두 가지 문제를 발견했다.

(1) 네 파일(`hud_renderer.py`/`WIP.md`/`CURRENT_STATUS.md`/`HANDOFF.md`) 전부 파일 맨 앞에 의도치 않은
UTF-8 BOM(`EF BB BF`)이 삽입되어 있었다. 원인: 이 네 파일 모두 스크립트 안에서 `Set-Content -Encoding UTF8`로
전체 재작성됐는데, Windows PowerShell 5.1의 `Set-Content`(`Out-File`도 동일)는 `-Encoding UTF8`을 지정하면
원본에 BOM이 없었어도 항상 새로 BOM을 붙인다. 지침 문서 9절의 기존 문구("Set-Content -Encoding UTF8 또는
BOM 없는 UTF-8을 사용한다")가 이 둘을 사실상 동의어처럼 서술해 놓은 것 자체가 잘못된 전제였음을 확인했다
(핵심 발견 41). `hud_renderer.py`는 Python이 파일 맨 앞 UTF-8 BOM을 자동으로 건너뛰므로 `py_compile`은
정상 통과해 이번에도 걸러지지 않았다.

(2) `WIP.md`는 이번 84차 반영 스크립트의 anchor/치환 로직 자체 버그로 최상단 "# WIP" 제목 줄이 통째로
사라진 채 push됐다(기존에 알려진 "# WIP 헤더 중복" 이슈와는 반대로, 이번엔 "소실"). 원인: 삽입 anchor를
`"# WIP\n\n## 83차"`로 잡고 이를 `[새 84차 항목]\n\n## 83차`로 치환했는데, 새 콘텐츠 쪽에 "# WIP"를
다시 넣지 않았다. anchor가 정확히 1회 매치됐다는 것만 확인하고 치환 *결과* 텍스트를 다시 훑어보지 않아서
발견이 늦었다(핵심 발견 42).

두 문제 모두 이번 보정 스크립트로 즉시 수정(코드: BOM만 제거 / devnotes: BOM 제거 + "# WIP" 헤더 복원),
지침 문서(PROJECT_INSTRUCTIONS_carrot-ryu.md) 9절에 아래 세 가지를 실제로 반영했다(19절 절차, 사용자
승인 완료 -- 직전 세션에서 문구만 준비되고 실제 파일 반영이 누락되어 있었던 것을 이번에 바로잡음):
(a) 대상 파일 전체 재작성은 `[System.IO.File]::WriteAllText($Path, $Content,
(New-Object System.Text.UTF8Encoding($false)))`만 사용하고, 쓴 뒤 대상 파일 첫 3바이트가 BOM이 아닌지
`od`/`Get-Content -Encoding Byte`류로 확인하는 것을 표준 절차로 명문화, (b) anchor 매치 횟수뿐 아니라
치환 *결과* 텍스트(특히 파일 맨 앞/헤더 줄)를 다시 확인하는 절차 추가, (c) 21차/26(39차)·37차에 걸쳐
반복된 BOM(.ps1)/core.autocrlf/임시폴더/Get-PythonCmd 규칙을 "전달 전 필수 자가검증 체크리스트"로
승격(모두 py_compile과 동급의, 실행하고 결과를 응답에 보여줘야 하는 검증 단계). 상세: FINDINGS.md
2026-09-18(84차 계속) 항목, 핵심 발견 41/42.

**검증**: 4개 파일 모두 BOM 제거 후 `od -An -tx1 -N3`로 첫 3바이트가 더 이상 `ef bb bf`가 아님을 확인,
`hud_renderer.py`는 `py_compile` 재통과 확인, `WIP.md`는 파일 맨 앞이 `# WIP`로 시작하는지 재확인.
PROJECT_INSTRUCTIONS_carrot-ryu.md 9절 변경은 Replace-Block anchor 1회 매치 + 치환 결과 재확인(핵심
발견 42 재발 방지 원칙을 이 수정 자체에도 바로 적용).

**실차 검증**: 이번 회차는 devnotes/인코딩 보정만이며 로직 변경 없음 -- 84차 sdi_descr 배지 수정 자체의
실차 검증은 여전히 미실시로 다음 세션 최우선 과제.

## 핵심 발견 43 (84차 계속2, 사용자 실행 중 발견) -- `& $cmd @verArgs 2>&1` 형태의 Python 버전/컴파일 호출이 특정 환경에서 인터랙티브 REPL로 빠져 스크립트를 무한 대기시킬 수 있음

사용자가 `84cha2_hud_renderer_bom_fix.ps1`을 실행하던 중, `Get-PythonCmd`의 `py -3 --version` 호출은
정상적으로 "Python 3.12.10"을 출력했으나, 그 직후 실제 `py_compile` 검증 호출 단계에서 스크립트가
Python 인터랙티브 셸(`>>>`)에 빠져 멈췄다(사용자가 `Ctrl+C`로 중단, `git commit`/`push` 이전이라 반영
사고는 없었음). 정확한 재현 조건은 로컬에서 재현이 불가능해 확정하지 못했으나(11절: 이 부분은 추정),
Windows PowerShell에서 배열 스플래팅(`@CompileArgs`)으로 외부 `.exe`를 호출할 때 인자 조합이 특정
조건에서 예상과 다르게 전달되어, `py` 런처가 버전 선택자만 받고 실행할 스크립트/모듈 인자를 못 받으면
인터랙티브 REPL로 빠지는 것으로 추정된다.

**재발 방지**: 이 인터랙티브 진입 가능성 자체를 구조적으로 차단하기 위해, Python을 외부 프로세스로
호출하는 모든 지점(버전 확인 + `py_compile` 실행 모두)에서 표준입력에 빈 문자열을 미리 파이프해
EOF를 즉시 공급한다: `"" | & $Cmd @Args 2>&1`. 이렇게 하면 설령 인자 전달이 잘못돼 REPL로 빠지더라도
즉시 EOF를 받아 종료되므로 스크립트가 무한 대기하지 않는다(단, 이 경우 `py_compile`이 실제로 실행되지
않았을 수 있으므로, 종료 코드와 함께 출력 내용도 항상 응답에 남겨 "그냥 통과"로 오판하지 않도록 함).
9절 체크리스트 항목 4("Get-PythonCmd 자동탐지 패턴 사용")에 "표준입력 EOF 선공급"을 추가 조건으로
반영. `84cha2_hud_renderer_bom_fix_v2.ps1`로 하드닝된 버전을 재전달.

## 84차 (코드 push 대기) — 신호과속/교통정보 배지 위치·글자크기 수정 + 40차 검증 범위 오류 발견

사용자가 실기기 스크린샷(2026-09-17)으로 우측하단 경로안내 박스의 "교통정보 수집지점"(sdi_descr)
문구가 그 위 초록 배지 밖으로 밀려 보이는 버그를 제보. 사용자가 "carrot-ryu-v1 브랜치에서 고치자"고
표현했으나, v1은 20절/18절에 따라 수정 불가한 아카이브라 carrot-ryu(작업 브랜치)에 반영하는 것으로
합의.

조사 결과 (1) 이 sdi_descr 분기는 프로젝트 전체 역사상 실차로 제대로 검증된 적이 없었음을 확인 --
이 박스는 `if sdi_descr: ... elif road_name: ...` 구조인데, FINDINGS.md 38차가 "신호과속 배지
부재로 판단 보류"라고 명시했고 HANDOFF.md 40차의 "정상 확인" 목록에도 도로명까지만 있고 sdi_descr
케이스는 없었음(그동안 모든 실차 스크린샷이 도로명 분기만 우연히 캡처). (2) 근본 원인을
`openpilot/system/ui/lib/text_draw.py`의 `get_text_draw_pos()`에서 확정 -- `align="left_bottom"`
분기가 아예 없어(다른 6개 정렬 케이스만 존재), `hud_renderer.py`의 `_draw_text_left_bottom()`
(제목/신호과속·교통정보 배지/도로명 3곳에서 호출)이 실제로는 `left_top`과 동일하게 동작해 텍스트가
자기 글자 높이만큼 아래로 밀려 그려짐. carrot-ryu(`435d0b58`)/carrot-ryu-v1(`9ccf1206`) 양쪽 다
동일하게 존재.

사용자 요청(공용 정렬 함수는 그대로 두고 신호과속/교통정보 배지 텍스트만 수정 + 글자크기 90%)에 따라
`hud_renderer.py`의 `_draw_turn_info_hud()` 중 `if info["sdi_descr"]:` 블록만 범위를 한정해
수정: 배지 전용 글자크기를 `eta_size`의 90%로 줄이고, 배지 위치(`badge_top`)를 먼저 고정한 뒤
실제 렌더링 동작에 맞춰 텍스트가 배지 안에 세로 중앙 정렬되도록 `label_y`를 역산. 제목(`tbt_main_text`)/
도로명(`road_name_text`)은 같은 원인이지만 이번엔 의도적으로 미수정.

anchor 1회 매치, `python3 -m py_compile` 통과 확인(리눅스 샌드박스). 반영 스크립트
(`84cha_item_sdi_badge_fix.ps1`) 전달, 실행 대기(push 미실시). 실차 검증: 미실시(이 코드 경로
자체가 프로젝트 역사상 처음 검증 대상). 상세: FINDINGS.md 2026-09-18(84차) 항목, 핵심 발견 40.

## 83차 (devnotes 정정만 · 코드 변경 없음) — 항목 21(37차) push 확인, Drive 파이프라인 이식 완료

세션 시작 체크포인트(`git ls-remote`)에서 carrot-ryu HEAD가 이미 `435d0b58e6fc3a1012d659f379770fb48654e01f`로,
82차 HANDOFF.md에 기록된 base(`1bd10a7c`, "push 대기")와 다름을 발견(4절/16절). GitHub compare
`.diff` 엔드포인트로 `1bd10a7c`..`435d0b58` 구간을 조회한 결과 정확히 1개 커밋(82cha item21
재적용)이며, 변경 파일이 gdrive_upload.py 1개뿐이고 diff 내용(import asyncio + _folder_lock +
_ensure_folder() 전체를 락으로 감싸는 것)이 82차 HANDOFF.md 기록과 정확히 일치함을 확인. 즉
사용자가 이미 `82cha_item21_gdrive_folder_lock_v4.ps1`을 실행해 push까지 완료했고, devnotes의
"push 대기" 표기만 뒤처져 있었던 것(핵심 발견 27/38과 동일 패턴). 이로써 Google Drive 파이프라인
(항목 5~10·12·17·18·20·21) 이식이 전부 완료됨. 코드 변경 없이 HANDOFF.md/CURRENT_STATUS.md 표기만
정정. 다음 세션 최우선: 항목 22(39차, `797fca2e`, 화면녹화 탭 사진 업로드 UI 신규 구현: 체크박스/
전체선택/다운로드/전송) 본편 착수.

## 82차 계속 (코드 push 대기 · v4로 원인 수정) — item21 py_compile 검증 원인 확정/수정

82차 v3 스크립트가 anchor 3개 전부 1회 매치 + 파일 쓰기까지 성공했으나 [5/6] py_compile
검증 단계에서 아무 진단 출력 없이 실패로 중단됨(commit/push는 안전하게 되지 않음, 15절/18절
안전장치 정상 동작 -- carrot-ryu HEAD는 이번 세션 시작 `git ls-remote`로도 여전히 `1bd10a7c`
그대로임을 재확인). 리눅스 샌드박스에서 v3의 anchor/치환 로직을 그대로 재현: anchor 3개 전부
1회 매치, 결과가 carrot-ryu-v1의 gdrive_upload.py와 byte-exact 일치, `python3 -m py_compile`
정상 통과(exit 0) 재확인 -- 코드/치환 로직 자체는 문제가 없음을 재확정.

원인: 핵심 발견 37(54차)과 동일한 패턴. v3의 `Get-PythonCmd`가 "python3"/"python" 존재
여부를 `Get-Command`로만 확인했는데, Windows 10/11이 이 두 이름을 App Execution Alias
(Microsoft Store 유도용 스텁)로 PATH에 기본 등록해두는 경우가 흔해 `Get-Command` 상으로는
"존재"로 잡히지만 실행하면 콘솔 출력 없이 조용히 비정상 종료함 -- v3에서 관찰된 증상과
정확히 일치. 54차에서 이미 확정된 순서("py -3" -> "python3" -> "python")를 이 스크립트가
아직 반영하지 않고 있었음(핵심 발견 37이 개별 스크립트마다 매번 재적용돼야 하는 방어
로직이라는 것을 다시 한 번 보여준 사례).

수정(v4): `Get-PythonCmd`를 "py -3" 최우선 + 각 후보를 `Get-Command` 존재 여부가 아니라
실제 `--version` 실행 결과("Python "으로 시작하는 정상 출력 + exit 0)로 검증하도록 강화.
추가로 py_compile 실행 결과(stdout/stderr)를 성공/실패 무관하게 항상 콘솔에 출력해, 다음에
다른 원인으로 실패하더라도 그 자리에서 바로 보이게 함. anchor 3개/CRLF->LF 정규화
(Read-Utf8Lf)/LF 저장 로직은 v3와 완전히 동일(이미 검증 완료, 변경 없음, 10절 최소 변경
원칙).

v1/v2/v3는 삭제하고 `82cha_item21_gdrive_folder_lock_v4.ps1`만 사용(18절: 동일 세션 재작성
시 파일명 버전 표시 규칙).

다음 세션 최우선: 실행 로그(특히 [5/6] "사용할 Python 후보 확정: ..." 로그와 py_compile
OK 여부, 최종 commit/push 출력) 확인부터. push 확인되면 Google Drive 파이프라인 이식(항목
5~10·12·17·18·20·21)이 전부 완료되므로, 이어서 항목 22(39차, `797fca2e`) 본편 착수 -> 항목
23(39cha-fix) -> 항목 26(44차) 순서로 진행. 실차 검증: 미실시(git pull 금지 상태 유지 중).


## 82차 (코드 반영, push 대기) — 항목 21(37차 원본) 재적용: gdrive_upload.py _ensure_folder() TOCTOU 레이스 수정

81차 확인(항목 20 push 완료) 이후 다음 우선순위였던 항목 21(37차, gdrive_upload.py의 _ensure_folder() Drive 폴더 중복생성 레이스컨디션 수정, asyncio.Lock)을 새 베이스(carrot-ryu `1bd10a7c790aea4a08c605502379a5da88f96aad`) 위에 재적용했습니다. 이 항목이 재적용 순서 11번(마지막)이라, push가 확인되면 Google Drive 파이프라인 이식(항목 5~10·12·17·18·20·21)이 전부 완료됩니다.

- 원인 재확인(11절 원칙, 여러 세션에 걸쳐 확장): gdrive_upload.py의 _ensure_folder()가 "캐시확인 -> 이름으로 검색 -> 없으면 생성 -> 캐시기록" 순서를 락 없이 수행해, 같은 프로세스 안에서 대시캠 탭 전송과 햄버거 메뉴 "최근 로그 업로드"가 거의 동시에 호출되면 첫 호출의 Drive API 왕복이 끝나기 전에 둘 다 캐시 미스로 판단해 폴더를 중복 생성할 수 있음(35차 핵심 발견 23 증상 4, 37차에서 확정).
- 수정: gdrive_upload.py에 모듈 레벨 `_folder_lock = asyncio.Lock()` 추가, `_ensure_folder()` 본문 전체(캐시확인~검색~생성~캐시기록)를 이 락으로 감싼. 문자열 블록 치환 3곳(import 추가, 전역 상태 변수 추가, 함수 본문 교체), 각각 파일 내 정확히 1회 매치 확인 후 반영(9절).
- 검증: 이번 세션에서 실제 `git clone`으로 carrot-ryu(`1bd10a7c`)와 carrot-ryu-v1(`9ccf1206`, 20절 리셋 직전 스냅샷, 37차 원본 수정이 이미 포함된 상태)을 각각 베이스리스 클론해 gdrive_upload.py를 직접 diff로 대조, 차이가 정확히 37차 수정(asyncio.Lock 추가 + 함수 본문을 락으로 감싸는 것) 하나임을 확인. 반영 스크립트와 동일한 Replace-Block 3개를 다른 레허사을 복본에 적용해 anchor 전부 1회만 매치함을 확인하고, 적용 결과가 carrot-ryu-v1의 파일과 byte-exact 일치(diff 0줄, md5 일치, `wc -l` 548/548)함을 확인, `python3 -m py_compile` 통과(9절/16절). 추가로 실제 반영 스크립트가 사용하는 base64 블록을 디코딩해 같은 치환을 적용한 결과도 동일함을 다시 한번 시뮬레이션으로 검증(9절/16절).
- js/css 소스 변경 없음(gdrive_upload.py 단일 파이썬 파일) 때문에 번들 재생성 불필요, params_keys.h 등록도 불필요(새 Params 키 추가 없음).
- 알려진 한계(37차와 동일, 그대로 이월): 이 락은 프로세스 내부에서만 유효함. carrot_man.py의 send_tmux_web()은 웹서버(server/app.py)와 별도 프로세스로 실행되므로, 그쪽에서 일어나는 호출까지는 이 수정으로도 보호되지 않음(근본 해결안은 범위 밖).
- 반영 스크립트(`82cha_item21_gdrive_folder_lock.ps1`) 전달, 실행 대기. 실차 검증: 미실시(git pull 금지 상태 유지 중, 항목 5~21 전체 이식이 끝나면 배포/검증 예정).

다음 세션 최우선: 82차 반영 스크립트 실행/push 확인부터. push가 확인되면 Google Drive 파이프라인 이식(항목 5~10·12·17·18·20·21)이 전부 완료되므로, 다음은 항목 22(39차, `797fca2e`) 본편 착수 -> 항목 23(39cha-fix) -> 항목 26(44차) 순서로 이어간다.


## 81차 (devnotes 정정만 · 코드 변경 없음) — 80차 반영 스크립트 실행/push 완료 확인

- 세션 시작 체크포인트(`git ls-remote`)에서 carrot-ryu HEAD가 이미
  `1bd10a7c790aea4a08c605502379a5da88f96aad`로, HANDOFF.md(80차)에 기록된 base(`a959576f`,
  "실행 대기")와 다름을 발견(4절/16절). api.github.com이 rate limit에 걸려 GitHub 웹의 compare
  `.diff` 엔드포인트로 대체 조회(working-practices 문서화된 fallback 순서)한 결과, `a959576f`..
  `1bd10a7c` 구간이 정확히 커밋 1개(`1bd10a7c`, 메시지 "36cha: screenrecord tab upload/download
  UI + gdrive label fix + tab-aware hamburger menu")임을 확인.
- 해당 커밋의 `.patch`를 직접 조회해 변경 파일 12개(routes.py `api_screenrecord_upload` 신규
  POST 엔드포인트 + 생성 번들 3종 + 소스 8개)가 80차 HANDOFF.md에 기록된 항목 20(36차,
  `0835b059`) 재적용 내용과 파일 목록·건수가 정확히 일치함을 확인.
- 결론: 사용자가 이미 `80cha_item20_screenrecord_upload.ps1`을 실행해 push까지 완료했고,
  HANDOFF.md/CURRENT_STATUS.md의 "실행 대기"/"push 미실시" 표기만 그 사이 갱신되지 못하고
  뒤처져 있었던 것(핵심 발견 27/38과 동일 패턴). 코드 변경 없이 CURRENT_STATUS.md/HANDOFF.md
  표기만 정정.
- 다음 세션 최우선: 항목 21(37차, `_ensure_folder()` TOCTOU 레이스 수정, asyncio.Lock) 재적용
  착수(재적용 순서 11번, 마지막).

## 80차 (항목 20 구현 완료 스크립트 전달, push는 사용자 실행 대기)

- 세션 시작 체크포인트: `git ls-remote`로 carrot-ryu `a959576f`/carrot-ryu-note `52af3bb`(79차) 확인, 지침
  문서(v2, 커밋 `52af3bb`)/HANDOFF.md/CURRENT_STATUS.md 재확인 후 79차가 지시한 다음 세션 최우선인
  항목 20(36차, commit `0835b059`, 화면녹화 탭 업로드 UI 신규 구현 + 당근서버 라벨/햄버거 메뉴 버그
  수정)을 이어받았다.
- 원본 커밋(`0835b059`)을 `.patch` 엔드포인트로 전체 조회(12개 파일 변경). 현재 베이스(`a959576f`)를 실제
  clone해 대상 9개 소스 파일(routes.py/index.html/en·ko·zh.js/dashcam.js/runtime.js/screenrecord.js/
  style.css)의 blob hash가 원본 diff의 pre-image hash와 정확히 일치함을 확인해 anchor가 그대로
  유효함을 확정했다(9절).
- Replace-Block 방식으로 9개 소스 파일 전체 적용(routes.py에 `api_screenrecord_upload` 신규 POST
  엔드포인트, index.html에 툴바 wrap, en/ko/zh.js에 번역키 6개, dashcam.js의 gdrive 라벨 버그
  수정, runtime.js의 탭-aware 햄버거 메뉴 + 체크박스/툴바 바인딩, screenrecord.js에 선택/업로드/
  다운로드 로직 전체 신규, style.css에 툴바 wrap 스타일). anchor 1회 매치 전부 확인.
- py_compile/node --check 통과 후 `npm install && node build.mjs`로 생성 번들(js/generated/logs.js,
  css/generated/logs.css, generated/asset-manifest.json) 재생성 -- 변경 파일이 원본 커밋과 정확히 같은
  12개임을 `git status`로 확인.
- `node --test` 747개 중 746개 통과, 유일 실패(`ar_projection_golden.test.mjs`)는 무수정 base clone에서도
  동일하게 재현되는 기존 환경 문제(Python/numpy)로 이번 변경과 무관함을 별도 무수정 clone으로
  재확인.
- 재현성 검증: 추출한 소스 전용 diff를 완전히 독립된 새 clone에 `git apply --check` + `git apply`로
  재적용하고 다시 빌드한 결과, 12개 파일 전부의 blob hash가 첫 번째 clone과 byte-exact 일치함을
  확인(16절/9절 검증 파이프라인).
- 반영 스크립트(`80cha_item20_screenrecord_upload.ps1`) 작성/전달. 실행 대기(push 미실시). 실차
  검증: 미실시(항목 5~21 전체가 아직 실기기 미배포, git pull 금지 유지 중).

## 79차 (항목 18 완료 -- ko.js gdrive 클라이언트 유형 안내 문구 수정)

- 세션 시작 체크포인트: `git ls-remote`로 carrot-ryu `c197cd4e`/carrot-ryu-note `2a3b6de`(78cha-fix,
  CRLF 정상화 완료) 확인, 지침 문서(v2, 커밋 `2a3b6de`)/HANDOFF.md/CURRENT_STATUS.md 재확인 후
  이어받음(HANDOFF.md 지시대로 항목 18부터 착수).
- 항목 18(33차, commit `789667f7`) 원본 커밋을 `github.com/.../commit/789667f7.patch`로 직접
  조회(GitHub API rate limit로 API 대신 .patch 엔드포인트 사용): `openpilot/selfdrive/carrot/web/
  js/translations/ko.js` 한 파일, 한 줄 변경(`web_gdrive_client_id_desc`: "데스크톱 앱 유형" ->
  "TV 및 제한된 입력이 있는 기기 유형"). sparse-checkout으로 `web/` 디렉터리 구조를 확인해 이 파일이
  `index.html`에서 `<script src="/js/translations/ko.js">`로 직접 로드되고 `build.mjs` 번들
  대상이 아님을 확인 -- npm 빌드 불필요.
- 새 베이스(`c197cd4e`)의 대상 라인이 원본 커밋 anchor와 1회만 매치함을 sandbox에서 미리 시뮬레이션,
  변경 후 결과가 원본 diff와 한 줄까지 완전히 동일함을 확인(9절).
- 반영 스크립트 최초 전달본(v1)이 실행 중 anchor 0회 매치로 안전하게 중단됨 -- 원인은 스크립트
  자체가 UTF-8 BOM 없이 생성되어 Windows PowerShell 5.1이 CP949로 잘못 해석, 스크립트 내부 한글
  anchor 문자열 자체가 로드 시점에 이미 깨져 있었던 것(9절 필수 규칙에 이미 명시된 이슈의 재발이나
  이번엔 Claude가 스크립트 생성 시 직접 저지름; 15절/18절의 "강제 진행 금지" 안전장치가 정상
  동작해 대상 파일은 전혀 손상되지 않음). BOM 포함 `-v2`로 재생성/재전달해 해결, push 완료.
- push 완료 후 `git ls-remote` + GitHub compare API(`c197cd4e...a959576f`)로 재검증: 변경 파일이
  정확히 1개(`ko.js`), diff가 원본 33차 커밋과 완전히 동일함을 확인. raw 조회(SHA고정, 새 HEAD
  `a959576f`)로 대상 파일 전체가 sandbox 예상 결과와 byte-exact 일치함도 확인(16절).
- carrot-ryu 새 HEAD: `a959576f6973b44d878617399241cd35c47bf1bd`.
- 실차 검증: 미실시.
- 다음 세션 최우선: 항목 20(36차, commit `0835b059`, 화면녹화 탭 업로드 UI 신규 구현 + 당근서버
  라벨/햄버거 메뉴 버그 수정) -- 항목 5~10·12·17·18 전부 끝난 뒤 순서 10번.

## 78차 (항목 17 완료 -- Google Drive drive.file 스코프+폴더 자동생성 복귀)

- 세션 시작 체크포인트: `git ls-remote`로 carrot-ryu `27d81a4`/carrot-ryu-note `227bde4`(77차-fix)
  확인, 지침 문서(v2, 커밋 `227bde4`)/HANDOFF.md/CURRENT_STATUS.md 재확인 후 이어받음.
- 사용자가 올린 첫 파일(`77cha-fix_devnotes_item12_complete.ps1`)이 채팅 설명("항목 17 스크립트")과
  다른 파일임을 발견 -- 실제로는 이미 push 완료된 77차-fix devnotes 정정 스크립트였음(커밋 메시지가
  carrot-ryu-note 현재 HEAD와 문자 그대로 일치함을 `git log`로 확인, 16절). 사용자가 실제 항목 17
  스크립트(`77cha_item17_gdrive_file_scope.ps1`, 챗지피티 작성)를 재업로드.
- 반영 전 원본 커밋(`c704371a`, 32차)을 독립적으로 fetch해 부모 SHA(`34bb41bc1b9c2fdb...`)와
  pre-image blob hash(`bfd4b0d0d770...`)가 새 베이스(`27d81a4`)의 대상 파일과 완전히 일치함을 확인,
  patch 생성/`git apply --check`/적용/`py_compile`까지 전부 독립 재현해 스크립트 로직 정확성을
  먼저 검증(9절).
- 실행 중 버그 3건을 사용자 실행 로그로 실증하며 순차 수정(매번 강제진행 없이 안전하게 중단됨을
  확인한 뒤 수정, 15절/18절 안전장치 정상 동작):
  1. `git fetch origin c704371a`(8자리 축약 SHA)가 GitHub에서 거부됨(`couldn't find remote ref`)
     -- carrot-ryu-v1 아카이브 브랜치에서 40자리 전체 SHA를 찾아 교체해 해결.
  2. `git diff ... | Out-File -Encoding ascii`로 patch를 생성하면 PowerShell 파이프라인 캡처
     과정에서 patch가 손상됨(`git apply --check`에서 `patch fragment without header`) -- 비ASCII
     (한글 주석) 다수 포함 diff를 파이프라인으로 캡처/재인코딩하는 과정의 손상으로 추정, `git diff
     --output=<file>`(git이 파이프라인 없이 직접 파일에 기록)로 교체해 해결.
  3. `$Diff = git ... diff -- $Target` 결과를 PowerShell 배열로 받은 뒤 `-notmatch`로 검사하던
     로직이 상시 실패: PowerShell의 배열 `-match`/`-notmatch`는 "전체가 매치 안 하면 참"이 아니라
     "매치 안 하는 개별 원소들의 배열"을 반환하므로, 89줄 중 1줄만 매치해도 나머지 88줄이 반환돼
     항상 참으로 평가됨. 이미 스칼라 문자열로 읽어둔 `$PatchText`를 재사용하도록 교체해 해결.
  4. (부수) `py_compile` 검증에서 Windows 앱 실행 별칭으로 인한 `python3`/`python` 스텁 문제
     재발(핵심 발견 37과 동일 패턴) -- `py -3`→`python3`→`python` 순으로 `--version` 출력을
     실제로 확인한 후보만 쓰는 `Get-PythonCmd` 함수를 재적용.
- v2→v5까지 버전 표시 규칙(9절)에 따라 순차 전달, 최종 v5 실행으로 carrot-ryu commit
  `c197cd4e627c6f266e6f5529d152d1984a47fcd6`(커밋 메시지: `32cha: restore drive.file scope and
  auto-create Drive folder`)로 push 완료.
- push 완료 후 `git ls-remote` + 독립 clone으로 재검증: 새 HEAD의 `gdrive_upload.py` blob hash
  (`e6a5832f07af9a3249942b9f4d64df28ffe4a5a7`)가 원본 32차 커밋의 결과 blob hash와 완전히
  일치함을 확인(byte-exact, 16절). diffstat도 스크립트 로그와 동일(`89 changes, 53 insertions(+),
  36 deletions(-)`).
- 코드 push까지 마친 직후 devnotes(CURRENT_STATUS.md/WIP.md/HANDOFF.md) 3개 파일을 편집하던 중
  대화가 HANDOFF.md 작성 전에 끊겨 아무것도 push되지 못한 채 남았다. 이어받은 새 대화가 세션 시작
  체크포인트에서 `git ls-remote`로 carrot-ryu-note가 여전히 `227bde4`(77차-fix, devnotes 미반영)임을
  확인하고, CURRENT_STATUS.md/WIP.md 편집을 처음부터 다시 확인/재작성한 뒤 이 파일까지 완성해 같은
  세션 번호(78차)로 한 번에 push했다 -- 76차/77차와 동일한 "코드 push는 됐는데 devnotes만 뒤처짐"
  패턴(핵심 발견 27/38)의 새로운 변형(지연이 아니라 완전 유실 직전까지 갔던 사례)이며, 상세는 핵심
  발견 39 항목 참고.
- 실차 검증: 미실시(git pull 금지 상태 유지 중). drive.file 스코프 자체는 리셋 이전 35차에서 실기기
  연결 성공 기록이 있었으나, 이번 재적용본은 처음부터 재검증 필요.
- 다음 세션 최우선: 항목 18(33차, commit `789667f7`, ko.js gdrive 클라이언트 유형 안내 문구 수정)
  -- 항목 10(web settings UI) 위에 적용.

## 77차 계속 (item12 push 완료 재확인 + devnotes 정정)

- `77cha_item12_log_upload_targets.ps1` 실행 완료 보고 수신, `git ls-remote`로 carrot-ryu HEAD가
  `27d81a4`로 바뀐 것을 확인. GitHub compare API(`c9a03b5`..`27d81a4`)로 diff가 원본 25차 커밋
  (`d338afb7`)과 정확히 동일함(`web_settings.py` 1개 파일, `f41e1bb4b4` -> `4d669cde7f`)을 재확인.
- `77cha_devnotes_carrot_ryu_note.ps1`(최초 버전)이 WIP.md 상단 anchor 검증에서 중단됨: WIP.md
  34862바이트 지점에 과거 세션이 남긴 "# WIP" 헤더 중복(이 파일 하단에 이미 낮은 우선순위 기지
  이슈로 기록돼 있던 것)이 있어 "파일 전체 매치 1회" 조건이 2회로 걸림. 아무것도 커밋되지 않고
  안전하게 중단됨을 `git ls-remote`로 확인(15절/18절 안전장치 정상 동작).
- 삽입 위치가 항상 파일 절대 최상단이라는 점에 착안, 검증을 전체 매치 횟수에서 `StartsWith`로
  바꾼 `77cha_devnotes_carrot_ryu_note-v2.ps1`로 재전달(9절 버전표시 규칙). 사용자 실행 →
  carrot-ryu-note commit `f76209d`로 push 완료.
- WIP.md/CURRENT_STATUS.md/HANDOFF.md 3개 파일 변경 내용을 raw 조회(SHA 고정)로 재확인,
  의도한 내용과 정확히 일치함을 확인.
- CURRENT_STATUS.md/HANDOFF.md에 남아있던 "실행 대기" 표기를 실제 완료 상태(commit `27d81a4`,
  `f76209d`)로 이번 세션 안에서 바로 정정(76차형 지연 재발 방지).
- 다음 세션 최우선: 항목 17(32차, `c704371a`, drive.file 스코프+폴더 자동생성 복귀)부터 착수.

## 77차 (항목 12 착수 -- LOG_UPLOAD_TARGETS gdrive 누락 수정)

- 세션 시작 체크포인트: `git ls-remote`로 carrot-ryu `c9a03b5`(76차)/carrot-ryu-note `102131e`(76차)
  확인, 지침 문서 v2(커밋 `102131e`) 재조회 후 HANDOFF.md/CURRENT_STATUS.md 순서로 이어받음.
  76차가 남긴 "다음 세션 최우선: 항목 12"를 그대로 착수.
- 항목 12(25차, commit `d338afb7`, "25cha: fix LOG_UPLOAD_TARGETS missing gdrive"): 원본 커밋 patch를
  `github.com/ryujmin97/openpilot/commit/d338afb7.patch`로 직접 조회 -- 대상 파일
  `openpilot/selfdrive/carrot/server/services/web_settings.py` 한 곳,
  `LOG_UPLOAD_TARGETS = {"carrot", "toss"}` -> `{"carrot", "toss", "gdrive"}` 한 줄 변경.
- 새 베이스(`c9a03b5`)에서 해당 파일을 raw로 조회해 `git hash-object`로 blob hash를 계산한 결과
  `f41e1bb4b4a31b380b33968d41781a98101b2661`로, 원본 커밋의 pre-image blob hash(`f41e1bb4b4...`)와
  완전히 일치함을 확인 -- 25차 이후 다른 어떤 세션도 이 파일을 건드리지 않았다는 뜻이므로 원본 diff를
  그대로(byte-exact) 재적용 가능하다고 판단.
- 대상 줄이 파일 전체에서 정확히 1회만 존재함을 확인(anchor 조건 충족, 9절).
- 반영 스크립트(`77cha_item12_log_upload_targets.ps1`) 작성: git clone(core.autocrlf=false) ->
  anchor 1회 매치 재확인 -> 문자열 치환 -> py_compile 정적 검증(Get-PythonCmd 자동탐지, 핵심 발견 37
  방식 적용) -> commit/push -> 임시폴더 삭제. 실행 대기.
- 실차 검증: 미실시(반영 자체가 아직 push 전).
- 다음 세션 최우선: 이 스크립트 push 완료 확인(`git ls-remote` + `git hash-object`로 결과 blob
  재확인) 후 항목 17(32차, `c704371a`, drive.file 스코프+폴더 자동생성 복귀)로 이어서 진행.

## 76차 (devnotes 정정: 항목 10 실제 push 완료 확인) -- 코드 변경 없음

- 배경: 세션 시작 시 HANDOFF.md(75차 최종 갱신)는 항목 10 반영 스크립트
  (`75cha_item10_web_settings_gdrive.ps1`) 실행 대기 상태로 기록돼 있었으나, `git ls-remote`로
  carrot-ryu HEAD를 직접 확인한 결과 이미 `c9a03b5`로, HANDOFF에 기록된 base(`7a1555ed`)와 달랐다.
- GitHub compare API(`7a1555ed`..`c9a03b5`)로 그 사이 커밋을 조회한 결과 정확히 2개:
  `61bfcd44`(AR projection golden fixture 갱신, Drive 작업과 무관) + `c9a03b5`("75cha: web settings
  Google Drive 계정 연결 UI 재적용", 항목 10, 번들 재생성 포함).
- `c9a03b5`의 변경 파일 9개(base.css/components.js/schema.js 전체교체 + en.js/ko.js/zh.js
  anchor삽입 + tools.css/tools.js/asset-manifest.json 생성번들)가 HANDOFF.md 75차 기록과 정확히
  일치함을 확인 -- 사용자가 이미 75차 반영 스크립트를 실행/push까지 완료했고, devnotes만 그 사실을
  따라가지 못했던 것(핵심 발견 27/38과 동일 패턴).
- 코드 변경 없이 CURRENT_STATUS.md(최상단 carrot-ryu HEAD 표기, 항목 10 줄) + HANDOFF.md만 정정.
- 다음 세션 최우선: 항목 12(25차, commit `d338afb7`, `LOG_UPLOAD_TARGETS`에 "gdrive" 누락 수정)
  원본 커밋 patch 조회부터 실제 착수.

## 75차 (항목 10 web settings Drive UI 재적용 스크립트 준비, 항목 5~9 반영 사후확인)

- 배경: 이 세션 시작 시 HANDOFF.md(69차 최종 갱신)는 "항목 5부터 순서대로 재적용" 상태로 기록돼
  있었으나, git ls-remote로 carrot-ryu HEAD를 직접 확인한 결과 이미 `7a1555ed`(74차 커밋)로, 항목
  5~9(70~74차, commit 017072dd/4b6c8f84/75c7c316/bc021ed9/7a1555ed)가 전부 재적용/push 완료돼
  있었다. devnotes(HANDOFF.md/CURRENT_STATUS.md)가 여기까지 갱신되지 못한 채 직전 세션이 끊긴
  것으로 추정된다(핵심 발견 27/38과 동일 패턴).
- 독립 조회로 재확인: `gdrive_upload.py` 존재(`openpilot/selfdrive/carrot/gdrive_upload.py`),
  `params_keys.h`에 `CarrotGDriveClientId/Secret/RefreshToken` 3종 등록, dashcam `routes.py`에
  `upload/summary`/`upload/start`/`upload/test`/`upload/job`/`upload/cancel` POST 엔드포인트
  전부 존재(항목 5~9 실제 반영 확인).
- 이어서 항목 10(23차, commit `272834b`, web settings log_upload에 Google Drive 계정 연결 UI
  추가) 재적용 착수. 원본 커밋 patch를 조회해 9개 파일(base.css/components.js/schema.js
  전체교체 3개, en.js/ko.js/zh.js anchor삽입 3개, tools.css/tools.js/asset-manifest.json
  생성번들 3개) 구조를 확인.
- base.css/components.js/schema.js pre-image hash(`d8d64ca104`/`3f81b85f7c`/`858a20ad21`)가
  현재 베이스(`7a1555ed`)와 정확히 일치함을 확인(항목 10 미반영 상태 재확인, 전체교체로 처리
  가능).
- en.js/ko.js/zh.js는 다른 세션들이 이미 다른 번역 키를 추가해 발산돼 있어(항목 7과 동일 패턴),
  `web_log_upload_target_toss` 줄을 anchor로 삼아 정확히 1회 매치 확인 후 15개 신규 키
  (`web_gdrive_*` 등)만 삽입하는 방식으로 처리.
- 독립 `git clone`(carrot-ryu HEAD `7a1555ed`)에 6개 소스 변경을 실제로 적용한 뒤
  `npm install && node build.mjs`로 생성 번들 3종(tools.css/tools.js/asset-manifest.json)
  재생성, 변경된 파일이 원본 커밋과 정확히 같은 9개 파일 목록임을 `git status`로 확인,
  `node --check`(tools.js 구문) + `node --test`(747/747) 전부 통과.
- 반영 스크립트(`75cha_item10_web_settings_gdrive.ps1`)를 9절 규칙(UTF-8 BOM,
  `core.autocrlf=false`, base64 임베드 전체교체 3개 + anchor 삽입 3개 + 사용자 PC에서
  `npm install && node build.mjs` 실행 + `node --test` 747/747 검증 + git add/commit/push +
  임시폴더 삭제)대로 작성, 스크립트에 임베드된 base64/anchor 데이터를 GitHub 최신 상태에서
  직접 재조회한 값으로 재검증(round-trip 확인, 이전 세션 결과를 그대로 신뢰하지 않고 이번
  세션에서 처음부터 재현 -- 세션 간 컨테이너 초기화 원칙).
- 실행 대기. 이번 세션에서 HANDOFF.md/CURRENT_STATUS.md를 실제 GitHub 상태(항목 5~9 완료, 항목
  10 스크립트 준비)에 맞게 동기화.

다음 세션 최우선: (1) 이번 75차 반영 스크립트 push 확인(`git ls-remote`), (2) 항목 12(25차,
`d338afb7`, `LOG_UPLOAD_TARGETS`에 "gdrive" 등록) 재적용(재적용 순서 7번, 항목 10 다음), (3)
이후 17→18→20→21 순서로 계속.

## 69차 (devnotes 정정만, 코드 변경 없음) — Google Drive 관련 항목(5~10·12·17·18·20·21) 61차 리셋 이후 미반영 재확인/정정

- 배경: 68차 HANDOFF의 "다음 세션 최우선: 항목 22(39차, `797fca2e`) 본편 착수"를 시작하기 전, 항목 22의
  routes.py 부분이 실제로 항목 20(36차, `0835b059`) 바로 뒤에 이어붙는 diff임을 확인했고, 항목 20 자체가
  Google Drive 업로드 파이프라인 전체(항목 5~10·12·17·18·21, 15~37차에 걸쳐 만들어짐)에 의존한다는 것을
  발견했다.
- 이 사슬이 61차(20절) 리셋 이후 실제로 재적용됐는지 CURRENT_STATUS.md 문구("GitHub 반영됨")만으로는
  판단할 수 없어서, `codeload.github.com`으로 현재 carrot-ryu 브랜치를 독립적으로 clone해 직접 확인했다.
- 확인 결과: `gdrive_upload.py` 파일이 저장소 어디에도 없고, `routes.py`(모든 서브시스템)에 업로드용
  POST 엔드포인트가 하나도 없음(GET만 존재). 즉 항목 5~10·12·17·18·20·21은 전부 61차 리셋 때 함께
  사라졌고, 지금까지(63~68차) 재적용되지 않았다.
- 원인 추정: 62차 안내문이 "재적용될 때마다 개별 갱신하라"고 이미 경고했지만, 63~68차는 hud_renderer.py
  계열(항목 3·4·11·13~16·19·25·27·28)만 순서대로 처리해와서 Drive 관련 항목은 그 사이 아무도 다시
  들여다보지 않았다. 목록 순서(5,6,...,17,18,...,20,21)만 보면 이미 다 끝난 것처럼 보이지만, "GitHub
  반영됨" 표기 자체가 리셋 이전(과거) 기록이었다.
- CURRENT_STATUS.md의 항목 5~10·12·17·18·20·21·22·23 줄과 carrot-ryu HEAD 표기를 실제 상태(2088c546,
  해당 항목 전부 미반영)에 맞게 정정했고, 각 줄에 재적용 순서(5→6→7→8→9→10→12→17→18→20→21)를 명시했다.
  핵심 발견 38로 이 패턴 자체도 기록해둠(20절 리셋 이후 stale 표기가 여러 세션 동안 방치될 수 있다는 것).
- 이번 세션은 코드 변경 없이 devnotes 3개 파일(HANDOFF.md/CURRENT_STATUS.md/WIP.md)만 교체/이어붙였다.
- 다음 세션 최우선: 항목 5(15차, `183bef9`, gdrive_upload.py 신규)부터 재적용 시작. 이후 6→7→8→9→10→
  12→17→18→20→21 순서 그대로(파일 스코프가 서로 겹치지 않아 순서 변경 근거 없음), 전부 끝난 뒤 22→23→26.


## 68차 (항목 13~16+19 재적용, 항목 22 착수 전 의존관계 정리)

- 배경: 직전 세션(67차/67차-fix) HANDOFF의 "다음 세션 최우선: 항목 22(39차, `797fca2e`) 재적용"을
  착수하기 전, 원본 diff와 현재 베이스(`81754ea3`)를 실제로 대조해봤다.
- 발견: 항목 22의 `hud_renderer.py` 부분(경로안내 박스 상하 여백 통일, `content_shift_y`)은
  항목 13→14→15→16(27~30차, 경로안내 박스 크기/레이아웃 변경)뿐 아니라 항목 19(34차, 실제 커밋
  메시지는 "33cha", `9fdefb3d` -- 도착 텍스트 크기 40->32, 도로명 위치 박스 안쪽 이동)까지 순서대로
  적용되어 있어야 anchor가 맞는 diff였다. CURRENT_STATUS.md 번호 목록만 보면 17·18(Drive 관련,
  hud_renderer.py와 무관)이 13~16과 19 사이에 끼어있어 이 의존관계가 바로 안 보였다.
- 사용자에게 이 발견을 보고하고 "먼저 13~16(+19) 재적용 -> 이후 항목 22 전체 적용" 순서로 진행하기로
  합의(사용자가 "2번" 선택).
- 격리된 로컬 git 저장소에서 원본 5개 커밋(`5f5e49d0`/`cc73f629`/`67a8e10`/`34bb41bc`/`9fdefb3d`)의
  `hud_renderer.py` diff를 현재 베이스 위에 13->14->15->16->19 순서로 `git apply --check` -> `git apply`로
  재현, 각 단계 성공 확인. 항목 13에서 `_format_eta_text` -> `_format_eta_time_text`로 이름이 바뀌는
  유일한 호출부도 같은 블록 안에 포함돼 dangling 참조가 남지 않음을 grep으로 확인.
- 5개 적용이 끝난 최종 상태에 항목 22(`797fca2e`)의 `hud_renderer.py` diff를 `git apply --check`로
  시도해 정상 통과함을 확인 -- 13→14→15→16→19 순서가 항목 22의 전제 상태와 정확히 일치함을
  실증했다(이번 세션에서 항목 22 자체는 적용하지 않음, 사전 검증만).
- 최종 반영 형태: `hud_renderer.py` 상단 `import re` 1줄 추가 + `_draw_turn_info_hud`를 포함하는
  연속 블록(원본 168줄 -> 242줄) 교체. 두 anchor(상단 import 3줄 컨텍스트, 본문 블록) 모두 현재
  베이스에서 1회만 매치함을 확인(9절 anchor 유일성 원칙). `python3 -m py_compile` 통과.
- 코드 변경은 아직 반영 스크립트 실행 전(다음 단계: 사용자 PC에서 PowerShell 스크립트 실행 ->
  push -> `git ls-remote`로 재확인).
- 다음 세션(또는 이 세션 이어서) 최우선: (1) 이번 68차 반영 스크립트 push 확인, (2) 항목 22 본편
  착수(스크린샷 업로드 UI 체크박스/전체선택/다운로드/전송 툴바 + `content_shift_y` + 생성 번들
  재생성), (3) 항목 23(39cha-fix, `bdde8326`), (4) 항목 26(44차, formatLogBytes import).

## 67차 계속 (stray 파일 발견 → 제거 완료, 항목 11 최종 정리)

- reapply_item11_67cha.ps1 실행 로그를 이어받아 `git ls-remote` + 독립 `git clone`으로 재확인한 결과, carrot-ryu HEAD가 `63addc2e`로 push되어 항목 11(24차, 화면녹화 탭 사진 스트립) 코드 자체는 원본과 동일하게 정상 반영됨을 확인.
- 저장소 루트를 전수 점검하는 과정에서, 반영 스크립트 준비 중 만들어진 파이썬 헬퍼(`apply_item11_67cha.py`)가 같은 커밋에 실수로 함께 커밋된 것을 발견(9절/18절 -- 산출물이 아닌 임시 파일 유입). 다른 루트 파일은 전부 정상 openpilot 저장소 파일로 확인, stray는 이 파일 하나뿐.
- 제거 전용 스크립트(`cleanup_stray_67cha.ps1`)를 9절 형식(UTF-8 BOM, CRLF, `core.autocrlf=false` clone, stray 없으면 무변경 중단, 각 단계 실패 시 즉시 중단, `--force` 미사용)으로 작성해 사용자가 실행, `carrot-ryu`에 commit `81754ea3`로 push됨을 push 로그로 확인.
- 독립 `git clone --depth 1 --branch carrot-ryu`로 재검증: `apply_item11_67cha.py`가 저장소에서 완전히 사라졌고, 항목 11 코드(`screenshots.js`, `runtime.js`, `style.css`, `config.py`, `catalog.py`, `routes.py`, 생성 번들)는 그대로 정상 존재함을 확인(16절). 항목 11은 이제 최종 정리 완료 상태.
- CURRENT_STATUS.md 항목 11/26 및 최상단 HEAD 표기를 `81754ea3` 기준 "정리 완료"로 갱신.

## 67차 (20절 이식 항목 11 재적용 준비) — 화면녹화 탭 사진 스트립 재적용 스크립트 전달 (실행 대기)

- 66차 미완료 이월(항목 11->22->23->26 의존관계, 순서 확정 필요)에 대해 사용자가 "항목 11만 우선 적용(22/23/26은 이월)"로 확정.
- 원본 24차 커밋(a7a912c1)의 diff를 github.com/.../commit/a7a912c1.patch로 직접 조회 -- 9개 소스 파일 수정 + screenshots.js 신규 생성 내용 전부 확인.
- 현재 carrot-ryu HEAD(0d511753)에서 raw 조회한 9개 파일에 anchor가 전부 1회씩 매치됨을 sandbox에서 검증, screenshots.js는 여전히 없음(GitHub 404, 66차 전제와 일치).
- 독립적인 실제 git clone(carrot-ryu)에 같은 패치를 다시 적용해 재현하고, 그 자리에서 npm install && node build.mjs로 생성 번들(logs.css/asset-manifest.json/logs.js)까지 재생성 -- node --check(runtime.js/screenshots.js/generated logs.js) + python3 -m py_compile(config.py/catalog.py/routes.py) + node --test(747/747) 전부 통과 확인(45차 핵심 발견 30 재발 방지).
- config.py/catalog.py/routes.py, screenshots.js, style.css는 원본 24차 결과와 바이트 단위 완전 동일, index.html/en.js/ko.js/zh.js/runtime.js는 그 사이 다른 세션들의 변경과 정상 공존/병합됨을 확인.
- 반영 스크립트(reapply_item11_67cha.ps1)는 9절 형식(Replace-Block + CRLF/LF 정규화, autocrlf=false clone, UTF-8 BOM, Get-PythonCmd) + 그 자리에서 npm install/node build.mjs/node --check/py_compile까지 전부 수행하도록 작성, 사용자 실행 대기.
- 부수적으로 CURRENT_STATUS.md 최상단 carrot-ryu HEAD 표기가 61차 커밋으로 오래 방치돼 66차 실제 최신과 어긋나 있던 것을 발견/정정(16절, 코드 변경 아님).

## 66차 (20절 이식 항목 27+28 재적용) — delete_all_videos 확장 + 녹화 버튼 깜빡임(44차 e2f35619 일부)

- 44차 원본 diff를 GitHub commit patch로 재확인: 커밋 하나(e2f35619)에 항목 26·27·28이 함께
  묶여있었음. 항목 26(screenshots.js formatLogBytes import 수정)은 전제 파일인 screenshots.js
  자체(항목 11, 24차)가 새 베이스(706efb47 계열)에 아직 없어(GitHub raw 조회 404) 적용 불가로
  확정, 이번 세션은 파일 의존성이 없는 항목 27+28만 진행.
- 항목 27: dispatcher.py의 delete_all_videos(비동기/동기 두 구현)가 `/data/media/0/videos`
  한 곳만 하드코딩되어 있던 것을, 이미 config.py에 정의된 SCREEN_RECORDING_DIRS(영상+스크린샷
  폴더 전체) 기준으로 확장. import 한 줄 + 두 함수 내 경로 리스트 두 곳 수정.
- 항목 28: record_button.py 전체교체(set_blink_phase() 추가, 녹화 중 채움/테두리를 번갈아
  그림) + hud_renderer.py 1줄(_record_button.set_blink_phase(self._blink_timer <= 8) 호출) --
  기존 _blink_timer(카메라감지/과열경고에 이미 쓰던 프레임 카운터)를 재사용.
- sandbox에서 5곳 전부 1회 매치 + py_compile 통과 확인 후 전달, 원본 44차 커밋과 diff까지 동일함을
  git commit patch 대조로 확인.
- 사용자가 `reapply_items2728_66cha.ps1` 실행, commit `0d5117533e0703e442fd1664b8ee00146cf40a4f`로
  carrot-ryu에 push 완료(실행 로그 끝까지 확인, 3 files changed).
- 남은 항목 26(screenshots.js)은 항목 11(24차)과 항목 23(39cha-fix)까지 먼저 반영돼야 처리 가능 --
  다음 세션 이후로 이월, WIP_SYNC.md에 의존관계 기록 필요.
- 콤마 디바이스 git pull 금지 상태 계속 유지.

## 65차 (20절 이식 항목 25 재적용) — 온로드 원형 녹화 버튼 추가(42차 4f81ab75 원본)

- 64차에서 완료된 항목 4에 이어, 스크린샷 후속 수정 묶음(25·26~28·30~36번)을 17절 원칙대로
  세션 하나에 몰지 않고 항목 단위로 나눠 진행하기로 함. 그 첫 항목인 25번(42차, 온로드 원형
  녹화 버튼 추가)부터 착수.
- record_button.py 신규 추가(스크린샷 버튼 오른쪽에 배치, ScreenRecord 파라미터를 토글하는
  원형 녹화 버튼, 녹화 중엔 빨간 원 채움) + hud_renderer.py에 import/UIConfig 필드/__init__/
  _render/user_interacting 5곳 배선. 원본 커밋(4f81ab75)과 동일한 diff.
- 사전 확인: ScreenRecord 파라미터는 params_keys.h에 이미 등록되어 있어 추가 등록 불필요,
  put_bool_nonblocking(params_pyx.pyx)/gui_app.is_recording()(application.py)/Widget/
  set_click_callback 모두 새 베이스에 그대로 존재함을 확인.
- sandbox에서 5개 Replace-Block 전부 1회 매치 + 신규 파일까지 py_compile 통과 확인 후 전달.
- 사용자가 `reapply_item25_65cha.ps1` 실행, commit `b152e192`로 carrot-ryu에 push 완료(원본
  42차 커밋과 정확히 일치함을 git ls-remote + commit diff로 재확인).
- 콤마 디바이스 git pull 금지 상태 계속 유지.

## 64차 (20절 이식 항목 4 재적용) — 온로드 시계 좌측 화면 경계 잘림 수정(13차 원본)

- 63차에서 이월된 다음 작업 후보 중 13차(시계 좌측 경계 잘림, 2adced8)를 선택해 착수.
- GitHub commit diff 조회로 원본 diff 확인: hud_renderer.py `_draw_date_time`의
  `if show_datetime in (1, 2):` 블록에, 시계 텍스트 실측 폭(`measure_text_cached`) 기준으로
  좌측 여백(`UI_CONFIG.border_size`)을 보장하도록 x좌표를 보정하는 7줄 추가가 전부인 작은
  diff였음.
- 새 베이스(carrot-ryu HEAD `429f105e`, 63차에서 12차 재적용된 상태)의 hud_renderer.py를 직접
  조회해, 해당 함수가 13차 원본이 기준으로 삼은 blob(`0e9c84a51e`)과 정확히 동일하게 남아있음을
  확인(12차 재적용 이후 변경된 적 없음). `measure_text_cached`/`draw_text_ui_style`/
  `UI_CONFIG.border_size` 모두 이미 import/정의되어 있어 추가 의존성 없음.
- Replace-Block(9절, CRLF->LF 정규화 병행)으로 sandbox에서 원본과 동일한 삽입 블록을 구성,
  정확히 1회 매치 + `py_compile` 통과 확인. 치환 결과 blob이 원본 13차 커밋의 결과 blob
  (`d7e8d7b6a5`)과 완전히 일치함까지 diff로 재확인(바이트 단위 재현 -- 의미상 동등이 아니라
  원본과 완전히 같은 코드가 반영됐음을 뜻함).
- 사용자가 `reapply_13cha_64.ps1` 실행, commit `4e3b44a81f2fc79c3b6f23ebaee40a1bc73d370b`로
  carrot-ryu에 push 완료. git ls-remote + commit diff로 재확인.
- 콤마 디바이스 git pull 금지 상태 계속 유지(12·13차 두 항목만 반영된 상태).

## 63차 (20절 이식 항목 3 재적용) — 온로드 시계 초단위 표시 + 스크린샷 버튼(12차 원본)

- 62차에서 확정한 이식 순서대로 항목 1번(12차, 684b30d 기준: hud_renderer.py에 스크린샷 버튼
  배선 + 시계를 분 단위에서 초 단위로 변경, screenshot_button.py/screenshot_capture.py 신규)에
  착수.
- 첫 반영 스크립트가 hud_renderer.py의 여러 줄짜리 Replace-Block(5번, "render screenshot
  button")에서 "expected 1 match, found 0"으로 중단됨(commit/push 이전이라 GitHub에는 영향
  없음). 원인은 저장소 루트 `.gitattributes`의 `* text=auto` -- `git clone
  --config core.autocrlf=false`를 줘도 일부 Windows Git 환경에서는 체크아웃 시 CRLF로 변환될
  수 있음(GitHub 원본 blob은 LF임을 raw 조회로 확인). 한 줄짜리 anchor(1~4번)는 우연히 통과하고
  여러 줄짜리(5~7번)만 취약했던 것.
- Replace-Block 함수에 매칭 전 CRLF->LF 정규화(9절에 이미 있던 원칙을 실제로 구현)를 추가한
  reapply_12cha-v2.ps1로 재작성, sandbox에서 새 베이스(706efb47) 파일에 대해 7개 블록 전부 +
  신규 파일 2개를 재현해 정확히 1회 매치 + py_compile 통과를 사전 확인한 뒤 전달.
- 사용자가 실행, commit `429f105e`로 carrot-ryu에 push 완료. git ls-remote + commit diff(API
  rate limit 회피용 github.com/.../commit/<sha>.diff)로 실제 반영 내용이 의도와 정확히 일치함을
  확인.
- 12차 "원본" 그대로 반영된 상태이며, 이후 세션들(25·26~28·30~36번)에서 쌓인 스크린샷 관련
  후속 수정(DPI 반전, 캡처 타이밍, render-texture 재설계, 상하반전 등, carrot-ryu-v1에는 이미
  실차검증까지 끝난 상태로 존재)은 아직 미반영 -- 다음 세션에서 순서를 정해 이어감.
- 콤마 디바이스 git pull 금지 상태 계속 유지.

## 62차 (devnotes 사후 동기화, 코드 변경 없음) — 61차 20절 리셋 결과를 devnotes에 반영

- 직전 61차 세션에서 20절 절차에 따라 carrot-ryu를 carrot-ms 현재 HEAD(706efb47)로 force-push
  재생성하는 작업 자체는 실제로 완료됐으나(사용자 승인, git ls-remote로 확인), 뒤이어 작성
  중이던 devnotes(HANDOFF/WIP_SYNC/WIP/CURRENT_STATUS) 61차 갱신 스크립트는 무료 사용량
  소진으로 전달되지 못한 채 세션이 끊겼다.
- 62차 세션 시작 시 4절 0단계에 따라 재확인하는 과정에서, 코드 브랜치(이미 706efb47로
  리셋됨)와 devnotes(여전히 60차 상태)가 서로 다른 시점을 가리키는 것을 16절 원칙대로
  발견해 사용자에게 보고, 승인 받은 뒤 devnotes 네 파일을 코드 브랜치의 실제 결과에
  맞춰 사후 동기화했다(코드 변경 없음, devnotes만).
- 이 시점부터 carrot-ryu에는 지금까지 쌓아온 커스텀 코드(36개 항목)가 전혀 없는 상태. 다음
  세션부터 carrot-ryu-v1의 "코드 수정 현황"을 체크리스트 삼아 서브시스템 단위로 하나씩
  재적용 시작 예정(20절 5번, 17절 원칙에 따라 여러 세션에 걸쳐 진행).
- 이식이 상당 부분 끝나기 전까지 콤마 디바이스 git pull 금지 상태 유지.

## 60차 (devnotes 오염 발견/복구, 코드 변경 없음) — HANDOFF.md/WIP_SYNC.md 히어스트링 오염 복구

- 세션 시작 4절 0단계(SHA 고정 조회) 중 devnotes/HANDOFF.md(59차분)에 WIP_SYNC.md 전체
  내용이 PowerShell 히어스트링 조각(`'@`, `$WipSyncContent = @'`)과 함께 이어붙어 있고,
  실제 devnotes/WIP_SYNC.md는 0바이트로 커밋되어 있음을 발견(16절 해당 사항으로 즉시 보고).
- 59차(또는 그 이전) 반영 스크립트가 여러 교체형 파일을 한 스크립트에 담는 과정에서
  히어스트링 종료 따옴표(`'@`) 처리에 문제가 있었던 것으로 추정.
- HANDOFF.md 안에 남아있던 WIP_SYNC 원문을 Python으로 바이트 단위 정확한 경계에서 추출,
  57~59차 체크포인트 포함 내용 손실 없이 복구 확인.
- HANDOFF.md는 정상 60차 내용으로 교체, WIP_SYNC.md는 복구 내용 + 60차 체크포인트로 복원.
- 20절 리셋(carrot-ms 베이스로 carrot-ryu 재생성) 착수 여부는 이번 세션에서 재확정되지
  않음, 다음 세션 최우선 이월.

## 58차 (분석만, 코드 변경 없음) — carrot-ms fork 이후 신규 25건 오래된순 1차 분류

- fork point(02015190f5) 이후 carrot-ms 신규 커밋 25건을 오래된 시간순으로 개별 조회, carrot-ryu 현재 코드와 직접 대조해 관련성·충돌 가능성을 1차 판정.
- 3건 제외 확정: 8dcd32f7(sensord, tizi 전용 무관), ce8cbffe(C3XL 팬제어, C3X 전용 무관), 9d50f986(CI/문서 링크체크 툴링, 우리 워크플로우와 무관).
- 1건 반영 후보 확정: 6f63ad35(외부내비 우선 로직) — 관련 함수 전부 carrot-ryu에서 fork 시점과 동일함을 확인해 충돌 없음, 기능적으로도 직접 관련. 실제 반영은 사용자 의도(동시사용 원하는지) 확인 후 진행.
- 나머지 21건을 3개 고위험 클러스터로 분류: (A) 종방향 gap/lead-response 대개편 10건 — carrot-ryu가 fork 이후 독자적으로 같은 영역을 재설계해 와서 병행 발전 충돌 위험 높음. (B) 현대/제네시스 CAN 상태 2건. (C) Cinque v2 eGPU 모델 3건 — carrot-ryu 자체 eGPU 커밋과 병행 발전 가능성. 저위험 설정값/Web UI 3건은 개별 대조만 남음. 빌드 인프라 2건(acados/json11·Catch2 패키지화)은 별도 판단 필요.
- 상세 판정 근거와 각 클러스터 소속 커밋 해시는 WIP_SYNC.md 58차 체크포인트 참고.
- 실차 검증: 미실시(코드 변경 없음, 12절).## 57차 (설계 논의만, 코드 변경 없음) -- carrot-ms 동기화 분석 범위 재설정

- 사용자 요청: "carrot-ms 모델셀렉터 분석 착수".
- 41개 모델셀렉터 전용 커밋(carrot-wip/carrot-ms bare clone 비교로 특정)을 git merge-base --is-ancestor로 전수 검증한 결과, 전부 carrot-ryu fork point(02015190f5, 6~7차 체크포인트)의 조상 -> 이미 반영돼 있어 신규 작업 불필요함을 확인.
- carrot-ryu의 carrot/model_selector/ 코드가 fork 이후 무수정, upstream 침습 지점/파람 등록 전부 정상임을 직접 확인.
- 사용자가 이 결과를 듣고 분석 범위를 재설정: "모델셀렉터 코드뿐 아니라, carrot-ryu 브랜치 만든 이후 생긴 커밋은 다 분석해서 필요없는 커밋은 제외하고, 우리 차에 필요한 커밋만 추려서 우리가 수정한 코드와 충돌은 없는지 확인" -> fork point 이후 carrot-ms 신규 커밋 25건 전체를 대상으로 확대.
- 다음 세션 작업 순서: (1) 25건 필요 여부 선별 (2) 필요한 것만 diff 분석 (3) carrot-ryu 커스텀 코드와 충돌/상충 여부 확인. 이번 세션은 이 설계까지만, 실제 분석은 이월.
- 부수 발견: CURRENT_STATUS.md 항목 36(55차) 표기가 실제 push 상태(9ccf1206)와 어긋나 있었음. 상세: HANDOFF.md 57차 참고.
## 56차 (완료, 코드 변경 없음) -- 55차 스크린샷 상하반전 수정 실차검증

- 사용자가 스크린샷 버튼으로 실기기에서 촬영한 이미지 1장(HYUNDAI_GENESIS(CAMERA SCC) 온로드 HUD, 16:59:49 09-16(수))을 제공하며 "정상됨"이라고 확인.
- 이미지를 직접 확인해 55차 `rl.image_flip_vertical()` 수정 이후 상하반전 없이 정방향으로 저장됨을 실차 검증(12절)으로 확정.
- 같은 이미지에 border HUD 요소(차량명/시계/날짜/LD·LT·SR/laneless/git branch/IP), CPU·MEM·DISK, 속도/기어/LIMIT까지 전부 정상 포함돼 있어, 54차 render-texture 재설계 항목(border HUD 누락/480p/PNG)도 함께 재확인됨.
- 49~55차에 걸쳐 순차 수정해온 스크린샷 관련 이슈(HUD 누락 -> DPI 반전 -> 캡처 타이밍 -> 상하반전)가 이 확인으로 전부 해소됨.
- 코드 변경 없음(carrot-ryu HEAD는 55차 `e047beb3` 그대로 유지). devnotes만 갱신.
- 다음 작업 우선순위는 사용자 확인 필요(이월 목록: 핵심 발견 31/37 9절 정식반영, 37차 락 동시성 재현, 34차 도로명-신호과속 배치, 28~30차 재검증, 선택 다운로드 동작, 데드코드 삭제, docs 갱신, carrot-ms 모델셀렉터 분석).

## 55차 (코드 완료, push 대기) -- 54차 render-texture 스크린샷의 상하반전 버그 원인 확정/수정

- 사용자가 54차 render-texture 재사용 스크린샷 캡처를 실기기에서 테스트한 결과, 480p 다운스케일/PNG 저장은 정상이었으나 이미지가 상하반전으로 저장된다고 제보(스크린샷 첨부).
- application.py 코드 조사로 원인 확정(추측 아님, 11절): 영상 녹화 경로(카메라/화면 인코딩 2곳)는 ffmpeg `-vf vflip`으로 OpenGL render texture의 아래->위 픽셀 순서를 이미 보정하고 있었으나, 54차가 스크린샷 캡처를 `rl.load_image_from_screen()`(보정 불필요)에서 `rl.load_image_from_texture()`(보정 필요)로 바꿀 때 이 vflip 보정을 옮겨오지 않았음.
- `screenshot_capture.py`의 `save_screenshot_image()` 맨 앞에 `rl.image_flip_vertical(image)` 한 줄 추가(Replace-Block, anchor 1회 매치 확인). 다른 파일은 손대지 않음(10절).
- 사용자가 Termux 환경임을 명시해 bash 스크립트로 전달(9절, 51차와 동일 패턴).
- 실차 검증: 미실시(다음 세션 최우선 -- 상하반전 해소 여부만 확인하면 됨).

## 54차 (코드 완료, push 완료) -- render-texture 재사용 스크린샷 캡처 재설계 구현 + push/반영 검증, Windows python3 미탐지로 인한 py_compile 무출력 실패 진단/수정

- 53차에서 합의된 설계를 그대로 구현. 반영 스크립트 작성 직전 carrot-ryu 최신 원본(HEAD `e4816edc`)을 다시 조회해 그 위에서 Replace-Block anchor를 구성(6절).
- `application.py`(공통 파일, `openpilot/system/ui/lib/`)에 `request_temp_capture(callback)` 신규 메서드를 3개 지점에 추가: (1) `__init__` 끝에 pending 플래그/콜백/텍스처 소유 플래그 초기화 + 메서드 정의, (2) 렌더 루프 시작 시 pending 캡처가 있고 `self._render_texture`가 없으면 기존 `_ensure_render_texture_for_recording()`으로 그 프레임만 임시 texture 생성, (3) `end_texture_mode()` 이후 녹화 프레임 추출과 동일한 지점에서 `rl.load_image_from_texture()`로 추출 후 콜백 호출, 임시로 만든 texture라면 즉시 해제. selfdrive 코드 import 없이 제네릭 유지(기존 레이어링 규칙, 10절).
- `screenshot_capture.py`를 `capture_onroad_screenshot()` -> `save_screenshot_image(image: rl.Image)`로 전체 재작성 -- 이제 화면을 직접 읽지 않고, 이미 캡처된 이미지를 받아 480p(세로기준) 다운스케일 + PNG export만 담당(51·50차 로직 그대로 이식).
- `screenshot_button.py`를 전체 재작성 -- `_on_click()`이 `gui_app.request_temp_capture(self._on_frame_captured)`만 호출하도록 단순화, pending 플래그/consume 로직 완전 제거.
- `hud_renderer.py`에서 `consume_pending_screenshot_capture()` 제거(더 이상 캡처 소비를 위임받을 필요 없음).
- `augmented_road_view.py`에서 51·52차가 추가했던 `capture_onroad_screenshot` import 및 프레임 끝 호출부 원복.
- **최초 반영 스크립트 실행 시 이상 현상**: py_compile 검증 단계에서 어떤 에러 텍스트도 출력되지 않은 채 `[중단] py_compile 실패: application.py`로 끝남(commit/push는 안전하게 안 됨 -- 스크립트의 방어 로직 자체는 의도대로 동작). 코드 문제인지 환경 문제인지 구분하기 위해, 동일한 3개 Replace-Block을 Linux sandbox에서 그대로 재현해 `python3 -m py_compile` 실행 -> **정상 통과(exit 0)** 확인. `Callable`도 파일에 이미 `from collections.abc import Callable, Iterable`로 import돼 있음을 확인해, 반영된 코드 자체에는 결함이 없음을 확정(11절: 추측 대신 재현으로 확인).
- 원인은 Windows PC의 `python3` 명령으로 추정(핵심 발견 37): python.org 설치본은 보통 `python.exe`/`py.exe`(런처)만 PATH에 등록하고 `python3.exe`는 없는 경우가 흔한데, 이 상태에서 `python3`를 호출하면 Windows 10/11의 앱 실행 별칭(Microsoft Store 유도 스텁)이 가로채 콘솔 출력 없이 조용히 실패함 -- 로그에 파이썬 에러가 한 줄도 안 찍힌 정황과 정확히 일치.
- 대응: 반영 스크립트에 `Get-PythonCmd` 함수를 추가해 `py -3` -> `python3` -> `python` 순으로 실제 `--version` 출력이 나오는 후보를 자동탐지해 py_compile 호출에 사용하도록 방어적으로 수정. 나머지 5개 파일 반영 내용은 원본과 100% 동일. 같은 세션 내 재작성이므로 9절 버전표시 규칙에 따라 파일명에 `-v2` 부여.
- 사용자가 `54cha_code_carrot_ryu-v2.ps1` 실행 -> `(python 실행 파일 감지: ...)` 로그와 함께 py_compile 전체 통과 -> `git push` 로그(`e4816edc..e047beb3 carrot-ryu -> carrot-ryu`)로 커밋/push 성공 확인.
- push 후 검증 시퀀스(6절/16절) 전체 수행: `git ls-remote`로 실제 HEAD가 `e047beb3`임을 재확인 -> SHA 고정 raw URL로 5개 파일 전체 재조회 -> 5개 파일 전부 `python3 -m py_compile` 재통과 -> grep으로 `application.py`의 `request_temp_capture`/`_temp_capture_pending`/`_temp_capture_owns_texture` 존재, `screenshot_capture.py`의 `save_screenshot_image` 존재, `screenshot_button.py`의 `gui_app.request_temp_capture()` 호출 존재, `hud_renderer.py`의 `consume_pending_screenshot_capture` 0건(완전 제거), `augmented_road_view.py`의 `capture_onroad_screenshot` 0건(완전 제거)까지 확인 -- 실제 반영 내용이 설계·의도와 정확히 일치함을 실증.
- devnotes(WIP.md/HANDOFF.md/CURRENT_STATUS.md) 갱신, 핵심 발견 37로 이번 진단 과정 기록.
- 실차 검증: 미실시(다음 세션 최우선 -- 스크린샷 버튼으로 border HUD(차량명/시계/LD·LT·SR/laneless/git branch/IP) 전부가 포함되는지, 480p 다운스케일과 PNG 저장이 정상 동작하는지 확인. 49~52차/47차/51차의 개별 이월 항목들은 구조가 완전히 바뀌었으므로 이번 한 번의 실차 테스트로 함께 흡수해 확인).


## 53차 (설계 논의만, 코드 변경 없음) -- 스크린샷 캡처 근본 재설계 방향 합의: 녹화 프레임 추출 로직 재사용

- 세션 시작 시 지침 문서 4절 0단계 확인 후 체크포인트: `git ls-remote`로 carrot-ryu HEAD가 `e4816edc`(52차, 커밋 메시지 "52cha: move screenshot capture trigger to end of AugmentedRoadView frame..."로 확정)임을 확인 -- 사용자가 52차 반영 스크립트를 이미 실행해 push까지 완료했음이 실증됨. 바로 위 "52차 (코드 완료, push 대기)" 항목은 그 시점 기준 표기이며 7절 규칙상 수정하지 않고 그대로 둠 -- 실제로는 이미 push 완료 상태였고, devnotes(WIP/HANDOFF/CURRENT_STATUS) 갱신이 그 사이 세션 종료로 누락된 것(16절/핵심 발견 27과 동일 패턴). carrot-ryu-note HEAD(`57062bb1`)는 체크포인트 전후로 변화 없음(HANDOFF 본문 안의 "이전 base" 참조 텍스트를 현재 HEAD로 순간 오인했으나, 재확인 결과 착오였음을 세션 내에서 스스로 정정).
- 52차 수정(캡처 호출을 AugmentedRoadView._render() 끝, `_draw_border_carrot()` 다음으로 이동) 이후에도 실기기에서 여전히 border 관련 HUD(차량명/시계/LD·LT·SR/laneless/git branch/IP)가 캡처에서 빠지는 문제가 계속된다는 전제로, 화면녹화(정상)와 스크린샷(계속 실패)의 구조적 차이를 `application.py` 코드로 직접 대조:
  - 녹화 중에는 위젯 트리 전체를 화면에 직접 그리지 않고 오프스크린 render texture에 그린 뒤(`begin_texture_mode()`~`end_texture_mode()`), `end_texture_mode()` 호출 뒤(그 프레임의 모든 내용이 텍스처에 확실히 다 쓰인 시점)에 `rl.load_image_from_texture()`로 읽는다 -- 순서가 구조적으로 보장됨.
  - 스크린샷은 녹화 중이 아닐 때 render texture 자체가 없는 상태에서, 위젯 렌더 콜백 한가운데(51·52차가 호출 위치를 옮겨도 여전히 프레임이 완성되기 전)에 `rl.load_image_from_screen()`으로 화면을 직접 읽어 raylib 배치 플러시 타이밍에 구조적으로 취약함.
- 해결 방향으로 "스크린샷 버튼을 누르면 녹화 로직으로 딱 1프레임만 떠서 이미지로 저장"(사용자 제안, 가장 실질적인 구현)에 합의. 구체 설계:
  1. `GuiApplication`에 스크린샷 pending 플래그(예: `request_screenshot()`) 추가.
  2. 렌더 루프 시작 시, pending 스크린샷이 있고 현재 녹화 중이 아니어서 `self._render_texture`가 없으면, 기존 `_ensure_render_texture_for_recording()`과 같은 패턴으로 그 프레임만 임시 render texture 생성 -- 자동으로 녹화와 동일한 `begin_texture_mode()` 경로를 타게 됨.
  3. `end_texture_mode()` 직후(녹화가 프레임을 추출하는 지점과 정확히 동일한 위치)에서 pending 스크린샷이 있으면 `rl.load_image_from_texture()`로 해당 프레임을 가져와, 기존 `screenshot_capture.py`의 480p 다운스케일+`export_image` 로직을 그대로 재사용해 저장.
  4. 이미 녹화 중일 때 스크린샷 버튼을 누른 경우는 별도 텍스처 생성 없이 같은 프레임을 한 번 더 추출.
  5. 스크린샷 때문에 임시로 만든 render texture는, 녹화 중이 아니라면 캡처 직후(다음 프레임 시작 전) `unload_render_texture()`로 정리 -- 평소엔 화면에 직접 그리는 기존 경로 유지, 스크린샷 순간에만 텍스처 경로로 잠깐 전환.
- 이 설계는 51·52차보다 범위가 넓어(공통 파일 `application.py` 포함) 사용자에게 진행 여부를 물었고, 사용자가 다음 세션에 구현하기로 결정 -- 이번 세션은 코드 변경 없이 설계 합의까지만 진행. 51·52차가 수정한 `augmented_road_view.py`의 캡처 호출부는 다음 세션 구현 시 되돌릴 예정.
- 실차 검증: 미실시(코드 변경 자체가 없었음).


## 52차 (코드 완료, push 대기) -- 스크린샷에서 여전히 빠지는 HUD(차량명/디버그/laneless/IP 등) 원인 확정 + 수정

사용자가 51차 반영 후 실기기 사진 2장(스크린샷 결과물 1장, 실기기 직접 촬영 1장)을 제공하며 처음엔 "오른쪽 HUD가 안 나온다"고 했다가 "오른쪽이 아니라 화면 전체가 다 안 나온다"고 정정.

- 두 사진을 비교: 스크린샷에는 hud_renderer.py가 그리는 CPU/MEM/VOLT 박스, 우측 "교차로" 경로안내 박스, 플롯 디버그(1.Accel...)는 정상 포함돼 있었으나, 차량명("HYUNDAI_GENESIS(CAMERA SCC)"), 좌상단 시계, 우상단 LD/LT/SR 디버그, 하단 laneless 상태 텍스트, git branch, IP 주소는 전부 빠져 있음을 확인.
- 코드 조사(augmented_road_view.py)로 원인 확정: AugmentedRoadView._render()가 self._hud_renderer.render(rect)를 먼저 호출하고, 그 다음에 alert_renderer.render(), driver_state_renderer.render(), 마지막으로 self._draw_border_carrot(rect)(차량명/LD·LT·SR/laneless/git branch/IP 텍스트를 실제로 그리는 곳)를 호출함. 51차는 HudRenderer *내부*의 그리기 순서만 고쳤을 뿐, 캡처 호출(consume_pending_capture → capture_onroad_screenshot) 자체가 여전히 hud_renderer.render() 안에 있어서, 이 호출 시점엔 border 텍스트와 alert/driver-state 오버레이가 아직 그려지기 전이었음(11절: 코드로 확정, 추측 아님).
- 수정: capture_onroad_screenshot() 호출을 HudRenderer._render() 밖으로 빼서 AugmentedRoadView._render()의 맨 끝(self._draw_border_carrot(rect) 다음)으로 옮김. HudRenderer는 대기 플래그를 소비만 하는 공개 메서드 consume_pending_screenshot_capture()를 새로 노출.
- 수정 파일 3개: hud_renderer.py(캡처 호출 제거 + 공개 메서드 추가 + import 정리), augmented_road_view.py(import 추가 + 프레임 끝 캡처 호출 추가), screenshot_button.py(클래스 docstring을 새 구조에 맞게 갱신, 18절).
- 실제 GitHub 최신 코드(git clone)로 anchor 5곳 모두 정확히 1회 매치 확인 후 교체, py_compile 통과 확인(6절: 스크립트 작성 직전 최신 원본 기준으로 구성).
- 실차 검증: 미실시. 다음 세션 최우선 -- 차량명/시계/LD·LT·SR/laneless/IP가 이번에는 전부 캡처에 포함되는지 확인.

## 51차 (코드 완료, push 대기) -- 스크린샷 캡처 타이밍 버그(시계/온도 HUD 누락) 수정 + 480p 다운스케일

사용자가 50차 PNG 롤백 실차 결과 사진 2장(HUD 없는 순수 배경 스크린샷 1장, carrotweb 로그탭에 파일이 실제로 잡힌 화면 1장)을 제공하며 "캡쳐는 되는데 시간/온도 UI가 안 나온다, 480p로 낮춰달라, Termux로 달라"고 요청.

- git ls-remote로 carrot-ryu HEAD 08c7e9ae7964... 확인 -- 50차 PNG 롤백이 이미 push 완료됐고 실제로 export가 성공하고 있음을 실증(50차 미완료 1,2번 해소).
- hud_renderer.py _render()에서 스크린샷 버튼 render()(클릭 처리 포함)가 _draw_date_time/_draw_tpms/_draw_egpu_badge/_draw_cruise_speed_animation보다 먼저 호출됨을 코드로 확인 -- 클릭 시점에 즉시 rl.load_image_from_screen()으로 캡처하면 이 프레임의 나머지 HUD가 아직 안 그려진 상태라 빠지는 것이 사용자 제보 사진과 일치함을 확정.
- 수정: _on_click()은 pending 플래그만 세우고, _render() 맨 끝에서 그 플래그를 소비해 캡처를 실행하도록 이동(screenshot_button.py + hud_renderer.py).
- screenshot_capture.py에 rl.image_resize() 기반 480p(세로 기준) 다운스케일 추가.
- 사용자가 이번 세션에서 Termux 사용을 명시 -> PowerShell 대신 bash 스크립트로 작성(9절).
- py_compile 통과, hud_renderer.py 앵커 2곳 1회 매치 확인(스크립트 자체 검증 포함).
- 실차 검증: 미실시(다음 세션 최우선 -- 시계/온도 포함 여부, 480p 다운스케일 실제 동작 여부).

## 50차 (코드 완료, push 대기) -- 49차 진단 로그 실차 분석 + JPG export 실패 원인 좁힘 + PNG 롤백

사용자가 49차 반영 스크립트를 이미 실행했고(git pull 41fd34a74..dfdbfff9a, reboot 로그 확인), 실기기 swaglog grep 결과와 스크린샷 버튼 위치 확인 사진을 제공.

- `git ls-remote`로 carrot-ryu HEAD `dfdbfff9a7df48aac869b1417ea6398dd6768f32`(49차) 확인 -- 49차 미완료 1번 해소.
- swaglog grep(git pull 전/후 구간)을 분석: git pull 이후 매 실패마다 `screenshot_button.py:28 _on_click`에서 `capture_onroad_screenshot: export_image failed for ...` 경고가 raylib `Failed to export image` 경고와 함께 찍힘 -> `_on_click()`->`capture_onroad_screenshot()` 호출, `load_image_from_screen()` 성공까지는 실증(11절, 로그 근거) -- 클릭 전달 문제 가설 배제.
- 실패 지점을 `rl.export_image()` 자체로 좁힘. git pull 이전(47차)에도 동일 실패가 있었던 점, 46차까지 PNG는 저장에 성공했던 점을 근거로 "JPG export가 이 기기 raylib 빌드(comma-deps-raylib==6.0.0.1.post101)에서 지원되지 않는다"를 유력 가설로 제시(확정 아님, DPI수정과 확장자변경이 47차에 같이 들어가 변수 미분리).
- 사용자가 스크린샷 버튼 위치가 의도한 대로 이동됐음을 실기기 촬영 사진으로 확인 -- 49차 미완료 3번 해소.
- 변수 분리를 위해 screenshot_capture.py 저장 확장자만 `.jpg` -> `.png`로 롤백(load_image_from_screen() DPI 수정은 유지). Replace-Block 앵커 1회 매치 확인(9절).
- 실차 검증: 미실시(PNG 롤백 후 저장 성공 여부가 다음 세션 최우선).



## 49차 (코드 완료, push 대기) -- 스크린샷 버튼 무반응 진단 로그 추가 + 버튼 위치 사용자 요청 반영

사용자가 실기기 스크린샷 2장(정상 캡처 예시, 실제 로그탭 화면 -- 목록에 사진 0건/영상 3건)을 제공하며 "스크린샷 버튼이 안 눌러지고 로그탭에 저장되지 않음" 제보 + "사진캡쳐버튼을 참고 사진의 빨간색 동그라미 위치로 이동" 요청.

**증거**: 로그탭 스크린샷에서 목록의 항목 3개가 전부 MP4(화면녹화)이고 JPG(사진)가 하나도 없음 -- 스크린샷 저장이 실제로 0건이라는 뜻이라 제보와 일치.

**코드 조사**: click 처리 로직(`Widget._process_mouse_events`), `capture_onroad_screenshot()`(47차 버전), pyray 바인딩(`uv.lock`에 고정된 `comma-deps-raylib==6.0.0.1.post101`을 sandbox에 실제 설치해 `load_image_from_screen`/`export_image` 존재 확인) 어디에서도 명백한 버그를 못 찾음. 11절 원칙(추측만으로 원인을 확정하지 않음)에 따라, 원인 확정 대신 다음 실차 테스트에서 원인이 드러나도록 진단 로그를 추가:
1. `screenshot_capture.py`: 3개 실패 분기(캡처 크기 이상/`export_image` 실패/파일 생성 실패)와 예외 처리에 `cloudlog.warning`/`cloudlog.exception` 추가.
2. `screenshot_button.py`: `_on_click`에 `cloudlog.debug("ScreenshotButton clicked")` 추가 -- 클릭 자체가 콜백까지 도달하는지, 캡처만 실패하는지 다음 실차 테스트에서 구분 가능.

**버튼 위치 변경**: `hud_renderer.py`에서 스크린샷(카메라) 버튼을 화면 중앙(기존 자리, `anchor_x`로 명명)에서 좌측으로 버튼 한 칸(140px 폭 + 30px 간격 = 170px) 이동. record 버튼 위치는 `anchor_x` 기준 수식이 이전과 동일해 절대 위치 그대로 유지.

**검증**: `py_compile`/`ast.parse` 3개 파일 모두 통과. Replace-Block 방식으로 `hud_renderer.py` 변경 전 블록이 파일 전체에서 정확히 1회 매치함을 Python으로 확인(9절). `cloudlog.debug/warning/exception`이 `SwagLogger`(`logging.Logger` 서브클래스)의 표준 메서드임을 `common/logging_extra.py` 소스로 확인(추측 아님, 11절).

**실차 검증**: 미실시 -- 이번 세션은 "원인 확정"이 아니라 "다음 테스트에서 원인이 보이게 만드는" 진단 단계(11절). 버튼 위치 변경도 실기기 확인 전.

상세: FINDINGS.md 2026-09-16(49차) 항목, 핵심 발견 34. HANDOFF.md 49차 참고.

## 48차 (검증 완료) — 47차 push 확인 + 36차/39차/37차 이월 항목 실기기 검증

사용자가 "체크포인트"를 요청. 4절 0단계(`git ls-remote`로 carrot-ryu-note SHA 고정 조회)부터 시작.

- `git ls-remote`로 carrot-ryu HEAD를 확인한 결과 `41fd34a7458d663d27e16d96fbeb2c6bcb20c1b5`(47차 스크린샷 DPI/JPG 수정)로 이미 push돼 있음을 확인. GitHub commit API로 커밋 메시지("47cha: fix screenshot DPI-scale portrait bug, save as jpg")와 변경 파일(`openpilot/selfdrive/ui/onroad/screenshot_capture.py` 1개)을 확인하고, raw.githubusercontent.com(SHA 고정)으로 파일 실제 내용을 재조회해 `rl.load_image_from_screen()` + `.jpg` export가 계획대로 반영됐음을 재확인. 47차 HANDOFF 미완료 1번이 세션 사이에 해소됨.
- 사용자가 제공한 실기기 스크린샷 7장(로그 전송 확인창 2장, HUD 디바이스 직접촬영 1장, 로그탭 화면녹화/사진 목록 2장, 구글드라이브 폴더·파일 목록 2장)으로 아래 이월 항목들을 실기기 검증:
  1. Issue 1(당근서버 라벨 오표시, 36차): 로그 전송 확인창에 "구글 드라이브"로 정확히 표시됨 -- 정상 확인.
  2. Issue 3(햄버거 메뉴 탭 무관 업로드, 36차): 화면녹화/로그 탭에서 탭 전용 선택-전송 UI(체크박스 + "선택 전송")가 정상 동작 -- 정상 확인.
  3. 39차/46차에서 미확인이던 "선택 전송" 버튼의 실제 전송 성공 여부: 사진/영상 3개 항목 체크 후 전송하는 흐름을 확인했고, 구글드라이브 "CarrotWeb Logs" 폴더에 해당 타임스탬프 mp4 파일(`20260916-111847.mp4` 등)이 실제로 존재함을 확인 -- 전송 성공까지 실증됨. (단, "선택 다운로드" 버튼 동작은 이번에도 확인 안 됨, 이월.)
  4. Issue 4(Drive 폴더 중복생성, 37차 락 수정): 구글드라이브 루트에 "CarrotWeb Logs" 폴더가 1개만 존재함을 재확인 -- 정상.
  5. 27차 HUD 경로안내 박스: 디바이스 화면 직접촬영 사진에서 레이아웃(교차로/회전아이콘/route=/도착거리/ETA/도로명)이 정상임을 재확인.
- 코드 변경 없음(전부 검증/문서화 세션). devnotes(WIP.md/CURRENT_STATUS.md/HANDOFF.md)만 갱신.
- 다음 세션 최우선 이월: 47차 스크린샷 수정 자체의 실차 검증(스크린샷 버튼을 실제로 눌러 가로 2160x1080 JPG로 저장되는지, 용량, 목록 표시 확인) -- 아직 확인 안 됨.

## 47차 (코드 완료, push 대기) -- 스크린샷 캡처 세로 뒤바뀜/과대용량 원인수정

사용자가 정상 캡처 예시(가로 2160x1080)와 실제 저장된 사진(세로 1080x2160, 상단 대부분 검정, 용량도 4배가량 큼) 두 장을 제공하며 버그 제보.

1. **원인**: `screenshot_capture.py`의 `rl.take_screenshot()`이 raylib 내부에서 `render 크기 * GetWindowScaleDPI()`로 캡처 크기를 계산하는데, 이 기기에서 DPI 스케일이 비등방으로 나와 가로/세로가 뒤바뀐 채 저장됨. 제공받은 두 이미지의 실제 픽셀 크기(2160x1080 vs 1080x2160)를 직접 확인해 실증.
2. **수정**: `rl.load_image_from_screen()`으로 교체(DPI 배율 계산 없이 논리적 화면 크기로 프레임버퍼를 그대로 읽음 -- 영상 녹화 파이프라인이 이미 쓰고 있는 "DPI 우회" 방식과 동일 원리, 46차에서 실차 검증된 접근).
3. **겸사겸사**: 저장 포맷을 PNG -> JPG로 전환(사진 용량 축소). `SCREEN_RECORDING_PHOTO_EXTS`에 `.jpg`/`.jpeg`가 이미 등록돼 있어 백엔드/프론트엔드 추가 수정 불필요함을 코드 조사로 확인.
4. `py_compile` 통과 + sandbox에 pyray를 별도 설치해 `export_image`의 JPG 저장 자체가 정상 동작함을 headless로 확인(실제 화면 렌더 검증은 아님).
5. carrot-ryu(코드, 전면 교체 방식) + carrot-ryu-note(devnotes) 반영 스크립트 작성, 둘 다 실행 대기. 실차 검증은 다음 세션 최우선 이월.

상세: FINDINGS.md 2026-09-16(47차) 항목, 핵심 발견 33. HANDOFF.md 47차 참고.

## 46차 (완료 -- HEAD 99b49a1 실기기 검증 4건, 최우선 이월 항목 전부 해소) -- 45차 배포분 실기기 검증

사용자가 제공한 스크린샷 2장(도구 탭 git pull 로그, 로그 탭 사진목록 화면)과 영상 1개(20260916-095343.mp4, 온로드 화면 4초 분량)로 HANDOFF.md 최우선 이월 1~4번을 전부 실기기 검증 완료.

1. **carrot-ryu HEAD(99b49a1) 실기기 배포 확인**: 도구 탭 로그에 실제 git pull 출력이 캡처됨 -- "Updating e2f356198..99b49a113", "Fast-forward", 변경 파일 ".../carrot/web/generated/asset-manifest.json"(2줄)/".../selfdrive/carrot/web/js/generated/logs.js"(32줄) 정확히 일치, 이어서 reboot 실행까지 로그로 확인. 45차 최종본이 실기기에 실제로 반영/재부팅됐음이 최초로 실증됨(45차-정정까지는 "미실시"였음).
2. **사진 목록 크래시 해소 확인(44/45차 formatLogBytes)**: 재부팅 후 로그 탭 스크린샷에서 사진 목록이 정상 렌더되고, 파일 크기가 "2.2 MB"/"2.3 MB"로 정확히 포맷되어 나옴(formatLogBytes가 실제로 호출/동작하는 증거). 체크박스/다운로드/전송 아이콘 정상.
3. **delete_all_videos 스크린샷 폴더 포함 확인(44차)**: 사용자가 실기기에서 전체 삭제 시 사진까지 삭제됨을 확인(사용자 보고).
4. **로그탭 새로고침 아이콘 확인(41차)**: 에러 없이 동작하며, 실제로 목록이 갱신됨을 사용자가 확인(사용자 보고). 41차 이월 항목 완료.
5. **녹화 버튼 깜빡임 확인(44차 3번, 정량 분석)**: 영상을 6fps(24프레임)로 추출, 버튼 좌표(원본 해상도 2160x1080 기준 x:1212-1288, y:912-988)를 색상 필터로 특정한 뒤 프레임별 평균 RGB를 측정. 밝은 상태(R≈193, 평균밝기≈99)와 어두운 상태(R≈33, 평균밝기≈34)가 프레임마다 규칙적으로 교대됨을 확인 -- 이전 세션(1.8초 영상, 정지 프레임 육안 비교)에서는 판단 불가였던 것을, 버튼 영역 크롭+수치 비교로 명확히 실증함(핵심 발견 32 참고).

이로써 HANDOFF.md의 "최우선" 이월 항목(1~4번)이 전부 해소됨. 남은 이월 항목(37차 락 동시성 재현, 34차 도로명-신호과속 같은 줄 배치, 28~30차 레이아웃 정밀 재검증, 나머지 코드 변경 전부 실차 재검증, tools.js 실기기 확인, 데드코드/테스트 정리, docs 갱신, carrot-ms 모델 셀렉터 분석, 핵심 발견 31 재발방지 제안 채택 여부)은 계속 이월.

검증: 실기기 스크린샷 2장 + 실기기 촬영 영상 1개(사용자 제공) 근거. 코드 변경 없음(devnotes만 갱신).

## 핵심 발견 31 (45차-정정) -- carrot-ryu-note에 반영된 45차 devnotes가 최종본이 아닌 중간 초안이었음 (코드는 최종본대로 정상 반영/검증됨)

바로 아래 "45차" WIP 항목(및 FINDINGS/HANDOFF의 45차 기록)은 실제로 이번 세션에서 push된 것이 맞지만, Linux sandbox 재빌드로 전환하기 *이전* 단계 -- 즉 사용자 PC에서 `npm install && node build.mjs`를 직접 실행하려던 1차 시도(`45cha_rebuild_bundle_carrot_ryu.ps1`, 예상 밖 diff ~25개 파일로 안전 중단됨) 시점 기준의 중간 초안 내용이다.

실제로는 그 이후 Linux sandbox 빌드로 전환한 최종 스크립트(`45cha_apply_bundle_carrot_ryu.ps1`)가 별도로 만들어져 carrot-ryu에 정상 push/검증까지 완료됐다(commit `99b49a113e48ddaeebf83074b04e42d417a88612`, `js/generated/logs.js` sha256 `9236a3838ecae5b81ef147c03a3b26f87ff1e15d738a159b4905b530acc49cbd` 일치, `node --test` 737/737 통과, 커밋 메시지에 CRLF/npm allow-scripts 가설 기각 및 esbuild 플랫폼 비결정성 결론까지 정확히 기록됨).

문제는 같은 세션에서 devnotes 반영용으로 준비했던 최종 스크립트(파일명 `45cha_devnotes_carrot_ryu_note.ps1`)가 아니라, 그보다 먼저 만들어졌던 동일 파일명의 중간 초안이 사용자 PC에서 실행되어 push됐다는 점이다. 두 버전의 커밋 메시지("bundle-not-rebuilt root cause + rebuild fix" vs 최종본의 "carrotweb 번들 재빌드 크로스플랫폼 비결정성 진단/우회 기록")와 HANDOFF.md Worker 라인이 서로 완전히 다름을 직접 바이트 비교로 확인했다.

원인 추정(직접 재현은 못 함): 한 세션 안에서 devnotes 스크립트를 같은 파일명으로 두 번(중간 초안 -> 최종본) 전달했고, 사용자 PC의 Downloads 폴더에 이미 이전 버전이 남아있어 최종본이 다른 이름으로 저장됐거나, 재실행 시 이전 로컬 파일이 그대로 실행됐을 가능성이 높다.

부가 확인: 검증 과정에서 `git clone --depth 1` 뒤 `git show --stat HEAD`를 실행하면 부모 커밋이 로컬에 없어 빈 트리 대비 diff로 처리되어(grafted root 취급) devnotes 폴더의 무관한 파일들까지 대량으로 나열되는 착시가 있었다 -- 이는 실제 이상 징후가 아니라 shallow clone의 부작용이며, `--depth 5` 이상(부모 포함)으로 다시 확인해 배제했다.

재발 방지 제안(승인 시 지침 문서에 규칙으로 추가 검토): 한 세션 안에서 같은 대상에 대해 스크립트를 다시 만들 때는 파일명에 버전 표시(-v2, -final 등)를 붙여 Downloads 폴더의 이전 로컬 파일과 절대 겹치지 않게 한다.

부가 수정: 이번 검증 중 WIP.md 파일 맨 앞에 있어야 할 "# WIP" 타이틀 헤더가 실제로는 없는 상태임을 발견(FINDINGS.md는 "# FINDINGS" 헤더가 정상적으로 파일 맨 앞에 있는 것과 대조됨 -- 언제부터 이랬는지는 확인 못 함, 과거 어느 세션의 스크립트가 anchor 매칭에 실패한 채로 다른 위치에 텍스트를 삽입했을 가능성). 과거 devnotes 반영 스크립트들이 "# WIP`n`n" 앵커로 매칭했던 것은 사실 파일 맨 앞이 아니라 본문 중 이 앵커 기법 자체를 설명하는 텍스트(과거 세션 기록) 안의 우연한 일치였을 가능성이 있음 -- 다만 그 경우에도 매치 수가 정확히 1이었으므로 항목이 엉뚱한 위치에 삽입되지는 않았을 것으로 추정(직접 재현 확인은 못 함). 이 커밋에서 "# WIP" 헤더를 파일 맨 앞에 복원함.

## 45차 -- 44차 소스 수정은 맞았으나 생성 번들(js/generated/logs.js)이 재생성되지 않아 크래시가 실기기에 그대로 남아있던 문제 발견/수정

사용자가 44차 스크립트 실행 후에도 실기기에서 `formatLogBytes is not defined`가 그대로 재현된다고 제보. GitHub의 carrot-ryu HEAD(commit e2f35619, 44차)를 직접 조회해 보니 `screenshots.js` 소스에는 `formatLogBytes` import가 정상적으로 추가돼 있었지만, 같이 커밋된 `js/generated/logs.js` 번들 안에는 `formatLogBytes` 함수 정의가 없고 호출부만 미해석 외부 참조로 그대로 남아있음을 확인(esbuild가 번들링/이름축약을 못 하고 원문 그대로 남겨둔 상태 -- 정상적으로 번들되면 다른 로컬 함수들처럼 짧은 이름으로 축약되어 원문에 `formatLogBytes` 리터럴이 아예 남지 않아야 함). 즉 44차 세션이 소스 파일은 정확히 고쳤지만, 그 위에서 `npm install && node build.mjs`를 실행해 생성 번들을 다시 만드는 단계를 건너뛴 채 예전(깨진) 번들 그대로 커밋한 것이 원인.

동일 소스로 직접 `npm install && node build.mjs`를 실행해 재현: 재생성된 번들에서는 `formatLogBytes` 호출부가 로컬 함수와 정상적으로 결합/축약되어(리터럴 `formatLogBytes` 문자열이 0회로 사라짐, 축약된 다른 로컬 함수들과 동일 패턴), `node --test tests/**/*.test.mjs` 737/737 통과 확인. 재생성 전후 diff는 `js/generated/logs.js`와 `generated/asset-manifest.json`(해시값 한 줄) 딱 2개 파일로 한정됨 -- 수동 코드 수정은 없고 순수 빌드 재실행 결과.

반영 스크립트(`45cha_rebuild_bundle_carrot_ryu.ps1`)는 이번엔 Replace-Block 문자열 치환이 아니라, 사용자 PC에서 `git clone`(임시 폴더) 후 그 자리에서 실제로 `npm install && node build.mjs`를 실행하고 변경된 생성 파일만 커밋/push하는 방식으로 작성함(9절 "코드 파일" 유형 중 신규/전면 재작성에 해당하되, Claude가 완성 파일을 만들어 전달하는 대신 빌드 과정 자체를 스크립트가 재현하도록 함 -- 100KB 넘는 압축 번들을 문자열로 스크립트에 박아넣는 것보다 안전하고, 진짜 소스인 build.mjs/esbuild 결과를 그대로 신뢰할 수 있음). 스크립트는 빌드 후 `git status`로 변경 파일 목록을 확인해 `js/generated/`, `css/generated/`, `generated/asset-manifest.json` 범위 밖의 변경이 섞이면 커밋하지 않고 중단하도록 방어장치를 넣음(15절 강제 진행 금지 원칙).

미완료: 스크립트 사용자 실행 대기 -> 실행 후 push 반영을 `git ls-remote`+commit patch로 재확인, 이어서 사진 목록 렌더가 실제로 크래시 없이 뜨는지 실기기 재검증(44차 미완료 항목 1~2번과 동일 검증이 이제야 가능).

## 44차 (진행 중 -- 실기기 버그 3건 수정 + 반영 스크립트 경로 오류 사전 발견/수정) -- 사진목록 크래시/전체삭제 범위/녹화버튼 깜빡임

사용자가 제공한 42차 녹화 버튼·41차 새로고침 아이콘 실기기 검증 스크린샷(녹화 시작/종료, 화면녹화 파일 생성/전송 성공)을 검토하던 중 신규 버그 발견 및 요청 2건이 추가됨:

1. **사진 목록 크래시**: 화면녹화 탭에서 파일을 체크박스로 선택하는 순간 `formatLogBytes is not defined` 토스트 발생. 코드 조사 결과 `selfdrive/carrot/web/src/features/logs/screenshots.js`가 `formatLogBytes()`를 62번째 줄(개별 항목 크기)과 162번째 줄(선택 합계 크기)에서 쓰면서 `./runtime.js` import문에는 누락돼 있었음(39cha-fix, 40차에서 같은 파일의 `formatRelativeEpoch` 누락은 고쳤으나 `formatLogBytes` 누락은 그때 못 잡음). `dashcam.js`/`screenrecord.js`는 정상적으로 import 중. 수정: import문에 `formatLogBytes` 한 항목 추가.
2. **사용자 요청**: 도구탭 "delete all videos"를 누르면 영상과 사진(캡쳐 스크린샷)까지 함께 삭제되게 해달라. 코드 조사 결과 `dispatcher.py`의 `delete_all_videos` 액션이 비동기(682번째 줄)/동기(1164번째 줄) 두 곳 모두 `/data/media/0/videos` 폴더 하나만 하드코딩돼 있었음. 반면 캡쳐 사진(.png)은 `screenshot_capture.py`에서 `SCREEN_RECORDING_DIRS[1]`(`/data/media/0/screenrecord`)에 저장됨 -- 영상/사진이 서로 다른 폴더라 기존 로직은 사진 폴더를 건드리지 않았음. 수정: 두 곳 모두 `config.py`에 이미 정의된 `SCREEN_RECORDING_DIRS`(영상+사진 후보 폴더 7개 전체, `catalog.py`가 실제 목록 조회에 쓰는 것과 동일한 소스) 기준으로 변경.
3. **녹화 버튼 깜빡임 없음**: 사용자 설명("평상시 흰색테두리, 누르면 빨간색으로 채워짐, 깜빡이지는 않음, 다시 누르면 흰 테두리로 복귀")을 코드로 재확인한 결과 정확히 그대로 구현돼 있었고(42차), 깜빡임 로직 자체가 없어 "실제 녹화 중"이라는 느낌이 안 드는 것이 원인이었음. `hud_renderer.py`가 카메라 감지/CPU·메모리 과열 경고에 이미 쓰고 있는 `_blink_timer` 프레임 카운터를 재사용해, `record_button.py`에 `set_blink_phase()`를 추가하고 녹화 중일 때만 채움/테두리를 번갈아 그리도록 수정(녹화 안 할 때는 42차와 동일하게 유지).

3건 모두 최신 GitHub 재조회 후 Replace-Block 앵커 1회 매치 확인, py_compile/`node --check` 통과.

**[중요, 세션 재개 시 발견]** 이 세션은 이전 세션(스크립트까지 완성한 상태)을 이어받아 시작했으나, 이 환경의 로컬 작업 디렉터리가 세션 사이 초기화되는 특성상 이전 세션이 검증에 썼던 경로 가정을 그대로 신뢰하지 않고 `git clone` 전체 리허설로 처음부터 재검증함. 그 결과 **이전 세션이 작성한 Replace-Block 대상 경로가 `selfdrive/...`로 돼 있었는데, 실제 ryujmin97/openpilot 레포는 루트에 `openpilot` 서브디렉터리가 한 겹 더 있어 정확한 경로는 `openpilot/selfdrive/...`임을 발견**(핵심 발견 29 참고). 만약 그대로 전달됐다면 사용자가 스크립트를 실행하는 순간 `FileNotFoundException`으로 실패했을 것 -- 경로를 수정한 뒤 앵커 매치(전부 1회)와 `py_compile`/`node --check`를 다시 통과시키고, 최종적으로 실제 `git clone`으로 대상 파일 존재까지 확인함.

수정 파일: `openpilot/selfdrive/carrot/web/src/features/logs/screenshots.js`, `openpilot/selfdrive/carrot/server/features/tools/dispatcher.py`, `openpilot/selfdrive/ui/onroad/hud_renderer.py`, `openpilot/selfdrive/ui/onroad/record_button.py`(전체 교체).

미완료: carrot-ryu 반영 스크립트(`44cha_carrot_ryu_fixes.ps1`) 사용자 실행 대기. 실행 후 3건 모두 실기기 재검증 필요(사진 목록이 크래시 없이 뜨는지, delete all videos가 사진까지 지우는지, 녹화 중 버튼이 실제로 깜빡이는지).



## 43차 (완료 -- devnotes/실제 상태 괴리 확인 + HANDOFF·CURRENT_STATUS 42차 기준 정리)

사용자가 "지침을 전체 읽고 다시" + "레포도 다시 읽고" 요청 -> 4절 0~3번 절차(지침 문서 -> HANDOFF -> CURRENT_STATUS -> carrot-ryu 최신 commit)를 처음부터 재수행. 그 과정에서 이 대화가 몰랐던 41차(로그탭 새로고침 아이콘)·42차(온로드 원형 녹화 버튼)가 다른 세션에 의해 이미 push 완료돼 있음을 발견했으나, HANDOFF.md/WIP.md 본문은 여전히 "push 미실시"로 남아있는 괴리를 확인(16절 사례, 핵심 발견 27로 CURRENT_STATUS.md에 기록).

검증 방법: `git ls-remote`로 carrot-ryu(`4f81ab75`)·carrot-ryu-note(`8bbc7c82`) HEAD 확인 -> commit patch로 메시지/변경 파일 확인 -> raw.githubusercontent.com으로 실제 파일 내용까지 재조회(index.html의 `#logsRefreshButton`, hud_renderer.py의 `RecordButton` 배선 5곳) -- 텍스트 문구가 아니라 실제 파일 내용으로 반영을 확인함.

반영: CURRENT_STATUS.md(carrot-ryu HEAD 줄, 41차/42차 bullet, 코드 수정 현황 24~25번, 다음 작업 순서, 핵심 발견 27)와 HANDOFF.md(전체)를 42차 기준으로 바로잡음. 코드 변경은 없음, devnotes만 갱신.

교훈: 코드 push와 devnotes push가 시간차를 두고 이루어지는 세션 구조상, devnotes 스크립트 작성 시점의 "미확인" 문구가 이후 실제로 반영된 뒤에도 갱신되지 않은 채 남을 수 있음. 다음 세션은 devnotes 텍스트를 그대로 믿지 말고 항상 `git ls-remote`부터 재확인할 것.

## 42차 (코드 작성 완료 -- 반영 스크립트 실행 대기 -- 온로드 화면에 원형 녹화(Record) 버튼 추가)

사용자 요청: 온로드 화면의 스크린샷 캡쳐 버튼 옆에 동그라미 모양 녹화 버튼을 추가. 한 번 누르면 빨간색으로 점등(녹화 중), 다시 누르면 빨간색이 꺼지고 투명 원(대기 중)으로 표시.

기존 화면녹화 기능(carrotweb Home 탭 `btnRecordToggle` + carrotMan `RECORD` 명령)은 이미 `ScreenRecord` bool param + `layouts/main.py`의 `_handle_carrot_record_cmd`로 구현돼 있었으나, 온로드 UI(디바이스 화면) 자체에는 트리거 버튼이 없었음. 이번 회차는 그 세 번째 트리거로 온로드 UI에 버튼을 추가.

구현:
- 신규 파일 `openpilot/selfdrive/ui/onroad/record_button.py`: `ScreenshotButton`과 동일한 스타일(검정 반투명 배경 원)의 `RecordButton` 위젯. 클릭 시 `ui_state.params.get_bool("ScreenRecord")`를 읽어 반전값을 `put_bool_nonblocking`으로 씀(carrotweb `car.js`의 `toggleRecord()`와 동일한 패턴). 그리기 상태는 로컬 토글 플래그가 아니라 매 프레임 `gui_app.is_recording()`을 직접 읽어 반영 -- carrotweb/carrotMan 등 다른 경로로 녹화 상태가 바뀌어도 항상 실제 상태와 일치.
  - 녹화 중: 안쪽에 빨간 원(`rl.draw_circle`, 사용자 요청의 "빨간색 점등")
  - 대기 중: 안쪽에 흰색 원 테두리만(`rl.draw_circle_lines`, 사용자 요청의 "투명 원")
- `hud_renderer.py` 5곳 수정(문자열 블록 치환): import 추가, `UIConfig`에 `record_button_size`/`record_button_gap` 필드 추가, `__init__`에 `RecordButton` 인스턴스 생성, `_render()`에서 스크린샷 버튼 오른쪽(간격 30px)에 배치해 렌더, `user_interacting()`에 눌림 상태 포함(사이드바 토글 오탭 방지, 27차 이전 더블탭 제스처 폐기 사유와 동일 원칙).

참고 조사 (반영 안 함): 사용자가 `ryujmin97/openpilot`의 `c3-ms-dev` 브랜치(폐기 프로젝트, 코드 참조용으로만 유지)에 이 기능이 있는지 확인 요청 -> Qt 기반 구형 UI(`selfdrive/ui/qt/screenrecorder/`, OMX 하드웨어 인코더)로 지금 carrot-ryu의 pyray 기반 UI와 프레임워크 자체가 달라 이식 대상 아님, 사용자도 "신경 안 써도 됨"으로 확인. `c3-ms-dev`는 1절이 문서화한 브랜치 구성(carrot-ryu/carrot-ryu-note)에 없는 브랜치이나, 사용자 확인으로 조치 불필요 처리.

세션 번호 관련 주의: 이 회차를 준비하던 중 원래 "41차"로 라벨링했으나, 세션 종료 시점에 다른 세션이 이미 "41차"(carrotweb 로그탭 새로고침 아이콘, commit `da6ad815`)를 실제로 push 완료한 것을 `git ls-remote` 재확인으로 발견해 "42차"로 재번호. 코드 자체(record_button.py/hud_renderer.py)는 그 41차 커밋과 겹치는 파일이 없어 영향 없음(41차 커밋 파일: index.html/style.css/runtime.js/생성 번들, 이번 42차 파일: record_button.py/hud_renderer.py).

검증: `py_compile` 통과(2개 파일). 반영 스크립트의 5개 anchor 블록 모두 GitHub 실제 최신 `hud_renderer.py`(41차 커밋 `da6ad815` 기준, 41차가 이 파일을 건드리지 않아 27차 세션 시점 내용과 바이트 단위로 동일함을 diff로 확인) 대비 정확히 1회씩만 매치함을 Python으로 재현해 확인, 치환 결과가 Claude가 로컬에서 직접 작성한 최종본과 바이트 단위로 동일함을 diff로 확인(6절, 9절, 20절). **실기기 검증은 미실시** -- 반영 스크립트 실행 자체가 이번 세션에서 아직 안 됨(12절 원칙: 사용자가 실행해 push하기 전까지 미반영으로 간주).

미완료 (다음 세션 이월):
1. [최우선] `push_carrot_ryu_42cha.ps1` 실행 여부 확인 -- `git ls-remote` + commit patch로 실제 push 재확인 필요.
2. 실기기에서 버튼 위치(스크린샷 버튼 오른쪽, 간격 30px)가 화면 밖으로 벗어나지 않는지, 버튼을 눌렀을 때 실제로 빨간 원 점등/소등이 정상 동작하는지 확인.
3. 41차(logs 탭 새로고침 아이콘) 실기기 검증도 여전히 미실시 상태로 남아있음(아래 HANDOFF.md 이월 목록 참고).

## 41차 (완료 -- 코드 작성/빌드/테스트, push 및 실기기 검증은 다음 세션 이월) -- carrotweb 로그탭 새로고침 아이콘 추가

사용자 요청: 로그탭에서 대시캠/화면녹화 탭바(`#logsTabs`)와 hamburger 메뉴(`#logsMenu`) 사이에 새로고침 아이콘 버튼을 추가하고, 누르면 현재 화면 내용이 새로고침되도록.

완료:
- `index.html`: `#logsTabs`와 `#logsMenu` 사이에 `#logsRefreshButton`(원형 화살표 SVG) 마크업 삽입. Replace-Block anchor 1회 매치 확인.
- `style.css`: `.logs-refresh`/`.logs-refresh__button`/`.logs-refresh-icon` 추가(기존 `.logs-menu__button`과 동일한 `--menu-trigger-size` 박스 크기 공유), 클릭 시 0.6s 회전 애니메이션(`is-spinning` 클래스), 저해상도(<=620px) 미디어쿼리의 `min-height: 38px` 규칙에도 `.logs-refresh__button` 함께 반영.
- `runtime.js`: `refreshActiveLogsTab()`(활성 탭이 화면녹화면 `loadScreenrecordVideos()`+`loadScreenshots()`, 대시캠이면 `loadDashcamRoutes()`를 모두 non-silent 기본 옵션으로 재호출 -- 즉 목록을 처음부터 다시 조회) + `bindLogsRefresh()`(클릭 중 버튼 disable, `is-spinning` 토글) 추가, `bindLogsPage()` 초기화부에 `bindLogsRefresh()` 호출 삽입.
- 빌드 산출물 재생성: `npm install && npm run build`(`node build.mjs`)로 `js/generated/logs.js`/`css/generated/logs.css`/`generated/asset-manifest.json` 3종을 함께 갱신 -- 소스만 바꾸고 번들을 안 바꾸면 실기기에는 반영되지 않으므로 필수(9절).

검증:
- 5개 Replace-Block anchor(index.html 1, style.css 2, runtime.js 2) 모두 carrot-ryu 최신 clone(`bdde8326` 기준) 대상 파이썬 재현으로 정확히 1회 매치 확인.
- `node --check`로 `runtime.js`/`js/generated/logs.js` 문법 확인(PASS).
- `npm test`(logs_tabbar_contract 4개 포함, 로그/대시캠/화면녹화/스크린샷 관련 32개) 전부 pass.
- 별도의 신선한 clone에 동일 Replace-Block 로직과 `npm install && npm run build`를 처음부터 재현해, 스크립트로 전달할 최종 파일이 최초 작업본과 바이트 단위로 동일함을 확인(39차 핵심 발견 26 이후 습관).
- **carrot-ryu push 자체는 이 세션 종료 시점까지 사용자가 아직 실행하지 않음 -- 다음 세션은 반드시 GitHub에서 실제 반영 여부부터 재확인할 것(5절/16절).**

미완료 (다음 세션 이월):
1. [신규, 최우선] `add_logs_refresh_button_41cha.ps1` 실행(push) 여부 GitHub에서 직접 재확인 -- carrot-ryu HEAD가 41차 커밋으로 갱신됐는지 `git ls-remote`+commit patch로 확인.
2. [신규] 새로고침 아이콘 실기기 검증: 위치(탭바-hamburger 사이)가 의도대로 보이는지, 클릭 시 회전 애니메이션과 실제 목록 재조회(대시캠/화면녹화 각각)가 정상 동작하는지.
3. [이월] 사진 업로드 UI(체크박스/전체선택/다운로드/전송)가 `bdde8326`(39cha-fix) 반영 후 에러 없이 정상 렌더링되는지 실기기 재확인.
4. [이월] 화면녹화 탭 "영상" 업로드 UI(36차 구현분) 자체 동작 검증 -- 실제 화면녹화 파일 확보 후 재검증 필요.
5. [이월] 37차 락 수정의 실제 동시성(거의 동시 호출) 재현 검증.
6. [이월] 34차 도로명-신호과속 같은 줄 배치 확인(신호과속 배지가 나타나는 구간에서).
7. [이월] 28~30차 레이아웃 정밀 재검증(육안 확인만 완료).
8. [이월] 실차 재검증(8~41차 코드 변경 전부, 12절 원칙) -- 계속 이월.
9. [이월] 실기기에서 직접 디버깅: 배포된 tools.js에 "web-gdrive-connect" 문자열 실제 존재 여부.
10. [이월] test_web_upload.py 실제 실행해 낡은 테스트 수 확인 -> 데드코드 3개 + 대응 테스트 삭제/갱신.
11. [이월] docs/carrot_web_upload.md 갱신(Drive 기준).
12. [이월] run_upload_segments() 설계 변경 실사용 문제 없는지 재확인.
13. [이월] carrot-ms 모델 셀렉터 코드 분석 착수(6차 이후 계속 미착수).

교훈: 이번 요청은 코드 변경 자체는 작았지만(마크업 1곳, CSS 2곳, JS 2곳) esbuild 번들(`js/generated/logs.js`, 110KB+)을 텍스트로 직접 전달하는 대신 스크립트가 clone 직후 `npm install && npm run build`를 실행해 번들을 그 자리에서 재생성하도록 구성함 -- 39차(`.gitignore` 주석: "device serves this source tree directly and does not run Node at startup")에서 확인된 대로 생성 번들은 커밋되어야 하지만, 전달 스크립트 자체가 무겁게 그 내용을 내장할 필요는 없다는 것이 이번에 실증됨. 향후 esbuild 번들이 걸리는 변경은 이 패턴(소스만 Replace-Block, 번들은 스크립트 내 `npm run build`로 생성 후 커밋)을 기본으로 고려할 것.

## 40차 계속2 (완료 -- devnotes 반영 스크립트 here-string 종료 버그로 인한 조용한 실패 수정)

직전 "40차 계속" 반영 스크립트를 실행한 뒤 `git ls-remote` + commit patch로 재확인하는 과정(16절)에서, `HANDOFF.md`가 완전히 빈 파일(0바이트)로 덮어써졌고 `CURRENT_STATUS.md`는 전혀 갱신되지 않은 채 옛 내용 그대로 남아있음을 발견.

원인: PowerShell here-string(`@'...'@`)은 종료 마커 `'@`가 반드시 줄 맨 앞에 와야 인식되는데, `CURRENT_STATUS.md` 내용을 담은 here-string이 줄바꿈 없이 끝나 `'@`가 이전 줄 텍스트 끝에 바로 붙어버림. PowerShell이 이를 종료로 인식하지 못해, 그 뒤에 이어지는 실제 스크립트 코드(`[System.IO.File]::WriteAllText($StatusPath, ...)` 호출부터 `$HandoffNew = @'` 변수 대입, HANDOFF.md 전체 내용, 그다음 here-string의 정상 종료 마커까지)를 전부 "문자열 리터럴"로 통째로 삼켜버림. 그 결과 (1) `CURRENT_STATUS.md`를 실제로 쓰는 코드 자체가 문자열 안에 파묻혀 실행되지 않아 파일이 그대로 남았고, (2) `$HandoffNew` 변수가 끝내 정의되지 않은 채(`$null`) `HANDOFF.md`에 써져 빈 파일이 됨. 에러 없이 `git commit`/`git push`까지 정상 진행되어 "Push complete"로 보고됨 -- 18절이 경계해온 "조용한 실패" 패턴의 새로운 변종.

수정: devnotes 반영 스크립트를 생성할 때 here-string에 담기는 모든 내용 블록이 줄바꿈으로 끝나도록 보장하는 절차를 추가(내용 끝에 개행이 없으면 자동 추가). 이번 세션에서 이 방식으로 재생성한 스크립트로 `HANDOFF.md`를 복구하고 `CURRENT_STATUS.md`를 실제로 갱신함.

교훈: 9절의 anchor 1회매치 검증처럼, here-string으로 파일 전체를 교체하는 "전체 교체형" 작업도 실행 전에 "내용이 줄바꿈으로 끝나는지"를 기계적으로 검증할 필요가 있음. 이 문제는 anchor 매칭 문제(20차 핵심 발견)나 인코딩 문제(21차)와는 다른, PowerShell here-string 구문 자체의 함정이라 별도로 기록.

## 40차 계속 (완료 -- 경로안내 박스 상하 여백 실기기 검증 + 39cha-fix push 재확인)

직전 40차 HANDOFF.md가 "fix_carrot_ryu_39cha.ps1 미실행"으로 남겨뒀던 1순위 미완료 항목을 이번 세션에서 재확인: `git ls-remote`로 carrot-ryu HEAD가 `bdde832654a6...`임을 확인하고, `github.com/.../commit/bdde8326....patch`로 커밋 메시지("39cha-fix: import missing formatRelativeEpoch in screenshots.js")와 변경 파일(screenshots.js/logs.js/asset-manifest.json)을 직접 조회해 실제 반영을 확인(16절, API rate limit로 REST 엔드포인트가 막혀 ls-remote+patch 조합으로 우회).

이어서 사용자가 제공한 실기기 스크린샷(제네시스 DH 2015, 20:14:25 캡처)으로 27차 이후 계속 이월되던 "우측하단 경로안내 박스 상하 여백" 항목을 처음으로 실기기에서 확인. "교차로"(제목) → 회전아이콘/895m → "도착: 286.1km" → "193.6분(23:28)" → "용산2로" 순서가 27차 설계대로 나타났고, 34차 `content_shift_y=20` 적용 이후 상단/하단 여백이 균등하게 보임(12절, 이 항목의 첫 실차 검증 사례).

미확인: 사진 업로드 UI(체크박스/전체선택/다운로드/전송) 자체 동작은 이 스크린샷에 나타나지 않아 별도 확인 필요(39cha-fix가 실제로 크래시를 해소했는지도 미확인, 다음 세션 최우선 이월).

## 40차 (완료 -- 39차 사진 업로드 UI 실기기 크래시 원인 규명 및 수정: formatRelativeEpoch import 누락)

사용자가 39차 코드 반영 후 실기기에서 "구현안됨"(체크박스/툴바 없이 예전 가로 썸네일만 보임)이라고 보고. 우선 GitHub carrot-ryu HEAD를 확인해 39차 커밋(`797fca2e`)이 정상 push됐음을 확인했고, 사용자가 디바이스에서 `git rev-parse HEAD`/`git status`/`git branch --show-current`를 직접 실행한 결과도 `797fca2e`·clean·`carrot-ryu`로 일치 -- 즉 코드 반영 자체는 문제 없었음. 사용자가 화면을 다시 캡처해 보낸 스크린샷에서 실제 에러 토스트 `formatRelativeEpoch is not defined`를 확인하며 진짜 원인을 특정.

원인: 39차에서 신규 작성된 `screenshots.js`가 `runtime.js`의 `formatRelativeEpoch`를 import하지 않음(같은 패턴을 쓰는 `dashcam.js`/`screenrecord.js`는 정상 import). 사진 행 렌더링 중 `ReferenceError`가 발생해 목록 전체가 비어버리고 에러 토스트만 노출되는 것이 실제 증상이었음 -- 디바이스/캐시/빌드 반영 문제가 아니라 순수 코드 버그.

수정: `screenshots.js` import문에 `formatRelativeEpoch` 1개 식별자만 추가(1줄 변경). 이 저장소를 별도로 shallow clone해 로컬에서 직접 수정 → `npm install` → `node build.mjs`로 재빌드 → `py_compile`(hud_renderer.py, routes.py) 통과, `node --check` 통과, `npm test` 737/737 통과 확인. 재빌드로 `js/generated/logs.js`(esbuild가 import 추가로 인해 파일 전역의 축약 식별자를 재배정 -- 문자열 블록 치환이 아닌 전체 교체로 처리) 및 `generated/asset-manifest.json`(logs.runtime 해시 1줄만 변경, anchor 치환)이 함께 변경됨.

반영: `screenshots.js`/`asset-manifest.json`은 1줄 anchor 치환(카운트=1 검증 포함), `logs.js`는 전체 교체 방식의 PowerShell 스크립트(`fix_carrot_ryu_39cha.ps1`, UTF-8 BOM, `--config core.autocrlf=false`, 임시폴더 자동삭제 포함)로 준비해 사용자에게 전달. **이번 세션 종료 시점까지 사용자가 스크립트를 실행하지 않았으므로, 다음 세션은 carrot-ryu 최신 commit이 이 수정 커밋으로 갱신됐는지 반드시 재확인할 것(16절 원칙).**

교훈: "코드/디바이스 반영 문제로 보이는 증상"이 실제로는 반영과 무관한 순수 JS 런타임 에러일 수 있음 -- 반영 상태(git HEAD/status)를 아무리 정밀하게 검증해도 실제 브라우저 에러 메시지를 직접 확인하기 전까지는 근본 원인을 알 수 없었음. 다음부터 "화면이 예전 그대로다"류 보고를 받으면, 반영 상태 확인과 별개로 최대한 빨리 실제 에러 화면 캡처를 요청하는 것이 효율적.


## 39차 (완료 -- 코드 반영, 실기기 검증은 다음 세션 이월) -- 화면녹화 탭 사진 업로드 UI 신규 구현 + 경로안내 박스 상하 여백 통일

사용자가 38차 미확인 항목("화면녹화 탭 업로드 UI 자체 동작")의 의도를 정정: 녹화본이 아니라 화면캡쳐 사진 업로드를 원했던 것. 사진 목록에 체크박스(앞)/다운로드+전송 버튼(뒤), 목록 상단에 전체선택/다운로드/전송 툴바를 신규 요청. 추가로 34차에서 이월됐던 경로안내 박스 상하 여백 불균형(제목 위 여백은 넉넉한데 하단 배지가 경계에 닿음)도 함께 요청.

완료:
- `screenshots.js` 전면 재작성 -- 기존 썸네일 전용 가로 스트립(클릭 시 원본 열기만 가능)을 `screenrecord.js`(영상 목록) 컨벤션과 동일한 세로 행(row) 목록으로 교체. 행별 체크박스(`select-screenshot`) + 다운로드/전송 버튼, 선택 상태(Set) 관리, 전체선택/선택다운로드/선택전송 툴바, 업로드 확인/결과 다이얼로그, 다운로드는 `<a download>` 순차 클릭 방식(팝업 차단 회피, screenrecord와 동일 패턴).
- `runtime.js` -- `screenshots.js` import 확장(downloadScreenshots/uploadScreenshots/screenshotsSelectedPhotos/toggleScreenshotSelectAll/toggleScreenshotSelection 추가), 사진 목록 click/change 위임에 download-screenshot/upload-screenshot/select-screenshot 핸들러 추가, 신규 `screenshotsToolbar` click 위임(전체선택/선택다운로드/선택전송) 추가.
- `index.html` -- `screenshotsToolbarWrap`/`screenshotsToolbar` 마크업 추가(screenrecordToolbar와 동일 구조, `dashcam-selection-row` 클래스 재사용).
- `style.css` -- `.screenrecord-photos`를 가로 썸네일 스트립(overflow-x)에서 세로 행 리스트(overflow-y, flex-column)로 전환, `.screenrecord-photos-wrap`에 `max-height: 46vh` + 내부 스크롤 적용(사진이 많아도 영상 목록을 화면 밖으로 밀어내지 않도록), 이제 안 쓰는 `.screenrecord-photo`/`.screenrecord-photo:hover`/`.screenrecord-photo img`(구 썸네일 버튼) 규칙 삭제.
- `js/translations/{ko,en,zh}.js` -- `screenshot_upload`, `no_selected_photos` 2개 키 추가(3개 언어).
- `server/features/screenrecord/routes.py` -- `POST /api/screenrecord/photo/upload` 신규 엔드포인트 추가. 기존 `api_screenrecord_upload()`(영상용)를 `find_photo()` 기준으로 그대로 미러링(동기, 파일별 순차, job/폴링 없음). 라우터에 등록.
- `openpilot/selfdrive/ui/onroad/hud_renderer.py` -- `_draw_turn_info_hud()`에 `content_shift_y = 20` 상수 도입, 제목/route=숫자/도착 거리·시간/회전아이콘(따라서 신호과속·도로명 배지까지 연쇄) 기준 y좌표 4곳에서 이 값을 일괄로 뺌. 요소 간 상대 간격(95/175/190 등)은 그대로 유지한 채 절대 기준선만 위로 이동. 실기기에서 여백이 여전히 안 맞으면 이 상수 하나만 조정하면 되도록 주석에 명시.

검증:
- `python3 -m py_compile`(hud_renderer.py, routes.py) 통과.
- `node --check`(runtime.js, screenshots.js, ko/en/zh.js) 통과.
- `npm install && node build.mjs`로 생성 번들(`js/generated/logs.js`, `css/generated/logs.css`, `generated/asset-manifest.json`) 재생성 확인.
- `npm test` 737/737 통과.
- 반영 전 사전 검증: 코드 반영 스크립트를 별도 클론(HEAD `c01d9ec`, 37차와 동일)에 대해 Python으로 anchor 로직을 재현해 시뮬레이션 실행, 문자열 anchor 17곳 모두 정확히 1회 매치 확인 후 실제로 적용 → py_compile/node --check/build/npm test까지 전부 재확인(9절 사전 dry-run, 새 세션에서 재검증).
- 실차/실기기 검증: 미실시(12절 원칙) -- 사진 업로드 UI 자체 동작(선택/전송/다운로드)과 경로안내 박스 여백 실측은 다음 세션 이월.

주의사항:
- `.screenrecord-photo`(단수, 구 썸네일 버튼) 클래스는 완전히 삭제됨. 사진 행은 이제 `.screenrecord-row`(영상 목록과 공유)를 그대로 재사용하므로 별도 CSS 스타일링이 필요 없었음.
- `content_shift_y`는 `_draw_turn_info_hud()` 지역 상수이며 Params 등 외부 설정이 아님 -- 실기기에서 상하 여백을 추가로 조정하려면 코드 값(현재 20)을 바꿔야 함.


## 38차 (완료 -- 36차/37차/34차 실기기 검증 1차 진행, 일부 확인/일부 이월) -- 사용자 제보 스크린샷 9장 분석

사용자가 실기기 스크린샷 9장(온로드 HUD 1장, 대시캠 탭 로그 전송 플로우 3장, 화면녹화 탭/도구 탭/햄버거 메뉴 3장, 구글드라이브 앱 2장)을 제공. 37차 HANDOFF 미완료 1번(36차 변경사항 실기기 검증)과 4번(34차 UI 실기기 재확인)을 함께 검증. 코드 변경 없음, devnotes만 갱신.

확인됨:
- 당근서버 라벨 오표시 버그(36차 dashcam.js 수정) -- 대시캠 탭 세그먼트 메뉴의 "로그 전송" 확인 다이얼로그가 "구글 드라이브"로 정상 표시됨. 실제 전송도 "전송 완료 1/1"(qcamera 1개+rlog 1개, 11.2MB)로 성공.
- 햄버거 메뉴 화면녹화 탭 분기(36차 runtime.js 수정) -- 화면녹화 탭에서 우측상단 메뉴를 열면 "로그 메뉴"에 정렬 옵션만 있고 "최근 로그 업로드" 섹션이 없음. 35차 증상 3(탭 무관 대시캠 전용 업로드) 해소 확인.
- Drive 폴더 단일화 -- 내 드라이브에 "CarrotWeb Logs" 폴더가 1개만 존재, 그 안에 이번 세션 업로드 3건(대시캠 로그 전송 1건 14:52, tmux로 추정되는 항목 2건 14:48/14:50)이 모두 같은 폴더로 들어감.
- 34차 UI(도착 텍스트 40->32 축소) -- 경로안내 박스에서 회전아이콘 초록박스와 "도착: 3.0km / 6.7분(14:54)" 텍스트가 겹치지 않음, 육안상 정상.

미확인/이월(근거 포함):
- 화면녹화 탭 업로드 UI(체크박스/전체선택/다운로드/전송) 자체 동작 -- 실제 화면녹화 파일이 없어("화면녹화 기록이 없습니다") 테스트 대상 부재, 사진 스트립만 존재. 녹화본이 생긴 뒤 재검증 필요.
- 37차 락 수정의 실기기 동시성 재현 -- 업로드 3건이 14:48/14:50/14:52로 수 분 간격이 있어 "거의 동시 호출" 레이스 조건을 재현한 테스트가 아님. 폴더 1개만 생성된 것은 정황상 문제없어 보이나, 락이 실제로 레이스를 막았다는 확정적 증거로 보고하지 않음(12절 원칙).
- 34차 도로명-신호과속 같은 줄 배치 -- 스크린샷 촬영 시점에 신호과속 배지가 화면에 없어(과속/신호 구간 아님) 같은 줄 비교 불가. 도로명("대덕대로989번길")은 경로안내 박스 바깥쪽 하단(IP 주소와 같은 줄)에 표시되고 있어, WIP 34차에 기록된 "박스 안쪽" 목표와 실제로 일치하는지 신호과속 배지가 뜨는 구간에서 추가 확인 필요.
- 28~30차 레이아웃 -- 확인한 스크린샷 범위에서는 특별한 깨짐/겹침 없음(육안 확인 수준, 좌표 단위 정밀 검증 아님).

부가 발견: 37차 push 직후 raw.githubusercontent.com 브랜치-head 조회에서 캐시 지연이 재현됨(핵심 발견 21, 33차와 동일 패턴) -- commit-pinned raw URL(`/{sha}/...`)로 우회해 실제 최신 내용 확인. 상세: FINDINGS.md 2026-09-15(38차) 항목.
## 37차 (완료 -- gdrive_upload.py Drive 폴더 중복생성 레이스컨디션 수정) -- 35차 핵심발견23 증상4 근본조치

35차에서 "추정, 미확정"으로 이월됐던 Drive 폴더 2개 생성 문제(핵심 발견 23 증상 4)의 원인을 코드 조사로 확정하고 최소 수정으로 고침. 화면녹화 탭 실기기 검증(36차 이월 1번)은 이번 세션에서 다루지 않음(사용자가 2번 항목부터 진행하기로 결정).

원인: gdrive_upload.py의 _ensure_folder()가 "캐시확인 -> 이름으로 검색 -> 없으면 생성 -> 캐시기록" 순서를 락 없이 수행함(TOCTOU 레이스). 같은 프로세스(웹서버) 안에서 대시캠 탭 전송과 햄버거 메뉴 "최근 로그 업로드"처럼 서로 다른 업로드 job이 거의 동시에 이 함수를 호출하면, 첫 호출의 Drive API 왕복(수백ms)이 끝나기 전에 두 번째 호출도 캐시 미스로 판단해 files.list가 둘 다 빈 결과를 받고 둘 다 새 폴더를 생성함.

수정: gdrive_upload.py에 모듈 레벨 `_folder_lock = asyncio.Lock()` 추가, `_ensure_folder()` 본문 전체(캐시확인~생성~캐시기록)를 이 락으로 감쌈. 문자열 블록 치환 3곳(import 추가, 전역 상태 변수 추가, 함수 본문 교체), 각각 파일 내 정확히 1회 매치 확인 후 반영.

검증:
- `python3 -m py_compile` 통과.
- 목(mock) 기반 동시성 테스트 직접 작성해 실행: aiohttp 세션을 50ms 지연이 있는 가짜 객체로 교체하고 `asyncio.gather`로 `_ensure_folder()`를 동시에 2번 호출. **수정 전** 코드로는 실제로 폴더 생성 API가 2번 호출되는 것을 재현 확인(버그 재현 성공). **수정 후** 코드로는 1번만 호출되고 두 호출 모두 같은 folder_id를 반환함을 확인(수정 확인). 이 테스트 스크립트는 이번 세션의 1회성 검증 산출물이며 toolkit에 저장하지 않음.
- 실기기 검증: 미실시(로컬 코드 조사 + 목 테스트만 진행, 실제 Drive API 대상 동시성 재현은 하지 않음. 12절 원칙에 따라 실차 검증으로 표기하지 않음).

알려진 한계(그대로 이월, FINDINGS 37차 참고): 이 락은 프로세스 내부에서만 유효함. `carrot_man.py`의 `send_tmux_web()`은 웹서버(`server/app.py`)와 별도 프로세스로 실행되므로, 그쪽에서 발생하는 tmux 진단정보 전송과 웹서버 쪽 대시캠/화면녹화 업로드가 우연히 겹치는 경우까지는 이번 수정으로 막지 못함. 근본 해결안(폴더 id를 Params에 영구 저장)은 사용자와 논의 후 이번 세션에서는 범위 밖으로 확정(31차 발견 이후 두 번째로 "최소수정 vs 근본수정" 중 최소수정을 선택한 사례).
## 36차 (완료 -- 화면녹화 탭 업로드 UI 구현 + 버그 수정 3건) -- 35차 스펙 반영

35차에서 확정된 스펙(화면녹화 탭 체크박스/전체선택/다운로드/전송)을 구현하고, 함께 발견됐던 버그 2건과 UX 문제 1건을 같이 수정함.

완료:
- screenrecord.js: 선택 상태(Set), 행별 체크박스 + 전송 버튼, 상단 툴바(전체선택/선택다운로드/선택전송), 업로드 확인/결과 다이얼로그, 동기 순차 업로드(개별 파일, 사용자 확정 스펙), <a download> 순차 클릭 방식 다운로드(팝업 차단 회피), 새로고침 시 사라진 파일 선택 자동 정리.
- runtime.js: 체크박스 change/전송 버튼 click 위임, 신규 screenrecordToolbar 클릭 위임(전체선택/선택다운로드/선택전송).
- index.html: screenrecordToolbarWrap/screenrecordToolbar 마크업 추가.
- style.css: .screenrecord-toolbar-wrap 패딩 규칙 추가(체크박스/버튼은 기존 클래스 재사용).
- server/features/screenrecord/routes.py: POST /api/screenrecord/upload 신규 -- gdrive_upload.upload_file_resumable()을 파일별 순차 호출, job/폴링 없이 결과 배열 반환.
- js/translations/{ko,en,zh}.js: download_selected/screenrecord_upload/no_selected_recordings 3개 키 추가.
- dashcam.js: "당근서버" 라벨 오표시 버그 수정 -- dashcamUploadConfirmHtml() targetLabel 분기에 gdrive 케이스 추가(35차 원인 특정, 이번 세션에 수정).
- runtime.js logsMenuChoices(): 햄버거 메뉴 "최근 로그 업로드" 항목을 화면녹화 탭에서 숨김 처리(사용자 확정 -- 대시캠 탭에서는 그대로 유지). "항상 대시캠 세그먼트만 업로드"하는 설계 문제(35차 발견)에 대한 사용자 결정 반영.
- npm install && node build.mjs로 esbuild 번들(js/generated/logs.js, css/generated/logs.css, generated/asset-manifest.json) 재생성 확인, npm test 737/737 통과 확인(이전 세션에서 중단됐던 빌드 검증을 이번 세션에서 완료).

검증: 정적 문법 검사(node --check) + 빌드(node build.mjs) + 전체 테스트(npm test, 737/737 pass) 통과. 실차 검증: 미실시.

주의사항:
- 이 회차는 직전 세션(도구 호출 한도로 중단, carrot-ryu에 커밋된 적 없음)에서 로컬로만 작성됐던 코드를 이어받아, 새 세션에서 GitHub carrot-ryu(당시 HEAD 9fdefb3d) 위에 다시 clone하여 재검증(문법/빌드/테스트)까지 마친 뒤 반영한 것. 커밋 히스토리 불연속은 없음.
- 생성 번들(js/generated/*, css/generated/*, generated/asset-manifest.json)은 기기가 소스가 아닌 이 파일들을 직접 서빙하므로 소스와 함께 커밋이 필수 -- 코드 반영 스크립트가 npm install && node build.mjs를 실행해 자동 재생성 후 커밋함.

다음 세션 후보:
- Drive 폴더 2개 생성 원인 확정 조사(우선순위 낮음)
- 이번 세션 변경사항(화면녹화 업로드, 라벨 수정, 햄버거 메뉴) 실기기 검증
- 34차 UI 변경 실기기 재확인, 28~30차 레이아웃 실기기 재검증
- test_web_upload.py 실행 + 데드코드 3개 정리
- docs/carrot_web_upload.md 갱신
- carrot-ms 모델 셀렉터 코드 분석 착수

## 35차 (진행 중 -- 코드 변경 없음, 조사/스펙 확정만) -- 화면녹화 탭 업로드 기능 조사 및 신규 스펙 확정

- 사용자가 실기기 스크린샷 3장(대시캠 탭 "로그 전송" 다이얼로그 1세그먼트/10.8MB, 5세그먼트/51.5MB, 화면녹화 탭 "화면녹화 기록이 없습니다" 화면)과 Drive "내 드라이브"에 "CarrotWeb Logs" 폴더가 2개 생성된 스크린샷을 제보. 이를 바탕으로 32차 Drive 연동 이후 실기기 첫 검증 결과를 코드 조사로 분석함.
- **핵심 발견 1 (당근서버 라벨 오표시)**: `web/src/features/logs/dashcam.js`의 `dashcamUploadConfirmHtml()` 1277~1279행, targetLabel 분기가 `uploadTarget === "toss"` 여부만 검사하고 else는 무조건 `web_log_upload_target_carrot`("당근서버")을 반환 -- `"gdrive"` 케이스가 없음. 실제 업로드 자체는 `getWebSettingByKey("log_upload_target")`로 정상적으로 gdrive를 타는 것으로 보이나(1653~1661행), 확인 다이얼로그의 표시 라벨만 어긋남. ko.js에 `web_log_upload_target_gdrive: "구글 드라이브"` 키가 웹설정 드롭다운용으로 이미 존재해서, 매핑만 추가하면 되는 간단한 수정.
- **핵심 발견 2 (화면녹화 탭 업로드 기능 전무)**: `screenrecord.js`(영상 목록)와 `screenshots.js`(사진 스트립) 둘 다 조회/썸네일/재생/다운로드만 구현돼 있고, 선택 상태(selection state)나 업로드 호출이 코드에 전혀 없음. 서버 쪽 `server/features/screenrecord/routes.py`에도 조회/썸네일/다운로드 엔드포인트뿐 업로드 엔드포인트가 없음. 대시캠 탭(`dashcam.js`)에만 선택+전송 UI가 구현돼 있는 상태.
- **핵심 발견 3 (햄버거 메뉴가 탭 무관 대시캠 전용)**: 로그 페이지 상단 햄버거 버튼(`logsMenuButton`, `runtime.js`)은 대시캠/화면녹화 탭 구분 없이 페이지 전역에 떠 있음. 메뉴의 "최근 로그 업로드(2/5/10)" 항목은 `uploadRecentDashcamSegments()` -> `/api/dashcam/recent` -> `uploadDashcamSegments()`로 이어져 **무조건 대시캠 세그먼트(qcamera/rlog)만 업로드**함. 화면녹화 탭에서 열어도 화면녹화 영상과는 무관 -- 사용자가 제보한 "화면녹화에서 전송" 스크린샷(qcamera/rlog 카운트)이 이 경로로 설명됨.
- **Drive 폴더 2개 생성 (원인 추정, 미확정)**: `gdrive_upload.py`의 `_ensure_folder()`는 이름으로 폴더 검색 후 없으면 생성하며, 인메모리 캐시(`_folder_verified_cache`, 300초)만 사용. 핵심 발견 1의 개별 세그먼트 전송과 핵심 발견 3의 햄버거 메뉴 업로드가 각각 별도로 `_ensure_folder()`를 호출했고, 캐시 만료 또는 Drive 검색 인덱스의 생성 직후 지연(eventual consistency)으로 두 번째 호출이 방금 만든 폴더를 못 찾아 새로 만들었을 가능성이 유력. 코드 조사만으로 확정할 수 없어 미해결로 이월.
- **사용자 확정 스펙 (화면녹화 탭 신규 기능, 다음 세션 최우선)**:
  1. 영상목록 표시 (현재도 목록 렌더링 로직 자체는 있으나 선택/전송 UI가 전혀 없는 상태 -> 아래 UI를 추가)
  2. 각 항목: 파일명(저장 시간 포함) 앞에 체크박스, 뒤에 다운로드 버튼 + 전송 버튼
  3. 목록 상단: 전체선택 버튼, 그 옆에 다운로드 버튼 + 전송 버튼
- 이번 세션에서 진행 중이던 것: `dashcam.js`의 기존 선택 UI(체크박스 렌더링, 선택 상태 관리, 클릭 디스패치 구조, 업로드 확인 다이얼로그)를 화면녹화 탭에 동일 컨벤션으로 이식하기 위해 `index.js`/`web/src/shared/` 디렉터리 구조까지 확인하던 중 세션 종료 -- 코드 작성 전.
- 실차/실기기 검증: 해당없음(이번 세션은 코드 변경 없이 분석/스펙 확정만 진행, 12절 원칙).
## 34차 (완료 -- 코드 수정 1건 GitHub 반영 완료) -- 경로안내 박스 도착 텍스트 크기/도로명 위치 수정

- 사용자 요청 2건: (1) 도착 거리/시간 텍스트가 회전 아이콘 초록박스와 겹쳐 보임 -> 글자 크기를 40에서 32로 축소(arrival_size 변수 신규 도입, eta_size 자체는 다른 요소용으로 그대로 유지). (2) 일반도로 도로명 텍스트가 박스 아래 경계를 벗어나 보임 -> 신호과속 배지와 동일한 y좌표 계산식(회전 아이콘 초록박스 하단 by+115 기준)으로 이동해 박스 안쪽, 신호과속 문구와 같은 줄 위치로 조정.
- 변경 파일: `openpilot/selfdrive/ui/onroad/hud_renderer.py` 2곳, 문자열 블록 치환(Replace-Block, 9절)으로 반영. commit `9fdefb3d`(부모 `789667f7`, 33차 ko.js 수정 위에 쌓임).
- **[핵심 발견 22 참고] 세션 번호 충돌**: 이 세션은 시작 시점에 32차까지만 인지한 상태로 작업해 코드 주석/커밋 메시지에 `[33차]`로 표기했으나, 실제로는 그 사이 다른 경로로 33차(ko.js 문구 수정, commit 789667f7)가 이미 진행/기록돼 있었음. 코드에 이미 커밋된 `[33차]` 주석 문구는 과거 기록이므로 수정하지 않고(18절, 기존 기록 임의 수정 금지 원칙과 동일하게 취급), devnotes 상의 회차 번호만 실제 순서에 맞춰 34차로 기록함.
- 반영 전 검증: 문자열 anchor 블록 2곳 모두 push 직전 최신 GitHub 내용과 정확히 1회 매치 확인(사전 dry-run). 반영 후 검증: `github.com/.../commit/9fdefb3d.diff` 및 commit-pinned raw URL로 실제 내용 재조회, 두 블록 모두 정상 반영·`py_compile` 문법 검사 통과 확인.
- 실차/실기기 검증: 미실시(정적 레이아웃 변경, 12절 원칙).
## 33차 (완료 -- 코드 수정 1건 GitHub 반영 완료) -- ko.js Google Drive 클라이언트 유형 안내 문구 수정

- 32차 HANDOFF.md 미완료 3번(31차부터 이월된 버그): ko.js의 `web_gdrive_client_id_desc`가 "데스크톱 앱 유형"으로 안내하지만, gdrive_upload.py 주석/실제 요구사항은 "TV 및 제한된 입력이 있는 기기" 유형임을 수정.
- 변경 파일: `openpilot/selfdrive/carrot/web/js/translations/ko.js` 1곳(584번째 줄), commit `789667f7`(부모 `c704371a`, 32차).
- 반영 방식: 소규모 문자열 치환(9절), 치환 전 원본 라인이 파일 내 정확히 1회 매치되는지 확인 후 진행.
- **검증 관련 신규 관찰**: `github.com/.../commit/789667f7.diff`로는 즉시 정상 반영이 확인됐으나, `raw.githubusercontent.com`은 `?nocache=<timestamp>` 쿼리를 붙여도 한동안 수정 전 내용을 계속 반환함(캐시 지연). 상세: FINDINGS.md 2026-09-15(33차) 항목.
- 실차/실기기 검증: 미실시(UI 안내 문구 텍스트 변경, 우선순위는 낮음 -- 필요 시 다음 실기기 검증 때 함께 확인).
## 32차 (devnotes 사후 정리 -- 코드 반영은 이미 GitHub에 완료된 상태로 확인) -- Google Drive drive.file 스코프 + 폴더 자동생성 복귀

- 세션 시작 시 4절 0~3번 절차로 carrot-ryu 최신 커밋을 확인한 결과, `c704371a`(부모 `34bb41bc`, 메시지: `32cha: gdrive drive.file scope + folder auto-create revert (c3-ms-dev, 31cha device-flow block fix)`)가 이미 GitHub에 반영돼 있었음. 이 커밋에 대한 devnotes(WIP/HANDOFF/CURRENT_STATUS)는 남아있지 않아, 이번 세션에서 `github.com/.../commit/<sha>.diff`로 실제 변경 내용을 직접 조회해 사후 정리함(16절 상황, 24차·30차와 유사한 "코드 반영과 devnotes 갱신이 다른 시점에 이루어진" 사례).
- 이 커밋은 31차(FINDINGS 핵심 발견 19)에서 사용자에게 제시한 3가지 대안 중 **(a) drive.file 스코프 + 폴더 자동생성 방식(c3-ms-dev 원본)으로 복귀**를 선택해 반영한 것으로 보임.
- 변경 파일: `openpilot/selfdrive/carrot/gdrive_upload.py` 1개뿐(diff로 확인).
- 변경 내용:
  1. `DRIVE_SCOPE`: `.../auth/drive`(전체) -> `.../auth/drive.file`(비민감, 앱이 만든 파일만 접근).
  2. 고정 `DRIVE_FOLDER_ID` 상수 제거, `DRIVE_FOLDER_NAME = "CarrotWeb Logs"` 신설.
  3. `_verify_folder()`(ID로 존재/휴지통/타입만 확인) -> `_ensure_folder()`(이름으로 검색, 없으면 생성)로 교체.
  4. `_folder_verified_cache` 구조 변경: `{"ok": bool}` -> `{"id": str|None}`.
  5. `api_gdrive_status` 응답에서 `folder_id` 필드 제거(고정 ID 개념 자체가 없어짐).
  6. 파일 상단 docstring을 새 설계(31차 근거, drive.file 복귀 사유, 폴더 자동생성 동작)에 맞춰 갱신.
- 31차에서 확인된 "Device Authorization Grant가 전체 drive 스코프를 정책적으로 차단"하는 제약(핵심 발견 19)을 정면으로 우회하는 방향.
- 실차/실기기 검증: 미실시. 실제 Drive 연결 버튼을 눌러 새 폴더가 정상 생성/재사용되는지는 아직 확인되지 않음 -- 기존에 만들어둔 폴더(구 DRIVE_FOLDER_ID)는 이제 사용되지 않고, 앱이 "CarrotWeb Logs"라는 새 폴더를 자동 생성/검색하는 구조로 바뀌었으므로 반드시 실사용 테스트 필요.
## 31차 (진행 중 -- 코드 변경 없음, Google Drive 연동 설계 근본 제약 발견) -- OAuth 연결 실패 원인 조사: Device Flow가 Drive 스코프를 구조적으로 차단

- 사용자가 실기기에서 "웹 설정 > 로그 업로드" Google Drive 연결을 시도하며 스크린샷 3장 제공. 순서대로 (1) 클라이언트 ID에 "http://"가 붙은 값 입력 + "Google Drive가 연결되어 있지 않습니다"/OAuth client not found 화면, (2) 클라이언트 보안 비밀번호까지 입력 후 "The OAuth client was not found." 에러, (3) 정상 형식의 Client ID로 재시도 후 "Invalid device flow scope: https://www.googleapis.com/auth/drive" 에러.
- 1차 가설(클라이언트 ID 값 자체의 형식 문제) 확인 시도 -> 사용자가 이미 정상 형식으로 재입력했음에도 동일 계열 에러 지속.
- 2차 가설: ko.js 번역 문구(web_gdrive_client_id_desc, 23차 추가)가 "데스크톱 앱 유형"이라고 안내하지만, gdrive_upload.py 설계 주석(15차)은 "TV 및 제한된 입력이 있는 기기" 유형을 필수로 요구함 -> UI 문구가 실제 요구사항과 다른 버그로 확인. 다만 사용자는 이미 올바른 유형(TV/제한된 기기)으로 발급받아 적용했다고 확인 -> 이 불일치가 이번 에러의 직접 원인은 아님.
- 3차 가설: OAuth 동의 화면(Data Access)에 auth/drive 스코프가 실제 등록됐는지 확인 요청 -> 사용자 확인 결과 이미 등록돼 있음 -> 배제.
- 4차(확정): 웹 검색으로 독립된 다수 개발자 사례를 확인한 결과, Google이 OAuth Device Authorization Grant(기기 인증 흐름) 자체에서 전체 Drive 스코프(https://www.googleapis.com/auth/drive)를 수년째 구조적으로 차단하고 있음을 확인함(클라이언트 유형, 동의 화면 스코프 등록 여부와 무관하게 항상 거부됨). Calendar 등 다른 API 스코프는 동일 흐름에서 정상 동작하는 것으로 보아, Drive 전체 스코프 특유의 제약으로 판단.
- 설계 충돌 확인: gdrive_upload.py(15차)는 원래 drive.file(비민감) 스코프를 쓰다가, 사용자가 미리 만들어둔 고정 폴더(DRIVE_FOLDER_ID)에 ID로 직접 접근하기 위해 의도적으로 전체 drive 스코프로 넓혔음(주석에 명시). 이 설계 변경이 바로 device flow에서 차단되는 조합이었음 -> 현재 설계로는 애초에 성공할 수 없는 구조였던 것으로 확인됨.
- 사용자에게 3가지 대안 제시, 결정 대기 중(상세 내용은 FINDINGS.md 참고):
  1. drive.file 스코프로 되돌리고 폴더를 앱이 직접 생성하는 방식(c3-ms-dev 원본 _ensure_folder())으로 복귀 -- device flow 유지 가능성 높으나 미검증, 기존에 만들어둔 폴더는 사용 불가.
  2. Device flow를 포기하고 표준 Authorization Code Flow(콤마 기기 자체 웹서버가 redirect URI 수신)로 전면 재설계.
  3. Google Drive 대신 다른 저장 수단으로 전환.
- 이번 세션은 조사만 진행, 코드/carrot-ryu 커밋 없음. carrot-ryu HEAD는 30차와 동일(34bb41bc).

## 30차 (완료 — 코드 수정 1건 GitHub 반영 완료) — 경로안내 박스 route=/도착 텍스트 위치 재조정

- 사용자 요청: (1) "route=숫자" 글자 크기를 28→32로 키우고, 세로 위치를 회전 아이콘 초록박스 상단(box_y+95)과 텍스트 상단이 맞도록 이동. (2) "도착:"/ETA 텍스트가 박스 우측 경계(edge_x = box_x+box_w-6)를 넘어 삐져나오는 문제를 pad(24px)만큼 안쪽으로 들여 해결. (3) 위 변경에 맞춰 도착/ETA 텍스트를 route= 한 줄 아래(eta_top = box_y+175)에서 상단기준(right_top)으로 다시 배치.
- 적용한 수정(carrot-ryu, selfdrive/ui/onroad/hud_renderer.py만, commit 34bb41bc): route_debug_text 크기/좌표 수정, edge_x를 box_x+box_w-6에서 box_x+box_w-pad로 변경, eta_top 변수 신설(box_y+175), 도착/ETA 정렬을 right_bottom→right_top으로 변경.
- 반영 방식: 문자열 블록 치환(Replace-Block, 20차 원칙) 2곳, GitHub 최신(67a8e10, 29차) 대비 각각 정확히 1회 매치 확인 후 진행.
- 실차 검증: 미실시(정적 코드 변경 단계, 12절 원칙). 실기기 스크린샷으로 재확인 필요(HANDOFF.md 참고).

## 29차 (완료 — 코드 수정 1건 GitHub 반영 완료) — 경로안내 박스 제목/ETA/신호과속 배지 위치 조정

- 사용자가 실기기 사진 한 장을 제공하며 세 가지 레이아웃 조정 요청: (1) "교차로"(제목) 텍스트를 위로 이동(box_y+55 → box_y+38)해 회전 아이콘 초록박스와 겹치지 않게. (2) "도착:"/ETA 텍스트를 pad(24px) 인셋이 아니라 박스 우측 경계(box_x+box_w-6)에 거의 붙여(끝맞춤) 표시. (3) "신호과속" 배지를 박스 맨 아래 고정 위치(box_y+box_h-35, 다른 하단 상태줄과 겹쳐 보이던 위치)에서, 회전 아이콘 초록박스 바로 아래(by+115 기준, 배지 텍스트 실측 높이로 역산한 label_y)로 이동.
- 적용한 수정(carrot-ryu, selfdrive/ui/onroad/hud_renderer.py만, commit 67a8e10): 제목 y좌표 수정, edge_x 변수 신설, bx/by 계산을 if x_turn_info 블록 밖으로 이동(신호과속 배지 위치 계산에도 재사용하기 위함), 신호과속 label_y를 by+115 기준 역산 방식으로 변경.
- 반영 방식: 문자열 블록 치환(Replace-Block) 4곳, GitHub 최신(cc73f629, 28차) 대비 각각 정확히 1회 매치 확인 후 py_compile 통과 확인.
- **devnotes 절차 문제(중요, FINDINGS 참고)**: 이 회차의 HANDOFF.md는 "사용자가 스크립트를 아직 실행하지 않음(미반영)"으로 작성됐으나, 실제로는 사용자가 스크립트를 실행해 GitHub에 정상 반영된 상태였음. 다음 세션(30차) 시작 시 4절 절차에 따라 carrot-ryu 커밋 로그를 직접 재조회하며 발견함. 상세 원인/재발 방지는 FINDINGS.md "2026-09-15(30차) — HANDOFF.md 미반영 기록과 실제 GitHub 상태 불일치" 항목 참고.
- 실차 검증: 미실시(정적 코드 변경 단계, 12절 원칙).

## 28차 (완료 — 코드 수정 1건 GitHub 반영 완료) — 경로안내 박스 높이 축소 및 요소 재배치

- 사용자 요청: 27차에서 475x495로 확대했던 경로안내 박스의 높이를 495→400으로 축소하고, 그에 맞춰 "도착: 거리"/ETA 텍스트를 route=숫자 바로 아래(우측끝맞춤)로 옮기고, 회전 아이콘 초록박스를 박스 가로 중앙이 아니라 좌측(상단 제목과 동일한 pad 기준선)에, 세로는 박스 정중앙에 오도록 재배치.
- 적용한 수정(carrot-ryu, selfdrive/ui/onroad/hud_renderer.py만, commit cc73f629): box_h 495→400, 도착/ETA 텍스트를 좌측하단 정렬(_draw_text_left_bottom)에서 우측끝맞춤 상대좌표(draw_text_ui_style, align="right_bottom")로 이동, bx 계산을 박스 가로중앙(box_x+box_w//2)에서 좌측 pad 기준(box_x+pad+80)으로, by를 box_y+200에서 box_y+190으로, 초록박스 크기를 160x230→160x210으로 축소.
- 반영 방식: 문자열 블록 치환(Replace-Block) 3곳, GitHub 최신(5f5e49d0, 27차) 대비 각각 정확히 1회 매치 확인 후 py_compile 통과 확인.
- 실차 검증: 미실시(정적 코드 변경 단계, 12절 원칙).

## 27차 (완료 — 코드 수정 1건 GitHub 반영·재확인 완료) — 우측하단 경로안내 박스 크기/레이아웃 개편

- 사용자가 실기기 스크린샷(20260913_183642.jpg) 제공. 요청: 우측하단 경로안내 박스를 좌측하단 디버그 박스(475x495)와 동일 크기로, "도착: 2.4분(18:39) / 0.9km" 순서를 "도착: 0.9km" -> "2.4분(18:39)" 2줄로, 글자크기는 신호과속 라벨과 동일(40)로, 박스가 세로로 길어진 만큼 각 요소가 겹치지 않게 재배치, "route=숫자"는 신호과속이 떠도 겹치거나 사라지지 않도록 항상 우측끝맞춤으로 별도 표시.
- 원인 분석: 우측하단 박스는 _draw_turn_info_hud()(기존 790x300 고정). "route=숫자"는 carrot_serv.py의 self.debugText(f"route={{route_speed:.1f}}")가 carrotMan.szPosRoadName(도로명)에 공백으로 이어붙어 들어오는 값이며, 기존 코드는 if 신호과속(sdi_descr) / elif 도로명 구조라 신호과속이 뜨면 route= 값이 도로명과 함께 통째로 사라지는 구조였음(원인 확정, 스크린샷과 코드 대조로 확인).
- 적용한 수정(carrot-ryu, selfdrive/ui/onroad/hud_renderer.py만, 최소 변경, commit 5f5e49d0):
  1. import re 추가.
  2. _format_eta_text() -> _format_eta_time_text()로 이름 변경 + "도착:" 라벨 제거(거리 줄과 분리해 두 번째 줄 전용), _split_road_name_debug() 신규 헬퍼 추가(정규식 route=[-0-9.]+ 로 도로명과 route= 디버그 값을 분리).
  3. _draw_turn_info_hud() 레이아웃 재구성: 박스 475x495(좌하단 디버그 박스와 동일), 상단에 안내제목(좌)+route=숫자(우측끝맞춤, 항상 별도 줄), 중단에 회전아이콘+거리, 중하단에 "도착: 거리"/"N.N분(HH:MM)" 2줄(글자크기 40), 하단에 신호과속(또는 도로명) 배지 — 신호과속 배지와 route=숫자가 물리적으로 분리되어 있어 항상 함께 보임.
- 반영 방식: 문자열 블록 치환(Replace-Block, 20차 원칙) 3곳, 치환 전 GitHub 최신(d338afb7) 대비 정확히 1회 매치 확인 후 진행. Python 문법 검증(ast.parse) 통과.
- 실행 이슈 1건 발생 -> 해결: 최초 실행 시 Windows Git의 core.autocrlf로 clone된 파일이 CRLF로 변환되어 있어, LF 기준으로 만든 치환 블록이 import-re 단계에서 0회 매치로 실패 -> 15절/18절/20절 원칙대로 아무 것도 건드리지 않고 안전하게 중단(커밋/푸시 이전이라 carrot-ryu 영향 없음, 임시 폴더도 정상 삭제됨 확인). git clone에 --config core.autocrlf=false 추가 + 읽은 직후 CRLF->LF 정규화 안전장치를 넣어 재작성한 스크립트로 재실행, 정상 반영됨(d338afb7..5f5e49d0).
- 반영 후 재확인: raw.githubusercontent.com으로 carrot-ryu HEAD(5f5e49d0)의 hud_renderer.py를 직접 재조회해, 의도한 변경 외 차이가 없음(diff 1곳, 의도한 주석 라벨 변경)과 ast.parse 문법 통과를 확인함(16절/20절 원칙).
- 사용자에게 변경 후 UI 레이아웃을 설명하는 목업(SVG, 실제 기기 픽셀/폰트와는 다른 개략도)을 별도로 렌더링해 전달함.
- 실차 검증: 미실시(정적 코드 변경 단계, 12절 원칙).


## 26차 (진행 중 — 실기기 검증 결과와 정적 코드 리뷰 결과가 모순되어 원인 미확정, 실기기 디버깅 다음 세션으로 이월) — Google Drive 연결 UI 미노출 재조사

- 세션 시작: 지침 문서 22차 버전 확인 -> HANDOFF.md/CURRENT_STATUS.md(25차 상태, carrot-ryu HEAD d338afb7) 확인 후 진행.
- 사용자가 오늘(2026-09-14) 실기기에서 찍은 스크린샷 10장 제공(14:47~18:41). 내용: 웹 설정 > 로그 업로드에서 업로드 서버를 "구글 드라이브"로 선택한 화면, 화면녹화 세그먼트 전송 시도 및 결과.
- 관찰 1: "웹 설정 > 로그 업로드" 카드의 업로드 서버 드롭다운은 당근서버/토스서버/구글드라이브 3개 옵션이 정상 표시되고 구글드라이브가 선택돼 있음. 그런데 그 아래에는 23차에서 추가한 Client ID/Secret 입력란(web-gdrive-connect 컴포넌트) 대신 "당근서버 주소"/"토스서버 주소" 입력란이 그대로 보임.
- 관찰 2(신규 발견): 화면녹화 탭에서 세그먼트 "전송" 시도 시 다이얼로그 라벨이 "당근서버"로 표시됨(업로드 서버는 구글드라이브로 설정된 상태인데도). 최종적으로 "Google Drive가 연결되어 있지 않습니다" 에러가 뜸 -> 실제 라우팅은 gdrive로 가는 것으로 추정되나 다이얼로그 라벨 텍스트만 하드코딩된 "당근서버"를 쓰고 있는 것으로 보임(코드 위치는 아직 조사 안 함).
- carrot-ryu 최신(commit d338afb7) 소스를 codeload tarball로 직접 받아 정적 코드 리뷰 수행:
  - web/src/features/tools/web_settings/schema.js: log_upload 그룹에 web-upload, web-gdrive-connect 두 항목 모두 정상 존재.
  - web/src/features/tools/web_settings/components.js: web-gdrive-connect 컴포넌트가 Client ID/Secret 입력란을 포함해 정상 등록돼 있음. isVisible을 별도 정의하지 않아 기본값(빈 settingKeys -> every()가 vacuous true)이 적용되므로 이론상 항상 visible이어야 함.
  - web/js/generated/tools.js(esbuild 번들): 위 로직이 소스와 완전히 동일하게 반영돼 있음을 확인 -- 예전에 있었던 "esbuild 번들 재생성 누락" 유형 문제는 이번 소스/번들 비교로는 재현되지 않음.
  - web/css/generated/tools.css: .web-gdrive-settings 관련 셀렉터가 전부 정상 포함돼 있고 display:none 등 숨김 규칙 없음.
  - web-upload 컴포넌트의 당근서버/토스서버 주소 필드는 코드상 target === "carrot" / target === "toss" 일 때만 hidden이 해제되도록 짜여 있어, 스크린샷처럼 target이 "gdrive"인 상황에서는 두 필드가 반드시 숨겨져야 함. 그런데 스크린샷은 정반대(두 필드는 보이고 gdrive 전용 필드는 안 보임) -- 정적 코드 리뷰 결과와 실기기 스크린샷이 모순됨.
- 결론(미확정): 코드 자체에서는 문제를 찾지 못함. 실기기 브라우저가 최신 tools.js/tools.css 번들을 실제로 로드하고 있는지 의심됨(브라우저 캐시, 또는 scons 빌드 시 esbuild 재생성 누락 가능성). 사용자가 이번 세션 중에는 실기기 디버깅(터미널로 배포된 파일 내용 확인, 강제 새로고침/시크릿모드 재현 테스트)을 진행할 수 없어 다음 세션으로 이월.
- 이번 세션은 코드/devnotes 커밋 변경 없이 조사만 진행. carrot-ryu HEAD는 25차와 동일하게 d338afb7 유지.


## 25차 (완료 -- 코드 수정 1건 GitHub 반영 확인, 조사 1건 추가 발견) -- LOG_UPLOAD_TARGETS "gdrive" 누락 수정 + 데드코드/낡은 테스트 의심 발견

- 24차 계속2에서 발견한 확실한 버그(server/services/web_settings.py의 LOG_UPLOAD_TARGETS = {"carrot", "toss"}에 "gdrive" 누락)를 사용자 승인 후 수정. 문자열 치환(소규모 변경, 9절) 방식으로 anchor 1회 매치 검증 -> py_compile 검증 -> 스크립트 전달 -> 사용자 실행 -> commit d338afb7 push 확인 -> raw.githubusercontent.com으로 실제 파일 내용까지 직접 재조회해 `LOG_UPLOAD_TARGETS = {"carrot", "toss", "gdrive"}`로 반영됨을 확인(5절/16절).
- 수정 과정에서 사용자가 "관련 죽은 코드도 같이 삭제하면 안 되나" 요청 -> 조사 결과, 처음 보고했던 것과 달리 web_upload.py의 `UPLOAD_TARGETS`/`selected_upload_settings()`는 carrot_man.py의 `_tmux_toss_only()`(Discord/carrot_logs 진단 전송 시 "Toss 전용이면 스킵" 게이트, 958/1054줄에서 실제 호출)가 사용하는 **살아있는 코드**로 정정 확인됨. 반면 `web_upload.py`의 `tmux_web_target()`과 `server/features/dashcam/upload.py`의 `resolve_upload_target()`/`upload_target_settings()`는 프로덕션 호출자가 없고 테스트에서만 참조되는 **진짜 죽은 코드**로 확인됨.
- 이 3개 함수를 삭제하려고 `server/tests/test_web_upload.py`의 관련 테스트를 조사하던 중, `test_dashcam_upload_completion_notifies_web_server_and_discord`(397번째 줄 부근)가 `upload_jobs.upload_folder_to_web`/`upload_jobs.send_web_upload_complete`를 monkeypatch하는데, 이 두 함수는 **16차(대시캠 업로드를 세그먼트별 HTTP 업로드에서 zip+Google Drive 단일 업로드로 전환)에서 이미 제거되어 현재 upload_jobs.py에 존재하지 않음**을 발견. `monkeypatch.setattr`은 대상 속성이 실존해야 하므로 이 테스트는 16차 이후 갱신되지 않은 채 이미 깨져 있을 가능성이 높음(테스트 스위트를 직접 실행해 확인하지는 못함, openpilot 전체 런타임 의존성 없이는 이 파일만 단독 실행이 어려움).
- 범위가 예상보다 커서(데드코드 3개 삭제 -> 관련 테스트 삭제 -> "16차 전환 이후 방치된 낡은 테스트 뭉치" 가능성) 10절(최소 변경)·17절(세션 크기 관리) 원칙에 따라, 이번 세션에서는 확실한 버그 수정(LOG_UPLOAD_TARGETS)만 반영하고 데드코드 삭제/낡은 테스트 정리는 사용자 결정에 따라 다음 세션으로 이월.
- 상세: FINDINGS.md 2026-09-14 "web_upload.py/dashcam upload.py 데드코드 및 test_web_upload.py 낡은 테스트 의심" 항목 참고.
## 24차 계속2 (완료 -- 조사만, 코드 미수정) -- Google Drive 연결 UI 입력란 미노출 문제 조사 + 리포지토리 외부 변경 사항 확인

- HANDOFF 우선순위 1번(Drive UI 입력란 미노출)을 조사함. 캐싱 가설은 기각(index.html이 매 요청 no-cache로 서빙되고 정적 자산 URL이 콘텐츠 해시로 재작성됨을 코드로 확인, 서비스워커 없음).
- 실제 소스 파일(schema.js/state.js/components.js/render.js)을 Node.js 환경에 그대로 옮겨 renderWebSettingsDialogHtml()을 직접 실행하는 시뮬레이션으로, web-gdrive-connect 컴포넌트가 Client ID/Secret 입력란을 포함해 정상적으로 HTML을 생성함을 실증. 렌더링 로직 자체에는 버그 없음.
- 대신 server/services/web_settings.py의 LOG_UPLOAD_TARGETS = {"carrot", "toss"}에 "gdrive"가 빠져 있는 확실한 버그를 발견(23차에서 프론트엔드 드롭다운에만 옵션을 추가하고 백엔드 enum choices는 갱신 안 함). 아직 코드 수정은 하지 않음 -- 사용자 승인 대기.
- 입력란이 안 보이는 증상 자체는 .web-settings-group__body{overflow:auto} 구조상 스크롤 필요일 가능성이 유력한 가설로 남음(실기기 확인 필요, 미검증).
- 상세: FINDINGS.md 2026-09-14 "Google Drive 연결 UI Client ID/Secret 입력란 미노출 문제 조사" 항목 참고.
- [리포지토리 확인] 이번 체크포인트 전에 GitHub 상태를 먼저 재확인하다가, carrot-ryu-note에 이 세션의 스크립트가 아닌 다른 경로(작성자 "Ryu <ryu@example.com>", PowerShell 스크립트 커밋의 작성자 "ryujmin97"과 다름)로 커밋 2개(7d44f2f, c7b86a0)가 더 있었음을 발견. 7d44f2f가 PROJECT_INSTRUCTIONS_carrot-ryu.md를 실수로 9차 시점 구버전으로 덮어썼고, c7b86a0이 같은 작성자에 의해 22차(98fad93) 상태로 직접 복구됨. 이 세션이 만든 24차 devnotes 커밋(33fcfcc)은 이 두 커밋 사이에 위치하며 PROJECT_INSTRUCTIONS_carrot-ryu.md를 건드리지 않아 영향 없음. 현재 문서는 22차 상태로 정상.
## 24차 계속 (완료 -- GitHub push 확인됨) -- carrot_ryu_24cha_photos.ps1 실행 결과 검증

- 세션 초반에는 carrot-ryu HEAD가 여전히 272834b(23차)로, 24차 스크린샷 스트립 반영 스크립트가 실행되지 않은 상태였음(위 "24차" 항목 참고).
- 세션 도중 사용자가 carrot_ryu_24cha_photos.ps1을 실행: npm 실행 정책 문제(PowerShell 스크립트 차단)를 `Set-ExecutionPolicy -Scope Process -ExecutionPolicy Bypass`로 우회 후 정상 실행. clone -> 문자열 블록 치환 반영 -> commit -> push까지 로그가 끝까지 출력됨(임시 폴더 자동 삭제 포함).
- 5절/16절/20절 원칙에 따라 로그만으로 "완료"로 단정하지 않고, api.github.com 및 raw.githubusercontent.com으로 직접 재조회: carrot-ryu HEAD가 a7a912c1로 갱신되었고, 신규 파일 openpilot/selfdrive/carrot/web/src/features/logs/screenshots.js가 실제로 브랜치에 존재함을 확인.
- 결론: 24차(화면녹화 탭 스크린샷 "사진" 스트립) 코드는 GitHub에 정상 반영 완료(commit a7a912c1). devnotes(HANDOFF.md/CURRENT_STATUS.md)도 이 확인 결과에 맞춰 함께 갱신.
- 남은 작업은 위 "24차" 항목의 "미완료" 목록 중 코드 반영 자체가 아닌 나머지 항목(Drive UI 입력란 미노출 조사, 실제 Drive 연결 테스트, 실주행 재검증 등)으로 이월.
## 24차 (완료 — 코드 반영 스크립트 준비, GitHub push는 사용자 실행 대기) — 화면녹화 탭에 스크린샷(.png) "사진" 스트립 추가

- 배경: 실기기에서 온로드 캡처 버튼(screenshot_capture.py)으로 찍은 .png 스크린샷이 웹 로그탭 어디에도 보이지 않는다는 사용자 보고. server/features/screenrecord/catalog.py의 build_videos()가 SCREEN_RECORDING_EXTS(영상 확장자만)만 스캔해서 .png가 애초에 목록화되지 않는 것이 원인으로 확인됨.
- 사진을 영상 목록(screenrecord.js, 가상 스크롤 적용)에 억지로 섞지 않고, 별도의 작은 비가상화 가로 스트립(screenshots.js, 신규 파일)으로 분리 구현. 사진 개수가 영상 개수보다 훨씬 적을 것으로 예상되어 가상 스크롤의 복잡도를 들일 가치가 없다고 판단.
- 백엔드: config.py에 SCREEN_RECORDING_PHOTO_EXTS(.png/.jpg/.jpeg) 추가, catalog.py에 build_photos()/find_photo()/photo_thumbnail_path() 추가(build_videos() 로직과 의도적으로 코드 공유하지 않고 병행 구현 — 영상 목록 동작이 회귀하지 않도록), routes.py에 /api/screenrecord/photos, /api/screenrecord/photo/thumbnail/{id}, /api/screenrecord/photo/{id}, /api/screenrecord/photo/download/{id} 4개 라우트 추가.
- 프론트엔드: screenshots.js(신규) — loadScreenshots()/renderScreenshots()/openScreenshot() 구현. index.html에 screenrecordPhotosWrap/screenrecordPhotosTitle/screenrecordPhotos 마크업 추가, style.css에 가로 스크롤 스트립 스타일 추가, runtime.js에 import + 로드 훅 4곳 + 클릭 핸들러 바인딩 추가. en/ko/zh 번역 3종에 screenrecord_photos_title/screenrecord_photos_load_failed 키 추가.
- 검증: carrot-ryu 실제 HEAD(272834b, 23차)를 그대로 clone하여 반영 스크립트(문자열 블록 치환, Replace-Block 패턴)를 실제로 적용 -> `npm install && node build.mjs`로 실제 빌드 실행 -> `python -m py_compile`로 수정된 .py 3개 확인 -> `node --test tests/logs_tabbar_contract.test.mjs` 통과 확인. 별도의 독립 시뮬레이션(원본 파일에 동일 블록 치환을 파이썬으로 재현)으로 모든 소스 파일이 바이트 단위로 일치함을 재확인.
- 전달 방식: 9절 규칙대로 코드 파일 여러 곳의 부분 수정이므로 diff가 아닌 문자열 블록 치환(Replace-Block) 방식으로 스크립트 구성, `.ps1` 파일 자체는 21차 규칙대로 UTF-8 BOM 포함하여 생성(`carrot_ryu_24cha_photos.ps1`). js/generated/logs.js, css/generated/logs.css, generated/asset-manifest.json 등 빌드 산출물은 스크립트 안에 손으로 담지 않고, 스크립트가 실제 `node build.mjs`를 실행해 생성하도록 함(18~20차에서 확인된 "손으로 만든 빌드 산출물이 실제 빌드 결과와 달라지는" 위험 회피).
- 미완료: 사용자가 아직 이 스크립트를 실행하지 않은 상태(24차 세션 시작 시 carrot-ryu HEAD가 여전히 272834b/23차인 것으로 GitHub에서 직접 확인). 즉 이번 회차의 코드 변경은 스크립트 형태로만 준비되었고 실제 push는 다음 확인 필요.
- 별도 미해결 이슈(23차 관련, 사용자 실기기 보고): Google Drive 연결 UI의 드롭다운은 "구글 드라이브"로 바뀌었으나 그 아래 Client ID/Secret 입력란과 연결 버튼이 나타나지 않음. 브라우저가 js/generated/tools.js의 이전 캐시를 물고 있을 가능성(캐시 버스팅 부재)이 유력하나 사용자의 하드 리프레시/시크릿창 확인으로 아직 미검증. 다음 세션 우선순위로 이월.

## 23차 (완료 — 코드 반영, GitHub push 완료, devnotes만 소급 기록) — web settings log_upload에 Google Drive 계정 연결 UI 추가

- 배경: 15~22차에 걸쳐 만든 gdrive_upload.py 백엔드(OAuth device flow, params_keys.h 등록까지 완료)에 대응하는 프론트엔드 연결 UI가 없어 사용자가 실제로 Drive 계정을 연결할 방법이 없었음. HANDOFF 미완료 우선순위 1번(15차부터 이월)에 해당.
- carrot-ryu commit 272834b8("23cha: web settings log_upload에 Google Drive 계정 연결 UI 추가 (web-gdrive-connect)")로 이미 GitHub에 반영되어 있었음을 24차 세션 시작 시 발견(devnotes에는 22차까지만 기록되어 있어 16절 해당 괴리 사례).
- 변경 파일(commit 272834b8 기준, GitHub에서 직접 diff 조회로 확인): web/src/features/tools/web_settings/schema.js, web/src/features/tools/web_settings/components.js(174줄 추가, 연결 버튼/Client ID·Secret 입력/인증 코드 표시 UI 구현 추정), web/src/features/tools/styles/base.css(45줄 추가), web/js/translations/{en,ko,zh}.js(각 15줄, 관련 UI 텍스트), 그리고 이에 따른 생성 산출물(tools.js/tools.css/asset-manifest.json) 갱신.
- 24차 세션에서 실제 코드 내용을 상세 분석하지는 않음(이번 세션의 초점은 스크린샷 기능이었음) — 다음 세션에서 필요 시 components.js/schema.js 상세 리뷰.
- 검증: 실차 검증 미실시. 실제 Drive 연결 테스트(OAuth 인증 코드 입력까지)도 미실시. 사용자가 실기기에서 확인한 결과 드롭다운은 바뀌었으나 입력란이 안 보이는 문제가 있었음(24차 항목 참고, 원인 미확정).

## 22차 (완료 — Google Drive 파라미터 등록 버그 발견 및 수정) — params_keys.h 미등록 수정 + PARAMS_REGISTRY.md 정리

- 배경: HANDOFF 다음 작업 후보 중 "PARAMS_REGISTRY.md 파라미터 3종 등록"(가장 가벼운 작업으로 사용자 선택)을 진행하기 위해 gdrive_upload.py의 실제 파라미터 이름(PARAM_CLIENT_ID/PARAM_CLIENT_SECRET/PARAM_REFRESH_TOKEN = CarrotGDriveClientId/CarrotGDriveClientSecret/CarrotGDriveRefreshToken)을 GitHub에서 직접 조회하던 중, openpilot/common/params_keys.h에 이 3개가 전혀 등록되어 있지 않은 것을 발견함.
- 원인: openpilot Params 클래스는 get()/put() 호출 시 내부적으로 checkKey()를 거쳐 params_keys.h에 등록 안 된 키면 UnknownKeyName 예외를 던짐(params_pyx.pyx 101-102줄 확인). gdrive_upload.py의 api_gdrive_device()(Drive 연결 시작 API)는 client_id 저장 단계(_params().put(PARAM_CLIENT_ID, ...))에서 이 예외를 그대로 받아 HTTP 500을 반환하도록 되어 있어, 15차부터 만들어온 Drive 연동 기능 전체가 "연결" 버튼을 누르는 순간부터 실패하는 상태였음(실제 기기 연결 테스트를 아직 안 해봐서 지금까지 미발견 — FINDINGS.md 참고).
- 사용자에게 즉시 보고(11절/16절 원칙) 후 승인받아, 원래 "문서화만" 범위였던 이번 작업을 "코드 수정(params_keys.h) + 문서화(PARAMS_REGISTRY.md)"로 확대함.
- 수정: params_keys.h에 다른 모든 Carrot* 파라미터와 동일한 패턴({PERSISTENT, STRING})으로 3줄 추가. 문자열 블록 치환 방식(CarrotExceptionDiscordWebhookUrl 줄을 앵커로 사용) 적용, carrot-ryu commit 48c2e081.
- 최종 GitHub 반영 확인: raw.githubusercontent.com으로 commit 48c2e081 시점의 params_keys.h를 직접 재조회하여 3줄이 정확한 위치(CarrotExceptionDiscordWebhookUrl 다음, CwebPushRecoveryBoot 이전)에 들어간 것을 확인 완료.
- PARAMS_REGISTRY.md에 이 3개 파라미터(이름/타입/용도)와 버그 경위를 함께 등록.
- 미완료: 실제 기기에서 Drive 연결(OAuth device flow) 테스트 — params_keys.h 수정으로 UnknownKeyName 예외는 해소됐으나, 실제 Google Cloud Console 클라이언트 ID/Secret 발급 및 콤마 기기에서의 연결은 여전히 미실시.

## 21차 (완료 — 소급 기록, 22차 세션에서 devnotes 누락 발견 후 작성) — 반영 방식을 .ps1 파일 생성 + BOM 필수로 개정

- 배경: PROJECT_INSTRUCTIONS_carrot-ryu.md 자체에는 21차 변경사항이 이미 반영되어 있었으나(carrot-ryu-note commit 21da1364, "docs: PROJECT_INSTRUCTIONS_carrot-ryu.md 21차 갱신"), WIP.md/HANDOFF.md/CURRENT_STATUS.md에는 21차 회차 기록이 전혀 없었음. 22차 세션 시작 시 이 불일치를 발견(16절 해당 사례), 사용자 확인 결과 "21차는 실제 있었던 세션, devnotes 기록만 누락"으로 확인되어 이번 커밋에서 소급 기록함.
- 변경 1: 9절 기본 전달 방식을 "스크립트 전체를 채팅에 붙여넣기"에서 ".ps1 파일로 생성해 전달 + 실행 명령만 채팅에 별도 안내"로 전환. 사유: 대용량 교체형 파일(PROJECT_INSTRUCTIONS_carrot-ryu.md 등)을 채팅에 직접 붙여넣는 것이 파일 생성 도구로 전달하는 것보다 무료 사용량(토큰)을 훨씬 많이 쓰는 것이 실측으로 확인됨.
- 변경 2: 9절·18절에 ".ps1 스크립트 파일에 한글 등 비ASCII 문자가 있으면 반드시 UTF-8 BOM을 포함해 생성한다" 규칙 추가. 사유: BOM 없는 .ps1 파일을 Windows PowerShell 5.1이 시스템 코드페이지(CP949 등)로 잘못 읽어, 쓰기 시점 인코딩 지정과 무관하게 스크립트 내 한글 문자열 자체가 이미 손상된 채 커밋되는 사고가 실제 발생함. BOM 포함 스크립트로 재실행해 정상 복구 확인.
- 22차부터 전달하는 모든 .ps1 파일은 이 규칙(파일 생성 도구로 전달 + UTF-8 BOM 포함)을 따름(이번 22차 params_keys.h 수정 스크립트도 BOM 포함하여 정상 실행 확인됨).## 18~20차 (완료 — 코드 반영, GitHub push 완료) — api_dashcam_upload_test를 Google Drive 연결 테스트로 전환

- 배경: HANDOFF 미완료 우선순위 1번(15차부터 이월). dashcam 업로드 연결 테스트 버튼(`/api/dashcam/upload/test`, routes.py의 `api_dashcam_upload_test`)이 16~17차에서 이미 Drive로 전환된 실제 업로드 경로와 달리 여전히 옛 Carrot/Toss 헬스체크(`check_web_upload_health`)를 가리키고 있었음.
- gdrive_upload.py에 `test_connection()` 추가: `is_connected()`가 refresh_token 존재 여부만 보는 것과 달리, 실제 access_token 갱신 + 대상 폴더 조회까지 왕복해 Drive 연동이 실제로 동작하는지 확인.
- routes.py: `api_dashcam_upload_test`를 `gdrive_upload.test_connection()` 호출로 교체, 옛 `web_upload`(check_web_upload_health/create_web_upload_session) import 및 `upload` 모듈 참조 제거.
- test_web_upload.py: 옛 toss/carrot 대상 관련 테스트 2개를 제거하고, 라우트 유일성 1개 + Drive 연결 성공/실패 케이스 2개로 교체.
- ⚠ [중요 교훈] 18차에서 diff/`git apply` 시도가 조용히 실패함 — 스크립트는 에러 없이 "적용 완료"로 끝났으나, 실제로는 patch 파일만 carrot-ryu에 잘못 커밋되고 의도했던 코드 변경은 전혀 반영되지 않음(정확한 근본원인은 사용자 PC를 직접 디버깅할 수 없어 확정 불가, `Apply-Patch` 함수 내부의 반복적인 `Push-Location`/`Pop-Location`이 셸 위치 추적을 꼬이게 한 것으로 추정). 17차(`corrupt patch`로 안전 중단)보다 더 나쁜, 조용히 실패하는 양상이었음.
- 19차에서 방식을 전면 교체: diff 대신 **파일 전체 텍스트에서 블록을 통째로 찾아 `.Replace()`로 치환**(치환 전 블록이 정확히 1회만 존재하는지 검증 후 치환, 아니면 중단), `Push-Location` 대신 `git -C $TempDir`만 사용. 이 방식으로 routes.py/test_web_upload.py 반영 및 18차에서 잘못 커밋된 임시 patch 파일 3개 정리까지 정상 완료(commit a44f1580).
- 다만 19차에서 gdrive_upload.py 하나는 Claude가 anchor 문자열을 잘못 옮겨 적어(`dict[str, Any]` vs 실제 `dict[str, dict[str, Any]]`) 매치 0회로 안전하게 중단됨 — `Replace-Block`의 "정확히 1회 아니면 중단" 안전장치가 의도대로 작동한 사례로, carrot-ryu에는 영향 없었음. 20차에서 GitHub 최신 원본과 anchor를 바이트 단위로 재대조하여 정정, 정상 반영 완료(commit ad055dd4).
- 최종 GitHub 반영 확인: raw.githubusercontent.com으로 ad055dd4 시점의 3개 파일을 모두 직접 재조회하여 `test_connection()` 정의, routes.py import/함수 교체를 확인 완료.
- 사용자 승인 하에 9절을 "코드 파일 부분 수정은 문자열 블록 치환을 기본으로, diff/git apply는 예외적 보조 수단으로" 개정.
- ⚠ [별도 발견] 이번 세션은 채팅에 9차 버전의 PROJECT_INSTRUCTIONS_carrot-ryu.md를 붙여넣은 채로 시작됐으나, 실제 carrot-ryu-note의 GitHub 버전은 이미 12차까지 진행되어 있었음. 20차에서 GitHub 버전(12차) 위에 이번 변경을 반영해 정정.
- ⚠ [WIP.md 반영 후속] 이 회차 자체가 처음 만들어진 20차 devnotes 반영 스크립트에서 `Prepend-Top` 함수에 CRLF 정규화가 빠져 있어("# WIP" marker가 `\r\n` 파일과 불일치) 실패했고, HANDOFF.md/CURRENT_STATUS.md/PROJECT_INSTRUCTIONS만 먼저 commit 450a1cd로 반영됨. 이 회차는 그 직후 별도 후속 커밋으로 반영됨.

## 17차 (완료 -- 코드 반영, GitHub push 완료) -- send_tmux_web() Google Drive 업로드 전환

- 배경: 16차 HANDOFF 미완료 우선순위 1번. tmux 진단 전송(온로드 자동 진단, CAN
  에러, 예외 상황, tmux_send 명령)의 "carrot/toss 선택 전송" 경로가 아직 옛
  Carrot/Toss HTTP 업로드(session 발급 -> multipart POST)를 쓰고 있었음.
- carrot_man.py의 send_tmux_web()을 tmux.log[+toggle_values.json]+metadata.json을
  zip으로 묶어 gdrive_upload.upload_file_resumable()로 업로드하는 방식으로 전면
  재작성.
  - metadata.json에 기존 payload(_tmux_upload_payload: tmux_why, car_name,
    git_branch 등)를 그대로 담아, Carrot/Toss 서버가 받던 진단 필드가 유실되지
    않도록 함(Drive는 별도 DB가 없으므로 파일로 동봉).
  - 파일명: tmux_{car_name}_{tmux_why}_{timestamp}.zip (영숫자/-/_ 외 문자는
    _ 치환)
  - 압축 방식은 ZIP_DEFLATED 선택(16차 대시캠 zip은 이미 압축된 h265/zstd라
    ZIP_STORED였지만, tmux.log/json은 텍스트라 DEFLATE 이득이 있고 콤마 기기
    CPU 부담도 미미함).
  - 동기 메서드(send_tmux_web)에서 비동기 gdrive_upload.upload_file_resumable()을
    호출해야 해서, 파일 내 기존 관례(carrot_navi_http_server 호출부의
    asyncio.run() 패턴)를 그대로 따라 asyncio.run()으로 브릿지.
  - 반환값 계약(web_response.ok / .status_code, 실패 시 None)은 호출부
    (1255/1285/1318/1319행 등)가 그대로 재사용하므로 변경하지 않음 --
    성공 시 SimpleNamespace(ok=True, status_code=200, drive_result=...)를
    반환, 실패 시 기존과 동일하게 예외를 잡아 None 반환.
  - send_tmux_carrot_logs()(Discord carrot_logs 포럼용 독립 고정 전송)는 이번
    변경과 무관하며 손대지 않음(HANDOFF 지침대로).
  - import 정리: create_web_upload_session_sync, tmux_web_target은 이 함수에서만
    쓰였는데 더 이상 필요 없어 import 목록에서 제거(10절 최소 변경 원칙 -- 직접
    관련된 dead import 제거만, 그 외 리팩터링 없음). read_web_settings/
    selected_upload_settings는 _tmux_toss_only()가 계속 사용하므로 유지.

- ⚠ [중요 교훈] diff(git apply) 방식 최초 실전 시도가 실패함:
  - 9차 세션에서 도입한 "파일은 크지만 변경 범위가 작은 경우 unified diff 사용"
    원칙에 따라 처음에 diff/git apply 스크립트를 전달했으나, 사용자 실행 시
    `error: corrupt patch at ...patch:101`로 git apply --check 단계에서 실패.
  - 원인 추정: git diff의 컨텍스트 공백 줄(빈 줄, 들여쓰기 공백)이 채팅
    복사/붙여넣기 과정에서 손상됨(트레일링 공백 유실 등). PowerShell here-string
    자체의 CRLF/LF 정규화로는 해결되지 않는 종류의 손상.
  - 대응: 15/18절 원칙대로 git apply 실패 시 스크립트가 즉시 중단되어 carrot-ryu에
    어떤 손상도 남기지 않음(HEAD는 cc734e18 그대로 유지됨을 GitHub API로 재확인).
    강제 적용(--3way/--reject 등)은 시도하지 않음.
  - 최종 해결: diff 대신 "문자열 치환(find & replace) 방식"으로 전환. 변경 전/후
    블록을 통째로 here-string으로 담고, 치환 전 `[regex]::Matches(...).Count -eq 1`로
    "정확히 1회만 매치"하는지 검증한 뒤에만 치환 실행(매치 0회/2회 이상이면 아무
    것도 바꾸지 않고 중단) -- 이 방식이 diff보다 채팅 복사 손상에 훨씬 강함.
  - 문자열 치환 스크립트로 재시도 -> 3개 블록 모두 1회 매치 확인 -> 치환 ->
    py_compile 통과 -> commit/push 성공(commit 2869149, GitHub API/git ls-remote로
    재확인 완료).
  - [다음 세션부터 반영할 원칙 제안, 19절 절차로 사용자 승인 필요]: 9절의 diff
    옵션을 "1순위"가 아니라 "문자열 치환으로 처리하기 어려운 경우(같은 텍스트가
    여러 곳에 나타나 유일 매치를 만들 수 없는 대규모/분산 변경)의 대안"으로
    재조정하는 것을 고려. 문자열 치환은 (a) 유일 매치 검증이 가능해 채팅 복사
    손상에 강하고 (b) git apply의 컨텍스트 줄 민감도 문제가 없음. 아직 문서
    변경은 하지 않았고, 다음 세션에 사용자 승인받아 9절을 수정할지 결정.
- 반영 방식: 문자열 치환(위 사유로 diff에서 전환) -- import 블록 2곳 + 함수 본문
  1곳, 총 3개 블록. 실제 carrot-ryu clone에서 각 블록 유일 매치(count=1) 확인 +
  치환 후 py_compile 통과 확인 후 commit/push.
- 검증: 정적 분석 + 실제 GitHub carrot-ryu에 반영 후 최신 HEAD(2869149)를
  git ls-remote로 재확인 완료. 실제 Google Drive 업로드 테스트, 실차 검증은
  미실시.
- 미완료: PARAMS_REGISTRY.md에 Drive 파라미터 3종 아직 미등록(15차부터 이월,
  16차 HANDOFF 우선순위 4). CURRENT_STATUS.md가 13차 시점에서 갱신이 멈춰 있던
  것을 17차에서 16~17차분까지 소급 반영.
## 16차 (완료 -- 코드 반영 + hotfix) -- upload_jobs.py zip+Drive 재작성 + app.py 연결 + 반영 스크립트 버그 3종 발견/수정

- 배경: 15차에서 만든 gdrive_upload.py가 아직 아무 데서도 호출되지 않는
  상태였음(15차 HANDOFF 우선순위 1a/1c). 이번 세션에서 실제로 연결.
- 1) gdrive_upload.py: upload_file_resumable()에 progress_cb(sent, total)
  콜백 파라미터 추가. 호출자가 자체 진행률/취소 체계를 가질 때 바이트 단위
  진행률을 전달받기 위함. 콜백에서 예외를 던지면 그대로 전파되어 업로드 중단.
- 2) server/features/dashcam/upload_jobs.py: run_upload_segments() 전면
  재작성. 세그먼트별 개별 스트리밍 업로드(Carrot/Toss 대상) -> 세그먼트
  파일들을 zip(무압축 ZIP_STORED)으로 묶어 gdrive_upload.upload_file_resumable()
  로 단일 업로드하는 방식으로 전환. job/progress/취소/Discord 알림 골격은
  유지, 내부 구현만 교체(10절 최소 변경 원칙).
  - 설계 변경: 성공/실패 판정이 "세그먼트별" -> "zip 전체 단위"로 바뀜.
    Discord 알림을 target 무관 항상 시도하도록 변경(기존엔 carrot일 때만).
- 3) server/app.py: gdrive_upload.register(app) 앱 진입점 연결
  (15차 HANDOFF 우선순위 1c 완료).
- 4) server/services/dashcam_upload_report.py: gdrive 대상일 때
  "Open & Analyze" 구간 링크 생성 스킵 (이번 세션에 새로 발견).
- **반영 과정에서 스크립트 버그 3종을 실전에서 발견/수정함** (전부 Claude
  샌드박스 리허설로는 못 잡았던, 사용자 실제 Windows PC 환경에서만
  드러난 문제들 -- 앞으로 반영 스크립트 작성 시 반드시 유의할 것):
  a) **CRLF 정규화 누락**: Windows git의 core.autocrlf로 로컬 체크아웃 시
     .py 파일이 CRLF로 변환됨. PowerShell 문자열 치환 코드가 LF(`` `n ``)
     기준으로 .Contains()/.Replace()를 했다가 실패 -> 이후 파일을 읽을 때
     항상 CRLF/CR을 LF로 정규화하는 Read-Utf8Lf 헬퍼를 표준으로 채택.
  b) **상대경로 vs 프로세스 작업 디렉터리 불일치**: PowerShell의
     Push-Location/Set-Location으로 "현재 위치"를 옮겨도 .NET
     [System.IO.File]::WriteAllText 같은 API는 그 위치를 따라가지 않고
     실제 프로세스 작업 디렉터리(예: C:\WINDOWS\system32)를 기준으로
     상대경로를 해석함 -> 이후 모든 파일 I/O 경로는 $TempDir 기준
     절대경로(Join-Path)로 고정하는 것을 표준으로 채택.
  c) **PowerShell here-string(`@' ... '@`) 끝 개행 소실**: 닫는 줄(`'@`)
     바로 앞의 개행이 문자열에 포함되지 않아, 줄바꿈을 포함해야 하는
     교체 텍스트 끝에 개행이 누락됨 -> dashcam_upload_report.py에
     `else []  if runs:` 처럼 두 줄이 한 줄로 붙는 문법 오류가 실제로
     **한 번 GitHub에 push된 채로 남아있었음**(commit dae901ce). hotfix
     커밋(cc734e18)으로 즉시 수정. 앞으로 here-string으로 만드는 교체
     텍스트는 항상 명시적으로 끝에 개행이 있는지 눈으로 재확인할 것.
  d) (버그는 아니지만 함께 발견) **py_compile 실패가 스크립트를 멈추지
     못함**: `python -m py_compile`이 SyntaxError로 실패(exit code != 0)
     했는데도 PowerShell이 이를 종료 오류로 인식하지 못해 그대로
     commit/push까지 진행됨(외부 프로세스의 비정상 exit code는
     $ErrorActionPreference="Stop"의 대상이 아님) -> 이후 `$LASTEXITCODE`
     를 명시적으로 확인해 0이 아니면 throw하도록 표준화.
- 결과: dae901ce(문법 오류 포함, 실사용 불가 상태로 짧게 존재)
  -> cc734e18(hotfix, 정상)까지 push 완료 확인. GitHub 실제 파일(4개)을
  codeload tarball로 재조회해 py_compile 전부 통과 재확인함(16절 원칙:
  스크립트 출력만 믿지 않고 GitHub 실제 상태로 재검증).
- 반영: 9절 방식. 1차 스크립트(diff 2개 + 문자열치환 2개) 실행 중
  app.py 단계에서 CRLF 문제로 1차 실패 -> 수정판 실행 중 상대경로 문제로
  2차 실패 -> 수정판2로 4개 파일 반영 성공(dae901ce)하되
  dashcam_upload_report.py에 here-string 개행 버그로 인한 문법 오류
  포함된 채 push됨 -> hotfix 스크립트로 해당 한 줄만 수정해 push(cc734e18)
- 실차 검증: 미실시(정적 분석 + mock 시뮬레이션만. 실제 Google Drive
  계정/토큰 업로드 테스트 없음. carrot-ryu가 콤마 디바이스에 설치되어
  실제로 대시캠 업로드 버튼을 눌러봐야 최종 검증됨)

## 15차 (진행 중 -- Carrotweb 구글드라이브 전환 범위 확정 + gdrive_upload.py 신규 모듈) -- web_upload.py Carrot/Toss -> Drive 2단계

- 배경: 14차에서 설계 방향(zip 압축 후 Drive 업로드)까지는 정리했으나
  tmux 진단/Discord 웹훅 처리 여부가 미결이었음. 이번 세션에서 사용자와
  범위를 재확인
- 1단계 - carrot-ryu 실제 구조 재확인 (codeload tarball, 리포 루트 밑에
  `openpilot/` 서브폴더가 한 겹 더 있음 확인 -- 이후 스크립트의 파일
  경로는 모두 `openpilot/selfdrive/carrot/...` 기준):
  - `selfdrive/carrot/web_upload.py`(333줄): Carrot/Toss HTTP 업로드 +
    tmux/carrot_logs 진단 전송 함수가 **한 파일에 공존**
  - `server/features/dashcam/upload_jobs.py`(663줄): 세그먼트별 동시
    스트리밍 업로드, 바이트 단위 진행률 추적
  - `server/features/dashcam/upload.py`: `resolve_upload_target()`,
    `discord_webhook_url()`/`send_discord_webhook()`(대시캠 업로드 완료
    알림용, tmux/carrot_logs 포럼과는 별개의 또 다른 Discord 웹훅임)
- 2단계 - **중요 구조 발견**: `log_upload_target`(carrot/toss) 설정
  하나가 서로 다른 두 시스템에서 공유되고 있었음
  1. 로그탭 "전송" 버튼(대시캠 세그먼트 업로드,
     `upload_jobs.py` -> `upload.resolve_upload_target()`)
  2. tmux 진단 전송 중 "선택 전송"(`carrot_man.py` ->
     `send_tmux_web()` -> `selected_upload_settings()`)
  - 반면 `send_tmux_carrot_logs()`(Discord `carrot_logs` 포럼용)는 대상
    URL이 `tmux.carrotpilot.app`으로 고정이고 `log_upload_target`은
    "Toss 전용이면 이 전송을 건너뛴다"는 `_tmux_toss_only()` 체크에만
    쓰임 -- 완전히 별개는 아니지만 대상 자체는 공유하지 않음
  - `web_settings.py`의 `LOG_UPLOAD_TARGETS = {"carrot","toss"}`,
    `log_upload_target` enum 필드가 이 모든 것의 공통 데이터 소스
- 3단계 - 사용자와 범위 확정 (2번의 확인 질문 거침):
  - 로그탭 "전송" 버튼(대시캠 업로드) -> Drive: 기존 확정 유지
  - tmux 진단 중 "carrot/toss 선택 전송"(`send_tmux_web()`) -> **이번에
    Drive로 추가 확정**
  - tmux 진단 중 "Discord carrot_logs 포럼용 고정 전송"
    (`send_tmux_carrot_logs()`) -> **그대로 유지** (Drive로 바꾸지 않음,
    Discord 봇이 소비하는 고정 엔드포인트라 구조가 다름)
  - `log_upload_target`/`LOG_UPLOAD_TARGETS`/`web_settings.py` 스키마
    자체는 건드리지 않기로 함(`_tmux_toss_only()`가 계속 이 값을 참조
    하므로) -- 다만 대시캠 업로드와 `send_tmux_web()`이 모두 Drive로
    이관되면 `log_upload_target`은 "carrot_logs 포럼 스킵 여부" 판단
    외에는 실질적으로 안 쓰이게 됨(설계상 다소 어색하지만 최소 변경
    원칙에 따라 이번엔 그대로 둠 -- 정리 필요성은 다음 세션 이월)
- 4단계 - c3-ms-dev의 `server/gdrive.py`(511줄, OAuth Device
  Authorization Grant + resumable 업로드) 재확인:
  - codeload로 다시 받아보니 **원본(폴더 이름 자동검색, drive.file
    스코프) 상태**였음 -- 14차에서 언급된 "폴더 ID 고정 + 전체 스코프"
    치환은 사용자 로컬(C:\dev\ryu)에서만 확인됐고 c3-ms-dev 원격 브랜치
    에는 반영 안 된 것으로 추정(다음 세션에서 재확인 필요, 우선순위는
    낮음 -- carrot-ryu 포팅에는 영향 없음)
  - carrot-ryu 이식본은 이 원본을 기준으로, 처음부터 폴더 ID 고정
    (`DRIVE_FOLDER_ID`) + `drive`(전체) 스코프로 직접 작성함
- 5단계 - 신규 모듈 `openpilot/selfdrive/carrot/gdrive_upload.py` 작성
  (Claude 샌드박스에서 py_compile 통과 확인, 사용자 PC 환경 기준 검증은
  아직):
  - OAuth Device Flow 엔드포인트(status/device/token/disconnect) +
    `upload_file_resumable()`(8MB 청크 resumable PUT) + job 진행률 추적
    -- c3-ms-dev와 동일 패턴
  - `_ensure_folder()`(이름 검색/자동생성) 대신 `_verify_folder()`(고정
    ID 존재/휴지통/타입 검증만, 신규 생성 안 함)로 교체
  - 위치를 `selfdrive/carrot/gdrive_upload.py`에 둔 이유: `web_upload.py`
    와 같은 레벨에 둬야 `carrot_man.py`(server/ 밖에 위치)와
    `server/features/dashcam/upload_jobs.py`(server/ 안에 위치) 양쪽에서
    같은 상대 경로 부담 없이 import 가능
  - `register(app)`은 인증/상태조회/job조회 엔드포인트만 등록. 실제
    "업로드 시작"(zip 압축, tmux 로그 전송)은 각 호출부가
    `upload_file_resumable()`을 직접 호출하는 방식으로 다음 세션에 연결
    예정(아직 미연결)
  - 반영: 9절 방식(신규 파일, PowerShell 스크립트) `apply_15_gdrive_module.ps1`
    로 carrot-ryu 브랜치에 전달함
- 실차 검증: 미실시(신규 모듈 작성 + 문법 검증만, 실제 업로드 동작
  테스트 없음. `upload_jobs.py`/`carrot_man.py`와 아직 연결 전이라 단독
  실행도 불가능한 상태)

## 13차 (완료 — 온로드 시계 좌측 화면 경계 잘림 버그 수정) — hud_renderer.py _draw_date_time() x좌표 보정

- 배경: 사용자가 실제 화면 사진(2026-09-13 23:32:34 촬영)을 공유, 좌측 상단
  시계가 "23:32:34"가 아니라 "3:32:34"로 보여 맨 앞 "2"가 잘림을 보고
- 원인 분석 (코드 레벨):
  - openpilot/selfdrive/ui/onroad/hud_renderer.py의 _draw_date_time()에서
    시계 텍스트(HH:MM:SS, font_size=100)를 align="center_bottom"으로 그리는데,
    기준 x가 rect.x+170(고정값)
  - text_draw.py의 get_text_draw_pos()는 center_bottom일 때
    draw_x = x - text_size.x*0.5 로 계산 -> 텍스트 폭이 넓을수록 draw_x가
    더 왼쪽으로 밀림
  - 8자 "HH:MM:SS" 폭이 넓어 draw_x가 음수(화면 밖)로 계산되어 좌측 첫 글자
    (시 10의 자리)가 잘림 (사진 현상과 일치)
  - 12차에서 시계 캐시 키에 tm_sec을 추가하며 "%H:%M"(5자) -> "%H:%M:%S"(8자)
    로 표시 자릿수가 늘어난 것이 이 clipping을 유발한 회귀로 추정
- 수정: measure_text_cached로 시계 텍스트 실측 폭을 구해, 좌측 여백
  (UI_CONFIG.border_size=30)을 보장하도록 x를 동적으로 보정(clamp)하는 로직
  추가. 날짜 텍스트(MM-DD(요일))는 동일 x를 재사용해 시계와 세로 정렬 유지
- 파일: openpilot/selfdrive/ui/onroad/hud_renderer.py, _draw_date_time()만
  수정(10절 최소 변경 원칙)
- 반영 방식: 9절 diff(git apply) 방식. 반영 직전 GitHub 최신
  hud_renderer.py를 다시 조회해 그 위에서 diff 생성, 별도 clone
  시뮬레이션에서 git apply --check/git apply 성공 + py_compile 통과 확인
  (Claude 샌드박스, 사용자 PC python 환경과 무관)
- 실차 검증: 미실시(정적 분석 + 코드 시뮬레이션만)

## 12차 (완료 — 코드 반영 + 반영 프로세스 디버깅) — 더블탭 대신 화면 중앙 하단 스크린샷 버튼 + 온로드 시계 초단위 표시(재반영)

- 배경: 11차에서 설계했던 "더블탭으로 스크린샷" + "시계 초단위 표시"가 실제로는
  GitHub에 반영되지 못한 채(패치 적용 실패 반복) 이번 12차까지 넘어옴. 이번
  세션에서 설계를 바꿔 실제로 반영을 완료함.
- 설계 변경: 더블탭 제스처(augmented_road_view.py 수정) 대신, 온로드 화면 중앙
  하단에 항상 보이는 버튼(ScreenshotButton, 지름 140px 원형 카메라 아이콘)을
  새로 추가하는 방식으로 재설계. 기존 단일 탭(사이드바 토글)과 겹치지 않도록
  명시적 탭 대상만 사용.
  - 신규 파일: selfdrive/ui/onroad/screenshot_button.py (버튼 위젯, pyray로
    원형 카메라 아이콘 직접 그림)
  - 신규 파일: selfdrive/ui/onroad/screenshot_capture.py (11차와 동일한 로직 —
    take_screenshot()으로 cwd에 저장 후 SCREEN_RECORDING_DIRS[1]로 이동)
  - hud_renderer.py: ScreenshotButton import, __init__에서 인스턴스 생성,
    _render 하단 중앙에 배치, user_interacting()에 버튼 눌림 상태 포함
  - hud_renderer.py: 11차 계획대로 시계 캐시 키에 tm_sec 추가,
    "%H:%M" -> "%H:%M:%S"
  - 이번 회차에서는 augmented_road_view.py 더블탭 판정 코드는 적용하지 않음
    (설계 변경으로 불필요) — 11차 WIP 기록의 더블탭 관련 서술은 이번 재설계로
    대체됨
  - 11차가 계획했던 backend(config.py의 SCREEN_RECORDING_IMAGE_EXTS,
    catalog.py의 kind 구분)와 frontend(screenrecord.js/runtime.js의 이미지
    뷰어 액션) 변경은 이번 12차에 포함되지 않음 — 스크린샷 파일은 폴더에
    저장되지만, carrotweb 로그탭에서 정지 이미지로 정상 표시/재생될지는
    미확인 상태로 남음(다음 세션 후보)
- 반영 프로세스 디버깅(참고용, 앞으로 비슷한 실수 방지):
  1. 최초 diff에 PowerShell Set-Content -NoNewline으로 diff 파일 끝 개행이
     빠져 "corrupt patch" 발생 -> -NoNewline 제거로 1차 수정
  2. 그 다음 "patch does not apply" 발생 -> 처음엔 core.autocrlf 체크아웃
     변환을 원인으로 추정했으나, Claude 샌드박스에서 실제 GitHub 최신
     hud_renderer.py를 직접 받아(raw.githubusercontent.com이 네트워크 허용
     도메인이라 컨테이너에서 바로 curl 접근 가능함을 확인) LF/CRLF/BOM 각각
     재현 테스트했지만 모두 정상 적용됨 -> 이 진단은 근거 부족으로 폐기
  3. BOM 회피를 위해 Set-Content를 [System.IO.File]::WriteAllText 기반
     헬퍼로 바꿨다가, PowerShell here-string이 마지막 줄 개행을 보존하지
     않는 특성 때문에 diff 파일에 "corrupt patch"가 재발 -> 헬퍼에 "끝에
     개행 없으면 추가" 로직을 넣어 최종 해결(샌드박스에서 재현/수정 모두 검증)
  4. py_compile 단계에서 원인불명 실패 -> 실제로는 이 PC에 진짜 Python이
     없고 Windows "App Execution Alias" 더미 python.exe만 있어서 발생.
     Claude 샌드박스의 실제 Python으로 3개 파일 모두 문법 검증 완료(정상)로
     대체 확인. 스크립트의 python 감지 로직(Get-Command python)이 이 더미를
     걸러내지 못하는 문제는 아직 미수정(다음 세션 후보)
  5. 반영 스크립트의 git add -A 범위에 diff 파일 자체(hud_renderer.diff)가
     포함되어 carrot-ryu에 잘못 커밋됨 -> git rm으로 후속 커밋(4f4f8a8)에서
     제거, GitHub raw로 삭제 확인(단, raw.githubusercontent.com CDN 캐시로
     약 5분간 이전 내용이 잠깐 더 보일 수 있음 확인)
- 검증: Claude 샌드박스에서 실제 GitHub 최신 파일 기준 diff 적용 성공 확인,
  py_compile 통과(3개 파일) 확인. GitHub push 후 raw.githubusercontent.com으로
  반영 내용 재확인(ScreenshotButton import/사용, second_key 로직 모두 확인됨)
- 실차 검증: 미실시
- carrot-ryu HEAD: 12차 완료 후 4f4f8a8 (684b30d에서 hud_renderer.diff
  오커밋 제거)

> **[94차, devnotes 표기 추가 · 코드 변경 없음]** 아래 11차~1차 회차 기록은 과거(정확한 발생 시점 미상) 인코딩 사고로 텍스트가 손상되어 있음을 확인함. 역변환(CP949 재인코딩 -> UTF-8 재디코딩)을 시도했으나 160곳 이상에서 문자 자체가 이미 제어문자로 치환되어 있는 등 여러 단계의 손상이 겹쳐 있어 byte-exact 복구가 불가능함을 확정함(추측 아님, 실제 역변환 시도로 확인). 7절 원칙에 따라 원문은 그대로 보존하며 삭제/수정하지 않음. 해당 회차들의 요약은 `PROJECT_INSTRUCTIONS_carrot-ryu.md`의 "핵심 발견 1~8" 및 `CURRENT_STATUS.md`에 정상 텍스트로 남아있으니 참고할 것.

## 11李?(?꾨즺 ??肄붾뱶 ?섏젙) ???붾툝??罹≪퀜 ?ㅽ겕由곗꺑 + ?⑤줈???쒓퀎 珥덈떒???쒖떆

- ?ъ슜???붿껌 1: ?⑤줈???붾㈃ 醫뚯긽???쒓퀎媛 遺??⑥쐞濡쒕쭔 媛깆떊?섏뼱 珥??⑥쐞 ?쒖떆媛 ?꾩슂
  - 肄붾뱶 ?꾩튂: selfdrive/ui/onroad/hud_renderer.py??_refresh_date_time_text()
  - ?먯씤: 罹먯떆 ?ㅺ? tm_min源뚯?留??ъ슜??媛숈? 遺??덉뿉?쒕뒗 媛깆떊??嫄대꼫?
  - ?섏젙: 罹먯떆 ?ㅼ뿉 tm_sec 異붽?, ?щ㎎ "%H:%M"  "%H:%M:%S"濡?蹂寃?(18:36:02 ?뺤떇, 留ㅼ큹 媛깆떊)
- ?ъ슜???붿껌 2: ?⑤줈???붾㈃???붾툝??븯硫??ㅽ겕由곗꺑??李띿뼱 carrotweb 濡쒓렇??쓽
  "?붾㈃?뱁솕" 紐⑸줉?먯꽌 諛붾줈 蹂댁씠寃??섍퀬 ?띠쓬
  - ?붾툝???먯젙: selfdrive/ui/onroad/augmented_road_view.py??_handle_mouse_press()??    0.4珥?0px ?대궡 ?ы꺆?대㈃ ?붾툝??쑝濡?蹂대뒗 ?먯젙 濡쒖쭅 異붽?(_check_double_tap_screenshot).
    湲곗〈 ?⑥씪 ???대┃(?ъ씠?쒕컮 ?좉?)怨?HUD ?명꽣?숈뀡 以?臾댁떆 ?숈옉? 洹몃?濡??좎?
  - 罹≪퀜: ???뚯씪 selfdrive/ui/onroad/screenshot_capture.py 異붽?. pyray??    take_screenshot()?쇰줈 PNG ??? ????꾩튂??SCREEN_RECORDING_DIRS[1]
    (/data/media/0/screenrecord) ??carrotweb???대? ?ㅼ틪 以묒씤 ?대뜑??蹂꾨룄 諛섏쁺 ?놁씠
    ?먮룞 ?몄텧
  - 諛깆뿏??selfdrive/carrot/server/): config.py??SCREEN_RECORDING_IMAGE_EXTS
    (.png/.jpg/.jpeg) 異붽??섍퀬 SCREEN_RECORDING_EXTS???⑹궛. catalog.py??    build_videos()媛 kind="image"/"video" 援щ텇媛믪쓣 ?대젮二쇰룄濡??섍퀬, ?뺤? ?대?吏??    thumbnail_path()?먯꽌 ffmpeg -ss ?먯깋 ?놁씠 諛붾줈 由ъ궗?댁쫰留??섎룄濡?遺꾧린
  - ?꾨줎?몄뿏??selfdrive/carrot/web/): screenrecord.js?먯꽌 kind==="image"???됱?
    data-action??"view-screenrecord-image"濡?諛붽퓭 鍮꾨뵒???뚮젅?댁뼱 ???????뿉??    ?먮낯 ?대?吏媛 ?대━?꾨줉 ?섍퀬, runtime.js???대떦 ?≪뀡 ?몃뱾??異붽?. npm run build濡?    js/generated/logs.js(諛?asset-manifest.json ?댁떆) ?щ퉴??- 寃利? Claude ?뚮뱶諛뺤뒪?먯꽌 GitHub 理쒖떊 肄붾뱶(carrot-ryu, 10李?諛섏쁺 吏곹썑 = e1e587b,
  洹??꾩쓽 ?댁슜 ?녿뒗 鍮?而ㅻ컠 2c33603 "token test" ?ы븿) 湲곗??쇰줈 誘몃━ ?⑥튂 ?곸슜 
  py_compile ?듦낵(?섏젙 Python ?뚯씪 5媛?, node --check ?듦낵(JS ?뚯씪 2媛?, npm run
  build濡?濡쒓렇??踰덈뱾 ?щ퉴???뺤긽 ?꾨즺(esbuild ?먮윭 ?놁쓬)源뚯? ?뺤씤. cereal/capnp
  誘몃퉴?쒕줈 UI ?먯껜 援щ룞/pytest ?ㅽ뻾? ?대쾲?먮룄 遺덇?(9~10李⑥? ?숈씪???쒓퀎)
- ?ㅼ감 寃利? 誘몄떎?? ?ㅼ쓬 ?ㅼ＜?됱뿉???쒓퀎媛 珥??⑥쐞濡?留ㅼ큹 媛깆떊?섎뒗吏, ?⑤줈??  ?붾㈃ ?붾툝?????ㅽ겕由곗꺑??李랁? carrotweb 濡쒓렇??> ?붾㈃?뱁솕 紐⑸줉???대?吏濡??④퀬
  ??븯硫?????뿉???먮낯 ?대?吏媛 ?대━?붿? ?뺤씤 ?꾩슂
- 愿???녿뒗 由ы뙥?곕쭅 ?놁쓬. ?뚯씪 6媛??섏젙(hud_renderer.py, augmented_road_view.py,
  config.py, catalog.py, screenrecord.js, runtime.js) + ?뚯씪 1媛??좉퇋
  (screenshot_capture.py) + 鍮뚮뱶 ?곗텧臾?2媛?js/generated/logs.js,
  generated/asset-manifest.json)

## 10李?(?꾨즺 ??肄붾뱶 ?섏젙) ??RES/+ ?멸쾶?댁? ???ㅼ젙?띾룄媛 ?꾩옱?띾룄蹂대떎 ??븘吏??臾몄젣 ?덉쟾?μ튂 異붽?

- ?ъ슜???쒕낫: 異쒕컻 ??媛??以??? ??50km/h) ?몃뱾 +RES 踰꾪듉?쇰줈 ?щ（利??멸쾶?댁? ??
  ?ㅼ젙?띾룄媛 ?꾩옱?띾룄蹂대떎 ??쾶(?? ??30km/h) ?≫? 湲됯컧?띿씠 諛쒖깮?섎뒗 寃쎌슦媛 ?덈떎??  ?ㅼ궗??利앹긽 蹂닿퀬 (?ㅼ＜??濡쒓렇 ?놁씠 ?ъ슜???ㅻ챸 湲곕컲, ?꾩쭅 rlog濡??ы쁽 ?뺤씤 ??
- 肄붾뱶 ?뺤씤(carrot-ryu 2dbe492 湲곗?, selfdrive/car/cruise.py):
  - `_update_cruise_buttons()`??accelCruise ?멸쾶?댁? 遺꾧린(`_cruise_ready or not
    CC.enabled or CS.cruiseState.standstill`)?먯꽌, `_v_cruise_kph_at_brake`(釉뚮젅?댄겕
    ?쒖젏????ν빐?먮뒗 "?ш컻?? ?띾룄) ?먮뒗 ?꾩쭅 珥덇린?붾릺吏 ?딆? v_cruise_kph 媛믪씠
    ?꾩옱?띾룄(v_ego_kph_set)蹂대떎 ??? 梨꾨줈 洹몃?濡??멸쾶?댁? ?띾룄濡?梨꾪깮?????덈뒗
    寃쎈줈 議댁옱
  - `_v_cruise_kph_at_brake`??釉뚮젅?댄겕 ?ш컻 紐⑹쟻 ?몄뿉 `_auto_speed_up()`???꾨줈?쒗븳
    ?띾룄 ?숆린??濡쒖쭅(`AutoRoadSpeedLimitOffset > 0`???? 留??꾨젅??CC.enabled ?щ??
    臾닿??섍쾶 `nRoadLimitSpeed + offset`?쇰줈 ??뼱?, 726踰?以?遺洹??먯꽌??媛믪씠 梨꾩썙吏?    ???덉뼱, 理쒖큹 ?멸쾶?댁? ?쒖젏???꾨줈?쒗븳?띾룄 湲곕컲????? 媛믪씠 ?⑥븘?덉쓣 媛?μ꽦 ?덉쓬
    (?? `AutoRoadSpeedLimitOffset` 湲곕낯媛믪? -1?대씪 ?ъ슜?먭? ???듭뀡??耳?寃쎌슦?먮쭔
    ?대떦 寃쎈줈媛 ?대┝ - PARAMS_REGISTRY????媛?誘멸린濡앹씠????李⑤웾 ?ㅼ젙? 誘명솗??
  - `SpeedFromPCM`??1???꾨땶 湲곕낯 ?ㅼ젙(0 ???먯꽌??openpilot ?먯껜 v_cruise_kph 濡쒖쭅??    ?곗씠誘濡???寃쎈줈媛 ?ㅼ젣濡??곹뼢??以????덉쓬(1?대㈃ ?쒖젙 SCC 媛믪쓣 洹몃?濡?? - ??    寃쎌슦 臾몄젣媛 ?덈떎硫??쒖젙 ECU 履??댁뒋?대?濡??대쾲 肄붾뱶?섏젙 ????꾨떂)
- ?섏젙: 理쒖냼 蹂寃??먯튃???곕씪 ?멸쾶?댁? 遺꾧린 留덉?留됱뿉 ?덉쟾?μ튂(floor)留?異붽?.
  怨꾩궛???멸쾶?댁? ?띾룄媛 "?꾩옱?띾룄 + ENGAGE_SPEED_MARGIN_KPH(2km/h)"蹂대떎 ??쑝硫?  "?꾩옱?띾룄 + 2km/h"濡??щ┝. 釉뚮젅?댄겕 ????λ맂 ?띾룄媛 ?꾩옱?띾룄蹂대떎 ?믪? ?뺤긽?곸씤
  ?ш컻(?? 而ㅻ툕?먯꽌 媛먯냽 ??RES濡??댁쟾 ?ㅼ젙?띾룄濡?蹂듦?) 耳?댁뒪??洹몃?濡??좎???  (洹?媛믪씠 floor蹂대떎 ?щ?濡??곹뼢 ?놁쓬)
- 寃利?
  - 臾몃쾿寃利?py_compile) ?듦낵
  - 湲곗〈 `test_carrot_cruise_buttons.py`???멸쾶?댁? 愿???뚯뒪??4嫄?    (`test_accel_restores_at_least_brake_speed_while_cruise_is_off` 2嫄?
    `test_accel_keeps_initialized_speed_without_brake_snapshot_while_cruise_is_off`,
    "釉뚮젅?댄겕 ?????믪? ?띾룄濡??뺤긽 ?ш컻" ?좉퇋 耳?댁뒪)???숈씪 濡쒖쭅?쇰줈 ?ы쁽??    standalone ?⑹꽦 ?ㅽ겕由쏀듃濡?寃곌낵 ?쇱튂 ?뺤씤 (?뚮뱶諛뺤뒪??cereal/capnp 鍮뚮뱶媛 ?놁뼱
    pytest ?먯껜 ?ㅽ뻾? 9李⑥? ?숈씪?섍쾶 遺덇?)
  - ?ъ슜?먭? 蹂닿퀬??"50km/h 二쇳뻾 以?RES ??30km/h濡?湲됯컧?? ?쒕굹由ъ삤瑜??숈씪 濡쒖쭅?쇰줈
    ?ы쁽 ???섏젙 ??52km/h(?꾩옱?띾룄+2)濡??멸쾶?댁??⑥쓣 ?⑹꽦 ?뚯뒪?몃줈 ?뺤씤
- ?ㅼ감 寃利? 誘몄떎?? ?ㅼ쓬 ?몄뀡/?ㅼ＜?됱뿉???숈씪 ?곹솴(異쒕컻 媛??以?RES ?멸쾶?댁?) ?ы쁽
  ??湲됯컧?띿씠 ?щ씪議뚮뒗吏 ?뺤씤 ?꾩슂
- 愿???녿뒗 由ы뙥?곕쭅 ?놁쓬, ?뚯씪 1媛?cruise.py)留??섏젙, 12以?異붽?


## 9李?(?꾨즺 ??肄붾뱶 ?섏젙) ??route 而ㅻ툕 ?ㅺ?異?洹쇰낯?섏젙: median ?ㅽ뙆?댄겕 ?꾪꽣 異붽?

- 8李⑥뿉???ㅼ＜??濡쒓렇濡??뺤씤??route 媛먯냽 ?ㅺ?異쒖뿉 ??? ?ъ슜?먭? 洹쇰낯?섏젙(?듭뀡 ??
  ?좏깮
- carrot_man.py??carrot_navi_route()瑜??섏젙: 3??怨〓쪧??癒쇱? ?꾨? 怨꾩궛????
  3-?섑뵆 ?щ씪?대뵫 median ?꾪꽣瑜??곸슜?섍퀬 洹?寃곌낵濡쒕쭔 紐⑺몴?띾룄 ?곗텧?섎룄濡?援ъ“ 蹂寃?  (鍮꾩쟾 而ㅻ툕 curve_speed.py???대? ?덈뜕 median ?꾪꽣 諛⑹떇??route 履쎌뿉???숈씪 ?곸슜)
- 理쒖냼 蹂寃??⑥닔 ????釉붾줉留?援먯껜), Claude ?뚮뱶諛뺤뒪?먯꽌 GitHub 理쒖떊 肄붾뱶濡?誘몃━
  ?⑥튂 ?곸슜/臾몃쾿寃利?diff 寃利????ㅽ겕由쏀듃濡??꾨떖 ???ъ슜?먭? Termux?먯꽌 ?ㅽ뻾,
  carrot-ryu 釉뚮옖移섏뿉 諛섏쁺 ?꾨즺 (commit 0201519..2dbe492)
- ?ㅽ겕由쏀듃 ?ㅽ뻾 以???媛吏 ?댁뒋 諛쒖깮 諛??닿껐: ?쟦eredoc ???쒓? ?띿뒪?멸? Termux
  遺숈뿬?ｊ린 怨쇱젙?먯꽌 以꾨컮轅덉씠 源⑥졇 ?덉뼱?낆씠 ???ロ엺 臾몄젣(?ъ떆?꾨줈 ?닿껐, ?ㅼ젣 諛섏쁺
  ?????곹깭?먯꽌 以묐떒?먮뜕 寃??뺤씤) ?죊it diff媛 less ?섏씠?瑜??꾩슦硫??붾㈃??瑗ъ뿬
  ?멸퉴吏 源⑥쭊 臾몄젣(GIT_PAGER=cat, --no-pager diff --stat濡??닿껐). ???댁뒋 紐⑤몢
  肄붾뱶/devnotes???ㅼ젣 ?먯긽 ?놁씠 ?덉쟾?섍쾶 ?ъ떆?꾨줈 ?닿껐??- ?⑹꽦 ?뚯뒪?몃줈 ?꾪꽣媛 ?⑤컻??怨〓쪧 ?ㅽ뙆?댄겕瑜??쒓굅?섎㈃???뺤긽 而ㅻ툕???좎??⑥쓣 ?뺤씤
- ?ㅼ감 寃利? 誘몄떎?? ?ㅼ쓬 ?ㅼ＜?됱뿉???숈씪 遺꾧린???ы넻怨???rlog濡??ы솗???꾩슂

## 8李?(?꾨즺 ???ㅼ＜??濡쒓렇 遺꾩꽍) ??route 媛먯냽 ?ㅺ?異?理쒖큹 ?ㅼ쬆

- ?ъ슜?먭? ?ㅼ젣 肄ㅻ쭏 ?붾컮?댁뒪 二쇳뻾 濡쒓렇(route 000003fb--8470375f65--21, rlog/qlog/
  qcamera)瑜??낅줈?? 利앹긽: 怨좎냽?꾨줈 醫뚯빱釉?遺꾧린???묎렐 ??route湲곕컲 媛먯냽??誘몃━
  怨쇳븯寃?嫄몃졇?ㅺ? ?ㅼ떆 ?먮났?섎뒗 ?먮굦
- pycapnp + carrot-wip cereal ?ㅽ궎留덈줈 rlog.zst瑜?吏곸젒 蹂듯샇?뷀븯??carrotMan/carState/
  carControl/longitudinalPlan ??꾨씪???ш뎄?? 臾몄젣 援ш컙(t=47~59s) ?뺣? 遺꾩꽍
- ?뺤씤: t=47.3s寃?desiredSource="route"濡?desiredSpeed媛 67km/h濡?湲됰씫(?뱀떆 遺꾧린??  源뚯? ?꾩쭅 499m). ?ㅼ젣 媛먯냽 紐낅졊源뚯? ?댁뼱??vEgo 96??9km/h ?섎씫. ?댁쟾?먭? 7.5珥덇컙
  媛??媛쒖엯. ?댄썑 t=54.8~57.9s??route ?뚯뒪媛 115~121km/h濡??먯껜 ?ш퀎?곕릺硫?蹂듦?
- ?먯씤: carrot_navi_route()??3??40m) 怨〓쪧 怨꾩궛???ㅽ뙆?댄겕 ?쒓굅 ?꾪꽣媛 ?놁뼱, 遺꾧린??  ?대━?쇱씤 湲고븯 援?냼 ?쒓끝???ㅼ젣蹂대떎 湲됲븳 而ㅻ툕濡??ㅺ?異쒗븳 寃껋쑝濡?異붿젙(5李④퀎???뺤쟻
  遺꾩꽍?먯꽌 ?대? 吏?곷맂 由ъ뒪?ъ쓽 ?ㅼ젣 諛쒗쁽). ?ㅻ쭔 ?대━?쇱씤 湲고븯 ?먯껜??吏곸젒 ?議?紐삵븿
- FINDINGS.md???곸꽭 湲곕줉. 肄붾뱶 ?섏젙? ?꾩쭅 ?섏? ?딆쓬(????듭뀡 3媛吏 ?쒖떆, ?ъ슜??  ?먮떒 ?湲?
- ?ㅼ감 寃利? ?꾩긽 ?먯껜???ㅼ＜??濡쒓렇濡??뺤씤. ?먯씤 硫붿빱?덉쬁 ?쇰?(?대━?쇱씤 湲고븯)??  誘명솗吏?
## 7李?(?꾨즺 ????UI ?꾪솚 留덈Т由?+ carrot-ms ?숆린???먭?) ??釉뚮옖移??뺣━ 諛??좉퇋 而ㅻ컠 ?놁쓬 ?뺤씤

- ryujmin97/openpilot???ㅼ젣濡??⑥븘?덈뜕 carrot-ms, carrot-wip 釉뚮옖移?媛곴컖
  happymaj11r/openpilot, ajouatom/openpilot???꾩쟾??蹂듭궗蹂?瑜??ъ슜?먭? GitHub ??UI?먯꽌
  吏곸젒 ??젣 ?꾨즺. ?댁젣 ryujmin97/openpilot?먮뒗 carrot-ryu, carrot-ryu-note ??釉뚮옖移섎쭔
  議댁옱?섏뿬 臾몄꽌?붾맂 釉뚮옖移?援ъ꽦怨??쇱튂?섎뒗 ?곹깭濡??뺣━??(吏移?16????ぉ ?댁냼)
- carrot-ms(happymaj11r/openpilot) ?좉퇋 而ㅻ컠 ?숆린??寃??吏꾪뻾: git ls-remote濡??뺤씤??寃곌낵
  carrot-ryu HEAD? carrot-ms HEAD媛 ?뺥솗???쇱튂(02015190f58a4380a433ee0130e6374455dddc2e)
  ??6李??몄뀡 ?댄썑 carrot-ms???덈줈??rebase/而ㅻ컠???꾪? ?놁쓬. 諛섏쁺 ???而ㅻ컠 0嫄?- 李멸퀬濡?carrot-wip(ajouatom/openpilot)? HEAD媛 bb0e18bb8c09422fcd50dcf25c17e0d5c75072b1濡?  怨꾩냽 吏꾪뻾 以묒씠?? carrot-ms媛 ?꾩쭅 ?대? ?곕씪 rebase?섏? ?딆븘 吏移?2???먯튃?濡?吏곸젒 鍮꾧탳
  ??곸쑝濡??쇱? ?딆쓬
- WIP_SYNC.md瑜?carrot-ms 湲곗? 泥댄겕?ъ씤??諛⑹떇?쇰줈 媛깆떊(?대쾲 ?먭? 寃곌낵 湲곕줉)
- 肄붾뱶 蹂寃??놁쓬 (釉뚮옖移??뺣━ + ?먭?留??섑뻾), carrot-ryu???ъ쟾??carrot-ms? ?숈씪
- ?ㅼ감 寃利? ?대떦 ?놁쓬 (?명봽???먭? ?묒뾽)

## 6李?(?꾨즺 ??踰좎씠??釉뚮옖移??꾪솚) ??carrot-wip ??carrot-ms 濡?蹂寃?
- ?ъ슜?먭? happymaj11r/openpilot ??μ냼??carrot-ms 釉뚮옖移?肄ㅻ쭏 二쇳뻾紐⑤뜽 ?좏깮 湲곕뒫,
  carrot-wip 湲곕컲?쇰줈 留ㅻ쾲 ?ъ깮??rebase??瑜??뺤씤 ?붿껌
- git merge-base濡??뺤씤??寃곌낵 carrot-wip怨?carrot-ms??怨듯넻 議곗긽 而ㅻ컠???놁쓬(?덉뒪?좊━
  怨듭쑀 ???? ??carrot-ms??carrot-wip???낅뜲?댄듃???뚮쭏??洹??꾩뿉 紐⑤뜽?좏깮 湲곕뒫???ㅼ떆
  ?뱀뼱 ?듭㎏濡??ъ옉??rebase/force-push)?섎뒗 諛⑹떇?쇰줈 ?먮떒??- ?꾩껜 ?덉뒪?좊━ 鍮꾧탳 寃곌낵 carrot-wip???녾퀬 carrot-ms?먮쭔 ?덈뒗 而ㅻ컠 117媛??뺤씤.
  ??以?紐⑤뜽 ??됲꽣 愿???ㅼ썙?쒕줈 ?꾪꽣留곹븳 寃???58媛? ?섎㉧吏 ??59媛쒕뒗 ?대윭?ㅽ꽣(怨꾧린??
  HUD, PC ?쒕??덉씠??吏?? 濡쒓렇 ?낅줈???쒕쾭(?좎뒪/?밴렐) ?좏깮 湲곕뒫 ?????꾨줈?앺듃? 臾닿???  湲곕뒫?쇰줈 ?먮떒?? ?좊퀎 ?댁떇(cherry-pick)? ?ㅻ떒怨??묒뾽????寃껋쑝濡??덉긽??- ?ъ슜??寃곗젙: ?좊퀎 ?댁떇 ??? carrot-ryu 釉뚮옖移??먯껜??踰좎씠?ㅻ? carrot-wip?먯꽌
  carrot-ms濡??꾨㈃ ?꾪솚?섍린濡?寃곗젙 (?뱀떆 carrot-ryu???ъ슜??肄붾뱶媛 ?꾪? ?놁뼱 ?덉쟾?섍쾶
  媛?ν븳 ?쒖젏?댁뿀??
- ?ㅽ뻾: carrot-ryu(origin) 釉뚮옖移???젣 ??happymaj11r/carrot-ms 湲곗??쇰줈 ?ъ깮??
  carrot-ryu HEAD媛 carrot-ms HEAD(02015190f58a4380a433ee0130e6374455dddc2e,
  "Recover evil-merge resolutions from carrot-wip PR #516 and PR #517")? ?쇱튂?⑥쓣 ?뺤씤
- carrot-ryu-note??洹몃?濡??좎? (湲곗〈 醫낅갑??遺꾩꽍 ?댁슜? carrot-wip 湲곕컲 肄붾뱶 遺꾩꽍?대씪
  carrot-ms?먮룄 ?遺遺?洹몃?濡??좏슚????肄붾뱶媛 ?ш쾶 媛덈씪吏吏 ?딅뒗 ???щ텇??遺덊븘??
- ?꾨줈?앺듃 吏移?臾몄꽌(PROJECT_INSTRUCTIONS)??"踰좎씠??釉뚮옖移? ??ぉ??carrot-wip ??  carrot-ms濡??섏젙?섎뒗 臾멸뎄瑜??ъ슜?먯뿉寃??꾨떖??(臾몄꽌 ?먯껜????μ냼 諛뽰뿉???ъ슜?먭?
  蹂닿??섎뒗 寃껋쑝濡??뚯븙?섏뼱 Claude媛 吏곸젒 ?섏젙?섏? ?딆쓬)
- ???ν썑 ?곹뼢: carrot-ms??留ㅻ쾲 ?덉뒪?좊━媛 ?ъ옉?깅릺誘濡? carrot-wip泥섎읆 fast-forward
  ?숆린?붽? 遺덇??ν븿. carrot-ms媛 ?낅뜲?댄듃???뚮쭏??carrot-ms? carrot-wip??而ㅻ컠 硫붿떆吏瑜?  鍮꾧탳??"紐⑤뜽 ??됲꽣 愿??而ㅻ컠"留??좊퀎 諛섏쁺?섎뒗 諛⑹떇???꾩슂??(2???숆린???먯튃???뺤옣 ?곸슜
  ?꾩슂 ???ㅼ쓬 ?몄뀡?먯꽌 WIP_SYNC.md 援ъ“瑜?carrot-ms?⑹쑝濡쒕룄 ?뺤옣?좎? 寃???꾩슂)
- 肄붾뱶 蹂寃??놁쓬 (釉뚮옖移?踰좎씠???꾪솚留??섑뻾, carrot-ryu???ъ쟾??carrot-ms? ?숈씪)
- ?ㅼ감 寃利? ?대떦 ?놁쓬 (?명봽??蹂寃??묒뾽)

## 5李?怨꾩냽 (?꾨즺 ??traffic_stop / curve_speed / MPC 肄붿뒪???⑥닔 遺꾩꽍) ??醫낅갑??肄붾뱶 遺꾩꽍 1?④퀎 留덈Т由?
- 媛숈? ?몄뀡?먯꽌 ?댁뼱??traffic_stop.py(?뺤????좏샇 媛먯냽) ??curve_speed.py(鍮꾩쟾 而ㅻ툕 媛먯냽) ??  longitudinal MPC 肄붿뒪???⑥닔(set_weights, jerk_factor) ?쒖쑝濡?遺꾩꽍 吏꾪뻾
- traffic_stop.py: 二쇳뻾紐⑤뜽 ?덉륫(x,y,v)留뚯쑝濡??뺤??좏샇 ?먮떒?섎뒗 ?쒖닔 E2E ?대━?ㅽ떛 ?뺤씤.
  XState ?곹깭癒몄떊, TrafficStopModelLeadMatcher(5?꾨젅??confirm)源뚯? ?뺤씤. HD留??좏샇?됱긽
  ?몄떇 ?놁쓬 ??紐⑤뜽 ?깅뒫 ?섏〈 由ъ뒪???덉쓬. long_mpc.py??x2 obstacle源뚯? ?ㅼ젣 ?곌껐???뺤씤.
  ??李⑤웾 ?ㅼ젙: TrafficLightDetectMode=2(湲곕낯媛? ?대? ?쒖꽦 ?곹깭)
- curve_speed.py(鍮꾩쟾): route 踰꾩쟾怨??щ━ ?몃? ?대퉬 ??遺덊븘?? ?쒖닔 modelV2 湲곕컲. 怨〓쪧=
  yaw_rate/velocity瑜?3??median ?꾪꽣留???臾쇰━怨듭떇(v=sqrt(?↔??띾룄?덉궛/怨〓쪧))?쇰줈 怨꾩궛 ??  route 踰꾩쟾蹂대떎 寃ш퀬?? ??李⑤웾 AutoCurveSpeedFactor=80(湲곕낯蹂대떎 ?먯뒯?섍쾶 ?ㅼ젙?? ?뺤씤
- longitudinal MPC 肄붿뒪???⑥닔: stock openpilot acados ?꾨젅?꾩썙??洹몃?濡? carrot? ?낅젰媛믩쭔
  二쇱엯. jerk_factor媛 personality/myDrivingMode???곕룞(0.5~1.0)?⑥쓣 ?뺤씤, TFollowGap
  ?좏깮怨??쇨??섍쾶 ?ㅺ퀎?섏뼱 ?덉쓬???뺤씤
- 醫낅갑???꾩껜 泥닿퀎(LongControl PID ??v_cruise ?곹븳 ??MPC obstacle/肄붿뒪?????≪텛?먯씠??
  醫낇빀 ?ㅼ씠?닿렇?⑥쑝濡?FINDINGS.md???뺣━
- 醫낅갑??肄붾뱶 遺꾩꽍 1?④퀎(4李?5李?瑜??ш린??留덈Т由ы븯湲곕줈 寃곗젙. ?ㅼ쓬 ?④퀎???ㅼ감二쇳뻾 ??  route 濡쒓렇 ?앹꽦 ??濡쒓렇遺꾩꽍
- FINDINGS.md, PARAMS_REGISTRY.md, LAST_ANALYZED.md, CURRENT_STATUS.md, HANDOFF.md 媛깆떊
- 肄붾뱶 蹂寃??놁쓬 (遺꾩꽍/湲곕줉留?, carrot-ryu??carrot-wip怨??ъ쟾???숈씪
- ?ㅼ감 寃利? 誘몄떎??
## 5李?(?꾨즺 ??route 媛먯냽 泥댁씤 + T_FOLLOW/TFollowGap 泥댁씤 遺꾩꽍) ??醫낅갑??媛먯냽 濡쒖쭅 怨꾩냽

- ?ъ슜??諛⑺뼢: "醫낅갑??愿??肄붾뱶遺??遺꾩꽍 ???ㅼ감二쇳뻾 ??濡쒓렇遺꾩꽍" ?쒖꽌濡?吏꾪뻾?섍린濡?寃곗젙
- route(寃쎈줈) 湲곕컲 而ㅻ툕 媛먯냽 泥댁씤 ?꾩껜 異붿쟻:
  carrot_man.py(carrot_navi_route, GPS ?대━?쇱씤?믨끝瑜졻넂?띾룄) ??carrot_serv.py(update_navi,
  speed_n_sources 理쒖넖媛??좏깮) ??carrot_functions.py(_update_carrot_man, v_cruise_kph 媛깆떊) ??  longitudinal_planner.py ??MPC v_cruise ?곹븳 ???ㅼ젣 媛먯냽 紐낅졊源뚯? ?댁뼱吏먯쓣 ?뺤씤 (?쒖떆 ?꾩슜???꾨떂)
- ?쒖꽦???꾩젣議곌굔 ?뺤씤: TurnSpeedControlMode>=2 ?꾩슂(湲곕낯媛믪? 1=鍮꾩쟾留?, ???대퉬 ?깆쓽
  APN ?곌껐濡?寃쎈줈 ?대━?쇱씤 ?섏떊 ?꾩슂, shapely ?쇱씠釉뚮윭由??꾩슂
- ????李⑤웾???ㅼ젣 ??κ컪? TurnSpeedControlMode=2濡? route 媛먯냽??耳쒖졇 ?덈뒗 ?곹깭?꾩쓣
  params_backup-4.json?먯꽌 ?뺤씤 (DisableDM=2泥섎읆 "?ㅼ젙? 耳쒖졇?덈뒗???섎룄 誘명솗?? ?⑦꽩)
- T_FOLLOW/TFollowGap(李④컙嫄곕━) 泥댁씤 ?꾩껜 異붿쟻:
  t_follow.py(?ы띁) ??carrot_functions.py(_get_base_t_follow ~ get_T_FOLLOW, personality蹂?  湲곕낯媛??띾룄蹂댁젙/媛먯냽???ъ쑀嫄곕━ boost&hold/?대┰/?⑦봽) ??long_mpc.py(t_follow ??  desired_follow_distance ??MPC 由щ뱶李??μ븷臾??쒖빟)濡??ㅼ젣 異붿쥌嫄곕━ ?쒖뼱??諛섏쁺?⑥쓣 ?뺤씤
- ??李⑤웾? EnableSpeedTF=0, LeadAccelResponse=0?쇰줈 媛???⑥닚??personality 怨좎젙媛?  紐⑤뱶濡??댁슜 以묒엫???뺤씤 (TFollowGap1~4=110/120/140/160, ?쒖? 踰붿쐞 ???댁긽 ?놁쓬)
- ?뺤쟻 遺꾩꽍 湲곗? 踰꾧렇??諛쒓껄?섏? ?딆쓬(?곹깭 蹂??珥덇린?? ?대┰/?⑦봽 濡쒖쭅 紐⑤몢 ?덉쟾?섍쾶 ?묒꽦??
- FINDINGS.md, PARAMS_REGISTRY.md, LAST_ANALYZED.md 媛깆떊
- 肄붾뱶 蹂寃??놁쓬 (遺꾩꽍/湲곕줉留?, carrot-ryu??carrot-wip怨??ъ쟾???숈씪
- ?ㅼ감 寃利? 誘몄떎??
## 4李?怨꾩냽 (?꾨즺 ??DisableDM / LateralTorqueCustom 遺꾩꽍) ??蹂대쪟?덈뜕 ????ぉ ?뺤씤

- 媛숈? ?몄뀡?먯꽌 ?댁뼱??"DisableDM=2 / LateralTorqueCustom" 蹂대쪟 ??ぉ 遺꾩꽍 吏꾪뻾
- DisableDM=2 ?뺤씤: carrot_settings.json ?ㅻ챸("1.DisableDM, 2: +EnableWebRTC")怨?  process_config.py/selfdrived.py/controlsd.py 肄붾뱶濡??섎? ?뺤젙
  ???댁쟾??紐⑤땲?곕쭅(議몄쓬/二쇱쓽遺꾩궛 媛먯?쨌寃쎄퀬쨌媛뺤젣媛먯냽) ?꾩쟾 OFF + Carrot Vision WebRTC ?쒖꽦??  ???덉쟾 愿???ㅼ젙?대씪 ?ъ슜?먯뿉寃??섎룄 ?щ? ?ы솗???꾩슂 (?ㅼ쓬 ?몄뀡 ?먮뒗 吏湲??뺤씤)
- LateralTorqueCustom=0 ?뺤씤: latcontrol_torque.py 遺꾧린 援ъ“??0?대㈃ ??λ맂
  LateralTorqueKf/Friction/AccelFactor/KiV/KpV/Kd 媛믪씠 ?꾪? ?쏀엳吏 ?딆쓬.
  ?ㅼ젣濡쒕뒗 opendbc torque_data/params.toml??HYUNDAI_GENESIS ?ㅼ륫媛?  (LAT_ACCEL_FACTOR??.7808, FRICTION??.0984)濡?議고뼢 ?좏겕 怨꾩궛 以묒엫???뺤씤
- FINDINGS.md, PARAMS_REGISTRY.md 媛깆떊
- 肄붾뱶 蹂寃??놁쓬 (遺꾩꽍/湲곕줉留?
- ?ㅼ감 寃利? 誘몄떎??
## 4李?(?꾨즺 ??醫낅갑??PID 寃뚯씤 怨좎젙 ?뺤씤) ??LongTuningKpV/KiV/Kf 臾댄슚??諛쒓껄

- ?ъ슜???붿껌?쇰줈 "醫낅갑???쒖뼱(媛媛먯냽) 濡쒖쭅 遺꾩꽍" 李⑹닔
  (DisableDM=2 / LateralTorqueCustom ??ぉ? ?대쾲 ?몄뀡?먯꽌 蹂대쪟)
- longcontrol.py 遺꾩꽍 以? 而ㅻ컠 a26b108d(2026-09-04)?먯꽌 ?꾨?쨌湲곗븘쨌?쒕꽕?쒖뒪 李⑤웾??  醫낅갑??PID 寃뚯씤(Kp/Ki/Kf)??肄붾뱶??怨좎젙(1.0/0.0/1.0)?섏뼱 ?덉쓬???뺤씤
- ?ъ슜?먭? 蹂댁쑀??LongTuningKpV=100/KiV=0/Kf=100 ?ㅼ젙媛믪? ?쒕꽕?쒖뒪 DH 2015?먯꽌
  ?ㅼ젣濡쒕뒗 ?쏀엳吏 ?딄퀬 臾댁떆??(臾몄꽌?먮룄 紐낆떆???섎룄???숈옉, 踰꾧렇 ?꾨떂)
- ?ㅼ젣 ?곸슜?섎뒗 醫낅갑???몃툕??LongActuatorDelay / VEgoStopping / StoppingAccel 肉먯엫???뺤씤
- ACCEL_MIN/MAX(-4.0/2.5 m/s짼)???쒕꽕?쒖뒪 ?꾩슜 媛??놁씠 Hyundai 怨꾩뿴 怨듯넻媛믪엫???뺤씤
- FINDINGS.md, PARAMS_REGISTRY.md, LAST_ANALYZED.md??諛섏쁺
- 肄붾뱶 蹂寃??놁쓬 (遺꾩꽍/湲곕줉留?, carrot-ryu??carrot-wip怨??ъ쟾???숈씪
- ?ㅼ감 寃利? 誘몄떎??
## 3李?(?꾨즺 ???뚮씪誘명꽣 踰좎씠?ㅻ씪??湲곕줉) ???꾩옱 ?곸슜 ?ㅼ젙媛??ㅻ깄??
- ?ъ슜?먭? 肄ㅻ쭏 ?붾컮?댁뒪?먯꽌 export??params_backup-4.json ?섎졊
- CarSelected3="Hyundai Genesis 2015-16"濡?李⑤웾 留ㅼ묶 ?뺤씤
- DisableMinSteerSpeed=1???ㅼ젣濡??곸슜?섏뼱 ?덉쓬???뺤씤 (2李?FINDINGS? ?쇱튂)
- ?먮낯 ?뚯씪??devnotes/params_snapshots/2026-09-12_params_backup-4.json?쇰줈 蹂닿?
- PARAMS_REGISTRY.md??二쇱슂 而ㅼ뒪? 媛?議고뼢 ?좏겕, 醫낅갑???쒕떇, ?щ（利??꾨줈?뚯씪 ?? ?붿빟 湲곕줉
- DisableDM=2, LateralTorqueCustom=0 ???섎? 誘명솗????ぉ???ㅼ쓬 遺꾩꽍 ?꾨낫濡??깅줉
- ?ㅼ감 寃利? ?대떦 ?놁쓬 (湲곕줉 ?묒뾽)

## 2李?(?꾨즺 ????띿“???쒗븳 遺꾩꽍) ??minSteerSpeed / SMDPS

- CAR.HYUNDAI_GENESIS minSteerSpeed=60km/h ?섎뱶肄붾뵫 ?뺤씤
- DisableMinSteerSpeed Params ?좉???carrot-wip???대? 援ы쁽?섏뼱 ?덉쓬???뺤씤
  (interfaces.py + carrot_settings.json UI ?몄텧)
- 肄붾뱶 ?섏젙 ?놁씠 ?ㅼ젙媛?蹂寃쎈쭔?쇰줈 ?닿껐 媛???먮떒
- ?ㅼ감 寃利? 誘몄떎??
## 1李?(?꾨즺 ??釉뚮옖移??명똿) ???꾨줈?앺듃 援ъ“ 珥덇린??
- carrot-wip: ?먮낯 李멸퀬 釉뚮옖移??뺤씤
- carrot-ryu: carrot-wip?먯꽌 遺꾧린?섏뿬 ?앹꽦
- carrot-ryu-note: orphan 釉뚮옖移섎줈 ?앹꽦, devnotes ?대뜑 援ъ“ ?명똿
- ?ㅼ감 寃利? 誘몄떎??