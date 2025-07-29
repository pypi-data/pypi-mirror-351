# MemberIn


## Properties
Name | Type | Description | Notes
------------ | ------------- | ------------- | -------------
**team_id** | **int** |  | 
**user_id** | **int** |  | 
**role** | [**Role**](Role.md) |  | 
**is_active** | **bool** |  | [optional] [default to False]

## Example

```python
from compute_api_client.models.member_in import MemberIn

# TODO update the JSON string below
json = "{}"
# create an instance of MemberIn from a JSON string
member_in_instance = MemberIn.from_json(json)
# print the JSON string representation of the object
print MemberIn.to_json()

# convert the object into a dict
member_in_dict = member_in_instance.to_dict()
# create an instance of MemberIn from a dict
member_in_form_dict = member_in.from_dict(member_in_dict)
```
[[Back to Model list]](../README.md#documentation-for-models) [[Back to API list]](../README.md#documentation-for-api-endpoints) [[Back to README]](../README.md)


