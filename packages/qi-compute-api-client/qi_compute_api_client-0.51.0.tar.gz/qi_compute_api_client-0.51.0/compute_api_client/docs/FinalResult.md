# FinalResult


## Properties
Name | Type | Description | Notes
------------ | ------------- | ------------- | -------------
**id** | **int** |  | 
**created_on** | **datetime** |  | 
**job_id** | **int** |  | 
**final_result** | **Dict[str, object]** |  | 

## Example

```python
from compute_api_client.models.final_result import FinalResult

# TODO update the JSON string below
json = "{}"
# create an instance of FinalResult from a JSON string
final_result_instance = FinalResult.from_json(json)
# print the JSON string representation of the object
print FinalResult.to_json()

# convert the object into a dict
final_result_dict = final_result_instance.to_dict()
# create an instance of FinalResult from a dict
final_result_form_dict = final_result.from_dict(final_result_dict)
```
[[Back to Model list]](../README.md#documentation-for-models) [[Back to API list]](../README.md#documentation-for-api-endpoints) [[Back to README]](../README.md)


