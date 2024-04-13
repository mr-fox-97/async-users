CREATE TABLE IF NOT EXISTS accounts (
    id UUID,
    created_at TIMESTAMP WITH TIME ZONE DEFAULT CURRENT_TIMESTAMP,
    updated_at TIMESTAMP WITH TIME ZONE DEFAULT CURRENT_TIMESTAMP,
    PRIMARY KEY (id)
);

CREATE TABLE IF NOT EXISTS credentials (
    id SERIAL,
    account_id UUID,
    username VARCHAR(50),
    password VARCHAR(255),
    PRIMARY KEY (id),
    FOREIGN KEY (account_id) REFERENCES accounts(id)
);