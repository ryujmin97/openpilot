#!/usr/bin/env bash
# devnotes/toolkit/pytest_ci_setup.sh (124~125차)
#
# carrot-ryu(ryujmin97/openpilot)를 conftest.py 포함 실제 pytest CI 조건으로
# 돌리기 위한 샌드박스 환경 구성 스크립트. Claude 컨테이너(Ubuntu 24, Python
# 3.12, root, apt/pip 가능, /home/claude 쓰기 가능)에서만 검증됨 -- 콤마
# 디바이스나 사용자 PC용이 아니다. 파일시스템은 대화(세션)마다 초기화되므로
# pytest를 다시 돌리려면 매번 이 스크립트부터 다시 실행해야 한다.
#
# 배경: 96차 이전까지는 "샌드박스에 conftest/컴파일 의존성이 없어 pytest
# 미실시"로 기록돼 있었으나(92차 등), 124차에서 실제로는 이 의존성들이
# apt/pip로 전부 설치 가능하고 acados 코드생성까지 포함해 컴파일 가능함이
# 확인됐다. 이 스크립트는 그 재현 절차를 그대로 기록한 것이다.
#
# 실행: bash pytest_ci_setup.sh [branch]  (기본 branch=carrot-ryu)
# 이후: cd /home/claude/repo && export PYTHONPATH=/home/claude/repo:/home/claude/repo/opendbc_repo
#       python3 -m pytest <경로...>
#
# 주의: opendbc의 일부 차량 DBC(예: toyota_new_mc_pt_generated.dbc,
# nissan_leaf_2018_generated.dbc)는 opendbc_repo/opendbc/dbc/generator/에서
# 별도 생성 단계가 더 필요해 이 스크립트만으로는 없다(124차에 발견, 미해결).
# 그 DBC를 쓰는 차량의 CarInterface를 생성하는 테스트는 이 상태로는 실패한다.

set -euo pipefail
BRANCH="${1:-carrot-ryu}"
ROOT=/home/claude/repo

echo "=== [1/6] clone (${BRANCH}) ==="
rm -rf "$ROOT"
git clone --depth 1 --branch "$BRANCH" --config core.autocrlf=false \
  https://github.com/ryujmin97/openpilot.git "$ROOT"
cd "$ROOT"

echo "=== [2/6] apt (capnproto/libzmq) ==="
apt-get update >/dev/null 2>&1 || true
apt-get install -y capnproto libcapnp-dev libzmq3-dev >/dev/null

echo "=== [3/6] pip (Cython/pycapnp/comma-deps-*/기타 런타임 의존성) ==="
pip install --break-system-packages -q \
  Cython pycapnp==2.1.0 \
  comma-deps-json11==20170411.0.post103 \
  comma-deps-acados==0.2.2.post103 \
  pyzmq zstandard sympy crcmod-plus tqdm msgpack cffi requests pyserial \
  sounddevice setproctitle psutil pycryptodome PyJWT json-rpc \
  websocket_client sentry-sdk xattr qrcode jeepney inputs av aiohttp aiortc \
  libusb1 pyusb \
  pytest pytest-randomly pytest-xdist pytest-timeout pytest-asyncio pytest-cpp

echo "=== [4/6] cereal capnp C++ 헤더 생성 (SConscript와 동일 커맨드) ==="
mkdir -p openpilot/cereal/gen/cpp
(cd openpilot/cereal && capnpc \
  --src-prefix=. --src-prefix=../../opendbc_repo/opendbc/car \
  --import-path=../../opendbc_repo/opendbc/car \
  log.capnp deprecated.capnp custom.capnp ../../opendbc_repo/opendbc/car/car.capnp \
  -o c++:gen/cpp/)

echo "=== [5/6] openpilot.common.params_pyx 컴파일 (Cython/C++ 확장) ==="
cat > /tmp/build_params.py << 'PYEOF'
from setuptools import setup, Extension
from Cython.Build import cythonize
JSON11 = "/usr/local/lib/python3.12/dist-packages/json11/install"
ext = Extension(
    "openpilot.common.params_pyx",
    sources=["openpilot/common/params_pyx.pyx", "openpilot/common/params.cc",
             "openpilot/common/util.cc", "openpilot/common/swaglog.cc"],
    language="c++",
    include_dirs=[".", "openpilot", "openpilot/cereal/gen/cpp", f"{JSON11}/include"],
    library_dirs=[f"{JSON11}/lib"],
    libraries=["zmq", "json11"],
    extra_compile_args=["-std=c++17"],
)
setup(name="params_pyx_build", packages=[],
      ext_modules=cythonize([ext], language_level=3),
      script_args=["build_ext", "--inplace"])
PYEOF
python3 /tmp/build_params.py

