# Toolkit README

재사용 가능한 분석/검증 스크립트 목록

## lead_decel/ — 선행차 감속에 대한 자차 반응 분석 (97차, 98차 게이팅 평가 추가)

rlog.zst에서 carState/radarState.leadOne/longitudinalPlan을 뽑아 리드 감속 이벤트를 분석하고, MPC 복제본으로 what-if를 돌리는 도구 모음. 결과 해석·수치는 WIP.md 97차.

| 파일 | 역할 |
|---|---|
| `parse_lead_log.py` | `<schema_dir> <seg_dir> <out.pkl>`: rlog.zst -> DataFrame(cs/rs/lp). 의존: pycapnp, zstandard, pandas |
| `merge_lead_series.py` | 20Hz 병합 -> `out/merged.pkl` (t, margin=dRel-desiredDistance 등). 연속 세그먼트 묶음(pairs)은 파일 안에서 수정 |
| `counterfactual.py` | 리드 궤적 고정, 자차 상수 감속 반사실(사후 기준 필요 감속 크기) |
| `mpc_replica.py` | long_mpc OCP의 casadi/IPOPT 복제본(acados 실물 아님, RMSE 약 0.22 m/s²) |
| `closed_loop.py` | 복제본 폐루프 what-if: baseline / lpf(리드 속도 저역통과) / tau(투사 감쇠) / noproj |
| `events.py` | `out/merged.pkl`에서 aLeadK<-1 리드 감속 이벤트 추출(연속 간격 2 s 초과 시 분리, 26건) + 실제 로그 지표 표(`out/events.pkl`) |
| `needed_decel.py` | 이벤트별 사후(hindsight) 필요 감속: 시간차 하한(1.0/1.2/1.5/1.8 s)을 지키는 최소 상수 감속(`counterfactual.sim` 사용, 이상화 값) |
| `gating_eval.py` | 게이팅 후보(시간차·TTC 기반 g로 투사 감쇠/저역통과를 약화) 폐루프 평가 + 초기 거리 스트레스. 후보 A=G1T, B=G2T(98차 채택) |

환경 구성: `pip install --break-system-packages pycapnp zstandard casadi scipy`. 스키마는 **로그를 기록한 커밋** 기준으로 받는다(tmux metadata.json의 git_commit; 97차는 carrot-ryu-v1 `9ccf1206`). 그 커밋의 `openpilot/cereal/*.capnp`, `openpilot/cereal/include/`, `opendbc_repo/opendbc/car/car.capnp`를 한 폴더에 모은다(`git clone --filter=blob:none --no-checkout` + `sparse-checkout`).
실행 순서(작업 폴더에 `out/` 생성): `parse_lead_log.py <schema> <seg_dir> out/all.pkl` -> `merge_lead_series.py` -> `counterfactual.py <t_on>` / `closed_loop.py <pair> <t0> <t1>`. 한계와 미검증 사항은 각 파일 상단 docstring과 WIP.md 97차 참고. 실차 검증 아님.

98차 추가 실행 순서(위 `merge_lead_series.py`까지 끝낸 뒤): `events.py`(이벤트 표) -> `needed_decel.py`(사후 필요 감속) -> `gating_eval.py <tag> <idx,..> <offsets,..> <variants,..>`(예: `gating_eval.py key 5,8,22 0,-10,-20 base,G1T,G2T`). 로그 zip은 세그먼트별 zip을 풀어 `<route>--<n>/rlog.zst`를 한 폴더에 모은 뒤(심볼릭 링크 가능) `parse_lead_log.py`에 넘긴다. 폐루프 1회가 CPU 1코어 기준 약 10 s이며, 백그라운드 실행은 `setsid nohup`을 쓴다. 결과 해석은 WIP.md 98차. 실차 검증 아님.

### 106차 추가 (gating_eval_105.py, merge_lead_series.py 인자)

| 파일 | 역할 |
|---|---|
| `gating_eval_105.py` | `gating_eval.py` 확장: 105차 실제 게이트(margin_ratio 1.0/1.2 + TTC 6/12 s, 투사 감쇠만)를 후보 `M105`로 추가. 사용: `gating_eval_105.py <tag> <idx,..> <offsets,..> [base,B,M105]`(변형 기본값 base,B,M105). 필요: `out/merged.pkl`, `out/events.pkl`, 같은 폴더의 `gating_eval.py`/`mpc_replica.py`. 결과 `out/gate_<tag>.pkl`(열에 margin `m` 포함). 튜닝은 파일 안 `M105` dict 상수 수정 |

