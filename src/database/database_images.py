import sqlite3
from playwright.sync_api import sync_playwright

# --- MODULE 1: NEW DATABASE SETUP ---
def init_image_db():
    """Initializes the new database to store images and job details."""
    conn = sqlite3.connect('topjobs_images.db')
    cursor = conn.cursor()
    
    # image_bytes uses the BLOB data type to store raw binary data
    cursor.execute('''
        CREATE TABLE IF NOT EXISTS job_details_with_images (
            job_ref_no TEXT PRIMARY KEY,
            position TEXT,
            employer TEXT,
            job_url TEXT,
            image_bytes BLOB
        )
    ''')
    conn.commit()
    return conn

def is_image_already_saved(conn, job_ref_no):
    """Checks if the image for this job has already been collected."""
    cursor = conn.cursor()
    cursor.execute('SELECT 1 FROM job_details_with_images WHERE job_ref_no = ?', (job_ref_no,))
    return cursor.fetchone() is not None

def save_job_with_image(conn, job_ref_no, position, employer, job_url, image_bytes):
    """Saves the complete record including the image BLOB to the new database."""
    cursor = conn.cursor()
    try:
        cursor.execute('''
            INSERT INTO job_details_with_images (job_ref_no, position, employer, job_url, image_bytes)
            VALUES (?, ?, ?, ?, ?)
        ''', (job_ref_no, position, employer, job_url, sqlite3.Binary(image_bytes)))
        conn.commit()
        print(f"[+] Successfully captured image for Ref: {job_ref_no}")
    except Exception as e:
        print(f"[-] Failed to save Ref {job_ref_no} to image database: {e}")

# --- MODULE 2: SOURCE DATA RETRIEVAL ---
def get_urls_from_source_db():
    """Fetches all rows from the original listings database."""
    try:
        source_conn = sqlite3.connect('topjobs_listings.db')
        cursor = source_conn.cursor()
        cursor.execute('SELECT job_ref_no, position, employer, job_url FROM jobs')
        rows = cursor.fetchall()
        source_conn.close()
        return rows
    except sqlite3.OperationalError:
        print("[-] Error: 'topjobs_listings.db' or the 'jobs' table does not exist. Run your first script first.")
        return []
