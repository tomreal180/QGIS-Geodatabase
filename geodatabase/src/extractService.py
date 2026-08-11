import ssl
import urllib.error
import urllib.request
import xml.etree.ElementTree as ET


# def _build_ssl_context(verify_ssl=True):
#     if not verify_ssl:
#         return ssl._create_unverified_context()

#     try:
#         import certifi

#         return ssl.create_default_context(cafile=certifi.where())
#     except Exception:
#         # Fallback to system trust store if certifi is unavailable.
#         return ssl.create_default_context()


def extract_ogc_layers(base_url, service_type="WFS", verify_ssl=True, timeout=30):
    """
    Hàm đọc GetCapabilities và lấy danh sách Title, Name/typename
    """
    # Remove query parameters from the base URL if present
    clean_url = base_url.split('?')[0]
    if "geoportal.rlp" in base_url :
        capabilities_url = base_url
    else:
    # The GetCapabilities URL
        capabilities_url = f"{clean_url}?request=GetCapabilities&service={service_type}&version=1.1.0"
    
    # tag containing layer information differs between WMS and WFS
    target_tag = 'FeatureType' if service_type.upper() == 'WFS' else 'Layer'
    
    results = []
    try:
        # Simulate User-Agent to avoid being rejected by the server
        req = urllib.request.Request(capabilities_url, headers={'User-Agent': 'Mozilla/5.0'})
        response = urllib.request.urlopen(
            req,
            context=ssl.SSLContext(),
            timeout=timeout,
        )

        xml_data = response.read()
        
        # Parse the XML structure
        root = ET.fromstring(xml_data)
        # Iterate through all tags, ignoring the Namespace (usually in the form {http://...}Name)
        for elem in root.iter():
            
            tag = elem.tag.split('}')[-1] 
            
            if tag == target_tag:
                layer_data = {}
                for child in elem:
                    child_tag = child.tag.split('}')[-1]
                    print(f"Child tag: {child_tag}, text: {child.text}")
                    if 'Name' in child_tag:
                        layer_data['typename'] = child.text
                    elif 'Title' in child_tag:
                        layer_data['title'] = child.text
                layer_data['base_url'] = clean_url
                
                # Only save if there is a typename (to avoid capturing general Layer tags)
                if layer_data.get('typename'):
                    results.append(layer_data)
                    
        return results
        
    except urllib.error.URLError as e:
        reason = getattr(e, "reason", None)
        if isinstance(reason, ssl.SSLCertVerificationError):
            print(
                f"SSL Certificate error when accessing {base_url}: {reason}."
            )
        else:
            print(f"Error accessing {base_url}: {e}")
        return []
    except Exception as e:
        print(f"Error accessing {base_url}: {e}")
        return []

# # --- Test ---
# test_url = "https://www.geoportal.rlp.de/mapbender/php/wfs.php?INSPIRE=1&FEATURETYPE_ID=5064&REQUEST=GetCapabilities&SERVICE=WFS&VERSION=2.0.0"
# print("Đang quét WMS...")
# layers = extract_ogc_layers(test_url, "WFS")

# for layer in layers:
#     print(f"- Title: {layer.get('title')}")
#     print(f"  Technical name (Typename): {layer.get('typename')}\n")
#     print(f"  Original URL: {layer.get('base_url')}\n")