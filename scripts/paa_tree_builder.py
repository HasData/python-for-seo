import requests
import time


# --- CONFIGURATION (Injected by Manager) ---
if 'API_KEY' not in globals():
    API_KEY = "HASDATA_API_KEY"

if 'root_keyword' not in globals():
    root_keyword = "coffee"

if 'max_depth' not in globals():
    max_depth = 2


ROOT_KEYWORD = root_keyword
MAX_DEPTH = max_depth


def get_paa_questions(query):
    """
    Fetches PAA questions for a given query using HasData's Google SERP API.
    """
    url = "https://api.hasdata.com/scrape/google/serp"

    params = {
        "q": query,
        "location": "United States",
        "deviceType": "desktop",
    }

    headers = {
        "x-api-key": API_KEY,
        "Content-Type": "application/json"
    }

    try:
        response = requests.get(url, params=params, headers=headers, timeout=20)

        if response.status_code == 200:
            data = response.json()
            return [item['question'] for item in data.get("relatedQuestions", [])]
        else:
            print(f"Error {response.status_code}: {response.text}")
            return []

    except Exception as e:
        print(f"Connection Failed: {e}")
        return []


def build_topic_tree(query, current_depth, max_depth, visited):
    """
    Recursively builds a tree of questions.
    """
    if current_depth > max_depth or query in visited:
        return {}

    print(f"Scanning Level {current_depth}: {query}")
    visited.add(query)

    paa_list = get_paa_questions(query)
    tree = {}

    for question in paa_list:
        sub_tree = build_topic_tree(
            question,
            current_depth + 1,
            max_depth,
            visited
        )
        tree[question] = sub_tree

    return tree


def print_tree(tree, level=0):
    for question, sub_questions in tree.items():
        indent = "    " * level
        print(f"{indent}- {question}")
        print_tree(sub_questions, level + 1)


if __name__ == "__main__":
    visited_queries = set()

    print(f"Building PAA Tree for: '{ROOT_KEYWORD}'")
    print(f"Max depth: {MAX_DEPTH}\n")

    topic_tree = build_topic_tree(
        ROOT_KEYWORD,
        current_depth=1,
        max_depth=MAX_DEPTH,
        visited=visited_queries
    )

    print(f"\n--- Topic Authority Tree ---")
    print(f"- {ROOT_KEYWORD}")
    print_tree(topic_tree)