#!/usr/bin/env python3
"""extract_log.py <schema_dir> <segs_dir> <out.pkl>  (276cha, 275cha 로그 0000049d 분석의 스크립트를 복원)
<segs_dir>/*--<n>/rlog.zst(세그먼트 번호순)에서 앞차 재생용 프레임을 뽑아 pkl 하나로 저장한다.
  cs: carState (t vEgo aEgo gas brake)   cc: carControl (t accel longActive)
  rs: radarState 프레임별 leadOne(l1_*)/leadTwo(l2_*): status radar tid dRel vRel vLead aLeadK aLeadTau prob yRel
  lp: longitudinalPlan (t aTarget desired tFollow)
  gt: logMessage 안의 'lead_gate idx= g= m= h= dRel= vEgo= vLead=' 줄 (t idx g m h dRel vEgo vLead)
t는 첫 carState 기준 초. initData는 읽지 않는다(Google Drive 토큰 등 시크릿이 들어 있다).
스키마는 로그를 기록한 커밋 기준으로 모은다(README 97차 환경 구성). `python3 -I`로 실행한다(PYTHONPATH 무시).
옛 `lead_decel/parse_lead_log.py`와 목적이 겹치지만 leadTwo, carControl, lead_gate 로그 줄이 더 있어 별도로 둔다.
의존: pycapnp zstandard numpy pandas. 실차 검증 아님."""
import sys, os, glob, pickle, re
import numpy as np, pandas as pd
import capnp, zstandard


def main(schema, segs_dir, out):
    capnp.remove_import_hook()
    log = capnp.load(schema + '/log.capnp', imports=[schema, schema + '/include'])
    segs = sorted(glob.glob(os.path.join(segs_dir, '*', 'rlog.zst')), key=lambda p: int(p.split('/')[-2].split('--')[-1]))
    cs, cc, rs, lp, gt = [], [], [], [], []
    t0 = None

    def L(l):
        return dict(status=bool(l.status), radar=bool(l.radar), tid=int(l.radarTrackId), dRel=float(l.dRel), vRel=float(l.vRel),
                    vLead=float(l.vLead), aLeadK=float(l.aLeadK), aLeadTau=float(l.aLeadTau), prob=float(l.modelProb), yRel=float(l.yRel))
    for sp in segs:
        data = zstandard.ZstdDecompressor().stream_reader(open(sp, 'rb')).read()
        for ev in log.Event.read_multiple_bytes(data):
            w = ev.which()
            if w == 'initData':
                continue
            if t0 is None:
                if w == 'carState':
                    t0 = ev.logMonoTime
                else:
                    continue
            t = (ev.logMonoTime - t0) * 1e-9
            if w == 'carState':
                c = ev.carState
                cs.append((t, float(c.vEgo), float(c.aEgo), bool(c.gasPressed), bool(c.brakePressed)))
            elif w == 'carControl':
                c = ev.carControl
                cc.append((t, float(c.actuators.accel), bool(c.longActive)))
            elif w == 'radarState':
                r = ev.radarState
                d = {'t': t}
                for k, l in (('l1', r.leadOne), ('l2', r.leadTwo)):
                    for kk, vv in L(l).items():
                        d[k + '_' + kk] = vv
                rs.append(d)
            elif w == 'longitudinalPlan':
                p = ev.longitudinalPlan
                lp.append((t, float(p.aTarget), float(p.desiredDistance), float(p.tFollow)))
            elif w == 'logMessage':
                m = ev.logMessage
                if 'lead_gate' in m:
                    mm = re.search(r'lead_gate idx=(\d) g=([\d.]+) m=([-\d.]+) h=([-\d.]+) dRel=([-\d.]+) vEgo=([-\d.]+) vLead=([-\d.]+)', m)
                    if mm:
                        gt.append((t,) + tuple(float(x) for x in mm.groups()))
    D = dict(cs=pd.DataFrame(cs, columns='t vEgo aEgo gas brake'.split()), cc=pd.DataFrame(cc, columns='t accel longActive'.split()),
             rs=pd.DataFrame(rs), lp=pd.DataFrame(lp, columns='t aTarget desired tFollow'.split()),
             gt=pd.DataFrame(gt, columns='t idx g m h dRel vEgo vLead'.split()))
    pickle.dump(D, open(out, 'wb'))
    print({k: len(v) for k, v in D.items()}, 't_end', D['cs'].t.max())


if __name__ == '__main__':
    if len(sys.argv) != 4:
        sys.exit(__doc__)
    main(*sys.argv[1:4])
