# UserDetailsRequest


## Properties

Name | Type | Description | Notes
------------ | ------------- | ------------- | -------------
**organization_name** | **str** |  | 
**industry** | **str** |  | 
**use_case** | **str** |  | 

## Example

```python
from verity_ai_pyc.models.user_details_request import UserDetailsRequest

# TODO update the JSON string below
json = "{}"
# create an instance of UserDetailsRequest from a JSON string
user_details_request_instance = UserDetailsRequest.from_json(json)
# print the JSON string representation of the object
print(UserDetailsRequest.to_json())

# convert the object into a dict
user_details_request_dict = user_details_request_instance.to_dict()
# create an instance of UserDetailsRequest from a dict
user_details_request_from_dict = UserDetailsRequest.from_dict(user_details_request_dict)
```
[[Back to Model list]](../README.md#documentation-for-models) [[Back to API list]](../README.md#documentation-for-api-endpoints) [[Back to README]](../README.md)


