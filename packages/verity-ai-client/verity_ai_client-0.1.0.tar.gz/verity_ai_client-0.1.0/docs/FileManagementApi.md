# verity_ai_pyc.FileManagementApi

All URIs are relative to *https://chat.veritylabs.ai*

Method | HTTP request | Description
------------- | ------------- | -------------
[**delete_files_fileman_data_delete_delete**](FileManagementApi.md#delete_files_fileman_data_delete_delete) | **DELETE** /services/fileman/data/delete | delete files
[**list_files_get_fileman_data_list_get**](FileManagementApi.md#list_files_get_fileman_data_list_get) | **GET** /services/fileman/data/list | list files (GET method)
[**upload_file_fileman_data_upload_post**](FileManagementApi.md#upload_file_fileman_data_upload_post) | **POST** /services/fileman/data/upload | upload files


# **delete_files_fileman_data_delete_delete**
> DeleteResponse delete_files_fileman_data_delete_delete(storage_type, delete_request, base_path=base_path, sub_path=sub_path)

delete files

Delete one or more files from S3 using the organization name and tier from the user token.

### Example

* Api Key Authentication (XAPIKeyAuth):

```python
import verity_ai_pyc
from verity_ai_pyc.models.delete_request import DeleteRequest
from verity_ai_pyc.models.delete_response import DeleteResponse
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
    api_instance = verity_ai_pyc.FileManagementApi(api_client)
    storage_type = 'storage_type_example' # str | 
    delete_request = verity_ai_pyc.DeleteRequest() # DeleteRequest | 
    base_path = 'base_path_example' # str |  (optional)
    sub_path = 'sub_path_example' # str |  (optional)

    try:
        # delete files
        api_response = api_instance.delete_files_fileman_data_delete_delete(storage_type, delete_request, base_path=base_path, sub_path=sub_path)
        print("The response of FileManagementApi->delete_files_fileman_data_delete_delete:\n")
        pprint(api_response)
    except Exception as e:
        print("Exception when calling FileManagementApi->delete_files_fileman_data_delete_delete: %s\n" % e)
```



### Parameters


Name | Type | Description  | Notes
------------- | ------------- | ------------- | -------------
 **storage_type** | **str**|  | 
 **delete_request** | [**DeleteRequest**](DeleteRequest.md)|  | 
 **base_path** | **str**|  | [optional] 
 **sub_path** | **str**|  | [optional] 

### Return type

[**DeleteResponse**](DeleteResponse.md)

### Authorization

[XAPIKeyAuth](../README.md#XAPIKeyAuth)

### HTTP request headers

 - **Content-Type**: application/json
 - **Accept**: application/json

### HTTP response details

| Status code | Description | Response headers |
|-------------|-------------|------------------|
**200** | Successful Response |  -  |
**401** | Unauthorized |  -  |
**400** | Bad Request |  -  |
**404** | Not Found |  -  |
**500** | Internal Server Error |  -  |
**422** | Validation Error |  -  |

[[Back to top]](#) [[Back to API list]](../README.md#documentation-for-api-endpoints) [[Back to Model list]](../README.md#documentation-for-models) [[Back to README]](../README.md)

# **list_files_get_fileman_data_list_get**
> ListFilesResponse list_files_get_fileman_data_list_get(storage_type, base_path=base_path, sub_path=sub_path, page=page, page_size=page_size, continuation_token=continuation_token, dir_flag=dir_flag)

list files (GET method)

List up to 50 latest files from storage using a GET request.

- storage_type: 'structured' or 'unstructured' to list files from the appropriate storage
- base_path: Base directory path (e.g., database name for structured data or knowledge base name for unstructured)
- sub_path: Sub-directory path (e.g., table name for structured data)
- page: Page number (for compatibility, S3 pagination uses continuation tokens)
- page_size: Number of files per page (max 1000)
- continuation_token: Token for fetching the next page of results
- dir_flag: When True, directories are listed first followed by files (default: False)

### Example

* Api Key Authentication (XAPIKeyAuth):

```python
import verity_ai_pyc
from verity_ai_pyc.models.list_files_response import ListFilesResponse
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
    api_instance = verity_ai_pyc.FileManagementApi(api_client)
    storage_type = 'storage_type_example' # str | 
    base_path = 'base_path_example' # str |  (optional)
    sub_path = 'sub_path_example' # str |  (optional)
    page = 1 # int |  (optional) (default to 1)
    page_size = 50 # int |  (optional) (default to 50)
    continuation_token = 'continuation_token_example' # str |  (optional)
    dir_flag = False # bool |  (optional) (default to False)

    try:
        # list files (GET method)
        api_response = api_instance.list_files_get_fileman_data_list_get(storage_type, base_path=base_path, sub_path=sub_path, page=page, page_size=page_size, continuation_token=continuation_token, dir_flag=dir_flag)
        print("The response of FileManagementApi->list_files_get_fileman_data_list_get:\n")
        pprint(api_response)
    except Exception as e:
        print("Exception when calling FileManagementApi->list_files_get_fileman_data_list_get: %s\n" % e)
```



### Parameters


Name | Type | Description  | Notes
------------- | ------------- | ------------- | -------------
 **storage_type** | **str**|  | 
 **base_path** | **str**|  | [optional] 
 **sub_path** | **str**|  | [optional] 
 **page** | **int**|  | [optional] [default to 1]
 **page_size** | **int**|  | [optional] [default to 50]
 **continuation_token** | **str**|  | [optional] 
 **dir_flag** | **bool**|  | [optional] [default to False]

### Return type

[**ListFilesResponse**](ListFilesResponse.md)

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

# **upload_file_fileman_data_upload_post**
> UploadFileResponse upload_file_fileman_data_upload_post(file, storage_type, database_name=database_name, table_name=table_name, knowledge_base=knowledge_base, sub_path=sub_path, base_path=base_path)

upload files

Upload a file to storage:
For structured data, provide database_name and table_name.
For unstructured data, provide knowledge_base.

### Example

* Api Key Authentication (XAPIKeyAuth):

```python
import verity_ai_pyc
from verity_ai_pyc.models.upload_file_response import UploadFileResponse
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
    api_instance = verity_ai_pyc.FileManagementApi(api_client)
    file = None # bytearray | 
    storage_type = 'storage_type_example' # str | 
    database_name = 'database_name_example' # str |  (optional)
    table_name = 'table_name_example' # str |  (optional)
    knowledge_base = 'knowledge_base_example' # str |  (optional)
    sub_path = 'sub_path_example' # str |  (optional)
    base_path = 'base_path_example' # str |  (optional)

    try:
        # upload files
        api_response = api_instance.upload_file_fileman_data_upload_post(file, storage_type, database_name=database_name, table_name=table_name, knowledge_base=knowledge_base, sub_path=sub_path, base_path=base_path)
        print("The response of FileManagementApi->upload_file_fileman_data_upload_post:\n")
        pprint(api_response)
    except Exception as e:
        print("Exception when calling FileManagementApi->upload_file_fileman_data_upload_post: %s\n" % e)
```



### Parameters


Name | Type | Description  | Notes
------------- | ------------- | ------------- | -------------
 **file** | **bytearray**|  | 
 **storage_type** | **str**|  | 
 **database_name** | **str**|  | [optional] 
 **table_name** | **str**|  | [optional] 
 **knowledge_base** | **str**|  | [optional] 
 **sub_path** | **str**|  | [optional] 
 **base_path** | **str**|  | [optional] 

### Return type

[**UploadFileResponse**](UploadFileResponse.md)

### Authorization

[XAPIKeyAuth](../README.md#XAPIKeyAuth)

### HTTP request headers

 - **Content-Type**: multipart/form-data
 - **Accept**: application/json

### HTTP response details

| Status code | Description | Response headers |
|-------------|-------------|------------------|
**200** | Successful Response |  -  |
**401** | Unauthorized |  -  |
**400** | Bad Request |  -  |
**404** | Not Found |  -  |
**500** | Internal Server Error |  -  |
**422** | Validation Error |  -  |

[[Back to top]](#) [[Back to API list]](../README.md#documentation-for-api-endpoints) [[Back to Model list]](../README.md#documentation-for-models) [[Back to README]](../README.md)

