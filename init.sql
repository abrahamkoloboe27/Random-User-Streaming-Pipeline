
\c etl;

CREATE TABLE IF NOT EXISTS users(
    id PRIMARY KEY,
    first_name VARCHAR(50),
    last_name VARCHAR(50),
    gender VARCHAR(50),
    address VARCHAR(50),
    post_code VARCHAR(50),
    email VARCHAR(50),
    username VARCHAR(50),
    registered_date VARCHAR(50),
    phone VARCHAR(50),
    picture VARCHAR(50)
);