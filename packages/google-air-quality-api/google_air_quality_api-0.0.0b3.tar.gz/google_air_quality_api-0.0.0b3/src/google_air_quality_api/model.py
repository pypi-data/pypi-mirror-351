"""Google Air Quality Library API Data Model."""

from dataclasses import dataclass, field
from datetime import datetime
from re import sub
from typing import Any, ClassVar

from mashumaro import DataClassDictMixin, field_options
from mashumaro.mixins.json import DataClassJSONMixin


@dataclass(frozen=True)
class AQICategory:
    """Represents an AQI category with normalized and original names."""

    normalized: str
    original: str


class AQICategoryMapping:
    """Mapping of AQI categories to their normalized and original names."""

    _mapping: ClassVar[dict[str, list[AQICategory]]] = {
        "uaqi": [
            AQICategory("excellent", "Excellent air quality"),
            AQICategory("good", "Good air quality"),
            AQICategory("moderate", "Moderate air quality"),
            AQICategory("low", "Low air quality"),
            AQICategory("poor", "Poor air quality"),
        ],
        "and_aire": [
            AQICategory("excellent", "Excellent air quality"),
            AQICategory("good", "Good air quality"),
            AQICategory("regular", "Regular air quality"),
            AQICategory("poor", "Poor air quality"),
            AQICategory("bad", "Bad air quality"),
        ],
        "aus_combined": [
            AQICategory("very_good", "Very good air quality"),
            AQICategory("good", "Good air quality"),
            AQICategory("fair", "Fair air quality"),
            AQICategory("poor", "Poor air quality"),
            AQICategory("very_poor", "Very poor air quality"),
            AQICategory("hazardous", "Hazardous air quality"),
        ],
        "aus_nsw": [
            AQICategory("good", "Good air quality"),
            AQICategory("fair", "Fair air quality"),
            AQICategory("poor", "Poor air quality"),
            AQICategory("very_poor", "Very poor air quality"),
            AQICategory("extremely_poor", "Extremely poor air quality"),
        ],
        "aut_umwelt": [
            AQICategory("1_green", "1 - Green"),
            AQICategory("2_light_green", "2 - Light green"),
            AQICategory("2_yellow", "3 - Yellow"),
            AQICategory("2_orange", "4 - Orange"),
            AQICategory("2_red", "5 - Red"),
        ],
        "aut_vienna": [
            AQICategory("very_good", "Very good air quality"),
            AQICategory("good", "Good air quality"),
            AQICategory("satisfactory", "Satisfactory air quality"),
            AQICategory("unsatisfactory", "Unsatisfactory air quality"),
            AQICategory("bad", "Bad air quality"),
            AQICategory("very_bad", "Very bad air quality"),
        ],
        "bel_irceline": [
            AQICategory("excellent", "Excellent air quality"),
            AQICategory("very_good", "Very good air quality"),
            AQICategory("good", "Good air quality"),
            AQICategory("fairly_good", "Fairly good air quality"),
            AQICategory("moderate", "Moderate air quality"),
            AQICategory("poor", "Poor air quality"),
            AQICategory("very_poor", "Very poor air quality"),
            AQICategory("bad", "Bad air quality"),
            AQICategory("very_bad", "Very bad air quality"),
            AQICategory("horrible", "Horrible air quality"),
        ],
        "bgd_case": [
            AQICategory("good", "Good air quality"),
            AQICategory("moderate", "Moderate air quality"),
            AQICategory("caution", "Caution"),
            AQICategory("unhealthy", "Unhealthy air quality"),
            AQICategory("very_unhealthy", "Very Unhealthy air quality"),
            AQICategory("extremely_unhealthy", "Extremely Unhealthy air quality"),
        ],
        "bgr_niggg": [
            AQICategory("low", "Low air pollution"),
            AQICategory("moderate", "Moderate air pollution"),
            AQICategory("high", "High air pollution"),
            AQICategory("very_high", "Very High air pollution"),
        ],
        "bra_saopaulo": [
            AQICategory("n1_good", "N1 - Good air quality"),
            AQICategory("n2_moderate", "N2 - Moderate air quality"),
            AQICategory("n3_bad", "N3 - Bad air quality"),
            AQICategory("n4_very_bad", "N4 - Very bad air quality"),
            AQICategory("n5_poor", "N5 - Poor air quality"),
        ],
        "can_ec": [
            AQICategory("low_health_risk", "Low health risk"),
            AQICategory("moderate_health_risk", "Moderate health risk"),
            AQICategory("high_health_risk", "High health risk"),
            AQICategory("very_high_health_risk", "Very high health risk"),
        ],
        "caqi": [
            AQICategory("very_low_air_pollution", "Very low air pollution"),
            AQICategory("low_air_pollution", "Low air pollution"),
            AQICategory("medium_air_pollution", "Medium air pollution"),
            AQICategory("high_air_pollution", "High air pollution"),
            AQICategory("very_high_air_pollution", "Very high air pollution"),
        ],
        "che_cerclair": [
            AQICategory("low_air_pollution", "Low air pollution"),
            AQICategory("moderate_air_pollution", "Moderate air pollution"),
            AQICategory("evident_air_pollution", "Evident air pollution"),
            AQICategory("considerable_air_pollution", "Considerable air pollution"),
            AQICategory("high_air_pollution", "High air pollution"),
            AQICategory("very_high_air_pollution", "Very high air pollution"),
        ],
        "chn_mee": [  # ehem. chn_mep
            AQICategory("excellent", "Excellent air quality"),
            AQICategory("good", "Good air quality"),
            AQICategory("light", "Light air pollution"),
            AQICategory("moderate", "Moderate air pollution"),
            AQICategory("heavy", "Heavy air pollution"),
            AQICategory("severe", "Severe air pollution"),
        ],
        "chn_mee_1h": [  # ehem. chn_mep_1h
            AQICategory("excellent", "Excellent air quality"),
            AQICategory("good", "Good air quality"),
            AQICategory("light", "Light air pollution"),
            AQICategory("moderate", "Moderate air pollution"),
            AQICategory("heavy", "Heavy air pollution"),
            AQICategory("severe", "Severe air pollution"),
        ],
        "col_rmcab": [
            AQICategory("fair", "Fair air quality"),
            AQICategory("moderate", "Moderate air quality"),
            AQICategory("regular", "Regular air quality"),
            AQICategory("bad", "Bad air quality"),
            AQICategory("very_bad", "Very bad air quality"),
            AQICategory("hazardous", "Hazardous air quality"),
        ],
        "cri_icca": [
            AQICategory("good", "Good air quality"),
            AQICategory(
                "unfavorable_sensitive", "Unfavorable air quality for sensitive groups"
            ),
            AQICategory("unfavorable", "Unfavorable air quality"),
            AQICategory("very_unfavorable", "Very unfavorable air quality"),
            AQICategory("hazardous", "Hazardous air quality"),
        ],
        "cyp_dli": [
            AQICategory("low_air_pollution", "Low air pollution"),
            AQICategory("moderate_air_pollution", "Moderate air pollution"),
            AQICategory("high_air_pollution", "High air pollution"),
            AQICategory("very_high_air_pollution", "Very high air pollution"),
        ],
        "cze_chmi": [
            AQICategory("1a_very_good", "1A - Very good air quality"),
            AQICategory("1b_good", "1B - Good air quality"),
            AQICategory("2a_acceptable", "2A - Acceptable air quality"),
            AQICategory("2b_acceptable", "2B - Acceptable air quality"),
            AQICategory("3a_aggravated", "3A - Aggravated air quality"),
            AQICategory("3b_bad", "3B - Bad air quality"),
        ],
        "deu_lubw": [
            AQICategory("very_good", "Very good air quality"),
            AQICategory("good", "Good air quality"),
            AQICategory("satisfactory", "Satisfactory air quality"),
            AQICategory("sufficient", "Sufficient air quality"),
            AQICategory("bad", "Bad air quality"),
            AQICategory("very_bad", "Very bad air quality"),
        ],
        "deu_uba": [
            AQICategory("very_good", "Very good air quality"),
            AQICategory("good", "Good air quality"),
            AQICategory("moderate", "Moderate air quality"),
            AQICategory("poor", "Poor air quality"),
            AQICategory("very_poor", "Very poor air quality"),
        ],
        "dnk_aarhus": [
            AQICategory("below_average_air_pollution", "Below average air pollution"),
            AQICategory("average_air_pollution", "Average air pollution"),
            AQICategory("above_average_air_pollution", "Above average air pollution"),
            AQICategory("high_air_pollution", "High air pollution"),
            AQICategory("warning_air_pollution", "Warning level air pollution"),
        ],
        "eaqi": [
            AQICategory("good", "Good air quality"),
            AQICategory("fair", "Fair air quality"),
            AQICategory("moderate", "Moderate air quality"),
            AQICategory("poor", "Poor air quality"),
            AQICategory("very_poor", "Very poor air quality"),
            AQICategory("extremely_poor", "Extremely poor air quality"),
        ],
        "ecu_quitoambiente": [
            AQICategory("desirable", "Desirable air quality"),
            AQICategory("acceptable", "Acceptable air quality"),
            AQICategory("precautionary", "Precautionary level"),
            AQICategory("alert", "Alert level"),
            AQICategory("alarm", "Alarm level"),
            AQICategory("emergency", "Emergency level"),
        ],
        "esp_madrid": [
            AQICategory("good", "Good air quality"),
            AQICategory("acceptable", "Acceptable air quality"),
            AQICategory("poor", "Poor air quality"),
            AQICategory("bad", "Bad air quality"),
        ],
        "esp_miteco": [
            AQICategory("good", "Good air quality"),
            AQICategory("reasonably_good", "Reasonably good air quality"),
            AQICategory("regular", "Regular air quality"),
            AQICategory("unfavorable", "Unfavorable air quality"),
            AQICategory("very_unfavorable", "Very unfavorable air quality"),
            AQICategory("extremely_unfavorable", "Extremely unfavorable air quality"),
        ],
        "est_ekuk": [
            AQICategory("very_good", "Very Good air quality"),
            AQICategory("good", "Good air quality"),
            AQICategory("medium", "Medium air quality"),
            AQICategory("bad", "Bad air quality"),
            AQICategory("very_bad", "Very Bad air quality"),
        ],
        "fin_hsy": [
            AQICategory("good", "Good air quality"),
            AQICategory("satisfactory", "Satisfactory air quality"),
            AQICategory("fair", "Fair air quality"),
            AQICategory("poor", "Poor air quality"),
            AQICategory("very_poor", "Very poor air quality"),
        ],
        "fra_atmo": [
            AQICategory("good", "Good air quality"),
            AQICategory("medium", "Medium air quality"),
            AQICategory("degraded", "Degraded air quality"),
            AQICategory("bad", "Bad air quality"),
            AQICategory("very_bad", "Very bad air quality"),
            AQICategory("extremely_bad", "Extremely bad air quality"),
        ],
        "gbr_defra": [
            AQICategory("low_air_pollution", "Low air pollution"),
            AQICategory("moderate_air_pollution", "Moderate air pollution"),
            AQICategory("high_air_pollution", "High air pollution"),
            AQICategory("very_high_air_pollution", "Very high air pollution"),
        ],
        "gib_gea": [
            AQICategory("low_air_pollution", "Low air pollution"),
            AQICategory("moderate_air_pollution", "Moderate air pollution"),
            AQICategory("high_air_pollution", "High air pollution"),
            AQICategory("very_high_air_pollution", "Very high air pollution"),
        ],
        "hkg_epd": [
            AQICategory("low_air_pollution", "Low air pollution"),
            AQICategory("moderate_air_pollution", "Moderate air pollution"),
            AQICategory("high_air_pollution", "High air pollution"),
            AQICategory("very_high_air_pollution", "Very high air pollution"),
            AQICategory("serious_air_pollution", "Serious air pollution"),
        ],
        "hrv_azo": [
            AQICategory("very_low_air_pollution", "Very low air pollution"),
            AQICategory("low_air_pollution", "Low air pollution"),
            AQICategory("medium_air_pollution", "Medium air pollution"),
            AQICategory("high_air_pollution", "High air pollution"),
            AQICategory("very_high_air_pollution", "Very high air pollution"),
        ],
        "hun_bler": [
            AQICategory("low_air_pollution", "Low air pollution"),
            AQICategory("medium_air_pollution", "Medium air pollution"),
            AQICategory("high_air_pollution", "High air pollution"),
            AQICategory("very_high_air_pollution", "Very high air pollution"),
        ],
        "idn_menlhk": [
            AQICategory("good", "Good air quality"),
            AQICategory("moderate", "Moderate air quality"),
            AQICategory("unhealthy", "Unhealthy air quality"),
            AQICategory("very_unhealthy", "Very unhealthy air quality"),
            AQICategory("hazardous", "Hazardous air quality"),
        ],
        "ind_cpcb": [
            AQICategory("good", "Good air quality"),
            AQICategory("satisfactory", "Satisfactory air quality"),
            AQICategory("moderate", "Moderate air quality"),
            AQICategory("poor", "Poor air quality"),
            AQICategory("very_poor", "Very poor air quality"),
            AQICategory("severe", "Severe air quality"),
        ],
        "irl_epa": [
            AQICategory("good", "Good air quality"),
            AQICategory("fair", "Fair air quality"),
            AQICategory("poor", "Poor air quality"),
            AQICategory("very_poor", "Very poor air quality"),
        ],
        "isr_moep": [
            AQICategory("good", "Good air quality"),
            AQICategory("medium_air_pollution", "Medium air pollution"),
            AQICategory("high_air_pollution", "High air pollution"),
            AQICategory("very_high_air_pollution", "Very high air pollution"),
        ],
        "ita_moniqa": [
            AQICategory("good", "Good air quality"),
            AQICategory("fair", "Fair air quality"),
            AQICategory("moderate", "Moderate air quality"),
            AQICategory("poor", "Poor air quality"),
            AQICategory("bad", "Bad air quality"),
        ],
        "jpn_aeros": [
            AQICategory("1_blue", "1 - Blue"),
            AQICategory("2_cyan", "2 - Cyan"),
            AQICategory("3_green", "3 - Green"),
            AQICategory("4_yellow_watch", "4 - Yellow/Watch"),
            AQICategory("5_orange_alert", "5 - Orange/Alert"),
            AQICategory("6_red_alert", "6 - Red/Alert+"),
        ],
        "kor_airkorea": [
            AQICategory("good", "Good air quality"),
            AQICategory("moderate", "Moderate air quality"),
            AQICategory("unhealthy", "Unhealthy air quality"),
            AQICategory("very_unhealthy", "Very unhealthy air quality"),
        ],
        "kwt_beatona": [
            AQICategory("very_good", "Very good air quality"),
            AQICategory("good", "Good air quality"),
            AQICategory("moderate", "Moderate air quality"),
            AQICategory("bad", "Bad air quality"),
            AQICategory("very_bad", "Very bad air quality"),
        ],
        "lie_cerclair": [
            AQICategory("low_air_pollution", "Low air pollution"),
            AQICategory("moderate_air_pollution", "Moderate air pollution"),
            AQICategory("evident_air_pollution", "Evident air pollution"),
            AQICategory("considerable_air_pollution", "Considerable air pollution"),
            AQICategory("high_air_pollution", "High air pollution"),
            AQICategory("very_high_air_pollution", "Very high air pollution"),
        ],
        "ltu_gamta": [
            AQICategory("very_low_air_pollution", "Very low air pollution"),
            AQICategory("low_air_pollution", "Low air pollution"),
            AQICategory("average_air_pollution", "Average air pollution"),
            AQICategory("high_air_pollution", "High air pollution"),
            AQICategory("very_high_air_pollution", "Very high air pollution"),
        ],
        "lux_emwelt": [
            AQICategory("excellent", "Excellent air quality"),
            AQICategory("very_good", "Very good air quality"),
            AQICategory("good", "Good air quality"),
            AQICategory("fairly_good", "Fairly good air quality"),
            AQICategory("moderate", "Moderate air quality"),
            AQICategory("poor", "Poor air quality"),
            AQICategory("very_poor", "Very poor air quality"),
            AQICategory("bad", "Bad air quality"),
            AQICategory("very_bad", "Very bad air quality"),
            AQICategory("horrible", "Horrible air quality"),
        ],
        "mex_cdmx": [
            AQICategory("good", "Good air quality"),
            AQICategory("regular", "Regular air quality"),
            AQICategory("poor", "Poor air quality"),
            AQICategory("very_poor", "Very poor air quality"),
            AQICategory("extremely_poor", "Extremely poor air quality"),
            AQICategory("hazardous", "Hazardous air quality"),
        ],
        "mex_gto": [
            AQICategory("good", "Good air quality"),
            AQICategory("satisfactory", "Satisfactory air quality"),
            AQICategory("unsatisfactory", "Unsatisfactory air quality"),
            AQICategory("bad", "Bad air quality"),
            AQICategory("very_bad", "Very bad air quality"),
        ],
        "mex_icars": [
            AQICategory("good", "Good air quality"),
            AQICategory("acceptable", "Acceptable air quality"),
            AQICategory("poor", "Poor air quality"),
            AQICategory("very_poor", "Very poor air quality"),
            AQICategory("extremely_poor", "Extremely poor air quality"),
        ],
        "mkd_moepp": [
            AQICategory("very_low", "Very low air pollution"),
            AQICategory("low", "Low air pollution"),
            AQICategory("medium", "Medium air pollution"),
            AQICategory("high", "High air pollution"),
            AQICategory("very_high", "Very high air pollution"),
        ],
        "mng_eic": [
            AQICategory("clean", "Clean"),
            AQICategory("normal", "Normal"),
            AQICategory("low", "Low pollution"),
            AQICategory("moderate", "Moderate pollution"),
            AQICategory("high", "High pollution"),
            AQICategory("very_high", "Very High pollution"),
        ],
        "mng_ubgov": [
            AQICategory("clean", "Clean"),
            AQICategory("normal", "Normal"),
            AQICategory("slightly_polluted", "Slightly Polluted"),
            AQICategory("polluted", "Polluted"),
            AQICategory("heavily_polluted", "Heavily Polluted"),
            AQICategory("seriously_polluted", "Seriously Polluted"),
        ],
        "mys_doe": [
            AQICategory("good", "Good air quality"),
            AQICategory("moderate", "Moderate air quality"),
            AQICategory("unhealthy", "Unhealthy air quality"),
            AQICategory("very_unhealthy", "Very unhealthy air quality"),
            AQICategory("hazardous", "Hazardous air quality"),
        ],
        "nld_rivm": [
            AQICategory("good", "Good air quality"),
            AQICategory("moderate", "Moderate air quality"),
            AQICategory("bad", "Bad air quality"),
            AQICategory("very_bad", "Very bad air quality"),
        ],
        "nor_nilu": [
            AQICategory("low", "Low air pollution"),
            AQICategory("moderate", "Moderate air pollution"),
            AQICategory("high", "High air pollution"),
            AQICategory("very_high", "Very high air pollution"),
        ],
        "npl_doenv": [
            AQICategory("good", "Good air quality"),
            AQICategory("satisfactory", "Satisfactory air quality"),
            AQICategory("moderately_polluted", "Moderately polluted"),
            AQICategory("poor", "Poor air quality"),
            AQICategory("very_poor", "Very poor air quality"),
            AQICategory("severe", "Severe air quality"),
        ],
        "nzl_lawa": [
            AQICategory("below_10", "Less than 10% of guideline"),
            AQICategory("10_33", "10-33% of guideline"),
            AQICategory("33_66", "33-66% of guideline"),
            AQICategory("66_100", "66-100% of guideline"),
            AQICategory("greater_100", "Greater than 100% of guideline"),
        ],
        "per_infoaire": [
            AQICategory("good", "Good air quality"),
            AQICategory("moderate", "Moderate air quality"),
            AQICategory("bad", "Bad air quality"),
            AQICategory("alert", "Alert threshold"),
        ],
        "phl_emb": [
            AQICategory("good", "Good air quality"),
            AQICategory("fair", "Fair air quality"),
            AQICategory(
                "unhealthy_sensitive", "Unhealthy air quality for sensitive groups"
            ),
            AQICategory("very_unhealthy", "Very unhealthy air quality"),
            AQICategory("acutely_unhealthy", "Acutely unhealthy air quality"),
            AQICategory("emergency", "Emergency"),
        ],
        "pol_gios": [
            AQICategory("very_good", "Very good air quality"),
            AQICategory("good", "Good air quality"),
            AQICategory("moderate", "Moderate air quality"),
            AQICategory("sufficient", "Sufficient air quality"),
            AQICategory("bad", "Bad air quality"),
            AQICategory("very_bad", "Very bad air quality"),
        ],
        "prt_qualar": [
            AQICategory("very_good", "Very good air quality"),
            AQICategory("good", "Good air quality"),
            AQICategory("moderate", "Moderate air quality"),
            AQICategory("low", "Low air quality"),
            AQICategory("bad", "Bad air quality"),
        ],
        "rou_calitateaer": [
            AQICategory("excellent", "Excellent air quality"),
            AQICategory("very_good", "Very good air quality"),
            AQICategory("good", "Good air quality"),
            AQICategory("moderate", "Moderate air quality"),
            AQICategory("bad", "Bad air quality"),
            AQICategory("very_bad", "Very bad air quality"),
        ],
        "sgp_nea": [
            AQICategory("good", "Good air quality"),
            AQICategory("moderate", "Moderate air quality"),
            AQICategory("unhealthy", "Unhealthy air quality"),
            AQICategory("very_unhealthy", "Very unhealthy air quality"),
            AQICategory("hazardous", "Hazardous air quality"),
        ],
        "srb_sepa": [
            AQICategory("excellent", "Excellent"),
            AQICategory("good", "Good"),
            AQICategory("acceptable", "Acceptable"),
            AQICategory("polluted", "Polluted"),
            AQICategory("very_polluted", "Very Polluted"),
        ],
        "svk_shmu": [
            AQICategory("very_good", "Very good air quality"),
            AQICategory("good", "Good air quality"),
            AQICategory("moderate", "Moderate air quality"),
            AQICategory("bad", "Bad air quality"),
            AQICategory("very_bad", "Very bad air quality"),
        ],
        "tha_pcd": [
            AQICategory("excellent", "Excellent air quality"),
            AQICategory("satisfactory", "Satisfactory air quality"),
            AQICategory("moderate", "Moderate air quality"),
            AQICategory("unhealthy", "Unhealthy air quality"),
            AQICategory("very_unhealthy", "Very unhealthy air quality"),
        ],
        "tur_havaizleme": [
            AQICategory("good", "Good air quality"),
            AQICategory("moderate", "Moderate air quality"),
            AQICategory(
                "unhealthy_sensitive", "Unhealthy for sensitive groups air quality"
            ),
            AQICategory("unhealthy", "Unhealthy air quality"),
            AQICategory("poor", "Poor air quality"),
            AQICategory("hazardous", "Hazardous air quality"),
        ],
        "twn_epa": [
            AQICategory("good", "Good air quality"),
            AQICategory("moderate", "Moderate air quality"),
            AQICategory(
                "unhealthy_sensitive", "Unhealthy air quality for sensitive groups"
            ),
            AQICategory("unhealthy", "Unhealthy air quality"),
            AQICategory("very_unhealthy", "Very unhealthy air quality"),
            AQICategory("hazardous", "Hazardous air quality"),
        ],
        "usa_epa": [
            AQICategory("good", "Good air quality"),
            AQICategory("moderate", "Moderate air quality"),
            AQICategory(
                "unhealthy_sensitive", "Unhealthy air quality for sensitive groups"
            ),
            AQICategory("unhealthy", "Unhealthy air quality"),
            AQICategory("very_unhealthy", "Very unhealthy air quality"),
            AQICategory("hazardous", "Hazardous air quality"),
        ],
        "usa_epa_nowcast": [
            AQICategory("good", "Good air quality"),
            AQICategory("moderate", "Moderate air quality"),
            AQICategory(
                "unhealthy_sensitive", "Unhealthy air quality for sensitive groups"
            ),
            AQICategory("unhealthy", "Unhealthy air quality"),
            AQICategory("very_unhealthy", "Very unhealthy air quality"),
            AQICategory("hazardous", "Hazardous air quality"),
        ],
        "vnm_vea": [
            AQICategory("good", "Good air quality"),
            AQICategory("average", "Average air quality"),
            AQICategory("poor", "Poor air quality"),
            AQICategory("bad", "Bad air quality"),
            AQICategory("very_bad", "Very Bad air quality"),
            AQICategory("hazardous", "Hazardous air quality"),
        ],
    }

    @classmethod
    def get(cls, code: str) -> list[AQICategory] | None:
        """Return the AQI categories for a given code."""
        return cls._mapping.get(code)

    @classmethod
    def get_all(cls) -> list[AQICategory]:
        """Return all AQI categories across all mappings."""
        categories = []
        for entries in cls._mapping.values():
            categories.extend(entries)
        return categories


