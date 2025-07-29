# ResultIn


## Properties
Name | Type | Description | Notes
------------ | ------------- | ------------- | -------------
**job_id** | **int** |  | 
**execution_time_in_seconds** | **float** |  | 
**shots_requested** | **int** |  | [optional] 
**shots_done** | **int** |  | [optional] 
**results** | **Dict[str, object]** |  | [optional] 
**raw_data** | **List[str]** |  | [optional] 

## Example

```python
from compute_api_client.models.result_in import ResultIn

# TODO update the JSON string below
json = "{}"
# create an instance of ResultIn from a JSON string
result_in_instance = ResultIn.from_json(json)
# print the JSON string representation of the object
print ResultIn.to_json()

# convert the object into a dict
result_in_dict = result_in_instance.to_dict()
# create an instance of ResultIn from a dict
result_in_form_dict = result_in.from_dict(result_in_dict)
```
[[Back to Model list]](../README.md#documentation-for-models) [[Back to API list]](../README.md#documentation-for-api-endpoints) [[Back to README]](../README.md)


