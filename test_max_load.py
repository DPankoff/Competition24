import requests
from bs4 import BeautifulSoup
from sklearn.feature_extraction.text import TfidfVectorizer
from sklearn.metrics.pairwise import cosine_similarity
import nltk
from nltk.corpus import stopwords
import gradio as gr
import tldextract
import time

nltk.download('stopwords')
stop_words = set(stopwords.words('english'))

def fetch_page_content(url):
    response = requests.get(url)
    if response.status_code == 200:
        return response.text
    else:
        return None

def extract_meta_data(html_content):
    soup = BeautifulSoup(html_content, 'html.parser')
    
    title = soup.title.string if soup.title else ''
    meta_description = ''
    meta_desc_tag = soup.find('meta', attrs={'name': 'description'})
    if meta_desc_tag:
        meta_description = meta_desc_tag.get('content', '')
        
    h1_tags = [h1.get_text() for h1 in soup.find_all('h1')]
    
    return {
        'title': title,
        'meta_description': meta_description,
        'h1_tags': h1_tags,
        'content': soup.get_text()
    }

def remove_stop_words(text):
    words = text.split()
    return ' '.join([word for word in words if word.lower() not in stop_words])

def analyze_similarity(pages):
    tfidf_vectorizer = TfidfVectorizer()
    tfidf_matrix = tfidf_vectorizer.fit_transform([page['content'] for page in pages])
    cosine_similarities = cosine_similarity(tfidf_matrix)
    
    return cosine_similarities

def check_robots_txt(url):
    robots_url = f"{url.scheme}://{url.netloc}/robots.txt"
    response = requests.get(robots_url)
    if response.status_code == 200:
        return "No errors"
    else:
        return "Errors found"

def find_internal_links(soup, base_url):
    links = []
    for link in soup.find_all('a', href=True):
        href = link['href']
        if href.startswith('/'):
            href = base_url + href
        if href.startswith(base_url):
            links.append(href)
    return links

def check_images_weight(soup):
    total_weight = 0
    for img in soup.find_all('img'):
        src = img.get('src')
        if src:
            try:
                response = requests.head(src)
                if 'content-length' in response.headers:
                    total_weight += int(response.headers['content-length'])
            except:
                pass
    return total_weight

def analyze_speed(url):
    start_time = time.time()
    response = requests.get(url)
    end_time = time.time()
    return end_time - start_time

def analyze_page(url):
    html_content = fetch_page_content(url)
    if not html_content:
        return None
    
    soup = BeautifulSoup(html_content, 'html.parser')
    meta_data = extract_meta_data(html_content)
    meta_data['content'] = remove_stop_words(meta_data['content'])
    
    # Check robots.txt
    url_parts = requests.utils.urlparse(url)
    meta_data['robots_txt'] = check_robots_txt(url_parts)
    
    # Check for duplicate content
    pages = [meta_data]
    similarities = analyze_similarity(pages)
    meta_data['duplicate_content'] = "No" if similarities[0][0] == 1.0 else "Yes"
    
    # Check for errors in code
    meta_data['code_errors'] = "No" if len(soup.find_all('html')) == 1 else "Yes"
    
    # Check for links
    meta_data['internal_links'] = len(find_internal_links(soup, f"{url_parts.scheme}://{url_parts.netloc}"))
    
    # Check image weight
    meta_data['image_weight'] = check_images_weight(soup)
    
    # Analyze speed
    meta_data['load_time'] = analyze_speed(url)
    
    meta_data['url'] = url
    
    return meta_data

def compare_pages(urls):
    urls_list = urls.split(',')
    results = []
    for url in urls_list:
        url = url.strip()
        result = analyze_page(url)
        if result:
            results.append([
                result['url'],
                result['title'],
                result['meta_description'],
                ", ".join(result['h1_tags']),
                result['robots_txt'],
                result['duplicate_content'],
                result['code_errors'],
                result['internal_links'],
                result['image_weight'],
                result['load_time']
            ])
    
    return results

# Создание интерфейса Gradio
iface = gr.Interface(
    fn=compare_pages,
    inputs=gr.Textbox(lines=2, placeholder="Enter URLs separated by commas", label="URLs"),
    outputs=gr.Dataframe(headers=["URL", "Title", "Meta Description", "H1 Tags", "Robots.txt", "Duplicate Content", "Code Errors", "Internal Links", "Image Weight", "Load Time"]),
    title="Page Analysis",
    description="Введите URL-адреса страниц, разделенные запятыми, для анализа их индексации и ранжирования."
)

# Запуск интерфейса
iface.launch()

# urls = [
#     'https://www.trustpilot.com/trust/the-cost-of-living/',
#     'https://www.trustpilot.com/trust/combating-fake-reviews',
# ]

# main(urls)