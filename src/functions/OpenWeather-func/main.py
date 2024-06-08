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
    location = {"Milano": (45.4685, 9.1824), "Warszawa": (52.2297, 21.0122), "Vienna": (48.2090, 16.3728)}
    results = {}

    for city, pos in location.items():
        params = {
            'lat': pos[0],
            'lon': pos[1],
            'appid': '0ab6b3dd1c466a7045c579e3182f855b',
            'units': 'metric'
        }
        forecast_data = requests.get('http://api.openweathermap.org/data/2.5/forecast', params=params).json()
        current_data = requests.get('https://api.openweathermap.org/data/2.5/weather', params=params).json()
        name = forecast_data['city']['name']
        forecast_data = forecast_data['list']

        forecast = {key: [] for key in
                    ['Time', 'Temperature', 'Apparent temperature', 'Humidity', 'Precipitation', 'Rain', 'Weather',
                     'Surface pressure', 'Cloud cover', 'Wind speed']}

        for item in forecast_data:
            forecast['Time'].append(datetime.fromtimestamp(item['dt']).strftime('%d %b, %H:%M'))
            forecast['Temperature'].append(item['main']['temp'])
            forecast['Apparent temperature'].append(item['main']['feels_like'])
            forecast['Humidity'].append(item['main']['humidity'])
            forecast['Precipitation'].append(item['pop'] * 100)
            forecast['Rain'].append(item.get('rain', {}).get('3h', 0))
            forecast['Weather'].append(item['weather'][0]['description'].capitalize())
            forecast['Surface pressure'].append(item['main']['grnd_level'])
            forecast['Cloud cover'].append(item['clouds']['all'])
            forecast['Wind speed'].append(item['wind']['speed'])

        current = {
            'Time': datetime.fromtimestamp(current_data['dt']).strftime('%d %b, %H:%M'),
            'Temperature': current_data['main']['temp'],
            'Apparent temperature': current_data['main']['feels_like'],
            'Humidity': current_data['main']['humidity'],
            'Rain': current_data.get('rain', {}).get('1h', 0),
            'Weather': current_data['weather'][0]['description'].capitalize(),
            'Surface pressure': current_data['main']['pressure'],
            'Cloud cover': current_data['clouds']['all'],
            'Wind speed': current_data['wind']['speed'],
        }
        results[name] = (current, forecast)

    # return name, forecast, current
    return results


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