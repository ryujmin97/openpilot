# Toolkit README

재사용 가능한 분석/검증 스크립트 목록

## replace_block_template.ps1 -- 코드/devnotes 반영 스크립트의 Replace-Block + git 실행 공통 헬퍼 (133차, 144차에 Invoke-Git 추가)

문자열 블록 치환(Replace-Block)을 쓰는 모든 반영 스크립트가 매번 새로 작성하지 않고
그대로 복사해서 쓰는 `Invoke-ReplaceBlock`/`Invoke-ReplaceBlock-CrlfNative` 함수 모음.
CRLF->LF 정규화(핵심 발견 44/46/48/50 재발 방지)와 치환 결과 재확인(핵심 발견 42 재발
방지)을 포함한다. FINDINGS.md처럼 원본이 CRLF인 파일은 `-CrlfNative` 변형을 쓴다(전체를
LF로 재작성하면 손대지 않은 기존 줄까지 diff에 잡히는 부작용이 있음). 9절 체크리스트
2번이 이 파일 재사용을 요구한다.

`Invoke-Git`(144차 신규): `git <args...>` 실행 공통 헬퍼. stderr를 stdout과 병합하지
않고(2>&1 금지, 핵심 발견 53/55) `$LASTEXITCODE`만으로 성공/실패를 판단하며, 이름 있는
파라미터를 선언하지 않고 자동 변수 `$args`만 참조한다(`git add -A`의 `-A`가 파라미터
이름과 접두어 충돌을 일으키는 문제 차단, 핵심 발견 54). 핵심 발견 53/54/55가 요구하던
"Invoke-Git 계열 헬퍼를 새로 만들 때는 이 두 조건을 모두 지킨 버전을 채택한다"는 원칙을
이 파일에 정식 등록해, 앞으로 devnotes/코드 반영 스크립트가 매번 새로 작성하지 않고
재사용하도록 했다. 상세 사용법은 파일 상단 주석 참고.

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

### 113차 계속 추가 (route 감속 분석: route_decel/route_extract.py)

route(내비 경로) 목표속도/안내 정보와 자차 거동을 rlog 1개에서 뽑아 20Hz로 병합하고, 배율 변경(`carrot_serv.map_turn_speed_factor`)을 로그에 산술 재계산하는 도구. 실차 검증 아님(로그 확인, 플래너/차량 시뮬레이션 아님).

| 파일 | 역할 |
|---|---|
| `route_decel/route_extract.py` | `extract <schema_dir> <rlog.zst> <out.pkl>`: carState/carControl/longitudinalPlan/carrotMan/radarState/selfdriveState를 carrotMan 20Hz로 병합(t는 첫 carState 기준 초, `route`는 szPosRoadName 안 `route=` 디버그값). `show <out.pkl> <t0> <t1> [step]`: 구간 표(vE/aEgo/brakeP/accel/longActive/state/des/src/route/vTurn/xTurn/xDist). `replay <out.pkl> <t0> <t1> <base> [near far guide]`: route=값/base로 원시값을 되돌리고 안내 종류 3/4/6이면 far~near 선형·near 이내 guide 배율을 적용한 새 목표와 vE와의 차이 출력(base는 로그 당시 MapTurnSpeedFactor/100, 예 1.35) |

스키마는 **로그를 기록한 커밋** 기준으로 받는다(113차 로그: carrot-ryu `a430d114`의 `openpilot/cereal/*.capnp`, `openpilot/cereal/include/`, `opendbc_repo/opendbc/car/car.capnp`를 한 폴더에). 의존: pycapnp, zstandard, pandas, numpy. 실행 예: `route_extract.py extract ../schema <route>--<n>/rlog.zst out/r.pkl` -> `route_extract.py show out/r.pkl 44 52` -> `route_extract.py replay out/r.pkl 36 45 1.35`. `route=` 값은 이 도구를 쓰려면 debugText 형식(`route=숫자`)이 유지돼야 한다(hud_renderer도 이 형식을 파싱). 113차 결과와 해석은 FINDINGS.md 113차 계속 참고.

### 125차 추가 (pytest CI 환경 재현: pytest_ci_setup.sh)

