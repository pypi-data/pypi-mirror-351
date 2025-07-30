# ChatCompletionRequestPublic


## Properties

Name | Type | Description | Notes
------------ | ------------- | ------------- | -------------
**data_type** | **str** | Unstructured or structured data type | [optional] 
**agent_flag** | **bool** |  | [optional] 
**agent_name** | **str** |  | [optional] 
**agent_strategy** | **str** |  | [optional] 
**agent_history_enabled** | **bool** |  | [optional] 
**model** | **str** | Model ID | [optional] 
**knowledge_base** | **str** |  | [optional] 
**messages** | [**List[Message]**](Message.md) | List of conversation messages | 
**database_name** | **str** |  | [optional] 
**table_name** | **str** |  | [optional] 
**stream** | **bool** |  | [optional] 
**max_trials** | **int** |  | [optional] 

## Example

```python
from verity_ai_pyc.models.chat_completion_request_public import ChatCompletionRequestPublic

# TODO update the JSON string below
json = "{}"
# create an instance of ChatCompletionRequestPublic from a JSON string
chat_completion_request_public_instance = ChatCompletionRequestPublic.from_json(json)
# print the JSON string representation of the object
print(ChatCompletionRequestPublic.to_json())

# convert the object into a dict
chat_completion_request_public_dict = chat_completion_request_public_instance.to_dict()
# create an instance of ChatCompletionRequestPublic from a dict
chat_completion_request_public_from_dict = ChatCompletionRequestPublic.from_dict(chat_completion_request_public_dict)
```
[[Back to Model list]](../README.md#documentation-for-models) [[Back to API list]](../README.md#documentation-for-api-endpoints) [[Back to README]](../README.md)


