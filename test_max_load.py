import requests
from bs4 import BeautifulSoup
from sklearn.feature_extraction.text import TfidfVectorizer
from sklearn.metrics.pairwise import cosine_similarity
import nltk
from nltk.corpus import stopwords

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

def main(urls):
    pages = []
    for url in urls:
        html_content = fetch_page_content(url)
        if html_content:
            meta_data = extract_meta_data(html_content)
            meta_data['content'] = remove_stop_words(meta_data['content'])
            pages.append(meta_data)
    
    similarities = analyze_similarity(pages)
    
    for i in range(len(urls)):
        for j in range(i+1, len(urls)):
            print(f"Similarity between {urls[i]} and {urls[j]}: {similarities[i][j]:.2f}")

# Пример использования
urls = [
    'https://www.trustpilot.com/trust/the-cost-of-living/',
    'https://www.trustpilot.com/trust/combating-fake-reviews',
]

main(urls)