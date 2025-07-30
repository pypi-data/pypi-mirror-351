# -*- coding: utf-8 -*-
"""
OpenAlgo Python Library
"""

from .orders import OrderAPI
from .data import DataAPI
from .account import AccountAPI
from .strategy import Strategy
from .feed import FeedAPI
from .indicators import ta

class api(OrderAPI, DataAPI, AccountAPI, FeedAPI):
    """
    OpenAlgo API client class
    """
    pass

__version__ = "1.0.14"

# Export main components for easy access
__all__ = ['api', 'Strategy', 'ta']
