# Job


## Properties
Name | Type | Description | Notes
------------ | ------------- | ------------- | -------------
**id** | **int** |  | 
**created_on** | **datetime** |  | 
**file_id** | **int** |  | 
**algorithm_type** | [**AlgorithmType**](AlgorithmType.md) |  | 
**status** | [**JobStatus**](JobStatus.md) |  | 
**batch_job_id** | **int** |  | 
**queued_at** | **datetime** |  | 
**finished_at** | **datetime** |  | 
**number_of_shots** | **int** |  | 
**raw_data_enabled** | **bool** |  | 
**session_id** | **str** |  | 
**trace_id** | **str** |  | 
**message** | **str** |  | 
**source** | **str** | The source application of an exception that caused a job to fail (if applicable). | [optional] [default to '']

## Example

```python
from compute_api_client.models.job import Job

# TODO update the JSON string below
json = "{}"
# create an instance of Job from a JSON string
job_instance = Job.from_json(json)
# print the JSON string representation of the object
print Job.to_json()

# convert the object into a dict
job_dict = job_instance.to_dict()
# create an instance of Job from a dict
job_form_dict = job.from_dict(job_dict)
```
[[Back to Model list]](../README.md#documentation-for-models) [[Back to API list]](../README.md#documentation-for-api-endpoints) [[Back to README]](../README.md)


