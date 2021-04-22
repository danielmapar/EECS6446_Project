import os
import json
import sys
from prometheus_api_client import PrometheusConnect
from pymongo import MongoClient

# Setting up Mongo DB
MONGO_HOST = str(os.environ.get('MONGO_HOST'))
MONGO_PORT = str(os.environ.get('MONGO_PORT'))
MONGO_DB = str(os.environ.get('MONGO_DBNAME'))
MONGO_USER = str(os.environ.get('MONGO_USERNAME'))
MONGO_PASS = str(os.environ.get('MONGO_PASSWORD'))
mongodb_client = MongoClient('mongodb://{}:{}@{}:{}/?authSource=admin'.format(MONGO_USER, MONGO_PASS, MONGO_HOST, MONGO_PORT))

cpa_db = mongodb_client[MONGO_DB]
deployments_collection = cpa_db.deployments
list_of_deployments = []

for deployment in deployments_collection.find():
    list_of_deployments = deployment['list']

# Setting up Prometheus
prometheus_base = str(os.environ.get('PROMETHEUS_URL'))
prom = PrometheusConnect(url=prometheus_base, disable_ssl=True)

# get workload cpu
query_workload_cpu = """
sum(
  irate(container_cpu_usage_seconds_total{cluster="", namespace="default"}[2m])
* on(namespace,pod)
  group_left(workload, workload_type) namespace_workload_pod:kube_pod_owner:relabel{cluster="", namespace="default", workload_type="deployment"}
) by (workload, workload_type)
"""
get_workload_cpu_query = lambda: prom.custom_query(query=query_workload_cpu)

def get_deployment_cpu_usage(deployments):
    wl_cpu_res = get_workload_cpu_query()
    # filter results (unit is millicores)
    filtered_cpu_query = { q['metric']['workload']: float(q['value'][1])*1000 for q in wl_cpu_res if q['metric']['workload'] in deployments}
    # if metric skipped, put in None instead
    for d in deployments:
      if d not in filtered_cpu_query:
        filtered_cpu_query[d] = None
    return filtered_cpu_query

def main():
    # Parse spec into a dict
    spec = json.loads(sys.stdin.read())
    metric(spec)

def metric(spec):
    sys.stderr.write("--> DEBUG - metric")
    sys.stderr.write(json.dumps(spec))
    sys.stderr.write("-----")
    sys.stderr.write(json.dumps(list_of_deployments))
    sys.stderr.write("-----")
    cpu_metrics = get_deployment_cpu_usage(list_of_deployments)
    sys.stderr.write(cpu_metrics)

    exit(1)

if __name__ == "__main__":
    main()