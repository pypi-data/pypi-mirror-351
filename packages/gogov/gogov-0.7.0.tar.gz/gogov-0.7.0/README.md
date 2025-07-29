# gogov
Unofficial API Client for GoGov CRM

## install
```sh
pip install gogov
```

## basic CLI usage
```sh
gogov export-requests --email="jdoe@fakecity.gov" --password="2c56477e97ab8b2d180a6513" --site="fakecityXYZ" --city-id="123" $PWD/requests.csv
```

## basic Python usage
```python
from gogov import Client

# client automatically logs in when initialized
client = Client(
    username = "jdoe",
    password = "2c56477e97ab8b2d180a6513",
    site = "fakecityXYZ",
    city_id = "123"
)

## download csv of all requests to a file
client.export_requests("requests.csv")

## Submit a 311 request
location = {
    "shortAddress": "123 Any Street, Anytown, TN, 12345",
    "coordinates": {
        "longitude": -12.345678
        "latitude": 87.654321
    }
}

# Use "fields" for any additional necessary fields
client.submit_request(
    topic_id="12345"
    location=location,
    description="Test"
    contact_id=1234567
    assigned_to_id=7654321
    fields = [{"id": "field1", "value": "value1"}, {"id": "field2", "value": "value2}]
)

## log out
client.logout()
```

## advanced usage
coming soon
