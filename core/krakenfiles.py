import requests
from bs4 import BeautifulSoup
import re

host = "https://krakenfiles.com"
headers = {'User-Agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/91.0.4472.124 Safari/537.36'}

def get_id(url):
    try:
        if "view/" in url and "/file" in url:
            return url.split("view/")[1].split("/file")[0]
        elif "/view/" in url:
            return url.split("/view/")[1].split("/")[0]
        else:
            # Coba ekstrak ID dari berbagai format URL
            patterns = [
                r"krakenfiles\.com/view/([a-zA-Z0-9]+)/",
                r"krakenfiles\.com/embed-video/([a-zA-Z0-9]+)",
                r"/([a-zA-Z0-9]{8,})/"
            ]
            
            for pattern in patterns:
                match = re.search(pattern, url)
                if match:
                    return match.group(1)
            
            # Jika tidak ditemukan pattern yang cocok, return empty string
            return ""
    except Exception as e:
        print(f"Error in getId: {e}")
        return ""

def get_stream(url):
    """Mendapatkan URL stream dari KrakenFiles dengan error handling"""
    try:
        # Validasi input
        if not url or not isinstance(url, str):
            return ""
        
        file_id = get_id(url)
        if not file_id:
            return ""
        
        # Coba beberapa endpoint
        endpoints = [
            f"{host}/embed-video/{file_id}",
            f"{host}/view/{file_id}",
        ]
        
        for endpoint in endpoints:
            try:
                response = requests.get(endpoint, headers=headers, timeout=10)
                if response.status_code == 200:
                    soup = BeautifulSoup(response.content, 'html.parser')
                    
                    # Multiple methods to extract stream URL
                    sources = [
                        soup.find("source"),
                        soup.find("video"),
                        soup.find("div", {"data-stream": True})
                    ]
                    
                    for source in sources:
                        if source and source.get("src"):
                            src = source.get("src")
                            if src.startswith("//"):
                                return "https:" + src
                            elif src.startswith("http"):
                                return src
                            else:
                                return "https://" + src.lstrip('/')
                        
                        if source and source.get("data-stream"):
                            return source.get("data-stream")
                
            except Exception as e:
                continue
        
        return ""
    except Exception as e:
        print(f"Error in get_stream: {e}")
        return ""



def short_link(url):
    """Meresolve shortlink dengan error handling yang lebih baik"""
    try:
        # Pastikan URL adalah string yang valid
        if not isinstance(url, str):
            url = str(url)
        
        # Bersihkan URL dari karakter yang tidak diinginkan
        url = url.strip().replace("'", "").replace('"', '')
        
        # Pastikan URL memiliki scheme yang valid
        if not url.startswith(('http://', 'https://')):
            url = 'https://' + url
        
        print(f"Processing URL: {url}")  # Debug info
        
        response = requests.get(url, headers=headers, timeout=10)
        soup = BeautifulSoup(response.text, 'html.parser')
        
        # Cari meta refresh
        meta_refresh = soup.find('meta', attrs={'http-equiv': re.compile('refresh', re.I)})
        
        if meta_refresh:
            content = meta_refresh.get('content', '')
            if 'url=' in content:
                url_final = content.split('url=')[-1].strip()
                return get_stream(url_final)
        
        # Cari iframe
        iframe = soup.find('iframe')
        if iframe and iframe.get('src'):
            result = iframe.get('src')
            return get_stream(result)
        
        # Cari direct link
        direct_link = soup.find('a', href=True)
        if direct_link and 'krakenfiles' in direct_link['href']:
            return get_stream(direct_link['href'])
        
        return ""
        
    except requests.exceptions.MissingSchema as e:
        print(f"URL schema error: {e}")
        return ""
    except requests.exceptions.InvalidURL as e:
        print(f"Invalid URL error: {e}")
        return ""
    except Exception as e:
        print(f"Error in short_link: {e}")
        return ""
        
        