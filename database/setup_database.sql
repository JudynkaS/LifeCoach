-- Create users table
CREATE TABLE auth_user (
    id INT AUTO_INCREMENT PRIMARY KEY,
    username VARCHAR(150) NOT NULL UNIQUE,
    password VARCHAR(128) NOT NULL,
    email VARCHAR(254) NOT NULL UNIQUE,
    first_name VARCHAR(150),
    last_name VARCHAR(150),
    is_active BOOLEAN DEFAULT TRUE,
    date_joined TIMESTAMP DEFAULT CURRENT_TIMESTAMP
);

-- Create user profiles table
CREATE TABLE accounts_profile (
    id INT AUTO_INCREMENT PRIMARY KEY,
    user_id INT,
    phone VARCHAR(20),
    timezone VARCHAR(50),
    bio TEXT,
    preferred_contact VARCHAR(20),
    is_client BOOLEAN DEFAULT FALSE,
    is_coach BOOLEAN DEFAULT FALSE,
    FOREIGN KEY (user_id) REFERENCES auth_user(id) ON DELETE CASCADE
);

-- Create services table
CREATE TABLE service (
    id INT AUTO_INCREMENT PRIMARY KEY,
    name VARCHAR(100) NOT NULL,
    description TEXT,
    price DECIMAL(10,2) NOT NULL,
    duration INT NOT NULL,
    is_active BOOLEAN DEFAULT TRUE,
    currency VARCHAR(100) NOT NULL
);

-- Create booking sessions table
CREATE TABLE booking_session (
    id INT AUTO_INCREMENT PRIMARY KEY,
    client_id INT,
    coach_id INT,
    service_id INT,
    date_time TIMESTAMP NOT NULL,
    duration INT NOT NULL,
    type ENUM('online', 'in-person') NOT NULL,
    status ENUM('CANCELLED', 'CONFIRMED', 'CHANGED') NOT NULL,
    notes TEXT,
    created TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
    updated TIMESTAMP DEFAULT CURRENT_TIMESTAMP ON UPDATE CURRENT_TIMESTAMP,
    FOREIGN KEY (client_id) REFERENCES auth_user(id),
    FOREIGN KEY (coach_id) REFERENCES auth_user(id),
    FOREIGN KEY (service_id) REFERENCES service(id)
);

-- Create payments table
CREATE TABLE payment (
    id INT AUTO_INCREMENT PRIMARY KEY,
    session_id INT,
    amount DECIMAL(10,2) NOT NULL,
    payment_method ENUM('cash', 'paypal', 'bank_transfer') NOT NULL,
    status VARCHAR(20) NOT NULL,
    transaction_id VARCHAR(100),
    currency VARCHAR(100) NOT NULL,
    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
    FOREIGN KEY (session_id) REFERENCES booking_session(id)
);

-- Create reviews table
CREATE TABLE review (
    id INT AUTO_INCREMENT PRIMARY KEY,
    session_id INT,
    rating INT CHECK (rating >= 1 AND rating <= 5),
    comment TEXT,
    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
    FOREIGN KEY (session_id) REFERENCES booking_session(id)
);

-- Create indexes for better performance
CREATE INDEX idx_auth_user_email ON auth_user(email);
CREATE INDEX idx_auth_user_username ON auth_user(username);
CREATE INDEX idx_booking_session_datetime ON booking_session(date_time);
CREATE INDEX idx_booking_session_status ON booking_session(status);
CREATE INDEX idx_payment_status ON payment(status);
CREATE INDEX idx_service_active ON service(is_active);

-- Insert sample data

