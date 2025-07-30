# verity_ai_pyc.StructuredApi

All URIs are relative to *https://chat.veritylabs.ai*

Method | HTTP request | Description
------------- | ------------- | -------------
[**list_db_tables_unstructured**](StructuredApi.md#list_db_tables_unstructured) | **GET** /services/rag-generation/db_tables | list db tables


# **list_db_tables_unstructured**
> object list_db_tables_unstructured()

list db tables

Get Glue databases and tables for the specified organization.

Parameters:
- org: Organization prefix to filter databases

Returns:
- Dictionary of databases and their tables

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
    api_instance = verity_ai_pyc.StructuredApi(api_client)

    try:
        # list db tables
        api_response = api_instance.list_db_tables_unstructured()
        print("The response of StructuredApi->list_db_tables_unstructured:\n")
        pprint(api_response)
    except Exception as e:
        print("Exception when calling StructuredApi->list_db_tables_unstructured: %s\n" % e)
```



### Parameters

This endpoint does not need any parameter.

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

[[Back to top]](#) [[Back to API list]](../README.md#documentation-for-api-endpoints) [[Back to Model list]](../README.md#documentation-for-models) [[Back to README]](../README.md)

