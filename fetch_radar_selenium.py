import requests
import xml.etree.ElementTree as ET
from selenium import webdriver
from selenium.webdriver.edge.options import Options
import time
from PIL import Image

# GetCapabilities URL
cap_url = "https://opengeo.ncep.noaa.gov/geoserver/conus/conus_bref_qcd/ows?service=WMS&request=GetCapabilities&version=1.3.0"
cap_resp = requests.get(cap_url)
root = ET.fromstring(cap_resp.content)
ns = {'wms': 'http://www.opengis.net/wms'}
time_dim = root.find(".//wms:Dimension[@name='time']", ns)
timestamps = time_dim.text.split(",") if time_dim is not None else []
latest_time = timestamps[-1].strip() if timestamps else ""
if not latest_time:
    raise Exception("Could not find timestamp")

# Build GetMap URL with TRANSPARENT=true and latest timestamp
getmap_url = (
    "https://opengeo.ncep.noaa.gov/geoserver/conus/conus_bref_qcd/ows"
    "?SERVICE=WMS&VERSION=1.3.0&REQUEST=GetMap&LAYERS=conus_bref_qcd"
    "&STYLES=&CRS=EPSG:3857&BBOX=-14471533.80310966,2273348.7246112144,"
    "-6678812.50227643,7361866.113023452&WIDTH=1024&HEIGHT=768"
    "&FORMAT=image/png&TRANSPARENT=true&TIME=" + latest_time
)

# Selenium Edge headless options
opts = Options()
opts.add_argument("--headless")
opts.add_argument("--disable-gpu")
opts.add_argument("--new-window")
opts.add_argument("--force-color-profile=srgb")

driver = webdriver.Edge(options=opts)
driver.set_window_size(1024, 768)
driver.get(getmap_url)
time.sleep(5)  # ensure tile loads fully
driver.save_screenshot("conus_bref_qcd.png")
driver.quit()

# Apply transparency filtering (keep image size intact)
img = Image.open("conus_bref_qcd.png").convert("RGBA")
filtered = []
for r,g,b,a in img.getdata():
    # black frame (~14 ±5)
    if 9 <= r <= 19 and 9 <= g <= 19 and 9 <= b <= 19:
        filtered.append((r,g,b,0))
    # off-white (threshold >= 230)
    elif r >= 230 and g >= 230 and b >= 230:
        filtered.append((r,g,b,0))
    else:
        filtered.append((r,g,b,a))
img.putdata(filtered)
img.save("conus_bref_qcd.png")
print("Saved transparent conus_bref_qcd.png using timestamp:", latest_time)
