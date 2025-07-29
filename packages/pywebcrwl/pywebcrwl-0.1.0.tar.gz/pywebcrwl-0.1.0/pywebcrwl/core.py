import requests
from bs4 import BeautifulSoup
import re
from urllib.parse import urljoin,urlparse
from collections import deque, Counter
import os
import phonenumbers
from geotext import GeoText




HEADERS = {
        "User-Agent": "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/91.0.4472.124 Safari/537.36"
    }



def extract_emails(urls):
    EMAIL = set()
    email_pattern = r"[a-zA-Z0-9._%+-]+@[a-zA-Z0-9.-]+\.[a-zA-Z]{2,}(?:\.[a-zA-Z]{2,})*"
    for url in urls:
        print(f'Extracting emails from : {url}')
        response = requests.get(url,headers=HEADERS)
        if response.status_code != 200 or "text/html" not in response.headers.get("Content-Type", ""):
            continue
        all_emails = set(re.findall(email_pattern, response.text))
        for email in all_emails:
            if email not in EMAIL: 
                EMAIL.add(email)  
    return list(EMAIL)            

def extract_pages_from_url(url):
    print('-------------------------------------------------------------------------------------------')
    VISITED_PAGES = set([url])
    TO_VISIT = deque([])
    response = requests.get(url, headers=HEADERS)
    if response.status_code != 200 or "text/html" not in response.headers.get("Content-Type", ""):
        print('An error has occured, the response cannot be loaded.')
        return
    soup = BeautifulSoup(response.text, 'html.parser')
    print(f'Processing : {url}')
    for link in soup.find_all('a', href=True):
        link_href = link["href"]
        full_url = urljoin(f"{url}", link_href)  
        if full_url.startswith(f'{url}') and full_url not in VISITED_PAGES and full_url not in TO_VISIT:
            TO_VISIT.append(full_url)      
    extract_subpages_from_suburl(VISITED_PAGES,TO_VISIT)
    return list(VISITED_PAGES)       


def extract_subpages_from_suburl(VISITED_PAGES,TO_VISIT):
    while TO_VISIT:
        url = TO_VISIT.popleft()
        print(f'Processing : {url}')
        if url not in VISITED_PAGES:
            VISITED_PAGES.add(url)
            response = requests.get(url, headers=HEADERS)
            if response.status_code != 200 or "text/html" not in response.headers.get("Content-Type", ""):
                continue
            soup = BeautifulSoup(response.text, 'html.parser')
            for link in soup.find_all('a', href=True):
                link_href = link["href"]
                full_url = urljoin(f"{url}", link_href)
                if full_url.startswith(f'{url}') and full_url not in VISITED_PAGES and full_url not in TO_VISIT:
                    TO_VISIT.append(full_url)
        continue            
    return   

def extract_by_regex(urls,regex):
    all_matchs = set()
    for url in urls:
        response = requests.get(url,headers=HEADERS)
        if response.status_code != 200 or "text/html" not in response.headers.get("Content-Type", ""):
            continue
        regex_matchs = set(re.findall(regex,response.text))
        for match in regex_matchs:
            all_matchs.add(match)
    return list(all_matchs)   


def extract_emails_by_domain(urls,domain):
    EMAIL = set()
    email_pattern = rf"[a-zA-Z0-9._%+-]+@{domain}"
    print('-------------------------------------------------------------------------------------------')
    for url in urls:
        print(f'Extracting emails from : {url}')
        response = requests.get(url,headers=HEADERS)
        if response.status_code != 200 or "text/html" not in response.headers.get("Content-Type", ""):
            continue   
        all_emails = set(re.findall(email_pattern, response.text))
        for email in all_emails:
            if email not in EMAIL: 
                EMAIL.add(email)  
    return list(EMAIL)            



def extract_images_from_url(urls,output_folder):
    image_founed = False
    print('-------------------------------------------------------------------------------------------')
    for url in urls:
        
        print(f'Extracting images from : {url}')
        response = requests.get(url, headers=HEADERS)
        if response.status_code != 200 or "text/html" not in response.headers.get("Content-Type", ""):
            return
        soup = BeautifulSoup(response.text, 'html.parser')
        for img in soup.find_all('img', src=True):
            image_url = urljoin(url, img['src'])
            response_image = requests.get(image_url,headers=HEADERS)
            if response_image.status_code != 200:
                continue
            parsed_url = urlparse(image_url)
            image_name = os.path.basename(parsed_url.path)
            image_founed = True
            with open(rf"{output_folder}\{image_name}", "wb") as f:
               f.write(response_image.content)

    if image_founed:           
        print(f"The images has been saved successfully in {output_folder} folder")
    else:
        print('No image has been founded')
    return   


