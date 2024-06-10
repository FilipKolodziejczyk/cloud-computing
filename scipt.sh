#Compilation
gcloud dataflow flex-template build gs://cloud-computing-3454685-dataflow-real-time-temp-bucket/real-time-flow-py.json  --image-gcr-path "europe-central2-docker.pkg.dev/cloud-computing-3454685/workflow-repo/real-time-flow-python:latest"  --sdk-language "PYTHON"  --flex-template-base-image "PYTHON3"  --metadata-file "real-time-flow.metadata.json"  --py-path "."  --env "FLEX_TEMPLATE_PYTHON_PY_FILE=real-time-flow.py"  --env "FLEX_TEMPLATE_PYTHON_REQUIREMENTS_FILE=requirements.txt"

#Deployment OpenWeather
gcloud dataflow flex-template run "real-time-flow-open-weather-`date +%Y%m%d-%H%M%S`" \
 --template-file-gcs-location "gs://cloud-computing-3454685-dataflow-real-time-temp-bucket/real-time-flow-py.json" \
 --parameters=project_id="cloud-computing-3454685",pubsub_subscription="projects/cloud-computing-3454685/subscriptions/OpenWeather-realtime-subscription",bigtable_instance_id="real-time-bigtable",bigtable_table_id="OpenWeather" \
 --region "europe-central2" \
--additional-experiments=streaming_mode_exactly_once

#Deployment IOT
gcloud dataflow flex-template run "real-time-flow-iot-`date +%Y%m%d-%H%M%S`" \
 --template-file-gcs-location "gs://cloud-computing-3454685-dataflow-real-time-temp-bucket/real-time-flow-py.json" \
 --parameters=project_id="cloud-computing-3454685",pubsub_subscription="projects/cloud-computing-3454685/subscriptions/IOT-realtime-subscription",bigtable_instance_id="real-time-bigtable",bigtable_table_id="IOT" \
 --region "europe-central2" \
--additional-experiments=streaming_mode_exactly_once

gcloud dataflow flex-template run "real-time-flow-open-meteo-`date +%Y%m%d-%H%M%S`" \
 --template-file-gcs-location "gs://cloud-computing-3454685-dataflow-real-time-temp-bucket/real-time-flow-py.json" \
 --parameters=project_id="cloud-computing-3454685",pubsub_subscription="projects/cloud-computing-3454685/subscriptions/OpenMeteo-realtime-subscription",bigtable_instance_id="real-time-bigtable",bigtable_table_id="OpenMeteo" \
 --region "europe-central2" \
--additional-experiments=streaming_mode_exactly_once