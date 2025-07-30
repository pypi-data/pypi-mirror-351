# ListFilesPagination


## Properties

Name | Type | Description | Notes
------------ | ------------- | ------------- | -------------
**current_page** | **int** |  | 
**total_pages** | **int** |  | 
**is_truncated** | **bool** |  | 
**next_token** | [**NextToken**](NextToken.md) |  | [optional] 

## Example

```python
from verity_ai_pyc.models.list_files_pagination import ListFilesPagination

# TODO update the JSON string below
json = "{}"
# create an instance of ListFilesPagination from a JSON string
list_files_pagination_instance = ListFilesPagination.from_json(json)
# print the JSON string representation of the object
print(ListFilesPagination.to_json())

# convert the object into a dict
list_files_pagination_dict = list_files_pagination_instance.to_dict()
# create an instance of ListFilesPagination from a dict
list_files_pagination_from_dict = ListFilesPagination.from_dict(list_files_pagination_dict)
```
[[Back to Model list]](../README.md#documentation-for-models) [[Back to API list]](../README.md#documentation-for-api-endpoints) [[Back to README]](../README.md)


