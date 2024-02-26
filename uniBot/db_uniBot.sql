CREATE TABLE courses (
    id INT AUTO_INCREMENT PRIMARY KEY,
    course_title VARCHAR(255),
    course_code VARCHAR(10),
    semester VARCHAR(20),
    course_type VARCHAR(50),
    lectures VARCHAR(255),
    ects VARCHAR(10),
    instructors TEXT,
    course_webpage VARCHAR(255),
    educational_goals TEXT,
    course_contents TEXT,
    teaching_method TEXT,
    students_evaluation TEXT
);
