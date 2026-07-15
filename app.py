from database import *
from scraping import *

if __name__ == "__main__":
    run_scraper("https://www.topjobs.lk/applicant/vacancybyfunctionalarea.jsp?jst=OPEN")
    run_image_pipeline()