import sqlite3

class User:
    def __init__(self, user_id: int, city: str | None = None):
        self.user_id = user_id
        self.city = city

class Database:
    def __init__(self):
        self.connection = sqlite3.connect("sqlite.db")
        self.cursor = self.connection.cursor()
        self._init_table()

    def _init_table(self):
        self.cursor.execute("""
            CREATE TABLE IF NOT EXISTS users (
                id INTEGER PRIMARY KEY,
                city TEXT
            )
        """)
        self.connection.commit()

    def get_user(self, user_id: int) -> User | None:
        self.cursor.execute("SELECT * FROM users WHERE id = ?", (user_id,))
        row = self.cursor.fetchone()
        if row:
            return User(user_id=row[0], city=row[1])
        return None

    def create_user(self, user_id: int):
        self.cursor.execute("INSERT OR IGNORE INTO users(id) VALUES (?)", (user_id,))
        self.connection.commit()

    def set_city(self, user_id: int, city: str):
        self.cursor.execute("UPDATE users SET city = ? WHERE id = ?", (city, user_id))
        self.connection.commit()

    def get_users_count(self) -> int:
        self.cursor.execute("SELECT COUNT(*) FROM users")
        return self.cursor.fetchone()[0]

    def close(self):
        self.connection.close()
