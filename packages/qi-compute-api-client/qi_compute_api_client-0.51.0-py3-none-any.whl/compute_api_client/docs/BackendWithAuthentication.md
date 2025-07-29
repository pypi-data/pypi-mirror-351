# BackendWithAuthentication


## Properties
Name | Type | Description | Notes
------------ | ------------- | ------------- | -------------
**id** | **int** |  | 
**name** | **str** |  | 
**location** | **str** |  | 
**backend_type_id** | **int** |  | 
**status** | [**BackendStatus**](BackendStatus.md) |  | 
**last_heartbeat** | **datetime** |  | 
**authentication_hash** | **str** |  | 

## Example

```python
from compute_api_client.models.backend_with_authentication import BackendWithAuthentication

# TODO update the JSON string below
json = "{}"
# create an instance of BackendWithAuthentication from a JSON string
backend_with_authentication_instance = BackendWithAuthentication.from_json(json)
# print the JSON string representation of the object
print BackendWithAuthentication.to_json()

# convert the object into a dict
backend_with_authentication_dict = backend_with_authentication_instance.to_dict()
# create an instance of BackendWithAuthentication from a dict
backend_with_authentication_form_dict = backend_with_authentication.from_dict(backend_with_authentication_dict)
```
[[Back to Model list]](../README.md#documentation-for-models) [[Back to API list]](../README.md#documentation-for-api-endpoints) [[Back to README]](../README.md)