@dataclass
class Concentration(DataClassDictMixin):
    """Represents a pollutant concentration."""

    value: float
    units: str


@dataclass
class Pollutant(DataClassDictMixin):
    """Represents a pollutant with metadata."""

    code: str
    display_name: str = field(metadata={"alias": "displayName"})
    full_name: str = field(metadata={"alias": "fullName"})
    concentration: Concentration


class PollutantList(list[Pollutant]):
    """Allows attribute access by pollutant code."""

    def __getattr__(self, name: str) -> Pollutant:
        """Enable dynamic access to pollutants via attribute name (case-insensitive)."""
        name = name.lower()
        for pollutant in self:
            if pollutant.code.lower() == name:
                return pollutant
        message = f"No pollutant named {name!r}"
        raise AttributeError(message)


@dataclass
class Color(DataClassDictMixin):
    """Represents RGB color components."""

    red: float | None = None
    green: float | None = None
    blue: float | None = None


@dataclass
class Index(DataClassDictMixin):
    """Represents an air quality index entry."""

    code: str
    display_name: str = field(metadata={"alias": "displayName"})
    color: Color
    category: str = field(
        metadata=field_options(deserialize=lambda x: sub(r"\s+", "_", x.lower()))
    )
    dominant_pollutant: str = field(metadata={"alias": "dominantPollutant"})
    aqi: int | None = None
    aqi_display: str | None = field(default=None, metadata={"alias": "aqiDisplay"})

    @property
    def category_options(self) -> list[str] | None:
        """Return the options for the index category."""
        raw = AQICategoryMapping.get(self.code)
        if raw is None:
            return None
        return [cat.original for cat in raw]


