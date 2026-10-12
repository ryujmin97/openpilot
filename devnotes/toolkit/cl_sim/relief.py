"""편안함 완화(comfort_relief)가 켜지는 먼/근거리 완만 감속 앞차 시나리오. comfort_path_has_reserve 호출/거절 횟수도 센다."""
import os, sys
sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))
import cl_sim as C, scen as S


def far_lead(tf, v0, vl0, gap_extra, events, T=45.):
  sc = S.mk(vl0, tf, events, gap_extra=gap_extra)
  sc['v0'] = v0
  sc['gap0'] = 6.0 + v0 * tf + gap_extra
  return sc, T


def main():
  cnt = dict(calls=0, rejects=0)
  orig = C.head_mod.comfort_path_has_reserve
  def wrapped(*a, **k):
    r = orig(*a, **k); cnt['calls'] += 1; cnt['rejects'] += (not r); return r
  C.head_mod.comfort_path_has_reserve = wrapped
  cases = {}
  for tf in (1.2, 1.45, 2.0):
    cases[f'far_decel_0.5_tf{tf}'] = (tf, far_lead(tf, 22., 20., 40., [(3., -0.5, 14.)]), 22.)
    cases[f'far_decel_1.0_tf{tf}'] = (tf, far_lead(tf, 22., 20., 40., [(3., -1.0, 12.)]), 22.)
    cases[f'near_decel_0.6_tf{tf}'] = (tf, far_lead(tf, 22., 21., 8., [(3., -0.6, 15.)]), 22.)
    cases[f'hwy_decel_0.8_tf{tf}'] = (tf, far_lead(tf, 28., 27., 20., [(3., -0.8, 18.)]), 28.)
    cases[f'hwy_decel_2.0_tf{tf}'] = (tf, far_lead(tf, 28., 27., 20., [(3., -2.0, 14.)]), 28.)
  print(f"{'case':<24} {'relief>0 frames':>15} {'maxRel':>6} | {'minGap H/B':>13} {'minTTC H/B':>13} {'aMin H/B':>12} {'rejects/calls':>13} {'crash':>5}")
  for name, (tf, (sc, T), vset) in cases.items():
    cnt['calls'] = cnt['rejects'] = 0
    lh = C.run(C.head_mod, sc, tf=tf, T=T, vset=vset)
    c, r = cnt['calls'], cnt['rejects']
    lb = C.run(C.base_mod, sc, tf=tf, T=T, vset=vset)
    h, b = C.metrics(lh), C.metrics(lb)
    nrel = sum(1 for x in lh if x['relief'] > 0)
    print(f"{name:<24} {nrel:15d} {h['max_relief']:6.2f} | {h['min_gap']:6.1f}/{b['min_gap']:<6.1f} {h['min_ttc']:6.1f}/{b['min_ttc']:<6.1f} {h['a_min']:5.2f}/{b['a_min']:<5.2f} {r:>6}/{c:<6} {h['crash_max']:5.1f}")


if __name__ == '__main__':
  main()
