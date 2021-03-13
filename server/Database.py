import hashlib
import sqlite3
import uuid


class DatabaseConnection:
    def __init__(self):
        self.con = sqlite3.connect('drawpy.db')
        # self.con.cursor().execute('DROP TABLE users')
        self.con.cursor().execute('CREATE TABLE IF NOT EXISTS users (email text primary key, password text, password_salt text)')
        # self.con.cursor().execute('CREATE TABLE IF NOT EXISTS scores (id INTEGER PRIMARY KEY AUTOINCREMENT, email text, score integer )')

    @staticmethod
    def hash_password(password, salt=uuid.uuid4().hex):
        hashed_password = hashlib.sha512(password.encode('utf-8') + salt.encode('utf-8')).hexdigest()
        return hashed_password, salt

    @property
    def cursor(self):
        return self.con.cursor()

    def add_user(self, email, password):
        try:
            (hashed_password, salt) = DatabaseConnection.hash_password(password)
            self.cursor.execute('INSERT INTO users VALUES (?, ?, ?)', [email, hashed_password, salt])
            self.con.commit()
            return True
        except sqlite3.IntegrityError:
            return "Couldn't add the user as a user with that email already exists"

    def validate_user(self, email, password):
        cursor = self.cursor
        cursor.execute('SELECT email, password, password_salt FROM users WHERE email=?', [email])
        user = cursor.fetchone()
        if user is None:
            return False

        (user_email, user_password, user_password_salt) = user
        (hashed_password, salt) = DatabaseConnection.hash_password(password, salt=user_password_salt)
        if user_password == hashed_password:
            return True

        return False

    def get_scores(self, email):
        # TODO
        pass

    def add_scores(self, emails, scores):
        # TODO
        pass

    def close_connection(self):
        self.con.close()
