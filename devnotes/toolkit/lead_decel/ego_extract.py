#!/usr/bin/env python3
"""rlog.zst -> 자차 실제 주행 시계열 pickle (107차). 실차 로그 분석용. 실차 검증 아님(로그 확인 도구).
사용: 작업 폴더(out/ 가 있는 곳)에서 `python3 ego_extract.py`  (인자 없음)
가정하는 폴더 배치(작업 폴더 기준 상대경로 고정):
  ../schema/            log.capnp/custom.capnp/deprecated.capnp/include/ + car.capnp (로그를 기록한 커밋 기준, parse_lead_log.py와 동일 구성)
  ../segs/<route>--<n>/rlog.zst   세그먼트 폴더(심볼릭 링크 가능)
출력 out/ego.pkl = {cs, cc, lp, rs, sw, ss} DataFrame, 각각 t_abs와 t(첫 carState 기준 초).
  cs: carState(vEgo, aEgo, brakePressed, gasPressed, vCruise, cruiseState.enabled) 100Hz
  cc: carControl(actuators.accel=accelCmd, longActive, enabled) 100Hz
  lp: longitudinalPlan(aTarget, aTargetBase, hasLead, desiredDistance, tFollow, vTargetNow, trafficState) 20Hz
  rs: radarState.leadOne(status, dRel, vRel, vLead, aLeadK, vLeadK) 20Hz
  sw: swaglog 'lead_gate idx=.. g=.. m=.. h=.. dRel=.. vEgo=.. vLead=..' 파싱(105차 게이트 로그)
  ss: selfdriveState(state, enabled, active)
의존: pycapnp, zstandard, pandas
"""
import os, glob, re, json, capnp, zstandard, pandas as pd
capnp.remove_import_hook()
log = capnp.load('../schema/log.capnp', imports=['../schema'])
def segno(p): return int(re.search(r'--(\d+)$', os.path.dirname(p)).group(1))
files = sorted(glob.glob('../segs/*/rlog.zst'), key=segno)
cs, cc, lp, rs, sw, ss = [], [], [], [], [], []
for f in files:
    raw = zstandard.ZstdDecompressor().stream_reader(open(f,'rb')).read()
    for ev in log.Event.read_multiple_bytes(raw):
        w = ev.which(); t = ev.logMonoTime*1e-9
        if w=='carState':
            c=ev.carState
            cs.append(dict(t_abs=t,vEgo=c.vEgo,aEgo=c.aEgo,brake=c.brakePressed,gas=c.gasPressed,vCruise=c.vCruise,cruiseEn=c.cruiseState.enabled))
        elif w=='carControl':
            a=ev.carControl.actuators
            cc.append(dict(t_abs=t,accelCmd=a.accel,longActive=ev.carControl.longActive,enabled=ev.carControl.enabled))
        elif w=='longitudinalPlan':
            p=ev.longitudinalPlan
            lp.append(dict(t_abs=t,aTarget=p.aTarget,aTargetBase=p.aTargetBase,hasLead=p.hasLead,desiredDist=p.desiredDistance,tFollow=p.tFollow,vTargetNow=p.vTargetNow,trafficState=p.trafficState))
        elif w=='radarState':
            l=ev.radarState.leadOne
            rs.append(dict(t_abs=t,status=l.status,dRel=l.dRel,vRel=l.vRel,vLead=l.vLead,aLeadK=l.aLeadK,vLeadK=l.vLeadK))
        elif w=='logMessage':
            m=ev.logMessage
            if 'lead_gate' in m:
                d=json.loads(m); mm=re.search(r'idx=(\d+) g=([\d.]+) m=([\d.]+) h=([\d.]+) dRel=([\d.]+) vEgo=([\d.]+) vLead=([\d.]+)',d['msg'])
                if mm: sw.append(dict(t_abs=t,idx=int(mm[1]),g=float(mm[2]),m=float(mm[3]),h=float(mm[4]),dRel=float(mm[5]),vEgo=float(mm[6]),vLead=float(mm[7])))
        elif w=='selfdriveState':
            s=ev.selfdriveState
            ss.append(dict(t_abs=t,state=str(s.state),enabled=s.enabled,active=s.active))
D={k:pd.DataFrame(v) for k,v in dict(cs=cs,cc=cc,lp=lp,rs=rs,sw=sw,ss=ss).items()}
t0=D['cs'].t_abs.iloc[0]
for k,v in D.items(): v['t']=v.t_abs-t0
pd.to_pickle(D,'out/ego.pkl')
print({k:len(v) for k,v in D.items()}, 't0',t0)
