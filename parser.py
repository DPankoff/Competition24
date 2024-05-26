# файл для парсинга по ссылке 
# возвращает список сайтов для проверки

import requests
import xml.etree.ElementTree as ET

def parse_xml_from_url(url):
    response = requests.get(url)
    if response.status_code == 200:
        xml_content = response.content
        root = ET.fromstring(xml_content)
        
        # Парсим XML и извлекаем нужные данные
        namespaces = {'ns': 'http://www.sitemaps.org/schemas/sitemap/0.9'}
        urls = []
        for url in root.findall('ns:url', namespaces):
            loc = url.find('ns:loc', namespaces).text
            lastmod = url.find('ns:lastmod', namespaces).text if url.find('ns:lastmod', namespaces) else 'N/A'
            urls.append({'loc': loc, 'lastmod': lastmod})
        
        return urls
    else:
        print(f"Failed to retrieve XML. Status code: {response.status_code}")
        return None


url = 'https://www.trustpilot.com/trust/sitemaps/domain_en-us.xml'
parsed_urls = parse_xml_from_url(url)

print(parsed_urls)