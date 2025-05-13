# Copyright 2013-2023 Lawrence Livermore National Security, LLC and other
# Spack Project Developers. See the top-level COPYRIGHT file for details.
#
# SPDX-License-Identifier: (Apache-2.0 OR MIT)

from spack.package import *
from spack.operating_systems.mac_os import macos_cltools_version
import sys

class Geosfvdycore(CMakePackage):
    """
    GEOS Earth System Model GEOSfvdycore Fixture
    """

    homepage = "https://github.com/GEOS-ESM/GEOSfvdycore"
    url = "https://github.com/GEOS-ESM/GEOSfvdycore/archive/refs/tags/v2.16.0.tar.gz"
    git = "https://github.com/GEOS-ESM/GEOSfvdycore.git"
    list_url = "https://github.com/GEOS-ESM/GEOSfvdycore/tags"

    maintainers("mathomp4", "tclune")

    version("main", branch="main")
    #version("3.0.0", branch="feature/sdrabenh/gcm_v12")
    version("3.0.0-rc.3", tag="v3.0.0-rc.3", commit="7f4b922287a860421c145d23a13c7a2f3fc30e69", preferred=True)
    version("3.0.0-rc.2", tag="v3.0.0-rc.2", commit="c953eb6c22f3b9f8a8ebf8bc261cd80b00637880")
    version("3.0.0-rc.1", tag="v3.0.0-rc.1", commit="61a7818e4f4496a0713d721150f94e47eb8f01ac")
    # NOTE: We use tag and commit due to an issue in mepo:
    #   https://github.com/GEOS-ESM/mepo/issues/311
    # This hopefully will be fixed soon and we can move to "normal" checksum style
    version("2.23.0", tag="v2.23.0", commit="479b0bb21bc876b3ab56d2cf1de765f8b39aea2b")
    version("2.22.0", tag="v2.22.0", commit="4c6705bb205a26890a0327eeed049cbf5edf6d1a")
    version("2.21.0", tag="v2.21.0", commit="ecd01f19718de9e76fce3d5d5630d4727f67f80d")
    version("2.20.0", tag="v2.20.0", commit="c8529e55cf002b71b101c265b328155fa848c53d")
    version("2.19.1", tag="v2.19.1", commit="67e6b3915c3e0ebab20e9df29a354db8cc5e987b")
    version("2.19.0", tag="v2.19.0", commit="89ea359c91bae105d7a4a3ac2ca83421b15b5c80")
    version("2.18.0", tag="v2.18.0", commit="f86f61656a76fd02a24814167f29e7a20acf63df")

    variant("debug", default=False, description="Build with debugging")
    variant("f2py", default=False, description="Build with f2py support")
    variant(
        "develop",
        default=False,
        description="Update GMAO_Shared GEOS_Util "
        "subrepos to their develop branches (used internally for testing)",
    )

    variant(
        "build_type",
        default="Release",
        description="The build type to build",
        values=("Debug", "Release", "Aggressive"),
    )

    variant("external-mapl", default=False, description="Build with external MAPL", when="@3:")

    variant("jemalloc", default=True, description="Use jemalloc for memory allocation", when="@3:")

    depends_on("fortran", type="build")
    depends_on("c", type="build")
    depends_on("cxx", type="build")

    depends_on("cmake@3.24:", type="build")

    depends_on("mpi")

    depends_on("blas")
    depends_on("lapack")

    # These are for MAPL AGC and stubber
    depends_on("python@3:")
    depends_on("py-pyyaml")
    depends_on("py-numpy")
    depends_on("perl")

    # These are similarly the dependencies of MAPL. Not sure if we'll ever use MAPL as library
    depends_on("hdf5 +fortran +hl +threadsafe +mpi")
    depends_on("netcdf-c")
    depends_on("netcdf-fortran")
    depends_on("esmf@8.6.1:")
    depends_on("esmf ~debug", when="~debug")
    depends_on("esmf +debug", when="+debug")

    depends_on("gftl@1.14.0:")
    depends_on("gftl-shared@1.9.0:")
    depends_on("pflogger@1.15.0: +mpi")
    depends_on("fargparse@1.8.0:")

    # when using apple-clang version 15.x or newer, need to use the llvm-openmp library
    depends_on("llvm-openmp", when="%apple-clang", type=("build", "run"))

    depends_on("udunits")

    depends_on("tcsh", type="run")

    # Notice to maintainers, make sure this is the same version as in MAPL
    # that GEOSgcm has internally. Also, make sure the ESMF version above
    # is compatible with this version of MAPL
    depends_on("mapl@2.52:", when="+external-mapl")
    depends_on("mapl@2.52: +debug", when="+external-mapl +debug")

    variant("fmsyaml", default=False, description="Build FMS with YAML support")

    depends_on("fms@2024.03 precision=32 ~gfs_phys +pic constants=GEOS +deprecated_io +yaml build_type=Release", when="@3: ~debug +fmsyaml")
    depends_on("fms@2024.03 precision=32 ~gfs_phys +pic constants=GEOS +deprecated_io ~yaml build_type=Release", when="@3: ~debug ~fmsyaml")

    depends_on("fms@2024.03 precision=32 ~gfs_phys +pic constants=GEOS +deprecated_io +yaml build_type=Debug",   when="@3: +debug +fmsyaml")
    depends_on("fms@2024.03 precision=32 ~gfs_phys +pic constants=GEOS +deprecated_io ~yaml build_type=Debug",   when="@3: +debug ~fmsyaml")

    # We also depend on mepo
    depends_on("mepo", type="build")

    depends_on("jemalloc", when="+jemalloc")

    # We have only tested with gcc 13+
    conflicts("%gcc@:12")

    # If you have XCode 16.3, we require the v2.23 or v3.0.0-rc.3
    cltools_ver = macos_cltools_version()
    if sys.platform == "darwin" and cltools_ver is not None and cltools_ver >= Version("16.3"):
        conflicts("@:2.22", msg="XCode 16.3+ requires v2.23")
        conflicts("@:3.0.0-rc.2", msg="XCode 16.3+ requires v3.0.0-rc.3")

    @run_before("cmake")
    def clone_mepo(self):
        with working_dir(self.stage.source_path):
            # Now we need to run "mepo clone" which is a python package
            # that will clone the other repositories that are needed

            # First we need the path to the mepo script
            mepo = self.spec["mepo"].command

            # Note: Some of the repos used by GEOSgcm have big histories
            #       and it was found that blobless clones can save a lot of
            #       time
            mepo("clone", "--partial=blobless")

            # If we use the develop variant, we run "mepo develop GMAO_Shared GEOS_Util"
            if self.spec.satisfies("+develop"):
                mepo("develop", "GMAO_Shared", "GEOS_Util")

            # Currently, when the version is 12 or higher we also need to run:
            #  mepo checkout-if-exists feature/sdrabenh/gcm_v12
            # As this branch is still in development
            if self.spec.satisfies("@12:"):
                mepo("checkout-if-exists", "feature/sdrabenh/gcm_v12")

    def cmake_args(self):
        args = [
            self.define_from_variant("USE_F2PY", "f2py"),
            self.define_from_variant("FMS_BUILT_WITH_YAML", "fmsyaml"),
            self.define("CMAKE_MODULE_PATH", self.spec["esmf"].prefix.cmake),
        ]

        # Compatibility flags for gfortran
        fflags = []
        if self.compiler.name in ["gcc", "clang", "apple-clang"]:
            if "gfortran" in self.compiler.fc:
                fflags.append("-ffree-line-length-none")
                fflags.append("-fallow-invalid-boz")
                fflags.append("-fallow-argument-mismatch")
        if fflags:
            args.append(self.define("CMAKE_Fortran_FLAGS", " ".join(fflags)))

        # Scripts often need to know the MPI stack used to setup the environment.
        # Normally, we can autodetect this, but building with Spack does not
        # seem to work. We need to pass in the MPI stack used to CMake
        # via -DMPI_STACK on the CMake command line. We use the following
        # names for the MPI stacks:
        #
        # - MPICH --> mpich
        # - Open MPI --> openmpi
        # - Intel MPI --> intelmpi
        # - MVAPICH --> mvapich
        # - HPE MPT --> mpt
        # - Cray MPICH --> mpich

        if self.spec.satisfies("^mpich"):
            args.append(self.define("MPI_STACK", "mpich"))
        elif self.spec.satisfies("^openmpi"):
            args.append(self.define("MPI_STACK", "openmpi"))
        elif self.spec.satisfies("^intel-oneapi-mpi"):
            args.append(self.define("MPI_STACK", "intelmpi"))
        elif self.spec.satisfies("^mvapich"):
            args.append(self.define("MPI_STACK", "mvapich"))
        elif self.spec.satisfies("^mpt"):
            args.append(self.define("MPI_STACK", "mpt"))
        elif self.spec.satisfies("^cray-mpich"):
            args.append(self.define("MPI_STACK", "mpich"))
        else:
            raise InstallError("Unsupported MPI stack")

        return args

    def setup_build_environment(self, env):
        # esma_cmake, an internal dependency of mapl, is
        # looking for the cmake argument -DBASEDIR, and
        # if it doesn't find it, it's looking for an
        # environment variable with the same name. This
        # name is common and used all over the place,
        # and if it is set it breaks the mapl build.
        env.unset("BASEDIR")

