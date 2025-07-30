# verity_ai_pyc.CompletionsApi

All URIs are relative to *https://chat.veritylabs.ai*

Method | HTTP request | Description
------------- | ------------- | -------------
[**create_chat_completion_rag_generation_chat_completions_post**](CompletionsApi.md#create_chat_completion_rag_generation_chat_completions_post) | **POST** /services/rag-generation/chat/completions | chat completions


# **create_chat_completion_rag_generation_chat_completions_post**
> ChatCompletionResponse create_chat_completion_rag_generation_chat_completions_post(chat_completion_request_public)

chat completions

### Example

* Api Key Authentication (XAPIKeyAuth):

```python
import verity_ai_pyc
from verity_ai_pyc.models.chat_completion_request_public import ChatCompletionRequestPublic
from verity_ai_pyc.models.chat_completion_response import ChatCompletionResponse
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
    api_instance = verity_ai_pyc.CompletionsApi(api_client)
    chat_completion_request_public = verity_ai_pyc.ChatCompletionRequestPublic() # ChatCompletionRequestPublic | 

    try:
        # chat completions
        api_response = api_instance.create_chat_completion_rag_generation_chat_completions_post(chat_completion_request_public)
        print("The response of CompletionsApi->create_chat_completion_rag_generation_chat_completions_post:\n")
        pprint(api_response)
    except Exception as e:
        print("Exception when calling CompletionsApi->create_chat_completion_rag_generation_chat_completions_post: %s\n" % e)
```



### Parameters


Name | Type | Description  | Notes
------------- | ------------- | ------------- | -------------
 **chat_completion_request_public** | [**ChatCompletionRequestPublic**](ChatCompletionRequestPublic.md)|  | 

### Return type

[**ChatCompletionResponse**](ChatCompletionResponse.md)

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

