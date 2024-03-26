# A .. B  Returns all extents that start with A and end with B

import pandas as pd
import time


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

def read_intervals_from_excel(file_path):
    df = pd.read_excel(file_path, header=None)
    return df

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

def merge_intervals(union_pairs):
    union_pairs = sorted(union_pairs, key=lambda x: (x[0], x[1]))
    merged_intervals = set()

    for i in range(len(union_pairs)):
        for j in range(i + 1, len(union_pairs)):
            # Check if intervals can be merged
            if union_pairs[i][1] >= union_pairs[j][0]:
                merged_intervals.add((union_pairs[i][0], union_pairs[j][1]))

    return sorted(merged_intervals, key=lambda x: (x[0], x[1]))

def print_intervals_without_gaps(intervals):
    current_line = []
    for interval in intervals:
        if not current_line or interval[0] <= current_line[-1][1]:
            current_line.append(interval)
        else:
            print_line(current_line)
            current_line = [interval]
    print_line(current_line)

def print_line(intervals):
    for interval in intervals:
        print(f"({interval[0]},{interval[1]})", end=' ')
    print()

def main(input_excel_path='C:/Users/Thanh/OneDrive/Documents/Intersection_Input.xlsx'):
    with Timer() as timer:
        df = read_intervals_from_excel(input_excel_path)
        interval_lists = [df[col].dropna().apply(lambda x: tuple(map(int, x.split(', '))) if isinstance(x, str) else x).tolist() for col in df.columns]

        union_pairs = set()
        for i in range(len(interval_lists)):
            for j in range(i + 1, len(interval_lists)):
                union_pairs.update(find_union_pairs_linear(interval_lists[i], interval_lists[j]))

        merged_intervals = merge_intervals(union_pairs)
        print_intervals_without_gaps(merged_intervals)

    print(f"Total running time: {timer.secs:.6f} seconds")

if __name__ == "__main__":
    main()