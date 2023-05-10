import requests
import json
from db import get_database_connection
import os

# Set up the endpoint URL
url = "https://filecoin.infura.io"
# Set up the HTTP headers with authentication
headers = {
        "Content-Type": "application/json",
        "Authorization": "Basic Mk02WGJHNndmWlN6akxlY2JiQkxab3dJNXBsOjlkMzBhMjAyYzgxYTlhOWM3NTQxMTMxZjJhY2U3ZTM2"
    }

# Gets the cids and height of the lastest block validated and 
# returns a tuple containting a list of cid and the height
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
            if "Cids" in result and "Height" in result:
                # Return the CID strings
                cids = result["Cids"]
                height = result["Height"]
                return cids, height
            else:
                print("Error: fields not found in response")
        else:
            print("Error: 'result' field not found in response")
    else:
        # Handle the error if the request was not successful
        print("Error: Request failed with status code {}".format(response.status_code))

# Connects to db, calls get_chain_head() and inserts the returned tuple into db
# Connects to the database and inserts the latest chain head data into the "cid" table
def update_db_chain_head():
    mydb = get_database_connection()
    mycursor = mydb.cursor()

    # Call the get_chain_head() function to retrieve the latest chain head data
    chain_head = get_chain_head()

    # If the chain head data was successfully retrieved
    if chain_head is not None:
        # Unpack the chain head data into separate variables
        cids, height = chain_head

        # For each CID in the list of CIDs
        for cid in cids:
            # Extract the CID string from the dictionary format
            cid = cid['/']

            # Define an SQL query to insert the CID and height data into the "cid" table
            insert_query = "INSERT INTO cid (cid, height) VALUES (%s, %s)"

            # Execute the insert query with the CID and height values as parameters
            mycursor.execute(insert_query, (str(cid), height))
    mydb.commit()
    mycursor.close()
    mydb.close()

# Connects to db, gets all cids from cid table and returns a list
def get_cid_from_db():
    mydb = get_database_connection()
    mycursor = mydb.cursor()

    select_query = "SELECT cid FROM cid"
    mycursor.execute(select_query)

    # Fetch all the rows of the query result
    rows = mycursor.fetchall()

    # Convert the rows to a list
    cids = [row[0] for row in rows]

    return cids

# Gets a list of cids or a single string of cid and resturns a list of
# varius information about each cid block
def get_blocks(cids):
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
                #print(f"Response for CID {cid}: {json.dumps(json_data, indent=4)}\n")
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
            #print(f"Response for CID {cid}: {json.dumps(json_data, indent=4)}\n")
            results.append(json_data)
        else:
            # Handle the error if the request was not successful
            print(f"Error: Request failed with status code {response.status_code} for CID {cid} with parameters {data}\n")
    else:
        print("Wrong cids format")
    return results

# for each cid, calls get_blocks and inserts various information
# if a block has multiple parents, muliple rows are inserted for the block cid
def update_db_get_blocks(cids):
    mydb = get_database_connection()
    mycursor = mydb.cursor()

    # for each cid, get block info and add it to db
    for cid in cids:
        # get block info for singular cid
        block_info = get_blocks(cid)

        # Access the values
        miner = block_info[0]['result']['Miner']
        height = block_info[0]['result']['Height']

        messages = block_info[0]['result']['Messages']
        messages = messages['/']
        # TODO: check see if a block can have multiple messages

        #get a list of all parents in the block
        parents = block_info[0]['result']['Parents']
        parent_values = []
        for parent in parents:
            value = parent['/']
            parent_values.append(value)

        # Insert the values into cid_info table
        insert_query = "INSERT INTO cid_info (cid, miner, height, messages, parent) VALUES (%s, %s, %s, %s, %s)"
        for parent_value in parent_values:
            data = (cid, miner, height, messages, parent_value)
            mycursor.execute(insert_query, data)
            # TODO: update the cid rows that have missing column values, 
            # right now we just insert so existing cids don't get updated
    mydb.commit()
    mycursor.close()
    mydb.close()

def traverse(cid,n):
    for i in range(0, n):
        # get info about current block
        block = get_blocks(cid)
        print(f"Response for CID {cid}: {json.dumps(block, indent=4)}\n")

        # get first parent
        parents = block[0]['result']['Parents']
        parent_cid = parents[0]['/']

        # update cid with parent cid for next iteration
        cid = parent_cid





# update db with latest block
# update_db_chain_head()

# get a list of all cids in cid table
# cids = get_cid_from_db()

# insert block info for all cids in cid table into cid_info table
# update_db_get_blocks(cids)

# traversing example
starting_cid = ['bafy2bzacea6wz43k7rgsq73ywqh42odimhprllm6u43v7jofq42z7ncokpqzc']
traverse(starting_cid,5)