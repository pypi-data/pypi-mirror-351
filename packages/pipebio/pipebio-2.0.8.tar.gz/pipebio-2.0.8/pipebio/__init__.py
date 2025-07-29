"""
pipebio

A PipeBio client package.
"""

try:
    from importlib.metadata import version
except ImportError:
    from importlib_metadata import version  # for Python <3.8 fallback

__version__ = version("pipebio")
__author__ = 'PipeBio'
