import json
import os

import requests

api_key = os.environ["PRM_API_KEY"]

response = requests.get(
    "http://localhost:8000/api/v1/users", headers={"x-key": api_key}
)
print("users:", response.json())

with open("./tests/test_data/normalized/olympiad_selected.json", "r") as f:
    data = json.load(f)

for item in data:
    item["final_answer"] = {}

dataset = {
    "name": "Olympiad",
    "domain": "math",
    "description": "olympiadbench dataset",
    "problems": data,
}

response = requests.post(
    "http://localhost:8000/api/v1/datasets", headers={"x-key": api_key}, json=dataset
)
print("added dataset:", response.json())

annotation = {
    "step_labels": {0: "bad", 1: "good"},
    "complete": False,
    "problem_id": 1000000000,
}

response = requests.post(
    "http://localhost:8000/api/v1/annotations",
    headers={"x-key": api_key},
    json=annotation,
)
print("added annotation:", response.json())
