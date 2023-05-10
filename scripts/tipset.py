import requests
import json
from db import get_database_connection
import datetime

# Set up the endpoint URL
url = "https://filecoin.infura.io"
# Set up the HTTP headers with authentication
headers = {
        "Content-Type": "application/json",
        "Authorization": "Basic Mk02WGJHNndmWlN6akxlY2JiQkxab3dJNXBsOjlkMzBhMjAyYzgxYTlhOWM3NTQxMTMxZjJhY2U3ZTM2"
    }

# returns cids and blocks info for a certain height
def get_tipset_by_height(height):
    # Set up the  data payload
    data = {
        "id": 0,
        "jsonrpc": "2.0",
        "method": "Filecoin.ChainGetTipSetByHeight",
        "params": [height,None]
    }

    # print(json.dumps(data, indent=4))
    
    # Make the request using the requests library
    response = requests.post(url, headers=headers, json=data)

    # Check that the request was successful (status code 200)
    if response.status_code == 200:
        # Extract the desired part of the JSON data
        json_data = response.json()
        # print(f"Response for height {height}: {json.dumps(json_data, indent=4)}\n")

        if "result" in json_data:
            result = json_data["result"]

            cids = result["Cids"]
            blocks = result["Blocks"]
            
            # print(json.dumps(cids,indent=2))
            # print(json.dumps(blocks,indent=1))
            return cids, blocks
        else:
            print("Error: 'result' field not found in response")
    else:
        print("Error: Request failed with status code {}".format(response.status_code))

# inserts cid and block info into tipset datatable
def insert_tipset_block(cid,block):
    # print(f"CID: {cid}")
    # print(json.dumps(block, indent=4))
    cid = cid["/"]
    miner = block["Miner"]
    height = block["Height"]
    parentweight = block["ParentWeight"]
    messages = block["Messages"]["/"]
    timestamp = datetime.datetime.fromtimestamp(block["Timestamp"])
    # print(cid,miner,height,parentweight,messages,timestamp)

    # connect to db
    mydb = get_database_connection()
    mycursor = mydb.cursor()
    # prepare inset query
    insert_query = "INSERT INTO tipset (cid, miner, height, parent_weight, messages, timestamp) VALUES (%s, %s, %s, %s, %s, %s)"
    data = (cid, miner, height, parentweight, messages, timestamp)
    mycursor.execute(insert_query, data)
    # commit query and disconnect
    mydb.commit()
    mycursor.close()
    mydb.close()

# returns the height of last validated tipset
def find_latest_tipset():
    # Set up the  data payload
    data = {
        "id": 0,
        "jsonrpc": "2.0",
        "method": "Filecoin.ChainHead",
        "params": []
    }

    # print(json.dumps(data, indent=4))
    
    # Make the request using the requests library
    response = requests.post(url, headers=headers, json=data)

    # Check that the request was successful (status code 200)
    if response.status_code == 200:
        # Extract the desired part of the JSON data
        json_data = response.json()
        # print(f"Response: {json.dumps(json_data, indent=4)}\n")

        if "result" in json_data:
            result = json_data["result"]

            height = result["Height"]
            
            # print(json.dumps(height,indent=4))
            return height
        else:
            print("Error: 'result' field not found in response")
    else:
        print("Error: Request failed with status code {}".format(response.status_code))

# returns a list of heights between the latest height and largest height available in the tipset datatable
def get_missing_heights_from_tipset_table(latest_height):
    mydb = get_database_connection()
    mycursor = mydb.cursor()

    # Find the largest height in the tipset table
    select_query = "SELECT MAX(height) FROM tipset;"
    mycursor.execute(select_query)
    largest_height = mycursor.fetchone()[0]
    print(f"largest:{largest_height}")

    # Construct a list of heights from n down to the largest height
    heights = list(range(latest_height, largest_height, -1))

    return heights

# calls get_tipset_by_height and insert_tipset_block for a list of heights
def insert_missing_heights_from_tipset_table(missing_heights):
    for height in missing_heights:
        cids, blocks = get_tipset_by_height(height)
        for i in range(len(cids)):
            cid = cids[i]
            block = blocks[i]
            insert_tipset_block(cid, block)
        print(f"added height:{height}")

latest_height = find_latest_tipset()

print(f"latest:{latest_height}")

# Run this code when the tipset table is empty
# cids, blocks = get_tipset_by_height(latest_height-10)
# for i in range(len(cids)):
#     cid = cids[i]
#     block = blocks[i]
#     insert_tipset_block(cid, block)

missing_heights = get_missing_heights_from_tipset_table(latest_height)

print(f"missing:{missing_heights}")

insert_missing_heights_from_tipset_table(missing_heights)
