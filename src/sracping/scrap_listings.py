import re
from bs4 import BeautifulSoup
from playwright.sync_api import sync_playwright
from database import *


def extract_jobs_from_html(html_content, conn):
    soup = BeautifulSoup(html_content, 'html.parser')
    rows = soup.find_all('tr', id=re.compile(r'^tr\d+$'))
    
    for row in rows:
        try:
            onclick_text = row.get('onclick', '')
            match = re.search(r"createAlert\((.*?)\)", onclick_text) # type: ignore
            
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
            position = h2_tag.find('span').text.strip() if h2_tag and h2_tag.find('span') else "N/A" # type: ignore
            
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
