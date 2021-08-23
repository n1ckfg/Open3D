@echo off

git-lfs install
git submodule update --init --recursive

rd /s /q build
mkdir build
cd build
cmake -A=x64 -D BUILD_PYTHON_MODULE=OFF -D BUILD_LIB_REALSENSE=ON ..

rem cmake --build . --config RELEASE --target ALL_BUILD
cmake --build . --config RELEASE --target INSTALL

@pause