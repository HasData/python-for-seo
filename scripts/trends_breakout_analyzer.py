import requests

# --- CONFIGURATION (Injected by Manager) ---
if 'API_KEY' not in globals():
    API_KEY = "HASDATA_API_KEY"
if 'seed_topic' not in globals():
    seed_topic = "Coffee"
if 'geo' not in globals():
    geo = "US"
if 'date' not in globals():
    date = "now 7-d"

SEED_TOPIC = seed_topic
GEO = geo
DATE_RANGE = date

def get_breakout_trends(topic):
    """Fetches 'Rising' and 'Top' related queries from Google Trends."""
    url = "https://api.hasdata.com/scrape/google-trends/search"
    headers = {"x-api-key": API_KEY, "Content-Type": "application/json"}
    
    params = {
        "q": topic,
        "dataType": "relatedQueries",
        "geo": GEO,
        "date": DATE_RANGE
    }

    try:
        response = requests.get(url, headers=headers, params=params)
        
        if response.status_code == 200:
            return response.json()
        else:
            print(f"Error {response.status_code}: {response.text}")
            return None
            
    except Exception as e:
        print(f"Connection Error: {e}")
        return None

if __name__ == "__main__":
    print(f"Fetching breakout trends for: '{SEED_TOPIC}'...")
    print(f"Geo: {GEO}, Date Range: {DATE_RANGE}\n")
    
    data = get_breakout_trends(SEED_TOPIC)

    if data and "relatedQueries" in data:
        rising = data["relatedQueries"].get("rising", [])
        print(f"\n--- Rising Queries (The Opportunity) ---")
        for item in rising[:10]:
            print(f"[Growth: {item['value']}] {item['query']}")

        top = data["relatedQueries"].get("top", [])
        print(f"\n--- Top Queries (The Volume) ---")
        for item in top[:5]:
            print(f"[Index: {item['value']}] {item['query']}")
    else:
        print("No trend data found.")