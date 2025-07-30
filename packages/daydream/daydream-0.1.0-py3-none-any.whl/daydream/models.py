from typing import Any

from pydantic import BaseModel


class Metric(BaseModel, extra="allow"):
    metric_name: str
    data: Any


class CloudwatchMetric(Metric):
    region: str
