import pandas as pd
import pymongo

# File path
file_path = "C:/Users/Thanh/OneDrive/Documents/data.csv"

# Connect to MongoDB
client = pymongo.MongoClient("mongodb://localhost:27017")
database = client["noSQL_Connect"]  # Replace with your actual database name
collection = database["noSQL_Connection"]  # Replace with your actual collection name

# Read CSV into a pandas DataFrame
df = pd.read_csv(file_path)

# Convert DataFrame to dictionary
data_dict = df.to_dict(orient="list")

# Rename the columns as per your MongoDB document structure
data_dict["_id"] = {"$oid": "65bdd1887aff671bafeb233f"}
data_dict = {f"table{i+1}": [[start, end] for start, end in zip(data_dict[f"col{i+1}_start"], data_dict[f"col{i+1}_end"])] for i in range(4)}

# Insert data into MongoDB
collection.insert_one(data_dict)

print("Data inserted successfully into MongoDB.")
