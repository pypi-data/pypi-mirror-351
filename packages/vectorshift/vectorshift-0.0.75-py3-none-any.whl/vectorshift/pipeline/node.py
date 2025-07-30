from abc import ABC
from typing import Any, ClassVar, Dict, List, Type, Protocol, runtime_checkable, TypeVar, Generic
from bson import ObjectId
import re

@runtime_checkable
class NodeOutputs(Protocol):
    """Protocol for node outputs that can be statically type checked."""
    pass

T = TypeVar('T', bound=NodeOutputs)

class Node(ABC):
    # Class-level registry for node types
    _node_registry: ClassVar[Dict[str, Type['Node']]] = {}

    # Common inputs and outputs
    _COMMON_INPUTS: List[Dict[str, Any]] = []
    _COMMON_OUTPUTS: List[Dict[str, Any]] = []
    
    # Configuration patterns and their associated inputs/outputs - to be overridden by subclasses
    _CONFIGS: ClassVar[Dict[str, Dict[str, Any]]] = {}
    
    # List of parameters that affect configuration - to be overridden by subclasses
    _PARAMS: ClassVar[List[str]] = []

    def __init__(self, node_type: str, params: Dict[str, Any], id: str = None, node_name: str = None, execution_mode: str = None):
        """Initialize a node with its type and configuration parameters.
        
        Args:
            node_type: The type of node (e.g., "llm", "text", etc.)
            params: Dictionary of parameter values that determine the node's configuration.
                   These values are locked in for the lifetime of the node.
            id: Optional ID for the node. If not provided, one will be generated.
        """
        self.id = id if id else f"{node_type}_{str(ObjectId())}"
        self.node_type = node_type
        self.name = node_name
        self.task_name: str = None
        self.execution_mode = execution_mode
        
        # Validate and store params
        self._params = {}
        for param in self._PARAMS:
            if param not in params:
                raise ValueError(f"Missing required parameter: {param}")
            self._params[param] = params[param]
        
        # Initialize inputs and outputs based on configuration
        self.inputs: Dict[str, Any] = {}
        self.outputs: List[str] = []
        self.cyclic_inputs: Dict[str, Any] = {}
        
        # Get valid inputs and outputs for these params
        valid_inputs = self._get_valid_inputs_for_params(self._params)
        valid_outputs = self._get_valid_outputs_for_params(self._params)
        
        # Set up inputs with defaults from valid inputs
        for field, input_def in valid_inputs.items():
            self.inputs[field] = input_def.get('value')
        
        # Set up outputs
        self.outputs = valid_outputs

    @classmethod
    def register_node_type(cls, node_type: str):
        """Decorator to register node types with their implementing classes."""
        def decorator(node_class: Type['Node']) -> Type['Node']:
            cls._node_registry[node_type] = node_class
            return node_class
        return decorator

    @classmethod
    def from_json(cls, data: dict) -> 'Node':
        """Create a node instance from a JSON dictionary."""
        node_type = data.get('type')
        if not node_type:
            raise ValueError("JSON data must include 'type' field")
        node_class = cls._node_registry.get(node_type)
        if not node_class:
            raise ValueError(f"Unknown node type: {node_type}")

        return node_class.from_dict(data)

    def __getattr__(self, name: str) -> str:
        """Handle access to output names as attributes."""
        # Get valid outputs for current params
        valid_outputs = self._get_valid_outputs_for_params(self._params)
        
        # Check if output is valid for current configuration
        if name in self.outputs and name in valid_outputs:
            return f"{{{{ {self.id}.{name} }}}}"
        raise AttributeError(
            f"'{self.__class__.__name__}' has no output '{name}' for current parameter values: "
            f"{', '.join(f'{k}={v!r}' for k, v in self._params.items())}\n"
            f"Available outputs: {valid_outputs}"
        )

    @staticmethod
    def _match_config_key(config_key: str, param_values: Dict[str, Any]) -> bool:
        """Match a config key pattern against actual parameter values."""
        if not config_key or not param_values:
            return False
            
        # Split the pattern into parts
        pattern_parts = config_key.split("**")
        if len(pattern_parts) != len(param_values):
            return False
            
        # Check each part against the corresponding value
        for pattern, (param, value) in zip(pattern_parts, param_values.items()):
            if pattern != "(*)" and str(value).lower() != pattern.lower():
                return False
                
        return True

    @classmethod
    def _get_valid_inputs_for_params(cls, param_values: Dict[str, Any]) -> Dict[str, Dict[str, Any]]:
        """Get valid inputs based on the current parameter values."""
        valid_inputs = {input.get('field'): input for input in cls._COMMON_INPUTS}
        valid_inputs['dependencies'] = {'field': 'dependencies', 'type': 'vec<string>', 'value': []}
        
        # Add base inputs from defaults
        for config_key, config in cls._CONFIGS.items():
            if cls._match_config_key(config_key, param_values):
                for input_def in config.get('inputs', []):
                    field = input_def['field']
                    valid_inputs[field] = input_def
        
        return valid_inputs

    @classmethod
    def _get_valid_outputs_for_params(cls, param_values: Dict[str, Any]) -> List[str]:
        """Get valid outputs based on the current parameter values."""
        valid_outputs = set(output.get('field') for output in cls._COMMON_OUTPUTS)
        
        for config_key, config in cls._CONFIGS.items():
            if cls._match_config_key(config_key, param_values):
                if 'outputs' in config:
                    for output_def in config['outputs']:
                        valid_outputs.add(output_def['field'])
        
        return list(valid_outputs)

    @classmethod
    def get_available_inputs(cls, **params) -> Dict[str, Dict[str, Any]]:
        """Get available inputs based on the provided parameter values."""
        param_values = {param: params.get(param) for param in cls._PARAMS}
        return cls._get_valid_inputs_for_params(param_values)

    @classmethod
    def get_available_outputs(cls, **params) -> List[str]:
        """Get available outputs based on the provided parameter values."""
        param_values = {param: params.get(param) for param in cls._PARAMS}
        return cls._get_valid_outputs_for_params(param_values)

    def update_inputs(self, **kwargs):
        """Update input values for the node.
        
        Args:
            **kwargs: Input values to update
            
        Raises:
            ValueError: If an invalid input is provided for the current configuration
        """
        # Get valid inputs for current params
        valid_inputs = self._get_valid_inputs_for_params(self._params)
        
        # Check for invalid inputs
        invalid_inputs = []
        for key in kwargs:
            if key not in valid_inputs:
                invalid_inputs.append(key)
        
        if invalid_inputs:
            param_str = ", ".join(f"{k}={v!r}" for k, v in self._params.items())
            raise ValueError(
                f"Invalid input(s) for current parameters ({param_str}): {invalid_inputs}\n"
                f"Available inputs: {list(valid_inputs.keys())}"
            )
        
        # Update valid inputs
        for key, value in kwargs.items():
            self.inputs[key] = value
    
    def get_dependencies(self) -> tuple[set[str], set[str]]:
        """Get the dependency node ids of the node."""
        non_cyclic_dependencies = set()
        dependencies = set()
        for input_value in self.inputs.values():
            node_input_deps = extract_dependecies_from_node_input(input_value)
            non_cyclic_dependencies.update(node_input_deps - dependencies)
            dependencies.update(node_input_deps)

        for cyclic_input_value in self.cyclic_inputs.values():
            node_input_deps = extract_dependecies_from_node_input(cyclic_input_value)
            dependencies.update(node_input_deps)

        return non_cyclic_dependencies, dependencies
    
    def add_cyclic_input(self, key: str, value: str):
        """Add a cyclic input to the node. This input value will be used during subsequent iterations of the node after the first iteration."""
         # Get valid inputs for current params
        valid_inputs = self._get_valid_inputs_for_params(self._params)
        if key not in valid_inputs:
            param_str = ", ".join(f"{k}={v!r}" for k, v in self._params.items())
            raise ValueError(
                f"Invalid input(s) for current parameters ({param_str}): {key}\n"
                f"Available inputs: {list(valid_inputs.keys())}"
            )
        self.cyclic_inputs[key] = value

    def __str__(self) -> str:
        """Return a string representation of the node as a constructor call.
        
        Returns:
            A string in the format ClassName(input1="value1", input2="value2", ...)
        """
        # Get the actual class name
        class_name = self.__class__.__name__
        
        # Format each input as a key=value pair, properly handling different types
        input_pairs = []
        for field, value in self.inputs.items():
            if value is not None:  # Only include non-None values
                if isinstance(value, str):
                    formatted_value = f'"{value}"'
                elif isinstance(value, (list, dict)):
                    formatted_value = repr(value)
                else:
                    formatted_value = str(value)
                input_pairs.append(f"{field}={formatted_value}")
        
        # Join all input pairs with commas
        inputs_str = ", ".join(input_pairs)
        
        return f"{class_name}({inputs_str})"

    def __repr__(self) -> str:
        """Return a detailed string representation of the node showing type, parameters, inputs, and outputs.
        
        Returns:
            A formatted string showing the node's type, current inputs, and available outputs.
        """
        # Get the actual class name without the module prefix
        class_name = self.__class__.__name__
        
        # Format inputs section
        input_lines = []
        for field, value in self.inputs.items():
            # Format the value, handling special cases
            if isinstance(value, (list, dict)):
                formatted_value = repr(value)
            elif value is None:
                formatted_value = "None"
            else:
                formatted_value = f"'{value}'" if isinstance(value, str) else str(value)
            input_lines.append(f"    {field}: {formatted_value}")
        inputs_str = "\n".join(input_lines) if input_lines else "    None"

        # Format outputs section
        output_lines = []
        for output in self.outputs:
            output_lines.append(f"    {output}")
        outputs_str = "\n".join(output_lines) if output_lines else "    None"

        # Build the complete string
        return f"""{class_name} (id: {self.id})

Inputs:
{inputs_str}

Outputs:
{outputs_str}"""
    
def extract_dependecies_from_node_input(node_input: Any) -> list[str]:
    """Extract dependency node ids from a node input."""
    dependencies = set()
    if isinstance(node_input, str):
        variable_regex = re.compile(r"\{\{\s*([\w.]+)\s*\}\}")
        matches = variable_regex.findall(node_input)
        
        for match in matches:
            # Split by dot and take the first part (node_id)
            if "." in match:
                node_id = match.split(".")[0]
                dependencies.add(node_id)
    
    elif isinstance(node_input, list):
        for item in node_input:
            dependencies.update(extract_dependecies_from_node_input(item))
    
    elif isinstance(node_input, dict):
        for value in node_input.values():
            dependencies.update(extract_dependecies_from_node_input(value))
    
    return dependencies

