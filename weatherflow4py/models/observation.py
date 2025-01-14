from dataclasses import dataclass
from enum import Enum
from typing import List
from dataclasses_json import dataclass_json


class WetBulbFlag(Enum):
    WHITE = 1
    GREEN = 2
    YELLOW = 3
    RED = 4
    BLACK = 5


@dataclass_json
@dataclass(frozen=True, eq=True)
class Observation:
    air_density: float
    air_temperature: float
    barometric_pressure: float
    brightness: int
    delta_t: float
    dew_point: float
    feels_like: float
    heat_index: float
    lightning_strike_count: int
    lightning_strike_count_last_1hr: int
    lightning_strike_count_last_3hr: int
    lightning_strike_last_distance: int
    lightning_strike_last_epoch: int
    precip: float
    precip_accum_last_1hr: float
    precip_accum_local_day: float
    precip_accum_local_day_final: float
    precip_accum_local_yesterday: float
    precip_accum_local_yesterday_final: float
    precip_analysis_type_yesterday: int
    precip_minutes_local_day: int
    precip_minutes_local_yesterday: int
    precip_minutes_local_yesterday_final: int
    pressure_trend: str
    relative_humidity: int
    sea_level_pressure: float
    solar_radiation: int
    station_pressure: float
    timestamp: int
    uv: float
    wet_bulb_globe_temperature: float
    wet_bulb_temperature: float
    wind_avg: float
    wind_chill: float
    wind_direction: int
    wind_gust: float
    wind_lull: float

    @property
    def wet_bulb_globe_temperature_category(self) -> int:
        """Calculates a wet bulb globe temp category - based on wikipedia: https://en.wikipedia.org/wiki/Wet-bulb_globe_temperature."""

        if self.wet_bulb_globe_temperature <= 25.6:
            return 1  # Low risk
        if self.wet_bulb_globe_temperature <= 29.4:
            return 2  # Moderate risk
        if self.wet_bulb_globe_temperature <= 31.0:
            return 3
        if self.wet_bulb_globe_temperature <= 32.1:
            return 4
        return 5

    def wet_bulb_globe_temperature_flag(self) -> WetBulbFlag:
        return WetBulbFlag(self.wet_bulb_globe_temperature)


@dataclass_json
@dataclass(frozen=True, eq=True)
class StationUnits:
    """The station_units values represent the units of the Station's owner, not the units of the observation values in the API response."""

    units_temp: str
    units_wind: str
    units_precip: str
    units_pressure: str
    units_distance: str
    units_direction: str
    units_other: str


@dataclass_json
@dataclass(frozen=True, eq=True)
class StationStatus:
    status_code: int
    status_message: str


@dataclass_json
@dataclass(frozen=True, eq=True)
class StationObservation:
    elevation: float
    is_public: bool
    latitude: float
    longitude: float
    obs: List[Observation]
    outdoor_keys: List[str]
    public_name: str
    station_id: int
    station_name: str
    station_units: StationUnits
    status: StationStatus
    timezone: str
