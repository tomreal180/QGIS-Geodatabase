import json
import os
import sys
from pathlib import Path
import urllib3

from owslib.csw import CatalogueServiceWeb
from owslib.fes import  And, PropertyIsLike, Not, Or
from owslib.util import Authentication
import concurrent.futures

urllib3.disable_warnings(urllib3.exceptions.InsecureRequestWarning)


dir = os.path.dirname(__file__)
def fetch_csw_services(city_name=None, keyword=None):
    """
    Fetches services from a CSW endpoint based on the provided city name and keyword.
    Args:
        city_name (str): The name of the city to filter services by.
        keyword (str): A keyword to filter services by title.
    Returns:
        set: A set of tuples containing the service title, protocol, and URL.
    """

    # Load the service URLs from the JSON file
    service_urls = json.loads(Path(os.path.join(dir,"data", "service_url.json")).read_text(encoding="utf-8"))
    csw_url = service_urls.get(city_name)
    csw = CatalogueServiceWeb(csw_url, auth=Authentication(verify=False), timeout=10)
    print(f"Connected to CSW GDI-DE version {csw.version}")
    city_filter = None

    if city_name == 'Hamburg':
        city_filter = PropertyIsLike(propertyname='csw:AnyText', literal="%hamburg%", wildCard="%")
    elif city_name == 'Sachsen-Anhalt':
        city_filter = PropertyIsLike(propertyname='csw:AnyText', literal="%anhalt%", wildCard="%")
    elif city_name == 'Brandenburg':
        city_filter = PropertyIsLike(propertyname='csw:AnyText', literal="%brandenburg%", wildCard="%")
    elif city_name == 'Bremen':
        bremen_base = PropertyIsLike(propertyname='csw:AnyText', literal="%bremen%", wildCard="%")
        not_nieder = Not([PropertyIsLike(
                        propertyname='csw:AnyText', 
                        literal="%niedersachsen%", 
                        wildCard="%"
                     )])
        city_filter = And([bremen_base, not_nieder])
        
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
    elif city_name == 'Schleswig-Holstein':
        city_filter = PropertyIsLike(propertyname='csw:AnyText', literal="%schleswig%", wildCard="%")
    # elif city_name == 'Deutschland':
    #     deutsch_filter = PropertyIsLike(propertyname='dc:title', literal="%deutschland%", wildCard="%")
    #     englisch_filter = PropertyIsLike(propertyname='dc:title', literal="%germany%", wildCard="%")
    #     city_filter = Or([deutsch_filter, englisch_filter])

    
    # If a keyword is provided, create a title filter and combine it with the city filter if it exists
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

    # Process the records concurrently to extract service URLs
    results = set()
    urls_checked = set()
    with concurrent.futures.ThreadPoolExecutor(max_workers=10) as executor:
        future_to_result = {
            executor.submit(process_single_record, record): 
            record for record in csw.records.values()
        }

        for future in concurrent.futures.as_completed(future_to_result):
            try:
                record, urls = future.result()
                if urls:
                    for protocol, url in urls:
                        # print(f"Found service: {record.title} - {protocol}")
                        if url in urls_checked:
                            continue
                        else:
                            results.add((
                                record.title,
                                protocol,
                                url
                            ))
                            urls_checked.add(url)
                            
            except Exception as e:
                print(f"Error when processing record {record.title}: {e}")

    return results
        
def process_single_record(record):
   """
    Process a single CSW record to extract service URLs.
    Args:
        record: A CSW record object.
    Returns:
        tuple: A tuple containing the record and a list of service URLs.
    """
   return record, extract_geo_service_urls(record)


def extract_geo_service_urls(record):
    """
    Extracts geospatial service URLs from a CSW record.
    Args:
        record: A CSW record object.
    Returns:
        list: A list of tuples containing the protocol and URL of geospatial services.
    """
    service_urls = []

    if not getattr(record, "uris", None):
        return service_urls

    for uri in record.uris:
        if not isinstance(uri, dict):
            continue
        protocol = str(uri.get("protocol", "")).upper()
        url = str(uri.get("url", ""))
        lowered_url = url.lower()

        if "WMS" in protocol or "WFS" in protocol or "WCS" in protocol or "WMTS" in protocol or "wms" in lowered_url or "wfs" in lowered_url or "wcs" in lowered_url or "wmts" in lowered_url:
            if not protocol or ("WMS" not in protocol and "WFS" not in protocol and "WCS" not in protocol and "WMTS" not in protocol):
                protocol = "WMS" if "wms" in lowered_url else "WFS" if "wfs" in lowered_url else "WCS" if "wcs" in lowered_url else "WMTS" if "wmts" in lowered_url else ""

            else:
                protocol = "WMS" if "WMS" in protocol else "WFS" if "WFS" in protocol else "WCS" if "WCS" in protocol else "WMTS" if "WMTS" in protocol else ""
            service_urls.append((protocol, url))


    return service_urls


if __name__ == "__main__":
    fetch_csw_services(city_name="Berlin", keyword="ALKIS")

