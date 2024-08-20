# Copyright 2013-2023 Lawrence Livermore National Security, LLC and other
# Spack Project Developers. See the top-level COPYRIGHT file for details.
#
# SPDX-License-Identifier: (Apache-2.0 OR MIT)

from spack.package import *


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
    version("3.0.0", branch="feature/sdrabenh/gcm_v12-rc1")
    version("2.16.0", tag="v2.16.0", commit="13a12a77c279068aab252263068128323630c322", preferred=True)

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

    depends_on("cmake@3.17:", type="build")
    depends_on("ecbuild", type="build")

    depends_on("mpi")

    depends_on("blas")
    depends_on("lapack")

    # These are for MAPL AGC and stubber
    depends_on("python@3:")
    depends_on("py-pyyaml")
    depends_on("py-numpy")
    depends_on("perl")

    # Currently we are having issues with our f2py code and python 3.12 (aka meson) For now
    # we will restrict the python version to <3.12
    depends_on("python@3:3.11", when="+f2py")

    # These are similarly the dependencies of MAPL. Not sure if we'll ever use MAPL as library
    depends_on("hdf5")
    depends_on("netcdf-c")
    depends_on("netcdf-fortran")
    depends_on("esmf@8.6.1:")
    depends_on("esmf~debug", when="~debug")
    depends_on("esmf+debug", when="+debug")

    depends_on("gftl@1.14.0:")
    depends_on("gftl-shared@1.9.0:")
    depends_on("pflogger@1.15.0:")
    depends_on("fargparse@1.8.0:")

    # when using apple-clang version 15.x or newer, need to use the llvm-openmp library
    depends_on("llvm-openmp", when="%apple-clang", type=("build", "run"))

    # MAPL as library would be like:
    #  depends_on("mapl@2.46.1")
    # but we don't want to do this in general due to the speed of MAPL development
    # and the fact that it just doesn't work at the moment

    # When we move to FMS as library, we'll need to add something like this:
    depends_on("fms precision=32,64 +quad_precision ~gfs_phys +openmp +pic constants=GEOS build_type=Release +deprecated_io", when="@3: ~debug")
    depends_on("fms precision=32,64 +quad_precision ~gfs_phys +openmp +pic constants=GEOS build_type=Debug +deprecated_io", when="@3: +debug")

    # We also depend on mepo
    depends_on("mepo", type="build")

    @run_before("cmake")
    def clone_mepo(self):
        with working_dir(self.stage.source_path):
            # Now we need to run "mepo clone" which is a python script
            # that will clone the other repositories that are needed

            # First we need the path to the mepo script
            mepo = self.spec["mepo"].command

            # Note: Some of the repos used by GEOSgcm have big histories
            #       and it was found that blobless clones can save a lot of
            #       time
            mepo("clone", "--partial=blobless")

            # If we use the develop variant, we run "mepo develop GMAO_Shared GEOS_Util"
            if "+develop" in self.spec:
                mepo("develop", "GMAO_Shared", "GEOS_Util")

    def cmake_args(self):
        args = [
            self.define_from_variant("USE_F2PY", "f2py"),
            self.define("CMAKE_MODULE_PATH", self.spec["esmf"].prefix.cmake),
        ]

        # Compatibility flags for gfortran
        fflags = []
        if self.compiler.name in ["gcc", "clang", "apple-clang"]:
            fflags.append("-ffree-line-length-none")
            gfortran_major_ver = int(
                spack.compiler.get_compiler_version_output(self.compiler.fc, "-dumpversion").split(
                    "."
                )[0]
            )
            if gfortran_major_ver >= 10:
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
