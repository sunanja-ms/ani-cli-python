import requests
from bs4 import BeautifulSoup
import re
from rich.console import Console

console = Console()

HOST = "https://otakudesu.best/"
HEADERS = {'User-Agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/91.0.4472.124 Safari/537.36'}

def get_page_soup(url):
    """Mengambil URL dan mengembalikan objek BeautifulSoup."""
    try:
        response = requests.get(url, headers=HEADERS, timeout=15)
        response.raise_for_status()
        return BeautifulSoup(response.content, "html.parser")
    except requests.RequestException as e:
        console.print(f"[bold red]Error saat mengambil URL {url}:[/bold red] {e}")
        return None

def search_anime(query):
    """Mencari anime di Otakudesu berdasarkan judul."""
    url = f"{HOST}?s={query}&post_type=anime"
    soup = get_page_soup(url)
    if not soup:
        return []

    results = []
    search_list = soup.find("ul", {"class": "chivsrc"})
    if not search_list:
        return []
        
    for item in search_list.find_all("li"):
        title_element = item.find("h2")
        img_element = item.find("img")
        if title_element and title_element.a and img_element:
            results.append({
                "title": title_element.text.strip(),
                "url": title_element.a['href'],
                "thumbnail": img_element['src']
            })
    return results

def get_download_links(url):
	data = get_page_soup(url)
	ret = {}

	download = data.find('div', {'class': 'download'})
	if download:
		for dlurl in download.find_all("li"):  # Ganti findAll dengan find_all
			filetype = dlurl.strong.text
			fileurl = ""
			for urlname in dlurl.find_all("a"):  # Ganti findAll dengan find_all
				if "kfiles" in urlname.text.lower():
					fileurl = urlname['href']
					if "desudrive" in fileurl:
						fileurl = desudrive(fileurl)
			if not fileurl:
				fileurl = dlurl.a['href']
			ret[filetype] = fileurl
	elif batchlink := data.find('div', {'class': 'batchlink'}):
		for dlurl in batchlink.find_all("li"):  # Ganti findAll dengan find_all
			filetype = dlurl.strong.text
			fileurl = ""
			for urlname in dlurl.find_all("a"):  # Ganti findAll dengan find_all
				if "kfiles" in urlname.text.lower():
					fileurl = urlname['href']
					if "desudrive" in fileurl:
						fileurl = desudrive(fileurl)
			if not fileurl:
				fileurl = dlurl.a['href']
			ret[filetype] = fileurl

	return ret
def get_all_ongoing_anime(page=1):
    """Mengambil daftar anime ongoing dari halaman tertentu."""
    url = f"{HOST}/ongoing-anime/page/{page}/"
    soup = get_page_soup(url)
    if not soup:
        return []

    anime_list = []
    venz_div = soup.find('div', {'class': 'venz'})
    if not venz_div:
        return []
    
    for anime in venz_div.find_all("li"):
        title_tag = anime.find('h2', {"class": "jdlflm"})
        eps_tag = anime.find('div', {"class": "epz"})
        hari_tag = anime.find('div', {"class": "epztipe"})
        url_tag = anime.find('a')

        if all([title_tag, eps_tag, hari_tag, url_tag]):
            anime_list.append({
                "title": title_tag.text,
                "eps": eps_tag.text,
                "hari": hari_tag.text.strip(),
                "url": url_tag['href']
            })
    return anime_list

# core/otakudesu.py

# ... (kode lain tetap sama) ...
import re # Tambahkan ini di bagian atas

# ...

# core/otakudesu.py

def get_anime_details(url):
    """Mengambil detail lengkap dari halaman anime."""
    soup = get_page_soup(url)
    if not soup:
        return None
    
    details = {'url': url}

    details['title'] = soup.find('div', {"class": "jdlrx"}).text.strip() if soup.find('div', {"class": "jdlrx"}) else "Tidak Diketahui"
    details['cover'] = soup.find('img', {'class': 'attachment-post-thumbnail'})['src'] if soup.find('img', {'class': 'attachment-post-thumbnail'}) else ""
    sinopsis_p = soup.find('div', {'class': 'sinopc'}).find_all('p') if soup.find('div', {'class': 'sinopc'}) else []
    details['sinopsis'] = "\n".join([p.text for p in sinopsis_p])

    info_p = soup.find("div", {"class": "infozingle"}).find_all('p') if soup.find("div", {"class": "infozingle"}) else []
    details["info"] = "\n".join([p.text for p in info_p])

    details["episodes"] = []
    for eps_list in soup.find_all('div', {'class': 'episodelist'}):
        for eps_item in eps_list.find_all("li"):
            a_tag = eps_item.find('a')
            date_span = eps_item.find('span', {"class": "zeebr"})
            if a_tag and date_span:
                title = a_tag.text
                
                if re.search(r'(\d+\s*–\s*\d+|batch|end\))', title, re.IGNORECASE):
                    continue

                details['episodes'].append({
                    "title": title,
                    "url": a_tag['href'],
                    "date": date_span.text
                })

    # --- PERUBAHAN DI SINI: Balik urutan list episode ---
    details['episodes'].reverse()

    return details


# ... (sisa kode di file ini tetap sama) ...
def getDownload(url):
	data = get_page_soup(url)
	ret = {}

	download = data.find('div', {'class': 'download'})
	if download:
		for dlurl in download.find_all("li"):  # Ganti findAll dengan find_all
			filetype = dlurl.strong.text
			fileurl = ""
			for urlname in dlurl.find_all("a"):  # Ganti findAll dengan find_all
				if "kfiles" in urlname.text.lower():
					fileurl = urlname['href']
					if "desudrive" in fileurl:
						fileurl = desudrive(fileurl)
			if not fileurl:
				fileurl = dlurl.a['href']
			ret[filetype] = fileurl
	elif batchlink := data.find('div', {'class': 'batchlink'}):
		for dlurl in batchlink.find_all("li"):  # Ganti findAll dengan find_all
			filetype = dlurl.strong.text
			fileurl = ""
			for urlname in dlurl.find_all("a"):  # Ganti findAll dengan find_all
				if "kfiles" in urlname.text.lower():
					fileurl = urlname['href']
					if "desudrive" in fileurl:
						fileurl = desudrive(fileurl)
			if not fileurl:
				fileurl = dlurl.a['href']
			ret[filetype] = fileurl

	return ret