-- Enable local file loading in MySQL configuration file and restart MySQL server

-- Create database and table
CREATE DATABASE IF NOT EXISTS csvConnection;
USE csvConnection;
SET GLOBAL local_infile = 1;

CREATE TABLE consolidated_intervals (
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
GRANT FILE ON *.* TO 'root'@'localhost';

-- Load data from CSV file
LOAD DATA LOCAL INFILE 'C:/Users/Thanh/OneDrive/Documents/data.csv'
INTO TABLE consolidated_intervals
FIELDS TERMINATED BY ','
ENCLOSED BY '"'
LINES TERMINATED BY '\n'
IGNORE 1 ROWS; -- This ignores the header row in the CSV file

-- Verify data has been loaded
SELECT * FROM consolidated_intervals;
