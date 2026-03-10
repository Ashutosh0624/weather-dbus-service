# =============================================================================
# weather_service.py — D-Bus Server (pydbus + GLib)
#
# Exposes:
#   Properties : Temperature, Humidity, City, LastUpdated  (read-only)
#   Methods    : GetWeather(city) → dict                   (on-demand fetch)
#   Signals    : WeatherUpdated(city, temp, humidity)       (emitted on poll)
#
# Bus  : Session Bus
# Name : com.weather.Service
# Path : /com/weather/Service
# =============================================================================

import logging
import datetime

from pydbus import SessionBus
from pydbus.generic import signal
from gi.repository import GLib

from config import (
    DBUS_SERVICE_NAME,
    POLL_INTERVAL_SEC,
    DEFAULT_CITY,
    DBUS_INTERFACE_NAME,
)
from weather_fetcher import WeatherFetcher, WeatherFetchError

logging.basicConfig(
    level=logging.INFO,
    format="%(asctime)s [%(levelname)s] %(name)s: %(message)s"
)
logger = logging.getLogger(__name__)


class WeatherService:
    """
    D-Bus service object.

    pydbus reads the docstring XML for introspection — the XML MUST be
    the class docstring (or assigned to `dbus` class attribute).

    Introspection defines:
      - <method>    : callable by clients
      - <property>  : readable by clients (EmitsChangedSignal = true → PropertiesChanged auto-fired)
      - <signal>    : emitted by server, subscribed by clients
    """

    # ------------------------------------------------------------------ #
    #  D-Bus Introspection XML (pydbus reads this as class docstring)     #
    # ------------------------------------------------------------------ #
    dbus = """
    <node>
      <interface name='com.weather.Service'>

        <!-- ===== Methods ===== -->
        <method name='GetWeather'>
          <arg type='s'    name='city' direction='in'/>
          <arg type='a{sv}' name='data' direction='out'/>
        </method>

        <!-- ===== Properties ===== -->
        <property name='Temperature' type='d' access='read'>
          <annotation name='org.freedesktop.DBus.Property.EmitsChangedSignal' value='true'/>
        </property>
        <property name='Humidity' type='i' access='read'>
          <annotation name='org.freedesktop.DBus.Property.EmitsChangedSignal' value='true'/>
        </property>
        <property name='City'        type='s' access='read'/>
        <property name='LastUpdated' type='s' access='read'/>
        <property name='Description' type='s' access='read'/>
        <property name='WindSpeed'   type='d' access='read'/>

        <!-- ===== Signals ===== -->
        <signal name='WeatherUpdated'>
          <arg type='s' name='city'/>
          <arg type='d' name='temperature'/>
          <arg type='i' name='humidity'/>
          <arg type='s' name='description'/>
        </signal>

      </interface>
    </node>
    """

    # pydbus signal descriptor — calling self.WeatherUpdated(...) emits it
    WeatherUpdated = signal()

    # ------------------------------------------------------------------ #
    #  Constructor                                                         #
    # ------------------------------------------------------------------ #
    def __init__(self, city: str = DEFAULT_CITY):
        self._fetcher     = WeatherFetcher()
        self._city        = city
        self._temperature = 0.0
        self._humidity    = 0
        self._description = "N/A"
        self._wind_speed  = 0.0
        self._last_updated = "Never"

    # ------------------------------------------------------------------ #
    #  D-Bus Properties (Python @property → exposed as D-Bus Properties)  #
    # ------------------------------------------------------------------ #
    @property
    def Temperature(self) -> float:
        return self._temperature

    @property
    def Humidity(self) -> int:
        return self._humidity

    @property
    def City(self) -> str:
        return self._city

    @property
    def LastUpdated(self) -> str:
        return self._last_updated

    @property
    def Description(self) -> str:
        return self._description

    @property
    def WindSpeed(self) -> float:
        return self._wind_speed

    # ------------------------------------------------------------------ #
    #  D-Bus Method : GetWeather(city)                                     #
    #  On-demand fetch — client can query any city at any time            #
    # ------------------------------------------------------------------ #
    def GetWeather(self, city: str) -> dict:
        """
        D-Bus Method: Fetch weather for any city on demand.

        Returns a{sv} dict (D-Bus variant map) with:
          temperature, humidity, description, feels_like, wind_speed, city
        """
        logger.info(f"[Method] GetWeather called for: {city}")
        try:
            data = self._fetcher.fetch(city)
            return {
                "city"        : GLib.Variant("s", data.city),
                "temperature" : GLib.Variant("d", data.temperature),
                "humidity"    : GLib.Variant("i", data.humidity),
                "description" : GLib.Variant("s", data.description),
                "feels_like"  : GLib.Variant("d", data.feels_like),
                "wind_speed"  : GLib.Variant("d", data.wind_speed),
            }
        except WeatherFetchError as e:
            logger.error(f"[Method] GetWeather failed: {e}")
            return {"error": GLib.Variant("s", str(e))}

    # ------------------------------------------------------------------ #
    #  Polling Callback (called by GLib.timeout_add_seconds)              #
    # ------------------------------------------------------------------ #
    def _poll(self) -> bool:
        """
        Periodic polling handler.
        - Fetches weather for the monitored city
        - Updates internal properties
        - Emits WeatherUpdated signal
        - Fires PropertiesChanged for Temperature & Humidity

        Returns True to keep the GLib timer running (False would stop it).
        """
        logger.info(f"[Poll] Fetching weather for: {self._city}")
        try:
            data = self._fetcher.fetch(self._city)

            # Update internal state
            self._temperature  = data.temperature
            self._humidity     = data.humidity
            self._description  = data.description
            self._wind_speed   = data.wind_speed
            self._last_updated = datetime.datetime.now().strftime("%Y-%m-%d %H:%M:%S")

            # --- Emit WeatherUpdated signal ---
            # All subscribed D-Bus clients will receive this
            self.WeatherUpdated(
                self._city,
                self._temperature,
                self._humidity,
                self._description,
            )
            logger.info(
                f"[Poll] Updated → {self._city}: "
                f"{self._temperature}°C, {self._humidity}%, '{self._description}'"
            )

            # --- Emit PropertiesChanged (standard D-Bus notification) ---
            # pydbus handles this via EmitsChangedSignal annotation
            self.PropertiesChanged(
                DBUS_INTERFACE_NAME,
                {
                    "Temperature": GLib.Variant("d", self._temperature),
                    "Humidity"   : GLib.Variant("i", self._humidity),
                },
                []  # invalidated properties list (empty = none invalidated)
            )

        except WeatherFetchError as e:
            logger.error(f"[Poll] Fetch failed: {e}")

        return True  # MUST return True to keep GLib timer alive


# ======================================================================= #
#  Entry Point                                                              #
# ======================================================================= #
if __name__ == "__main__":
    bus     = SessionBus()
    service = WeatherService(city=DEFAULT_CITY)

    # Register service on D-Bus Session Bus
    # bus.publish(name, object) → object is exposed at OBJECT_PATH derived from name
    bus.publish(DBUS_SERVICE_NAME, service)

    logger.info(f"WeatherService published on: {DBUS_SERVICE_NAME}")
    logger.info(f"Polling every {POLL_INTERVAL_SEC}s for city: {DEFAULT_CITY}")

    # GLib Main Loop — required for D-Bus event processing
    loop = GLib.MainLoop()

    # Initial fetch immediately on startup
    service._poll()

    # Register periodic polling with GLib timer
    GLib.timeout_add_seconds(POLL_INTERVAL_SEC, service._poll)

    try:
        loop.run()
    except KeyboardInterrupt:
        logger.info("WeatherService shutting down.")
        loop.quit()
