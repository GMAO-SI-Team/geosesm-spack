# Copyright Spack Project Developers. See COPYRIGHT file for details.
#
# SPDX-License-Identifier: (Apache-2.0 OR MIT)


from spack_repo.builtin.build_systems.bundle import BundlePackage

from spack.package import *


class GeosgcmDeps(BundlePackage):
    """Meta-package: everything needed to build GEOSgcm outside Spack."""

    homepage = "https://github.com/GEOS-ESM/GEOSgcm"

    maintainers("mathomp4")

    license("Apache-2.0", checked_by="mathomp4")

    version("12.0.0")
    version("11.10.0", preferred=True)

    variant("debug", default=False, description="Build with debugging")
    variant("f2py", default=False, description="Build with f2py support")

    variant(
        "external-mapl",
        default=False,
        description="Pull in MAPL as an external dependency",
        when="@11.7:",
    )

    # Tooling / scripting
    depends_on("cmake@3.24:", type="build")
    depends_on("python@3:", type=("build", "run"))
    depends_on("py-pyyaml", type=("build", "run"))
    depends_on("py-numpy", type=("build", "run"))
    depends_on("py-ruamel-yaml")
    ## We need questionary for the remapping tool
    depends_on("py-questionary")
    ## For MAPL ACG and stubber
    depends_on("perl", type=("build", "run"))
    depends_on("tcsh", type="run")
    depends_on("mepo", type=("build", "run"))

    # Core HPC deps
    depends_on("mpi")
    depends_on("blas")
    depends_on("lapack")

    # Base libraries
    depends_on("hdf5 +fortran +hl +threadsafe +mpi")
    depends_on("netcdf-c")
    depends_on("netcdf-fortran")
    depends_on("esmf@8.9.1:")
    depends_on("esmf ~debug", when="~debug")
    depends_on("esmf +debug", when="+debug")

    # Utility libs used by MAPL / GEOS ecosystem
    depends_on("gftl@1.14.0:")
    depends_on("gftl-shared@1.9.0:")
    depends_on("pflogger@1.15.0: +mpi")
    depends_on("fargparse@1.8.0:")
    depends_on("pfunit +mpi +fhamcrest")
    depends_on("udunits", type=("build", "run"))

    # Apple clang needs OpenMP runtime
    depends_on("llvm-openmp", when="%apple-clang", type=("build", "run"))

    # Notice to maintainers, make sure this is the same version as in MAPL
    # that GEOSgcm has internally. Also, make sure the ESMF version above
    # is compatible with this version of MAPL
    depends_on("mapl@2.67:", when="+external-mapl")
    depends_on("mapl@2.67: +debug", when="+external-mapl +debug")

    # Optional FMS feature parity with GEOS v12 dependency pins
    variant(
        "fmsyaml",
        default=False,
        description="Pull in FMS built with YAML support (GEOS v12+)",
    )
    depends_on(
        "fms@2024.03 precision=32,64 ~gfs_phys +openmp +pic constants=GEOS +deprecated_io +yaml build_type=Release", #noqa: E501
        when="@11.10: ~debug +fmsyaml",
    )
    depends_on(
        "fms@2024.03 precision=32,64 ~gfs_phys +openmp +pic constants=GEOS +deprecated_io ~yaml build_type=Release", #noqa: E501
        when="@11.10: ~debug ~fmsyaml",
    )

    depends_on(
        "fms@2024.03 precision=32,64 ~gfs_phys +openmp +pic constants=GEOS +deprecated_io +yaml build_type=Debug", #noqa: E501
        when="@11.10: +debug +fmsyaml",
    )
    depends_on(
        "fms@2024.03 precision=32,64 ~gfs_phys +openmp +pic constants=GEOS +deprecated_io ~yaml build_type=Debug", #noqa: E501
        when="@11.10: +debug ~fmsyaml",
    )

    variant(
        "jemalloc", default=False, when="@:11.9", description="Use jemalloc for memory allocation"
    )
    variant(
        "jemalloc", default=True, when="@11.10:", description="Use jemalloc for memory allocation"
    )
    depends_on("jemalloc", when="+jemalloc")

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
