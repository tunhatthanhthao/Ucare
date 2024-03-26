import mysql.connector
import time
import csv
from connection.connect_to_mysql import connect_to_mysql


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

def get_table_columns(cursor, table_name):
    try:
        cursor.execute(f"SHOW COLUMNS FROM {table_name}")
        columns = [column[0] for column in cursor.fetchall()]
        return columns
    except Exception as e:
        print(f"Error fetching columns from {table_name}: {e}")
        return []

def read_intervals_from_mysql(cursor, table_name, start_col, end_col):
    try:
        query = f"SELECT {start_col}, {end_col} FROM {table_name}"
        cursor.execute(query)
        intervals = cursor.fetchall()
        return intervals  # Assuming intervals are stored as (start, end) pairs
    except Exception as e:
        print(f"Error reading intervals from {table_name}: {e}")
        return []

def find_union(A, B):
    union_intervals = []
    for interval_a in A:
        if interval_a[0] is None or interval_a[1] is None:
            continue
        for interval_b in B:
            if interval_b[0] is None or interval_b[1] is None:
                continue
            if interval_a[0] > interval_b[0] and interval_a[1] < interval_b[1]:
                union_intervals.append((interval_a, interval_b))
    return union_intervals


def print_intervals_without_gaps(intervals):
    current_line = []
    seen_intervals = set()  # To track seen intervals
    for interval in intervals:
        # Check if interval is a tuple before accessing its elements
        if isinstance(interval, tuple) and len(interval) >= 2:
            if interval not in seen_intervals:  # Check if interval is already seen
                if not current_line or interval[0] <= current_line[-1][1]:
                    current_line.append(interval)
                else:
                    print_line(current_line)
                    current_line = [interval]
                seen_intervals.add(interval)  # Add interval to seen_intervals
        else:
            print("Invalid interval:", interval)
    if current_line:  # Print the remaining intervals if any
        print_line(current_line)


def print_line(intervals):
    for interval in intervals:
        print(f"({interval[0]}, {interval[1]})", end=' ')
    print() 

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
                result_set.add(extent_a)
                result_set.add(extent_b)

    return sorted(result_set, key=lambda x: (x[0], x[1]))

def main():
    # Establish a connection to MySQL
    db_connection = connect_to_mysql(
        host="127.0.0.1",
        user="root",
        password="Ed&11281999",
        database="CsvData"
    )
    cursor = db_connection.cursor()

    with Timer() as timer:
        # Fetch all column names from the Data_table
        columns = get_table_columns(cursor, "Data_table")
        
        # Filter columns ending with "_start" and "_end"
        start_col_A = "col1_start"
        end_col_A = "col1_end"
        
        union_results = []  # Store union results for each pair of columns
        
        for i in range(2, 5):
            start_col_B = f"col{i}_start"
            end_col_B = f"col{i}_end"
            
            # Read intervals from MySQL
            intervals_A = read_intervals_from_mysql(cursor, "Data_table", start_col_A, end_col_A)
            intervals_B = read_intervals_from_mysql(cursor, "Data_table", start_col_B, end_col_B)

            # Find union intervals between intervals_A and intervals_B
            union_intervals = find_union(intervals_A, intervals_B)
            
            if union_intervals:
                print(f"Union intervals between A and {i}:")
                for interval_pair in union_intervals:
                    print(f"A{interval_pair[0]} < {i}{interval_pair[1]}")
                
                # Check if any intervals in the union are unions
                unions = union([x[0] for x in union_intervals], [x[1] for x in union_intervals])
                if unions:
                    print("Unions:", unions)
                
                # Append to union_results
                union_results.extend(union_intervals)

        # Perform union operation
        union_result = union_results[0]
        for i in range(1, len(union_results)):
            union_result = union(union_result, union_results[i])
        
        # Print intervals without gaps
            print_intervals_without_gaps(union_result)

    cursor.close()
    db_connection.close()

    print(f"Total running time: {timer.secs:.6f} seconds")
    
    # Exporting to CSV
    with open('extend_A_Mysql.csv', 'w', newline='') as csvfile:
        writer = csv.writer(csvfile)
        writer.writerow(['Start', 'End'])
        for line in union_result:
            writer.writerow([line[0], line[1]])

if __name__ == "__main__":
    main()
