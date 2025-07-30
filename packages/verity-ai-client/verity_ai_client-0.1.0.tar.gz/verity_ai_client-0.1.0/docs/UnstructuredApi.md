# verity_ai_pyc.UnstructuredApi

All URIs are relative to *https://chat.veritylabs.ai*

Method | HTTP request | Description
------------- | ------------- | -------------
[**list_kb_documents**](UnstructuredApi.md#list_kb_documents) | **GET** /services/rag-generation/kb_docs | list knowledge base documents
[**retrieve**](UnstructuredApi.md#retrieve) | **POST** /services/rag-generation/retrieve | retrieve unstructured data
[**validate_ingestion_rag_generation_validate_ingestion_post**](UnstructuredApi.md#validate_ingestion_rag_generation_validate_ingestion_post) | **POST** /services/rag-generation/validate_ingestion | Validate ingestion status of uploaded documents


# **list_kb_documents**
> object list_kb_documents(knowledge_base=knowledge_base, page=page, page_size=page_size, continuation_token=continuation_token)

list knowledge base documents

Retrieve documents grouped by knowledge base for the user's organization.

Parameters:
- knowledge_base: Optional filter to limit results to a specific knowledge base
- page: Page number (for compatibility, pagination uses continuation tokens)
- page_size: Number of documents per page (max 1000)
- continuation_token: Token for fetching the next page of results

Returns:
- Dictionary containing:
  - documents: Dictionary of knowledge bases and their associated documents
  - pagination: Pagination information including next_token if there are more results

### Example

* Api Key Authentication (XAPIKeyAuth):

```python
import verity_ai_pyc
from verity_ai_pyc.rest import ApiException
from pprint import pprint

# Defining the host is optional and defaults to https://chat.veritylabs.ai
# See configuration.py for a list of all supported configuration parameters.
configuration = verity_ai_pyc.Configuration(
    host = "https://chat.veritylabs.ai"
)

# The client must configure the authentication and authorization parameters
# in accordance with the API server security policy.
# Examples for each auth method are provided below, use the example that
# satisfies your auth use case.

# Configure API key authorization: XAPIKeyAuth
configuration.api_key['XAPIKeyAuth'] = os.environ["API_KEY"]

# Uncomment below to setup prefix (e.g. Bearer) for API key, if needed
# configuration.api_key_prefix['XAPIKeyAuth'] = 'Bearer'

# Enter a context with an instance of the API client
with verity_ai_pyc.ApiClient(configuration) as api_client:
    # Create an instance of the API class
    api_instance = verity_ai_pyc.UnstructuredApi(api_client)
    knowledge_base = 'knowledge_base_example' # str | Optional knowledge base filter (optional)
    page = 1 # int | Page number for pagination (optional) (default to 1)
    page_size = 50 # int | Number of documents per page (max 1000) (optional) (default to 50)
    continuation_token = 'continuation_token_example' # str | Token for fetching the next page of results (optional)

    try:
        # list knowledge base documents
        api_response = api_instance.list_kb_documents(knowledge_base=knowledge_base, page=page, page_size=page_size, continuation_token=continuation_token)
        print("The response of UnstructuredApi->list_kb_documents:\n")
        pprint(api_response)
    except Exception as e:
        print("Exception when calling UnstructuredApi->list_kb_documents: %s\n" % e)
```



### Parameters


Name | Type | Description  | Notes
------------- | ------------- | ------------- | -------------
 **knowledge_base** | **str**| Optional knowledge base filter | [optional] 
 **page** | **int**| Page number for pagination | [optional] [default to 1]
 **page_size** | **int**| Number of documents per page (max 1000) | [optional] [default to 50]
 **continuation_token** | **str**| Token for fetching the next page of results | [optional] 

### Return type

**object**

### Authorization

[XAPIKeyAuth](../README.md#XAPIKeyAuth)

### HTTP request headers

 - **Content-Type**: Not defined
 - **Accept**: application/json

### HTTP response details

| Status code | Description | Response headers |
|-------------|-------------|------------------|
**200** | Successful Response |  -  |
**422** | Validation Error |  -  |

[[Back to top]](#) [[Back to API list]](../README.md#documentation-for-api-endpoints) [[Back to Model list]](../README.md#documentation-for-models) [[Back to README]](../README.md)

# **retrieve**
> object retrieve(retrieval_request_public)

retrieve unstructured data

Trigger the RAG retrieval process using the provided query and knowledge_base.

Request Body:
  - query: The query string to use for document retrieval.
  - top_k: The number of top documents to retrieve (5-10).
  - knowledge_base: The specific knowledge base to use, default is 'all'.

Returns:
  A JSON object containing the retrieval results.

### Example

* Api Key Authentication (XAPIKeyAuth):

```python
import verity_ai_pyc
from verity_ai_pyc.models.retrieval_request_public import RetrievalRequestPublic
from verity_ai_pyc.rest import ApiException
from pprint import pprint

# Defining the host is optional and defaults to https://chat.veritylabs.ai
# See configuration.py for a list of all supported configuration parameters.
configuration = verity_ai_pyc.Configuration(
    host = "https://chat.veritylabs.ai"
)

# The client must configure the authentication and authorization parameters
# in accordance with the API server security policy.
# Examples for each auth method are provided below, use the example that
# satisfies your auth use case.

# Configure API key authorization: XAPIKeyAuth
configuration.api_key['XAPIKeyAuth'] = os.environ["API_KEY"]

# Uncomment below to setup prefix (e.g. Bearer) for API key, if needed
# configuration.api_key_prefix['XAPIKeyAuth'] = 'Bearer'

# Enter a context with an instance of the API client
with verity_ai_pyc.ApiClient(configuration) as api_client:
    # Create an instance of the API class
    api_instance = verity_ai_pyc.UnstructuredApi(api_client)
    retrieval_request_public = verity_ai_pyc.RetrievalRequestPublic() # RetrievalRequestPublic | 

    try:
        # retrieve unstructured data
        api_response = api_instance.retrieve(retrieval_request_public)
        print("The response of UnstructuredApi->retrieve:\n")
        pprint(api_response)
    except Exception as e:
        print("Exception when calling UnstructuredApi->retrieve: %s\n" % e)
```



### Parameters


Name | Type | Description  | Notes
------------- | ------------- | ------------- | -------------
 **retrieval_request_public** | [**RetrievalRequestPublic**](RetrievalRequestPublic.md)|  | 

### Return type

**object**

### Authorization

[XAPIKeyAuth](../README.md#XAPIKeyAuth)

### HTTP request headers

 - **Content-Type**: application/json
 - **Accept**: application/json

### HTTP response details

| Status code | Description | Response headers |
|-------------|-------------|------------------|
**200** | Successful Response |  -  |
**422** | Validation Error |  -  |

[[Back to top]](#) [[Back to API list]](../README.md#documentation-for-api-endpoints) [[Back to Model list]](../README.md#documentation-for-models) [[Back to README]](../README.md)

# **validate_ingestion_rag_generation_validate_ingestion_post**
> ValidateDocsResponse validate_ingestion_rag_generation_validate_ingestion_post(validate_docs_request)

Validate ingestion status of uploaded documents

Validate ingestion of given document IDs by checking their presence in the OpenSearch index.

### Example

* Api Key Authentication (XAPIKeyAuth):

```python
import verity_ai_pyc
from verity_ai_pyc.models.validate_docs_request import ValidateDocsRequest
from verity_ai_pyc.models.validate_docs_response import ValidateDocsResponse
from verity_ai_pyc.rest import ApiException
from pprint import pprint

# Defining the host is optional and defaults to https://chat.veritylabs.ai
# See configuration.py for a list of all supported configuration parameters.
configuration = verity_ai_pyc.Configuration(
    host = "https://chat.veritylabs.ai"
)

# The client must configure the authentication and authorization parameters
# in accordance with the API server security policy.
# Examples for each auth method are provided below, use the example that
# satisfies your auth use case.

# Configure API key authorization: XAPIKeyAuth
configuration.api_key['XAPIKeyAuth'] = os.environ["API_KEY"]

# Uncomment below to setup prefix (e.g. Bearer) for API key, if needed
# configuration.api_key_prefix['XAPIKeyAuth'] = 'Bearer'

# Enter a context with an instance of the API client
with verity_ai_pyc.ApiClient(configuration) as api_client:
    # Create an instance of the API class
    api_instance = verity_ai_pyc.UnstructuredApi(api_client)
    validate_docs_request = verity_ai_pyc.ValidateDocsRequest() # ValidateDocsRequest | 

    try:
        # Validate ingestion status of uploaded documents
        api_response = api_instance.validate_ingestion_rag_generation_validate_ingestion_post(validate_docs_request)
        print("The response of UnstructuredApi->validate_ingestion_rag_generation_validate_ingestion_post:\n")
        pprint(api_response)
    except Exception as e:
        print("Exception when calling UnstructuredApi->validate_ingestion_rag_generation_validate_ingestion_post: %s\n" % e)
```



### Parameters


Name | Type | Description  | Notes
------------- | ------------- | ------------- | -------------
 **validate_docs_request** | [**ValidateDocsRequest**](ValidateDocsRequest.md)|  | 

### Return type

[**ValidateDocsResponse**](ValidateDocsResponse.md)

### Authorization

[XAPIKeyAuth](../README.md#XAPIKeyAuth)

### HTTP request headers

 - **Content-Type**: application/json
 - **Accept**: application/json

### HTTP response details

| Status code | Description | Response headers |
|-------------|-------------|------------------|
**200** | Successful Response |  -  |
**422** | Validation Error |  -  |

[[Back to top]](#) [[Back to API list]](../README.md#documentation-for-api-endpoints) [[Back to Model list]](../README.md#documentation-for-models) [[Back to README]](../README.md)

