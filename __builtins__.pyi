# Names injected by `from spack.package import *` that shadow Python builtins.
# Declared here as Any since spack is not installed in the type-checking environment.
# Without this, ty resolves `license` as the Python builtin `_Printer` object and
# produces incorrect call-signature diagnostics.
#
# See: https://github.com/astral-sh/ruff/pull/22021
from typing import Any

license: Any