Claude 샌드박스에서 conftest.py를 포함한 실제 pytest CI 조건을 재현하는 원클릭 설치 스크립트. 92차 등에서 "샌드박스에 컴파일 의존성이 없어 미실시"로 기록됐던 전제가 실제로는 틀렸음을 124~125차에서 확인하고 그 절차를 기록한 것. 콤마 디바이스/사용자 PC용이 아니며, 대화(세션)가 바뀌면 파일시스템이 초기화되므로 pytest를 다시 돌리려면 매번 이 스크립트부터 실행해야 한다.

| 파일 | 역할 |
|---|---|
| `pytest_ci_setup.sh` | `bash pytest_ci_setup.sh [branch]`(기본 carrot-ryu): clone -> apt(capnproto/libzmq) -> pip(Cython/pycapnp/comma-deps-json11/comma-deps-acados 등) -> cereal capnp C++ 헤더 생성 -> `openpilot.common.params_pyx`/`msgq.ipc_pyx` Cython 컴파일 -> `long_mpc.py`용 acados OCP 솔버 코드생성(`ACADOS_SOURCE_DIR` 등 3개 환경변수로 acados wheel 경로 지정) + gcc 링크 + Cython 래퍼 컴파일까지 전부 자동화. 끝에 params/msgq/long_mpc import+instantiate 자가검증 포함 |

실행 후: `cd /home/claude/repo && export PYTHONPATH=/home/claude/repo:/home/claude/repo/opendbc_repo && python3 -m pytest <경로...>`. 알려진 한계: opendbc 일부 차량(Toyota new_mc/Nissan Leaf 등) DBC는 `opendbc_repo/opendbc/dbc/generator/`에서 별도 생성 단계가 더 필요해 이 스크립트만으로는 없음 -- 그 DBC를 쓰는 CarInterface 생성 테스트는 실패한다(125차 발견, 미해결). `pyray`(cluster/UI)와 xiaoge ONNX 모델(이 환경 OpenCV 버전과 포맷 불일치)도 이 스크립트 범위 밖. 125차 실행 결과(23/23 목표 테스트 통과, 전체 확장 시 1928 passed/59 failed/85 errors)와 발견 사항은 WIP.md 125차 참고.

### 149차 추가 (147차 감속 프리뷰 게이트 실로그 재생: replay_gate147.py, extract_radar_flag.py)

실제 코드를 재구현 없이 재사용해 rlog 위에서 감속 프리뷰 게이트를 20Hz 재생한다. 실차 검증 아님(로그 재생, open-loop).

| 파일 | 역할 |
|---|---|
| `lead_decel/extract_radar_flag.py` | run/ 폴더에서 실행: `radarState.leadOne/leadTwo.radar` 플래그 추출 -> `out/radarflag.pkl` (`ego_extract2.py`에 없는 필드, 플래너 `lead.radar` 조건 재현용) |
| `lead_decel/replay_gate147.py` | `[PBAND=lo,hi] [TAG=_x] python3 replay_gate147.py <run_dir> <src_old> <src_new> [cb] [sd]`: `long_mpc.py`에서 상수/`get_safe_obstacle_distance`/`get_stopped_equivalence_factor`/`LongitudinalMpc._gate_raw`를 ast로 원문 추출해 exec, `longitudinal_preview.py`는 import. 20Hz 주기마다 gate -> `get_lead_preview_request` -> `rate_limit_preview` -> `clip_preview_offset` 체인을 재생하고 로그 `accels`로 출력 a_target을 재구성. 출력 `out/replay147<TAG>.pkl`. 기본 cb=2.4/sd=7.0(149차 swaglog 역산값), 기본 밴드 1.05,1.25 |

준비: `<run_dir>/out/ego2.pkl`(ego_extract2.py) + `out/radarflag.pkl`(extract_radar_flag.py), 폴더 배치는 ego_extract2.py와 동일(`../schema`, `../segs`). `src_old`/`src_new`는 각각 로그 기록 커밋과 비교 대상 커밋의 `openpilot/selfdrive/controls/lib/longitudinal_preview.py`와 `openpilot/selfdrive/controls/lib/longitudinal_mpc_lib/long_mpc.py`를 같은 폴더에 사본으로 둔 것(`git fetch --depth 1 --filter=blob:none origin <SHA>` 후 `git show <SHA>:<path>`). 실행하면 재생 신뢰도(새 코드 gate=1 == 기록 커밋 코드, 로그 leadPreviewSeconds/aTargetBase 재현 오차)를 먼저 출력하므로 그 값이 작은지 확인한 뒤 결과를 해석한다. 한계: MPC 궤적은 로그값 고정(자차 거동이 바뀐 뒤의 폐루프는 재현 안 됨), `myDrivingMode`/`reset_state`는 미로깅. 결과와 해석은 WIP.md 149차 참고. `comfort_brake/stop_distance`는 swaglog `lead_gate`(m 소수2자리) 역산으로 정한 값이라 다른 설정의 디바이스 로그에는 다시 역산해야 한다.


