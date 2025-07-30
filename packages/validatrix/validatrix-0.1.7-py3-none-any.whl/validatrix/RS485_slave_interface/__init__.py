"""
RS485 slave Interface module for Validatrix.
Provides functionality for RS485 slave emulation
"""

from .RS485_slave import *
from .RS485_slave_server import *
from .RS485_device_data import *

__all__ = [
    'RS485_slave_class',
    'RS485_slave_server_class',
] 