from flask import current_app
import pymysql
import pymysql.cursors
import sqlite3


class DBManager:
    def get_db_connection(self):
        if 'sqlite' in current_app.config['SQLALCHEMY_DATABASE_URI']:
            # Connect to SQLite for tests
            conn = sqlite3.connect(current_app.config['SQLALCHEMY_DATABASE_URI'].replace('sqlite:///', ''))
            conn.row_factory = sqlite3.Row  # This makes the rows behave like dictionaries
            return conn
        else:
            # Existing MySQL connection logic
            host = current_app.config['DB_HOST']
            user = current_app.config['DB_USER']
            password = current_app.config['DB_PASSWORD']
            db = current_app.config['DB_NAME']
            return pymysql.connect(
                host=host,
                user=user,
                password=password,
                db=db,
                charset='utf8mb4',
                cursorclass=pymysql.cursors.DictCursor
            )

