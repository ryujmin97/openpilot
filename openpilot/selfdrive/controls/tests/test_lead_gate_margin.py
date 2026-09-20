"""margin_ratio 리드 감속 게이트(long_mpc.py) 단위 테스트. acados 없이 ast로 함수/메서드만 실행한다."""

import ast
from pathlib import Path
from types import SimpleNamespace as NS

import numpy as np
import pytest

COMFORT_BRAKE, STOP_DISTANCE, T_FOLLOW = 2.5, 6.0, 1.45
DT = 0.05


def load():
  path = Path(__file__).resolve().parents[1] / "lib/longitudinal_mpc_lib/long_mpc.py"
  tree = ast.parse(path.read_text(encoding="utf-8"))
  consts = {"LEAD_DANGER_FACTOR", "GATE_M_LO", "GATE_M_HI", "GATE_T_LO", "GATE_T_HI", "GATE_TAU_G", "GATE_TAU_TARGET"}
  assigns = [node for node in tree.body if isinstance(node, ast.Assign)
             and any(isinstance(t, ast.Name) and t.id in consts for t in node.targets)]
  # "GATE_M_LO, GATE_M_HI = ..." 처럼 튜플 대입도 포함되도록 Tuple 타깃 처리
  assigns += [node for node in tree.body if isinstance(node, ast.Assign)
              and any(isinstance(t, ast.Tuple) and any(isinstance(e, ast.Name) and e.id in consts for e in t.elts) for t in node.targets)]
  helpers = [node for node in tree.body if isinstance(node, ast.FunctionDef)
             and node.name in ("get_stopped_equivalence_factor", "get_safe_obstacle_distance")]
  mpc = next(node for node in tree.body if isinstance(node, ast.ClassDef) and node.name == "LongitudinalMpc")
  methods = [node for node in mpc.body if isinstance(node, ast.FunctionDef) and node.name in ("_gate_raw", "process_lead", "extrapolate_lead")]
  times = np.array([10. * (i / 12) ** 2 for i in range(13)])
  ns = {"np": np, "COMFORT_BRAKE": COMFORT_BRAKE, "STOP_DISTANCE": STOP_DISTANCE, "ACCEL_MIN": -3.5,
        "LEAD_ACCEL_TAU": 1.5, "T_IDXS": times, "T_DIFFS": np.diff(times, prepend=0.),
        "time": NS(monotonic=lambda: 0.0), "cloudlog": NS(debug=lambda *a, **k: None),
        "staticmethod": staticmethod}
  exec(compile(ast.Module(body=assigns + helpers, type_ignores=[]), str(path), "exec"), ns)
  cls = {}
  module = ast.fix_missing_locations(ast.Module(body=[ast.ClassDef(name="M", bases=[], keywords=[], body=methods, decorator_list=[])], type_ignores=[]))
  exec(compile(module, str(path), "exec"), ns, cls)
  return ns, cls["M"]


def make(v_ego=20., t_follow=T_FOLLOW):
  ns, M = load()
  self = M.__new__(M)
  self.x0 = np.array([0., v_ego, 0.])
  self.dt = DT
  self._gate_g = np.array([1.0, 1.0])
  self._gate_ctx = (t_follow, COMFORT_BRAKE, STOP_DISTANCE)
  self._gate_last_cloudlog_t = 0.0
  return ns, M, self


def raw(v_ego, v_lead, gap, t_follow=T_FOLLOW):
  ns, M, _ = make(v_ego, t_follow)
  return M._gate_raw(gap, v_ego, v_lead, t_follow, COMFORT_BRAKE, STOP_DISTANCE)


def steady_gap(v, t_follow=T_FOLLOW):
  return t_follow * v + STOP_DISTANCE


def test_steady_following_is_fully_relaxed():
  # 정상 추종 평형(gap = tFollow*v + stop_distance)에서는 m = 1/LEAD_DANGER_FACTOR = 1.25 -> 게이트 완전 약화
  for v in (5., 15., 25.):
    g, m = raw(v, v, steady_gap(v))
    assert m == pytest.approx(1.25)
    assert g == 0.


