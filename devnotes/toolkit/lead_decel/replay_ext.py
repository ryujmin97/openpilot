#!/usr/bin/env python3
"""이벤트 1개를 게이트 후보별로 폐루프 재생 (107차). gating_eval_105.py 확장: 후보 M0.8/1.0, M0.9/1.1을 CANDS에 주입. 실차 검증 아님, acados 실물 아님.
사용: `python3 replay_ext.py <event_idx> <variants,...>`  예: `python3 replay_ext.py 8 M105,base,B,M0.8/1.0`
  변형: base, B, M105(현행 M 1.0/1.2), M0.8/1.0, M0.9/1.1 (gating_eval_105.CANDS 그대로 + 두 후보). gap 오프셋은 0 고정.
필요: 같은 폴더의 gating_eval_105.py/gating_eval.py/mpc_replica.py, out/merged.pkl, out/events.pkl. 결과 out/ext_<idx>.pkl = {(idx,0.0,variant): (DataFrame, summary)}.
한 폴더에서 CPU 1코어면 이벤트당 약 10 s x 변형 수(여러 개를 동시에 돌리면 그만큼 느려진다). 백그라운드는 setsid nohup.
"""
import sys, os, time, pandas as pd
sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))
import gating_eval_105 as X, gating_eval as G
X.CANDS['M0.8/1.0']=dict(m_lo=0.8,m_hi=1.0,t_lo=6.0,t_hi=12.0,mode='tau',kind='margin')
X.CANDS['M0.9/1.1']=dict(m_lo=0.9,m_hi=1.1,t_lo=6.0,t_hi=12.0,mode='tau',kind='margin')
idx=int(sys.argv[1]); variants=sys.argv[2].split(','); res={}
for v in variants:
    t0=time.time(); d=X.simulate(G.E.loc[idx], v, 0.0); s=G.summary(d); res[(idx,0.0,v)]=(d,s)
    print(f"#{idx} {v:9s} aEmin={s['aEmin']:6.2f} minGap={s['minGap']:5.1f} minHw={s['minHw']:4.2f} minTTC={s['minTTC']:6.1f} gMax={s['gMax']:.2f} gMean={s['gMean']:.2f} ({time.time()-t0:.0f}s)",flush=True)
pd.to_pickle(res,f'out/ext_{idx}.pkl')
