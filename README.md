# weather-dbus-service
A D-Bus microservice demonstrating REST API → D-Bus → Client  pipeline using Python (pydbus, GLib). Reference implementation  for embedded Linux IPC patterns.

# Weather D-Bus Application
## REST API → D-Bus → Clients (Python / pydbus)

---

## Architecture

```
┌─────────────────────────────────────────────────────┐
│              OpenWeatherMap REST API                │
│         http://api.openweathermap.org               │
└────────────────────┬────────────────────────────────┘
                     │ HTTP GET (requests library)
                     ▼
┌─────────────────────────────────────────────────────┐
│             WeatherFetcher (REST Layer)             │
│  weather_fetcher.py                                 │
│  - fetch(city) → WeatherData dataclass              │
│  - Error handling (HTTP, Timeout, Parse)            │
└────────────────────┬────────────────────────────────┘
                     │ WeatherData object
                     ▼
┌─────────────────────────────────────────────────────┐
│           WeatherService (D-Bus Server)             │
│  weather_service.py                                 │
│                                                     │
│  Bus  : Session Bus                                 │
│  Name : com.weather.Service                         │
│  Path : /com/weather/Service                        │
│                                                     │
│  PROPERTIES (read-only):                            │
│    Temperature, Humidity, City,                     │
│    LastUpdated, Description, WindSpeed              │
│                                                     │
│  METHODS:                                           │
│    GetWeather(city) → a{sv}  [on-demand]            │
│                                                     │
│  SIGNALS:                                           │
│    WeatherUpdated(city, temp, humidity, desc)       │
│    PropertiesChanged (standard D-Bus)               │
│                                                     │
│  POLLING:                                           │
│    GLib.timeout_add_seconds(60, _poll)              │
│    _poll() → fetches + emits signal                 │
└────────────────────┬────────────────────────────────┘
                     │ Session D-Bus (IPC)
          ┌──────────┴──────────┐
          ▼                     ▼
┌──────────────────┐   ┌──────────────────────────┐
│  weather_client  │   │  Any other D-Bus client  │
│  (Python)        │   │  (C++, JS, dbus-send...) │
│                  │   │                          │
│  1. Read Props   │   │                          │
│  2. Call Methods │   │                          │
│  3. Subscribe    │   │                          │
│     Signals      │   │                          │
└──────────────────┘   └──────────────────────────┘
```

---

## D-Bus Concepts Used

| Concept | What it does | Where in code |
|---|---|---|
| **Service Name** | Unique bus name (`com.weather.Service`) | `config.py` |
| **Object Path** | Address of object (`/com/weather/Service`) | `config.py` |
| **Interface** | Contract definition (XML introspection) | `dbus = """..."""` in service |
| **Property** | State variable, readable by clients | `@property` + XML `<property>` |
| **Method** | RPC call from client to server | Python method + XML `<method>` |
| **Signal** | Server → clients async broadcast | `signal()` descriptor |
| **GLib.MainLoop** | Event loop for D-Bus message processing | Both service & client |
| **timeout_add_seconds** | GLib timer for periodic polling | `weather_service.py` |
| **PropertiesChanged** | Standard signal when properties change | `self.PropertiesChanged(...)` |

---

## D-Bus Type System (a{sv} explained)

```
a{sv}  =  Array of {String : Variant}  =  Python dict

GLib.Variant("s", "London")   → D-Bus string
GLib.Variant("d", 23.5)       → D-Bus double (float)
GLib.Variant("i", 65)         → D-Bus int32

Why variants? Because D-Bus is strongly typed — a{sv} lets
you return mixed types in one dict (like JSON objects).
```

---

## Setup & Run

### 1. Install dependencies
```bash
sudo apt install python3-gi python3-gi-cairo gir1.2-glib-2.0
pip install pydbus requests
```

### 2. Get API Key
- Register at: https://openweathermap.org/api
- Free tier: 60 calls/minute, 1M calls/month
- Edit `config.py` → set `OWM_API_KEY`

### 3. Run the service (Terminal 1)
```bash
python3 weather_service.py
```

### 4. Run the client (Terminal 2)
```bash
python3 weather_client.py
```

### 5. Debug with dbus-send (Terminal 3)
```bash
# List all services on session bus
dbus-send --session --print-reply --dest=org.freedesktop.DBus \
  /org/freedesktop/DBus org.freedesktop.DBus.ListNames

# Call GetWeather method
dbus-send --session --print-reply \
  --dest=com.weather.Service \
  /com/weather/Service \
  com.weather.Service.GetWeather \
  string:"Delhi"

# Read a property
dbus-send --session --print-reply \
  --dest=com.weather.Service \
  /com/weather/Service \
  org.freedesktop.DBus.Properties.Get \
  string:"com.weather.Service" \
  string:"Temperature"

# Monitor all signals
dbus-monitor --session "type='signal',interface='com.weather.Service'"
```

---

## Key Learning Points

1. **pydbus XML introspection** — `dbus = """..."""` class attribute defines the D-Bus contract
2. **pydbus.generic.signal()** — descriptor that makes `self.Signal(args)` emit on D-Bus
3. **GLib.MainLoop** — mandatory for D-Bus; without it, signals never arrive
4. **GLib.timeout_add_seconds** — non-blocking timer; returns True to repeat
5. **PropertiesChanged** — standard D-Bus pattern; clients can monitor property changes without custom signals
6. **a{sv} variants** — typed heterogeneous dict; standard pattern for method return values

---

## Files

```
weather_dbus/
├── config.py           — API keys, D-Bus names, constants
├── weather_fetcher.py  — REST API layer (SRP: only HTTP)
├── weather_service.py  — D-Bus server (Properties + Methods + Signals)
├── weather_client.py   — D-Bus client (read + call + subscribe)
└── README.md           — This file
```