-- Insert users
INSERT INTO auth_user (username, password, email, first_name, last_name, is_active, date_joined) VALUES
('john.doe', 'hashed_password1', 'john.doe@email.com', 'John', 'Doe', TRUE, NOW()),
('jane.smith', 'hashed_password2', 'jane.smith@email.com', 'Jane', 'Smith', TRUE, NOW()),
('coach.mike', 'hashed_password3', 'mike.coach@email.com', 'Mike', 'Johnson', TRUE, NOW()),
('coach.sarah', 'hashed_password4', 'sarah.coach@email.com', 'Sarah', 'Williams', TRUE, NOW()),
('alice.brown', 'hashed_password5', 'alice.brown@email.com', 'Alice', 'Brown', TRUE, NOW());

-- Insert profiles
INSERT INTO accounts_profile (user_id, phone, timezone, bio, preferred_contact, is_client, is_coach) VALUES
(1, '+1234567890', 'America/New_York', 'Looking for personal growth', 'email', TRUE, FALSE),
(2, '+1987654321', 'Europe/London', 'Seeking career guidance', 'phone', TRUE, FALSE),
(3, '+1122334455', 'America/Chicago', 'Professional life coach with 10 years experience', 'email', FALSE, TRUE),
(4, '+1555666777', 'Europe/Paris', 'Certified psychologist and career coach', 'email', FALSE, TRUE),
(5, '+1445566778', 'America/Los_Angeles', 'Exploring mindfulness and personal development', 'email', TRUE, FALSE);

-- Insert services
INSERT INTO service (name, description, price, duration, is_active, currency) VALUES
('Initial Consultation', 'First meeting to discuss your goals and create a personalized plan', 50.00, 60, TRUE, 'USD'),
('Career Coaching', 'Professional guidance for career development and transitions', 100.00, 60, TRUE, 'USD'),
('Life Balance Session', 'Help with work-life balance and stress management', 80.00, 45, TRUE, 'USD'),
('Personal Growth Workshop', 'Group session focused on personal development', 150.00, 120, TRUE, 'USD'),
('Mindfulness Coaching', 'One-on-one mindfulness and meditation guidance', 90.00, 60, TRUE, 'USD');

-- Insert booking sessions
INSERT INTO booking_session (client_id, coach_id, service_id, date_time, duration, type, status, notes) VALUES
(1, 3, 1, DATE_ADD(NOW(), INTERVAL 1 DAY), 60, 'online', 'CONFIRMED', 'Initial consultation for career change'),
(2, 4, 2, DATE_ADD(NOW(), INTERVAL 2 DAY), 60, 'in-person', 'CONFIRMED', 'Career transition planning'),
(5, 3, 3, DATE_ADD(NOW(), INTERVAL 3 DAY), 45, 'online', 'CONFIRMED', 'Stress management session'),
(1, 4, 4, DATE_ADD(NOW(), INTERVAL 4 DAY), 120, 'online', 'CONFIRMED', 'Personal development workshop'),
(2, 3, 5, DATE_ADD(NOW(), INTERVAL 5 DAY), 60, 'in-person', 'CONFIRMED', 'Mindfulness introduction');

-- Insert payments
INSERT INTO payment (session_id, amount, payment_method, status, transaction_id, currency, created_at) VALUES
(1, 50.00, 'paypal', 'completed', 'PP123456789', 'USD', NOW()),
(2, 100.00, 'cash', 'completed', 'CASH987654321', 'USD', NOW()),
(3, 80.00, 'bank_transfer', 'completed', 'VM456789123', 'USD', NOW()),
(4, 150.00, 'paypal', 'pending', 'PP987654321', 'USD', NOW()),
(5, 90.00, 'cash', 'completed', 'CASH123456789', 'USD', NOW());

-- Insert reviews
INSERT INTO review (session_id, rating, comment, created_at) VALUES
(1, 5, 'Great initial consultation, very professional and helpful', NOW()),
(2, 4, 'Good session, helped clarify my career goals', NOW()),
(3, 5, 'Excellent stress management techniques', NOW()),
(4, 5, 'Workshop was very informative and engaging', NOW()),
(5, 4, 'Good introduction to mindfulness practices', NOW()); 