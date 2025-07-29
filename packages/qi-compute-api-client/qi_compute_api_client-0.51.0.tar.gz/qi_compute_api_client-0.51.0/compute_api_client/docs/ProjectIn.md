# ProjectIn


## Properties
Name | Type | Description | Notes
------------ | ------------- | ------------- | -------------
**owner_id** | **int** |  | 
**name** | **str** |  | 
**description** | **str** |  | 
**starred** | **bool** |  | [optional] [default to False]

## Example

```python
from compute_api_client.models.project_in import ProjectIn

# TODO update the JSON string below
json = "{}"
# create an instance of ProjectIn from a JSON string
project_in_instance = ProjectIn.from_json(json)
# print the JSON string representation of the object
print ProjectIn.to_json()

# convert the object into a dict
project_in_dict = project_in_instance.to_dict()
# create an instance of ProjectIn from a dict
project_in_form_dict = project_in.from_dict(project_in_dict)
```
[[Back to Model list]](../README.md#documentation-for-models) [[Back to API list]](../README.md#documentation-for-api-endpoints) [[Back to README]](../README.md)


