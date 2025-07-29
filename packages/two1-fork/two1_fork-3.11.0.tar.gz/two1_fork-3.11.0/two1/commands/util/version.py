"""Utils for 21 version."""

import requests
import urllib.parse as parse
from packaging.version import parse as parse_version, Version
from distutils.version import LooseVersion
import re

import two1


def get_latest_two1_version_pypi():
    """Fetch latest version of two1 from pypi.

    Returns:
        latest_version (str): latest version of two1
    """
    url = parse.urljoin(two1.TWO1_PYPI_HOST, "pypi/two1/json")
    response = requests.get(url)
    return response.json()["info"]["version"]


def is_version_gte(actual, expected):
    """Checks two versions for actual >= expected condition

        Versions need to be in Major.Minor.Patch format.

    Args:
        actual (str): the actual version being checked
        expected (str): the expected version being checked

    Returns:
        bool: True if the actual version is greater than or equal to
            the expected version.

    Raises:
        ValueError: if expected or actual version is not in Major.Minor.Patch
            format.
    """

    def extract_base_version(version_str):
        """Extract the base version number from a version string with suffixes."""
        # Match version pattern like "3.13.0" from "3.13.0-74-generic"
        match = re.match(r"^(\d+\.\d+\.\d+)", version_str)
        if match:
            return match.group(1)
        return version_str

    try:
        # Extract base versions for comparison
        actual_base = extract_base_version(actual)
        expected_base = extract_base_version(expected)

        # Try to parse as standard versions first
        return parse_version(actual_base) >= parse_version(expected_base)
    except Exception:
        # Fall back to LooseVersion for non-standard versions
        return LooseVersion(actual) >= LooseVersion(expected)
