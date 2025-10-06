import os
import xml.etree.ElementTree as ET

import requests

token = os.getenv("ENTSOE_TOKEN")

result = requests.get(
    f"https://web-api.tp.entsoe.eu/api?securityToken={token}&documentType=A44&contract_MarketAgreement.type=A01&out_Domain=10Y1001A1001A82H&in_Domain=10Y1001A1001A82H&periodStart=202507250000&periodEnd=202507252359"
)

with open("results.xml", "w") as f:
    f.write(result.text)

parsed_xml = ET.parse(result.text)
# print(parsed_xml)
