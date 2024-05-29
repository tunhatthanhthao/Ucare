# Interval Intersection and Union Algorithm (pyRAP)

This repository contains an implementation of algorithms to find intersecting and union intervals from both MySQL and MongoDB databases. The intervals are retrieved from specified columns of a table or collection, and the intersecting or union intervals are identified and saved to a CSV or Excel file.

## Elementary Types

- **"token"**: Tokens are quoted strings. Use `\"` to escape quotes, and `\\` to escape backslashes.
- **"a", "b", "c"**: Phrases are comma-separated tokens.
- **INT**: Positions are indicated as bare integers (e.g., 4071).

## Operators

- `A ^ B`: Returns all extents that match both A and B.
  - **Example**: Given intervals:
    ```
    3  13  2  7  2  10  8  16
    20  24  9  17 11 18 23 33
    25  33  22 26 28 30 39 40
    ```
    The intersections of A (3, 13), B (9, 17), C (2, 10), and D (8, 16) would return:
    ```
    ((3, 13), (9, 17), (2, 10), (8, 16))
    ((3, 13), (9, 17), (11, 18), (8, 16))
    ```

- `A + B`: Returns all extents that match either A or B (or both).
  - **Example**: Given intervals:
    ```
    3  13  2  7  2  10  8  16
    20  24  9  17 11 18 23 33
    25  33  22 26 28 30 39 40
    ```
    The union of A (3, 13), B (9, 17), C (2, 10), and D (8, 16) would return:
    ```
    (2, 7) (2, 10) (3, 13) (8, 16) (9, 17) (11, 18)
    (20, 24) (22, 26) (23, 33) (25, 33) (28, 30)
    (34, 35) (35, 36)
    (37, 41) (39, 40)
    ```

- `A .. B`: Returns all extents that start with A and end with B.
  - **Example**: Given intervals:
    ```
    '1', '3', '13', '2', '7', '2', '10', '8', '16'
    '2', '20', '24', '9', '17', '11', '18', '23', '33'
    '3', '25', '33', '22', '26', '28', '30', '39', '40'
    ```
    The extents that start with A and end with B would return:
    ```
    (2, 10) (2, 13) (2, 16) (2, 17) (3, 16) (3, 17) (3, 18) (8, 17) (8, 18) (9, 18)
    (20, 26) (20, 33) (22, 33) (23, 30) (23, 33) (25, 30)
    (34, 36)
    (37, 40)
    ```

- `A > B`: Returns all extents that match A and contain an extent matching B.
  - **Example**: Given intervals:
    ```
    52 60 101 110 191 201 219 229 329 337 736 743 756 764 898 907
    57 58 102 105 196 199 220 225 331 334 738 742 761 763 901 903
    25 33 347 354 372 379 426 433 561 568 698 707 792 796 810 815
    28 30 349 350 375 376 430 432 562 566 701 703 794 795 811 814
    52 60 72 82 86 93 145 155 191 201 204 213 272 281 500 510 547 557 606 615 698 707 853 859 1046 1056
    54 58 73 81 87 89 146 151 193 197 207 212 277 278 503 509 553 554 610 611 700 706 854 857 1050 1054
    ```
    The extents A containing extents B would return:
    ```
    Union intervals between A and 2:
    A(52, 60) > 2(57, 58)
    A(101, 110) > 2(102, 105)
    A(191, 201) > 2(196, 199)
    A(219, 229) > 2(220, 225)
    A(329, 337) > 2(331, 334)
    A(736, 743) > 2(738, 742)
    A(756, 764) > 2(761, 763)
    A(898, 907) > 2(901, 903)
    
    Union intervals between A and 3:
    A(25, 33) > 3(28, 30)
    A(347, 354) > 3(349, 350)
    A(372, 379) > 3(375, 376)
    A(426, 433) > 3(430, 432)
    A(561, 568) > 3(562, 566)
    A(698, 707) > 3(701, 703)
    A(792, 796) > 3(794, 795)
    A(810, 815) > 3(811, 814)
    
    Union intervals between A and 4:
    A(52, 60) > 4(54, 58)
    A(72, 82) > 4(73, 81)
    A(86, 93) > 4(87, 89)
    A(145, 155) > 4(146, 151)
    A(191, 201) > 4(193, 197)
    A(204, 213) > 4(207, 212)
    A(272, 281) > 4(277, 278)
    A(500, 510) > 4(503, 509)
    A(547, 557) > 4(553, 554)
    A(606, 615) > 4(610, 611)
    A(698, 707) > 4(700, 706)
    A(853, 859) > 4(854, 857)
    A(1046, 1056) > 4(1050, 1054)
    ```

- `A < B`: Returns all extents that match A, contained in an extent matching B.
  - **Example**: Given intervals:
    ```
    52 60 101 110 191 201 219 229 329 337 736 743 756 764 898 907
    57 58 102 105 196 199 220 225 331 334 738 742 761 763 901 903
    25 33 347 354 372 379 426 433 561 568 698 707 792 796 810 815
    28 30 349 350 375 376 430 432 562 566 701 703 794 795 811 814
    52 60 72 82 86 93 145 155 191 201 204 213 272 281 500 510 547 557 606 615 698 707 853 859 1046 1056
    54 58 73 81 87 89 146 151 193 197 207 212 277 278 503 509 553 554 610 611 700 706 854 857 1050 1054
    ```
    The extents A contained within extents B would return:
    ```
    Union intervals between A and 2:
    A(52, 60) > 2(57, 58)
    A(101, 110) > 2(102, 105)
    A(191, 201) > 2(196, 199)
    A(219, 229) > 2(220, 225)
    A(329, 337) > 2(

331, 334)
    A(736, 743) > 2(738, 742)
    A(756, 764) > 2(761, 763)
    A(898, 907) > 2(901, 903)
    ```

