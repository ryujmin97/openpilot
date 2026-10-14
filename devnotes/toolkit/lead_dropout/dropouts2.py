#!/usr/bin/env python3
"""dropouts2.py [log_lead.pkl]  (286cha, 285/286cha 로그 000004a0 분석 스크립트를 앞 구간 기록에서 복원)
extract_log.py(lead_replay/)가 만든 pkl에서, 크루즈(carControl.longActive) 중 leadOne.status가 False로 끊겼다가 돌아온
구간(앞뒤가 모두 정상 프레임)을 전부 표로 출력한다: 구간 시각, 길이(status False 프레임 수 x 0.05 s), 직전/재인식의 dRel vLead aLeadK 종류(레이더/비전),
accel 명령(직전 -> 끊김 중 최소/최대 -> 재인식 뒤 2 s 최소). pkl 경로는 인자 또는 환경변수 LR_PKL(기본 ./log_lead.pkl).
길이는 radarState 20 Hz 가정(0.05 s)이다. 크루즈 시작 전 구간은 제외한다(285cha의 5건은 시작 전을 포함해 센 것).
의존: numpy pandas. 실차 검증 아님."""
import sys, os, pickle, numpy as np, pandas as pd

def main():
    path = sys.argv[1] if len(sys.argv) > 1 else os.environ.get('LR_PKL', 'log_lead.pkl')
    d = pickle.load(open(path, 'rb'))
    rs, cs, cc, lp = d['rs'], d['cs'], d['cc'], d['lp']
    la = cc[cc.longActive]
    print('longActive 첫/마지막 t:', round(la.t.min(), 2), round(la.t.max(), 2), ' 프레임', len(la), '/', len(cc))
    T0 = la.t.min()
    st = rs['l1_status'].astype(bool).values; t = rs['t'].values

    def at(df, col, tt):
        k = np.searchsorted(df['t'].values, tt, side='right') - 1; return float(df[col].values[max(k, 0)])
    runs = []; i = 0
    while i < len(st):
        if not st[i]:
            j = i
            while j < len(st) and not st[j]: j += 1
            if i > 0 and j < len(st) and t[i] >= T0: runs.append((i, j))
            i = j
        else: i += 1
    print('크루즈 활성 중 양쪽이 정상인 끊김 전체:', len(runs))
    print(' idx   구간(s)       길이  | 직전(dRel vLead aLeadK 종류)            | 재인식(dRel vLead aLeadK 종류)          | accel직전 -> 끊김중 최소/최대 -> 재인식후2s 최소')
    for (i, j) in runs:
        r0, r1 = rs.iloc[i - 1], rs.iloc[j]; t0, t1 = t[i], t[j]; dur = (j - i) * 0.05
        kind = lambda r: '레이더' if r.l1_radar else '비전'
        seg = cc[(cc.t >= t0) & (cc.t < t1)]; aft = cc[(cc.t >= t1) & (cc.t < t1 + 2.0)]
        print(f"{i:5d} {t0:7.2f}~{t1:7.2f} {dur:5.2f} | {r0.l1_dRel:5.1f} {r0.l1_vLead:5.2f} {r0.l1_aLeadK:+5.2f} {kind(r0):4s}"
              f"              | {r1.l1_dRel:5.1f} {r1.l1_vLead:5.2f} {r1.l1_aLeadK:+5.2f} {kind(r1):4s}"
              f"             | {at(cc,'accel',t0-0.05):+.2f} -> {seg.accel.min() if len(seg) else float('nan'):+.2f}/{seg.accel.max() if len(seg) else float('nan'):+.2f} -> {aft.accel.min() if len(aft) else float('nan'):+.2f}")

main()
