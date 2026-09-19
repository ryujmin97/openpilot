"""폐루프 what-if: mpc_replica로 리드 궤적 투사 방식을 바꿔가며 자차 감속을 비교. 리드(vLead/aLeadK/aLeadTau)는 로그 그대로 외생 입력, 자차는 1차 지연 액추에이터로 시뮬레이션.
사용: closed_loop.py <pair> <t0> <t1>   예) closed_loop.py 32/33 84 95   (out/merged.pkl 필요, out/ 에 결과 저장)
변형: baseline / lpf1.0,lpf2.0(리드 속도 저역통과 τ초) / tau1.5,tau0.5(aLeadTau 강제) / noproj(가속도 투사 없음)
한계: 복제본은 acados 실물이 아님(mpc_replica.py 설명 참고). 실차 검증 아님.
"""
import sys, os; sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))
import numpy as np, pandas as pd
import mpc_replica as R
M = pd.read_pickle('out/merged.pkl')
def lead_model(kind, tau_log, a_lead, v_lead, gap_margin=None):
    """리드 궤적 투사 변형. 반환: (a_lead_used, tau_used)"""
    if kind=='baseline': return a_lead, tau_log
    if kind=='tau1.5':   return a_lead, 1.5          # 상수가속 가정 해제(스톡 radard의 |a|<0.5 상태와 같은 감쇠)
    if kind=='tau0.5':   return a_lead, 0.5
    if kind=='noproj':   return 0.0, 1.5             # 투사 없음(현재 속도 유지)
    raise ValueError(kind)
def simulate(pair, t0, t1, kind, jf=1.0, lag=0.35, act_t=0.4, cb=2.47, sd=11.6, dt=0.05):
    m = M[pair]; w = m[(m.t>=t0)&(m.t<=t1)].reset_index(drop=True)
    tt = w.t.values
    i0=0
    vE, aE = w.vEgo[i0], w.aEgo[i0]; gap = w.dRel[i0]
    prev_a = np.full(13, w.accels[i0][0]); a_pl = w.accels[i0][0]
    vLf = w.vLead[i0]
    out=[]; warm=None
    for i in range(len(w)):
        r = w.iloc[i]
        # 리드 입력은 로그 그대로(외생). 거리는 시뮬 ego 기준으로 적분
        vL, aL, tau = r.vLead, r.aLeadK, r.aLeadTau
        a_use, tau_use = lead_model(kind if not kind.startswith('lpf') else 'baseline', tau, aL, vL)
        if kind.startswith('lpf'):
            tau_f = float(kind[3:]); vLf += (vL - vLf)*dt/tau_f; v_in = vLf
        else: v_in = vL
        xt,vt = R.process_lead(gap, v_in, a_use, tau_use, vE)
        xo = R.obstacle(xt,vt,cb)
        X,J = R.solve(vE, a_pl, xo, r.tFollow, prev_a, jerk_factor=jf, cb=cb, sd=sd, warm=warm)
        warm=(X,J)
        a_cmd = float(np.interp(act_t, R.T, X[2]))
        a_pl = float(np.interp(dt, R.T, X[2]))
        prev_a = np.interp(R.T+dt, R.T, X[2])
        out.append((tt[i], vE*3.6, vL*3.6, gap, aE, a_cmd, X[2][0]))
        # 액추에이터(1차 지연) + 운동학
        aE += (a_cmd-aE)*dt/lag
        gap += (vL-vE)*dt; vE = max(0.0, vE + aE*dt)
    return pd.DataFrame(out, columns=['t','vE_kph','vL_kph','gap','aE','aCmd','a0'])
if __name__=='__main__':
    pair=sys.argv[1]; t0=float(sys.argv[2]); t1=float(sys.argv[3])
    res={}
    for k in ['baseline','lpf1.0','lpf2.0','tau1.5','noproj']:
        d = simulate(pair,t0,t1,k); res[k]=d
        hw = (d.gap/np.maximum(d.vE_kph/3.6,1)).min()
        print(f'{k:9s}: 최대감속 aE={d.aE.min():6.2f} m/s², 최소 aCmd={d.aCmd.min():6.2f}, 최소 gap={d.gap.min():5.1f} m, 최소 시간차={hw:4.2f}s, 최종 vE={d.vE_kph.iloc[-1]:.0f}km/h')
    m = M[pair]; w = m[(m.t>=t0)&(m.t<=t1)]
    print(f'{"실제로그":9s}: 최대감속 aEgo={w.aEgo.min():6.2f}, 최소 aTargetBase={w.aTargetBase.min():6.2f}, 최소 dRel={w.dRel.min():5.1f} m, 최소 시간차={(w.dRel/w.vEgo).min():4.2f}s, 최종 vE={w.vE_kph.iloc[-1]:.0f}km/h')
    pd.to_pickle(res, f'out/cl_{pair.replace("/","_")}.pkl')
