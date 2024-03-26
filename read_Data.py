import pandas as pd
import mysql.connector

# Define MySQL connection parameters
mysql_config = {
    'host': 'localhost',
    'user': 'root',
    'password': 'Ed&11281999',
    'raise_on_warnings': True
}

# Connect to MySQL server
cnx = mysql.connector.connect(**mysql_config)
cursor = cnx.cursor()

# Create the database if it doesn't exist
cursor.execute("CREATE DATABASE IF NOT EXISTS CsvData;")
cursor.execute("USE CsvData;")

# Define MySQL connection parameters including the database
mysql_config['database'] = 'CsvData'

# Reconnect to MySQL server with the database specified
cnx = mysql.connector.connect(**mysql_config)
cursor = cnx.cursor()

# Create the table if it doesn't exist
cursor.execute("""
    CREATE TABLE IF NOT EXISTS Data_table (
        id INT AUTO_INCREMENT PRIMARY KEY,
        col1_start INT,
        col1_end INT,
        col2_start INT,
        col2_end INT,
        col3_start INT,
        col3_end INT,
        col4_start INT,
        col4_end INT
    );
""")

# Read CSV file into a pandas DataFrame
csv_file = "C:/Users/Thanh/OneDrive/Documents/data.csv"
data = pd.read_csv(csv_file)

# Insert data from the DataFrame into the MySQL table
for _, row in data.iterrows():
    cursor.execute("""
        INSERT INTO Data_table (col1_start, col1_end, col2_start, col2_end, col3_start, col3_end, col4_start, col4_end)
        VALUES (%s, %s, %s, %s, %s, %s, %s, %s);
    """, tuple(row))

# Commit changes and close connection
cnx.commit()
cursor.close()
cnx.close()

print("Data inserted successfully.")
