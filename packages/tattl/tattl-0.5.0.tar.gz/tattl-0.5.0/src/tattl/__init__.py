"""Totally Awesome Type-Aware TOML Loader

TATTL is a library to deserialize data, particularly application configuration, while validating
types. It builds an instance of a given ``dataclass`` and checks the value of each field against its
type annotations. It supports nested ``dataclass`` structures and modern type definitions.

This is the base module for ``tattl``, and the package's functionality is available under its
various submodules.

Licensed under the BSD 3-Clause License. Copyright Theo Court and contributors.

https://github.com/thcrt/tattl


"""

from .unpack import unpack_dict

__all__ = ["unpack_dict", "__version__"]


# Define the variable '__version__':
try:
    # If setuptools_scm is installed (e.g. in a development environment with
    # an editable install), then use it to determine the version dynamically.
    from setuptools_scm import get_version as _get_version  # type: ignore

    # This will fail with LookupError if the package is not installed in
    # editable mode or if Git is not installed.
    __version__ = _get_version(root="..", relative_to=__file__)
except (ImportError, LookupError):
    # As a fallback, use the version that is hard-coded in the file.
    try:
        from ._version import __version__  # noqa: F401
    except ModuleNotFoundError:
        # The user is probably trying to run this without having installed
        # the package, so complain.
        raise RuntimeError(
            "tattl is not correctly installed. Install it with pip or uv."
        )
