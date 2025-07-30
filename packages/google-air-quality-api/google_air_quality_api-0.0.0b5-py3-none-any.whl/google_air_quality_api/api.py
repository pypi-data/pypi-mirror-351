"""API for Google Air Quality bound to Home Assistant OAuth."""

import logging
from math import cos, floor, log, pi, radians, tan

from .auth import AbstractAuth
from .const import API_BASE_URL
from .model import AirQualityData, UserInfoResult

_LOGGER = logging.getLogger(__name__)


USERINFO_API = "https://www.googleapis.com/oauth2/v1/userinfo"
CURRENT_CONDITIONS = "currentConditions:lookup"


def latlon_to_tile(lat: float, lon: float, zoom: int) -> tuple[int, int]:
    """Convert lat/lon to tile coordinates."""
    lat_rad = radians(lat)
    n = 2.0**zoom
    x_tile = floor((lon + 180.0) / 360.0 * n)
    y_tile = floor((1.0 - log(tan(lat_rad) + 1.0 / cos(lat_rad)) / pi) / 2.0 * n)
    return x_tile, y_tile


class GoogleAirQualityApi:
    """The Google Air Quality library api client."""

    def __init__(self, auth: AbstractAuth) -> None:
        """Initialize GoogleAirQualityApi."""
        self._auth = auth

    async def async_air_quality(self, lat: float, long: float) -> AirQualityData:
        """Get all air quality data."""
        payload = {
            "location": {"latitude": lat, "longitude": long},
            "extraComputations": [
                "LOCAL_AQI",
                "POLLUTANT_CONCENTRATION",
            ],
            "universalAqi": True,
        }
        return await self._auth.post_json(
            CURRENT_CONDITIONS, json=payload, data_cls=AirQualityData
        )

    async def async_heatmap(self, lat: float, long: float, zoom: int) -> AirQualityData:
        """Get all air quality data."""
        x, y = latlon_to_tile(lat, long, zoom)
        heat_map_uri = (
            f"{API_BASE_URL}/mapTypes/UAQI_RED_GREEN/heatmapTiles/{zoom}/{x}/{y}"
        )
        return await self._auth.get(heat_map_uri)

    async def get_user_info(self) -> UserInfoResult:
        """Get the user profile info.

        This call requires the userinfo.email scope.
        """
        return await self._auth.get_json(USERINFO_API, data_cls=UserInfoResult)
