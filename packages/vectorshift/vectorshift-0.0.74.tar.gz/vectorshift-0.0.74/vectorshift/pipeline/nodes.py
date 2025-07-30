"""
Generated node classes from TOML configuration.
This file is auto-generated. Do not edit manually.
"""

from typing import Any, Dict, List, Optional, Union, Protocol, runtime_checkable
from .node import Node, NodeOutputs


@Node.register_node_type("append_files")
class AppendFilesNode(Node):
    """
    Append files together in successive fashion

    ## Inputs
    ### Common Inputs
        file_type: The type of file to append.
        selected_files: The number of files to be appended. Files will be appended in successive fashion (e.g., file-1 first, then file-2, etc.).

    ## Outputs
    ### Common Outputs
        file: A file with all the files appended together.
    """

    # Common inputs and outputs
    _COMMON_INPUTS = [
        {
            "field": "file_type",
            "helper_text": "The type of file to append.",
            "value": "PDF",
            "type": "enum<string>",
        },
        {
            "field": "selected_files",
            "helper_text": "The number of files to be appended. Files will be appended in successive fashion (e.g., file-1 first, then file-2, etc.).",
            "value": [""],
            "type": "vec<file>",
        },
    ]

    # Common outputs and inputs
    _COMMON_OUTPUTS = [
        {"field": "file", "helper_text": "A file with all the files appended together."}
    ]

    # Configuration patterns and their associated inputs/outputs
    _CONFIGS = {}

    # List of parameters that affect configuration
    _PARAMS = []

    def __init__(
        self,
        id: Optional[str] = None,
        node_name: Optional[str] = None,
        execution_mode: Optional[str] = None,
        file_type: str = "PDF",
        selected_files: List[str] = [""],
        **kwargs
    ):
        # Initialize with params
        params = {}

        super().__init__(
            node_type="append_files",
            params=params,
            id=id,
            node_name=node_name,
            execution_mode=execution_mode,
        )

        # Set input values
        if file_type is not None:
            self.inputs["file_type"] = file_type
        if selected_files is not None:
            self.inputs["selected_files"] = selected_files

        # Update any additional inputs
        if kwargs:
            self.update_inputs(**kwargs)

    @property
    def file(self) -> str:
        """
        A file with all the files appended together.


        Raises:
            AttributeError: If this output is not available for the current parameter values
        """
        return self.__getattr__("file")

    @classmethod
    def from_dict(cls, data: dict) -> "AppendFilesNode":
        """Create a node instance from a dictionary."""
        inputs = data.get("inputs", {})
        id = data.get("id", None)
        name = data.get("name", None)
        execution_mode = data.get("execution_mode", None)
        return cls(**inputs, id=id, node_name=name, execution_mode=execution_mode)


@Node.register_node_type("sticky_note")
class StickyNoteNode(Node):
    """


    ## Inputs
    ### Common Inputs
        text: The text input

    ## Outputs
        None
    """

    # Common inputs and outputs
    _COMMON_INPUTS = [
        {
            "field": "text",
            "helper_text": "The text input",
            "value": "",
            "type": "string",
        }
    ]

    # Common outputs and inputs
    _COMMON_OUTPUTS = []

    # Configuration patterns and their associated inputs/outputs
    _CONFIGS = {}

    # List of parameters that affect configuration
    _PARAMS = []

    def __init__(
        self,
        id: Optional[str] = None,
        node_name: Optional[str] = None,
        execution_mode: Optional[str] = None,
        text: str = "",
        **kwargs
    ):
        # Initialize with params
        params = {}

        super().__init__(
            node_type="sticky_note",
            params=params,
            id=id,
            node_name=node_name,
            execution_mode=execution_mode,
        )

        # Set input values
        if text is not None:
            self.inputs["text"] = text

        # Update any additional inputs
        if kwargs:
            self.update_inputs(**kwargs)

    @classmethod
    def from_dict(cls, data: dict) -> "StickyNoteNode":
        """Create a node instance from a dictionary."""
        inputs = data.get("inputs", {})
        id = data.get("id", None)
        name = data.get("name", None)
        execution_mode = data.get("execution_mode", None)
        return cls(**inputs, id=id, node_name=name, execution_mode=execution_mode)


@Node.register_node_type("transformation")
class TransformationNode(Node):
    """


    ## Inputs
    ### Common Inputs
        transformation_id: The transformation_id input
    ### [transformations._id.<A>]
        [<A>.inputs]: The [<A>.inputs] input

    ## Outputs
    ### [transformations._id.<A>]
        [<A>.outputs]: The [<A>.outputs] output
    """

    # Common inputs and outputs
    _COMMON_INPUTS = [
        {
            "field": "transformation_id",
            "helper_text": "The transformation_id input",
            "value": "",
            "type": "enum<string>",
        }
    ]

    # Common outputs and inputs
    _COMMON_OUTPUTS = []

    # Configuration patterns and their associated inputs/outputs
    _CONFIGS = {
        "[transformations._id.<A>]": {
            "inputs": [{"field": "[<A>.inputs]", "type": ""}],
            "outputs": [{"field": "[<A>.outputs]", "type": ""}],
        }
    }

    # List of parameters that affect configuration
    _PARAMS = ["transformation_id"]

    def __init__(
        self,
        id: Optional[str] = None,
        node_name: Optional[str] = None,
        execution_mode: Optional[str] = None,
        transformation_id: str = "",
        **kwargs
    ):
        # Initialize with params
        params = {}
        params["transformation_id"] = transformation_id

        super().__init__(
            node_type="transformation",
            params=params,
            id=id,
            node_name=node_name,
            execution_mode=execution_mode,
        )

        # Set input values
        if transformation_id is not None:
            self.inputs["transformation_id"] = transformation_id

        # Update any additional inputs
        if kwargs:
            self.update_inputs(**kwargs)

    @classmethod
    def from_dict(cls, data: dict) -> "TransformationNode":
        """Create a node instance from a dictionary."""
        inputs = data.get("inputs", {})
        id = data.get("id", None)
        name = data.get("name", None)
        execution_mode = data.get("execution_mode", None)
        return cls(**inputs, id=id, node_name=name, execution_mode=execution_mode)


@Node.register_node_type("chat_file_reader")
class ChatFileReaderNode(Node):
    """
    Allows for document upload within chatbots (often connected to the LLM node).

    ## Inputs
    ### Common Inputs
        chunk_overlap: The number of tokens of overlap between chunks (1 token = 4 characters)
        chunk_size: The number of tokens per chunk (1 token = 4 characters)
        file_parser: The processing model with which the document will be processed. Default processing model includes standard document parsing / OCR. Llamaparse will allow for ability to read documents with complex features (e.g., tables, charts, etc.). Llamaparse will be charged at 0.3 cents per page. Textract for most advanced data extraction and will be charged at 1.5 cents per page.
        max_docs_per_query: Sets the maximum number of chunks to retrieve for each query
        retrieval_unit: Return the most relevant Chunks (text content) or Documents (will return the document metadata)

    ## Outputs
    ### Common Outputs
        documents: The uploaded file (in the chat interface) is processed into text
    """

    # Common inputs and outputs
    _COMMON_INPUTS = [
        {
            "field": "chunk_overlap",
            "helper_text": "The number of tokens of overlap between chunks (1 token = 4 characters)",
            "value": 200,
            "type": "int32",
        },
        {
            "field": "chunk_size",
            "helper_text": "The number of tokens per chunk (1 token = 4 characters)",
            "value": 1000,
            "type": "int32",
        },
        {
            "field": "file_parser",
            "helper_text": "The processing model with which the document will be processed. Default processing model includes standard document parsing / OCR. Llamaparse will allow for ability to read documents with complex features (e.g., tables, charts, etc.). Llamaparse will be charged at 0.3 cents per page. Textract for most advanced data extraction and will be charged at 1.5 cents per page.",
            "value": "default",
            "type": "enum<string>",
        },
        {
            "field": "max_docs_per_query",
            "helper_text": "Sets the maximum number of chunks to retrieve for each query",
            "value": 10,
            "type": "int32",
        },
        {
            "field": "retrieval_unit",
            "helper_text": "Return the most relevant Chunks (text content) or Documents (will return the document metadata)",
            "value": "chunks",
            "type": "enum<string>",
        },
    ]

    # Common outputs and inputs
    _COMMON_OUTPUTS = [
        {
            "field": "documents",
            "helper_text": "The uploaded file (in the chat interface) is processed into text",
        }
    ]

    # Configuration patterns and their associated inputs/outputs
    _CONFIGS = {}

    # List of parameters that affect configuration
    _PARAMS = []

    def __init__(
        self,
        id: Optional[str] = None,
        node_name: Optional[str] = None,
        execution_mode: Optional[str] = None,
        chunk_overlap: int = 200,
        chunk_size: int = 1000,
        file_parser: str = "default",
        max_docs_per_query: int = 10,
        retrieval_unit: str = "chunks",
        **kwargs
    ):
        # Initialize with params
        params = {}

        super().__init__(
            node_type="chat_file_reader",
            params=params,
            id=id,
            node_name=node_name,
            execution_mode=execution_mode,
        )

        # Set input values
        if file_parser is not None:
            self.inputs["file_parser"] = file_parser
        if max_docs_per_query is not None:
            self.inputs["max_docs_per_query"] = max_docs_per_query
        if retrieval_unit is not None:
            self.inputs["retrieval_unit"] = retrieval_unit
        if chunk_size is not None:
            self.inputs["chunk_size"] = chunk_size
        if chunk_overlap is not None:
            self.inputs["chunk_overlap"] = chunk_overlap

        # Update any additional inputs
        if kwargs:
            self.update_inputs(**kwargs)

    @property
    def documents(self) -> List[str]:
        """
        The uploaded file (in the chat interface) is processed into text


        Raises:
            AttributeError: If this output is not available for the current parameter values
        """
        return self.__getattr__("documents")

    @classmethod
    def from_dict(cls, data: dict) -> "ChatFileReaderNode":
        """Create a node instance from a dictionary."""
        inputs = data.get("inputs", {})
        id = data.get("id", None)
        name = data.get("name", None)
        execution_mode = data.get("execution_mode", None)
        return cls(**inputs, id=id, node_name=name, execution_mode=execution_mode)


@Node.register_node_type("pipeline")
class PipelineNode(Node):
    """
    Pipeline

    ## Inputs
    ### Common Inputs
        pipeline_id: The pipeline_id input
    ### [pipelines._id.<A>]
        [<A>.inputs]: The [<A>.inputs] input

    ## Outputs
    ### [pipelines._id.<A>]
        [<A>.outputs]: The [<A>.outputs] output
    """

    # Common inputs and outputs
    _COMMON_INPUTS = [
        {
            "field": "pipeline_id",
            "helper_text": "The pipeline_id input",
            "value": "",
            "type": "enum<string>",
        }
    ]

    # Common outputs and inputs
    _COMMON_OUTPUTS = []

    # Configuration patterns and their associated inputs/outputs
    _CONFIGS = {
        "[pipelines._id.<A>]": {
            "inputs": [{"field": "[<A>.inputs]", "type": ""}],
            "outputs": [{"field": "[<A>.outputs]", "type": ""}],
        }
    }

    # List of parameters that affect configuration
    _PARAMS = ["pipeline_id"]

    def __init__(
        self,
        id: Optional[str] = None,
        node_name: Optional[str] = None,
        execution_mode: Optional[str] = None,
        pipeline_id: str = "",
        **kwargs
    ):
        # Initialize with params
        params = {}
        params["pipeline_id"] = pipeline_id

        super().__init__(
            node_type="pipeline",
            params=params,
            id=id,
            node_name=node_name,
            execution_mode=execution_mode,
        )

        # Set input values
        if pipeline_id is not None:
            self.inputs["pipeline_id"] = pipeline_id

        # Update any additional inputs
        if kwargs:
            self.update_inputs(**kwargs)

    @classmethod
    def from_dict(cls, data: dict) -> "PipelineNode":
        """Create a node instance from a dictionary."""
        inputs = data.get("inputs", {})
        id = data.get("id", None)
        name = data.get("name", None)
        execution_mode = data.get("execution_mode", None)
        return cls(**inputs, id=id, node_name=name, execution_mode=execution_mode)


@Node.register_node_type("agent")
class AgentNode(Node):
    """
    Agent

    ## Inputs
    ### Common Inputs
        agent_id: The agent_id input
    ### [agents._id.<A>]
        [<A>.inputs]: The [<A>.inputs] input

    ## Outputs
    ### [agents._id.<A>]
        [<A>.outputs]: The [<A>.outputs] output
    """

    # Common inputs and outputs
    _COMMON_INPUTS = [
        {
            "field": "agent_id",
            "helper_text": "The agent_id input",
            "value": "",
            "type": "enum<string>",
        }
    ]

    # Common outputs and inputs
    _COMMON_OUTPUTS = []

    # Configuration patterns and their associated inputs/outputs
    _CONFIGS = {
        "[agents._id.<A>]": {
            "inputs": [{"field": "[<A>.inputs]", "type": ""}],
            "outputs": [{"field": "[<A>.outputs]", "type": ""}],
        }
    }

    # List of parameters that affect configuration
    _PARAMS = ["agent_id"]

    def __init__(
        self,
        id: Optional[str] = None,
        node_name: Optional[str] = None,
        execution_mode: Optional[str] = None,
        agent_id: str = "",
        **kwargs
    ):
        # Initialize with params
        params = {}
        params["agent_id"] = agent_id

        super().__init__(
            node_type="agent",
            params=params,
            id=id,
            node_name=node_name,
            execution_mode=execution_mode,
        )

        # Set input values
        if agent_id is not None:
            self.inputs["agent_id"] = agent_id

        # Update any additional inputs
        if kwargs:
            self.update_inputs(**kwargs)

    @classmethod
    def from_dict(cls, data: dict) -> "AgentNode":
        """Create a node instance from a dictionary."""
        inputs = data.get("inputs", {})
        id = data.get("id", None)
        name = data.get("name", None)
        execution_mode = data.get("execution_mode", None)
        return cls(**inputs, id=id, node_name=name, execution_mode=execution_mode)


@Node.register_node_type("chat_memory")
class ChatMemoryNode(Node):
    """
    Give connected nodes access to conversation history.

    ## Inputs
    ### Common Inputs
        memory_type: The type of memory to use
        memory_window: The number of tokens to store in memory

    ## Outputs
    ### Common Outputs
        memory: The conversation history in the format of the selected type
    """

    # Common inputs and outputs
    _COMMON_INPUTS = [
        {
            "field": "memory_type",
            "helper_text": "The type of memory to use",
            "value": "Token Buffer",
            "type": "string",
        },
        {
            "field": "memory_window",
            "helper_text": "The number of tokens to store in memory",
            "value": 2048,
            "type": "int32",
        },
    ]

    # Common outputs and inputs
    _COMMON_OUTPUTS = [
        {
            "field": "memory",
            "helper_text": "The conversation history in the format of the selected type",
        }
    ]

    # Configuration patterns and their associated inputs/outputs
    _CONFIGS = {
        "Vector Database": {
            "inputs": [
                {"field": "memory_window", "type": "int32", "value": 20},
                {
                    "field": "memory_type",
                    "type": "string",
                    "value": "Vector Database",
                    "helper_text": "Stores all previous messages in a Vector Database. Will return most similar messages based on the user message",
                },
            ],
            "outputs": [],
        },
        "Message Buffer": {
            "inputs": [
                {
                    "field": "memory_type",
                    "type": "string",
                    "value": "Message Buffer",
                    "helper_text": "Returns a set number of previous consecutive messages",
                }
            ],
            "outputs": [],
        },
        "Token Buffer": {
            "inputs": [
                {
                    "field": "memory_type",
                    "type": "string",
                    "value": "Token Buffer",
                    "helper_text": "Returns a set number of previous consecutive messages until adding an additional message would cause the total history size to be larger than the Max Tokens",
                }
            ],
            "outputs": [],
        },
        "Full - Formatted": {
            "inputs": [
                {
                    "field": "memory_type",
                    "type": "string",
                    "value": "Full - Formatted",
                    "helper_text": "Returns all previous chat history",
                }
            ],
            "outputs": [],
        },
        "Full - Raw": {
            "inputs": [
                {
                    "field": "memory_type",
                    "type": "string",
                    "value": "Full - Raw",
                    "helper_text": 'Returns a Python list with elements in the following format: {"type": type, "message": message}',
                }
            ],
            "outputs": [],
        },
    }

    # List of parameters that affect configuration
    _PARAMS = []

    def __init__(
        self,
        id: Optional[str] = None,
        node_name: Optional[str] = None,
        execution_mode: Optional[str] = None,
        memory_type: str = "Token Buffer",
        memory_window: int = 2048,
        **kwargs
    ):
        # Initialize with params
        params = {}

        super().__init__(
            node_type="chat_memory",
            params=params,
            id=id,
            node_name=node_name,
            execution_mode=execution_mode,
        )

        # Set input values
        if memory_type is not None:
            self.inputs["memory_type"] = memory_type
        if memory_window is not None:
            self.inputs["memory_window"] = memory_window

        # Update any additional inputs
        if kwargs:
            self.update_inputs(**kwargs)

    @property
    def memory(self) -> str:
        """
        The conversation history in the format of the selected type


        Raises:
            AttributeError: If this output is not available for the current parameter values
        """
        return self.__getattr__("memory")

    @classmethod
    def from_dict(cls, data: dict) -> "ChatMemoryNode":
        """Create a node instance from a dictionary."""
        inputs = data.get("inputs", {})
        id = data.get("id", None)
        name = data.get("name", None)
        execution_mode = data.get("execution_mode", None)
        return cls(**inputs, id=id, node_name=name, execution_mode=execution_mode)


@Node.register_node_type("llm")
class LlmNode(Node):
    """
    LLM

    ## Inputs
    ### Common Inputs
        enable_moderation: Whether to enable moderation
        enable_pii_address: Whether to enable PII address
        enable_pii_cc: Whether to enable PII cc
        enable_pii_email: Whether to enable PII email
        enable_pii_name: Whether to enable PII name
        enable_pii_phone: Whether to enable PII phone
        enable_pii_ssn: Whether to enable PII ssn
        max_tokens: The maximum amount of input + output tokens the model will take in and generate per run (1 token = 4 characters). Note: different models have different token limits and the workflow will error if the max token is reached.
        model: Select the LLM model to be used
        prompt: The data that is sent to the LLM. Add data from other nodes with double curly braces e.g., {{input_0.text}}
        provider: Select the LLM provider to be used
        show_confidence: Whether to show the confidence score of the response
        show_sources: Whether to show the sources used to generate the response
        stream: Whether to stream the response
        system: The system prompt to be used
        temperature: The “creativity” of the response - increase the temperature for more creative responses.
        top_p: The “randomness” of the output - higher Top P values increase the randomness
    ### When use_personal_api_key = True
        api_key: Your personal API key
    ### When provider = 'custom'
        api_key: Your personal API key
        base_url: The base URL of the custom LLM provider
        finetuned_model: Use your finetuned model for response generation. Make sure to select the matching base model from the dropdown.
        use_personal_api_key: Whether to use a personal API key
    ### When show_sources = True
        citation_metadata: The metadata of the sources used to generate the response
        json_response: Whether to return the response as a JSON object
        use_personal_api_key: Whether to use a personal API key
    ### When provider = 'azure' and use_personal_api_key = True
        deployment_id: The deployment ID for the Azure OpenAI model. This is required when using Azure OpenAI services.
        endpoint: The Azure OpenAI endpoint URL (e.g., https://your-resource-name.openai.azure.com)
    ### When provider = 'openai' and use_personal_api_key = True
        finetuned_model: Use your finetuned model for response generation. Make sure to select the matching base model from the dropdown.
    ### When provider = 'openai'
        json_response: Whether to return the response as a JSON object
        use_personal_api_key: Whether to use a personal API key
    ### When provider = 'anthropic'
        json_response: Whether to return the response as a JSON object
        use_personal_api_key: Whether to use a personal API key
    ### When provider = 'google'
        json_response: Whether to return the response as a JSON object
        use_personal_api_key: Whether to use a personal API key
    ### When provider = 'cohere'
        json_response: Whether to return the response as a JSON object
        use_personal_api_key: Whether to use a personal API key
    ### When provider = 'together'
        json_response: Whether to return the response as a JSON object
        use_personal_api_key: Whether to use a personal API key
    ### When provider = 'bedrock'
        json_response: Whether to return the response as a JSON object
    ### When provider = 'azure'
        json_response: Whether to return the response as a JSON object
        use_personal_api_key: Whether to use a personal API key
    ### When json_response = True
        json_schema: The schema of the JSON response
    ### When provider = 'perplexity'
        use_personal_api_key: Whether to use a personal API key

    ## Outputs
    ### Common Outputs
        credits_used: The number of credits used
        input_tokens: The number of input tokens
        output_tokens: The number of output tokens
        tokens_used: The number of tokens used
    ### When stream = True
        response: The response as a stream of text
    ### When stream = False
        response: The response as a single string
    """

    # Common inputs and outputs
    _COMMON_INPUTS = [
        {
            "field": "enable_moderation",
            "helper_text": "Whether to enable moderation",
            "value": False,
            "type": "bool",
        },
        {
            "field": "enable_pii_address",
            "helper_text": "Whether to enable PII address",
            "value": False,
            "type": "bool",
        },
        {
            "field": "enable_pii_cc",
            "helper_text": "Whether to enable PII cc",
            "value": False,
            "type": "bool",
        },
        {
            "field": "enable_pii_email",
            "helper_text": "Whether to enable PII email",
            "value": False,
            "type": "bool",
        },
        {
            "field": "enable_pii_name",
            "helper_text": "Whether to enable PII name",
            "value": False,
            "type": "bool",
        },
        {
            "field": "enable_pii_phone",
            "helper_text": "Whether to enable PII phone",
            "value": False,
            "type": "bool",
        },
        {
            "field": "enable_pii_ssn",
            "helper_text": "Whether to enable PII ssn",
            "value": False,
            "type": "bool",
        },
        {
            "field": "max_tokens",
            "helper_text": "The maximum amount of input + output tokens the model will take in and generate per run (1 token = 4 characters). Note: different models have different token limits and the workflow will error if the max token is reached.",
            "value": 128000,
            "type": "int32",
        },
        {
            "field": "model",
            "helper_text": "Select the LLM model to be used",
            "value": "gpt-4o",
            "type": "enum<string>",
        },
        {
            "field": "prompt",
            "helper_text": "The data that is sent to the LLM. Add data from other nodes with double curly braces e.g., {{input_0.text}}",
            "value": "",
            "type": "string",
        },
        {
            "field": "provider",
            "helper_text": "Select the LLM provider to be used",
            "value": "openai",
            "type": "enum<string>",
        },
        {
            "field": "show_confidence",
            "helper_text": "Whether to show the confidence score of the response",
            "value": False,
            "type": "bool",
        },
        {
            "field": "show_sources",
            "helper_text": "Whether to show the sources used to generate the response",
            "value": False,
            "type": "bool",
        },
        {
            "field": "stream",
            "helper_text": "Whether to stream the response",
            "value": False,
            "type": "bool",
        },
        {
            "field": "system",
            "helper_text": "The system prompt to be used",
            "value": "",
            "type": "string",
        },
        {
            "field": "temperature",
            "helper_text": "The “creativity” of the response - increase the temperature for more creative responses.",
            "value": 0.5,
            "type": "float",
        },
        {
            "field": "top_p",
            "helper_text": "The “randomness” of the output - higher Top P values increase the randomness",
            "value": 0.5,
            "type": "float",
        },
    ]

    # Common outputs and inputs
    _COMMON_OUTPUTS = [
        {"field": "credits_used", "helper_text": "The number of credits used"},
        {"field": "input_tokens", "helper_text": "The number of input tokens"},
        {"field": "output_tokens", "helper_text": "The number of output tokens"},
        {"field": "tokens_used", "helper_text": "The number of tokens used"},
    ]

    # Configuration patterns and their associated inputs/outputs
    _CONFIGS = {
        "(*)**true**(*)**(*)**(*)": {
            "inputs": [],
            "outputs": [
                {
                    "field": "response",
                    "type": "stream<string>",
                    "helper_text": "The response as a stream of text",
                }
            ],
        },
        "(*)**false**(*)**(*)**(*)": {
            "inputs": [],
            "outputs": [
                {
                    "field": "response",
                    "type": "string",
                    "helper_text": "The response as a single string",
                }
            ],
        },
        "(*)**(*)**true**(*)**(*)": {
            "inputs": [
                {
                    "field": "api_key",
                    "type": "string",
                    "value": "",
                    "helper_text": "Your personal API key",
                }
            ],
            "outputs": [],
        },
        "(*)**(*)**(*)**true**(*)": {
            "inputs": [
                {
                    "field": "json_schema",
                    "type": "string",
                    "value": "",
                    "helper_text": "The schema of the JSON response",
                }
            ],
            "outputs": [],
        },
        "(*)**(*)**(*)**(*)**true": {
            "inputs": [
                {
                    "field": "citation_metadata",
                    "type": "vec<string>",
                    "value": [""],
                    "helper_text": "The metadata of the sources used to generate the response",
                },
                {
                    "field": "json_response",
                    "type": "bool",
                    "value": False,
                    "helper_text": "Whether to return the response as a JSON object",
                },
                {
                    "field": "use_personal_api_key",
                    "type": "bool",
                    "value": False,
                    "helper_text": "Whether to use a personal API key",
                },
            ],
            "outputs": [],
        },
        "custom**(*)**(*)**(*)**(*)": {
            "inputs": [
                {
                    "field": "base_url",
                    "type": "string",
                    "value": "",
                    "helper_text": "The base URL of the custom LLM provider",
                },
                {
                    "field": "model",
                    "type": "string",
                    "value": "",
                    "helper_text": "The model to be used",
                },
                {
                    "field": "api_key",
                    "type": "string",
                    "value": "",
                    "helper_text": "Your API key",
                },
                {
                    "field": "use_personal_api_key",
                    "type": "bool",
                    "value": True,
                    "helper_text": "Whether to use a personal API key",
                },
                {
                    "field": "finetuned_model",
                    "type": "string",
                    "value": "",
                    "helper_text": "Use your finetuned model for response generation. Make sure to select the matching base model from the dropdown.",
                },
            ],
            "outputs": [],
            "title": "Custom",
        },
        "openai**(*)**(*)**(*)**(*)": {
            "inputs": [
                {
                    "field": "json_response",
                    "type": "bool",
                    "value": False,
                    "helper_text": "Whether to return the response as a JSON object",
                },
                {
                    "field": "use_personal_api_key",
                    "type": "bool",
                    "value": False,
                    "helper_text": "Whether to use a personal API key",
                },
            ],
            "outputs": [],
            "title": "OpenAI",
        },
        "openai**(*)**true**(*)**(*)": {
            "inputs": [
                {
                    "field": "finetuned_model",
                    "type": "string",
                    "value": "",
                    "helper_text": "Use your finetuned model for response generation. Make sure to select the matching base model from the dropdown.",
                }
            ],
            "outputs": [],
        },
        "anthropic**(*)**(*)**(*)**(*)": {
            "inputs": [
                {
                    "field": "use_personal_api_key",
                    "type": "bool",
                    "value": False,
                    "helper_text": "Whether to use a personal API key",
                },
                {
                    "field": "json_response",
                    "type": "bool",
                    "value": False,
                    "helper_text": "Whether to return the response as a JSON object",
                },
            ],
            "outputs": [],
            "title": "Anthropic",
        },
        "perplexity**(*)**(*)**(*)**(*)": {
            "inputs": [
                {
                    "field": "use_personal_api_key",
                    "type": "bool",
                    "value": False,
                    "helper_text": "Whether to use a personal API key",
                }
            ],
            "outputs": [],
            "title": "Perplexity",
        },
        "google**(*)**(*)**(*)**(*)": {
            "inputs": [
                {
                    "field": "use_personal_api_key",
                    "type": "bool",
                    "value": False,
                    "helper_text": "Whether to use a personal API key",
                },
                {
                    "field": "json_response",
                    "type": "bool",
                    "value": False,
                    "helper_text": "Whether to return the response as a JSON object",
                },
            ],
            "outputs": [],
            "title": "Google",
        },
        "cohere**(*)**(*)**(*)**(*)": {
            "inputs": [
                {
                    "field": "json_response",
                    "type": "bool",
                    "value": False,
                    "helper_text": "Whether to return the response as a JSON object",
                },
                {
                    "field": "use_personal_api_key",
                    "type": "bool",
                    "value": False,
                    "helper_text": "Whether to use a personal API key",
                },
            ],
            "outputs": [],
            "title": "Cohere",
        },
        "together**(*)**(*)**(*)**(*)": {
            "inputs": [
                {
                    "field": "json_response",
                    "type": "bool",
                    "value": False,
                    "helper_text": "Whether to return the response as a JSON object",
                },
                {
                    "field": "use_personal_api_key",
                    "type": "bool",
                    "value": False,
                    "helper_text": "Whether to use a personal API key",
                },
            ],
            "outputs": [],
            "title": "Open Source",
        },
        "bedrock**(*)**(*)**(*)**(*)": {
            "inputs": [
                {
                    "field": "json_response",
                    "type": "bool",
                    "value": False,
                    "helper_text": "Whether to return the response as a JSON object",
                }
            ],
            "outputs": [],
            "title": "Bedrock",
        },
        "azure**(*)**(*)**(*)**(*)": {
            "inputs": [
                {
                    "field": "json_response",
                    "type": "bool",
                    "value": False,
                    "helper_text": "Whether to return the response as a JSON object",
                },
                {
                    "field": "use_personal_api_key",
                    "type": "bool",
                    "value": False,
                    "helper_text": "Whether to use a personal API key",
                },
            ],
            "outputs": [],
            "title": "Azure",
        },
        "azure**(*)**true**(*)**(*)": {
            "inputs": [
                {
                    "field": "endpoint",
                    "type": "string",
                    "value": "",
                    "helper_text": "The Azure OpenAI endpoint URL (e.g., https://your-resource-name.openai.azure.com)",
                },
                {
                    "field": "deployment_id",
                    "type": "string",
                    "value": "",
                    "helper_text": "The deployment ID for the Azure OpenAI model. This is required when using Azure OpenAI services.",
                },
            ],
            "outputs": [],
        },
    }

    # List of parameters that affect configuration
    _PARAMS = [
        "provider",
        "stream",
        "use_personal_api_key",
        "json_response",
        "show_sources",
    ]

    def __init__(
        self,
        id: Optional[str] = None,
        node_name: Optional[str] = None,
        execution_mode: Optional[str] = None,
        provider: str = "openai",
        stream: bool = False,
        use_personal_api_key: bool = False,
        json_response: bool = False,
        show_sources: bool = False,
        api_key: str = "",
        base_url: str = "",
        citation_metadata: List[str] = [""],
        deployment_id: str = "",
        enable_moderation: bool = False,
        enable_pii_address: bool = False,
        enable_pii_cc: bool = False,
        enable_pii_email: bool = False,
        enable_pii_name: bool = False,
        enable_pii_phone: bool = False,
        enable_pii_ssn: bool = False,
        endpoint: str = "",
        finetuned_model: str = "",
        json_schema: str = "",
        max_tokens: int = 128000,
        model: str = "gpt-4o",
        prompt: str = "",
        show_confidence: bool = False,
        system: str = "",
        temperature: Any = 0.5,
        top_p: Any = 0.5,
        **kwargs
    ):
        # Initialize with params
        params = {}
        params["provider"] = provider
        params["stream"] = stream
        params["use_personal_api_key"] = use_personal_api_key
        params["json_response"] = json_response
        params["show_sources"] = show_sources

        super().__init__(
            node_type="llm",
            params=params,
            id=id,
            node_name=node_name,
            execution_mode=execution_mode,
        )

        # Set input values
        if provider is not None:
            self.inputs["provider"] = provider
        if model is not None:
            self.inputs["model"] = model
        if system is not None:
            self.inputs["system"] = system
        if prompt is not None:
            self.inputs["prompt"] = prompt
        if temperature is not None:
            self.inputs["temperature"] = temperature
        if max_tokens is not None:
            self.inputs["max_tokens"] = max_tokens
        if top_p is not None:
            self.inputs["top_p"] = top_p
        if stream is not None:
            self.inputs["stream"] = stream
        if show_sources is not None:
            self.inputs["show_sources"] = show_sources
        if show_confidence is not None:
            self.inputs["show_confidence"] = show_confidence
        if enable_moderation is not None:
            self.inputs["enable_moderation"] = enable_moderation
        if enable_pii_name is not None:
            self.inputs["enable_pii_name"] = enable_pii_name
        if enable_pii_email is not None:
            self.inputs["enable_pii_email"] = enable_pii_email
        if enable_pii_phone is not None:
            self.inputs["enable_pii_phone"] = enable_pii_phone
        if enable_pii_ssn is not None:
            self.inputs["enable_pii_ssn"] = enable_pii_ssn
        if enable_pii_address is not None:
            self.inputs["enable_pii_address"] = enable_pii_address
        if enable_pii_cc is not None:
            self.inputs["enable_pii_cc"] = enable_pii_cc
        if api_key is not None:
            self.inputs["api_key"] = api_key
        if json_schema is not None:
            self.inputs["json_schema"] = json_schema
        if citation_metadata is not None:
            self.inputs["citation_metadata"] = citation_metadata
        if json_response is not None:
            self.inputs["json_response"] = json_response
        if use_personal_api_key is not None:
            self.inputs["use_personal_api_key"] = use_personal_api_key
        if base_url is not None:
            self.inputs["base_url"] = base_url
        if finetuned_model is not None:
            self.inputs["finetuned_model"] = finetuned_model
        if endpoint is not None:
            self.inputs["endpoint"] = endpoint
        if deployment_id is not None:
            self.inputs["deployment_id"] = deployment_id

        # Update any additional inputs
        if kwargs:
            self.update_inputs(**kwargs)

    @property
    def credits_used(self) -> Any:
        """
        The number of credits used


        Raises:
            AttributeError: If this output is not available for the current parameter values
        """
        return self.__getattr__("credits_used")

    @property
    def input_tokens(self) -> int:
        """
        The number of input tokens


        Raises:
            AttributeError: If this output is not available for the current parameter values
        """
        return self.__getattr__("input_tokens")

    @property
    def output_tokens(self) -> int:
        """
        The number of output tokens


        Raises:
            AttributeError: If this output is not available for the current parameter values
        """
        return self.__getattr__("output_tokens")

    @property
    def response(self) -> Any:
        """
        The response as a stream of text

        Different behavior based on configuration:
          - The response as a stream of text (When stream = True)
          - The response as a single string (When stream = False)


        Raises:
            AttributeError: If this output is not available for the current parameter values
        """
        return self.__getattr__("response")

    @property
    def tokens_used(self) -> int:
        """
        The number of tokens used


        Raises:
            AttributeError: If this output is not available for the current parameter values
        """
        return self.__getattr__("tokens_used")

    @classmethod
    def from_dict(cls, data: dict) -> "LlmNode":
        """Create a node instance from a dictionary."""
        inputs = data.get("inputs", {})
        id = data.get("id", None)
        name = data.get("name", None)
        execution_mode = data.get("execution_mode", None)
        return cls(**inputs, id=id, node_name=name, execution_mode=execution_mode)


@Node.register_node_type("input")
class InputNode(Node):
    """
    Pass data of different types into your workflow.

    ## Inputs
    ### Common Inputs
        input_type: Raw Text
    ### file
        file_parser: The processing model with which the document will be processed. Default processing model includes standard document parsing / OCR. Llamaparse will allow for ability to read documents with complex features (e.g., tables, charts, etc.). Llamaparse will be charged at 0.3 cents per page. Textract for most advanced data extraction and will be charged at 1.5 cents per page.
    ### vec<file>
        file_parser: The processing model with which the document will be processed. Default processing model includes standard document parsing / OCR. Llamaparse will allow for ability to read documents with complex features (e.g., tables, charts, etc.). Llamaparse will be charged at 0.3 cents per page. Textract for most advanced data extraction and will be charged at 1.5 cents per page.

    ## Outputs
    ### audio
        audio: The audio that was passed in
    ### file
        file: The file that was passed in
        processed_text: The processed text of the file.
    ### vec<file>
        files: The files that were passed in
        processed_texts: The processed text of the files
    ### image
        image: The image that was passed in
    ### knowledge_base
        knowledge_base: The Knowledge Base that was passed in
    ### pipeline
        pipeline: The pipeline output
    ### string
        text: The text that was passed in
    """

    # Common inputs and outputs
    _COMMON_INPUTS = [
        {
            "field": "input_type",
            "helper_text": "Raw Text",
            "value": "string",
            "type": "enum<string>",
        }
    ]

    # Common outputs and inputs
    _COMMON_OUTPUTS = []

    # Configuration patterns and their associated inputs/outputs
    _CONFIGS = {
        "string": {
            "inputs": [
                {
                    "field": "input_type",
                    "type": "enum<string>",
                    "value": "string",
                    "helper_text": "Raw Text",
                }
            ],
            "outputs": [
                {
                    "field": "text",
                    "type": "string",
                    "helper_text": "The text that was passed in",
                }
            ],
        },
        "file": {
            "inputs": [
                {
                    "field": "file_parser",
                    "type": "enum<string>",
                    "value": "default",
                    "helper_text": "The processing model with which the document will be processed. Default processing model includes standard document parsing / OCR. Llamaparse will allow for ability to read documents with complex features (e.g., tables, charts, etc.). Llamaparse will be charged at 0.3 cents per page. Textract for most advanced data extraction and will be charged at 1.5 cents per page.",
                },
                {
                    "field": "input_type",
                    "type": "enum<string>",
                    "value": "file",
                    "helper_text": "File of any type: PDF, Word, MP3, JPEG, etc.",
                },
            ],
            "outputs": [
                {
                    "field": "processed_text",
                    "type": "string",
                    "helper_text": "The processed text of the file.",
                },
                {
                    "field": "file",
                    "type": "file",
                    "helper_text": "The file that was passed in",
                },
            ],
        },
        "audio": {
            "inputs": [
                {
                    "field": "input_type",
                    "type": "enum<string>",
                    "value": "audio",
                    "helper_text": "Allows you to record audio through the VectorShift platform. To convert the audio to text, connect the input node to a Speech to Text node",
                }
            ],
            "outputs": [
                {
                    "field": "audio",
                    "type": "audio",
                    "helper_text": "The audio that was passed in",
                }
            ],
        },
        "image": {
            "inputs": [
                {
                    "field": "input_type",
                    "type": "enum<string>",
                    "value": "image",
                    "helper_text": "Image of any type: JPEG, PNG, etc.",
                }
            ],
            "outputs": [
                {
                    "field": "image",
                    "type": "image",
                    "helper_text": "The image that was passed in",
                }
            ],
        },
        "knowledge_base": {
            "inputs": [
                {
                    "field": "input_type",
                    "type": "enum<string>",
                    "value": "knowledge_base",
                    "helper_text": "Allows you to pass a Knowledge Base as an input",
                }
            ],
            "outputs": [
                {
                    "field": "knowledge_base",
                    "type": "knowledge_base",
                    "helper_text": "The Knowledge Base that was passed in",
                }
            ],
        },
        "pipeline": {
            "inputs": [
                {
                    "field": "input_type",
                    "type": "enum<string>",
                    "value": "pipeline",
                    "helper_text": "Allows you to pass a Pipeline as an input",
                }
            ],
            "outputs": [{"field": "pipeline", "type": "pipeline"}],
        },
        "vec<file>": {
            "inputs": [
                {
                    "field": "file_parser",
                    "type": "enum<string>",
                    "value": "default",
                    "helper_text": "The processing model with which the document will be processed. Default processing model includes standard document parsing / OCR. Llamaparse will allow for ability to read documents with complex features (e.g., tables, charts, etc.). Llamaparse will be charged at 0.3 cents per page. Textract for most advanced data extraction and will be charged at 1.5 cents per page.",
                },
                {
                    "field": "input_type",
                    "type": "enum<string>",
                    "value": "vec<file>",
                    "helper_text": "Allows you to pass a list of files as an input",
                },
            ],
            "outputs": [
                {
                    "field": "processed_texts",
                    "type": "vec<string>",
                    "helper_text": "The processed text of the files",
                },
                {
                    "field": "files",
                    "type": "vec<file>",
                    "helper_text": "The files that were passed in",
                },
            ],
        },
    }

    # List of parameters that affect configuration
    _PARAMS = ["input_type"]

    def __init__(
        self,
        id: Optional[str] = None,
        node_name: Optional[str] = None,
        execution_mode: Optional[str] = None,
        input_type: str = "string",
        file_parser: str = "default",
        **kwargs
    ):
        # Initialize with params
        params = {}
        params["input_type"] = input_type

        super().__init__(
            node_type="input",
            params=params,
            id=id,
            node_name=node_name,
            execution_mode=execution_mode,
        )

        # Set input values
        if input_type is not None:
            self.inputs["input_type"] = input_type
        if file_parser is not None:
            self.inputs["file_parser"] = file_parser

        # Update any additional inputs
        if kwargs:
            self.update_inputs(**kwargs)

    @property
    def audio(self) -> Any:
        """
        The audio that was passed in

        Available: audio


        Raises:
            AttributeError: If this output is not available for the current parameter values
        """
        return self.__getattr__("audio")

    @property
    def file(self) -> str:
        """
        The file that was passed in

        Available: file


        Raises:
            AttributeError: If this output is not available for the current parameter values
        """
        return self.__getattr__("file")

    @property
    def files(self) -> List[str]:
        """
        The files that were passed in

        Available: vec<file>


        Raises:
            AttributeError: If this output is not available for the current parameter values
        """
        return self.__getattr__("files")

    @property
    def image(self) -> Any:
        """
        The image that was passed in

        Available: image


        Raises:
            AttributeError: If this output is not available for the current parameter values
        """
        return self.__getattr__("image")

    @property
    def knowledge_base(self) -> Any:
        """
        The Knowledge Base that was passed in

        Available: knowledge_base


        Raises:
            AttributeError: If this output is not available for the current parameter values
        """
        return self.__getattr__("knowledge_base")

    @property
    def pipeline(self) -> Any:
        """
        The pipeline output

        Available: pipeline


        Raises:
            AttributeError: If this output is not available for the current parameter values
        """
        return self.__getattr__("pipeline")

    @property
    def processed_text(self) -> str:
        """
        The processed text of the file.

        Available: file


        Raises:
            AttributeError: If this output is not available for the current parameter values
        """
        return self.__getattr__("processed_text")

    @property
    def processed_texts(self) -> List[str]:
        """
        The processed text of the files

        Available: vec<file>


        Raises:
            AttributeError: If this output is not available for the current parameter values
        """
        return self.__getattr__("processed_texts")

    @property
    def text(self) -> str:
        """
        The text that was passed in

        Available: string


        Raises:
            AttributeError: If this output is not available for the current parameter values
        """
        return self.__getattr__("text")

    @classmethod
    def from_dict(cls, data: dict) -> "InputNode":
        """Create a node instance from a dictionary."""
        inputs = data.get("inputs", {})
        id = data.get("id", None)
        name = data.get("name", None)
        execution_mode = data.get("execution_mode", None)
        return cls(**inputs, id=id, node_name=name, execution_mode=execution_mode)


@Node.register_node_type("output")
class OutputNode(Node):
    """
    Output data of different types from your workflow.

    ## Inputs
    ### Common Inputs
        output_type: The output_type input
    ### string
        value: The value input
    ### file
        value: The value input
    ### audio
        value: The value input
    ### json
        value: The value input
    ### image
        value: The value input
    ### stream<string>
        value: The value input
    ### vec<file>
        value: The value input

    ## Outputs
        None
    """

    # Common inputs and outputs
    _COMMON_INPUTS = [
        {
            "field": "output_type",
            "helper_text": "The output_type input",
            "value": "string",
            "type": "enum<string>",
        }
    ]

    # Common outputs and inputs
    _COMMON_OUTPUTS = []

    # Configuration patterns and their associated inputs/outputs
    _CONFIGS = {
        "string": {
            "inputs": [
                {"field": "value", "type": "string", "value": ""},
                {
                    "field": "output_type",
                    "type": "enum<string>",
                    "value": "string",
                    "helper_text": "Output raw text",
                },
            ],
            "outputs": [],
        },
        "file": {
            "inputs": [
                {"field": "value", "type": "file", "value": ""},
                {
                    "field": "output_type",
                    "type": "enum<string>",
                    "value": "file",
                    "helper_text": "Output file of any type: PDF, Word, Excel, CSV, MP3, JPEG, etc.",
                },
            ],
            "outputs": [],
        },
        "audio": {
            "inputs": [
                {"field": "value", "type": "audio", "value": ""},
                {
                    "field": "output_type",
                    "type": "enum<string>",
                    "value": "audio",
                    "helper_text": "Output raw audio. Output can be generated with the text to speech node",
                },
            ],
            "outputs": [],
        },
        "json": {
            "inputs": [
                {"field": "value", "type": "string", "value": ""},
                {
                    "field": "output_type",
                    "type": "enum<string>",
                    "value": "json",
                    "helper_text": "Output JSON (e.g., LLMs can output JSON - input the schema by selecting “JSON Output” in the gear of the LLM)",
                },
            ],
            "outputs": [],
        },
        "image": {
            "inputs": [
                {"field": "value", "type": "image", "value": ""},
                {
                    "field": "output_type",
                    "type": "enum<string>",
                    "value": "image",
                    "helper_text": "Output Image(s) (images are of file type PNG)",
                },
            ],
            "outputs": [],
        },
        "stream<string>": {
            "inputs": [
                {"field": "value", "type": "stream<string>", "value": ""},
                {
                    "field": "output_type",
                    "type": "enum<string>",
                    "value": "stream<string>",
                    "helper_text": "Output as a stream of raw text",
                },
            ],
            "outputs": [],
            "banner_text": 'Ensure to check "Stream Response" in gear of the LLM',
        },
        "vec<file>": {
            "inputs": [
                {"field": "value", "type": "vec<file>", "value": []},
                {
                    "field": "output_type",
                    "type": "enum<string>",
                    "value": "vec<file>",
                    "helper_text": "Output a list of files",
                },
            ],
            "outputs": [],
        },
    }

    # List of parameters that affect configuration
    _PARAMS = ["output_type"]

    def __init__(
        self,
        id: Optional[str] = None,
        node_name: Optional[str] = None,
        execution_mode: Optional[str] = None,
        output_type: str = "string",
        value: str = "",
        **kwargs
    ):
        # Initialize with params
        params = {}
        params["output_type"] = output_type

        super().__init__(
            node_type="output",
            params=params,
            id=id,
            node_name=node_name,
            execution_mode=execution_mode,
        )

        # Set input values
        if output_type is not None:
            self.inputs["output_type"] = output_type
        if value is not None:
            self.inputs["value"] = value

        # Update any additional inputs
        if kwargs:
            self.update_inputs(**kwargs)

    @classmethod
    def from_dict(cls, data: dict) -> "OutputNode":
        """Create a node instance from a dictionary."""
        inputs = data.get("inputs", {})
        id = data.get("id", None)
        name = data.get("name", None)
        execution_mode = data.get("execution_mode", None)
        return cls(**inputs, id=id, node_name=name, execution_mode=execution_mode)


@Node.register_node_type("categorizer")
class CategorizerNode(Node):
    """
    Categorize text using AI into custom-defined buckets

    ## Inputs
    ### Common Inputs
        additional_context: Provide any additional context or instructions
        fields: The fields to be categorized
        justification: Include the AI’s justification for its score
        max_tokens: The maximum number of tokens to generate
        model: The specific model for categorization
        provider: The model provider
        temperature: The temperature of the model
        text: The text that will be categorized
        top_p: The top-p value

    ## Outputs
    ### Common Outputs
        category: The category of the input text
        credits_used: The number of credits used
        input_tokens: The number of input tokens
        output_tokens: The number of output tokens
        tokens_used: The number of tokens used
    ### When justification = True
        justification: The AI justification
    """

    # Common inputs and outputs
    _COMMON_INPUTS = [
        {
            "field": "additional_context",
            "helper_text": "Provide any additional context or instructions",
            "value": "",
            "type": "string",
        },
        {
            "field": "fields",
            "helper_text": "The fields to be categorized",
            "value": [],
            "type": "vec<Dict[str, Any]>",
        },
        {
            "field": "justification",
            "helper_text": "Include the AI’s justification for its score",
            "value": False,
            "type": "bool",
        },
        {
            "field": "max_tokens",
            "helper_text": "The maximum number of tokens to generate",
            "value": 2048,
            "type": "int32",
        },
        {
            "field": "model",
            "helper_text": "The specific model for categorization",
            "value": "gpt-4o",
            "type": "enum<string>",
        },
        {
            "field": "provider",
            "helper_text": "The model provider",
            "value": "openai",
            "type": "enum<string>",
        },
        {
            "field": "temperature",
            "helper_text": "The temperature of the model",
            "value": 0.7,
            "type": "float",
        },
        {
            "field": "text",
            "helper_text": "The text that will be categorized",
            "value": "",
            "type": "string",
        },
        {
            "field": "top_p",
            "helper_text": "The top-p value",
            "value": 1.0,
            "type": "float",
        },
    ]

    # Common outputs and inputs
    _COMMON_OUTPUTS = [
        {"field": "category", "helper_text": "The category of the input text"},
        {"field": "credits_used", "helper_text": "The number of credits used"},
        {"field": "input_tokens", "helper_text": "The number of input tokens"},
        {"field": "output_tokens", "helper_text": "The number of output tokens"},
        {"field": "tokens_used", "helper_text": "The number of tokens used"},
    ]

    # Configuration patterns and their associated inputs/outputs
    _CONFIGS = {
        "true": {
            "inputs": [],
            "outputs": [
                {
                    "field": "justification",
                    "type": "string",
                    "helper_text": "The AI justification",
                }
            ],
        },
        "false": {"inputs": [], "outputs": []},
    }

    # List of parameters that affect configuration
    _PARAMS = ["justification"]

    def __init__(
        self,
        id: Optional[str] = None,
        node_name: Optional[str] = None,
        execution_mode: Optional[str] = None,
        justification: bool = False,
        additional_context: str = "",
        fields: List[Any] = [],
        max_tokens: int = 2048,
        model: str = "gpt-4o",
        provider: str = "openai",
        temperature: Any = 0.7,
        text: str = "",
        top_p: Any = 1.0,
        **kwargs
    ):
        # Initialize with params
        params = {}
        params["justification"] = justification

        super().__init__(
            node_type="categorizer",
            params=params,
            id=id,
            node_name=node_name,
            execution_mode=execution_mode,
        )

        # Set input values
        if justification is not None:
            self.inputs["justification"] = justification
        if fields is not None:
            self.inputs["fields"] = fields
        if provider is not None:
            self.inputs["provider"] = provider
        if model is not None:
            self.inputs["model"] = model
        if additional_context is not None:
            self.inputs["additional_context"] = additional_context
        if text is not None:
            self.inputs["text"] = text
        if temperature is not None:
            self.inputs["temperature"] = temperature
        if max_tokens is not None:
            self.inputs["max_tokens"] = max_tokens
        if top_p is not None:
            self.inputs["top_p"] = top_p

        # Update any additional inputs
        if kwargs:
            self.update_inputs(**kwargs)

    @property
    def category(self) -> str:
        """
        The category of the input text


        Raises:
            AttributeError: If this output is not available for the current parameter values
        """
        return self.__getattr__("category")

    @property
    def credits_used(self) -> Any:
        """
        The number of credits used


        Raises:
            AttributeError: If this output is not available for the current parameter values
        """
        return self.__getattr__("credits_used")

    @property
    def input_tokens(self) -> int:
        """
        The number of input tokens


        Raises:
            AttributeError: If this output is not available for the current parameter values
        """
        return self.__getattr__("input_tokens")

    @property
    def justification(self) -> str:
        """
        The AI justification

        Available: When justification = True


        Raises:
            AttributeError: If this output is not available for the current parameter values
        """
        return self.__getattr__("justification")

    @property
    def output_tokens(self) -> int:
        """
        The number of output tokens


        Raises:
            AttributeError: If this output is not available for the current parameter values
        """
        return self.__getattr__("output_tokens")

    @property
    def tokens_used(self) -> int:
        """
        The number of tokens used


        Raises:
            AttributeError: If this output is not available for the current parameter values
        """
        return self.__getattr__("tokens_used")

    @classmethod
    def from_dict(cls, data: dict) -> "CategorizerNode":
        """Create a node instance from a dictionary."""
        inputs = data.get("inputs", {})
        id = data.get("id", None)
        name = data.get("name", None)
        execution_mode = data.get("execution_mode", None)
        return cls(**inputs, id=id, node_name=name, execution_mode=execution_mode)


@Node.register_node_type("extract_data")
class ExtractDataNode(Node):
    """
    Extract key pieces of information or a list of information from a input text.

    ## Inputs
    ### Common Inputs
        additional_context: Provide any additional context or instructions
        fields: The fields input
        model: The specific model for data extraction
        processed_outputs: The processed_outputs input
        provider: The model provider
        text: The text that data will be extracted from

    ## Outputs
    ### Common Outputs
        [processed_outputs]: The [processed_outputs] output
    """

    # Common inputs and outputs
    _COMMON_INPUTS = [
        {
            "field": "additional_context",
            "helper_text": "Provide any additional context or instructions",
            "value": "",
            "type": "string",
        },
        {
            "field": "fields",
            "helper_text": "The fields input",
            "value": [],
            "type": "vec<Dict[str, Any]>",
        },
        {
            "field": "model",
            "helper_text": "The specific model for data extraction",
            "value": "gpt-4o",
            "type": "enum<string>",
        },
        {
            "field": "processed_outputs",
            "helper_text": "The processed_outputs input",
            "value": {},
            "type": "map<string, string>",
        },
        {
            "field": "provider",
            "helper_text": "The model provider",
            "value": "openai",
            "type": "enum<string>",
        },
        {
            "field": "text",
            "helper_text": "The text that data will be extracted from",
            "value": "",
            "type": "string",
        },
    ]

    # Common outputs and inputs
    _COMMON_OUTPUTS = [
        {
            "field": "[processed_outputs]",
            "helper_text": "The [processed_outputs] output",
        }
    ]

    # Configuration patterns and their associated inputs/outputs
    _CONFIGS = {}

    # List of parameters that affect configuration
    _PARAMS = []

    def __init__(
        self,
        id: Optional[str] = None,
        node_name: Optional[str] = None,
        execution_mode: Optional[str] = None,
        additional_context: str = "",
        fields: List[Any] = [],
        model: str = "gpt-4o",
        processed_outputs: Dict[str, str] = {},
        provider: str = "openai",
        text: str = "",
        **kwargs
    ):
        # Initialize with params
        params = {}

        super().__init__(
            node_type="extract_data",
            params=params,
            id=id,
            node_name=node_name,
            execution_mode=execution_mode,
        )

        # Set input values
        if fields is not None:
            self.inputs["fields"] = fields
        if provider is not None:
            self.inputs["provider"] = provider
        if model is not None:
            self.inputs["model"] = model
        if additional_context is not None:
            self.inputs["additional_context"] = additional_context
        if text is not None:
            self.inputs["text"] = text
        if processed_outputs is not None:
            self.inputs["processed_outputs"] = processed_outputs

        # Update any additional inputs
        if kwargs:
            self.update_inputs(**kwargs)

    @classmethod
    def from_dict(cls, data: dict) -> "ExtractDataNode":
        """Create a node instance from a dictionary."""
        inputs = data.get("inputs", {})
        id = data.get("id", None)
        name = data.get("name", None)
        execution_mode = data.get("execution_mode", None)
        return cls(**inputs, id=id, node_name=name, execution_mode=execution_mode)


@Node.register_node_type("data_collector")
class DataCollectorNode(Node):
    """
    Allows a chatbot to collect information by asking the user to provide specific pieces of information (e.g., name, email, etc.).

    ## Inputs
    ### Common Inputs
        auto_generate: If checked, the node will output questions in successive order until all fields are successfully collected. If unchecked, the node will output the data that is collected (often passed to an LLM with a prompt to ask successive questions to the user, along with specific instructions after all fields are collected) - e.g., {'Field1': 'Collected_Data', 'Field2': 'Collected_Data'}
        data_collector_node_id: The ID of the data collector node
        fields: The fields to be collected
        prompt: Specific instructions of how the LLM should collect the information
        query: The query to be analysed for data collection (passed to the LLM)
    ### When auto_generate = True
        llm: The model provider
        model: The specific model for question generation

    ## Outputs
    ### When auto_generate = False
        collected_data: The data that is collected
    ### When auto_generate = True
        question: The question to be asked to the user
    """

    # Common inputs and outputs
    _COMMON_INPUTS = [
        {
            "field": "auto_generate",
            "helper_text": "If checked, the node will output questions in successive order until all fields are successfully collected. If unchecked, the node will output the data that is collected (often passed to an LLM with a prompt to ask successive questions to the user, along with specific instructions after all fields are collected) - e.g., {'Field1': 'Collected_Data', 'Field2': 'Collected_Data'}",
            "value": True,
            "type": "bool",
        },
        {
            "field": "data_collector_node_id",
            "helper_text": "The ID of the data collector node",
            "value": "",
            "type": "string",
        },
        {
            "field": "fields",
            "helper_text": "The fields to be collected",
            "value": [],
            "type": "vec<Dict[str, Any]>",
        },
        {
            "field": "prompt",
            "helper_text": "Specific instructions of how the LLM should collect the information",
            "value": "",
            "type": "string",
        },
        {
            "field": "query",
            "helper_text": "The query to be analysed for data collection (passed to the LLM)",
            "value": "",
            "type": "string",
        },
    ]

    # Common outputs and inputs
    _COMMON_OUTPUTS = []

    # Configuration patterns and their associated inputs/outputs
    _CONFIGS = {
        "true": {
            "inputs": [
                {
                    "field": "llm",
                    "type": "enum<string>",
                    "value": "openai",
                    "helper_text": "The model provider",
                },
                {
                    "field": "model",
                    "type": "enum<string>",
                    "value": "gpt-4-1106-preview",
                    "helper_text": "The specific model for question generation",
                },
            ],
            "outputs": [
                {
                    "field": "question",
                    "type": "string",
                    "helper_text": "The question to be asked to the user",
                }
            ],
        },
        "false": {
            "inputs": [],
            "outputs": [
                {
                    "field": "collected_data",
                    "type": "string",
                    "helper_text": "The data that is collected",
                }
            ],
        },
    }

    # List of parameters that affect configuration
    _PARAMS = ["auto_generate"]

    def __init__(
        self,
        id: Optional[str] = None,
        node_name: Optional[str] = None,
        execution_mode: Optional[str] = None,
        auto_generate: bool = True,
        data_collector_node_id: str = "",
        fields: List[Any] = [],
        llm: str = "openai",
        model: str = "gpt-4-1106-preview",
        prompt: str = "",
        query: str = "",
        **kwargs
    ):
        # Initialize with params
        params = {}
        params["auto_generate"] = auto_generate

        super().__init__(
            node_type="data_collector",
            params=params,
            id=id,
            node_name=node_name,
            execution_mode=execution_mode,
        )

        # Set input values
        if auto_generate is not None:
            self.inputs["auto_generate"] = auto_generate
        if prompt is not None:
            self.inputs["prompt"] = prompt
        if fields is not None:
            self.inputs["fields"] = fields
        if data_collector_node_id is not None:
            self.inputs["data_collector_node_id"] = data_collector_node_id
        if query is not None:
            self.inputs["query"] = query
        if llm is not None:
            self.inputs["llm"] = llm
        if model is not None:
            self.inputs["model"] = model

        # Update any additional inputs
        if kwargs:
            self.update_inputs(**kwargs)

    @property
    def collected_data(self) -> str:
        """
        The data that is collected

        Available: When auto_generate = False


        Raises:
            AttributeError: If this output is not available for the current parameter values
        """
        return self.__getattr__("collected_data")

    @property
    def question(self) -> str:
        """
        The question to be asked to the user

        Available: When auto_generate = True


        Raises:
            AttributeError: If this output is not available for the current parameter values
        """
        return self.__getattr__("question")

    @classmethod
    def from_dict(cls, data: dict) -> "DataCollectorNode":
        """Create a node instance from a dictionary."""
        inputs = data.get("inputs", {})
        id = data.get("id", None)
        name = data.get("name", None)
        execution_mode = data.get("execution_mode", None)
        return cls(**inputs, id=id, node_name=name, execution_mode=execution_mode)


@Node.register_node_type("scorer")
class ScorerNode(Node):
    """
    Score text using AI based on a set of criteria.

    ## Inputs
    ### Common Inputs
        additional_context: Provide any additional context or instructions
        criteria: The criteria that the text will be scored
        justification: Include the AI’s justification for its score
        model: The specific model for scoring
        provider: The model provider
        text: The text that will be scored

    ## Outputs
    ### Common Outputs
        score: The score of the text based on the criteria
    ### When justification = True
        justification: The AI justification
    """

    # Common inputs and outputs
    _COMMON_INPUTS = [
        {
            "field": "additional_context",
            "helper_text": "Provide any additional context or instructions",
            "value": "",
            "type": "string",
        },
        {
            "field": "criteria",
            "helper_text": "The criteria that the text will be scored",
            "value": "",
            "type": "string",
        },
        {
            "field": "justification",
            "helper_text": "Include the AI’s justification for its score",
            "value": False,
            "type": "bool",
        },
        {
            "field": "model",
            "helper_text": "The specific model for scoring",
            "value": "gpt-4o",
            "type": "enum<string>",
        },
        {
            "field": "provider",
            "helper_text": "The model provider",
            "value": "openai",
            "type": "enum<string>",
        },
        {
            "field": "text",
            "helper_text": "The text that will be scored",
            "value": "",
            "type": "string",
        },
    ]

    # Common outputs and inputs
    _COMMON_OUTPUTS = [
        {"field": "score", "helper_text": "The score of the text based on the criteria"}
    ]

    # Configuration patterns and their associated inputs/outputs
    _CONFIGS = {
        "true": {
            "inputs": [],
            "outputs": [
                {
                    "field": "justification",
                    "type": "string",
                    "helper_text": "The AI justification",
                }
            ],
        },
        "false": {"inputs": [], "outputs": []},
    }

    # List of parameters that affect configuration
    _PARAMS = ["justification"]

    def __init__(
        self,
        id: Optional[str] = None,
        node_name: Optional[str] = None,
        execution_mode: Optional[str] = None,
        justification: bool = False,
        additional_context: str = "",
        criteria: str = "",
        model: str = "gpt-4o",
        provider: str = "openai",
        text: str = "",
        **kwargs
    ):
        # Initialize with params
        params = {}
        params["justification"] = justification

        super().__init__(
            node_type="scorer",
            params=params,
            id=id,
            node_name=node_name,
            execution_mode=execution_mode,
        )

        # Set input values
        if justification is not None:
            self.inputs["justification"] = justification
        if text is not None:
            self.inputs["text"] = text
        if criteria is not None:
            self.inputs["criteria"] = criteria
        if additional_context is not None:
            self.inputs["additional_context"] = additional_context
        if provider is not None:
            self.inputs["provider"] = provider
        if model is not None:
            self.inputs["model"] = model

        # Update any additional inputs
        if kwargs:
            self.update_inputs(**kwargs)

    @property
    def justification(self) -> str:
        """
        The AI justification

        Available: When justification = True


        Raises:
            AttributeError: If this output is not available for the current parameter values
        """
        return self.__getattr__("justification")

    @property
    def score(self) -> Any:
        """
        The score of the text based on the criteria


        Raises:
            AttributeError: If this output is not available for the current parameter values
        """
        return self.__getattr__("score")

    @classmethod
    def from_dict(cls, data: dict) -> "ScorerNode":
        """Create a node instance from a dictionary."""
        inputs = data.get("inputs", {})
        id = data.get("id", None)
        name = data.get("name", None)
        execution_mode = data.get("execution_mode", None)
        return cls(**inputs, id=id, node_name=name, execution_mode=execution_mode)


@Node.register_node_type("speech_to_text")
class SpeechToTextNode(Node):
    """


    ## Inputs
    ### Common Inputs
        audio: The audio input
        model: The model input
    ### Deepgram
        submodel: The submodel input
        tier: The tier input

    ## Outputs
    ### Common Outputs
        text: The text output
    """

    # Common inputs and outputs
    _COMMON_INPUTS = [
        {
            "field": "audio",
            "helper_text": "The audio input",
            "value": "",
            "type": "audio",
        },
        {
            "field": "model",
            "helper_text": "The model input",
            "value": "OpenAI Whisper",
            "type": "enum<string>",
        },
    ]

    # Common outputs and inputs
    _COMMON_OUTPUTS = [{"field": "text", "helper_text": "The text output"}]

    # Configuration patterns and their associated inputs/outputs
    _CONFIGS = {
        "OpenAI Whisper": {"inputs": [], "outputs": []},
        "Deepgram": {
            "inputs": [
                {"field": "submodel", "type": "enum<string>", "value": "nova-2"},
                {"field": "tier", "type": "enum<string>", "value": "general"},
            ],
            "outputs": [],
        },
    }

    # List of parameters that affect configuration
    _PARAMS = ["model"]

    def __init__(
        self,
        id: Optional[str] = None,
        node_name: Optional[str] = None,
        execution_mode: Optional[str] = None,
        model: str = "OpenAI Whisper",
        audio: Any = None,
        submodel: str = "nova-2",
        tier: str = "general",
        **kwargs
    ):
        # Initialize with params
        params = {}
        params["model"] = model

        super().__init__(
            node_type="speech_to_text",
            params=params,
            id=id,
            node_name=node_name,
            execution_mode=execution_mode,
        )

        # Set input values
        if model is not None:
            self.inputs["model"] = model
        if audio is not None:
            self.inputs["audio"] = audio
        if submodel is not None:
            self.inputs["submodel"] = submodel
        if tier is not None:
            self.inputs["tier"] = tier

        # Update any additional inputs
        if kwargs:
            self.update_inputs(**kwargs)

    @property
    def text(self) -> str:
        """
        The text output


        Raises:
            AttributeError: If this output is not available for the current parameter values
        """
        return self.__getattr__("text")

    @classmethod
    def from_dict(cls, data: dict) -> "SpeechToTextNode":
        """Create a node instance from a dictionary."""
        inputs = data.get("inputs", {})
        id = data.get("id", None)
        name = data.get("name", None)
        execution_mode = data.get("execution_mode", None)
        return cls(**inputs, id=id, node_name=name, execution_mode=execution_mode)


@Node.register_node_type("file_save")
class FileSaveNode(Node):
    """
    Save a file on the VectorShift platform (under the 'Files' tab).

    ## Inputs
    ### Common Inputs
        files: The files to be saved
        name: The name of the file

    ## Outputs
    ### Common Outputs
        file_name: The name of the file saved
    """

    # Common inputs and outputs
    _COMMON_INPUTS = [
        {
            "field": "files",
            "helper_text": "The files to be saved",
            "value": [""],
            "type": "vec<file>",
        },
        {
            "field": "name",
            "helper_text": "The name of the file",
            "value": "",
            "type": "string",
        },
    ]

    # Common outputs and inputs
    _COMMON_OUTPUTS = [
        {"field": "file_name", "helper_text": "The name of the file saved"}
    ]

    # Configuration patterns and their associated inputs/outputs
    _CONFIGS = {}

    # List of parameters that affect configuration
    _PARAMS = []

    def __init__(
        self,
        id: Optional[str] = None,
        node_name: Optional[str] = None,
        execution_mode: Optional[str] = None,
        files: List[str] = [""],
        name: str = "",
        **kwargs
    ):
        # Initialize with params
        params = {}

        super().__init__(
            node_type="file_save",
            params=params,
            id=id,
            node_name=node_name,
            execution_mode=execution_mode,
        )

        # Set input values
        if name is not None:
            self.inputs["name"] = name
        if files is not None:
            self.inputs["files"] = files

        # Update any additional inputs
        if kwargs:
            self.update_inputs(**kwargs)

    @property
    def file_name(self) -> List[str]:
        """
        The name of the file saved


        Raises:
            AttributeError: If this output is not available for the current parameter values
        """
        return self.__getattr__("file_name")

    @classmethod
    def from_dict(cls, data: dict) -> "FileSaveNode":
        """Create a node instance from a dictionary."""
        inputs = data.get("inputs", {})
        id = data.get("id", None)
        name = data.get("name", None)
        execution_mode = data.get("execution_mode", None)
        return cls(**inputs, id=id, node_name=name, execution_mode=execution_mode)


@Node.register_node_type("image_gen")
class ImageGenNode(Node):
    """


    ## Inputs
    ### Common Inputs
        aspect_ratio: The aspect_ratio input
        image_count: The image_count input
        model: The model input
        prompt: The prompt input
        provider: The provider input
        size: The size input

    ## Outputs
    ### Common Outputs
        images: The images output
    """

    # Common inputs and outputs
    _COMMON_INPUTS = [
        {
            "field": "aspect_ratio",
            "helper_text": "The aspect_ratio input",
            "value": "1:1",
            "type": "enum<string>",
        },
        {
            "field": "image_count",
            "helper_text": "The image_count input",
            "value": "1",
            "type": "string",
        },
        {
            "field": "model",
            "helper_text": "The model input",
            "value": "gpt-4-1106-preview",
            "type": "enum<string>",
        },
        {
            "field": "prompt",
            "helper_text": "The prompt input",
            "value": "",
            "type": "string",
        },
        {
            "field": "provider",
            "helper_text": "The provider input",
            "value": "llmOpenAI",
            "type": "enum<string>",
        },
        {
            "field": "size",
            "helper_text": "The size input",
            "value": "512x512",
            "type": "enum<string>",
        },
    ]

    # Common outputs and inputs
    _COMMON_OUTPUTS = [{"field": "images", "helper_text": "The images output"}]

    # Configuration patterns and their associated inputs/outputs
    _CONFIGS = {}

    # List of parameters that affect configuration
    _PARAMS = []

    def __init__(
        self,
        id: Optional[str] = None,
        node_name: Optional[str] = None,
        execution_mode: Optional[str] = None,
        aspect_ratio: str = "1:1",
        image_count: str = "1",
        model: str = "gpt-4-1106-preview",
        prompt: str = "",
        provider: str = "llmOpenAI",
        size: str = "512x512",
        **kwargs
    ):
        # Initialize with params
        params = {}

        super().__init__(
            node_type="image_gen",
            params=params,
            id=id,
            node_name=node_name,
            execution_mode=execution_mode,
        )

        # Set input values
        if prompt is not None:
            self.inputs["prompt"] = prompt
        if provider is not None:
            self.inputs["provider"] = provider
        if model is not None:
            self.inputs["model"] = model
        if size is not None:
            self.inputs["size"] = size
        if aspect_ratio is not None:
            self.inputs["aspect_ratio"] = aspect_ratio
        if image_count is not None:
            self.inputs["image_count"] = image_count

        # Update any additional inputs
        if kwargs:
            self.update_inputs(**kwargs)

    @property
    def images(self) -> List[Any]:
        """
        The images output


        Raises:
            AttributeError: If this output is not available for the current parameter values
        """
        return self.__getattr__("images")

    @classmethod
    def from_dict(cls, data: dict) -> "ImageGenNode":
        """Create a node instance from a dictionary."""
        inputs = data.get("inputs", {})
        id = data.get("id", None)
        name = data.get("name", None)
        execution_mode = data.get("execution_mode", None)
        return cls(**inputs, id=id, node_name=name, execution_mode=execution_mode)


@Node.register_node_type("file")
class FileNode(Node):
    """
    Load a static file into the workflow as a raw File or process it into Text.

    ## Inputs
    ### Common Inputs
        file_parser: The processing model with which the document will be processed. Default processing model includes standard document parsing / OCR. Llamaparse will allow for ability to read documents with complex features (e.g., tables, charts, etc.). Llamaparse will be charged at 0.3 cents per page. Textract for most advanced data extraction and will be charged at 1.5 cents per page.
        selected_option: Select an existing file from the VectorShift platform
    ### upload
        file: The file that was passed in
    ### name
        file_name: The name of the file from the VectorShift platform (for files on the File tab)

    ## Outputs
    ### Common Outputs
        file: The file that was passed in
        processed_text: The processed text of the file
    """

    # Common inputs and outputs
    _COMMON_INPUTS = [
        {
            "field": "file_parser",
            "helper_text": "The processing model with which the document will be processed. Default processing model includes standard document parsing / OCR. Llamaparse will allow for ability to read documents with complex features (e.g., tables, charts, etc.). Llamaparse will be charged at 0.3 cents per page. Textract for most advanced data extraction and will be charged at 1.5 cents per page.",
            "value": "default",
            "type": "enum<string>",
        },
        {
            "field": "selected_option",
            "helper_text": "Select an existing file from the VectorShift platform",
            "value": "upload",
            "type": "enum<string>",
        },
    ]

    # Common outputs and inputs
    _COMMON_OUTPUTS = [
        {"field": "file", "helper_text": "The file that was passed in"},
        {"field": "processed_text", "helper_text": "The processed text of the file"},
    ]

    # Configuration patterns and their associated inputs/outputs
    _CONFIGS = {
        "upload": {
            "inputs": [
                {
                    "field": "file",
                    "type": "file",
                    "helper_text": "The file that was passed in",
                }
            ],
            "outputs": [],
        },
        "name": {
            "inputs": [
                {
                    "field": "file_name",
                    "type": "string",
                    "value": "",
                    "helper_text": "The name of the file from the VectorShift platform (for files on the File tab)",
                }
            ],
            "outputs": [],
        },
    }

    # List of parameters that affect configuration
    _PARAMS = ["selected_option"]

    def __init__(
        self,
        id: Optional[str] = None,
        node_name: Optional[str] = None,
        execution_mode: Optional[str] = None,
        selected_option: str = "upload",
        file: Optional[str] = None,
        file_name: str = "",
        file_parser: str = "default",
        **kwargs
    ):
        # Initialize with params
        params = {}
        params["selected_option"] = selected_option

        super().__init__(
            node_type="file",
            params=params,
            id=id,
            node_name=node_name,
            execution_mode=execution_mode,
        )

        # Set input values
        if file_parser is not None:
            self.inputs["file_parser"] = file_parser
        if selected_option is not None:
            self.inputs["selected_option"] = selected_option
        if file is not None:
            self.inputs["file"] = file
        if file_name is not None:
            self.inputs["file_name"] = file_name

        # Update any additional inputs
        if kwargs:
            self.update_inputs(**kwargs)

    @property
    def file(self) -> str:
        """
        The file that was passed in


        Raises:
            AttributeError: If this output is not available for the current parameter values
        """
        return self.__getattr__("file")

    @property
    def processed_text(self) -> str:
        """
        The processed text of the file


        Raises:
            AttributeError: If this output is not available for the current parameter values
        """
        return self.__getattr__("processed_text")

    @classmethod
    def from_dict(cls, data: dict) -> "FileNode":
        """Create a node instance from a dictionary."""
        inputs = data.get("inputs", {})
        id = data.get("id", None)
        name = data.get("name", None)
        execution_mode = data.get("execution_mode", None)
        return cls(**inputs, id=id, node_name=name, execution_mode=execution_mode)


@Node.register_node_type("get_list_item")
class GetListItemNode(Node):
    """
    Get a value from a list given an index. The first item in the list is index 0.

    ## Inputs
    ### Common Inputs
        index: The index of the item to retrieve
        type: The type of the list
    ### <T>
        list: The list to retrieve the item from

    ## Outputs
    ### <T>
        output: The item retrieved from the list
    """

    # Common inputs and outputs
    _COMMON_INPUTS = [
        {
            "field": "index",
            "helper_text": "The index of the item to retrieve",
            "value": 0,
            "type": "int32",
        },
        {
            "field": "type",
            "helper_text": "The type of the list",
            "value": "string",
            "type": "enum<string>",
        },
    ]

    # Common outputs and inputs
    _COMMON_OUTPUTS = []

    # Configuration patterns and their associated inputs/outputs
    _CONFIGS = {
        "<T>": {
            "inputs": [
                {
                    "field": "list",
                    "type": "vec<<T>>",
                    "value": "",
                    "helper_text": "The list to retrieve the item from",
                }
            ],
            "outputs": [
                {
                    "field": "output",
                    "type": "<T>",
                    "helper_text": "The item retrieved from the list",
                }
            ],
        }
    }

    # List of parameters that affect configuration
    _PARAMS = ["type"]

    def __init__(
        self,
        id: Optional[str] = None,
        node_name: Optional[str] = None,
        execution_mode: Optional[str] = None,
        type: str = "string",
        index: int = 0,
        list: List[Any] = [],
        **kwargs
    ):
        # Initialize with params
        params = {}
        params["type"] = type

        super().__init__(
            node_type="get_list_item",
            params=params,
            id=id,
            node_name=node_name,
            execution_mode=execution_mode,
        )

        # Set input values
        if type is not None:
            self.inputs["type"] = type
        if index is not None:
            self.inputs["index"] = index
        if list is not None:
            self.inputs["list"] = list

        # Update any additional inputs
        if kwargs:
            self.update_inputs(**kwargs)

    @classmethod
    def from_dict(cls, data: dict) -> "GetListItemNode":
        """Create a node instance from a dictionary."""
        inputs = data.get("inputs", {})
        id = data.get("id", None)
        name = data.get("name", None)
        execution_mode = data.get("execution_mode", None)
        return cls(**inputs, id=id, node_name=name, execution_mode=execution_mode)


@Node.register_node_type("llm_open_ai_vision")
class LlmOpenAiVisionNode(Node):
    """


    ## Inputs
    ### Common Inputs
        image: The image input
        json_response: The json_response input
        max_tokens: The max_tokens input
        model: The model input
        prompt: The prompt input
        provider: The provider input
        stream: The stream input
        system: The system input
        temperature: The temperature input
        top_p: The top_p input
        use_personal_api_key: The use_personal_api_key input
    ### When use_personal_api_key = True
        api_key: The api_key input
    ### When json_response = True
        json_schema: The json_schema input

    ## Outputs
    ### Common Outputs
        response: The response output
        tokens_used: The tokens_used output
    ### When stream = True
        response_deltas: The response_deltas output
    """

    # Common inputs and outputs
    _COMMON_INPUTS = [
        {
            "field": "image",
            "helper_text": "The image input",
            "value": None,
            "type": "image",
        },
        {
            "field": "json_response",
            "helper_text": "The json_response input",
            "value": False,
            "type": "bool",
        },
        {
            "field": "max_tokens",
            "helper_text": "The max_tokens input",
            "value": 128000,
            "type": "int32",
        },
        {
            "field": "model",
            "helper_text": "The model input",
            "value": "gpt-4-vision-preview",
            "type": "enum<string>",
        },
        {
            "field": "prompt",
            "helper_text": "The prompt input",
            "value": "",
            "type": "string",
        },
        {
            "field": "provider",
            "helper_text": "The provider input",
            "value": "openAiImageToText",
            "type": "enum<string>",
        },
        {
            "field": "stream",
            "helper_text": "The stream input",
            "value": False,
            "type": "bool",
        },
        {
            "field": "system",
            "helper_text": "The system input",
            "value": "",
            "type": "string",
        },
        {
            "field": "temperature",
            "helper_text": "The temperature input",
            "value": 0.7,
            "type": "float",
        },
        {
            "field": "top_p",
            "helper_text": "The top_p input",
            "value": 0.9,
            "type": "float",
        },
        {
            "field": "use_personal_api_key",
            "helper_text": "The use_personal_api_key input",
            "value": False,
            "type": "bool",
        },
    ]

    # Common outputs and inputs
    _COMMON_OUTPUTS = [
        {"field": "response", "helper_text": "The response output"},
        {"field": "tokens_used", "helper_text": "The tokens_used output"},
    ]

    # Configuration patterns and their associated inputs/outputs
    _CONFIGS = {
        "(*)**true**(*)**(*)": {
            "inputs": [],
            "outputs": [{"field": "response_deltas", "type": "Stream<string>"}],
        },
        "(*)**false**(*)**(*)": {"inputs": [], "outputs": []},
        "(*)**(*)**true**(*)": {
            "inputs": [{"field": "api_key", "type": "string", "value": ""}],
            "outputs": [],
        },
        "(*)**(*)**false**(*)": {"inputs": [], "outputs": []},
        "(*)**(*)**(*)**true": {
            "inputs": [{"field": "json_schema", "type": "string", "value": ""}],
            "outputs": [],
        },
        "(*)**(*)**(*)**false": {"inputs": [], "outputs": []},
    }

    # List of parameters that affect configuration
    _PARAMS = ["provider", "stream", "use_personal_api_key", "json_response"]

    def __init__(
        self,
        id: Optional[str] = None,
        node_name: Optional[str] = None,
        execution_mode: Optional[str] = None,
        provider: str = "openAiImageToText",
        stream: bool = False,
        use_personal_api_key: bool = False,
        json_response: bool = False,
        api_key: str = "",
        image: Optional[Any] = None,
        json_schema: str = "",
        max_tokens: int = 128000,
        model: str = "gpt-4-vision-preview",
        prompt: str = "",
        system: str = "",
        temperature: Any = 0.7,
        top_p: Any = 0.9,
        **kwargs
    ):
        # Initialize with params
        params = {}
        params["provider"] = provider
        params["stream"] = stream
        params["use_personal_api_key"] = use_personal_api_key
        params["json_response"] = json_response

        super().__init__(
            node_type="llm_open_ai_vision",
            params=params,
            id=id,
            node_name=node_name,
            execution_mode=execution_mode,
        )

        # Set input values
        if system is not None:
            self.inputs["system"] = system
        if prompt is not None:
            self.inputs["prompt"] = prompt
        if provider is not None:
            self.inputs["provider"] = provider
        if model is not None:
            self.inputs["model"] = model
        if max_tokens is not None:
            self.inputs["max_tokens"] = max_tokens
        if temperature is not None:
            self.inputs["temperature"] = temperature
        if top_p is not None:
            self.inputs["top_p"] = top_p
        if stream is not None:
            self.inputs["stream"] = stream
        if json_response is not None:
            self.inputs["json_response"] = json_response
        if use_personal_api_key is not None:
            self.inputs["use_personal_api_key"] = use_personal_api_key
        if image is not None:
            self.inputs["image"] = image
        if api_key is not None:
            self.inputs["api_key"] = api_key
        if json_schema is not None:
            self.inputs["json_schema"] = json_schema

        # Update any additional inputs
        if kwargs:
            self.update_inputs(**kwargs)

    @property
    def response(self) -> str:
        """
        The response output


        Raises:
            AttributeError: If this output is not available for the current parameter values
        """
        return self.__getattr__("response")

    @property
    def tokens_used(self) -> int:
        """
        The tokens_used output


        Raises:
            AttributeError: If this output is not available for the current parameter values
        """
        return self.__getattr__("tokens_used")

    @classmethod
    def from_dict(cls, data: dict) -> "LlmOpenAiVisionNode":
        """Create a node instance from a dictionary."""
        inputs = data.get("inputs", {})
        id = data.get("id", None)
        name = data.get("name", None)
        execution_mode = data.get("execution_mode", None)
        return cls(**inputs, id=id, node_name=name, execution_mode=execution_mode)


@Node.register_node_type("llm_google_vision")
class LlmGoogleVisionNode(Node):
    """


    ## Inputs
    ### Common Inputs
        api_key: The api_key input
        image: The image input
        json_response: The json_response input
        max_tokens: The max_tokens input
        model: The model input
        prompt: The prompt input
        provider: The provider input
        stream: The stream input
        temperature: The temperature input
        top_p: The top_p input

    ## Outputs
    ### Common Outputs
        response: The response output
    """

    # Common inputs and outputs
    _COMMON_INPUTS = [
        {
            "field": "api_key",
            "helper_text": "The api_key input",
            "value": "",
            "type": "string",
        },
        {
            "field": "image",
            "helper_text": "The image input",
            "value": None,
            "type": "image",
        },
        {
            "field": "json_response",
            "helper_text": "The json_response input",
            "value": False,
            "type": "bool",
        },
        {
            "field": "max_tokens",
            "helper_text": "The max_tokens input",
            "value": 32760,
            "type": "int32",
        },
        {
            "field": "model",
            "helper_text": "The model input",
            "value": "gemini-pro-vision",
            "type": "enum<string>",
        },
        {
            "field": "prompt",
            "helper_text": "The prompt input",
            "value": "",
            "type": "string",
        },
        {
            "field": "provider",
            "helper_text": "The provider input",
            "value": "googleImageToText",
            "type": "enum<string>",
        },
        {
            "field": "stream",
            "helper_text": "The stream input",
            "value": False,
            "type": "bool",
        },
        {
            "field": "temperature",
            "helper_text": "The temperature input",
            "value": 0.7,
            "type": "float",
        },
        {
            "field": "top_p",
            "helper_text": "The top_p input",
            "value": 0.9,
            "type": "float",
        },
    ]

    # Common outputs and inputs
    _COMMON_OUTPUTS = [{"field": "response", "helper_text": "The response output"}]

    # Configuration patterns and their associated inputs/outputs
    _CONFIGS = {}

    # List of parameters that affect configuration
    _PARAMS = []

    def __init__(
        self,
        id: Optional[str] = None,
        node_name: Optional[str] = None,
        execution_mode: Optional[str] = None,
        api_key: str = "",
        image: Optional[Any] = None,
        json_response: bool = False,
        max_tokens: int = 32760,
        model: str = "gemini-pro-vision",
        prompt: str = "",
        provider: str = "googleImageToText",
        stream: bool = False,
        temperature: Any = 0.7,
        top_p: Any = 0.9,
        **kwargs
    ):
        # Initialize with params
        params = {}

        super().__init__(
            node_type="llm_google_vision",
            params=params,
            id=id,
            node_name=node_name,
            execution_mode=execution_mode,
        )

        # Set input values
        if prompt is not None:
            self.inputs["prompt"] = prompt
        if provider is not None:
            self.inputs["provider"] = provider
        if model is not None:
            self.inputs["model"] = model
        if max_tokens is not None:
            self.inputs["max_tokens"] = max_tokens
        if temperature is not None:
            self.inputs["temperature"] = temperature
        if top_p is not None:
            self.inputs["top_p"] = top_p
        if stream is not None:
            self.inputs["stream"] = stream
        if json_response is not None:
            self.inputs["json_response"] = json_response
        if api_key is not None:
            self.inputs["api_key"] = api_key
        if image is not None:
            self.inputs["image"] = image

        # Update any additional inputs
        if kwargs:
            self.update_inputs(**kwargs)

    @property
    def response(self) -> str:
        """
        The response output


        Raises:
            AttributeError: If this output is not available for the current parameter values
        """
        return self.__getattr__("response")

    @classmethod
    def from_dict(cls, data: dict) -> "LlmGoogleVisionNode":
        """Create a node instance from a dictionary."""
        inputs = data.get("inputs", {})
        id = data.get("id", None)
        name = data.get("name", None)
        execution_mode = data.get("execution_mode", None)
        return cls(**inputs, id=id, node_name=name, execution_mode=execution_mode)


@Node.register_node_type("split_text")
class SplitTextNode(Node):
    """
    Takes input text and separate it into a List of texts based on the delimiter.

    ## Inputs
    ### Common Inputs
        delimiter: The delimiter to split the text on
        text: The text to split
    ### character(s)
        character: The character(s) to split the text on

    ## Outputs
    ### Common Outputs
        processed_text: The text split into a list
    """

    # Common inputs and outputs
    _COMMON_INPUTS = [
        {
            "field": "delimiter",
            "helper_text": "The delimiter to split the text on",
            "value": "space",
            "type": "enum<string>",
        },
        {
            "field": "text",
            "helper_text": "The text to split",
            "value": "",
            "type": "string",
        },
    ]

    # Common outputs and inputs
    _COMMON_OUTPUTS = [
        {"field": "processed_text", "helper_text": "The text split into a list"}
    ]

    # Configuration patterns and their associated inputs/outputs
    _CONFIGS = {
        "character(s)": {
            "inputs": [
                {
                    "field": "character",
                    "type": "string",
                    "value": "",
                    "helper_text": "The character(s) to split the text on",
                }
            ],
            "outputs": [],
        },
        "space": {"inputs": [], "outputs": []},
        "newline": {"inputs": [], "outputs": []},
    }

    # List of parameters that affect configuration
    _PARAMS = ["delimiter"]

    def __init__(
        self,
        id: Optional[str] = None,
        node_name: Optional[str] = None,
        execution_mode: Optional[str] = None,
        delimiter: str = "space",
        character: str = "",
        text: str = "",
        **kwargs
    ):
        # Initialize with params
        params = {}
        params["delimiter"] = delimiter

        super().__init__(
            node_type="split_text",
            params=params,
            id=id,
            node_name=node_name,
            execution_mode=execution_mode,
        )

        # Set input values
        if delimiter is not None:
            self.inputs["delimiter"] = delimiter
        if text is not None:
            self.inputs["text"] = text
        if character is not None:
            self.inputs["character"] = character

        # Update any additional inputs
        if kwargs:
            self.update_inputs(**kwargs)

    @property
    def processed_text(self) -> List[str]:
        """
        The text split into a list


        Raises:
            AttributeError: If this output is not available for the current parameter values
        """
        return self.__getattr__("processed_text")

    @classmethod
    def from_dict(cls, data: dict) -> "SplitTextNode":
        """Create a node instance from a dictionary."""
        inputs = data.get("inputs", {})
        id = data.get("id", None)
        name = data.get("name", None)
        execution_mode = data.get("execution_mode", None)
        return cls(**inputs, id=id, node_name=name, execution_mode=execution_mode)


@Node.register_node_type("summarizer")
class SummarizerNode(Node):
    """
    Summarize text with AI

    ## Inputs
    ### Common Inputs
        model: The specific model for summarization
        provider: The model provider
        text: The text to be summarized

    ## Outputs
    ### Common Outputs
        summary: The summary of the text
    """

    # Common inputs and outputs
    _COMMON_INPUTS = [
        {
            "field": "model",
            "helper_text": "The specific model for summarization",
            "value": "gpt-4o",
            "type": "enum<string>",
        },
        {
            "field": "provider",
            "helper_text": "The model provider",
            "value": "openai",
            "type": "enum<string>",
        },
        {
            "field": "text",
            "helper_text": "The text to be summarized",
            "value": "",
            "type": "string",
        },
    ]

    # Common outputs and inputs
    _COMMON_OUTPUTS = [{"field": "summary", "helper_text": "The summary of the text"}]

    # Configuration patterns and their associated inputs/outputs
    _CONFIGS = {}

    # List of parameters that affect configuration
    _PARAMS = []

    def __init__(
        self,
        id: Optional[str] = None,
        node_name: Optional[str] = None,
        execution_mode: Optional[str] = None,
        model: str = "gpt-4o",
        provider: str = "openai",
        text: str = "",
        **kwargs
    ):
        # Initialize with params
        params = {}

        super().__init__(
            node_type="summarizer",
            params=params,
            id=id,
            node_name=node_name,
            execution_mode=execution_mode,
        )

        # Set input values
        if text is not None:
            self.inputs["text"] = text
        if provider is not None:
            self.inputs["provider"] = provider
        if model is not None:
            self.inputs["model"] = model

        # Update any additional inputs
        if kwargs:
            self.update_inputs(**kwargs)

    @property
    def summary(self) -> str:
        """
        The summary of the text


        Raises:
            AttributeError: If this output is not available for the current parameter values
        """
        return self.__getattr__("summary")

    @classmethod
    def from_dict(cls, data: dict) -> "SummarizerNode":
        """Create a node instance from a dictionary."""
        inputs = data.get("inputs", {})
        id = data.get("id", None)
        name = data.get("name", None)
        execution_mode = data.get("execution_mode", None)
        return cls(**inputs, id=id, node_name=name, execution_mode=execution_mode)


@Node.register_node_type("text")
class TextNode(Node):
    """
    Accepts Text from upstream nodes and allows you to write additional text / concatenate different texts to pass to downstream nodes.

    ## Inputs
    ### Common Inputs
        text: The text to be processed

    ## Outputs
    ### Common Outputs
        text: The text from the node
    """

    # Common inputs and outputs
    _COMMON_INPUTS = [
        {
            "field": "text",
            "helper_text": "The text to be processed",
            "value": "",
            "type": "string",
        }
    ]

    # Common outputs and inputs
    _COMMON_OUTPUTS = [{"field": "text", "helper_text": "The text from the node"}]

    # Configuration patterns and their associated inputs/outputs
    _CONFIGS = {}

    # List of parameters that affect configuration
    _PARAMS = []

    def __init__(
        self,
        id: Optional[str] = None,
        node_name: Optional[str] = None,
        execution_mode: Optional[str] = None,
        text: str = "",
        **kwargs
    ):
        # Initialize with params
        params = {}

        super().__init__(
            node_type="text",
            params=params,
            id=id,
            node_name=node_name,
            execution_mode=execution_mode,
        )

        # Set input values
        if text is not None:
            self.inputs["text"] = text

        # Update any additional inputs
        if kwargs:
            self.update_inputs(**kwargs)

    @property
    def text(self) -> str:
        """
        The text from the node


        Raises:
            AttributeError: If this output is not available for the current parameter values
        """
        return self.__getattr__("text")

    @classmethod
    def from_dict(cls, data: dict) -> "TextNode":
        """Create a node instance from a dictionary."""
        inputs = data.get("inputs", {})
        id = data.get("id", None)
        name = data.get("name", None)
        execution_mode = data.get("execution_mode", None)
        return cls(**inputs, id=id, node_name=name, execution_mode=execution_mode)


@Node.register_node_type("text_to_file")
class TextToFileNode(Node):
    """
    Convert data from type Text to type File

    ## Inputs
    ### Common Inputs
        file_type: The type of file to convert the text to.
        text: The text for conversion.

    ## Outputs
    ### Common Outputs
        file: The text as converted to a file.
        file_type: The type of file that was converted the text to.
    """

    # Common inputs and outputs
    _COMMON_INPUTS = [
        {
            "field": "file_type",
            "helper_text": "The type of file to convert the text to.",
            "value": "PDF",
            "type": "enum<string>",
        },
        {
            "field": "text",
            "helper_text": "The text for conversion.",
            "value": "",
            "type": "string",
        },
    ]

    # Common outputs and inputs
    _COMMON_OUTPUTS = [
        {"field": "file", "helper_text": "The text as converted to a file."},
        {
            "field": "file_type",
            "helper_text": "The type of file that was converted the text to.",
        },
    ]

    # Configuration patterns and their associated inputs/outputs
    _CONFIGS = {}

    # List of parameters that affect configuration
    _PARAMS = []

    def __init__(
        self,
        id: Optional[str] = None,
        node_name: Optional[str] = None,
        execution_mode: Optional[str] = None,
        file_type: str = "PDF",
        text: str = "",
        **kwargs
    ):
        # Initialize with params
        params = {}

        super().__init__(
            node_type="text_to_file",
            params=params,
            id=id,
            node_name=node_name,
            execution_mode=execution_mode,
        )

        # Set input values
        if file_type is not None:
            self.inputs["file_type"] = file_type
        if text is not None:
            self.inputs["text"] = text

        # Update any additional inputs
        if kwargs:
            self.update_inputs(**kwargs)

    @property
    def file(self) -> str:
        """
        The text as converted to a file.


        Raises:
            AttributeError: If this output is not available for the current parameter values
        """
        return self.__getattr__("file")

    @property
    def file_type(self) -> str:
        """
        The type of file that was converted the text to.


        Raises:
            AttributeError: If this output is not available for the current parameter values
        """
        return self.__getattr__("file_type")

    @classmethod
    def from_dict(cls, data: dict) -> "TextToFileNode":
        """Create a node instance from a dictionary."""
        inputs = data.get("inputs", {})
        id = data.get("id", None)
        name = data.get("name", None)
        execution_mode = data.get("execution_mode", None)
        return cls(**inputs, id=id, node_name=name, execution_mode=execution_mode)


@Node.register_node_type("time")
class TimeNode(Node):
    """
    Outputs the current time (often connected to LLM node)

    ## Inputs
    ### Common Inputs
        delta_time_unit: The unit of the delta
        delta_value: The value of the delta
        is_positive: If the time should be positive
        is_positive_delta: If the time should be positive
        output_format: The format of the output time
        time_node_zone: The timezone of the time node

    ## Outputs
    ### Common Outputs
        processed_time: The time from the node
    """

    # Common inputs and outputs
    _COMMON_INPUTS = [
        {
            "field": "delta_time_unit",
            "helper_text": "The unit of the delta",
            "value": "Seconds",
            "type": "enum<string>",
        },
        {
            "field": "delta_value",
            "helper_text": "The value of the delta",
            "value": 0,
            "type": "int32",
        },
        {
            "field": "is_positive",
            "helper_text": "If the time should be positive",
            "value": "+",
            "type": "enum<string>",
        },
        {
            "field": "is_positive_delta",
            "helper_text": "If the time should be positive",
            "value": True,
            "type": "bool",
        },
        {
            "field": "output_format",
            "helper_text": "The format of the output time",
            "value": "DD/MM/YYYY",
            "type": "enum<string>",
        },
        {
            "field": "time_node_zone",
            "helper_text": "The timezone of the time node",
            "value": "America/New_York",
            "type": "enum<string>",
        },
    ]

    # Common outputs and inputs
    _COMMON_OUTPUTS = [
        {"field": "processed_time", "helper_text": "The time from the node"}
    ]

    # Configuration patterns and their associated inputs/outputs
    _CONFIGS = {}

    # List of parameters that affect configuration
    _PARAMS = []

    def __init__(
        self,
        id: Optional[str] = None,
        node_name: Optional[str] = None,
        execution_mode: Optional[str] = None,
        delta_time_unit: str = "Seconds",
        delta_value: int = 0,
        is_positive: str = "+",
        is_positive_delta: bool = True,
        output_format: str = "DD/MM/YYYY",
        time_node_zone: str = "America/New_York",
        **kwargs
    ):
        # Initialize with params
        params = {}

        super().__init__(
            node_type="time",
            params=params,
            id=id,
            node_name=node_name,
            execution_mode=execution_mode,
        )

        # Set input values
        if is_positive is not None:
            self.inputs["is_positive"] = is_positive
        if is_positive_delta is not None:
            self.inputs["is_positive_delta"] = is_positive_delta
        if delta_value is not None:
            self.inputs["delta_value"] = delta_value
        if delta_time_unit is not None:
            self.inputs["delta_time_unit"] = delta_time_unit
        if output_format is not None:
            self.inputs["output_format"] = output_format
        if time_node_zone is not None:
            self.inputs["time_node_zone"] = time_node_zone

        # Update any additional inputs
        if kwargs:
            self.update_inputs(**kwargs)

    @property
    def processed_time(self) -> str:
        """
        The time from the node


        Raises:
            AttributeError: If this output is not available for the current parameter values
        """
        return self.__getattr__("processed_time")

    @classmethod
    def from_dict(cls, data: dict) -> "TimeNode":
        """Create a node instance from a dictionary."""
        inputs = data.get("inputs", {})
        id = data.get("id", None)
        name = data.get("name", None)
        execution_mode = data.get("execution_mode", None)
        return cls(**inputs, id=id, node_name=name, execution_mode=execution_mode)


@Node.register_node_type("translator")
class TranslatorNode(Node):
    """
    Translate text from one language to another

    ## Inputs
    ### Common Inputs
        model: The specific model for translation
        provider: The model provider
        source_language: The language of the input text
        target_language: The language to translate to
        text: The text to be translated

    ## Outputs
    ### Common Outputs
        translation: The translation of the text
    """

    # Common inputs and outputs
    _COMMON_INPUTS = [
        {
            "field": "model",
            "helper_text": "The specific model for translation",
            "value": "gpt-4o",
            "type": "enum<string>",
        },
        {
            "field": "provider",
            "helper_text": "The model provider",
            "value": "openai",
            "type": "enum<string>",
        },
        {
            "field": "source_language",
            "helper_text": "The language of the input text",
            "value": "Detect Language",
            "type": "enum<string>",
        },
        {
            "field": "target_language",
            "helper_text": "The language to translate to",
            "value": "English",
            "type": "enum<string>",
        },
        {
            "field": "text",
            "helper_text": "The text to be translated",
            "value": "",
            "type": "string",
        },
    ]

    # Common outputs and inputs
    _COMMON_OUTPUTS = [
        {"field": "translation", "helper_text": "The translation of the text"}
    ]

    # Configuration patterns and their associated inputs/outputs
    _CONFIGS = {}

    # List of parameters that affect configuration
    _PARAMS = []

    def __init__(
        self,
        id: Optional[str] = None,
        node_name: Optional[str] = None,
        execution_mode: Optional[str] = None,
        model: str = "gpt-4o",
        provider: str = "openai",
        source_language: str = "Detect Language",
        target_language: str = "English",
        text: str = "",
        **kwargs
    ):
        # Initialize with params
        params = {}

        super().__init__(
            node_type="translator",
            params=params,
            id=id,
            node_name=node_name,
            execution_mode=execution_mode,
        )

        # Set input values
        if text is not None:
            self.inputs["text"] = text
        if provider is not None:
            self.inputs["provider"] = provider
        if model is not None:
            self.inputs["model"] = model
        if source_language is not None:
            self.inputs["source_language"] = source_language
        if target_language is not None:
            self.inputs["target_language"] = target_language

        # Update any additional inputs
        if kwargs:
            self.update_inputs(**kwargs)

    @property
    def translation(self) -> str:
        """
        The translation of the text


        Raises:
            AttributeError: If this output is not available for the current parameter values
        """
        return self.__getattr__("translation")

    @classmethod
    def from_dict(cls, data: dict) -> "TranslatorNode":
        """Create a node instance from a dictionary."""
        inputs = data.get("inputs", {})
        id = data.get("id", None)
        name = data.get("name", None)
        execution_mode = data.get("execution_mode", None)
        return cls(**inputs, id=id, node_name=name, execution_mode=execution_mode)


@Node.register_node_type("tts_eleven_labs")
class TtsElevenLabsNode(Node):
    """


    ## Inputs
    ### Common Inputs
        api_key: The api_key input
        model: The model input
        text: The text input
        voice: The voice input

    ## Outputs
    ### Common Outputs
        audio: The audio output
    """

    # Common inputs and outputs
    _COMMON_INPUTS = [
        {
            "field": "api_key",
            "helper_text": "The api_key input",
            "value": "",
            "type": "string",
        },
        {
            "field": "model",
            "helper_text": "The model input",
            "value": "eleven_multilingual_v2",
            "type": "enum<string>",
        },
        {
            "field": "text",
            "helper_text": "The text input",
            "value": "",
            "type": "string",
        },
        {
            "field": "voice",
            "helper_text": "The voice input",
            "value": "shimmer",
            "type": "enum<string>",
        },
    ]

    # Common outputs and inputs
    _COMMON_OUTPUTS = [{"field": "audio", "helper_text": "The audio output"}]

    # Configuration patterns and their associated inputs/outputs
    _CONFIGS = {}

    # List of parameters that affect configuration
    _PARAMS = []

    def __init__(
        self,
        id: Optional[str] = None,
        node_name: Optional[str] = None,
        execution_mode: Optional[str] = None,
        api_key: str = "",
        model: str = "eleven_multilingual_v2",
        text: str = "",
        voice: str = "shimmer",
        **kwargs
    ):
        # Initialize with params
        params = {}

        super().__init__(
            node_type="tts_eleven_labs",
            params=params,
            id=id,
            node_name=node_name,
            execution_mode=execution_mode,
        )

        # Set input values
        if model is not None:
            self.inputs["model"] = model
        if voice is not None:
            self.inputs["voice"] = voice
        if api_key is not None:
            self.inputs["api_key"] = api_key
        if text is not None:
            self.inputs["text"] = text

        # Update any additional inputs
        if kwargs:
            self.update_inputs(**kwargs)

    @property
    def audio(self) -> Any:
        """
        The audio output


        Raises:
            AttributeError: If this output is not available for the current parameter values
        """
        return self.__getattr__("audio")

    @classmethod
    def from_dict(cls, data: dict) -> "TtsElevenLabsNode":
        """Create a node instance from a dictionary."""
        inputs = data.get("inputs", {})
        id = data.get("id", None)
        name = data.get("name", None)
        execution_mode = data.get("execution_mode", None)
        return cls(**inputs, id=id, node_name=name, execution_mode=execution_mode)


@Node.register_node_type("tts_open_ai")
class TtsOpenAiNode(Node):
    """


    ## Inputs
    ### Common Inputs
        model: The model input
        text: The text input
        use_personal_api_key: The use_personal_api_key input
        voice: The voice input
    ### When use_personal_api_key = True
        api_key: The api_key input

    ## Outputs
    ### Common Outputs
        audio: The audio output
    """

    # Common inputs and outputs
    _COMMON_INPUTS = [
        {
            "field": "model",
            "helper_text": "The model input",
            "value": "tts-1",
            "type": "enum<string>",
        },
        {
            "field": "text",
            "helper_text": "The text input",
            "value": "",
            "type": "string",
        },
        {
            "field": "use_personal_api_key",
            "helper_text": "The use_personal_api_key input",
            "value": False,
            "type": "bool",
        },
        {
            "field": "voice",
            "helper_text": "The voice input",
            "value": "alloy",
            "type": "enum<string>",
        },
    ]

    # Common outputs and inputs
    _COMMON_OUTPUTS = [{"field": "audio", "helper_text": "The audio output"}]

    # Configuration patterns and their associated inputs/outputs
    _CONFIGS = {
        "false": {"inputs": [], "outputs": []},
        "true": {
            "inputs": [{"field": "api_key", "type": "string", "value": ""}],
            "outputs": [],
        },
    }

    # List of parameters that affect configuration
    _PARAMS = ["use_personal_api_key"]

    def __init__(
        self,
        id: Optional[str] = None,
        node_name: Optional[str] = None,
        execution_mode: Optional[str] = None,
        use_personal_api_key: bool = False,
        api_key: str = "",
        model: str = "tts-1",
        text: str = "",
        voice: str = "alloy",
        **kwargs
    ):
        # Initialize with params
        params = {}
        params["use_personal_api_key"] = use_personal_api_key

        super().__init__(
            node_type="tts_open_ai",
            params=params,
            id=id,
            node_name=node_name,
            execution_mode=execution_mode,
        )

        # Set input values
        if model is not None:
            self.inputs["model"] = model
        if voice is not None:
            self.inputs["voice"] = voice
        if text is not None:
            self.inputs["text"] = text
        if use_personal_api_key is not None:
            self.inputs["use_personal_api_key"] = use_personal_api_key
        if api_key is not None:
            self.inputs["api_key"] = api_key

        # Update any additional inputs
        if kwargs:
            self.update_inputs(**kwargs)

    @property
    def audio(self) -> Any:
        """
        The audio output


        Raises:
            AttributeError: If this output is not available for the current parameter values
        """
        return self.__getattr__("audio")

    @classmethod
    def from_dict(cls, data: dict) -> "TtsOpenAiNode":
        """Create a node instance from a dictionary."""
        inputs = data.get("inputs", {})
        id = data.get("id", None)
        name = data.get("name", None)
        execution_mode = data.get("execution_mode", None)
        return cls(**inputs, id=id, node_name=name, execution_mode=execution_mode)


@Node.register_node_type("ai_audio_operations")
class AiAudioOperationsNode(Node):
    """


    ## Inputs
    ### Common Inputs
        sub_type: The sub_type input

    ## Outputs
        None
    """

    # Common inputs and outputs
    _COMMON_INPUTS = [
        {
            "field": "sub_type",
            "helper_text": "The sub_type input",
            "value": "",
            "type": "string",
        }
    ]

    # Common outputs and inputs
    _COMMON_OUTPUTS = []

    # Configuration patterns and their associated inputs/outputs
    _CONFIGS = {}

    # List of parameters that affect configuration
    _PARAMS = []

    def __init__(
        self,
        id: Optional[str] = None,
        node_name: Optional[str] = None,
        execution_mode: Optional[str] = None,
        sub_type: str = "",
        **kwargs
    ):
        # Initialize with params
        params = {}

        super().__init__(
            node_type="ai_audio_operations",
            params=params,
            id=id,
            node_name=node_name,
            execution_mode=execution_mode,
        )

        # Set input values
        if sub_type is not None:
            self.inputs["sub_type"] = sub_type

        # Update any additional inputs
        if kwargs:
            self.update_inputs(**kwargs)

    @classmethod
    def from_dict(cls, data: dict) -> "AiAudioOperationsNode":
        """Create a node instance from a dictionary."""
        inputs = data.get("inputs", {})
        id = data.get("id", None)
        name = data.get("name", None)
        execution_mode = data.get("execution_mode", None)
        return cls(**inputs, id=id, node_name=name, execution_mode=execution_mode)


@Node.register_node_type("ai_text_to_speech")
class AiTextToSpeechNode(Node):
    """
    Generate Audio from text using AI

    ## Inputs
    ### Common Inputs
        model: Select the text-to-speech model
        provider: Select the model provider.
        text: The text for conversion.
        use_personal_api_key: Use your personal API key
        voice: Select the voice
    ### When use_personal_api_key = True
        api_key: Input your personal API key from the model provider. Note: if you do not have access to the selected model, the workflow will not run

    ## Outputs
    ### Common Outputs
        audio: The Text as converted to Audio.
    """

    # Common inputs and outputs
    _COMMON_INPUTS = [
        {
            "field": "model",
            "helper_text": "Select the text-to-speech model",
            "value": "tts-1",
            "type": "enum<string>",
        },
        {
            "field": "provider",
            "helper_text": "Select the model provider.",
            "value": "openai",
            "type": "enum<string>",
        },
        {
            "field": "text",
            "helper_text": "The text for conversion.",
            "value": "",
            "type": "string",
        },
        {
            "field": "use_personal_api_key",
            "helper_text": "Use your personal API key",
            "value": False,
            "type": "bool",
        },
        {
            "field": "voice",
            "helper_text": "Select the voice",
            "value": "alloy",
            "type": "enum<string>",
        },
    ]

    # Common outputs and inputs
    _COMMON_OUTPUTS = [
        {"field": "audio", "helper_text": "The Text as converted to Audio."}
    ]

    # Configuration patterns and their associated inputs/outputs
    _CONFIGS = {
        "false**(*)": {"inputs": [], "outputs": []},
        "true**(*)": {
            "inputs": [
                {
                    "field": "api_key",
                    "type": "string",
                    "value": "",
                    "helper_text": "Input your personal API key from the model provider. Note: if you do not have access to the selected model, the workflow will not run",
                }
            ],
            "outputs": [],
        },
        "(*)**openai": {"inputs": [], "outputs": [], "title": "OpenAI Text to Speech"},
        "(*)**eleven_labs": {
            "inputs": [],
            "outputs": [],
            "title": "Eleven Labs Text to Speech",
        },
    }

    # List of parameters that affect configuration
    _PARAMS = ["use_personal_api_key", "provider"]

    def __init__(
        self,
        id: Optional[str] = None,
        node_name: Optional[str] = None,
        execution_mode: Optional[str] = None,
        use_personal_api_key: bool = False,
        provider: str = "openai",
        api_key: str = "",
        model: str = "tts-1",
        text: str = "",
        voice: str = "alloy",
        **kwargs
    ):
        # Initialize with params
        params = {}
        params["use_personal_api_key"] = use_personal_api_key
        params["provider"] = provider

        super().__init__(
            node_type="ai_text_to_speech",
            params=params,
            id=id,
            node_name=node_name,
            execution_mode=execution_mode,
        )

        # Set input values
        if provider is not None:
            self.inputs["provider"] = provider
        if model is not None:
            self.inputs["model"] = model
        if voice is not None:
            self.inputs["voice"] = voice
        if text is not None:
            self.inputs["text"] = text
        if use_personal_api_key is not None:
            self.inputs["use_personal_api_key"] = use_personal_api_key
        if api_key is not None:
            self.inputs["api_key"] = api_key

        # Update any additional inputs
        if kwargs:
            self.update_inputs(**kwargs)

    @property
    def audio(self) -> Any:
        """
        The Text as converted to Audio.


        Raises:
            AttributeError: If this output is not available for the current parameter values
        """
        return self.__getattr__("audio")

    @classmethod
    def from_dict(cls, data: dict) -> "AiTextToSpeechNode":
        """Create a node instance from a dictionary."""
        inputs = data.get("inputs", {})
        id = data.get("id", None)
        name = data.get("name", None)
        execution_mode = data.get("execution_mode", None)
        return cls(**inputs, id=id, node_name=name, execution_mode=execution_mode)


@Node.register_node_type("ai_speech_to_text")
class AiSpeechToTextNode(Node):
    """
    Generate Text from Audio using AI

    ## Inputs
    ### Common Inputs
        audio: The audio for conversion
        model: Select the speech-to-text model
        provider: Select the model provider.
        use_personal_api_key: Use your personal API key
    ### When use_personal_api_key = True
        api_key: The api_key input
    ### When provider = 'deepgram'
        tier: Select the tier

    ## Outputs
    ### Common Outputs
        text: The Text from the Audio.
    """

    # Common inputs and outputs
    _COMMON_INPUTS = [
        {
            "field": "audio",
            "helper_text": "The audio for conversion",
            "value": "",
            "type": "audio",
        },
        {
            "field": "model",
            "helper_text": "Select the speech-to-text model",
            "value": "whisper-1",
            "type": "enum<string>",
        },
        {
            "field": "provider",
            "helper_text": "Select the model provider.",
            "value": "openai",
            "type": "enum<string>",
        },
        {
            "field": "use_personal_api_key",
            "helper_text": "Use your personal API key",
            "value": False,
            "type": "bool",
        },
    ]

    # Common outputs and inputs
    _COMMON_OUTPUTS = [{"field": "text", "helper_text": "The Text from the Audio."}]

    # Configuration patterns and their associated inputs/outputs
    _CONFIGS = {
        "(*)**openai": {"inputs": [], "outputs": [], "title": "OpenAI Speech to Text"},
        "(*)**deepgram": {
            "inputs": [
                {
                    "field": "tier",
                    "type": "enum<string>",
                    "value": "general",
                    "helper_text": "Select the tier",
                }
            ],
            "outputs": [],
            "title": "Deepgram Speech to Text",
        },
        "false**(*)": {"inputs": [], "outputs": []},
        "true**(*)": {
            "inputs": [{"field": "api_key", "type": "string", "value": ""}],
            "outputs": [],
        },
    }

    # List of parameters that affect configuration
    _PARAMS = ["use_personal_api_key", "provider"]

    def __init__(
        self,
        id: Optional[str] = None,
        node_name: Optional[str] = None,
        execution_mode: Optional[str] = None,
        use_personal_api_key: bool = False,
        provider: str = "openai",
        api_key: str = "",
        audio: Any = None,
        model: str = "whisper-1",
        tier: str = "general",
        **kwargs
    ):
        # Initialize with params
        params = {}
        params["use_personal_api_key"] = use_personal_api_key
        params["provider"] = provider

        super().__init__(
            node_type="ai_speech_to_text",
            params=params,
            id=id,
            node_name=node_name,
            execution_mode=execution_mode,
        )

        # Set input values
        if provider is not None:
            self.inputs["provider"] = provider
        if model is not None:
            self.inputs["model"] = model
        if audio is not None:
            self.inputs["audio"] = audio
        if use_personal_api_key is not None:
            self.inputs["use_personal_api_key"] = use_personal_api_key
        if tier is not None:
            self.inputs["tier"] = tier
        if api_key is not None:
            self.inputs["api_key"] = api_key

        # Update any additional inputs
        if kwargs:
            self.update_inputs(**kwargs)

    @property
    def text(self) -> str:
        """
        The Text from the Audio.


        Raises:
            AttributeError: If this output is not available for the current parameter values
        """
        return self.__getattr__("text")

    @classmethod
    def from_dict(cls, data: dict) -> "AiSpeechToTextNode":
        """Create a node instance from a dictionary."""
        inputs = data.get("inputs", {})
        id = data.get("id", None)
        name = data.get("name", None)
        execution_mode = data.get("execution_mode", None)
        return cls(**inputs, id=id, node_name=name, execution_mode=execution_mode)


@Node.register_node_type("ai_image_operations")
class AiImageOperationsNode(Node):
    """


    ## Inputs
    ### Common Inputs
        sub_type: The sub_type input

    ## Outputs
        None
    """

    # Common inputs and outputs
    _COMMON_INPUTS = [
        {
            "field": "sub_type",
            "helper_text": "The sub_type input",
            "value": "",
            "type": "string",
        }
    ]

    # Common outputs and inputs
    _COMMON_OUTPUTS = []

    # Configuration patterns and their associated inputs/outputs
    _CONFIGS = {}

    # List of parameters that affect configuration
    _PARAMS = []

    def __init__(
        self,
        id: Optional[str] = None,
        node_name: Optional[str] = None,
        execution_mode: Optional[str] = None,
        sub_type: str = "",
        **kwargs
    ):
        # Initialize with params
        params = {}

        super().__init__(
            node_type="ai_image_operations",
            params=params,
            id=id,
            node_name=node_name,
            execution_mode=execution_mode,
        )

        # Set input values
        if sub_type is not None:
            self.inputs["sub_type"] = sub_type

        # Update any additional inputs
        if kwargs:
            self.update_inputs(**kwargs)

    @classmethod
    def from_dict(cls, data: dict) -> "AiImageOperationsNode":
        """Create a node instance from a dictionary."""
        inputs = data.get("inputs", {})
        id = data.get("id", None)
        name = data.get("name", None)
        execution_mode = data.get("execution_mode", None)
        return cls(**inputs, id=id, node_name=name, execution_mode=execution_mode)


@Node.register_node_type("ai_image_to_text")
class AiImageToTextNode(Node):
    """
    Generate Text from Image using AI

    ## Inputs
    ### Common Inputs
        image: The image for conversion
        json_response: Return the response as a JSON object
        max_tokens: The maximum number of tokens to generate
        model: Select the image-to-text model
        prompt: The data that is sent to the LLM. Add data from other nodes with double curly braces, e.g., {{input1}}
        provider: Select the model provider.
        stream: Stream the response
        system: Tell the AI model how you would like it to respond. Be as specific as possible. For example, you can instruct the model on what tone to respond in or how to respond given the information you provide
        temperature: The temperature of the model
        top_p: The top-p value
        use_personal_api_key: Use your personal API key
    ### When use_personal_api_key = True
        api_key: Input your personal API key from the model provider. Note: if you do not have access to the selected model, the workflow will not run
    ### When json_response = True
        json_schema: The JSON schema to use for the response

    ## Outputs
    ### Common Outputs
        tokens_used: The number of tokens used
    ### When stream = False
        text: The Text from the Image.
    ### When stream = True
        text: Stream of text generated from the Image.
    """

    # Common inputs and outputs
    _COMMON_INPUTS = [
        {
            "field": "image",
            "helper_text": "The image for conversion",
            "value": None,
            "type": "image",
        },
        {
            "field": "json_response",
            "helper_text": "Return the response as a JSON object",
            "value": False,
            "type": "bool",
        },
        {
            "field": "max_tokens",
            "helper_text": "The maximum number of tokens to generate",
            "value": 128000,
            "type": "int32",
        },
        {
            "field": "model",
            "helper_text": "Select the image-to-text model",
            "value": "chatgpt-4o-latest",
            "type": "enum<string>",
        },
        {
            "field": "prompt",
            "helper_text": "The data that is sent to the LLM. Add data from other nodes with double curly braces, e.g., {{input1}}",
            "value": "",
            "type": "string",
        },
        {
            "field": "provider",
            "helper_text": "Select the model provider.",
            "value": "openai",
            "type": "enum<string>",
        },
        {
            "field": "stream",
            "helper_text": "Stream the response",
            "value": False,
            "type": "bool",
        },
        {
            "field": "system",
            "helper_text": "Tell the AI model how you would like it to respond. Be as specific as possible. For example, you can instruct the model on what tone to respond in or how to respond given the information you provide",
            "value": "",
            "type": "string",
        },
        {
            "field": "temperature",
            "helper_text": "The temperature of the model",
            "value": 0.7,
            "type": "float",
        },
        {
            "field": "top_p",
            "helper_text": "The top-p value",
            "value": 0.9,
            "type": "float",
        },
        {
            "field": "use_personal_api_key",
            "helper_text": "Use your personal API key",
            "value": False,
            "type": "bool",
        },
    ]

    # Common outputs and inputs
    _COMMON_OUTPUTS = [
        {"field": "tokens_used", "helper_text": "The number of tokens used"}
    ]

    # Configuration patterns and their associated inputs/outputs
    _CONFIGS = {
        "false**(*)**(*)**(*)": {"inputs": [], "outputs": []},
        "true**(*)**(*)**(*)": {
            "inputs": [
                {
                    "field": "api_key",
                    "type": "string",
                    "value": "",
                    "helper_text": "Input your personal API key from the model provider. Note: if you do not have access to the selected model, the workflow will not run",
                }
            ],
            "outputs": [],
        },
        "(*)**false**(*)**(*)": {"inputs": [], "outputs": []},
        "(*)**true**(*)**(*)": {
            "inputs": [
                {
                    "field": "json_schema",
                    "type": "string",
                    "value": "",
                    "helper_text": "The JSON schema to use for the response",
                }
            ],
            "outputs": [],
        },
        "(*)**(*)**false**(*)": {
            "inputs": [],
            "outputs": [
                {
                    "field": "text",
                    "type": "string",
                    "helper_text": "The Text from the Image.",
                }
            ],
        },
        "(*)**(*)**true**(*)": {
            "inputs": [],
            "outputs": [
                {
                    "field": "text",
                    "type": "stream<string>",
                    "helper_text": "Stream of text generated from the Image.",
                }
            ],
        },
        "(*)**(*)**(*)**openai": {
            "inputs": [],
            "outputs": [],
            "title": "OpenAI Image to Text",
        },
        "(*)**(*)**(*)**anthropic": {
            "inputs": [],
            "outputs": [],
            "title": "Anthropic Image to Text",
        },
        "(*)**(*)**(*)**google": {
            "inputs": [],
            "outputs": [],
            "title": "Google Image to Text",
        },
        "(*)**(*)**(*)**xai": {
            "inputs": [],
            "outputs": [],
            "title": "XAI Image to Text",
        },
    }

    # List of parameters that affect configuration
    _PARAMS = ["use_personal_api_key", "json_response", "stream", "provider"]

    def __init__(
        self,
        id: Optional[str] = None,
        node_name: Optional[str] = None,
        execution_mode: Optional[str] = None,
        use_personal_api_key: bool = False,
        json_response: bool = False,
        stream: bool = False,
        provider: str = "openai",
        api_key: str = "",
        image: Optional[Any] = None,
        json_schema: str = "",
        max_tokens: int = 128000,
        model: str = "chatgpt-4o-latest",
        prompt: str = "",
        system: str = "",
        temperature: Any = 0.7,
        top_p: Any = 0.9,
        **kwargs
    ):
        # Initialize with params
        params = {}
        params["use_personal_api_key"] = use_personal_api_key
        params["json_response"] = json_response
        params["stream"] = stream
        params["provider"] = provider

        super().__init__(
            node_type="ai_image_to_text",
            params=params,
            id=id,
            node_name=node_name,
            execution_mode=execution_mode,
        )

        # Set input values
        if provider is not None:
            self.inputs["provider"] = provider
        if model is not None:
            self.inputs["model"] = model
        if system is not None:
            self.inputs["system"] = system
        if prompt is not None:
            self.inputs["prompt"] = prompt
        if image is not None:
            self.inputs["image"] = image
        if use_personal_api_key is not None:
            self.inputs["use_personal_api_key"] = use_personal_api_key
        if json_response is not None:
            self.inputs["json_response"] = json_response
        if max_tokens is not None:
            self.inputs["max_tokens"] = max_tokens
        if temperature is not None:
            self.inputs["temperature"] = temperature
        if top_p is not None:
            self.inputs["top_p"] = top_p
        if stream is not None:
            self.inputs["stream"] = stream
        if api_key is not None:
            self.inputs["api_key"] = api_key
        if json_schema is not None:
            self.inputs["json_schema"] = json_schema

        # Update any additional inputs
        if kwargs:
            self.update_inputs(**kwargs)

    @property
    def text(self) -> str:
        """
        The Text from the Image.

        Different behavior based on configuration:
          - The Text from the Image. (When stream = False)
          - Stream of text generated from the Image. (When stream = True)


        Raises:
            AttributeError: If this output is not available for the current parameter values
        """
        return self.__getattr__("text")

    @property
    def tokens_used(self) -> int:
        """
        The number of tokens used


        Raises:
            AttributeError: If this output is not available for the current parameter values
        """
        return self.__getattr__("tokens_used")

    @classmethod
    def from_dict(cls, data: dict) -> "AiImageToTextNode":
        """Create a node instance from a dictionary."""
        inputs = data.get("inputs", {})
        id = data.get("id", None)
        name = data.get("name", None)
        execution_mode = data.get("execution_mode", None)
        return cls(**inputs, id=id, node_name=name, execution_mode=execution_mode)


@Node.register_node_type("ai_text_to_image")
class AiTextToImageNode(Node):
    """
    Generate Image from Text using AI

    ## Inputs
    ### Common Inputs
        aspect_ratio: Select the aspect ratio.
        model: Select the text-to-image model
        prompt: Tell the AI model how you would like it to respond. Be as specific as possible. For example, you can instruct the model to use bright colors.
        provider: Select the model provider.
        size: Select the size.
        use_personal_api_key: Use your personal API key
    ### When use_personal_api_key = True
        api_key: Input your personal API key from the model provider. Note: if you do not have access to the selected model, the workflow will not run

    ## Outputs
    ### Common Outputs
        image: The Image(s) generated from the Text.
    """

    # Common inputs and outputs
    _COMMON_INPUTS = [
        {
            "field": "aspect_ratio",
            "helper_text": "Select the aspect ratio.",
            "value": "1:1",
            "type": "enum<string>",
        },
        {
            "field": "model",
            "helper_text": "Select the text-to-image model",
            "value": "dall-e-2",
            "type": "enum<string>",
        },
        {
            "field": "prompt",
            "helper_text": "Tell the AI model how you would like it to respond. Be as specific as possible. For example, you can instruct the model to use bright colors.",
            "value": "",
            "type": "string",
        },
        {
            "field": "provider",
            "helper_text": "Select the model provider.",
            "value": "openai",
            "type": "enum<string>",
        },
        {
            "field": "size",
            "helper_text": "Select the size.",
            "value": "512x512",
            "type": "enum<string>",
        },
        {
            "field": "use_personal_api_key",
            "helper_text": "Use your personal API key",
            "value": False,
            "type": "bool",
        },
    ]

    # Common outputs and inputs
    _COMMON_OUTPUTS = [
        {"field": "image", "helper_text": "The Image(s) generated from the Text."}
    ]

    # Configuration patterns and their associated inputs/outputs
    _CONFIGS = {
        "false**(*)": {"inputs": [], "outputs": []},
        "true**(*)": {
            "inputs": [
                {
                    "field": "api_key",
                    "type": "string",
                    "value": "",
                    "helper_text": "Input your personal API key from the model provider. Note: if you do not have access to the selected model, the workflow will not run",
                }
            ],
            "outputs": [],
        },
        "(*)**openai": {"inputs": [], "outputs": [], "title": "OpenAI Text to Image"},
        "(*)**stabilityai": {
            "inputs": [],
            "outputs": [],
            "title": "Stability AI Text to Image",
        },
        "(*)**flux": {"inputs": [], "outputs": [], "title": "Flux Text to Image"},
    }

    # List of parameters that affect configuration
    _PARAMS = ["use_personal_api_key", "provider"]

    def __init__(
        self,
        id: Optional[str] = None,
        node_name: Optional[str] = None,
        execution_mode: Optional[str] = None,
        use_personal_api_key: bool = False,
        provider: str = "openai",
        api_key: str = "",
        aspect_ratio: str = "1:1",
        model: str = "dall-e-2",
        prompt: str = "",
        size: str = "512x512",
        **kwargs
    ):
        # Initialize with params
        params = {}
        params["use_personal_api_key"] = use_personal_api_key
        params["provider"] = provider

        super().__init__(
            node_type="ai_text_to_image",
            params=params,
            id=id,
            node_name=node_name,
            execution_mode=execution_mode,
        )

        # Set input values
        if provider is not None:
            self.inputs["provider"] = provider
        if model is not None:
            self.inputs["model"] = model
        if prompt is not None:
            self.inputs["prompt"] = prompt
        if size is not None:
            self.inputs["size"] = size
        if aspect_ratio is not None:
            self.inputs["aspect_ratio"] = aspect_ratio
        if use_personal_api_key is not None:
            self.inputs["use_personal_api_key"] = use_personal_api_key
        if api_key is not None:
            self.inputs["api_key"] = api_key

        # Update any additional inputs
        if kwargs:
            self.update_inputs(**kwargs)

    @property
    def image(self) -> Any:
        """
        The Image(s) generated from the Text.


        Raises:
            AttributeError: If this output is not available for the current parameter values
        """
        return self.__getattr__("image")

    @classmethod
    def from_dict(cls, data: dict) -> "AiTextToImageNode":
        """Create a node instance from a dictionary."""
        inputs = data.get("inputs", {})
        id = data.get("id", None)
        name = data.get("name", None)
        execution_mode = data.get("execution_mode", None)
        return cls(**inputs, id=id, node_name=name, execution_mode=execution_mode)


@Node.register_node_type("llm_anthropic_vision")
class LlmAnthropicVisionNode(Node):
    """


    ## Inputs
    ### Common Inputs
        image: The image input
        json_response: The json_response input
        max_tokens: The max_tokens input
        model: The model input
        prompt: The prompt input
        system: The system input
        temperature: The temperature input
        top_p: The top_p input
        use_personal_api_key: The use_personal_api_key input
    ### When use_personal_api_key = True
        api_key: The api_key input
    ### When json_response = True
        json_schema: The json_schema input

    ## Outputs
    ### Common Outputs
        response: The response output
    """

    # Common inputs and outputs
    _COMMON_INPUTS = [
        {
            "field": "image",
            "helper_text": "The image input",
            "value": None,
            "type": "image",
        },
        {
            "field": "json_response",
            "helper_text": "The json_response input",
            "value": False,
            "type": "bool",
        },
        {
            "field": "max_tokens",
            "helper_text": "The max_tokens input",
            "value": 200000,
            "type": "int32",
        },
        {
            "field": "model",
            "helper_text": "The model input",
            "value": "claude-3-haiku-20240307",
            "type": "enum<string>",
        },
        {
            "field": "prompt",
            "helper_text": "The prompt input",
            "value": "",
            "type": "string",
        },
        {
            "field": "system",
            "helper_text": "The system input",
            "value": "",
            "type": "string",
        },
        {
            "field": "temperature",
            "helper_text": "The temperature input",
            "value": 0.7,
            "type": "float",
        },
        {
            "field": "top_p",
            "helper_text": "The top_p input",
            "value": 0.9,
            "type": "float",
        },
        {
            "field": "use_personal_api_key",
            "helper_text": "The use_personal_api_key input",
            "value": False,
            "type": "bool",
        },
    ]

    # Common outputs and inputs
    _COMMON_OUTPUTS = [{"field": "response", "helper_text": "The response output"}]

    # Configuration patterns and their associated inputs/outputs
    _CONFIGS = {
        "false**(*)": {"inputs": [], "outputs": []},
        "true**(*)": {
            "inputs": [{"field": "api_key", "type": "string", "value": ""}],
            "outputs": [],
        },
        "(*)**false": {"inputs": [], "outputs": []},
        "(*)**true": {
            "inputs": [{"field": "json_schema", "type": "string", "value": ""}],
            "outputs": [],
        },
    }

    # List of parameters that affect configuration
    _PARAMS = ["use_personal_api_key", "json_response"]

    def __init__(
        self,
        id: Optional[str] = None,
        node_name: Optional[str] = None,
        execution_mode: Optional[str] = None,
        use_personal_api_key: bool = False,
        json_response: bool = False,
        api_key: str = "",
        image: Optional[Any] = None,
        json_schema: str = "",
        max_tokens: int = 200000,
        model: str = "claude-3-haiku-20240307",
        prompt: str = "",
        system: str = "",
        temperature: Any = 0.7,
        top_p: Any = 0.9,
        **kwargs
    ):
        # Initialize with params
        params = {}
        params["use_personal_api_key"] = use_personal_api_key
        params["json_response"] = json_response

        super().__init__(
            node_type="llm_anthropic_vision",
            params=params,
            id=id,
            node_name=node_name,
            execution_mode=execution_mode,
        )

        # Set input values
        if system is not None:
            self.inputs["system"] = system
        if prompt is not None:
            self.inputs["prompt"] = prompt
        if image is not None:
            self.inputs["image"] = image
        if model is not None:
            self.inputs["model"] = model
        if use_personal_api_key is not None:
            self.inputs["use_personal_api_key"] = use_personal_api_key
        if json_response is not None:
            self.inputs["json_response"] = json_response
        if max_tokens is not None:
            self.inputs["max_tokens"] = max_tokens
        if temperature is not None:
            self.inputs["temperature"] = temperature
        if top_p is not None:
            self.inputs["top_p"] = top_p
        if api_key is not None:
            self.inputs["api_key"] = api_key
        if json_schema is not None:
            self.inputs["json_schema"] = json_schema

        # Update any additional inputs
        if kwargs:
            self.update_inputs(**kwargs)

    @property
    def response(self) -> str:
        """
        The response output


        Raises:
            AttributeError: If this output is not available for the current parameter values
        """
        return self.__getattr__("response")

    @classmethod
    def from_dict(cls, data: dict) -> "LlmAnthropicVisionNode":
        """Create a node instance from a dictionary."""
        inputs = data.get("inputs", {})
        id = data.get("id", None)
        name = data.get("name", None)
        execution_mode = data.get("execution_mode", None)
        return cls(**inputs, id=id, node_name=name, execution_mode=execution_mode)


@Node.register_node_type("semantic_search")
class SemanticSearchNode(Node):
    """
    Generate a temporary vector database at run-time and retrieve the most relevant pieces from the documents based on the query.

    ## Inputs
    ### Common Inputs
        alpha: The alpha value for the retrieval
        analyze_documents: To analyze document contents and enrich them when parsing
        answer_multiple_questions: Extract separate questions from the query and retrieve content separately for each question to improve search performance
        do_advanced_qa: Use additional LLM calls to analyze each document to improve answer correctness
        do_nl_metadata_query: Do a natural language metadata query
        documents: The text for semantic search. Note: you may add multiple upstream nodes to this field.
        enable_context: Additional context passed to advanced search and query analysis
        enable_document_db_filter: Filter the documents returned from the knowledge base
        enable_filter: Filter the content returned from the knowledge base
        expand_query: Expand query to improve semantic search
        expand_query_terms: Expand query terms to improve semantic search
        format_context_for_llm: Format the context for the LLM
        is_hybrid: Whether to create a hybrid knowledge base
        max_docs_per_query: The maximum number of relevant chunks to be returned
        model: The model to use for the embedding
        query: The query will be used to search documents for relevant pieces semantically.
        rerank_documents: Refine the initial ranking of returned chunks based on relevancy
        retrieval_unit: The unit of retrieval
        score_cutoff: The score cutoff
        segmentation_method: The method to break text into units before chunking. 'words': splits by word; 'sentences': splits by sentence boundary; 'paragraphs': splits by blank line/paragraph.
        show_intermediate_steps: Show intermediate steps
        splitter_method: Strategy for grouping segmented text into final chunks. 'sentence': groups sentences; 'markdown': respects Markdown structure (headers, code); 'dynamic': optimizes breaks for size using chosen segmentation method.
        transform_query: Transform the query for better semantic search
    ### When do_advanced_qa = True
        advanced_search_mode: The mode to use for the advanced search
        qa_model_name: The model to use for the QA
    ### When enable_context = True
        context: Additional context to pass to the query analysis and qa steps
    ### When enable_document_db_filter = True
        document_db_filter: Filter the documents returned from the knowledge base
    ### When enable_filter = True
        filter: Filter the content returned from the knowledge base
    ### When rerank_documents = True
        rerank_model: Refine the initial ranking of returned chunks based on relevancy

    ## Outputs
    ### When do_advanced_qa = False and retrieval_unit = 'chunks' and format_context_for_llm = False
        chunks: Semantically similar chunks retrieved from the knowledge base
    ### When do_advanced_qa = False and retrieval_unit = 'chunks' and format_context_for_llm = True
        chunks: Semantically similar chunks retrieved from the knowledge base
        formatted_text: Knowledge base outputs formatted for input to a LLM
    ### When do_advanced_qa = True
        citation_metadata: Citation metadata for semantic search outputs, used for showing sources in LLM responses
        response: The response from the semantic search
    ### When do_advanced_qa = False and retrieval_unit = 'documents' and format_context_for_llm = False
        documents: Semantically similar documents retrieved from the knowledge base
    ### When do_advanced_qa = False and retrieval_unit = 'documents' and format_context_for_llm = True
        documents: Semantically similar documents retrieved from the knowledge base
        formatted_text: Knowledge base outputs formatted for input to a LLM
    """

    # Common inputs and outputs
    _COMMON_INPUTS = [
        {
            "field": "alpha",
            "helper_text": "The alpha value for the retrieval",
            "value": 0.5,
            "type": "float",
        },
        {
            "field": "analyze_documents",
            "helper_text": "To analyze document contents and enrich them when parsing",
            "value": False,
            "type": "bool",
        },
        {
            "field": "answer_multiple_questions",
            "helper_text": "Extract separate questions from the query and retrieve content separately for each question to improve search performance",
            "value": False,
            "type": "bool",
        },
        {
            "field": "do_advanced_qa",
            "helper_text": "Use additional LLM calls to analyze each document to improve answer correctness",
            "value": False,
            "type": "bool",
        },
        {
            "field": "do_nl_metadata_query",
            "helper_text": "Do a natural language metadata query",
            "value": False,
            "type": "bool",
        },
        {
            "field": "documents",
            "helper_text": "The text for semantic search. Note: you may add multiple upstream nodes to this field.",
            "value": [],
            "type": "string",
        },
        {
            "field": "enable_context",
            "helper_text": "Additional context passed to advanced search and query analysis",
            "value": False,
            "type": "bool",
        },
        {
            "field": "enable_document_db_filter",
            "helper_text": "Filter the documents returned from the knowledge base",
            "value": False,
            "type": "bool",
        },
        {
            "field": "enable_filter",
            "helper_text": "Filter the content returned from the knowledge base",
            "value": False,
            "type": "bool",
        },
        {
            "field": "expand_query",
            "helper_text": "Expand query to improve semantic search",
            "value": False,
            "type": "bool",
        },
        {
            "field": "expand_query_terms",
            "helper_text": "Expand query terms to improve semantic search",
            "value": False,
            "type": "bool",
        },
        {
            "field": "format_context_for_llm",
            "helper_text": "Format the context for the LLM",
            "value": False,
            "type": "bool",
        },
        {
            "field": "is_hybrid",
            "helper_text": "Whether to create a hybrid knowledge base",
            "value": False,
            "type": "bool",
        },
        {
            "field": "max_docs_per_query",
            "helper_text": "The maximum number of relevant chunks to be returned",
            "value": 5,
            "type": "int32",
        },
        {
            "field": "model",
            "helper_text": "The model to use for the embedding",
            "value": "openai/text-embedding-3-small",
            "type": "enum<string>",
        },
        {
            "field": "query",
            "helper_text": "The query will be used to search documents for relevant pieces semantically.",
            "value": "",
            "type": "string",
        },
        {
            "field": "rerank_documents",
            "helper_text": "Refine the initial ranking of returned chunks based on relevancy",
            "value": False,
            "type": "bool",
        },
        {
            "field": "retrieval_unit",
            "helper_text": "The unit of retrieval",
            "value": "chunks",
            "type": "enum<string>",
        },
        {
            "field": "score_cutoff",
            "helper_text": "The score cutoff",
            "value": 0,
            "type": "float",
        },
        {
            "field": "segmentation_method",
            "helper_text": "The method to break text into units before chunking. 'words': splits by word; 'sentences': splits by sentence boundary; 'paragraphs': splits by blank line/paragraph.",
            "value": "words",
            "type": "enum<string>",
        },
        {
            "field": "show_intermediate_steps",
            "helper_text": "Show intermediate steps",
            "value": False,
            "type": "bool",
        },
        {
            "field": "splitter_method",
            "helper_text": "Strategy for grouping segmented text into final chunks. 'sentence': groups sentences; 'markdown': respects Markdown structure (headers, code); 'dynamic': optimizes breaks for size using chosen segmentation method.",
            "value": "markdown",
            "type": "enum<string>",
        },
        {
            "field": "transform_query",
            "helper_text": "Transform the query for better semantic search",
            "value": False,
            "type": "bool",
        },
    ]

    # Common outputs and inputs
    _COMMON_OUTPUTS = []

    # Configuration patterns and their associated inputs/outputs
    _CONFIGS = {
        "true**(*)**(*)**(*)**(*)**(*)**(*)**(*)": {
            "inputs": [
                {
                    "field": "qa_model_name",
                    "type": "enum<string>",
                    "value": "gpt-4o-mini",
                    "helper_text": "The model to use for the QA",
                },
                {
                    "field": "advanced_search_mode",
                    "type": "enum<string>",
                    "value": "accurate",
                    "helper_text": "The mode to use for the advanced search",
                },
            ],
            "outputs": [
                {
                    "field": "response",
                    "type": "string",
                    "helper_text": "The response from the semantic search",
                },
                {
                    "field": "citation_metadata",
                    "type": "vec<string>",
                    "helper_text": "Citation metadata for semantic search outputs, used for showing sources in LLM responses",
                },
            ],
        },
        "(*)**true**(*)**(*)**(*)**(*)**(*)**(*)": {
            "inputs": [
                {
                    "field": "filter",
                    "type": "string",
                    "value": "",
                    "helper_text": "Filter the content returned from the knowledge base",
                }
            ],
            "outputs": [],
        },
        "(*)**(*)**true**(*)**(*)**(*)**(*)**(*)": {
            "inputs": [
                {
                    "field": "rerank_model",
                    "type": "enum<string>",
                    "value": "cohere/rerank-english-v3.0",
                    "helper_text": "Refine the initial ranking of returned chunks based on relevancy",
                }
            ],
            "outputs": [],
        },
        "false**(*)**(*)**documents**(*)**false**(*)**(*)": {
            "inputs": [],
            "outputs": [
                {
                    "field": "documents",
                    "type": "vec<string>",
                    "helper_text": "Semantically similar documents retrieved from the knowledge base",
                }
            ],
        },
        "false**(*)**(*)**chunks**(*)**false**(*)**(*)": {
            "inputs": [],
            "outputs": [
                {
                    "field": "chunks",
                    "type": "vec<string>",
                    "helper_text": "Semantically similar chunks retrieved from the knowledge base",
                }
            ],
        },
        "false**(*)**(*)**documents**(*)**true**(*)**(*)": {
            "inputs": [],
            "outputs": [
                {
                    "field": "documents",
                    "type": "vec<string>",
                    "helper_text": "Semantically similar documents retrieved from the knowledge base",
                },
                {
                    "field": "formatted_text",
                    "type": "string",
                    "helper_text": "Knowledge base outputs formatted for input to a LLM",
                },
            ],
        },
        "false**(*)**(*)**chunks**(*)**true**(*)**(*)": {
            "inputs": [],
            "outputs": [
                {
                    "field": "chunks",
                    "type": "vec<string>",
                    "helper_text": "Semantically similar chunks retrieved from the knowledge base",
                },
                {
                    "field": "formatted_text",
                    "type": "string",
                    "helper_text": "Knowledge base outputs formatted for input to a LLM",
                },
            ],
        },
        "(*)**(*)**(*)**(*)**true**(*)**(*)**(*)": {
            "inputs": [
                {
                    "field": "context",
                    "type": "string",
                    "value": "",
                    "helper_text": "Additional context to pass to the query analysis and qa steps",
                }
            ],
            "outputs": [],
        },
        "(*)**(*)**(*)**(*)**(*)**(*)**true**(*)": {
            "inputs": [
                {
                    "field": "document_db_filter",
                    "type": "string",
                    "value": "",
                    "helper_text": "Filter the documents returned from the knowledge base",
                }
            ],
            "outputs": [],
        },
        "(*)**(*)**(*)**(*)**(*)**(*)**(*)**(dynamic)": {
            "inputs": [
                {
                    "field": "segmentation_method",
                    "type": "enum<string>",
                    "value": "words",
                    "helper_text": "The method to break text into units before chunking. 'words': splits by word; 'sentences': splits by sentence boundary; 'paragraphs': splits by blank line/paragraph.",
                }
            ],
            "outputs": [],
        },
    }

    # List of parameters that affect configuration
    _PARAMS = [
        "do_advanced_qa",
        "enable_filter",
        "rerank_documents",
        "retrieval_unit",
        "enable_context",
        "format_context_for_llm",
        "enable_document_db_filter",
        "splitter_method",
    ]

    def __init__(
        self,
        id: Optional[str] = None,
        node_name: Optional[str] = None,
        execution_mode: Optional[str] = None,
        do_advanced_qa: bool = False,
        enable_filter: bool = False,
        rerank_documents: bool = False,
        retrieval_unit: str = "chunks",
        enable_context: bool = False,
        format_context_for_llm: bool = False,
        enable_document_db_filter: bool = False,
        splitter_method: str = "markdown",
        advanced_search_mode: str = "accurate",
        alpha: Any = 0.5,
        analyze_documents: bool = False,
        answer_multiple_questions: bool = False,
        context: str = "",
        do_nl_metadata_query: bool = False,
        document_db_filter: str = "",
        documents: str = "[]",
        expand_query: bool = False,
        expand_query_terms: bool = False,
        filter: str = "",
        is_hybrid: bool = False,
        max_docs_per_query: int = 5,
        model: str = "openai/text-embedding-3-small",
        qa_model_name: str = "gpt-4o-mini",
        query: str = "",
        rerank_model: str = "cohere/rerank-english-v3.0",
        score_cutoff: Any = 0,
        segmentation_method: str = "words",
        show_intermediate_steps: bool = False,
        transform_query: bool = False,
        **kwargs
    ):
        # Initialize with params
        params = {}
        params["do_advanced_qa"] = do_advanced_qa
        params["enable_filter"] = enable_filter
        params["rerank_documents"] = rerank_documents
        params["retrieval_unit"] = retrieval_unit
        params["enable_context"] = enable_context
        params["format_context_for_llm"] = format_context_for_llm
        params["enable_document_db_filter"] = enable_document_db_filter
        params["splitter_method"] = splitter_method

        super().__init__(
            node_type="semantic_search",
            params=params,
            id=id,
            node_name=node_name,
            execution_mode=execution_mode,
        )

        # Set input values
        if model is not None:
            self.inputs["model"] = model
        if query is not None:
            self.inputs["query"] = query
        if max_docs_per_query is not None:
            self.inputs["max_docs_per_query"] = max_docs_per_query
        if rerank_documents is not None:
            self.inputs["rerank_documents"] = rerank_documents
        if documents is not None:
            self.inputs["documents"] = documents
        if enable_filter is not None:
            self.inputs["enable_filter"] = enable_filter
        if do_nl_metadata_query is not None:
            self.inputs["do_nl_metadata_query"] = do_nl_metadata_query
        if retrieval_unit is not None:
            self.inputs["retrieval_unit"] = retrieval_unit
        if alpha is not None:
            self.inputs["alpha"] = alpha
        if transform_query is not None:
            self.inputs["transform_query"] = transform_query
        if answer_multiple_questions is not None:
            self.inputs["answer_multiple_questions"] = answer_multiple_questions
        if expand_query is not None:
            self.inputs["expand_query"] = expand_query
        if expand_query_terms is not None:
            self.inputs["expand_query_terms"] = expand_query_terms
        if do_advanced_qa is not None:
            self.inputs["do_advanced_qa"] = do_advanced_qa
        if show_intermediate_steps is not None:
            self.inputs["show_intermediate_steps"] = show_intermediate_steps
        if score_cutoff is not None:
            self.inputs["score_cutoff"] = score_cutoff
        if enable_context is not None:
            self.inputs["enable_context"] = enable_context
        if format_context_for_llm is not None:
            self.inputs["format_context_for_llm"] = format_context_for_llm
        if enable_document_db_filter is not None:
            self.inputs["enable_document_db_filter"] = enable_document_db_filter
        if analyze_documents is not None:
            self.inputs["analyze_documents"] = analyze_documents
        if is_hybrid is not None:
            self.inputs["is_hybrid"] = is_hybrid
        if splitter_method is not None:
            self.inputs["splitter_method"] = splitter_method
        if segmentation_method is not None:
            self.inputs["segmentation_method"] = segmentation_method
        if qa_model_name is not None:
            self.inputs["qa_model_name"] = qa_model_name
        if advanced_search_mode is not None:
            self.inputs["advanced_search_mode"] = advanced_search_mode
        if filter is not None:
            self.inputs["filter"] = filter
        if rerank_model is not None:
            self.inputs["rerank_model"] = rerank_model
        if context is not None:
            self.inputs["context"] = context
        if document_db_filter is not None:
            self.inputs["document_db_filter"] = document_db_filter

        # Update any additional inputs
        if kwargs:
            self.update_inputs(**kwargs)

    @property
    def chunks(self) -> List[str]:
        """
        Semantically similar chunks retrieved from the knowledge base

        Available: When do_advanced_qa = False and retrieval_unit = 'chunks' and format_context_for_llm = False, When do_advanced_qa = False and retrieval_unit = 'chunks' and format_context_for_llm = True


        Raises:
            AttributeError: If this output is not available for the current parameter values
        """
        return self.__getattr__("chunks")

    @property
    def citation_metadata(self) -> List[str]:
        """
        Citation metadata for semantic search outputs, used for showing sources in LLM responses

        Available: When do_advanced_qa = True


        Raises:
            AttributeError: If this output is not available for the current parameter values
        """
        return self.__getattr__("citation_metadata")

    @property
    def documents(self) -> List[str]:
        """
        Semantically similar documents retrieved from the knowledge base

        Available: When do_advanced_qa = False and retrieval_unit = 'documents' and format_context_for_llm = False, When do_advanced_qa = False and retrieval_unit = 'documents' and format_context_for_llm = True


        Raises:
            AttributeError: If this output is not available for the current parameter values
        """
        return self.__getattr__("documents")

    @property
    def formatted_text(self) -> str:
        """
        Knowledge base outputs formatted for input to a LLM

        Available: When do_advanced_qa = False and retrieval_unit = 'documents' and format_context_for_llm = True, When do_advanced_qa = False and retrieval_unit = 'chunks' and format_context_for_llm = True


        Raises:
            AttributeError: If this output is not available for the current parameter values
        """
        return self.__getattr__("formatted_text")

    @property
    def response(self) -> str:
        """
        The response from the semantic search

        Available: When do_advanced_qa = True


        Raises:
            AttributeError: If this output is not available for the current parameter values
        """
        return self.__getattr__("response")

    @classmethod
    def from_dict(cls, data: dict) -> "SemanticSearchNode":
        """Create a node instance from a dictionary."""
        inputs = data.get("inputs", {})
        id = data.get("id", None)
        name = data.get("name", None)
        execution_mode = data.get("execution_mode", None)
        return cls(**inputs, id=id, node_name=name, execution_mode=execution_mode)


@Node.register_node_type("knowledge_base")
class KnowledgeBaseNode(Node):
    """
    Semantically query a knowledge base that can contain files, scraped URLs, and data from synced integrations (e.g., Google Drive).

    ## Inputs
    ### Common Inputs
        alpha: The alpha value for the retrieval
        answer_multiple_questions: Extract separate questions from the query and retrieve content separately for each question to improve search performance
        do_advanced_qa: Use additional LLM calls to analyze each document to improve answer correctness
        do_nl_metadata_query: Do a natural language metadata query
        enable_context: Enable context
        enable_document_db_filter: Enable the document DB filter
        enable_filter: Filter the content returned from the knowledge base
        expand_query: Expand query to improve semantic search
        expand_query_terms: Expand query terms to improve semantic search
        format_context_for_llm: Format the context for the LLM
        knowledge_base: Select an existing knowledge base
        max_docs_per_query: The number of relevant chunks to be returned
        query: The query will be used to search documents for relevant pieces semantically.
        rerank_documents: Rerank the documents returned from the knowledge base
        retrieval_unit: The unit of retrieval
        score_cutoff: The score cutoff
        show_intermediate_steps: Show intermediate steps
        transform_query: Transform the query for better semantic search
    ### When do_advanced_qa = True
        advanced_search_mode: The mode to use for the advanced search
        qa_model_name: The model to use for the QA
    ### When enable_context = True
        context: Additional context to pass to the query analysis and qa steps
    ### When enable_document_db_filter = True
        document_db_filter: Filter the documents returned from the knowledge base
    ### When enable_filter = True
        filter: Filter the content returned from the knowledge base
    ### When rerank_documents = True
        rerank_model: Refine the initial ranking of returned chunks based on relevancy

    ## Outputs
    ### When do_advanced_qa = False and retrieval_unit = 'chunks' and format_context_for_llm = False
        chunks: Semantically similar chunks retrieved from the knowledge base.
        citation_metadata: Citation metadata for knowledge base outputs, used for showing sources in LLM responses
    ### When do_advanced_qa = False and retrieval_unit = 'chunks' and format_context_for_llm = True
        chunks: Semantically similar chunks retrieved from the knowledge base.
        citation_metadata: Citation metadata for knowledge base outputs, used for showing sources in LLM responses
        formatted_text: Knowledge base outputs formatted for input to a LLM
    ### When do_advanced_qa = True
        citation_metadata: Citation metadata for knowledge base outputs, used for showing sources in LLM responses
        response: The response from the knowledge base
    ### When enable_filter = True
        citation_metadata: Citation metadata for knowledge base outputs, used for showing sources in LLM responses
    ### When do_advanced_qa = False and retrieval_unit = 'documents' and format_context_for_llm = False
        citation_metadata: Citation metadata for knowledge base outputs, used for showing sources in LLM responses
        documents: The documents returned from the knowledge base
    ### When do_advanced_qa = False and retrieval_unit = 'documents' and format_context_for_llm = True
        citation_metadata: Citation metadata for knowledge base outputs, used for showing sources in LLM responses
        documents: Semantically similar documents retrieved from the knowledge base.
        formatted_text: Knowledge base outputs formatted for input to a LLM
    ### When enable_context = True
        citation_metadata: Citation metadata for knowledge base outputs, used for showing sources in LLM responses
    ### When enable_document_db_filter = True
        citation_metadata: Citation metadata for knowledge base outputs, used for showing sources in LLM responses
    """

    # Common inputs and outputs
    _COMMON_INPUTS = [
        {
            "field": "alpha",
            "helper_text": "The alpha value for the retrieval",
            "value": 0.5,
            "type": "float",
        },
        {
            "field": "answer_multiple_questions",
            "helper_text": "Extract separate questions from the query and retrieve content separately for each question to improve search performance",
            "value": False,
            "type": "bool",
        },
        {
            "field": "do_advanced_qa",
            "helper_text": "Use additional LLM calls to analyze each document to improve answer correctness",
            "value": False,
            "type": "bool",
        },
        {
            "field": "do_nl_metadata_query",
            "helper_text": "Do a natural language metadata query",
            "value": False,
            "type": "bool",
        },
        {
            "field": "enable_context",
            "helper_text": "Enable context",
            "value": False,
            "type": "bool",
        },
        {
            "field": "enable_document_db_filter",
            "helper_text": "Enable the document DB filter",
            "value": False,
            "type": "bool",
        },
        {
            "field": "enable_filter",
            "helper_text": "Filter the content returned from the knowledge base",
            "value": False,
            "type": "bool",
        },
        {
            "field": "expand_query",
            "helper_text": "Expand query to improve semantic search",
            "value": False,
            "type": "bool",
        },
        {
            "field": "expand_query_terms",
            "helper_text": "Expand query terms to improve semantic search",
            "value": False,
            "type": "bool",
        },
        {
            "field": "format_context_for_llm",
            "helper_text": "Format the context for the LLM",
            "value": False,
            "type": "bool",
        },
        {
            "field": "knowledge_base",
            "helper_text": "Select an existing knowledge base",
            "value": {},
            "type": "knowledge_base",
        },
        {
            "field": "max_docs_per_query",
            "helper_text": "The number of relevant chunks to be returned",
            "value": 10,
            "type": "int32",
        },
        {
            "field": "query",
            "helper_text": "The query will be used to search documents for relevant pieces semantically.",
            "value": "",
            "type": "string",
        },
        {
            "field": "rerank_documents",
            "helper_text": "Rerank the documents returned from the knowledge base",
            "value": False,
            "type": "bool",
        },
        {
            "field": "retrieval_unit",
            "helper_text": "The unit of retrieval",
            "value": "chunks",
            "type": "enum<string>",
        },
        {
            "field": "score_cutoff",
            "helper_text": "The score cutoff",
            "value": 0,
            "type": "float",
        },
        {
            "field": "show_intermediate_steps",
            "helper_text": "Show intermediate steps",
            "value": False,
            "type": "bool",
        },
        {
            "field": "transform_query",
            "helper_text": "Transform the query for better semantic search",
            "value": False,
            "type": "bool",
        },
    ]

    # Common outputs and inputs
    _COMMON_OUTPUTS = []

    # Configuration patterns and their associated inputs/outputs
    _CONFIGS = {
        "true**(*)**(*)**(*)**(*)**(*)**(*)": {
            "inputs": [
                {
                    "field": "qa_model_name",
                    "type": "enum<string>",
                    "value": "gpt-4o-mini",
                    "helper_text": "The model to use for the QA",
                },
                {
                    "field": "advanced_search_mode",
                    "type": "enum<string>",
                    "value": "accurate",
                    "helper_text": "The mode to use for the advanced search",
                },
            ],
            "outputs": [
                {
                    "field": "response",
                    "type": "string",
                    "helper_text": "The response from the knowledge base",
                },
                {
                    "field": "citation_metadata",
                    "type": "vec<string>",
                    "helper_text": "Citation metadata for knowledge base outputs, used for showing sources in LLM responses",
                },
            ],
        },
        "(*)**true**(*)**(*)**(*)**(*)**(*)": {
            "inputs": [
                {
                    "field": "filter",
                    "type": "string",
                    "value": "",
                    "helper_text": "Filter the content returned from the knowledge base",
                }
            ],
            "outputs": [
                {
                    "field": "citation_metadata",
                    "type": "vec<string>",
                    "helper_text": "Citation metadata for knowledge base outputs, used for showing sources in LLM responses",
                }
            ],
        },
        "(*)**(*)**true**(*)**(*)**(*)**(*)": {
            "inputs": [
                {
                    "field": "rerank_model",
                    "type": "enum<string>",
                    "value": "cohere/rerank-english-v3.0",
                    "helper_text": "Refine the initial ranking of returned chunks based on relevancy",
                }
            ],
            "outputs": [],
        },
        "false**(*)**(*)**documents**(*)**false**(*)": {
            "inputs": [],
            "outputs": [
                {
                    "field": "documents",
                    "type": "vec<string>",
                    "helper_text": "The documents returned from the knowledge base",
                },
                {
                    "field": "citation_metadata",
                    "type": "vec<string>",
                    "helper_text": "Citation metadata for knowledge base outputs, used for showing sources in LLM responses",
                },
            ],
        },
        "false**(*)**(*)**chunks**(*)**false**(*)": {
            "inputs": [],
            "outputs": [
                {
                    "field": "chunks",
                    "type": "vec<string>",
                    "helper_text": "Semantically similar chunks retrieved from the knowledge base.",
                },
                {
                    "field": "citation_metadata",
                    "type": "vec<string>",
                    "helper_text": "Citation metadata for knowledge base outputs, used for showing sources in LLM responses",
                },
            ],
        },
        "false**(*)**(*)**documents**(*)**true**(*)": {
            "inputs": [],
            "outputs": [
                {
                    "field": "documents",
                    "type": "vec<string>",
                    "helper_text": "Semantically similar documents retrieved from the knowledge base.",
                },
                {
                    "field": "citation_metadata",
                    "type": "vec<string>",
                    "helper_text": "Citation metadata for knowledge base outputs, used for showing sources in LLM responses",
                },
                {
                    "field": "formatted_text",
                    "type": "string",
                    "helper_text": "Knowledge base outputs formatted for input to a LLM",
                },
            ],
        },
        "false**(*)**(*)**chunks**(*)**true**(*)": {
            "inputs": [],
            "outputs": [
                {
                    "field": "chunks",
                    "type": "vec<string>",
                    "helper_text": "Semantically similar chunks retrieved from the knowledge base.",
                },
                {
                    "field": "citation_metadata",
                    "type": "vec<string>",
                    "helper_text": "Citation metadata for knowledge base outputs, used for showing sources in LLM responses",
                },
                {
                    "field": "formatted_text",
                    "type": "string",
                    "helper_text": "Knowledge base outputs formatted for input to a LLM",
                },
            ],
        },
        "(*)**(*)**(*)**(*)**true**(*)**(*)": {
            "inputs": [
                {
                    "field": "context",
                    "type": "string",
                    "value": "",
                    "helper_text": "Additional context to pass to the query analysis and qa steps",
                }
            ],
            "outputs": [
                {
                    "field": "citation_metadata",
                    "type": "vec<string>",
                    "helper_text": "Citation metadata for knowledge base outputs, used for showing sources in LLM responses",
                }
            ],
        },
        "(*)**(*)**(*)**(*)**(*)**(*)**true": {
            "inputs": [
                {
                    "field": "document_db_filter",
                    "type": "string",
                    "value": "",
                    "helper_text": "Filter the documents returned from the knowledge base",
                }
            ],
            "outputs": [
                {
                    "field": "citation_metadata",
                    "type": "vec<string>",
                    "helper_text": "Citation metadata for knowledge base outputs, used for showing sources in LLM responses",
                }
            ],
        },
    }

    # List of parameters that affect configuration
    _PARAMS = [
        "do_advanced_qa",
        "enable_filter",
        "rerank_documents",
        "retrieval_unit",
        "enable_context",
        "format_context_for_llm",
        "enable_document_db_filter",
    ]

    def __init__(
        self,
        id: Optional[str] = None,
        node_name: Optional[str] = None,
        execution_mode: Optional[str] = None,
        do_advanced_qa: bool = False,
        enable_filter: bool = False,
        rerank_documents: bool = False,
        retrieval_unit: str = "chunks",
        enable_context: bool = False,
        format_context_for_llm: bool = False,
        enable_document_db_filter: bool = False,
        advanced_search_mode: str = "accurate",
        alpha: Any = 0.5,
        answer_multiple_questions: bool = False,
        context: str = "",
        do_nl_metadata_query: bool = False,
        document_db_filter: str = "",
        expand_query: bool = False,
        expand_query_terms: bool = False,
        filter: str = "",
        knowledge_base: Any = {},
        max_docs_per_query: int = 10,
        qa_model_name: str = "gpt-4o-mini",
        query: str = "",
        rerank_model: str = "cohere/rerank-english-v3.0",
        score_cutoff: Any = 0,
        show_intermediate_steps: bool = False,
        transform_query: bool = False,
        **kwargs
    ):
        # Initialize with params
        params = {}
        params["do_advanced_qa"] = do_advanced_qa
        params["enable_filter"] = enable_filter
        params["rerank_documents"] = rerank_documents
        params["retrieval_unit"] = retrieval_unit
        params["enable_context"] = enable_context
        params["format_context_for_llm"] = format_context_for_llm
        params["enable_document_db_filter"] = enable_document_db_filter

        super().__init__(
            node_type="knowledge_base",
            params=params,
            id=id,
            node_name=node_name,
            execution_mode=execution_mode,
        )

        # Set input values
        if knowledge_base is not None:
            self.inputs["knowledge_base"] = knowledge_base
        if query is not None:
            self.inputs["query"] = query
        if max_docs_per_query is not None:
            self.inputs["max_docs_per_query"] = max_docs_per_query
        if enable_filter is not None:
            self.inputs["enable_filter"] = enable_filter
        if rerank_documents is not None:
            self.inputs["rerank_documents"] = rerank_documents
        if do_nl_metadata_query is not None:
            self.inputs["do_nl_metadata_query"] = do_nl_metadata_query
        if retrieval_unit is not None:
            self.inputs["retrieval_unit"] = retrieval_unit
        if alpha is not None:
            self.inputs["alpha"] = alpha
        if transform_query is not None:
            self.inputs["transform_query"] = transform_query
        if answer_multiple_questions is not None:
            self.inputs["answer_multiple_questions"] = answer_multiple_questions
        if expand_query is not None:
            self.inputs["expand_query"] = expand_query
        if expand_query_terms is not None:
            self.inputs["expand_query_terms"] = expand_query_terms
        if do_advanced_qa is not None:
            self.inputs["do_advanced_qa"] = do_advanced_qa
        if show_intermediate_steps is not None:
            self.inputs["show_intermediate_steps"] = show_intermediate_steps
        if score_cutoff is not None:
            self.inputs["score_cutoff"] = score_cutoff
        if enable_context is not None:
            self.inputs["enable_context"] = enable_context
        if format_context_for_llm is not None:
            self.inputs["format_context_for_llm"] = format_context_for_llm
        if enable_document_db_filter is not None:
            self.inputs["enable_document_db_filter"] = enable_document_db_filter
        if qa_model_name is not None:
            self.inputs["qa_model_name"] = qa_model_name
        if advanced_search_mode is not None:
            self.inputs["advanced_search_mode"] = advanced_search_mode
        if filter is not None:
            self.inputs["filter"] = filter
        if rerank_model is not None:
            self.inputs["rerank_model"] = rerank_model
        if context is not None:
            self.inputs["context"] = context
        if document_db_filter is not None:
            self.inputs["document_db_filter"] = document_db_filter

        # Update any additional inputs
        if kwargs:
            self.update_inputs(**kwargs)

    @property
    def chunks(self) -> List[str]:
        """
        Semantically similar chunks retrieved from the knowledge base.

        Available: When do_advanced_qa = False and retrieval_unit = 'chunks' and format_context_for_llm = False, When do_advanced_qa = False and retrieval_unit = 'chunks' and format_context_for_llm = True


        Raises:
            AttributeError: If this output is not available for the current parameter values
        """
        return self.__getattr__("chunks")

    @property
    def citation_metadata(self) -> List[str]:
        """
        Citation metadata for knowledge base outputs, used for showing sources in LLM responses

        Available: When do_advanced_qa = True, When enable_filter = True, When do_advanced_qa = False and retrieval_unit = 'documents' and format_context_for_llm = False, When do_advanced_qa = False and retrieval_unit = 'chunks' and format_context_for_llm = False, When do_advanced_qa = False and retrieval_unit = 'documents' and format_context_for_llm = True, When do_advanced_qa = False and retrieval_unit = 'chunks' and format_context_for_llm = True, When enable_context = True, When enable_document_db_filter = True


        Raises:
            AttributeError: If this output is not available for the current parameter values
        """
        return self.__getattr__("citation_metadata")

    @property
    def documents(self) -> List[str]:
        """
        The documents returned from the knowledge base

        Different behavior based on configuration:
          - The documents returned from the knowledge base (When do_advanced_qa = False and retrieval_unit = 'documents' and format_context_for_llm = False)
          - Semantically similar documents retrieved from the knowledge base. (When do_advanced_qa = False and retrieval_unit = 'documents' and format_context_for_llm = True)


        Raises:
            AttributeError: If this output is not available for the current parameter values
        """
        return self.__getattr__("documents")

    @property
    def formatted_text(self) -> str:
        """
        Knowledge base outputs formatted for input to a LLM

        Available: When do_advanced_qa = False and retrieval_unit = 'documents' and format_context_for_llm = True, When do_advanced_qa = False and retrieval_unit = 'chunks' and format_context_for_llm = True


        Raises:
            AttributeError: If this output is not available for the current parameter values
        """
        return self.__getattr__("formatted_text")

    @property
    def response(self) -> str:
        """
        The response from the knowledge base

        Available: When do_advanced_qa = True


        Raises:
            AttributeError: If this output is not available for the current parameter values
        """
        return self.__getattr__("response")

    @classmethod
    def from_dict(cls, data: dict) -> "KnowledgeBaseNode":
        """Create a node instance from a dictionary."""
        inputs = data.get("inputs", {})
        id = data.get("id", None)
        name = data.get("name", None)
        execution_mode = data.get("execution_mode", None)
        return cls(**inputs, id=id, node_name=name, execution_mode=execution_mode)


@Node.register_node_type("knowledge_base_loader")
class KnowledgeBaseLoaderNode(Node):
    """
    Load data into an existing knowledge base.

    ## Inputs
    ### Common Inputs
        document_type: Scrape sub-pages of the provided link
        knowledge_base: The knowledge base to load data into
        rescrape_frequency: The frequency to rescrape the URL
    ### File
        documents: The file to be added to the selected knowledge base. Note: to convert text to file, use the Text to File node
    ### URL
        max_recursive_urls: The maximum number of recursive URLs to scrape
        url: The raw URL link (e.g., https://vectorshift.ai/)
    ### Recursive URL
        max_recursive_urls: The maximum number of recursive URLs to scrape
        url: The raw URL link (e.g., https://vectorshift.ai/)

    ## Outputs
        None
    """

    # Common inputs and outputs
    _COMMON_INPUTS = [
        {
            "field": "document_type",
            "helper_text": "Scrape sub-pages of the provided link",
            "value": "File",
            "type": "enum<string>",
        },
        {
            "field": "knowledge_base",
            "helper_text": "The knowledge base to load data into",
            "value": {},
            "type": "knowledge_base",
        },
        {
            "field": "rescrape_frequency",
            "helper_text": "The frequency to rescrape the URL",
            "value": "Never",
            "type": "enum<string>",
        },
    ]

    # Common outputs and inputs
    _COMMON_OUTPUTS = []

    # Configuration patterns and their associated inputs/outputs
    _CONFIGS = {
        "URL": {
            "inputs": [
                {
                    "field": "max_recursive_urls",
                    "type": "int32",
                    "value": 10,
                    "helper_text": "The maximum number of recursive URLs to scrape",
                },
                {
                    "field": "url",
                    "type": "string",
                    "value": "",
                    "helper_text": "The raw URL link (e.g., https://vectorshift.ai/)",
                },
            ],
            "outputs": [],
        },
        "File": {
            "inputs": [
                {
                    "field": "documents",
                    "type": "vec<file>",
                    "value": [""],
                    "helper_text": "The file to be added to the selected knowledge base. Note: to convert text to file, use the Text to File node",
                }
            ],
            "outputs": [],
        },
        "Recursive URL": {
            "inputs": [
                {
                    "field": "max_recursive_urls",
                    "type": "int32",
                    "value": 10,
                    "helper_text": "The maximum number of recursive URLs to scrape",
                },
                {
                    "field": "url",
                    "type": "string",
                    "value": "",
                    "helper_text": "The raw URL link (e.g., https://vectorshift.ai/)",
                },
            ],
            "outputs": [],
        },
    }

    # List of parameters that affect configuration
    _PARAMS = ["document_type"]

    def __init__(
        self,
        id: Optional[str] = None,
        node_name: Optional[str] = None,
        execution_mode: Optional[str] = None,
        document_type: str = "File",
        documents: List[str] = [""],
        knowledge_base: Any = {},
        max_recursive_urls: int = 10,
        rescrape_frequency: str = "Never",
        url: str = "",
        **kwargs
    ):
        # Initialize with params
        params = {}
        params["document_type"] = document_type

        super().__init__(
            node_type="knowledge_base_loader",
            params=params,
            id=id,
            node_name=node_name,
            execution_mode=execution_mode,
        )

        # Set input values
        if knowledge_base is not None:
            self.inputs["knowledge_base"] = knowledge_base
        if document_type is not None:
            self.inputs["document_type"] = document_type
        if rescrape_frequency is not None:
            self.inputs["rescrape_frequency"] = rescrape_frequency
        if max_recursive_urls is not None:
            self.inputs["max_recursive_urls"] = max_recursive_urls
        if url is not None:
            self.inputs["url"] = url
        if documents is not None:
            self.inputs["documents"] = documents

        # Update any additional inputs
        if kwargs:
            self.update_inputs(**kwargs)

    @classmethod
    def from_dict(cls, data: dict) -> "KnowledgeBaseLoaderNode":
        """Create a node instance from a dictionary."""
        inputs = data.get("inputs", {})
        id = data.get("id", None)
        name = data.get("name", None)
        execution_mode = data.get("execution_mode", None)
        return cls(**inputs, id=id, node_name=name, execution_mode=execution_mode)


@Node.register_node_type("map")
class MapNode(Node):
    """


    ## Inputs
    ### Common Inputs
        function: The function input
        inputs: The inputs input

    ## Outputs
    ### Common Outputs
        output: The output output
    """

    # Common inputs and outputs
    _COMMON_INPUTS = [
        {
            "field": "function",
            "helper_text": "The function input",
            "value": "",
            "type": "string",
        },
        {
            "field": "inputs",
            "helper_text": "The inputs input",
            "value": "",
            "type": "string",
        },
    ]

    # Common outputs and inputs
    _COMMON_OUTPUTS = [{"field": "output", "helper_text": "The output output"}]

    # Configuration patterns and their associated inputs/outputs
    _CONFIGS = {}

    # List of parameters that affect configuration
    _PARAMS = []

    def __init__(
        self,
        id: Optional[str] = None,
        node_name: Optional[str] = None,
        execution_mode: Optional[str] = None,
        function: str = "",
        inputs: str = "",
        **kwargs
    ):
        # Initialize with params
        params = {}

        super().__init__(
            node_type="map",
            params=params,
            id=id,
            node_name=node_name,
            execution_mode=execution_mode,
        )

        # Set input values
        if inputs is not None:
            self.inputs["inputs"] = inputs
        if function is not None:
            self.inputs["function"] = function

        # Update any additional inputs
        if kwargs:
            self.update_inputs(**kwargs)

    @property
    def output(self) -> str:
        """
        The output output


        Raises:
            AttributeError: If this output is not available for the current parameter values
        """
        return self.__getattr__("output")

    @classmethod
    def from_dict(cls, data: dict) -> "MapNode":
        """Create a node instance from a dictionary."""
        inputs = data.get("inputs", {})
        id = data.get("id", None)
        name = data.get("name", None)
        execution_mode = data.get("execution_mode", None)
        return cls(**inputs, id=id, node_name=name, execution_mode=execution_mode)


@Node.register_node_type("merge")
class MergeNode(Node):
    """
    Recombine paths created by a condition node. Note: if you are not using a condition node, you shouldn’t use a merge node

    ## Inputs
    ### Common Inputs
        function: The function to apply to the input fields
        type: The expected type of the input and output fields
    ### When function = 'first' and type = '<T>'
        fields: The fields input
    ### When function = 'join' and type = '<T>'
        fields: The fields input

    ## Outputs
    ### When function = 'first' and type = '<T>'
        output: The Text from the path based on the condition node
    ### When function = 'join' and type = '<T>'
        output: The Text from the path based on the condition node
    """

    # Common inputs and outputs
    _COMMON_INPUTS = [
        {
            "field": "function",
            "helper_text": "The function to apply to the input fields",
            "value": "first",
            "type": "enum<string>",
        },
        {
            "field": "type",
            "helper_text": "The expected type of the input and output fields",
            "value": "string",
            "type": "enum<string>",
        },
    ]

    # Common outputs and inputs
    _COMMON_OUTPUTS = []

    # Configuration patterns and their associated inputs/outputs
    _CONFIGS = {
        "first**<T>": {
            "inputs": [
                {"field": "fields", "type": "vec<<T>>", "value": [""]},
                {
                    "field": "function",
                    "type": "enum<string>",
                    "value": "first",
                    "helper_text": "The function to apply to the input fields",
                },
            ],
            "outputs": [
                {
                    "field": "output",
                    "type": "<T>",
                    "helper_text": "The Text from the path based on the condition node",
                }
            ],
        },
        "join**<T>": {
            "inputs": [
                {"field": "fields", "type": "vec<<T>>", "value": [""]},
                {
                    "field": "function",
                    "type": "enum<string>",
                    "value": "join",
                    "helper_text": "The function to apply to the output fields",
                },
            ],
            "outputs": [
                {
                    "field": "output",
                    "type": "vec<<T>>",
                    "helper_text": "The Text from the path based on the condition node",
                }
            ],
        },
    }

    # List of parameters that affect configuration
    _PARAMS = ["function", "type"]

    def __init__(
        self,
        id: Optional[str] = None,
        node_name: Optional[str] = None,
        execution_mode: Optional[str] = None,
        function: str = "first",
        type: str = "string",
        fields: List[Any] = [""],
        **kwargs
    ):
        # Initialize with params
        params = {}
        params["function"] = function
        params["type"] = type

        super().__init__(
            node_type="merge",
            params=params,
            id=id,
            node_name=node_name,
            execution_mode=execution_mode,
        )

        # Set input values
        if type is not None:
            self.inputs["type"] = type
        if function is not None:
            self.inputs["function"] = function
        if fields is not None:
            self.inputs["fields"] = fields

        # Update any additional inputs
        if kwargs:
            self.update_inputs(**kwargs)

    @classmethod
    def from_dict(cls, data: dict) -> "MergeNode":
        """Create a node instance from a dictionary."""
        inputs = data.get("inputs", {})
        id = data.get("id", None)
        name = data.get("name", None)
        execution_mode = data.get("execution_mode", None)
        return cls(**inputs, id=id, node_name=name, execution_mode=execution_mode)


@Node.register_node_type("condition")
class ConditionNode(Node):
    """
    Specify a series of conditions and execute different paths based on the value of the conditions.

    ## Inputs
    ### Common Inputs
        conditions: The conditions input
        outputs: The outputs input

    ## Outputs
    ### Common Outputs
        [outputs]: The [outputs] output
    """

    # Common inputs and outputs
    _COMMON_INPUTS = [
        {
            "field": "conditions",
            "helper_text": "The conditions input",
            "value": [],
            "type": "vec<Dict[str, Any]>",
        },
        {
            "field": "outputs",
            "helper_text": "The outputs input",
            "value": {},
            "type": "map<string, string>",
        },
    ]

    # Common outputs and inputs
    _COMMON_OUTPUTS = [{"field": "[outputs]", "helper_text": "The [outputs] output"}]

    # Configuration patterns and their associated inputs/outputs
    _CONFIGS = {}

    # List of parameters that affect configuration
    _PARAMS = []

    def __init__(
        self,
        id: Optional[str] = None,
        node_name: Optional[str] = None,
        execution_mode: Optional[str] = None,
        conditions: List[Any] = [],
        outputs: Dict[str, str] = {},
        **kwargs
    ):
        # Initialize with params
        params = {}

        super().__init__(
            node_type="condition",
            params=params,
            id=id,
            node_name=node_name,
            execution_mode=execution_mode,
        )

        # Set input values
        if conditions is not None:
            self.inputs["conditions"] = conditions
        if outputs is not None:
            self.inputs["outputs"] = outputs

        # Update any additional inputs
        if kwargs:
            self.update_inputs(**kwargs)

    @classmethod
    def from_dict(cls, data: dict) -> "ConditionNode":
        """Create a node instance from a dictionary."""
        inputs = data.get("inputs", {})
        id = data.get("id", None)
        name = data.get("name", None)
        execution_mode = data.get("execution_mode", None)
        return cls(**inputs, id=id, node_name=name, execution_mode=execution_mode)


@Node.register_node_type("nl_to_sql")
class NlToSqlNode(Node):
    """
    Convert natural language queries to SQL queries.

    ## Inputs
    ### Common Inputs
        db_dialect: The database dialect to use
        model: The model to use for the conversion
        schema: The schema of the database
        text: The natural language query to convert to SQL

    ## Outputs
    ### Common Outputs
        sql_query: The SQL query generated from the natural language query
    """

    # Common inputs and outputs
    _COMMON_INPUTS = [
        {
            "field": "db_dialect",
            "helper_text": "The database dialect to use",
            "value": "PostgreSQL",
            "type": "enum<string>",
        },
        {
            "field": "model",
            "helper_text": "The model to use for the conversion",
            "value": "gpt-4o",
            "type": "enum<string>",
        },
        {
            "field": "schema",
            "helper_text": "The schema of the database",
            "value": "",
            "type": "string",
        },
        {
            "field": "text",
            "helper_text": "The natural language query to convert to SQL",
            "value": "",
            "type": "string",
        },
    ]

    # Common outputs and inputs
    _COMMON_OUTPUTS = [
        {
            "field": "sql_query",
            "helper_text": "The SQL query generated from the natural language query",
        }
    ]

    # Configuration patterns and their associated inputs/outputs
    _CONFIGS = {}

    # List of parameters that affect configuration
    _PARAMS = []

    def __init__(
        self,
        id: Optional[str] = None,
        node_name: Optional[str] = None,
        execution_mode: Optional[str] = None,
        db_dialect: str = "PostgreSQL",
        model: str = "gpt-4o",
        schema: str = "",
        text: str = "",
        **kwargs
    ):
        # Initialize with params
        params = {}

        super().__init__(
            node_type="nl_to_sql",
            params=params,
            id=id,
            node_name=node_name,
            execution_mode=execution_mode,
        )

        # Set input values
        if db_dialect is not None:
            self.inputs["db_dialect"] = db_dialect
        if schema is not None:
            self.inputs["schema"] = schema
        if text is not None:
            self.inputs["text"] = text
        if model is not None:
            self.inputs["model"] = model

        # Update any additional inputs
        if kwargs:
            self.update_inputs(**kwargs)

    @property
    def sql_query(self) -> str:
        """
        The SQL query generated from the natural language query


        Raises:
            AttributeError: If this output is not available for the current parameter values
        """
        return self.__getattr__("sql_query")

    @classmethod
    def from_dict(cls, data: dict) -> "NlToSqlNode":
        """Create a node instance from a dictionary."""
        inputs = data.get("inputs", {})
        id = data.get("id", None)
        name = data.get("name", None)
        execution_mode = data.get("execution_mode", None)
        return cls(**inputs, id=id, node_name=name, execution_mode=execution_mode)


@Node.register_node_type("read_json_values")
class ReadJsonValuesNode(Node):
    """
    Read values from a JSON object based on a provided key(s).

    ## Inputs
    ### Common Inputs
        json_string: The JSON you want to read from
        keys: Define the name(s) of the JSON keys from the JSON that you want to read
        processed_outputs: The processed_outputs input

    ## Outputs
    ### Common Outputs
        [processed_outputs]: The [processed_outputs] output
        json_values: The JSON Value
    """

    # Common inputs and outputs
    _COMMON_INPUTS = [
        {
            "field": "json_string",
            "helper_text": "The JSON you want to read from",
            "value": "",
            "type": "string",
        },
        {
            "field": "keys",
            "helper_text": "Define the name(s) of the JSON keys from the JSON that you want to read",
            "value": [],
            "type": "vec<Dict[str, Any]>",
        },
        {
            "field": "processed_outputs",
            "helper_text": "The processed_outputs input",
            "value": {},
            "type": "map<string, string>",
        },
    ]

    # Common outputs and inputs
    _COMMON_OUTPUTS = [
        {
            "field": "[processed_outputs]",
            "helper_text": "The [processed_outputs] output",
        },
        {"field": "json_values", "helper_text": "The JSON Value"},
    ]

    # Configuration patterns and their associated inputs/outputs
    _CONFIGS = {}

    # List of parameters that affect configuration
    _PARAMS = []

    def __init__(
        self,
        id: Optional[str] = None,
        node_name: Optional[str] = None,
        execution_mode: Optional[str] = None,
        json_string: str = "",
        keys: List[Any] = [],
        processed_outputs: Dict[str, str] = {},
        **kwargs
    ):
        # Initialize with params
        params = {}

        super().__init__(
            node_type="read_json_values",
            params=params,
            id=id,
            node_name=node_name,
            execution_mode=execution_mode,
        )

        # Set input values
        if json_string is not None:
            self.inputs["json_string"] = json_string
        if keys is not None:
            self.inputs["keys"] = keys
        if processed_outputs is not None:
            self.inputs["processed_outputs"] = processed_outputs

        # Update any additional inputs
        if kwargs:
            self.update_inputs(**kwargs)

    @property
    def json_values(self) -> str:
        """
        The JSON Value


        Raises:
            AttributeError: If this output is not available for the current parameter values
        """
        return self.__getattr__("json_values")

    @classmethod
    def from_dict(cls, data: dict) -> "ReadJsonValuesNode":
        """Create a node instance from a dictionary."""
        inputs = data.get("inputs", {})
        id = data.get("id", None)
        name = data.get("name", None)
        execution_mode = data.get("execution_mode", None)
        return cls(**inputs, id=id, node_name=name, execution_mode=execution_mode)


@Node.register_node_type("write_json_value")
class WriteJsonValueNode(Node):
    """
    Update a specific value in a JSON.

    ## Inputs
    ### Common Inputs
        fields: The fields input
        selected: Whether to update the JSON value or create a new JSON
    ### old
        json_string: The JSON to update

    ## Outputs
    ### Common Outputs
        updated_json: The updated JSON
    """

    # Common inputs and outputs
    _COMMON_INPUTS = [
        {
            "field": "fields",
            "helper_text": "The fields input",
            "value": [],
            "type": "vec<Dict[str, Any]>",
        },
        {
            "field": "selected",
            "helper_text": "Whether to update the JSON value or create a new JSON",
            "value": "new",
            "type": "enum<string>",
        },
    ]

    # Common outputs and inputs
    _COMMON_OUTPUTS = [{"field": "updated_json", "helper_text": "The updated JSON"}]

    # Configuration patterns and their associated inputs/outputs
    _CONFIGS = {
        "old": {
            "inputs": [
                {
                    "field": "json_string",
                    "type": "string",
                    "value": "",
                    "helper_text": "The JSON to update",
                }
            ],
            "outputs": [],
        }
    }

    # List of parameters that affect configuration
    _PARAMS = ["selected"]

    def __init__(
        self,
        id: Optional[str] = None,
        node_name: Optional[str] = None,
        execution_mode: Optional[str] = None,
        selected: str = "new",
        fields: List[Any] = [],
        json_string: str = "",
        **kwargs
    ):
        # Initialize with params
        params = {}
        params["selected"] = selected

        super().__init__(
            node_type="write_json_value",
            params=params,
            id=id,
            node_name=node_name,
            execution_mode=execution_mode,
        )

        # Set input values
        if selected is not None:
            self.inputs["selected"] = selected
        if fields is not None:
            self.inputs["fields"] = fields
        if json_string is not None:
            self.inputs["json_string"] = json_string

        # Update any additional inputs
        if kwargs:
            self.update_inputs(**kwargs)

    @property
    def updated_json(self) -> str:
        """
        The updated JSON


        Raises:
            AttributeError: If this output is not available for the current parameter values
        """
        return self.__getattr__("updated_json")

    @classmethod
    def from_dict(cls, data: dict) -> "WriteJsonValueNode":
        """Create a node instance from a dictionary."""
        inputs = data.get("inputs", {})
        id = data.get("id", None)
        name = data.get("name", None)
        execution_mode = data.get("execution_mode", None)
        return cls(**inputs, id=id, node_name=name, execution_mode=execution_mode)


@Node.register_node_type("api")
class ApiNode(Node):
    """
    Make an API request to a given URL.

    ## Inputs
    ### Common Inputs
        files: Files to include in the API request
        headers: Headers to include in the API request
        is_raw_json: Whether to return the raw JSON response from the API
        method: Choose the API Method desired (GET, POST, PUT, DELETE, PATCH)
        query_params: Query parameters to include in the API request
        url: Target URL for the API Request
    ### When is_raw_json = False
        body_params: The body parameters to include in the API request
    ### When is_raw_json = True
        raw_json: The raw JSON response from the API

    ## Outputs
    ### Common Outputs
        output: The response from the API
    """

    # Common inputs and outputs
    _COMMON_INPUTS = [
        {
            "field": "files",
            "helper_text": "Files to include in the API request",
            "value": [],
            "type": "vec<Dict[str, Any]>",
        },
        {
            "field": "headers",
            "helper_text": "Headers to include in the API request",
            "value": [],
            "type": "vec<Dict[str, Any]>",
        },
        {
            "field": "is_raw_json",
            "helper_text": "Whether to return the raw JSON response from the API",
            "value": False,
            "type": "bool",
        },
        {
            "field": "method",
            "helper_text": "Choose the API Method desired (GET, POST, PUT, DELETE, PATCH)",
            "value": "GET",
            "type": "enum<string>",
        },
        {
            "field": "query_params",
            "helper_text": "Query parameters to include in the API request",
            "value": [],
            "type": "vec<Dict[str, Any]>",
        },
        {
            "field": "url",
            "helper_text": "Target URL for the API Request",
            "value": "",
            "type": "string",
        },
    ]

    # Common outputs and inputs
    _COMMON_OUTPUTS = [{"field": "output", "helper_text": "The response from the API"}]

    # Configuration patterns and their associated inputs/outputs
    _CONFIGS = {
        "true": {
            "inputs": [
                {
                    "field": "raw_json",
                    "type": "string",
                    "value": "",
                    "helper_text": "The raw JSON response from the API",
                }
            ],
            "outputs": [],
        },
        "false": {
            "inputs": [
                {
                    "field": "body_params",
                    "type": "vec<Dict[str, Any]>",
                    "value": [],
                    "helper_text": "The body parameters to include in the API request",
                }
            ],
            "outputs": [],
        },
    }

    # List of parameters that affect configuration
    _PARAMS = ["is_raw_json"]

    def __init__(
        self,
        id: Optional[str] = None,
        node_name: Optional[str] = None,
        execution_mode: Optional[str] = None,
        is_raw_json: bool = False,
        body_params: List[Any] = [],
        files: List[Any] = [],
        headers: List[Any] = [],
        method: str = "GET",
        query_params: List[Any] = [],
        raw_json: str = "",
        url: str = "",
        **kwargs
    ):
        # Initialize with params
        params = {}
        params["is_raw_json"] = is_raw_json

        super().__init__(
            node_type="api",
            params=params,
            id=id,
            node_name=node_name,
            execution_mode=execution_mode,
        )

        # Set input values
        if method is not None:
            self.inputs["method"] = method
        if url is not None:
            self.inputs["url"] = url
        if headers is not None:
            self.inputs["headers"] = headers
        if query_params is not None:
            self.inputs["query_params"] = query_params
        if files is not None:
            self.inputs["files"] = files
        if is_raw_json is not None:
            self.inputs["is_raw_json"] = is_raw_json
        if raw_json is not None:
            self.inputs["raw_json"] = raw_json
        if body_params is not None:
            self.inputs["body_params"] = body_params

        # Update any additional inputs
        if kwargs:
            self.update_inputs(**kwargs)

    @property
    def output(self) -> str:
        """
        The response from the API


        Raises:
            AttributeError: If this output is not available for the current parameter values
        """
        return self.__getattr__("output")

    @classmethod
    def from_dict(cls, data: dict) -> "ApiNode":
        """Create a node instance from a dictionary."""
        inputs = data.get("inputs", {})
        id = data.get("id", None)
        name = data.get("name", None)
        execution_mode = data.get("execution_mode", None)
        return cls(**inputs, id=id, node_name=name, execution_mode=execution_mode)


@Node.register_node_type("url_loader")
class UrlLoaderNode(Node):
    """
    Scrape content from a URL.

    ## Inputs
    ### Common Inputs
        provider: The provider to use for the URL loader
        url: The URL to load
    ### When provider = 'modal'
        ai_enhance_content: Whether to enhance the content
        recursive: Whether to recursively load the URL
        url_limit: The maximum number of URLs to load
        use_personal_api_key: Whether to use a personal API key
    ### When provider = 'apify'
        api_key: The API key to use
        recursive: Whether to recursively load the URL
        url_limit: The maximum number of URLs to load
    ### When provider = 'jina' and use_personal_api_key = True
        api_key: The API key to use
    ### When provider = 'modal' and use_personal_api_key = True
        apify_key: The API key to use
    ### When provider = 'jina'
        use_personal_api_key: Whether to use a personal API key

    ## Outputs
    ### Common Outputs
        content: The content of the URL
    """

    # Common inputs and outputs
    _COMMON_INPUTS = [
        {
            "field": "provider",
            "helper_text": "The provider to use for the URL loader",
            "value": "modal",
            "type": "enum<string>",
        },
        {
            "field": "url",
            "helper_text": "The URL to load",
            "value": "",
            "type": "string",
        },
    ]

    # Common outputs and inputs
    _COMMON_OUTPUTS = [{"field": "content", "helper_text": "The content of the URL"}]

    # Configuration patterns and their associated inputs/outputs
    _CONFIGS = {
        "jina**(*)": {
            "inputs": [
                {
                    "field": "use_personal_api_key",
                    "type": "bool",
                    "value": False,
                    "helper_text": "Whether to use a personal API key",
                }
            ],
            "outputs": [],
        },
        "apify**(*)": {
            "inputs": [
                {
                    "field": "recursive",
                    "type": "bool",
                    "value": False,
                    "helper_text": "Whether to recursively load the URL",
                },
                {
                    "field": "url_limit",
                    "type": "int32",
                    "value": 10,
                    "helper_text": "The maximum number of URLs to load",
                },
                {
                    "field": "api_key",
                    "type": "string",
                    "value": "",
                    "helper_text": "The API key to use",
                },
            ],
            "outputs": [],
        },
        "modal**(*)": {
            "inputs": [
                {
                    "field": "recursive",
                    "type": "bool",
                    "value": False,
                    "helper_text": "Whether to recursively load the URL",
                },
                {
                    "field": "use_personal_api_key",
                    "type": "bool",
                    "value": False,
                    "helper_text": "Whether to use a personal API key",
                },
                {
                    "field": "ai_enhance_content",
                    "type": "bool",
                    "value": False,
                    "helper_text": "Whether to enhance the content",
                },
                {
                    "field": "url_limit",
                    "type": "int32",
                    "value": 10,
                    "helper_text": "The maximum number of URLs to load",
                },
            ],
            "outputs": [],
        },
        "modal**true": {
            "inputs": [
                {
                    "field": "apify_key",
                    "type": "string",
                    "value": "",
                    "helper_text": "The API key to use",
                }
            ],
            "outputs": [],
        },
        "jina**true": {
            "inputs": [
                {
                    "field": "api_key",
                    "type": "string",
                    "value": "",
                    "helper_text": "The API key to use",
                }
            ],
            "outputs": [],
        },
    }

    # List of parameters that affect configuration
    _PARAMS = ["provider", "use_personal_api_key"]

    def __init__(
        self,
        id: Optional[str] = None,
        node_name: Optional[str] = None,
        execution_mode: Optional[str] = None,
        provider: str = "modal",
        use_personal_api_key: bool = False,
        ai_enhance_content: bool = False,
        api_key: str = "",
        apify_key: str = "",
        recursive: bool = False,
        url: str = "",
        url_limit: int = 10,
        **kwargs
    ):
        # Initialize with params
        params = {}
        params["provider"] = provider
        params["use_personal_api_key"] = use_personal_api_key

        super().__init__(
            node_type="url_loader",
            params=params,
            id=id,
            node_name=node_name,
            execution_mode=execution_mode,
        )

        # Set input values
        if provider is not None:
            self.inputs["provider"] = provider
        if url is not None:
            self.inputs["url"] = url
        if use_personal_api_key is not None:
            self.inputs["use_personal_api_key"] = use_personal_api_key
        if recursive is not None:
            self.inputs["recursive"] = recursive
        if url_limit is not None:
            self.inputs["url_limit"] = url_limit
        if api_key is not None:
            self.inputs["api_key"] = api_key
        if ai_enhance_content is not None:
            self.inputs["ai_enhance_content"] = ai_enhance_content
        if apify_key is not None:
            self.inputs["apify_key"] = apify_key

        # Update any additional inputs
        if kwargs:
            self.update_inputs(**kwargs)

    @property
    def content(self) -> str:
        """
        The content of the URL


        Raises:
            AttributeError: If this output is not available for the current parameter values
        """
        return self.__getattr__("content")

    @classmethod
    def from_dict(cls, data: dict) -> "UrlLoaderNode":
        """Create a node instance from a dictionary."""
        inputs = data.get("inputs", {})
        id = data.get("id", None)
        name = data.get("name", None)
        execution_mode = data.get("execution_mode", None)
        return cls(**inputs, id=id, node_name=name, execution_mode=execution_mode)


@Node.register_node_type("wikipedia")
class WikipediaNode(Node):
    """
    Query Wikipedia to return relevant articles

    ## Inputs
    ### Common Inputs
        chunk_text: Whether to chunk the text
        query: The Wikipedia query
    ### When chunk_text = True
        chunk_overlap: The overlap of the chunks
        chunk_size: The size of the chunks to create

    ## Outputs
    ### When chunk_text = True
        output: List of raw text from the Wikipedia article
    ### When chunk_text = False
        output: The raw text from the Wikipedia article
    """

    # Common inputs and outputs
    _COMMON_INPUTS = [
        {
            "field": "chunk_text",
            "helper_text": "Whether to chunk the text",
            "value": False,
            "type": "bool",
        },
        {
            "field": "query",
            "helper_text": "The Wikipedia query",
            "value": "",
            "type": "string",
        },
    ]

    # Common outputs and inputs
    _COMMON_OUTPUTS = []

    # Configuration patterns and their associated inputs/outputs
    _CONFIGS = {
        "true": {
            "inputs": [
                {
                    "field": "chunk_size",
                    "type": "int32",
                    "value": 512,
                    "helper_text": "The size of the chunks to create",
                },
                {
                    "field": "chunk_overlap",
                    "type": "int32",
                    "value": 0,
                    "helper_text": "The overlap of the chunks",
                },
            ],
            "outputs": [
                {
                    "field": "output",
                    "type": "vec<string>",
                    "helper_text": "List of raw text from the Wikipedia article",
                }
            ],
        },
        "false": {
            "inputs": [],
            "outputs": [
                {
                    "field": "output",
                    "type": "string",
                    "helper_text": "The raw text from the Wikipedia article",
                }
            ],
        },
    }

    # List of parameters that affect configuration
    _PARAMS = ["chunk_text"]

    def __init__(
        self,
        id: Optional[str] = None,
        node_name: Optional[str] = None,
        execution_mode: Optional[str] = None,
        chunk_text: bool = False,
        chunk_overlap: int = 0,
        chunk_size: int = 512,
        query: str = "",
        **kwargs
    ):
        # Initialize with params
        params = {}
        params["chunk_text"] = chunk_text

        super().__init__(
            node_type="wikipedia",
            params=params,
            id=id,
            node_name=node_name,
            execution_mode=execution_mode,
        )

        # Set input values
        if query is not None:
            self.inputs["query"] = query
        if chunk_text is not None:
            self.inputs["chunk_text"] = chunk_text
        if chunk_size is not None:
            self.inputs["chunk_size"] = chunk_size
        if chunk_overlap is not None:
            self.inputs["chunk_overlap"] = chunk_overlap

        # Update any additional inputs
        if kwargs:
            self.update_inputs(**kwargs)

    @property
    def output(self) -> List[str]:
        """
        List of raw text from the Wikipedia article

        Different behavior based on configuration:
          - List of raw text from the Wikipedia article (When chunk_text = True)
          - The raw text from the Wikipedia article (When chunk_text = False)


        Raises:
            AttributeError: If this output is not available for the current parameter values
        """
        return self.__getattr__("output")

    @classmethod
    def from_dict(cls, data: dict) -> "WikipediaNode":
        """Create a node instance from a dictionary."""
        inputs = data.get("inputs", {})
        id = data.get("id", None)
        name = data.get("name", None)
        execution_mode = data.get("execution_mode", None)
        return cls(**inputs, id=id, node_name=name, execution_mode=execution_mode)


@Node.register_node_type("youtube")
class YoutubeNode(Node):
    """
    Get the transcript of a youtube video.

    ## Inputs
    ### Common Inputs
        chunk_text: Whether to chunk the text
        url: The YouTube URL to get the transcript of
    ### When chunk_text = True
        chunk_overlap: The overlap of the chunks
        chunk_size: The size of the chunks to create

    ## Outputs
    ### When chunk_text = True
        output: List of raw text from the YouTube transcript
    ### When chunk_text = False
        output: The raw text from the YouTube transcript
    """

    # Common inputs and outputs
    _COMMON_INPUTS = [
        {
            "field": "chunk_text",
            "helper_text": "Whether to chunk the text",
            "value": False,
            "type": "bool",
        },
        {
            "field": "url",
            "helper_text": "The YouTube URL to get the transcript of",
            "value": "",
            "type": "string",
        },
    ]

    # Common outputs and inputs
    _COMMON_OUTPUTS = []

    # Configuration patterns and their associated inputs/outputs
    _CONFIGS = {
        "true": {
            "inputs": [
                {
                    "field": "chunk_size",
                    "type": "int32",
                    "value": 512,
                    "helper_text": "The size of the chunks to create",
                },
                {
                    "field": "chunk_overlap",
                    "type": "int32",
                    "value": 0,
                    "helper_text": "The overlap of the chunks",
                },
            ],
            "outputs": [
                {
                    "field": "output",
                    "type": "vec<string>",
                    "helper_text": "List of raw text from the YouTube transcript",
                }
            ],
        },
        "false": {
            "inputs": [],
            "outputs": [
                {
                    "field": "output",
                    "type": "string",
                    "helper_text": "The raw text from the YouTube transcript",
                }
            ],
        },
    }

    # List of parameters that affect configuration
    _PARAMS = ["chunk_text"]

    def __init__(
        self,
        id: Optional[str] = None,
        node_name: Optional[str] = None,
        execution_mode: Optional[str] = None,
        chunk_text: bool = False,
        chunk_overlap: int = 0,
        chunk_size: int = 512,
        url: str = "",
        **kwargs
    ):
        # Initialize with params
        params = {}
        params["chunk_text"] = chunk_text

        super().__init__(
            node_type="youtube",
            params=params,
            id=id,
            node_name=node_name,
            execution_mode=execution_mode,
        )

        # Set input values
        if url is not None:
            self.inputs["url"] = url
        if chunk_text is not None:
            self.inputs["chunk_text"] = chunk_text
        if chunk_size is not None:
            self.inputs["chunk_size"] = chunk_size
        if chunk_overlap is not None:
            self.inputs["chunk_overlap"] = chunk_overlap

        # Update any additional inputs
        if kwargs:
            self.update_inputs(**kwargs)

    @property
    def output(self) -> List[str]:
        """
        List of raw text from the YouTube transcript

        Different behavior based on configuration:
          - List of raw text from the YouTube transcript (When chunk_text = True)
          - The raw text from the YouTube transcript (When chunk_text = False)


        Raises:
            AttributeError: If this output is not available for the current parameter values
        """
        return self.__getattr__("output")

    @classmethod
    def from_dict(cls, data: dict) -> "YoutubeNode":
        """Create a node instance from a dictionary."""
        inputs = data.get("inputs", {})
        id = data.get("id", None)
        name = data.get("name", None)
        execution_mode = data.get("execution_mode", None)
        return cls(**inputs, id=id, node_name=name, execution_mode=execution_mode)


@Node.register_node_type("arxiv")
class ArxivNode(Node):
    """
    Query ARXIV to return relevant articles

    ## Inputs
    ### Common Inputs
        chunk_text: Whether to chunk the text
        query: The ARXIV query
    ### When chunk_text = True
        chunk_overlap: The overlap of the chunks
        chunk_size: The size of the chunks to create

    ## Outputs
    ### When chunk_text = True
        output: List of raw text from the ARXIV article
    ### When chunk_text = False
        output: The raw text from the ARXIV article
    """

    # Common inputs and outputs
    _COMMON_INPUTS = [
        {
            "field": "chunk_text",
            "helper_text": "Whether to chunk the text",
            "value": False,
            "type": "bool",
        },
        {
            "field": "query",
            "helper_text": "The ARXIV query",
            "value": "",
            "type": "string",
        },
    ]

    # Common outputs and inputs
    _COMMON_OUTPUTS = []

    # Configuration patterns and their associated inputs/outputs
    _CONFIGS = {
        "true": {
            "inputs": [
                {
                    "field": "chunk_size",
                    "type": "int32",
                    "value": 512,
                    "helper_text": "The size of the chunks to create",
                },
                {
                    "field": "chunk_overlap",
                    "type": "int32",
                    "value": 0,
                    "helper_text": "The overlap of the chunks",
                },
            ],
            "outputs": [
                {
                    "field": "output",
                    "type": "vec<string>",
                    "helper_text": "List of raw text from the ARXIV article",
                }
            ],
        },
        "false": {
            "inputs": [],
            "outputs": [
                {
                    "field": "output",
                    "type": "string",
                    "helper_text": "The raw text from the ARXIV article",
                }
            ],
        },
    }

    # List of parameters that affect configuration
    _PARAMS = ["chunk_text"]

    def __init__(
        self,
        id: Optional[str] = None,
        node_name: Optional[str] = None,
        execution_mode: Optional[str] = None,
        chunk_text: bool = False,
        chunk_overlap: int = 0,
        chunk_size: int = 512,
        query: str = "",
        **kwargs
    ):
        # Initialize with params
        params = {}
        params["chunk_text"] = chunk_text

        super().__init__(
            node_type="arxiv",
            params=params,
            id=id,
            node_name=node_name,
            execution_mode=execution_mode,
        )

        # Set input values
        if query is not None:
            self.inputs["query"] = query
        if chunk_text is not None:
            self.inputs["chunk_text"] = chunk_text
        if chunk_size is not None:
            self.inputs["chunk_size"] = chunk_size
        if chunk_overlap is not None:
            self.inputs["chunk_overlap"] = chunk_overlap

        # Update any additional inputs
        if kwargs:
            self.update_inputs(**kwargs)

    @property
    def output(self) -> List[str]:
        """
        List of raw text from the ARXIV article

        Different behavior based on configuration:
          - List of raw text from the ARXIV article (When chunk_text = True)
          - The raw text from the ARXIV article (When chunk_text = False)


        Raises:
            AttributeError: If this output is not available for the current parameter values
        """
        return self.__getattr__("output")

    @classmethod
    def from_dict(cls, data: dict) -> "ArxivNode":
        """Create a node instance from a dictionary."""
        inputs = data.get("inputs", {})
        id = data.get("id", None)
        name = data.get("name", None)
        execution_mode = data.get("execution_mode", None)
        return cls(**inputs, id=id, node_name=name, execution_mode=execution_mode)


@Node.register_node_type("serp_api")
class SerpApiNode(Node):
    """
    Query the SERPAPI Google search API

    ## Inputs
    ### Common Inputs
        api_key: SERP API key
        query: The web search query

    ## Outputs
    ### Common Outputs
        output: Results of the SERP query
    """

    # Common inputs and outputs
    _COMMON_INPUTS = [
        {
            "field": "api_key",
            "helper_text": "SERP API key",
            "value": "",
            "type": "string",
        },
        {
            "field": "query",
            "helper_text": "The web search query",
            "value": "",
            "type": "string",
        },
    ]

    # Common outputs and inputs
    _COMMON_OUTPUTS = [{"field": "output", "helper_text": "Results of the SERP query"}]

    # Configuration patterns and their associated inputs/outputs
    _CONFIGS = {}

    # List of parameters that affect configuration
    _PARAMS = []

    def __init__(
        self,
        id: Optional[str] = None,
        node_name: Optional[str] = None,
        execution_mode: Optional[str] = None,
        api_key: str = "",
        query: str = "",
        **kwargs
    ):
        # Initialize with params
        params = {}

        super().__init__(
            node_type="serp_api",
            params=params,
            id=id,
            node_name=node_name,
            execution_mode=execution_mode,
        )

        # Set input values
        if query is not None:
            self.inputs["query"] = query
        if api_key is not None:
            self.inputs["api_key"] = api_key

        # Update any additional inputs
        if kwargs:
            self.update_inputs(**kwargs)

    @property
    def output(self) -> List[str]:
        """
        Results of the SERP query


        Raises:
            AttributeError: If this output is not available for the current parameter values
        """
        return self.__getattr__("output")

    @classmethod
    def from_dict(cls, data: dict) -> "SerpApiNode":
        """Create a node instance from a dictionary."""
        inputs = data.get("inputs", {})
        id = data.get("id", None)
        name = data.get("name", None)
        execution_mode = data.get("execution_mode", None)
        return cls(**inputs, id=id, node_name=name, execution_mode=execution_mode)


@Node.register_node_type("you_dot_com")
class YouDotComNode(Node):
    """
    Query the You.com search API

    ## Inputs
    ### Common Inputs
        api_key: You.com API key
        loader_type: Select the loader type: General or News
        query: The search query

    ## Outputs
    ### Common Outputs
        output: The output output
    """

    # Common inputs and outputs
    _COMMON_INPUTS = [
        {
            "field": "api_key",
            "helper_text": "You.com API key",
            "value": "",
            "type": "string",
        },
        {
            "field": "loader_type",
            "helper_text": "Select the loader type: General or News",
            "value": "YOU_DOT_COM",
            "type": "enum<string>",
        },
        {
            "field": "query",
            "helper_text": "The search query",
            "value": "",
            "type": "string",
        },
    ]

    # Common outputs and inputs
    _COMMON_OUTPUTS = [{"field": "output", "helper_text": "The output output"}]

    # Configuration patterns and their associated inputs/outputs
    _CONFIGS = {
        "YOU_DOT_COM": {"inputs": [], "outputs": [], "title": "You.com Web Search"},
        "YOU_DOT_COM_NEWS": {
            "inputs": [],
            "outputs": [],
            "title": "You.com Search News",
        },
    }

    # List of parameters that affect configuration
    _PARAMS = ["loader_type"]

    def __init__(
        self,
        id: Optional[str] = None,
        node_name: Optional[str] = None,
        execution_mode: Optional[str] = None,
        loader_type: str = "YOU_DOT_COM",
        api_key: str = "",
        query: str = "",
        **kwargs
    ):
        # Initialize with params
        params = {}
        params["loader_type"] = loader_type

        super().__init__(
            node_type="you_dot_com",
            params=params,
            id=id,
            node_name=node_name,
            execution_mode=execution_mode,
        )

        # Set input values
        if query is not None:
            self.inputs["query"] = query
        if api_key is not None:
            self.inputs["api_key"] = api_key
        if loader_type is not None:
            self.inputs["loader_type"] = loader_type

        # Update any additional inputs
        if kwargs:
            self.update_inputs(**kwargs)

    @property
    def output(self) -> str:
        """
        The output output


        Raises:
            AttributeError: If this output is not available for the current parameter values
        """
        return self.__getattr__("output")

    @classmethod
    def from_dict(cls, data: dict) -> "YouDotComNode":
        """Create a node instance from a dictionary."""
        inputs = data.get("inputs", {})
        id = data.get("id", None)
        name = data.get("name", None)
        execution_mode = data.get("execution_mode", None)
        return cls(**inputs, id=id, node_name=name, execution_mode=execution_mode)


@Node.register_node_type("exa_ai")
class ExaAiNode(Node):
    """
    Query the Exa search API

    ## Inputs
    ### Common Inputs
        loader_type: Select the loader type: General, Companies, or Research Papers
        query: The search query

    ## Outputs
    ### Common Outputs
        output: The output output
    """

    # Common inputs and outputs
    _COMMON_INPUTS = [
        {
            "field": "loader_type",
            "helper_text": "Select the loader type: General, Companies, or Research Papers",
            "value": "EXA_AI_SEARCH",
            "type": "enum<string>",
        },
        {
            "field": "query",
            "helper_text": "The search query",
            "value": "",
            "type": "string",
        },
    ]

    # Common outputs and inputs
    _COMMON_OUTPUTS = [{"field": "output", "helper_text": "The output output"}]

    # Configuration patterns and their associated inputs/outputs
    _CONFIGS = {
        "EXA_AI_SEARCH": {"inputs": [], "outputs": [], "title": "Exa AI Web Search"},
        "EXA_AI_SEARCH_COMPANIES": {
            "inputs": [],
            "outputs": [],
            "title": "Exa AI Companies",
        },
        "EXA_AI_SEARCH_RESEARCH_PAPERS": {
            "inputs": [],
            "outputs": [],
            "title": "Exa AI Research Papers",
        },
    }

    # List of parameters that affect configuration
    _PARAMS = ["loader_type"]

    def __init__(
        self,
        id: Optional[str] = None,
        node_name: Optional[str] = None,
        execution_mode: Optional[str] = None,
        loader_type: str = "EXA_AI_SEARCH",
        query: str = "",
        **kwargs
    ):
        # Initialize with params
        params = {}
        params["loader_type"] = loader_type

        super().__init__(
            node_type="exa_ai",
            params=params,
            id=id,
            node_name=node_name,
            execution_mode=execution_mode,
        )

        # Set input values
        if query is not None:
            self.inputs["query"] = query
        if loader_type is not None:
            self.inputs["loader_type"] = loader_type

        # Update any additional inputs
        if kwargs:
            self.update_inputs(**kwargs)

    @property
    def output(self) -> List[str]:
        """
        The output output


        Raises:
            AttributeError: If this output is not available for the current parameter values
        """
        return self.__getattr__("output")

    @classmethod
    def from_dict(cls, data: dict) -> "ExaAiNode":
        """Create a node instance from a dictionary."""
        inputs = data.get("inputs", {})
        id = data.get("id", None)
        name = data.get("name", None)
        execution_mode = data.get("execution_mode", None)
        return cls(**inputs, id=id, node_name=name, execution_mode=execution_mode)


@Node.register_node_type("google_search")
class GoogleSearchNode(Node):
    """
    Query the Google Search search API

    ## Inputs
    ### Common Inputs
        location: The location of the search
        num_results: The number of results to return
        query: The Google search query
        search_type: Select the search type: Web or Images

    ## Outputs
    ### Common Outputs
        snippets: The snippets of the Google search results
        urls: The URLs of the Google search results
    """

    # Common inputs and outputs
    _COMMON_INPUTS = [
        {
            "field": "location",
            "helper_text": "The location of the search",
            "value": "us",
            "type": "enum<string>",
        },
        {
            "field": "num_results",
            "helper_text": "The number of results to return",
            "value": 10,
            "type": "int32",
        },
        {
            "field": "query",
            "helper_text": "The Google search query",
            "value": "",
            "type": "string",
        },
        {
            "field": "search_type",
            "helper_text": "Select the search type: Web or Images",
            "value": "web",
            "type": "enum<string>",
        },
    ]

    # Common outputs and inputs
    _COMMON_OUTPUTS = [
        {
            "field": "snippets",
            "helper_text": "The snippets of the Google search results",
        },
        {"field": "urls", "helper_text": "The URLs of the Google search results"},
    ]

    # Configuration patterns and their associated inputs/outputs
    _CONFIGS = {}

    # List of parameters that affect configuration
    _PARAMS = []

    def __init__(
        self,
        id: Optional[str] = None,
        node_name: Optional[str] = None,
        execution_mode: Optional[str] = None,
        location: str = "us",
        num_results: int = 10,
        query: str = "",
        search_type: str = "web",
        **kwargs
    ):
        # Initialize with params
        params = {}

        super().__init__(
            node_type="google_search",
            params=params,
            id=id,
            node_name=node_name,
            execution_mode=execution_mode,
        )

        # Set input values
        if query is not None:
            self.inputs["query"] = query
        if num_results is not None:
            self.inputs["num_results"] = num_results
        if search_type is not None:
            self.inputs["search_type"] = search_type
        if location is not None:
            self.inputs["location"] = location

        # Update any additional inputs
        if kwargs:
            self.update_inputs(**kwargs)

    @property
    def snippets(self) -> List[str]:
        """
        The snippets of the Google search results


        Raises:
            AttributeError: If this output is not available for the current parameter values
        """
        return self.__getattr__("snippets")

    @property
    def urls(self) -> List[str]:
        """
        The URLs of the Google search results


        Raises:
            AttributeError: If this output is not available for the current parameter values
        """
        return self.__getattr__("urls")

    @classmethod
    def from_dict(cls, data: dict) -> "GoogleSearchNode":
        """Create a node instance from a dictionary."""
        inputs = data.get("inputs", {})
        id = data.get("id", None)
        name = data.get("name", None)
        execution_mode = data.get("execution_mode", None)
        return cls(**inputs, id=id, node_name=name, execution_mode=execution_mode)


@Node.register_node_type("google_alert_rss_reader")
class GoogleAlertRssReaderNode(Node):
    """
    Read the contents from a Google Alert RSS feed

    ## Inputs
    ### Common Inputs
        feed_link: The link of the Google Alert RSS feed you want to read
        timeframe: The publish dates of the items in the feed to read

    ## Outputs
    ### Common Outputs
        dates: The publish dates of the Google Alert RSS feed items
        links: The links of the Google Alert RSS feed items
        snippets: The snippets of the Google Alert RSS feed items
        titles: The titles of the Google Alert RSS feed items
    """

    # Common inputs and outputs
    _COMMON_INPUTS = [
        {
            "field": "feed_link",
            "helper_text": "The link of the Google Alert RSS feed you want to read",
            "value": "",
            "type": "string",
        },
        {
            "field": "timeframe",
            "helper_text": "The publish dates of the items in the feed to read",
            "value": "all",
            "type": "enum<string>",
        },
    ]

    # Common outputs and inputs
    _COMMON_OUTPUTS = [
        {
            "field": "dates",
            "helper_text": "The publish dates of the Google Alert RSS feed items",
        },
        {
            "field": "links",
            "helper_text": "The links of the Google Alert RSS feed items",
        },
        {
            "field": "snippets",
            "helper_text": "The snippets of the Google Alert RSS feed items",
        },
        {
            "field": "titles",
            "helper_text": "The titles of the Google Alert RSS feed items",
        },
    ]

    # Configuration patterns and their associated inputs/outputs
    _CONFIGS = {}

    # List of parameters that affect configuration
    _PARAMS = []

    def __init__(
        self,
        id: Optional[str] = None,
        node_name: Optional[str] = None,
        execution_mode: Optional[str] = None,
        feed_link: str = "",
        timeframe: str = "all",
        **kwargs
    ):
        # Initialize with params
        params = {}

        super().__init__(
            node_type="google_alert_rss_reader",
            params=params,
            id=id,
            node_name=node_name,
            execution_mode=execution_mode,
        )

        # Set input values
        if feed_link is not None:
            self.inputs["feed_link"] = feed_link
        if timeframe is not None:
            self.inputs["timeframe"] = timeframe

        # Update any additional inputs
        if kwargs:
            self.update_inputs(**kwargs)

    @property
    def dates(self) -> List[str]:
        """
        The publish dates of the Google Alert RSS feed items


        Raises:
            AttributeError: If this output is not available for the current parameter values
        """
        return self.__getattr__("dates")

    @property
    def links(self) -> List[str]:
        """
        The links of the Google Alert RSS feed items


        Raises:
            AttributeError: If this output is not available for the current parameter values
        """
        return self.__getattr__("links")

    @property
    def snippets(self) -> List[str]:
        """
        The snippets of the Google Alert RSS feed items


        Raises:
            AttributeError: If this output is not available for the current parameter values
        """
        return self.__getattr__("snippets")

    @property
    def titles(self) -> List[str]:
        """
        The titles of the Google Alert RSS feed items


        Raises:
            AttributeError: If this output is not available for the current parameter values
        """
        return self.__getattr__("titles")

    @classmethod
    def from_dict(cls, data: dict) -> "GoogleAlertRssReaderNode":
        """Create a node instance from a dictionary."""
        inputs = data.get("inputs", {})
        id = data.get("id", None)
        name = data.get("name", None)
        execution_mode = data.get("execution_mode", None)
        return cls(**inputs, id=id, node_name=name, execution_mode=execution_mode)


@Node.register_node_type("rss_feed_reader")
class RssFeedReaderNode(Node):
    """
    Read the contents from an RSS feed

    ## Inputs
    ### Common Inputs
        entries: The number of entries you want to fetch
        timeframe: The publish dates of the items in the feed to read
        url: The link of the RSS feed you want to read

    ## Outputs
    ### Common Outputs
        authors: The authors of the RSS feed items
        contents: The contents of the RSS feed items
        links: The links of the RSS feed items
        published_dates: The publish dates of the RSS feed items
        summaries: The summaries of the RSS feed items
        titles: The titles of the RSS feed items
    """

    # Common inputs and outputs
    _COMMON_INPUTS = [
        {
            "field": "entries",
            "helper_text": "The number of entries you want to fetch",
            "value": 10,
            "type": "int32",
        },
        {
            "field": "timeframe",
            "helper_text": "The publish dates of the items in the feed to read",
            "value": "all",
            "type": "enum<string>",
        },
        {
            "field": "url",
            "helper_text": "The link of the RSS feed you want to read",
            "value": "",
            "type": "string",
        },
    ]

    # Common outputs and inputs
    _COMMON_OUTPUTS = [
        {"field": "authors", "helper_text": "The authors of the RSS feed items"},
        {"field": "contents", "helper_text": "The contents of the RSS feed items"},
        {"field": "links", "helper_text": "The links of the RSS feed items"},
        {
            "field": "published_dates",
            "helper_text": "The publish dates of the RSS feed items",
        },
        {"field": "summaries", "helper_text": "The summaries of the RSS feed items"},
        {"field": "titles", "helper_text": "The titles of the RSS feed items"},
    ]

    # Configuration patterns and their associated inputs/outputs
    _CONFIGS = {}

    # List of parameters that affect configuration
    _PARAMS = []

    def __init__(
        self,
        id: Optional[str] = None,
        node_name: Optional[str] = None,
        execution_mode: Optional[str] = None,
        entries: int = 10,
        timeframe: str = "all",
        url: str = "",
        **kwargs
    ):
        # Initialize with params
        params = {}

        super().__init__(
            node_type="rss_feed_reader",
            params=params,
            id=id,
            node_name=node_name,
            execution_mode=execution_mode,
        )

        # Set input values
        if url is not None:
            self.inputs["url"] = url
        if timeframe is not None:
            self.inputs["timeframe"] = timeframe
        if entries is not None:
            self.inputs["entries"] = entries

        # Update any additional inputs
        if kwargs:
            self.update_inputs(**kwargs)

    @property
    def authors(self) -> List[str]:
        """
        The authors of the RSS feed items


        Raises:
            AttributeError: If this output is not available for the current parameter values
        """
        return self.__getattr__("authors")

    @property
    def contents(self) -> List[str]:
        """
        The contents of the RSS feed items


        Raises:
            AttributeError: If this output is not available for the current parameter values
        """
        return self.__getattr__("contents")

    @property
    def links(self) -> List[str]:
        """
        The links of the RSS feed items


        Raises:
            AttributeError: If this output is not available for the current parameter values
        """
        return self.__getattr__("links")

    @property
    def published_dates(self) -> List[str]:
        """
        The publish dates of the RSS feed items


        Raises:
            AttributeError: If this output is not available for the current parameter values
        """
        return self.__getattr__("published_dates")

    @property
    def summaries(self) -> List[str]:
        """
        The summaries of the RSS feed items


        Raises:
            AttributeError: If this output is not available for the current parameter values
        """
        return self.__getattr__("summaries")

    @property
    def titles(self) -> List[str]:
        """
        The titles of the RSS feed items


        Raises:
            AttributeError: If this output is not available for the current parameter values
        """
        return self.__getattr__("titles")

    @classmethod
    def from_dict(cls, data: dict) -> "RssFeedReaderNode":
        """Create a node instance from a dictionary."""
        inputs = data.get("inputs", {})
        id = data.get("id", None)
        name = data.get("name", None)
        execution_mode = data.get("execution_mode", None)
        return cls(**inputs, id=id, node_name=name, execution_mode=execution_mode)


@Node.register_node_type("csv_query")
class CsvQueryNode(Node):
    """
    Utilizes an LLM agent to query CSV(s). Delimeter for the CSV must be commas.

    ## Inputs
    ### Common Inputs
        csv: The CSV to be queried (file must be a CSV). Note: Ensure connecting node is of type File not text
        query: The question you want to be answered by the CSV
        stream: Whether to stream the results of the query

    ## Outputs
    ### Common Outputs
        output: The answer to the Query based on the CSV
    """

    # Common inputs and outputs
    _COMMON_INPUTS = [
        {
            "field": "csv",
            "helper_text": "The CSV to be queried (file must be a CSV). Note: Ensure connecting node is of type File not text",
            "value": None,
            "type": "file",
        },
        {
            "field": "query",
            "helper_text": "The question you want to be answered by the CSV",
            "value": "",
            "type": "string",
        },
        {
            "field": "stream",
            "helper_text": "Whether to stream the results of the query",
            "value": False,
            "type": "bool",
        },
    ]

    # Common outputs and inputs
    _COMMON_OUTPUTS = [
        {"field": "output", "helper_text": "The answer to the Query based on the CSV"}
    ]

    # Configuration patterns and their associated inputs/outputs
    _CONFIGS = {}

    # List of parameters that affect configuration
    _PARAMS = []

    def __init__(
        self,
        id: Optional[str] = None,
        node_name: Optional[str] = None,
        execution_mode: Optional[str] = None,
        csv: Optional[str] = None,
        query: str = "",
        stream: bool = False,
        **kwargs
    ):
        # Initialize with params
        params = {}

        super().__init__(
            node_type="csv_query",
            params=params,
            id=id,
            node_name=node_name,
            execution_mode=execution_mode,
        )

        # Set input values
        if csv is not None:
            self.inputs["csv"] = csv
        if query is not None:
            self.inputs["query"] = query
        if stream is not None:
            self.inputs["stream"] = stream

        # Update any additional inputs
        if kwargs:
            self.update_inputs(**kwargs)

    @property
    def output(self) -> str:
        """
        The answer to the Query based on the CSV


        Raises:
            AttributeError: If this output is not available for the current parameter values
        """
        return self.__getattr__("output")

    @classmethod
    def from_dict(cls, data: dict) -> "CsvQueryNode":
        """Create a node instance from a dictionary."""
        inputs = data.get("inputs", {})
        id = data.get("id", None)
        name = data.get("name", None)
        execution_mode = data.get("execution_mode", None)
        return cls(**inputs, id=id, node_name=name, execution_mode=execution_mode)


@Node.register_node_type("csv_reader")
class CsvReaderNode(Node):
    """
    Read the contents from a CSV file and output a list of the data for each column.

    ## Inputs
    ### Common Inputs
        columns: Define the name(s) of the columns that you want to read
        file_type: The type of file to read.
        processed_outputs: The processed_outputs input
        selected_file: The file to read.
    ### EXCEL
        sheet: The sheet input
        sheets: The sheets input

    ## Outputs
    ### Common Outputs
        [processed_outputs]: The [processed_outputs] output
    """

    # Common inputs and outputs
    _COMMON_INPUTS = [
        {
            "field": "columns",
            "helper_text": "Define the name(s) of the columns that you want to read",
            "value": [],
            "type": "vec<Dict[str, Any]>",
        },
        {
            "field": "file_type",
            "helper_text": "The type of file to read.",
            "value": "CSV",
            "type": "enum<string>",
        },
        {
            "field": "processed_outputs",
            "helper_text": "The processed_outputs input",
            "value": {},
            "type": "map<string, string>",
        },
        {
            "field": "selected_file",
            "helper_text": "The file to read.",
            "value": None,
            "type": "file",
        },
    ]

    # Common outputs and inputs
    _COMMON_OUTPUTS = [
        {
            "field": "[processed_outputs]",
            "helper_text": "The [processed_outputs] output",
        }
    ]

    # Configuration patterns and their associated inputs/outputs
    _CONFIGS = {
        "CSV": {"inputs": [], "outputs": []},
        "EXCEL": {
            "inputs": [
                {"field": "sheet", "type": "enum<string>"},
                {"field": "sheets", "type": "vec<string>", "value": []},
            ],
            "outputs": [],
        },
    }

    # List of parameters that affect configuration
    _PARAMS = ["file_type"]

    def __init__(
        self,
        id: Optional[str] = None,
        node_name: Optional[str] = None,
        execution_mode: Optional[str] = None,
        file_type: str = "CSV",
        columns: List[Any] = [],
        processed_outputs: Dict[str, str] = {},
        selected_file: Optional[str] = None,
        sheet: Optional[str] = None,
        sheets: List[str] = [],
        **kwargs
    ):
        # Initialize with params
        params = {}
        params["file_type"] = file_type

        super().__init__(
            node_type="csv_reader",
            params=params,
            id=id,
            node_name=node_name,
            execution_mode=execution_mode,
        )

        # Set input values
        if file_type is not None:
            self.inputs["file_type"] = file_type
        if selected_file is not None:
            self.inputs["selected_file"] = selected_file
        if processed_outputs is not None:
            self.inputs["processed_outputs"] = processed_outputs
        if columns is not None:
            self.inputs["columns"] = columns
        if sheet is not None:
            self.inputs["sheet"] = sheet
        if sheets is not None:
            self.inputs["sheets"] = sheets

        # Update any additional inputs
        if kwargs:
            self.update_inputs(**kwargs)

    @classmethod
    def from_dict(cls, data: dict) -> "CsvReaderNode":
        """Create a node instance from a dictionary."""
        inputs = data.get("inputs", {})
        id = data.get("id", None)
        name = data.get("name", None)
        execution_mode = data.get("execution_mode", None)
        return cls(**inputs, id=id, node_name=name, execution_mode=execution_mode)


@Node.register_node_type("csv_writer")
class CsvWriterNode(Node):
    """
    Create a CSV from data

    ## Inputs
    ### Common Inputs
        selected_option: Whether to create a new CSV or update an existing one.
    ### new
        columns: The columns to write to the CSV.
    ### old
        columns: The columns to write to the CSV.
        selected_file: The file to update.

    ## Outputs
    ### Common Outputs
        file: The CSV file created or updated.
    """

    # Common inputs and outputs
    _COMMON_INPUTS = [
        {
            "field": "selected_option",
            "helper_text": "Whether to create a new CSV or update an existing one.",
            "value": "new",
            "type": "enum<string>",
        }
    ]

    # Common outputs and inputs
    _COMMON_OUTPUTS = [
        {"field": "file", "helper_text": "The CSV file created or updated."}
    ]

    # Configuration patterns and their associated inputs/outputs
    _CONFIGS = {
        "new": {
            "inputs": [
                {
                    "field": "columns",
                    "type": "vec<Dict[str, Any]>",
                    "value": [],
                    "helper_text": "The columns to write to the CSV.",
                    "table": {
                        "name": {"helper_text": "The name of the column"},
                        "value": {"helper_text": "The value of the column"},
                    },
                }
            ],
            "outputs": [],
        },
        "old": {
            "inputs": [
                {
                    "field": "selected_file",
                    "type": "file",
                    "helper_text": "The file to update.",
                },
                {
                    "field": "columns",
                    "type": "vec<Dict[str, Any]>",
                    "value": [],
                    "helper_text": "The columns to write to the CSV.",
                    "table": {
                        "name": {"helper_text": "The name of the column"},
                        "value": {"helper_text": "The value of the column"},
                    },
                },
            ],
            "outputs": [],
        },
    }

    # List of parameters that affect configuration
    _PARAMS = ["selected_option"]

    def __init__(
        self,
        id: Optional[str] = None,
        node_name: Optional[str] = None,
        execution_mode: Optional[str] = None,
        selected_option: str = "new",
        columns: List[Any] = [],
        selected_file: Optional[str] = None,
        **kwargs
    ):
        # Initialize with params
        params = {}
        params["selected_option"] = selected_option

        super().__init__(
            node_type="csv_writer",
            params=params,
            id=id,
            node_name=node_name,
            execution_mode=execution_mode,
        )

        # Set input values
        if selected_option is not None:
            self.inputs["selected_option"] = selected_option
        if columns is not None:
            self.inputs["columns"] = columns
        if selected_file is not None:
            self.inputs["selected_file"] = selected_file

        # Update any additional inputs
        if kwargs:
            self.update_inputs(**kwargs)

    @property
    def file(self) -> str:
        """
        The CSV file created or updated.


        Raises:
            AttributeError: If this output is not available for the current parameter values
        """
        return self.__getattr__("file")

    @classmethod
    def from_dict(cls, data: dict) -> "CsvWriterNode":
        """Create a node instance from a dictionary."""
        inputs = data.get("inputs", {})
        id = data.get("id", None)
        name = data.get("name", None)
        execution_mode = data.get("execution_mode", None)
        return cls(**inputs, id=id, node_name=name, execution_mode=execution_mode)


@Node.register_node_type("create_list")
class CreateListNode(Node):
    """
    Create a list from input texts. Final list is ordered in the order of the inputs.

    ## Inputs
    ### Common Inputs
        type: The type of the list
    ### <T>
        list: Value to be added to the list

    ## Outputs
    ### <T>
        output: The created list
    """

    # Common inputs and outputs
    _COMMON_INPUTS = [
        {
            "field": "type",
            "helper_text": "The type of the list",
            "value": "string",
            "type": "enum<string>",
        }
    ]

    # Common outputs and inputs
    _COMMON_OUTPUTS = []

    # Configuration patterns and their associated inputs/outputs
    _CONFIGS = {
        "<T>": {
            "inputs": [
                {
                    "field": "list",
                    "type": "vec<<T>>",
                    "value": ["", ""],
                    "helper_text": "Value to be added to the list",
                }
            ],
            "outputs": [
                {
                    "field": "output",
                    "type": "vec<<T>>",
                    "helper_text": "The created list",
                }
            ],
        }
    }

    # List of parameters that affect configuration
    _PARAMS = ["type"]

    def __init__(
        self,
        id: Optional[str] = None,
        node_name: Optional[str] = None,
        execution_mode: Optional[str] = None,
        type: str = "string",
        list: List[Any] = ["", ""],
        **kwargs
    ):
        # Initialize with params
        params = {}
        params["type"] = type

        super().__init__(
            node_type="create_list",
            params=params,
            id=id,
            node_name=node_name,
            execution_mode=execution_mode,
        )

        # Set input values
        if type is not None:
            self.inputs["type"] = type
        if list is not None:
            self.inputs["list"] = list

        # Update any additional inputs
        if kwargs:
            self.update_inputs(**kwargs)

    @property
    def output(self) -> List[Any]:
        """
        The created list

        Available: <T>


        Raises:
            AttributeError: If this output is not available for the current parameter values
        """
        return self.__getattr__("output")

    @classmethod
    def from_dict(cls, data: dict) -> "CreateListNode":
        """Create a node instance from a dictionary."""
        inputs = data.get("inputs", {})
        id = data.get("id", None)
        name = data.get("name", None)
        execution_mode = data.get("execution_mode", None)
        return cls(**inputs, id=id, node_name=name, execution_mode=execution_mode)


@Node.register_node_type("combine_list")
class CombineListNode(Node):
    """
    Combine multiple lists into one list. Final list is ordered in the order of the input lists.

    ## Inputs
    ### Common Inputs
        type: The type of the list
    ### <T>
        list: List to be combined

    ## Outputs
    ### <T>
        output: The combined list
    """

    # Common inputs and outputs
    _COMMON_INPUTS = [
        {
            "field": "type",
            "helper_text": "The type of the list",
            "value": "string",
            "type": "enum<string>",
        }
    ]

    # Common outputs and inputs
    _COMMON_OUTPUTS = []

    # Configuration patterns and their associated inputs/outputs
    _CONFIGS = {
        "<T>": {
            "inputs": [
                {
                    "field": "list",
                    "type": "vec<vec<<T>>>",
                    "value": ["", ""],
                    "helper_text": "List to be combined",
                }
            ],
            "outputs": [
                {
                    "field": "output",
                    "type": "vec<<T>>",
                    "helper_text": "The combined list",
                }
            ],
        }
    }

    # List of parameters that affect configuration
    _PARAMS = ["type"]

    def __init__(
        self,
        id: Optional[str] = None,
        node_name: Optional[str] = None,
        execution_mode: Optional[str] = None,
        type: str = "string",
        list: List[List[Any]] = ["", ""],
        **kwargs
    ):
        # Initialize with params
        params = {}
        params["type"] = type

        super().__init__(
            node_type="combine_list",
            params=params,
            id=id,
            node_name=node_name,
            execution_mode=execution_mode,
        )

        # Set input values
        if type is not None:
            self.inputs["type"] = type
        if list is not None:
            self.inputs["list"] = list

        # Update any additional inputs
        if kwargs:
            self.update_inputs(**kwargs)

    @property
    def output(self) -> List[Any]:
        """
        The combined list

        Available: <T>


        Raises:
            AttributeError: If this output is not available for the current parameter values
        """
        return self.__getattr__("output")

    @classmethod
    def from_dict(cls, data: dict) -> "CombineListNode":
        """Create a node instance from a dictionary."""
        inputs = data.get("inputs", {})
        id = data.get("id", None)
        name = data.get("name", None)
        execution_mode = data.get("execution_mode", None)
        return cls(**inputs, id=id, node_name=name, execution_mode=execution_mode)


@Node.register_node_type("list_trimmer")
class ListTrimmerNode(Node):
    """
    Trim a list to just the sections you want. Enter enter the number of items or specify the section of the list that you want to keep.

    ## Inputs
    ### Common Inputs
        specify_section: Check this to specify a section of the list to keep. Leave unchecked to keep a specified number of items from the start.
        type: The type of the list
    ### When specify_section = True and type = '<T>'
        end_index: The ending index of the section to keep (exclusive).
        list: The list to trim
        start_index: The starting index of the section to keep (inclusive). The first item of the list is index 0.
    ### When specify_section = False and type = '<T>'
        item_to_keep: Check this to specify a section of the list to keep. Leave unchecked to keep a specified number of items.
        list: The list to trim

    ## Outputs
    ### When specify_section = False and type = '<T>'
        output: The trimmed list
    ### When specify_section = True and type = '<T>'
        output: The trimmed list
    """

    # Common inputs and outputs
    _COMMON_INPUTS = [
        {
            "field": "specify_section",
            "helper_text": "Check this to specify a section of the list to keep. Leave unchecked to keep a specified number of items from the start.",
            "value": False,
            "type": "bool",
        },
        {
            "field": "type",
            "helper_text": "The type of the list",
            "value": "string",
            "type": "enum<string>",
        },
    ]

    # Common outputs and inputs
    _COMMON_OUTPUTS = []

    # Configuration patterns and their associated inputs/outputs
    _CONFIGS = {
        "false**<T>": {
            "inputs": [
                {
                    "field": "item_to_keep",
                    "type": "int32",
                    "value": 0,
                    "helper_text": "Check this to specify a section of the list to keep. Leave unchecked to keep a specified number of items.",
                },
                {
                    "field": "list",
                    "type": "vec<<T>>",
                    "value": "",
                    "helper_text": "The list to trim",
                },
            ],
            "outputs": [
                {
                    "field": "output",
                    "type": "vec<<T>>",
                    "helper_text": "The trimmed list",
                }
            ],
        },
        "true**<T>": {
            "inputs": [
                {
                    "field": "start_index",
                    "type": "int32",
                    "value": 0,
                    "helper_text": "The starting index of the section to keep (inclusive). The first item of the list is index 0.",
                },
                {
                    "field": "end_index",
                    "type": "int32",
                    "value": 1,
                    "helper_text": "The ending index of the section to keep (exclusive).",
                },
                {
                    "field": "list",
                    "type": "vec<<T>>",
                    "value": "",
                    "helper_text": "The list to trim",
                },
            ],
            "outputs": [
                {
                    "field": "output",
                    "type": "vec<<T>>",
                    "helper_text": "The trimmed list",
                }
            ],
        },
    }

    # List of parameters that affect configuration
    _PARAMS = ["specify_section", "type"]

    def __init__(
        self,
        id: Optional[str] = None,
        node_name: Optional[str] = None,
        execution_mode: Optional[str] = None,
        specify_section: bool = False,
        type: str = "string",
        end_index: int = 1,
        item_to_keep: int = 0,
        list: List[Any] = [],
        start_index: int = 0,
        **kwargs
    ):
        # Initialize with params
        params = {}
        params["specify_section"] = specify_section
        params["type"] = type

        super().__init__(
            node_type="list_trimmer",
            params=params,
            id=id,
            node_name=node_name,
            execution_mode=execution_mode,
        )

        # Set input values
        if type is not None:
            self.inputs["type"] = type
        if specify_section is not None:
            self.inputs["specify_section"] = specify_section
        if item_to_keep is not None:
            self.inputs["item_to_keep"] = item_to_keep
        if list is not None:
            self.inputs["list"] = list
        if start_index is not None:
            self.inputs["start_index"] = start_index
        if end_index is not None:
            self.inputs["end_index"] = end_index

        # Update any additional inputs
        if kwargs:
            self.update_inputs(**kwargs)

    @property
    def output(self) -> List[Any]:
        """
        The trimmed list

        Available: When specify_section = False and type = '<T>', When specify_section = True and type = '<T>'


        Raises:
            AttributeError: If this output is not available for the current parameter values
        """
        return self.__getattr__("output")

    @classmethod
    def from_dict(cls, data: dict) -> "ListTrimmerNode":
        """Create a node instance from a dictionary."""
        inputs = data.get("inputs", {})
        id = data.get("id", None)
        name = data.get("name", None)
        execution_mode = data.get("execution_mode", None)
        return cls(**inputs, id=id, node_name=name, execution_mode=execution_mode)


@Node.register_node_type("duplicate_list")
class DuplicateListNode(Node):
    """
    Create a new list by duplicating a single item with the size of the new list either matching the size of another list, or a specified size.

    ## Inputs
    ### Common Inputs
        specify_list_size: Check this box if you want to manually specify the list size. In this case 'Match List Size' will not be used.
        type: The type of the list
    ### When specify_list_size = True and type = '<T>'
        input_field: Item to duplicate
        list_size: The size of the new list
    ### When specify_list_size = False and type = '<T>'
        input_field: Item to duplicate
        list_size_to_match: The size of the list you want to match

    ## Outputs
    ### When specify_list_size = True and type = '<T>'
        output: The duplicated list
    ### When specify_list_size = False and type = '<T>'
        output: The duplicated list
    """

    # Common inputs and outputs
    _COMMON_INPUTS = [
        {
            "field": "specify_list_size",
            "helper_text": "Check this box if you want to manually specify the list size. In this case 'Match List Size' will not be used.",
            "value": False,
            "type": "bool",
        },
        {
            "field": "type",
            "helper_text": "The type of the list",
            "value": "string",
            "type": "enum<string>",
        },
    ]

    # Common outputs and inputs
    _COMMON_OUTPUTS = []

    # Configuration patterns and their associated inputs/outputs
    _CONFIGS = {
        "true**<T>": {
            "inputs": [
                {
                    "field": "list_size",
                    "type": "int32",
                    "value": 1,
                    "helper_text": "The size of the new list",
                },
                {
                    "field": "input_field",
                    "type": "<T>",
                    "value": "",
                    "helper_text": "Item to duplicate",
                },
            ],
            "outputs": [
                {
                    "field": "output",
                    "type": "vec<<T>>",
                    "helper_text": "The duplicated list",
                }
            ],
        },
        "false**<T>": {
            "inputs": [
                {
                    "field": "list_size_to_match",
                    "type": "vec<string>",
                    "value": "",
                    "helper_text": "The size of the list you want to match",
                },
                {
                    "field": "input_field",
                    "type": "<T>",
                    "value": "",
                    "helper_text": "Item to duplicate",
                },
            ],
            "outputs": [
                {
                    "field": "output",
                    "type": "vec<<T>>",
                    "helper_text": "The duplicated list",
                }
            ],
        },
    }

    # List of parameters that affect configuration
    _PARAMS = ["specify_list_size", "type"]

    def __init__(
        self,
        id: Optional[str] = None,
        node_name: Optional[str] = None,
        execution_mode: Optional[str] = None,
        specify_list_size: bool = False,
        type: str = "string",
        list_size: int = 1,
        list_size_to_match: List[str] = [],
        input_field: Optional[Any] = None,
        **kwargs
    ):
        # Initialize with params
        params = {}
        params["specify_list_size"] = specify_list_size
        params["type"] = type

        super().__init__(
            node_type="duplicate_list",
            params=params,
            id=id,
            node_name=node_name,
            execution_mode=execution_mode,
        )

        # Set input values
        if type is not None:
            self.inputs["type"] = type
        if specify_list_size is not None:
            self.inputs["specify_list_size"] = specify_list_size
        if list_size is not None:
            self.inputs["list_size"] = list_size
        if input_field is not None:
            self.inputs["input_field"] = input_field
        if list_size_to_match is not None:
            self.inputs["list_size_to_match"] = list_size_to_match
        if input_field is not None:
            self.inputs["input_field"] = input_field

        # Update any additional inputs
        if kwargs:
            self.update_inputs(**kwargs)

    @property
    def output(self) -> List[Any]:
        """
        The duplicated list

        Available: When specify_list_size = True and type = '<T>', When specify_list_size = False and type = '<T>'


        Raises:
            AttributeError: If this output is not available for the current parameter values
        """
        return self.__getattr__("output")

    @classmethod
    def from_dict(cls, data: dict) -> "DuplicateListNode":
        """Create a node instance from a dictionary."""
        inputs = data.get("inputs", {})
        id = data.get("id", None)
        name = data.get("name", None)
        execution_mode = data.get("execution_mode", None)
        return cls(**inputs, id=id, node_name=name, execution_mode=execution_mode)


@Node.register_node_type("flatten_list")
class FlattenListNode(Node):
    """
    Flatten list of lists into a single list. For example, [[a, b], [c, d]] becomes [a,b,c,d].

    ## Inputs
    ### Common Inputs
        type: The type of the list
    ### <T>
        list_of_lists: List of lists to be flattened

    ## Outputs
    ### <T>
        flattened_list: The flattened list
    """

    # Common inputs and outputs
    _COMMON_INPUTS = [
        {
            "field": "type",
            "helper_text": "The type of the list",
            "value": "string",
            "type": "enum<string>",
        }
    ]

    # Common outputs and inputs
    _COMMON_OUTPUTS = []

    # Configuration patterns and their associated inputs/outputs
    _CONFIGS = {
        "<T>": {
            "inputs": [
                {
                    "field": "list_of_lists",
                    "type": "vec<vec<<T>>>",
                    "value": "",
                    "helper_text": "List of lists to be flattened",
                }
            ],
            "outputs": [
                {
                    "field": "flattened_list",
                    "type": "vec<<T>>",
                    "helper_text": "The flattened list",
                }
            ],
        }
    }

    # List of parameters that affect configuration
    _PARAMS = ["type"]

    def __init__(
        self,
        id: Optional[str] = None,
        node_name: Optional[str] = None,
        execution_mode: Optional[str] = None,
        type: str = "string",
        list_of_lists: List[List[Any]] = [],
        **kwargs
    ):
        # Initialize with params
        params = {}
        params["type"] = type

        super().__init__(
            node_type="flatten_list",
            params=params,
            id=id,
            node_name=node_name,
            execution_mode=execution_mode,
        )

        # Set input values
        if type is not None:
            self.inputs["type"] = type
        if list_of_lists is not None:
            self.inputs["list_of_lists"] = list_of_lists

        # Update any additional inputs
        if kwargs:
            self.update_inputs(**kwargs)

    @property
    def flattened_list(self) -> List[Any]:
        """
        The flattened list

        Available: <T>


        Raises:
            AttributeError: If this output is not available for the current parameter values
        """
        return self.__getattr__("flattened_list")

    @classmethod
    def from_dict(cls, data: dict) -> "FlattenListNode":
        """Create a node instance from a dictionary."""
        inputs = data.get("inputs", {})
        id = data.get("id", None)
        name = data.get("name", None)
        execution_mode = data.get("execution_mode", None)
        return cls(**inputs, id=id, node_name=name, execution_mode=execution_mode)


@Node.register_node_type("join_list_item")
class JoinListItemNode(Node):
    """
    Join a list of items into a single string. If join_by_newline is true, the items are joined by a newline character.

    ## Inputs
    ### Common Inputs
        join_by_newline: Separate each line in the final output with a new line
        type: The type of the list
    ### When join_by_newline = False
        join_characters: Use a specified character to join list items into a single string
    ### When type = '<T>'
        list: List of items to be joined

    ## Outputs
    ### Common Outputs
        joined_text: The joined string
    """

    # Common inputs and outputs
    _COMMON_INPUTS = [
        {
            "field": "join_by_newline",
            "helper_text": "Separate each line in the final output with a new line",
            "value": False,
            "type": "bool",
        },
        {
            "field": "type",
            "helper_text": "The type of the list",
            "value": "string",
            "type": "enum<string>",
        },
    ]

    # Common outputs and inputs
    _COMMON_OUTPUTS = [{"field": "joined_text", "helper_text": "The joined string"}]

    # Configuration patterns and their associated inputs/outputs
    _CONFIGS = {
        "false**(*)": {
            "inputs": [
                {
                    "field": "join_characters",
                    "type": "string",
                    "value": "",
                    "helper_text": "Use a specified character to join list items into a single string",
                }
            ],
            "outputs": [],
        },
        "(*)**<T>": {
            "inputs": [
                {
                    "field": "list",
                    "type": "vec<<T>>",
                    "value": "",
                    "helper_text": "List of items to be joined",
                }
            ],
            "outputs": [],
        },
    }

    # List of parameters that affect configuration
    _PARAMS = ["join_by_newline", "type"]

    def __init__(
        self,
        id: Optional[str] = None,
        node_name: Optional[str] = None,
        execution_mode: Optional[str] = None,
        join_by_newline: bool = False,
        type: str = "string",
        join_characters: str = "",
        list: List[Any] = [],
        **kwargs
    ):
        # Initialize with params
        params = {}
        params["join_by_newline"] = join_by_newline
        params["type"] = type

        super().__init__(
            node_type="join_list_item",
            params=params,
            id=id,
            node_name=node_name,
            execution_mode=execution_mode,
        )

        # Set input values
        if type is not None:
            self.inputs["type"] = type
        if join_by_newline is not None:
            self.inputs["join_by_newline"] = join_by_newline
        if join_characters is not None:
            self.inputs["join_characters"] = join_characters
        if list is not None:
            self.inputs["list"] = list

        # Update any additional inputs
        if kwargs:
            self.update_inputs(**kwargs)

    @property
    def joined_text(self) -> str:
        """
        The joined string


        Raises:
            AttributeError: If this output is not available for the current parameter values
        """
        return self.__getattr__("joined_text")

    @classmethod
    def from_dict(cls, data: dict) -> "JoinListItemNode":
        """Create a node instance from a dictionary."""
        inputs = data.get("inputs", {})
        id = data.get("id", None)
        name = data.get("name", None)
        execution_mode = data.get("execution_mode", None)
        return cls(**inputs, id=id, node_name=name, execution_mode=execution_mode)


@Node.register_node_type("csv_to_excel")
class CsvToExcelNode(Node):
    """
    Convert a CSV file into XLSX

    ## Inputs
    ### Common Inputs
        csv_file: The CSV file to convert.
        horizontal_alignment: The horizontal alignment of the text
        max_column_width: The maximum width of the columns
        vertical_alignment: The vertical alignment of the text
        wrap_text: Enable text wrapping

    ## Outputs
    ### Common Outputs
        xlsx_file: The Excel file created.
    """

    # Common inputs and outputs
    _COMMON_INPUTS = [
        {
            "field": "csv_file",
            "helper_text": "The CSV file to convert.",
            "value": None,
            "type": "file",
        },
        {
            "field": "horizontal_alignment",
            "helper_text": "The horizontal alignment of the text",
            "value": "left",
            "type": "enum<string>",
        },
        {
            "field": "max_column_width",
            "helper_text": "The maximum width of the columns",
            "value": 100,
            "type": "int32",
        },
        {
            "field": "vertical_alignment",
            "helper_text": "The vertical alignment of the text",
            "value": "top",
            "type": "enum<string>",
        },
        {
            "field": "wrap_text",
            "helper_text": "Enable text wrapping",
            "value": True,
            "type": "bool",
        },
    ]

    # Common outputs and inputs
    _COMMON_OUTPUTS = [{"field": "xlsx_file", "helper_text": "The Excel file created."}]

    # Configuration patterns and their associated inputs/outputs
    _CONFIGS = {}

    # List of parameters that affect configuration
    _PARAMS = []

    def __init__(
        self,
        id: Optional[str] = None,
        node_name: Optional[str] = None,
        execution_mode: Optional[str] = None,
        csv_file: Optional[str] = None,
        horizontal_alignment: str = "left",
        max_column_width: int = 100,
        vertical_alignment: str = "top",
        wrap_text: bool = True,
        **kwargs
    ):
        # Initialize with params
        params = {}

        super().__init__(
            node_type="csv_to_excel",
            params=params,
            id=id,
            node_name=node_name,
            execution_mode=execution_mode,
        )

        # Set input values
        if csv_file is not None:
            self.inputs["csv_file"] = csv_file
        if wrap_text is not None:
            self.inputs["wrap_text"] = wrap_text
        if max_column_width is not None:
            self.inputs["max_column_width"] = max_column_width
        if horizontal_alignment is not None:
            self.inputs["horizontal_alignment"] = horizontal_alignment
        if vertical_alignment is not None:
            self.inputs["vertical_alignment"] = vertical_alignment

        # Update any additional inputs
        if kwargs:
            self.update_inputs(**kwargs)

    @property
    def xlsx_file(self) -> str:
        """
        The Excel file created.


        Raises:
            AttributeError: If this output is not available for the current parameter values
        """
        return self.__getattr__("xlsx_file")

    @classmethod
    def from_dict(cls, data: dict) -> "CsvToExcelNode":
        """Create a node instance from a dictionary."""
        inputs = data.get("inputs", {})
        id = data.get("id", None)
        name = data.get("name", None)
        execution_mode = data.get("execution_mode", None)
        return cls(**inputs, id=id, node_name=name, execution_mode=execution_mode)


@Node.register_node_type("text_formatter")
class TextFormatterNode(Node):
    """
    Format text based off a specified formatter

    ## Inputs
    ### Common Inputs
        formatter: The formatter to apply to the text
        text: The text to format
    ### Truncate
        max_num_token: The maximum number of tokens to truncate the text to

    ## Outputs
    ### Common Outputs
        output: The formatted text
    """

    # Common inputs and outputs
    _COMMON_INPUTS = [
        {
            "field": "formatter",
            "helper_text": "The formatter to apply to the text",
            "value": "To Uppercase",
            "type": "enum<string>",
        },
        {
            "field": "text",
            "helper_text": "The text to format",
            "value": "",
            "type": "string",
        },
    ]

    # Common outputs and inputs
    _COMMON_OUTPUTS = [{"field": "output", "helper_text": "The formatted text"}]

    # Configuration patterns and their associated inputs/outputs
    _CONFIGS = {
        "Truncate": {
            "inputs": [
                {
                    "field": "max_num_token",
                    "type": "int32",
                    "value": 0,
                    "helper_text": "The maximum number of tokens to truncate the text to",
                }
            ],
            "outputs": [],
        }
    }

    # List of parameters that affect configuration
    _PARAMS = ["formatter"]

    def __init__(
        self,
        id: Optional[str] = None,
        node_name: Optional[str] = None,
        execution_mode: Optional[str] = None,
        formatter: str = "To Uppercase",
        max_num_token: int = 0,
        text: str = "",
        **kwargs
    ):
        # Initialize with params
        params = {}
        params["formatter"] = formatter

        super().__init__(
            node_type="text_formatter",
            params=params,
            id=id,
            node_name=node_name,
            execution_mode=execution_mode,
        )

        # Set input values
        if text is not None:
            self.inputs["text"] = text
        if formatter is not None:
            self.inputs["formatter"] = formatter
        if max_num_token is not None:
            self.inputs["max_num_token"] = max_num_token

        # Update any additional inputs
        if kwargs:
            self.update_inputs(**kwargs)

    @property
    def output(self) -> str:
        """
        The formatted text


        Raises:
            AttributeError: If this output is not available for the current parameter values
        """
        return self.__getattr__("output")

    @classmethod
    def from_dict(cls, data: dict) -> "TextFormatterNode":
        """Create a node instance from a dictionary."""
        inputs = data.get("inputs", {})
        id = data.get("id", None)
        name = data.get("name", None)
        execution_mode = data.get("execution_mode", None)
        return cls(**inputs, id=id, node_name=name, execution_mode=execution_mode)


@Node.register_node_type("json_operations")
class JsonOperationsNode(Node):
    """


    ## Inputs
    ### Common Inputs
        sub_type: The sub_type input

    ## Outputs
        None
    """

    # Common inputs and outputs
    _COMMON_INPUTS = [
        {
            "field": "sub_type",
            "helper_text": "The sub_type input",
            "value": "",
            "type": "string",
        }
    ]

    # Common outputs and inputs
    _COMMON_OUTPUTS = []

    # Configuration patterns and their associated inputs/outputs
    _CONFIGS = {}

    # List of parameters that affect configuration
    _PARAMS = []

    def __init__(
        self,
        id: Optional[str] = None,
        node_name: Optional[str] = None,
        execution_mode: Optional[str] = None,
        sub_type: str = "",
        **kwargs
    ):
        # Initialize with params
        params = {}

        super().__init__(
            node_type="json_operations",
            params=params,
            id=id,
            node_name=node_name,
            execution_mode=execution_mode,
        )

        # Set input values
        if sub_type is not None:
            self.inputs["sub_type"] = sub_type

        # Update any additional inputs
        if kwargs:
            self.update_inputs(**kwargs)

    @classmethod
    def from_dict(cls, data: dict) -> "JsonOperationsNode":
        """Create a node instance from a dictionary."""
        inputs = data.get("inputs", {})
        id = data.get("id", None)
        name = data.get("name", None)
        execution_mode = data.get("execution_mode", None)
        return cls(**inputs, id=id, node_name=name, execution_mode=execution_mode)


@Node.register_node_type("list_operations")
class ListOperationsNode(Node):
    """


    ## Inputs
    ### Common Inputs
        sub_type: The sub_type input

    ## Outputs
        None
    """

    # Common inputs and outputs
    _COMMON_INPUTS = [
        {
            "field": "sub_type",
            "helper_text": "The sub_type input",
            "value": "",
            "type": "string",
        }
    ]

    # Common outputs and inputs
    _COMMON_OUTPUTS = []

    # Configuration patterns and their associated inputs/outputs
    _CONFIGS = {}

    # List of parameters that affect configuration
    _PARAMS = []

    def __init__(
        self,
        id: Optional[str] = None,
        node_name: Optional[str] = None,
        execution_mode: Optional[str] = None,
        sub_type: str = "",
        **kwargs
    ):
        # Initialize with params
        params = {}

        super().__init__(
            node_type="list_operations",
            params=params,
            id=id,
            node_name=node_name,
            execution_mode=execution_mode,
        )

        # Set input values
        if sub_type is not None:
            self.inputs["sub_type"] = sub_type

        # Update any additional inputs
        if kwargs:
            self.update_inputs(**kwargs)

    @classmethod
    def from_dict(cls, data: dict) -> "ListOperationsNode":
        """Create a node instance from a dictionary."""
        inputs = data.get("inputs", {})
        id = data.get("id", None)
        name = data.get("name", None)
        execution_mode = data.get("execution_mode", None)
        return cls(**inputs, id=id, node_name=name, execution_mode=execution_mode)


@Node.register_node_type("integration")
class IntegrationNode(Node):
    """
    Integration

    ## Inputs
    ### Common Inputs
        action: The action input
        function: The function input
        integration: The integration input
        integration_type: The integration_type input
    ### When integration_type = 'Google Sheets' and action = 'extract_to_table'
        add_columns_manually: The add_columns_manually input
        additional_context: The additional_context input
        extract_multiple_rows: The extract_multiple_rows input
        manual_columns: The manual_columns input
        sheet_id: The sheet_id input
        text_for_extraction: The text_for_extraction input
    ### When integration_type = 'Hubspot' and action = 'create_deal'
        amount: The amount input
        associated_object_id: The associated_object_id input
        associated_object_type: The associated_object_type input
        closedate: The closedate input
        dealname: The dealname input
        dealstage: The dealstage input
        pipeline: The pipeline input
    ### When integration_type = 'Hubspot' and action = 'create_company'
        associated_object_id: The associated_object_id input
        associated_object_type: The associated_object_type input
        city: The city input
        domain: The domain input
        industry: The industry input
        name: The name input
        phone: The phone input
        state: The state input
    ### When integration_type = 'Hubspot' and action = 'create_contact'
        associated_object_id: The associated_object_id input
        associated_object_type: The associated_object_type input
        company: The company input
        email: The email input
        firstname: The firstname input
        lastname: The lastname input
        phone: The phone input
        website: The website input
    ### When integration_type = 'Hubspot' and action = 'create_ticket'
        associated_object_id: The associated_object_id input
        associated_object_type: The associated_object_type input
        hs_pipeline: The hs_pipeline input
        hs_pipeline_stage: The hs_pipeline_stage input
        hs_ticket_priority: The hs_ticket_priority input
        subject: The subject input
    ### When integration_type = 'Hubspot' and action = 'create_note'
        associated_object_id: The associated_object_id input
        associated_object_type: The associated_object_type input
        body: The body input
    ### When integration_type = 'Hubspot' and action = 'create_call'
        associated_object_id: The associated_object_id input
        associated_object_type: The associated_object_type input
        body: The body input
        duration: The duration input
        from_number: The from_number input
        title: The title input
        to_number: The to_number input
    ### When integration_type = 'Hubspot' and action = 'create_task'
        associated_object_id: The associated_object_id input
        associated_object_type: The associated_object_type input
        body: The body input
        priority: The priority input
        status: The status input
        subject: The subject input
    ### When integration_type = 'Hubspot' and action = 'create_meeting'
        associated_object_id: The associated_object_id input
        associated_object_type: The associated_object_type input
        body: The body input
        end_time: The end_time input
        meeting_notes: The meeting_notes input
        start_time: The start_time input
        title: The title input
    ### When integration_type = 'Hubspot' and action = 'create_email'
        associated_object_id: The associated_object_id input
        associated_object_type: The associated_object_type input
        direction: The direction input
        recipient_email: The recipient_email input
        sender_email: The sender_email input
        subject: The subject input
        text: The text input
    ### When integration_type = 'Outlook' and action = 'send_email'
        attachments: The attachments input
        body: The body input
        format: The format input
        recipients: The recipients input
        subject: The subject input
    ### When integration_type = 'Outlook' and action = 'send_reply'
        attachments: The attachments input
        body: The body input
        email_id: The email_id input
        format: The format input
        recipients: The recipients input
    ### When integration_type = 'Google Calendar' and action = 'new_event'
        attendees: The attendees input
        description: The description input
        duration: The duration input
        event_name: The event_name input
        location: The location input
        start_datetime: The start_datetime input
    ### When integration_type = 'Microsoft Calendar' and action = 'new_event'
        attendees: The attendees input
        body: The body input
        calendar: The calendar input
        duration: The duration input
        location: The location input
        start_datetime: The start_datetime input
        subject: The subject input
    ### When integration_type = 'Github' and action = 'create_pr'
        base: The base input
        body: The body input
        head: The head input
        title: The title input
    ### When integration_type = 'Airtable'
        base_id: The base_id input
        processed_outputs: The processed_outputs input
        table_id: The table_id input
    ### When integration_type = 'Mailgun' and action = 'send_mail'
        bcc_recipients: The bcc_recipients input
        body: The body input
        cc_recipients: The cc_recipients input
        domain: The domain input
        from_email: The from_email input
        from_name: The from_name input
        recipients: The recipients input
        subject: The subject input
    ### When integration_type = 'Gmail'
        body: The body input
        recipients: The recipients input
    ### When integration_type = 'Outlook' and action = 'create_draft'
        body: The body input
        format: The format input
        recipients: The recipients input
        subject: The subject input
    ### When integration_type = 'Outlook' and action = 'draft_reply'
        body: The body input
        email_id: The email_id input
        format: The format input
        recipients: The recipients input
    ### When integration_type = 'Github' and action = 'update_pr'
        body: The body input
        pull_number: The pull_number input
        title: The title input
    ### When integration_type = 'Zendesk' and action = 'create_ticket'
        body: The body input
        requester_email: The requester_email input
        requester_name: The requester_name input
        subject: The subject input
    ### When integration_type = 'Github' and action = 'read_file'
        branch_name: The branch_name input
        file_name: The file_name input
    ### When integration_type = 'Google Calendar'
        calendar: The calendar input
    ### When integration_type = 'Databricks'
        catalog_name: The catalog_name input
        schema_name: The schema_name input
        selected_input_dynamic_handle_names: The selected_input_dynamic_handle_names input
        table_name: The table_name input
        warehouse_id: The warehouse_id input
    ### When integration_type = 'Slack'
        channel: The channel input
        team: The team input
    ### When integration_type = 'Discord' and action = 'send_message'
        channel_name: The channel_name input
        message: The message input
    ### When integration_type = 'Teams' and action = 'send_message'
        channel_name: The channel_name input
        message: The message input
        team_name: The team_name input
    ### When integration_type = 'MongoDB'
        collection: The collection input
        query: The query input
    ### When integration_type = 'Weaviate'
        collection: The collection input
        embedding_model: The embedding_model input
        properties: The properties input
        query: The query input
    ### When integration_type = 'Linear' and action = 'create_comment'
        comment: The comment input
        issue_name: The issue_name input
    ### When integration_type = 'PeopleDataLabs' and action = 'enrich_person'
        company: The company input
        email: The email input
        first_name: The first_name input
        last_name: The last_name input
        location: The location input
        profile_url: The profile_url input
    ### When integration_type = 'Apollo' and action = 'fetch_companies'
        company_name: The company_name input
        keywords: The keywords input
        location: The location input
        max_size: The max_size input
        min_size: The min_size input
        num_results: The num_results input
    ### When integration_type = 'Apollo' and action = 'enrich_contact'
        company_name: The company_name input
        domain: The domain input
        first_name_input: The first_name_input input
        last_name_input: The last_name_input input
        linkedin_url_input: The linkedin_url_input input
    ### When integration_type = 'PeopleDataLabs' and action = 'search_companies'
        company_size_ranges: The company_size_ranges input
        country: The country input
        founded_year_range: The founded_year_range input
        industries: The industries input
        number_of_results: The number_of_results input
        tags: The tags input
    ### When integration_type = 'GoHighLevel' and action = 'create_opportunity'
        contact_name: The contact_name input
        name: The name input
        pipeline_name: The pipeline_name input
        status: The status input
        value: The value input
    ### When integration_type = 'Microsoft' and action = 'add_file'
        content: The content input
        file_name: The file_name input
    ### When integration_type = 'Dropbox' and action = 'post_file'
        content: The content input
        file_name: The file_name input
    ### When integration_type = 'PeopleDataLabs' and action = 'search_people'
        country: The country input
        job_company_names: The job_company_names input
        job_titles: The job_titles input
        number_of_results: The number_of_results input
        skills: The skills input
    ### When integration_type = 'Snowflake'
        database: The database input
        query: The query input
        query_agent_model: The query_agent_model input
        query_type: The query_type input
        schema: The schema input
        sql_generation_model: The sql_generation_model input
        warehouse: The warehouse input
    ### When integration_type = 'Outlook' and action = 'read_email' and use_date = True and use_exact_date = False
        date_range: The date_range input
    ### When integration_type = 'Slack' and action = 'read_message' and use_date = True and use_exact_date = False
        date_range: The date_range input
    ### When integration_type = 'Linear' and action = 'create_issue'
        description: The description input
        team_name: The team_name input
        title: The title input
    ### When integration_type = 'Apollo' and action = 'enrich_company'
        domain: The domain input
    ### When integration_type = 'Copper' and action = 'create_lead'
        email: The email input
        name: The name input
    ### When integration_type = 'GoHighLevel' and action = 'create_contact'
        email: The email input
        first_name: The first_name input
        last_name: The last_name input
        phone: The phone input
    ### When integration_type = 'Mailgun' and action = 'add_contact_to_mailing_list'
        email: The email input
        list_name: The list_name input
        name: The name input
    ### When integration_type = 'Gmail' and action = 'draft_reply'
        email_id: The email_id input
    ### When integration_type = 'Gmail' and action = 'send_reply'
        email_id: The email_id input
    ### When integration_type = 'Pinecone' and action = 'query_pinecone'
        embedding_model: The embedding_model input
        index: The index input
        namespace: The namespace input
        query: The query input
    ### When integration_type = 'Google Calendar' and action = 'check_availability'
        end_date: The end_date input
        end_work_time: The end_work_time input
        slot_duration: The slot_duration input
        start_date: The start_date input
        start_work_time: The start_work_time input
        timezone: The timezone input
    ### When integration_type = 'Microsoft Calendar' and action = 'check_availability'
        end_date: The end_date input
        end_work_time: The end_work_time input
        slot_duration: The slot_duration input
        start_date: The start_date input
        start_work_time: The start_work_time input
        timezone: The timezone input
    ### When integration_type = 'PeopleDataLabs' and action = 'search_people_query'
        es_query: The es_query input
        number_of_results: The number_of_results input
        sql: The sql input
    ### When integration_type = 'PeopleDataLabs' and action = 'search_companies_query'
        es_query: The es_query input
        number_of_results: The number_of_results input
        sql: The sql input
    ### When integration_type = 'Outlook' and action = 'read_email' and use_date = True and use_exact_date = True
        exact_date: The exact_date input
    ### When integration_type = 'Slack' and action = 'read_message' and use_date = True and use_exact_date = True
        exact_date: The exact_date input
    ### When integration_type = 'Google Drive' and action = 'save_drive'
        file: The file input
        file_name: The file_name input
    ### When integration_type = 'Google Docs'
        file_id: The file_id input
    ### When integration_type = 'Google Drive'
        file_id: The file_id input
    ### When integration_type = 'Box' and action = 'upload_files'
        files: The files input
    ### When integration_type = 'SugarCRM' and action = 'get_records'
        filter: The filter input
        module: The module input
    ### When integration_type = 'Bland AI'
        first_sentence: The first_sentence input
        model: The model input
        pathway_id: The pathway_id input
        phone_number: The phone_number input
        task: The task input
        temperature: The temperature input
        transfer_number: The transfer_number input
        wait_for_greeting: The wait_for_greeting input
    ### When integration_type = 'Dropbox'
        folder_id: The folder_id input
    ### When integration_type = 'Box'
        folder_id: The folder_id input
    ### When integration_type = 'Typeform'
        form_id: The form_id input
    ### When integration_type = 'Elasticsearch' and action = 'search_index'
        index: The index input
        query: The query input
    ### When integration_type = 'Algolia'
        index: The index input
        query: The query input
        return_mode: The return_mode input
    ### When integration_type = 'Outlook' and action = 'read_email'
        item_id: The item_id input
        num_messages: Specify the last n number of emails
        use_date: Toggle to use dates
        use_exact_date: Switch between exact date range and relative dates
    ### When integration_type = 'Microsoft'
        item_id: The item_id input
    ### When integration_type = 'Notion'
        item_id: The item_id input
        processed_outputs: The processed_outputs input
    ### When integration_type = 'Slack' and action = 'send_message'
        message: The message input
    ### When integration_type = 'Google Sheets'
        model: The model input
        processed_outputs: The processed_outputs input
        provider: The provider input
        sheet_id: The sheet_id input
    ### When integration_type = 'PeopleDataLabs' and action = 'enrich_company'
        name: The name input
        profile: The profile input
        website: The website input
    ### When integration_type = 'Slack' and action = 'read_message'
        num_messages: Specify the last n number of emails
        use_date: Toggle to use dates
        use_exact_date: Switch between exact date range and relative dates
    ### When integration_type = 'Typeform' and action = 'get_responses'
        number_of_responses: The number_of_responses input
    ### When integration_type = 'Github'
        owner_name: The owner_name input
        repo_name: The repo_name input
    ### When integration_type = 'Wordpress' and action = 'create_post'
        post_content: The post_content input
        post_title: The post_title input
        wordpress_url: The wordpress_url input
    ### When integration_type = 'Linkedin' and action = 'create_text_share'
        post_text: The post_text input
    ### When integration_type = 'Supabase S3' and action = 'search_files'
        query: The query input
    ### When integration_type = 'Hubspot' and action = 'fetch_contacts'
        query: The query input
    ### When integration_type = 'Hubspot' and action = 'fetch_companies'
        query: The query input
    ### When integration_type = 'Hubspot' and action = 'fetch_deals'
        query: The query input
    ### When integration_type = 'Hubspot' and action = 'fetch_tickets'
        query: The query input
    ### When integration_type = 'Hubspot' and action = 'fetch_notes'
        query: The query input
    ### When integration_type = 'Hubspot' and action = 'fetch_calls'
        query: The query input
    ### When integration_type = 'Hubspot' and action = 'fetch_tasks'
        query: The query input
    ### When integration_type = 'Hubspot' and action = 'fetch_meetings'
        query: The query input
    ### When integration_type = 'Hubspot' and action = 'fetch_emails'
        query: The query input
    ### When integration_type = 'Postgres'
        query: The query input
        query_agent_model: The query_agent_model input
        query_type: The query_type input
        sql_generation_model: The sql_generation_model input
    ### When integration_type = 'MySQL'
        query: The query input
        query_agent_model: The query_agent_model input
        query_type: The query_type input
        sql_generation_model: The sql_generation_model input
    ### When integration_type = 'Google Sheets' and action = 'write_to_sheet'
        selected_input_dynamic_handle_names: The selected_input_dynamic_handle_names input
    ### When integration_type = 'Google Sheets' and action = 'write_list_to_column'
        selected_input_dynamic_handle_names: The selected_input_dynamic_handle_names input
    ### When integration_type = 'Google Sheets' and action = 'update_rows'
        selected_input_dynamic_handle_names: The selected_input_dynamic_handle_names input
    ### When integration_type = 'Airtable' and action = 'new_record'
        selected_input_dynamic_handle_names: The selected_input_dynamic_handle_names input
    ### When integration_type = 'Airtable' and action = 'write_list_to_column'
        selected_input_dynamic_handle_names: The selected_input_dynamic_handle_names input
    ### When integration_type = 'Airtable' and action = 'update_records'
        selected_input_dynamic_handle_names: The selected_input_dynamic_handle_names input
    ### When integration_type = 'Notion' and action = 'write_to_database'
        selected_input_dynamic_handle_names: The selected_input_dynamic_handle_names input
    ### When integration_type = 'Notion' and action = 'create_new_page'
        selected_input_dynamic_handle_names: The selected_input_dynamic_handle_names input
    ### When integration_type = 'Notion' and action = 'create_new_block'
        selected_input_dynamic_handle_names: The selected_input_dynamic_handle_names input
    ### When integration_type = 'Notion' and action = 'update_database'
        selected_input_dynamic_handle_names: The selected_input_dynamic_handle_names input
    ### When integration_type = 'Google Sheets' and action = 'read_sheet_url'
        sheet_url: The sheet_url input
    ### When integration_type = 'Salesforce' and action = 'run_sql_query'
        sql_query: The sql_query input
    ### When integration_type = 'Gmail' and action = 'create_draft'
        subject: The subject input
    ### When integration_type = 'Gmail' and action = 'send_email'
        subject: The subject input
    ### When integration_type = 'X' and action = 'create_post'
        text: The text input
    ### When integration_type = 'X' and action = 'create_thread'
        text: The text input
    ### When integration_type = 'Google Docs' and action = 'write_to_doc'
        text: The text input

    ## Outputs
    ### When integration_type = 'Google Sheets'
        [processed_outputs]: The [processed_outputs] output
    ### When integration_type = 'Airtable'
        [processed_outputs]: The [processed_outputs] output
    ### When integration_type = 'Notion'
        [processed_outputs]: The [processed_outputs] output
    ### When integration_type = 'Apollo' and action = 'enrich_company'
        annual_revenue: The annual_revenue output
        company_name: The company_name output
        country: The country output
        industry: The industry output
        linkedin_url: The linkedin_url output
        num_employees: The num_employees output
        total_funding: The total_funding output
        website: The website output
    ### When integration_type = 'Bland AI'
        answered_by: The answered_by output
        transcript: The transcript output
    ### When integration_type = 'Slack' and action = 'read_message'
        attachment_names: The attachment_names output
        message: The message output
        sender_id: The sender_id output
        thread_id: The thread_id output
        thread_link: The thread_link output
    ### When integration_type = 'Outlook' and action = 'read_email'
        attachments: The attachments output
        email_bodies: The email_bodies output
        email_dates: The email_dates output
        email_display_names: The email_display_names output
        email_ids: The email_ids output
        email_subjects: The email_subjects output
        recipient_addresses: The recipient_addresses output
        sender_addresses: The sender_addresses output
    ### When integration_type = 'Apollo' and action = 'fetch_companies'
        company_names: The company_names output
        domains: The domains output
        linkedin_urls: The linkedin_urls output
        websites: The websites output
    ### When integration_type = 'Apollo' and action = 'enrich_contact'
        email: The email output
        first_name: The first_name output
        job_title: The job_title output
        last_name: The last_name output
        linkedin_url: The linkedin_url output
        phone_number: The phone_number output
    ### When integration_type = 'Typeform' and action = 'get_responses'
        list_of_responses: The list_of_responses output
    ### When integration_type = 'Salesforce' and action = 'run_sql_query'
        output: The output output
    ### When integration_type = 'SugarCRM' and action = 'get_records'
        output: The output output
    ### When integration_type = 'Github' and action = 'read_file'
        output: The output output
    ### When integration_type = 'Supabase S3' and action = 'search_files'
        output: The output output
    ### When integration_type = 'PeopleDataLabs' and action = 'enrich_person'
        output: The output output
    ### When integration_type = 'PeopleDataLabs' and action = 'search_people'
        output: The output output
    ### When integration_type = 'PeopleDataLabs' and action = 'search_people_query'
        output: The output output
    ### When integration_type = 'PeopleDataLabs' and action = 'enrich_company'
        output: The output output
    ### When integration_type = 'PeopleDataLabs' and action = 'search_companies'
        output: The output output
    ### When integration_type = 'PeopleDataLabs' and action = 'search_companies_query'
        output: The output output
    ### When integration_type = 'Hubspot' and action = 'fetch_contacts'
        output: The output output
    ### When integration_type = 'Hubspot' and action = 'fetch_companies'
        output: The output output
    ### When integration_type = 'Hubspot' and action = 'fetch_deals'
        output: The output output
    ### When integration_type = 'Hubspot' and action = 'fetch_tickets'
        output: The output output
    ### When integration_type = 'Hubspot' and action = 'fetch_notes'
        output: The output output
    ### When integration_type = 'Hubspot' and action = 'fetch_calls'
        output: The output output
    ### When integration_type = 'Hubspot' and action = 'fetch_tasks'
        output: The output output
    ### When integration_type = 'Hubspot' and action = 'fetch_meetings'
        output: The output output
    ### When integration_type = 'Hubspot' and action = 'fetch_emails'
        output: The output output
    ### When integration_type = 'Snowflake'
        output: The output output
    ### When integration_type = 'Elasticsearch' and action = 'search_index'
        output: The output output
    ### When integration_type = 'MongoDB'
        output: The output output
    ### When integration_type = 'Pinecone' and action = 'query_pinecone'
        output: The output output
    ### When integration_type = 'Postgres'
        output: The output output
    ### When integration_type = 'MySQL'
        output: The output output
    ### When integration_type = 'Linkedin' and action = 'create_text_share'
        output: The output output
    ### When integration_type = 'Google Calendar'
        output: The output output
    ### When integration_type = 'Microsoft Calendar'
        output: The output output
    ### When integration_type = 'Mailgun'
        output: The output output
    ### When integration_type = 'Microsoft' and action = 'read_file'
        output: The output output
    ### When integration_type = 'Weaviate'
        output: The output output
    ### When integration_type = 'Algolia'
        output: The output output
    ### When integration_type = 'X' and action = 'create_post'
        post_url: The post_url output
    ### When integration_type = 'X' and action = 'create_thread'
        post_url: The post_url output
    ### When integration_type = 'Wordpress' and action = 'create_post'
        post_url: The post_url output
    ### When integration_type = 'Google Sheets' and action = 'extract_to_table'
        table: The table output
    ### When integration_type = 'Google Docs' and action = 'read_doc'
        text: The text output
    ### When integration_type = 'Google Drive' and action = 'read_drive'
        text: The text output
    """

    # Common inputs and outputs
    _COMMON_INPUTS = [
        {
            "field": "action",
            "helper_text": "The action input",
            "value": "",
            "type": "string",
        },
        {
            "field": "function",
            "helper_text": "The function input",
            "value": None,
            "type": "any",
        },
        {
            "field": "integration",
            "helper_text": "The integration input",
            "value": None,
            "type": "any",
        },
        {
            "field": "integration_type",
            "helper_text": "The integration_type input",
            "value": "",
            "type": "string",
        },
    ]

    # Common outputs and inputs
    _COMMON_OUTPUTS = []

    # Configuration patterns and their associated inputs/outputs
    _CONFIGS = {
        "Gmail**(*)**(*)**(*)": {
            "inputs": [
                {"field": "recipients", "type": "string", "value": ""},
                {"field": "body", "type": "string", "value": ""},
            ],
            "outputs": [],
            "variant": "default_integration_nodes",
        },
        "Gmail**create_draft**(*)**(*)": {
            "inputs": [{"field": "subject", "type": "string", "value": ""}],
            "outputs": [],
        },
        "Gmail**send_email**(*)**(*)": {
            "inputs": [{"field": "subject", "type": "string", "value": ""}],
            "outputs": [],
        },
        "Gmail**draft_reply**(*)**(*)": {
            "inputs": [{"field": "email_id", "type": "string", "value": ""}],
            "outputs": [],
        },
        "Gmail**send_reply**(*)**(*)": {
            "inputs": [{"field": "email_id", "type": "string", "value": ""}],
            "outputs": [],
        },
        "Copper**(*)**(*)**(*)": {
            "inputs": [],
            "outputs": [],
            "variant": "default_integration_nodes",
        },
        "Copper**create_lead**(*)**(*)": {
            "inputs": [
                {"field": "name", "type": "string", "value": ""},
                {"field": "email", "type": "string", "value": ""},
            ],
            "outputs": [],
        },
        "Discord**(*)**(*)**(*)": {
            "inputs": [],
            "outputs": [],
            "variant": "default_integration_nodes",
        },
        "Discord**send_message**(*)**(*)": {
            "inputs": [
                {"field": "channel_name", "type": "string", "value": ""},
                {"field": "message", "type": "string", "value": ""},
            ],
            "outputs": [],
        },
        "Linear**(*)**(*)**(*)": {
            "inputs": [],
            "outputs": [],
            "variant": "default_integration_nodes",
        },
        "Linear**create_issue**(*)**(*)": {
            "inputs": [
                {"field": "title", "type": "string", "value": ""},
                {"field": "team_name", "type": "string", "value": ""},
                {"field": "description", "type": "string", "value": ""},
            ],
            "outputs": [],
        },
        "Linear**create_comment**(*)**(*)": {
            "inputs": [
                {"field": "issue_name", "type": "string", "value": ""},
                {"field": "comment", "type": "string", "value": ""},
            ],
            "outputs": [],
        },
        "Outlook**(*)**(*)**(*)": {
            "inputs": [],
            "outputs": [],
            "variant": "common_integration_nodes",
        },
        "Outlook**create_draft**(*)**(*)": {
            "inputs": [
                {"field": "recipients", "type": "string", "value": ""},
                {"field": "body", "type": "string", "value": ""},
                {"field": "format", "type": "enum<string>", "value": "text"},
                {"field": "subject", "type": "string", "value": ""},
            ],
            "outputs": [],
        },
        "Outlook**send_email**(*)**(*)": {
            "inputs": [
                {"field": "recipients", "type": "string", "value": ""},
                {"field": "body", "type": "string", "value": ""},
                {"field": "format", "type": "enum<string>", "value": "text"},
                {"field": "subject", "type": "string", "value": ""},
                {"field": "attachments", "type": "vec<file>", "value": []},
            ],
            "outputs": [],
        },
        "Outlook**draft_reply**(*)**(*)": {
            "inputs": [
                {"field": "recipients", "type": "string", "value": ""},
                {"field": "body", "type": "string", "value": ""},
                {"field": "format", "type": "enum<string>", "value": "text"},
                {"field": "email_id", "type": "string", "value": ""},
            ],
            "outputs": [],
        },
        "Outlook**send_reply**(*)**(*)": {
            "inputs": [
                {"field": "recipients", "type": "string", "value": ""},
                {"field": "body", "type": "string", "value": ""},
                {"field": "format", "type": "enum<string>", "value": "text"},
                {"field": "email_id", "type": "string", "value": ""},
                {"field": "attachments", "type": "vec<file>", "value": []},
            ],
            "outputs": [],
        },
        "Outlook**read_email**(*)**(*)": {
            "inputs": [
                {"field": "item_id", "type": "string", "show_date_range": True},
                {
                    "field": "use_date",
                    "type": "bool",
                    "value": False,
                    "show_date_range": True,
                    "label": "Use Date",
                    "helper_text": "Toggle to use dates",
                },
                {
                    "field": "use_exact_date",
                    "type": "bool",
                    "value": False,
                    "show_date_range": True,
                    "label": "Use Exact Date",
                    "helper_text": "Switch between exact date range and relative dates",
                },
                {
                    "field": "num_messages",
                    "type": "int32",
                    "value": 10,
                    "show_date_range": True,
                    "label": "Number of Emails",
                    "helper_text": "Specify the last n number of emails",
                },
            ],
            "outputs": [
                {"field": "email_ids", "type": "vec<string>"},
                {"field": "email_subjects", "type": "vec<string>"},
                {"field": "email_dates", "type": "vec<string>"},
                {"field": "email_bodies", "type": "vec<string>"},
                {"field": "sender_addresses", "type": "vec<string>"},
                {"field": "email_display_names", "type": "vec<string>"},
                {"field": "recipient_addresses", "type": "vec<string>"},
                {"field": "attachments", "type": "vec<vec<file>>"},
            ],
            "variant": "common_integration_file_nodes",
        },
        "Outlook**read_email**true**false": {
            "inputs": [
                {
                    "field": "date_range",
                    "type": "Dict[str, Any]",
                    "value": {
                        "date_type": "Last",
                        "date_value": 1,
                        "date_period": "Months",
                    },
                    "show_date_range": True,
                }
            ],
            "outputs": [],
        },
        "Outlook**read_email**true**true": {
            "inputs": [
                {
                    "field": "exact_date",
                    "type": "Dict[str, Any]",
                    "value": {"start": "", "end": ""},
                    "show_date_range": True,
                }
            ],
            "outputs": [],
        },
        "Salesforce**run_sql_query**(*)**(*)": {
            "inputs": [{"field": "sql_query", "type": "string", "value": ""}],
            "outputs": [{"field": "output", "type": "string"}],
        },
        "Slack**(*)**(*)**(*)": {
            "inputs": [
                {"field": "team", "type": "enum<Dict[str, Any]>", "value": ""},
                {"field": "channel", "type": "enum<Dict[str, Any]>"},
            ],
            "outputs": [],
            "variant": "common_integration_nodes",
        },
        "Slack**send_message**(*)**(*)": {
            "inputs": [{"field": "message", "type": "string", "value": ""}],
            "outputs": [],
        },
        "Slack**read_message**(*)**(*)": {
            "inputs": [
                {
                    "field": "use_date",
                    "type": "bool",
                    "value": False,
                    "show_date_range": True,
                    "label": "Use Date",
                    "helper_text": "Toggle to use dates",
                },
                {
                    "field": "use_exact_date",
                    "type": "bool",
                    "value": False,
                    "show_date_range": True,
                    "label": "Use Exact Date",
                    "helper_text": "Switch between exact date range and relative dates",
                },
                {
                    "field": "num_messages",
                    "type": "int32",
                    "value": 10,
                    "show_date_range": True,
                    "label": "Number of Messages",
                    "helper_text": "Specify the last n number of messages",
                },
            ],
            "outputs": [
                {"field": "message", "type": "vec<string>"},
                {"field": "thread_id", "type": "vec<string>"},
                {"field": "attachment_names", "type": "vec<vec<string>>"},
                {"field": "sender_id", "type": "vec<string>"},
                {"field": "thread_link", "type": "vec<string>"},
            ],
        },
        "Slack**read_message**true**false": {
            "inputs": [
                {
                    "field": "date_range",
                    "type": "Dict[str, Any]",
                    "value": {
                        "date_type": "Last",
                        "date_value": 1,
                        "date_period": "Months",
                    },
                    "show_data_range": True,
                }
            ],
            "outputs": [],
        },
        "Slack**read_message**true**true": {
            "inputs": [
                {
                    "field": "exact_date",
                    "type": "Dict[str, Any]",
                    "value": {"start": "", "end": ""},
                    "show_data_range": True,
                }
            ],
            "outputs": [],
        },
        "SugarCRM**(*)**(*)**(*)": {
            "inputs": [],
            "outputs": [],
            "variant": "default_integration_nodes",
        },
        "SugarCRM**get_records**(*)**(*)": {
            "inputs": [
                {"field": "module", "type": "string", "value": ""},
                {"field": "filter", "type": "string", "value": ""},
            ],
            "outputs": [{"field": "output", "type": "any"}],
        },
        "Github**(*)**(*)**(*)": {
            "inputs": [
                {"field": "owner_name", "type": "string", "value": ""},
                {"field": "repo_name", "type": "string", "value": ""},
            ],
            "outputs": [],
            "variant": "default_integration_nodes",
        },
        "Github**read_file**(*)**(*)": {
            "inputs": [
                {"field": "branch_name", "type": "string", "value": ""},
                {"field": "file_name", "type": "string", "value": ""},
            ],
            "outputs": [{"field": "output", "type": "string"}],
        },
        "Github**create_pr**(*)**(*)": {
            "inputs": [
                {"field": "base", "type": "string", "value": ""},
                {"field": "head", "type": "string", "value": ""},
                {"field": "title", "type": "string", "value": ""},
                {"field": "body", "type": "string", "value": ""},
            ],
            "outputs": [],
        },
        "Github**update_pr**(*)**(*)": {
            "inputs": [
                {"field": "pull_number", "type": "string", "value": ""},
                {"field": "title", "type": "string", "value": ""},
                {"field": "body", "type": "string", "value": ""},
            ],
            "outputs": [],
        },
        "Zendesk**(*)**(*)**(*)": {
            "inputs": [],
            "outputs": [],
            "variant": "default_integration_nodes",
        },
        "Zendesk**create_ticket**(*)**(*)": {
            "inputs": [
                {"field": "subject", "type": "string", "value": ""},
                {"field": "body", "type": "string", "value": ""},
                {"field": "requester_email", "type": "string", "value": ""},
                {"field": "requester_name", "type": "string", "value": ""},
            ],
            "outputs": [],
        },
        "Supabase S3**search_files**(*)**(*)": {
            "inputs": [{"field": "query", "type": "string", "value": ""}],
            "outputs": [{"field": "output", "type": "string"}],
        },
        "Teams**(*)**(*)**(*)": {
            "inputs": [],
            "outputs": [],
            "variant": "default_integration_nodes",
        },
        "Teams**send_message**(*)**(*)": {
            "inputs": [
                {"field": "team_name", "type": "string", "value": ""},
                {"field": "channel_name", "type": "string", "value": ""},
                {"field": "message", "type": "string", "value": ""},
            ],
            "outputs": [],
        },
        "X**(*)**(*)**(*)": {
            "inputs": [],
            "outputs": [],
            "variant": "default_integration_nodes",
        },
        "X**create_post**(*)**(*)": {
            "inputs": [{"field": "text", "type": "string", "value": ""}],
            "outputs": [{"field": "post_url", "type": "string"}],
        },
        "X**create_thread**(*)**(*)": {
            "inputs": [{"field": "text", "type": "string", "value": ""}],
            "outputs": [{"field": "post_url", "type": "string"}],
        },
        "GoHighLevel**(*)**(*)**(*)": {
            "inputs": [],
            "outputs": [],
            "variant": "default_integration_nodes",
        },
        "GoHighLevel**create_contact**(*)**(*)": {
            "inputs": [
                {"field": "first_name", "type": "string", "value": ""},
                {"field": "last_name", "type": "string", "value": ""},
                {"field": "email", "type": "string", "value": ""},
                {"field": "phone", "type": "string", "value": ""},
            ],
            "outputs": [],
        },
        "GoHighLevel**create_opportunity**(*)**(*)": {
            "inputs": [
                {"field": "name", "type": "string", "value": ""},
                {"field": "status", "type": "string", "value": ""},
                {"field": "value", "type": "string", "value": ""},
                {"field": "pipeline_name", "type": "string", "value": ""},
                {"field": "contact_name", "type": "string", "value": ""},
            ],
            "outputs": [],
        },
        "PeopleDataLabs**(*)**(*)**(*)": {
            "inputs": [],
            "outputs": [],
            "variant": "default_integration_nodes",
        },
        "PeopleDataLabs**enrich_person**(*)**(*)": {
            "inputs": [
                {"field": "first_name", "type": "string", "value": ""},
                {"field": "last_name", "type": "string", "value": ""},
                {"field": "location", "type": "string", "value": ""},
                {"field": "email", "type": "string", "value": ""},
                {"field": "company", "type": "string", "value": ""},
                {"field": "profile_url", "type": "string", "value": ""},
            ],
            "outputs": [{"field": "output", "type": "string"}],
        },
        "PeopleDataLabs**search_people**(*)**(*)": {
            "inputs": [
                {"field": "country", "type": "string", "value": ""},
                {"field": "job_titles", "type": "string", "value": ""},
                {"field": "job_company_names", "type": "string", "value": ""},
                {"field": "skills", "type": "string", "value": ""},
                {"field": "number_of_results", "type": "string", "value": ""},
            ],
            "outputs": [{"field": "output", "type": "string"}],
        },
        "PeopleDataLabs**search_people_query**(*)**(*)": {
            "inputs": [
                {"field": "es_query", "type": "string", "value": ""},
                {"field": "sql", "type": "string", "value": ""},
                {"field": "number_of_results", "type": "string", "value": ""},
            ],
            "outputs": [{"field": "output", "type": "string"}],
        },
        "PeopleDataLabs**enrich_company**(*)**(*)": {
            "inputs": [
                {"field": "name", "type": "string", "value": ""},
                {"field": "profile", "type": "string", "value": ""},
                {"field": "website", "type": "string", "value": ""},
            ],
            "outputs": [{"field": "output", "type": "string"}],
        },
        "PeopleDataLabs**search_companies**(*)**(*)": {
            "inputs": [
                {"field": "tags", "type": "string", "value": ""},
                {"field": "industries", "type": "string", "value": ""},
                {"field": "company_size_ranges", "type": "string", "value": ""},
                {"field": "founded_year_range", "type": "string", "value": ""},
                {"field": "country", "type": "string", "value": ""},
                {"field": "number_of_results", "type": "string", "value": ""},
            ],
            "outputs": [{"field": "output", "type": "string"}],
        },
        "PeopleDataLabs**search_companies_query**(*)**(*)": {
            "inputs": [
                {"field": "es_query", "type": "string", "value": ""},
                {"field": "sql", "type": "string", "value": ""},
                {"field": "number_of_results", "type": "int32", "value": 10},
            ],
            "outputs": [{"field": "output", "type": "string"}],
        },
        "Hubspot**(*)**(*)**(*)": {
            "inputs": [],
            "outputs": [],
            "variant": "default_integration_nodes",
        },
        "Hubspot**fetch_contacts**(*)**(*)": {
            "inputs": [{"field": "query", "type": "string", "value": ""}],
            "outputs": [{"field": "output", "type": "string"}],
        },
        "Hubspot**fetch_companies**(*)**(*)": {
            "inputs": [{"field": "query", "type": "string", "value": ""}],
            "outputs": [{"field": "output", "type": "string"}],
        },
        "Hubspot**fetch_deals**(*)**(*)": {
            "inputs": [{"field": "query", "type": "string", "value": ""}],
            "outputs": [{"field": "output", "type": "string"}],
        },
        "Hubspot**fetch_tickets**(*)**(*)": {
            "inputs": [{"field": "query", "type": "string", "value": ""}],
            "outputs": [{"field": "output", "type": "string"}],
        },
        "Hubspot**fetch_notes**(*)**(*)": {
            "inputs": [{"field": "query", "type": "string", "value": ""}],
            "outputs": [{"field": "output", "type": "string"}],
        },
        "Hubspot**fetch_calls**(*)**(*)": {
            "inputs": [{"field": "query", "type": "string", "value": ""}],
            "outputs": [{"field": "output", "type": "string"}],
        },
        "Hubspot**fetch_tasks**(*)**(*)": {
            "inputs": [{"field": "query", "type": "string", "value": ""}],
            "outputs": [{"field": "output", "type": "string"}],
        },
        "Hubspot**fetch_meetings**(*)**(*)": {
            "inputs": [{"field": "query", "type": "string", "value": ""}],
            "outputs": [{"field": "output", "type": "string"}],
        },
        "Hubspot**fetch_emails**(*)**(*)": {
            "inputs": [{"field": "query", "type": "string", "value": ""}],
            "outputs": [{"field": "output", "type": "string"}],
        },
        "Hubspot**create_company**(*)**(*)": {
            "inputs": [
                {"field": "name", "type": "string", "value": ""},
                {"field": "domain", "type": "string", "value": ""},
                {"field": "city", "type": "string", "value": ""},
                {"field": "industry", "type": "string", "value": ""},
                {"field": "phone", "type": "string", "value": ""},
                {"field": "state", "type": "string", "value": ""},
                {"field": "associated_object_id", "type": "string", "value": ""},
                {"field": "associated_object_type", "type": "string", "value": ""},
            ],
            "outputs": [],
        },
        "Hubspot**create_contact**(*)**(*)": {
            "inputs": [
                {"field": "email", "type": "string", "value": ""},
                {"field": "firstname", "type": "string", "value": ""},
                {"field": "lastname", "type": "string", "value": ""},
                {"field": "phone", "type": "string", "value": ""},
                {"field": "company", "type": "string", "value": ""},
                {"field": "website", "type": "string", "value": ""},
                {"field": "associated_object_id", "type": "string", "value": ""},
                {"field": "associated_object_type", "type": "string", "value": ""},
            ],
            "outputs": [],
        },
        "Hubspot**create_deal**(*)**(*)": {
            "inputs": [
                {"field": "amount", "type": "string", "value": ""},
                {"field": "closedate", "type": "string", "value": ""},
                {"field": "dealname", "type": "string", "value": ""},
                {"field": "pipeline", "type": "string", "value": ""},
                {"field": "dealstage", "type": "string", "value": ""},
                {"field": "associated_object_id", "type": "string", "value": ""},
                {"field": "associated_object_type", "type": "string", "value": ""},
            ],
            "outputs": [],
        },
        "Hubspot**create_ticket**(*)**(*)": {
            "inputs": [
                {"field": "hs_pipeline", "type": "string", "value": ""},
                {"field": "hs_pipeline_stage", "type": "string", "value": ""},
                {"field": "hs_ticket_priority", "type": "string", "value": ""},
                {"field": "subject", "type": "string", "value": ""},
                {"field": "associated_object_id", "type": "string", "value": ""},
                {"field": "associated_object_type", "type": "string", "value": ""},
            ],
            "outputs": [],
        },
        "Hubspot**create_note**(*)**(*)": {
            "inputs": [
                {"field": "body", "type": "string", "value": ""},
                {"field": "associated_object_id", "type": "string", "value": ""},
                {"field": "associated_object_type", "type": "string", "value": ""},
            ],
            "outputs": [],
        },
        "Hubspot**create_call**(*)**(*)": {
            "inputs": [
                {"field": "body", "type": "string", "value": ""},
                {"field": "duration", "type": "string", "value": ""},
                {"field": "title", "type": "string", "value": ""},
                {"field": "from_number", "type": "string", "value": ""},
                {"field": "to_number", "type": "string", "value": ""},
                {"field": "associated_object_id", "type": "string", "value": ""},
                {"field": "associated_object_type", "type": "string", "value": ""},
            ],
            "outputs": [],
        },
        "Hubspot**create_task**(*)**(*)": {
            "inputs": [
                {"field": "body", "type": "string", "value": ""},
                {"field": "status", "type": "string", "value": ""},
                {"field": "subject", "type": "string", "value": ""},
                {"field": "priority", "type": "string", "value": ""},
                {"field": "associated_object_id", "type": "string", "value": ""},
                {"field": "associated_object_type", "type": "string", "value": ""},
            ],
            "outputs": [],
        },
        "Hubspot**create_meeting**(*)**(*)": {
            "inputs": [
                {"field": "body", "type": "string", "value": ""},
                {"field": "title", "type": "string", "value": ""},
                {"field": "start_time", "type": "string", "value": ""},
                {"field": "end_time", "type": "string", "value": ""},
                {"field": "meeting_notes", "type": "string", "value": ""},
                {"field": "associated_object_id", "type": "string", "value": ""},
                {"field": "associated_object_type", "type": "string", "value": ""},
            ],
            "outputs": [],
        },
        "Hubspot**create_email**(*)**(*)": {
            "inputs": [
                {"field": "text", "type": "string", "value": ""},
                {"field": "subject", "type": "string", "value": ""},
                {"field": "recipient_email", "type": "string", "value": ""},
                {"field": "sender_email", "type": "string", "value": ""},
                {"field": "direction", "type": "string", "value": ""},
                {"field": "associated_object_id", "type": "string", "value": ""},
                {"field": "associated_object_type", "type": "string", "value": ""},
            ],
            "outputs": [],
        },
        "Snowflake**(*)**(*)**(*)": {
            "inputs": [
                {"field": "query", "type": "string", "value": ""},
                {"field": "query_type", "type": "string", "value": "Raw SQL"},
                {"field": "warehouse", "type": "enum<string>", "value": ""},
                {"field": "database", "type": "enum<string>", "value": ""},
                {"field": "schema", "type": "enum<string>", "value": ""},
                {
                    "field": "sql_generation_model",
                    "type": "string",
                    "value": "gpt-4-turbo-preview",
                },
                {
                    "field": "query_agent_model",
                    "type": "string",
                    "value": "gpt-4-turbo-preview",
                },
            ],
            "outputs": [{"field": "output", "type": "any"}],
            "variant": "common_integration_nodes",
        },
        "Elasticsearch**search_index**(*)**(*)": {
            "inputs": [
                {"field": "query", "type": "string", "value": ""},
                {"field": "index", "type": "string", "value": ""},
            ],
            "outputs": [{"field": "output", "type": "string"}],
        },
        "MongoDB**(*)**(*)**(*)": {
            "inputs": [
                {"field": "collection", "type": "enum<string>", "value": ""},
                {"field": "query", "type": "string", "value": ""},
            ],
            "outputs": [{"field": "output", "type": "string"}],
            "variant": "common_integration_nodes",
        },
        "Pinecone**(*)**(*)**(*)": {
            "inputs": [],
            "outputs": [],
            "variant": "common_integration_nodes",
        },
        "Pinecone**query_pinecone**(*)**(*)": {
            "inputs": [
                {"field": "index", "type": "enum<string>", "value": ""},
                {"field": "embedding_model", "type": "enum<string>", "value": ""},
                {"field": "namespace", "type": "enum<string>", "value": ""},
                {"field": "query", "type": "string", "value": ""},
            ],
            "outputs": [{"field": "output", "type": "any"}],
        },
        "Postgres**(*)**(*)**(*)": {
            "inputs": [
                {"field": "query", "type": "string", "value": ""},
                {"field": "query_type", "type": "string", "value": "Raw SQL"},
                {
                    "field": "sql_generation_model",
                    "type": "string",
                    "value": "gpt-4-turbo-preview",
                },
                {
                    "field": "query_agent_model",
                    "type": "string",
                    "value": "gpt-4-turbo-preview",
                },
            ],
            "outputs": [{"field": "output", "type": "string"}],
        },
        "MySQL**(*)**(*)**(*)": {
            "inputs": [
                {"field": "query", "type": "string", "value": ""},
                {"field": "query_type", "type": "string", "value": "Raw SQL"},
                {
                    "field": "sql_generation_model",
                    "type": "string",
                    "value": "gpt-4-turbo-preview",
                },
                {
                    "field": "query_agent_model",
                    "type": "string",
                    "value": "gpt-4-turbo-preview",
                },
            ],
            "outputs": [{"field": "output", "type": "string"}],
        },
        "Wordpress**(*)**(*)**(*)": {
            "inputs": [],
            "outputs": [],
            "variant": "default_integration_nodes",
        },
        "Wordpress**create_post**(*)**(*)": {
            "inputs": [
                {"field": "wordpress_url", "type": "string", "value": ""},
                {"field": "post_title", "type": "string", "value": ""},
                {"field": "post_content", "type": "string", "value": ""},
            ],
            "outputs": [{"field": "post_url", "type": "string"}],
        },
        "Linkedin**(*)**(*)**(*)": {
            "inputs": [],
            "outputs": [],
            "variant": "default_integration_nodes",
        },
        "Linkedin**create_text_share**(*)**(*)": {
            "inputs": [{"field": "post_text", "type": "string", "value": ""}],
            "outputs": [{"field": "output", "type": "string"}],
        },
        "Google Calendar**(*)**(*)**(*)": {
            "inputs": [{"field": "calendar", "type": "enum<Dict[str, Any]>"}],
            "outputs": [{"field": "output", "type": "string"}],
            "variant": "common_integration_nodes",
        },
        "Google Calendar**new_event**(*)**(*)": {
            "inputs": [
                {"field": "event_name", "type": "string", "value": ""},
                {"field": "start_datetime", "type": "string", "value": ""},
                {"field": "duration", "type": "string", "value": ""},
                {"field": "attendees", "type": "string", "value": ""},
                {"field": "location", "type": "string", "value": ""},
                {"field": "description", "type": "string", "value": ""},
            ],
            "outputs": [],
        },
        "Google Calendar**check_availability**(*)**(*)": {
            "inputs": [
                {"field": "start_date", "type": "string", "value": ""},
                {"field": "start_work_time", "type": "string", "value": ""},
                {"field": "end_date", "type": "string", "value": ""},
                {"field": "end_work_time", "type": "string", "value": ""},
                {"field": "slot_duration", "type": "string", "value": ""},
                {"field": "timezone", "type": "string", "value": ""},
            ],
            "outputs": [],
        },
        "Microsoft Calendar**(*)**(*)**(*)": {
            "inputs": [],
            "outputs": [{"field": "output", "type": "string"}],
            "variant": "common_integration_nodes",
        },
        "Microsoft Calendar**new_event**(*)**(*)": {
            "inputs": [
                {"field": "calendar", "type": "enum<Dict[str, Any]>"},
                {"field": "subject", "type": "string", "value": ""},
                {"field": "body", "type": "string", "value": ""},
                {"field": "start_datetime", "type": "string", "value": ""},
                {"field": "duration", "type": "string", "value": ""},
                {"field": "location", "type": "string", "value": ""},
                {"field": "attendees", "type": "string", "value": ""},
            ],
            "outputs": [],
        },
        "Microsoft Calendar**check_availability**(*)**(*)": {
            "inputs": [
                {"field": "start_date", "type": "string", "value": ""},
                {"field": "start_work_time", "type": "string", "value": ""},
                {"field": "end_date", "type": "string", "value": ""},
                {"field": "end_work_time", "type": "string", "value": ""},
                {"field": "slot_duration", "type": "string", "value": ""},
                {"field": "timezone", "type": "string", "value": ""},
            ],
            "outputs": [],
        },
        "Mailgun**(*)**(*)**(*)": {
            "inputs": [],
            "outputs": [{"field": "output", "type": "string"}],
            "variant": "common_integration_nodes",
        },
        "Mailgun**send_mail**(*)**(*)": {
            "inputs": [
                {"field": "domain", "type": "enum<Dict[str, Any]>"},
                {"field": "subject", "type": "string", "value": ""},
                {"field": "body", "type": "string", "value": ""},
                {"field": "from_name", "type": "string", "value": ""},
                {"field": "from_email", "type": "string", "value": ""},
                {"field": "recipients", "type": "string", "value": ""},
                {"field": "cc_recipients", "type": "string", "value": ""},
                {"field": "bcc_recipients", "type": "string", "value": ""},
            ],
            "outputs": [],
        },
        "Mailgun**add_contact_to_mailing_list**(*)**(*)": {
            "inputs": [
                {"field": "list_name", "type": "string", "value": ""},
                {"field": "name", "type": "string", "value": ""},
                {"field": "email", "type": "string", "value": ""},
            ],
            "outputs": [],
        },
        "Google Docs**(*)**(*)**(*)": {
            "inputs": [{"field": "file_id", "type": "string"}],
            "outputs": [],
            "variant": "common_integration_file_nodes",
        },
        "Google Docs**read_doc**(*)**(*)": {
            "inputs": [],
            "outputs": [{"field": "text", "type": "string"}],
        },
        "Google Docs**write_to_doc**(*)**(*)": {
            "inputs": [{"field": "text", "type": "string", "value": ""}],
            "outputs": [],
        },
        "Microsoft**(*)**(*)**(*)": {
            "inputs": [{"field": "item_id", "type": "string"}],
            "outputs": [],
            "variant": "common_integration_file_nodes",
        },
        "Microsoft**add_file**(*)**(*)": {
            "inputs": [
                {"field": "file_name", "type": "string", "value": ""},
                {"field": "content", "type": "string", "value": ""},
            ],
            "outputs": [],
        },
        "Microsoft**read_file**(*)**(*)": {
            "inputs": [],
            "outputs": [{"field": "output", "type": "string"}],
        },
        "Typeform**(*)**(*)**(*)": {
            "inputs": [{"field": "form_id", "type": "string", "value": ""}],
            "outputs": [],
            "variant": "common_integration_file_nodes",
        },
        "Typeform**get_responses**(*)**(*)": {
            "inputs": [{"field": "number_of_responses", "type": "string", "value": ""}],
            "outputs": [{"field": "list_of_responses", "type": "vec<string>"}],
        },
        "Dropbox**(*)**(*)**(*)": {
            "inputs": [{"field": "folder_id", "type": "string", "value": ""}],
            "outputs": [],
            "variant": "common_integration_file_nodes",
        },
        "Dropbox**post_file**(*)**(*)": {
            "inputs": [
                {"field": "file_name", "type": "string", "value": ""},
                {"field": "content", "type": "string", "value": ""},
            ],
            "outputs": [],
        },
        "Box**(*)**(*)**(*)": {
            "inputs": [{"field": "folder_id", "type": "string", "value": ""}],
            "outputs": [],
            "variant": "common_integration_file_nodes",
        },
        "Box**upload_files**(*)**(*)": {
            "inputs": [{"field": "files", "type": "vec<file>", "value": [""]}],
            "outputs": [],
        },
        "Google Drive**(*)**(*)**(*)": {
            "inputs": [{"field": "file_id", "type": "string", "value": ""}],
            "outputs": [],
            "variant": "common_integration_file_nodes",
        },
        "Google Drive**read_drive**(*)**(*)": {
            "inputs": [],
            "outputs": [{"field": "text", "type": "string"}],
        },
        "Google Drive**save_drive**(*)**(*)": {
            "inputs": [
                {"field": "file_name", "type": "string", "value": ""},
                {"field": "file", "type": "file", "value": ""},
            ],
            "outputs": [],
        },
        "Google Sheets**(*)**(*)**(*)": {
            "inputs": [
                {"field": "sheet_id", "type": "string", "value": ""},
                {"field": "provider", "type": "enum<string>", "value": "openai"},
                {"field": "model", "type": "enum<string>", "value": "gpt-4o"},
                {
                    "field": "processed_outputs",
                    "type": "map<string, string>",
                    "value": {},
                },
            ],
            "outputs": [{"field": "[processed_outputs]", "type": ""}],
            "variant": "google_sheet",
        },
        "Google Sheets**read_sheet_url**(*)**(*)": {
            "inputs": [{"field": "sheet_url", "type": "string", "value": ""}],
            "outputs": [],
            "banner_text": 'Ensure that the Google Sheet\'s permissions is set to "Anyone with the Link"',
        },
        "Google Sheets**write_to_sheet**(*)**(*)": {
            "inputs": [
                {
                    "field": "selected_input_dynamic_handle_names",
                    "type": "vec<Dict[str, Any]>",
                    "value": [],
                }
            ],
            "outputs": [],
        },
        "Google Sheets**write_list_to_column**(*)**(*)": {
            "inputs": [
                {
                    "field": "selected_input_dynamic_handle_names",
                    "type": "vec<Dict[str, Any]>",
                    "value": [],
                }
            ],
            "outputs": [],
        },
        "Google Sheets**update_rows**(*)**(*)": {
            "inputs": [
                {
                    "field": "selected_input_dynamic_handle_names",
                    "type": "vec<Dict[str, Any]>",
                    "value": [],
                }
            ],
            "outputs": [],
        },
        "Google Sheets**extract_to_table**(*)**(*)": {
            "inputs": [
                {"field": "sheet_id", "type": "string", "value": ""},
                {"field": "text_for_extraction", "type": "string", "value": ""},
                {"field": "extract_multiple_rows", "type": "bool", "value": True},
                {"field": "manual_columns", "type": "vec<Dict[str, Any]>", "value": []},
                {"field": "add_columns_manually", "type": "bool", "value": False},
                {"field": "additional_context", "type": "string", "value": ""},
            ],
            "outputs": [{"field": "table", "type": "file"}],
        },
        "Airtable**(*)**(*)**(*)": {
            "inputs": [
                {"field": "base_id", "type": "enum<string>", "value": ""},
                {"field": "table_id", "type": "enum<string>", "value": ""},
                {
                    "field": "processed_outputs",
                    "type": "map<string, string>",
                    "value": {},
                },
            ],
            "outputs": [{"field": "[processed_outputs]", "type": ""}],
            "variant": "common_integration_dynamic_nodes",
        },
        "Airtable**new_record**(*)**(*)": {
            "inputs": [
                {
                    "field": "selected_input_dynamic_handle_names",
                    "type": "vec<Dict[str, Any]>",
                    "value": [],
                }
            ],
            "outputs": [],
        },
        "Airtable**write_list_to_column**(*)**(*)": {
            "inputs": [
                {
                    "field": "selected_input_dynamic_handle_names",
                    "type": "vec<Dict[str, Any]>",
                    "value": [],
                }
            ],
            "outputs": [],
        },
        "Airtable**update_records**(*)**(*)": {
            "inputs": [
                {
                    "field": "selected_input_dynamic_handle_names",
                    "type": "vec<Dict[str, Any]>",
                    "value": [],
                }
            ],
            "outputs": [],
        },
        "Notion**(*)**(*)**(*)": {
            "inputs": [
                {"field": "item_id", "type": "enum<string>", "value": ""},
                {
                    "field": "processed_outputs",
                    "type": "map<string, string>",
                    "value": {},
                },
            ],
            "outputs": [{"field": "[processed_outputs]", "type": ""}],
            "variant": "common_integration_dynamic_nodes",
        },
        "Notion**write_to_database**(*)**(*)": {
            "inputs": [
                {
                    "field": "selected_input_dynamic_handle_names",
                    "type": "vec<Dict[str, Any]>",
                    "value": [],
                }
            ],
            "outputs": [],
        },
        "Notion**create_new_page**(*)**(*)": {
            "inputs": [
                {
                    "field": "selected_input_dynamic_handle_names",
                    "type": "vec<Dict[str, Any]>",
                    "value": [],
                }
            ],
            "outputs": [],
        },
        "Notion**create_new_block**(*)**(*)": {
            "inputs": [
                {
                    "field": "selected_input_dynamic_handle_names",
                    "type": "vec<Dict[str, Any]>",
                    "value": [],
                }
            ],
            "outputs": [],
        },
        "Notion**update_database**(*)**(*)": {
            "inputs": [
                {
                    "field": "selected_input_dynamic_handle_names",
                    "type": "vec<Dict[str, Any]>",
                    "value": [],
                }
            ],
            "outputs": [],
        },
        "Databricks**(*)**(*)**(*)": {
            "inputs": [
                {"field": "warehouse_id", "type": "enum<string>", "value": ""},
                {"field": "catalog_name", "type": "enum<string>", "value": ""},
                {"field": "schema_name", "type": "enum<string>", "value": ""},
                {"field": "table_name", "type": "enum<string>", "value": ""},
                {
                    "field": "selected_input_dynamic_handle_names",
                    "type": "vec<Dict[str, Any]>",
                    "value": [],
                },
            ],
            "outputs": [],
            "variant": "common_integration_dynamic_nodes",
        },
        "Weaviate**(*)**(*)**(*)": {
            "inputs": [
                {"field": "query", "type": "string", "value": ""},
                {"field": "embedding_model", "type": "enum<string>", "value": ""},
                {"field": "collection", "type": "enum<string>", "value": ""},
                {"field": "properties", "type": "enum<string>", "value": ""},
            ],
            "outputs": [{"field": "output", "type": "string"}],
            "variant": "common_integration_nodes",
        },
        "Bland AI**(*)**(*)**(*)": {
            "inputs": [
                {"field": "phone_number", "type": "string", "value": ""},
                {"field": "task", "type": "string", "value": ""},
                {"field": "first_sentence", "type": "string", "value": ""},
                {"field": "model", "type": "enum<string>", "value": "enhanced"},
                {"field": "pathway_id", "type": "string", "value": ""},
                {"field": "temperature", "type": "string", "value": ""},
                {"field": "transfer_number", "type": "string", "value": ""},
                {"field": "wait_for_greeting", "type": "bool", "value": False},
            ],
            "outputs": [
                {"field": "transcript", "type": "string"},
                {"field": "answered_by", "type": "string"},
            ],
            "variant": "bland_ai",
        },
        "Algolia**(*)**(*)**(*)": {
            "inputs": [
                {"field": "query", "type": "string", "value": ""},
                {"field": "index", "type": "string", "value": ""},
                {"field": "return_mode", "type": "enum<string>", "value": "json"},
            ],
            "outputs": [{"field": "output", "type": "any"}],
            "variant": "common_integration_nodes",
        },
        "Apollo**(*)**(*)**(*)": {
            "inputs": [],
            "outputs": [],
            "variant": "default_integration_nodes",
        },
        "Apollo**fetch_companies**(*)**(*)": {
            "inputs": [
                {"field": "company_name", "type": "string", "value": ""},
                {"field": "keywords", "type": "string", "value": ""},
                {"field": "min_size", "type": "string", "value": ""},
                {"field": "max_size", "type": "string", "value": ""},
                {"field": "location", "type": "string", "value": ""},
                {"field": "num_results", "type": "string", "value": ""},
            ],
            "outputs": [
                {"field": "company_names", "type": "string"},
                {"field": "websites", "type": "string"},
                {"field": "domains", "type": "string"},
                {"field": "linkedin_urls", "type": "string"},
            ],
        },
        "Apollo**enrich_company**(*)**(*)": {
            "inputs": [{"field": "domain", "type": "string", "value": ""}],
            "outputs": [
                {"field": "company_name", "type": "string"},
                {"field": "country", "type": "string"},
                {"field": "website", "type": "string"},
                {"field": "industry", "type": "string"},
                {"field": "annual_revenue", "type": "string"},
                {"field": "total_funding", "type": "string"},
                {"field": "num_employees", "type": "string"},
                {"field": "linkedin_url", "type": "string"},
            ],
        },
        "Apollo**enrich_contact**(*)**(*)": {
            "inputs": [
                {"field": "domain", "type": "string", "value": ""},
                {"field": "first_name_input", "type": "string", "value": ""},
                {"field": "last_name_input", "type": "string", "value": ""},
                {"field": "company_name", "type": "string", "value": ""},
                {"field": "linkedin_url_input", "type": "string", "value": ""},
            ],
            "outputs": [
                {"field": "first_name", "type": "string"},
                {"field": "last_name", "type": "string"},
                {"field": "job_title", "type": "string"},
                {"field": "phone_number", "type": "string"},
                {"field": "email", "type": "string"},
                {"field": "linkedin_url", "type": "string"},
            ],
        },
    }

    # List of parameters that affect configuration
    _PARAMS = ["integration_type", "action", "use_date", "use_exact_date"]

    def __init__(
        self,
        id: Optional[str] = None,
        node_name: Optional[str] = None,
        execution_mode: Optional[str] = None,
        integration_type: str = "",
        action: str = "",
        use_date: bool = False,
        use_exact_date: bool = False,
        add_columns_manually: bool = False,
        additional_context: str = "",
        amount: str = "",
        associated_object_id: str = "",
        associated_object_type: str = "",
        attachments: List[str] = [],
        attendees: str = "",
        base: str = "",
        base_id: str = "",
        bcc_recipients: str = "",
        body: str = "",
        branch_name: str = "",
        calendar: Optional[Dict[str, Any]] = None,
        catalog_name: str = "",
        cc_recipients: str = "",
        channel: Optional[Dict[str, Any]] = None,
        channel_name: str = "",
        city: str = "",
        closedate: str = "",
        collection: str = "",
        comment: str = "",
        company: str = "",
        company_name: str = "",
        company_size_ranges: str = "",
        contact_name: str = "",
        content: str = "",
        country: str = "",
        database: str = "",
        dealname: str = "",
        dealstage: str = "",
        description: str = "",
        direction: str = "",
        domain: str = "",
        duration: str = "",
        email: str = "",
        email_id: str = "",
        embedding_model: str = "",
        end_date: str = "",
        end_time: str = "",
        end_work_time: str = "",
        es_query: str = "",
        event_name: str = "",
        exact_date: Any = {"start": "", "end": ""},
        extract_multiple_rows: bool = True,
        file: str = "",
        file_id: Optional[str] = None,
        file_name: str = "",
        files: List[str] = [""],
        filter: str = "",
        first_name: str = "",
        first_name_input: str = "",
        first_sentence: str = "",
        firstname: str = "",
        folder_id: str = "",
        form_id: str = "",
        format: str = "text",
        founded_year_range: str = "",
        from_email: str = "",
        from_name: str = "",
        from_number: str = "",
        function: Optional[Any] = None,
        head: str = "",
        hs_pipeline: str = "",
        hs_pipeline_stage: str = "",
        hs_ticket_priority: str = "",
        index: str = "",
        industries: str = "",
        industry: str = "",
        integration: Optional[Any] = None,
        issue_name: str = "",
        item_id: Optional[str] = None,
        job_company_names: str = "",
        job_titles: str = "",
        keywords: str = "",
        last_name: str = "",
        last_name_input: str = "",
        lastname: str = "",
        linkedin_url_input: str = "",
        list_name: str = "",
        location: str = "",
        manual_columns: List[Any] = [],
        max_size: str = "",
        meeting_notes: str = "",
        message: str = "",
        min_size: str = "",
        model: str = "gpt-4o",
        module: str = "",
        name: str = "",
        namespace: str = "",
        num_messages: int = 10,
        num_results: str = "",
        number_of_responses: str = "",
        number_of_results: str = "",
        owner_name: str = "",
        pathway_id: str = "",
        phone: str = "",
        phone_number: str = "",
        pipeline: str = "",
        pipeline_name: str = "",
        post_content: str = "",
        post_text: str = "",
        post_title: str = "",
        priority: str = "",
        processed_outputs: Dict[str, str] = {},
        profile: str = "",
        profile_url: str = "",
        properties: str = "",
        provider: str = "openai",
        pull_number: str = "",
        query: str = "",
        query_agent_model: str = "gpt-4-turbo-preview",
        query_type: str = "Raw SQL",
        recipient_email: str = "",
        recipients: str = "",
        repo_name: str = "",
        requester_email: str = "",
        requester_name: str = "",
        return_mode: str = "json",
        schema: str = "",
        schema_name: str = "",
        selected_input_dynamic_handle_names: List[Any] = [],
        sender_email: str = "",
        sheet_id: str = "",
        sheet_url: str = "",
        skills: str = "",
        slot_duration: str = "",
        sql: str = "",
        sql_generation_model: str = "gpt-4-turbo-preview",
        sql_query: str = "",
        start_date: str = "",
        start_datetime: str = "",
        start_time: str = "",
        start_work_time: str = "",
        state: str = "",
        status: str = "",
        subject: str = "",
        table_id: str = "",
        table_name: str = "",
        tags: str = "",
        task: str = "",
        team: Dict[str, Any] = None,
        team_name: str = "",
        temperature: str = "",
        text: str = "",
        text_for_extraction: str = "",
        timezone: str = "",
        title: str = "",
        to_number: str = "",
        transfer_number: str = "",
        value: str = "",
        wait_for_greeting: bool = False,
        warehouse: str = "",
        warehouse_id: str = "",
        website: str = "",
        wordpress_url: str = "",
        date_range: Optional[Any] = None,
        **kwargs
    ):
        # Initialize with params
        params = {}
        params["integration_type"] = integration_type
        params["action"] = action
        params["use_date"] = use_date
        params["use_exact_date"] = use_exact_date

        super().__init__(
            node_type="integration",
            params=params,
            id=id,
            node_name=node_name,
            execution_mode=execution_mode,
        )

        # Set input values
        if integration_type is not None:
            self.inputs["integration_type"] = integration_type
        if action is not None:
            self.inputs["action"] = action
        if function is not None:
            self.inputs["function"] = function
        if integration is not None:
            self.inputs["integration"] = integration
        if recipients is not None:
            self.inputs["recipients"] = recipients
        if body is not None:
            self.inputs["body"] = body
        if subject is not None:
            self.inputs["subject"] = subject
        if email_id is not None:
            self.inputs["email_id"] = email_id
        if name is not None:
            self.inputs["name"] = name
        if email is not None:
            self.inputs["email"] = email
        if channel_name is not None:
            self.inputs["channel_name"] = channel_name
        if message is not None:
            self.inputs["message"] = message
        if title is not None:
            self.inputs["title"] = title
        if team_name is not None:
            self.inputs["team_name"] = team_name
        if description is not None:
            self.inputs["description"] = description
        if issue_name is not None:
            self.inputs["issue_name"] = issue_name
        if comment is not None:
            self.inputs["comment"] = comment
        if format is not None:
            self.inputs["format"] = format
        if attachments is not None:
            self.inputs["attachments"] = attachments
        if item_id is not None:
            self.inputs["item_id"] = item_id
        if use_date is not None:
            self.inputs["use_date"] = use_date
        if use_exact_date is not None:
            self.inputs["use_exact_date"] = use_exact_date
        if num_messages is not None:
            self.inputs["num_messages"] = num_messages
        if date_range is not None:
            self.inputs["date_range"] = date_range
        if exact_date is not None:
            self.inputs["exact_date"] = exact_date
        if sql_query is not None:
            self.inputs["sql_query"] = sql_query
        if team is not None:
            self.inputs["team"] = team
        if channel is not None:
            self.inputs["channel"] = channel
        if module is not None:
            self.inputs["module"] = module
        if filter is not None:
            self.inputs["filter"] = filter
        if owner_name is not None:
            self.inputs["owner_name"] = owner_name
        if repo_name is not None:
            self.inputs["repo_name"] = repo_name
        if branch_name is not None:
            self.inputs["branch_name"] = branch_name
        if file_name is not None:
            self.inputs["file_name"] = file_name
        if base is not None:
            self.inputs["base"] = base
        if head is not None:
            self.inputs["head"] = head
        if pull_number is not None:
            self.inputs["pull_number"] = pull_number
        if requester_email is not None:
            self.inputs["requester_email"] = requester_email
        if requester_name is not None:
            self.inputs["requester_name"] = requester_name
        if query is not None:
            self.inputs["query"] = query
        if text is not None:
            self.inputs["text"] = text
        if first_name is not None:
            self.inputs["first_name"] = first_name
        if last_name is not None:
            self.inputs["last_name"] = last_name
        if phone is not None:
            self.inputs["phone"] = phone
        if status is not None:
            self.inputs["status"] = status
        if value is not None:
            self.inputs["value"] = value
        if pipeline_name is not None:
            self.inputs["pipeline_name"] = pipeline_name
        if contact_name is not None:
            self.inputs["contact_name"] = contact_name
        if location is not None:
            self.inputs["location"] = location
        if company is not None:
            self.inputs["company"] = company
        if profile_url is not None:
            self.inputs["profile_url"] = profile_url
        if country is not None:
            self.inputs["country"] = country
        if job_titles is not None:
            self.inputs["job_titles"] = job_titles
        if job_company_names is not None:
            self.inputs["job_company_names"] = job_company_names
        if skills is not None:
            self.inputs["skills"] = skills
        if number_of_results is not None:
            self.inputs["number_of_results"] = number_of_results
        if es_query is not None:
            self.inputs["es_query"] = es_query
        if sql is not None:
            self.inputs["sql"] = sql
        if profile is not None:
            self.inputs["profile"] = profile
        if website is not None:
            self.inputs["website"] = website
        if tags is not None:
            self.inputs["tags"] = tags
        if industries is not None:
            self.inputs["industries"] = industries
        if company_size_ranges is not None:
            self.inputs["company_size_ranges"] = company_size_ranges
        if founded_year_range is not None:
            self.inputs["founded_year_range"] = founded_year_range
        if domain is not None:
            self.inputs["domain"] = domain
        if city is not None:
            self.inputs["city"] = city
        if industry is not None:
            self.inputs["industry"] = industry
        if state is not None:
            self.inputs["state"] = state
        if associated_object_id is not None:
            self.inputs["associated_object_id"] = associated_object_id
        if associated_object_type is not None:
            self.inputs["associated_object_type"] = associated_object_type
        if firstname is not None:
            self.inputs["firstname"] = firstname
        if lastname is not None:
            self.inputs["lastname"] = lastname
        if amount is not None:
            self.inputs["amount"] = amount
        if closedate is not None:
            self.inputs["closedate"] = closedate
        if dealname is not None:
            self.inputs["dealname"] = dealname
        if pipeline is not None:
            self.inputs["pipeline"] = pipeline
        if dealstage is not None:
            self.inputs["dealstage"] = dealstage
        if hs_pipeline is not None:
            self.inputs["hs_pipeline"] = hs_pipeline
        if hs_pipeline_stage is not None:
            self.inputs["hs_pipeline_stage"] = hs_pipeline_stage
        if hs_ticket_priority is not None:
            self.inputs["hs_ticket_priority"] = hs_ticket_priority
        if duration is not None:
            self.inputs["duration"] = duration
        if from_number is not None:
            self.inputs["from_number"] = from_number
        if to_number is not None:
            self.inputs["to_number"] = to_number
        if priority is not None:
            self.inputs["priority"] = priority
        if start_time is not None:
            self.inputs["start_time"] = start_time
        if end_time is not None:
            self.inputs["end_time"] = end_time
        if meeting_notes is not None:
            self.inputs["meeting_notes"] = meeting_notes
        if recipient_email is not None:
            self.inputs["recipient_email"] = recipient_email
        if sender_email is not None:
            self.inputs["sender_email"] = sender_email
        if direction is not None:
            self.inputs["direction"] = direction
        if query_type is not None:
            self.inputs["query_type"] = query_type
        if warehouse is not None:
            self.inputs["warehouse"] = warehouse
        if database is not None:
            self.inputs["database"] = database
        if schema is not None:
            self.inputs["schema"] = schema
        if sql_generation_model is not None:
            self.inputs["sql_generation_model"] = sql_generation_model
        if query_agent_model is not None:
            self.inputs["query_agent_model"] = query_agent_model
        if index is not None:
            self.inputs["index"] = index
        if collection is not None:
            self.inputs["collection"] = collection
        if embedding_model is not None:
            self.inputs["embedding_model"] = embedding_model
        if namespace is not None:
            self.inputs["namespace"] = namespace
        if wordpress_url is not None:
            self.inputs["wordpress_url"] = wordpress_url
        if post_title is not None:
            self.inputs["post_title"] = post_title
        if post_content is not None:
            self.inputs["post_content"] = post_content
        if post_text is not None:
            self.inputs["post_text"] = post_text
        if calendar is not None:
            self.inputs["calendar"] = calendar
        if event_name is not None:
            self.inputs["event_name"] = event_name
        if start_datetime is not None:
            self.inputs["start_datetime"] = start_datetime
        if attendees is not None:
            self.inputs["attendees"] = attendees
        if start_date is not None:
            self.inputs["start_date"] = start_date
        if start_work_time is not None:
            self.inputs["start_work_time"] = start_work_time
        if end_date is not None:
            self.inputs["end_date"] = end_date
        if end_work_time is not None:
            self.inputs["end_work_time"] = end_work_time
        if slot_duration is not None:
            self.inputs["slot_duration"] = slot_duration
        if timezone is not None:
            self.inputs["timezone"] = timezone
        if from_name is not None:
            self.inputs["from_name"] = from_name
        if from_email is not None:
            self.inputs["from_email"] = from_email
        if cc_recipients is not None:
            self.inputs["cc_recipients"] = cc_recipients
        if bcc_recipients is not None:
            self.inputs["bcc_recipients"] = bcc_recipients
        if list_name is not None:
            self.inputs["list_name"] = list_name
        if file_id is not None:
            self.inputs["file_id"] = file_id
        if content is not None:
            self.inputs["content"] = content
        if form_id is not None:
            self.inputs["form_id"] = form_id
        if number_of_responses is not None:
            self.inputs["number_of_responses"] = number_of_responses
        if folder_id is not None:
            self.inputs["folder_id"] = folder_id
        if files is not None:
            self.inputs["files"] = files
        if file is not None:
            self.inputs["file"] = file
        if sheet_id is not None:
            self.inputs["sheet_id"] = sheet_id
        if provider is not None:
            self.inputs["provider"] = provider
        if model is not None:
            self.inputs["model"] = model
        if processed_outputs is not None:
            self.inputs["processed_outputs"] = processed_outputs
        if sheet_url is not None:
            self.inputs["sheet_url"] = sheet_url
        if selected_input_dynamic_handle_names is not None:
            self.inputs["selected_input_dynamic_handle_names"] = (
                selected_input_dynamic_handle_names
            )
        if text_for_extraction is not None:
            self.inputs["text_for_extraction"] = text_for_extraction
        if extract_multiple_rows is not None:
            self.inputs["extract_multiple_rows"] = extract_multiple_rows
        if manual_columns is not None:
            self.inputs["manual_columns"] = manual_columns
        if add_columns_manually is not None:
            self.inputs["add_columns_manually"] = add_columns_manually
        if additional_context is not None:
            self.inputs["additional_context"] = additional_context
        if base_id is not None:
            self.inputs["base_id"] = base_id
        if table_id is not None:
            self.inputs["table_id"] = table_id
        if warehouse_id is not None:
            self.inputs["warehouse_id"] = warehouse_id
        if catalog_name is not None:
            self.inputs["catalog_name"] = catalog_name
        if schema_name is not None:
            self.inputs["schema_name"] = schema_name
        if table_name is not None:
            self.inputs["table_name"] = table_name
        if properties is not None:
            self.inputs["properties"] = properties
        if phone_number is not None:
            self.inputs["phone_number"] = phone_number
        if task is not None:
            self.inputs["task"] = task
        if first_sentence is not None:
            self.inputs["first_sentence"] = first_sentence
        if pathway_id is not None:
            self.inputs["pathway_id"] = pathway_id
        if temperature is not None:
            self.inputs["temperature"] = temperature
        if transfer_number is not None:
            self.inputs["transfer_number"] = transfer_number
        if wait_for_greeting is not None:
            self.inputs["wait_for_greeting"] = wait_for_greeting
        if return_mode is not None:
            self.inputs["return_mode"] = return_mode
        if company_name is not None:
            self.inputs["company_name"] = company_name
        if keywords is not None:
            self.inputs["keywords"] = keywords
        if min_size is not None:
            self.inputs["min_size"] = min_size
        if max_size is not None:
            self.inputs["max_size"] = max_size
        if num_results is not None:
            self.inputs["num_results"] = num_results
        if first_name_input is not None:
            self.inputs["first_name_input"] = first_name_input
        if last_name_input is not None:
            self.inputs["last_name_input"] = last_name_input
        if linkedin_url_input is not None:
            self.inputs["linkedin_url_input"] = linkedin_url_input
        if date_range is not None:
            self.inputs["date_range"] = date_range

        # Update any additional inputs
        if kwargs:
            self.update_inputs(**kwargs)

    @property
    def annual_revenue(self) -> str:
        """
        The annual_revenue output

        Available: When integration_type = 'Apollo' and action = 'enrich_company'


        Raises:
            AttributeError: If this output is not available for the current parameter values
        """
        return self.__getattr__("annual_revenue")

    @property
    def answered_by(self) -> str:
        """
        The answered_by output

        Available: When integration_type = 'Bland AI'


        Raises:
            AttributeError: If this output is not available for the current parameter values
        """
        return self.__getattr__("answered_by")

    @property
    def attachment_names(self) -> List[List[str]]:
        """
        The attachment_names output

        Available: When integration_type = 'Slack' and action = 'read_message'


        Raises:
            AttributeError: If this output is not available for the current parameter values
        """
        return self.__getattr__("attachment_names")

    @property
    def attachments(self) -> List[List[str]]:
        """
        The attachments output

        Available: When integration_type = 'Outlook' and action = 'read_email'


        Raises:
            AttributeError: If this output is not available for the current parameter values
        """
        return self.__getattr__("attachments")

    @property
    def company_name(self) -> str:
        """
        The company_name output

        Available: When integration_type = 'Apollo' and action = 'enrich_company'


        Raises:
            AttributeError: If this output is not available for the current parameter values
        """
        return self.__getattr__("company_name")

    @property
    def company_names(self) -> str:
        """
        The company_names output

        Available: When integration_type = 'Apollo' and action = 'fetch_companies'


        Raises:
            AttributeError: If this output is not available for the current parameter values
        """
        return self.__getattr__("company_names")

    @property
    def country(self) -> str:
        """
        The country output

        Available: When integration_type = 'Apollo' and action = 'enrich_company'


        Raises:
            AttributeError: If this output is not available for the current parameter values
        """
        return self.__getattr__("country")

    @property
    def domains(self) -> str:
        """
        The domains output

        Available: When integration_type = 'Apollo' and action = 'fetch_companies'


        Raises:
            AttributeError: If this output is not available for the current parameter values
        """
        return self.__getattr__("domains")

    @property
    def email(self) -> str:
        """
        The email output

        Available: When integration_type = 'Apollo' and action = 'enrich_contact'


        Raises:
            AttributeError: If this output is not available for the current parameter values
        """
        return self.__getattr__("email")

    @property
    def email_bodies(self) -> List[str]:
        """
        The email_bodies output

        Available: When integration_type = 'Outlook' and action = 'read_email'


        Raises:
            AttributeError: If this output is not available for the current parameter values
        """
        return self.__getattr__("email_bodies")

    @property
    def email_dates(self) -> List[str]:
        """
        The email_dates output

        Available: When integration_type = 'Outlook' and action = 'read_email'


        Raises:
            AttributeError: If this output is not available for the current parameter values
        """
        return self.__getattr__("email_dates")

    @property
    def email_display_names(self) -> List[str]:
        """
        The email_display_names output

        Available: When integration_type = 'Outlook' and action = 'read_email'


        Raises:
            AttributeError: If this output is not available for the current parameter values
        """
        return self.__getattr__("email_display_names")

    @property
    def email_ids(self) -> List[str]:
        """
        The email_ids output

        Available: When integration_type = 'Outlook' and action = 'read_email'


        Raises:
            AttributeError: If this output is not available for the current parameter values
        """
        return self.__getattr__("email_ids")

    @property
    def email_subjects(self) -> List[str]:
        """
        The email_subjects output

        Available: When integration_type = 'Outlook' and action = 'read_email'


        Raises:
            AttributeError: If this output is not available for the current parameter values
        """
        return self.__getattr__("email_subjects")

    @property
    def first_name(self) -> str:
        """
        The first_name output

        Available: When integration_type = 'Apollo' and action = 'enrich_contact'


        Raises:
            AttributeError: If this output is not available for the current parameter values
        """
        return self.__getattr__("first_name")

    @property
    def industry(self) -> str:
        """
        The industry output

        Available: When integration_type = 'Apollo' and action = 'enrich_company'


        Raises:
            AttributeError: If this output is not available for the current parameter values
        """
        return self.__getattr__("industry")

    @property
    def job_title(self) -> str:
        """
        The job_title output

        Available: When integration_type = 'Apollo' and action = 'enrich_contact'


        Raises:
            AttributeError: If this output is not available for the current parameter values
        """
        return self.__getattr__("job_title")

    @property
    def last_name(self) -> str:
        """
        The last_name output

        Available: When integration_type = 'Apollo' and action = 'enrich_contact'


        Raises:
            AttributeError: If this output is not available for the current parameter values
        """
        return self.__getattr__("last_name")

    @property
    def linkedin_url(self) -> str:
        """
        The linkedin_url output

        Available: When integration_type = 'Apollo' and action = 'enrich_company', When integration_type = 'Apollo' and action = 'enrich_contact'


        Raises:
            AttributeError: If this output is not available for the current parameter values
        """
        return self.__getattr__("linkedin_url")

    @property
    def linkedin_urls(self) -> str:
        """
        The linkedin_urls output

        Available: When integration_type = 'Apollo' and action = 'fetch_companies'


        Raises:
            AttributeError: If this output is not available for the current parameter values
        """
        return self.__getattr__("linkedin_urls")

    @property
    def list_of_responses(self) -> List[str]:
        """
        The list_of_responses output

        Available: When integration_type = 'Typeform' and action = 'get_responses'


        Raises:
            AttributeError: If this output is not available for the current parameter values
        """
        return self.__getattr__("list_of_responses")

    @property
    def message(self) -> List[str]:
        """
        The message output

        Available: When integration_type = 'Slack' and action = 'read_message'


        Raises:
            AttributeError: If this output is not available for the current parameter values
        """
        return self.__getattr__("message")

    @property
    def num_employees(self) -> str:
        """
        The num_employees output

        Available: When integration_type = 'Apollo' and action = 'enrich_company'


        Raises:
            AttributeError: If this output is not available for the current parameter values
        """
        return self.__getattr__("num_employees")

    @property
    def output(self) -> str:
        """
        The output output

        Different behavior based on configuration:
          - The output output (When integration_type = 'Salesforce' and action = 'run_sql_query', When integration_type = 'Github' and action = 'read_file', When integration_type = 'Supabase S3' and action = 'search_files', When integration_type = 'PeopleDataLabs' and action = 'enrich_person', When integration_type = 'PeopleDataLabs' and action = 'search_people', When integration_type = 'PeopleDataLabs' and action = 'search_people_query', When integration_type = 'PeopleDataLabs' and action = 'enrich_company', When integration_type = 'PeopleDataLabs' and action = 'search_companies', When integration_type = 'PeopleDataLabs' and action = 'search_companies_query', When integration_type = 'Hubspot' and action = 'fetch_contacts', When integration_type = 'Hubspot' and action = 'fetch_companies', When integration_type = 'Hubspot' and action = 'fetch_deals', When integration_type = 'Hubspot' and action = 'fetch_tickets', When integration_type = 'Hubspot' and action = 'fetch_notes', When integration_type = 'Hubspot' and action = 'fetch_calls', When integration_type = 'Hubspot' and action = 'fetch_tasks', When integration_type = 'Hubspot' and action = 'fetch_meetings', When integration_type = 'Hubspot' and action = 'fetch_emails', When integration_type = 'Elasticsearch' and action = 'search_index', When integration_type = 'MongoDB', When integration_type = 'Postgres', When integration_type = 'MySQL', When integration_type = 'Linkedin' and action = 'create_text_share', When integration_type = 'Google Calendar', When integration_type = 'Microsoft Calendar', When integration_type = 'Mailgun', When integration_type = 'Microsoft' and action = 'read_file', When integration_type = 'Weaviate')
          - The output output (When integration_type = 'SugarCRM' and action = 'get_records', When integration_type = 'Snowflake', When integration_type = 'Pinecone' and action = 'query_pinecone', When integration_type = 'Algolia')


        Raises:
            AttributeError: If this output is not available for the current parameter values
        """
        return self.__getattr__("output")

    @property
    def phone_number(self) -> str:
        """
        The phone_number output

        Available: When integration_type = 'Apollo' and action = 'enrich_contact'


        Raises:
            AttributeError: If this output is not available for the current parameter values
        """
        return self.__getattr__("phone_number")

    @property
    def post_url(self) -> str:
        """
        The post_url output

        Available: When integration_type = 'X' and action = 'create_post', When integration_type = 'X' and action = 'create_thread', When integration_type = 'Wordpress' and action = 'create_post'


        Raises:
            AttributeError: If this output is not available for the current parameter values
        """
        return self.__getattr__("post_url")

    @property
    def recipient_addresses(self) -> List[str]:
        """
        The recipient_addresses output

        Available: When integration_type = 'Outlook' and action = 'read_email'


        Raises:
            AttributeError: If this output is not available for the current parameter values
        """
        return self.__getattr__("recipient_addresses")

    @property
    def sender_addresses(self) -> List[str]:
        """
        The sender_addresses output

        Available: When integration_type = 'Outlook' and action = 'read_email'


        Raises:
            AttributeError: If this output is not available for the current parameter values
        """
        return self.__getattr__("sender_addresses")

    @property
    def sender_id(self) -> List[str]:
        """
        The sender_id output

        Available: When integration_type = 'Slack' and action = 'read_message'


        Raises:
            AttributeError: If this output is not available for the current parameter values
        """
        return self.__getattr__("sender_id")

    @property
    def table(self) -> str:
        """
        The table output

        Available: When integration_type = 'Google Sheets' and action = 'extract_to_table'


        Raises:
            AttributeError: If this output is not available for the current parameter values
        """
        return self.__getattr__("table")

    @property
    def text(self) -> str:
        """
        The text output

        Available: When integration_type = 'Google Docs' and action = 'read_doc', When integration_type = 'Google Drive' and action = 'read_drive'


        Raises:
            AttributeError: If this output is not available for the current parameter values
        """
        return self.__getattr__("text")

    @property
    def thread_id(self) -> List[str]:
        """
        The thread_id output

        Available: When integration_type = 'Slack' and action = 'read_message'


        Raises:
            AttributeError: If this output is not available for the current parameter values
        """
        return self.__getattr__("thread_id")

    @property
    def thread_link(self) -> List[str]:
        """
        The thread_link output

        Available: When integration_type = 'Slack' and action = 'read_message'


        Raises:
            AttributeError: If this output is not available for the current parameter values
        """
        return self.__getattr__("thread_link")

    @property
    def total_funding(self) -> str:
        """
        The total_funding output

        Available: When integration_type = 'Apollo' and action = 'enrich_company'


        Raises:
            AttributeError: If this output is not available for the current parameter values
        """
        return self.__getattr__("total_funding")

    @property
    def transcript(self) -> str:
        """
        The transcript output

        Available: When integration_type = 'Bland AI'


        Raises:
            AttributeError: If this output is not available for the current parameter values
        """
        return self.__getattr__("transcript")

    @property
    def website(self) -> str:
        """
        The website output

        Available: When integration_type = 'Apollo' and action = 'enrich_company'


        Raises:
            AttributeError: If this output is not available for the current parameter values
        """
        return self.__getattr__("website")

    @property
    def websites(self) -> str:
        """
        The websites output

        Available: When integration_type = 'Apollo' and action = 'fetch_companies'


        Raises:
            AttributeError: If this output is not available for the current parameter values
        """
        return self.__getattr__("websites")

    @classmethod
    def from_dict(cls, data: dict) -> "IntegrationNode":
        """Create a node instance from a dictionary."""
        inputs = data.get("inputs", {})
        id = data.get("id", None)
        name = data.get("name", None)
        execution_mode = data.get("execution_mode", None)
        return cls(**inputs, id=id, node_name=name, execution_mode=execution_mode)


@Node.register_node_type("zapier")
class ZapierNode(Node):
    """


    ## Inputs
    ### Common Inputs
        payload: The payload input
        webhook_url: The webhook_url input

    ## Outputs
        None
    """

    # Common inputs and outputs
    _COMMON_INPUTS = [
        {
            "field": "payload",
            "helper_text": "The payload input",
            "value": "",
            "type": "string",
        },
        {
            "field": "webhook_url",
            "helper_text": "The webhook_url input",
            "value": "",
            "type": "string",
        },
    ]

    # Common outputs and inputs
    _COMMON_OUTPUTS = []

    # Configuration patterns and their associated inputs/outputs
    _CONFIGS = {}

    # List of parameters that affect configuration
    _PARAMS = []

    def __init__(
        self,
        id: Optional[str] = None,
        node_name: Optional[str] = None,
        execution_mode: Optional[str] = None,
        payload: str = "",
        webhook_url: str = "",
        **kwargs
    ):
        # Initialize with params
        params = {}

        super().__init__(
            node_type="zapier",
            params=params,
            id=id,
            node_name=node_name,
            execution_mode=execution_mode,
        )

        # Set input values
        if payload is not None:
            self.inputs["payload"] = payload
        if webhook_url is not None:
            self.inputs["webhook_url"] = webhook_url

        # Update any additional inputs
        if kwargs:
            self.update_inputs(**kwargs)

    @classmethod
    def from_dict(cls, data: dict) -> "ZapierNode":
        """Create a node instance from a dictionary."""
        inputs = data.get("inputs", {})
        id = data.get("id", None)
        name = data.get("name", None)
        execution_mode = data.get("execution_mode", None)
        return cls(**inputs, id=id, node_name=name, execution_mode=execution_mode)


@Node.register_node_type("make")
class MakeNode(Node):
    """


    ## Inputs
    ### Common Inputs
        payload: The payload input
        webhook_url: The webhook_url input

    ## Outputs
        None
    """

    # Common inputs and outputs
    _COMMON_INPUTS = [
        {
            "field": "payload",
            "helper_text": "The payload input",
            "value": "",
            "type": "string",
        },
        {
            "field": "webhook_url",
            "helper_text": "The webhook_url input",
            "value": "",
            "type": "string",
        },
    ]

    # Common outputs and inputs
    _COMMON_OUTPUTS = []

    # Configuration patterns and their associated inputs/outputs
    _CONFIGS = {}

    # List of parameters that affect configuration
    _PARAMS = []

    def __init__(
        self,
        id: Optional[str] = None,
        node_name: Optional[str] = None,
        execution_mode: Optional[str] = None,
        payload: str = "",
        webhook_url: str = "",
        **kwargs
    ):
        # Initialize with params
        params = {}

        super().__init__(
            node_type="make",
            params=params,
            id=id,
            node_name=node_name,
            execution_mode=execution_mode,
        )

        # Set input values
        if payload is not None:
            self.inputs["payload"] = payload
        if webhook_url is not None:
            self.inputs["webhook_url"] = webhook_url

        # Update any additional inputs
        if kwargs:
            self.update_inputs(**kwargs)

    @classmethod
    def from_dict(cls, data: dict) -> "MakeNode":
        """Create a node instance from a dictionary."""
        inputs = data.get("inputs", {})
        id = data.get("id", None)
        name = data.get("name", None)
        execution_mode = data.get("execution_mode", None)
        return cls(**inputs, id=id, node_name=name, execution_mode=execution_mode)


@Node.register_node_type("text_manipulation")
class TextManipulationNode(Node):
    """


    ## Inputs
    ### Common Inputs
        sub_type: The sub_type input

    ## Outputs
        None
    """

    # Common inputs and outputs
    _COMMON_INPUTS = [
        {
            "field": "sub_type",
            "helper_text": "The sub_type input",
            "value": "",
            "type": "string",
        }
    ]

    # Common outputs and inputs
    _COMMON_OUTPUTS = []

    # Configuration patterns and their associated inputs/outputs
    _CONFIGS = {}

    # List of parameters that affect configuration
    _PARAMS = []

    def __init__(
        self,
        id: Optional[str] = None,
        node_name: Optional[str] = None,
        execution_mode: Optional[str] = None,
        sub_type: str = "",
        **kwargs
    ):
        # Initialize with params
        params = {}

        super().__init__(
            node_type="text_manipulation",
            params=params,
            id=id,
            node_name=node_name,
            execution_mode=execution_mode,
        )

        # Set input values
        if sub_type is not None:
            self.inputs["sub_type"] = sub_type

        # Update any additional inputs
        if kwargs:
            self.update_inputs(**kwargs)

    @classmethod
    def from_dict(cls, data: dict) -> "TextManipulationNode":
        """Create a node instance from a dictionary."""
        inputs = data.get("inputs", {})
        id = data.get("id", None)
        name = data.get("name", None)
        execution_mode = data.get("execution_mode", None)
        return cls(**inputs, id=id, node_name=name, execution_mode=execution_mode)


@Node.register_node_type("file_operations")
class FileOperationsNode(Node):
    """


    ## Inputs
    ### Common Inputs
        sub_type: The sub_type input

    ## Outputs
        None
    """

    # Common inputs and outputs
    _COMMON_INPUTS = [
        {
            "field": "sub_type",
            "helper_text": "The sub_type input",
            "value": "",
            "type": "string",
        }
    ]

    # Common outputs and inputs
    _COMMON_OUTPUTS = []

    # Configuration patterns and their associated inputs/outputs
    _CONFIGS = {}

    # List of parameters that affect configuration
    _PARAMS = []

    def __init__(
        self,
        id: Optional[str] = None,
        node_name: Optional[str] = None,
        execution_mode: Optional[str] = None,
        sub_type: str = "",
        **kwargs
    ):
        # Initialize with params
        params = {}

        super().__init__(
            node_type="file_operations",
            params=params,
            id=id,
            node_name=node_name,
            execution_mode=execution_mode,
        )

        # Set input values
        if sub_type is not None:
            self.inputs["sub_type"] = sub_type

        # Update any additional inputs
        if kwargs:
            self.update_inputs(**kwargs)

    @classmethod
    def from_dict(cls, data: dict) -> "FileOperationsNode":
        """Create a node instance from a dictionary."""
        inputs = data.get("inputs", {})
        id = data.get("id", None)
        name = data.get("name", None)
        execution_mode = data.get("execution_mode", None)
        return cls(**inputs, id=id, node_name=name, execution_mode=execution_mode)


@Node.register_node_type("ai_operations")
class AiOperationsNode(Node):
    """


    ## Inputs
    ### Common Inputs
        sub_type: The sub_type input

    ## Outputs
        None
    """

    # Common inputs and outputs
    _COMMON_INPUTS = [
        {
            "field": "sub_type",
            "helper_text": "The sub_type input",
            "value": "",
            "type": "string",
        }
    ]

    # Common outputs and inputs
    _COMMON_OUTPUTS = []

    # Configuration patterns and their associated inputs/outputs
    _CONFIGS = {}

    # List of parameters that affect configuration
    _PARAMS = []

    def __init__(
        self,
        id: Optional[str] = None,
        node_name: Optional[str] = None,
        execution_mode: Optional[str] = None,
        sub_type: str = "",
        **kwargs
    ):
        # Initialize with params
        params = {}

        super().__init__(
            node_type="ai_operations",
            params=params,
            id=id,
            node_name=node_name,
            execution_mode=execution_mode,
        )

        # Set input values
        if sub_type is not None:
            self.inputs["sub_type"] = sub_type

        # Update any additional inputs
        if kwargs:
            self.update_inputs(**kwargs)

    @classmethod
    def from_dict(cls, data: dict) -> "AiOperationsNode":
        """Create a node instance from a dictionary."""
        inputs = data.get("inputs", {})
        id = data.get("id", None)
        name = data.get("name", None)
        execution_mode = data.get("execution_mode", None)
        return cls(**inputs, id=id, node_name=name, execution_mode=execution_mode)


@Node.register_node_type("file_to_text")
class FileToTextNode(Node):
    """
    Convert data from type File to type Text

    ## Inputs
    ### Common Inputs
        chunk_text: Whether to chunk the text into smaller pieces.
        file: The file to convert to text.
        file_parser: The type of file parser to use.
        loader_type: The type of file to load.
    ### When chunk_text = True
        chunk_overlap: The overlap of each chunk of text.
        chunk_size: The size of each chunk of text.

    ## Outputs
    ### When chunk_text = True
        processed_text: The text as a list of chunks.
    ### When chunk_text = False
        processed_text: The text as a string.
    """

    # Common inputs and outputs
    _COMMON_INPUTS = [
        {
            "field": "chunk_text",
            "helper_text": "Whether to chunk the text into smaller pieces.",
            "value": False,
            "type": "bool",
        },
        {
            "field": "file",
            "helper_text": "The file to convert to text.",
            "value": None,
            "type": "file",
        },
        {
            "field": "file_parser",
            "helper_text": "The type of file parser to use.",
            "value": "default",
            "type": "enum<string>",
        },
        {
            "field": "loader_type",
            "helper_text": "The type of file to load.",
            "value": "File",
            "type": "enum<string>",
        },
    ]

    # Common outputs and inputs
    _COMMON_OUTPUTS = []

    # Configuration patterns and their associated inputs/outputs
    _CONFIGS = {
        "true": {
            "inputs": [
                {
                    "field": "chunk_size",
                    "type": "int32",
                    "value": 1024,
                    "helper_text": "The size of each chunk of text.",
                },
                {
                    "field": "chunk_overlap",
                    "type": "int32",
                    "value": 400,
                    "helper_text": "The overlap of each chunk of text.",
                },
            ],
            "outputs": [
                {
                    "field": "processed_text",
                    "type": "vec<string>",
                    "helper_text": "The text as a list of chunks.",
                }
            ],
        },
        "false": {
            "inputs": [],
            "outputs": [
                {
                    "field": "processed_text",
                    "type": "string",
                    "helper_text": "The text as a string.",
                }
            ],
        },
    }

    # List of parameters that affect configuration
    _PARAMS = ["chunk_text"]

    def __init__(
        self,
        id: Optional[str] = None,
        node_name: Optional[str] = None,
        execution_mode: Optional[str] = None,
        chunk_text: bool = False,
        chunk_overlap: int = 400,
        chunk_size: int = 1024,
        file: Optional[str] = None,
        file_parser: str = "default",
        loader_type: str = "File",
        **kwargs
    ):
        # Initialize with params
        params = {}
        params["chunk_text"] = chunk_text

        super().__init__(
            node_type="file_to_text",
            params=params,
            id=id,
            node_name=node_name,
            execution_mode=execution_mode,
        )

        # Set input values
        if file is not None:
            self.inputs["file"] = file
        if chunk_text is not None:
            self.inputs["chunk_text"] = chunk_text
        if file_parser is not None:
            self.inputs["file_parser"] = file_parser
        if loader_type is not None:
            self.inputs["loader_type"] = loader_type
        if chunk_size is not None:
            self.inputs["chunk_size"] = chunk_size
        if chunk_overlap is not None:
            self.inputs["chunk_overlap"] = chunk_overlap

        # Update any additional inputs
        if kwargs:
            self.update_inputs(**kwargs)

    @property
    def processed_text(self) -> List[str]:
        """
        The text as a list of chunks.

        Different behavior based on configuration:
          - The text as a list of chunks. (When chunk_text = True)
          - The text as a string. (When chunk_text = False)


        Raises:
            AttributeError: If this output is not available for the current parameter values
        """
        return self.__getattr__("processed_text")

    @classmethod
    def from_dict(cls, data: dict) -> "FileToTextNode":
        """Create a node instance from a dictionary."""
        inputs = data.get("inputs", {})
        id = data.get("id", None)
        name = data.get("name", None)
        execution_mode = data.get("execution_mode", None)
        return cls(**inputs, id=id, node_name=name, execution_mode=execution_mode)


@Node.register_node_type("code_execution")
class CodeExecutionNode(Node):
    """


    ## Inputs
    ### Common Inputs
        code: The code input
        language: The language input

    ## Outputs
    ### Common Outputs
        outputs: The outputs output
    """

    # Common inputs and outputs
    _COMMON_INPUTS = [
        {
            "field": "code",
            "helper_text": "The code input",
            "value": "",
            "type": "string",
        },
        {
            "field": "language",
            "helper_text": "The language input",
            "value": 0,
            "type": "enum<int32>",
        },
    ]

    # Common outputs and inputs
    _COMMON_OUTPUTS = [{"field": "outputs", "helper_text": "The outputs output"}]

    # Configuration patterns and their associated inputs/outputs
    _CONFIGS = {}

    # List of parameters that affect configuration
    _PARAMS = []

    def __init__(
        self,
        id: Optional[str] = None,
        node_name: Optional[str] = None,
        execution_mode: Optional[str] = None,
        code: str = "",
        language: int = 0,
        **kwargs
    ):
        # Initialize with params
        params = {}

        super().__init__(
            node_type="code_execution",
            params=params,
            id=id,
            node_name=node_name,
            execution_mode=execution_mode,
        )

        # Set input values
        if code is not None:
            self.inputs["code"] = code
        if language is not None:
            self.inputs["language"] = language

        # Update any additional inputs
        if kwargs:
            self.update_inputs(**kwargs)

    @property
    def outputs(self) -> str:
        """
        The outputs output


        Raises:
            AttributeError: If this output is not available for the current parameter values
        """
        return self.__getattr__("outputs")

    @classmethod
    def from_dict(cls, data: dict) -> "CodeExecutionNode":
        """Create a node instance from a dictionary."""
        inputs = data.get("inputs", {})
        id = data.get("id", None)
        name = data.get("name", None)
        execution_mode = data.get("execution_mode", None)
        return cls(**inputs, id=id, node_name=name, execution_mode=execution_mode)


@Node.register_node_type("chunking")
class ChunkingNode(Node):
    """
    Split text into chunks. Supports different chunking strategies like markdown-aware, sentence-based, or dynamic sizing.

    ## Inputs
    ### Common Inputs
        chunk_overlap: The overlap of each chunk of text.
        chunk_size: The size of each chunk of text.
        splitter_method: Strategy for grouping segmented text into final chunks. 'sentence': groups sentences; 'markdown': respects Markdown structure (headers, code); 'dynamic': optimizes breaks for size using chosen segmentation method.
        text: The text to chunk
    ### dynamic
        segmentation_method: The method to break text into units before chunking. 'words': splits by word; 'sentences': splits by sentence boundary; 'paragraphs': splits by blank line/paragraph.

    ## Outputs
    ### Common Outputs
        chunks: The chunks output
    """

    # Common inputs and outputs
    _COMMON_INPUTS = [
        {
            "field": "chunk_overlap",
            "helper_text": "The overlap of each chunk of text.",
            "value": 0,
            "type": "int32",
        },
        {
            "field": "chunk_size",
            "helper_text": "The size of each chunk of text.",
            "value": 512,
            "type": "int32",
        },
        {
            "field": "splitter_method",
            "helper_text": "Strategy for grouping segmented text into final chunks. 'sentence': groups sentences; 'markdown': respects Markdown structure (headers, code); 'dynamic': optimizes breaks for size using chosen segmentation method.",
            "value": "markdown",
            "type": "enum<string>",
        },
        {
            "field": "text",
            "helper_text": "The text to chunk",
            "value": "",
            "type": "string",
        },
    ]

    # Common outputs and inputs
    _COMMON_OUTPUTS = [{"field": "chunks", "helper_text": "The chunks output"}]

    # Configuration patterns and their associated inputs/outputs
    _CONFIGS = {
        "dynamic": {
            "inputs": [
                {
                    "field": "segmentation_method",
                    "type": "enum<string>",
                    "value": "words",
                    "helper_text": "The method to break text into units before chunking. 'words': splits by word; 'sentences': splits by sentence boundary; 'paragraphs': splits by blank line/paragraph.",
                }
            ],
            "outputs": [],
        }
    }

    # List of parameters that affect configuration
    _PARAMS = ["splitter_method"]

    def __init__(
        self,
        id: Optional[str] = None,
        node_name: Optional[str] = None,
        execution_mode: Optional[str] = None,
        splitter_method: str = "markdown",
        chunk_overlap: int = 0,
        chunk_size: int = 512,
        segmentation_method: str = "words",
        text: str = "",
        **kwargs
    ):
        # Initialize with params
        params = {}
        params["splitter_method"] = splitter_method

        super().__init__(
            node_type="chunking",
            params=params,
            id=id,
            node_name=node_name,
            execution_mode=execution_mode,
        )

        # Set input values
        if text is not None:
            self.inputs["text"] = text
        if chunk_size is not None:
            self.inputs["chunk_size"] = chunk_size
        if chunk_overlap is not None:
            self.inputs["chunk_overlap"] = chunk_overlap
        if splitter_method is not None:
            self.inputs["splitter_method"] = splitter_method
        if segmentation_method is not None:
            self.inputs["segmentation_method"] = segmentation_method

        # Update any additional inputs
        if kwargs:
            self.update_inputs(**kwargs)

    @property
    def chunks(self) -> List[str]:
        """
        The chunks output


        Raises:
            AttributeError: If this output is not available for the current parameter values
        """
        return self.__getattr__("chunks")

    @classmethod
    def from_dict(cls, data: dict) -> "ChunkingNode":
        """Create a node instance from a dictionary."""
        inputs = data.get("inputs", {})
        id = data.get("id", None)
        name = data.get("name", None)
        execution_mode = data.get("execution_mode", None)
        return cls(**inputs, id=id, node_name=name, execution_mode=execution_mode)


@Node.register_node_type("notifications")
class NotificationsNode(Node):
    """


    ## Inputs
    ### Common Inputs
        sub_type: The sub_type input

    ## Outputs
        None
    """

    # Common inputs and outputs
    _COMMON_INPUTS = [
        {
            "field": "sub_type",
            "helper_text": "The sub_type input",
            "value": "",
            "type": "string",
        }
    ]

    # Common outputs and inputs
    _COMMON_OUTPUTS = []

    # Configuration patterns and their associated inputs/outputs
    _CONFIGS = {}

    # List of parameters that affect configuration
    _PARAMS = []

    def __init__(
        self,
        id: Optional[str] = None,
        node_name: Optional[str] = None,
        execution_mode: Optional[str] = None,
        sub_type: str = "",
        **kwargs
    ):
        # Initialize with params
        params = {}

        super().__init__(
            node_type="notifications",
            params=params,
            id=id,
            node_name=node_name,
            execution_mode=execution_mode,
        )

        # Set input values
        if sub_type is not None:
            self.inputs["sub_type"] = sub_type

        # Update any additional inputs
        if kwargs:
            self.update_inputs(**kwargs)

    @classmethod
    def from_dict(cls, data: dict) -> "NotificationsNode":
        """Create a node instance from a dictionary."""
        inputs = data.get("inputs", {})
        id = data.get("id", None)
        name = data.get("name", None)
        execution_mode = data.get("execution_mode", None)
        return cls(**inputs, id=id, node_name=name, execution_mode=execution_mode)


@Node.register_node_type("custom_smtp_email_sender")
class CustomSmtpEmailSenderNode(Node):
    """
    Send emails via SMTP

    ## Inputs
    ### Common Inputs
        connection_type: Security type: SSL, TLS, or STARTTLS
        email_body: Email content
        email_subject: Subject line of the email
        recipient_email: Recipient email address(es), comma-separated
        send_as_html: Send email in HTML format
        sender_email: Sender email address
        sender_name: Display name for sender (optional)
        sender_password: SMTP server password
        smtp_server: SMTP server hostname or IP
        smtp_server_port: SMTP server port (25, 465, 587)

    ## Outputs
        None
    """

    # Common inputs and outputs
    _COMMON_INPUTS = [
        {
            "field": "connection_type",
            "helper_text": "Security type: SSL, TLS, or STARTTLS",
            "value": "SSL",
            "type": "enum<string>",
        },
        {
            "field": "email_body",
            "helper_text": "Email content",
            "value": "",
            "type": "string",
        },
        {
            "field": "email_subject",
            "helper_text": "Subject line of the email",
            "value": "",
            "type": "string",
        },
        {
            "field": "recipient_email",
            "helper_text": "Recipient email address(es), comma-separated",
            "value": "",
            "type": "string",
        },
        {
            "field": "send_as_html",
            "helper_text": "Send email in HTML format",
            "value": "",
            "type": "bool",
        },
        {
            "field": "sender_email",
            "helper_text": "Sender email address",
            "value": "",
            "type": "string",
        },
        {
            "field": "sender_name",
            "helper_text": "Display name for sender (optional)",
            "value": "",
            "type": "string",
        },
        {
            "field": "sender_password",
            "helper_text": "SMTP server password",
            "value": "",
            "type": "string",
        },
        {
            "field": "smtp_server",
            "helper_text": "SMTP server hostname or IP",
            "value": "",
            "type": "string",
        },
        {
            "field": "smtp_server_port",
            "helper_text": "SMTP server port (25, 465, 587)",
            "value": 465,
            "type": "int32",
        },
    ]

    # Common outputs and inputs
    _COMMON_OUTPUTS = []

    # Configuration patterns and their associated inputs/outputs
    _CONFIGS = {}

    # List of parameters that affect configuration
    _PARAMS = []

    def __init__(
        self,
        id: Optional[str] = None,
        node_name: Optional[str] = None,
        execution_mode: Optional[str] = None,
        connection_type: str = "SSL",
        email_body: str = "",
        email_subject: str = "",
        recipient_email: str = "",
        send_as_html: bool = False,
        sender_email: str = "",
        sender_name: str = "",
        sender_password: str = "",
        smtp_server: str = "",
        smtp_server_port: int = 465,
        **kwargs
    ):
        # Initialize with params
        params = {}

        super().__init__(
            node_type="custom_smtp_email_sender",
            params=params,
            id=id,
            node_name=node_name,
            execution_mode=execution_mode,
        )

        # Set input values
        if recipient_email is not None:
            self.inputs["recipient_email"] = recipient_email
        if email_subject is not None:
            self.inputs["email_subject"] = email_subject
        if email_body is not None:
            self.inputs["email_body"] = email_body
        if send_as_html is not None:
            self.inputs["send_as_html"] = send_as_html
        if smtp_server is not None:
            self.inputs["smtp_server"] = smtp_server
        if smtp_server_port is not None:
            self.inputs["smtp_server_port"] = smtp_server_port
        if sender_email is not None:
            self.inputs["sender_email"] = sender_email
        if sender_password is not None:
            self.inputs["sender_password"] = sender_password
        if sender_name is not None:
            self.inputs["sender_name"] = sender_name
        if connection_type is not None:
            self.inputs["connection_type"] = connection_type

        # Update any additional inputs
        if kwargs:
            self.update_inputs(**kwargs)

    @classmethod
    def from_dict(cls, data: dict) -> "CustomSmtpEmailSenderNode":
        """Create a node instance from a dictionary."""
        inputs = data.get("inputs", {})
        id = data.get("id", None)
        name = data.get("name", None)
        execution_mode = data.get("execution_mode", None)
        return cls(**inputs, id=id, node_name=name, execution_mode=execution_mode)


@Node.register_node_type("email_notification")
class EmailNotificationNode(Node):
    """
    Send email notifications from no-reply@vectorshiftmail.com

    ## Inputs
    ### Common Inputs
        email_body: Email content
        email_subject: Subject line of the email
        recipient_email: Recipient email address(es), comma-separated
        send_as_html: Send email in HTML format

    ## Outputs
        None
    """

    # Common inputs and outputs
    _COMMON_INPUTS = [
        {
            "field": "email_body",
            "helper_text": "Email content",
            "value": "",
            "type": "string",
        },
        {
            "field": "email_subject",
            "helper_text": "Subject line of the email",
            "value": "",
            "type": "string",
        },
        {
            "field": "recipient_email",
            "helper_text": "Recipient email address(es), comma-separated",
            "value": "",
            "type": "string",
        },
        {
            "field": "send_as_html",
            "helper_text": "Send email in HTML format",
            "value": "",
            "type": "bool",
        },
    ]

    # Common outputs and inputs
    _COMMON_OUTPUTS = []

    # Configuration patterns and their associated inputs/outputs
    _CONFIGS = {}

    # List of parameters that affect configuration
    _PARAMS = []

    def __init__(
        self,
        id: Optional[str] = None,
        node_name: Optional[str] = None,
        execution_mode: Optional[str] = None,
        email_body: str = "",
        email_subject: str = "",
        recipient_email: str = "",
        send_as_html: bool = False,
        **kwargs
    ):
        # Initialize with params
        params = {}

        super().__init__(
            node_type="email_notification",
            params=params,
            id=id,
            node_name=node_name,
            execution_mode=execution_mode,
        )

        # Set input values
        if recipient_email is not None:
            self.inputs["recipient_email"] = recipient_email
        if email_subject is not None:
            self.inputs["email_subject"] = email_subject
        if email_body is not None:
            self.inputs["email_body"] = email_body
        if send_as_html is not None:
            self.inputs["send_as_html"] = send_as_html

        # Update any additional inputs
        if kwargs:
            self.update_inputs(**kwargs)

    @classmethod
    def from_dict(cls, data: dict) -> "EmailNotificationNode":
        """Create a node instance from a dictionary."""
        inputs = data.get("inputs", {})
        id = data.get("id", None)
        name = data.get("name", None)
        execution_mode = data.get("execution_mode", None)
        return cls(**inputs, id=id, node_name=name, execution_mode=execution_mode)


@Node.register_node_type("sms_notification")
class SmsNotificationNode(Node):
    """
    Send text message notifications.

    ## Inputs
    ### Common Inputs
        message: SMS message content
        phone_number: US phone number in country code (+1)

    ## Outputs
        None
    """

    # Common inputs and outputs
    _COMMON_INPUTS = [
        {
            "field": "message",
            "helper_text": "SMS message content",
            "value": "",
            "type": "string",
        },
        {
            "field": "phone_number",
            "helper_text": "US phone number in country code (+1)",
            "value": "",
            "type": "string",
        },
    ]

    # Common outputs and inputs
    _COMMON_OUTPUTS = []

    # Configuration patterns and their associated inputs/outputs
    _CONFIGS = {}

    # List of parameters that affect configuration
    _PARAMS = []

    def __init__(
        self,
        id: Optional[str] = None,
        node_name: Optional[str] = None,
        execution_mode: Optional[str] = None,
        message: str = "",
        phone_number: str = "",
        **kwargs
    ):
        # Initialize with params
        params = {}

        super().__init__(
            node_type="sms_notification",
            params=params,
            id=id,
            node_name=node_name,
            execution_mode=execution_mode,
        )

        # Set input values
        if phone_number is not None:
            self.inputs["phone_number"] = phone_number
        if message is not None:
            self.inputs["message"] = message

        # Update any additional inputs
        if kwargs:
            self.update_inputs(**kwargs)

    @classmethod
    def from_dict(cls, data: dict) -> "SmsNotificationNode":
        """Create a node instance from a dictionary."""
        inputs = data.get("inputs", {})
        id = data.get("id", None)
        name = data.get("name", None)
        execution_mode = data.get("execution_mode", None)
        return cls(**inputs, id=id, node_name=name, execution_mode=execution_mode)


@Node.register_node_type("ai_filter_list")
class AiFilterListNode(Node):
    """
    Filter items in a list given a specific AI condition. Example, Filter (Red, White, Boat) by whether it is a color: (Red, White)

    ## Inputs
    ### Common Inputs
        ai_condition: Write in natural language the condition to filter each item in the list
        filter_by: The items to filter the list by
        list_to_filter: The list to filter
        model: The specific model for filtering
        output_blank_value: If true, output a blank value for values that do not meet the filter condition. If false, nothing will be outputted
        provider: The model provider

    ## Outputs
    ### Common Outputs
        output: The filtered list
    """

    # Common inputs and outputs
    _COMMON_INPUTS = [
        {
            "field": "ai_condition",
            "helper_text": "Write in natural language the condition to filter each item in the list",
            "value": "",
            "type": "string",
        },
        {
            "field": "filter_by",
            "helper_text": "The items to filter the list by",
            "value": "",
            "type": "vec<string>",
        },
        {
            "field": "list_to_filter",
            "helper_text": "The list to filter",
            "value": "",
            "type": "vec<string>",
        },
        {
            "field": "model",
            "helper_text": "The specific model for filtering",
            "value": "gpt-4o",
            "type": "enum<string>",
        },
        {
            "field": "output_blank_value",
            "helper_text": "If true, output a blank value for values that do not meet the filter condition. If false, nothing will be outputted",
            "value": False,
            "type": "bool",
        },
        {
            "field": "provider",
            "helper_text": "The model provider",
            "value": "openai",
            "type": "enum<string>",
        },
    ]

    # Common outputs and inputs
    _COMMON_OUTPUTS = [{"field": "output", "helper_text": "The filtered list"}]

    # Configuration patterns and their associated inputs/outputs
    _CONFIGS = {}

    # List of parameters that affect configuration
    _PARAMS = []

    def __init__(
        self,
        id: Optional[str] = None,
        node_name: Optional[str] = None,
        execution_mode: Optional[str] = None,
        ai_condition: str = "",
        filter_by: List[str] = [],
        list_to_filter: List[str] = [],
        model: str = "gpt-4o",
        output_blank_value: bool = False,
        provider: str = "openai",
        **kwargs
    ):
        # Initialize with params
        params = {}

        super().__init__(
            node_type="ai_filter_list",
            params=params,
            id=id,
            node_name=node_name,
            execution_mode=execution_mode,
        )

        # Set input values
        if list_to_filter is not None:
            self.inputs["list_to_filter"] = list_to_filter
        if filter_by is not None:
            self.inputs["filter_by"] = filter_by
        if ai_condition is not None:
            self.inputs["ai_condition"] = ai_condition
        if output_blank_value is not None:
            self.inputs["output_blank_value"] = output_blank_value
        if provider is not None:
            self.inputs["provider"] = provider
        if model is not None:
            self.inputs["model"] = model

        # Update any additional inputs
        if kwargs:
            self.update_inputs(**kwargs)

    @property
    def output(self) -> List[str]:
        """
        The filtered list


        Raises:
            AttributeError: If this output is not available for the current parameter values
        """
        return self.__getattr__("output")

    @classmethod
    def from_dict(cls, data: dict) -> "AiFilterListNode":
        """Create a node instance from a dictionary."""
        inputs = data.get("inputs", {})
        id = data.get("id", None)
        name = data.get("name", None)
        execution_mode = data.get("execution_mode", None)
        return cls(**inputs, id=id, node_name=name, execution_mode=execution_mode)


@Node.register_node_type("filter_list")
class FilterListNode(Node):
    """
    Filter a list given a specific condition. Example, Filter (Red, White, Blue) by (100, 95, 80)>90 is (Red, White)

    ## Inputs
    ### Common Inputs
        condition_type: The type of condition to apply
        condition_value: The value to compare the list items against
        output_blank_value: If true, output a blank value for values that do not meet the filter condition. If false, nothing will be outputted
        type: The type of the list
    ### <T>
        filter_by: The items to filter the list by
        list_to_filter: The list to filter

    ## Outputs
    ### <T>
        output: The filtered list
    """

    # Common inputs and outputs
    _COMMON_INPUTS = [
        {
            "field": "condition_type",
            "helper_text": "The type of condition to apply",
            "value": "IsEmpty",
            "type": "enum<string>",
        },
        {
            "field": "condition_value",
            "helper_text": "The value to compare the list items against",
            "value": "",
            "type": "string",
        },
        {
            "field": "output_blank_value",
            "helper_text": "If true, output a blank value for values that do not meet the filter condition. If false, nothing will be outputted",
            "value": False,
            "type": "bool",
        },
        {
            "field": "type",
            "helper_text": "The type of the list",
            "value": "string",
            "type": "enum<string>",
        },
    ]

    # Common outputs and inputs
    _COMMON_OUTPUTS = []

    # Configuration patterns and their associated inputs/outputs
    _CONFIGS = {
        "<T>": {
            "inputs": [
                {
                    "field": "list_to_filter",
                    "type": "vec<<T>>",
                    "value": "",
                    "helper_text": "The list to filter",
                },
                {
                    "field": "filter_by",
                    "type": "vec<<T>>",
                    "value": "",
                    "helper_text": "The items to filter the list by",
                },
            ],
            "outputs": [
                {
                    "field": "output",
                    "type": "vec<<T>>",
                    "helper_text": "The filtered list",
                }
            ],
        }
    }

    # List of parameters that affect configuration
    _PARAMS = ["type"]

    def __init__(
        self,
        id: Optional[str] = None,
        node_name: Optional[str] = None,
        execution_mode: Optional[str] = None,
        type: str = "string",
        condition_type: str = "IsEmpty",
        condition_value: str = "",
        filter_by: List[Any] = [],
        list_to_filter: List[Any] = [],
        output_blank_value: bool = False,
        **kwargs
    ):
        # Initialize with params
        params = {}
        params["type"] = type

        super().__init__(
            node_type="filter_list",
            params=params,
            id=id,
            node_name=node_name,
            execution_mode=execution_mode,
        )

        # Set input values
        if type is not None:
            self.inputs["type"] = type
        if condition_type is not None:
            self.inputs["condition_type"] = condition_type
        if condition_value is not None:
            self.inputs["condition_value"] = condition_value
        if output_blank_value is not None:
            self.inputs["output_blank_value"] = output_blank_value
        if list_to_filter is not None:
            self.inputs["list_to_filter"] = list_to_filter
        if filter_by is not None:
            self.inputs["filter_by"] = filter_by

        # Update any additional inputs
        if kwargs:
            self.update_inputs(**kwargs)

    @property
    def output(self) -> List[Any]:
        """
        The filtered list

        Available: <T>


        Raises:
            AttributeError: If this output is not available for the current parameter values
        """
        return self.__getattr__("output")

    @classmethod
    def from_dict(cls, data: dict) -> "FilterListNode":
        """Create a node instance from a dictionary."""
        inputs = data.get("inputs", {})
        id = data.get("id", None)
        name = data.get("name", None)
        execution_mode = data.get("execution_mode", None)
        return cls(**inputs, id=id, node_name=name, execution_mode=execution_mode)


@Node.register_node_type("sales_data_enrichment")
class SalesDataEnrichmentNode(Node):
    """


    ## Inputs
    ### Common Inputs
        sub_type: The sub_type input

    ## Outputs
        None
    """

    # Common inputs and outputs
    _COMMON_INPUTS = [
        {
            "field": "sub_type",
            "helper_text": "The sub_type input",
            "value": "",
            "type": "string",
        }
    ]

    # Common outputs and inputs
    _COMMON_OUTPUTS = []

    # Configuration patterns and their associated inputs/outputs
    _CONFIGS = {}

    # List of parameters that affect configuration
    _PARAMS = []

    def __init__(
        self,
        id: Optional[str] = None,
        node_name: Optional[str] = None,
        execution_mode: Optional[str] = None,
        sub_type: str = "",
        **kwargs
    ):
        # Initialize with params
        params = {}

        super().__init__(
            node_type="sales_data_enrichment",
            params=params,
            id=id,
            node_name=node_name,
            execution_mode=execution_mode,
        )

        # Set input values
        if sub_type is not None:
            self.inputs["sub_type"] = sub_type

        # Update any additional inputs
        if kwargs:
            self.update_inputs(**kwargs)

    @classmethod
    def from_dict(cls, data: dict) -> "SalesDataEnrichmentNode":
        """Create a node instance from a dictionary."""
        inputs = data.get("inputs", {})
        id = data.get("id", None)
        name = data.get("name", None)
        execution_mode = data.get("execution_mode", None)
        return cls(**inputs, id=id, node_name=name, execution_mode=execution_mode)


@Node.register_node_type("email_validator")
class EmailValidatorNode(Node):
    """
    Validate an email address

    ## Inputs
    ### Common Inputs
        email_to_validate: The email you want to validate
        model: The validation model to use
    ### custom-validator
        api_key: The API key to use
        provider: The validation provider to use

    ## Outputs
    ### Common Outputs
        status: Whether the email is valid
    """

    # Common inputs and outputs
    _COMMON_INPUTS = [
        {
            "field": "email_to_validate",
            "helper_text": "The email you want to validate",
            "value": "",
            "type": "string",
        },
        {
            "field": "model",
            "helper_text": "The validation model to use",
            "value": "regex",
            "type": "enum<string>",
        },
    ]

    # Common outputs and inputs
    _COMMON_OUTPUTS = [{"field": "status", "helper_text": "Whether the email is valid"}]

    # Configuration patterns and their associated inputs/outputs
    _CONFIGS = {
        "custom-validator": {
            "inputs": [
                {
                    "field": "provider",
                    "type": "enum<string>",
                    "value": "hunter",
                    "helper_text": "The validation provider to use",
                },
                {
                    "field": "api_key",
                    "type": "string",
                    "value": "",
                    "helper_text": "The API key to use",
                },
            ],
            "outputs": [],
        }
    }

    # List of parameters that affect configuration
    _PARAMS = ["model"]

    def __init__(
        self,
        id: Optional[str] = None,
        node_name: Optional[str] = None,
        execution_mode: Optional[str] = None,
        model: str = "regex",
        api_key: str = "",
        email_to_validate: str = "",
        provider: str = "hunter",
        **kwargs
    ):
        # Initialize with params
        params = {}
        params["model"] = model

        super().__init__(
            node_type="email_validator",
            params=params,
            id=id,
            node_name=node_name,
            execution_mode=execution_mode,
        )

        # Set input values
        if email_to_validate is not None:
            self.inputs["email_to_validate"] = email_to_validate
        if model is not None:
            self.inputs["model"] = model
        if provider is not None:
            self.inputs["provider"] = provider
        if api_key is not None:
            self.inputs["api_key"] = api_key

        # Update any additional inputs
        if kwargs:
            self.update_inputs(**kwargs)

    @property
    def status(self) -> bool:
        """
        Whether the email is valid


        Raises:
            AttributeError: If this output is not available for the current parameter values
        """
        return self.__getattr__("status")

    @classmethod
    def from_dict(cls, data: dict) -> "EmailValidatorNode":
        """Create a node instance from a dictionary."""
        inputs = data.get("inputs", {})
        id = data.get("id", None)
        name = data.get("name", None)
        execution_mode = data.get("execution_mode", None)
        return cls(**inputs, id=id, node_name=name, execution_mode=execution_mode)


@Node.register_node_type("combine_text")
class CombineTextNode(Node):
    """
    Combine text inputs into a singular output.

    ## Inputs
    ### Common Inputs
        text: The text to combine

    ## Outputs
    ### Common Outputs
        processed_text: The combined text
    """

    # Common inputs and outputs
    _COMMON_INPUTS = [
        {
            "field": "text",
            "helper_text": "The text to combine",
            "value": ["", ""],
            "type": "vec<string>",
        }
    ]

    # Common outputs and inputs
    _COMMON_OUTPUTS = [{"field": "processed_text", "helper_text": "The combined text"}]

    # Configuration patterns and their associated inputs/outputs
    _CONFIGS = {}

    # List of parameters that affect configuration
    _PARAMS = []

    def __init__(
        self,
        id: Optional[str] = None,
        node_name: Optional[str] = None,
        execution_mode: Optional[str] = None,
        text: List[str] = ["", ""],
        **kwargs
    ):
        # Initialize with params
        params = {}

        super().__init__(
            node_type="combine_text",
            params=params,
            id=id,
            node_name=node_name,
            execution_mode=execution_mode,
        )

        # Set input values
        if text is not None:
            self.inputs["text"] = text

        # Update any additional inputs
        if kwargs:
            self.update_inputs(**kwargs)

    @property
    def processed_text(self) -> str:
        """
        The combined text


        Raises:
            AttributeError: If this output is not available for the current parameter values
        """
        return self.__getattr__("processed_text")

    @classmethod
    def from_dict(cls, data: dict) -> "CombineTextNode":
        """Create a node instance from a dictionary."""
        inputs = data.get("inputs", {})
        id = data.get("id", None)
        name = data.get("name", None)
        execution_mode = data.get("execution_mode", None)
        return cls(**inputs, id=id, node_name=name, execution_mode=execution_mode)


@Node.register_node_type("find_and_replace")
class FindAndReplaceNode(Node):
    """
    Find and replace words in a given text.

    ## Inputs
    ### Common Inputs
        replacements: The replacements input
        text_to_manipulate: The text to find and replace words in

    ## Outputs
    ### Common Outputs
        processed_text: The final text with found words replaced
    """

    # Common inputs and outputs
    _COMMON_INPUTS = [
        {
            "field": "replacements",
            "helper_text": "The replacements input",
            "value": [],
            "type": "vec<Dict[str, Any]>",
        },
        {
            "field": "text_to_manipulate",
            "helper_text": "The text to find and replace words in",
            "value": "",
            "type": "string",
        },
    ]

    # Common outputs and inputs
    _COMMON_OUTPUTS = [
        {
            "field": "processed_text",
            "helper_text": "The final text with found words replaced",
        }
    ]

    # Configuration patterns and their associated inputs/outputs
    _CONFIGS = {}

    # List of parameters that affect configuration
    _PARAMS = []

    def __init__(
        self,
        id: Optional[str] = None,
        node_name: Optional[str] = None,
        execution_mode: Optional[str] = None,
        replacements: List[Any] = [],
        text_to_manipulate: str = "",
        **kwargs
    ):
        # Initialize with params
        params = {}

        super().__init__(
            node_type="find_and_replace",
            params=params,
            id=id,
            node_name=node_name,
            execution_mode=execution_mode,
        )

        # Set input values
        if text_to_manipulate is not None:
            self.inputs["text_to_manipulate"] = text_to_manipulate
        if replacements is not None:
            self.inputs["replacements"] = replacements

        # Update any additional inputs
        if kwargs:
            self.update_inputs(**kwargs)

    @property
    def processed_text(self) -> str:
        """
        The final text with found words replaced


        Raises:
            AttributeError: If this output is not available for the current parameter values
        """
        return self.__getattr__("processed_text")

    @classmethod
    def from_dict(cls, data: dict) -> "FindAndReplaceNode":
        """Create a node instance from a dictionary."""
        inputs = data.get("inputs", {})
        id = data.get("id", None)
        name = data.get("name", None)
        execution_mode = data.get("execution_mode", None)
        return cls(**inputs, id=id, node_name=name, execution_mode=execution_mode)


@Node.register_node_type("ai_fill_pdf")
class AiFillPdfNode(Node):
    """
    Fill out a PDF with form fields using AI. The AI will understand and fill each field using provided context. To convert your PDF to have fillable input fields, use: https://www.sejda.com/pdf-forms

    ## Inputs
    ### Common Inputs
        context: Context used by LLM to fill PDF fields
        file: The PDF with form fields to be filled
        model: The specific model for filling the PDF
        provider: The model provider
        select_pages: Whether to select specific pages to fill
    ### When select_pages = True
        selected_pages: PDF page range

    ## Outputs
    ### Common Outputs
        filled_pdf: Filled PDF
    """

    # Common inputs and outputs
    _COMMON_INPUTS = [
        {
            "field": "context",
            "helper_text": "Context used by LLM to fill PDF fields",
            "value": "",
            "type": "string",
        },
        {
            "field": "file",
            "helper_text": "The PDF with form fields to be filled",
            "value": None,
            "type": "file",
        },
        {
            "field": "model",
            "helper_text": "The specific model for filling the PDF",
            "value": "gpt-4o",
            "type": "enum<string>",
        },
        {
            "field": "provider",
            "helper_text": "The model provider",
            "value": "openai",
            "type": "enum<string>",
        },
        {
            "field": "select_pages",
            "helper_text": "Whether to select specific pages to fill",
            "value": False,
            "type": "bool",
        },
    ]

    # Common outputs and inputs
    _COMMON_OUTPUTS = [{"field": "filled_pdf", "helper_text": "Filled PDF"}]

    # Configuration patterns and their associated inputs/outputs
    _CONFIGS = {
        "true": {
            "inputs": [
                {
                    "field": "selected_pages",
                    "type": "string",
                    "value": "",
                    "helper_text": "PDF page range",
                }
            ],
            "outputs": [],
        },
        "false": {"inputs": [], "outputs": []},
    }

    # List of parameters that affect configuration
    _PARAMS = ["select_pages"]

    def __init__(
        self,
        id: Optional[str] = None,
        node_name: Optional[str] = None,
        execution_mode: Optional[str] = None,
        select_pages: bool = False,
        context: str = "",
        file: Optional[str] = None,
        model: str = "gpt-4o",
        provider: str = "openai",
        selected_pages: str = "",
        **kwargs
    ):
        # Initialize with params
        params = {}
        params["select_pages"] = select_pages

        super().__init__(
            node_type="ai_fill_pdf",
            params=params,
            id=id,
            node_name=node_name,
            execution_mode=execution_mode,
        )

        # Set input values
        if file is not None:
            self.inputs["file"] = file
        if provider is not None:
            self.inputs["provider"] = provider
        if model is not None:
            self.inputs["model"] = model
        if select_pages is not None:
            self.inputs["select_pages"] = select_pages
        if context is not None:
            self.inputs["context"] = context
        if selected_pages is not None:
            self.inputs["selected_pages"] = selected_pages

        # Update any additional inputs
        if kwargs:
            self.update_inputs(**kwargs)

    @property
    def filled_pdf(self) -> str:
        """
        Filled PDF


        Raises:
            AttributeError: If this output is not available for the current parameter values
        """
        return self.__getattr__("filled_pdf")

    @classmethod
    def from_dict(cls, data: dict) -> "AiFillPdfNode":
        """Create a node instance from a dictionary."""
        inputs = data.get("inputs", {})
        id = data.get("id", None)
        name = data.get("name", None)
        execution_mode = data.get("execution_mode", None)
        return cls(**inputs, id=id, node_name=name, execution_mode=execution_mode)


@Node.register_node_type("extract_to_table")
class ExtractToTableNode(Node):
    """
    Extract data to a CSV using AI

    ## Inputs
    ### Common Inputs
        add_columns_manually: Add data points for some columns manually instead of having them extracted by the AI model.
        additional_context: Provide any additional context that may help the AI model extract the data.
        extract_multiple_rows: Choose the mode of extraction. If checked, it will extract multiple rows of data. If unchecked, it will extract a single row.
        file: Your file should contain headers in the first row.
        manual_columns: Pass in data to column names manually.
        model: The specific model for extracting the table
        provider: The model provider
        text_for_extraction: Text to extract table from

    ## Outputs
    ### Common Outputs
        table: The table extracted from the text
    """

    # Common inputs and outputs
    _COMMON_INPUTS = [
        {
            "field": "add_columns_manually",
            "helper_text": "Add data points for some columns manually instead of having them extracted by the AI model.",
            "value": False,
            "type": "bool",
        },
        {
            "field": "additional_context",
            "helper_text": "Provide any additional context that may help the AI model extract the data.",
            "value": "",
            "type": "string",
        },
        {
            "field": "extract_multiple_rows",
            "helper_text": "Choose the mode of extraction. If checked, it will extract multiple rows of data. If unchecked, it will extract a single row.",
            "value": True,
            "type": "bool",
        },
        {
            "field": "file",
            "helper_text": "Your file should contain headers in the first row.",
            "value": "",
            "type": "file",
        },
        {
            "field": "manual_columns",
            "helper_text": "Pass in data to column names manually.",
            "value": [],
            "type": "vec<Dict[str, Any]>",
        },
        {
            "field": "model",
            "helper_text": "The specific model for extracting the table",
            "value": "gpt-4o",
            "type": "enum<string>",
        },
        {
            "field": "provider",
            "helper_text": "The model provider",
            "value": "openai",
            "type": "enum<string>",
        },
        {
            "field": "text_for_extraction",
            "helper_text": "Text to extract table from",
            "value": "",
            "type": "string",
        },
    ]

    # Common outputs and inputs
    _COMMON_OUTPUTS = [
        {"field": "table", "helper_text": "The table extracted from the text"}
    ]

    # Configuration patterns and their associated inputs/outputs
    _CONFIGS = {}

    # List of parameters that affect configuration
    _PARAMS = []

    def __init__(
        self,
        id: Optional[str] = None,
        node_name: Optional[str] = None,
        execution_mode: Optional[str] = None,
        add_columns_manually: bool = False,
        additional_context: str = "",
        extract_multiple_rows: bool = True,
        file: str = "",
        manual_columns: List[Any] = [],
        model: str = "gpt-4o",
        provider: str = "openai",
        text_for_extraction: str = "",
        **kwargs
    ):
        # Initialize with params
        params = {}

        super().__init__(
            node_type="extract_to_table",
            params=params,
            id=id,
            node_name=node_name,
            execution_mode=execution_mode,
        )

        # Set input values
        if text_for_extraction is not None:
            self.inputs["text_for_extraction"] = text_for_extraction
        if extract_multiple_rows is not None:
            self.inputs["extract_multiple_rows"] = extract_multiple_rows
        if add_columns_manually is not None:
            self.inputs["add_columns_manually"] = add_columns_manually
        if manual_columns is not None:
            self.inputs["manual_columns"] = manual_columns
        if provider is not None:
            self.inputs["provider"] = provider
        if model is not None:
            self.inputs["model"] = model
        if additional_context is not None:
            self.inputs["additional_context"] = additional_context
        if file is not None:
            self.inputs["file"] = file

        # Update any additional inputs
        if kwargs:
            self.update_inputs(**kwargs)

    @property
    def table(self) -> str:
        """
        The table extracted from the text


        Raises:
            AttributeError: If this output is not available for the current parameter values
        """
        return self.__getattr__("table")

    @classmethod
    def from_dict(cls, data: dict) -> "ExtractToTableNode":
        """Create a node instance from a dictionary."""
        inputs = data.get("inputs", {})
        id = data.get("id", None)
        name = data.get("name", None)
        execution_mode = data.get("execution_mode", None)
        return cls(**inputs, id=id, node_name=name, execution_mode=execution_mode)


@Node.register_node_type("sort_csv")
class SortCsvNode(Node):
    """
    Sort a CSV based on a column

    ## Inputs
    ### Common Inputs
        file: The CSV file to sort.
        has_headers: Whether the CSV has headers.
        is_file_variable: Whether the file is a variable.
        reverse_sort: Whether to reverse the sort.
    ### When is_file_variable = True
        column_index: The index of the column to sort by.
    ### When is_file_variable = False and has_headers = False
        column_index: The index of the column to sort by.
    ### When is_file_variable = False and has_headers = True
        column_to_sort_by: The column to sort by.

    ## Outputs
    ### Common Outputs
        output: The output output
    """

    # Common inputs and outputs
    _COMMON_INPUTS = [
        {
            "field": "file",
            "helper_text": "The CSV file to sort.",
            "value": None,
            "type": "file",
        },
        {
            "field": "has_headers",
            "helper_text": "Whether the CSV has headers.",
            "value": True,
            "type": "bool",
        },
        {
            "field": "is_file_variable",
            "helper_text": "Whether the file is a variable.",
            "value": False,
            "type": "bool",
        },
        {
            "field": "reverse_sort",
            "helper_text": "Whether to reverse the sort.",
            "value": False,
            "type": "bool",
        },
    ]

    # Common outputs and inputs
    _COMMON_OUTPUTS = [{"field": "output", "helper_text": "The output output"}]

    # Configuration patterns and their associated inputs/outputs
    _CONFIGS = {
        "true**(*)": {
            "inputs": [
                {
                    "field": "column_index",
                    "type": "int32",
                    "value": 0,
                    "helper_text": "The index of the column to sort by.",
                }
            ],
            "outputs": [],
        },
        "false**true": {
            "inputs": [
                {
                    "field": "column_to_sort_by",
                    "type": "enum<string>",
                    "value": "",
                    "helper_text": "The column to sort by.",
                }
            ],
            "outputs": [],
        },
        "false**false": {
            "inputs": [
                {
                    "field": "column_index",
                    "type": "int32",
                    "value": 0,
                    "helper_text": "The index of the column to sort by.",
                }
            ],
            "outputs": [],
        },
    }

    # List of parameters that affect configuration
    _PARAMS = ["is_file_variable", "has_headers"]

    def __init__(
        self,
        id: Optional[str] = None,
        node_name: Optional[str] = None,
        execution_mode: Optional[str] = None,
        is_file_variable: bool = False,
        has_headers: bool = True,
        column_index: int = 0,
        column_to_sort_by: str = "",
        file: Optional[str] = None,
        reverse_sort: bool = False,
        **kwargs
    ):
        # Initialize with params
        params = {}
        params["is_file_variable"] = is_file_variable
        params["has_headers"] = has_headers

        super().__init__(
            node_type="sort_csv",
            params=params,
            id=id,
            node_name=node_name,
            execution_mode=execution_mode,
        )

        # Set input values
        if is_file_variable is not None:
            self.inputs["is_file_variable"] = is_file_variable
        if file is not None:
            self.inputs["file"] = file
        if has_headers is not None:
            self.inputs["has_headers"] = has_headers
        if reverse_sort is not None:
            self.inputs["reverse_sort"] = reverse_sort
        if column_index is not None:
            self.inputs["column_index"] = column_index
        if column_to_sort_by is not None:
            self.inputs["column_to_sort_by"] = column_to_sort_by

        # Update any additional inputs
        if kwargs:
            self.update_inputs(**kwargs)

    @property
    def output(self) -> str:
        """
        The output output


        Raises:
            AttributeError: If this output is not available for the current parameter values
        """
        return self.__getattr__("output")

    @classmethod
    def from_dict(cls, data: dict) -> "SortCsvNode":
        """Create a node instance from a dictionary."""
        inputs = data.get("inputs", {})
        id = data.get("id", None)
        name = data.get("name", None)
        execution_mode = data.get("execution_mode", None)
        return cls(**inputs, id=id, node_name=name, execution_mode=execution_mode)


@Node.register_node_type("trigger")
class TriggerNode(Node):
    """
    Trigger

    ## Inputs
    ### Common Inputs
        event: The event input
        trigger_enabled: The trigger_enabled input
        trigger_type: The trigger_type input
    ### When trigger_type = 'Cron' and event = 'monthly'
        day_of_month: The day_of_month input
        time_of_day: The time_of_day input
    ### When trigger_type = 'Cron' and event = 'weekly'
        day_of_week: The day_of_week input
        time_of_day: The time_of_day input
    ### When trigger_type = 'Outlook'
        integration: The integration input
        integration_id: The integration_id input
        item_id: The item_id input
    ### When trigger_type = 'Gmail'
        integration: The integration input
        integration_id: The integration_id input
        item_id: The item_id input
    ### When trigger_type = 'Cron'
        integration: The integration input
        integration_id: The integration_id input
        item_id: The item_id input
        timezone: The timezone input
    ### When trigger_type = 'Cron' and event = 'daily'
        time_of_day: The time_of_day input
        trigger_on_weekends: The trigger_on_weekends input

    ## Outputs
    ### When trigger_type = 'Outlook' and event = 'new_email'
        attachments: The attachments output
        contents_of_email: The contents_of_email output
        email_id: The email_id output
        received_time: The received_time output
        recipient_email: The recipient_email output
        sender_email: The sender_email output
        subject: The subject output
    ### When trigger_type = 'Gmail' and event = 'new_email'
        attachments: The attachments output
        contents_of_email: The contents_of_email output
        email_id: The email_id output
        received_time: The received_time output
        recipient_email: The recipient_email output
        sender_email: The sender_email output
        subject: The subject output
    ### When trigger_type = 'Cron'
        timestamp: The timestamp output
    """

    # Common inputs and outputs
    _COMMON_INPUTS = [
        {
            "field": "event",
            "helper_text": "The event input",
            "value": "",
            "type": "enum<string>",
        },
        {
            "field": "trigger_enabled",
            "helper_text": "The trigger_enabled input",
            "value": True,
            "type": "bool",
        },
        {
            "field": "trigger_type",
            "helper_text": "The trigger_type input",
            "value": "",
            "type": "string",
        },
    ]

    # Common outputs and inputs
    _COMMON_OUTPUTS = []

    # Configuration patterns and their associated inputs/outputs
    _CONFIGS = {
        "Outlook**(*)": {
            "inputs": [
                {"field": "integration_id", "type": "string", "value": ""},
                {"field": "integration", "type": "any", "value": ""},
                {"field": "item_id", "type": "string", "value": ""},
            ],
            "outputs": [],
        },
        "Outlook**new_email": {
            "inputs": [],
            "outputs": [
                {"field": "email_id", "type": "string"},
                {"field": "subject", "type": "string"},
                {"field": "sender_email", "type": "string"},
                {"field": "recipient_email", "type": "string"},
                {"field": "received_time", "type": "string"},
                {"field": "contents_of_email", "type": "string"},
                {"field": "attachments", "type": "vec<file>"},
            ],
        },
        "Gmail**(*)": {
            "inputs": [
                {"field": "integration_id", "type": "string", "value": ""},
                {"field": "integration", "type": "any", "value": ""},
                {"field": "item_id", "type": "string", "value": ""},
            ],
            "outputs": [],
        },
        "Gmail**new_email": {
            "inputs": [],
            "outputs": [
                {"field": "email_id", "type": "string"},
                {"field": "subject", "type": "string"},
                {"field": "sender_email", "type": "string"},
                {"field": "recipient_email", "type": "string"},
                {"field": "received_time", "type": "string"},
                {"field": "contents_of_email", "type": "string"},
                {"field": "attachments", "type": "vec<file>"},
            ],
        },
        "Cron**(*)": {
            "inputs": [
                {"field": "timezone", "type": "enum<string>", "value": "UTC"},
                {
                    "field": "integration_id",
                    "type": "string",
                    "value": "6809a715ad4615eeb652a551",
                },
                {"field": "integration", "type": "any", "value": ""},
                {"field": "item_id", "type": "string", "value": "0 0 * * *"},
            ],
            "outputs": [{"field": "timestamp", "type": "string"}],
        },
        "Cron**daily": {
            "inputs": [
                {"field": "time_of_day", "type": "string", "value": "00:00"},
                {"field": "trigger_on_weekends", "type": "bool", "value": False},
            ],
            "outputs": [],
        },
        "Cron**weekly": {
            "inputs": [
                {"field": "day_of_week", "type": "enum<string>", "value": "Monday"},
                {"field": "time_of_day", "type": "string", "value": "00:00"},
            ],
            "outputs": [],
        },
        "Cron**monthly": {
            "inputs": [
                {"field": "day_of_month", "type": "int32", "value": 1},
                {"field": "time_of_day", "type": "string", "value": "00:00"},
            ],
            "outputs": [],
        },
        "Cron**custom": {"inputs": [], "outputs": []},
    }

    # List of parameters that affect configuration
    _PARAMS = ["trigger_type", "event"]

    def __init__(
        self,
        id: Optional[str] = None,
        node_name: Optional[str] = None,
        execution_mode: Optional[str] = None,
        trigger_type: str = "",
        event: str = "",
        day_of_month: int = 1,
        day_of_week: str = "Monday",
        integration: Any = None,
        integration_id: str = "",
        item_id: str = "",
        time_of_day: str = "00:00",
        timezone: str = "UTC",
        trigger_enabled: bool = True,
        trigger_on_weekends: bool = False,
        **kwargs
    ):
        # Initialize with params
        params = {}
        params["trigger_type"] = trigger_type
        params["event"] = event

        super().__init__(
            node_type="trigger",
            params=params,
            id=id,
            node_name=node_name,
            execution_mode=execution_mode,
        )

        # Set input values
        if trigger_type is not None:
            self.inputs["trigger_type"] = trigger_type
        if event is not None:
            self.inputs["event"] = event
        if trigger_enabled is not None:
            self.inputs["trigger_enabled"] = trigger_enabled
        if integration_id is not None:
            self.inputs["integration_id"] = integration_id
        if integration is not None:
            self.inputs["integration"] = integration
        if item_id is not None:
            self.inputs["item_id"] = item_id
        if timezone is not None:
            self.inputs["timezone"] = timezone
        if time_of_day is not None:
            self.inputs["time_of_day"] = time_of_day
        if trigger_on_weekends is not None:
            self.inputs["trigger_on_weekends"] = trigger_on_weekends
        if day_of_week is not None:
            self.inputs["day_of_week"] = day_of_week
        if day_of_month is not None:
            self.inputs["day_of_month"] = day_of_month

        # Update any additional inputs
        if kwargs:
            self.update_inputs(**kwargs)

    @property
    def attachments(self) -> List[str]:
        """
        The attachments output

        Available: When trigger_type = 'Outlook' and event = 'new_email', When trigger_type = 'Gmail' and event = 'new_email'


        Raises:
            AttributeError: If this output is not available for the current parameter values
        """
        return self.__getattr__("attachments")

    @property
    def contents_of_email(self) -> str:
        """
        The contents_of_email output

        Available: When trigger_type = 'Outlook' and event = 'new_email', When trigger_type = 'Gmail' and event = 'new_email'


        Raises:
            AttributeError: If this output is not available for the current parameter values
        """
        return self.__getattr__("contents_of_email")

    @property
    def email_id(self) -> str:
        """
        The email_id output

        Available: When trigger_type = 'Outlook' and event = 'new_email', When trigger_type = 'Gmail' and event = 'new_email'


        Raises:
            AttributeError: If this output is not available for the current parameter values
        """
        return self.__getattr__("email_id")

    @property
    def received_time(self) -> str:
        """
        The received_time output

        Available: When trigger_type = 'Outlook' and event = 'new_email', When trigger_type = 'Gmail' and event = 'new_email'


        Raises:
            AttributeError: If this output is not available for the current parameter values
        """
        return self.__getattr__("received_time")

    @property
    def recipient_email(self) -> str:
        """
        The recipient_email output

        Available: When trigger_type = 'Outlook' and event = 'new_email', When trigger_type = 'Gmail' and event = 'new_email'


        Raises:
            AttributeError: If this output is not available for the current parameter values
        """
        return self.__getattr__("recipient_email")

    @property
    def sender_email(self) -> str:
        """
        The sender_email output

        Available: When trigger_type = 'Outlook' and event = 'new_email', When trigger_type = 'Gmail' and event = 'new_email'


        Raises:
            AttributeError: If this output is not available for the current parameter values
        """
        return self.__getattr__("sender_email")

    @property
    def subject(self) -> str:
        """
        The subject output

        Available: When trigger_type = 'Outlook' and event = 'new_email', When trigger_type = 'Gmail' and event = 'new_email'


        Raises:
            AttributeError: If this output is not available for the current parameter values
        """
        return self.__getattr__("subject")

    @property
    def timestamp(self) -> str:
        """
        The timestamp output

        Available: When trigger_type = 'Cron'


        Raises:
            AttributeError: If this output is not available for the current parameter values
        """
        return self.__getattr__("timestamp")

    @classmethod
    def from_dict(cls, data: dict) -> "TriggerNode":
        """Create a node instance from a dictionary."""
        inputs = data.get("inputs", {})
        id = data.get("id", None)
        name = data.get("name", None)
        execution_mode = data.get("execution_mode", None)
        return cls(**inputs, id=id, node_name=name, execution_mode=execution_mode)


@Node.register_node_type("knowledge_base_actions")
class KnowledgeBaseActionsNode(Node):
    """


    ## Inputs
    ### Common Inputs
        sub_type: The sub_type input

    ## Outputs
        None
    """

    # Common inputs and outputs
    _COMMON_INPUTS = [
        {
            "field": "sub_type",
            "helper_text": "The sub_type input",
            "value": "",
            "type": "string",
        }
    ]

    # Common outputs and inputs
    _COMMON_OUTPUTS = []

    # Configuration patterns and their associated inputs/outputs
    _CONFIGS = {}

    # List of parameters that affect configuration
    _PARAMS = []

    def __init__(
        self,
        id: Optional[str] = None,
        node_name: Optional[str] = None,
        execution_mode: Optional[str] = None,
        sub_type: str = "",
        **kwargs
    ):
        # Initialize with params
        params = {}

        super().__init__(
            node_type="knowledge_base_actions",
            params=params,
            id=id,
            node_name=node_name,
            execution_mode=execution_mode,
        )

        # Set input values
        if sub_type is not None:
            self.inputs["sub_type"] = sub_type

        # Update any additional inputs
        if kwargs:
            self.update_inputs(**kwargs)

    @classmethod
    def from_dict(cls, data: dict) -> "KnowledgeBaseActionsNode":
        """Create a node instance from a dictionary."""
        inputs = data.get("inputs", {})
        id = data.get("id", None)
        name = data.get("name", None)
        execution_mode = data.get("execution_mode", None)
        return cls(**inputs, id=id, node_name=name, execution_mode=execution_mode)


@Node.register_node_type("knowledge_base_sync")
class KnowledgeBaseSyncNode(Node):
    """
    Automatically trigger a sync to the integrations in the selected knowledge base

    ## Inputs
    ### Common Inputs
        knowledge_base: The knowledge base to sync

    ## Outputs
        None
    """

    # Common inputs and outputs
    _COMMON_INPUTS = [
        {
            "field": "knowledge_base",
            "helper_text": "The knowledge base to sync",
            "value": {},
            "type": "knowledge_base",
        }
    ]

    # Common outputs and inputs
    _COMMON_OUTPUTS = []

    # Configuration patterns and their associated inputs/outputs
    _CONFIGS = {}

    # List of parameters that affect configuration
    _PARAMS = []

    def __init__(
        self,
        id: Optional[str] = None,
        node_name: Optional[str] = None,
        execution_mode: Optional[str] = None,
        knowledge_base: Any = {},
        **kwargs
    ):
        # Initialize with params
        params = {}

        super().__init__(
            node_type="knowledge_base_sync",
            params=params,
            id=id,
            node_name=node_name,
            execution_mode=execution_mode,
        )

        # Set input values
        if knowledge_base is not None:
            self.inputs["knowledge_base"] = knowledge_base

        # Update any additional inputs
        if kwargs:
            self.update_inputs(**kwargs)

    @classmethod
    def from_dict(cls, data: dict) -> "KnowledgeBaseSyncNode":
        """Create a node instance from a dictionary."""
        inputs = data.get("inputs", {})
        id = data.get("id", None)
        name = data.get("name", None)
        execution_mode = data.get("execution_mode", None)
        return cls(**inputs, id=id, node_name=name, execution_mode=execution_mode)


@Node.register_node_type("knowledge_base_create")
class KnowledgeBaseCreateNode(Node):
    """
    Dynamically create a Knowledge Base with configured options

    ## Inputs
    ### Common Inputs
        analyze_documents: To analyze document contents and enrich them when parsing
        apify_key: Apify API Key for scraping URLs (optional)
        chunk_overlap: The overlap of the chunks to store in the knowledge base
        chunk_size: The size of the chunks to store in the knowledge base
        collection_name: The name of the collection to store the knowledge base in
        embedding_model: LLM model to use for embedding documents in the KB
        embedding_provider: The embedding provider to use
        file_processing_implementation: The file processing implementation to use
        is_hybrid: Whether to create a hybrid knowledge base
        name: The name of the knowledge base
        precision: The precision to use for the knowledge base
        segmentation_method: The method to break text into units before chunking. 'words': splits by word; 'sentences': splits by sentence boundary; 'paragraphs': splits by blank line/paragraph.
        sharded: Whether to shard the knowledge base
        splitter_method: Strategy for grouping segmented text into final chunks. 'sentence': groups sentences; 'markdown': respects Markdown structure (headers, code); 'dynamic': optimizes breaks for size using chosen segmentation method.
        vector_db_provider: The vector database provider to use

    ## Outputs
    ### Common Outputs
        knowledge_base: The created knowledge base
    """

    # Common inputs and outputs
    _COMMON_INPUTS = [
        {
            "field": "analyze_documents",
            "helper_text": "To analyze document contents and enrich them when parsing",
            "value": False,
            "type": "bool",
        },
        {
            "field": "apify_key",
            "helper_text": "Apify API Key for scraping URLs (optional)",
            "value": "",
            "type": "string",
        },
        {
            "field": "chunk_overlap",
            "helper_text": "The overlap of the chunks to store in the knowledge base",
            "value": 0,
            "type": "int32",
        },
        {
            "field": "chunk_size",
            "helper_text": "The size of the chunks to store in the knowledge base",
            "value": 400,
            "type": "int32",
        },
        {
            "field": "collection_name",
            "helper_text": "The name of the collection to store the knowledge base in",
            "value": "text-embedding-3-small",
            "type": "string",
        },
        {
            "field": "embedding_model",
            "helper_text": "LLM model to use for embedding documents in the KB",
            "value": "text-embedding-3-small",
            "type": "string",
        },
        {
            "field": "embedding_provider",
            "helper_text": "The embedding provider to use",
            "value": "openai",
            "type": "string",
        },
        {
            "field": "file_processing_implementation",
            "helper_text": "The file processing implementation to use",
            "value": "default",
            "type": "string",
        },
        {
            "field": "is_hybrid",
            "helper_text": "Whether to create a hybrid knowledge base",
            "value": False,
            "type": "bool",
        },
        {
            "field": "name",
            "helper_text": "The name of the knowledge base",
            "value": "",
            "type": "string",
        },
        {
            "field": "precision",
            "helper_text": "The precision to use for the knowledge base",
            "value": "Float16",
            "type": "string",
        },
        {
            "field": "segmentation_method",
            "helper_text": "The method to break text into units before chunking. 'words': splits by word; 'sentences': splits by sentence boundary; 'paragraphs': splits by blank line/paragraph.",
            "value": "words",
            "type": "enum<string>",
        },
        {
            "field": "sharded",
            "helper_text": "Whether to shard the knowledge base",
            "value": True,
            "type": "bool",
        },
        {
            "field": "splitter_method",
            "helper_text": "Strategy for grouping segmented text into final chunks. 'sentence': groups sentences; 'markdown': respects Markdown structure (headers, code); 'dynamic': optimizes breaks for size using chosen segmentation method.",
            "value": "markdown",
            "type": "enum<string>",
        },
        {
            "field": "vector_db_provider",
            "helper_text": "The vector database provider to use",
            "value": "qdrant",
            "type": "string",
        },
    ]

    # Common outputs and inputs
    _COMMON_OUTPUTS = [
        {"field": "knowledge_base", "helper_text": "The created knowledge base"}
    ]

    # Configuration patterns and their associated inputs/outputs
    _CONFIGS = {
        "advanced": {
            "inputs": [
                {
                    "field": "segmentation_method",
                    "type": "enum<string>",
                    "value": "words",
                    "helper_text": "The method to break text into units before chunking. 'words': splits by word; 'sentences': splits by sentence boundary; 'paragraphs': splits by blank line/paragraph.",
                }
            ],
            "outputs": [],
        }
    }

    # List of parameters that affect configuration
    _PARAMS = ["splitter_method"]

    def __init__(
        self,
        id: Optional[str] = None,
        node_name: Optional[str] = None,
        execution_mode: Optional[str] = None,
        splitter_method: str = "markdown",
        analyze_documents: bool = False,
        apify_key: str = "",
        chunk_overlap: int = 0,
        chunk_size: int = 400,
        collection_name: str = "text-embedding-3-small",
        embedding_model: str = "text-embedding-3-small",
        embedding_provider: str = "openai",
        file_processing_implementation: str = "default",
        is_hybrid: bool = False,
        name: str = "",
        precision: str = "Float16",
        segmentation_method: str = "words",
        sharded: bool = True,
        vector_db_provider: str = "qdrant",
        **kwargs
    ):
        # Initialize with params
        params = {}
        params["splitter_method"] = splitter_method

        super().__init__(
            node_type="knowledge_base_create",
            params=params,
            id=id,
            node_name=node_name,
            execution_mode=execution_mode,
        )

        # Set input values
        if name is not None:
            self.inputs["name"] = name
        if file_processing_implementation is not None:
            self.inputs["file_processing_implementation"] = (
                file_processing_implementation
            )
        if vector_db_provider is not None:
            self.inputs["vector_db_provider"] = vector_db_provider
        if collection_name is not None:
            self.inputs["collection_name"] = collection_name
        if embedding_model is not None:
            self.inputs["embedding_model"] = embedding_model
        if embedding_provider is not None:
            self.inputs["embedding_provider"] = embedding_provider
        if precision is not None:
            self.inputs["precision"] = precision
        if sharded is not None:
            self.inputs["sharded"] = sharded
        if chunk_size is not None:
            self.inputs["chunk_size"] = chunk_size
        if chunk_overlap is not None:
            self.inputs["chunk_overlap"] = chunk_overlap
        if splitter_method is not None:
            self.inputs["splitter_method"] = splitter_method
        if segmentation_method is not None:
            self.inputs["segmentation_method"] = segmentation_method
        if analyze_documents is not None:
            self.inputs["analyze_documents"] = analyze_documents
        if is_hybrid is not None:
            self.inputs["is_hybrid"] = is_hybrid
        if apify_key is not None:
            self.inputs["apify_key"] = apify_key

        # Update any additional inputs
        if kwargs:
            self.update_inputs(**kwargs)

    @property
    def knowledge_base(self) -> Any:
        """
        The created knowledge base


        Raises:
            AttributeError: If this output is not available for the current parameter values
        """
        return self.__getattr__("knowledge_base")

    @classmethod
    def from_dict(cls, data: dict) -> "KnowledgeBaseCreateNode":
        """Create a node instance from a dictionary."""
        inputs = data.get("inputs", {})
        id = data.get("id", None)
        name = data.get("name", None)
        execution_mode = data.get("execution_mode", None)
        return cls(**inputs, id=id, node_name=name, execution_mode=execution_mode)


@Node.register_node_type("share_object")
class ShareObjectNode(Node):
    """
    Share a VectorShift object with another user

    ## Inputs
    ### Common Inputs
        object_type: The object_type input
        org_name: Enter the name of the organization of the user (leave blank if not part of org)
        user_identifier: Enter the username or email of the user you want to share with
    ### knowledge_base
        object: The object input

    ## Outputs
        None
    """

    # Common inputs and outputs
    _COMMON_INPUTS = [
        {
            "field": "object_type",
            "helper_text": "The object_type input",
            "value": "knowledge_base",
            "type": "enum<string>",
        },
        {
            "field": "org_name",
            "helper_text": "Enter the name of the organization of the user (leave blank if not part of org)",
            "value": "",
            "type": "string",
        },
        {
            "field": "user_identifier",
            "helper_text": "Enter the username or email of the user you want to share with",
            "value": "",
            "type": "string",
        },
    ]

    # Common outputs and inputs
    _COMMON_OUTPUTS = []

    # Configuration patterns and their associated inputs/outputs
    _CONFIGS = {
        "knowledge_base": {
            "inputs": [{"field": "object", "type": "knowledge_base"}],
            "outputs": [],
        }
    }

    # List of parameters that affect configuration
    _PARAMS = ["object_type"]

    def __init__(
        self,
        id: Optional[str] = None,
        node_name: Optional[str] = None,
        execution_mode: Optional[str] = None,
        object_type: str = "knowledge_base",
        object: Optional[Any] = None,
        org_name: str = "",
        user_identifier: str = "",
        **kwargs
    ):
        # Initialize with params
        params = {}
        params["object_type"] = object_type

        super().__init__(
            node_type="share_object",
            params=params,
            id=id,
            node_name=node_name,
            execution_mode=execution_mode,
        )

        # Set input values
        if object_type is not None:
            self.inputs["object_type"] = object_type
        if user_identifier is not None:
            self.inputs["user_identifier"] = user_identifier
        if org_name is not None:
            self.inputs["org_name"] = org_name
        if object is not None:
            self.inputs["object"] = object

        # Update any additional inputs
        if kwargs:
            self.update_inputs(**kwargs)

    @classmethod
    def from_dict(cls, data: dict) -> "ShareObjectNode":
        """Create a node instance from a dictionary."""
        inputs = data.get("inputs", {})
        id = data.get("id", None)
        name = data.get("name", None)
        execution_mode = data.get("execution_mode", None)
        return cls(**inputs, id=id, node_name=name, execution_mode=execution_mode)


@Node.register_node_type("rename_file")
class RenameFileNode(Node):
    """
    Rename an existing file, assigning a new name along with the file extension

    ## Inputs
    ### Common Inputs
        file: The file to rename.
        new_name: The new name of the file, including its extension (e.g., file.txt, file.pdf, file.csv)

    ## Outputs
    ### Common Outputs
        renamed_file: The renamed file
    """

    # Common inputs and outputs
    _COMMON_INPUTS = [
        {
            "field": "file",
            "helper_text": "The file to rename.",
            "value": None,
            "type": "file",
        },
        {
            "field": "new_name",
            "helper_text": "The new name of the file, including its extension (e.g., file.txt, file.pdf, file.csv)",
            "value": "",
            "type": "string",
        },
    ]

    # Common outputs and inputs
    _COMMON_OUTPUTS = [{"field": "renamed_file", "helper_text": "The renamed file"}]

    # Configuration patterns and their associated inputs/outputs
    _CONFIGS = {}

    # List of parameters that affect configuration
    _PARAMS = []

    def __init__(
        self,
        id: Optional[str] = None,
        node_name: Optional[str] = None,
        execution_mode: Optional[str] = None,
        file: Optional[str] = None,
        new_name: str = "",
        **kwargs
    ):
        # Initialize with params
        params = {}

        super().__init__(
            node_type="rename_file",
            params=params,
            id=id,
            node_name=node_name,
            execution_mode=execution_mode,
        )

        # Set input values
        if file is not None:
            self.inputs["file"] = file
        if new_name is not None:
            self.inputs["new_name"] = new_name

        # Update any additional inputs
        if kwargs:
            self.update_inputs(**kwargs)

    @property
    def renamed_file(self) -> str:
        """
        The renamed file


        Raises:
            AttributeError: If this output is not available for the current parameter values
        """
        return self.__getattr__("renamed_file")

    @classmethod
    def from_dict(cls, data: dict) -> "RenameFileNode":
        """Create a node instance from a dictionary."""
        inputs = data.get("inputs", {})
        id = data.get("id", None)
        name = data.get("name", None)
        execution_mode = data.get("execution_mode", None)
        return cls(**inputs, id=id, node_name=name, execution_mode=execution_mode)


@Node.register_node_type("start_flag")
class StartFlagNode(Node):
    """
    Start Flag

    ## Inputs
        None

    ## Outputs
        None
    """

    # Common inputs and outputs
    _COMMON_INPUTS = []

    # Common outputs and inputs
    _COMMON_OUTPUTS = []

    # Configuration patterns and their associated inputs/outputs
    _CONFIGS = {}

    # List of parameters that affect configuration
    _PARAMS = []

    def __init__(
        self,
        id: Optional[str] = None,
        node_name: Optional[str] = None,
        execution_mode: Optional[str] = None,
        **kwargs
    ):
        # Initialize with params
        params = {}

        super().__init__(
            node_type="start_flag",
            params=params,
            id=id,
            node_name=node_name,
            execution_mode=execution_mode,
        )

        # Set input values

        # Update any additional inputs
        if kwargs:
            self.update_inputs(**kwargs)

    @classmethod
    def from_dict(cls, data: dict) -> "StartFlagNode":
        """Create a node instance from a dictionary."""
        inputs = data.get("inputs", {})
        id = data.get("id", None)
        name = data.get("name", None)
        execution_mode = data.get("execution_mode", None)
        return cls(**inputs, id=id, node_name=name, execution_mode=execution_mode)


@Node.register_node_type("talk")
class TalkNode(Node):
    """
    Send a given message at a stage in a conversation.

    ## Inputs
    ### Common Inputs
        is_iframe: The is_iframe input
        variant: The variant input
    ### When variant = 'card'
        button: The button input
        content: The text to send to the user.
        description: The card’s description.
        image_url: The image to be sent at this step in the conversation.
        title: The card’s title.
    ### When variant = 'carousel'
        cards: The cards input
    ### When variant = 'message' and is_iframe = False
        content: The text to send to the user.
    ### When variant = 'message' and is_iframe = True
        content: The text to send to the user.
    ### When variant = 'image'
        image_url: The image to be sent at this step in the conversation.

    ## Outputs
        None
    """

    # Common inputs and outputs
    _COMMON_INPUTS = [
        {
            "field": "is_iframe",
            "helper_text": "The is_iframe input",
            "value": False,
            "type": "bool",
        },
        {
            "field": "variant",
            "helper_text": "The variant input",
            "value": "",
            "type": "string",
        },
    ]

    # Common outputs and inputs
    _COMMON_OUTPUTS = []

    # Configuration patterns and their associated inputs/outputs
    _CONFIGS = {
        "message**false": {
            "title": "Message",
            "helper_text": "Send a given message at a stage in a conversation.",
            "short_description": "Send a given message at a stage in a conversation.",
            "inputs": [
                {
                    "field": "content",
                    "type": "string",
                    "helper_text": "The text to send to the user.",
                    "value": "",
                },
                {"field": "variant", "type": "string", "value": "message"},
            ],
            "outputs": [],
        },
        "message**true": {
            "title": "Message",
            "helper_text": "Send a given message at a stage in a conversation.",
            "short_description": "Send a given iframe at a stage in a conversation.",
            "inputs": [
                {
                    "field": "content",
                    "type": "string",
                    "helper_text": "The text to send to the user.",
                    "value": "<iframe src='ENTER_URL_HERE' width='320px' height='400px'></iframe>",
                },
                {"field": "variant", "type": "string", "value": "message"},
            ],
            "outputs": [],
            "banner_text": "Please add your url in 'ENTER_URL_HERE'. Iframe width should be 320px",
        },
        "image**(*)": {
            "title": "Image",
            "helper_text": "Send an image in chat at this step in the conversation.",
            "short_description": "Send an image in chat at this step in the conversation.",
            "inputs": [
                {"field": "variant", "type": "string", "value": "image"},
                {
                    "field": "image_url",
                    "type": "image",
                    "helper_text": "The image to be sent at this step in the conversation.",
                },
            ],
            "outputs": [],
        },
        "card**(*)": {
            "title": "Card",
            "helper_text": "Send a card (a component with image, title, description, and button) in chat at this step in the conversation.",
            "short_description": "Send a card (a component with image, title, description, and button) in chat at this step in the conversation.",
            "inputs": [
                {"field": "variant", "type": "string", "value": "card"},
                {"field": "content", "type": "string", "value": "This is content"},
                {
                    "field": "title",
                    "type": "string",
                    "value": "",
                    "helper_text": "The card’s title.",
                },
                {
                    "field": "description",
                    "type": "string",
                    "value": "",
                    "helper_text": "The card’s description.",
                },
                {
                    "field": "button",
                    "type": "Dict[str, Any]",
                    "value": {
                        "id": "asfkwewkfmdke",
                        "name": "Submit",
                        "url": "https://vectorshift.ai/",
                        "actionType": "Link",
                    },
                    "table": {
                        "name": {"helper_text": "The name of the button."},
                        "url": {
                            "helper_text": "The URL to navigate to when the button is clicked."
                        },
                        "actionType": {
                            "helper_text": "Select the action to occur when the button is clicked."
                        },
                    },
                },
                {
                    "field": "image_url",
                    "type": "image",
                    "helper_text": "The card’s image.",
                },
            ],
            "outputs": [],
        },
        "carousel**(*)": {
            "title": "Carousel",
            "helper_text": "Send a carousel (a gallery of multiple cards) in chat at this step in the conversation.",
            "short_description": "Send a carousel (a gallery of multiple cards) in chat at this step in the conversation.",
            "inputs": [
                {"field": "variant", "type": "string", "value": "carousel"},
                {
                    "field": "cards",
                    "type": "vec<Dict[str, Any] }>",
                    "value": [
                        {
                            "id": "afgj3rf4fmo3i4jrf43rgfm",
                            "title": "Card 1",
                            "description": "This is a description",
                            "image_url": {},
                            "button": {
                                "id": "fref43jrfn",
                                "name": "Submit",
                                "url": "https://vectorshift.ai/",
                                "actionType": "Link",
                            },
                        }
                    ],
                    "table": {
                        "title": {"helper_text": "The card’s title."},
                        "description": {"helper_text": "The card’s description."},
                        "image_url": {"helper_text": "The card’s image URL."},
                        "button": {
                            "name": {"helper_text": "The name of the button."},
                            "url": {
                                "helper_text": "The URL to navigate to when the button is clicked."
                            },
                            "actionType": {
                                "helper_text": "Select the action to occur when the button is clicked."
                            },
                        },
                    },
                },
            ],
            "outputs": [],
        },
    }

    # List of parameters that affect configuration
    _PARAMS = ["variant", "is_iframe"]

    def __init__(
        self,
        id: Optional[str] = None,
        node_name: Optional[str] = None,
        execution_mode: Optional[str] = None,
        variant: str = "",
        is_iframe: bool = False,
        button: Any = {
            "id": "asfkwewkfmdke",
            "name": "Submit",
            "url": "https://vectorshift.ai/",
            "actionType": "Link",
        },
        cards: List[Any] = [
            {
                "id": "afgj3rf4fmo3i4jrf43rgfm",
                "title": "Card 1",
                "description": "This is a description",
                "image_url": {},
                "button": {
                    "id": "fref43jrfn",
                    "name": "Submit",
                    "url": "https://vectorshift.ai/",
                    "actionType": "Link",
                },
            }
        ],
        content: str = "",
        description: str = "",
        image_url: Optional[Any] = None,
        title: str = "",
        **kwargs
    ):
        # Initialize with params
        params = {}
        params["variant"] = variant
        params["is_iframe"] = is_iframe

        super().__init__(
            node_type="talk",
            params=params,
            id=id,
            node_name=node_name,
            execution_mode=execution_mode,
        )

        # Set input values
        if variant is not None:
            self.inputs["variant"] = variant
        if is_iframe is not None:
            self.inputs["is_iframe"] = is_iframe
        if content is not None:
            self.inputs["content"] = content
        if image_url is not None:
            self.inputs["image_url"] = image_url
        if title is not None:
            self.inputs["title"] = title
        if description is not None:
            self.inputs["description"] = description
        if button is not None:
            self.inputs["button"] = button
        if cards is not None:
            self.inputs["cards"] = cards

        # Update any additional inputs
        if kwargs:
            self.update_inputs(**kwargs)

    @classmethod
    def from_dict(cls, data: dict) -> "TalkNode":
        """Create a node instance from a dictionary."""
        inputs = data.get("inputs", {})
        id = data.get("id", None)
        name = data.get("name", None)
        execution_mode = data.get("execution_mode", None)
        return cls(**inputs, id=id, node_name=name, execution_mode=execution_mode)


@Node.register_node_type("listen")
class ListenNode(Node):
    """
    Listen for user input at a stage in the conversation.

    ## Inputs
    ### Common Inputs
        variant: The variant input
    ### button
        allow_user_message: The allow_user_message input
        buttons: The buttons input
        processed_outputs: The processed_outputs input
    ### capture
        value: The value input

    ## Outputs
    ### button
        [processed_outputs]: The [processed_outputs] output
    ### capture
        response: The user message.
    """

    # Common inputs and outputs
    _COMMON_INPUTS = [
        {
            "field": "variant",
            "helper_text": "The variant input",
            "value": "",
            "type": "string",
        }
    ]

    # Common outputs and inputs
    _COMMON_OUTPUTS = []

    # Configuration patterns and their associated inputs/outputs
    _CONFIGS = {
        "button": {
            "title": "Button",
            "helper_text": "Present users with clickable buttons during a conversation at this step and wait for the user to select one.",
            "short_description": "Present users with clickable buttons during a conversation at this step and wait for the user to select one.",
            "inputs": [
                {
                    "field": "buttons",
                    "type": "vec<Dict[str, Any]>",
                    "value": [{"name": "Button 1", "id": "8awi58eyqirm8ik9aq3"}],
                },
                {
                    "field": "processed_outputs",
                    "type": "map<string, string>",
                    "value": {"button_1": "path"},
                },
                {"field": "variant", "type": "string", "value": "button"},
                {"field": "allow_user_message", "type": "bool", "value": False},
            ],
            "outputs": [{"field": "[processed_outputs]", "type": ""}],
        },
        "capture": {
            "title": "Capture",
            "helper_text": "The conversation will pause at this step in the conversation and wait for the user to respond in chat. The user response will be stored in the capture response variable.",
            "short_description": "The conversation will pause at this step in the conversation and wait for the user to respond in chat. The user response will be stored in the capture response variable.",
            "inputs": [
                {"field": "value", "type": "string", "value": ""},
                {"field": "variant", "type": "string", "value": "capture"},
            ],
            "outputs": [
                {
                    "field": "response",
                    "type": "string",
                    "value": "",
                    "helper_text": "The user message.",
                }
            ],
        },
    }

    # List of parameters that affect configuration
    _PARAMS = ["variant"]

    def __init__(
        self,
        id: Optional[str] = None,
        node_name: Optional[str] = None,
        execution_mode: Optional[str] = None,
        variant: str = "",
        allow_user_message: bool = False,
        buttons: List[Any] = [{"name": "Button 1", "id": "8awi58eyqirm8ik9aq3"}],
        processed_outputs: Dict[str, str] = {"button_1": "path"},
        value: str = "",
        **kwargs
    ):
        # Initialize with params
        params = {}
        params["variant"] = variant

        super().__init__(
            node_type="listen",
            params=params,
            id=id,
            node_name=node_name,
            execution_mode=execution_mode,
        )

        # Set input values
        if variant is not None:
            self.inputs["variant"] = variant
        if buttons is not None:
            self.inputs["buttons"] = buttons
        if processed_outputs is not None:
            self.inputs["processed_outputs"] = processed_outputs
        if allow_user_message is not None:
            self.inputs["allow_user_message"] = allow_user_message
        if value is not None:
            self.inputs["value"] = value

        # Update any additional inputs
        if kwargs:
            self.update_inputs(**kwargs)

    @property
    def response(self) -> str:
        """
        The user message.

        Available: capture


        Raises:
            AttributeError: If this output is not available for the current parameter values
        """
        return self.__getattr__("response")

    @classmethod
    def from_dict(cls, data: dict) -> "ListenNode":
        """Create a node instance from a dictionary."""
        inputs = data.get("inputs", {})
        id = data.get("id", None)
        name = data.get("name", None)
        execution_mode = data.get("execution_mode", None)
        return cls(**inputs, id=id, node_name=name, execution_mode=execution_mode)


@Node.register_node_type("add_node")
class AddNodeNode(Node):
    """
    Add Node

    ## Inputs
        None

    ## Outputs
        None
    """

    # Common inputs and outputs
    _COMMON_INPUTS = []

    # Common outputs and inputs
    _COMMON_OUTPUTS = []

    # Configuration patterns and their associated inputs/outputs
    _CONFIGS = {}

    # List of parameters that affect configuration
    _PARAMS = []

    def __init__(
        self,
        id: Optional[str] = None,
        node_name: Optional[str] = None,
        execution_mode: Optional[str] = None,
        **kwargs
    ):
        # Initialize with params
        params = {}

        super().__init__(
            node_type="add_node",
            params=params,
            id=id,
            node_name=node_name,
            execution_mode=execution_mode,
        )

        # Set input values

        # Update any additional inputs
        if kwargs:
            self.update_inputs(**kwargs)

    @classmethod
    def from_dict(cls, data: dict) -> "AddNodeNode":
        """Create a node instance from a dictionary."""
        inputs = data.get("inputs", {})
        id = data.get("id", None)
        name = data.get("name", None)
        execution_mode = data.get("execution_mode", None)
        return cls(**inputs, id=id, node_name=name, execution_mode=execution_mode)


__all__ = [
    "AppendFilesNode",
    "StickyNoteNode",
    "TransformationNode",
    "ChatFileReaderNode",
    "PipelineNode",
    "AgentNode",
    "ChatMemoryNode",
    "LlmNode",
    "InputNode",
    "OutputNode",
    "CategorizerNode",
    "ExtractDataNode",
    "DataCollectorNode",
    "ScorerNode",
    "SpeechToTextNode",
    "FileSaveNode",
    "ImageGenNode",
    "FileNode",
    "GetListItemNode",
    "LlmOpenAiVisionNode",
    "LlmGoogleVisionNode",
    "SplitTextNode",
    "SummarizerNode",
    "TextNode",
    "TextToFileNode",
    "TimeNode",
    "TranslatorNode",
    "TtsElevenLabsNode",
    "TtsOpenAiNode",
    "AiAudioOperationsNode",
    "AiTextToSpeechNode",
    "AiSpeechToTextNode",
    "AiImageOperationsNode",
    "AiImageToTextNode",
    "AiTextToImageNode",
    "LlmAnthropicVisionNode",
    "SemanticSearchNode",
    "KnowledgeBaseNode",
    "KnowledgeBaseLoaderNode",
    "MapNode",
    "MergeNode",
    "ConditionNode",
    "NlToSqlNode",
    "ReadJsonValuesNode",
    "WriteJsonValueNode",
    "ApiNode",
    "UrlLoaderNode",
    "WikipediaNode",
    "YoutubeNode",
    "ArxivNode",
    "SerpApiNode",
    "YouDotComNode",
    "ExaAiNode",
    "GoogleSearchNode",
    "GoogleAlertRssReaderNode",
    "RssFeedReaderNode",
    "CsvQueryNode",
    "CsvReaderNode",
    "CsvWriterNode",
    "CreateListNode",
    "CombineListNode",
    "ListTrimmerNode",
    "DuplicateListNode",
    "FlattenListNode",
    "JoinListItemNode",
    "CsvToExcelNode",
    "TextFormatterNode",
    "JsonOperationsNode",
    "ListOperationsNode",
    "IntegrationNode",
    "ZapierNode",
    "MakeNode",
    "TextManipulationNode",
    "FileOperationsNode",
    "AiOperationsNode",
    "FileToTextNode",
    "CodeExecutionNode",
    "ChunkingNode",
    "NotificationsNode",
    "CustomSmtpEmailSenderNode",
    "EmailNotificationNode",
    "SmsNotificationNode",
    "AiFilterListNode",
    "FilterListNode",
    "SalesDataEnrichmentNode",
    "EmailValidatorNode",
    "CombineTextNode",
    "FindAndReplaceNode",
    "AiFillPdfNode",
    "ExtractToTableNode",
    "SortCsvNode",
    "TriggerNode",
    "KnowledgeBaseActionsNode",
    "KnowledgeBaseSyncNode",
    "KnowledgeBaseCreateNode",
    "ShareObjectNode",
    "RenameFileNode",
    "StartFlagNode",
    "TalkNode",
    "ListenNode",
    "AddNodeNode",
]
