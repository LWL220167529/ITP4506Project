import json

# create a dictionary to be written to the JSON file
data = {
    "name": "John",
    "age": 30,
    "city": "New York"
}

# open a file for writing
with open('food.json', 'w') as f:
    # write the dictionary to the file in JSON format
    json.dump(data, f)
