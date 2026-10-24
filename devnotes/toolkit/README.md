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

### 256차 추가 (jerk_sim/: 정차 앞차 접근 JerkCostEgo 폐루프 비교)

| 도구 | 설명 |
|---|---|
| `jerk_sim/sim_jerk.py <plan.pkl> <out.pkl>` | 실차 로그의 정차 앞차 접근 장면을 carrot-ryu의 실제 `LongitudinalPlanner`(acados MPC)와 `CarrotPlanner`에 넣어 `JerkCostEgo` 5/8/12/20을 폐루프로 비교한다(사용자가 256cha에 올린 파일, 수정 없음). `Plant` 서브클래스 `SimPlant.step2`가 앞차 측정값(dRel/vLead/aLeadK/modelProb)을 직접 주입하고 구동계(지연 `DELAY_S` + 1차 지연 `TAU_S`)를 모델링한다. 시나리오 A = 로그 그대로의 인식(거리 오차 + 로그 vLead/aLeadK), A2 = 거리 오차만 로그 그대로(vLead 0), B = 이상적 인식(정지 버스, 오차 없음). 버스 위치는 로그에서 vEgo < 0.1이 된 시점(t > 12초)의 비전 dRel과 vEgo 적분 위치로 복원한다(`build_inputs`, 버스가 정차 중이라는 가정). 기기 initData 파라미터를 `OpenpilotPrefix` 안에서 가능한 타입으로 주입하고 `JerkCostEgo`만 바꾼다. 이 파일을 그대로 `__main__`으로 돌리면 지연 0.30 s, 시상수 0.15 s이고 로그 구간은 t0 = 5 s ~ 14 s, 순항 설정속도 17.9 m/s가 하드코딩돼 있다. `build_inputs`의 `bus_gap_final` 인자는 함수 안에서 덮어써 쓰이지 않는다. |
| `jerk_sim/run_final.py <plan.pkl> [out.pkl]` | `sim_jerk.py`를 지연 0.35 s / 시상수 0.15 s로 덮어써 A/A2/B x J 5/8/12/20 12회를 돌리고 10.83초 속도·필요 감속(v^2/2g)·최대 저크·최소 간격 표를 출력한다. 0.35 s는 J=20 시뮬레이션의 10.85초 속도를 실차 13.69 m/s에 맞춘 값이다(지연 0.30/0.35/0.40에서 13.39/13.57/13.76, 이전 구간 보정 출력). 256cha에 실제 실행해 12행 표를 확인했다(WIP.md 256cha 6번). |

환경: `bash pytest_ci_setup.sh`(carrot-ryu clone + acados 코드생성까지, 약 4~5분)로 `/home/claude/repo`를 만든 뒤 `cd /home/claude/repo && export PYTHONPATH=/home/claude/repo:/home/claude/repo/opendbc_repo && python3 jerk_sim/run_final.py <plan.pkl>`. plan.pkl은 `gap_replay/ext2.py`(255차) 출력이고 열 `r_aLeadK`, `r_modelProb`, `r_status`, `r_dRel`, `r_vLead`, `vEgo`, `t`가 필요하다. 12회 실행은 약 100초이므로 한 명령 제한이 있는 환경에서는 `setsid nohup ... < /dev/null &`. 한계: 앞차 측정값을 로그에서 그대로 넣는 open-loop 인식이고, 구동 모델은 J=20 한 장면에 맞춘 것이라 J=5/8/12는 외삽이며, 실차에서 개입한 정지 경로(계획 소스 4)와 운전자 개입은 재현하지 않는다. 실차 검증 아님. 결과와 해석은 WIP.md 256cha.

### 257차 추가 (radar_gate/: EnableRadarTracks 0 대 -1 비전 앞차 게이트 재생)

| 도구 | 설명 |
|---|---|
| `radar_gate/gate_replay.py <schema_dir> <rlog.zst> [t_from t_to]` | rlog 1개에서 radarState.leadOne(status/radar/dRel/vLead), liveTracks 점 개수, modelV2.leadsV3[0](prob/x/v)와 modelV2.position 보간 dPath를 뽑아, 670f72c의 비전 앞차 규칙(`primary.py` `_update_vision_fallback` 채택 prob 0.40/유지 0.35 초과 10프레임, `controller.py` `_central_vision_fallback_allowed` prob 0.40 + |dPath| 1.0 m)을 프레임마다 재생한다. 모드 0(게이트 적용)과 모드 -1(게이트 면제)의 앞차 유무와 앞차 끊김 횟수를 구간별로 로그 값과 비교하고 로그에서 앞차가 끊긴 첫 프레임의 비전 prob/dPath를 출력한다. `<schema_dir>`는 `openpilot/cereal/*.capnp`, `cereal/include/c++.capnp`(include/ 아래), `opendbc_repo/opendbc/car/car.capnp`를 한 폴더에 모은 것이다. 실행 `python3 -I gate_replay.py <schema_dir> <rlog.zst> [8.0 10.85]`(zstandard, pycapnp, numpy 필요, 60초 세그먼트 약 수 초). |

한계: open-loop 근사다. dPath는 실제 `project_to_model_path` 대신 `modelV2.position`을 비전 x에서 보간한 값이고(256cha 로그 8.0~10.85초 57프레임 중 4프레임이 로그와 다름), SCC 점이 있는 프레임(liveTracks 점 있음)은 처리하지 않아 SCC 점이 없는 장면에서만 의미가 있다. 자차 거동 변화 반영 없음. 실차 검증 아님. 결과와 해석은 WIP.md 257cha.

### 258차 추가 (radar_gate/exact_gate.py: 실제 코드 함수로 비전 앞차 게이트 재생과 완화안 비교)

| 도구 | 설명 |
|---|---|
| `radar_gate/exact_gate.py <schema_dir> <repo_dir> <rlog.zst> [t_from:t_to ...]` | 670f72c의 `controller.py` `_central_vision_fallback_allowed`와 `primary.py` `vision_lead_from_model`/`_update_vision_fallback` 규칙을 재구현 없이 재생한다. 실제 `openpilot/selfdrive/carrot/radar_motion/predictor.py`의 `project_to_model_path`를 import하고(`<repo_dir>`는 로그 기록 커밋의 carrot-ryu 체크아웃 루트, 필요한 파일: `openpilot/selfdrive/carrot/radar_motion/*.py`와 `opendbc_repo`의 import 경로), 비전 후보는 `d_rel = x[0] - 1.52`, `y_rel = -y[0]`, radarState 직전의 최신 modelV2 값을 쓴다. 구간(기본 8.0:10.85, 40.9:45.1)별로 로그 present/모드 0 재생/모드 -1 재생/일치/끊김 횟수와 불일치 프레임, 레이더 앞차 없는 프레임 전체 일치율, 끊긴 첫 프레임의 prob/dPath/dRel, 끄는 문턱(1.2/1.5/1.8 m)과 홀드(3/6프레임) 완화안 비교표, 비전 후보 \|dPath\| 분포를 출력한다. 실행 `python3 -I exact_gate.py <schema_dir> <repo_dir> <rlog.zst> [8.0:10.85 40.9:45.1]`(zstandard, pycapnp, numpy 필요, 60초 세그먼트 약 수십 초). `<schema_dir>`는 gate_replay.py와 같다. |

