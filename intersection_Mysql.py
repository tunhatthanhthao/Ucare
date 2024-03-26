import time
from connection.connect_to_mysql import connect_to_mysql
import csv
import sys
sys.path.append('C:/Users/Thanh/OneDrive/Documents/Ucare Research/connection')


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
        return intervals
    except Exception as e:
        print(f"Error reading intervals from {table_name}: {e}")
        return []

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
    # Connect to MySQL
    db_connection = connect_to_mysql(
        host="127.0.0.1",
        user="root",
        password="Ed&11281999",
        database="CsvData"
    )

    if db_connection is not None:
        with Timer() as timer:
            cursor = db_connection.cursor()

            # Read intervals from the consolidated table
            interval_lists = []
            columns = get_table_columns(cursor, 'Data_table')
            valid_columns = [col for col in columns if col != 'id']
            for i in range(0, len(valid_columns), 2):
                start_col, end_col = valid_columns[i], valid_columns[i+1]
                intervals = read_intervals_from_mysql(cursor, 'Data_table', start_col, end_col)
                interval_lists.append(intervals)

            intersecting_pairs = intersection_pairs(interval_lists)

            # Print and write results to CSV file
            with open('intersecting_pairs_Mysql.csv', 'w', newline='') as csvfile:
                writer = csv.writer(csvfile)
                writer.writerow(['Start', 'End'])
                for result in intersecting_pairs:
                    writer.writerow(result)
                    print(result)

            print(f"Total {len(intersecting_pairs)} intersecting pairs written to intersecting_pairs.csv")

            cursor.close()
            db_connection.close()

        # Calculate the elapsed time
        print(f"Total running time: {timer.secs:.6f} seconds")

    else:
        print("Error: Unable to establish connection to MySQL.")

if __name__ == "__main__":
    main()