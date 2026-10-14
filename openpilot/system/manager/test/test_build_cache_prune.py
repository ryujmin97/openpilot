"""Exercise the production cache pruning of build.py without importing device-only modules."""
import ast
import os
from pathlib import Path

import pytest


@pytest.fixture
def cache_funcs():
  path = Path(__file__).parents[1] / 'build.py'
  tree = ast.parse(path.read_text(encoding='utf-8'))
  names = {'prunable_cache_files', 'prune_cache'}
  definitions = [n for n in tree.body if isinstance(n, ast.FunctionDef) and n.name in names]
  assert {d.name for d in definitions} == names
  namespace = {'Path': Path, 'MAX_CACHE_SIZE': 0}
  exec(compile(ast.Module(body=definitions, type_ignores=[]), str(path), 'exec'), namespace)
  return namespace


def write(path: Path, size: int, mtime: int) -> Path:
  path.parent.mkdir(parents=True, exist_ok=True)
  path.write_bytes(b'x' * size)
  os.utime(path, (mtime, mtime))
  return path


def test_only_bucket_files_are_prunable(tmp_path, cache_funcs):
  buckets = [write(tmp_path / 'ab' / 'obj1', 10, 100), write(tmp_path / '0f' / 'obj2', 10, 200)]
  # SCons config/lock and the Params stamp live at the top level; other
  # directory names are not two-character cache buckets.
  for name in ('config', 'config.lock', 'carrot_params_keys.sha256'):
    write(tmp_path / name, 5, 1)
  write(tmp_path / 'abc' / 'not_a_bucket', 5, 1)
  (tmp_path / 'cd' / 'nested').mkdir(parents=True)
  assert sorted(cache_funcs['prunable_cache_files'](tmp_path)) == sorted(buckets)


def test_missing_or_non_directory_cache_has_nothing_to_prune(tmp_path, cache_funcs):
  not_a_dir = write(tmp_path / 'plain_file', 1, 1)
  assert cache_funcs['prunable_cache_files'](tmp_path / 'missing') == []
  assert cache_funcs['prunable_cache_files'](not_a_dir) == []
  cache_funcs['prune_cache'](tmp_path / 'missing')


def test_prune_removes_oldest_bucket_files_and_keeps_top_level_stamp(tmp_path, cache_funcs):
  stamp = write(tmp_path / 'carrot_params_keys.sha256', 10, 1)  # oldest file in the cache
  config = write(tmp_path / 'config', 10, 2)
  buckets = [write(tmp_path / 'aa' / 'o1', 100, 1000), write(tmp_path / 'bb' / 'o2', 100, 2000),
             write(tmp_path / 'cc' / 'o3', 100, 3000), write(tmp_path / 'dd' / 'o4', 100, 4000)]
  cache_funcs['MAX_CACHE_SIZE'] = 250
  cache_funcs['prune_cache'](tmp_path)
  assert [p.exists() for p in buckets] == [False, False, True, True]
  assert stamp.exists() and config.exists()


def test_prune_does_nothing_below_the_limit(tmp_path, cache_funcs):
  files = [write(tmp_path / 'aa' / 'o1', 100, 1000), write(tmp_path / 'bb' / 'o2', 100, 2000)]
  cache_funcs['MAX_CACHE_SIZE'] = 1000
  cache_funcs['prune_cache'](tmp_path)
  assert all(p.exists() for p in files)
