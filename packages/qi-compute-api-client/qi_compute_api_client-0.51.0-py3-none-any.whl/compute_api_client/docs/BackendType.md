# BackendType


## Properties
Name | Type | Description | Notes
------------ | ------------- | ------------- | -------------
**id** | **int** |  | 
**name** | **str** |  | 
**infrastructure** | **str** |  | 
**description** | **str** |  | 
**image_id** | **str** |  | 
**is_hardware** | **bool** |  | 
**supports_raw_data** | **bool** |  | 
**features** | **List[str]** |  | 
**default_compiler_config** | **Dict[str, object]** |  | 
**gateset** | **List[str]** |  | 
**topology** | **List[List[int]]** |  | 
**nqubits** | **int** |  | 
**status** | [**BackendStatus**](BackendStatus.md) |  | 
**default_number_of_shots** | **int** |  | 
**max_number_of_shots** | **int** |  | 
**enabled** | **bool** |  | 

## Example

```python
from compute_api_client.models.backend_type import BackendType

# TODO update the JSON string below
json = "{}"
# create an instance of BackendType from a JSON string
backend_type_instance = BackendType.from_json(json)
# print the JSON string representation of the object
print BackendType.to_json()

# convert the object into a dict
backend_type_dict = backend_type_instance.to_dict()
# create an instance of BackendType from a dict
backend_type_form_dict = backend_type.from_dict(backend_type_dict)
```
[[Back to Model list]](../README.md#documentation-for-models) [[Back to API list]](../README.md#documentation-for-api-endpoints) [[Back to README]](../README.md)


