"""Backend package for generating vendor-specific configurations."""

from .routeros_backend import RouterOSBackend
from .openwrt_backend import OpenWrtBackend

__all__ = ['RouterOSBackend', 'OpenWrtBackend']
