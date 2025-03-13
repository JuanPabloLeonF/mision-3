from flask import json
import pandas as pd
import plotly.express as px
from datetime import datetime
import pytz
from app.configuration.api_configuration import openmeteo, url
from app.utils.utils_date import UtilDate


class ApiExternalUtil:

    @staticmethod
    def callApiOpenmeteo(params: dict):
        response = openmeteo.weather_api(url, params=params)
        return response[0]

    @staticmethod
    def createDataframeWithHourly(params: dict):

        hourly = ApiExternalUtil.callApiOpenmeteo(params=params)
        hourly = hourly.Hourly()
        hourly_temperature_2m = hourly.Variables(0).ValuesAsNumpy()
        hourly_precipitation_probability = hourly.Variables(1).ValuesAsNumpy()
        hourly_precipitation = hourly.Variables(2).ValuesAsNumpy()
        hourly_cloudcover = hourly.Variables(3).ValuesAsNumpy()

        hourly_data = {
            "date": pd.date_range(
                start=pd.to_datetime(hourly.Time(), unit="s", utc=True),
                end=pd.to_datetime(hourly.TimeEnd(), unit="s", utc=True),
                freq=pd.Timedelta(seconds=hourly.Interval()),
                inclusive="left"
            ),
            "temperature_2m": hourly_temperature_2m,
            "precipitation_probability": hourly_precipitation_probability,
            "precipitation": hourly_precipitation,
            "cloudcover": hourly_cloudcover
        }

        df = pd.DataFrame(data=hourly_data)
        df["day"] = df["date"].dt.date
        df_grouped = df.groupby("day").mean()

        df_grouped["sunny_percentage"] = 100 - (
                    (df_grouped["cloudcover"] * 0.7) + (df_grouped["precipitation_probability"] * 0.3))
        df_grouped["sunny_percentage"] = df_grouped["sunny_percentage"].clip(0, 100)

        day_translation = {
            "Monday": "Lunes",
            "Tuesday": "Martes",
            "Wednesday": "Miércoles",
            "Thursday": "Jueves",
            "Friday": "Viernes",
            "Saturday": "Sábado",
            "Sunday": "Domingo"
        }

        df_grouped["day_name"] = pd.to_datetime(df_grouped.index).strftime("%A").map(day_translation)

        days_order = ["Lunes", "Martes", "Miércoles", "Jueves", "Viernes", "Sábado", "Domingo"]
        df_grouped["day_name"] = pd.Categorical(df_grouped["day_name"], categories=days_order, ordered=True)
        df_grouped = df_grouped.sort_values("day_name")

        return df_grouped

    @staticmethod
    def createPlotlyGraph(dfGrouped, weatherType: str):
        if weatherType == "sunny":
            values = dfGrouped["sunny_percentage"]
            label = "Probabilidad (%)"
            border_color = "gold"
            color = "gold"
        elif weatherType == "cloudy":
            values = dfGrouped["cloudcover"]
            label = "Probabilidad (%)"
            border_color = "gray"
            color = "gray"
        elif weatherType == "rainy":
            values = dfGrouped["precipitation_probability"]
            label = "Probabilidad (%)"
            border_color = "blue"
            color = "blue"
        else:
            raise ValueError("Invalid weather type")

        dfGrouped["temperature_celsius"] = dfGrouped["temperature_2m"].apply(lambda x: f"{x:.1f}°C")

        if weatherType == "sunny":
            weatherType = "soleado"

        if weatherType == "cloudy":
            weatherType = "nublado"

        if weatherType == "rainy":
            weatherType = "lluvioso"

        dfGrouped["tooltip_text"] = dfGrouped.apply(
            lambda
                row: f"El día {row["day_name"]} tendrá una probabilidad del {values.loc[row.name]:.2f}% de estar {weatherType} "
                     f"con una posible temperatura de {row['temperature_celsius']}", axis=1
        )

        fig = px.bar(
            dfGrouped,
            x="day_name",
            y=values,
            text=dfGrouped["temperature_celsius"],
            color_discrete_sequence=[color],
            title=f"{weatherType.capitalize()}",
            custom_data=[dfGrouped["tooltip_text"]]
        )

        fig.update_traces(
            marker=dict(
                color="rgba(0,0,0,0)",
                line=dict(color=border_color, width=1)
            ),
            textposition='outside',
            hovertemplate="%{customdata}"
        )

        fig.update_layout(
            autosize=True,
            width=None,
            height=None,
            plot_bgcolor="rgba(0,0,0,0)",
            paper_bgcolor="rgba(0,0,0,0)",
            font=dict(color="white"),
            xaxis=dict(
                title="Días de la semana",
                color="white",
                showgrid=False
            ),
            yaxis=dict(
                title=label,
                color="white",
                range=[0, 100],
                showgrid=False,
                gridcolor="gray"
            )
        )


        return json.loads(fig.to_json())

    @staticmethod
    def getCurrentWeather(params: dict, timeZone: str) -> dict:
        weatherData = ApiExternalUtil.callApiOpenmeteo(params=params)

        hourly = weatherData.Hourly()
        hourlyTemperature2m = hourly.Variables(0).ValuesAsNumpy()

        hourlyData = {"date": pd.date_range(
            start=pd.to_datetime(hourly.Time(), unit="s", utc=True),
            end=pd.to_datetime(hourly.TimeEnd(), unit="s", utc=True),
            freq=pd.Timedelta(seconds=hourly.Interval()),
            inclusive="left"
        )}

        hourlyData["temperature_2m"] = hourlyTemperature2m
        hourlyDataframe = pd.DataFrame(data=hourlyData)

        daily = weatherData.Daily()
        dailyTemperature2mMax = daily.Variables(0).ValuesAsNumpy()
        dailyTemperature2mMin = daily.Variables(1).ValuesAsNumpy()

        dailyData = {"date": pd.date_range(
            start=pd.to_datetime(daily.Time(), unit="s", utc=True),
            end=pd.to_datetime(daily.TimeEnd(), unit="s", utc=True),
            freq=pd.Timedelta(seconds=daily.Interval()),
            inclusive="left"
        )}

        dailyData["temperature_2m_max"] = dailyTemperature2mMax
        dailyData["temperature_2m_min"] = dailyTemperature2mMin
        dailyDataframe = pd.DataFrame(data=dailyData)

        nowLocal, timezone = UtilDate.getHourCurrentLocal(timeZone=timeZone)
        nowLocal.strftime("%Y-%m-%d %I:%M %p %Z")

        hourlyDataframe["date"] = hourlyDataframe["date"].dt.tz_convert(timezone)
        currentTempRow = hourlyDataframe[hourlyDataframe["date"].dt.date == nowLocal.date()]

        if not currentTempRow.empty:
            currentTemp = currentTempRow.iloc[0]["temperature_2m"]
        else:
            currentTemp = None

        dailyDataframe["date"] = dailyDataframe["date"].dt.tz_convert(timezone)
        currentDayTemp = dailyDataframe[dailyDataframe["date"].dt.date == nowLocal.date()]

        if not currentDayTemp.empty:
            tempMax = currentDayTemp.iloc[0]["temperature_2m_max"]
            tempMin = currentDayTemp.iloc[0]["temperature_2m_min"]
        else:
            tempMax, tempMin = None, None

        if currentTemp is not None:
            if currentTemp > 30:
                weatherType = "soleado"
            elif currentTemp < 15:
                weatherType = "frío"
            else:
                weatherType = "templado"
        else:
            weatherType = "desconocido"

        dayTranslation = {
            "Monday": "Lunes", "Tuesday": "Martes", "Wednesday": "Miércoles",
            "Thursday": "Jueves", "Friday": "Viernes", "Saturday": "Sábado", "Sunday": "Domingo"
        }
        currentDay = dayTranslation[nowLocal.strftime("%A")]
        currentHour = nowLocal.strftime("%I:%M %p")

        response = {
            "day": currentDay,
            "hour": currentHour,
            "temperature": f"{currentTemp:.1f}°C" if currentTemp is not None else "N/A",
            "temperatureMax": f"{tempMax:.1f}°C" if tempMax is not None else "N/A",
            "temperatureMin": f"{tempMin:.1f}°C" if tempMin is not None else "N/A",
            "weather": weatherType
        }

        return response