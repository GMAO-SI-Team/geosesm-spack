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
    version("11")

    # Keep variants minimal but useful
    variant("debug", default=False, description="Match GEOSgcm debug-related deps (ESMF)")
    variant("fmsyaml", default=False, description="Pull in FMS built with YAML support (GEOS v12+)")

    # Tooling / scripting
    depends_on("cmake@3.24:", type="build")
    depends_on("python@3:", type=("build", "run"))
    depends_on("py-pyyaml", type=("build", "run"))
    depends_on("py-numpy", type=("build", "run"))
    depends_on("py-ruamel-yaml")
    depends_on("py-questionary")
    depends_on("perl", type=("build", "run"))
    depends_on("tcsh", type="run")
    depends_on("mepo", type=("build", "run"))

    # Core HPC deps
    depends_on("mpi")
    depends_on("blas")
    depends_on("lapack")

    # I/O + regridding stack (mirrors your geosgcm package)
    depends_on("hdf5 +fortran +hl +threadsafe +mpi")
    depends_on("netcdf-c")
    depends_on("netcdf-fortran")
    depends_on("esmf@8.9.1:")
    depends_on("esmf +debug", when="+debug")
    depends_on("esmf ~debug", when="~debug")

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
    depends_on("fms@2024.03 precision=32,64 ~gfs_phys +openmp +pic constants=GEOS +deprecated_io +yaml build_type=Release", when="@12: ~debug +fmsyaml")
    depends_on("fms@2024.03 precision=32,64 ~gfs_phys +openmp +pic constants=GEOS +deprecated_io ~yaml build_type=Release", when="@12: ~debug ~fmsyaml")

    depends_on("fms@2024.03 precision=32,64 ~gfs_phys +openmp +pic constants=GEOS +deprecated_io +yaml build_type=Debug", when="@12: +debug +fmsyaml")
    depends_on("fms@2024.03 precision=32,64 ~gfs_phys +openmp +pic constants=GEOS +deprecated_io ~yaml build_type=Debug", when="@12: +debug ~fmsyaml")

