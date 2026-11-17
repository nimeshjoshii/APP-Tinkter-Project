-- ================================================================
-- Smart Exam Hall – Anti-Cheating Seat Allocator
-- Run this script in MySQL Workbench (or any MySQL client).
-- ================================================================

CREATE DATABASE IF NOT EXISTS exam_hall_db;
USE exam_hall_db;

-- ── Students ────────────────────────────────────────────────
CREATE TABLE IF NOT EXISTS students (
    id           INT AUTO_INCREMENT PRIMARY KEY,
    reg_no       VARCHAR(20)  NOT NULL UNIQUE,
    name         VARCHAR(100) NOT NULL,
    branch       VARCHAR(30)  NOT NULL,
    subject_code VARCHAR(20)  NOT NULL
);

-- ── Halls ───────────────────────────────────────────────────
CREATE TABLE IF NOT EXISTS halls (
    id         INT AUTO_INCREMENT PRIMARY KEY,
    hall_name  VARCHAR(50) NOT NULL UNIQUE,
    total_rows INT         NOT NULL,
    total_cols INT         NOT NULL
);

-- ── Allocations ─────────────────────────────────────────────
CREATE TABLE IF NOT EXISTS allocations (
    id         INT AUTO_INCREMENT PRIMARY KEY,
    student_id INT NOT NULL,
    hall_id    INT NOT NULL,
    row_no     INT NOT NULL,
    col_no     INT NOT NULL,
    FOREIGN KEY (student_id) REFERENCES students(id) ON DELETE CASCADE,
    FOREIGN KEY (hall_id)    REFERENCES halls(id)    ON DELETE CASCADE,
    UNIQUE (hall_id, row_no, col_no),
    UNIQUE (student_id)
);

-- ── Sample Halls ────────────────────────────────────────────
INSERT IGNORE INTO halls (hall_name, total_rows, total_cols) VALUES
    ('Hall A', 5, 6),
    ('Hall B', 4, 5),
    ('Hall C', 4, 4);

-- ── Sample Students (40 across 4 branches × 4 subjects) ────
-- CSE  → CS101
-- ECE  → EC201
-- MECH → ME301
-- CIVIL → CE401

INSERT IGNORE INTO students (reg_no, name, branch, subject_code) VALUES
    ('CSE001', 'Aarav Sharma',     'CSE',   'CS101'),
    ('CSE002', 'Diya Patel',       'CSE',   'CS101'),
    ('CSE003', 'Ishaan Reddy',     'CSE',   'CS101'),
    ('CSE004', 'Meera Nair',       'CSE',   'CS101'),
    ('CSE005', 'Rohan Gupta',      'CSE',   'CS101'),
    ('CSE006', 'Ananya Singh',     'CSE',   'CS101'),
    ('CSE007', 'Vivaan Joshi',     'CSE',   'CS101'),
    ('CSE008', 'Kavya Rao',        'CSE',   'CS101'),
    ('CSE009', 'Arjun Menon',      'CSE',   'CS101'),
    ('CSE010', 'Priya Das',        'CSE',   'CS101'),

    ('ECE001', 'Aditya Kumar',     'ECE',   'EC201'),
    ('ECE002', 'Sneha Iyer',       'ECE',   'EC201'),
    ('ECE003', 'Karthik Bhat',     'ECE',   'EC201'),
    ('ECE004', 'Neha Verma',       'ECE',   'EC201'),
    ('ECE005', 'Siddharth Pillai', 'ECE',   'EC201'),
    ('ECE006', 'Ritu Agarwal',     'ECE',   'EC201'),
    ('ECE007', 'Manav Desai',      'ECE',   'EC201'),
    ('ECE008', 'Pooja Chauhan',    'ECE',   'EC201'),
    ('ECE009', 'Rahul Shetty',     'ECE',   'EC201'),
    ('ECE010', 'Tanya Mehta',      'ECE',   'EC201'),

    ('ME001',  'Vikram Kulkarni',  'MECH',  'ME301'),
    ('ME002',  'Anjali Saxena',    'MECH',  'ME301'),
    ('ME003',  'Suresh Yadav',     'MECH',  'ME301'),
    ('ME004',  'Lakshmi Prasad',   'MECH',  'ME301'),
    ('ME005',  'Deepak Tiwari',    'MECH',  'ME301'),
    ('ME006',  'Nisha Pandey',     'MECH',  'ME301'),
    ('ME007',  'Amit Bhatt',       'MECH',  'ME301'),
    ('ME008',  'Swati Mishra',     'MECH',  'ME301'),
    ('ME009',  'Rajesh Sinha',     'MECH',  'ME301'),
    ('ME010',  'Divya Kapoor',     'MECH',  'ME301'),

    ('CE001',  'Nikhil Rawat',     'CIVIL', 'CE401'),
    ('CE002',  'Shruti Malhotra',  'CIVIL', 'CE401'),
    ('CE003',  'Gaurav Hegde',     'CIVIL', 'CE401'),
    ('CE004',  'Pallavi Jain',     'CIVIL', 'CE401'),
    ('CE005',  'Tarun Sethi',      'CIVIL', 'CE401'),
    ('CE006',  'Aparna Nambiar',   'CIVIL', 'CE401'),
    ('CE007',  'Varun Gill',       'CIVIL', 'CE401'),
    ('CE008',  'Isha Banerjee',    'CIVIL', 'CE401'),
    ('CE009',  'Harsh Dubey',      'CIVIL', 'CE401'),
    ('CE010',  'Kriti Choudhary',  'CIVIL', 'CE401');