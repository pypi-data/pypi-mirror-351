set(YAML-CPP_TAG yaml-cpp-0.5.3) # version yaml-cpp-0.5.3

ExternalProject_Add(yaml-cpp
    GIT_REPOSITORY "https://github.com/ningfei/yaml-cpp.git"
    GIT_TAG "${YAML-CPP_TAG}"
    SOURCE_DIR yaml-cpp
    BINARY_DIR yaml-cpp-build
    CMAKE_ARGS
        -Wno-dev
        --no-warn-unused-cli
        -DCMAKE_BUILD_TYPE=${CMAKE_BUILD_TYPE}
        -DCMAKE_OSX_ARCHITECTURES=${CMAKE_OSX_ARCHITECTURES}
        -DCMAKE_OSX_DEPLOYMENT_TARGET=${CMAKE_OSX_DEPLOYMENT_TARGET}
	    # Compiler settings
        -DCMAKE_C_COMPILER:FILEPATH=${CMAKE_C_COMPILER}
        -DCMAKE_CXX_COMPILER:FILEPATH=${CMAKE_CXX_COMPILER}
        # Install directories
        -DCMAKE_INSTALL_PREFIX:PATH=${DEP_INSTALL_DIR}
)

set(YAML-CPP_DIR ${DEP_INSTALL_DIR}/lib/cmake/yaml-cpp)
