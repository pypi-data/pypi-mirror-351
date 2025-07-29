from aidge_core import GraphView
from typing import Dict
from model_explorer import Adapter, AdapterMetadata, ModelExplorerGraphs
from pathlib import Path
from .converters import runtime_converter, onnx_converter
from .consts import (
    MODULE_ID,
    MODULE_NAME,
    MODULE_DESCRIPTION
)

class AidgeAdapter(Adapter):
    metadata = AdapterMetadata(id=MODULE_ID,
                                name=MODULE_NAME,
                                description=MODULE_DESCRIPTION,
                                source_repo='https://gitlab.eclipse.org/eclipse/aidge/aidge_model_explorer',
                                fileExts=["onnx"])
    # Required.
    # pylint: disable=useless-parent-delegation
    def __init__(self):
        super().__init__()

    def convert(self, model_path: str, settings: Dict) -> ModelExplorerGraphs:
        graph = None
        model_path = Path(model_path)
        if model_path.suffix == ".onnx":
            graph = onnx_converter.convert_onnx(model_path, settings)
        else:
            raise RuntimeError(f"{MODULE_NAME} does not support {model_path.suffix} files.")
        return {'graphs': [graph]}

    def convert_graphview(self, model: GraphView, settings: Dict, name='') -> ModelExplorerGraphs:
        """Given an aidge_core.GraphView convert it to a ModelExplorerGraphs

        :param model: Aidge graph to convert
        :type model: aidge_core.GraphView
        :param settings: The settings that config the visualization.
        :type settings: Dict
        :param name: Name of the graph, defaults to ''
        :type name: str, optional
        """
        graph = runtime_converter.convert_graphview(model, name)
        return {'graphs': [graph]}

