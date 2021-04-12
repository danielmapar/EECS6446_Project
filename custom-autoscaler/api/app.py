import os
from datetime import datetime
from flask import Flask
from flask import jsonify
from flask import request
from flask_pymongo import PyMongo

app = Flask(__name__)

inside_cluster = os.environ.get('IN_K8')

if "True" in inside_cluster:
    app.config['MONGO_HOST'] = str(os.environ.get('MONGO_HOST'))
    app.config['MONGO_PORT'] = int(os.environ.get('MONGO_PORT'))
    app.config['MONGO_DBNAME'] = str(os.environ.get('MONGO_DBNAME'))
    app.config['MONGO_USERNAME'] = str(os.environ.get('MONGO_USERNAME'))
    app.config['MONGO_PASSWORD'] = str(os.environ.get('MONGO_PASSWORD'))
else:
    app.config['MONGO_URI'] = 'mongodb://localhost:27017/cpa'

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

  equation_str = str(request.json['equation'])
  data_str = str(request.json['data'])
  timestamp = str(datetime.now())

  loadtest_id = None

  loadtest_insert_obj = loadtest.insert_one({'equation': equation_str, "timestamp": timestamp, "data": data_str})
  loadtest_id = loadtest_insert_obj.inserted_id
  
  return jsonify({'result' : str(loadtest_id)})

@app.route('/loadTests', methods=['GET'])
def get_all_loadtests():
  loadtest = mongo.db.loadtest
  output = None
  for s in loadtest.find():
    output = {'equation': s['equation'], "timestamp": s['timestamp'], "data": s['data']}
  return jsonify({'result' : output})

if __name__ == '__main__':
    app.run(debug=True, host='0.0.0.0', port=5000)