#!/usr/bin/env python3
"""실차 vs 복제본 정합성 + 후보 비교 집계 (107차). 실차 검증 아님(로그 대조).
사용: `python3 real_vs_replay.py`  (필요: out/ext_*.pkl 16개 = replay_ext.py로 idx 0~15 재생, out/ego.pkl, out/merged.pkl, out/events.pkl)
(1) 이벤트별 실차 aEgo(0.5 s 이동중앙값, 스파이크 제거) 최소/accelCmd 최소 vs 복제본 M105 aEmin, 차이와 RMSE.
(2) idx 0,1,3,4,10~15에서 base/B/M105/M0.9-1.1/M0.8-1.0의 aEmin과 base 대비 평균 dAEmin/dMinHw(gap 오프셋 0).
"""
import glob, numpy as np, pandas as pd
import gating_eval as G
res={}
for f in glob.glob('out/ext_*.pkl'): res.update(pd.read_pickle(f))
D=pd.read_pickle('out/ego.pkl'); cs=D['cs']; cc=D['cc']
M=G.M['main']; E=G.E
# (1) 실차 vs 복제본(M105): 실차 aEgo는 0.5s 이동중앙값으로 스파이크 제거, 실차 명령(accelCmd)도 병기
cs['aMed']=cs.aEgo.rolling(50,center=True,min_periods=1).median()
rows=[]
for i in range(16):
    ev=E.loc[i]; d=res[(i,0.0,'M105')][0]
    w=M[(M.t>=ev.t_start-G.SIM_PRE)&(M.t<=ev.t_start+G.SIM_POST)]
    t0,t1=w.t.min(),w.t.max()
    r=cs[(cs.t>=t0)&(cs.t<=t1)]; k=cc[(cc.t>=t0)&(cc.t<=t1)]
    # 20Hz 샘플에 맞춰 보간
    real=np.interp(w.t.values, r.t.values, r.aMed.values); sim=d.aE.values[:len(real)]
    rows.append(dict(idx=i,real_aEmin_smooth=round(real.min(),2),real_accelCmdMin=round(k.accelCmd.min(),2),replay_M105_aEmin=round(sim.min(),2),diff=round(sim.min()-real.min(),2),rmse=round(float(np.sqrt(np.mean((real-sim)**2))),2)))
df=pd.DataFrame(rows); pd.set_option('display.width',200); print(df.to_string(index=False))
print('평균|diff|',round(df['diff'].abs().mean(),3),' 평균rmse',round(df.rmse.mean(),3),' 최대|diff|',df['diff'].abs().max())
# (2) 미재생 이벤트 idx 0,1,3,4,10~15 후보 비교(off 0)
print()
ids=[0,1,3,4,10,11,12,13,14,15]; V=['base','B','M105','M0.9/1.1','M0.8/1.0']; tab=[]
for i in ids:
    row=dict(idx=i)
    for v in V: row[v+'_aE']=round(res[(i,0.0,v)][1]['aEmin'],2)
    row['minHw_base']=round(res[(i,0.0,'base')][1]['minHw'],2); row['minHw_M0.8']=round(res[(i,0.0,'M0.8/1.0')][1]['minHw'],2); row['gMax_M0.8']=round(res[(i,0.0,'M0.8/1.0')][1]['gMax'],2)
    tab.append(row)
t=pd.DataFrame(tab); print(t.to_string(index=False))
for v in V[1:]:
    d=np.mean([res[(i,0.0,v)][1]['aEmin']-res[(i,0.0,'base')][1]['aEmin'] for i in ids]); h=np.mean([res[(i,0.0,v)][1]['minHw']-res[(i,0.0,'base')][1]['minHw'] for i in ids])
    print(f'{v:9s} 평균 dAEmin {d:+.3f}  평균 dMinHw {h:+.3f}')
