## How to deploy application

### Prerequisites

```bash
ansible-galaxy collection install kubernetes.core
pip3 install kubernetes
```

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

## Get Prometheus url

```bash
kubectl get svc prometheus --output jsonpath='{.status.loadBalancer.ingress[0].hostname}'
```

## How to stop aws cluster

```bash
./stop_aws_cluster.sh 
```