
-- Database schema for Neuro Assistant

CREATE DATABASE neuro_assistant_db;

-- Table for storing user information
CREATE TABLE Users (
    user_id SERIAL PRIMARY KEY,
    telegram_username VARCHAR(50) UNIQUE NOT NULL,
    name VARCHAR(100),
    registration_date TIMESTAMP DEFAULT CURRENT_TIMESTAMP
);

-- Table for storing user's progress
CREATE TABLE Progress (
    progress_id SERIAL PRIMARY KEY,
    user_id INT REFERENCES Users(user_id) ON DELETE CASCADE,
    module_name VARCHAR(100) NOT NULL,
    status VARCHAR(20) DEFAULT 'incomplete',
    completion_date TIMESTAMP
);

-- Table for storing quiz results
CREATE TABLE QuizResults (
    result_id SERIAL PRIMARY KEY,
    user_id INT REFERENCES Users(user_id) ON DELETE CASCADE,
    quiz_id INT NOT NULL,
    score INT CHECK (score >= 0 AND score <= 100),
    attempt_date TIMESTAMP DEFAULT CURRENT_TIMESTAMP
);

-- Table for storing lecture progress
CREATE TABLE LectureProgress (
    progress_id SERIAL PRIMARY KEY,
    user_id INT REFERENCES Users(user_id) ON DELETE CASCADE,
    lecture_id INT NOT NULL,
    completed BOOLEAN DEFAULT FALSE,
    completion_date TIMESTAMP
);
