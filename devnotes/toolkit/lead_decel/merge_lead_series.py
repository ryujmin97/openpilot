"""parse_lead_log.py 출력(out/all.pkl)을 20Hz 시계열로 병합해 out/merged.pkl 저장.
사용: (작업 폴더에서) merge_lead_series.py   # out/all.pkl 필요. pairs는 연속 세그먼트 묶음 — 실제 로그에 맞게 수정할 것.
열: t(구간 시작 기준 초), vE_kph, vL_kph, dRel, desiredDistance, margin=dRel-desiredDistance, aLeadK, aTarget, aTargetBase, accels 등.
"""
import pandas as pd, numpy as np
d = pd.read_pickle('out/all.pkl')
cs, rs, lp = d['cs'], d['rs'], d['lp']
pairs = {'32/33':(32,33), '37/38':(37,38), '39/40':(39,40), '123/124':(123,124), '34':(34,34)}
out = {}
for name,(a,b) in pairs.items():
    l = lp[lp.seg.between(a,b)].sort_values('t_abs').reset_index(drop=True)
    r = rs[rs.seg.between(a,b)].sort_values('t_abs')
    c = cs[cs.seg.between(a,b)].sort_values('t_abs')
    t0 = l.t_abs.iloc[0]
    m = pd.merge_asof(l, r.drop(columns='seg'), on='t_abs', direction='nearest', tolerance=0.06)
    m = pd.merge_asof(m, c.drop(columns='seg'), on='t_abs', direction='nearest', tolerance=0.06)
    m['t'] = m.t_abs - t0
    m['margin'] = m.dRel - m.desiredDistance
    m['vE_kph'] = m.vEgo*3.6; m['vL_kph'] = m.vLead*3.6
    out[name] = m
pd.to_pickle(out, 'out/merged.pkl')
for k,v in out.items(): print(k, len(v), round(v.t.max(),1), 's')
