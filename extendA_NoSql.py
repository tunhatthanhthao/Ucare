import pymongo
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

def find_union(A, B):
    union_intervals = []
    for interval_a in A:
        for interval_b in B:
            if interval_a[0] < interval_b[0] and interval_a[1] > interval_b[1]:
                union_intervals.append((interval_a, interval_b))
    return union_intervals

def print_intervals_without_gaps(intervals):
    current_line = []
    for interval in intervals:
        if not current_line or interval[0][0] <= current_line[-1][1][1]:
            current_line.append(interval)
        else:
            print_line(current_line)
            current_line = [interval]
    print_line(current_line)

def get_table_columns(collection):
    try:
        # Get the first document in the collection
        sample_document = collection.find_one()

        # Extract table columns
        columns = list(sample_document.keys())
        
        # Remove the '_id' field if present
        if '_id' in columns:
            columns.remove('_id')

        return columns
    except Exception as e:
        print(f"Error getting table columns: {e}")
        return []

def print_line(intervals):
    for interval in intervals:
        print(f"{interval[0]} {interval[1]}", end=' ')
    print() 

def read_intervals_from_mongodb(collection, table_name):
    try:
        result = collection.find_one({}, {table_name: 1, '_id': 0})
        return result[table_name]
    except Exception as e:
        print(f"Error reading from MongoDB: {e}")
        return []

def union(A, B):
    result_set = set()
    for extent_a in A:
        for extent_b in B:
            if not extent_a or not extent_b:
                continue  # Skip invalid intervals
            # Check for None values and handle them appropriately
            if extent_b[1] is None or extent_a[0] is None:
                continue  # Skip if any endpoint is None
            elif extent_b[1] < extent_a[0]:
                continue  # No overlap, skip to the next pair
            else:
                # There is an overlap, add both intervals to the result set
                result_set.add(tuple(extent_a))
                result_set.add(tuple(extent_b))
    return sorted(result_set, key=lambda x: (x[0], x[1]))


def main():
    # Connect to MongoDB
    database_name = "noSQL_Connect"  # Replace with your actual database name
    collection_name = "noSQL_Connection"  # Replace with your actual collection name
    database, collection = connect_to_mongodb(database_name, collection_name)

    output_lines = []  # Store output lines for exporting to CSV

    with Timer() as timer:
        tables = get_table_columns(collection)
        
        for i in range(len(tables)):
            table_A = tables[i]
            for j in range(i+1, len(tables)):
                table_B = tables[j]
                
                # Read intervals from MongoDB for both tables
                intervals_A = read_intervals_from_mongodb(collection, table_A)
                intervals_B = read_intervals_from_mongodb(collection, table_B)

                # Find union intervals between intervals_A and intervals_B
                union_intervals = find_union(intervals_A, intervals_B)
                
                if union_intervals:
                    print(f"Union intervals between {table_A} and {table_B}:")
                    for interval_pair in union_intervals:
                        print(f"{table_A}{interval_pair[0]} < {table_B}{interval_pair[1]}")
                    
                    # Check if any intervals in the union are unions
                    unions = union([x[0] for x in union_intervals], [x[1] for x in union_intervals])
                    if unions:
                        print("Unions:", unions)
                
                    # Append to output_lines
                    output_lines.extend(union_intervals)

    print(f"Total running time: {timer.secs:.6f} seconds")
    
    # Exporting to CSV
    with open('extend_A_Nosql.csv', 'w', newline='') as csvfile:
        writer = csv.writer(csvfile)
        writer.writerow(['Start', 'End'])
        for line in output_lines:
            writer.writerow([line[0], line[1]])

if __name__ == "__main__":
    main()
