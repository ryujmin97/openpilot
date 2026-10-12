"""Settings-catalogue parameters must exist in the native Params key table.

The settings server can read and write an unregistered key through a file
fallback, but every other reader (for example the live-runtime broker that
feeds the web driving view) calls Params().get(), which raises UnknownKeyName
for a key missing from params_keys.h. That left ShowPathEnd saved from the
settings UI but never seen by the driving view.
"""
import json
import re
from pathlib import Path

SETTINGS_PATH = Path(__file__).resolve().parents[3] / "carrot_settings.json"
PARAMS_KEYS_PATH = Path(__file__).resolve().parents[4] / "common" / "params_keys.h"

# Catalogue entries that still have no key in params_keys.h. Remove an entry
# when it gets registered (test_known_unregistered_entries_are_still_unregistered
# fails to remind you).
KNOWN_UNREGISTERED = {"ShowRouteInfo"}


def _registered_keys() -> set[str]:
  source = PARAMS_KEYS_PATH.read_text(encoding="utf-8")
  source = re.sub(r"/\*.*?\*/|//[^\n]*", "", source, flags=re.DOTALL)
  return set(re.findall(r'^\s*\{\s*"([^"]+)"\s*,\s*\{', source, flags=re.MULTILINE))


def _catalogue() -> dict[str, dict]:
  with SETTINGS_PATH.open(encoding="utf-8") as f:
    return {p["name"]: p for p in json.load(f)["params"]}


def test_catalogue_settings_are_registered_in_params_keys():
  missing = sorted(set(_catalogue()) - _registered_keys() - KNOWN_UNREGISTERED)
  assert not missing, f"settings missing from params_keys.h: {missing}"


def test_known_unregistered_entries_are_still_unregistered():
  assert KNOWN_UNREGISTERED <= set(_catalogue())
  assert KNOWN_UNREGISTERED.isdisjoint(_registered_keys())


def test_show_path_end_is_registered_with_the_catalogue_default():
  assert _catalogue()["ShowPathEnd"]["default"] == 1
  assert '{"ShowPathEnd", {PERSISTENT, INT, "1"}}' in PARAMS_KEYS_PATH.read_text(encoding="utf-8")
