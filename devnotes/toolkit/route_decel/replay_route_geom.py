#!/usr/bin/env python3
"""rlog 재생으로 carrot_man.get_path_after_distance() 수정(153차) 전/후 경로 기하를 비교한다.

재구현 없이 실제 소스에서 함수 원문을 ast로 뽑아 exec한다(haversine / closest_point_on_segment /
gps_to_relative_xy / calculate_curvature + V_CURVE 상수 + get_path_after_distance).
  OLD = 로그 기록 커밋(예: 8e8b0d1a)의 carrot_man.py, NEW = 153차 수정 후(예: f23d05f) carrot_man.py.
입력(로그에서): carrotMan(xPosLat/xPosLon/xPosAngle = get_path 입력 vpPosPoint/bearing, naviPaths = 기록된 리샘플 경로),
                navRoute(경로 폴리라인 = navi_points), carState.vEgo.
사용:
  replay_route_geom.py extract <schema_dir> <rlog.zst> <out.pkl>
  replay_route_geom.py run <old_carrot_man.py> <new_carrot_man.py> <out_prefix> <seg.pkl> [<seg2.pkl> ...]
      (여러 pkl을 주면 시간순 연속 세그먼트로 보고 start_index 상태를 이어받는다)
      가정 파라미터(로그에 없음): AutoNaviSpeedDecelRate=0.8 m/s^2, AutoNaviSpeedCtrlEnd=0 (run()의 decel/ctrl_end 인자)
  replay_route_geom.py report <label>=<prefix>_replay.pkl [<label2>=...] [--base 1.2] [--guide 1.0]
      충실도(OLD 재생 vs 로그 naviPaths) / 트리거(첫 세그먼트>=300m) 비율 / route 급변(>20km/h 프레임간) 로그·OLD·NEW 비교 /
      비트리거 사이클 OLD==NEW 무회귀 확인 / route source des 급변 집계. 세그먼트 표시는 <label>#<n>(n=run에 준 순서 0..).
      --base는 route/out_speed 계수(MapTurnSpeedFactor/100) 추정값(153~154차 로그에서 약 1.2로 역산), --guide는 MAP_TURN_GUIDE_FACTOR.
한계: 로그 xPos는 Float32(약 0.4~0.8 m 양자화). 세그먼트 첫 사이클의 start_index는 전역 최근접으로 시드.
      실차 검증 아님(로그 재생, open-loop).
"""
import ast, sys, math, pickle
import numpy as np


def load_funcs(path):
  src = open(path, encoding='utf-8').read()
  tree = ast.parse(src)
  want_f = {'haversine', 'closest_point_on_segment', 'get_path_after_distance', 'gps_to_relative_xy', 'calculate_curvature'}
  want_v = {'V_CURVE_LOOKUP_BP', 'V_CRUVE_LOOKUP_VALS'}
  ns = {'math': math, 'np': np}
  for n in tree.body:
    if isinstance(n, ast.FunctionDef) and n.name in want_f:
      exec(compile(ast.Module([n], []), path, 'exec'), ns)
    elif isinstance(n, ast.Assign) and any(isinstance(t, ast.Name) and t.id in want_v for t in n.targets):
      exec(compile(ast.Module([n], []), path, 'exec'), ns)
  missing = [k for k in want_f | want_v if k not in ns]
  assert not missing, missing
  return ns


def extract(schema_dir, rlog, out):
  import capnp, zstandard
  capnp.remove_import_hook()
  log = capnp.load(schema_dir.rstrip('/') + '/log.capnp', imports=[schema_dir])
  raw = zstandard.ZstdDecompressor().stream_reader(open(rlog, 'rb')).read()
  cm, nr, cs = [], [], []
  t0 = None
  for e in log.Event.read_multiple_bytes(raw):
    w = e.which(); t = e.logMonoTime * 1e-9
    if w == 'carState':
      if t0 is None: t0 = t
      cs.append((t, e.carState.vEgo))
    elif w == 'navRoute':
      nr.append((t, [(c.longitude, c.latitude) for c in e.navRoute.coordinates]))
    elif w == 'carrotMan':
      m = e.carrotMan
      cm.append(dict(t=t, lat=m.xPosLat, lon=m.xPosLon, ang=m.xPosAngle, navi=m.naviPaths, xTurn=m.xTurnInfo,
                     xDist=m.xDistToTurn, des=m.desiredSpeed, src=m.desiredSource, name=m.szPosRoadName,
                     road=m.nRoadLimitSpeed, vTurn=m.vTurnSpeed))
  pickle.dump(dict(t0=t0, cm=cm, nr=nr, cs=cs), open(out, 'wb'))
  print(f'carrotMan={len(cm)} navRoute={len(nr)} carState={len(cs)} -> {out}')