`merge_lead_series.py`는 인자로 연속 세그먼트 구간을 받는다: `merge_lead_series.py main=21-25`(인자 없으면 파일 안 기본 pairs). 106차 재생 순서: `parse_lead_log.py <schema> <seg_dir> out/all.pkl` -> `merge_lead_series.py main=21-25` -> `events.py` -> `gating_eval_105.py stress 2,5,6,7,8,9 0,-10,-20 base,B,M105`(약 10분, `setsid nohup`). 스키마는 로그 커밋(105차 로그: `67b0aa9`) 기준. 복제본 한계와 실차 검증 미실시는 WIP.md 106차 참고.

### 107차 추가 (실차 로그 대조: ego_extract.py, ego_episodes.py, replay_ext.py, real_vs_replay.py)

실제 주행 로그에서 자차 거동을 읽고, 같은 이벤트의 복제본 재생과 비교하는 도구. 실차 검증 아님(로그 확인).

| 파일 | 역할 |
|---|---|
| `ego_extract.py` | rlog에서 carState/carControl/longitudinalPlan/radarState.leadOne/swaglog(`lead_gate`)/selfdriveState를 뽑아 `out/ego.pkl` 생성(t는 첫 carState 기준 초) |
| `ego_episodes.py` | 0.5 s 이동평균 aEgo < -1.0 구간(자차 실제 급감속)을 뽑고 accelCmd/aTarget/브레이크/리드/게이트(g,m,h)를 함께 표시. 순간 센서 스파이크는 걸러진다 |
| `replay_ext.py` | `replay_ext.py <idx> <variants,..>`: 이벤트 1개를 base/B/M105/M0.8-1.0/M0.9-1.1로 폐루프 재생(gating_eval_105.py 확장), `out/ext_<idx>.pkl` |
| `real_vs_replay.py` | (1) 실차 aEgo(0.5 s 중앙값) vs 복제본 M105 정합성 16건 (2) idx 0,1,3,4,10~15 후보 비교. `out/ext_*.pkl` 16개 필요 |

폴더 배치(작업 폴더 기준 상대경로 고정): 작업 폴더에 `out/`, 상위에 `../schema/`(로그 기록 커밋의 cereal + car.capnp), `../segs/<route>--<n>/rlog.zst`. 107차 순서: `parse_lead_log.py ../schema ../segs out/all.pkl` -> `merge_lead_series.py main=21-25` -> `events.py` -> `ego_extract.py` -> `ego_episodes.py`; 복제본 대조는 이벤트별 `replay_ext.py <idx> M105`(idx 0~15, 후보 비교용 idx는 `M105,base,B,M0.8/1.0,M0.9/1.1`) 후 `real_vs_replay.py`. 재생은 CPU 1코어 기준 이벤트당 약 10 s x 변형 수이며 병렬 실행하면 그만큼 느려진다(`setsid nohup`). 결과 해석은 WIP.md 107차.

### 108차 계속 추가 (복제본 보정 검증: ego_extract2.py, openloop108.py, closedloop108.py)

복제본을 코드/Params 기준으로 보정하고 플래너 내부 상태를 로그에서 재구성해 검증하는 도구. 실차 검증 아님(로그 확인). 폴더 배치는 `../toolkit`(mpc_replica.py), `../schema`(로그 커밋 스키마), `../segs`(세그먼트 폴더), `out/ego2.pkl` 고정(각 파일 docstring 참고). 이 도구들은 기존 `mpc_replica.py` 기본값(a_min -3.5, cb 2.47/sd 11.6)을 인자로 덮어쓴다(a_min -4.0 = 67b0aa9 ACCEL_MIN, cb 2.4/sd 7.0 = params_backup.json).

| 파일 | 역할 |
|---|---|
| `ego_extract2.py` | ego_extract.py 확장 추출: longitudinalPlan(source/aChangeCost/leadPreview*/accels 등)과 radarState leadOne+leadTwo(cutOut 포함), swaglog `lead_gate`, selfdriveState. `out/ego2.pkl` = dict(cs, cc, lp, rs, sw, ss). `../schema`, `../segs/*/rlog.zst` 필요 |
| `openloop108.py` | `openloop108.py <seg> <t_from> <t_to> [tag]`: 플래너 x0(v_desired_filter, a_desired)·prev_a·게이트 g를 로그에서 재구성해 사이클마다 복제본을 1회 풀고 로그 accels(17점, 0~2.5 s)와 비교. 변형 P(cb 2.4/sd 7.0)/Pnogate/Old(2.47/11.6). swaglog g 대조 출력. 환경변수 `RSHIFT=1`(레이더 입력을 1 cycle 지연), `ONLYP=1`(변형 P만). 결과 `out/ol108_<tag>.pkl` |
| `closedloop108.py` | `closedloop108.py <seg> <t_from> <t_to> <variant> [tag]`: 보정 폐루프 what-if(리드는 로그 외생 입력, 자차 시정수 0.3 s, action_t 0.25). variant: none / M105 / M0.8/1.0 / M0.9/1.1(게이트 후보, TTC 6/12 s 고정). 환경변수 `RSHIFT`. 결과 `out/cl108_<tag>_<variant>.pkl`. 시작 상태는 t_from 직전까지 로그로 재구성 |

