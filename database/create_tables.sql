-- Create ENUM types
CREATE TYPE payment_method AS ENUM ('PAYPAL', 'VENMO', 'CASH');
CREATE TYPE session_type AS ENUM ('PERSONAL', 'ONLINE');
CREATE TYPE session_status AS ENUM ('SCHEDULED', 'COMPLETED', 'CANCELLED', 'PENDING');

-- Create auth_user table
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

-- Create accounts_profile table
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

-- Create service table
CREATE TABLE service (
    id INT AUTO_INCREMENT PRIMARY KEY,
    name VARCHAR(100) NOT NULL,
    description TEXT,
    price DECIMAL(10,2) NOT NULL,
    duration INT NOT NULL,
    is_active BOOLEAN DEFAULT TRUE,
    menu VARCHAR(100) NOT NULL,
    currency VARCHAR(3) NOT NULL DEFAULT 'USD'
);

-- Create booking_session table
CREATE TABLE booking_session (
    id INT AUTO_INCREMENT PRIMARY KEY,
    client_id INT,
    coach_id INT,
    service_id INT,
    date_time TIMESTAMP NOT NULL,
    duration INT NOT NULL,
    type ENUM('online', 'on-person') NOT NULL,
    status ENUM('canceled', 'confirmed', 'changed') NOT NULL,
    notes TEXT,
    created TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
    updated TIMESTAMP DEFAULT CURRENT_TIMESTAMP ON UPDATE CURRENT_TIMESTAMP,
    FOREIGN KEY (client_id) REFERENCES auth_user(id),
    FOREIGN KEY (coach_id) REFERENCES auth_user(id),
    FOREIGN KEY (service_id) REFERENCES service(id)
);

-- Create payment table
CREATE TABLE payment (
    id INT AUTO_INCREMENT PRIMARY KEY,
    session_id INT,
    amount DECIMAL(10,2) NOT NULL,
    payment_method ENUM('cash', 'paypall', 'venmo') NOT NULL,
    status VARCHAR(20) NOT NULL,
    transaction_id VARCHAR(100),
    menu VARCHAR(100) NOT NULL,
    currency VARCHAR(3) NOT NULL DEFAULT 'USD',
    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
    FOREIGN KEY (session_id) REFERENCES booking_session(id)
);

-- Create review table
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

-- Add trigger to update the 'updated' timestamp on booking_session table
CREATE OR REPLACE FUNCTION update_updated_column()
RETURNS TRIGGER AS $$
BEGIN
    NEW.updated = CURRENT_TIMESTAMP;
    RETURN NEW;
END;
$$ language 'plpgsql';

CREATE TRIGGER update_booking_session_updated
    BEFORE UPDATE ON booking_session
    FOR EACH ROW
    EXECUTE FUNCTION update_updated_column(); 