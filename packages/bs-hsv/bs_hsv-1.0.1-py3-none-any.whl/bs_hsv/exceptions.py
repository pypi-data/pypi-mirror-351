"""
Custom exceptions for the HSV module.

This module defines exception classes used throughout the HSV package.
"""

class HSVError(Exception):
    """Base exception for all HSV-related errors"""
    pass


class ValidationError(HSVError):
    """Exception raised for validation errors"""
    pass


class FileError(HSVError):
    """Exception raised for file-related errors"""
    pass