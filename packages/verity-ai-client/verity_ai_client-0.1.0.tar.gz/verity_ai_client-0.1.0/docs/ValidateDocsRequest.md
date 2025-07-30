# ValidateDocsRequest


## Properties

Name | Type | Description | Notes
------------ | ------------- | ------------- | -------------
**document_ids** | **List[str]** | List of document IDs to validate ingestion | 
**knowledge_base** | **str** |  | [optional] 

## Example

```python
from verity_ai_pyc.models.validate_docs_request import ValidateDocsRequest

# TODO update the JSON string below
json = "{}"
# create an instance of ValidateDocsRequest from a JSON string
validate_docs_request_instance = ValidateDocsRequest.from_json(json)
# print the JSON string representation of the object
print(ValidateDocsRequest.to_json())

# convert the object into a dict
validate_docs_request_dict = validate_docs_request_instance.to_dict()
# create an instance of ValidateDocsRequest from a dict
validate_docs_request_from_dict = ValidateDocsRequest.from_dict(validate_docs_request_dict)
```
[[Back to Model list]](../README.md#documentation-for-models) [[Back to API list]](../README.md#documentation-for-api-endpoints) [[Back to README]](../README.md)


