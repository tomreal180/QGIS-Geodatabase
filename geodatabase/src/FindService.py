import json
import os
import sys
from pathlib import Path
import urllib3

from owslib.csw import CatalogueServiceWeb
from owslib.fes import  And, PropertyIsLike, Not
from owslib.util import Authentication

urllib3.disable_warnings(urllib3.exceptions.InsecureRequestWarning)
# from  import extract_ogc_layers
dir = os.path.dirname(__file__)
def fetch_csw_services(city_name=None, keyword=None):
    service_urls = json.loads(Path(os.path.join(dir,"data", "service_url.json")).read_text(encoding="utf-8"))
    csw_url = service_urls.get(city_name)
    csw = CatalogueServiceWeb(csw_url, auth=Authentication(verify=False), timeout=10)
    print(f"Connected to CSW GDI-DE version {csw.version}")
    city_filter = None
    if city_name == 'Hamburg':
        city_filter = PropertyIsLike(propertyname='csw:AnyText', literal="%hamburg%", wildCard="%")
    elif city_name == 'Sachsen-Anhalt':
        city_filter = PropertyIsLike(propertyname='csw:AnyText', literal="%sachsen-anhalt%", wildCard="%")
    elif city_name == 'Brandenburg':
        city_filter = PropertyIsLike(propertyname='csw:AnyText', literal="%brandenburg%", wildCard="%")
    elif city_name == 'Bremen':
        city_filter = PropertyIsLike(propertyname='csw:AnyText', literal="%bremen%", wildCard="%")
    elif city_name == 'Mecklenburg-Vorpommern':
        city_filter = PropertyIsLike(propertyname='csw:AnyText', literal="%mecklenburg-vorpommern%", wildCard="%")
    elif city_name == 'Hessen':
        city_filter = PropertyIsLike(propertyname='csw:AnyText', literal="%hessen%", wildCard="%")
    elif city_name == 'Saarland':
        city_filter = PropertyIsLike(propertyname='csw:AnyText', literal="%saarland%", wildCard="%")
    elif city_name == 'Sachsen':
        # 1. Find Sachsen
        sachsen_base = PropertyIsLike(
            propertyname='csw:AnyText', 
            literal="%sachsen%", 
            wildCard="%"
        )
        # 2. Exclude Niedersachsen
        not_nieder = Not([PropertyIsLike(
            propertyname='csw:AnyText', 
            literal="%niedersachsen%", 
            wildCard="%"
        )])
        # 3. Exclude Sachsen-Anhalt
        not_anhalt = Not([PropertyIsLike(
            propertyname='csw:AnyText', 
            literal="%anhalt%", 
            wildCard="%"
        )])
        
        # 4. Combine: Take Sachsen AND (NOT Niedersachsen) AND (NOT Sachsen-Anhalt)
        city_filter = And([sachsen_base, not_nieder, not_anhalt])
    elif city_name == 'Rheinland-Pfalz':
        city_filter = PropertyIsLike(propertyname='csw:AnyText', literal="%rheinland%", wildCard="%")
        # rlp_bbox_coords = [6.12, 48.97, 8.51, 50.94]
        # city_filter = BBox(rlp_bbox_coords)
    elif city_name == 'Nordrhein-Westfalen':
        city_filter = PropertyIsLike(propertyname='csw:AnyText', literal="%nordrhein%", wildCard="%")
    elif city_name == 'Baden-Württemberg':
        city_filter = PropertyIsLike(propertyname='dc:title', literal="%BW%", wildCard="%")



    title_filter = None
    filter = None
    if keyword:
        title_filter = PropertyIsLike(propertyname="dc:title", literal=f"%{keyword}%", wildCard="%")
        if city_filter:
            filter = And([title_filter, city_filter])
        else:
            filter = title_filter
        csw.getrecords2(
            typenames="csw:Record",
            esn="full",
            constraints=[filter],
            maxrecords=200
        )
    else:
        if city_filter:
            filter = city_filter
            csw.getrecords2(
                typenames="csw:Record",
                esn="full",
                constraints=[filter],
                maxrecords=200
            )
        else:
            csw.getrecords2(
                typenames="csw:Record",
                esn="full",
                maxrecords=200
            )

    
    results = set()
    urls_checked = set()
    for rec_id, record in csw.records.items():
        # print(record.uris)
        urls = extract_geo_service_urls(record)
        if urls:
            # print(record.title)
            for protocol, url in urls:
                if url in urls_checked:
                    continue
                else:
                    print(f"   [Link/Protocol: {protocol}] {url}")
                    results.add((
                                    record.title,
                                    protocol,
                                    url
                                ))
                    urls_checked.add(url)
    return results
        



def extract_geo_service_urls(record):
    service_urls = []

    if not getattr(record, "uris", None):
        return service_urls

    for uri in record.uris:
        if not isinstance(uri, dict):
            continue
        protocol = str(uri.get("protocol", "")).upper()
        url = str(uri.get("url", ""))
        lowered_url = url.lower()

        if "WMS" in protocol or "WFS" in protocol or "wms" in lowered_url or "wfs" in lowered_url:
            if not protocol or ("WMS" not in protocol and "WFS" not in protocol):
                protocol = "WMS" if "wms" in lowered_url else "WFS" if "wfs" in lowered_url else ""

            else:
                protocol = "WMS" if "WMS" in protocol else "WFS" if "WFS" in protocol else ""
            service_urls.append((protocol, url))


    return service_urls


# if __name__ == "__main__":
#     fetch_csw_services(city_name="Bremen", keyword="ALKIS")
