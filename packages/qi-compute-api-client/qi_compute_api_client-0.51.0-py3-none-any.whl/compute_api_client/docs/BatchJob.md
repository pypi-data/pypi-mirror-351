# BatchJob


## Properties
Name | Type | Description | Notes
------------ | ------------- | ------------- | -------------
**id** | **int** |  | 
**created_on** | **datetime** |  | 
**status** | [**BatchJobStatus**](BatchJobStatus.md) |  | 
**user_id** | **int** |  | 
**backend_type_id** | **int** |  | 
**backend_id** | **int** |  | 
**queued_at** | **datetime** |  | 
**reserved_at** | **datetime** |  | 
**finished_at** | **datetime** |  | 
**job_ids** | **List[int]** |  | 
**aggregated_algorithm_type** | [**AlgorithmType**](AlgorithmType.md) |  | 

## Example

```python
from compute_api_client.models.batch_job import BatchJob

# TODO update the JSON string below
json = "{}"
# create an instance of BatchJob from a JSON string
batch_job_instance = BatchJob.from_json(json)
# print the JSON string representation of the object
print BatchJob.to_json()

# convert the object into a dict
batch_job_dict = batch_job_instance.to_dict()
# create an instance of BatchJob from a dict
batch_job_form_dict = batch_job.from_dict(batch_job_dict)
```
[[Back to Model list]](../README.md#documentation-for-models) [[Back to API list]](../README.md#documentation-for-api-endpoints) [[Back to README]](../README.md)


