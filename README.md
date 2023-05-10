# FileCoin Extraction Research

## Project Description

This is the project that I worked on for my capstone internship. The goal of this project was to research Filecoin blockchain and implement a data pipeline to extract and transform data from the Filecoin blockchain, and persist it to a database for further analysis.

## Features

- Leveraged Infura's  Filecoin RPC calls to retrieve blockchain data and metadata
- Developed custom parsers to extract and process the retrieved JSON data
- Designed and implemented a  Mysql database schema to store information about Filecoin's tipsets, blocks, and messages
- Implemented a efficient data ingestion pipeline to persist the parsed information into the database


## Installation

- Install Mysql workbench and setup a schema called "filecoin". 
- Run tabels.sql to create the necessary tables.
- Create a db.py like below and enter your credentials.
```
import mysql.connector
def get_database_connection():
    mydb = mysql.connector.connect(user='[]', password='[]',
                                  host='localhost', database='filecoin')
    return mydb
```

## Usage

- Execute tipset.py to populate tipset table. Note that you have to uncomment lines 137-141 when running it for the first time and/or when tipset table is empty.
- Execute block.py to populate block table.
- Execute block_messages.py to populate block_messages table.