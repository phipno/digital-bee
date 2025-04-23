sudo apt update
sudo apt install postgresql postgresql-contrib
sudo service postgresql start

set -a
source .env
set +a

echo "Database host: $DB_HOST"

sudo -u postgres psql -h localhost

CREATE DATABASE "$DB_NAME";
CREATE USER "$DB_USER" WITH PASSWORD "$DB_PASSWORD";
GRANT ALL PRIVILEGES ON DATABASE "$DB_NAME" TO "DB_USER";
\q

psql -U "$DB_USER" -d "$DB_NAME" -h localhost -f beehive_shema.sql

