"""fuzz.json 집계(안전 지표 기준): python3 fuzz_summary.py [fuzz.json]"""
import sys, json
import numpy as np
rows = json.load(open(sys.argv[1] if len(sys.argv) > 1 else 'fuzz.json'))
err = [r for r in rows if 'err' in r]; ok = [r for r in rows if 'err' not in r]
print('총', len(rows), '오류', len(err), '정상', len(ok))
for r in err[:3]: print('  err', r)
g = lambda k, s: np.array([r['h'][k] - r['b'][k] for r in ok])
d_gap, d_ttc, d_th, d_a, d_j = g('min_gap', 0), g('min_ttc', 0), g('min_th', 0), g('a_min', 0), g('jerk_min', 0)
hc = np.array([r['h']['crash_max'] for r in ok]); bc = np.array([r['b']['crash_max'] for r in ok])
hb = np.array([r['h']['bad_status'] for r in ok])
print(f"min_gap 차(H-B): 최소 {d_gap.min():.2f} 중앙 {np.median(d_gap):.2f} 최대 {d_gap.max():.2f} m | H<B-0.5m: {(d_gap<-0.5).sum()}건, H<B-0.1m: {(d_gap<-0.1).sum()}건")
print(f"min_TTC 차: 최소 {d_ttc.min():.2f} 중앙 {np.median(d_ttc):.2f} 최대 {d_ttc.max():.2f} s | H<B-1s: {(d_ttc<-1).sum()}건")
print(f"min_TH  차: 최소 {d_th.min():.3f} 중앙 {np.median(d_th):.3f} 최대 {d_th.max():.3f} s")
print(f"a_min 차(H-B): 최소 {d_a.min():.2f} 중앙 {np.median(d_a):.3f} 최대 {d_a.max():.2f} m/s2 (음수=HEAD가 더 강하게 제동)")
print(f"jerk_min 차: 최소 {d_j.min():.2f} 중앙 {np.median(d_j):.3f}")
print(f"FCW(crash>2): HEAD만 {int(((hc>2)&(bc<=2)).sum())}건, BASE만 {int(((bc>2)&(hc<=2)).sum())}건, 둘 다 {int(((hc>2)&(bc>2)).sum())}건")
print(f"솔버 비정상 status(HEAD) 프레임 있는 케이스: {int((hb>0).sum())}건")
print(f"margin>0 케이스 {int(sum(r['h']['max_margin']>0.01 for r in ok))}건, relief>0 케이스 {int(sum(r['h']['max_relief']>0 for r in ok))}건")
for key, d, label in (('min_gap', d_gap, 'min_gap이 기준선보다 가장 나빠진 5건'), ('min_ttc', d_ttc, 'min_TTC가 가장 나빠진 5건')):
  print('\n' + label + ':')
  for i in np.argsort(d)[:5]:
    r = ok[i]; print(f"  #{r['i']} tf={r['tf']} v0={r['v0']:.1f} gap배율={r['gapm']:.2f} adec={r['adec']} | gapH/B={r['h']['min_gap']:.1f}/{r['b']['min_gap']:.1f} ttcH/B={r['h']['min_ttc']:.1f}/{r['b']['min_ttc']:.1f} relief={r['h']['max_relief']:.2f} margin={r['h']['max_margin']:.1f}")
