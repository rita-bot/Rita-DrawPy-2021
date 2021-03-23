import datetime
import hashlib
import sqlite3
import uuid


class DatabaseConnection:
    def __init__(self):
        self.con = sqlite3.connect('drawpy.db')
        # self.con.cursor().execute('DROP TABLE users')
        # self.con.cursor().execute('DROP TABLE scores')
        self.con.cursor().execute('CREATE TABLE IF NOT EXISTS users (email text primary key, password text, password_salt text)')
        self.con.cursor().execute('CREATE TABLE IF NOT EXISTS scores (id INTEGER PRIMARY KEY AUTOINCREMENT, email text, score integer, dt text)')

    @staticmethod
    def hash_password(password, salt=uuid.uuid4().hex):
        """
        creates a hash and a salt from a password string
        :param password the password to hash
        :salt a given or generated salt for the sha512 algorithm
        """
        hashed_password = hashlib.sha512(password.encode('utf-8') + salt.encode('utf-8')).hexdigest()
        return hashed_password, salt

    @property
    def cursor(self):
        """
        returns the db connection cursor
        """
        return self.con.cursor()

    def add_user(self, email, password):
        """
        add a user to db using Email and check if already exists
        """
        try:
            (hashed_password, salt) = DatabaseConnection.hash_password(password)
            self.cursor.execute('INSERT INTO users VALUES (?, ?, ?)', [email, hashed_password, salt])
            self.con.commit()
            return True
        except sqlite3.IntegrityError:
            return "Couldn't add the user as a user with that email already exists"

    def validate_user(self, email, password):
        """
        check if username and password are correct
        """
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

    def get_user_scores(self, email):
        """
        get scores of user from db - not in use
        """
        cursor = self.cursor
        cursor.execute('SELECT score, dt FROM scores WHERE email=?', [email])

        return cursor.fetchall()

    def get_high_scores(self):
        """
        get high scores from db
        """
        cursor = self.cursor
        cursor.execute('SELECT email, score, dt FROM scores ORDER BY score DESC limit 10')

        return cursor.fetchall()


    def add_scores(self, emails, scores):
        """
        add scores of users using emails and time of scoring
        """
        cursor = self.cursor

        for index in range(len(emails)):
            email = emails[index]
            score = scores[index]
            date = datetime.datetime.now()

            cursor.execute('INSERT INTO scores (email, score, dt) VALUES (?, ?, ?)', [email, score, date])
            self.con.commit()


    def close_connection(self):
        """
        disconnect the users from the server
        """
        self.con.close()
