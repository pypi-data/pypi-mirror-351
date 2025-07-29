set(OPENJPEG_TAG  openjpeg-2.5)

ExternalProject_Add(openjpeg
    GIT_REPOSITORY "https://github.com/ningfei/openjpeg.git"
    GIT_TAG "${OPENJPEG_TAG}"
    SOURCE_DIR openjpeg
    BINARY_DIR openjpeg-build
    CMAKE_ARGS
        -Wno-dev
        --no-warn-unused-cli
        -DCMAKE_BUILD_TYPE=${CMAKE_BUILD_TYPE}
        -DCMAKE_OSX_ARCHITECTURES=${CMAKE_OSX_ARCHITECTURES}
        -DCMAKE_OSX_DEPLOYMENT_TARGET=${CMAKE_OSX_DEPLOYMENT_TARGET}
	    # Compiler settings
        -DCMAKE_C_COMPILER:FILEPATH=${CMAKE_C_COMPILER}
        # Install directories
        -DCMAKE_INSTALL_PREFIX:PATH=${DEP_INSTALL_DIR}
)

include(GNUInstallDirs)
set(OpenJPEG_DIR ${DEP_INSTALL_DIR}/${CMAKE_INSTALL_LIBDIR}/cmake/${OPENJPEG_TAG})
