"""Ultimate Notion provides a pythonic, high-level API for Notion

Notion-API: https://developers.notion.com/reference/intro
"""


# import
#
# try:
#     __version__ = version('pytestdornech')
# except PackageNotFoundError:  # pragma: no cover
#     __version__ = 'unknown'
# finally:
#     del version, PackageNotFoundError


# up-to-date version tag for modules installed in editable mode inspired by
# https://github.com/maresb/hatch-vcs-footgun-example/blob/main/hatch_vcs_footgun_example/__init__.py
# Define the variable '__version__':
try:

    # # If setuptools_scm is installed (e.g. in a development environment with
    # # an editable install), then use it to determine the version dynamically.
    # from setuptools_scm import get_version
    # # This will fail with LookupError if the package is not installed in
    # # editable mode or if Git is not installed.
    # __version__ = get_version(root="..\..", relative_to=__file__)

    # own developed alternative variant to hatch-vcs-fottgun overcoming problem of ignored setuptools_scm settings
    # from hatch-based pyproject.toml libraries
    from hatch.cli import hatch
    from click.testing import CliRunner
    # determine version via hatch
    __version__ = CliRunner().invoke(hatch, ["version"]).output.strip()

except (ImportError, LookupError):
    # As a fallback, use the version that is hard-coded in the file.
    try:
        from ._version import __version__  # noqa: F401
    except ModuleNotFoundError:
        # The user is probably trying to run this without having installed the
        # package, so complain.
        raise RuntimeError(
            f"Package {__package__} is not correctly installed. Please install it with pip."
        )
