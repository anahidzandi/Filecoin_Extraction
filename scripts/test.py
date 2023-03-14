import requests
import json
from db import get_database_connection

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
            if "Cids" in result and "Height" in result:
                # Return the CID strings
                cids = result["Cids"]
                height = result["Height"]
                return cids, height
            else:
                print("Error: 'Cids' field not found in response")
        else:
            print("Error: 'result' field not found in response")
    else:
        # Handle the error if the request was not successful
        print("Error: Request failed with status code {}".format(response.status_code))

def update_db_chain_head():
    mydb = get_database_connection()
    mycursor = mydb.cursor()

    chain_head = get_chain_head()

    if chain_head is not None:
        cids, height = chain_head
        for cid in cids:
            cid = cid['/']
            # print("CID:", cid)
            # print("Height:", height)

            insert_query = "INSERT INTO cid (cid, height) VALUES (%s, %s)"
            mycursor.execute(insert_query, (str(cid), height))

    mydb.commit()
    mycursor.close()
    mydb.close()

def get_cid_from_db():
    mydb = get_database_connection()
    mycursor = mydb.cursor()

    select_query = "SELECT cid FROM cid"
    mycursor.execute(select_query)

    # Fetch all the rows of the query result
    rows = mycursor.fetchall()

    # Convert the rows to a list
    cids = [row[0] for row in rows]

    # Print the resulting list
    # print(cids)

    return cids

def get_blocks(cids):
    results = []

    formatted_cids = [{'/': item} for item in cids]
    # print(formatted_cids)
    
    # Loop through each cid and call the "Filecoin.ChainGetBlock" method
    for cid in formatted_cids:
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
            #print(f"Response for CID {cid}: {json.dumps(json_data, indent=4)}\n")
            results.append(json_data)
        else:
            # Handle the error if the request was not successful
            print(f"Error: Request failed with status code {response.status_code} for CID {cid} with parameters {data}\n")
    return results

# Example usage

# chain_head = get_chain_head()
# print(chain_head)

# update db with latest
# update_db_chain_head()

cids = get_cid_from_db()
block_info = get_blocks(cids)

print(json.dumps(block_info, indent=4))
print(f"The number of blocks: {len(block_info)}")