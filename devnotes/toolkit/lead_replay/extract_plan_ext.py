#!/usr/bin/env python3
"""extract_plan_ext.py <schema_dir> <segs_dir> <out.pkl> [t_from t_to] (311cha) longitudinalPlan의 aTarget/aTargetBase/longitudinalPlanSource/leadPreviewAccel/aChangeCost/vTargetNow/jTargetNow 등을
첫 carState 기준 초로 뽑아 pkl(DataFrame)로 저장한다(기본 150~215초). scene76_plan.py의 LP_PKL(lp_ext.pkl)이다. `python3 -I`로 실행, initData는 읽지 않는다.
aTarget은 aTargetBase에 lead preview를 더한 값이다(aTarget - aTargetBase = 로그 183.65~184.5초에 -0.08~-0.23). 의존: pycapnp zstandard pandas. 실차 검증 아님."""
import sys, os, glob, pickle
import pandas as pd
import capnp, zstandard


def main(schema, segs_dir, out, lo=150.0, hi=215.0):
    capnp.remove_import_hook()
    log = capnp.load(schema + '/log.capnp', imports=[schema, schema + '/include'])
    segs = sorted(glob.glob(os.path.join(segs_dir, '*', 'rlog.zst')), key=lambda p: int(p.split('/')[-2].split('--')[-1]))
    t0 = None; rows = []
    for sp in segs:
        for ev in log.Event.read_multiple_bytes(zstandard.ZstdDecompressor().stream_reader(open(sp, 'rb')).read()):
            w = ev.which()
            if w == 'initData':
                continue
            if t0 is None:
                if w == 'carState':
                    t0 = ev.logMonoTime
                else:
                    continue
            if w == 'longitudinalPlan':
                p = ev.longitudinalPlan; t = (ev.logMonoTime - t0) * 1e-9
                if lo < t < hi:
                    rows.append((t, p.aTarget, p.aTargetBase, str(p.longitudinalPlanSource), p.leadPreviewAccel, p.aChangeCost, p.vTargetNow, p.jTargetNow, p.hasLead, p.shouldStop))
    df = pd.DataFrame(rows, columns='t aTarget aTargetBase src prevAccel aChg vTargetNow jTargetNow hasLead shouldStop'.split())
    pickle.dump(df, open(out, 'wb')); print(len(df), 'rows')


if __name__ == '__main__':
    if len(sys.argv) not in (4, 6):
        sys.exit(__doc__)
    main(*sys.argv[1:4], *[float(x) for x in sys.argv[4:6]])