def extract_all_urls_from_single_url(url):
    urls = set()
    response = requests.get(url,headers=HEADERS)
    if response.status_code != 200 or "text/html" not in response.headers.get("Content-Type", ""):
        return
    soup = BeautifulSoup(response.text, 'html.parser')
    for link in soup.find_all('a', href=True):
        link_href = link["href"]
        if link_href.startswith('https://'):
            full_url = urljoin(f"{url}", link_href)
            urls.add(full_url)
    return list(urls)    


def extract_documents_by_extension(urls,output_folder,ex = None):
    print('---------------------------------------------------------------------')
    founded_file = False
    if ex is None:
        ex = [".pdf", ".doc", ".docx", ".xls", ".xlsx", ".ppt", ".pptx", ".zip", ".txt", ".csv", ".sql"]
    for url in urls:
        print(f'Extracting documents from : {url}')
        response = requests.get(url,headers=HEADERS)
        if response.status_code != 200 or "text/html" not in response.headers.get("Content-Type", ""):
            continue
        soup = BeautifulSoup(response.text,'html.parser')
        for a in soup.find_all('a', href=True):
            href = a['href']
            if any(href.lower().endswith(ext) for ext in ex):
                full_url = urljoin(url, href)
                for e in ex:
                    if href.lower().endswith(e):
                        founded_file = True
                        response_file = requests.get(full_url,headers=HEADERS)
                        if response_file.status_code != 200:
                            continue
                        parsed_url = urlparse(full_url)
                        href_name = os.path.basename(parsed_url.path)
                        with open(rf"{output_folder}\{href_name}", "wb") as f:
                            f.write(response_file.content)
    if founded_file:                        
        print(f"Documents has been saved successfully in {output_folder} folder.")               
    else:
        print('No document has been founded')


def extract_html_code(urls,output_folder):
    for url in urls:
        response = requests.get(url,headers=HEADERS)
        if response.status_code != 200 or "text/html" not in response.headers.get("Content-Type", ""):
            continue
        parsed = urlparse(url)
        filename = os.path.basename(parsed.path)
        if not filename:
            filename = "index.html"
        elif not filename.endswith(".html"):
            filename += ".html"
        filepath = os.path.join(output_folder, filename)

        with open(filepath, "w", encoding="utf-8") as f:
            f.write(response.text)

    print(f'HTML files has been saved successfully in {output_folder} folder')        

def extract_keywords_from_urls(urls, numbers_words=20):
    print('---------------------------------------------------------------------')
    ENGLISH_STOPWORDS = set([
    "the", "and", "for", "are", "but", "with", "not", "you", "your", "that", "this", "from",
    "have", "has", "was", "were", "they", "their", "will", "would", "can", "could", "should",
    "about", "which", "when", "what", "where", "how", "who", "all", "any", "our", "more", "one",
    "into", "out", "also", "than", "then", "such", "its", "it's"
])
    all_words = []

    for url in urls:
            print(f'Extracting keywords from : {url}')
            response = requests.get(url, headers=HEADERS)
            if response.status_code != 200 or "text/html" not in response.headers.get("Content-Type", ""):
                continue

            soup = BeautifulSoup(response.text, 'html.parser')
            text = soup.get_text(separator=' ', strip=True)
            words = re.findall(r"\b[a-zA-Z]{3,}\b", text.lower())
            words = [word for word in words if word not in ENGLISH_STOPWORDS]
            all_words.extend(words)

    keyword_counts = Counter(all_words)
    return keyword_counts.most_common(numbers_words)



def extract_words(urls,words,output_file = None):
    print('---------------------------------------------------------------------')
    senteces = []
    for word in words:
        print(f'Searching for "{word}..."')
        for url in urls:
            response = requests.get(url,headers=HEADERS)
            if response.status_code != 200 or "text/html" not in response.headers.get("Content-Type", ""):
                continue
            soup = BeautifulSoup(response.text, 'html.parser')
            text = soup.get_text(separator=' ', strip=True).split('.')
            for sentence in text:
                if word in sentence:
                    senteces.append(sentence)
    if output_file is not None:
        with open(output_file,'w') as f:
            for s in senteces:
                f.write(f"{s}\n")                
    return senteces                

