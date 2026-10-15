import os, json, glob, collections
from load import *
segs = sorted(glob.glob(os.path.join(os.environ.get('SEGS_DIR','.'),'*--*','rlog.zst')), key=lambda p:int(p.split('--')[-1].split('/')[0]))
def g(o,k,d=None):
    try: return getattr(o,k)
    except Exception: return d
out={}; allev=collections.Counter()
for p in segs:
    n=p.split('--')[-1].split('/')[0]
    cpu=[];pw=[];mem=[];thr=collections.Counter();free=None;pv=[];ign=0;pn=0
    lead=0;rs=0;dmin=999;gps=[];busc=collections.Counter();sendc=collections.Counter();dm=collections.Counter();gn=0
    for e in events(p):
        w=e.which(); allev[w]+=1
        if w=='deviceState':
            d=e.deviceState; cpu.append(max(list(d.cpuTempC) or [0])); pw.append(g(d,'powerDrawW',0)); mem.append(d.memoryUsagePercent)
            thr[str(d.thermalStatus)]+=1; free=d.freeSpacePercent
        elif w=='pandaStates':
            for ps in e.pandaStates: pv.append(ps.voltage); pn+=1; ign+=bool(ps.ignitionLine or ps.ignitionCan)
        elif w=='radarState':
            r=e.radarState; rs+=1; l=r.leadOne
            if g(l,'status',g(l,'present',False)): lead+=1; dmin=min(dmin,l.dRel)  # carrot-ryu는 status, upstream은 present
        elif w in('gpsLocationExternal','gpsLocation'):
            x=getattr(e,w); gps.append((x.latitude,x.longitude,x.speed,g(x,'horizontalAccuracy',0)))
        elif w=='qcomGnss': gn+=1
        elif w=='can':
            for m in e.can: busc[m.src]+=1
        elif w=='sendcan':
            for m in e.sendcan: sendc[m.src]+=1
        elif w=='driverMonitoringState':
            dm['awareMin']=min(dm.get('awareMin',9),e.driverMonitoringState.awarenessStatus)
    r=lambda x:round(x,1)
    out[n]=dict(cpu_max=r(max(cpu or [0])),cpu_avg=r(sum(cpu)/max(len(cpu),1)),pw_avg=r(sum(pw)/max(len(pw),1)),mem_max=max(mem or [0]),
      thermal=dict(thr),free_pct=free,panda_v=[r(min(pv or [0])),r(max(pv or [0]))],ign_pct=r(100*ign/max(pn,1)),
      lead_pct=r(100*lead/max(rs,1)),lead_dmin=r(dmin) if dmin<999 else None,
      gps_n=len(gps),gps_first=gps[0][:2] if gps else None,gps_last=gps[-1][:2] if gps else None,gps_acc=gps[0][3] if gps else None,
      gnss_msgs=gn,can_bus=dict(busc),sendcan_bus=dict(sendc),dm=dict(dm))
    json.dump(out,open('summary3.json','w'),ensure_ascii=False); print(n,'saved',flush=True)
print([k for k in allev if k not in('accelerometer','gyroscope')][:80])
