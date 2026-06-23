CREATE TABLE users(
    id SERIAL PRIMARY KEY,
    username VARCHAR(255) NOT NULL UNIQUE,
    password TEXT,
    mfa TEXT,
    gendate BIGINT,
    expired BOOLEAN DEFAULT FALSE
);