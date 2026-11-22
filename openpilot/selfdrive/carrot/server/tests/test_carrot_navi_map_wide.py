from openpilot.selfdrive.carrot.server.features.carrot_navi.bridge import CarrotNaviWebBridge


class FakeParams:
  def __init__(self) -> None:
    self.writes: list[tuple[str, int]] = []

  def put_int_nonblocking(self, key: str, value: int) -> None:
    self.writes.append((key, value))


def make_bridge() -> tuple[CarrotNaviWebBridge, FakeParams]:
  bridge = CarrotNaviWebBridge(messaging_module=object())
  params = FakeParams()
  bridge._params = params
  return bridge, params


def test_map_wide_follows_last_connected_viewer() -> None:
  bridge, params = make_bridge()
  portrait, landscape = object(), object()

  bridge.set_media_map_wide(portrait, False)
  bridge.set_media_map_wide(landscape, True)
  bridge.clear_media_map_wide(landscape)

  assert params.writes == [
    ("CarrotNaviMapWide", 1),
    ("CarrotNaviMapWide", 0),
  ]


def test_map_wide_is_kept_when_last_viewer_leaves() -> None:
  bridge, params = make_bridge()
  first, second = object(), object()

  bridge.set_media_map_wide(first, True)
  bridge.clear_media_map_wide(first)
  bridge.set_media_map_wide(second, True)

  assert params.writes == [("CarrotNaviMapWide", 1)]


def test_map_wide_ignores_clear_for_unknown_viewer() -> None:
  bridge, params = make_bridge()

  bridge.clear_media_map_wide(object())

  assert params.writes == []