### 154차 추가 (153차 get_path_after_distance() 수정 rlog 재생 교차검증: route_decel/replay_route_geom.py)

153차가 합성 좌표로만 검증한 `get_path_after_distance()` 수정(첫 세그먼트≥300m 처리)을 seg70/71/92/93 실제 rlog로 교차검증하는 도구. 재구현 없이 실제 소스에서 함수 원문(`haversine`/`closest_point_on_segment`/`get_path_after_distance`/`gps_to_relative_xy`/`calculate_curvature`/`V_CURVE_LOOKUP_BP` 등)을 ast로 추출해 exec하고, 로그의 `carrotMan.xPosLat/xPosLon/xPosAngle`(get_path 입력)·`navRoute`(폴리라인)·`carState.vEgo`로 OLD/NEW 두 버전을 20Hz 재생한다. 실차 검증 아님(로그 재생, open-loop).

| 파일 | 역할 |
|---|---|
| `route_decel/replay_route_geom.py` | `extract <schema_dir> <rlog.zst> <out.pkl>`: carrotMan(xPos*/naviPaths/xTurn/xDist/des/src 등)+navRoute+carState.vEgo를 뽑는다(20Hz가 아니라 carrotMan 이벤트 기준, route_extract.py의 extract와 별개). `run <old_carrot_man.py> <new_carrot_man.py> <out_prefix> <seg.pkl> [<seg2.pkl> ...]`: OLD/NEW `get_path_after_distance()`를 재생해 `<out_prefix>_replay.pkl` 생성(연속 세그먼트는 start_index를 이어받음). `report <label>=<prefix>_replay.pkl [...] [--base 1.2] [--guide 1.0]`: 재생 충실도(로그 naviPaths 대비)/트리거 비율/route 급변 건수(로그·OLD·NEW)/비트리거 무회귀/route-source desiredSpeed 급변을 집계 표로 출력 |

가정 파라미터(로그에 없음, `run()` 인자로 덮어쓰기 가능): `AutoNaviSpeedDecelRate=0.8 m/s^2`, `AutoNaviSpeedCtrlEnd=0`. `report`의 `--base`(route/out_speed 계수, MapTurnSpeedFactor/100)는 154차 로그에서 약 1.2로 역산한 값. 폴더 배치는 `route_extract.py`와 동일(`schema_dir`에 log.capnp/custom.capnp/deprecated.capnp/include/+car.capnp를 로그 기록 커밋 기준으로 모음). 한계: 로그 xPos는 Float32(약 0.4~0.8m 양자화)라 트리거 사이클(버그 발현 조건) 개별 값은 재생과 어긋날 수 있어 집계 지표로만 해석한다(154차 실측: 비트리거 재생 충실도 93.3~98.2%(3m 이내) vs 트리거 62.3~73.3%). 154차 결과와 해석은 WIP.md 154차 참고.


### 160차 추가 (route= 필드 1사이클 지연 주의: report()/직접 비교 시)

로그 `carrotMan.szPosRoadName`의 `route=` 값(디버그 표기)을 재생값(`r_o`, `out_o × 배율`)과 같은 사이클끼리 직접 비교하면 실제로는 일치하는 변화도 불일치로 보일 수 있다(160차 발견). seg8/seg15 구간에서 재생 `r_o`와 로그 `route=`의 오르내림 패턴이 정확히 한 사이클(20Hz, 0.03~0.06s) 어긋난 채 동일한 모양으로 나타났고, `run()`의 decel 인자를 0.3~2.0으로 바꿔도 이 타이밍 자체는 변하지 않았다(크기만 스케일) -- 즉 재생 파라미터 오차가 아니라 로그 `route=` 필드 표기 자체의 1사이클 지연으로 추정된다(정적 추적 기반 추정, 확정 아님). 같은 사이클 대조에서 급변이 재현되지 않으면, 재생 r_o를 1사이클(-1) 시프트해 로그와 다시 대조해 볼 것. 상세 근거는 WIP.md 160차 참고.

