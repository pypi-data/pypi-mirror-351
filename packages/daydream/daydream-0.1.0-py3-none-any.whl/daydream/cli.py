import time

import anyio
import typer

from daydream import mcp
from daydream.config import load_config
from daydream.config.utils import get_config_dir
from daydream.knowledge import Graph
from daydream.plugins import PluginManager
from daydream.plugins.mixins import KnowledgeGraphMixin

app = typer.Typer(context_settings={"help_option_names": ["-h", "--help"]})

PROFILE_OPTION = typer.Option(
    ...,
    "--profile",
    envvar="DAYDREAM_PROFILE",
    help="Use profiles to manage multiple graphs",
    show_default=True,
)
PROFILE_OPTION.default = "default"


@app.command()
def start(
    profile: str = PROFILE_OPTION,
    disable_sse: bool = typer.Option(
        False, "--disable-sse", help="Disable the SSE transport for the MCP Server"
    ),
    disable_stdio: bool = typer.Option(
        False, "--disable-stdio", help="Disable the stdio transport for the MCP Server"
    ),
) -> None:
    """Start the Daydream MCP Server"""
    anyio.run(mcp.start, profile, disable_sse, disable_stdio)


@app.command()
def build_graph(
    profile: str = PROFILE_OPTION,
) -> None:
    """Build a knowledge graph for your cloud infrastructure"""

    async def _build_graph() -> None:
        print("Building graph...")

        start_time = time.perf_counter()

        graph = Graph()
        config = load_config(profile, create=True)
        output_path = (get_config_dir(profile) / "graph.json").resolve()
        plugin_manager = PluginManager(config)

        async with anyio.create_task_group() as tg:
            for plugin in plugin_manager.get_plugins_with_capability(KnowledgeGraphMixin):
                print(f"Populating graph with the {plugin.name} plugin...")
                tg.start_soon(plugin.populate_graph, graph)

        await graph.infer_edges()

        print(f"Saving graph to {output_path!s}...")
        await graph.save(output_path)

        end_time = time.perf_counter()
        print(f"Graph built in {end_time - start_time:.2f} seconds")
        print(f"Graph saved to {output_path!s}")

    anyio.run(_build_graph)


@app.command()
def visualize(
    profile: str = PROFILE_OPTION,
    topology: bool = typer.Option(False, "--topology"),
) -> None:
    """Visualize the knowledge graph topology"""

    async def _visualize() -> None:
        graph = Graph(get_config_dir(profile) / "graph.json")

        if topology:
            graph = await graph.get_topology()

        print(await graph.to_pydot())

    anyio.run(_visualize)


def main() -> None:
    app()


if __name__ == "__main__":
    main()
