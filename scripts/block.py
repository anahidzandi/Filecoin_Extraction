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

# returns a list of cids available in tipset table that are not in block table
def get_cids_from_tipset_table():
    mydb = get_database_connection()
    mycursor = mydb.cursor()

    # gets a list of cids in tipset table that are not included in block table
    select_query = "SELECT filecoin.tipset.cid FROM filecoin.tipset LEFT JOIN filecoin.block ON filecoin.tipset.cid = filecoin.block.cid WHERE filecoin.block.cid IS NULL;"
    mycursor.execute(select_query)

    # Fetch all the rows of the query result
    rows = mycursor.fetchall()

    # Convert the rows to a list
    cids = [row[0] for row in rows]
    # print(cids)

    return cids

# returns a list of cids and their corresponding block info
def get_block_info_for_cids(cids):
    results = []
    
    #check is cids is a list of cid or just a single string of cid
    if isinstance(cids, list):
        # format the cids list so it can be inserted correctly into
        # the data payload
        formatted_cids = [{'/': item} for item in cids]
        for cid in formatted_cids:
            # Set up the  data payload
            data = {
                "id": 1,
                "jsonrpc": "2.0",
                "method": "Filecoin.ChainGetBlock",
                "params": [cid]
            }

            # Make the request using the requests library
            response = requests.post(url, headers=headers, json=data)

            # Check that the request was successful (status code 200)
            if response.status_code == 200:
                # Extract the desired part of the JSON data
                json_data = response.json()
                print(f"Retrieved info for CID: {cid}\n")
                results.append(json_data)
            else:
                # Handle the error if the request was not successful
                print(f"Error: Request failed with status code {response.status_code} for CID {cid} with parameters {data}\n")
    elif isinstance(cids, str):
        # format the cids string so it can be inserted correctly into
        # the data payload
        cid = {"/": cids}
        # Set up the  data payload
        data = {
                "id": 1,
                "jsonrpc": "2.0",
                "method": "Filecoin.ChainGetBlock",
                "params": [cid]
            }

        # Make the request using the requests library
        response = requests.post(url, headers=headers, json=data)

        # Check that the request was successful (status code 200)
        if response.status_code == 200:
            # Extract the desired part of the JSON data
            json_data = response.json()
            print(f"Retrieved info for CID: {cid}\n")
            results.append(json_data)
        else:
            # Handle the error if the request was not successful
            print(f"Error: Request failed with status code {response.status_code} for CID {cid} with parameters {data}\n")
    else:
        print("Wrong cids format")

    # Loop through the cids and corresponding results and print them
    # for cid, info in zip(cids, results):
    #     print(f"CID: {cid}")
    #     print(json.dumps(info, indent=4))
    return cids, results

# inserts the cid and block info into the block table
def insert_block(cid,block):
    # print(f"CID: {cid}")
    # print(json.dumps(block, indent=4))
    miner = block["result"]["Miner"]
    parentweight = block["result"]["ParentWeight"]
    parentstateroot = block["result"]["ParentStateRoot"]["/"]
    height = block["result"]["Height"]
    parentmessagereceipts = block["result"]["ParentMessageReceipts"]["/"]
    messages = block["result"]["Messages"]["/"]
    timestamp = datetime.datetime.fromtimestamp(block["result"]["Timestamp"])
    # print(cid,miner,parentweight,parentstateroot,height,parentmessagereceipts,messages,timestamp)

    # connect to db
    mydb = get_database_connection()
    mycursor = mydb.cursor()
    # prepare inset query
    insert_query = "INSERT INTO block (cid, miner, parent_weight, parent_stateroot, height, parent_message_recipt, messages, timestamp) VALUES (%s, %s, %s, %s, %s, %s, %s, %s)"
    data = (cid,miner,parentweight,parentstateroot,height,parentmessagereceipts,messages,timestamp)
    mycursor.execute(insert_query, data)
    # commit query and disconnect
    mydb.commit()
    mycursor.close()
    mydb.close()

cids = get_cids_from_tipset_table()
print(cids)
fetched_cids, blocks= get_block_info_for_cids(cids)

for i in range(len(fetched_cids)):
    cid = fetched_cids[i]
    block = blocks[i]
    insert_block(cid, block)
    print(f"Inserted CID: {cid}")