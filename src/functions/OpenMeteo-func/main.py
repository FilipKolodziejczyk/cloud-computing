import base64
import json
import os
import pandas as pd
import random
from datetime import datetime

import functions_framework
import pytz
import requests
import openmeteo_requests
from retry_requests import retry
from google.cloud import pubsub_v1
import requests_cache

project_id = os.getenv("GCP_PROJECT_ID")
topic_id = os.getenv("PUBSUB_TOPIC_ID")
publisher = pubsub_v1.PublisherClient()
topic_path = publisher.topic_path(project_id, topic_id)





def generate_weather_data():
    cache_session = requests_cache.CachedSession('.cache', expire_after=3600)
    retry_session = retry(cache_session, retries=5, backoff_factor=0.2)
    openmeteo = openmeteo_requests.Client(session=retry_session)

    params = {
        'lat': 45.4685,
        'lon': 9.1824,
        "hourly": ["temperature_2m", "apparent_temperature", "relative_humidity_2m",
                   "precipitation", "rain", "weather_code", "surface_pressure",
                   "cloud_cover", "wind_speed_10m", "wind_direction_10m"],
        "current": ["temperature_2m", "apparent_temperature", "relative_humidity_2m",
                    "precipitation", "rain", "weather_code", "surface_pressure",
                    "cloud_cover", "wind_speed_10m", "wind_direction_10m"],
        "wind_speed_unit": "ms",
        "timeformat": "unixtime"
    }

    response = openmeteo.weather_api('https://api.open-meteo.com/v1/forecast', params=params)[0]

    forecast_data = response.Hourly()
    current_data = response.Current()

    times = pd.date_range(start=datetime.fromtimestamp(forecast_data.Time(), tz=response.Timezone()),
                          end=datetime.fromtimestamp(forecast_data.TimeEnd(), tz=response.Timezone()),
                          freq=pd.Timedelta(seconds=forecast_data.Interval()),
                          inclusive='left')

    forecast = {
        'Time': times.strftime('%d %b, %H:%M').tolist(),
        'Temperature': forecast_data.Variables(0).ValuesAsNumpy().tolist(),
        'Apparent temperature': forecast_data.Variables(1).ValuesAsNumpy().tolist(),
        'Humidity': forecast_data.Variables(2).ValuesAsNumpy().tolist(),
        'Precipitation': forecast_data.Variables(3).ValuesAsNumpy().tolist(),
        'Rain': forecast_data.Variables(4).ValuesAsNumpy().tolist(),
        'Weather': [forecast_data.Variables(5).ValuesAsNumpy().tolist()],
        'Surface pressure': forecast_data.Variables(6).ValuesAsNumpy().tolist(),
        'Cloud cover': forecast_data.Variables(7).ValuesAsNumpy().tolist(),
        'Wind speed': forecast_data.Variables(8).ValuesAsNumpy().tolist(),
        'Wind direction': forecast_data.Variables(9).ValuesAsNumpy().tolist()
    }

    current = {
        'Time': datetime.fromtimestamp(current_data.Time(), tz=response.Timezone()).strftime('%d %b, %H:%M'),
        'Temperature': round(current_data.Variables(0).Value(), 2),
        'Apparent temperature': round(current_data.Variables(1).Value(), 2),
        'Humidity': round(current_data.Variables(2).Value(), 2),
        'Precipitation': round(current_data.Variables(3).Value(), 2),
        'Rain': round(current_data.Variables(4).Value(), 2),
        'Weather': current_data.Variables(5).Value(),
        'Surface pressure': round(current_data.Variables(6).Value(), 2),
        'Cloud cover': round(current_data.Variables(7).Value(), 2),
        'Wind speed': round(current_data.Variables(8).Value(), 2),
        'Wind direction': round(current_data.Variables(9).Value(), 2),
    }

    return forecast, current


def publish_to_pubsub(data):
    """Publish data to Pub/Sub and return message ID."""
    data_str = json.dumps(data)
    future = publisher.publish(topic_path, data=data_str.encode("utf-8"))
    return future.result()


def main():
    # TODO: Replace with real data
    for _ in range(5):  # Adjust the range for more or fewer entries
        data = generate_weather_data()
        message_id = publish_to_pubsub(data)
        print(f"Published data to Pub/Sub with message ID: {message_id}")





@functions_framework.cloud_event
def cloud_function_entry_point(cloud_event):
    trigger_data = base64.b64decode(cloud_event.data["message"]["data"])
    print(f"Cloud Event Trigger Data: {trigger_data}")
    main()
    return "Data generated and processed successfully."