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
    MetricNameQuery(name="total_queries_counter", query=f"sum by (instance) (delta(mongodb_top_total_count{METRICS_FETCH_FREQUENCY}))"),
    MetricNameQuery(name="total_queries_time", query=f"sum by (instance) (delta(mongodb_top_total_time{METRICS_FETCH_FREQUENCY}))"),
]


def get_metrics_endpoint() -> str:
    metrics_endpoint = sys.argv[1]
    if not metrics_endpoint.startswith("http://"):
        metrics_endpoint = "http://"+metrics_endpoint
    return metrics_endpoint


def get_instances_with_query_result(query: str):
    try:
        response = requests.get(f"{get_metrics_endpoint()}/api/v1/query",params={'query': query})

        response_json = response.json()
        if response_json["status"] == "success":
            table = parse_metrics(response_json)

            return table
    except InvalidURL:
        logging.error("Invalid URL")


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
        for q in queries:
            instances_with_values = get_instances_with_query_result(q.query)

            save_metrics_to_file(filename="predefined_"+q.name, metrics=instances_with_values)
        time.sleep(30)


SKIPPED_FIELDS = ["__name__", "job", "cl_id", "cl_role"]


def parse_metrics(raw_json):
    table = []

    for row in raw_json["data"]["result"]:
        if "values" in row:
            for val in row["values"]:
                timestamp = val[0]
                value = val[1]

                metric = {key: value for key, value in row["metric"].items() if key not in SKIPPED_FIELDS}
                metric["timestamp"] = timestamp
                metric["value"] = value

                table.append(metric)
        elif "value" in row:
            timestamp = row["value"][0]
            value = row["value"][1]

            metric = {key: value for key, value in row["metric"].items() if key not in SKIPPED_FIELDS}
            metric["timestamp"] = timestamp
            metric["value"] = value

            table.append(metric)

    return table

def export_raw_metrics():
    metric_names = sys.argv[2].split(",")

    for metrix_name in metric_names:
        response = requests.get(f"{get_metrics_endpoint()}/api/v1/query",
            params={'query': metrix_name+METRICS_FETCH_FREQUENCY})
        
        result = response.json()
        table = parse_metrics(result)

        save_metrics_to_file(filename="raw_"+metrix_name, metrics=table)


if __name__ == "__main__":
    if len(sys.argv) == 2:
        export_predefined_metrics()
    elif len(sys.argv) == 3:
        export_raw_metrics()
    else:
        print(f"Usage: poetry run python 'Your Prometheus Endpoint' [comma separated metrics]")
        sys.exit(1)
        

