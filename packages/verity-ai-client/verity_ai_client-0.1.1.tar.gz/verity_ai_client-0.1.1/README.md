# Verity AI Python Client

[![PyPI version](https://badge.fury.io/py/verity-ai-client.svg)](https://badge.fury.io/py/verity-ai-client)
[![Python Support](https://img.shields.io/pypi/pyversions/verity-ai-client.svg)](https://pypi.org/project/verity-ai-client/)
[![License: MIT](https://img.shields.io/badge/License-MIT-yellow.svg)](https://opensource.org/licenses/MIT)

Official Python client for **Verity AI** - A comprehensive API service for unstructured and structured RAG (Retrieval-Augmented Generation), file management, AI interactions, and knowledge base operations.

## 🚀 Features

- **RAG Generation**: Powerful retrieval-augmented generation for both structured and unstructured data
- **File Management**: Upload, list, and delete files with ease
- **Knowledge Base Operations**: Manage and query knowledge bases
- **Database Integration**: Natural language SQL queries and database operations
- **AI Chat Completions**: Advanced chat completions with multiple AI models
- **Type Safety**: Full type hints and Pydantic models for better development experience
- **Async Support**: Built for modern async Python applications

## 📦 Installation

Install the Verity AI Python client using pip:

```bash
pip install verity-ai-client
```

For development with optional dependencies:

```bash
pip install verity-ai-client[dev]
```

## 🔧 Quick Start

### Authentication

First, obtain your API key from [Verity Labs](https://veritylabs.ai) and set it as an environment variable:

```bash
export API_KEY="your-api-key-here"
```

### Basic Usage

```python
import os
import verity_ai_pyc
from verity_ai_pyc.rest import ApiException

# Configure the client
configuration = verity_ai_pyc.Configuration(
    host="https://chat.veritylabs.ai"
)
configuration.api_key['XAPIKeyAuth'] = os.environ["API_KEY"]

# Create API client
with verity_ai_pyc.ApiClient(configuration) as api_client:
    # List available models
    models_api = verity_ai_pyc.ModelsApi(api_client)
    try:
        models = models_api.list_models_rag_generation_models_get()
        print("Available models:", models)
    except ApiException as e:
        print(f"Error: {e}")
```

### Chat Completions

```python
# Create a chat completion
completions_api = verity_ai_pyc.CompletionsApi(api_client)

chat_request = verity_ai_pyc.ChatCompletionRequestPublic(
    model="anthropic_claude_3_5_sonnet_v1",
    messages=[
        verity_ai_pyc.Message(
            role="user",
            content="What is artificial intelligence?"
        )
    ],
    data_type="unstructured",
    knowledge_base="all"
)

try:
    response = completions_api.create_chat_completion_rag_generation_chat_completions_post(chat_request)
    print("AI Response:", response.messages[0].content)
except ApiException as e:
    print(f"Error: {e}")
```

### SQL Database Queries

```python
# Query a database using natural language
completions_api = verity_ai_pyc.CompletionsApi(api_client)

chat_request = verity_ai_pyc.ChatCompletionRequestPublic(
    model="anthropic_claude_3_5_sonnet_v1",
    messages=[
        verity_ai_pyc.Message(
            role="user",
            content="How many records are in the database?"
        )
    ],
    data_type="structured",
    database_name="veritydemo_mimic"
)

try:
    response = completions_api.create_chat_completion_rag_generation_chat_completions_post(chat_request)
    print("SQL Response:", response.messages[0].content)
except ApiException as e:
    print(f"Error: {e}")
```

### File Management

```python
# List files
file_management_api = verity_ai_pyc.FileManagementApi(api_client)

try:
    response = file_management_api.list_files_get_fileman_data_list_get(
        storage_type="unstructured",
        page=1,
        page_size=5
    )
    print(f"Found {len(response.files)} files:")
    for file_info in response.files:
        print(f"- {file_info.filename} ({file_info.size_mb:.2f} MB)")
except ApiException as e:
    print(f"Error: {e}")
```

### Knowledge Base Retrieval

```python
# Retrieve relevant documents
unstructured_api = verity_ai_pyc.UnstructuredApi(api_client)

retrieval_request = verity_ai_pyc.RetrievalRequestPublic(
    query="machine learning algorithms",
    knowledge_base="all",
    top_k=5
)

try:
    results = unstructured_api.retrieve(retrieval_request)
    print("Document search completed successfully!")
    print(f"Retrieved {len(results.documents)} documents")
except ApiException as e:
    print(f"Retrieval error: {e}")
```

## 📚 API Documentation

### Available APIs

- **CompletionsApi**: Chat completions and AI interactions
- **FileManagementApi**: File upload, listing, and deletion
- **ModelsApi**: List available AI models
- **UnstructuredApi**: Knowledge base and document operations
- **StructuredApi**: Database and SQL operations

### Key Models

- `ChatCompletionRequestPublic`: Request structure for chat completions
- `Message`: Individual message in a conversation
- `FileInfo`: File metadata and information
- `RetrievalRequestPublic`: Document retrieval requests

For detailed API documentation, visit: [https://docs.veritylabs.ai](https://docs.veritylabs.ai)

## 🔒 Authentication

The Verity AI API uses API key authentication. Include your API key in the `x-api-key` header:

```python
configuration.api_key['XAPIKeyAuth'] = "your-api-key"
```

## 🛠️ Development

### Requirements

- Python 3.9+
- Dependencies listed in `pyproject.toml`

### Installation for Development

```bash
git clone https://github.com/veritylabs/verity-ai-python-client.git
cd verity-ai-python-client
pip install -e .[dev]
```

### Running Tests

```bash
pytest
```

### Code Formatting

```bash
black .
isort .
```

### Type Checking

```bash
mypy verity_ai_pyc
```

## 📄 License

This project is licensed under the MIT License - see the [LICENSE](LICENSE) file for details.

## 🤝 Contributing

We welcome contributions! Please see our [Contributing Guidelines](CONTRIBUTING.md) for details.

## 📞 Support

- **Documentation**: [https://docs.veritylabs.ai](https://docs.veritylabs.ai)
- **Issues**: [GitHub Issues](https://github.com/veritylabs/verity-ai-python-client/issues)
- **Email**: support@veritylabs.ai

## 🔗 Links

- **Homepage**: [https://veritylabs.ai](https://veritylabs.ai)
- **PyPI**: [https://pypi.org/project/verity-ai-client/](https://pypi.org/project/verity-ai-client/)
- **GitHub**: [https://github.com/veritylabs/verity-ai-python-client](https://github.com/veritylabs/verity-ai-python-client)

---

Built with ❤️ by [Verity Labs](https://veritylabs.ai)




