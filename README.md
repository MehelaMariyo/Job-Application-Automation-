# Job-Application-Automation-

## System Steup

```bash
conda activate -n job python=3.11 -y
```
```bash
conda activate job
```
```bash
pip install -r reqirment.txt
```

## Database Setup

Used python `sqlite3` library to define the schema of the databases
Used two separate tables for store data
- topjob_listing.db
    - job_ref_no
    - alert_string
    - job_url (constructed using alert_string)
    - position
    - employer
    - opening_date
    - closing_date

- topjob_images.db
    Created with going trough every single URL that were constructed in the `topjob_listing.db` and scraping the image bytes and stored with following additional columns:
    - job_ref_no
    - position
    - employer
    - job_url
    - image_bytes

## Web Sracping Setup

For web scraping python `BeautifulSoup` library was used.
- First given target URL HTML was scraping to populate `topjob_listing.db`
- Then after using constructed URL `image_bytes` were scraped. 