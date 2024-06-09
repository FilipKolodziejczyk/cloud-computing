import base64
import json
import os
import random
from datetime import datetime

import functions_framework
import pytz
from google.cloud import pubsub_v1

project_id = os.getenv("GCP_PROJECT_ID")
topic_id = os.getenv("PUBSUB_TOPIC_ID")
publisher = pubsub_v1.PublisherClient()
topic_path = publisher.topic_path(project_id, topic_id)


def generate_weather_data():
    """Generate random weather data."""
    locations = ["New York", "Los Angeles", "Chicago", "Houston", "Phoenix"]
    temperature = random.uniform(-20, 40)
    humidity = random.uniform(20, 100)
    location = random.choice(locations)
    timestamp = datetime.now(pytz.utc).isoformat()
    return {
        "temperature": temperature,
        "humidity": humidity,
        "location": location,
        "timestamp": timestamp,
    }


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
