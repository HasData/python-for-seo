import requests
import pandas as pd
from urllib.parse import urlparse

# --- CONFIGURATION (Injected by Manager) ---
if 'API_KEY' not in globals():
    API_KEY = "HASDATA_API_KEY"
if 'keyword' not in globals():
    keyword = "instant coffee"
if 'device_type' not in globals():
    device_type = "desktop"
if 'location' not in globals():
    location = "United States"

KEYWORD = keyword
DEVICE_TYPE = device_type
LOCATION = location

def get_serp_links(query):
    url = "https://api.hasdata.com/scrape/google/serp"
    params = {
        "q": query,
        "gl": "us",
        "hl": "en",
        "deviceType": DEVICE_TYPE,
        "location": LOCATION
    }
    headers = {"x-api-key": API_KEY}

    try:
        response = requests.get(url, params=params, headers=headers, timeout=20)
        if response.status_code == 200:
            data = response.json()
            return [result['link'] for result in data.get('organicResults', [])]
        return []
    except Exception as e:
        print(f"Error: {e}")
        return []

def classify_url(url):
    """Classifies a URL based on domain and path."""
    try:
        parsed = urlparse(url)
        domain = parsed.netloc.lower()
        path = parsed.path.lower()
        
        if "wikipedia.org" in domain:
            return "Encyclopedic (Wikipedia)"
        if "youtube.com" in domain or "youtu.be" in domain:
            return "Video Content (YouTube)"
        if any(x in domain for x in ['reddit.com', 'quora.com', 'stackoverflow.com']):
            return "UGC (Forum/Discussion)"
        if any(x in path for x in ['/forum', '/threads', '/community', '/board']):
            return "UGC (Forum/Discussion)"
        if path == "" or path == "/":
            return "Homepage (Brand)"
        if any(x in path for x in ['/product', '/shop', '/item', '/collections', '/buy', '/pricing', '/store']) or "amazon.com" in domain:
            return "Transactional (Product)"
        if any(x in path for x in ['/blog', '/guide', '/news', '/article', '/how-to', '/tips', '/wiki']):
            return "Informational (Blog)"
        return "General Page"
    except:
        return "Unknown"

if __name__ == "__main__":
    print(f"Analyzing SERP for: '{KEYWORD}'")
    print(f"Device: {DEVICE_TYPE}, Location: {LOCATION}\n")
    
    links = get_serp_links(KEYWORD)
    
    if links:
        df = pd.DataFrame(links, columns=['URL'])
        df['Type'] = df['URL'].apply(classify_url)
        
        breakdown = df['Type'].value_counts(normalize=True) * 100
        
        print("--- SERP Composition ---")
        print(df[['Type', 'URL']].to_string(index=True))
        
        print("\n--- Strategic Verdict ---")
        if not breakdown.empty:
            dominant_type = breakdown.idxmax()
            percent = breakdown.max()
            
            print(f"Dominant Type: {dominant_type} ({percent:.1f}%)")
            
            if "Informational" in dominant_type:
                print("Action: Create a long-form Guide or Blog Post.")
            elif "Transactional" in dominant_type:
                print("Action: Create a Product Page or Collection Page.")
            elif "Homepage" in dominant_type:
                print("Action: High difficulty. Requires strong Brand Authority.")
            elif "Video" in dominant_type:
                print("Action: Text alone won't rank. Produce a high-quality Video.")
            elif "UGC" in dominant_type:
                print("Action: Engage in community discussions or create 'Real Review' style content.")
            elif "Encyclopedic" in dominant_type:
                print("Action: Definitional intent. Very hard to outrank Wikipedia directly.")
            else:
                print("Action: Mixed SERP. Manual review recommended.")
    else:
        print("No results found.")