`gate_replay.py`(257차)는 dPath를 `modelV2.position` 보간으로 근사하고 `x - 1.52`와 `y` 부호를 쓰지 않아 실제 값과 다르다(258cha: 8.05초 0.89 대 실제 -1.02 등). 비전 게이트 재생에는 `exact_gate.py`를 쓴다. 한계: open-loop이고 레이더/SCC 앞차가 있는 프레임은 대상이 아니며, 완화안은 오감속과 제어 거동을 시뮬레이션하지 않는다. 670f72c 로그(route 00000492 세그먼트 4)에서 레이더 앞차 없는 336프레임이 로그와 336/336 일치했다. 실차 검증 아님. 결과와 해석은 WIP.md 258cha.

### 259차 추가 (radar_gate/release_replay.py: carrot-ryu 1326f21 비전 앞차 해제 대역·홀드 게이트를 실제 코드로 재생)

| 도구 | 설명 |
|---|---|
| `radar_gate/release_replay.py <schema_dir> <repo_dir> <rlog.zst> [t_from:t_to ...]` | 1326f21 이상 carrot-ryu의 `openpilot/selfdrive/carrot/radar_motion/controller.py` `DPathRadarController._update_vision_central_gate`를 재구현 없이 호출한다(상태 `_vision_central_gate_active`/`_vision_central_gate_release_frames`와 `_reset_vision_central_gate`를 가진 대역 객체에 바인딩, `<repo_dir>`는 그 커밋 체크아웃 루트이며 `openpilot/selfdrive/carrot`, `openpilot/cereal`, opendbc `car.capnp`가 필요). 비전 후보는 `exact_gate.py`와 같다(`d_rel = x[0] - 1.52`, `y_rel = -y[0]`, 채택 prob 0.40 이상, 0.35 초과 최대 10프레임 유지, radarState 직전 최신 modelV2). 레이더 앞차(`leadOne.radar` True)가 있는 프레임은 실제 코드가 vision=None으로 게이트 상태를 초기화하는 경로라 비교에서 빼고 present로 센다. 출력: 레이더 앞차 없는 프레임의 670f72c 규칙 재생 대 로그 일치 수, 670f72c/1326f21 규칙 present 수와 증감, 구간(기본 8.0:10.85 40.9:45.1)·전체 60초 끊김 횟수, 추가 present 프레임 목록(dRel/prob/dPath/비전 v/자차 속도/`cruiseState.enabled`)과 크루즈 작동 중 개수, 레이더 인계 전후 프레임, 홀드 중 prob 0.40 미만 present 수. 실행 `python3 -I release_replay.py <schema_dir> <repo_dir> <rlog.zst>`(zstandard, pycapnp, numpy 필요, 60초 세그먼트 수십 초). `<schema_dir>`는 `exact_gate.py`와 같다. |

한계: open-loop이고 자차 거동이나 오감속은 시뮬레이션하지 않는다(추가 present가 실제 앞차인지 옆 차선 차인지는 이 도구로 판정할 수 없다). 레이더/SCC 앞차가 있는 프레임은 재생 대상이 아니다. 로그가 1326f21 이전 코드로 기록됐다면 새 코드의 기기 거동이 아니라 새 함수에 로그 입력을 넣은 결과다. 670f72c 로그(route 00000492 세그먼트 4)에서 670f72c 규칙 재생이 로그와 336/336 일치했고 1326f21 재생은 끊김 10 -> 0, 추가 present 30프레임이었다. 실차 검증 아님. 결과와 해석은 WIP.md 259cha.

### 260차 추가 (radar_gate/margin_scan.py, jerk_sim/run_gap.py, jerk_sim/calib_gap.py: 1326f21 게이트가 크루즈 작동 중 만드는 프레임과 끊김 유지 대 채움 시뮬레이션)

| 도구 | 설명 |
|---|---|
| `radar_gate/margin_scan.py <schema_dir> <repo_dir> <rlog.zst> [<rlog.zst> ...]` | 1326f21 이상 carrot-ryu의 `_update_vision_central_gate`와 670f72c 규칙 `_central_vision_fallback_allowed`를 `release_replay.py`와 같은 방식(실제 코드 호출, 비전 후보 `d_rel = x[0] - 1.52`, `y_rel = -y[0]`, 채택 prob 0.40/유지 0.35 초과 10프레임)으로 rlog 여러 개에 재생하고, 레이더 앞차(`leadOne.radar` True)가 없는 radarState 프레임 중 `cruiseState.enabled`인 프레임만 세그먼트별로 집계한다: n(레이더 앞차 없는 프레임), cr(그중 크루즈 작동), cand_cr(비전 후보 있음), old_cr/new_cr(670f72c/1326f21 규칙 present), extra_cr(1326f21만 present), blocked_cr(후보가 있는데 1326f21도 차단), slower_blocked(차단된 후보 중 비전 v가 자차보다 1 m/s 이상 느림), minblk(차단된 후보의 최소 \|dPath\|). `<schema_dir>`와 `<repo_dir>`는 `release_replay.py`와 같다. 실행 `python3 -I margin_scan.py <schema_dir> <repo_dir> seg1/rlog.zst seg2/rlog.zst ...`(세그먼트당 수십 초). |
| `jerk_sim/run_gap.py <plan.pkl> [out.pkl]` | `sim_jerk.py`의 `SimPlant`/`build_inputs`를 재사용해 시나리오 G(로그의 `r_status`/`r_dRel>1`이 False인 프레임에서 lead=None, 끊김 유지 = 670f72c 거동)와 A(256cha의 A: 끊김 프레임을 선형 보간으로 채움 = 1326f21 거동의 근사)를 J 5/8/12/20으로 돌려 10.83초 속도, 필요 감속, 최대 저크, 최소 간격, 정지 버스 도달 시각/속도 표와 앞차 없음 프레임 수를 출력한다. 지연 0.35 s/시상수 0.15 s. `sim_jerk.py`와 같은 폴더에서 `pytest_ci_setup.sh` 환경(`PYTHONPATH=/home/claude/repo:/home/claude/repo/opendbc_repo`)으로 실행, plan.pkl은 `gap_replay/ext2.py` 출력. 8회 실행 약 90초이므로 `setsid nohup ... < /dev/null &`. |
| `jerk_sim/calib_gap.py <plan.pkl>` | 같은 환경에서 G/A를 J=20, 구동 지연 0.10/0.20/0.30/0.35/0.45 s로 돌려 실제 속도(`vEgo`)와의 8~11.5초 RMSE와 10.85초 속도를 출력한다(어느 시나리오가 실제와 맞는지 보는 보정 검사, 10회 실행 약 100초). |

