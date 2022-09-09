from dataclasses import dataclass
from http.client import InvalidURL
from pathlib import Path
from typing import Dict, List
import requests
import sys
import pandas as pd
import logging
import time

METRICS_FILENAME = "metrics.csv"
METRICS_FETCH_FREQUENCY = "[1h]"

@dataclass
class SingleMetricResult:
    instance_name: str
    metric_result: int

@dataclass
class MetricNameQuery:
    name: str
    query: str

queries = [
    MetricNameQuery(name="active_connections", query="mongodb_ss_connections{conn_type=\"active\"}"),
    MetricNameQuery(name="available_connections", query="mongodb_ss_connections{conn_type=\"available\"}"),
    MetricNameQuery(name="current_connections", query="mongodb_ss_connections{conn_type=\"current\"}"),
    MetricNameQuery(name="total_created_connections", query=f"delta(mongodb_ss_connections{{conn_type=\"totalCreated\"}}{METRICS_FETCH_FREQUENCY})"),
    MetricNameQuery(name="total_operations_counter", query=f"sum by (instance) (delta(mongodb_ss_opcounters{METRICS_FETCH_FREQUENCY}))"),
    MetricNameQuery(name="total_queries_counter", query="sum by (instance) (delta(mongodb_top_total_count{METRICS_FETCH_FREQUENCY}))"),
    MetricNameQuery(name="total_queries_time", query="sum by (instance) (delta(mongodb_top_total_time{METRICS_FETCH_FREQUENCY}))"),
]

def get_metrics_endpoint() -> str:
    metrics_endpoint = sys.argv[1]
    if not metrics_endpoint.startswith("http://"):
        metrics_endpoint = "http://"+metrics_endpoint
    return metrics_endpoint

def get_instances_with_query_result(query: str) -> List[SingleMetricResult]:
    instances_with_values = []
    try:
        response = requests.get(f"{get_metrics_endpoint()}/api/v1/query",params={'query': query})

        response_json = response.json()
        if response_json["status"] == "success":
            results = response_json["data"]["result"]
            for result in results:
                metric = SingleMetricResult(instance_name=result["metric"]["instance"], metric_result=int(float(result["value"][1])))
                instances_with_values.append(metric)
    except InvalidURL:
        logging.error("Invalid URL")
    
    return instances_with_values

def get_starting_dict_with_instances(query="mongodb_ss_connections{conn_type=\"active\"}") -> Dict[str, Dict]:
    final_dict = {}
    instances_with_values = get_instances_with_query_result(query)
    for metric in instances_with_values:
        final_dict[metric.instance_name] = {}
    return final_dict

def trim_instance_name(instance_name: str) -> str:
    return instance_name.split("-mongo")[0]

def save_metrics_to_file(filename: str, metrics: Dict) -> None:
    json_df = pd.json_normalize(metrics)
    if not Path(filename).exists():
        json_df.to_csv(filename, mode="w+", index=False)
    else:
        json_df.to_csv(filename, mode="a", index=False, header=False)

def export_predefined_metrics():
     while True:
        current_timestamp = int(time.time())
        final_json_dict = get_starting_dict_with_instances()

        for key in final_json_dict:
            final_json_dict[key]['timestamp'] = current_timestamp
            final_json_dict[key]['instance'] = trim_instance_name(key)

        for q in queries:
            instances_with_values = get_instances_with_query_result(q.query)
            for metric in instances_with_values:
                final_json_dict[metric.instance_name][q.name] = metric.metric_result

        save_metrics_to_file(filename="predefined_"+METRICS_FILENAME, metrics=final_json_dict.values())
        time.sleep(24 * 3600)

def export_raw_metrics():
    metric_names = sys.argv[2].split(",")
    current_timestamp = int(time.time())

    for metrix_name in metric_names:
        response = requests.get(f"{get_metrics_endpoint()}/api/v1/query",
            params={'query': metrix_name+METRICS_FETCH_FREQUENCY})
        
        result = response.json()
        result.update({'timestamp': current_timestamp})
        save_metrics_to_file(filename="raw_"+METRICS_FILENAME, metrics=result)

if __name__ == "__main__":
    if len(sys.argv) == 2:
        export_predefined_metrics()
    elif len(sys.argv) == 3:
        export_raw_metrics()
    else:
        print(f"Usage: poetry run python 'Your Prometheus Endpoint' [comma separated metrics]")
        sys.exit(1)
        

