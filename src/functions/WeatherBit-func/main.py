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





def generate_weather_data():
    params = {
        'lat': 45.4685,
        'lon': 9.1824,
        'key': 'b796f2836a134645b84af9573dbaf150',
        'hours': 120
    }

    forecast_response = requests.get('https://api.weatherbit.io/v2.0/forecast/hourly', params=params).json()
    current_response = requests.get('https://api.weatherbit.io/v2.0/current', params=params).json()

    forecast_data = forecast_response['data']
    current_data = current_response['data'][0]

    forecast = {key: [] for key in
                ['Time', 'Temperature', 'Apparent temperature', 'Humidity', 'Precipitation', 'Rain', 'Weather',
                 'Surface pressure', 'Cloud cover', 'Wind speed']}

    for item in forecast_data:
        forecast['Time'].append(datetime.fromtimestamp(item['ts']).strftime('%d %b, %H:%M'), )
        forecast['Temperature'].append(item['temp'])
        forecast['Apparent temperature'].append(item['app_temp'])
        forecast['Humidity'].append(item['rh'])
        forecast['Precipitation'].append(item['pop'])
        forecast['Rain'].append(item['precip'])
        forecast['Weather'].append(item['weather']['description'])
        forecast['Surface pressure'].append(item['pres'])
        forecast['Cloud cover'].append(item['clouds'])
        forecast['Wind speed'].append(item['wind_spd'])

    current = {
        'Time': datetime.strptime(current_data['ob_time'], '%Y-%m-%d %H:%M').strftime('%d %b, %H:%M'),
        'Temperature': current_data['temp'],
        'Apparent temperature': current_data['app_temp'],
        'Humidity': current_data['rh'],
        'Rain': current_data['precip'],
        'Weather': current_data['weather']['description'],
        'Surface pressure': current_data['pres'],
        'Cloud cover': current_data['clouds'],
        'Wind speed': current_data['wind_spd'],
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