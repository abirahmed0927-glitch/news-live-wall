from selenium import webdriver
from selenium.webdriver.common.by import By
from selenium.webdriver.support.ui import WebDriverWait
from selenium.webdriver.support import expected_conditions as EC
from selenium.webdriver.chrome.options import Options

import http.server
import socketserver
import threading

# =========================
# 1️⃣ Headless Chrome setup (ONLY for scraping)
# =========================
chrome_options = Options()
chrome_options.add_argument("--headless=new")
chrome_options.add_argument("--disable-gpu")
chrome_options.add_argument("--window-size=1920,1080")
chrome_options.add_argument("--log-level=3")

# =========================
# 2️⃣ YouTube Channel URLs
# =========================
urls = [
    "https://www.youtube.com/@somoynews360/streams",
    "https://www.youtube.com/@JamunaTVbd/streams",
    "https://www.youtube.com/@channel24digital/streams",
    "https://www.youtube.com/@IndependentTelevision/streams",
    "https://www.youtube.com/@dbcnewstv/streams",
    "https://www.youtube.com/@EkattorTelevision/streams",
    "https://www.youtube.com/@ekhontv/streams",
    "https://www.youtube.com/@RtvLiveBD/streams",
    "https://www.youtube.com/@channelionline/streams",
]

# =========================
# 3️⃣ Headless Selenium → collect live links
# =========================
driver = webdriver.Chrome(options=chrome_options)
wait = WebDriverWait(driver, 15)

live_links = []
l=1
for url in urls:
    driver.get(url)
    try:
        element = wait.until(
            EC.presence_of_element_located((By.ID, "video-title-link"))
        )
        link = element.get_attribute("href")
        live_links.append(link)
        print("Live found:",l,"/9")
    except:
        print("No live:", url)
        live_links.append(None)
    l = l+1

driver.quit()

# =========================
# 4️⃣ Extract VIDEO IDs
# =========================
video_ids = []

for link in live_links:
    if link and "watch?v=" in link:
        vid = link.split("watch?v=")[1].split("&")[0]
        video_ids.append(vid)

# =========================
# 5️⃣ Generate HTML (NO SCROLL)
# =========================
html_content = """
<!DOCTYPE html>
<html>
<head>
<meta charset="UTF-8">
<title>YouTube Live Grid</title>

<style>
html, body {
    margin: 0;
    padding: 0;
    height: 100%;
    background: #000;
    color: white;
    font-family: Arial, sans-serif;
    overflow: hidden;
}

h2 {
    margin: 6px 0;
    font-size: 18px;
    text-align: center;
}

.grid {
    display: grid;
    grid-template-columns: repeat(3, 1fr);
    grid-template-rows: repeat(3, 1fr);
    gap: 8px;
    padding: 8px;
    height: calc(100vh - 32px);
}

iframe {
    width: 100%;
    height: 100%;
    border: 1px solid #333;
}
</style>

</head>
<body>

<h2>Bangladesh Live News – 3×3 Wall</h2>

<div class="grid">
"""

for vid in video_ids:
    html_content += f"""
    <iframe
        src="https://www.youtube.com/embed/{vid}?autoplay=1&mute=1"
        allow="autoplay"
        allowfullscreen>
    </iframe>
    """

html_content += """
</div>

</body>
</html>
"""

with open("index.html", "w", encoding="utf-8") as f:
    f.write(html_content)

# =========================
# 6️⃣ Start Local Server
# =========================
PORT = 8000

def start_server():
    handler = http.server.SimpleHTTPRequestHandler
    with socketserver.TCPServer(("", PORT), handler) as httpd:
        print(f"Server running → http://localhost:{PORT}")
        httpd.serve_forever()

threading.Thread(target=start_server, daemon=True).start()

# =========================
# 7️⃣ Open FINAL grid (VISIBLE browser)
# =========================
driver = webdriver.Chrome()   # ❗ NOT headless
driver.get(f"http://localhost:{PORT}")
driver.maximize_window()

input("Press Enter to stop everything...")
