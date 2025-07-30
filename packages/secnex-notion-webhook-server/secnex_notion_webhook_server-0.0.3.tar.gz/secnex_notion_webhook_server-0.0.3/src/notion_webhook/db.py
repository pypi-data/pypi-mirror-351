import sqlite3
import uuid
import base64
from argon2 import PasswordHasher
from typing import Optional, Tuple

class TokenDatabase:
    def __init__(self, db_path: str = "tokens.db"):
        self.db_path = db_path
        self.ph = PasswordHasher()
        self._init_db()

    def _init_db(self) -> None:
        with sqlite3.connect(self.db_path) as conn:
            cursor = conn.cursor()
            cursor.execute('''
                CREATE TABLE IF NOT EXISTS tokens (
                    id TEXT PRIMARY KEY,
                    token_hash TEXT NOT NULL,
                    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
                )
            ''')
            conn.commit()

    def check_first_run(self) -> bool:
        with sqlite3.connect(self.db_path) as conn:
            cursor = conn.cursor()
            cursor.execute("SELECT COUNT(*) FROM tokens")
            return cursor.fetchone()[0] == 0

    def create_token(self) -> Tuple[str, str]:
        """Erstellt einen neuen Token und gibt (id, encoded_token) zurück"""
        token_id = str(uuid.uuid4())
        token = str(uuid.uuid4())
        token_hash = self.ph.hash(token)
        
        with sqlite3.connect(self.db_path) as conn:
            cursor = conn.cursor()
            cursor.execute(
                "INSERT INTO tokens (id, token_hash) VALUES (?, ?)",
                (token_id, token_hash)
            )
            conn.commit()

        # Encode token als base64
        encoded_token = base64.b64encode(f"{token_id}:{token}".encode()).decode()
        return token_id, encoded_token

    def verify_token(self, encoded_token: str) -> bool:
        """Überprüft einen Token"""
        try:
            # Decode base64 token
            decoded = base64.b64decode(encoded_token.encode()).decode()
            token_id, token = decoded.split(":")
            
            with sqlite3.connect(self.db_path) as conn:
                cursor = conn.cursor()
                cursor.execute(
                    "SELECT token_hash FROM tokens WHERE id = ?",
                    (token_id,)
                )
                result = cursor.fetchone()
                
                if not result:
                    return False
                
                stored_hash = result[0]
                try:
                    self.ph.verify(stored_hash, token)
                    return True
                except Exception as e:
                    print(f"Error verifying token: {encoded_token} - {str(e)}")
                    return False
                
        except Exception as e:
            print(f"Error processing token: {encoded_token} - {str(e)}")
            return False

    def get_token(self, encoded_token: str) -> Optional[str]:
        """Gibt den Token zurück, wenn er gültig ist"""
        if self.verify_token(encoded_token):
            return encoded_token
        return None

    def delete_token(self, token_id: str) -> bool:
        """Löscht einen Token"""
        try:
            with sqlite3.connect(self.db_path) as conn:
                cursor = conn.cursor()
                cursor.execute("DELETE FROM tokens WHERE id = ?", (token_id,))
                conn.commit()
                return cursor.rowcount > 0
        except Exception:
            return False 