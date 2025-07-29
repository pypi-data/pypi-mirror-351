# JobIn


## Properties
Name | Type | Description | Notes
------------ | ------------- | ------------- | -------------
**file_id** | **int** |  | 
**batch_job_id** | **int** |  | 
**number_of_shots** | **int** |  | [optional] 
**raw_data_enabled** | **bool** |  | [optional] [default to False]

## Example

```python
from compute_api_client.models.job_in import JobIn

# TODO update the JSON string below
json = "{}"
# create an instance of JobIn from a JSON string
job_in_instance = JobIn.from_json(json)
# print the JSON string representation of the object
print JobIn.to_json()

# convert the object into a dict
job_in_dict = job_in_instance.to_dict()
# create an instance of JobIn from a dict
job_in_form_dict = job_in.from_dict(job_in_dict)
```
[[Back to Model list]](../README.md#documentation-for-models) [[Back to API list]](../README.md#documentation-for-api-endpoints) [[Back to README]](../README.md)


