import requests
import pandas as pd
import time
from urllib.parse import urlparse


# --- CONFIGURATION (Injected by Manager) ---
if 'API_KEY' not in globals():
    API_KEY = "HASDATA_API_KEY"

if 'target_domain' not in globals():
    target_domain = "webmd.com"

if 'keywords' not in globals():
    keywords = [
        "health benefits of coffee",
        "benefits of coffee for men",
        "benefits of coffee for women",
        "health benefits of black coffee",
        "health benefits of mushroom coffee",
        "health benefits of decaf coffee"
    ]


TARGET_DOMAIN = target_domain
KEYWORDS = keywords


def normalize_domain(url):
    """
    Extracts the base domain from a URL to ensure accurate matching.
    """
    try:
        parsed = urlparse(url)
        return parsed.netloc.lower().replace('www.', '')
    except Exception:
        return ""


def fetch_serp_data(query):
    """
    Executes a SERP API request targeting Google's AI Overview.
    """
    endpoint = "https://api.hasdata.com/scrape/google/serp"
    params = {
        "q": query,
        "gl": "us",
        "hl": "en",
        "deviceType": "desktop"
    }
    headers = {"x-api-key": API_KEY}

    try:
        response = requests.get(endpoint, params=params, headers=headers, timeout=30)
        if response.status_code == 200:
            return response.json()
        else:
            print(f"[API Error] Status: {response.status_code} for query '{query}'")
            return None
    except Exception as e:
        print(f"[Network Error] {e}")
        return None


def extract_ai_citations(serp_data):
    """
    Parses the JSON response to locate the 'aiOverview' block.
    """
    ai_overview = serp_data.get('aiOverview')

    if not ai_overview:
        return None, []

    references = ai_overview.get('references', [])

    citations = []
    for ref in references:
        citations.append({
            'index': ref.get('index'),
            'title': ref.get('title'),
            'url': ref.get('link'),
            'source_name': ref.get('source')
        })

    return ai_overview, citations


def run_monitor():
    results = []

    print(f"--- Starting AI Overview Monitor for: {TARGET_DOMAIN} ---")
    print(f"Processing {len(KEYWORDS)} keywords...\n")

    for query in KEYWORDS:
        print(f"Analyzing: '{query}'...")

        data = fetch_serp_data(query)
        if not data:
            continue

        ai_block, citations = extract_ai_citations(data)

        is_triggered = ai_block is not None
        is_cited = False
        citation_rank = None
        found_url = None

        if is_triggered:
            target_clean = normalize_domain(f"https://{TARGET_DOMAIN}")

            for cit in citations:
                cited_domain = normalize_domain(cit['url'])
                if target_clean in cited_domain:
                    is_cited = True
                    citation_rank = cit['index']
                    found_url = cit['url']
                    break

        results.append({
            "Keyword": query,
            "AI Triggered": is_triggered,
            "Is Cited": is_cited,
            "Citation Index": citation_rank if is_cited else "-",
            "Cited URL": found_url if is_cited else "-"
        })

        time.sleep(1)

    df = pd.DataFrame(results)

    print("\n" + "=" * 60)
    print("AI OVERVIEW VISIBILITY REPORT")
    print("=" * 60)

    if df.empty:
        print("No data collected.")
        return

    df['AI Triggered'] = df['AI Triggered'].map({True: '✅ Yes', False: '❌ No'})
    df['Is Cited'] = df['Is Cited'].map({True: '✅ YES', False: '❌ No'})

    try:
        print(df.to_markdown(index=False))
    except ImportError:
        print(df.to_string(index=False))

    total = len(df)
    triggered = len(df[df['AI Triggered'] == '✅ Yes'])
    cited = len(df[df['Is Cited'] == '✅ YES'])

    print("\n--- SUMMARY METRICS ---")
    print(f"AI Coverage: {triggered}/{total} keywords ({(triggered/total)*100:.1f}%)")

    if triggered > 0:
        print(f"Share of Voice: {cited}/{triggered} AI Overviews ({(cited/triggered)*100:.1f}%)")
    else:
        print("Share of Voice: N/A (No AI Overviews generated)")


if __name__ == "__main__":
    run_monitor()