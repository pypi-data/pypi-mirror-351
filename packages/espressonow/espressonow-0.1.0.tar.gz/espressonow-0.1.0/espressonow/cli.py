"""
Command Line Interface for EspressoNow
"""

import click
import os
from typing import Optional
from rich.console import Console
from rich.table import Table
from rich.panel import Panel
from rich.text import Text
from rich.progress import Progress, SpinnerColumn, TextColumn
from dotenv import load_dotenv

from .core import CoffeeShopFinder
from .location import LocationService
from .models import CoffeeShop, Location

# Load environment variables
load_dotenv()

console = Console()


def format_rating(rating: Optional[float]) -> str:
    """Format rating with stars"""
    if rating is None:
        return "No rating"
    
    stars = "⭐" * int(rating)
    return f"{stars} ({rating:.1f})"


def format_price_level(price_level: Optional[int]) -> str:
    """Format price level with dollar signs"""
    if price_level is None:
        return "No price info"
    
    return "$" * price_level


def format_distance(distance: Optional[float]) -> str:
    """Format distance"""
    if distance is None:
        return "Unknown"
    
    if distance < 1:
        return f"{distance * 1000:.0f}m"
    else:
        return f"{distance:.1f}km"


def display_coffee_shops(coffee_shops: list[CoffeeShop], location: Location):
    """Display coffee shops in a beautiful table"""
    if not coffee_shops:
        console.print("[yellow]No coffee shops found in the area.[/yellow]")
        return
    
    table = Table(title="☕ Specialty Coffee Shops Near You", show_header=True, header_style="bold magenta")
    table.add_column("Name", style="cyan", no_wrap=True)
    table.add_column("Address", style="white")
    table.add_column("Rating", justify="center")
    table.add_column("Price", justify="center")
    table.add_column("Distance", justify="right", style="green")
    table.add_column("Phone", style="blue")
    
    for shop in coffee_shops:
        table.add_row(
            shop.name,
            shop.address,
            format_rating(shop.rating),
            format_price_level(shop.price_level),
            format_distance(shop.distance),
            shop.phone or "N/A"
        )
    
    console.print(table)


@click.group()
@click.version_option(version="0.1.0", prog_name="EspressoNow")
def cli():
    """☕ EspressoNow - Find specialty coffee shops near you!"""
    pass


