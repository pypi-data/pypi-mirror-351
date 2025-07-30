from collections import defaultdict
import time

import anyio

from daydream.knowledge import Graph, Node
from daydream.knowledge.edges import Edge
from daydream.plugins import Plugin
from daydream.plugins.aptible.client import AptibleClient
from daydream.plugins.aptible.nodes.base import inflate_resource
from daydream.plugins.mixins import KnowledgeGraphMixin
from daydream.utils import print


class AptiblePlugin(Plugin, KnowledgeGraphMixin):
    """A plugin for the Aptible PaaS."""

    async def populate_graph(self, graph: Graph) -> None:
        """Initialize the graph with nodes and edges from the Aptible API."""
        self.client = AptibleClient()

        edge_count = 0
        node_counts = defaultdict(int)

        async with self.client.concurrent_paginator("/edges") as (
            edges,
            total_count,
        ):
            notify_threshold = int(total_count * 0.01)

            start = time.perf_counter()

            async for edge in edges:
                source_node = inflate_resource(
                    edge["_embedded"]["source_resource"],
                    _graph=graph,
                )
                destination_node = inflate_resource(
                    edge["_embedded"]["destination_resource"],
                    _graph=graph,
                )

                await graph.add_edge(
                    Edge(
                        source_node=source_node,
                        destination_node=destination_node,
                        properties={
                            "relationship_type": edge["relationship_type"],
                        },
                    )
                )

                node_counts[source_node.node_type] += 1
                node_counts[destination_node.node_type] += 1
                edge_count += 1

                if edge_count % notify_threshold == 0:
                    percent_complete = (edge_count / total_count) * 100
                    print(f"Edge loading: {edge_count}/{total_count} ({percent_complete:.2f}%)")

            print(f"Loaded {edge_count} edges in {time.perf_counter() - start:.2f} seconds")

        # Update app configurations
        async def _update_app_configuration(node: Node) -> None:
            # If the app has no link to a current_configuration, skip it.
            if "current_configuration" not in node.raw_data["_links"]:
                return

            # If the app has no services, it wont have a configuration, so skip it.
            if not node.raw_data["_embedded"]["services"]:
                return

            print(f"Retrieving the current configuration for {node.nid}")
            response = await self.client.get(
                node.raw_data["_links"]["current_configuration"]["href"]
            )

            if response.status_code != 200:
                print(f"Failed to retrieve the current configuration for {node.nid}")
                return

            node.raw_data["_embedded"]["current_configuration"] = response.json()

        async with anyio.create_task_group() as tg:
            async for node in graph.iter_nodes():
                if node.node_type == "aptible_app":
                    tg.start_soon(_update_app_configuration, node)

        print(f"Initialized {edge_count} edges")
        print(f"Initialized {sum(node_counts.values())} nodes:")
        for node_type, count in node_counts.items():
            print(f"  - {node_type}: {count}")
