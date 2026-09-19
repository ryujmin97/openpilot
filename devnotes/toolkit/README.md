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
