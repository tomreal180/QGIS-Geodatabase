from qgis.PyQt.QtCore import QThread, pyqtSignal
from .FindService import fetch_csw_services
import ssl
import urllib.error
import urllib.request
import xml.etree.ElementTree as ET
import concurrent.futures



class SearchWorker(QThread):
    finished = pyqtSignal(list)  # Signal to emit the results
    progress_update = pyqtSignal(int)  # Signal to emit progress updates

    def __init__(self, city_name, keyword=None):
        super().__init__()
        self.city_name = city_name
        self.keyword = keyword

    def run(self):
        # Call the function to get extracted layers
        results = self.get_extracted_layers(self.city_name, self.keyword)
        # Emit the results when done
        self.finished.emit(results)

    def extract_ogc_layers(self, base_url, service_type="WFS", verify_ssl=True, timeout=30):

        # Remove any extra parameters from the URL to get the base URL
        clean_url = base_url.split('?')[0]
        
        # Create the GetCapabilities URL
        capabilities_url = f"{clean_url}?request=GetCapabilities&service={service_type}&version=1.1.0"
        
        # The tag containing layer information differs between WMS and WFS
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
                        if child_tag == 'Name':
                            layer_data['typename'] = child.text
                        elif child_tag == 'Title':
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

    def get_extracted_layers(self, city_name, keyword=None):
        Services = fetch_csw_services(city_name, keyword)
        extracted_layers = []
        total_steps = len(Services)

        if total_steps == 0:
            return extracted_layers

        completed_steps = 0

        with concurrent.futures.ThreadPoolExecutor(max_workers=10) as executor:
            future_to_service = {
                executor.submit(self.process_single_service, service): 
                service for service in Services
            }

            for future in concurrent.futures.as_completed(future_to_service):
                service_info = future_to_service[future]
                try:
                    result_layers = future.result()
                    if result_layers:
                        extracted_layers.extend(result_layers)

                except Exception as e:
                    print(f"Error processing service {service_info[2]}: {e}")
                completed_steps += 1
                percentage = int((completed_steps / total_steps) * 100)
                self.progress_update.emit(percentage)  # Emit progress update signal

        return extracted_layers

    def process_single_service(self,service_info):
            title, protocol, url = service_info
            layers = self.extract_ogc_layers(url, protocol)
            
            parsed_layers = []
            if layers:
                for layer in layers:
                    typename = layer.get('typename')
                    layer_title = layer.get('title')
                    base_url = layer.get('base_url')
                    parsed_layers.append({
                        "title": layer_title,
                        "protocol": protocol,
                        "url": base_url,
                        "typename": typename
                    })
            return parsed_layers