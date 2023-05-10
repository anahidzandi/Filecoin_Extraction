import requests
import json
from db import get_database_connection
import datetime
from decimal import Decimal

# Set up the endpoint URL
url = "https://filecoin.infura.io"
# Set up the HTTP headers with authentication
headers = {
        "Content-Type": "application/json",
        "Authorization": "Basic Mk02WGJHNndmWlN6akxlY2JiQkxab3dJNXBsOjlkMzBhMjAyYzgxYTlhOWM3NTQxMTMxZjJhY2U3ZTM2"
    }

# returns a list of cids available in block table that are not in block_messages table
def get_cids_from_block_table():
    mydb = get_database_connection()
    mycursor = mydb.cursor()

    # gets a list of cids in block table that are not included in block_messages table
    select_query = "SELECT filecoin.block.cid FROM filecoin.block LEFT JOIN filecoin.block_messages ON filecoin.block.cid = filecoin.block_messages.cid WHERE filecoin.block_messages.cid IS NULL;"
    mycursor.execute(select_query)

    # Fetch all the rows of the query result
    rows = mycursor.fetchall()

    # Convert the rows to a list
    cids = [row[0] for row in rows]
    # print(cids)
    print(f"\nNumber of cids returned from the block table: {len(cids)}")

    return cids

# returns a list of cids and their messages
def get_messages_for_cids(cids):
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
                "method": "Filecoin.ChainGetBlockMessages",
                "params": [cid]
            }

            # Make the request using the requests library
            response = requests.post(url, headers=headers, json=data)

            # Check that the request was successful (status code 200)
            if response.status_code == 200:
                # Extract the desired part of the JSON data
                json_data = response.json()
                # print(f"Response for CID {cid}: {json.dumps(json_data, indent=4)}\n")
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
                "method": "Filecoin.ChainGetBlockMessages",
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

    # some of the results from rpc call have errors, so we only return thoes who don't raise errors
    # although, this error doesn't happen sometimes with the cids that previously raised errors
    filtered_cids = []
    filtered_results = []
    error_cids = []
    # Loop through the cids and corresponding results and print them
    for cid, info in zip(cids, results):
        if "error" not in info:
            # print(f"CID: {cid}")
            # print(json.dumps(info, indent=4))
            filtered_cids.append(cid)
            filtered_results.append(info)
        else:
            error_cids.append(cid)
    
    print(f"\nNumber of filtered cids: {len(filtered_cids)}")

    if len(error_cids) > 0:
        print(f"\nNumber of error cids: {len(error_cids)}")
    #     print(f"Error cids: {error_cids}")

    return filtered_cids, filtered_results

# inserts the cid and messages into the block_messages table
def insert_block_messages(cid,messages):
    # print(f"CID: {cid}")
    # print(json.dumps(messages, indent=4))

    # if the cid block has no messages
    if messages["result"]["BlsMessages"] == [] and messages["result"]["SecpkMessages"] == []:
        message_id = None
        to_miner = None
        from_miner = None
        nonc = None
        value = None
        # print(f"empty message_id: {message_id}, to_miner: {to_miner}, from_miner: {from_miner}, nonc: {nonc}, value: {value}")
    # else the cid block has messages
    else:
        # connect to db
        mydb = get_database_connection()
        mycursor = mydb.cursor()

        #BlsMessages part
        for msg in messages["result"]["BlsMessages"]:
            message_id = msg["CID"]["/"]
            to_miner = msg["To"]
            from_miner = msg["From"]
            nonc = msg["Nonce"]
            value = int(msg["Value"]) / (10 ** 18) # to get value in FIL

            # print the values for this message
            # print(f" Bls message_id: {message_id}, to_miner: {to_miner}, from_miner: {from_miner}, nonc: {nonc}, value: {value}")

            # prepare inset query
            insert_query = "INSERT INTO block_messages (messages_cid, to_miner, from_miner, nonc, value, cid) VALUES (%s, %s, %s, %s, %s, %s)"
            data = (message_id,to_miner,from_miner,nonc,value,cid)
            mycursor.execute(insert_query, data)
            print(f"CID: {cid} with message id: {message_id} inserted")

        #SecpkMessages part
        for msg in messages["result"]["SecpkMessages"]:
            message_id = msg["CID"]["/"]
            to_miner = msg["Message"]["To"]
            from_miner = msg["Message"]["From"]
            nonc = msg["Message"]["Nonce"]
            value = int(msg["Message"]["Value"]) / (10 ** 18) # to get value in FIL

            
            # print the values for this message
            # print(f"Secpk message_id: {message_id}, to_miner: {to_miner}, from_miner: {from_miner}, nonc: {nonc}, value: {value}")

            # prepare inset query
            insert_query = "INSERT INTO block_messages (messages_cid, to_miner, from_miner, nonc, value, cid) VALUES (%s, %s, %s, %s, %s, %s)"
            data = (message_id,to_miner,from_miner,nonc,value,cid)
            mycursor.execute(insert_query, data)
            print(f"CID: {cid} with message id: {message_id} inserted")

        # commit query and disconnect
        mydb.commit()
        mycursor.close()
        mydb.close()

cids = get_cids_from_block_table()

fetched_cids, messages = get_messages_for_cids(cids)

for i in range(len(fetched_cids)):
    cid = fetched_cids[i]
    message = messages[i]
    insert_block_messages(cid, message)