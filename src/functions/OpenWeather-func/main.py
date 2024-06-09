import base64
import json
import os
import random
from datetime import datetime

import functions_framework
import pytz
import requests
from google.cloud import pubsub_v1

project_id = os.getenv("GCP_PROJECT_ID")
topic_id = os.getenv("PUBSUB_TOPIC_ID")
publisher = pubsub_v1.PublisherClient()
topic_path = publisher.topic_path(project_id, topic_id)


def generate_weather_data(city, location):
    results = {
        'location': [],
        'timestamp': [],
        'time': [],
        'temperature': [],
        'humidity': [],
        'apparent_temperature': [],
        'rain': [],
        'weather': [],
        'surface_pressure': [],
        'cloud_cover': [],
        'wind_speed': []
    }
    params = {
        'lat': location[0],
        'lon': location[1],
        'appid': '0ab6b3dd1c466a7045c579e3182f855b',
        'units': 'metric'
    }
    current_data = requests.get('https://api.openweathermap.org/data/2.5/weather', params=params).json()

    results['location'].append(city)
    results['timestamp'] = datetime.now(pytz.utc).isoformat()
    results['time'].append(datetime.fromtimestamp(current_data['dt'], pytz.utc).isoformat())
    results['temperature'].append(current_data['main']['temp'])
    results['humidity'].append(current_data['main']['humidity'])
    results['apparent_temperature'].append(current_data['main']['feels_like'])
    results['rain'].append(current_data.get('rain', {}).get('1h', 0))
    results['weather'].append(current_data['weather'][0]['description'].capitalize())
    results['surface_pressure'].append(current_data['main']['pressure'])
    results['cloud_cover'].append(current_data['clouds']['all'])
    results['wind_speed'].append(current_data['wind']['speed'])

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
    for city, postion in location:
        data = generate_weather_data(city, location)
        message_id = publish_to_pubsub(data)
        print(f"Published data to Pub/Sub with message ID: {message_id}")


@functions_framework.cloud_event
def cloud_function_entry_point(cloud_event):
    trigger_data = base64.b64decode(cloud_event.data["message"]["data"])
    print(f"Cloud Event Trigger Data: {trigger_data}")
    main()
    return "Data generated and processed successfully."
