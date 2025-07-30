"""
Core coffee shop finding functionality
"""

import requests
import os
from typing import List, Optional
from .models import CoffeeShop, Location, SearchResult
from .location import LocationService


class CoffeeShopFinder:
    """Main service for finding coffee shops"""
    
    # Common chain coffee shops to filter out
    CHAIN_COFFEE_SHOPS = {
        'starbucks', 'dunkin', 'dunkin donuts', 'mcdonalds', 'mcdonald\'s',
        'tim hortons', 'costa coffee', 'peet\'s coffee', 'caribou coffee',
        'panera bread', 'panera', 'subway', 'seven eleven', '7-eleven',
        'wawa', 'sheetz', 'circle k', 'speedway', 'shell', 'bp', 'exxon',
        'chevron', 'mobil', 'texaco', 'valero', 'marathon'
    }
    
    def __init__(self, api_key: Optional[str] = None):
        """
        Initialize the coffee shop finder
        
        Args:
            api_key: Google Places API key (optional, can be set via environment)
        """
        self.api_key = api_key or os.getenv('GOOGLE_PLACES_API_KEY')
        self.location_service = LocationService()
        self.base_url = "https://places.googleapis.com/v1/places:searchNearby"
    
    def search_nearby(
        self, 
        location: Location, 
        radius_km: float = 2.0,
        max_results: int = 10,
        min_rating: Optional[float] = None,
        exclude_chains: bool = False
    ) -> SearchResult:
        """
        Search for coffee shops near a location
        
        Args:
            location: Location to search around
            radius_km: Search radius in kilometers
            max_results: Maximum number of results to return
            min_rating: Minimum rating filter (e.g., 4.0 for >4 stars)
            exclude_chains: Whether to exclude chain coffee shops
            
        Returns:
            SearchResult containing found coffee shops
        """
        coffee_shops = []
        
        if self.api_key:
            # Use Google Places API if available
            coffee_shops = self._search_google_places(location, radius_km, max_results * 2)  # Get more to filter
        # If no API key, return empty results
        
        # Apply filters
        if exclude_chains:
            coffee_shops = self._filter_chains(coffee_shops)
        
        if min_rating:
            coffee_shops = self._filter_by_rating(coffee_shops, min_rating)
        
        # Calculate distances and sort by rating (highest first), then distance
        for shop in coffee_shops:
            shop.distance = self.location_service.calculate_distance(location, shop.location)
        
        # Sort by rating (highest first), then by distance (closest first)
        # Handle None ratings by treating them as 0
        coffee_shops.sort(key=lambda x: (-(x.rating or 0), x.distance or float('inf')))
        
        return SearchResult(
            query_location=location,
            coffee_shops=coffee_shops[:max_results],
            total_results=len(coffee_shops),
            search_radius_km=radius_km
        )
    
    def _filter_chains(self, coffee_shops: List[CoffeeShop]) -> List[CoffeeShop]:
        """
        Filter out chain coffee shops
        
        Args:
            coffee_shops: List of coffee shops to filter
            
        Returns:
            Filtered list without chain coffee shops
        """
        filtered_shops = []
        for shop in coffee_shops:
            shop_name_lower = shop.name.lower()
            is_chain = any(chain in shop_name_lower for chain in self.CHAIN_COFFEE_SHOPS)
            if not is_chain:
                filtered_shops.append(shop)
        return filtered_shops
    
    def _filter_by_rating(self, coffee_shops: List[CoffeeShop], min_rating: float) -> List[CoffeeShop]:
        """
        Filter coffee shops by minimum rating
        
        Args:
            coffee_shops: List of coffee shops to filter
            min_rating: Minimum rating threshold
            
        Returns:
            Filtered list with only highly-rated coffee shops
        """
        return [shop for shop in coffee_shops if shop.rating and shop.rating >= min_rating]
    
    def _search_google_places(
        self, 
        location: Location, 
        radius_km: float, 
        max_results: int
    ) -> List[CoffeeShop]:
        """
        Search using Google Places API (New)
        
        Args:
            location: Location to search around
            radius_km: Search radius in kilometers
            max_results: Maximum number of results
            
        Returns:
            List of CoffeeShop objects
        """
        try:
            # Convert km to meters for Google Places API
            radius_m = int(radius_km * 1000)
            
            # Prepare request body for new Places API
            request_body = {
                "includedTypes": ["cafe", "coffee_shop"],
                "maxResultCount": min(max_results, 20),  # API limit is 20
                "locationRestriction": {
                    "circle": {
                        "center": {
                            "latitude": location.latitude,
                            "longitude": location.longitude
                        },
                        "radius": radius_m
                    }
                }
            }
            
            # Prepare headers
            headers = {
                'Content-Type': 'application/json',
                'X-Goog-Api-Key': self.api_key,
                'X-Goog-FieldMask': 'places.displayName,places.formattedAddress,places.location,places.rating,places.priceLevel,places.nationalPhoneNumber,places.id,places.regularOpeningHours'
            }
            
            response = requests.post(self.base_url, json=request_body, headers=headers)
            response.raise_for_status()
            data = response.json()
            
            coffee_shops = []
            for place in data.get('places', []):
                shop = self._parse_google_place(place)
                if shop:
                    coffee_shops.append(shop)
            
            return coffee_shops
            
        except Exception as e:
            print(f"Error searching Google Places: {e}")
            return []
    
    def _parse_google_place(self, place: dict) -> Optional[CoffeeShop]:
        """
        Parse a Google Places API (New) result into a CoffeeShop object
        
        Args:
            place: Google Places API place result
            
        Returns:
            CoffeeShop object or None if parsing fails
        """
        try:
            location_data = place.get('location', {})
            
            if not location_data:
                return None
            
            location = Location(
                latitude=location_data['latitude'],
                longitude=location_data['longitude']
            )
            
            # Extract display name
            display_name = place.get('displayName', {})
            name = display_name.get('text', 'Unknown') if display_name else 'Unknown'
            
            # Extract opening hours
            opening_hours = []
            regular_hours = place.get('regularOpeningHours', {})
            if regular_hours and 'weekdayDescriptions' in regular_hours:
                opening_hours = regular_hours['weekdayDescriptions']
            
            return CoffeeShop(
                name=name,
                address=place.get('formattedAddress', 'Address not available'),
                location=location,
                rating=place.get('rating'),
                price_level=self._convert_price_level(place.get('priceLevel')),
                phone=place.get('nationalPhoneNumber'),
                opening_hours=opening_hours,
                place_id=place.get('id')
            )
            
        except Exception as e:
            print(f"Error parsing place data: {e}")
            return None
    
    def _convert_price_level(self, price_level_str: Optional[str]) -> Optional[int]:
        """
        Convert new API price level string to integer
        
        Args:
            price_level_str: Price level string from new API
            
        Returns:
            Integer price level (1-4) or None
        """
        if not price_level_str:
            return None
        
        price_mapping = {
            'PRICE_LEVEL_INEXPENSIVE': 1,
            'PRICE_LEVEL_MODERATE': 2,
            'PRICE_LEVEL_EXPENSIVE': 3,
            'PRICE_LEVEL_VERY_EXPENSIVE': 4
        }
        
        return price_mapping.get(price_level_str) 