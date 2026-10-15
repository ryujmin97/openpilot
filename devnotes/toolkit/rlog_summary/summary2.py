import os, json, glob, math
from load import *
segs = sorted(glob.glob(os.path.join(os.environ.get('SEGS_DIR','.'),'*--*','rlog.zst')), key=lambda p:int(p.split('--')[-1].split('/')[0]))
def g(o,k,d=None):
    try: return getattr(o,k)
    except Exception: return d
def rms(x): return round(math.sqrt(sum(a*a for a in x)/len(x)),5) if x else None
out={}
for p in segs:
    n=p.split('--')[-1].split('/')[0]
    t0=None; ce=[]; ae=[]; lat_kind={}; jerk=[]; prev=None; tq=[]; spr=0; cs=0
    la=None; ov=[]; dis=[]; lastst=None
    for e in events(p):
        w=e.which()
        if w=='carState':
            c=e.carState; cs+=1
            if t0 is None: t0=e.logMonoTime
            a=g(c,'aEgo',0); 
            if prev is not None: jerk.append((a-prev)*100)
            prev=a; la=a
            tq.append(abs(g(c,'steeringTorque',0))); spr+=bool(g(c,'steeringPressed',0))
        elif w=='controlsState':
            c=e.controlsState; ce.append(c.curvature-c.desiredCurvature)
            lat_kind[c.lateralControlState.which()]=1
        elif w=='longitudinalPlan':
            l=e.longitudinalPlan
            if la is not None: ae.append(la-g(l,'aTarget',0))
        elif w=='selfdriveState' and t0 is not None:
            s=str(e.selfdriveState.state); t=(e.logMonoTime-t0)/1e9
            if s!=lastst:
                (dis if s=='disabled' else ov).append((round(t,1),s)) if s in('disabled','overriding') else None
                lastst=s
    out[n]=dict(curv_err_rms=rms(ce), curv_err_max=round(max(map(abs,ce)),5) if ce else None,
        a_err_rms=rms(ae), jerk_rms=rms(jerk), jerk_max=round(max(map(abs,jerk)),1) if jerk else None,
        torque_max=round(max(tq),2), torque_pressed_pct=round(100*spr/max(cs,1),1),
        lat=list(lat_kind), trans=(dis+ov)[:6])
    json.dump(out,open('summary2.json','w'),ensure_ascii=False); print(n,'saved',flush=True)
