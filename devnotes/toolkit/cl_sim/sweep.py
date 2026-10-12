"""고정 시나리오 10개 x TF 3종: HEAD 대 기준선 최소 간격/시간차/TTC/최대 제동/저크 비교. 결과는 sweep.json에도 저장."""
import os, sys, json
sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))
import cl_sim as C, scen as S


def scenarios(tf):
  out = {}
  out['mod_brake_1.2'] = (S.mk(25., tf, [(5., -1.2, 17.), (20., 1.0, 25.)]), 35.)
  out['gentle_0.5'] = (S.mk(25., tf, [(5., -0.5, 20.), (25., 0.8, 25.)]), 40.)
  out['mild_0.8'] = (S.mk(22., tf, [(5., -0.8, 14.), (22., 0.8, 22.)]), 40.)
  out['hard_3.0_hwy'] = (S.mk(28., tf, [(5., -3.0, 10.)]), 30.)
  out['hard_5.0_hwy'] = (S.mk(28., tf, [(5., -5.0, 8.)]), 30.)
  out['stop_2.0'] = (S.mk(20., tf, [(5., -2.0, 0.)]), 45.)
  out['accordion'] = (S.mk(22., tf, [(4., -1.0, 14.), (14., 1.0, 22.), (24., -1.0, 14.), (34., 1.0, 22.)]), 50.)
  out['cutin_close'] = (dict(S.mk(25., tf, [(0., 0., 20.)], present_from=5.0), appear=(5.0, 22.)), 30.)
  out['cutin_brake'] = (dict(S.mk(25., tf, [(6., -2.0, 12.)], present_from=5.0), appear=(5.0, 35.)), 30.)
  out['approach_slow'] = (dict(S.mk(15., tf, [(0., 0., 15.)], gap_extra=70.)), 40.)
  return out


if __name__ == '__main__':
  rows = []
  for tf in (1.0, 1.45, 2.0):
    for name, (sc, T) in scenarios(tf).items():
      mh = C.metrics(C.run(C.head_mod, sc, tf=tf, T=T))
      mb = C.metrics(C.run(C.base_mod, sc, tf=tf, T=T))
      rows.append((tf, name, mh, mb))
  print(f"{'tf':>4} {'scenario':<14} | {'minGap H/B':>13} {'minTH H/B':>11} {'minTTC H/B':>13} {'aMin H/B':>12} {'jMin H/B':>12} {'crash':>5} {'badSt':>5} {'maxMgn':>6} {'maxRel':>6}")
  for tf, name, h, b in rows:
    print(f"{tf:>4} {name:<14} | {h['min_gap']:6.1f}/{b['min_gap']:<6.1f} {h['min_th']:5.2f}/{b['min_th']:<5.2f} {h['min_ttc']:6.1f}/{b['min_ttc']:<6.1f} {h['a_min']:5.2f}/{b['a_min']:<5.2f} {h['jerk_min']:5.2f}/{b['jerk_min']:<5.2f} {h['crash_max']:5.1f} {h['bad_status']:5d} {h['max_margin']:6.1f} {h['max_relief']:6.2f}")
  json.dump(rows, open('sweep.json', 'w'), default=float)
