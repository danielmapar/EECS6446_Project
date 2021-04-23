# EECS6446: Performance Modelling of Computing Systems

## Project - Phase 1

Welcome to `EECS6446` course project. In the first phase of this project, you will deploy a sample
application based on microservice architecture on a `Kubernetes` cluster. Then you exercise various
pre-defined autoscaling strategies to handle/investigate flactuations in the applied workload to your cluster.

In fact, the first phase of the project is like a tutorial that you need to follow the steps mentioned in 
the below table. We also provided a complete walk-through of all steps here: [Phase 1 Tutorial](https://youtu.be/DKAhQk7W1Rw).

At the end of each step, you will see a list of references that may help you gain a better
understanding of the elements and concepts in that part.

Here is the table of contents for phase 1:

| No. | Topic |
|-----|-------|
|1    | [Requirements, SSH, and Initial Setup](tutorials/01-requirements.md) |
|2    | [Installation of Kubernetes, Kubectl, and Other Tools](tutorials/02-kubernetes.md) |
|3    | [Microservice Deployment](tutorials/03-microservice.md) |
|4    | [Interacting and Testing the Load Generator](tutorials/04-loadgenerator.md) |
|5    | [Deploying Monitoring Stack using Prometheus, Grafana, and Prometheus Operator](tutorials/05-monitoring.md) |
|6    | [Interacting with the Monitoring Stack](tutorials/06-monitoring-interaction.md) |
|7    | [Kubernetes API for Scaling Resources](tutorials/07-kubernetes-api.md) |
|8    | [Testing the Horizontal Pod Autoscaler](tutorials/08-hpa-test.md) |
|9    | [Submission and Evaluation](tutorials/09-phase1-evaluation.md) |

Should you have any question or issue, please post them in the course's forum
or [open an issue on GitHub](https://github.com/pacslab/EECS6446_Project/issues/new/choose).

## Project - Phase 2 (Custom Pod Autoscaler)

### K8s Setup

* Setup MongoDB inside your cluster

    * Install MongoDB by using Helm
        * `helm repo add bitnami https://charts.bitnami.com/bitnami`
        * `helm install mongodb bitnami/mongodb`

    * Port-forward traffic for port `27017`
        * `kubectl port-forward --namespace default svc/mongodb 27017:27017 &`
    
    * Try accessing the database
        * `sudo apt install mongodb-clients`
            * This is a client to interact with MongoDB
        * `export MONGODB_ROOT_PASSWORD=$(kubectl get secret --namespace default mongodb -o jsonpath="{.data.mongodb-root-password}" | base64 --decode)`
        * `mongo --host 127.0.0.1 --authenticationDatabase admin -u root -p $MONGODB_ROOT_PASSWORD`

    * For more details check [this](https://hub.kubeapps.com/charts/bitnami/mongodb)

* Setup Flask API

    * Setup credentials for API to access Kubernetes cluster:
        * ```sh
            kubectl create clusterrolebinding serviceaccounts-cluster-admin \
            --clusterrole=cluster-admin \
            --group=system:serviceaccounts
            ```

    * Navigate to the Custom Pod Autoscaler API folder: `cd custom-autoscaler/api`
    * Add the API to your cluster: `kubectl apply -f api.yaml`
        * Update `env` vars inside the file to match your cluster settings

* Setup Web Frontend

    * Navigate to the Custom Pod Autoscaler frontend folder: `cd custom-autoscaler/frontend`
    * Add the frontend to your cluster: `kubectl apply -f frontend.yaml`
        * Update `env` vars inside the file to match your cluster settings

* Setup Custom Pod Autoscaler job
    * Add the Custom Pod Autoscaler Operator to your cluster
        * ```sh
            VERSION=v1.1.0
            kubectl apply -f https://github.com/jthomperoo/custom-pod-autoscaler-operator/releases/download/${VERSION}/cluster.yaml
            ```
    * Navigate to the Custom Pod Autoscaler job folder `cd custom-autoscaler/cpa`
    * Add the Custom Pod Autoscaler jobs to your cluster: `kubectl apply -f cpa.yaml`
        * Update `env` vars inside the file to match your cluster settings

### Developer setup

* Setup Flask API

    * Navigate to the Custom Pod Autoscaler API folder: `cd custom-autoscaler/api`
    * Install dependencies: `pip install -r requirements.txt`
    * Run the API locally: `python app.py`

    * To publish a new version
        * `docker build -t danielmapar/cpa-api:latest .`
        * `docker push danielmapar/cpa-api`
        * `kubectl apply -f api.yaml`
            * Update `env` vars inside the file to match your cluster settings

* Setup Web Frontend

    * Navigate to the Custom Pod Autoscaler frontend folder: `cd custom-autoscaler/frontend`
    * Install dependencies `yarn install`
    * Run the frontend locally: `yarn start`

    * To publish a new version
        * `docker build -t danielmapar/cpa-frontend:latest .`
        * `docker push danielmapar/cpa-frontend`
        * `kubectl apply -f frontend.yaml`
            * Update `env` vars inside the file to match your cluster settings

* Setup Custom Pod Autoscaler Job

    * Navigate to the Custom Pod Autoscaler job folder: `cd custom-autoscaler/cpa`
    * Install dependencies: `pip install -r requirements.txt`
    * Run the CPA job locally: `python metric.py` or `python evaluate.py`

    * To publish a new version
        * `docker build -t danielmapar/cpa:latest .`
        * `docker push danielmapar/cpa`
        * `kubectl apply -f cpa.yaml`
            * Update `env` vars inside the file to match your cluster settings