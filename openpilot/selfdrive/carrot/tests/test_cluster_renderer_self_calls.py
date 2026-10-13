"""ClusterUiRenderer must not call private draw/navi helpers that are not defined.

A cleanup removed _draw_navi_round_line together with the structured
traffic-light panel it was written for, but the navi turn icon and the lane
strip still called it. pyflakes cannot see a missing self.<method>, and the
renderer needs raylib, so a plain import-and-draw test hides the problem.
This guard reads the source with ast instead, so it runs anywhere.
"""
import ast
from pathlib import Path

RENDERER_PATH = Path(__file__).resolve().parents[1] / "cluster" / "cluster_renderer.py"
RENDERER_CLASS = "ClusterUiRenderer"
CHECKED_PREFIXES = ("_draw", "_navi")


def _self_name(node: ast.AST) -> bool:
  return isinstance(node, ast.Name) and node.id == "self"


def _defined_names(cls: ast.ClassDef) -> set[str]:
  names: set[str] = set()
  for node in ast.walk(cls):
    if isinstance(node, (ast.FunctionDef, ast.AsyncFunctionDef)):
      names.add(node.name)
    targets: list[ast.AST] = []
    if isinstance(node, ast.Assign):
      targets = list(node.targets)
    elif isinstance(node, (ast.AnnAssign, ast.AugAssign)):
      targets = [node.target]
    for target in targets:
      if isinstance(target, ast.Name):
        names.add(target.id)
      elif isinstance(target, ast.Attribute) and _self_name(target.value):
        names.add(target.attr)
  return names


def _checked_self_calls(cls: ast.ClassDef) -> dict[str, list[int]]:
  calls: dict[str, list[int]] = {}
  for node in ast.walk(cls):
    if isinstance(node, ast.Call) and isinstance(node.func, ast.Attribute) and _self_name(node.func.value):
      if node.func.attr.startswith(CHECKED_PREFIXES):
        calls.setdefault(node.func.attr, []).append(node.lineno)
  return calls


def undefined_self_calls(source: str, class_name: str) -> dict[str, list[int]]:
  tree = ast.parse(source)
  cls = next(n for n in tree.body if isinstance(n, ast.ClassDef) and n.name == class_name)
  assert not cls.bases, f"{class_name} now has base classes; extend this guard to resolve inherited names"
  defined = _defined_names(cls)
  return {name: lines for name, lines in _checked_self_calls(cls).items() if name not in defined}


def test_renderer_self_calls_are_defined():
  source = RENDERER_PATH.read_text(encoding="utf-8")
  missing = undefined_self_calls(source, RENDERER_CLASS)
  assert not missing, f"{RENDERER_CLASS} calls undefined helpers (name: line numbers): {missing}"


def test_renderer_guard_is_not_vacuous():
  tree = ast.parse(RENDERER_PATH.read_text(encoding="utf-8"))
  cls = next(n for n in tree.body if isinstance(n, ast.ClassDef) and n.name == RENDERER_CLASS)
  assert len(_checked_self_calls(cls)) >= 10


def test_guard_detects_a_missing_helper():
  broken = "class R:\n  def draw(self):\n    self._draw_gone(1)\n    self._draw_here(2)\n  def _draw_here(self, x):\n    pass\n"
  assert undefined_self_calls(broken, "R") == {"_draw_gone": [3]}
  fixed = broken + "  @staticmethod\n  def _draw_gone(x):\n    pass\n"
  assert undefined_self_calls(fixed, "R") == {}
