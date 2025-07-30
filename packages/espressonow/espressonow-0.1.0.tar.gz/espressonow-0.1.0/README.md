# EspressoNow ☕

Python CLI tool to find specialty coffee shops near your current location.

## Features

- 🌍 **Auto-location detection** - Automatically detects your current location
- 📍 **Custom location search** - Search near any address or coordinates
- ☕ **Specialty coffee focus** - Finds high-quality, specialty coffee shops
- 🎨 **Beautiful output** - Rich, colorful CLI interface with tables and progress bars
- 🔍 **Flexible search** - Customizable search radius and result limits
- 🗺️ **Google Places API integration** - Real-time coffee shop data from Google's database

## Installation

### From Source

```bash
git clone https://github.com/ethanqcarter/EspressoNow.git
cd EspressoNow
pip install -e .
```

### Dependencies

```bash
pip install -r requirements.txt
```

## Quick Start

### Configuration

**Required:** You'll need a Google Places API key to search for coffee shops:

1. Get an API key at [Google Places API](https://developers.google.com/places/web-service/get-api-key)
2. Set it as an environment variable:
   ```bash
   export GOOGLE_PLACES_API_KEY=your_key_here
   ```
3. Or create a `.env` file:
   ```bash
   cp env.example .env
   # Edit .env and add your API key
   ```

### Basic Usage

```bash
# Find coffee shops near your current location
espresso search

# Search with custom radius
espresso search --radius 5

# Search near a specific address
espresso search --location "123 Main St, San Francisco, CA"

# Search near coordinates
espresso search --location "37.7749,-122.4194"
```

## Commands

### `search` - Find coffee shops

```bash
espresso search [OPTIONS]

Options:
  -r, --radius FLOAT         Search radius in kilometers (default: 2.0)
  -n, --max-results INTEGER  Maximum number of results (default: 10)
  -l, --location TEXT        Search location (address or "lat,lng")
  --api-key TEXT             Google Places API key
  --min-rating FLOAT         Minimum rating (e.g., 4.0 for >4 stars)
  --exclude-chains           Exclude chain coffee shops (Starbucks, Dunkin, etc.)
  --specialty-only           Show only specialty coffee (4+ stars, no chains)
  --help                     Show help message
```

### `config` - Show configuration

```bash
espresso config
```

Shows current configuration status and setup instructions.

## Examples

### Find coffee shops near current location
```bash
espresso search
```

### Search with 5km radius, max 20 results
```bash
espresso search --radius 5 --max-results 20
```

### Search near specific coordinates (San Francisco)
```bash
espresso search --location "37.7749,-122.4194"
```

### Search near coordinates (New York City)
```bash
espresso search --location "40.7128,-74.0060"
```

### Find only specialty coffee (4+ stars, no chains)
```bash
espresso search --specialty-only
```

### Exclude chain coffee shops
```bash
espresso search --exclude-chains
```

### Use specific API key
```bash
espresso search --api-key your_google_places_api_key
```

## Example Output

Here's what you'll see when searching for specialty coffee in San Francisco:

```bash
$ espresso search --location "37.7749,-122.4194" --radius 8 --specialty-only --max-results 5
```

```
Using provided coordinates: 37.7749, -122.4194
⠸ Searching for coffee shops...

╭────────────────────────────────────────────── Search Info ───────────────────────────────────────────────╮
│ 📍 Search Location: 37.7749, -122.4194                                                                   │
│ 🔍 Search Radius: 8.0km                                                                                  │
│ 📊 Results Found: 8                                                                                      │
│ 🔧 Filters: ⭐ Min Rating: 4.0 | 🚫 Chains Excluded | ☕ Specialty Only                                  │
╰──────────────────────────────────────────────────────────────────────────────────────────────────────────╯

                                     ☕ Specialty Coffee Shops Near You                                     
┏━━━━━━━━━━━━━━━━━━━┳━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━┳━━━━━━━━━━━━━━━━┳━━━━━━━┳━━━━━━━━━━┳━━━━━━━━━━━━━━━━┓
┃ Name              ┃ Address                         ┃     Rating     ┃ Price ┃ Distance ┃ Phone          ┃
┡━━━━━━━━━━━━━━━━━━━╇━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━╇━━━━━━━━━━━━━━━━╇━━━━━━━╇━━━━━━━━━━╇━━━━━━━━━━━━━━━━┩
│ Zuni Café         │ 1658 Market St, San Francisco,  │ ⭐⭐⭐⭐ (4.4) │  $$$  │     242m │ (415) 552-2522 │
│                   │ CA 94102, USA                   │                │       │          │                │
│ Sightglass Coffee │ 270 7th St, San Francisco, CA   │ ⭐⭐⭐⭐ (4.5) │  $$   │     991m │ (415) 861-1313 │
│                   │ 93103, USA                      │                │       │          │                │
│ Tartine Bakery    │ 600 Guerrero St, San Francisco, │ ⭐⭐⭐⭐ (4.5) │  $$   │    1.6km │ (415) 487-2600 │
│                   │ CA 94110, USA                   │                │       │          │                │
│ The Mill          │ 736 Divisadero St, San          │ ⭐⭐⭐⭐ (4.5) │  $$   │    1.6km │ (415) 345-1953 │
│                   │ Francisco, CA 94117, USA        │                │       │          │                │
│ Sweet Maple       │ 2101 Sutter St, San Francisco,  │ ⭐⭐⭐⭐ (4.6) │  $$   │    1.8km │ (415) 655-9169 │
│                   │ CA 94115, USA                   │                │       │          │                │
└───────────────────┴─────────────────────────────────┴────────────────┴───────┴──────────┴────────────────┘
```

This example shows EspressoNow finding top-rated specialty coffee shops in San Francisco, including famous spots like **Tartine Bakery**, **Sightglass Coffee**, and **The Mill** - all with 4+ star ratings and no chain coffee shops included!

## Output

EspressoNow displays results in a beautiful table format showing:

- ☕ **Name** - Coffee shop name
- 📍 **Address** - Street address
- ⭐ **Rating** - Star rating (1-5)
- 💰 **Price** - Price level ($-$$$$)
- 📏 **Distance** - Distance from search location
- 📞 **Phone** - Contact number

## API Integration

### Google Places API (New)

EspressoNow uses the latest Google Places API (New) to find real coffee shops:
- POST-based Nearby Search with "cafe" and "coffee_shop" types
- Real-time data from Google's comprehensive database
- Detailed place information including ratings, prices, and contact details
- Supports up to 50km search radius

**Note:** A Google Places API key is required for the application to function.

## Development

### Project Structure

```
espressonow/
├── __init__.py          # Package initialization
├── cli.py              # Command-line interface
├── core.py             # Core coffee shop finding logic
├── location.py         # Location detection and services
└── models.py           # Data models (Pydantic)
```

### Running Tests

```bash
# Install in development mode
pip install -e .

# Test the CLI
espresso search --help
espresso config

# Test with API key
export GOOGLE_PLACES_API_KEY=your_key_here
espresso search --location "San Francisco, CA"
```

## Contributing

1. Fork the repository
2. Create a feature branch
3. Make your changes
4. Add tests if applicable
5. Submit a pull request

## License

MIT License - see LICENSE file for details.

## Support

- 🐛 **Issues**: [GitHub Issues](https://github.com/ethanqcarter/EspressoNow/issues)
- 📧 **Contact**: ethanqcarter@example.com

---

Made with ☕ and ❤️ by coffee enthusiasts, for coffee enthusiasts.
