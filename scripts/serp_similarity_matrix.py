import requests
import pandas as pd
import seaborn as sns
import matplotlib.pyplot as plt
from collections import Counter
import time


# --- CONFIGURATION (Injected by Manager) ---
if 'API_KEY' not in globals():
    API_KEY = "HASDATA_API_KEY"

if 'keywords' not in globals():
    keywords = [
        "health benefits of coffee",
        "benefits of coffee for men",
        "benefits of coffee for women",
        "health benefits of black coffee",
        "health benefits of mushroom coffee",
        "health benefits of decaf coffee",
    ]


KEYWORDS = keywords
# -----------------------------------------


def get_top_urls_set(query):
    """
    Requests the API and returns a SET of organic URLs.
    """
    url = "https://api.hasdata.com/scrape/google/serp"
    params = {
        "q": query,
        "gl": "us",
        "hl": "en",
        "deviceType": "desktop"
    }
    headers = {
        "x-api-key": API_KEY,
        "Content-Type": "application/json"
        }

    print(f"Scanning SERP for: '{query}'...")
    try:
        response = requests.get(url, params=params, headers=headers, timeout=25)
        if response.status_code == 200:
            data = response.json()
            organic = data.get('organicResults', [])
            links = [
                result['link']
                for result in organic[:10]
                if 'link' in result
            ]
            return set(links)
        else:
            print(f"Error {response.status_code} for query '{query}'")
            return set()

    except Exception as e:
        print(f"Exception for query '{query}': {e}")
        return set()


def calculate_jaccard(set1, set2):
    """Calculates Jaccard Index between two sets."""
    union = len(set1.union(set2))
    if union == 0:
        return 0.0
    return len(set1.intersection(set2)) / union


def visualize_similarity_heatmap(similarity_df):
    """Builds and displays the heatmap."""
    plt.figure(figsize=(10, 8))
    sns.set_theme(context='notebook', style='whitegrid', font_scale=1.1)

    ax = sns.heatmap(
        similarity_df,
        annot=True,
        fmt=".0%",
        cmap="YlGnBu",
        vmin=0,
        vmax=1,
        cbar_kws={'label': 'Jaccard Similarity Score'}
    )

    plt.title("SERP Similarity Heatmap", fontsize=16, pad=20)
    plt.xticks(rotation=45, ha='right')
    plt.yticks(rotation=0)
    plt.tight_layout()
    print("Visualizing heatmap...")
    plt.show()


def show_top_common_urls(results_data):
    """Counts and prints the most frequently occurring URLs."""
    all_urls_flat = []
    for url_set in results_data.values():
        all_urls_flat.extend(list(url_set))

    url_counts = Counter(all_urls_flat).most_common(15)

    print(f"\n### Top Recurring URLs (across {len(KEYWORDS)} queries)")
    print(f"{'Frequency':<10} | URL")
    print("-" * 80)

    for url, count in url_counts:
        if count > 1 or len(KEYWORDS) <= 2:
            print(f"{count:<10} | {url}")


# --- MAIN LOGIC ---
if __name__ == "__main__":
    results_data = {}

    print("--- Start SERP Collection ---\n")
    for keyword in KEYWORDS:
        results_data[keyword] = get_top_urls_set(keyword)
        time.sleep(1)

    print("\n--- Collection Finished ---")

    n = len(KEYWORDS)
    similarity_matrix = pd.DataFrame(
        index=KEYWORDS,
        columns=KEYWORDS,
        dtype=float
    )

    for i in range(n):
        for j in range(n):
            kw1 = KEYWORDS[i]
            kw2 = KEYWORDS[j]
            similarity_matrix.iloc[i, j] = calculate_jaccard(
                results_data[kw1],
                results_data[kw2]
            )

    print("\n### Similarity Matrix (Jaccard Index)")
    pd.set_option('display.max_columns', None)
    pd.set_option('display.width', 1000)
    print(similarity_matrix.style.format("{:.1%}").to_string())

    print("\n" + "=" * 50 + "\n")

    show_top_common_urls(results_data)

    visualize_similarity_heatmap(similarity_matrix)