echo "=== [5b/6] msgq.ipc_pyx 컴파일 (conftest.py가 import) ==="
cat > /tmp/build_msgq.py << 'PYEOF'
from setuptools import setup, Extension
from Cython.Build import cythonize
ext = Extension(
    "msgq.ipc_pyx",
    sources=["msgq_repo/msgq/ipc_pyx.pyx", "msgq_repo/msgq/ipc.cc",
             "msgq_repo/msgq/event.cc", "msgq_repo/msgq/impl_msgq.cc",
             "msgq_repo/msgq/impl_fake.cc", "msgq_repo/msgq/msgq.cc"],
    language="c++", include_dirs=["msgq_repo"], libraries=["pthread"],
    extra_compile_args=["-std=c++17"],
)
setup(name="msgq_build", packages=[],
      ext_modules=cythonize([ext], language_level=3),
      script_args=["build_ext", "--inplace"])
PYEOF
python3 /tmp/build_msgq.py

echo "=== [6/6] long_mpc.py용 acados OCP solver 코드생성 + 컴파일 ==="
LMPC_DIR="$ROOT/openpilot/selfdrive/controls/lib/longitudinal_mpc_lib"
ACADOS_DIR=/usr/local/lib/python3.12/dist-packages/acados/install
export ACADOS_SOURCE_DIR="$ACADOS_DIR"
export ACADOS_PYTHON_INTERFACE_PATH=/usr/local/lib/python3.12/dist-packages/acados/acados_template
export TERA_PATH="$ACADOS_DIR/bin/t_renderer"
export PYTHONPATH="$ROOT:$ROOT/opendbc_repo"
(cd "$LMPC_DIR" && python3 long_mpc.py)

GEN="$LMPC_DIR/c_generated_code"
for lib in libacados.so libblasfeo.so libhpipm.so libqpOASES_e.so.3.1; do
  cp "$ACADOS_DIR/lib/$lib" "$GEN/"
done
ln -sf libqpOASES_e.so.3.1 "$GEN/libqpOASES_e.so"

BUILD_FILES="acados_solver_long.c long_model/long_expl_ode_fun.c long_model/long_expl_vde_forw.c \
long_cost/long_cost_y_fun.c long_cost/long_cost_y_fun_jac_ut_xt.c long_cost/long_cost_y_hess.c \
long_cost/long_cost_y_e_fun.c long_cost/long_cost_y_e_fun_jac_ut_xt.c long_cost/long_cost_y_e_hess.c \
long_cost/long_cost_y_0_fun.c long_cost/long_cost_y_0_fun_jac_ut_xt.c long_cost/long_cost_y_0_hess.c \
long_constraints/long_constr_h_fun.c long_constraints/long_constr_h_fun_jac_uxt_zt.c"
(cd "$GEN" && gcc -shared -fPIC -DACADOS_WITH_QPOASES -Wno-unused \
  -I"$ACADOS_DIR/include" -I"$ACADOS_DIR/include/acados" \
  -I"$ACADOS_DIR/include/blasfeo/include" -I"$ACADOS_DIR/include/hpipm/include" \
  -I"$ACADOS_DIR/include/qpOASES_e/include" \
  -I. -I long_model -I long_cost -I long_constraints \
  $BUILD_FILES -L. -lm -lacados -lhpipm -lblasfeo -lqpOASES_e \
  -Wl,-rpath,'$ORIGIN' -Wl,--disable-new-dtags \
  -o libacados_ocp_solver_long.so)

NPINC=$(python3 -c "import numpy; print(numpy.get_include())")
TEMPLATE_DIR=/usr/local/lib/python3.12/dist-packages/acados/acados_template
cython -o "$GEN/acados_ocp_solver_pyx.c" -I "$GEN" -I "$TEMPLATE_DIR" \
  "$TEMPLATE_DIR/acados_ocp_solver_pyx.pyx"
(cd "$GEN" && gcc -shared -fPIC -DACADOS_WITH_QPOASES -Wno-unused \
  -I"$ACADOS_DIR/include" -I"$ACADOS_DIR/include/acados" \
  -I"$ACADOS_DIR/include/blasfeo/include" -I"$ACADOS_DIR/include/hpipm/include" \
  -I/usr/include/python3.12 -I"$NPINC" -I. \
  acados_ocp_solver_pyx.c -L. -lacados_ocp_solver_long \
  -Wl,-rpath,'$ORIGIN' -o acados_ocp_solver_pyx.so)
touch "$GEN/__init__.py"

echo "=== 검증 ==="
python3 -c "
import sys
from openpilot.common.params import Params
p = Params('/tmp/paramstest'); p.put_int('LongitudinalPersonality', 2)
assert p.get_int('LongitudinalPersonality') == 2
from opendbc.car.interfaces import ACCEL_MIN
from openpilot.selfdrive.controls.lib.longitudinal_mpc_lib.long_mpc import LongitudinalMpc
LongitudinalMpc()
print('OK: params_pyx / msgq / acados long_mpc 전부 정상 import+instantiate')
"
echo "=== 완료: cd $ROOT && export PYTHONPATH=$ROOT:$ROOT/opendbc_repo && python3 -m pytest <경로...> ==="
