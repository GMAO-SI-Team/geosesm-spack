# Copyright Spack Project Developers. See COPYRIGHT file for details.
#
# SPDX-License-Identifier: (Apache-2.0 OR MIT)


from spack_repo.builtin.build_systems.bundle import BundlePackage

from spack.package import *


class GeosgcmDeps(BundlePackage):
    """Meta-package: everything needed to build GEOSgcm outside Spack."""

    homepage = "https://github.com/GEOS-ESM/GEOSgcm"
    url = "https://github.com/GEOS-ESM/GEOSgcm/archive/refs/tags/v11.6.3.tar.gz"
    git = "https://github.com/GEOS-ESM/GEOSgcm.git"
    list_url = "https://github.com/GEOS-ESM/GEOSgcm/tags"

    maintainers("mathomp4")

    license("Apache-2.0", checked_by="mathomp4")

    version("main", branch="main")
    version("12.0.0-rc.6", tag="v12.0.0-rc.6", commit="a1ff8601b8e72fbe2511c02d0c78434c558a5c8f")
    version("12.0.0-rc.5", tag="v12.0.0-rc.5", commit="d312795ac0be53396a49e611231a7f68c2cdfcdc")
    version("12.0.0-rc.4", tag="v12.0.0-rc.4", commit="6b1698a32b58269255cd97762343bc4d21206252")
    version("12.0.0-rc.3", tag="v12.0.0-rc.3", commit="5aec9b5c5540a0226bf03feabc7a7d3f4c3c375c")
    version("12.0.0-rc.2", tag="v12.0.0-rc.2", commit="f28b993033d9583080193bf6d2161c896bb07617")
    version("12.0.0-rc1", tag="v12.0.0-rc1", commit="b41d7d5858a511acea0d62b335ebc5755d309fe5")
    version("11.8.1", tag="v11.8.1", commit="9e1778c83758cfec7b89fc701486c5fc14afdd4a", preferred=True)
    version("11.8.0", tag="v11.8.0", commit="e8e2a4727db6e64dcc55ef3f256b47acb0ae2962")
    version("11.7.3", tag="v11.7.3", commit="526adc8d19300ac3a64bf088843973b6d78d3e95")
    version("11.7.2", tag="v11.7.2", commit="ed4d529bd22f262b1ac7ff6d565abe4d2d4b0a7e")
    version("11.7.1", tag="v11.7.1", commit="402d26c88408e1d5a75f371a440e5a182e4338e9")
    version("11.7.0", tag="v11.7.0", commit="a5c504d04f0b0fc15342a65131c67b5d98e33535")
    version("11.6.3", tag="v11.6.3", commit="1bf10d3fd30ad9ee90d3400bd214d88ed763b06f")
    version("11.6.2", tag="v11.6.2", commit="fdbab3d7f32fe17bef689a1cdc5be2da71f03e5e")
    version("11.6.1", tag="v11.6.1", commit="c3a0f1b3c7ea340ed0b532e49742f410da966ec4")
    version("11.6.0", tag="v11.6.0", commit="3feaeb6695134ed04ad29079af176d104fdd73bb")

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
        "fms@2024.03 precision=32,64 ~gfs_phys +openmp +pic constants=GEOS +deprecated_io +yaml build_type=Release",
        when="@12: ~debug +fmsyaml",
    )
    depends_on(
        "fms@2024.03 precision=32,64 ~gfs_phys +openmp +pic constants=GEOS +deprecated_io ~yaml build_type=Release",
        when="@12: ~debug ~fmsyaml",
    )

    depends_on(
        "fms@2024.03 precision=32,64 ~gfs_phys +openmp +pic constants=GEOS +deprecated_io +yaml build_type=Debug",
        when="@12: +debug +fmsyaml",
    )
    depends_on(
        "fms@2024.03 precision=32,64 ~gfs_phys +openmp +pic constants=GEOS +deprecated_io ~yaml build_type=Debug",
        when="@12: +debug ~fmsyaml",
    )

    variant("jemalloc", default=False, when="@:11", description="Use jemalloc for memory allocation")
    variant("jemalloc", default=True, when="@12:", description="Use jemalloc for memory allocation")
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
