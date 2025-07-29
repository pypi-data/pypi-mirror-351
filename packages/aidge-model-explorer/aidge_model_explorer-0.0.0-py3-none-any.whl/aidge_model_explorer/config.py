import aidge_core

from .main import AidgeAdapter
from .consts import MODULE_ID

from model_explorer.config import ModelExplorerConfig
from typing import TypedDict
from typing_extensions import NotRequired

ModelSource = TypedDict(
    'ModelSource', {'url': str, 'adapterId': NotRequired[str]}
)

def config() -> ModelExplorerConfig:
  """Create a new config object."""
  return AidgeExplorerConfig()

class AidgeExplorerConfig(ModelExplorerConfig):
    """Stores the data to be visualized in Model Explorer."""

    # Required
    # pylint: disable=useless-parent-delegation
    def __init__(self) -> None:
        super().__init__()

    def add_graphview(self, graphview: aidge_core.GraphView, name:str) -> 'ModelExplorerConfig':
        """Add a aidge_core.GraphView to the list of graph to visualize

        :param graphview: Graph view to add to the list
        :type graphview: aidge_core.GraphView
        :return: Return a reference to itself
        :rtype: ModelExplorerConfig
        """
        aidge_core.Log.notice(f"Converting GraphView {name}...")
        adapter = AidgeAdapter()
        graphs_index = len(self.graphs_list)
        graphs = adapter.convert_graphview(graphview, {}, name=name)
        self.graphs_list.append(graphs)

        # Construct model source.
        #
        # The model source has a special format, in the form of:
        # graphs://{name}/{graphs_index}
        model_source: ModelSource = {
            'url': f'graphs://{name}/{graphs_index}',
            'adapterId': MODULE_ID
        }
        self.model_sources.append(model_source)
        return self
