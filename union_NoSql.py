import time
import pymongo
from openpyxl import Workbook
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

def read_intervals_from_mongodb(collection, start_col, end_col):
    try:
        result = collection.find({}, {f'{start_col}': 1, f'{end_col}': 1, '_id': 0})
        return [(doc[f'{start_col}'], doc[f'{end_col}']) for doc in result]
    except Exception as e:
        print(f"Error reading from MongoDB: {e}")
        return []

def union(A, B):
    result_set = set()

    for extent_a in A:
        for extent_b in B:
            if not extent_a or not extent_b or len(extent_a) != 2 or len(extent_b) != 2:
                continue  # Skip invalid intervals

            if extent_b[1] < extent_a[0] or extent_a[1] < extent_b[0]:
                continue  # No overlap, skip to the next pair
            else:
                # There is an overlap, add both intervals to the result set
                result_set.add(extent_a)
                result_set.add(extent_b)

    return sorted(result_set, key=lambda x: (x[0], x[1]))

def print_intervals_without_gaps(intervals):
    current_line = []
    output_lines = []
    for interval in intervals:
        if not current_line or interval[0] <= current_line[-1][1]:
            current_line.append(interval)
        else:
            output_lines.append(current_line)
            current_line = [interval]
    output_lines.append(current_line)

    for line in output_lines:
        print_line(line)

    return output_lines

def print_line(intervals):
    output_line = []
    for interval in intervals:
        output_line.append(f"({interval[0]},{interval[1]})")
    print(' '.join(output_line))

    return output_line

def main():
    try:
        # Connect to MongoDB
        database_name = "noSQL_Connect"  # Replace with your actual database name
        collection_name = "noSQL_Connection"  # Replace with your actual collection name
        database, collection = connect_to_mongodb(database_name, collection_name)

        with Timer() as timer:
            # Get table columns dynamically
            table_columns = get_table_columns(collection)

            # Read data from MongoDB
            cursor = collection.find({})
            result = list(cursor)

            # Process data into separate lists for each table
            tables = {column: [item[column] for item in result] for column in table_columns}
            
            # Convert values to integers if they are integers or strings
            table_data = {table_name: [(int(i[0]), int(i[1])) for sublist in table_values for i in sublist] for table_name, table_values in tables.items()}

            interval_lists = list(table_data.values())
            union_result = interval_lists[0]
            for i in range(1, len(interval_lists)):
                union_result = union(union_result, interval_lists[i])

            # Print result
            output_lines = print_intervals_without_gaps(union_result)

            # Exporting to Excel
            wb = Workbook()
            ws = wb.active
            for line in output_lines:
                ws.append(print_line(line))
            wb.save("union_Nosql.xlsx")

    except Exception as e:
        print(f"Error: {e}")

    print(f"Total running time: {timer.secs:.6f} seconds")

if __name__ == "__main__":
    main()
