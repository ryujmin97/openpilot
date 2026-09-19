"""리드 감속 이벤트(aLeadK < -1.0) 추출 + 실제 로그 지표 표.
사용: (작업 폴더에서) events.py   # out/merged.pkl 필요(merge_lead_series.py 출력). 결과: out/events.pkl 와 표 출력.
이벤트: 연속 간격 2 s 초과 시 분리(pairs 순서 x 시간 순으로 idx 부여, 97차 데이터 기준 26건 = 6+5+7+7+1).
창: t0=t_start-3 s, t1=t_start+11 s (구간 범위로 자름). 지표는 이 창 안의 실제 로그 값.
열: idx, pair, t_start/t_end, aLeadK_min, aEgo_min(실제 최대 감속), dRel_min, hw_min(dRel/vEgo 최소), ttc_min(dRel/-vRel, 접근 중일 때), vRel0(시작 시 dRel 변화 방향 확인용), tFollow(평균).
한계: 이벤트 정의(임계값 -1.0, 간격 2 s)는 97차 분석 기준. 끼어들기(vRel>0) 이벤트도 포함되므로 해석은 WIP.md 98차 참고.
"""
import pandas as pd, numpy as np
M = pd.read_pickle('out/merged.pkl')
THR, GAP, PRE, POST = -1.0, 2.0, 3.0, 11.0
rows = []
for pair, m in M.items():
    s = m[m.aLeadK < THR].t.values
    if len(s) == 0: continue
    cuts = np.where(np.diff(s) > GAP)[0]
    starts = np.r_[0, cuts + 1]; ends = np.r_[cuts, len(s) - 1]
    for a, b in zip(starts, ends):
        ts, te = float(s[a]), float(s[b])
        t0, t1 = max(m.t.min(), ts - PRE), min(m.t.max(), ts + POST)
        w = m[(m.t >= t0) & (m.t <= t1)]
        cl = -w.vRel.values            # 접근 속도(레이더 vRel 기준, >0이면 가까워지는 중)
        appr = cl > 0.1
        ttc = (w.dRel.values[appr] / cl[appr]) if appr.any() else np.array([np.inf])
        rows.append(dict(idx=len(rows), pair=pair, t_start=ts, t_end=te, t0=t0, t1=t1,
                         aLeadK_min=float(w.aLeadK.min()), aEgo_min=float(w.aEgo.min()),
                         dRel_min=float(w.dRel.min()), hw_min=float((w.dRel / np.maximum(w.vEgo, 1.0)).min()),
                         ttc_min=float(ttc.min()), vRel_mean=float(w.vRel.mean()), tFollow=float(w.tFollow.mean())))
E = pd.DataFrame(rows)
E.to_pickle('out/events.pkl')
if __name__ == '__main__':
    pd.set_option('display.width', 200)
    print(E.round(2).to_string(index=False)); print('이벤트 수:', len(E))
