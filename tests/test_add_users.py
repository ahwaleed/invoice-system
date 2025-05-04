import sqlite3, passlib.hash, pathlib

db = pathlib.Path("invoice.db")
hash_ = passlib.hash.bcrypt.hash("secret")

with sqlite3.connect(db) as conn:
    conn.execute(
        "INSERT OR IGNORE INTO users (username,password_hash,role) VALUES (?,?,?)",
        ("alice", hash_, "Employee"),
    )
    conn.execute(
        "INSERT OR IGNORE INTO users (username,password_hash,role) VALUES (?,?,?)",
        ("bob", hash_, "Manager"),
    )
    conn.commit()
print("Seeded alice (Employee) and bob (Manager) with password 'secret'")
