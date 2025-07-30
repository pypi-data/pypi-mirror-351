"""
Exceptions for the dwdpollen package.
"""


class DwdPollenError(Exception):
    """Base exception for dwdpollen package."""


class DwdPollenApiError(DwdPollenError):
    """Exception raised for errors in the API requests."""


class DwdPollenDataError(DwdPollenError):
    """Exception raised for errors in the data processing."""
