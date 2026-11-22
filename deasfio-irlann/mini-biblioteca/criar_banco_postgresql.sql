CREATE ROLE biblioteca_user
    LOGIN
    NOSUPERUSER
    NOCREATEDB
    NOCREATEROLE
    PASSWORD 'troque_esta_senha';

CREATE DATABASE biblioteca_db
    OWNER biblioteca_user
    ENCODING 'UTF8';
