# BackendIn


## Properties
Name | Type | Description | Notes
------------ | ------------- | ------------- | -------------
**name** | **str** |  | 
**location** | **str** |  | 
**backend_type_id** | **int** |  | 
**status** | [**BackendStatus**](BackendStatus.md) |  | 
**last_heartbeat** | **datetime** |  | 

## Example

```python
from compute_api_client.models.backend_in import BackendIn

# TODO update the JSON string below
json = "{}"
# create an instance of BackendIn from a JSON string
backend_in_instance = BackendIn.from_json(json)
# print the JSON string representation of the object
print BackendIn.to_json()

# convert the object into a dict
backend_in_dict = backend_in_instance.to_dict()
# create an instance of BackendIn from a dict
backend_in_form_dict = backend_in.from_dict(backend_in_dict)
```
[[Back to Model list]](../README.md#documentation-for-models) [[Back to API list]](../README.md#documentation-for-api-endpoints) [[Back to README]](../README.md)