def parse_navi(s):
  """'x,y,d;x,y,d;...' -> (pts Nx2, d N)"""
  if not s: return np.zeros((0, 2)), np.zeros(0)
  a = np.array([[float(v) for v in p.split(',')] for p in s.split(';')])
  return a[:, :2], a[:, 2]


def resample(rel, interval=10.0):
  from shapely.geometry import LineString
  line = LineString(rel)
  pts, ds, cur = [], [], 0.0
  while cur <= line.length:
    p = line.interpolate(cur); pts.append((p.x, p.y)); ds.append(cur); cur += interval
  return pts, ds, line.length


def curv_speeds(F, pts, road_limit, sample=4):
  """carrot_navi_route()의 곡률->속도(역방향 감속 제한 이전) 부분. 원문 그대로."""
  speeds, curv = [], []
  if len(pts) >= sample * 2 + 1:
    for i in range(len(pts) - sample * 2):
      c = F['calculate_curvature'](pts[i], pts[i + sample], pts[i + sample * 2])
      curv.append(c)
      sp = np.interp(abs(c), F['V_CURVE_LOOKUP_BP'], F['V_CRUVE_LOOKUP_VALS'])
      if abs(c) < 0.02: sp = max(sp, road_limit)
      speeds.append(sp)
  return speeds, curv


def out_speed_of(speeds, v_ego_kph, decel, ctrl_end=0.0, interval=10.0):
  """carrot_navi_route() 역방향 감속 제한 루프 원문."""
  if not speeds: return 300.0
  accel_limit_kmh = decel * 3.6
  out = [0] * len(speeds); out[-1] = speeds[-1]
  time_delay = ctrl_end; time_wait = 0
  for i in range(len(speeds) - 2, -1, -1):
    target = speeds[i]; nxt = out[i + 1]
    if target < nxt:
      time_delay = max(0, (v_ego_kph - target) / accel_limit_kmh)
      time_wait = -time_delay
    ti = interval / (nxt / 3.6) if nxt > 0 else 0
    ta = min(ti, max(0, ti + time_wait))
    out[i] = min(target, nxt + accel_limit_kmh * ta)
    time_wait += min(2.0, ti)
  return out[0]


def run_one(F, coords, idx, pos, heading, decel, ctrl_end, vkph, road):
  path, idx, sp = F['get_path_after_distance'](idx, coords, pos, 300)
  first = None
  if path and len(path) >= 2:
    first = F['haversine'](path[0][0], path[0][1], coords[idx + 1][0], coords[idx + 1][1])
  rel = F['gps_to_relative_xy'](path, sp, heading) if path else []
  if len(rel) >= 2:
    pts, ds, L = resample(rel)
  else:
    pts, ds, L = [], [], 0.0
  speeds, curv = curv_speeds(F, pts, road)
  return dict(idx=idx, pts=pts, ds=ds, L=L, speeds=speeds, curv=curv, first=first,
              vmin_raw=(min(speeds) if speeds else 300.0), out=out_speed_of(speeds, vkph, decel, ctrl_end), npath=len(path))


def run(old_py, new_py, prefix, pkls, decel=0.8, ctrl_end=0.0):
  import pandas as pd
  Fo, Fn = load_funcs(old_py), load_funcs(new_py)
  rows = []; st = {}
  segs = [pickle.load(open(p, 'rb')) for p in pkls]
  poly_key = None; idx_o = idx_n = 0
  for si, S in enumerate(segs):
    nr_t = np.array([x[0] for x in S['nr']]); cs_t = np.array([x[0] for x in S['cs']]); cs_v = np.array([x[1] for x in S['cs']])
    for k, m in enumerate(S['cm']):
      if not m['navi']: continue
      j = max(0, int(np.searchsorted(nr_t, m['t'], side='right')) - 1)
      coords = S['nr'][j][1]
      key = (len(coords), coords[0], coords[-1])
      pos = (float(m['lon']), float(m['lat']))
      if key != poly_key:  # 폴리라인 교체 -> 전역 최근접으로 시드
        poly_key = key
        best, bi = 1e18, 0
        for i in range(len(coords) - 1):
          c = Fo['closest_point_on_segment'](coords[i], coords[i + 1], pos)
          d = Fo['haversine'](pos[0], pos[1], c[0], c[1])
          if d < best: best, bi = d, i
        idx_o = idx_n = bi
      vk = float(cs_v[min(len(cs_v) - 1, int(np.searchsorted(cs_t, m['t'])))]) * 3.6
      o = run_one(Fo, coords, idx_o, pos, m['ang'], decel, ctrl_end, vk, m['road']); idx_o = o['idx']
      n = run_one(Fn, coords, idx_n, pos, m['ang'], decel, ctrl_end, vk, m['road']); idx_n = n['idx']
      lp, ld = parse_navi(m['navi'])
      rows.append(dict(seg=si, t=m['t'] - S['t0'], xTurn=m['xTurn'], xDist=m['xDist'], des=m['des'], src=m['src'], name=m['name'],
                       idx_o=o['idx'], first_o=o['first'], npath_o=o['npath'], L_o=o['L'], L_n=n['L'],
                       vmin_o=o['vmin_raw'], vmin_n=n['vmin_raw'], out_o=o['out'], out_n=n['out'],
                       log_L=(ld[-1] if len(ld) else 0.0), log_n=len(lp), o_n=len(o['pts']), n_n=len(n['pts']),
                       # 로그 경로 vs OLD 재생 경로 끝점 편차(충실도)
                       end_dev=(float(np.hypot(*(np.array(o['pts'][-1]) - lp[-1]))) if len(lp) and o['pts'] else np.nan),
                       lat=m['lat'], lon=m['lon'], pts_o=o['pts'], pts_n=n['pts'], pts_log=lp.tolist(), curv_o=o['curv'], curv_n=n['curv']))
  df = pd.DataFrame(rows)
  df.to_pickle(prefix + '_replay.pkl')
  print(f'rows={len(df)} -> {prefix}_replay.pkl')
  return df


