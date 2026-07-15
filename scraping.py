import sqlite3
import time
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

# --- MODULE 3: PLAYWRIGHT IMAGE CAPTURE ---
def get_job_image(page, job_url):
    """Navigates to the job URL and captures the raw image bytes."""
    page.goto(job_url)
    
    # Give the servlet page a moment to resolve and render the image
    page.wait_for_load_state("networkidle")
    time.sleep(1.5) 
    
    # Topjobs JobAdvertismentServlet pages usually render the ad as the primary image on the page.
    # We locate the main <img> tag. If it's inside a specific container, we grab the first visible img.
    image_locator = page.locator("img.shrunk-image")
    
    # Take an element screenshot which returns raw binary bytes directly
    image_bytes = image_locator.screenshot()
    return image_bytes

# --- MODULE 4: PIPELINE ORCHESTRATOR ---
def run_image_pipeline():
    # 1. Get targets from the source database
    job_records = get_urls_from_source_db()
    if not job_records:
        return
        
    print(f"Found {len(job_records)} records in source database. Initializing image pipeline...")
    
    # 2. Open connection to the new image database
    dest_conn = init_image_db()
    
    # 3. Start Playwright
    with sync_playwright() as p:
        browser = p.chromium.launch(headless=True)
        page = browser.new_page()
        
        for job_ref_no, position, employer, job_url in job_records:
            # Skip if we already downloaded the image in a previous session
            if is_image_already_saved(dest_conn, job_ref_no):
                print(f"[*] Ref {job_ref_no} already has an image stored. Skipping.")
                continue
                
            print(f"[>] Processing: {position} at {employer}...")
            
            try:
                # Run the image capture function
                image_bytes = get_job_image(page, job_url)
                
                # Store it in the new DB
                save_job_with_image(dest_conn, job_ref_no, position, employer, job_url, image_bytes)
                
            except Exception as e:
                print(f"[-] Error downloading image for Ref {job_ref_no}: {e}")
                
        browser.close()
    
    dest_conn.close()
    print("\n[✓] Image pipeline execution complete.")

if __name__ == "__main__":
    run_image_pipeline()