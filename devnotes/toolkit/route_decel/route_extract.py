#!/usr/bin/env python3
"""rlog.zst 1개 -> route(내비 경로) 감속 분석용 20Hz 병합 표 + 구간 출력 + 배율 오프라인 재계산.

사용:
  route_extract.py extract <schema_dir> <rlog.zst> <out.pkl>
      carState/carControl/longitudinalPlan/carrotMan/radarState/selfdriveState를 뽑아 carrotMan(20Hz) 기준으로 병합.
      t는 첫 carState 기준 초. 열: vE(km/h), aEgo, brakeP, gasP, accel(carControl), longActive, state/enabled/alertType(selfdriveState),
      src_y/aTarget(longitudinalPlan), des/src_x(carrotMan desiredSpeed/Source), vTurn, road, xTurn, xDist, route(디버그 문자열 route=값), name 등.
  route_extract.py show <out.pkl> <t0> <t1> [step]
      구간을 step행 간격(기본 4행 = 0.2 s)으로 표로 출력.
  route_extract.py replay <out.pkl> <t0> <t1> <base> [near far guide]
      로그의 route=값을 base로 나눠 원시값을 되돌리고, carrot_serv.map_turn_speed_factor()와 같은 공식
      (xTurn 3/4/6일 때 far~near 선형, near 이내 guide)으로 새 route 목표를 산술 재계산. 차량/플래너 시뮬레이션이 아님.
      base는 로그 당시 MapTurnSpeedFactor/100(예: 135 -> 1.35). 기본 near=200, far=300, guide=1.05.
schema_dir: log.capnp/custom.capnp/deprecated.capnp/include/ + car.capnp를 한 폴더에 모은 곳(로그 기록 커밋 기준, README 참고).
의존: pycapnp, zstandard, pandas, numpy. 주의: route= 값은 carrotMan.szPosRoadName 안의 debugText에서 읽는다.
"""
import sys, re
import numpy as np
import pandas as pd


def extract(schema_dir, rlog, out):
  import capnp, zstandard
  capnp.remove_import_hook()
  log = capnp.load(schema_dir.rstrip('/') + '/log.capnp', imports=[schema_dir])
  raw = zstandard.ZstdDecompressor().stream_reader(open(rlog, 'rb')).read()
  R = {k: [] for k in ('cs', 'cc', 'lp', 'cm', 'rs', 'ss')}
  for e in log.Event.read_multiple_bytes(raw):
    w = e.which(); t = e.logMonoTime * 1e-9
    if w == 'carState':
      c = e.carState
      R['cs'].append(dict(t=t, vEgo=c.vEgo, aEgo=c.aEgo, brakeP=c.brakePressed, gasP=c.gasPressed, vCruise=c.vCruise))
    elif w == 'carControl':
      c = e.carControl
      R['cc'].append(dict(t=t, longActive=c.longActive, accel=c.actuators.accel))
    elif w == 'longitudinalPlan':
      p = e.longitudinalPlan
      R['lp'].append(dict(t=t, lpsrc=str(p.longitudinalPlanSource), aTarget=p.aTarget, vNow=p.vTargetNow, hasLead=p.hasLead))
    elif w == 'carrotMan':
      m = e.carrotMan
      R['cm'].append(dict(t=t, road=m.nRoadLimitSpeed, xTurn=m.xTurnInfo, xDist=m.xDistToTurn, vTurn=m.vTurnSpeed,
                          name=m.szPosRoadName, des=m.desiredSpeed, src=m.desiredSource))
    elif w == 'radarState':
      l = e.radarState.leadOne
      R['rs'].append(dict(t=t, leadStatus=l.status, dRel=l.dRel))
    elif w == 'selfdriveState':
      s = e.selfdriveState
      R['ss'].append(dict(t=t, state=str(s.state), enabled=s.enabled, alertType=s.alertType))
  D = {k: pd.DataFrame(v).sort_values('t') for k, v in R.items()}
  t0 = D['cs'].t.iloc[0]
  m = D['cm'].copy()
  for d in D.values():
    d['t'] = d['t'] - t0
  m['t'] = m['t'] - t0
  for k in ('cs', 'cc', 'lp', 'rs', 'ss'):
    m = pd.merge_asof(m, D[k], on='t', direction='nearest')
  m['vE'] = m.vEgo * 3.6
  m['route'] = m.name.map(lambda s: float(re.search(r'route=([-0-9.]+)', s).group(1)) if re.search(r'route=([-0-9.]+)', s or '') else np.nan)
  m.to_pickle(out)
  print(f'rows={len(m)} duration={m.t.iloc[-1]:.1f}s -> {out}')


def factor(base, turn, dist, near=200., far=300., guide=1.05):
  if turn not in (3, 4, 6):
    return base
  g = min(base, guide)
  if dist <= near: return g
  if dist >= far: return base
  return g + (base - g) * (dist - near) / (far - near)


def main():
  pd.set_option('display.width', 250); pd.set_option('display.max_rows', 500)
  mode = sys.argv[1]
  if mode == 'extract':
    extract(sys.argv[2], sys.argv[3], sys.argv[4])
  elif mode == 'show':
    m = pd.read_pickle(sys.argv[2]); t0, t1 = float(sys.argv[3]), float(sys.argv[4]); step = int(sys.argv[5]) if len(sys.argv) > 5 else 4
    w = m[(m.t >= t0) & (m.t <= t1)]
    cols = ['t', 'vE', 'aEgo', 'brakeP', 'accel', 'longActive', 'state', 'alertType', 'aTarget', 'des', 'src', 'route', 'vTurn', 'road', 'xTurn', 'xDist', 'vCruise']
    print(w[cols].iloc[::step].round(2).to_string())
  elif mode == 'replay':
    m = pd.read_pickle(sys.argv[2]); t0, t1, base = float(sys.argv[3]), float(sys.argv[4]), float(sys.argv[5])
    near, far, guide = (float(x) for x in sys.argv[6:9]) if len(sys.argv) >= 9 else (200., 300., 1.05)
    w = m[(m.t >= t0) & (m.t <= t1)].copy()
    w['raw'] = w.route / base
    w['fac'] = [factor(base, x, d, near, far, guide) for x, d in zip(w.xTurn, w.xDist)]
    w['route_new'] = w.raw * w.fac
    w['gap_new'] = w.route_new - w.vE
    print(w[['t', 'vE', 'xTurn', 'xDist', 'route', 'raw', 'fac', 'route_new', 'gap_new', 'vTurn', 'des', 'src']].iloc[::8].round(1).to_string())
  else:
    print(__doc__)


if __name__ == '__main__':
  main()
