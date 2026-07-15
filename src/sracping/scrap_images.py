import time
from playwright.sync_api import sync_playwright
from src.database.database_listings import *
from src.database.database_images import *

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