한계: 세 도구 모두 open-loop 인식 주입이고 후보가 옆 차선인지 자차 차선인지 판정하지 않는다. `margin_scan.py`는 차단 사유(prob 대 dPath)를 구분하지 않는다. `run_gap.py`의 A는 채운 프레임의 dRel/vLead가 보간값이고 구동 모델은 J=20 한 장면에 맞춘 것이며(256cha), 운전자 개입과 정지 경로(계획 소스 4)를 재현하지 않는다. G는 실제보다 끊김의 누적 효과를 크게 만든다(실제 속도는 A 쪽, 260cha). 결과와 해석은 WIP.md 260cha. 실차 검증 아님.

### 269차 추가 (cl_sim/: 실제 acados MPC 폐루프로 기준선 대 변경본 비교)

carrot-ms 8212379 이식(carrot-ryu 760905a)을 검증하려고 만든 도구다. `LongitudinalMpc`(실제 acados 솔버)를 자차 플랜트 모델과 이상적 레이더 앞차 1대로 폐루프 구동하고, HEAD 모듈과 기준선 모듈을 같은 시나리오에 돌려 최소 간격/시간차/TTC/최대 제동/저크/FCW 카운트를 비교한다. 결과 해석은 WIP.md 269cha. 실차 검증 아님.

| 파일 | 역할 |
|---|---|
| `prep_base.sh <기준선 커밋> [저장소 루트]` | 기준선의 `long_mpc.py`를 `long_mpc_base110.py`(같은 폴더, 모듈 이름 고정)로 복사한다. 쓰고 나면 그 파일을 지워 `git status`를 깨끗하게 한다. depth 1 clone이면 먼저 `git fetch --depth 2 origin <브랜치>`로 부모 커밋을 받는다. |
| `cl_sim.py` | `run(mod, scen, tf, ego_tau=0.35, delay=0.15, T, vset, lead_gap_enabled)` 폐루프와 `metrics(log)`. 이 모듈이 `head_mod`(현재 long_mpc)와 `base_mod`(기준선 모듈)를 임포트한다. 레이더 노이즈/지연, 플래너 리셋 램프, 끼어들기 사전감속, 앞차 2대는 없다. |
| `scen.py` | `mk(v0, tf, events, appear=None, present_from=0, gap_extra=0)`: 앞차를 `(시작 시각, 가속도, 목표속도)` 목록으로 만든다. `appear=(t, 간격)`은 끼어들기. |
| `sweep.py` | 고정 10시나리오(완만/중간/급 감속, 정지, 아코디언, 끼어들기 2종, 접근 진입) x TF 1.0/1.45/2.0. 약 20초. `sweep.json` 저장. |
| `relief.py` | 편안함 완화가 켜지는 먼/근거리 완만 감속 15케이스와 `comfort_path_has_reserve` 호출/거절 횟수. |
| `fuzz.py [N]`, `fuzz_summary.py [fuzz.json]` | 시드 20261012 무작위 케이스 N개(기본 120, 160케이스 약 7분이라 `setsid nohup ... < /dev/null &`)와 안전 지표 집계. |
| `fallback.py` | `comfort_path_has_reserve`를 항상 False로 바꿔 완화 해제 폴백을 강제로 발동시키고 정상/강제/기준선을 비교. |

환경: `pytest_ci_setup.sh`(약 3~4분)로 `/home/claude/repo`를 만든 뒤 `export PYTHONPATH=/home/claude/repo:/home/claude/repo/opendbc_repo`. 스크립트들은 같은 폴더에서 서로를 임포트하고 결과 json을 현재 폴더에 쓴다(`cd <작업 폴더>; python3 <cl_sim 경로>/sweep.py`). 기준선 모듈 이름이 `long_mpc_base110`로 고정돼 있어 다른 기준선을 쓰면 파일 이름은 그대로 두고 내용만 바꾼다. 한계: 레이더 이상적, 앞차 1대, 자차 응답 값(0.35 s/0.15 s)을 실차에 맞춰 보정하지 않았다. 복원 이력: 앞 세션 파일이 샌드박스 초기화로 사라져 기록에서 복원했고, 복원본으로 앞 세션 수치를 재현했다(269cha). 이 파일들은 Windows PowerShell 5.1에서 실행하는 도구가 아니다(샌드박스 전용).

### 276차 추가 (lead_replay/: 로그 앞차 입력 재생과 로그 앞차 궤적 폐루프)

275cha 로그(route 0000049d)의 119초 급제동 장면을 분석하려고 만든 도구다(앞 구간 기록에서 복원, 275cha 해석 정정 포함, 결과 해석은 WIP.md 276cha). 실제 acados `LongitudinalMpc`(HEAD)에 로그의 앞차 입력을 넣어 게이트만 끈 열린 루프 재생과, 앞차 참값 궤적을 만들어 자차를 1차 플랜트로 응답시키는 폐루프를 돌린다. `cl_sim/`은 합성 시나리오용이고 이 폴더는 실로그용이다(`cl_sim.py`의 `mk_carrot`, `lead_ns`를 가져다 쓴다). 실차 검증 아님.

| 파일 | 역할 |
|---|---|
| `extract_log.py <schema> <segs> <out.pkl>` | rlog.zst -> pkl(cs/cc/rs/lp/gt). leadOne/leadTwo 전 필드, carControl accel, longitudinalPlan, logMessage의 `lead_gate` 줄을 담는다. `python3 -I`로 실행. initData는 읽지 않는다(시크릿). 옛 `lead_decel/parse_lead_log.py`의 후속 격 |
| `ol_replay.py [t0 t1]` | 열린 루프: 로그 leadOne/leadTwo와 vEgo/aEgo를 MPC에 투입, 게이트 그대로(hd) 대 g=1 강제(goff) 대 로그 aTarget. `gate_trace()`로 프레임별 g도 본다. 결과 `ol_replay.pkl` |
| `lead_fit.py [lo hi]` | 앞차 감속 시작 ts와 감속 a를 비전 점에 최소제곱으로 맞춘다. 275/276cha 로그에서는 해가 경계에 붙어 참고용 |
| `plant_fit.py [lo hi]` | 자차 1차 플랜트(시정수, 지연)를 로그 명령과 vEgo에 맞춘다. 로그에서 0.4 s/0 s, RMSE 0.236 m/s |
| `cl_replay.py` | 폐루프: `lead_true(ts)`로 앞차 참값 궤적, `run(ts, 'vision'/'ideal', gate_off, vset)`, `summ()`, `log_row()`. 인자 없이 실행하면 8런(약 2~4분) |
| `batch.py` | `cl_replay.run` 민감도 묶음(ts 3점 x 입력 x 게이트 + 설정속도 19.4). 약 11런이라 `setsid nohup ... < /dev/null &`로 돌린다 |
| `vision_stats.py` | 비전 단독 대 레이더 앞차의 속도 잡음/aLeadK 과소 보고 통계와 비전 -> 레이더 인계 사건 표 |
| `cruise_speed.py <schema> <segs> [t ...]` | `carState.cruiseState.speed/enabled`를 지정 시각에 출력(로그에서 설정속도를 읽을 수 있는지 확인) |

