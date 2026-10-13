#!/usr/bin/env python3
"""batch.py (276cha, batch15.py 복원) cl_replay.run 민감도 묶음: 앞차 감속 시작 ts 116.1/116.8/117.5 x 입력(vision/ideal) x 게이트(on/off) + 설정속도 19.4 m/s 2런.
(vision은 ts 116.1만, 앞차 입력이 로그 그대로라 ts와 무관.) 표: 시각 -0.5/-1.0/-2.0 m/s² 도달, 118/118.5/119/120초 가속도, 최소 가속도, 최소 간격, 121초 속도, 끝 속도.
이어서 'ideal' 참값 간격과 로그 leadOne dRel을 비교 출력(비전 거리 오차 확인). 같은 폴더 cl_replay.py 필요. 약 11런(약 4~5분이라 300초 제한 주의, setsid nohup 권장). 결과 batch.pkl. 실차 검증 아님."""
import pickle, numpy as np, pandas as pd
import cl_replay as cl
rows = [cl.log_row()]; res = {}
for ts in (116.1, 116.8, 117.5):
    for inp in ('vision', 'ideal'):
        if inp == 'vision' and ts != 116.1:
            continue
        for go in (False, True):
            nm = 'ts%.1f|%s|%s' % (ts, inp, 'gate_off' if go else 'gate_on'); d = cl.run(ts, inp, go); res[nm] = d; rows.append(cl.summ(d, nm))
for inp in ('vision', 'ideal'):
    nm = 'vset19.4 ts116.1|%s|gate_on' % inp; d = cl.run(116.1, inp, False, vset=19.4); res[nm] = d; rows.append(cl.summ(d, nm))
pickle.dump((rows, res), open('batch.pkl', 'wb'))
df = pd.DataFrame(rows); pd.set_option('display.width', 260); pd.set_option('display.max_colwidth', 40)
print(df[['name', 't_a05', 't_a10', 't_a20', 'a118', 'a1185', 'a119', 'a120', 'amin', 'gap_min', 'v121', 'v_end']].round(2).to_string(index=False))
d = res['ts116.1|ideal|gate_on']
for q in (116.5, 117, 117.5, 118, 118.5, 119):
    k = int(np.abs(d.t - q).argmin()); i = cl._ix(q)
    print('t=%.1f 참값 간격(시뮬) %.1f m, 로그 leadOne dRel %.1f (status=%s radar=%s)' % (q, d.gap[k], cl.rs.l1_dRel.values[i], cl.rs.l1_status.values[i], cl.rs.l1_radar.values[i]))
