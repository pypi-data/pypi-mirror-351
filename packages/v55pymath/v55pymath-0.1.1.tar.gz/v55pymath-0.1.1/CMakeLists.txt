cmake_minimum_required(VERSION 3.15)
project(pymath)

set(CMAKE_CXX_STANDARD 17)

set(PYBIND11_FINDPYTHON ON)


set(pybind11_DIR "C:/projects/pymath-v2/.venv/Lib/site-packages/pybind11/share/cmake/pybind11")
find_package(pybind11 REQUIRED)

include_directories(include)

pybind11_add_module(v55pymath
    src/algebra.cpp
    src/calculus.cpp
    src/interpolation.cpp
    src/math_utils.cpp
    src/matrix.cpp
    src/montecarlo.cpp
    src/norms_metrics.cpp
    src/transforms.cpp
    src/visualization.cpp
    src/bindings.cpp
)

install(TARGETS v55pymath DESTINATION .)