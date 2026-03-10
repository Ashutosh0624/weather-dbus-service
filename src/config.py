# =============================================================================
# config.py — Central configuration for Weather D-Bus Application
# =============================================================================

# --- OpenWeatherMap REST API ---
OWM_API_KEY     = "Your API KEY"          # Replace with your free API key
OWM_BASE_URL    = "http://api.openweathermap.org/data/2.5/weather"
OWM_UNITS       = "metric"                     # "metric" = Celsius
OWM_TIMEOUT_SEC = 5                            # HTTP request timeout

# --- D-Bus Identifiers ---
DBUS_SERVICE_NAME   = "com.weather.Service"
DBUS_OBJECT_PATH    = "/com/weather/Service"
DBUS_INTERFACE_NAME = "com.weather.Service"

# --- Polling ---
POLL_INTERVAL_SEC   = 60        # Auto-refresh interval (GLib.timeout_add_seconds)
DEFAULT_CITY        = "London"  # City to monitor on startup



# Direct curl test — apni key paste karo
