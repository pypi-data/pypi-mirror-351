# AgentCreatePublic

Public model for creating a new agent

## Properties

Name | Type | Description | Notes
------------ | ------------- | ------------- | -------------
**name** | **str** | Name of the agent | 
**description** | **str** |  | [optional] 
**model** | **str** | LLM model identifier (e.g., &#39;anthropic_claude_3_5_sonnet_v1&#39;) | [optional] [default to 'anthropic_claude_3_5_sonnet_v1']
**custom_prompt** | **str** |  | [optional] 
**allowed_tools** | **List[Optional[str]]** | List of tool names the agent is allowed to use | [optional] 
**use_mcp** | **bool** | Whether to enable MCP (Model Context Protocol) integration | [optional] [default to False]
**mcp_server_urls** | **List[Optional[str]]** | List of MCP server URLs | [optional] 
**agent_strategy** | **str** | Reasoning strategy (&#39;react&#39;, &#39;cot&#39;, etc.) | [optional] [default to 'react']
**stream** | **bool** | Whether to enable streaming responses by default | [optional] [default to False]
**active** | **bool** | Whether the agent is active and available for use | [optional] [default to True]

## Example

```python
from verity_ai_pyc.models.agent_create_public import AgentCreatePublic

# TODO update the JSON string below
json = "{}"
# create an instance of AgentCreatePublic from a JSON string
agent_create_public_instance = AgentCreatePublic.from_json(json)
# print the JSON string representation of the object
print(AgentCreatePublic.to_json())

# convert the object into a dict
agent_create_public_dict = agent_create_public_instance.to_dict()
# create an instance of AgentCreatePublic from a dict
agent_create_public_from_dict = AgentCreatePublic.from_dict(agent_create_public_dict)
```
[[Back to Model list]](../README.md#documentation-for-models) [[Back to API list]](../README.md#documentation-for-api-endpoints) [[Back to README]](../README.md)


