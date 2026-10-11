import os
from playwright.sync_api import sync_playwright

rec_dir = "C:/Users/DELL/geo_shorts_factory/test_record"
os.makedirs(rec_dir, exist_ok=True)

with sync_playwright() as p:
    browser = p.chromium.launch()
    context = browser.new_context(
        viewport={"width": 1080, "height": 1920},
        record_video_dir=rec_dir,
        record_video_size={"width": 1080, "height": 1920}
    )
    page = context.new_page()
    page.set_content("""
    <!DOCTYPE html>
    <html>
    <body style="background:#111;color:#fff;display:flex;align-items:center;justify-content:center;height:100vh;margin:0;">
        <h1 style="font-size:80px;font-family:sans-serif;">ANIMATION TEST</h1>
    </body>
    </html>
    """)
    page.wait_for_timeout(1500)
    context.close()
    browser.close()

files = os.listdir(rec_dir)
print("Recorded files:", files)
