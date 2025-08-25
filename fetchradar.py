import requests

OUTPUT_PNG = "gh-pages/radar.png"
OUTPUT_KML = "gh-pages/radar.kml"

# WMS GetMap request
url = (
    "https://opengeo.ncep.noaa.gov/geoserver/conus/conus_bref_qcd/wms"
    "?service=WMS&version=1.3.0&request=GetMap"
    "&layers=conus_bref_qcd&styles=&crs=EPSG:4326"
    "&bbox=-125,23,-66,50&width=1024&height=512&format=image/png"
)

print("Fetching radar image")
r = requests.get(url)
r.raise_for_status()

with open(OUTPUT_PNG, "wb") as f:
    f.write(r.content)

# Write the KML overlay
kml = f"""<?xml version="1.0" encoding="UTF-8"?>
<kml xmlns="http://www.opengis.net/kml/2.2">
  <Document>
    <name>NOAA Radar (CONUS)</name>
    <GroundOverlay>
      <name>Radar Composite</name>
      <Icon>
        <href>radar.png</href>
      </Icon>
      <LatLonBox>
        <north>50</north>
        <south>23</south>
        <east>-66</east>
        <west>-125</west>
      </LatLonBox>
    </GroundOverlay>
  </Document>
</kml>
"""

with open(OUTPUT_KML, "w") as f:
    f.write(kml)

print("Radar overlay KML written.")

