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

## Project - Phase 2

* Setup a MongoDB inside your cluster
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

* Setup FlaskAPI
    * Navigate to the Custom Autoscaler API folder: `cd custom-autoscaler/api`
    * Install dependencies: `pip install -r requirements.txt`

First we should enable custom autoscalers on our cluster by installing the Custom Pod Autoscaler Operator, for this guide we are using `v1.0.3`, but check out the latest version from the [Custom Pod Autoscaler Operator releases](https://github.com/jthomperoo/custom-pod-autoscaler-operator/releases) and see the [install guide](https://github.com/jthomperoo/custom-pod-autoscaler-operator/blob/master/INSTALL.md) for the latest install information.

```sh
VERSION=v1.0.3
kubectl apply -f https://github.com/jthomperoo/custom-pod-autoscaler-operator/releases/download/${VERSION}/cluster.yaml`
```


