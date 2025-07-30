import asyncio

from pydantic import AwareDatetime

from daydream.models import Metric


class HasMetrics:
    """Capability for nodes that can retrieve metrics."""

    async def list_available_metrics(self) -> list[str]:
        """List the names of all available metrics for a given entity."""
        raise NotImplementedError

    async def get_metric(
        self,
        metric_name: str,
        time_range_start: AwareDatetime,
        time_range_end: AwareDatetime,
    ) -> Metric | str:
        """Retrieve the data for a specific metric for a given entity."""
        raise NotImplementedError

    async def get_metrics(
        self,
        time_range_start: AwareDatetime,
        time_range_end: AwareDatetime,
        metric_names: list[str] | None = None,
    ) -> list[Metric | str]:
        """Retrieve the data for multiple metrics for a given entity.

        If no metric names are provided, all available metrics will be retrieved.

        Args:
            node: The node for which to retrieve metrics.
            time_range_start: The start time of the time range to retrieve metrics for.
            time_range_end: The end time of the time range to retrieve metrics for.
            metric_names: The names of the metrics to retrieve.

        Returns:
            A list of metrics.
        """
        metric_names = metric_names or await self.list_available_metrics()
        results = await asyncio.gather(
            *[self.get_metric(m, time_range_start, time_range_end) for m in metric_names],
            return_exceptions=True,
        )

        if any(isinstance(r, Exception) for r in results):
            raise ExceptionGroup(
                "Failed to retrieve metrics", [e for e in results if isinstance(e, Exception)]
            )

        return [r for r in results if isinstance(r, Metric)]
