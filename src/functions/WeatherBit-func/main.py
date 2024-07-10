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
        'lat': location[0],
        'lon': location[1],
        'key': 'b796f2836a134645b84af9573dbaf150',
        'hours': 120
    }

    current_response = requests.get('https://api.weatherbit.io/v2.0/current', params=params).json()
    current_data = current_response['data'][0]

    results['location'] = city
    results['timestamp'] = datetime.now(pytz.utc).isoformat()
    results['time'] = datetime.strptime(current_data['ob_time'], '%Y-%m-%d %H:%M').strftime('%d %b, %H:%M')
    results['temperature'] = current_data['temp']
    results['humidity'] = current_data['rh']
    results['apparent_temperature'] = current_data['app_temp']
    results['rain'] = current_data['precip']
    results['weather'] = current_data['weather']['description']
    results['surface_pressure'] = current_data['pres']
    results['cloud_cover'] = current_data['clouds']
    results['wind_speed'] = current_data['wind_spd']


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