@cli.command()
@click.option('--radius', '-r', default=2.0, help='Search radius in kilometers (default: 2.0)')
@click.option('--max-results', '-n', default=10, help='Maximum number of results (default: 10)')
@click.option('--location', '-l', help='Search location (address or "lat,lng")')
@click.option('--api-key', help='Google Places API key (or set GOOGLE_PLACES_API_KEY env var)')
@click.option('--min-rating', type=float, help='Minimum rating (e.g., 4.0 for >4 stars)')
@click.option('--exclude-chains', is_flag=True, help='Exclude chain coffee shops (Starbucks, Dunkin, etc.)')
@click.option('--specialty-only', is_flag=True, help='Show only specialty coffee (4+ stars, no chains)')
def search(radius: float, max_results: int, location: Optional[str], api_key: Optional[str], 
          min_rating: Optional[float], exclude_chains: bool, specialty_only: bool):
    """Search for specialty coffee shops near your location"""
    
    # Handle specialty-only flag
    if specialty_only:
        min_rating = 4.0
        exclude_chains = True
    
    # Initialize services
    location_service = LocationService()
    finder = CoffeeShopFinder(api_key=api_key)
    
    # Determine search location
    search_location = None
    
    if location:
        # Parse provided location
        if ',' in location and location.replace(',', '').replace('.', '').replace('-', '').replace(' ', '').isdigit():
            # Looks like coordinates
            try:
                lat, lng = map(float, location.split(','))
                search_location = Location(latitude=lat, longitude=lng)
                console.print(f"[green]Using provided coordinates: {lat}, {lng}[/green]")
            except ValueError:
                console.print(f"[red]Invalid coordinates format: {location}[/red]")
                return
        else:
            # Treat as address
            with Progress(
                SpinnerColumn(),
                TextColumn("[progress.description]{task.description}"),
                console=console
            ) as progress:
                task = progress.add_task("Geocoding address...", total=None)
                search_location = location_service.get_location_from_address(location)
            
            if not search_location:
                console.print(f"[red]Could not find location: {location}[/red]")
                return
            
            console.print(f"[green]Found location: {location_service.format_location(search_location)}[/green]")
    else:
        # Auto-detect current location
        with Progress(
            SpinnerColumn(),
            TextColumn("[progress.description]{task.description}"),
            console=console
        ) as progress:
            task = progress.add_task("Detecting your location...", total=None)
            search_location = location_service.get_current_location()
        
        if not search_location:
            console.print("[red]Could not detect your location. Please provide a location with --location[/red]")
            return
        
        console.print(f"[green]Detected location: {location_service.format_location(search_location)}[/green]")
    
    # Search for coffee shops
    with Progress(
        SpinnerColumn(),
        TextColumn("[progress.description]{task.description}"),
        console=console
    ) as progress:
        task = progress.add_task("Searching for coffee shops...", total=None)
        result = finder.search_nearby(
            search_location, 
            radius, 
            max_results,
            min_rating=min_rating,
            exclude_chains=exclude_chains
        )
    
    # Display results
    console.print()
    
    # Create search info with filter details
    filter_info = []
    if min_rating:
        filter_info.append(f"⭐ Min Rating: {min_rating}")
    if exclude_chains:
        filter_info.append("🚫 Chains Excluded")
    if specialty_only:
        filter_info.append("☕ Specialty Only")
    
    filter_text = " | ".join(filter_info)
    search_info_text = (
        f"📍 Search Location: {location_service.format_location(search_location)}\n"
        f"🔍 Search Radius: {radius}km\n"
        f"📊 Results Found: {result.total_results}"
    )
    
    if filter_text:
        search_info_text += f"\n🔧 Filters: {filter_text}"
    
    location_info = Panel(
        search_info_text,
        title="Search Info",
        border_style="blue"
    )
    console.print(location_info)
    console.print()
    
    display_coffee_shops(result.coffee_shops, search_location)
    
    if not finder.api_key:
        console.print()
        console.print(Panel(
            "🔑 [yellow]API Key Required:[/yellow] To search for coffee shops, you need a Google Places API key.\n\n"
            "   • Set environment variable: [cyan]GOOGLE_PLACES_API_KEY=your_key[/cyan]\n"
            "   • Or use: [cyan]--api-key your_key[/cyan]\n"
            "   • Get a key at: https://developers.google.com/places/web-service/get-api-key",
            title="No API Key Configured",
            border_style="red"
        ))
    elif result.total_results == 0:
        console.print()
        suggestions = [
            "🔍 Try expanding your search:",
            "   • Increase the search radius with [cyan]--radius[/cyan]",
            "   • Search in a different location with [cyan]--location[/cyan]"
        ]
        
        if min_rating or exclude_chains:
            suggestions.extend([
                "   • Lower the minimum rating with [cyan]--min-rating[/cyan]",
                "   • Include chains by removing [cyan]--exclude-chains[/cyan]"
            ])
        else:
            suggestions.append("   • Check that your location has specialty coffee shops nearby")
        
        console.print(Panel(
            "\n".join(suggestions),
            title="No Results Found",
            border_style="yellow"
        ))


@cli.command()
def config():
    """Show configuration information"""
    
    api_key = os.getenv('GOOGLE_PLACES_API_KEY')
    
    config_table = Table(title="EspressoNow Configuration", show_header=True, header_style="bold cyan")
    config_table.add_column("Setting", style="white", no_wrap=True)
    config_table.add_column("Value", style="green")
    config_table.add_column("Status", justify="center")
    
    config_table.add_row(
        "Google Places API Key",
        "***" + api_key[-4:] if api_key else "Not set",
        "✅ Set" if api_key else "❌ Missing"
    )
    
    console.print(config_table)
    
    if not api_key:
        console.print()
        console.print(Panel(
            "To get real coffee shop data, you need a Google Places API key:\n\n"
            "1. Go to: https://developers.google.com/places/web-service/get-api-key\n"
            "2. Create a project and enable the Places API\n"
            "3. Create an API key\n"
            "4. Set it as an environment variable:\n"
            "   [cyan]export GOOGLE_PLACES_API_KEY=your_key_here[/cyan]\n"
            "5. Or create a .env file with:\n"
            "   [cyan]GOOGLE_PLACES_API_KEY=your_key_here[/cyan]",
            title="Setup Instructions",
            border_style="blue"
        ))


def main():
    """Main entry point"""
    cli()


if __name__ == '__main__':
    main() 