실행 순서: (1) `pytest_ci_setup.sh`(약 3~4분) -> `cd /home/claude/repo && git fetch --depth 3 origin carrot-ryu` -> `bash <toolkit>/cl_sim/prep_base.sh HEAD~2`(`cl_sim.py`가 기준선 모듈을 임포트하므로 필요하다. 끝나면 `long_mpc_base110.py`를 지운다) -> `export PYTHONPATH=/home/claude/repo:/home/claude/repo/opendbc_repo`. (2) 스키마를 로그 기록 커밋 기준으로 모으고(97차 환경 구성) `python3 -I extract_log.py <schema> <segs> log_lead.pkl`. (3) 작업 폴더에서 `export LR_PKL=$PWD/log_lead.pkl` 뒤 `python3 ol_replay.py`, `plant_fit.py`, `cl_replay.py`, `batch.py`, `vision_stats.py`. `cl_sim` 폴더 위치는 같은 toolkit 안 `../cl_sim`이 기본이고 `CL_SIM_DIR`로 바꾼다.

주의: `cl_replay.py`의 값 중 로그 0000049d 전용이 있다(T0~T1 112~126초, 앞차 감속 전 속도 16.4 m/s, 레이더 인계 119.0초, 설정속도 17.9 m/s, stop_distance 7.0, comfort_brake 2.5, TAU/DELAY 0.4/0). 다른 로그에는 이 값부터 바꾼다. 앞차 참값 궤적은 추정이고 레이더/비전 지연과 노이즈, 플래너 리셋 램프가 없다. 로그 값 조회는 영차 유지여야 하고(선형 보간은 앞차 끊김 구간에서 가짜 제동을 만든다), 게이트 교체는 `__dict__['_gate_raw'].__func__`로 한다(WIP.md 276cha 함정).

복원 이력: 앞 구간의 스크립트가 샌드박스 초기화로 사라져 대화 기록에서 복원했다. 경로를 인자/환경변수로 바꾸고 앞 구간에서 고친 내용을 반영했으며 논리는 같다. 실제 로그로는 다시 돌리지 못했고, 합성 로그(pkl, rlog.zst)로 8개 모두 끝까지 도는 것만 샌드박스에서 확인했다. 이 파일들은 Windows PowerShell 5.1에서 실행하는 도구가 아니다(샌드박스 전용).

### 277차 추가 (dead_scan/: first-party 정의의 이름 기준 참조 스캔과 연쇄 후보 분류)

277cha 데드코드 감사(HANDOFF 13)에서 만든 도구다(결과 해석은 WIP.md 277cha). 파일마다 ast를 한 번만 파싱해 `selfdrive/carrot/**`, `carrot/**`, `controls/lib/**`(테스트 제외)의 함수/메서드/클래스 정의마다 이름 기준 참조 수를 센다. 파이썬 3 표준 라이브러리만 쓴다.

| 파일 | 역할 |
|---|---|
| `scan.py <repo_dir> <out_dir>` | `<out_dir>/defs.json`(정의별 비테스트/테스트/비파이썬/문자열 참조 수), `refs_low.json`(참조 6개 이하 이름의 위치)을 만든다. 저장소 전체에서 `docs/`, `tinygrad_repo/`, 생성 번들, 2 MB 초과 파일은 건너뛴다. 약 40초 |
| `classify.py <out_dir>` | live / 참조 0건(zero) / 데코레이터 있는 0건 / 자기 본문에서만 / 테스트에서만(test_only) / 비파이썬·비테스트 문자열에서만(dyn_only)으로 분류하고, 프레임워크 오버라이드·벤더·`_ingest_*`·데코레이터 등록 함수를 뺀 직접 후보와, 후보 본문 안에서만 호출되는 정의를 고정점까지 추가한 연쇄 후보를 출력한다. `candidates.json`도 쓴다 |

실행 순서: `git clone --depth 1 --branch carrot-ryu <url> repo`(약 508 MB, 샌드박스에서 약 90초라 `setsid nohup ... < /dev/null &`로 분리) -> `python3 scan.py repo out` -> `python3 classify.py out`. 한 명령은 300초 제한이 있어 scan은 파일당 1회 파싱으로 유지한다.

한계: 이름 기준이라 "참조 0건"은 확실하지만 "참조 있음"은 상한이다(동명 메서드, `getattr` 동적 호출 구분 불가). `__all__` 안의 문자열은 사용으로 세지 않는다. `*_test.py` 접미사 파일(`server/**/vision_test.py`, `youtube_test.py`)은 `carrot` 명령이 쓰는 운영 유틸이라 테스트로 보지 않는다. 저장소 밖 소비자(앱 등)는 보지 못하고, 연쇄 2단계 이후는 삭제 전에 호출처를 grep으로 다시 확인한다. 새로 작성한 도구라 복원 이력은 없고, carrot-ryu c4f13a7에서 실행해 직접 후보 19, 연쇄 11을 얻었다. 실차 검증과 무관한 정적 분석이다.

### 286차 추가 (lead_dropout/: 크루즈 중 앞차 끊김 구간 표, 프레임 덤프, 비전 앞차 차선 위치, 게이트 변형 재생)

286cha(WIP.md 286cha, 286cha 계속)에서 route 000004a0(기록 커밋 e1fa15a, 도심 180초)의 97.90~99.15초 "앞차 끊김"을 분석하려고 만든 도구다. 앞 구간 기록에서 복원했고 경로를 인자/환경변수로 바꿨으며 논리는 같다. 286cha 계속에서 올린 로그(세그먼트 1~3)와 e1fa15a 스키마/`radar_motion` 코드로 5개 모두 실제 로그에서 끝까지 돌려 앞 구간 수치(끊김 7개 표, V0~V5 표, 97.85/97.90초 게이트 프레임)와 같은 값을 얻었다. 실차 검증 아님.

