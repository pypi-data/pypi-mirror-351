# ChatCompletionResponse


## Properties

Name | Type | Description | Notes
------------ | ------------- | ------------- | -------------
**id** | **str** | Unique identifier for the response | 
**created** | **int** | Timestamp (Unix epoch) when the response was created | 
**model** | **str** | The model used to generate the response | 
**messages** | [**List[ChatCompletionMessage]**](ChatCompletionMessage.md) | A list of messages containing the model&#39;s response | 
**structured_data** | **List[Dict[str, object]]** | Raw structured output from the query | 
**sources** | **List[str]** | List of document sources utilized for the response | [optional] 
**usage** | [**Usage**](Usage.md) | Usage statistics for the response | 
**metadata** | **Dict[str, object]** |  | [optional] 
**llm_sql_generation** | **str** |  | [optional] 

## Example

```python
from verity_ai_pyc.models.chat_completion_response import ChatCompletionResponse

# TODO update the JSON string below
json = "{}"
# create an instance of ChatCompletionResponse from a JSON string
chat_completion_response_instance = ChatCompletionResponse.from_json(json)
# print the JSON string representation of the object
print(ChatCompletionResponse.to_json())

# convert the object into a dict
chat_completion_response_dict = chat_completion_response_instance.to_dict()
# create an instance of ChatCompletionResponse from a dict
chat_completion_response_from_dict = ChatCompletionResponse.from_dict(chat_completion_response_dict)
```
[[Back to Model list]](../README.md#documentation-for-models) [[Back to API list]](../README.md#documentation-for-api-endpoints) [[Back to README]](../README.md)


