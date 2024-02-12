from flask import current_app
import pymysql
import pymysql.cursors

class DBManager:
    def get_db_connection(self):
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