실행 예: `python3 ego_extract2.py`(run/ 폴더에서) -> `ONLYP=1 python3 openloop108.py 113 3.0 6.5 a` -> `RSHIFT=1 python3 closedloop108.py 113 2.0 9.0 M105 113`. 단일 코어 기준 IPOPT 1회 약 0.3~0.4 s(폐루프 변형 1개, 7 s 구간 약 35 s). 백그라운드는 `setsid nohup ... < /dev/null`. 결과 해석과 한계(폐루프 복제본이 강한 리드 감속에서 실차보다 약함)는 WIP.md 108차 계속 참고.

### 108차 계속2 추가 (출력단 저크 제한 what-if: closedloop_jlim.py)

`closedloop108.py`에 출력단 rate limiter를 더한 도구. 실차 검증 아님(로그 확인). MPC 내부 가정(게이트/tau/tf/prev_a/warm)은 그대로 두고 실행 명령 a_cmd만 "더 세지는 방향"으로 `J_MAX` m/s³ 이하로 서서히 강화하고 완화는 즉시 반영한다. 폴더 배치와 입출력은 `closedloop108.py`와 같다(`../toolkit`, `../schema`, `../segs`, `out/ego2.pkl`).

| 파일 | 역할 |
|---|---|
| `closedloop_jlim.py` | `J_MAX=<m/s^3> python3 closedloop_jlim.py <seg> <t_from> <t_to> <variant> [tag]`. `J_MAX` 기본 999(비활성 = `closedloop108.py`와 동일). 결과 `out/cl108_<tag>_<variant>.pkl`. 파일 상단 docstring/사용법은 `closedloop108.py` 것을 그대로 두었다(파일명만 다름) |

실행 예: `J_MAX=6 python3 closedloop_jlim.py 113 2.0 9.0 M105 jl113`. 108차 계속2 결과: seg 113/146에서 J_MAX 6 이상은 완전 무효, 4에서도 최솟값이 오히려 0.01 강해짐(복제본 최대 강화 저크가 seg 113 -4.66 m/s³뿐). 한계와 해석은 WIP.md 108차 계속2 참고.

### 109차 추가 (필요 감속 기반 명령 상한 what-if: closedloop_ncap.py)

`closedloop108.py`/`closedloop_jlim.py`와 같은 재구성 규칙 + 매 사이클 실시간(causal) 필요 감속으로 그 사이클의 MPC `a_min`만 교체하는 what-if. 실차 검증 아님(로그 확인 + 합성 stress). 폴더 배치는 `closedloop108.py`와 같다(`../toolkit`, `../schema`, `../segs`, `out/ego2.pkl`). event 모드는 로그 필요, stress 모드는 로그 불필요(합성 시나리오).

| 파일 | 역할 |
|---|---|
| `closedloop_ncap.py` | `event <seg> <t_from> <t_to> <gate_variant> [tag]` 또는 `stress <v0_kph> <gap0_m> <lead_decel> <gate_variant> [tag]`. 환경변수 `NCAP`(0/1, 기본1), `NCAP_MARGIN`(기본0.6), `NCAP_HFLOOR`(기본1.2, 초), `RSHIFT`(event만). `d_target=NCAP_HFLOOR×vL` 기준. 결과 `out/ncap_ev_*.pkl` / `out/ncap_st_*.pkl` |

109차 결과: `d_target=HFLOOR×vL` 구조가 리드 급감속 시 avail을 다시 키워 cap을 역방향으로 풀어버리는 결함 확인(리드 속도가 줄면 목표거리도 같이 줄어듦). hfloor 1.0~3.0 전 구간에서 stress(94km/h, 앞차 -5m/s² 지속) 안전 여유가 baseline(무제한)보다 나쁨. 이 구조는 폐기, vE 기준 재설계는 별도 검증 필요. 한계와 해석은 WIP.md 109차 참고.
