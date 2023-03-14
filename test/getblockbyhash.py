import requests
import json

url = "https://eth-mainnet.g.alchemy.com/v2/cZczn1_aHhSTdTw5vYQb4oaZv9_K6672"

payload = {
    "id": 1,
    "jsonrpc": "2.0",
    "method": "eth_getBlockByHash",
    "params": ['0xe76d777791f48b5995d20789183514f4aa8bbf09e357383e9a44fae025c6c50a', False]
}
headers = {
    "accept": "application/json",
    "content-type": "application/json"
}

response = requests.post(url, json=payload, headers=headers)

# print(response.text)

obj = json.loads(response.text)
 
json_formatted_str = json.dumps(obj, indent=2)
print(json_formatted_str)

with open("getblockbyhash.json", "w") as write_file:
    json.dump(json_formatted_str, write_file, indent=4)

with open('getblockbyhash.json', 'r') as f:
    data = json.load(f)

if isinstance(data, dict):
    # Access a specific key in the dictionary
    my_variable = data['hash']
    print(my_variable)
else:
    # Handle the case where the JSON data isn't a dictionary
    print("JSON data isn't a dictionary")