def _fac(base, turn, dist, near=200., far=300., guide=1.0):
  if turn not in (3, 4, 6): return base
  g = min(base, guide)
  if dist <= near: return g
  if dist >= far: return base
  return g + (base - g) * (dist - near) / (far - near)


def report(items, base=1.2, guide=1.0):
  import re
  import pandas as pd
  pd.set_option('display.width', 250); pd.set_option('display.max_columns', 40)
  def dev(a, b):
    a = np.array(a); b = np.array(b)
    if len(a) == 0 or len(b) == 0: return np.nan
    n = min(len(a), len(b)); return float(np.max(np.hypot(*(a[:n] - b[:n]).T)))
  parts = []
  for lab, path in items:
    d = pd.read_pickle(path)
    d['sn'] = [f'{lab}#{s}' for s in d.seg]
    parts.append(d)
  d = pd.concat(parts, ignore_index=True)
  d['trig'] = d.first_o >= 300
  d['route'] = d.name.map(lambda s: float(re.search(r'route=([-0-9.]+)', s or '').group(1)) if re.search(r'route=([-0-9.]+)', s or '') else np.nan)
  d['f'] = [_fac(base, t, x, guide=guide) for t, x in zip(d.xTurn, d.xDist)]
  d['r_o'] = d.out_o * d.f; d['r_n'] = d.out_n * d.f
  d['maxdev'] = [dev(a, b) for a, b in zip(d.pts_o, d.pts_log)]
  def jumps(x, thr=20): return np.where(np.abs(np.diff(x)) > thr)[0]
  rows = []
  for sn, g in d.groupby('sn', sort=False):
    g = g.sort_values('t').reset_index(drop=True)
    tr = g.trig.values
    row = dict(seg=sn, cycles=len(g), trig_pct=round(tr.mean() * 100, 1),
               fid3_trig=round((g[g.trig].maxdev <= 3).mean() * 100, 1) if tr.any() else np.nan,
               fid3_nontrig=round((g[~g.trig].maxdev <= 3).mean() * 100, 1))
    for nm, col in (('log', 'route'), ('old', 'r_o'), ('new', 'r_n')):
      j = jumps(g[col].values)
      row[nm + '_jumps'] = len(j); row[nm + '_jumps_trig'] = int(sum(tr[i] or tr[i + 1] for i in j))
    nt = g[~g.trig]
    row['nontrig_out_diff'] = int((nt.out_o != nt.out_n).sum())
    des = g.des.values.astype(float); rt = (g.src == 'route').values
    j = np.where((np.abs(np.diff(des)) > 20) & (rt[:-1] | rt[1:]))[0]
    row['route_src_cycles'] = int(rt.sum()); row['des_jumps_route'] = len(j); row['des_jumps_route_trig'] = int(sum(tr[i] or tr[i + 1] for i in j))
    rows.append(row)
  print(pd.DataFrame(rows).to_string(index=False))


if __name__ == '__main__':
  if sys.argv[1] == 'extract':
    extract(sys.argv[2], sys.argv[3], sys.argv[4])
  elif sys.argv[1] == 'run':
    run(sys.argv[2], sys.argv[3], sys.argv[4], sys.argv[5:])
  elif sys.argv[1] == 'report':
    args = sys.argv[2:]; base = 1.2; guide = 1.0
    if '--base' in args: i = args.index('--base'); base = float(args[i + 1]); del args[i:i + 2]
    if '--guide' in args: i = args.index('--guide'); guide = float(args[i + 1]); del args[i:i + 2]
    report([a.split('=', 1) for a in args], base, guide)
  else:
    print(__doc__)
