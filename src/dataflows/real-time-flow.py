import json
import argparse
import logging
from datetime import datetime
import apache_beam as beam
from apache_beam.io.gcp.bigtableio import WriteToBigTable
from apache_beam.options.pipeline_options import PipelineOptions, SetupOptions
from google.cloud.bigtable.row import DirectRow

# Configure logging
logging.basicConfig(level=logging.INFO, format='%(asctime)s: %(levelname)s: %(message)s')

class ParseJson(beam.DoFn):
    """A DoFn to parse JSON strings into Python dictionaries."""

    def process(self, element):
        try:
            # Parse the JSON string into a Python dictionary
            record = json.loads(element)
            logging.info(f"Successfully parsed JSON: {record}")
            yield record
        except json.JSONDecodeError as e:
            # Log JSON decode errors
            logging.error(f"Error decoding JSON: {e}")
            yield beam.pvalue.TaggedOutput("dead_letter", element)

class CreateDirectRow(beam.DoFn):
    def process(self, element):
        try:
            key = f"{element['location']}_{element['timestamp']}"
            direct_row = DirectRow(row_key=key)
            column_family = "base"
            for qualifier, value in element.items():
                value = str(value)
                direct_row.set_cell(
                    column_family,
                    qualifier.encode("utf-8"),
                    value.encode("utf-8"),
                    timestamp=datetime.utcnow(),
                )
            logging.info(f"Created DirectRow for key: {key}")
            yield direct_row
        except Exception as e:
            logging.error(f"Failed to create DirectRow: {e}")
            raise

def run(argv=None, save_main_session=True):
    parser = argparse.ArgumentParser()
    parser.add_argument("--project_id", help="Google Cloud Project ID.")
    parser.add_argument("--pubsub_subscription", help="Pub/Sub subscription ID (format projects/<project>/subscriptions/<subscription>).")
    parser.add_argument("--bigtable_instance_id", help="Bigtable instance ID.")
    parser.add_argument("--bigtable_table_id", help="Bigtable table ID.")
    args, pipeline_args = parser.parse_known_args(argv)

    pipeline_options = PipelineOptions(pipeline_args)
    pipeline_options.view_as(SetupOptions).save_main_session = save_main_session

    logging.info("Starting pipeline...")
    with beam.Pipeline(options=pipeline_options) as pipeline:
        raw_messages = (
            pipeline
            | "Read From Pub/Sub" >> beam.io.ReadFromPubSub(subscription=args.pubsub_subscription)
            | "UTF-8 Decode" >> beam.Map(lambda x: x.decode("utf-8"))
        )

        parsed_messages = raw_messages | "Parse JSON" >> beam.ParDo(ParseJson())

        transformed_messages = parsed_messages | "Transform Data" >> beam.Map(lambda x: x)  # Replace this with transformation logic

        direct_rows = transformed_messages | "Create DirectRow" >> beam.ParDo(CreateDirectRow())

        result = direct_rows | "Write to Bigtable" >> WriteToBigTable(
            project_id=args.project_id,
            instance_id=args.bigtable_instance_id,
            table_id=args.bigtable_table_id,
        )
        logging.info("Data written to Bigtable.")

if __name__ == "__main__":
    import sys
    run(sys.argv)
