#!/usr/bin/env python3
"""frame.py <t0> <t1> [step=0.1]  (286cha, 로그 000004a0 분석 스크립트를 앞 구간 기록에서 복원)
extract_log.py pkl의 시각 구간을 step 간격 한 줄씩 출력한다: vEgo aEgo, accel 명령, aTarget, desiredDistance, tFollow, leadOne(status radar dRel vLead aLeadK prob),
leadTwo(status dRel vLead), swaglog lead_gate g(idx)(직전 0.5 s 이내 값). t는 pkl 기준(첫 carState = 0, 세그먼트를 이어 붙인 route 시각).
pkl 경로는 환경변수 LR_PKL(기본 ./log_lead.pkl). 의존: numpy pandas. 실차 검증 아님."""
import pickle, os, sys, numpy as np, pandas as pd

d = pickle.load(open(os.environ.get('LR_PKL', 'log_lead.pkl'), 'rb'))
rs, cs, cc, lp, gt = d['rs'], d['cs'], d['cc'], d['lp'], d['gt']
t0, t1 = float(sys.argv[1]), float(sys.argv[2]); step = float(sys.argv[3]) if len(sys.argv) > 3 else 0.1

def at(df, col, tt):
    k = np.searchsorted(df['t'].values, tt, side='right') - 1; return df[col].values[max(k, 0)]
print('   t     vEgo  aEgo | cmd   aTarget desDist tF | L1 st rad dRel  vLead aLeadK prob | L2 st dRel vLead | gate g(idx)')
tt = t0
while tt <= t1 + 1e-9:
    k = np.searchsorted(rs.t.values, tt, side='right') - 1; r = rs.iloc[k]
    g = gt[(gt.t <= tt) & (gt.t > tt - 0.5)]
    gs = f"{g.iloc[-1].g:.2f}({int(g.iloc[-1].idx)})" if len(g) else '-'
    print(f"{tt:7.2f} {at(cs,'vEgo',tt):5.2f} {at(cs,'aEgo',tt):+5.2f} | {at(cc,'accel',tt):+5.2f} {at(lp,'aTarget',tt):+6.2f} {at(lp,'desired',tt):6.1f} {at(lp,'tFollow',tt):4.2f} | "
          f"{int(r.l1_status)}  {int(r.l1_radar)} {r.l1_dRel:5.1f} {r.l1_vLead:5.2f} {r.l1_aLeadK:+5.2f} {r.l1_prob:4.2f} | {int(r.l2_status)} {r.l2_dRel:5.1f} {r.l2_vLead:5.2f} | {gs}")
    tt += step
