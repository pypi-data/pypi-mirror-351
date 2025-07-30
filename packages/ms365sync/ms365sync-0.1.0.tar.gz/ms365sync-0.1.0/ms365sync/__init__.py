"""
MS365Sync - A Python library for syncing files between Microsoft 365
SharePoint and local storage.

This library provides a simple interface to sync files between SharePoint
document libraries and local directories, with support for detecting changes
and maintaining file hierarchies.
"""

__version__ = "0.1.0"
__author__ = "Abdullah Meda"
__email__ = "abdullah@phianalytica.com"

from .sharepoint_sync import SharePointSync

__all__ = ["SharePointSync"]
