import sqlite3
import re
from bs4 import BeautifulSoup
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

# --- MODULE 2: EXTRACTION LOGIC ---
def extract_jobs_from_html(html_content, conn):
    soup = BeautifulSoup(html_content, 'html.parser')
    rows = soup.find_all('tr', id=re.compile(r'^tr\d+$'))
    
    for row in rows:
        try:
            onclick_text = row.get('onclick', '')
            match = re.search(r"createAlert\((.*?)\)", onclick_text)
            
            if not match:
                continue
            
            # 1. Grab the ENTIRE string inside the parentheses
            alert_string = match.group(1) 
            
            # 2. Extract Variables and Construct URL
            params = [p.strip().strip("'") for p in alert_string.split(',')]
            
            if len(params) >= 4:
                # Map the variables exactly as the JS function does
                i = params[0]
                agentCode = params[1]
                joCode = params[2]  # This is the job_ref_no
                empCode = params[3]
                
                # The 5th parameter 'id' is only used for the window name in JS, not the URL.
                
                # Construct the absolute URL
                job_url = f"https://www.topjobs.lk/employer/JobAdvertismentServlet?rid={i}&ac={agentCode}&jc={joCode}&ec={empCode}&pg=applicant/vacancybyfunctionalarea.jsp"
            else:
                continue
            
            # 3. Extract Job Position
            h2_tag = row.find('h2')
            position = h2_tag.find('span').text.strip() if h2_tag and h2_tag.find('span') else "N/A"
            
            # 4. Extract Employer
            h1_tag = row.find('h1')
            employer = h1_tag.text.strip() if h1_tag else "N/A"
            
            # 5. Extract Dates
            tds = row.find_all('td')
            if len(tds) >= 6:
                opening_date = tds[4].text.strip()
                closing_date = tds[5].text.strip()
            else:
                opening_date = "N/A"
                closing_date = "N/A"
            
            # Save all extracted data to the DB, now including the newly constructed job_url
            save_job(conn, joCode, alert_string, job_url, position, employer, opening_date, closing_date)
            
        except Exception as e:
            print(f"Error processing row {row.get('id')}: {e}")

# --- MODULE 3: ORCHESTRATION ---
def run_scraper(target_url):
    conn = init_db()
    
    with sync_playwright() as p:
        browser = p.chromium.launch(headless=True)
        page = browser.new_page()
        
        print(f"Navigating to {target_url}...")
        page.goto(target_url)
        
        page.wait_for_selector('tbody tr#tr0') 
        html_content = page.content()
        extract_jobs_from_html(html_content, conn)
        
        browser.close()
    
    conn.close()
    print("Scraping cycle complete.")

if __name__ == "__main__":
    TARGET_URL = "https://www.topjobs.lk/applicant/vacancybyfunctionalarea.jsp?FA=HNS" 
    run_scraper(TARGET_URL)