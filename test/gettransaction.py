import requests
import json

url = "https://eth-mainnet.g.alchemy.com/v2/cZczn1_aHhSTdTw5vYQb4oaZv9_K6672"

payload = {
    "id": 1,
    "jsonrpc": "2.0",
    "method": "eth_getBlockTransactionCountByHash",
    "params": ["0xe76d777791f48b5995d20789183514f4aa8bbf09e357383e9a44fae025c6c50a"]
}
headers = {
    "accept": "application/json",
    "content-type": "application/json"
}

response = requests.post(url, json=payload, headers=headers)

obj = json.loads(response.text)
 
json_formatted_str = json.dumps(obj, indent=2)
print(json_formatted_str)

with open("gettransaction.json", "w") as write_file:
    json.dump(json_formatted_str, write_file, indent=4)

