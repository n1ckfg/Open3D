#!/usr/bin/env bash
set -euo pipefail

pushd /root/Open3D
mkdir build
pushd build

# Configure
cmake -DBUILD_SHARED_LIBS=OFF \
      -DCMAKE_BUILD_TYPE=Release \
      -DBUILD_LIBREALSENSE=ON \
      -DBUILD_CUDA_MODULE=ON \
      -DBUILD_TENSORFLOW_OPS=ON \
      -DBUILD_PYTORCH_OPS=ON \
      -DBUILD_RPC_INTERFACE=OFF \
      -DCMAKE_INSTALL_PREFIX=/root/open3d_install \
      -DBUILD_UNIT_TESTS=ON \
      -DBUILD_BENCHMARKS=ON \
      -DBUILD_EXAMPLES=ON \
      ..

# Build
make -j$(nproc)
make -j$(nproc) install-pip-package

# Test, the filtered test is just to save time
CUDA_VISIBLE_DEVICES=0 ./bin/tests --gtest_filter="-*Sum*"
CUDA_VISIBLE_DEVICES=0 pytest ../python/test --ignore ../python/test/test_color_map.py

popd
popd
