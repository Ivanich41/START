-- Удалем старые таблицы
DROP TABLE IF EXISTS emails;
DROP TABLE IF EXISTS phones;

ALTER USER postgres WITH PASSWORD '111';
CREATE USER repl_user WITH REPLICATION PASSWORD '111';

SELECT pg_create_physical_replication_slot('replication_slot');

CREATE TABLE emails (
    id SERIAL PRIMARY KEY,
    email VARCHAR(40) NOT NULL 
);

CREATE TABLE phones (
    id SERIAL PRIMARY KEY,
    phone VARCHAR(20) NOT NULL 
);

INSERT INTO emails (email)
VALUES('test@test.ts');
INSERT INTO phones (phone)
VALUES('88005553535');