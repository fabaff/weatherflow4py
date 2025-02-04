import aiohttp

from weatherflow4py.exceptions import TokenError
from weatherflow4py.models.device import DeviceObservationTempest
from weatherflow4py.models.forecast import WeatherData
from weatherflow4py.models.observation import StationObservation
from weatherflow4py.models.station import StationsResponse
from weatherflow4py.models.unified import WeatherFlowData


class WeatherFlowRestAPI:
    """Our REST rate limits are not connected to our web socket rate limits. For REST you can make 100 requests per minute. There is some burst capacity built into the system, but the general rule of thumb it to keep the number of REST requests per user to under 100 per minute."""

    BASE_URL = "https://swd.weatherflow.com/swd/rest"

    def __init__(self, api_token: str):
        if not api_token:
            raise TokenError

        self.api_token = api_token

    async def __aenter__(self):
        self.session = aiohttp.ClientSession(headers={"Accept": "application/json"})
        return self

    async def __aexit__(self, exc_type, exc_val, exc_tb):
        await self.session.close()

    async def _make_request(
        self, endpoint: str, params: dict = None, response_model=None
    ):
        if self.session is None:
            raise RuntimeError(
                "Session is not initialized. Use the async with statement."
            )

        url = f"{self.BASE_URL}/{endpoint}"
        full_params = {"token": self.api_token, **(params or {})}
        async with self.session.get(url, params=full_params) as response:
            response.raise_for_status()
            data = await response.text()

        return (
            response_model.from_json(data)
            if response_model
            else aiohttp.helpers.BasicAuth.from_url(response.json())
        )

    async def async_get_stations(self) -> StationsResponse:
        """
        Gets station data.

        Raises:
            ClientResponseError: If there is a client response error.
        """
        ret = await self._make_request("stations", response_model=StationsResponse)
        return ret

    async def async_get_station(self, station_id: int) -> StationsResponse:
        """
        Gets data for a specific station.

        Args:
            station_id (int): The ID of the station.

        Raises:
            ClientResponseError: If there is a client response error.
        """
        return (
            await self._make_request(
                f"stations/{station_id}", response_model=StationsResponse
            )
        ).stations

    async def async_get_forecast(self, station_id: int):
        """
        Gets the forecast for a given station.

        Args:
            station_id (int): The ID of the station.

        Raises:
            ClientResponseError: If there is a client response error.
        """
        return await self._make_request(
            "better_forecast",
            params={"station_id": station_id},
            response_model=WeatherData,
        )

    async def async_get_device_observations(
        self, device_id: int
    ) -> DeviceObservationTempest:
        """
        Gets the device observation data for a given device.

        Args:
            device_id (int): The ID of the device.

        Raises:
            ClientResponseError: If there is a client response error.
        """
        return await self._make_request(
            f"observations/device/{device_id}",
            response_model=DeviceObservationTempest,
        )

    async def async_get_observation(self, station_id: int) -> StationObservation:
        """
        Gets the observation data for a given station.

        Args:
            station_id (int): The ID of the station.

        Raises:
            ClientResponseError: If there is a client response error.
        """
        return await self._make_request(
            "observations/station",
            params={"station_id": station_id},
            response_model=StationObservation,
        )

    async def get_all_data(self) -> dict[int, WeatherFlowData]:
        """
        Builds a full data set of stations and forecasts.

        Raises:
            ClientResponseError: If there is a client response error during data retrieval.
        """
        ret: dict[int, WeatherFlowData] = {}
        station_response = await self.async_get_stations()
        for station in station_response.stations:
            device_id = station.outdoor_devices[0].device_id

            ret[station.station_id] = WeatherFlowData(
                weather=await self.async_get_forecast(station_id=station.station_id),
                observation=await self.async_get_observation(
                    station_id=station.station_id
                ),
                station=station,
                device_observations=await self.async_get_device_observations(
                    device_id=device_id
                ),
            )

        return ret
