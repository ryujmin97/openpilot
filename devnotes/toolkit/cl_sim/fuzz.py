"""무작위 케이스(기본 120, 인자로 변경, 시드 20261012)를 HEAD/기준선에 돌려 fuzz.json 저장. 160케이스는 약 6~7분이라 setsid nohup으로 분리해 돌린다."""
import os, sys, json
sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))
import cl_sim as C, scen as S
import numpy as np

rng = np.random.default_rng(20261012)
N = int(sys.argv[1]) if len(sys.argv) > 1 else 120
rows = []
for i in range(N):
  tf = float(rng.choice([1.0, 1.2, 1.45, 1.8, 2.0]))
  v0 = float(rng.uniform(8, 32))
  gapm = float(rng.uniform(0.7, 2.0))
  base = 6.0 + v0 * tf
  adec = -float(rng.choice([0.3, 0.5, 0.8, 1.2, 1.8, 2.5, 3.5]))
  vfrac = float(rng.uniform(0.2, 0.9))
  t_on = float(rng.uniform(3, 8))
  vl0 = max(v0 + float(rng.uniform(-2, 1.0)), 5.0)
  vend = max(0.0, vl0 * vfrac)
  rel = bool(rng.random() < 0.5)
  ev = [(t_on, adec, vend)]
  if rel:
    ev.append((t_on + 12.0, 0.9, vl0))
  vset = v0 + float(rng.uniform(0, 6))
  sc = S.mk(vl0, tf, ev)
  sc['v0'] = v0
  sc['gap0'] = max(8.0, base * gapm)
  try:
    mh = C.metrics(C.run(C.head_mod, sc, tf=tf, T=40.0, vset=vset))
    mb = C.metrics(C.run(C.base_mod, sc, tf=tf, T=40.0, vset=vset))
  except Exception as e:
    rows.append(dict(i=i, err=str(e))); continue
  rows.append(dict(i=i, tf=tf, v0=v0, gapm=gapm, adec=adec, vl0=vl0, vend=vend, t_on=t_on, rel=rel, vset=vset, h=mh, b=mb))
json.dump(rows, open('fuzz.json', 'w'), default=float)
print('done', len(rows))
