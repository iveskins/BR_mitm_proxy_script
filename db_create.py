import sqlite3

def create_database(db_file):
    # Connect to the SQLite database
    conn = sqlite3.connect(db_file)

    # Create a new SQLite table
    conn.execute('''
        CREATE TABLE IF NOT EXISTS jobs (
            job_id TEXT PRIMARY KEY,
            job_details TEXT,
            gpt_response TEXT,
            batch_status TEXT,
            sync_status TEXT
        )
    ''')

    # Commit the changes and close the connection
    conn.commit()
    conn.close()

if __name__ == "__main__":
    # Specify the name of the database file
    db_filename = 'jobs.db'
    create_database(db_filename)
    print(f"Database '{db_filename}' created with 'jobs' table.")
