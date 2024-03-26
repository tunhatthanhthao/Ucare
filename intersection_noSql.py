import time
import csv
from connection.mongo_connection import connect_to_mongodb

class Timer(object):
    def __init__(self, verbose=False):
        self.verbose = verbose

    def __enter__(self):
        self.start = time.perf_counter()
        return self

    def __exit__(self, *args):
        self.end = time.perf_counter()
        self.secs = self.end - self.start
        self.msecs = self.secs * 1000  # millisecs
        if self.verbose:
            print('elapsed time: %f ms' % self.msecs)

def intersection_pairs(S):
    num_S = len(S)
    indices = [0] * num_S

    min_end = [S[i][0][1] for i in range(num_S)]
    max_start = [S[i][0][0] for i in range(num_S)]

    T = []

    while True:
        min_end_val = min(min_end)
        max_start_val = max(max_start)

        if max_start_val <= min_end_val:
            T.append(tuple(S[i][indices[i]] for i in range(num_S)))

        for i in range(num_S):
            if S[i][indices[i]][1] == min_end_val:
                indices[i] += 1
                if indices[i] < len(S[i]):
                    min_end[i] = S[i][indices[i]][1]
                    max_start[i] = S[i][indices[i]][0]
                else:
                    min_end[i] = float('inf')

        if any(indices[i] >= len(S[i]) for i in range(num_S)):
            break

    return T

def main():
    # Connect to MongoDB
    database_name = "noSQL_Connect"  # Replace with your actual database name
    collection_name = "noSQL_Connection"  # Replace with your actual collection name
    database, collection = connect_to_mongodb(database_name, collection_name)

    # Get table columns dynamically
    distinct_keys = collection.find_one().keys()
    # Exclude the default MongoDB "_id" field, if present
    table_columns = [key for key in distinct_keys if key != "_id"]

    # Read data from MongoDB
    cursor = collection.find({})
    result = list(cursor)

    # Process data into separate lists for each table
    tables = {column: [item[column] for item in result] for column in table_columns}
    
    # Convert values to integers if they are integers or strings
    table_data = {table_name: [(int(i[0]), int(i[1])) for sublist in table_values for i in sublist] for table_name, table_values in tables.items()}

    with Timer() as intersecting_timer:
        intersecting_pairs = intersection_pairs(list(table_data.values()))

    # Print intersecting pairs and write to CSV file
    print("Intersecting Pairs:")
    with open('intersecting_pairs_Nosql.csv', 'w', newline='') as csvfile:
        writer = csv.writer(csvfile)
        writer.writerow(['Start', 'End'])
        for result in intersecting_pairs:
            writer.writerow(result)
            print(result)

    print(f"Intersecting pairs exported to intersecting_pairs_Nosql.csv")
    print(f"Total pairs: {len(intersecting_pairs)}")
    print(f"Total running time: {intersecting_timer.secs} seconds")


if __name__ == "__main__":
    main()
