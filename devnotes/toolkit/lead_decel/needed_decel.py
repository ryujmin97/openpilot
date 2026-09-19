"""이벤트별 사후(hindsight) 필요 감속: 리드 궤적을 미리 안다고 가정하고, 이벤트 시작(t_start)부터 자차가 상수 감속(지연 0.3 s, counterfactual.sim)을
해서 시간차(gap/vE) 하한 1.0/1.2/1.5/1.8 s를 지키는 최소 감속 크기(m/s², 이분법). 시뮬 구간은 t_start ~ t_start+16 s(시리즈 끝에서 자름).
사용: (작업 폴더에서) needed_decel.py   # out/merged.pkl, out/events.pkl 필요. 결과: out/needed.pkl 와 표 출력.
한계: 사후 정보를 쓰는 이상화 값 — 실시간 제어기가 쓸 수 없는 '필요 최소 감속의 크기 파악용'이지 설계값이 아님. 0.0은 감속 없이도 하한 유지.
      리드가 이후 가속하는 구간·끼어들기(#18~21) 이벤트에서는 의미가 다르므로 해석에 주의(WIP.md 98차).
"""
import sys, os; sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))
import numpy as np, pandas as pd
import counterfactual as C
E = pd.read_pickle('out/events.pkl')
FLOORS, SPAN = (1.0, 1.2, 1.5, 1.8), 16.0
def need(m, t_on, floor, t_end):
    def ok(mag):
        g, v, _ = C.sim(m, t_on, -mag, t_end=t_end); return (g / np.maximum(v, 1.0)).min() >= floor
    if ok(0.0): return 0.0
    lo, hi = 0.0, 6.0
    if not ok(hi): return float('nan')
    for _ in range(30):
        mid = (lo + hi) / 2
        if ok(mid): hi = mid
        else: lo = mid
    return hi
rows = []
for _, r in E.iterrows():
    m = C.M[r.pair]; t_on = r.t_start
    rows.append(dict(idx=int(r.idx), pair=r.pair, t_start=round(r.t_start, 1), aEgo_actual=round(r.aEgo_min, 2),
                     **{f'h{f}': round(need(m, t_on, f, t_on + SPAN), 2) for f in FLOORS}))
N = pd.DataFrame(rows); N.to_pickle('out/needed.pkl')
if __name__ == '__main__':
    print(N.to_string(index=False))
