#!/usr/bin/env python3
"""108차 계속(원인 조사): longitudinalPlanSource/aChangeCost/leadPreview*/leadTwo/cutOut까지 포함한 확장 추출.
폴더 배치는 toolkit ego_extract.py(107차)와 동일: ../schema, ../segs. 실차 검증 아님(로그 확인).
"""
import os, glob, re, json, capnp, zstandard, pandas as pd
capnp.remove_import_hook()
log = capnp.load('../schema/log.capnp', imports=['../schema'])
def segno(p): return int(re.search(r'--(\d+)$', os.path.dirname(p)).group(1))
files = sorted(glob.glob('../segs/*/rlog.zst'), key=segno)
cs, cc, lp, rs, sw, ss = [], [], [], [], [], []
for f in files:
    seg = segno(f)
    raw = zstandard.ZstdDecompressor().stream_reader(open(f,'rb')).read()
    for ev in log.Event.read_multiple_bytes(raw):
        w = ev.which(); t = ev.logMonoTime*1e-9
        if w=='carState':
            c=ev.carState
            cs.append(dict(seg=seg,t_abs=t,vEgo=c.vEgo,aEgo=c.aEgo,brake=c.brakePressed,gas=c.gasPressed,vCruise=c.vCruise,cruiseEn=c.cruiseState.enabled))
        elif w=='carControl':
            a=ev.carControl.actuators
            cc.append(dict(seg=seg,t_abs=t,accelCmd=a.accel,longActive=ev.carControl.longActive,enabled=ev.carControl.enabled))
        elif w=='longitudinalPlan':
            p=ev.longitudinalPlan
            lp.append(dict(seg=seg,t_abs=t,aTarget=p.aTarget,aTargetBase=p.aTargetBase,hasLead=p.hasLead,
                            desiredDist=p.desiredDistance,tFollow=p.tFollow,vTargetNow=p.vTargetNow,
                            trafficState=p.trafficState,
                            source=str(p.longitudinalPlanSource),
                            aChangeCost=p.aChangeCost,
                            leadPreviewSeconds=p.leadPreviewSeconds,
                            leadPreviewActionTime=p.leadPreviewActionTime,
                            leadPreviewAccel=p.leadPreviewAccel,
                            trafficStopModelLeadOffset=p.trafficStopModelLeadOffset,
                            xState=p.xState,
                            shouldStop=p.shouldStop,
                            fastLeadMask=p.fastLeadMask,
                            accels=list(p.accels)))
        elif w=='radarState':
            r=ev.radarState
            l1=r.leadOne; l2=r.leadTwo
            rs.append(dict(seg=seg,t_abs=t,
                            status=l1.status,dRel=l1.dRel,vRel=l1.vRel,vLead=l1.vLead,aLeadK=l1.aLeadK,vLeadK=l1.vLeadK,aLeadTau=l1.aLeadTau,
                            radarTrackId=l1.radarTrackId,cutOutTime=l1.cutOutTime,cutOutConfidence=l1.cutOutConfidence,
                            status2=l2.status,dRel2=l2.dRel,vRel2=l2.vRel,vLead2=l2.vLead,aLeadK2=l2.aLeadK,aLeadTau2=l2.aLeadTau))
        elif w=='logMessage':
            m=ev.logMessage
            if 'lead_gate' in m:
                try:
                    d=json.loads(m); mm=re.search(r'idx=(\d+) g=([\d.]+) m=([\d.]+) h=([\d.]+) dRel=([\d.]+) vEgo=([\d.]+) vLead=([\d.]+)',d['msg'])
                    if mm: sw.append(dict(seg=seg,t_abs=t,idx=int(mm[1]),g=float(mm[2]),m=float(mm[3]),h=float(mm[4]),dRel=float(mm[5]),vEgo=float(mm[6]),vLead=float(mm[7])))
                except Exception:
                    pass
        elif w=='selfdriveState':
            s=ev.selfdriveState
            ss.append(dict(seg=seg,t_abs=t,state=str(s.state),enabled=s.enabled,active=s.active))
D={k:pd.DataFrame(v) for k,v in dict(cs=cs,cc=cc,lp=lp,rs=rs,sw=sw,ss=ss).items()}
t0=D['cs'].t_abs.iloc[0]
for k,v in D.items():
    if len(v): v['t']=v.t_abs-t0
pd.to_pickle(D,'out/ego2.pkl')
print({k:len(v) for k,v in D.items()}, 't0',t0)
print('sources seen:', D['lp']['source'].value_counts().to_dict() if len(D['lp']) else {})
