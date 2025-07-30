# ChatCompletionMessage


## Properties

Name | Type | Description | Notes
------------ | ------------- | ------------- | -------------
**role** | **str** | Role of the message (always &#39;assistant&#39; in response) | 
**content** | **str** | Generated message content | 
**metadata** | **Dict[str, object]** |  | [optional] 

## Example

```python
from verity_ai_pyc.models.chat_completion_message import ChatCompletionMessage

# TODO update the JSON string below
json = "{}"
# create an instance of ChatCompletionMessage from a JSON string
chat_completion_message_instance = ChatCompletionMessage.from_json(json)
# print the JSON string representation of the object
print(ChatCompletionMessage.to_json())

# convert the object into a dict
chat_completion_message_dict = chat_completion_message_instance.to_dict()
# create an instance of ChatCompletionMessage from a dict
chat_completion_message_from_dict = ChatCompletionMessage.from_dict(chat_completion_message_dict)
```
[[Back to Model list]](../README.md#documentation-for-models) [[Back to API list]](../README.md#documentation-for-api-endpoints) [[Back to README]](../README.md)


