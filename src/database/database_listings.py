import sqlite3
from playwright.sync_api import sync_playwright

# --- MODULE 1: DATABASE SETUP ---
def init_db():
    conn = sqlite3.connect('topjobs_listings.db')
    cursor = conn.cursor()
    
    # Added job_url to the schema
    cursor.execute('''
        CREATE TABLE IF NOT EXISTS jobs (
            job_ref_no TEXT PRIMARY KEY,
            alert_string TEXT,
            job_url TEXT,
            position TEXT,
            employer TEXT,
            opening_date TEXT,
            closing_date TEXT
        )
    ''')
    conn.commit()
    return conn

def save_job(conn, job_ref_no, alert_string, job_url, position, employer, opening_date, closing_date):
    cursor = conn.cursor()
    try:
        # Updated INSERT statement to include job_url
        cursor.execute('''
            INSERT INTO jobs (job_ref_no, alert_string, job_url, position, employer, opening_date, closing_date)
            VALUES (?, ?, ?, ?, ?, ?, ?)
        ''', (job_ref_no, alert_string, job_url, position, employer, opening_date, closing_date))
        conn.commit()
        print(f"[+] Saved: {job_ref_no} | {position}")
    except sqlite3.IntegrityError:
        print(f"[-] Skipped: {job_ref_no} already in database.")