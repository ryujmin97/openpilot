"""proclogd process-metadata cache stays bounded by live (pid, starttime) identities."""
import os
import types

import pytest

from openpilot.system import proclogd

MEM_KEYS = ("MemTotal:", "MemFree:", "MemAvailable:", "Buffers:", "Cached:", "Active:", "Inactive:", "Shmem:")


class FakeProc:
  def init(self, name, n):
    return [None] * n


class FakeProcLog:
  def __init__(self):
    self.mem = types.SimpleNamespace()

  def init(self, name, n):
    if name == 'procs':
      return [FakeProc() for _ in range(n)]
    return [types.SimpleNamespace() for _ in range(n)]


class FakeMsg:
  def __init__(self):
    self.procLog = FakeProcLog()


def stat(pid, starttime, name='worker'):
  # rss=0 keeps the expensive smaps path out of these tests
  return {'pid': pid, 'name': name, 'state': 'S', 'ppid': 1, 'utime': 0, 'stime': 0, 'cutime': 0, 'cstime': 0,
          'priority': 20, 'nice': 0, 'num_threads': 1, 'starttime': starttime, 'vms': 0, 'rss': 0, 'processor': 0}


def extra(pid, starttime, name='worker'):
  return {'pid': pid, 'starttime': starttime, 'name': name, 'exe': '/bin/' + name, 'cmdline': [name]}


@pytest.fixture(autouse=True)
def isolated_state(monkeypatch):
  monkeypatch.setattr(proclogd, '_proc_cache', {})
  monkeypatch.setattr(proclogd, '_smaps_cycle', 0)
  monkeypatch.setattr(proclogd, '_cpu_times', lambda: [])
  monkeypatch.setattr(proclogd, '_mem_info', lambda: dict.fromkeys(MEM_KEYS, 0))


def test_prune_drops_exited_and_reused_pids():
  proclogd._proc_cache.update({1: extra(1, 10), 2: extra(2, 20), 3: extra(3, 30)})
  proclogd._prune_proc_cache({1: 10, 3: 31})  # pid 2 exited, pid 3 was reused with a new start time
  assert set(proclogd._proc_cache) == {1}


def test_prune_with_no_live_processes_empties_cache():
  proclogd._proc_cache.update({1: extra(1, 10), 2: extra(2, 20)})
  proclogd._prune_proc_cache({})
  assert proclogd._proc_cache == {}


@pytest.mark.skipif(not os.path.isdir('/proc/self'), reason='needs procfs')
def test_start_time_change_refreshes_cached_command():
  pid = os.getpid()
  first = proclogd._get_proc_extra(pid, 'python', 100)
  first['cmdline'] = ['stale']  # what a recycled PID would still show with a PID-only cache
  assert proclogd._get_proc_extra(pid, 'python', 100)['cmdline'] == ['stale']
  refreshed = proclogd._get_proc_extra(pid, 'python', 101)
  assert refreshed['starttime'] == 101
  assert refreshed['cmdline'] != ['stale']


def test_build_message_keeps_cache_to_listed_processes(monkeypatch):
  procs = [stat(1, 10), stat(2, 20)]
  monkeypatch.setattr(proclogd, '_procs', lambda: procs)
  proclogd.build_proc_log_message(FakeMsg())
  assert set(proclogd._proc_cache) == {1, 2}

  procs[:] = [stat(2, 20), stat(3, 30)]  # pid 1 exited, pid 3 appeared
  proclogd.build_proc_log_message(FakeMsg())
  assert set(proclogd._proc_cache) == {2, 3}

  procs[:] = [stat(2, 21)]  # pid 2 reused by a new process
  proclogd.build_proc_log_message(FakeMsg())
  assert {pid: e['starttime'] for pid, e in proclogd._proc_cache.items()} == {2: 21}


def test_helper_churn_does_not_grow_cache(monkeypatch):
  procs = [stat(1, 10)]
  monkeypatch.setattr(proclogd, '_procs', lambda: procs)
  for i in range(300):
    procs[:] = [stat(1, 10), stat(1000 + i, 5000 + i, name='helper')]
    proclogd.build_proc_log_message(FakeMsg())
    assert len(proclogd._proc_cache) <= 2
