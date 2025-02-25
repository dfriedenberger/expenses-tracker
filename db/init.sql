CREATE DATABASE expenses;
CREATE USER youruser WITH ENCRYPTED PASSWORD 'yourpassword';
GRANT ALL PRIVILEGES ON DATABASE expenses TO youruser;

-- GRANT ALL PRIVILEGES ON SCHEMA public TO youruser;

\c expenses  -- Mit der Datenbank `expenses` verbinden

GRANT USAGE ON SCHEMA public TO youruser;
GRANT CREATE ON SCHEMA public TO youruser;
ALTER DEFAULT PRIVILEGES IN SCHEMA public GRANT ALL ON TABLES TO youruser;
ALTER DEFAULT PRIVILEGES IN SCHEMA public GRANT ALL ON SEQUENCES TO youruser;
