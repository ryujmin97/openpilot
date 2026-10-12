#!/usr/bin/env bash
# 기준선 long_mpc.py를 모듈로 복사한다: bash prep_base.sh <기준선 커밋> [저장소 루트]
# 기준선 커밋의 파일은 `git show`로 읽으므로 저장소가 depth 1이면 먼저 `git fetch --depth 2 origin <커밋>` 등이 필요하다.
set -euo pipefail
BASE="${1:?기준선 커밋}"; ROOT="${2:-/home/claude/repo}"
git -C "$ROOT" show "$BASE:openpilot/selfdrive/controls/lib/longitudinal_mpc_lib/long_mpc.py" \
  > "$ROOT/openpilot/selfdrive/controls/lib/longitudinal_mpc_lib/long_mpc_base110.py"
wc -l "$ROOT/openpilot/selfdrive/controls/lib/longitudinal_mpc_lib/long_mpc_base110.py"
echo "끝나면 삭제: rm $ROOT/openpilot/selfdrive/controls/lib/longitudinal_mpc_lib/long_mpc_base110.py (git status를 깨끗하게)"
