# Changelog

All notable changes to the Verity AI Python Client will be documented in this file.

The format is based on [Keep a Changelog](https://keepachangelog.com/en/1.0.0/),
and this project adheres to [Semantic Versioning](https://semver.org/spec/v2.0.0.html).

## [0.1.0] - 2024-12-19

### Added
- Initial release of Verity AI Python Client
- Support for chat completions with multiple AI models
- File management operations (upload, list, delete)
- Knowledge base document operations
- Database and SQL query capabilities
- Retrieval-augmented generation (RAG) functionality
- Full type safety with Pydantic models
- Comprehensive API coverage for Verity AI services
- Authentication via API key (x-api-key header)
- Support for Python 3.9+

### Features
- **CompletionsApi**: Chat completions and AI interactions
- **FileManagementApi**: File upload, listing, and deletion
- **ModelsApi**: List available AI models
- **UnstructuredApi**: Knowledge base and document operations
- **StructuredApi**: Database and SQL operations

### Models
- Complete set of Pydantic models for all API operations
- Type-safe request and response handling
- Validation and serialization support

### Documentation
- Comprehensive README with usage examples
- API documentation for all endpoints
- Type hints and docstrings throughout

### Infrastructure
- Modern pyproject.toml configuration
- Support for development dependencies
- Testing framework setup
- Code quality tools (black, isort, mypy)
- MIT license

## [Unreleased]

### Planned
- Async client support
- Enhanced error handling
- Additional utility functions
- Performance optimizations
- Extended examples and tutorials 