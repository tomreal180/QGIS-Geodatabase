import json
import os
import inspect
import sys
from pathlib import Path

from owslib.csw import CatalogueServiceWeb
from owslib.fes import PropertyIsGreaterThanOrEqualTo, PropertyIsLessThanOrEqualTo, And, PropertyIsLike
from owslib.util import Authentication

if hasattr(sys.stdout, "reconfigure"):
    sys.stdout.reconfigure(encoding="utf-8")


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


def record_contains_year(record, year=2025):
    values = []

    def collect(value):
        if value is None:
            return
        if isinstance(value, str):
            values.append(value)
        elif isinstance(value, (list, tuple, set)):
            for item in value:
                collect(item)
        elif isinstance(value, dict):
            for item in value.values():
                collect(item)
        elif hasattr(value, "__dict__"):
            for item in vars(value).values():
                collect(item)

    collect(record)
    text = " ".join(values).lower()
    return str(year) in text


def save_results_to_json(results, file_name="csw_results.json"):
    output_path = Path(__file__).with_name(file_name)
    output_path.write_text(json.dumps(results, ensure_ascii=False, indent=2), encoding="utf-8")
    print(f"\nSaved {len(results)} results to {output_path}")


def _resolve_csw_verify():
    if os.getenv("CSW_INSECURE_SKIP_VERIFY", "").strip().lower() in {"1", "true", "yes"}:
        return False

    try:
        import certifi

        return certifi.where()
    except Exception:
        return True


def _create_csw_client(csw_url, timeout=10):
    verify = _resolve_csw_verify()
    kwargs = {}

    try:
        sig = inspect.signature(CatalogueServiceWeb)
        supported = set(sig.parameters.keys())
    except (TypeError, ValueError):
        supported = set()

    if "auth" in supported:
        kwargs["auth"] = Authentication(verify=verify)
    if "verify" in supported:
        kwargs["verify"] = verify
    if "timeout" in supported:
        kwargs["timeout"] = timeout

    if kwargs:
        return CatalogueServiceWeb(csw_url, **kwargs)

    # Last-resort compatibility path for very old OWSLib versions.
    try:
        return CatalogueServiceWeb(csw_url, timeout=timeout)
    except TypeError:
        return CatalogueServiceWeb(csw_url)


def fetch_csw_services(keyword=None):
    csw_url = 'https://gdi.berlin.de/geonetwork/srv/ger/csw'
    csw = CatalogueServiceWeb(csw_url, auth=Authentication(verify=False), timeout=10)

    print(f"Đã kết nối CSW phiên bản {csw.version}")

    # 1. Tạo danh sách các bộ lọc (Filter)
    filters = []

    # Bộ lọc cho năm 2025 (tùy chọn, có thể bỏ nếu không cần)
    # Sử dụng trường 'dc:date' chuẩn của Dublin Core (áp dụng cho csw:Record)
    start_date = PropertyIsGreaterThanOrEqualTo(propertyname='dc:date', literal='2025-01-01')
    end_date = PropertyIsLessThanOrEqualTo(propertyname='dc:date', literal='2025-12-31')
    filters.extend([start_date, end_date])

    # Thêm bộ lọc từ khóa nếu có
    if keyword:
        print(f"Đang tìm kiếm với từ khóa: '{keyword}'")
        # wildCard='*' cho phép tìm kiếm bất kỳ vị trí nào trong chuỗi
        title_filter = PropertyIsLike(propertyname='dc:title', literal=f'*{keyword}*', wildCard='*')
        filters.append(title_filter)

    # Kết hợp tất cả các bộ lọc bằng toán tử AND
    final_filter = And(filters)

    # 2. Truy vấn CSW và gắn thêm tham số constraints
    csw.getrecords2(
        typenames='csw:Record',
        esn='full',
        constraints=[final_filter],
    )

    results = []

    for rec_id, record in csw.records.items():
        service_urls = extract_geo_service_urls(record)

        if service_urls:
            record_data = {
                "id": rec_id,
                "title": getattr(record, "title", ""),
                "services": [
                    {"protocol": protocol, "url": url}
                    for protocol, url in service_urls
                ],
            }
            results.append(record_data)
            print(f"\n🌍 {record_data['title']}")
            for service in record_data["services"]:
                print(f"   [Link/Protocol: {service['protocol']}] {service['url']}")

    if not results:
        print("\nNo WFS/WMS records from 2025 were found.")
    else:
        save_results_to_json(results)


if __name__ == "__main__":
    # Ví dụ: tìm các bản ghi có từ "Alkis" trong tiêu đề
    fetch_csw_services(keyword="Flächenpotenziale")
    