| 파일 | 역할 |
|---|---|
| `dropouts2.py [log_lead.pkl]` | `lead_replay/extract_log.py`의 pkl에서 크루즈(longActive) 중 leadOne.status가 끊겼다 돌아온 구간(앞뒤 정상)을 표로 출력: 시각, 길이(False 프레임 수 x 0.05 s), 직전/재인식의 dRel vLead aLeadK 종류, accel 명령(직전 -> 끊김 중 최소/최대 -> 재인식 뒤 2 s 최소). 크루즈 시작 전 구간은 제외한다 |
| `frame.py <t0> <t1> [step]` | 같은 pkl의 시각 구간을 step 간격 한 줄씩: vEgo/aEgo, accel 명령, aTarget, desiredDistance, tFollow, leadOne/leadTwo, `lead_gate` g. pkl은 `LR_PKL`(기본 `./log_lead.pkl`) |
| `lane_check.py <rlog.zst> <t_from> <t_to> [route_offset]` | modelV2 후보(leadsV3[0])가 가까운 좌/우 차선(laneLines[1]/[2]) 사이 어디인지(0 = 왼쪽 선, 1 = 오른쪽 선), 모델 경로 y, 선 확률을 약 0.1 s 간격으로. 스키마는 `SCHEMA_DIR`(기본 `/tmp/schema`), `python3 -I`로 실행 |
| `variants.py <schema_dir> <repo_dir> <segs_dir> [ev_from:ev_to]` | 비전 앞차 중앙 차선 게이트를 변형 파라미터 V0~V5(현행, 유지 prob 0.35, 해제 대역 2.5/4.0 m, 유예 10프레임)로 오프라인 재생하는 open-loop 비교표. 세그먼트 route 오프셋은 첫 carState에서 계산한다. 게이트는 이 파일 안의 재구현이고(V0가 레이더 앞차 없는 프레임에서 로그와 전부 일치하는지로 확인), 실제 코드 호출은 `radar_gate/release_replay.py`다 |
| `release_replay_dump.py <schema_dir> <repo_dir> <rlog.zst> [t_from:t_to ...]` | `radar_gate/release_replay.py`에 `DUMP=<t_from>:<t_to>`(세그먼트 로컬 시각)와 `ROUTE_OFF=<초>` 환경변수 블록을 더한 사본. DUMP를 주면 프레임별 로그 status, 레이더, 1326f21 게이트(new), 670f72c 규칙(old), 비전 prob/dRel/dPath/v 표를 출력한다. 환경 변수 없이 쓰면 `release_replay.py`와 같다 |

실행 순서(000004a0 예시): (1) 스키마를 로그 기록 커밋 기준으로 모으고(97차 환경 구성), 로그 zip을 풀어 `<route>--<n>/rlog.zst`를 한 폴더(`segs`)에 모은다. `radar_motion` 코드는 `git fetch --depth 1 --filter=blob:none origin <커밋>` 뒤 `git checkout FETCH_HEAD -- openpilot/selfdrive/carrot/radar_motion`으로 받는다(`variants.py`, `release_replay_dump.py`용 `<repo_dir>`). (2) `python3 -I lead_replay/extract_log.py <schema> <segs> log_lead.pkl` 뒤 `export LR_PKL=$PWD/log_lead.pkl`, `python3 dropouts2.py`, `python3 frame.py 97.8 98.1 0.1`. (3) `SCHEMA_DIR=<schema> python3 -I lane_check.py <seg2 rlog.zst> 35.0 40.6 60.021`. (4) `python3 -I variants.py <schema> <repo_dir> <segs>`. (5) `DUMP=37.70:39.30 ROUTE_OFF=60.021 python3 -I release_replay_dump.py <schema> <repo_dir> <seg2 rlog.zst> 34:44`.

한계: 모두 open-loop이고 자차 거동과 오감속은 반영하지 않는다. `variants.py`의 변형 평가는 옆 차선 오감속 위험을 보지 못한다. `lane_check.py`의 위치 비 범위는 샘플 시각 격자에 따라 달라진다(약 0.095 s 간격으로 첫 샘플 시각 기준으로 뽑으며, 000004a0 route 97.88~99.14초는 `35.0 40.6`으로 시작하면 0.71~1.13, `37.7`로 시작하면 0.71~1.16). 부호 해석은 modeld 규약(y 양수가 오른쪽) 기준으로 코드로 확인하지 않았다. 구간·시각 기본값(`97.90:99.09`)은 000004a0 전용이다. 이 파일들은 Windows PowerShell 5.1에서 실행하는 도구가 아니다(샌드박스 전용).

### 287차 추가 (lead_dropout/full_replay2.py: DPathRadarController 전체 재생)

287cha(WIP.md 287cha)에서 route 000004a0(기록 커밋 e1fa15a)의 136.25초와 140.64~148.83초 앞차 끊김을 분석하려고 다시 쓴 도구다. 앞 세션의 `full_replay2.py`는 기록이 잘려 복원하지 못해 새로 썼고, 같은 로그에서 앞 세션과 같은 결과(로그 대조 일치율 100%)를 얻었다. 실차 검증 아님.

| 파일 | 역할 |
|---|---|
| `full_replay2.py <schema_dir> <repo_dir> <segs_dir>` | `<segs_dir>/<route>--<n>/rlog.zst`를 n 순서로 이어서, `radard_dpath.DPathRadarD.update`와 같은 입력(모델 시각 timestampEof, v_ego, liveTracks 점, livePose yaw, 레이더-모델 시간차)으로 `DPathRadarController`를 재생한다. 컨트롤러 인자(EnableRadarTracks, EnableCornerRadar, radarDelay)는 로그의 initData.params와 CarParams에서 읽는다. 매 radarState 프레임의 leadOne (status, radar)를 직전 modelV2 재생 결과와 대조(`CMPFROM`, 기본 route 100초 이후)하고 재생 끊김 구간(status False, route 90초 이후)을 출력한다 |

환경변수: `DUMP=a:b`(route 초 구간 프레임표: 재생 status/radar/dRel, 로그 값, 비전 prob(원->사용), 비전 d와 y_rel, 가장 가까운 레이더 점), `PROBFIX=a:b`와 `PROBMIN`(기본 0.45, 그 구간 비전 prob 하한), `FREEZE=a:b:src_t`(a~b 동안 비전 x/y를 src_t 직전 마지막 값으로 고정), `YSHIFT=a:b:dy`(a~b 동안 비전 y에 dy를 더함, 모델 y 부호 기준이고 y_rel = -y), `CMPFROM`, `QUIET=1`(요약과 끊김 구간만). `python3 -I`로 실행하고 의존은 pycapnp, zstandard다.

`<repo_dir>`은 `git fetch --depth 1 --filter=blob:none origin <기록 커밋>` 뒤 `git checkout FETCH_HEAD -- openpilot/selfdrive/carrot/radar_motion openpilot/selfdrive/carrot/radar`(스키마용 `openpilot/cereal/*.capnp`, `include`, `opendbc_repo/opendbc/car/car.capnp` 포함)로 받은 트리다. 횡 위치 허용치 변형(`YTOL`)은 이 트리를 복사한 사본에서 `primary.py`의 `or abs(point.y_rel - vision.y_rel) >= 2.0`(e1fa15a 3486행, 한 번만 나타남)을 `or abs(point.y_rel - vision.y_rel) >= float(__import__('os').environ.get('YTOL','2.0'))`로 바꾸고, 그 사본을 `<repo_dir>`로 넘기면서 `YTOL=2.5` 등을 주는 방식으로 쓴다(스크립트 안에는 이 치환이 없다).

