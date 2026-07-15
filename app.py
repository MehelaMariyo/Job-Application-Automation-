from src.database.database_listings import *
from src.database.database_images import *
from src.sracping.scrap_listings import *
from src.sracping.scrap_images import *


if __name__ == "__main__":
    TARGET_URL = "https://www.topjobs.lk/applicant/vacancybyfunctionalarea.jsp?jst=OPEN"
    run_scraper(TARGET_URL)
    run_image_pipeline()