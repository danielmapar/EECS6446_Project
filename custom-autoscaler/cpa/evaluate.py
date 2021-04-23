import json
import sys
import os
from pymongo import MongoClient
from types import FunctionType

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
        
        equation_collection = cpa_db.equation
        equation_str = None
        for s in equation_collection.find():
            equation_str = s['equation']
        
        if equation_str == None:
            sys.stderr.write(f"Equation is empty. Save an equation!")
            exit(1)

        predictions_collection = cpa_db.predictions

        # Parse provided spec into a dict
        spec = json.loads(sys.stdin.read())
        # spec = json.loads(r'{"metrics": [{"resource": "redis-cart", "value": "{\"cpu_avr_consump_percent\": 1.0179603758043334}"}], "resource": {"kind": "Deployment", "apiVersion": "apps/v1", "metadata": {"name": "redis-cart", "namespace": "default", "uid": "1b25ec34-965e-4f57-9638-b95e78edfe41", "resourceVersion": "2238", "generation": 1, "creationTimestamp": "2021-02-13T06:18:09Z", "annotations": {"deployment.kubernetes.io/revision": "1", "kubectl.kubernetes.io/last-applied-configuration": "{\"apiVersion\":\"apps/v1\",\"kind\":\"Deployment\",\"metadata\":{\"annotations\":{},\"name\":\"redis-cart\",\"namespace\":\"default\"},\"spec\":{\"selector\":{\"matchLabels\":{\"app\":\"redis-cart\"}},\"template\":{\"metadata\":{\"labels\":{\"app\":\"redis-cart\"}},\"spec\":{\"containers\":[{\"image\":\"redis:alpine\",\"livenessProbe\":{\"periodSeconds\":5,\"tcpSocket\":{\"port\":6379}},\"name\":\"redis\",\"ports\":[{\"containerPort\":6379}],\"readinessProbe\":{\"periodSeconds\":5,\"tcpSocket\":{\"port\":6379}},\"resources\":{\"limits\":{\"cpu\":\"125m\",\"memory\":\"256Mi\"},\"requests\":{\"cpu\":\"70m\",\"memory\":\"200Mi\"}},\"volumeMounts\":[{\"mountPath\":\"/data\",\"name\":\"redis-data\"}]}],\"volumes\":[{\"emptyDir\":{},\"name\":\"redis-data\"}]}}}}\n"}, "managedFields": [{"manager": "kubectl", "operation": "Update", "apiVersion": "apps/v1", "time": "2021-02-13T06:18:09Z", "fieldsType": "FieldsV1", "fieldsV1": {"f:metadata": {"f:annotations": {".": {}, "f:kubectl.kubernetes.io/last-applied-configuration": {}}}, "f:spec": {"f:progressDeadlineSeconds": {}, "f:replicas": {}, "f:revisionHistoryLimit": {}, "f:selector": {}, "f:strategy": {"f:rollingUpdate": {".": {}, "f:maxSurge": {}, "f:maxUnavailable": {}}, "f:type": {}}, "f:template": {"f:metadata": {"f:labels": {".": {}, "f:app": {}}}, "f:spec": {"f:containers": {"k:{\"name\":\"redis\"}": {".": {}, "f:image": {}, "f:imagePullPolicy": {}, "f:livenessProbe": {".": {}, "f:failureThreshold": {}, "f:periodSeconds": {}, "f:successThreshold": {}, "f:tcpSocket": {".": {}, "f:port": {}}, "f:timeoutSeconds": {}}, "f:name": {}, "f:ports": {".": {}, "k:{\"containerPort\":6379,\"protocol\":\"TCP\"}": {".": {}, "f:containerPort": {}, "f:protocol": {}}}, "f:readinessProbe": {".": {}, "f:failureThreshold": {}, "f:periodSeconds": {}, "f:successThreshold": {}, "f:tcpSocket": {".": {}, "f:port": {}}, "f:timeoutSeconds": {}}, "f:resources": {".": {}, "f:limits": {".": {}, "f:cpu": {}, "f:memory": {}}, "f:requests": {".": {}, "f:cpu": {}, "f:memory": {}}}, "f:terminationMessagePath": {}, "f:terminationMessagePolicy": {}, "f:volumeMounts": {".": {}, "k:{\"mountPath\":\"/data\"}": {".": {}, "f:mountPath": {}, "f:name": {}}}}}, "f:dnsPolicy": {}, "f:restartPolicy": {}, "f:schedulerName": {}, "f:securityContext": {}, "f:terminationGracePeriodSeconds": {}, "f:volumes": {".": {}, "k:{\"name\":\"redis-data\"}": {".": {}, "f:emptyDir": {}, "f:name": {}}}}}}}}, {"manager": "k3s", "operation": "Update", "apiVersion": "apps/v1", "time": "2021-02-13T06:18:21Z", "fieldsType": "FieldsV1", "fieldsV1": {"f:metadata": {"f:annotations": {"f:deployment.kubernetes.io/revision": {}}}, "f:status": {"f:availableReplicas": {}, "f:conditions": {".": {}, "k:{\"type\":\"Available\"}": {".": {}, "f:lastTransitionTime": {}, "f:lastUpdateTime": {}, "f:message": {}, "f:reason": {}, "f:status": {}, "f:type": {}}, "k:{\"type\":\"Progressing\"}": {".": {}, "f:lastTransitionTime": {}, "f:lastUpdateTime": {}, "f:message": {}, "f:reason": {}, "f:status": {}, "f:type": {}}}, "f:observedGeneration": {}, "f:readyReplicas": {}, "f:replicas": {}, "f:updatedReplicas": {}}}}]}, "spec": {"replicas": 1, "selector": {"matchLabels": {"app": "redis-cart"}}, "template": {"metadata": {"creationTimestamp": null, "labels": {"app": "redis-cart"}}, "spec": {"volumes": [{"name": "redis-data", "emptyDir": {}}], "containers": [{"name": "redis", "image": "redis:alpine", "ports": [{"containerPort": 6379, "protocol": "TCP"}], "resources": {"limits": {"cpu": "125m", "memory": "256Mi"}, "requests": {"cpu": "70m", "memory": "200Mi"}}, "volumeMounts": [{"name": "redis-data", "mountPath": "/data"}], "livenessProbe": {"tcpSocket": {"port": 6379}, "timeoutSeconds": 1, "periodSeconds": 5, "successThreshold": 1, "failureThreshold": 3}, "readinessProbe": {"tcpSocket": {"port": 6379}, "timeoutSeconds": 1, "periodSeconds": 5, "successThreshold": 1, "failureThreshold": 3}, "terminationMessagePath": "/dev/termination-log", "terminationMessagePolicy": "File", "imagePullPolicy": "IfNotPresent"}], "restartPolicy": "Always", "terminationGracePeriodSeconds": 30, "dnsPolicy": "ClusterFirst", "securityContext": {}, "schedulerName": "default-scheduler"}}, "strategy": {"type": "RollingUpdate", "rollingUpdate": {"maxUnavailable": "25%", "maxSurge": "25%"}}, "revisionHistoryLimit": 10, "progressDeadlineSeconds": 600}, "status": {"observedGeneration": 1, "replicas": 1, "updatedReplicas": 1, "readyReplicas": 1, "availableReplicas": 1, "conditions": [{"type": "Available", "status": "True", "lastUpdateTime": "2021-02-13T06:18:21Z", "lastTransitionTime": "2021-02-13T06:18:21Z", "reason": "MinimumReplicasAvailable", "message": "Deployment has minimum availability."}, {"type": "Progressing", "status": "True", "lastUpdateTime": "2021-02-13T06:18:21Z", "lastTransitionTime": "2021-02-13T06:18:09Z", "reason": "NewReplicaSetAvailable", "message": "ReplicaSet \"redis-cart-74594bd569\" has successfully progressed."}]}}, "runType": "scaler"}')
        evaluate(spec, equation_str, predictions_collection)
    except Exception as err:
        sys.stderr.write(f"Error evaluate: {err}")
        exit(1)

def evaluate(spec, equation_str, predictions_collection):
    f_code = compile(equation_str, "<string>", "exec")
    scale_func = FunctionType(f_code.co_consts[0], globals(), "scale")

    deployment_name = spec['metrics'][0]['resource']
    deployment_cpu_avr_consump_percent= float(json.loads(spec['metrics'][0]['value'])['cpu_avr_consump_percent'])
    deployment_num_of_replicas = spec['resource']['status']['replicas']

    last_prediction = None
    for prediction in predictions_collection.find({'name': deployment_name}).sort("_id", -1):
        last_prediction = prediction['value']
        break

    resp = scale_func(last_prediction, deployment_cpu_avr_consump_percent, deployment_num_of_replicas)

    desired_num_of_replicas = resp[0]
    current_prediction = resp[1]

    predictions_collection.insert_one({'name': deployment_name, 'value': current_prediction})

    # Build JSON dict with targetReplicas
    evaluation = {}
    evaluation["targetReplicas"] = desired_num_of_replicas

    # Output JSON to stdout
    sys.stdout.write(json.dumps(evaluation))

if __name__ == "__main__":
    main()
