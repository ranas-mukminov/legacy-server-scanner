"""Backend package for generating vendor-specific configurations."""

from .openwrt_backend import OpenWrtBackend
from .routeros_backend import RouterOSBackend

__all__ = ['OpenWrtBackend', 'RouterOSBackend']
