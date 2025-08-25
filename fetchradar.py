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
with open(OU
