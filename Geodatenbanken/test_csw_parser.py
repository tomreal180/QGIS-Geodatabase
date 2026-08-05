from types import SimpleNamespace

from test import extract_geo_service_urls


def test_extract_geo_service_urls_skips_none_and_non_dict_entries():
    record = SimpleNamespace(
        title="Test record",
        uris=[None, {"protocol": "OGC:WMS", "url": "https://example.com/wms"}, "ignored"],
    )

    assert extract_geo_service_urls(record) == [("OGC:WMS", "https://example.com/wms")]


def test_extract_geo_service_urls_handles_missing_uris():
    record = SimpleNamespace(title="Test record")

    assert extract_geo_service_urls(record) == []
