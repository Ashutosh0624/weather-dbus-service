# =============================================================================
# weather_fetcher.py — REST API Layer (OpenWeatherMap)
#
# Responsibility : ONLY fetches weather data from REST API.
#                  No D-Bus, No GLib, No threading here.
# Pattern        : Single Responsibility (SRP)
# =============================================================================

import requests
import logging
from dataclasses import dataclass
from config import OWM_API_KEY, OWM_BASE_URL, OWM_UNITS, OWM_TIMEOUT_SEC

logger = logging.getLogger(__name__)


# --- Data Model ---
@dataclass
class WeatherData:
    """Plain data object returned by WeatherFetcher."""
    city        : str
    temperature : float     # Celsius
    humidity    : int       # Percentage
    description : str       # e.g., "light rain"
    feels_like  : float
    wind_speed  : float


class WeatherFetchError(Exception):
    """Raised when REST API call fails."""
    pass


class WeatherFetcher:
    """
    Fetches weather data from OpenWeatherMap REST API.

    Usage:
        fetcher = WeatherFetcher()
        data = fetcher.fetch("Mumbai")
        print(data.temperature)
    """

    def fetch(self, city: str) -> WeatherData:
        """
        Makes a GET request to OWM API and returns structured WeatherData.

        Args:
            city: City name (e.g., "London", "Mumbai")

        Returns:
            WeatherData dataclass

        Raises:
            WeatherFetchError: On HTTP error or JSON parse failure
        """
        params = {
            "q"     : city,
            "appid" : OWM_API_KEY,
            "units" : OWM_UNITS,
        }

        try:
            logger.info(f"Fetching weather for: {city}")
            response = requests.get(OWM_BASE_URL, params=params, timeout=OWM_TIMEOUT_SEC)
            response.raise_for_status()     # Raises HTTPError for 4xx/5xx
            raw = response.json()

            return WeatherData(
                city        = raw["name"],
                temperature = float(raw["main"]["temp"]),
                humidity    = int(raw["main"]["humidity"]),
                description = raw["weather"][0]["description"],
                feels_like  = float(raw["main"]["feels_like"]),
                wind_speed  = float(raw["wind"]["speed"]),
            )

        except requests.exceptions.HTTPError as e:
            raise WeatherFetchError(f"HTTP error for '{city}': {e}") from e
        except requests.exceptions.ConnectionError as e:
            raise WeatherFetchError(f"Connection failed: {e}") from e
        except requests.exceptions.Timeout:
            raise WeatherFetchError(f"Request timed out for '{city}'")
        except (KeyError, ValueError) as e:
            raise WeatherFetchError(f"Unexpected API response format: {e}") from e
