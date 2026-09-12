import sqlite3
import os

db_path = "skillmatch.db"
conn = sqlite3.connect(db_path)
cursor = conn.cursor()

# Check opportunities table
cursor.execute("PRAGMA table_info(opportunities)")
opp_cols = [row[1] for row in cursor.fetchall()]
print("Opportunities columns:", opp_cols)

if "status" not in opp_cols:
    print("Adding status to opportunities...")
    cursor.execute("ALTER TABLE opportunities ADD COLUMN status TEXT DEFAULT 'UNMARKED'")
    conn.commit()
    print("Added status column to opportunities.")

# Check applications table
cursor.execute("PRAGMA table_info(applications)")
app_cols = [row[1] for row in cursor.fetchall()]
print("Applications columns:", app_cols)

conn.close()
print("Migration check completed successfully!")