### 170차 추가 (dead code 판별 방법론: DEAD_CODE_REVIEW.md 원본 폐지, 방법론만 이관)

carrot-ryu의 dead code(호출/참조되지 않는 코드) 판별에 115~135차에 걸쳐 쓰인 방법론. 원본 `devnotes/DEAD_CODE_REVIEW.md`(완료된 배치별 이력 문서)는 170차에 삭제됐고, 재사용 가치가 있는 방법론만 이 절로 옮겼다. 배치별 상세 이력(어떤 커밋에서 무엇을 지웠는지, 실차 검증 여부)은 WIP.md 115/117/118/120/121/123/135차 및 FINDINGS.md를 참고. 원본 문서 전체는 이 삭제 커밋 이전 carrot-ryu-note 히스토리에서 조회 가능.

**원칙**: (1) 후보는 저장소 전체를 codeload tarball로 받아 심볼 단위 grep으로 참조 0건을 확정한 뒤에만 삭제한다(추측 금지, 11절). (2) 삭제 diff를 `py_compile`과 기존 테스트(pyflakes 경고 비교 포함)로 확인한다. (3) 사용자가 스크립트를 실행해 push하기 전에는 "제거 완료"로 쓰지 않는다. (4) 지침 10절 "최소 변경 원칙"과 방향이 반대(코드를 줄이는 이니셔티브)이므로 배치마다 사용자 승인을 받는다. (5) carrot-ms와의 차이가 늘어나는 점을 감안한다(20절 리셋 시 재이식 대상이 됨).

**탐색 방법**: first-party 스코프(selfdrive/carrot, controls/lib, carrot/model_selector, tools/carrot_* 등, opendbc_repo/tinygrad_repo/.vendor 제외) 함수·메서드 정의를 AST(`ast.parse`)로 추출 → 코드/문자열/비-py 파일/테스트로 구분해 참조를 토큰 단위로 카운트 → 죽은 함수에서만 호출되는 함수까지 연쇄로 추적 → 최종 후보는 저장소 전체 `grep -w`(rg 가능)로 재확인(11절). 삭제 전/후 py_compile + pyflakes 경고 비교, pytest 실패 목록 동일 여부, 로컬 bare 저장소에서 반영 스크립트 로직 전체(clone → pre-image blob hash 가드 → 치환 → post-image 확인 → py_compile → commit/push)를 재현해 diff가 예상과 일치하는지까지 확인한다(9절 9번과 동일한 사고방식).

**오탐(false positive) 배제 패턴 누적 목록** — 새 배치에서 "참조 0건"으로 보여도 아래 패턴이면 실제로는 살아있는 코드일 수 있으니 먼저 제외하고 검토한다:
- opendbc_repo 등 외부/vendor 라이브러리가 쓰는 심볼(예: `apply_deadzone`은 opendbc `gm/carcontroller.py`가 사용 — 1차 스캔이 opendbc 제외 범위였던 탓에 생긴 오탐)
- `.vendor/` 외부 라이브러리 코드
- 프레임워크 콜백/오버라이드(예: `do_POST`/`do_DELETE`/`handle_starttag`/`handle_startendtag`)
- 동적 디스패치로 호출되는 함수(예: `_ingest_*`)
- `@pytest.fixture(autouse=True)` 픽스처(예: `clean_baseline`/`fake_param_key_type`/`isolated_git`)
- 커스텀 데코레이터로 등록되는 함수(예: `@register_command`)
- 테스트에서만 참조되는 이름 — 곧바로 삭제 대상에 넣지 말고 "보류"로 분류해 별도 검토(회귀 가드일 수 있음, 예: `_draw_navi_traffic_light_panel`)

### 206차 계속 추가 (pytest_ci_setup.sh에 pytest-mock 추가)

