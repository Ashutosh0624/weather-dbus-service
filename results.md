2026-03-11 00:28:38,647 [INFO] __main__: Connected to D-Bus service: com.weather.Service

--- [1] Reading D-Bus Properties ---
  City        : London
  Temperature : 9.4°C
  Humidity    : 80%
  Description : scattered clouds
  Wind Speed  : 4.97 m/s
  Last Updated: 2026-03-11 00:28:07

--- [2] Calling GetWeather('Mumbai') Method ---
  City        : Mumbai
  Temperature : 27.9°C
  Humidity    : 66%
  Description : clear sky
  Feels Like  : 29.9°C
  Wind Speed  : 1.98 m/s

--- [3] Subscribing to WeatherUpdated signal ---
  Waiting for next poll cycle... (Ctrl+C to exit)




=======================================================
  📡 [SIGNAL] WeatherUpdated received!
  🌍 City       : London
  🌡️  Temperature: 9.3°C
  💧 Humidity   : 80%
  ☁️  Description: scattered clouds
=======================================================




=======================================================
  📡 [SIGNAL] WeatherUpdated received!
  🌍 City       : London
  🌡️  Temperature: 9.3°C
  💧 Humidity   : 80%
  ☁️  Description: scattered clouds
=======================================================




=======================================================
  📡 [SIGNAL] WeatherUpdated received!
  🌍 City       : London
  🌡️  Temperature: 9.3°C
  💧 Humidity   : 80%
  ☁️  Description: scattered clouds
=======================================================




-> dbus-send --session --print-reply \
  --dest=com.weather.Service \
  /com/weather/Service \
  org.freedesktop.DBus.Properties.Get \
  string:"com.weather.Service" \
  string:"Temperature"
method return time=1773169473.356050 sender=:1.142 -> destination=:1.159 serial=19 reply_serial=2
   variant       double 9.3




-> ashutosh@ashutosh-Vivobook-ASUSLaptop-M1502IA-M1502IA:~/Desktop/dbus_projects/weather-dbus-service/src$ dbus-monitor --session "type='signal',interface='com.weather.Service'"
signal time=1773169486.554105 sender=org.freedesktop.DBus -> destination=:1.160 serial=2 path=/org/freedesktop/DBus; interface=org.freedesktop.DBus; member=NameAcquired
   string ":1.160"
signal time=1773169486.554135 sender=org.freedesktop.DBus -> destination=:1.160 serial=4 path=/org/freedesktop/DBus; interface=org.freedesktop.DBus; member=NameLost
   string ":1.160"
signal time=1773169507.365744 sender=:1.142 -> destination=(null destination) serial=20 path=/com/weather/Service; interface=com.weather.Service; member=WeatherUpdated
   string "London"
   double 9.3
   int32 80
   string "scattered clouds"
signal time=1773169567.473821 sender=:1.142 -> destination=(null destination) serial=21 path=/com/weather/Service; interface=com.weather.Service; member=WeatherUpdated
   string "London"
   double 9.3
   int32 80
   string "scattered clouds"
