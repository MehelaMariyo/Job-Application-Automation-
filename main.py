import sqlite3

def verify_saved_image(job_ref_no_to_check):
    conn = sqlite3.connect('topjobs_images.db')
    cursor = conn.cursor()
    
    cursor.execute('SELECT image_bytes FROM job_details_with_images WHERE job_ref_no = ?', (job_ref_no_to_check,))
    row = cursor.fetchone()
    conn.close()
    
    if row and row[0]:
        # Write the binary blob back out to a physical file
        with open("verified_output.png", "wb") as file:
            file.write(row[0])
        print(f"[✓] Extracted image for {job_ref_no_to_check} and saved it as 'verified_output.png'")
    else:
        print("[-] No image found for that Reference Number.")

# Usage: Replace with a real ref number from your database run
verify_saved_image("0001524657")