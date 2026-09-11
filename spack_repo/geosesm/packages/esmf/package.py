# Copyright Spack Project Developers. See COPYRIGHT file for details.
#
# SPDX-License-Identifier: (Apache-2.0 OR MIT)

from spack_repo.builtin.packages.esmf.package import Esmf as BuiltinEsmf
from spack_repo.builtin.packages.esmf.package import MakefileBuilder as BuiltinMakefileBuilder

from spack.package import *


class Esmf(BuiltinEsmf):
    """Override ESMF to provide 9.0.0b snapshots for GEOS testing."""

    version("9.0.0b18", commit="c12f7f42f7c6e95ede1a19c0b596f36d714620c3")
    version("9.0.0b17", commit="45870de0c59f2c79f8444dd909b2f628bce81442")

    depends_on("llvm-openmp", when="+openmp %apple-clang")


class MakefileBuilder(BuiltinMakefileBuilder):
    def setup_build_environment(self, env: EnvironmentModifications) -> None:
        super().setup_build_environment(env)

        if self.spec.satisfies("+openmp %apple-clang"):
            openmp = self.spec["llvm-openmp"]
            env.append_flags("ESMF_CXXCOMPILEOPTS", f"-I{openmp.prefix.include}")
            env.append_flags("ESMF_CXXLINKOPTS", f"-L{openmp.prefix.lib} -lomp")
            env.append_flags("ESMF_SL_LIBOPTS", f"-L{openmp.prefix.lib} -lomp")
