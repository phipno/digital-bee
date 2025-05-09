# *--------------------------------------------------------------------------------------*#
# *                                                                                .|    *#
# *     $FILENAME                 data_collector.py    /     (__)          |/            *#
# *                                                          (oo)------/'   ,__,    ,    *#
# *     By: $AUTHOR                          phipno       |  (__)     ||    (oo)_____/   *#
# *                                                             ||---/||    (__)    ||   *#
# *     Created: $CREATEDAT 2025.04.18    by phipno   |/                  ,    ||--w||   *#
# *                                                  ,,       !              |'          *#
# *                                                       ,           ,|             |/  *#
# *----------------8<------------------[ mooooooo ]--------------------------------------*#

import os
import psycopg2
from psycopg2 import sql
from dotenv import load_dotenv

class DatabaseManager:
    def __init__(self):
        load_dotenv()
        self._connect_to_db()

    def _connect_to_db(self):
        """Establish connection to PostgreSQL database"""
        try:
            self.conn = psycopg2.connect(
                database=os.getenv('DB_NAME'),
                host=os.getenv('DB_HOST'), # If hosted publicly
                # host=os.getenv('localhost'), # If hosted locally
                user=os.getenv('DB_USER'),
                password=os.getenv('DB_PASSWORD'),
                port=os.getenv('DB_PORT')
            )
            self.cursor = self.conn.cursor()
        except psycopg2.Error as e:
            print(f"Database connection error: {e}")
            raise

    def close(self):
        """Close database connection"""
        if hasattr(self, 'conn'):
            self.conn.close()

    def execute_query(self, query, params=None, fetch=False):
        """Generic method to execute SQL queries"""
        try:
            self.cursor.execute(query, params or ())
            if fetch:
                return self.cursor.fetchone()
            self.conn.commit()
        except psycopg2.Error as e:
            self.conn.rollback()
            print(f"Database error: {e}")
            raise

    def get_row_by_value(self, table_name, column_name, value):
        """Get a row by column value"""
        query = sql.SQL("SELECT * FROM {} WHERE {} = %s").format(
            sql.Identifier(table_name), 
            sql.Identifier(column_name)
        )
        return self.execute_query(query, (value,), fetch=True)

    def get_row_by_two_values(self, table_name, column_name, column_name2, value, value2):
        """Get a row by two column values"""
        query = sql.SQL("SELECT * FROM {} WHERE {} = %s AND {} = %s").format(
            sql.Identifier(table_name),
            sql.Identifier(column_name),
            sql.Identifier(column_name2)
        )

        return self.execute_query(query, (value, value2), fetch=True)

    def table_exists(self, table_name, schema="public"):
        """Check if table exists in database"""
        query = """
            SELECT EXISTS(
                SELECT 1
                FROM pg_catalog.pg_tables
                WHERE schemaname = %s
                AND tablename = %s
            );
        """
        return self.execute_query(query, (schema, table_name), fetch=True)[0]


#.~"~._.~"~._.~"~._.~"~.__.~"~._.~"~._.~  EOF  ~._.~"~.__.~"~._.~"~._.~"~._.~"~._.~"~._.~#