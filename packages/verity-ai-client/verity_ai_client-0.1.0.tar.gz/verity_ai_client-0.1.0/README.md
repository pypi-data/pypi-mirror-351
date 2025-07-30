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
export VERITY_API_KEY="your-api-key-here"
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
configuration.api_key['XAPIKeyAuth'] = os.environ["VERITY_API_KEY"]

# Create API client
with verity_ai_pyc.ApiClient(configuration) as api_client:
    # List available models
    models_api = verity_ai_pyc.ModelsApi(api_client)
    try:
        models = models_api.list_models_rag_generation_models_get()
        print("Available models:", [model.id for model in models.data])
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
        verity_ai_pyc.ChatCompletionMessage(
            role="user",
            content="What is artificial intelligence?"
        )
    ],
    max_tokens=150
)

try:
    response = completions_api.create_chat_completion_rag_generation_chat_completions_post(chat_request)
    print("AI Response:", response.choices[0].message.content)
except ApiException as e:
    print(f"Error: {e}")
```

### File Management

```python
# Upload a file
file_api = verity_ai_pyc.FileManagementApi(api_client)

with open("document.pdf", "rb") as file:
    try:
        upload_response = file_api.upload_file_fileman_data_upload_post(
            file=file,
            knowledge_base_id="your-kb-id"
        )
        print("File uploaded:", upload_response.file_id)
    except ApiException as e:
        print(f"Upload error: {e}")

# List files
try:
    files = file_api.list_files_get_fileman_data_list_get()
    print("Your files:", [f.filename for f in files.files])
except ApiException as e:
    print(f"List error: {e}")
```

### Knowledge Base Retrieval

```python
# Retrieve relevant documents
unstructured_api = verity_ai_pyc.UnstructuredApi(api_client)

retrieval_request = verity_ai_pyc.RetrievalRequestPublic(
    query="machine learning algorithms",
    top_k=5,
    knowledge_base_id="your-kb-id"
)

try:
    results = unstructured_api.retrieve(retrieval_request)
    print("Retrieved documents:", len(results.documents))
    for doc in results.documents:
        print(f"- {doc.content[:100]}...")
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
- `ChatCompletionResponse`: Response from chat completions
- `FileInfo`: File metadata and information
- `RetrievalRequestPublic`: Document retrieval requests
- `ValidateDocsRequest`: Document validation requests

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




