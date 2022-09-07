import csv
from dataclasses import dataclass
from email import header
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
PROMETHEUS_ENDPOINT = sys.argv[1]

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

def get_instances_with_query_result(query: str) -> List[SingleMetricResult]:
    instances_with_values = []
    try:
        response = requests.get('{0}/api/v1/query'.format(PROMETHEUS_ENDPOINT),params={'query': query})

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

if __name__ == "__main__":
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

        json_df = pd.json_normalize(final_json_dict.values())
        if not Path(METRICS_FILENAME).exists():
            json_df.to_csv(METRICS_FILENAME, mode="w+", index=False)
        else:
            json_df.to_csv(METRICS_FILENAME, mode="a", index=False, header=False)

        time.sleep(24 * 3600)

