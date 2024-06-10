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


def generate_weather_data(city, location):
    cache_session = requests_cache.CachedSession('.cache', expire_after=3600)
    retry_session = retry(cache_session, retries=5, backoff_factor=0.2)
    openmeteo = openmeteo_requests.Client(session=retry_session)

    results = {
        'location': None,
        'timestamp': None,
        'time': None,
        'temperature': None,
        'humidity': None,
        'apparent_temperature': None,
        'rain': None,
        'weather': None,
        'surface_pressure': None,
        'cloud_cover': None,
        'wind_speed': None
    }

    params = {
        'latitude': location[0],
        'longitude': location[1],
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

    current_data = response.Current()

    results['location'] = city
    results['timestamp'] = datetime.now(pytz.utc).isoformat()
    results['time'] = datetime.fromtimestamp(current_data.Time(), tz=response.Timezone()).strftime('%d %b, %H:%M')
    results['temperature'] = round(current_data.Variables(0).Value(), 2)
    results['humidity'] = round(current_data.Variables(2).Value(), 2)
    results['apparent_temperature'] = round(current_data.Variables(1).Value(), 2)
    results['rain'] = round(current_data.Variables(4).Value(), 2),
    results['weather'] = current_data.Variables(5).Value()
    results['surface_pressure'] = round(current_data.Variables(6).Value(), 2)
    results['cloud_cover'] = round(current_data.Variables(7).Value(), 2)
    results['wind_speed'] = round(current_data.Variables(8).Value(), 2)

    return results


def publish_to_pubsub(data):
    """Publish data to Pub/Sub and return message ID."""
    data_str = json.dumps(data)
    future = publisher.publish(topic_path, data=data_str.encode("utf-8"))
    return future.result()


def main():
    location = {
        "Milan": (45.4685, 9.1824),
        "Warsaw": (52.2297, 21.0122),
        "Paris": (48.8575, 2.3514)
    }
    for city, postion in location.items():
        data = generate_weather_data(city, postion)
        message_id = publish_to_pubsub(data)
        print(f"Published data to Pub/Sub with message ID: {message_id}")


@functions_framework.cloud_event
def cloud_function_entry_point(cloud_event):
    trigger_data = base64.b64decode(cloud_event.data["message"]["data"])
    print(f"Cloud Event Trigger Data: {trigger_data}")
    main()
    return "Data generated and processed successfully."
