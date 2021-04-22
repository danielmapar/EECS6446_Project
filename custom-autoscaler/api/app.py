import os
from datetime import datetime
import time

from flask import g
from flask import Flask
from flaskthreads import AppContextThread
from flask import jsonify
from flask import request
from flask_pymongo import PyMongo
from flask_cors import CORS

from prometheus_api_client import PrometheusConnect
import pacs_load_tester as load_tester
from tqdm.auto import tqdm
from kubernetes import client, config

print("debug")
print(os.getenv('KUBERNETES_SERVICE_HOST'))

if os.getenv('KUBERNETES_SERVICE_HOST'): 
  config.load_incluster_config()
else: 
  config.load_kube_config()

app = Flask(__name__)
CORS(app) # This will enable CORS for all routes

MONGO_HOST = str(os.environ.get('MONGO_HOST', '127.0.0.1'))
MONGO_PORT = str(os.environ.get('MONGO_PORT', '27017'))
MONGO_DB = str(os.environ.get('MONGO_DBNAME', 'cpa'))
MONGO_USER = str(os.environ.get('MONGO_USERNAME', 'root'))
MONGO_PASS = str(os.environ.get('MONGO_PASSWORD', 'iRhrF6O0vp'))
app.config["MONGO_URI"] = "mongodb://{}:{}@{}:{}/{}?authSource=admin".format(MONGO_USER, MONGO_PASS, MONGO_HOST, MONGO_PORT, MONGO_DB)

mongo = PyMongo(app)

# Setting up Prometheus, Locust and Kubernetes API
prometheus_base = str(os.environ.get('PROMETHEUS_URL', 'http://192.168.23.92:9090'))
prom = PrometheusConnect(url=prometheus_base, disable_ssl=True)

locust_base = str(os.environ.get('LOCUST_URL', 'http://192.168.23.92:8089')) + "/"

api_instance = client.AppsV1Api()

def run_locust():

  deploy_list = g.list_of_deployments

  print("Running Locust Thread!")
  
  # get workload cpu
  query_workload_cpu = """
  sum(
    irate(container_cpu_usage_seconds_total{cluster="", namespace="default"}[2m])
  * on(namespace,pod)
    group_left(workload, workload_type) namespace_workload_pod:kube_pod_owner:relabel{cluster="", namespace="default", workload_type="deployment"}
  ) by (workload, workload_type)
  """
  get_workload_cpu_query = lambda: prom.custom_query(query=query_workload_cpu) 

  def get_all_deployment_cpu_usage():
      wl_cpu_res = get_workload_cpu_query()
      # filter results (unit is millicores)
      filtered_cpu_query = { q['metric']['workload']: float(q['value'][1])*1000 for q in wl_cpu_res if q['metric']['workload'] in deploy_list}
      # if metric skipped, put in None instead
      for d in deploy_list:
        if d not in filtered_cpu_query:
          filtered_cpu_query[d] = None
      return filtered_cpu_query
  
  # get pod count
  query_pod_count = """count(
          kube_pod_info{namespace="default"}
      ) by (created_by_kind,created_by_name)"""
  get_pod_count_query = lambda: prom.custom_query(query=query_pod_count)

  def get_pod_count(deploy_name, count_q_res):
    filtered_res = [{
        'name': q['metric']['created_by_name'],
        'count': int(q['value'][1]),
    } for q in count_q_res]
    for res in filtered_res:
        if res['name'].startswith(deploy_name):
            return res['count']
    # if not found, return -1
    return None

  def get_all_deployment_pod_counts():
    count_q_res = get_pod_count_query()
    deploy_pod_counts = {}
    for d in deploy_list:
        deploy_pod_counts[d] = get_pod_count(d, count_q_res)
    return deploy_pod_counts
  
  def get_replica_and_ready(deployment_name, deployment_ns="default"):
    api_response = api_instance.read_namespaced_deployment(deployment_name, deployment_ns)
    return api_response.status.replicas, api_response.status.ready_replicas

  def get_all_deployment_kubernetes_count():
    result = {}
    for d in deploy_list:
        counts = get_replica_and_ready(d)
        result[d + '_ordered'] = counts[0]
        result[d + '_ready'] = counts[1]
    return result

  # first, add a helper function to add prefix to dict keys
  def prefix_dict(prefix, dict):
      return {prefix+'_'+k: v for k,v in dict.items()}

  def custom_sensing():
      result = {}
      result.update(
          prefix_dict('cpu', get_all_deployment_cpu_usage())
      )
      result.update(
          prefix_dict('monitored_count', get_all_deployment_pod_counts())
      )
      result.update(
          prefix_dict('kubernetes', get_all_deployment_kubernetes_count())
      )
      return result

  tqdm.pandas()
  
  loop_timer = load_tester.TimerClass()
  total_timer = load_tester.TimerClass()

  user_sequence = [50,100,500,1000,1000,1000,500,100,50,50]
  lt = load_tester.PACSLoadTester(hatch_rate=1000, temp_stat_max_len=60, base=locust_base)
  # add the custom sensing function
  lt.custom_sensing = custom_sensing
  lt.change_count(user_sequence[0])
  lt.reset_remote_stats()
  # wait for changes to take effect
  time.sleep(10)
  lt.start_capturing()

  loop_time_in_secs = load_tester.get_loop_time_in_secs('60s')

  loop_timer.tic()
  total_timer.tic()

  arr_results = []
  for i in tqdm(range(len(user_sequence))):
      user_count = user_sequence[i]
      lt.change_count(user_count)
      
      time.sleep(loop_time_in_secs - loop_timer.toc())
      
      loop_timer.tic()
      
      result = lt.get_all_stats()    
      arr_results.append(result)
      
  lt.stop_test()

  print("Done!")

  g.locust_result = arr_results