검증(287cha, route 000004a0, e1fa15a, 세그먼트 3개): 재생 3,600프레임, route 100초 이후 1,599프레임에서 로그와 (status, radar) 1,599개(100.00%) 일치, 끊김 구간 95.35~95.75, 96.30~96.39, 97.90~99.09, 99.80~100.05, 136.25~139.54, 140.64~148.80, 160.80~160.90초. 한계: open-loop(자차 거동과 오감속 미반영). `radard_dpath`는 cereal 런타임이 필요해 샌드박스에서 import되지 않으므로 `corner_radar_enabled`를 줄여 썼고 `EnableCornerRadar`가 0보다 크면 중단한다. route 시각은 첫 세그먼트 첫 carState 기준 mono 초라 앞 세션 표(첫 carState 오프셋 상수 사용)와 약 0.02초 다를 수 있다. 앞 세션이 같이 쓰던 `geom_dump.py`(레이더 점/비전 후보 dPath 표)와 `track_dump.py`(liveTracks 덤프)는 저장하지 않았다. 샌드박스 전용이다.

### 288차 추가 (lead_dropout/track_dump.py, geom_dump.py: liveTracks 점 덤프와 radar_motion 매처 반환 경로 추적)

288cha(WIP.md 288cha)에서 route 000004a0(기록 커밋 e1fa15a)의 149.14초 레이더 5 m 대 비전 13~14 m 불일치를 조사하려고 쓴 도구 2개다. 287cha에서 앞 세션 사본이 저장되지 않아 288cha에서 다시 썼다. 같은 로그에서 288cha 분석 출력과 같은 값을 얻었다. open-loop 로그 읽기와 재생이며 실차 검증 아님.

| 파일 | 역할 |
|---|---|
| `track_dump.py <schema_dir> <segs_dir> <t_from> <t_to> [max_d]` | route 초(첫 carState 기준 mono 초) 구간에서 `liveTracks` 프레임마다 한 블록: 자차 vEgo, 비전 후보(`modelV2.leadsV3[0]`)의 d(= x[0] - 1.52)/y_rel/v/prob, 이어서 점(dRel < max_d, 기본 40 m, dRel 순)의 id, d, y, vRel, measured, source. 점 필드는 스키마에 없으면 `-`. `radarSource` 필드를 읽는다(`source`가 아니다). 재생 없이 로그만 읽으므로 `repo_dir` 불필요, `python3 -I`로 실행 |
| `geom_dump.py <schema_dir> <repo_dir> <segs_dir>` | `full_replay2.py`와 같은 재생에 `VisionRadarMatcher`의 `_match_*` 메서드를 감싸, `WRAP=a:b`(route 초 구간, 필수) 안의 매 modelV2 프레임에 비전 d/y_rel, 레이더 점 목록, 비전 후보의 d/prob/dPath(`visdPath` 줄), 각 `_match_*`가 돌려준 점(또는 None), 최종 leadOne (status, radar, dRel)을 출력한다. `full_replay2.py`의 CMPFROM/QUIET/PROBFIX/FREEZE/YSHIFT도 그대로 쓴다(QUIET=1 권장). `repo_dir`의 `primary.py`를 고친 사본을 넘기면 그 코드로 재생한다 |

사용 예(000004a0, 288cha): `python3 -I track_dump.py <schema> <segs> 148.7 149.45 40`, `WRAP=148.95:149.30 QUIET=1 python3 -I geom_dump.py <schema> <repo_dir> <segs>`. `<repo_dir>`와 스키마 모으는 법은 287차 추가(`full_replay2.py`)와 같다.

검증(288cha, route 000004a0, e1fa15a, 세그먼트 3개): 두 파일 모두 `py_compile` 통과. `track_dump.py 149.05 149.25 40`은 149.11초에 id 0 d 5.1 y -0.60 vRel -0.60 meas True src scc 블록을 낸다. `geom_dump.py`(WRAP=149.05:149.2)는 149.13초에 `_match_vision_corroborated_radar` -> `pt d=5.1 y=-0.60 id=0 src=scc`, `visdPath d=12.9 prob=0.99 dPath=+0.72`, leadOne st=True radar=True dRel=5.1을 낸다. 같은 실행에서 재생 3,600프레임, 비교 1,599프레임 (status, radar) 100.00% 일치. 한계: open-loop(자차 거동 미반영). `geom_dump.py`는 `_match_*` 반환만 찍고 각 매처 내부 한도(거리 오차, dPath 차, 속도 차)는 찍지 않는다. `_match_vision_corroborated_radar` 내부 값은 288cha에서 1회용 래퍼로 따로 찍었고 저장하지 않았다.

### 291차 추가 (rlog_summary/: rlog 10세그먼트 요약 분석)
route 단위로 rlog.zst를 읽어 오류, 활성 비율, 속도, 제어 품질, 장치, panda, CAN, GPS, 선행차를 세그먼트별 JSON으로 요약하는 읽기 전용 도구. 291cha(route 000004a6, 기록 커밋 0255dc6)에서 만들었다. 실차 검증 아님(로그 확인).
| `rlog_summary/load.py` | `capnp` 스키마 로더와 `events(path)`. 스키마 폴더는 환경변수 `SCHEMA_DIR`(기본 `./schema`)로 지정하며 **로그를 기록한 커밋**의 `openpilot/cereal/{log,deprecated,custom}.capnp`, `openpilot/cereal/include/c++.capnp`, `opendbc_repo/opendbc/car/car.capnp`를 한 폴더에 모은다(`include/`는 하위 폴더). 인자 없이 `python3 load.py <rlog.zst>`는 이벤트 종류별 개수를 출력 |
| `rlog_summary/summary1.py` | 세그먼트별 carState/selfdriveState/pandaStates/logMessage/deviceState 요약(폴트, 활성 %, 속도, 알림, 가속/브레이크 %, 조향각, panda 폴트, 경고 로그) -> `summary1.json` |
| `rlog_summary/summary2.py` | 제어 품질: `controlsState.curvature - desiredCurvature` RMS/최대, `aEgo - aTarget` RMS, aEgo 미분 저크(노이즈 포함, 참고용), 조향 토크/`steeringPressed`, 상태 전이(disabled/overriding) 시각 -> `summary2.json` |
| `rlog_summary/summary3.py` | 장치 온도/전력/메모리/저장공간, panda 전압/점화, `radarState.leadOne` 감지율과 최근접 dRel, GPS 픽스 수와 위치, bus별 CAN/sendcan 개수 -> `summary3.json` |
환경: `pip install --break-system-packages pycapnp zstandard`. 실행(작업 폴더에서): `SCHEMA_DIR=<schema> SEGS_DIR=<segs> python3 summary1.py`(2, 3도 같음). `SEGS_DIR` 아래 `<route>--<n>/rlog.zst` 구조를 `n` 순서로 읽고, 결과 JSON은 현재 폴더에 쓴다(각 세그먼트 처리 뒤 덮어써 중간저장).
한계: 스키마를 기록 커밋 것으로 받지 않으면 필드가 다르다(upstream은 `leadOne.present`와 `thermalStatus` `ok`, carrot-ryu는 `status`와 `green`; `summary3.py`는 둘 다 처리). `logMonoTime` 범위로 구간 길이를 재면 부팅 이전 이벤트 때문에 틀리므로 쓰지 않았다(carState 건수 / 100 Hz로 판단). logMessage 레벨 키는 `levelnum`. 저크는 aEgo 단순 미분이라 센서 노이즈가 크다. 영상(`qcamera.ts`)은 다루지 않는다.

