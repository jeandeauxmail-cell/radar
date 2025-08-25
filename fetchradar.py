import os
import requests
import xml.etree.ElementTree as ET
from PIL import Image

OUTPUT_DIR = "site"
os.makedirs(OUTPUT_DIR, exist_ok=True)

OUTPUT_PNG = f"{OUTPUT_DIR}/radar.png"
OUTPUT_KML = f"{OUTPUT_DIR}/radar.kml"

# Step 1: GetCapabilities and latest timestamp
cap_url = "https://opengeo.ncep.noaa.gov/geoserver/conus/conus_bref_qcd/ows?service=WMS&request=GetCapabilities&version=1.3.0"
cap_resp = requests.get(cap_url)
root = ET.fromstring(cap_resp.content)
ns = {'wms': 'http://www.opengis.net/wms'}

time_dim = root.find(".//wms:Dimension[@name='time']", ns)
timestamps = time_dim.text.split(",") if time_dim is not None else []
latest_time = timestamps[-1].strip() if timestamps else ""
if not latest_time:
    raise Exception("Could not find timestamp in WMS capabilities")

# Step 2: Build GetMap URL
getmap_url = (
    "https://opengeo.ncep.noaa.gov/geoserver/conus/conus_bref_qcd/ows"
    "?SERVICE=WMS&VERSION=1.3.0&REQUEST=GetMap&LAYERS=conus_bref_qcd"
    "&STYLES=&CRS=EPSG:3857&BBOX=-14471533.80310966,2273348.7246112144,"
    "-6678812.50227643,7361866.113023452&WIDTH=1024&HEIGHT=768"
    "&FORMAT=image/png&TRANSPARENT=true&TIME=" + latest_time
)

# Step 3: Fetch PNG
resp = requests.get(getmap_url)
with open(OUTPUT_PNG, "wb") as f:
    f.write(resp.content)

# Step 4: Apply transparency filtering
img = Image.open(OUTPUT_PNG).convert("RGBA")
filtered = []
for r,g,b,a in img.getdata():
    # black frame (~14 ±5)
    if 9 <= r <= 19 and 9 <= g <= 19 and 9 <= b <= 19:
        filtered.append((r,g,b,0))
    # off-white background (>=230)
    elif r >= 230 and g >= 230 and b >= 230:
        filtered.append((r,g,b,0))
    else:
        filtered.append((r,g,b,a))
img.putdata(filtered)
img.save(OUTPUT_PNG)

print("✅ Saved transparent radar overlay using timestamp:", latest_time)

# Step 5: Write KML GroundOverlay
kml = f"""<?xml version="1.0" encoding="UTF-8"?>
<kml xmlns="http://www.opengis.net/kml/2.2">
  <Document>
    <name>Radar Overlay</name>
    <GroundOverlay>
      <name>Radar {latest_time}</name>
      <Icon>
        <href>radar.png</href>
      </Icon>
      <LatLonBox>
        <north>60</north>
        <south>20</south>
        <east>-60</east>
        <west>-130</west>
      </LatLonBox>
    </GroundOverlay>
  </Document>
</kml>"""

with open(OUTPUT_KML, "w") as f:
    f.write(kml)
