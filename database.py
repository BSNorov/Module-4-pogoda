import sqlite3


class User:
    def __init__(self, user_id: int, city: str | None = None):
        self.user_id = user_id
        self.city = city


class Database:
    def __init__(self):
        self.connection = sqlite3.connect("sqlite.db")
        self.cursor = self.connection.cursor()
        self._create_tables()

    def _create_tables(self):
        self.cursor.execute("""
            CREATE TABLE IF NOT EXISTS users (
                id INTEGER PRIMARY KEY,
                city TEXT
            )
        """)
        self.connection.commit()

    def get_user(self, user_id: int) -> User | None:
        query = "SELECT * FROM users WHERE id = ?"
        self.cursor.execute(query, (user_id,))
        row = self.cursor.fetchone()
        return User(user_id=row[0], city=row[1]) if row else None

    def create_user(self, user_id: int):
        query = "INSERT OR IGNORE INTO users(id) VALUES (?)"
        self.cursor.execute(query, (user_id,))
        self.connection.commit()

    def set_city(self, user_id: int, city: str):
        query = "UPDATE users SET city = ? WHERE id = ?"
        self.cursor.execute(query, (city, user_id))
        self.connection.commit()

    def get_users_count(self) -> int:
        self.cursor.execute("SELECT COUNT(*) FROM users")
        return self.cursor.fetchone()[0]

    def close(self):
        self.connection.close()
