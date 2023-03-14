import requests
import json
# Set up the endpoint URL
url = "https://filecoin.infura.io"
# Set up the HTTP headers with authentication
headers = {
        "Content-Type": "application/json",
        "Authorization": "Basic Mk02WGJHNndmWlN6akxlY2JiQkxab3dJNXBsOjlkMzBhMjAyYzgxYTlhOWM3NTQxMTMxZjJhY2U3ZTM2"
    }

def get_chain_head():
    # Set up the  data payload
    data = {
        "id": 0,
        "jsonrpc": "2.0",
        "method": "Filecoin.ChainHead",
        "params": []
    }
    
    # Make the request using the requests library
    response = requests.post(url, headers=headers, json=data)

    # Check that the request was successful (status code 200)
    if response.status_code == 200:
        # Extract the desired part of the JSON data
        json_data = response.json()

        # Check if the "result" field exists
        if "result" in json_data:
            result = json_data["result"]

            # Check if the "Cids" field exists in the result
            if "Cids" in result:
                # Return the CID strings
                cids = result["Cids"]
                return cids
            else:
                print("Error: 'Cids' field not found in response")
        else:
            print("Error: 'result' field not found in response")
    else:
        # Handle the error if the request was not successful
        print("Error: Request failed with status code {}".format(response.status_code))

def get_blocks(cids):
    # Loop through each cid and call the "Filecoin.ChainGetBlock" method
    for cid in cids:
        data = {
            "id": 1,
            "jsonrpc": "2.0",
            "method": "Filecoin.ChainGetBlock",
            "params": [cid]
        }

        #print(f"The request sent: {data}\n")

        # Make the request using the requests library
        response = requests.post(url, headers=headers, json=data)

        # Check that the request was successful (status code 200)
        if response.status_code == 200:
            # Extract the desired part of the JSON data
            json_data = response.json()
            print(f"Response for CID {cid}: {json.dumps(json_data, indent=4)}\n")
        else:
            # Handle the error if the request was not successful
            print(f"Error: Request failed with status code {response.status_code} for CID {cid}\n")

# Example usage
chain_head_cids = get_chain_head()
#print(chain_head_cids)

get_blocks(chain_head_cids)