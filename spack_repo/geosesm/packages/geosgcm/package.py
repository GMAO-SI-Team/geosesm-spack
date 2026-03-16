# Copyright 2013-2023 Lawrence Livermore National Security, LLC and other
# Spack Project Developers. See the top-level COPYRIGHT file for details.
#
# SPDX-License-Identifier: (Apache-2.0 OR MIT)

from spack_repo.builtin.build_systems.cmake import CMakePackage
from spack.package import *
from spack_repo.geosesm.packages.geosgcm_deps.package import GeosgcmDeps


class Geosgcm(CMakePackage, GeosgcmDeps):
    """
    GEOS Earth System Model GEOSgcm Fixture
    """

    homepage = "https://github.com/GEOS-ESM/GEOSgcm"
    url = "https://github.com/GEOS-ESM/GEOSgcm/archive/refs/tags/v11.6.3.tar.gz"
    git = "https://github.com/GEOS-ESM/GEOSgcm.git"
    list_url = "https://github.com/GEOS-ESM/GEOSgcm/tags"

    maintainers("mathomp4", "tclune")

    license("Apache-2.0", checked_by="mathomp4")

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

    depends_on("fortran", type="build")
    depends_on("c", type="build")
    depends_on("cxx", type="build")

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

    def setup_run_environment(self, env):
        # Point CMake's FindPython at the Spack-managed Python so it is
        # preferred over any system/Homebrew Python on the PATH.
        python_prefix = self.spec["python"].prefix
        env.set("Python_ROOT_DIR", python_prefix)
        env.set("Python3_ROOT_DIR", python_prefix)
