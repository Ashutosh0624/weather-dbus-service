# =============================================================================
# weather_client.py — D-Bus Client
#
# Demonstrates:
#   1. Reading D-Bus Properties
#   2. Calling D-Bus Methods (on-demand)
#   3. Subscribing to D-Bus Signals (async, event-driven)
# =============================================================================

import logging
from pydbus import SessionBus
from gi.repository import GLib

from config import DBUS_SERVICE_NAME, DBUS_OBJECT_PATH

logging.basicConfig(
    level=logging.INFO,
    format="%(asctime)s [%(levelname)s] %(name)s: %(message)s"
)
logger = logging.getLogger(__name__)


# ------------------------------------------------------------------ #
#  Signal Handler                                                      #
# ------------------------------------------------------------------ #
def on_weather_updated(city: str, temperature: float, humidity: int, description: str):
    """
    Callback fired when WeatherService emits WeatherUpdated signal.
    This is event-driven — no polling needed on client side.
    """
    print("\n" + "="*55)
    print(f"  📡 [SIGNAL] WeatherUpdated received!")
    print(f"  🌍 City       : {city}")
    print(f"  🌡️  Temperature: {temperature:.1f}°C")
    print(f"  💧 Humidity   : {humidity}%")
    print(f"  ☁️  Description: {description}")
    print("="*55 + "\n")


def on_properties_changed(interface: str, changed: dict, invalidated: list):
    """
    Callback fired on org.freedesktop.DBus.Properties.PropertiesChanged.
    Triggered when Temperature or Humidity property changes.
    """
    logger.info(f"[PropertiesChanged] interface={interface}")
    for prop, variant in changed.items():
        logger.info(f"  {prop} → {variant}")


# ------------------------------------------------------------------ #
#  Main Client Logic                                                   #
# ------------------------------------------------------------------ #
def main():
    bus = SessionBus()

    # --- Get proxy object for WeatherService ---
    # pydbus creates a proxy with same Properties/Methods/Signals as server
    try:
        weather = bus.get(DBUS_SERVICE_NAME, DBUS_OBJECT_PATH)
        logger.info(f"Connected to D-Bus service: {DBUS_SERVICE_NAME}")
    except Exception as e:
        logger.error(f"Failed to connect to D-Bus service: {e}")
        logger.error("Is weather_service.py running?")
        return

    # ----------------------------------------------------------------
    # 1. READ PROPERTIES (direct attribute access on proxy)
    # ----------------------------------------------------------------
    print("\n--- [1] Reading D-Bus Properties ---")
    print(f"  City        : {weather.City}")
    print(f"  Temperature : {weather.Temperature:.1f}°C")
    print(f"  Humidity    : {weather.Humidity}%")
    print(f"  Description : {weather.Description}")
    print(f"  Wind Speed  : {weather.WindSpeed} m/s")
    print(f"  Last Updated: {weather.LastUpdated}")

    # ----------------------------------------------------------------
    # 2. CALL METHOD (on-demand fetch for different city)
    # ----------------------------------------------------------------
    print("\n--- [2] Calling GetWeather('Mumbai') Method ---")
    result = weather.GetWeather("Mumbai")

    if "error" in result:
        print(f"  Error: {result['error']}")
    else:
        print(f"  City        : {result['city']}")
        print(f"  Temperature : {result['temperature']:.1f}°C")
        print(f"  Humidity    : {result['humidity']}%")
        print(f"  Description : {result['description']}")
        print(f"  Feels Like  : {result['feels_like']:.1f}°C")
        print(f"  Wind Speed  : {result['wind_speed']} m/s")

    # ----------------------------------------------------------------
    # 3. SUBSCRIBE TO SIGNALS (event-driven, async)
    # ----------------------------------------------------------------
    print("\n--- [3] Subscribing to WeatherUpdated signal ---")
    print("  Waiting for next poll cycle... (Ctrl+C to exit)\n")

    # Connect signal handler — pydbus uses .connect() on signal descriptor
    weather.WeatherUpdated.connect(on_weather_updated)

    # Also subscribe to standard PropertiesChanged
    weather.PropertiesChanged.connect(on_properties_changed)

    # GLib Main Loop — required to receive async signals
    loop = GLib.MainLoop()
    try:
        loop.run()
    except KeyboardInterrupt:
        logger.info("Client shutting down.")
        loop.quit()


if __name__ == "__main__":
    main()
