-- Users and Profiles
CREATE TABLE lifecoach.accounts_user (
    id INT AUTO_INCREMENT PRIMARY KEY,
    password VARCHAR(128) NOT NULL,
    last_login DATETIME NULL,
    is_superuser BOOLEAN NOT NULL DEFAULT FALSE,
    username VARCHAR(150) NOT NULL UNIQUE,
    first_name VARCHAR(150) NOT NULL,
    last_name VARCHAR(150) NOT NULL,
    email VARCHAR(254) NOT NULL UNIQUE,
    is_staff BOOLEAN NOT NULL DEFAULT FALSE,
    is_active BOOLEAN NOT NULL DEFAULT TRUE,
    date_joined DATETIME NOT NULL,
    is_client BOOLEAN NOT NULL DEFAULT FALSE,
    is_coach BOOLEAN NOT NULL DEFAULT FALSE
);

CREATE TABLE lifecoach.accounts_profile (
    id INT AUTO_INCREMENT PRIMARY KEY,
    user_id INT NOT NULL,
    phone VARCHAR(20) NULL,
    timezone VARCHAR(50) NOT NULL DEFAULT 'UTC',
    bio TEXT NULL,
    preferred_contact VARCHAR(20) NOT NULL DEFAULT 'email',
    is_client BOOLEAN NOT NULL DEFAULT TRUE,
    is_coach BOOLEAN NOT NULL DEFAULT FALSE,
    created DATETIME NOT NULL,
    updated DATETIME NOT NULL,
    FOREIGN KEY (user_id) REFERENCES accounts_user(id) ON DELETE CASCADE
);

-- Session Types and Statuses
CREATE TABLE lifecoach.viewer_sessiontype (
    id INT AUTO_INCREMENT PRIMARY KEY,
    name VARCHAR(100) NOT NULL,
    description TEXT NULL,
    created DATETIME NOT NULL,
    updated DATETIME NOT NULL
);

CREATE TABLE lifecoach.viewer_sessionstatus (
    id INT AUTO_INCREMENT PRIMARY KEY,
    name VARCHAR(50) NOT NULL,
    description TEXT NULL,
    created DATETIME NOT NULL,
    updated DATETIME NOT NULL
);

CREATE TABLE lifecoach.viewer_paymentmethod (
    id INT AUTO_INCREMENT PRIMARY KEY,
    name VARCHAR(50) NOT NULL,
    description TEXT NULL,
    created DATETIME NOT NULL,
    updated DATETIME NOT NULL
);

-- Services
CREATE TABLE lifecoach.viewer_service (
    id INT AUTO_INCREMENT PRIMARY KEY,
    name VARCHAR(100) NOT NULL,
    description TEXT NOT NULL,
    price DECIMAL(10,2) NOT NULL,
    duration VARCHAR(50) NOT NULL,
    coach_id INT NOT NULL,
    session_type_id INT NOT NULL,
    created DATETIME NOT NULL,
    updated DATETIME NOT NULL,
    FOREIGN KEY (coach_id) REFERENCES accounts_user(id),
    FOREIGN KEY (session_type_id) REFERENCES viewer_sessiontype(id)
);

-- Sessions
CREATE TABLE lifecoach.viewer_session (
    id INT AUTO_INCREMENT PRIMARY KEY,
    client_id INT NOT NULL,
    coach_id INT NOT NULL,
    service_id INT NOT NULL,
    status_id INT NOT NULL,
    scheduled_at DATETIME NOT NULL,
    notes TEXT NULL,
    created DATETIME NOT NULL,
    updated DATETIME NOT NULL,
    FOREIGN KEY (client_id) REFERENCES accounts_user(id),
    FOREIGN KEY (coach_id) REFERENCES accounts_user(id),
    FOREIGN KEY (service_id) REFERENCES viewer_service(id),
    FOREIGN KEY (status_id) REFERENCES viewer_sessionstatus(id)
);

-- Payments
CREATE TABLE lifecoach.viewer_payment (
    id INT AUTO_INCREMENT PRIMARY KEY,
    session_id INT NOT NULL,
    amount DECIMAL(10,2) NOT NULL,
    payment_method_id INT NOT NULL,
    paid_at DATETIME NULL,
    created DATETIME NOT NULL,
    updated DATETIME NOT NULL,
    FOREIGN KEY (session_id) REFERENCES viewer_session(id),
    FOREIGN KEY (payment_method_id) REFERENCES viewer_paymentmethod(id)
);

