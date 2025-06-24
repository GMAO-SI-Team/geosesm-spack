# Copyright 2013-2023 Lawrence Livermore National Security, LLC and other
# Spack Project Developers. See the top-level COPYRIGHT file for details.
#
# SPDX-License-Identifier: (Apache-2.0 OR MIT)

from spack.package import *


class Geosgcm(CMakePackage):
    """
    GEOS Earth System Model GEOSgcm Fixture
    """

    homepage = "https://github.com/GEOS-ESM/GEOSgcm"
    url = "https://github.com/GEOS-ESM/GEOSgcm/archive/refs/tags/v11.6.3.tar.gz"
    git = "https://github.com/GEOS-ESM/GEOSgcm.git"
    list_url = "https://github.com/GEOS-ESM/GEOSgcm/tags"

    maintainers("mathomp4", "tclune")

    version("main", branch="main")
    #version("aquaplanet", branch="feature/mathomp4/v12-spack-gcm-aquaplanet")
    #version("12.0.0", branch="feature/sdrabenh/gcm_v12")
    version("12.0.0-rc.2", tag="v12.0.0-rc.2", commit="f28b993033d9583080193bf6d2161c896bb07617")
    version("12.0.0-rc1", tag="v12.0.0-rc1", commit="b41d7d5858a511acea0d62b335ebc5755d309fe5")
    # NOTE: We use tag and commit due to an issue in mepo:
    #   https://github.com/GEOS-ESM/mepo/issues/311
    # This hopefully will be fixed soon and we can move to "normal" checksum style
    version("11.7.1", tag="v11.7.1", commit="402d26c88408e1d5a75f371a440e5a182e4338e9", preferred=True)
    version("11.7.0", tag="v11.7.0", commit="a5c504d04f0b0fc15342a65131c67b5d98e33535")
    version("11.6.3", tag="v11.6.3", commit="1bf10d3fd30ad9ee90d3400bd214d88ed763b06f")
    version("11.6.2", tag="v11.6.2", commit="fdbab3d7f32fe17bef689a1cdc5be2da71f03e5e")
    version("11.6.1", tag="v11.6.1", commit="c3a0f1b3c7ea340ed0b532e49742f410da966ec4")
    version("11.6.0", tag="v11.6.0", commit="3feaeb6695134ed04ad29079af176d104fdd73bb")

    variant("debug", default=False, description="Build with debugging")
    variant("f2py", default=False, description="Build with f2py support")
    variant(
        "develop",
        default=False,
        description="Update GEOSgcm_GridComp GEOSgcm_App GMAO_Shared GEOS_Util "
        "subrepos to their develop branches (used internally for testing)",
    )

    variant(
        "build_type",
        default="Release",
        description="The build type to build",
        values=("Debug", "Release", "Aggressive"),
    )

    variant("external-mapl", default=False, description="Build with external MAPL", when="@11.7:")

    variant("aquaplanet", default=False, description="Build with aquaplanet support (experimental)")
    #variant("aquaplanet", default=True, description="Build with aquaplanet support (experimental)", when="@aquaplanet")

    variant("jemalloc", default=False, when="@:11", description="Use jemalloc for memory allocation")
    variant("jemalloc", default=True, when="@12:", description="Use jemalloc for memory allocation")

    depends_on("fortran", type="build")
    depends_on("c", type="build")
    depends_on("cxx", type="build")

    depends_on("cmake@3.24:", type="build")

    depends_on("mpi")

    depends_on("blas")
    depends_on("lapack")

    # These are for MAPL AGC and stubber
    depends_on("python@3:", type=("build", "run"))
    depends_on("py-pyyaml", type=("build", "run"))
    depends_on("py-numpy", type=("build", "run"))
    depends_on("py-ruamel-yaml")
    depends_on("perl", type=("build", "run"))

    # We need questionary for the remapping tool
    depends_on("py-questionary")

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

    depends_on("udunits", type=("build", "run"))

    depends_on("tcsh", type="run")

    # Notice to maintainers, make sure this is the same version as in MAPL
    # that GEOSgcm has internally. Also, make sure the ESMF version above
    # is compatible with this version of MAPL
    depends_on("mapl@2.52:", when="+external-mapl")
    depends_on("mapl@2.52: +debug", when="+external-mapl +debug")

    variant("fmsyaml", default=False, description="Build FMS with YAML support")
    depends_on("fms@2024.03 precision=32,64 ~gfs_phys +openmp +pic constants=GEOS +deprecated_io +yaml build_type=Release", when="@12: ~debug +fmsyaml")
    depends_on("fms@2024.03 precision=32,64 ~gfs_phys +openmp +pic constants=GEOS +deprecated_io ~yaml build_type=Release", when="@12: ~debug ~fmsyaml")

    #depends_on("fms@2024.03 precision=32,64 ~gfs_phys +openmp +pic constants=GEOS +deprecated_io +yaml build_type=Release", when="@aquaplanet ~debug +fmsyaml")
    #depends_on("fms@2024.03 precision=32,64 ~gfs_phys +openmp +pic constants=GEOS +deprecated_io ~yaml build_type=Release", when="@aquaplanet ~debug ~fmsyaml")

    depends_on("fms@2024.03 precision=32,64 ~gfs_phys +openmp +pic constants=GEOS +deprecated_io +yaml build_type=Debug", when="@12: +debug +fmsyaml")
    depends_on("fms@2024.03 precision=32,64 ~gfs_phys +openmp +pic constants=GEOS +deprecated_io ~yaml build_type=Debug", when="@12: +debug ~fmsyaml")

    # We also depend on mepo
    depends_on("mepo", type="build")

    depends_on("jemalloc", when="+jemalloc")

    # We have only tested with gcc 13+
    conflicts("%gcc@:12")

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

            # If we build with the develop variant, we need to run
            # 'mepo develop GEOSgcm_GridComp GEOSgcm_App GMAO_Shared GEOS_Util'
            if self.spec.satisfies("+develop"):
                mepo("develop", "GEOSgcm_GridComp", "GEOSgcm_App", "GMAO_Shared", "GEOS_Util")

            # Currently, when the version is 12 or higher we also need to run:
            #  mepo checkout-if-exists feature/sdrabenh/gcm_v12
            # As this branch is still in development
            if self.spec.satisfies("@12:"):
                mepo("checkout-if-exists", "feature/sdrabenh/gcm_v12")

    def cmake_args(self):
        args = [
            self.define_from_variant("USE_F2PY", "f2py"),
            self.define_from_variant("FMS_BUILT_WITH_YAML", "fmsyaml"),
            self.define_from_variant("AQUAPLANET", "aquaplanet"),
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