`pytest_ci_setup.sh`의 3/6 단계 pip 목록 끝에 `pytest-mock`을 추가하고 이유를 주석 2줄로 남겼다(다른 단계는 변경 없음). `mocker` 픽스처를 쓰는 테스트(예: `controls/tests/test_plannerd_clock.py`, `system/athena/tests`, `system/hardware/tests`)는 pytest-mock이 없으면 전부 ERROR로 끝난다. 206cha 샌드박스 실측(`test_plannerd_clock.py`, `-n 0 -p no:randomly`): pytest-mock 없이 54 errors, 설치 후 54 passed. 이전에는 세션마다 `pip install pytest-mock`을 수동으로 해야 했다. 수정한 스크립트를 처음부터 끝까지 다시 실행해 보지는 않았고 `bash -n` 구문 검사만 통과했다(다음에 이 스크립트를 새 세션에서 처음 돌릴 때 실제 확인).

### 207차 추가 (pytest 밖에서 Plant를 돌릴 때: OpenpilotPrefix로 감쌀 것)

`openpilot/selfdrive/test/longitudinal_maneuvers/plant.py`의 `Plant.__init__`은 `Params()`를 만들고 `params_keys.h` 기본값을 아직 값이 없는 키에 put한다(68~73행, 주석 "same as manager_init()"). pytest 안에서는 루트 `conftest.py`(51행)가 테스트마다 `OpenpilotPrefix`(`openpilot/common/prefix.py`)로 msgq 경로와 Params 경로를 격리한다. pytest 밖(임의의 측정/분석 스크립트)에서 Plant를 돌릴 때는 이 격리가 없으므로 아래처럼 감싼다.

```python
from openpilot.common.prefix import OpenpilotPrefix
with OpenpilotPrefix():
    ...  # Plant/Maneuver 생성과 실행
```

197cha 측정 기록: 감싸지 않으면 기본 Params 경로(`Path.home()/.comma/params/d`, 디바이스는 `/data/params/d`)에 실제로 쓰고, msgq 경로도 격리되지 않아 `IpcError: Messaging failure with radarState`가 났다. 이 두 증상은 197cha 세션 기록이며 207cha에서는 재현하지 않았다(코드로 확인한 것은 위 68~73행, `conftest.py` 51행, `prefix.py`의 존재까지).

매 스텝 기록이 필요하면 `openpilot/selfdrive/controls/tests/test_following_distance.py` 25행의 `RecordingPlant`(Plant 서브클래스를 만들어 33행에서 `maneuver_module.Plant`를 대체하는 방식)를 참고한다. 197cha 측정 스크립트 자체는 저장소에 없는 스크래치라 재현할 수 없어 toolkit에 넣지 않기로 했다(207cha 사용자 결정, WIP.md 207cha 2번).

### 215차 추가 (pytest_ci_setup.sh에 comma-deps-raylib 설치 추가)

`pytest_ci_setup.sh`의 3/6 단계에서 기존 pip 목록 설치 뒤에 `comma-deps-raylib==6.0.0.1.post103`을 별도 `pip install` 한 줄로 추가하고 이유를 주석 4줄로 남겼다. 끝의 자가검증(`python3 -c`)에는 `import pyray`를 넣고 성공 메시지에 pyray를 추가했다(다른 단계는 변경 없음). `openpilot/selfdrive/ui/tests`의 HUD 테스트(`test_carrot_hud_renderer.py`, `test_carrot_param_cache.py` 등)는 pyray를 import하는데, 이전에는 세션마다 수동으로 `pip install`을 해야 했다(213cha/214cha).

주의: PyPI의 별도 패키지 `raylib`도 같은 `pyray` 디렉터리를 쓴다. 섞였으면 `pip uninstall --break-system-packages raylib` 뒤 `pip install --break-system-packages --force-reinstall --no-deps comma-deps-raylib==6.0.0.1.post103`. 이 줄이 실패하면 스크립트의 `set -e` 때문에 전체가 중단된다(wheel 파일명이 `manylinux_2_28_x86_64`라 다른 플랫폼에서는 실패할 수 있다. 이 스크립트의 대상은 Claude 샌드박스 Ubuntu 24다).

215cha 샌드박스 실측: 수정본 전체 실행 1~6단계 통과와 자가검증 OK, HUD 테스트 3개 파일(`-n 0 -p no:randomly -q -W default`) 46 passed(수동 pip install 없이). 이 구성만으로 `test_raylib_ui.py::test_raylib_ui` 1건과 `mici/tests/test_widget_leaks.py` 수집 에러가 어떻게 되는지는 확인하지 않았다(원인 미조사).

### 216차 추가 (pytest_ci_setup.sh에 msgq.visionipc.visionipc_pyx 빌드 추가)