- `_{A}`: The 'start' projection. For each extent (u, v) in A, return (u, u).
  - **Example**: Given intervals in A:
    ```
    52 60 101 110 191 201 219 229 329 337 736 743 756 764 898 907
    ```
    The 'start' projection would return:
    ```
    52 52
    101 101
    191 191
    219 219
    329 329
    736 736
    756 756
    898 898
    ```

- `{A}_`: The 'end' projection. For each extent (u, v) in A, return (v, v).
  - **Example**: Given intervals in A:
    ```
    52 60 101 110 191 201 219 229 329 337 736 743 756 764 898 907
    ```
    The 'end' projection would return:
    ```
    60 60
    110 110
    201 201
    229 229
    337 337
    743 743
    764 764
    907 907
    ```

- `[N]`: Returns all extents of length N, where N is an integer (basically a sliding window).
  - **Example**: Given intervals of various lengths:
    ```
    52 60 101 110 191 201 219 229 329 337 736 743 756 764 898 907
    ```
    With `N = 8`, the extents of length 8 would return:
    ```
    52 60
    736 743
    756 764
    ```

## Files

- **main_mysql.py**: Main script to run the interval intersection and union algorithm using MySQL.
- **main_mongodb.py**: Main script to run the interval intersection and union algorithm using MongoDB.
- **intersection.py**: Module containing the `intersection_pairs` function for computing intersecting intervals.
- **connection/mongo_connection.py**: Module containing the function `connect_to_mongodb` for connecting to MongoDB.
- **connection/connect_to_mysql.py**: Module containing the function `connect_to_mysql` for connecting to MySQL.

## Requirements

- Python 3.x
- MySQL Server or MongoDB Server
- Required Python packages: `mysql-connector-python`, `pymongo`, `csv`, `openpyxl`

Install the required Python packages using pip:
```bash
pip install mysql-connector-python pymongo openpyxl
```

## Usage

### MySQL Version

1. **Setup MySQL Database**: Ensure you have a MySQL database running with the required table and columns containing the interval data.

2. **Update Connection Details**: You can either provide the MySQL connection details (host, user, password, database) directly as arguments or be prompted for them when running the script.

3. **Run the Script**:
   ```bash
   python main_mysql.py
   ```

   If connection details are not provided as arguments, you will be prompted to enter:
   - MySQL host address
   - MySQL username
   - MySQL password
   - MySQL database name

4. **Results**: The script will output the intersecting intervals to the console and write them to `intersecting_pairs_Mysql.csv` or `find_Extend_mySql.xlsx`.

### MongoDB Version

1. **Setup MongoDB Database**: Ensure you have a MongoDB database running with the required collection containing the interval data.

2. **Run the Script**:
   ```bash
   python main_mongodb.py
   ```

   You will be prompted to enter:
   - MongoDB database name
   - MongoDB collection name

3. **Results**: The script will output the intersecting intervals to the console and write them to `intersecting_pairs_Nosql.csv`.

## Code Explanation

### Timer Class
A utility class for timing the execution of code blocks.
```python
class Timer(object):
    ...
```

### MySQL Connection Functions
Functions for connecting to MySQL and fetching data from specified columns.
```python
def connect_to_mysql(host, user, password, database):
    ...

def get_table_columns(cursor, table_name):
    ...

def read_intervals_from_mysql(cursor, table_name, start_col, end_col):
    ...
```

### MongoDB Connection Functions
Function for connecting to MongoDB and fetching data from specified collections.
```python
def connect_to_mongodb(database_name, collection_name):
    ...
```

### Intersection and Union Pairs Functions
Functions to compute intersecting and union intervals from the given sets of intervals.
```python
def intersection_pairs(S):
    ...

def find_union_pairs_linear(A, B):
    ...
```

### Print Functions
Functions to print and format intervals.
```python
def print_line(intervals):
    ...

def print_intervals_without_gaps(intervals):
    ...
```

### Main Function for MySQL
The main function orchestrates the process of:
1. Connecting to MySQL.
2. Fetching interval data from the specified columns.
3. Computing intersecting or union intervals using the appropriate functions.
4. Writing results to a CSV or Excel file.
```python
def main_mysql(host=None, user=None, password=None, database=None):
    ...
```

### Main Function for MongoDB
The main function orchestrates the process of:
1. Connecting to MongoDB.
2. Fetching interval data from the specified collection.
3. Computing intersecting intervals using the appropriate functions.
4. Writing results to a CSV file.
```python
def main_mongodb():
    ...
```

### Example
An example of running the script:
```bash
# For MySQL
python main_mysql.py

# For MongoDB
python main_mongodb.py
```

You will be prompted to enter your database connection details if not provided as arguments. The script will then fetch the interval data, compute intersections or unions, and save the results to `intersecting_pairs_Mysql.csv`, `intersecting_pairs_Nosql.csv`, or `find_Extend_mySql.xlsx`.

## License
This project is licensed under the MIT License. See the LICENSE file for details.

## Acknowledgements
This project uses the `mysql-connector-python` library for MySQL connectivity, `pymongo` for MongoDB connectivity, and the `csv` and `openpyxl` libraries for CSV and Excel file operations.

---

This README should now better reflect the functionality and examples related to the `_{A}`, `{A}_`, and `[N]` operators as specified.
