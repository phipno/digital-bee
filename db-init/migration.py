import os
import psycopg2
from psycopg2 import sql
from dotenv import load_dotenv

class DatabaseMigrator:
    def __init__(self):
        load_dotenv()
        self._connect_to_db()

    def _connect_to_db(self):
        """Establish connection to PostgreSQL database"""
        try:
            self.conn = psycopg2.connect(
                database=os.getenv('DB_NAME'),
                host=os.getenv('DB_HOST'),
                user=os.getenv('DB_USER'),
                password=os.getenv('DB_PASSWORD'),
                port=os.getenv('DB_PORT')
            )
            self.cursor = self.conn.cursor()
            print("Connected to database successfully")
        except psycopg2.Error as e:
            print(f"Database connection error: {e}")
            raise

    def close(self):
        """Close database connection"""
        if hasattr(self, 'conn'):
            self.conn.close()
            print("Database connection closed")

    def execute_query(self, query, params=None, fetch=False):
        """Generic method to execute SQL queries"""
        try:
            self.cursor.execute(query, params or ())
            if fetch:
                return self.cursor.fetchall()
            self.conn.commit()
        except psycopg2.Error as e:
            self.conn.rollback()
            print(f"Database error: {e}")
            raise

    def create_new_tables(self):
        """Create new tables in the database"""
        queries = [
            """
            CREATE TABLE IF NOT EXISTS measurement_units (
                unit_id SERIAL PRIMARY KEY,
                unit_name VARCHAR(50) UNIQUE NOT NULL
            )
            """,
            """
            CREATE TABLE IF NOT EXISTS beehive_sensors (
                beehive_id INTEGER REFERENCES beehives(beehive_id),
                sensor_id INTEGER REFERENCES sensors(sensor_id),
                PRIMARY KEY (beehive_id, sensor_id)
            )
            """,
            """
            ALTER TABLE sensors 
            DROP COLUMN IF EXISTS beehive_id,
            DROP COLUMN IF EXISTS measurement_units
            """,
            """
            ALTER TABLE data 
            ALTER COLUMN sensor_id TYPE INTEGER,
            ALTER COLUMN beehive_id TYPE INTEGER,
            ADD COLUMN IF NOT EXISTS unit_id INTEGER REFERENCES measurement_units(unit_id),
            DROP COLUMN IF EXISTS measurement_unit
            """
        ]
        
        for query in queries:
            try:
                self.execute_query(query)
                print(f"Executed: {query[:50]}...")
            except psycopg2.Error as e:
                print(f"Error creating tables: {e}")
                raise

    def migrate_data(self):
        """Migrate data from old schema to new schema"""
        try:
            # Step 1: Migrate measurement units
            print("Migrating measurement units...")
            self.execute_query("""
                INSERT INTO measurement_units (unit_name)
                SELECT DISTINCT measurement_unit FROM data
                WHERE measurement_unit IS NOT NULL
                ON CONFLICT (unit_name) DO NOTHING
            """)
            
            # Step 2: Update data table with unit_ids
            print("Updating data table with unit_ids...")
            self.execute_query("""
                UPDATE data d
                SET unit_id = mu.unit_id
                FROM measurement_units mu
                WHERE d.measurement_unit = mu.unit_name
            """)
            
            # Step 3: Create beehive_sensors relationships
            print("Creating beehive_sensor relationships...")
            self.execute_query("""
                INSERT INTO beehive_sensors (beehive_id, sensor_id)
                SELECT DISTINCT beehive_id, sensor_id FROM data
                ON CONFLICT DO NOTHING
            """)
            
            # Step 4: Remove old sensors references to beehives
            print("Migration completed successfully!")
            
        except psycopg2.Error as e:
            print(f"Migration error: {e}")
            raise

    def run_migration(self):
        """Run the complete migration process"""
        try:
            self.create_new_tables()
            self.migrate_data()
        finally:
            self.close()

if __name__ == "__main__":
    migrator = DatabaseMigrator()
    migrator.run_migration()