### 292차 추가 (rlog_summary/: 구간 읽기 3종과 영상 프레임 추출)
291차 요약 도구의 후속으로, 한 rlog.zst의 시간 구간만 읽는 읽기 전용 도구 3개다. 292cha(route 000004a6, 기록 커밋 0255dc6)에서 만들었고, 앞 대화의 원본이 샌드박스 초기화로 사라져 이 사양대로 다시 썼다(실제 로그로 재실행해 수치 확인). 실차 검증 아님(로그 확인). 시각은 모두 그 rlog의 첫 carState를 0으로 한 초(세그먼트 안 시각)다. `load.py`와 같은 폴더에 두고 `SCHEMA_DIR`(기록 커밋의 스키마 폴더)을 지정한다.
| `rlog_summary/lead_win.py` | `<rlog.zst> <t_from> <t_to> [step_s]`: `radarState.leadOne`의 최소 dRel 한 줄(status True 기준, 시각/vEgo/yRel/vRel/radar)과 구간 안 step 간격 행(status, dRel, yRel, vRel, radar). `radar`는 carrot-ryu 스키마의 레이더/비전 구분(False면 비전 단독) |
| `rlog_summary/steer_win.py` | `<rlog.zst> <t_from> <t_to> [step_s]`: vEgo, 조향각, 조향 토크, `steeringPressed`, 좌우 깜빡이, 가속/브레이크 페달, `selfdriveState.state`, `carControl.latActive`, `actuators.accel`을 구간 안 step 간격으로 출력(state, latActive, accel은 직전 메시지 값). 개입 전이를 보려면 step 0.01~0.05로 돌려야 한다(0.25~0.5초 표본은 `steeringPressed`가 짧게 번갈아 바뀌는 것을 놓쳐 연속 구간으로 보인다) |
| `rlog_summary/gps_gap.py` | `<rlog.zst> [...]`: `gpsLocation` 개수와 1.5초 넘는 공백 구간. 000004a6 로그에는 `gpsLocationExternal` 데이터가 없고 `gpsLocation`만 1 Hz로 있었다. 공백 원인(터널 등 환경인지 장치인지)은 이 도구가 가르지 못한다 |
영상 프레임 컨택트시트(ffmpeg, 눈으로 대조용): `ffmpeg -v error -y -ss <시작초> -t <길이초> -i qcamera.ts -map 0:v:0 -vf "fps=2,drawtext=text='%{pts\:hms}':x=4:y=4:fontcolor=yellow:fontsize=18:box=1:boxcolor=black@0.5,scale=263:-1,tile=3x3" -frames:v 1 out.png`. qcamera.ts는 526x330, 20 fps이고 비디오 스트림이 2개라 `-map 0:v:0`이 필요하다. `-ss`를 `-i` 앞에 두면 화면의 시각 표기는 시작초 기준 0부터 다시 센다. 영상과 로그의 시각 정렬 오차는 확인하지 않았고 화면 속 거리는 눈대중이다. 이 명령은 앞 대화에서 쓴 것이며 다시 쓴 세 도구와 달리 이 대화에서 재실행하지 않았다.
한계: 앞차 표시값은 `leadOne` 한 개만 본다(leadTwo, 비전 후보 목록, liveTracks는 안 읽는다). 후보 선택 과정은 `lead_dropout/` 재생 도구로 따로 본다.

### 293차 추가 (rlog_summary/lane_win.py: 모델 차선 상태 구간 읽기)
292차 `steer_win.py`의 짝으로, 조향 토크 구간이 차선 변경이나 차선 중앙 이동과 겹치는지 보는 읽기 전용 도구다. 293cha(route 000004a6, 기록 커밋 0255dc6)에서 만들었고 앞 대화 원본이 사라져 이 사양대로 다시 썼다(실제 로그로 재실행). 실차 검증 아님(로그 확인). `load.py`와 같은 폴더에 두고 `SCHEMA_DIR`을 지정한다(0255dc6 기준 스키마는 `openpilot/cereal/{log,deprecated,custom}.capnp`, `include/c++.capnp`, `opendbc_repo/opendbc/car/car.capnp`를 한 폴더에 모으고 `include/c++.capnp`는 그 폴더 아래 `include/`에 둔다).
| `rlog_summary/lane_win.py` | `<rlog.zst> <t_from> <t_to> [step_s]`: `modelV2`의 `laneChangeState`/`Direction`, `laneWidthLeft/Right`(wL/wR), `laneChangeAvailableLeft/Right`(AL/AR), `laneLines` 안쪽 두 줄(index 1, 2)의 첫 점 y(yL/yR)와 `laneLineProbs`(pL/pR), 중간값 mid=(yL+yR)/2를 step 간격(기본 0.5초)으로 출력. 시각은 그 rlog의 첫 carState 기준 초 |
한계: 그 시각 이후 가장 가까운 `modelV2` 표본만 찍는다(step이 크면 `laneChangeState` 전이 시각을 놓친다, 전이는 step 0.01~0.05로 돌린다). `laneChangeState`는 세그먼트 경계를 넘어 이어질 수 있어 앞뒤 세그먼트를 같이 본다. y 부호(왼쪽 선 음수로 읽힘)와 mid 양수의 의미는 이 로그에서 읽은 것이고 좌표계 정의를 확인하지 않았다. 차선 변경 시작이 운전자인지 시스템인지는 이 도구가 가르지 못한다(`carrotMan` 필드 안 읽음).

### 311차 추가 (lead_replay/scene76_plan.py, extract_plan_ext.py: 실제 플래너 호출부를 따르는 재생)

311cha(WIP.md 311cha)에서 route 000004bf 세그먼트 76의 신호정지 2.7 m 장면을 재생하려고 만든 도구다. `cl_replay.py`/`ol_replay.py`는 MPC에 측정 자차 상태를 넣고 `a_solution[0.05초]`를 명령으로 읽는데, 실제 `longitudinal_planner.py`(5339d98)는 그렇지 않아서 노출 뒤 반응이 로그보다 약 0.5초 늦게 재생됐다. 이 도구는 플래너의 MPC 호출부를 따른다. 실차 검증 아님.

