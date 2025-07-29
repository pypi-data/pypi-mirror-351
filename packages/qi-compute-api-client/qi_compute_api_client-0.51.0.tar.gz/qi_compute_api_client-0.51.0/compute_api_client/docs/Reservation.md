# Reservation


## Properties
Name | Type | Description | Notes
------------ | ------------- | ------------- | -------------
**id** | **int** |  | 
**member_id** | **int** |  | 
**start_time** | **datetime** |  | 
**end_time** | **datetime** |  | 
**backend_type_id** | **int** |  | 
**backend_id** | **int** |  | 
**is_terminated** | **bool** |  | 

## Example

```python
from compute_api_client.models.reservation import Reservation

# TODO update the JSON string below
json = "{}"
# create an instance of Reservation from a JSON string
reservation_instance = Reservation.from_json(json)
# print the JSON string representation of the object
print Reservation.to_json()

# convert the object into a dict
reservation_dict = reservation_instance.to_dict()
# create an instance of Reservation from a dict
reservation_form_dict = reservation.from_dict(reservation_dict)
```
[[Back to Model list]](../README.md#documentation-for-models) [[Back to API list]](../README.md#documentation-for-api-endpoints) [[Back to README]](../README.md)


