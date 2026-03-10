# weather-dbus-service

A D-Bus microservice demonstrating a **REST API → D-Bus → Client** pipeline using Python (`pydbus`, `GLib`). Reference implementation for embedded Linux IPC patterns.

---

## Architecture

```
OpenWeatherMap REST API  (or Mock)
        │
        ▼
WeatherFetcher           (REST layer — SRP)
        │
        ▼
WeatherService           (D-Bus Server)
  ├── Properties   →  Temperature, Humidity, City, LastUpdated
  ├── Methods      →  GetWeather(city) → dict
  └── Signals      →  WeatherUpdated, PropertiesChanged
        │
        │  Session Bus: com.weather.Service
        ▼
WeatherClient            (D-Bus Client)
  ├── Read Properties
  ├── Call Methods
  └── Subscribe Signals
```

---

## D-Bus Interface

| Type       | Name             | Signature       | Description                        |
|------------|------------------|-----------------|------------------------------------|
| Property   | `Temperature`    | `d` (double)    | Current temperature in °C          |
| Property   | `Humidity`       | `i` (int32)     | Current humidity in %              |
| Property   | `City`           | `s` (string)    | Monitored city name                |
| Property   | `LastUpdated`    | `s` (string)    | Last poll timestamp                |
| Property   | `Description`    | `s` (string)    | Weather description                |
| Property   | `WindSpeed`      | `d` (double)    | Wind speed                         |
| Method     | `GetWeather`     | `s → a{sv}`     | On-demand fetch for any city       |
| Signal     | `WeatherUpdated` | `s, d, i, s`    | Emitted on every poll cycle        |

---

## Project Structure

```
weather-dbus-service/
├── config.py            # API keys, D-Bus names, constants
├── weather_fetcher.py   # REST API layer (SRP — HTTP only)
├── weather_service.py   # D-Bus server (Properties + Methods + Signals)
├── weather_client.py    # D-Bus client (read + call + subscribe)
├── requirements.txt     # Python dependencies
└── README.md
```

---

## Prerequisites

### System Dependencies
```bash
sudo apt install python3-gi python3-gi-cairo \
  gir1.2-glib-2.0 dbus-tools
```

### Python Dependencies
```bash
pip install -r requirements.txt
```

---

## Configuration

Edit `config.py`:

```python
# Option 1: OpenWeatherMap (free tier — register at openweathermap.org)
OWM_API_KEY = "your_api_key_here"

# Option 2: Mock fetcher (no internet required — default)
# weather_fetcher.py already uses mock data out of the box
```

---

## Usage

### Terminal 1 — Start the D-Bus Service
```bash
python3 weather_service.py
```

Expected output:
```
2026-03-10 12:00:00 [INFO] WeatherService published on: com.weather.Service
2026-03-10 12:00:00 [INFO] Polling every 10s for city: London
2026-03-10 12:00:00 [INFO] [Poll] Updated → London: 23.5°C, 65%, 'Cloudy'
```

### Terminal 2 — Run the Client
```bash
python3 weather_client.py
```

Expected output:
```
--- [1] Reading D-Bus Properties ---
  City        : London
  Temperature : 23.5°C
  Humidity    : 65%

--- [2] Calling GetWeather('Mumbai') Method ---
  Temperature : 34.1°C
  Humidity    : 87%

--- [3] Subscribing to WeatherUpdated signal ---
  Waiting for next poll cycle...

========================================
  📡 [SIGNAL] WeatherUpdated received!
  🌍 City       : London
  🌡️  Temperature: 24.0°C
  💧 Humidity   : 63%
========================================
```

### Terminal 3 — Debug with dbus-send
```bash
# Read a property
dbus-send --session --print-reply \
  --dest=com.weather.Service \
  /com/weather/Service \
  org.freedesktop.DBus.Properties.Get \
  string:"com.weather.Service" \
  string:"Temperature"

# Call GetWeather method
dbus-send --session --print-reply \
  --dest=com.weather.Service \
  /com/weather/Service \
  com.weather.Service.GetWeather \
  string:"Delhi"

# Monitor all signals
dbus-monitor --session "type='signal',interface='com.weather.Service'"
```

---

## Key D-Bus Concepts Demonstrated

| Concept                  | Implementation                          |
|--------------------------|-----------------------------------------|
| Introspection XML        | `dbus = """..."""` class attribute      |
| Properties               | `@property` + XML `<property>` tag      |
| EmitsChangedSignal       | Annotation in XML + `PropertiesChanged` |
| Custom Signal            | `signal()` descriptor + emit            |
| Method (RPC)             | Python method + XML `<method>` tag      |
| GLib MainLoop            | `GLib.MainLoop().run()` — both sides    |
| Periodic Polling         | `GLib.timeout_add_seconds()`            |
| D-Bus Variant Type       | `GLib.Variant('d', value)`              |

---

## D-Bus Type Signatures Used

| Signature | Type              | Example                        |
|-----------|-------------------|--------------------------------|
| `s`       | String            | City name                      |
| `d`       | Double            | Temperature (23.5)             |
| `i`       | Int32             | Humidity (65)                  |
| `a{sv}`   | Dict<String, Var> | Method return value            |

---

## Relation to SPM Architecture

This project is a **reference implementation** for the `com.safran.SatelliteModemManager` D-Bus architecture:

| Weather Project          | SPM Project                              |
|--------------------------|------------------------------------------|
| `com.weather.Service`    | `com.safran.SatelliteModemManager`       |
| `Temperature`, `Humidity`| `SNR`, `LinkQuality`, `ModCod`           |
| `GetWeather(city)`       | `GetModemStats(modem_id)`                |
| `WeatherUpdated` signal  | `ModCodChanged`, `ModemFaultDetected`    |
| `GLib.timeout_add_seconds` | Same polling pattern                   |

---

## Author

**Ashutosh Kumar Tiwari**  
Engineer II — Connectivity & Embedded Systems  
SESI, Bangalore  

---

## License

MIT License — see [LICENSE](LICENSE)
