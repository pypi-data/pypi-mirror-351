import base64
from bson import ObjectId
from typing import Any, Optional

from vectorshift.pipeline.graph import PipelineGraph
from vectorshift.pipeline.node import Node
from vectorshift.request import request, stream_request

class Pipeline:
    def __init__(self, nodes: list[Node] = None, id: str = None, branch_id: Optional[str] = None, inputs: dict[str, Any] = None, outputs: dict[str, Any] = None):
        self.id = id
        self.nodes = nodes if nodes else []
        self.branch_id = branch_id
        self.inputs = inputs or {}
        self.outputs = outputs or {}

    @classmethod
    def new(cls, name: str, nodes: list[Node] = []):
        """
        Create a new pipeline with the specified parameters.
        
        Args:
            name: The name of the pipeline.
            nodes: List of nodes to include in the pipeline.
            
        Returns:
            A new Pipeline instance.
        """
        data = {
            "name": name,
            "nodes": {},
            "canvas_metadata": {
                "nodes": {},
                "edges": []
            }
        }

        node_type_counter = {}

        for node in nodes:
            node_name = node.name or f"{node.node_type}_{node_type_counter.get(node.node_type, 0)}"
            node_data = {
                "id": node.id,
                "name": node_name,
                "type": node.node_type,
                "inputs": node.inputs,
                "outputs": node.outputs,
                "task_name": node.task_name,
                "execution_mode": node.execution_mode or "normal"
            }
            if node.cyclic_inputs:
                node_data["cyclic_inputs"] = node.cyclic_inputs
            if node.node_type == "input":
                data["inputs"][node_name] = node.inputs.get("input_type", "string")
            elif node.node_type == "output":
                data["outputs"][node_name] = node.inputs.get("output_type", "string")
            data["nodes"][node.id] = node_data
            node_type_counter[node.node_type] = node_type_counter.get(node.node_type, 0) + 1
        
        graph = PipelineGraph.new(nodes)
        graph.validate()
        graph.populate_node_canvas_metadata()

        data["canvas_metadata"]["nodes"] = {
            node_id: metadata.model_dump() 
            for node_id, metadata in graph.node_canvas_metadata.items()
        }
        
        data["canvas_metadata"]["edges"] = [
            edge.model_dump() 
            for edge in graph.edges
        ]

        response = request("POST", "/pipeline", json=data)

        return cls(
            nodes=nodes,
            id=response["id"],
            branch_id=response["branch_id"]
        )

    def add_node(self, node: Node):
        """
        Add a node to the pipeline.

        Args:
            node: The node to add to the pipeline.

        Returns:
            A dictionary containing the status of the addition operation.
        """
        self.nodes.append(node)
        data = {
            "nodes": {},
            "canvas_metadata": {
                "nodes": {},
                "edges": []
            }
        }

        node_type_counter = {}

        for node in self.nodes:
            node_name = node.name or f"{node.node_type}_{node_type_counter.get(node.node_type, 0)}"
            node_data = {
                "id": node.id,
                "name": node_name,
                "type": node.node_type,
                "inputs": node.inputs,
                "outputs": node.outputs,
                "task_name": node.task_name,
                "execution_mode": node.execution_mode or "normal"
            }
            if node.cyclic_inputs:
                node_data["cyclic_inputs"] = node.cyclic_inputs
            if node.node_type == "input":
                data["inputs"][node_name] = node.inputs.get("input_type", "string")
            elif node.node_type == "output":
                data["outputs"][node_name] = node.inputs.get("output_type", "string")
            data["nodes"][node.id] = node_data
            node_type_counter[node.node_type] = node_type_counter.get(node.node_type, 0) + 1
        
        graph = PipelineGraph.new(self.nodes)
        graph.validate()
        graph.populate_node_canvas_metadata()

        data["canvas_metadata"]["nodes"] = {
            node_id: metadata.model_dump() 
            for node_id, metadata in graph.node_canvas_metadata.items()
        }
        
        data["canvas_metadata"]["edges"] = [
            edge.model_dump() 
            for edge in graph.edges
        ]

        data["branch_id"] = self.branch_id

        response = request("POST", f"/update/pipeline/{self.id}", json=data)

        return response

    def save(self, nodes: list[Node] = []):
        """
        Overwrites the pipeline with the specified nodes.

        Args:
            nodes: List of nodes to overwrite the pipeline with.

        Returns:
            A dictionary containing the status of the save operation.
        """

        self.nodes = nodes
        data = {
            "nodes": {},
            "canvas_metadata": {
                "nodes": {},
                "edges": []
            }
        }

        node_type_counter = {}

        for node in self.nodes:
            node_name = node.name or f"{node.node_type}_{node_type_counter.get(node.node_type, 0)}"
            node_data = {
                "id": node.id,
                "name": node_name,
                "type": node.node_type,
                "inputs": node.inputs,
                "outputs": node.outputs,
                "task_name": node.task_name,
                "execution_mode": node.execution_mode or "normal"
            }
            if node.cyclic_inputs:
                node_data["cyclic_inputs"] = node.cyclic_inputs
            if node.node_type == "input":
                data["inputs"][node_name] = node.inputs.get("input_type", "string")
            elif node.node_type == "output":
                data["outputs"][node_name] = node.inputs.get("output_type", "string")
            data["nodes"][node.id] = node_data
            node_type_counter[node.node_type] = node_type_counter.get(node.node_type, 0) + 1
        
        graph = PipelineGraph.new(self.nodes)
        graph.validate()
        graph.populate_node_canvas_metadata()

        data["canvas_metadata"]["nodes"] = {
            node_id: metadata.model_dump() 
            for node_id, metadata in graph.node_canvas_metadata.items()
        }
        
        data["canvas_metadata"]["edges"] = [
            edge.model_dump() 
            for edge in graph.edges
        ]
        data["branch_id"] = self.branch_id

        response = request("POST", f"/update/pipeline/{self.id}", json=data)

        return response

    def run(self, inputs: dict[str, Any], stream: bool = False) -> dict[str, Any]:
        """
        Run the pipeline with the specified inputs.
        
        Args:
            inputs: Dictionary of input values for the pipeline.
            stream: Whether to stream the response. (Set true only when pipeline has an output node with a streaming llm input)
            
        Returns:
            Union[dict[str, Any], Generator]: A dictionary containing pipeline outputs and run_id. If stream is True, returns a generator that yields response chunks.
        
        Raises:
            Exception: If the pipeline execution fails.
        """

        pipeline_inputs = {}

        for input_name, input_value in inputs.items():
            if input_name in self.inputs:
                if self.inputs[input_name] == "file" and isinstance(input_value, str):
                    with open(input_value, "rb") as file:
                        raw_bytes = file.read()
                        file_dict = dict(
                            type="file",
                            raw_bytes=base64.b64encode(raw_bytes).decode('utf-8'),
                        )
                        pipeline_inputs[input_name] = file_dict
                else:
                    pipeline_inputs[input_name] = input_value

        data = {
            "inputs": pipeline_inputs
        }

        if stream:
            data["stream"] = True
            return stream_request("POST", f"/pipeline/{self.id}/run", json=data)
        else:
            return request("POST", f"/pipeline/{self.id}/run", json=data)

    def bulk_run(self, inputs: list[dict[str, Any]]) -> list[dict[str, Any]]:
        """
        Run the pipeline with a list of specified inputs.
        
        Args:
            inputs: List of dictionaries of input values for the pipeline.
            
        Returns:
            A list of dictionaries containing the run_id and outputs for each set of inputs.

        Raises:
            Exception: If the pipeline execution fails.
        """
        data = {
            "runs": [{"inputs": input} for input in inputs]
        }

        return request("POST", f"/pipeline/{self.id}/bulk-run", json=data)

    @classmethod
    def fetch(
        cls,
        id: Optional[str] = None,
        name: Optional[str] = None,
        username: Optional[str] = None,
        org_name: Optional[str] = None,
    ) -> 'Pipeline':
        """Fetches an existing pipeline.
        
        Args:
            id (Optional[str]): The unique identifier of the pipeline to fetch.
            name (Optional[str]): The name of the pipeline to fetch.
            username (Optional[str]): The username of the pipeline owner.
            org_name (Optional[str]): The organization name of the pipeline owner.
            
        Returns:
            Pipeline: The fetched Pipeline instance.
            
        Raises:
            ValueError: If neither id nor name is provided.
            Exception: If the pipeline couldn't be fetched.
        """
        if id is None and name is None:
            raise ValueError("Either id or name must be provided")
        query = {}
        if id is not None:
            query["id"] = id
        if name is not None:
            query["name"] = name
        if username is not None:
            query["username"] = username
        if org_name is not None:
            query["org_name"] = org_name
        response = request("GET", f'/pipeline', query=query)

        obj = response['object']
        
        return cls.from_json(obj)
    
    def delete(self):
        """Deletes an existing pipeline.
        
        Returns:
            dict: A dictionary containing the status of the deletion operation.
            
        Raises:
            Exception: If the pipeline couldn't be deleted.
        """
        response = request("DELETE", f"/pipeline/{self.id}")
        return response

    @classmethod
    def from_json(cls, data: dict) -> 'Pipeline':
        nodes = [Node.from_json(node_data) for node_data in data.get('nodes', {}).values()]
        inputs, outputs = {}, {}
        for node in nodes:
            if node.node_type == "input":
                inputs[node.name] = node.inputs.get("input_type", "string")
            elif node.node_type == "output":
                outputs[node.name] = node.inputs.get("output_type", "string")
        return cls(nodes=nodes, id=data.get('_id'), branch_id=data.get('mainBranch'), inputs=inputs, outputs=outputs)

# pipeline = Pipeline.fetch(id="64cca0b6c819a3e6ac39fe89")
