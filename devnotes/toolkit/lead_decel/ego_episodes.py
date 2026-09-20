#!/usr/bin/env python3
"""자차 실제 급감속 에피소드 추출 (107차). out/ego.pkl 필요(ego_extract.py). 실차 검증 아님(로그 확인 도구).
사용: `python3 ego_episodes.py`
정의: carState.aEgo의 0.5 s 이동평균이 -1.0 m/s² 미만인 구간, 2 s 이내 간격은 병합. 순간 센서 스파이크(수십 ms)는 이동평균으로 걸러진다.
출력: 세션 요약(상태/브레이크/가속 페달 시간/속도 범위/aEgo 분위) + 에피소드별 aEgoMin, accelCmdMin, aTargetMin, 브레이크 유무,
      리드(dRel/vRel/aLeadK), 게이트(gMax, mMin, hMin) 표. 107차 결과는 WIP.md 107차.
"""
import pandas as pd, numpy as np
D=pd.read_pickle('out/ego.pkl'); cs,cc,lp,rs,sw,ss=[D[k] for k in ['cs','cc','lp','rs','sw','ss']]
print('seg 길이 s', cs.t.iloc[-1]); print('상태 분포', ss.state.value_counts().to_dict(), ' longActive 비율', round(cc.longActive.mean(),3))
print('brakePressed 시간(s)', round(cs.brake.mean()*cs.t.iloc[-1],1), ' gasPressed 시간(s)', round(cs.gas.mean()*cs.t.iloc[-1],1))
print('vEgo 범위 km/h', round(cs.vEgo.min()*3.6,1), round(cs.vEgo.max()*3.6,1), ' vCruise 범위', cs.vCruise.min(), cs.vCruise.max())
print('aEgo 분위 min/1%/5%/median', np.round([cs.aEgo.min(), cs.aEgo.quantile(.01), cs.aEgo.quantile(.05), cs.aEgo.median()],2))
print('accelCmd min', round(cc.accelCmd.min(),2), ' aTarget min', round(lp.aTarget.min(),2))
# 0.5초 이동평균 aEgo로 에피소드
a=cs.aEgo.rolling(50,center=True,min_periods=1).mean().values; t=cs.t.values
thr=-1.0; on=a<thr; eps=[]; i=0
while i<len(t):
    if on[i]:
        j=i
        while j<len(t) and on[j]: j+=1
        eps.append((i,j)); i=j
    else: i+=1
# 병합: 2초 이내 간격
merged=[]
for e in eps:
    if merged and t[e[0]]-t[merged[-1][1]-1]<2.0: merged[-1]=(merged[-1][0],e[1])
    else: merged.append(e)
print('\n자차 실제 감속 에피소드(0.5s 평균 aEgo < -1.0):', len(merged))
rows=[]
for (i,j) in merged:
    t0,t1=t[i],t[j-1]; m=(cs.t>=t0-1)&(cs.t<=t1+1)
    seg=cs[m]; k=seg.aEgo.idxmin()
    ccm=cc[(cc.t>=t0-1)&(cc.t<=t1+1)]; lpm=lp[(lp.t>=t0-1)&(lp.t<=t1+1)]; rsm=rs[(rs.t>=t0-1)&(rs.t<=t1+1)]
    swm=sw[(sw.t>=t0-1)&(sw.t<=t1+1)]
    rows.append(dict(t0=round(t0,1),t1=round(t1,1),dur=round(t1-t0,1),aEgoMin=round(seg.aEgo.min(),2),vEgo_kmh=round(seg.vEgo.mean()*3.6,0),
      accelCmdMin=round(ccm.accelCmd.min(),2),aTargetMin=round(lpm.aTarget.min(),2),brake=bool(seg.brake.any()),
      hasLead=round(lpm.hasLead.mean(),2),dRelMin=round(rsm.dRel.min(),1) if len(rsm) else None,vRelMin=round(rsm.vRel.min(),1) if len(rsm) else None,
      aLeadKmin=round(rsm.aLeadK.min(),2) if len(rsm) else None,gMax=round(swm.g.max(),2) if len(swm) else None,mMin=round(swm.m.min(),2) if len(swm) else None,hMin=round(swm.h.min(),2) if len(swm) else None))
pd.set_option('display.width',250); pd.set_option('display.max_columns',30)
print(pd.DataFrame(rows).to_string())
