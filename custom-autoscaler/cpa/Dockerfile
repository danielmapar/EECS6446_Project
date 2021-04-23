# Pull in Python build of CPA
FROM custompodautoscaler/python:latest

# Add in python requirements to install dependencies
ADD requirements.txt /
# Install dependencies, done before adding Py files to allow Docker to cache better
RUN pip install -r /requirements.txt

# Add config, evaluator and metric gathering Py scripts
ADD config.yaml evaluate.py metric.py /