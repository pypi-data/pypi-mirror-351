import os
from dotenv import load_dotenv
from datetime import datetime
import requests
import pandas as pd
import pytz

load_dotenv()

def dummy_api_call():
    api_key = os.getenv("API_KEY")
    if not api_key:
        raise ValueError("API_KEY not found in environment variables.")
    return f"Calling API with key: {api_key[:4]}****"



def get_weather_data(
    weather_station="RJAA",
    country_code="JP",
    startDate="20190201",
    endDate="20190301",
    number=2,
    timezone="US/Pacific",
):
    """
    Fetches historical weather data from Weather.com for a specific station and time range.

    Parameters:
        weather_station (str): Weather station ID (e.g., "RJAA").
        country_code (str): Country code (e.g., "JP").
        startDate (str): Start date in 'YYYYMMDD' format.
        endDate (str): End date in 'YYYYMMDD' format.
        number (int): Location type (e.g., 2 for airport stations).
        timezone (str): Timezone name (e.g., "US/Pacific").

    Returns:
        pd.DataFrame: A cleaned and hourly-resampled DataFrame of weather observations,
                      including temperature, dew point, humidity, wind, pressure, and precipitation.

    Notes:
        - Requires an API key set in a .env file as `API_KEY`.
        - Will attempt to backfill and forward-fill missing data.
        - Returns an empty DataFrame if no data is fetched.
    """
    api_key = os.getenv("API_KEY")
    tz = pytz.timezone(timezone)

    # startDate = dateparser.parse(startDate)
    # endDate = dateparser.parse(endDate)
    ends = pd.date_range(start=startDate, end=endDate, freq="M")

    starts = pd.date_range(start=startDate, end=endDate, freq="M")
    starts = [s.replace(day=1) for s in starts]
    s_e = zip(starts, ends)

    weather_dfs = []
    for s, e in s_e:
        s = s.strftime("%Y%m%d")
        e = e.strftime("%Y%m%d")

        endpoint = f"https://api.weather.com/v1/location/{weather_station}:{number}:{country_code}/observations/historical.json?apiKey={api_key}&units=e&startDate={s}&endDate={e}"
        try:
            response = requests.get(endpoint).json()["observations"]
            weather_data = sorted(response, key=lambda k: k["valid_time_gmt"])

            table = []
            for item in weather_data:
                row = [
                    datetime.fromtimestamp(item["valid_time_gmt"], tz),
                    item["temp"],
                    f'{item["dewPt"]}',
                    f'{item["rh"]}',
                    item["wdir_cardinal"],
                    item["wspd"],
                    f'{item["gust"] if item["gust"] else 0}',
                    f'{item["pressure"]}',
                    f'{item["precip_total"] if item["precip_total"] else "0.0"}',
                    item["wx_phrase"],
                ]
                table.append(row)

            columns = [
                "Time",
                "tempf",
                "dewPt",
                "rh",
                "wdir_cardinal",
                "wspd",
                "gust",
                "pressure",
                "precip",
                "wx_phrase",
            ]
            weather_df = pd.DataFrame(table, columns=columns)
            weather_dfs.append(weather_df)
        except Exception:
            pass

    if len(weather_dfs) > 0:
        weather_dfs = pd.concat(weather_dfs)
        try:
            weather_dfs["Time"] = weather_dfs["Time"].dt.ceil("1h")
            # Drop timezone
            weather_dfs["Time"] = weather_dfs["Time"].dt.tz_localize(None)
        except Exception:
            pass

        # Make sure data has no duplicate times (drop, keep last)
        weather_dfs.drop_duplicates(subset=["Time"], keep="last", inplace=True)
        weather_dfs["Time"] = pd.to_datetime(weather_dfs["Time"])
        min_time = weather_dfs.Time.min().normalize()
        max_time = weather_dfs.Time.max()
        weather_dfs = weather_dfs.set_index("Time")
        # Set new index
        dt_range = pd.date_range(min_time, max_time, freq="1h")
        # Fillna
        weather_dfs = weather_dfs.reindex(dt_range).bfill().ffill()

        weather_dfs.reset_index(drop=False, inplace=True)
        weather_dfs.rename({"index": "Time"}, axis=1, inplace=True)

        return weather_dfs
    else:
        return pd.DataFrame()