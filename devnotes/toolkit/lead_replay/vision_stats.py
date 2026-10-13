#!/usr/bin/env python3
"""vision_stats.py (276cha 복원) 비전 단독 대 레이더 앞차 통계와 비전->레이더 인계 사건 표.
(1) leadOne 프레임을 비전 단독(status & ~radar)과 레이더(status & radar)로 나눠 연속 구간(0.15초 이내 간격, 25프레임 이상)마다
    vLead의 1초 중앙값(21프레임) 대비 잔차 RMS, aLeadK 평균, 1초 평활 dv/dt < -1.5 m/s² 프레임 수와 그중 aLeadK > -1.0(과소 보고) 프레임 수를 센다.
(2) 비전 -> 레이더 인계(프레임 i-1 비전, i 레이더)마다 직전 3프레임 비전 vLead 평균과 인계 직후 레이더 vLead, dRel 비교를 한 줄씩 출력.
275cha/276cha 로그 0000049d 결과: 비전 518프레임 RMS 0.70 대 레이더 1,418프레임 0.07 m/s, 감속 구간 과소 보고 비전 44/53(83%) 대 레이더 6/159(4%), 인계 13건 중 119.0초가 -5.1 m/s로 최대.
한 로그의 통계라 일반화 못 한다(다른 로그에서 반복 확인은 미실시). 환경변수 LR_PKL(기본 ./log_lead.pkl). 실차 검증 아님."""
import os, pickle, numpy as np, pandas as pd
D = pickle.load(open(os.environ.get('LR_PKL', 'log_lead.pkl'), 'rb')); rs = D['rs']


def stats(mask, name):
    d = rs[mask].copy()
    d['grp'] = (d.t.diff() > 0.15).cumsum(); res = []; dvdt = []; ak = []
    for _, g in d.groupby('grp'):
        if len(g) < 25:
            continue
        v = g.l1_vLead; med = v.rolling(21, center=True, min_periods=11).median(); res += list((v - med).dropna())
        dv = np.gradient(v.rolling(11, center=True, min_periods=5).mean().values, g.t.values); dvdt += list(dv); ak += list(g.l1_aLeadK.values)
    res = np.array(res); dvdt = np.array(dvdt); ak = np.array(ak)
    print('%-12s 프레임 %5d  vLead 1초 중앙값 대비 잔차 RMS %.2f m/s | aLeadK 평균 %.2f, 1초 평활 dv/dt<-1.5 구간 %d프레임, 그중 aLeadK>-1.0: %d' % (
        name, mask.sum(), np.sqrt(np.mean(res ** 2)), ak.mean(), int((dvdt < -1.5).sum()), int(((dvdt < -1.5) & (ak > -1.0)).sum())))


stats(rs.l1_status & ~rs.l1_radar, '비전 단독'); stats(rs.l1_status & rs.l1_radar, '레이더')
d = rs.l1_status.values; r = rs.l1_radar.values; t = rs.t.values; v = rs.l1_vLead.values
idx = [i for i in range(1, len(rs)) if d[i] and r[i] and d[i - 1] and not r[i - 1]]
print('비전->레이더 인계 %d건: 인계 직전 3프레임 비전 vLead 평균 대 인계 직후 레이더 vLead, 차이(레이더-비전) m/s' % len(idx))
for i in idx:
    print('  t=%.1f  비전 %.1f  레이더 %.1f  차 %+.1f   dRel비전 %.1f 레이더 %.1f' % (t[i], v[i - 3:i].mean(), v[i], v[i] - v[i - 3:i].mean(), rs.l1_dRel.values[i - 1], rs.l1_dRel.values[i]))
