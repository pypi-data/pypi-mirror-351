import asyncio
from typing import Any

from aioboto3 import Session

from daydream.knowledge import Node
from daydream.models import CloudwatchMetric, Metric
from daydream.plugins.aws.utils import (
    list_accessible_regions_for_service,
    swallow_boto_client_access_errors,
)


class AwsNode(Node):
    """A base class for all AWS nodes."""

    def __init__(self, **kwargs: Any) -> None:
        super().__init__(**kwargs)
        self._session = Session()

    @property
    def session(self) -> Session:
        return self._session

    async def _get_cloudwatch_metric_for_accessible_regions(
        self,
        **cloudwatch_params: Any,
    ) -> Metric:
        accessible_regions = await list_accessible_regions_for_service(self.session, "cloudwatch")

        return Metric(
            metric_name=cloudwatch_params["MetricName"],
            data=[
                metric
                for metric in await asyncio.gather(
                    *(
                        self._get_cloudwatch_metric_for_region(region, **cloudwatch_params)
                        for region in accessible_regions
                    )
                )
                if metric.data
            ],
        )

    async def _get_cloudwatch_metric_for_region(
        self,
        region: str,
        **cloudwatch_params: Any,
    ) -> CloudwatchMetric:
        async with (
            swallow_boto_client_access_errors(service_name="cloudwatch", region=region),
            self.session.client("cloudwatch", region_name=region) as client,
        ):
            result = await client.get_metric_statistics(
                **cloudwatch_params,
            )

            return CloudwatchMetric(
                region=region,
                metric_name=cloudwatch_params["MetricName"],
                data=result.get("Datapoints", []),
            )
