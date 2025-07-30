# This Source Code Form is subject to the terms of the Mozilla Public
# License, v. 2.0. If a copy of the MPL was not distributed with this
# file, You can obtain one at https://mozilla.org/MPL/2.0/.

# vim: set filetype=python
import importlib
from collections import defaultdict

# Debug information for the tools required
_cython_build_version = """Cython version 3.1.1"""
_numpy_build_version = """2.0.2"""

_cc = """/opt/rh/devtoolset-10/root/usr/bin/gcc"""
_cc_version = """10.2.1"""
_cflags = """"""

_fc = """/opt/rh/devtoolset-10/root/usr/bin/gfortran"""
_fc_version = """10.2.1"""
_fflags = """"""

_definitions = """NPY_NO_DEPRECATED_API=NPY_1_20_API_VERSION CYTHON_NO_PYINIT_EXPORT=1"""

_cmake_args = [
    ("CMAKE_VERSION", """4.0.0"""),
    ("CMAKE_BUILD_TYPE", """Release"""),
    ("WITH_FORTRAN", """ON"""),
    ("F2PY_REPORT_ON_ARRAY_COPY", """10"""),
    ("WITH_F2PY_REPORT_COPY", """OFF"""),
    ("WITH_F2PY_REPORT_EXIT", """OFF"""),
    ("WITH_COVERAGE", """OFF"""),
    ("WITH_LINE_DIRECTIVES", """OFF"""),
    ("WITH_ANNOTATE", """OFF"""),
    ("WITH_GDB", """OFF"""),
    ("NO_COMPILATION", """"""),
]

def _print_fmt(*args, fmt:str ="{0:30s}{1}") -> None:
    if len(args) == 1:
        print(args[0])
    else:
        print(fmt.format(*args))


def print_dependencies() -> None:
    """Print the dependencies of sisl (will import it) """

    print("[sisl.dependencies]")

    # Get Python requirements (for this version)
    metadata = importlib.metadata.metadata("sisl")
    py_reqs = metadata["Requires-Python"].split(",")
    _print_fmt("python", ", ".join(py_reqs))

    requires = importlib.metadata.requires("sisl")

    # Create condensed form with different `extra` segments
    extras = defaultdict(list)
    for req in requires:
        reqs = list(map(str.strip, req.split(";")))
        if len(reqs) == 2:
            package, extra = reqs
        else:
            package, extra = reqs, "extra == ."
        extra = extra.split("==")[1].strip().replace('"', '')
        extras[extra].append(package)

    def print_packages(packages):
        for package in sorted(packages):
            if isinstance(package, list):
                if len(package) == 1:
                    _print_fmt("", package[0])
                else:
                    _print_fmt("", ", ".join(package))
            else:
                _print_fmt("", package)

    print_packages(extras.pop("."))
    for key in extras:
        print(f"[sisl.dependencies.{key}]")
        print_packages(extras[key])

    try:
        scripts = importlib.metadata.entry_points(group="console_scripts")

        print("[sisl.console_scripts]")
        for script in scripts:
            if script.module.startswith("sisl."):
                _print_fmt(script.name, script.value)

        print("[sisl_toolbox.console_scripts]")
        for script in scripts:
            if script.module.startswith("sisl_toolbox."):
                _print_fmt(script.name, script.value)

    except:
        pass


def print_debug_info() -> None:
    """Write (to stdout) the debug information gathered by the installed debug script."""
    from pathlib import Path
    import sys

    print("[sys]")
    _print_fmt("python_version", sys.version)
    # We import it like this to ensure there are no import errors
    # with sisl, this might be problematic, however, it should at least
    # provide consistent information
    import sisl._version as sisl_version

    print("[sisl]")
    _print_fmt("version", sisl_version.__version__)
    path = Path(sisl_version.__file__)
    _print_fmt("path", str((path / "..").resolve()))

    def print_attr(module, attr: str = ""):
        attr_val = None
        try:
            mod = importlib.import_module(module)
            if attr:
                attr_val = getattr(mod, attr)
                _print_fmt(module, attr_val)
        except BaseException as e:
            _print_fmt(module, "not found")
            _print_fmt("", str(e))

        return attr_val

    # regardless of whether it is on, or not, we try to import fortran extension
    print_attr("sisl.io.siesta._siesta")

    _print_fmt("CC", _cc)
    _print_fmt("CFLAGS", _cflags)
    _print_fmt("C version", _cc_version)
    _print_fmt("FC", _fc)
    _print_fmt("FFLAGS", _fflags)
    _print_fmt("FC version", _fc_version)
    _print_fmt("cython build version", _cython_build_version)
    _print_fmt("numpy build version", _numpy_build_version)

    print("[sisl.definitions]")
    for df in _definitions.split():
        try:
            name, value = df.split("=", 1)
            _print_fmt(name, value)
        except ValueError:
            _print_fmt(df, "")

    print("[sisl.cmake_args]")
    for d, v in _cmake_args:
        _print_fmt(d, v)

    print("[sisl.env]")
    from sisl._environ import SISL_ENVIRON, get_environ_variable

    for envvar in SISL_ENVIRON:
        _print_fmt(envvar, get_environ_variable(envvar))

    print_dependencies()

    print("[runtime]")

    pip_install = []
    conda_install = []
    for pip, conda, mod in (
        ("numpy", "numpy", "numpy"),
        ("scipy", "scipy", "scipy"),
        ("xarray", "xarray", "xarray"),
        ("netCDF4", "netCDF4", "netCDF4"),
        ("pandas", "pandas", "pandas"),
        ("matplotlib", "matplotlib", "matplotlib"),
        ("dill", "dill", "dill"),
        ("pathos", "pathos", "pathos"),
        ("scikit-image", "scikit-image", "skimage"),
        ("plotly", "plotly", "plotly"),
        ("ase", "ase", "ase"),
        ("pymatgen", "pymatgen", "pymatgen"),
    ):
        attr = print_attr(mod, "__version__")
        if attr is not None:
            pip_install.append(f"{pip}=={attr}")
            conda_install.append(f"{conda}=={attr}")

    print("[install]")
    _print_fmt("pip install", " ".join(pip_install))
    _print_fmt("conda install -c conda-forge", " ".join(conda_install))
