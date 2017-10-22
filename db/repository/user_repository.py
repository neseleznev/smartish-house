from core.common import Singleton
from db.database import Database
from db.model.user import User

INIT_SCRIPT = [
    'DROP TABLE users',
    'CREATE TABLE IF NOT EXISTS users(username text)'
]


class UserRepository(metaclass=Singleton):

    def __init__(self):
        self.db = Database()
        for sql in INIT_SCRIPT:
            self.db.execute(sql)
        self.db.commit()

    def save(self, user: User):
        existing = self.get_by_username(user.username)
        if not existing:
            self.db.execute('INSERT INTO users VALUES (?)', (user.username,))
            self.db.commit()

    def get_by_username(self, username: str):
        c = self.db.execute('SELECT * FROM users WHERE username=?', (username,))
        return c.fetchone()
