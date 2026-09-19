"""반사실 시뮬레이션: 리드 궤적(로그의 vLead)을 고정하고 자차가 t_on 이후 상수 감속 a_c(지연 0.3s)로 리드 속도까지 감속 후 추종한다고 가정.
사용: counterfactual.py <t_on>   # out/merged.pkl 의 '32/33' 구간. 다른 구간은 코드의 M[...] 키 수정.
한계: 사후(hindsight) 정보를 쓰는 이상화 — '필요 최소 감속'의 대략적 크기 파악용이지 제어기 설계값이 아님.
"""
import pandas as pd, numpy as np, sys
M = pd.read_pickle('out/merged.pkl')
def sim(m, t_on, a_c, delay=0.3, t_end=None, dt=0.05):
    """리드 궤적(로그의 vLead)을 외생 입력으로 두고, t_on 이후 자차가 상수 감속 a_c로 vLead에 수렴 후 추종하는 반사실 시뮬레이션."""
    w = m[(m.t>=t_on-0.5)&(m.t<= (t_end or m.t.max()))].reset_index(drop=True)
    tt = w.t.values; vL = w.vLead.values
    i0 = np.argmin(abs(tt-t_on))
    gap = w.dRel.values[i0]; vE = w.vEgo.values[i0]
    gaps=[gap]; vEs=[vE]; caught=False
    for i in range(i0+1, len(tt)):
        d = tt[i]-tt[i-1]
        a = a_c if (tt[i]-t_on) >= delay else 0.0
        vE_new = vE + a*d
        if caught or vE_new <= vL[i]:
            vE_new = vL[i]; caught = True   # 리드 속도에 도달하면 이후 그 속도로 추종(이상화)
        gap += (vL[i]-vE)*d
        vE = vE_new
        gaps.append(gap); vEs.append(vE)
    g = np.array(gaps); v = np.array(vEs)
    return g, v, tt[i0:]
if __name__ == '__main__':
    m = M['32/33']; t_on = float(sys.argv[1]) if len(sys.argv)>1 else 85.5
    w = m[(m.t>=t_on)&(m.t<=t_on+12)]
    print(f'실제 로그: 최소 dRel={w.dRel.min():.1f}m, 최소 dRel/vEgo={ (w.dRel/w.vEgo).min():.2f}s, 최대 감속 aEgo={w.aEgo.min():.2f}, 최소 aTarget={w.aTarget.min():.2f}, vEgo {w.vE_kph.iloc[0]:.0f}->{w.vE_kph.iloc[-1]:.0f}km/h')
    print('반사실(상수 감속, 지연 0.3s) — 최소 gap / 최소 시간차(gap/vE) / 최종 gap:')
    for a in [-0.5,-0.8,-1.0,-1.2,-1.5,-2.0,-2.5]:
        g,v,tt = sim(m, t_on, a, t_end=t_on+12)
        # 시간차는 시뮬 vE 기준
        hw = g/np.maximum(v,1.0)
        print(f'  a={a:5.1f}: min gap={g.min():5.1f}m  min headway={hw.min():.2f}s  final gap={g[-1]:5.1f}m  final vE={v[-1]*3.6:.0f}km/h')
