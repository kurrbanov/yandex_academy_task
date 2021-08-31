import json

import requests as req

base = 'http://127.0.0.1:8000/'
headers = {
    'Content-Type': 'application/json'
}

body = {
    "data": [
        {
            "courier_id": 1,
            "courier_type": "foot",
            "regions": [1, 12, 22],
            "working_hours": ["00:00-23:59"]
        },
        {
            "courier_id": 2,
            "courier_type": "fool",
            "regions": [1, 12, 22],
            "working_hours": ["00:00-23:59"]
        }
    ]
}

response = req.post(base + 'couriers', data=json.dumps(body), headers=headers)
print(response.text)

response = req.get(base + 'couriers')
print(response.text)

body = {
    "data": [
        {
            "order_id": 1,
            "weight": 1,
            "region": 16,
            "delivery_hours": ["09:00-12:00", "16:00-21:30"]
        },
{
            "order_id": 2,
            "weight": 0.001,
            "region": 16,
            "delivery_hours": ["09:00-12:00", "16:00-21:30"]
        },
{
            "order_id": 3,
            "weight": 1,
            "region": 16,
            "delivery_hours": []
        }
    ]
}

response = req.post(base + 'orders', data=json.dumps(body), headers=headers)
print(response.text)

response = req.get(base + 'orders')
print(response.text)
