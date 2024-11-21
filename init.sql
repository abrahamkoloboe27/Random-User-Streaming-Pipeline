DO $$
BEGIN
   IF NOT EXISTS (
      SELECT FROM pg_database
      WHERE datname = 'etl'
   ) THEN
      PERFORM dblink_exec('dbname=etl', 'CREATE DATABASE etl');
   END IF;
END
$$;

\c etl;

CREATE TABLE IF NOT EXISTS public."users"(
    id  VARCHAR(2250) PRIMARY KEY,
    first_name VARCHAR(250),
    last_name VARCHAR(250),
    gender VARCHAR(250),
    address VARCHAR(250),
    post_code VARCHAR(250),
    email VARCHAR(250),
    username VARCHAR(250),
    registered_date VARCHAR(250),
    phone VARCHAR(250),
    picture VARCHAR(250)
);