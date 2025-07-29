import aidge_onnx
from model_explorer import ModelExplorerGraphs
from typing import Dict
from .runtime_converter import convert_graphview
from pathlib import Path

def convert_onnx(model_path: Path, settings: Dict) -> ModelExplorerGraphs:
    return convert_graphview(aidge_onnx.load_onnx(model_path), name=model_path.stem)
