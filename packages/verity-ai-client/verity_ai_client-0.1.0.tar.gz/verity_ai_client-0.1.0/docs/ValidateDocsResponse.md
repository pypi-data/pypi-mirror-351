# ValidateDocsResponse


## Properties

Name | Type | Description | Notes
------------ | ------------- | ------------- | -------------
**results** | **Dict[str, bool]** | Mapping of document IDs to ingestion status | 

## Example

```python
from verity_ai_pyc.models.validate_docs_response import ValidateDocsResponse

# TODO update the JSON string below
json = "{}"
# create an instance of ValidateDocsResponse from a JSON string
validate_docs_response_instance = ValidateDocsResponse.from_json(json)
# print the JSON string representation of the object
print(ValidateDocsResponse.to_json())

# convert the object into a dict
validate_docs_response_dict = validate_docs_response_instance.to_dict()
# create an instance of ValidateDocsResponse from a dict
validate_docs_response_from_dict = ValidateDocsResponse.from_dict(validate_docs_response_dict)
```
[[Back to Model list]](../README.md#documentation-for-models) [[Back to API list]](../README.md#documentation-for-api-endpoints) [[Back to README]](../README.md)


