import os
import json
import sys
from prometheus_api_client import PrometheusConnect
from pymongo import MongoClient

def main():
    try:
        # Setting up Mongo DB
        MONGO_HOST = str(os.environ.get('MONGO_HOST', '127.0.0.1'))
        MONGO_PORT = str(os.environ.get('MONGO_PORT', '27017'))
        MONGO_DB = str(os.environ.get('MONGO_DBNAME', 'cpa'))
        MONGO_USER = str(os.environ.get('MONGO_USERNAME', 'root'))
        MONGO_PASS = str(os.environ.get('MONGO_PASSWORD', 'iRhrF6O0vp'))
        mongodb_client = MongoClient('mongodb://{}:{}@{}:{}/?authSource=admin'.format(MONGO_USER, MONGO_PASS, MONGO_HOST, MONGO_PORT))

        cpa_db = mongodb_client[MONGO_DB]
        deployments_collection = cpa_db.deployments
        list_of_deployments = []

        for deployment in deployments_collection.find():
            list_of_deployments = deployment['list']

        # Setting up Prometheus
        prometheus_base = str(os.environ.get('PROMETHEUS_URL', 'http://192.168.23.92:9090'))
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

        def get_deployments_cpu_usage(list_of_deployments):
            wl_cpu_res = get_workload_cpu_query()
            # filter results (unit is millicores)
            filtered_cpu_query = { q['metric']['workload']: float(q['value'][1])*1000 for q in wl_cpu_res if q['metric']['workload'] in list_of_deployments}
            # if metric skipped, put in None instead
            for d in list_of_deployments:
              if d not in filtered_cpu_query:
                filtered_cpu_query[d] = None
            return filtered_cpu_query

        # Parse spec into a dict
        # spec = json.loads(r'{"resource": {"kind": "Deployment", "apiVersion": "apps/v1", "metadata": {"name": "redis-cart", "namespace": "default", "uid": "1b25ec34-965e-4f57-9638-b95e78edfe41", "resourceVersion": "2238", "generation": 1, "creationTimestamp": "2021-02-13T06:18:09Z", "annotations": {"deployment.kubernetes.io/revision": "1", "kubectl.kubernetes.io/last-applied-configuration": "{\"apiVersion\":\"apps/v1\",\"kind\":\"Deployment\",\"metadata\":{\"annotations\":{},\"name\":\"redis-cart\",\"namespace\":\"default\"},\"spec\":{\"selector\":{\"matchLabels\":{\"app\":\"redis-cart\"}},\"template\":{\"metadata\":{\"labels\":{\"app\":\"redis-cart\"}},\"spec\":{\"containers\":[{\"image\":\"redis:alpine\",\"livenessProbe\":{\"periodSeconds\":5,\"tcpSocket\":{\"port\":6379}},\"name\":\"redis\",\"ports\":[{\"containerPort\":6379}],\"readinessProbe\":{\"periodSeconds\":5,\"tcpSocket\":{\"port\":6379}},\"resources\":{\"limits\":{\"cpu\":\"125m\",\"memory\":\"256Mi\"},\"requests\":{\"cpu\":\"70m\",\"memory\":\"200Mi\"}},\"volumeMounts\":[{\"mountPath\":\"/data\",\"name\":\"redis-data\"}]}],\"volumes\":[{\"emptyDir\":{},\"name\":\"redis-data\"}]}}}}\n"}, "managedFields": [{"manager": "kubectl", "operation": "Update", "apiVersion": "apps/v1", "time": "2021-02-13T06:18:09Z", "fieldsType": "FieldsV1", "fieldsV1": {"f:metadata": {"f:annotations": {".": {}, "f:kubectl.kubernetes.io/last-applied-configuration": {}}}, "f:spec": {"f:progressDeadlineSeconds": {}, "f:replicas": {}, "f:revisionHistoryLimit": {}, "f:selector": {}, "f:strategy": {"f:rollingUpdate": {".": {}, "f:maxSurge": {}, "f:maxUnavailable": {}}, "f:type": {}}, "f:template": {"f:metadata": {"f:labels": {".": {}, "f:app": {}}}, "f:spec": {"f:containers": {"k:{\"name\":\"redis\"}": {".": {}, "f:image": {}, "f:imagePullPolicy": {}, "f:livenessProbe": {".": {}, "f:failureThreshold": {}, "f:periodSeconds": {}, "f:successThreshold": {}, "f:tcpSocket": {".": {}, "f:port": {}}, "f:timeoutSeconds": {}}, "f:name": {}, "f:ports": {".": {}, "k:{\"containerPort\":6379,\"protocol\":\"TCP\"}": {".": {}, "f:containerPort": {}, "f:protocol": {}}}, "f:readinessProbe": {".": {}, "f:failureThreshold": {}, "f:periodSeconds": {}, "f:successThreshold": {}, "f:tcpSocket": {".": {}, "f:port": {}}, "f:timeoutSeconds": {}}, "f:resources": {".": {}, "f:limits": {".": {}, "f:cpu": {}, "f:memory": {}}, "f:requests": {".": {}, "f:cpu": {}, "f:memory": {}}}, "f:terminationMessagePath": {}, "f:terminationMessagePolicy": {}, "f:volumeMounts": {".": {}, "k:{\"mountPath\":\"/data\"}": {".": {}, "f:mountPath": {}, "f:name": {}}}}}, "f:dnsPolicy": {}, "f:restartPolicy": {}, "f:schedulerName": {}, "f:securityContext": {}, "f:terminationGracePeriodSeconds": {}, "f:volumes": {".": {}, "k:{\"name\":\"redis-data\"}": {".": {}, "f:emptyDir": {}, "f:name": {}}}}}}}}, {"manager": "k3s", "operation": "Update", "apiVersion": "apps/v1", "time": "2021-02-13T06:18:21Z", "fieldsType": "FieldsV1", "fieldsV1": {"f:metadata": {"f:annotations": {"f:deployment.kubernetes.io/revision": {}}}, "f:status": {"f:availableReplicas": {}, "f:conditions": {".": {}, "k:{\"type\":\"Available\"}": {".": {}, "f:lastTransitionTime": {}, "f:lastUpdateTime": {}, "f:message": {}, "f:reason": {}, "f:status": {}, "f:type": {}}, "k:{\"type\":\"Progressing\"}": {".": {}, "f:lastTransitionTime": {}, "f:lastUpdateTime": {}, "f:message": {}, "f:reason": {}, "f:status": {}, "f:type": {}}}, "f:observedGeneration": {}, "f:readyReplicas": {}, "f:replicas": {}, "f:updatedReplicas": {}}}}]}, "spec": {"replicas": 1, "selector": {"matchLabels": {"app": "redis-cart"}}, "template": {"metadata": {"creationTimestamp": null, "labels": {"app": "redis-cart"}}, "spec": {"volumes": [{"name": "redis-data", "emptyDir": {}}], "containers": [{"name": "redis", "image": "redis:alpine", "ports": [{"containerPort": 6379, "protocol": "TCP"}], "resources": {"limits": {"cpu": "125m", "memory": "256Mi"}, "requests": {"cpu": "70m", "memory": "200Mi"}}, "volumeMounts": [{"name": "redis-data", "mountPath": "/data"}], "livenessProbe": {"tcpSocket": {"port": 6379}, "timeoutSeconds": 1, "periodSeconds": 5, "successThreshold": 1, "failureThreshold": 3}, "readinessProbe": {"tcpSocket": {"port": 6379}, "timeoutSeconds": 1, "periodSeconds": 5, "successThreshold": 1, "failureThreshold": 3}, "terminationMessagePath": "/dev/termination-log", "terminationMessagePolicy": "File", "imagePullPolicy": "IfNotPresent"}], "restartPolicy": "Always", "terminationGracePeriodSeconds": 30, "dnsPolicy": "ClusterFirst", "securityContext": {}, "schedulerName": "default-scheduler"}}, "strategy": {"type": "RollingUpdate", "rollingUpdate": {"maxUnavailable": "25%", "maxSurge": "25%"}}, "revisionHistoryLimit": 10, "progressDeadlineSeconds": 600}, "status": {"observedGeneration": 1, "replicas": 1, "updatedReplicas": 1, "readyReplicas": 1, "availableReplicas": 1, "conditions": [{"type": "Available", "status": "True", "lastUpdateTime": "2021-02-13T06:18:21Z", "lastTransitionTime": "2021-02-13T06:18:21Z", "reason": "MinimumReplicasAvailable", "message": "Deployment has minimum availability."}, {"type": "Progressing", "status": "True", "lastUpdateTime": "2021-02-13T06:18:21Z", "lastTransitionTime": "2021-02-13T06:18:09Z", "reason": "NewReplicaSetAvailable", "message": "ReplicaSet \"redis-cart-74594bd569\" has successfully progressed."}]}}, "runType": "scaler"}')
        spec = json.loads(sys.stdin.read())

        deployments_cpu = get_deployments_cpu_usage(list_of_deployments)

        metric(spec, list_of_deployments, deployments_cpu)
    except Exception as err:
        sys.stderr.write(f"Error metric: {err}")
        exit(1)

def metric(spec, list_of_deployments, deployments_cpu):

    # Ignore anything that is not a deployment
    if spec['resource']['kind'] != "Deployment":
        sys.stderr.write("Resource type is not deployment!")
        exit(1)

    deployment_name = spec['resource']['metadata']['name']

    # Ignore deployments that are not being tracked
    if deployment_name not in list_of_deployments:
        sys.stderr.write("Deployment not inside the list of watched deployments!")
        exit(1)

    deployment_cpu_limit = int(spec['resource']['spec']['template']['spec']['containers'][0]['resources']['limits']['cpu'].replace('m', ''))

    cpu_avr_consump_percent = (deployments_cpu[deployment_name] * 100) / deployment_cpu_limit

    result = {}
    result['cpu_avr_consump_percent'] = str(cpu_avr_consump_percent)
    
    sys.stdout.write(json.dumps(result))

if __name__ == "__main__":
    main()

