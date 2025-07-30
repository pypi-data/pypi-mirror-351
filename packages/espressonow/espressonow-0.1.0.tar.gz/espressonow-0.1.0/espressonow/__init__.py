"""
EspressoNow - Find specialty coffee shops near you.

A Python CLI tool that uses the Google Places API to discover 
high-quality coffee shops in your area or any specified location.
"""

__version__ = "0.1.0"
__author__ = "ethanqcarter"
__email__ = "ethanqcarter@gmail.com"

from .core import CoffeeShopFinder
from .location import LocationService
from .models import Location, CoffeeShop, SearchResult

__all__ = [
    "CoffeeShopFinder",
    "LocationService", 
    "Location",
    "CoffeeShop",
    "SearchResult",
]
