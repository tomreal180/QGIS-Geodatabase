import ssl
import urllib.error
import urllib.request
import xml.etree.ElementTree as ET


def _build_ssl_context(verify_ssl=True):
    if not verify_ssl:
        return ssl._create_unverified_context()

    try:
        import certifi

        return ssl.create_default_context(cafile=certifi.where())
    except Exception:
        # Fallback to system trust store if certifi is unavailable.
        return ssl.create_default_context()


def extract_ogc_layers(base_url, service_type="WFS", verify_ssl=True, timeout=30):
    """
    Hàm đọc GetCapabilities và lấy danh sách Title, Name/typename
    """
    # Xóa các param thừa nếu có để lấy URL gốc
    clean_url = base_url.split('?')[0]
    
    # Tạo URL GetCapabilities
    capabilities_url = f"{clean_url}?request=GetCapabilities&service={service_type}&version=1.1.0"
    
    # Thẻ chứa thông tin layer khác nhau giữa WMS và WFS
    target_tag = 'FeatureType' if service_type.upper() == 'WFS' else 'Layer'
    
    results = []
    try:
        # Giả lập User-Agent để tránh bị server từ chối
        req = urllib.request.Request(capabilities_url, headers={'User-Agent': 'Mozilla/5.0'})
        response = urllib.request.urlopen(
            req,
            context=_build_ssl_context(verify_ssl=verify_ssl),
            timeout=timeout,
        )

        xml_data = response.read()
        
        # Đọc cấu trúc XML
        root = ET.fromstring(xml_data)
        # Duyệt qua tất cả các thẻ, bỏ qua Namespace (thường có dạng {http://...}Name)
        for elem in root.iter():
            
            tag = elem.tag.split('}')[-1] 
            
            if tag == target_tag:
                layer_data = {}
                for child in elem:
                    child_tag = child.tag.split('}')[-1]
                    if child_tag == 'Name':
                        layer_data['typename'] = child.text
                    elif child_tag == 'Title':
                        layer_data['title'] = child.text
                layer_data['base_url'] = clean_url
                
                # Chỉ lưu nếu có typename (tránh lấy nhầm các thẻ Layer tổng)
                if layer_data.get('typename'):
                    results.append(layer_data)
                    
        return results
        
    except urllib.error.URLError as e:
        reason = getattr(e, "reason", None)
        if isinstance(reason, ssl.SSLCertVerificationError):
            print(
                f"Lỗi SSL khi tải {base_url}: {reason}. "
                "Hãy cài certifi (pip install certifi) hoặc cập nhật chứng chỉ hệ thống."
            )
        else:
            print(f"Lỗi khi tải {base_url}: {e}")
        return []
    except Exception as e:
        print(f"Lỗi khi tải {base_url}: {e}")
        return []

# # --- CHẠY THỬ VỚI WFS BERLIN ---
# test_url = "https://gdi.berlin.de/services/wfs/amarex_potenziale"
# print("Đang quét WFS...")
# layers = extract_ogc_layers(test_url, "WFS")

# for layer in layers:
#     print(f"- Hiển thị (Title): {layer.get('title')}")
#     print(f"  Tên kỹ thuật (Typename): {layer.get('typename')}\n")
#     print(f"  URL gốc: {layer.get('base_url')}\n")