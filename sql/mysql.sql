SET NAMES utf8mb4;

CREATE TABLE IF NOT EXISTS student_record (
    id INT PRIMARY KEY,
    full_name VARCHAR(100),
    group_code VARCHAR(30)
) DEFAULT CHARACTER SET utf8mb4;

INSERT INTO student_record (id, full_name, group_code)
VALUES (1, 'Тимков Дмитро Віталійович', '6.1214-пі-2');