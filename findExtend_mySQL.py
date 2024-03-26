import time
import mysql.connector
from openpyxl import Workbook
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
        return intervals
    except Exception as e:
        print(f"Error reading intervals from {table_name}: {e}")
        return []

def find_union_pairs_linear(A, B):
    union_pairs = set()
    i, j = 0, 0

    while i < len(A) and j < len(B):
        extent_a = A[i]
        extent_b = B[j]

        if not extent_a or not extent_b or len(extent_a) != 2 or len(extent_b) != 2:
            continue  # Skip invalid intervals

        if extent_b[1] < extent_a[0]:
            j += 1
        else:
            # There is an overlap, add both intervals to the union pairs set
            union_pairs.add(extent_a)
            union_pairs.add(extent_b)
            i += 1
            j += 1  # Move both pointers forward

    return sorted(union_pairs, key=lambda x: (x[0], x[1]))

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

def merge_intervals(union_pairs):
    union_pairs = sorted(union_pairs, key=lambda x: (x[0], x[1]))
    merged_intervals = set()

    for i in range(len(union_pairs)):
        for j in range(i + 1, len(union_pairs)):
            # Check if intervals can be merged
            if union_pairs[i][1] >= union_pairs[j][0]:
                merged_intervals.add((union_pairs[i][0], union_pairs[j][1]))

    return sorted(merged_intervals, key=lambda x: (x[0], x[1]))

def main():
    try:
        db_connection = connect_to_mysql(
        host="127.0.0.1",
        user="root",
        password="Ed&11281999",
        database="CsvData"
    )

        if db_connection.is_connected():
            with Timer() as timer:
                cursor = db_connection.cursor()

                columns = get_table_columns(cursor, "Data_table")
                start_cols = [col for col in columns if col.endswith("_start")]
                end_cols = [col for col in columns if col.endswith("_end")]

                # Read intervals from the consolidated table
                interval_lists = [read_intervals_from_mysql(cursor, "Data_table", start_col, end_col) for start_col, end_col in zip(start_cols, end_cols)]

            union_pairs = set()
            for i in range(len(interval_lists)):
                for j in range(i + 1, len(interval_lists)):
                    union_pairs.update(find_union_pairs_linear(interval_lists[i], interval_lists[j]))

            merged_intervals = merge_intervals(union_pairs)
            output_lines = print_intervals_without_gaps(merged_intervals)

            # Exporting to Excel
            wb = Workbook()
            ws = wb.active
            for line in output_lines:
                ws.append(print_line(line))
            wb.save("find_Extend_mySql.xlsx")

    except Exception as e:
        print(f"Error: {e}")

    print(f"Total running time: {timer.secs:.6f} seconds")


if __name__ == "__main__":
    main()
