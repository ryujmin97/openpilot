import os, json, glob, collections, os, re
from load import *
segs = sorted(glob.glob(os.path.join(os.environ.get('SEGS_DIR','.'),'*--*','rlog.zst')), key=lambda p:int(p.split('--')[-1].split('/')[0]))
out = {}
def g(o,k,d=None):
    try: return getattr(o,k)
    except Exception: return d
for p in segs:
    n = p.split('--')[-1].split('/')[0]
    t0=t1=None; v=[]; en=0; tot=0; states=collections.Counter(); alerts=collections.Counter()
    sf=collections.Counter(); gas=brk=0; cs_n=0; pan=collections.Counter(); logs=collections.Counter()
    cpu=0; therm=0; lat_err=[]; steer=[]; sdt=0
    for e in events(p):
        w=e.which(); t=e.logMonoTime
        t0 = t if t0 is None else t0; t1=t
        if w=='carState':
            c=e.carState; cs_n+=1
            v.append(g(c,'vEgo',0)*3.6)
            gas+=bool(g(c,'gasPressed',0)); brk+=bool(g(c,'brakePressed',0))
            for k in ('steerFaultTemporary','steerFaultPermanent','accFaulted','canValid','canTimeout'):
                x=g(c,k)
                if (k=='canValid' and x is False) or (k!='canValid' and x): sf[k]+=1
            steer.append(abs(g(c,'steeringAngleDeg',0)))
        elif w=='selfdriveState':
            s=e.selfdriveState; tot+=1; en+=bool(s.enabled); states[str(s.state)]+=1
            if s.alertType: alerts[s.alertType]+=1
        elif w=='pandaStates':
            for ps in e.pandaStates:
                if ps.faults: pan['faults:'+','.join(map(str,ps.faults))]+=1
                for k in ('heartbeatLost','safetyRxInvalid','safetyTxBlocked','rxBufferOverflow','txBufferOverflow','safetyRxChecksInvalid'):
                    if g(ps,k): pan[k]+=int(g(ps,k)) if not isinstance(g(ps,k),bool) else 1
        elif w=='logMessage':
            try:
                d=json.loads(e.logMessage); lv=str(d.get('level','?')); 
                if lv in('ERROR','WARNING','CRITICAL'):
                    m=re.sub(r'\d+','#',str(d.get('msg',''))[:110]); logs[lv+'|'+d.get('ctx',{}).get('daemon','')+'|'+m]+=1
            except Exception: pass
        elif w=='deviceState':
            d=e.deviceState; cpu=max(cpu,max(list(d.cpuTempC) or [0])); therm=max(therm,int(d.thermalStatus.raw) if hasattr(d.thermalStatus,'raw') else 0)
    dur=(t1-t0)/1e9 if t0 else 0
    out[n]=dict(dur_s=round(dur,1), v_mean=round(sum(v)/max(len(v),1),1), v_max=round(max(v or [0]),1),
      engaged_pct=round(100*en/max(tot,1),1), states=dict(states), alerts=dict(alerts.most_common(8)),
      carfault=dict(sf), gas_pct=round(100*gas/max(cs_n,1),1), brk_pct=round(100*brk/max(cs_n,1),1),
      steer_max=round(max(steer or [0]),1), panda=dict(pan), cpu_max=cpu, log=dict(logs.most_common(6)))
    json.dump(out, open('summary1.json','w'), ensure_ascii=False)
    print(n, 'saved', flush=True)