def test_margin_at_danger_boundary_is_fully_engaged():
  # 위험거리 경계(gap + 정지환산거리 = 0.8 * 쾌적거리) 이하에서는 g = 1
  v_ego, v_lead = 20., 10.
  d_comf = v_ego ** 2 / (2 * COMFORT_BRAKE) + T_FOLLOW * v_ego + STOP_DISTANCE
  gap = 0.8 * d_comf - v_lead ** 2 / (2 * COMFORT_BRAKE)
  g, m = raw(v_ego, v_lead, gap)
  assert m == pytest.approx(1.0)
  assert g == 1.0
  assert raw(v_ego, v_lead, gap * 0.8)[0] == 1.0


def test_margin_band_is_linear_between_lo_and_hi():
  v = 20.
  d_comf = v ** 2 / (2 * COMFORT_BRAKE) + T_FOLLOW * v + STOP_DISTANCE
  gap = 1.1 * 0.8 * d_comf - v ** 2 / (2 * COMFORT_BRAKE)   # m = 1.1 (밴드 중간), 접근 없음(TTC 성분 0)
  g, m = raw(v, v, gap)
  assert m == pytest.approx(1.1)
  assert g == pytest.approx(0.5)


def test_ttc_component_engages_even_when_margin_is_large():
  # 거리 여유가 커도(m>=1.2) 빠른 접근(TTC<=6s)이면 g = 1
  # 정지 리드(vLead=0)에 vEgo=10으로 접근: gap 55m -> m ~ 1.7(여유 충분)이지만 TTC = 5.5s
  g, m = raw(10., 0., 55.)
  assert m > 1.2
  assert g == 1.0
  # TTC 12s 이상이면 TTC 성분 없음(gap 130m -> TTC 13s)
  g2, m2 = raw(10., 0., 130.)
  assert m2 > 1.2 and g2 == 0.


def test_gate_uses_tfollow_and_comfort_brake_passed_in():
  v = 20.
  gap = steady_gap(v)
  assert raw(v, v, gap, T_FOLLOW)[0] == 0.
  # 더 긴 tFollow를 요구하면 같은 gap이 위험 쪽이 됨
  assert raw(v, v, gap, 2.5)[0] > 0.


def lead(d, v, a=-0.5, tau=1.5):
  return NS(status=True, dRel=d, vLead=v, aLeadK=a, aLeadTau=tau)


def test_process_lead_relaxes_aleadtau_when_far_and_keeps_it_when_close():
  ns, M, self = make(20.)
  self._gate_g[:] = 0.
  far = lead(steady_gap(20.) + 20., 20.)
  M.process_lead(self, far, 0)
  assert self._gate_g[0] == 0.
  # 위험 상황: 즉시 g=1 (상승은 즉시)
  d_comf = 20. ** 2 / (2 * COMFORT_BRAKE) + T_FOLLOW * 20. + STOP_DISTANCE
  near = lead(0.8 * d_comf - 20. ** 2 / (2 * COMFORT_BRAKE) - 1., 20.)
  M.process_lead(self, near, 0)
  assert self._gate_g[0] == 1.0


def test_process_lead_release_follows_tau_g():
  ns, M, self = make(20.)
  self._gate_g[0] = 1.0
  far = lead(steady_gap(20.) + 20., 20.)
  M.process_lead(self, far, 0)
  assert self._gate_g[0] == pytest.approx(1.0 - DT / ns["GATE_TAU_G"])   # g_raw=0 -> 1 + (0-1)*dt/tau


def test_process_lead_without_lead_resets_gate():
  ns, M, self = make(20.)
  self._gate_g[:] = 0.3
  M.process_lead(self, NS(status=False), 0)
  assert self._gate_g[0] == 1.0 and self._gate_g[1] == 0.3
