import pymongo

def connect_to_mongodb(database_name, collection_name):
    """
    Connects to MongoDB and returns the specified database and collection.
    """
    client = pymongo.MongoClient()
    database = client[database_name]
    collection = database[collection_name]
    return database, collection
