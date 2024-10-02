"""
MongoDB Utility Script for CRUD Operations

This script provides utility functions to connect to a MongoDB database, and perform CRUD operations (Create, Read, Update, Delete).
The functions allow you to insert documents, read/query documents, update existing documents, and delete documents in a specified MongoDB collection.
"""

from pymongo.mongo_client import MongoClient
from pymongo.server_api import ServerApi


def get_database(db_name, collection_name, username, password, ca_file):
    """
    Use the get_database function to establish a connection to the MongoDB cluster by providing the necessary parameters such as:
        db_name: The name of the database.
        collection_name: The collection you want to interact with.
        username: MongoDB username for authentication.
        password: MongoDB password for authentication.
        ca_file: Path to the CA file for SSL connection.
    """
    uri = f"mongodb+srv://{username}:{password}@bt4103.cnngw.mongodb.net/?retryWrites=true&w=majority&appName=BT4103&tlsCAFile={ca_file}"
    client = MongoClient(uri, server_api=ServerApi("1"))
    db = client[db_name]
    return db[collection_name]


def insert_one_document(collection, data):
    """
    Insert a single document into the collection.

    Inputs:
        collection: The MongoDB collection object.
        A dictionary representing the document to insert.

    Returns:
        The ID of the inserted document.
    """
    result = collection.insert_one(data)
    return result.inserted_id


def insert_many_documents(collection, data_list):
    """
    Insert multiple documents into the collection.

    Inputs:
        collection: The MongoDB collection object.
        data_list: A list of dictionaries representing documents to insert.

    Returns:
        A list of the inserted document IDs.
    """
    result = collection.insert_many(data_list)
    return result.inserted_ids


def find_all_documents(collection):
    """
    Retrieve all documents from the collection.

    Inputs:
        collection: The MongoDB collection object.

    Returns:
        A list of all documents in the collection.
    """
    return list(collection.find())


def find_document_by_query(collection, query):
    """
    Retrieve documents based on a specific query.

    Inputs:
        collection: The MongoDB collection object.
        query: A dictionary representing the MongoDB query.

    Returns:
        A list of documents that match the query.
    """
    return list(collection.find(query))


def update_one_document(collection, query, new_values):
    """
    Update a single document in the collection.

    Inputs:
        collection: The MongoDB collection object.
        query: A dictionary representing the MongoDB query for identifying which document to update.
        new_values: A dictionary representing the fields to update.

    Returns:
        The number of documents updated.
    """
    result = collection.update_one(query, {"$set": new_values})
    return result.modified_count


def update_many_documents(collection, query, new_values):
    """
    Update multiple documents in the collection.

    Inputs:
        collection: The MongoDB collection object.
        query: A dictionary representing the MongoDB query for identifying documents to update.
        new_values: A dictionary representing the fields to update.

    Returns:
        The number of documents updated.
    """
    result = collection.update_many(query, {"$set": new_values})
    return result.modified_count


def delete_one_document(collection, query):
    """
    Delete a single document from the collection.

    Inputs:
        collection: The MongoDB collection object.
        query: A dictionary representing the MongoDB query for identifying which document to delete.

    Returns:
        The number of documents deleted.
    """
    result = collection.delete_one(query)
    return result.deleted_count


def delete_many_documents(collection, query):
    """
    Delete multiple documents from the collection.

    Inputs:
        collection: The MongoDB collection object.
        query: A dictionary representing the MongoDB query for identifying documents to delete.

    Returns:
        The number of documents deleted.
    """
    result = collection.delete_many(query)
    return result.deleted_count

def delete_all(collection):
    """
    Deletes all documents from the collection.

    Inputs:
        collection: The MongoDB collection object.

    Returns:
        The number of documents deleted.
    """
    result = collection.delete_many({})
    return print(f'{result.deleted_count} documents deleted.')



