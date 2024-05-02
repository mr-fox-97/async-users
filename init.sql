CREATE TABLE IF NOT EXISTS accounts (
    id SERIAL PRIMARY KEY,
    user_id UUID NOT NULL,
    user_name VARCHAR(255) UNIQUE NOT NULL,
    created_at TIMESTAMP NOT NULL DEFAULT CURRENT_TIMESTAMP
);

CREATE TABLE IF NOT EXISTS credentials (
    id SERIAL PRIMARY KEY,
    account_id INT NOT NULL,
    password_hash VARCHAR(255) NOT NULL,
    password_salt VARCHAR(255),
    FOREIGN KEY (account_id) REFERENCES accounts(id)
);

CREATE TABLE IF NOT EXISTS emails (
    id SERIAL PRIMARY KEY,
    account_id INT NOT NULL,
    email_address VARCHAR(255) NOT NULL,
    email_is_primary BOOLEAN NOT NULL,
    email_is_verified BOOLEAN NOT NULL,
    FOREIGN KEY (account_id) REFERENCES accounts(id)
);

CREATE TABLE IF NOT EXISTS phones (
    id SERIAL PRIMARY KEY,
    account_id INT NOT NULL,
    phone_number VARCHAR(255) NOT NULL,
    phone_is_primary BOOLEAN NOT NULL,
    phone_is_verified BOOLEAN NOT NULL,
    FOREIGN KEY (account_id) REFERENCES accounts(id)
);