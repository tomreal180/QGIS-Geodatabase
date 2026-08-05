import json
import sys
from pathlib import Path

from owslib.csw import CatalogueServiceWeb
from owslib.fes import PropertyIsGreaterThanOrEqualTo, PropertyIsLessThanOrEqualTo, And, PropertyIsLike
from test_extrac import extract_ogc_layers

def fetch_csw_services(city_name=None, keyword=None):
    service_urls = json.loads(Path("Service_url.json").read_text(encoding="utf-8"))
    csw_url = service_urls.get(city_name)
    csw = CatalogueServiceWeb(csw_url)

    if keyword:
        title_filter = PropertyIsLike(propertyname="dc:title", literal=f"%{keyword}%", wildCard="%")

        csw.getrecords2(
            typenames="csw:Record",
            esn="full",
            constraints=[title_filter],
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
        urls = extract_geo_service_urls(record)
        if urls:
            for protocol, url in urls:
                if url in urls_checked:
                    continue
                else:
                    # print(f"   [Link/Protocol: {protocol}] {url}")
                    results.add((
                                    record.title,
                                    protocol,
                                    url
                                ))
                    urls_checked.add(url)
    # json_output_path = Path(__file__).with_name("csw_results.json")
    # json_output_path.write_text(json.dumps([{
    #                             "title": title,
    #                             "protocol": protocol,
    #                             "url": url
    #                         } for title, protocol, url in results], ensure_ascii=False, indent=2), encoding="utf-8")
    # print(f"\nSaved {len(results)} results to {json_output_path}")
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
            if not protocol:
                protocol = "WMS" if "wms" in lowered_url else "WFS" if "wfs" in lowered_url else ""
            service_urls.append((protocol, url))

    return service_urls

def get_extracted_layers(city_name, keyword=None):
    Services = fetch_csw_services(city_name, keyword)
    extracted_layers = []
    for title, protocol, url in Services:
        # print(f"\nĐang quét {protocol} tại {url}...")
        layers = extract_ogc_layers(url, protocol)
        if layers:
            for layer in layers:
                typename = layer.get('typename')
                title = layer.get('title')
                base_url = layer.get('base_url')
                extracted_layers.append({
                    "title": title,
                    "protocol": protocol,
                    "url": base_url,
                    "typename": typename
                })
                print(f"   - Hiển thị (Title): {title}")
                print(f"     Service Type (protocol): {protocol}")
                print(f"     Tên kỹ thuật (Typename): {typename}\n")
                print(f"     URL gốc: {base_url}\n")
        else:
            print(f"   Không tìm thấy layer nào tại {url}.")

    json_output_path = Path(__file__).with_name(f"{city_name}_extracted_layers.json")
    json_output_path.write_text(json.dumps(extracted_layers, ensure_ascii=False, indent=2), encoding="utf-8")
    print(f"\nSaved {len(extracted_layers)} extracted layers to {json_output_path}")


if __name__ == "__main__":
    # Ví dụ: tìm các bản ghi có từ "Alkis" trong tiêu đề
    # fetch_csw_services(city_name="Berlin", keyword="ALKIS")
    get_extracted_layers(city_name="Berlin", keyword="ALKIS")