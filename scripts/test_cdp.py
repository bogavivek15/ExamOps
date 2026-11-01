import subprocess
import time
import urllib.request
import json

chrome_path = r"C:\Program Files\Google\Chrome\Application\chrome.exe"
proc = subprocess.Popen([
    chrome_path,
    "--headless=new",
    "--remote-debugging-port=9222",
    "--disable-gpu",
    r"--user-data-dir=C:\Users\USER\AppData\Local\Temp\chrome_cdp",
])

print("Launched Chrome with PID:", proc.pid)
time.sleep(2)

try:
    resp = urllib.request.urlopen("http://127.0.0.1:9222/json/version", timeout=5)
    print("CDP Version response:", json.loads(resp.read()))
finally:
    proc.terminate()

