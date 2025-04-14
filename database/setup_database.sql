-- Vytvoření tabulky uživatelů
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

-- Vytvoření tabulky profilů uživatelů
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

-- Vytvoření tabulky služeb
CREATE TABLE service (
    id INT AUTO_INCREMENT PRIMARY KEY,
    name VARCHAR(100) NOT NULL,
    description TEXT,
    price DECIMAL(10,2) NOT NULL,
    duration INT NOT NULL,
    is_active BOOLEAN DEFAULT TRUE,
    currency VARCHAR(100) NOT NULL
);

-- Vytvoření tabulky rezervací sezení
CREATE TABLE booking_session (
    id INT AUTO_INCREMENT PRIMARY KEY,
    client_id INT,
    coach_id INT,
    service_id INT,
    date_time TIMESTAMP NOT NULL,
    duration INT NOT NULL,
    type ENUM('online', 'osobní') NOT NULL,
    status ENUM('zrušeno', 'potvrzeno', 'změněno') NOT NULL,
    notes TEXT,
    created TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
    updated TIMESTAMP DEFAULT CURRENT_TIMESTAMP ON UPDATE CURRENT_TIMESTAMP,
    FOREIGN KEY (client_id) REFERENCES auth_user(id),
    FOREIGN KEY (coach_id) REFERENCES auth_user(id),
    FOREIGN KEY (service_id) REFERENCES service(id)
);

-- Vytvoření tabulky plateb
CREATE TABLE payment (
    id INT AUTO_INCREMENT PRIMARY KEY,
    session_id INT,
    amount DECIMAL(10,2) NOT NULL,
    payment_method ENUM('hotovost', 'paypal', 'bankovní převod') NOT NULL,
    status VARCHAR(20) NOT NULL,
    transaction_id VARCHAR(100),
    currency VARCHAR(100) NOT NULL,
    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
    FOREIGN KEY (session_id) REFERENCES booking_session(id)
);

-- Vytvoření tabulky recenzí
CREATE TABLE review (
    id INT AUTO_INCREMENT PRIMARY KEY,
    session_id INT,
    rating INT CHECK (rating >= 1 AND rating <= 5),
    comment TEXT,
    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
    FOREIGN KEY (session_id) REFERENCES booking_session(id)
);

-- Vytvoření indexů pro lepší výkon
CREATE INDEX idx_auth_user_email ON auth_user(email);
CREATE INDEX idx_auth_user_username ON auth_user(username);
CREATE INDEX idx_booking_session_datetime ON booking_session(date_time);
CREATE INDEX idx_booking_session_status ON booking_session(status);
CREATE INDEX idx_payment_status ON payment(status);
CREATE INDEX idx_service_active ON service(is_active);

-- Vložení ukázkových dat

-- Vložení uživatelů
INSERT INTO auth_user (username, password, email, first_name, last_name, is_active, date_joined) VALUES
('jan.novak', 'hashed_password1', 'jan.novak@email.com', 'Jan', 'Novák', TRUE, NOW()),
('jana.svobodova', 'hashed_password2', 'jana.svobodova@email.com', 'Jana', 'Svobodová', TRUE, NOW()),
('kouc.michal', 'hashed_password3', 'michal.kouc@email.com', 'Michal', 'Kouč', TRUE, NOW()),
('kouc.tereza', 'hashed_password4', 'tereza.kouc@email.com', 'Tereza', 'Koučová', TRUE, NOW()),
('alena.cerna', 'hashed_password5', 'alena.cerna@email.com', 'Alena', 'Černá', TRUE, NOW());

-- Vložení profilů
INSERT INTO accounts_profile (user_id, phone, timezone, bio, preferred_contact, is_client, is_coach) VALUES
(1, '+420123456789', 'Europe/Prague', 'Hledám osobní rozvoj', 'email', TRUE, FALSE),
(2, '+420987654321', 'Europe/Prague', 'Potřebuji kariérní poradenství', 'telefon', TRUE, FALSE),
(3, '+420112233445', 'Europe/Prague', 'Profesionální kouč s 10 lety zkušeností', 'email', FALSE, TRUE),
(4, '+420155566677', 'Europe/Prague', 'Certifikovaná psycholožka a kariérní koučka', 'email', FALSE, TRUE),
(5, '+420144556677', 'Europe/Prague', 'Zajímám se o mindfulness a osobní rozvoj', 'email', TRUE, FALSE);

-- Vložení služeb
INSERT INTO service (name, description, price, duration, is_active, currency) VALUES
('Úvodní konzultace', 'První schůzka pro diskuzi o vašich cílech a vytvoření personalizovaného plánu', 1200.00, 60, TRUE, 'CZK'),
('Kariérní koučink', 'Profesionální vedení pro kariérní rozvoj a změny', 2000.00, 60, TRUE, 'CZK'),
('Sezení pro rovnováhu', 'Pomoc s rovnováhou mezi prací a soukromím a zvládání stresu', 1600.00, 45, TRUE, 'CZK'),
('Workshop osobního rozvoje', 'Skupinové sezení zaměřené na osobní rozvoj', 3000.00, 120, TRUE, 'CZK'),
('Koučink mindfulness', 'Individuální vedení mindfulness a meditace', 1800.00, 60, TRUE, 'CZK');

-- Vložení rezervací sezení
INSERT INTO booking_session (client_id, coach_id, service_id, date_time, duration, type, status, notes) VALUES
(1, 3, 1, DATE_ADD(NOW(), INTERVAL 1 DAY), 60, 'online', 'potvrzeno', 'Úvodní konzultace pro kariérní změnu'),
(2, 4, 2, DATE_ADD(NOW(), INTERVAL 2 DAY), 60, 'osobní', 'potvrzeno', 'Plánování kariérní změny'),
(5, 3, 3, DATE_ADD(NOW(), INTERVAL 3 DAY), 45, 'online', 'potvrzeno', 'Sezení pro zvládání stresu'),
(1, 4, 4, DATE_ADD(NOW(), INTERVAL 4 DAY), 120, 'online', 'potvrzeno', 'Workshop osobního rozvoje'),
(2, 3, 5, DATE_ADD(NOW(), INTERVAL 5 DAY), 60, 'osobní', 'potvrzeno', 'Úvod do mindfulness');

-- Vložení plateb
INSERT INTO payment (session_id, amount, payment_method, status, transaction_id, currency, created_at) VALUES
(1, 1200.00, 'paypal', 'dokončeno', 'PP123456789', 'CZK', NOW()),
(2, 2000.00, 'hotovost', 'dokončeno', 'CASH987654321', 'CZK', NOW()),
(3, 1600.00, 'bankovní převod', 'dokončeno', 'VM456789123', 'CZK', NOW()),
(4, 3000.00, 'paypal', 'čeká se', 'PP987654321', 'CZK', NOW()),
(5, 1800.00, 'hotovost', 'dokončeno', 'CASH123456789', 'CZK', NOW());

-- Vložení recenzí
INSERT INTO review (session_id, rating, comment, created_at) VALUES
(1, 5, 'Skvělá úvodní konzultace, velmi profesionální a užitečná', NOW()),
(2, 4, 'Dobré sezení, pomohlo mi objasnit kariérní cíle', NOW()),
(3, 5, 'Výborné techniky pro zvládání stresu', NOW()),
(4, 5, 'Workshop byl velmi informativní a zajímavý', NOW()),
(5, 4, 'Dobrý úvod do mindfulness praktik', NOW()); 