@app.route('/setDeployments', methods=['PUT'])
def add_deployments():
  deployments = mongo.db.deployments
  list_of_deployments = request.json['list']

  deployment_id = None
  for deployment_obj in deployments.find():
    deployment_id = deployment_obj['_id']
  
  if deployment_id == None:
    deployment_insert_obj = deployments.insert_one({'list': list_of_deployments})
    deployment_id = deployment_insert_obj.inserted_id
  else:
    deployments.update_one({"_id": deployment_id}, { "$set": { "list": list_of_deployments} }, upsert=True)

  return jsonify({'result' : str(deployment_id)})

@app.route('/deployments', methods=['GET'])
def get_all_deployments():
  deployments = mongo.db.deployments
  output = None
  for s in deployments.find():
    output = {'list' : s['list']}
  return jsonify({'result' : output})

@app.route('/setEquation', methods=['PUT'])
def update_equation():
  equation = mongo.db.equation

  equation_str = str(request.json['equation'])

  equation_id = None
  for equation_obj in equation.find():
    equation_id = equation_obj['_id']
  
  if equation_id == None:
    equation_insert_obj = equation.insert_one({'equation': equation_str})
    equation_id = equation_insert_obj.inserted_id
  else:
    equation.update_one({"_id": equation_id}, { "$set": { "equation": equation_str} }, upsert=True)
  
  return jsonify({'result' : str(equation_id)})

@app.route('/equation', methods=['GET'])
def get_equation():
  equation = mongo.db.equation
  output = None
  for s in equation.find():
    output = {'equation' : s['equation']}
  return jsonify({'result' : output})

@app.route('/createLoadTest', methods=['POST'])
def create_load_test():
  loadtest = mongo.db.loadtest
  deployments = mongo.db.deployments

  equation_str = str(request.json['equation'])
  timestamp = str(datetime.now())

  list_of_deployments = []
  for s in deployments.find():
    list_of_deployments = s['list']

  loadtest_insert_obj = loadtest.insert_one({'status': "Running", 'equation': equation_str, "timestamp": timestamp, "deployments": list_of_deployments, "data": "none"})
  loadtest_id = loadtest_insert_obj.inserted_id

  g.list_of_deployments = list_of_deployments

  t = AppContextThread(target=run_locust)
  t.start()
  t.join()

  loadtest.update_one({"_id": loadtest_id}, { "$set": { 'status': "Done", "data": g.locust_result} }, upsert=True)
  
  return jsonify({'result' : str(loadtest_id)})

@app.route('/loadTests', methods=['GET'])
def get_all_loadtests():
  loadtest = mongo.db.loadtest
  output = []
  for s in loadtest.find():
    output.append({'status': s['status'],'equation': s['equation'], "timestamp": s['timestamp'], "deployments": s['deployments'], "data": s['data']})
  return jsonify({'result' : output})

@app.route('/predictions', methods=['GET'])
def get_all_predictions():
  predictions = mongo.db.predictions
  output = []
  for s in predictions.find():
    output.append({'name': s['name'],'value': s['value']})
  return jsonify({'result' : output})

if __name__ == '__main__':
    app.run(debug=True, host='0.0.0.0', port=int(os.environ.get('API_PORT', '5002')))