`pytest_ci_setup.sh`에 5c단계를 추가했다(5b의 `msgq.ipc_pyx` 빌드 바로 뒤, 6/6 앞). `msgq_repo/SConscript`의 visionipc 소스 목록(`visionipc.cc`, `visionipc_server.cc`, `visionipc_client.cc`, /dev/ion이 없는 PC이므로 `visionbuf.cc`)과 msgq 소스 5개를 5b와 같은 setuptools 방식으로 컴파일해 `msgq.visionipc.visionipc_pyx`를 만든다. 끝의 자가검증에는 `import msgq.visionipc.visionipc_pyx`를 넣고 성공 메시지에 visionipc를 추가했다(다른 단계는 변경 없음, +26/-1). 산출 `.so`는 `msgq_repo/msgq/visionipc/` 안에 생기며 git이 무시한다(`git status` 변화 없음 확인).

이유: `selfdrive/ui`의 `onroad/driver_camera_dialog.py` 등이 `from msgq.visionipc import VisionStreamType`를 하는데, 5b는 `msgq.ipc_pyx`만 빌드해서 `ModuleNotFoundError: No module named 'msgq.visionipc.visionipc_pyx'`가 났다. 이 때문에 `ui` 프로세스를 띄우는 `test_raylib_ui.py::test_raylib_ui`가 프로세스 조기 종료 단언(`selfdrive/test/helpers.py` 92행)으로 실패했고, `mici/tests/test_widget_leaks.py`는 수집 단계에서 같은 에러였다.

216cha 샌드박스 실측(수정본 전체 실행 1~6단계 통과, 자가검증 OK): `selfdrive/ui/tests` 175 passed / 86 skipped / 0 failed(수정 전 214cha 기록은 1 failed / 174 passed / 0 errors), `test_raylib_ui.py` 1 passed(약 5초), `mici/tests`는 `test_widget_leaks.py`를 뺀 21 passed.

한계: `mici/tests/test_widget_leaks.py`는 이 빌드로 해결되지 않는다. 13행이 `mici/widgets/dialog.py`에 없는 `BigConfirmationDialogV2`를 import해 여전히 수집 에러이며, carrot-ms(d03c0ae)의 같은 두 파일과 바이트 동일한 업스트림 상태다(WIP.md 216cha 2번). 그 테스트 함수는 원래 `@pytest.mark.skip(reason="segfaults")`라 이름을 고쳐도 실행되지 않는다. `mici/tests`를 돌릴 때는 `--ignore=openpilot/selfdrive/ui/mici/tests/test_widget_leaks.py`를 주거나 `--continue-on-collection-errors`를 쓴다. 이 스크립트의 대상은 Claude 샌드박스 Ubuntu 24이며, /dev/ion이 있는 기기에서는 SConscript가 `visionbuf_ion.cc`를 쓰므로 소스 목록이 다르다.

### 252차 추가 (gap_recovery 실로그 재생: gap_replay/gap_replay.py)

| 도구 | 설명 |
|---|---|
| `gap_replay/gap_replay.py extract <schema_dir> <segs_dir> <out.pkl>` | `<segs_dir>/*--<n>/rlog.zst`를 읽어 longitudinalPlan 20Hz 프레임마다 carState/selfdriveState/carControl/modelV2.meta/radarState.leadOne/longitudinalPlan(tFollow, desiredDistance 등)을 최신값으로 병합하고 initData 파라미터와 함께 `out.pkl`(dict(df, params))로 저장 |
| `gap_replay/gap_replay.py replay <plan.pkl> <new_gap.py> [<old_gap.py>] [--cb 2.5]` | `longitudinal_gap_recovery.py`의 `LeadGapState`를 로그 입력으로 20Hz open-loop 재생해 로그 desiredDistance와 비교(충실도 MAE/상관, 기준 거리 대비 거리비 구간별 마진 표). `new_gap.py`/`old_gap.py`는 비교할 커밋의 `openpilot/selfdrive/controls/lib/longitudinal_gap_recovery.py` 사본 |

