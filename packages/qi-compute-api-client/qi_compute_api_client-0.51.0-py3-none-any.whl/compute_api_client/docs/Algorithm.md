# Algorithm


## Properties
Name | Type | Description | Notes
------------ | ------------- | ------------- | -------------
**id** | **int** |  | 
**project_id** | **int** |  | 
**type** | [**AlgorithmType**](AlgorithmType.md) |  | 
**shared** | [**ShareType**](ShareType.md) |  | 
**link** | **str** |  | 
**name** | **str** |  | 

## Example

```python
from compute_api_client.models.algorithm import Algorithm

# TODO update the JSON string below
json = "{}"
# create an instance of Algorithm from a JSON string
algorithm_instance = Algorithm.from_json(json)
# print the JSON string representation of the object
print Algorithm.to_json()

# convert the object into a dict
algorithm_dict = algorithm_instance.to_dict()
# create an instance of Algorithm from a dict
algorithm_form_dict = algorithm.from_dict(algorithm_dict)
```
[[Back to Model list]](../README.md#documentation-for-models) [[Back to API list]](../README.md#documentation-for-api-endpoints) [[Back to README]](../README.md)