-- Reviews
CREATE TABLE lifecoach.viewer_review (
    id INT AUTO_INCREMENT PRIMARY KEY,
    session_id INT NOT NULL,
    rating INT NOT NULL,
    comment TEXT NULL,
    created DATETIME NOT NULL,
    updated DATETIME NOT NULL,
    FOREIGN KEY (session_id) REFERENCES viewer_session(id)
);

-- Initial data for session types
INSERT INTO lifecoach.viewer_sessiontype (name, description, created, updated) VALUES
('Individual', 'One-on-one coaching session', NOW(), NOW()),
('Group', 'Group coaching session', NOW(), NOW()),
('Workshop', 'Interactive workshop session', NOW(), NOW());

-- Initial data for session statuses
INSERT INTO lifecoach.viewer_sessionstatus (name, description, created, updated) VALUES
('Scheduled', 'Session is scheduled', NOW(), NOW()),
('Completed', 'Session has been completed', NOW(), NOW()),
('Cancelled', 'Session was cancelled', NOW(), NOW()),
('Rescheduled', 'Session was rescheduled', NOW(), NOW());

-- Initial data for payment methods
INSERT INTO lifecoach.viewer_paymentmethod (name, description, created, updated) VALUES
('Cash', 'Cash payment', NOW(), NOW()),
('Bank Transfer', 'Direct bank transfer', NOW(), NOW()),
('Credit Card', 'Credit card payment', NOW(), NOW()),
('PayPal', 'PayPal payment', NOW(), NOW());

-- Create superuser
INSERT INTO lifecoach.accounts_user (
    username,
    password,
    is_superuser,
    first_name,
    last_name,
    email,
    is_staff,
    is_active,
    date_joined,
    is_client,
    is_coach
) VALUES (
    'admin',
    -- heslo je 'admin' zahashované pomocí Django's default hasher
    'pbkdf2_sha256$600000$ucMYt3bDgOoYcw2lNgfoLD$w5+3bzS+H3gAydM5PRXC+AyV6Riez5/qeXvt6rChhK8=',
    TRUE,
    'Admin',
    'User',
    'admin@example.com',
    TRUE,
    TRUE,
    NOW(),
    FALSE,
    FALSE
);

-- Django's built-in tables
CREATE TABLE lifecoach.django_session (
    session_key varchar(40) NOT NULL PRIMARY KEY,
    session_data longtext NOT NULL,
    expire_date datetime(6) NOT NULL,
    INDEX django_session_expire_date_a5c62663 (expire_date)
);

CREATE TABLE lifecoach.django_content_type (
    id int NOT NULL AUTO_INCREMENT PRIMARY KEY,
    app_label varchar(100) NOT NULL,
    model varchar(100) NOT NULL,
    UNIQUE KEY django_content_type_app_label_model_76bd3d3b_uniq (app_label, model)
);

CREATE TABLE lifecoach.django_migrations (
    id int NOT NULL AUTO_INCREMENT PRIMARY KEY,
    app varchar(255) NOT NULL,
    name varchar(255) NOT NULL,
    applied datetime(6) NOT NULL
);

CREATE TABLE lifecoach.django_admin_log (
    id int NOT NULL AUTO_INCREMENT PRIMARY KEY,
    action_time datetime(6) NOT NULL,
    object_id longtext,
    object_repr varchar(200) NOT NULL,
    action_flag smallint UNSIGNED NOT NULL,
    change_message longtext NOT NULL,
    content_type_id int NULL,
    user_id int NOT NULL,
    CONSTRAINT django_admin_log_content_type_id_c4bce8eb_fk_django_co FOREIGN KEY (content_type_id) REFERENCES django_content_type (id),
    CONSTRAINT django_admin_log_user_id_c564eba6_fk_auth_user_id FOREIGN KEY (user_id) REFERENCES accounts_user (id),
    CONSTRAINT django_admin_log_action_flag_check CHECK ((action_flag >= 0))
); 