환경: `pip install --break-system-packages pycapnp zstandard numpy pandas`. 스키마 폴더는 **로그를 기록한 커밋**의 `openpilot/cereal/*.capnp`, `openpilot/cereal/include/`, `opendbc_repo/opendbc/car/car.capnp`를 한 폴더에 모은 것이다(`car.capnp`는 `log.capnp`와 같은 위치, `git clone --filter=blob:none --no-checkout` + `sparse-checkout`). 로그 zip은 세그먼트별로 풀어 `<route>--<n>/rlog.zst`를 한 폴더(`<segs_dir>`)에 모은다. 실행 예: `gap_replay.py extract ../schema ../segs out/plan.pkl`(18개 세그먼트 약 45초, 한 명령 300초 제한이 있는 환경에서는 `setsid nohup ... < /dev/null &`) -> `gap_replay.py replay out/plan.pkl new_gap.py old_gap.py`. 구버전 사본은 SHA 고정 raw URL(`https://raw.githubusercontent.com/ryujmin97/openpilot/<40자리 SHA>/openpilot/selfdrive/controls/lib/longitudinal_gap_recovery.py`)로 받는다.

재생 조건(로그 `initData`와 plan에서 읽음): level은 `LeadAccelResponse`와 `LeadAccelResponseTF1~4`(selfdriveState.personality로 선택, -1이면 공통값)에 `MyDrivingMode` 상한(Eco 2, Safe 3, 그 외 5)을 적용하고, stop_distance는 `StopDistanceCarrot`/100, comfort_brake는 `--cb`(기본 2.5)다. 활성 조건은 `long_mpc.py`의 eligible과 `longitudinal_planner.py`의 `lead_gap_enabled`를 로그로 근사한 것이다: experimentalMode False, longActive, not gasPressed, modelV2 laneChangeState == off, lead_track_frames >= 3(planner `update_lead_tracks` 규칙을 radarState.leadOne status/radar/radarTrackId로 재계산), leadOne.status and leadOne.radar. 로그에 없는 reset_state, force_slow_decel, `carrot.lane_change_active`는 근사다. 한계: v_ego는 MPC의 x0[1]이 아니라 carState.vEgo, 로그 desiredDistance의 relief(컷아웃/차선변경 완화)는 무시, 자차 거동이 바뀐 뒤의 폐루프는 재현하지 않는다. 앞차 트랙이 끊겨 desiredDistance가 0 이하로 튀는 프레임은 `desired > 0` 조건으로 제외된다. level 0의 `LeadAccelResponse` 0 설정에서만 252cha에 확인했다. 252cha 결과와 해석은 WIP.md 252cha 참고(670f72c 기록 로그에서 신 코드 재생 MAE 0.440 m, f9ffbc2 재생 0.810 m, 거리비 1.2 초과에서 0.492 m 대 2.246 m). 실차 검증 아님.

### 255차 추가 (gap_replay/ext2.py: 확장 필드 병합)

| 도구 | 설명 |
|---|---|
| `gap_replay/ext2.py <schema_dir> <segs_dir> <out.pkl>` | `gap_replay.py extract`와 같은 입력(`<segs_dir>/*--<n>/rlog.zst`, 스키마 폴더)으로 longitudinalPlan 20Hz 프레임마다 최신값을 병합하되 필드를 늘린 버전. 추가 필드: carState aEgo/brake/standstill/vCruise, selfdriveState enabled, carControl accelCmd(actuators.accel), radarState leadOne yRel/aLeadK/aLeadTau/modelProb와 leadTwo status, longitudinalPlan aTargetBase/longitudinalPlanSource/shouldStop/hasLead/fcw/jTargetNow/xState/vTargetNow/cruiseTarget/allowThrottle/leadPreviewSeconds/aChangeCost/accels[0,5,10]. pkl은 dict(df, params, ev_count)이고 `df` 열 이름은 `gap_replay.py replay`가 읽는 열(t, vEgo, gas, lc, pers, exp, longActive, r_status/r_radar/r_tid/r_dRel/r_vRel/r_vLead, tFollow, desired, aTarget, myMode)을 포함한다. |

`gap_replay.py replay`에 이 pkl을 그대로 넘겨도 동작한다(255cha 실측: 신 MAE 0.440, 구 0.810으로 252cha와 같은 수치). 환경과 실행 시간(18개 세그먼트 약 45~60초, `setsid nohup ... < /dev/null &`)은 252차 추가 절과 같다. 한계: 재생은 open-loop이고 정지 앞차 근처 장면은 로그에 활성 프레임이 있어야 검증된다. 실차 검증 아님.