| 파일 | 역할 |
|---|---|
| `extract_plan_ext.py <schema> <segs> <out.pkl> [t_from t_to]` | `longitudinalPlan`의 `aTarget`, `aTargetBase`, `longitudinalPlanSource`, `leadPreviewAccel`, `aChangeCost`, `vTargetNow`, `jTargetNow`, `hasLead`, `shouldStop`을 첫 carState 기준 초로 뽑는다(기본 150~215초). `python3 -I`로 실행, initData는 읽지 않는다 |
| `scene76_plan.py ol` | 열린 루프: 로그 vEgo/aEgo/앞차 입력으로 플래너 MPC를 돌려 `a_target_base`를 로그 `aTargetBase`와 비교(183.3~190초 RMSE 0.006, 최대 0.015) |
| `scene76_plan.py cl [런 이름...]` | 폐루프 8런(로그 입력, 이상적 정지 차량, 게이트 끔, `StopDistanceCarrot` 6/8 m, 노출 0.5/1.0/2.0초 일찍): 노출 전 자차는 로그 상태, 노출부터 cmd = `a_target_base`를 1차 플랜트로 따른다. 약 1.5분이라 `setsid nohup ... < /dev/null &` |

플래너 호출부를 따른 점: MPC 시작 상태 `(v_desired_filter.x, a_desired)`(`FirstOrderFilter` rc 2.0이 vEgo로 당기고 계획 가속도를 적분), 명령 `get_accel_from_plan(v_traj, a_traj, CONTROL_N_T_IDX, action_t = LongActuatorDelay x 0.01 + 0.05, vEgoStopping)`, `a_change_cost_starting` = 로그 `AChangeCostStarting`(150), 가속 하한 `min(A_CRUISE_MIN -2.0, a_desired + 0.05)`.

사전 준비: `pytest_ci_setup.sh` -> `cl_sim/prep_base.sh HEAD`(`cl_sim.py`가 기준선 모듈을 임포트한다, 쓴 뒤 `long_mpc_base110.py` 삭제) -> 스키마를 로그 기록 커밋 기준으로 모으고(sh가 아니라 bash로 복사) `extract_log.py`(log_lead.pkl)와 `extract_plan_ext.py`(lp_ext.pkl) -> `export PYTHONPATH=/home/claude/repo:/home/claude/repo/opendbc_repo LR_PKL=<log_lead.pkl> LP_PKL=<lp_ext.pkl>`. `cl_sim` 폴더는 `../cl_sim`이 기본이고 `CL_SIM_DIR`로 바꾼다.

주의: `scene76_plan.py`의 값 중 route 000004bf 세그먼트 76 전용이 있다(`T_SW` 183.355954초 = 레이더가 정지 차량을 처음 잡은 프레임, `A_CHANGE_COST_STARTING` 150, `LongActuatorDelay` 20, `VEgoStopping` 5, 정지 거리 7.0, 플랜트 tau 0.35, 설정속도 15 m/s 가정). 다른 로그에는 이 값(initData 키는 `AChangeCostStarting`, `LongActuatorDelay`, `VEgoStopping`, `StopDistanceCarrot`만 골라 읽는다)부터 바꾼다. 한계: 앞차 위치는 `xego_log + dRel`에서 만든 추정이고 레이더 `dRel` 오프셋을 모른다(이 로그에서 속도 적분 이동거리와 레이더 거리 감소가 2.2 m 달랐다), 모델 궤적(x, v, a, j)은 0, lead preview와 controlsd 한계는 없다, 센서 지연과 노이즈 없음. 저장판은 열린 루프만 폴더를 옮긴 사본에서 다시 돌려 RMSE 0.006을 확인했고 폐루프 8런은 경로 하드코딩판으로 돌렸다. 처음 두 판(`scene76_replay.py`, 측정 자차 상태와 `a_solution[0.05초]` 사용)은 틀려서 저장하지 않았다. 이 파일들은 Windows PowerShell 5.1에서 실행하는 도구가 아니다(샌드박스 전용).

### 311차 후속 추가 (lead_replay/start_replay.py: 앞차 따라 출발 재생)

311cha 후속에서 route 000004bf 세그먼트 77의 정지 후 출발(238초)을 재생하려고 만든 도구다. `scene76_plan.py`(같은 폴더)의 `Plan`(플래너 MPC 호출부 사본)을 그대로 쓰고 앞차는 로그 `leadOne`(vLead/aLeadK, 위치 = `xego_log + dRel`)이다. 실차 검증 아님.

| 모드(`python3 start_replay.py <모드>`) | 내용 |
|---|---|
| `ol` | 열린 루프(233~241초): 로그 자차 상태로 플래너 MPC를 돌려 로그 `aTargetBase`와 RMSE(0.009)를 보고, 설정 변형(JerkCostEgo, `a_change_cost_starting`, tFollow, 정지 거리, `LeadAccelResponse` 5)별 `shouldStop` 해제 시각과 0.2/0.4/0.6 m/s² 도달 시각을 비교 |
| `cl` | 폐루프(235~262초, 자차 1차 플랜트 tau 0.35, 지연 0.15): 변형 런별 속도(240/243/246/250초), 평균 가속, 간격 |
| `lar` | 폐루프, `LeadAccelResponse` 레벨 0/1/2/3/5 |
| `gap` | 폐루프, 정차 간격 가정(자차를 로그 위치에서 `off`만큼 뒤에 세움) 2.7/5/7 m |
| `combo` | 폐루프, `LeadAccelResponse` 4/5와 tFollow 1.4/1.2 조합 |

사전 준비와 환경변수는 `scene76_plan.py`와 같다. 단 `LP_PKL`은 `extract_plan_ext.py <schema> <segs> <out.pkl> 150 300`으로 뽑는다(기본 구간 150~215초는 출발 구간을 포함하지 않아 `IndexError`가 난다). `scene76_plan.py`에 `Plan.lar`(LeadAccelResponse 레벨, 기본 0)와 `Plan.ss`(`get_accel_from_plan`의 should_stop)를 추가했다. 기본값은 311차 판과 같아 `scene76_plan.py ol/cl` 결과는 달라지지 않는다. `cl_sim`의 `mk_carrot` 객체에 `jerkCostEgo`, `jerk_factor`, `leadAccelResponse`를 덧씌우고 끝나면 되돌린다.

한계: 로그의 출발 한 건이다. 플랜트는 1차 지연이라 차가 움직이기 시작하는 문턱(명령 약 0.4 m/s²)을 재현하지 못한다(재생 v240 0.87 대 로그 1.44 m/s, v250 7.25 대 6.98). 설정속도는 15 m/s 가정, 모델 궤적(x, v, a, j)은 0, lead preview와 controlsd 한계는 없다. 앞차 위치는 로그 거리에서 만든 추정이고 레이더 `dRel` 오프셋을 모른다. 변형 런은 한 번씩이다. 저장판은 `ol`, `gap`, `combo`, `lar`를 저장 레이아웃 사본에서 다시 돌려 확인했고 `cl`은 저장판으로 다시 돌리지 않았다. 이 파일들은 Windows PowerShell 5.1에서 실행하는 도구가 아니다(샌드박스 전용).
