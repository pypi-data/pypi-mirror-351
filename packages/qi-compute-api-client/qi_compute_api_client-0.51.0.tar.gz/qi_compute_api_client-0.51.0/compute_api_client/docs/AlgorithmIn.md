# AlgorithmIn


## Properties
Name | Type | Description | Notes
------------ | ------------- | ------------- | -------------
**project_id** | **int** |  | 
**type** | [**AlgorithmType**](AlgorithmType.md) |  | 
**shared** | [**ShareType**](ShareType.md) |  | 
**link** | **str** |  | [optional] 
**name** | **str** |  | 

## Example

```python
from compute_api_client.models.algorithm_in import AlgorithmIn

# TODO update the JSON string below
json = "{}"
# create an instance of AlgorithmIn from a JSON string
algorithm_in_instance = AlgorithmIn.from_json(json)
# print the JSON string representation of the object
print AlgorithmIn.to_json()

# convert the object into a dict
algorithm_in_dict = algorithm_in_instance.to_dict()
# create an instance of AlgorithmIn from a dict
algorithm_in_form_dict = algorithm_in.from_dict(algorithm_in_dict)
```
[[Back to Model list]](../README.md#documentation-for-models) [[Back to API list]](../README.md#documentation-for-api-endpoints) [[Back to README]](../README.md)


