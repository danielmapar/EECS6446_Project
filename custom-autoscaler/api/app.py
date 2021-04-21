import os
from datetime import datetime
from flask import Flask
from flask import jsonify
from flask import request
from flask_pymongo import PyMongo
from flask_cors import CORS

app = Flask(__name__)
CORS(app) # This will enable CORS for all routes

inside_cluster = os.environ.get('IN_K8')

if inside_cluster == "True":
    MONGO_HOST = str(os.environ.get('MONGO_HOST'))
    MONGO_PORT = str(os.environ.get('MONGO_PORT'))
    MONGO_DB = str(os.environ.get('MONGO_DBNAME'))
    MONGO_USER = str(os.environ.get('MONGO_USERNAME'))
    MONGO_PASS = str(os.environ.get('MONGO_PASSWORD'))
    app.config["MONGO_URI"] = "mongodb://{}:{}@{}:{}/{}?authSource=admin".format(MONGO_USER, MONGO_PASS, MONGO_HOST, MONGO_PORT, MONGO_DB)
else:
    app.config['MONGO_URI'] = 'mongodb://localhost:27017/cpa'

print("LIVE URI:")
print(app.config["MONGO_URI"])

mongo = PyMongo(app)

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

  list_of_deployments = None
  for s in deployments.find():
    list_of_deployments = s['list']

  loadtest_id = None

  loadtest_insert_obj = loadtest.insert_one({'equation': equation_str, "timestamp": timestamp, "deployments": list_of_deployments, "data": "test"})
  loadtest_id = loadtest_insert_obj.inserted_id
  
  return jsonify({'result' : str(loadtest_id)})

@app.route('/loadTests', methods=['GET'])
def get_all_loadtests():
  loadtest = mongo.db.loadtest
  output = []
  for s in loadtest.find():
    output.append({'equation': s['equation'], "timestamp": s['timestamp'], "deployments": s['deployments'], "data": s['data']})
  return jsonify({'result' : output})

if __name__ == '__main__':
    app.run(debug=True, host='0.0.0.0', port=int(os.environ.get('API_PORT')))