def extract_favicons(urls,output_folder):
    print('---------------------------------------------------------------------')
    for url in urls:
        print(f'Searching for favicon in "{url}..."')
        response = requests.get(url,headers=HEADERS)
        if response.status_code != 200:
            continue
        soup = BeautifulSoup(response.text, 'html.parser')
        link_tags = soup.find_all("link", href=True, rel=True)
        for icon in link_tags:
            fav = icon['href']
            if '.ico' in fav or '.png' in fav or '.svg' in fav:
                favicon_url = urljoin(url, fav)
                response_fav = requests.get(favicon_url,headers=HEADERS)
                if response_fav.status_code != 200:
                    continue
                filename = os.path.basename(urlparse(favicon_url).path)
                with open(fr'{output_folder}\{filename}','wb') as f:
                    f.write(response_fav.content)    


def extract_social_media_links(urls,domains = None):
    print('---------------------------------------------------------------------')
    social = set()
    if domains is None:
        domains = [
    "facebook.com", "instagram.com", "linkedin.com",
    "twitter.com", "t.me", "youtube.com", "pinterest.com",
    "snapchat.com", "whatsapp.com","x.com"
        ]
    for url in urls:
        print(f'Searching for social media links in {url}')
        response = requests.get(url,headers=HEADERS)
        if response.status_code != 200 or "text/html" not in response.headers.get("Content-Type", ""):
            continue
        soup = BeautifulSoup(response.text,'html.parser')
        for a in soup.find_all('a',href=True):
            href = a['href']
            if any(domain in href for domain in domains):
                social.add(href)
    return list(social)   

def resume_site(url):
    try:
        response = requests.get(url, headers=HEADERS)
        if response.status_code != 200 or "text/html" not in response.headers.get("Content-Type", ""):
            return 

        soup = BeautifulSoup(response.text, 'html.parser')
        title = soup.title.string.strip() if soup.title else "No website"
        description = ""
        desc_tag = soup.find("meta", attrs={"name": "description"})
        if desc_tag and 'content' in desc_tag.attrs:
            description = desc_tag["content"].strip()
        paragraphs = soup.find_all("p")
        main_text = " ".join(p.get_text() for p in paragraphs[:5]).strip()

        # Résumé simple
        return f"Title : {title}\nDescription : {description}\nAbout the website : {main_text[:900]}..."

    except Exception as e:
        return f"Error : {str(e)}"



def extract_phone_numbers(urls):
    print('---------------------------------------------------------------------')
    num = set()
    for url in urls:
        print(f'Searching for phone numbers in {url}')
        response = requests.get(url,headers=HEADERS)
        if response.status_code != 200 or "text/html" not in response.headers.get("Content-Type", ""):
            continue
        text = response.text
        numbers = phonenumbers.PhoneNumberMatcher(text,None)
        for number in numbers:
            formatted_number = phonenumbers.format_number(number.number, phonenumbers.PhoneNumberFormat.E164)
            num.add(formatted_number)
    return list(num)      


def extract_cities(url):
    cities = set()
    response = requests.get(url,headers=HEADERS)
    if response.status_code != 200 or "text/html" not in response.headers.get("Content-Type", ""):
        print(f"HTTP ERROR : {response.status_code}, the website cannot be loaded")
        return
    places = GeoText(response.text).cities
    for p in places:
        cities.add(str(p))
    return list(cities)    
    

    


# print(extract_emails_by_domain(extract_pages_from_url(),"jadaya.com"))
# extract_images_from_url(['https://jadaya.com'],r"C:\Users\idriss\Desktop\test")
# print(extract_all_urls_from_single_url('https://jadaya.com/products/'))
# extract_documents_by_extension(extract_pages_from_url('https://jadaya.com'),fr"C:\Users\idriss\Desktop\test")
# print(extract_images_from_url(['https://ccis.ksu.edu.sa/en'],r"C:\Users\idriss\Desktop\test"))
# print(extract_html_code(['https://jadaya.com'],r"C:\Users\idriss\Desktop\test"))
# print(extract_keywords_from_urls(extract_pages_from_url('https://jadaya.com')))
# print(extract_words(extract_pages_from_url('https://jadaya.com/'),["software"],r"C:\Users\idriss\Desktop\test.txt"))
# print(extract_images_from_url(extract_pages_from_url('https://jadaya.com'),r"C:\Users\idriss\Desktop\test"))
# print(extract_social_media_links(extract_pages_from_url('https://jadaya.com/'),['twitter']))
# print(resume_site())
# print(extract_phone_numbers(extract_pages_from_url('https://www.managed.sa/')))
# print(extract_cities('https://www.managed.sa/'))
print(resume_site('https://www.managed.sa/'))