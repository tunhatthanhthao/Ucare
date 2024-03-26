import pymongo
import time
import csv
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

def find_union_pairs_linear(A, B):
    union_pairs = set()
    i, j = 0, 0

    while i < len(A) and j < len(B):
        extent_a = tuple(A[i])  # Convert list to tuple
        extent_b = tuple(B[j])  # Convert list to tuple

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
    output_lines = []
    current_line = []
    for interval in intervals:
        if not current_line or interval[0] <= current_line[-1][1]:
            current_line.append(interval)
        else:
            output_lines.append(current_line)
            current_line = [interval]
    output_lines.append(current_line)
    return output_lines

def print_line(intervals):
    line = []
    for interval in intervals:
        line.append(f"({interval[0]},{interval[1]})")
    return line

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
    # Connect to MongoDB
    database_name = "noSQL_Connect"  # Replace with your actual database name
    collection_name = "noSQL_Connection"  # Replace with your actual collection name
    database, collection = connect_to_mongodb(database_name, collection_name)
    
    with Timer() as timer:
        # Read all documents from the MongoDB collection
        documents = collection.find()

        # Extract intervals from each document and flatten the list
        interval_lists = []
        for doc in documents:
            intervals = []
            for key in doc:
                if isinstance(doc[key], list):
                    intervals.extend(doc[key])
            interval_lists.append(intervals)

        # Flatten the list of lists
        intervals = [interval for sublist in interval_lists for interval in sublist]

        # Find union pairs and merge intervals
        union_pairs = find_union_pairs_linear(intervals, intervals)
        merged_intervals = merge_intervals(union_pairs)
        output_lines = print_intervals_without_gaps(merged_intervals)
        output_filename = "find_Extend_noSql.xlsx"

        # Print intervals
        for line in output_lines:
            print(*print_line(line))

        
        # Exporting to Excel
        wb = Workbook()
        ws = wb.active
        for line in output_lines:
            ws.append(print_line(line))
        wb.save(output_filename)
        print(f"Output written to {output_filename}")

    print(f"Total running time: {timer.secs:.6f} seconds")


if __name__ == "__main__":
    main()
