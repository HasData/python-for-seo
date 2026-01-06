import trafilatura
import requests
import pandas as pd
import json
import re
from sklearn.feature_extraction.text import CountVectorizer
from sklearn.feature_extraction.text import ENGLISH_STOP_WORDS


# --- CONFIGURATION (Injected by Manager) ---
if 'API_KEY' not in globals():
    API_KEY = "HASDATA_API_KEY"

if 'target_keyword' not in globals():
    target_keyword = "health benefits of decaf coffee"

if 'my_url' not in globals():
    my_url = "https://www.telegraph.co.uk/health-fitness/diet/nutrition/is-decaf-coffee-good-or-bad-for-you/"

if 'top_n_competitors' not in globals():
    top_n_competitors = 10


TARGET_KEYWORD = target_keyword
MY_URL = my_url
TOP_N_COMPETITORS = top_n_competitors


# Extend standard stop words to filter out conversational noise and contractions
CUSTOM_STOP_WORDS = list(ENGLISH_STOP_WORDS) + [
    've', 'll', 're', 'don', 'won', 't', 's', 'm', 'd'
]


def get_serp_links(query):
    """Retrieves top organic search results to establish the competitor baseline."""
    url = "https://api.hasdata.com/scrape/google/serp"

    try:
        response = requests.get(
            url,
            params={
                "q": query,
                "gl": "us",
                "hl": "en",
                "deviceType": "desktop",
                "num": TOP_N_COMPETITORS
            },
            headers={"x-api-key": API_KEY},
            timeout=20
        )

        if response.status_code == 200:
            return [
                res['link']
                for res in response.json().get('organicResults', [])
            ]
        return []

    except Exception:
        return []


def scrape_content(target_url):
    """
    Extracts main content from a URL using Trafilatura.
    """
    api_url = "https://api.hasdata.com/scrape/web"
    payload = {
        "url": target_url,
        "proxyType": "datacenter",
        "proxyCountry": "US",
        "jsRendering": True,
        "outputFormat": ["html"]
    }

    headers = {
        'x-api-key': API_KEY,
        'Content-Type': 'application/json'
    }

    try:
        response = requests.post(
            api_url,
            data=json.dumps(payload),
            headers=headers,
            timeout=60
        )

        if response.status_code == 200:
            text = trafilatura.extract(
                response.text,
                include_comments=False,
                include_tables=False,
                no_fallback=True
            )
            return text if text else ""

        return ""

    except Exception as e:
        print(f"Scrape Error: {e}")
        return ""


def analyze_ngrams_sklearn(my_text, competitor_texts, n_gram_range=(1, 1)):
    """
    Performs N-Gram gap analysis using CountVectorizer.
    """
    if not competitor_texts:
        return pd.DataFrame()

    min_freq = 2 if len(competitor_texts) >= 3 else 1

    vec = CountVectorizer(
        ngram_range=n_gram_range,
        stop_words=CUSTOM_STOP_WORDS,
        min_df=min_freq
    )

    try:
        X_comp = vec.fit_transform(competitor_texts)
    except ValueError:
        return pd.DataFrame()

    feature_names = vec.get_feature_names_out()
    competitors_count = (X_comp > 0).astype(int).sum(axis=0).A1
    my_counts = (
        vec.transform([my_text]).toarray()[0]
        if my_text else [0] * len(feature_names)
    )

    df = pd.DataFrame({
        'Phrase': feature_names,
        'Competitors_Count': competitors_count,
        'My_Count': my_counts
    })

    return df.sort_values(
        by=['Competitors_Count', 'Phrase'],
        ascending=[False, True]
    )


def run_analysis():
    competitor_urls = get_serp_links(TARGET_KEYWORD)

    if not competitor_urls:
        print("No competitors found via SERP API.")
        return

    print(f"\n--- CONTENT EXTRACTION & ANALYSIS ---")

    my_text = scrape_content(MY_URL)
    my_text = re.sub(r'\s+', ' ', my_text).strip()
    my_wc = len(my_text.split())

    status_icon = "✅" if my_wc > 100 else "⚠️"
    print(f"{status_icon} [TARGET] {my_wc} words | {MY_URL}")

    competitor_texts = []
    print(f"\nScanning {len(competitor_urls)} competitors...")

    for url in competitor_urls:
        if url == MY_URL:
            continue

        txt = scrape_content(url)
        txt = re.sub(r'\s+', ' ', txt).strip()
        wc = len(txt.split())

        if wc > 200:
            print(f"✅ [COMP]   {wc} words | {url}")
            competitor_texts.append(txt)
        else:
            print(f"⚠️ [SKIP]   {wc} words | {url} (Insufficient content)")

    total_competitors = len(competitor_texts)

    if total_competitors == 0:
        print("No valid competitor content available.")
        return

    print(f"\nAnalyzing gaps against {total_competitors} competitors...\n")

    dfs = {
        "MISSING KEYWORDS (1-Gram)": analyze_ngrams_sklearn(my_text, competitor_texts, (1, 1)),
        "MISSING PHRASES (2-Grams)": analyze_ngrams_sklearn(my_text, competitor_texts, (2, 2)),
        "MISSING LONG-TAIL (3-Grams)": analyze_ngrams_sklearn(my_text, competitor_texts, (3, 3))
    }

    print("=" * 60 + "\nGAP ANALYSIS REPORT\n" + "=" * 60)

    if my_wc <= 50:
        print("❌ Critical: Target content could not be parsed.")
        return

    for title, df in dfs.items():
        if df.empty:
            continue

        subset = df[df['My_Count'] == 0].head(10)

        if subset.empty:
            print(f"\n### {title}: No significant gaps.")
            continue

        print(f"\n### {title}")
        print(f"{'Phrase':<30} | {'Competitors':<15} | {'My Count':<10}")
        print("-" * 65)

        for _, row in subset.iterrows():
            print(
                f"{row['Phrase']:<30} | "
                f"{row['Competitors_Count']} of {total_competitors:<10} | ❌"
            )

    print("\n" + "=" * 60 + "\nSHARED TERMS OVERVIEW\n" + "=" * 60)

    shared = dfs["MISSING KEYWORDS (1-Gram)"]
    shared_subset = shared[shared['My_Count'] > 0].head(5)

    if not shared_subset.empty:
        for _, row in shared_subset.iterrows():
            print(
                f"{row['Phrase']:<30} | "
                f"{row['Competitors_Count']} of {total_competitors:<10} | "
                f"{row['My_Count']}"
            )


if __name__ == "__main__":
    print(f"Running Content Gap Analyzer")
    print(f"Keyword: {TARGET_KEYWORD}")
    print(f"URL: {MY_URL}")
    print(f"Top competitors: {TOP_N_COMPETITORS}\n")

    run_analysis()