class IndexList(list[Index]):
    """Allows attribute access by index code."""


@dataclass
class AirQualityData(DataClassJSONMixin):
    """Holds air quality data with timestamp and region."""

    date_time: datetime = field(metadata={"alias": "dateTime"})
    region_code: str = field(metadata={"alias": "regionCode"})
    _indexes: list[Index] = field(metadata={"alias": "indexes"})
    _pollutants: list[Pollutant] = field(metadata={"alias": "pollutants"})

    @property
    def indexes(self) -> IndexList:
        """Returns list of indexes with attribute access."""
        return IndexList(self._indexes)


@dataclass
class UserInfoResult(DataClassJSONMixin):
    """Response from getting user info."""

    id: str
    """User ID."""

    name: str
    """User name."""


@dataclass
class Error:
    """Error details from the API response."""

    status: str | None = None
    code: int | None = None
    message: str | None = None
    details: list[dict[str, Any]] | None = field(default_factory=list)

    def __str__(self) -> str:
        """Return a string representation of the error details."""
        error_message = ""
        if self.status:
            error_message += self.status
        if self.code:
            if error_message:
                error_message += f" ({self.code})"
            else:
                error_message += str(self.code)
        if self.message:
            if error_message:
                error_message += ": "
            error_message += self.message
        if self.details:
            error_message += f"\nError details: ({self.details})"
        return error_message


@dataclass
class ErrorResponse(DataClassJSONMixin):
    """A response message that contains an error message."""

    error: Error | None = None
