#!/bin/bash

set -ex

sudo apt update
sudo apt install -y postgresql postgresql-contrib
sudo service postgresql start

set -a
source .env || { echo "Failed to load .env file"; exit 1; }
set +a

echo "Database host: $DB_HOST"

psql -U postgres <<-EOSQL
    CREATE DATABASE "${DB_NAME}";
    CREATE USER "${DB_USER}" WITH PASSWORD '${DB_PASSWORD}';
    GRANT ALL PRIVILEGES ON DATABASE "${DB_NAME}" TO "${DB_USER}";
    ALTER DATABASE "${DB_NAME}" OWNER TO "${DB_USER}";
EOSQL

psql -U "$DB_USER" -d "$DB_NAME" -h localhost -f "${BEEHIVE_SCHEMA_PATH:-./db-init/init.sql}"

echo "Database setup completed successfully"