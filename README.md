## How to deploy application

### Prerequisites

```bash
ansible-galaxy collection install kubernetes.core
pip3 install kubernetes
```

Update the following parameter in the configuration file `remote_cluster/roles/eks/defaults/main.yml`
* role_arn
* create_subnet_1
* create_subnet_2
* ec2_resource_prefix

and update `~/.aws/credentials` with your credential to AWS.

### Deploy application

```bash
./start_aws_cluster.sh
```

## How to run tests

### Prerequisites

```bash
pip install locust
```

### Running tests

```bash
git clone https://github.com/pptam/pptam-tool
git checkout dd44cb917c3b1d1d6f5ec03ef3d57c2df4efb688 `# There is some regression on master branch, so we checkout to latest working version`
cd design_trainticket
locust -f locustfile.py
```

and then open `http://0.0.0.0:8089` in browser and pass `url` to application:

```
// extract url to deployed application 
$ kubectl get svc istio-ingressgateway -n istio-system  --output jsonpath='{.status.loadBalancer.ingress[0].hostname}'
```

## Get Jaeger url

```bash
kubectl get svc jaeger-query-public --output jsonpath='{.status.loadBalancer.ingress[0].hostname}'
```

Jaeger is hosted at the port `8080`

## Get Prometheus url

```bash
kubectl get svc prometheus --output jsonpath='{.status.loadBalancer.ingress[0].hostname}'
```

Prometheus is hosted at the port `9090`

## How to stop aws cluster

```bash
./stop_aws_cluster.sh 
```

# Exporter

## What metrics are in Exporter:
- ### timestamp
- ### instance
- ### active_connections - See [documentation](https://www.mongodb.com/docs/manual/reference/command/serverStatus/#connections)
- ### available_connections
- ### current_connections
- ### total_created_connections
- ### total_operations_counter - See [documentation](https://www.mongodb.com/docs/manual/reference/command/serverStatus/#opcounters)
- ### total_queries_counter - See [documentation](https://www.mongodb.com/docs/manual/reference/command/top/#mongodb-dbcommand-dbcmd.top)
- ### total_queries_time


## How to use Exporter
### To run exporter in virtual environment first install [Poetry](https://python-poetry.org/docs/#installation)
### Change the directory into /metrics_agent 
```shell
cd metrics_agent
``` 
### Install the environment
```shell
poetry install
``` 
### Run the exporter in two modes!
1. Get predefined metrics as in above:
```shell
poetry run python exporter.py [Your Prometheus endpoint:port]
```
2. Get the metrics of your choice
```shell
poetry run python exporter.py [Your Prometheus endpoint:port] [comma separated metrics]
```