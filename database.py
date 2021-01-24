import sqlite3

conn = sqlite3.connect("employment.db")
curr = conn.cursor()

table_names = ["users", "postings", "profile"]
for table in table_names:
    curr.execute(f"DROP TABLE IF EXISTS {table}")

# Creates the user table
curr.execute(
    """CREATE TABLE IF NOT EXISTS users (
        user_id INTEGER PRIMARY KEY AUTOINCREMENT NOT NULL,
        first_name TEXT NOT NULL,
        last_name TEXT NOT NULL,
        email TEXT NOT NULL,
        hash TEXT NOT NULL,
        user_type TEXT NOT NULL,
        company TEXT
    )
    """
)

# Creates the job postings
curr.execute(
    """CREATE TABLE IF NOT EXISTS postings (
        posting_id INTEGER PRIMARY KEY AUTOINCREMENT NOT NULL,
        job_name TEXT NOT NULL,
        location TEXT NOT NULL,
        max_distance INTEGER NOT NULL,
        skills TEXT NOT NULL,
        user_id INTEGER NOT NULL,
        job_description TEXT NOT NULL
    )
    """
)

# Creates the employee profile
curr.execute(
    """CREATE TABLE IF NOT EXISTS profile (
        profile_id INTEGER PRIMARY KEY AUTOINCREMENT NOT NULL,
        user_id INTEGER NOT NULL UNIQUE,
        location INTEGER NOT NULL,
        skills TEXT NOT NULL,
        highest_education TEXT NOT NULL,
        resume TEXT NOT NULL
    )
    """
)