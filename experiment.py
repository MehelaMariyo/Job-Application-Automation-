from playwright.sync_api import sync_playwright
import io
from PIL import Image
import base64

def get_job_image(job_url):
    with sync_playwright() as p:
        browser = p.chromium.launch(headless=True)
        page = browser.new_page()
        page.goto(job_url)
        
        # Topjobs often puts the image inside an iframe with an ID like 'vacancy-frame'
        # or directly as an img tag with a specific class. 
        # You will need to inspect the page to get the exact selector.
        
        # Example: Locate the main advertisement image
        image_locator = page.locator("img.shrunk-image") # Replace with actual selector
        
        # Capture the image directly into memory (no need to save to disk)
        image_bytes = image_locator.screenshot()
        
        browser.close()
        return image_bytes
    


def show_image_from_bytes(image_bytes):
    # Convert the raw bytes into a format Pillow can read
    image_stream = io.BytesIO(image_bytes)
    
    # Open the image
    img = Image.open(image_stream)
    
    # This will automatically pop open your OS's default image viewer 
    # (like Windows Photo Viewer or Mac Preview)
    img.show()
    print("Image displayed successfully.")


image_bytes = get_job_image("https://www.topjobs.lk/employer/JobAdvertismentServlet?rid=1&ac=DEFZZZ&jc=0001524395&ec=DEFZZZ&pg=applicant/vacancybyfunctionalarea.jsp") # Replace with an actual job URL
#show_image_from_bytes(image_bytes)

