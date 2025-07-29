import aidge_core
import json
import numpy as np
from model_explorer import graph_builder

def _is_metaop(node): return isinstance(node.get_operator(), aidge_core.MetaOperatorOp)

def _generate_unique_ids(graphview):

    def rec_add(graphview):
        view = aidge_core.GraphView()
        view.add(graphview)
        for n in graphview.get_nodes():
            if _is_metaop(n):
                view.add(rec_add(n.get_operator().get_micro_graph()))
        return view

    view_on_all_nodes = rec_add(graphview)

    for node, name in view_on_all_nodes.get_ranked_nodes_name("{0}[{1}#{3}]").items():
            aidge_core.Log.debug(f"Setting node name: {name}")
            view_on_all_nodes.remove(node, include_learnable_parameters=False)
            node.set_name(name)

def _tensor_to_json(tensor: aidge_core.Tensor) -> str:
    if not tensor.has_impl():
        aidge_core.Log.info("Tensor has no implementation; skipping value.")
        return ""
    try:
        array = np.array(tensor)
        size_limit = 20
        if size_limit < 0 or size_limit >= array.size:
            # Use separators=(',', ':') to remove spaces
            return json.dumps(array.tolist(), separators=(",", ":"))
        # Show the first `size_limit` elements if the tensor is too large
        return json.dumps(
            (array.flatten())[:size_limit].tolist(), separators=(",", ":")
        ).replace("]", ", ...]")
    except Exception as e:
        aidge_core.Log.warn("Failed to display tensor (%s): %s", tensor, e)
    return ""

def _get_in_name(aidge_node, in_idx):
    inputs_name = []
    if hasattr(aidge_node.get_operator(), "get_inputs_name"):
        inputs_name = aidge_node.get_operator().get_inputs_name()
    in_name = f"Input#{in_idx}"
    if in_idx < len(inputs_name):
        in_name = inputs_name[in_idx]
    return in_name

def _get_out_name(aidge_node, out_idx):
    outputs_name = []
    if hasattr(aidge_node.get_operator(), "get_outputs_name"):
        outputs_name = aidge_node.get_operator().get_outputs_name()
    out_name = f"Output#{out_idx}"
    if out_idx < len(outputs_name):
        out_name = outputs_name[out_idx]
    return out_name


def _convert_node(aidge_node, namespace='') -> dict[str, graph_builder.GraphNode]:
    aidge_operator = aidge_node.get_operator()
    node_name = aidge_node.name()
    # Convert nodes
    aidge_core.Log.debug(f"Converting {node_name} ...")
    converted_nodes: dict[str, graph_builder.GraphNode] = {}
    # if namespace != "": namespace += "/"
    if  _is_metaop(aidge_node):
        # MetaOperator are handled by namespace
        if namespace != "": namespace += "/"
        # Recursive call for each sub node with the
        # namespace corresponding to the MetaOperator label
        for sub_node in aidge_node.get_operator().get_micro_graph().get_nodes():
            converted_nodes.update(_convert_node(
                    sub_node,
                    namespace=f"{namespace}{node_name}"
            ))
    else:
        bg_color = ""
        border_color = ""
        # Border color on hover
        h_border_color = ""

        if isinstance(aidge_node.get_operator(), aidge_core.GenericOperatorOp):
            border_color="#d9534f"
            bg_color="#fbeaea"

        # Create node
        converted_node = graph_builder.GraphNode(
                id=f"{namespace}{node_name}",
                label=node_name,
                namespace=namespace,
                style=graph_builder.GraphNodeStyle(
                    backgroundColor=bg_color,
                    borderColor=border_color,
                    hoveredBorderColor=h_border_color
                ),
        )
        # Add node attributes
        if aidge_operator.attr:
            aidge_core.Log.debug("Attributes:")
            for key, value in aidge_operator.attr.dict().items():
                # Dirty fix @pineapple help me! :D
                if isinstance(value, aidge_core.Tensor):
                    value = str(value).replace("{", "[").replace("}", "]")
                aidge_core.Log.debug(f"\t- {key}: {value}")
                converted_node.attrs.append(
                    graph_builder.KeyValue(
                        key=key,
                        value=str(value)
                    )
                )

        # Add output information
        for out_id in range(aidge_node.get_nb_outputs()):
            out_tensor = aidge_node.get_operator().get_output(out_id)
            output_metadata = graph_builder.MetadataItem(
                id=str(out_id),
                attrs=[
                    graph_builder.KeyValue(key='data_format', value=str(out_tensor.dformat())),
                    graph_builder.KeyValue(key='data_type', value=str(out_tensor.dtype())),
                    graph_builder.KeyValue(key='size', value=str(out_tensor.size())),
                    graph_builder.KeyValue(key='dims', value=str(out_tensor.dims())),
                    graph_builder.KeyValue(key='values', value=_tensor_to_json(out_tensor)),
                    # __tensor_tag is a special tag that "name" the edge
                    graph_builder.KeyValue(key='__tensor_tag', value=_get_out_name(aidge_node, out_id))
                ]
            )
            converted_node.outputsMetadata.append(output_metadata)
        converted_nodes[node_name] = converted_node

    return converted_nodes

def convert_graphview(graphview: aidge_core.GraphView, name: str) -> graph_builder.Graph:
    meg: graph_builder.Graph = graph_builder.Graph(id=name)
    converted_nodes = {}
    # Set unique names to every operator of the graph
    _generate_unique_ids(graphview)
    # First step convert aidge node
    for aidge_node in graphview.get_nodes():
        converted_nodes.update(_convert_node(aidge_node))

    # Connect nodes together
    # Note: this is done after creating every nodes as we need
    # To know the id of every parents this is difficult to do for two reasons:
    # - 1. Inside of a MetaOperator we don't have access to parents and children of the MetaOp
    # - 2. GraphView.get_nodes returns an unordered list so we don't have guarantee that
    # the parent node id has been generated
    flatten_graphview = graphview.clone()
    aidge_core.expand_metaops(flatten_graphview, recursive=True)
    for aidge_node in flatten_graphview.get_nodes():
        # Connect nodes
        for in_id, (parent_node, out_id) in enumerate(aidge_node.inputs()):
            if parent_node:
                aidge_core.Log.debug(f"Connecting {parent_node.name()} -> {aidge_node.name()}")
                converted_nodes[aidge_node.name()].incomingEdges.append(
                    graph_builder.IncomingEdge(
                        sourceNodeId=converted_nodes[parent_node.name()].id,
                        targetNodeInputId=str(in_id),
                        sourceNodeOutputId=str(out_id)
                    )
                )
            input_metadata = graph_builder.MetadataItem(
                id=str(in_id),
                attrs=[
                    graph_builder.KeyValue(key='__tensor_tag', value=_get_in_name(aidge_node, in_id))
                ]
            )
            converted_nodes[aidge_node.name()].inputsMetadata.append(input_metadata)
    meg.nodes.extend(converted_nodes.values())

    return meg