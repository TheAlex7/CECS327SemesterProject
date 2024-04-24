# Name(s) : Alex Lopez, Anthony Tran, Glen Lee

import sys
import os
import time
import json
import jsonschema
import uuid
from jsonschema import validate

def writetojson(data, schema):
    uuid = str(uuid.uuid4())
    try:
        validate(instance=data, schema=schema)
    except jsonschema.exceptions.ValidationError as e:
        print("Data validation failed:", e)
    else:
        with open(f'./data/{data["name"]}{uuid}', 'w') as json_file:
            json.dump(data, json_file, indent=4)
        print(f"Data has been successfully written to '{data["name"]}{uuid}.json' ")



def main():
    # Load JSON Schema
    with open('./data/food_recipe_schema.json', 'r') as schema_file:
        schema = json.load(schema_file)
        
    # Retrieve NODE_ID environment variable to identify the node
    node_id = os.getenv('NODE_ID')
    print(f'STARTING UP NODE {node_id}')

if __name__ == "__main__":
    main()
