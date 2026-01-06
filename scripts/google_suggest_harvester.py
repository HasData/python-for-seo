import requests
import xml.etree.ElementTree as ET
import string
import time
from concurrent.futures import ThreadPoolExecutor, as_completed
from urllib.parse import quote
from requests.adapters import HTTPAdapter
from requests.packages.urllib3.util.retry import Retry

# --- CONFIGURATION (Injected by Manager) ---
# These variables are set by seo_toolkit_manager.py
# API_KEY = "your_api_key"
# base_keyword = "coffee"
# max_depth = 2
# max_workers = 1

# Use defaults if running standalone
if 'API_KEY' not in globals():
    API_KEY = "HASDATA_API_KEY"
if 'base_keyword' not in globals():
    base_keyword = "coffee"
if 'max_depth' not in globals():
    max_depth = 2
if 'max_workers' not in globals():
    max_workers = 1

# Convert to uppercase for consistency with original scripts
BASE_KEYWORD = base_keyword
MAX_DEPTH = max_depth
MAX_WORKERS = max_workers

# --- SESSION SETUP ---
session = requests.Session()
adapter = HTTPAdapter(
    pool_connections=1, 
    pool_maxsize=MAX_WORKERS + 5,
    max_retries=Retry(total=3, backoff_factor=1, status_forcelist=[500, 502, 503, 504])
)
session.mount("https://", adapter)
session.mount("http://", adapter)

def fetch_suggestions(query):
    """Sends a request to Google Suggest via HasData API."""
    encoded_query = quote(query)
    target_url = f"https://suggestqueries.google.com/complete/search?output=toolbar&hl=en&q={encoded_query}"
    
    headers = {"x-api-key": API_KEY, "Content-Type": "application/json"}
    payload = {
        "url": target_url,
        "jsRendering": False,
        "outputFormat": ["html"]
    }

    try:
        response = session.post(
            "https://api.hasdata.com/scrape/web",
            headers=headers,
            json=payload,
            timeout=30
        )
        
        if response.status_code != 200:
            print(f"Error {response.status_code} for '{query}': {response.text}")
            return []
        
        xml_content = response.content
        root = ET.fromstring(xml_content)
        
        suggestions = []
        for child in root:
            if len(child) > 0 and 'data' in child[0].attrib:
                suggestions.append(child[0].attrib['data'])
                
        return suggestions

    except ET.ParseError:
        return []
    except Exception as e:
        print(f"Exception for '{query}': {e}")
        return []

def generate_search_terms_suffix(base, current_suffix, depth, max_depth):
    """Recursively generates search terms by appending characters."""
    terms = []
    for char in string.ascii_lowercase:
        new_suffix = current_suffix + char
        term = f"{base} {new_suffix}"
        terms.append(term)
        
        if depth < max_depth:
            terms.extend(generate_search_terms_suffix(base, new_suffix, depth + 1, max_depth))
            
    return terms

def run_harvest():
    print(f"Generating queries for Depth {MAX_DEPTH}...")
    queries = generate_search_terms_suffix(BASE_KEYWORD, "", 1, MAX_DEPTH)
    print(f"Total queries to process: {len(queries)}")

    results = set()
    start_time_global = time.time()

    with ThreadPoolExecutor(max_workers=MAX_WORKERS) as executor:
        future_to_query = {executor.submit(fetch_suggestions, q): q for q in queries}
        
        count = 0
        total = len(queries)
        
        print(f"\nStarting harvest with {MAX_WORKERS} workers...")
        
        for future in as_completed(future_to_query):
            query = future_to_query[future]
            count += 1
            
            if count % 20 == 0:
                elapsed = time.time() - start_time_global
                rps = count / elapsed if elapsed > 0 else 0
                print(f"Progress: {count}/{total} | Speed: {rps:.2f} req/s")

            try:
                suggestions = future.result()
                if suggestions:
                    for s in suggestions:
                        results.add(s)
            except Exception:
                pass

    total_time = time.time() - start_time_global
    print(f"\nFinished in {total_time:.2f} seconds. Average Speed: {len(queries)/total_time:.2f} req/s")
    return results

if __name__ == "__main__":
    unique_keywords = run_harvest()
    
    filename = f"long_tail_keywords_{BASE_KEYWORD.replace(' ', '_')}.csv"
    
    with open(filename, "w", encoding="utf-8") as f:
        f.write("Keyword\n")
        f.write("\n".join(unique_keywords))

    print(f"Done. Collected {len(unique_keywords)} unique keywords.")
    print(f"Saved to {filename}")