"""comfort_path_has_reserve를 강제로 False로 만들어 완화 해제 폴백 경로를 발동시키고, 정상/강제/기준선을 비교한다(near_decel_0.6 시나리오)."""
import os, sys
sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))
import cl_sim as C, scen as S


def mkcase(tf):
  sc = S.mk(21., tf, [(3., -0.6, 15.)], gap_extra=8.)
  sc["v0"] = 22.; sc["gap0"] = 6.0 + 22. * tf + 8.
  return sc


def main():
  orig = C.head_mod.comfort_path_has_reserve
  calls = dict(n=0)
  def always_false(*a, **k):
    calls["n"] += 1; return False
  for tf in (1.2, 1.45, 2.0):
    sc = mkcase(tf)
    C.head_mod.comfort_path_has_reserve = orig
    A = C.run(C.head_mod, sc, tf=tf, T=40., vset=22.)
    C.head_mod.comfort_path_has_reserve = always_false; calls["n"] = 0
    B = C.run(C.head_mod, sc, tf=tf, T=40., vset=22.)
    n = calls["n"]
    C.head_mod.comfort_path_has_reserve = orig
    Z = C.run(C.base_mod, sc, tf=tf, T=40., vset=22.)
    mA, mB, mZ = C.metrics(A), C.metrics(B), C.metrics(Z)
    rel_after = max(r["relief"] for r in B)
    print(f"tf={tf}: 폴백 호출 {n}회 | relief최대 정상={mA['max_relief']:.2f} 강제거절={rel_after:.2f} | 솔버 비정상프레임 정상/강제={mA['bad_status']}/{mB['bad_status']} | minGap 정상/강제/기준선={mA['min_gap']:.2f}/{mB['min_gap']:.2f}/{mZ['min_gap']:.2f} | aMin={mA['a_min']:.2f}/{mB['a_min']:.2f}/{mZ['a_min']:.2f} | crash {mA['crash_max']}/{mB['crash_max']}")


if __name__ == '__main__':
  main()
