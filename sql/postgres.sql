CREATE TABLE IF NOT EXISTS student_record (
    id INTEGER PRIMARY KEY,
    full_name VARCHAR(100),
    group_code VARCHAR(30)
);

INSERT INTO student_record (id, full_name, group_code)
VALUES (1, 'Тимков Дмитро Віталійович', '6.1214-пі-2');