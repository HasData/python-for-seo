"""Runs the script Google's AI Overview serves for "python script for seo" against
200 live domains, unchanged, and classifies each outcome.

Three outcomes per URL:
  data          - HTTP 200 and the audit found a title (the tool worked)
  blocked       - explicit refusal: non-200, timeout, connection error
  silent_blank  - HTTP 200 but the audit reports missing title/description/H1
                  while the rendered page has them (checked through the API leg)

Then the same URLs through the Web Scraping API with rendering, to see which of the
silent blanks and blocks actually carry the tags.

Domains are the top-ranked names per category from the Tranco list (list ZJQ6G,
2026-09-02); each domain's rank is recorded. One thread, polite delay.
Writes ai_script_probe.json next to the script.
"""
import json
import os
import pathlib
import re
import sys
import time
from urllib.parse import urljoin, urlparse

import requests
from bs4 import BeautifulSoup

sys.stdout.reconfigure(encoding="utf-8", errors="replace")
S = pathlib.Path(__file__).resolve().parent
KEY = os.environ["HASDATA_API_KEY"]
HD = {"Content-Type": "application/json", "x-api-key": KEY}

CATEGORIES = {
    "ecommerce": [
        "amazon.com", "walmart.com", "ebay.com", "target.com", "etsy.com", "bestbuy.com",
        "homedepot.com", "costco.com", "lowes.com", "wayfair.com", "nike.com", "ikea.com",
        "chewy.com", "macys.com", "kohls.com", "sephora.com", "ulta.com", "newegg.com",
        "asos.com", "zara.com", "shein.com", "temu.com", "aliexpress.com", "wish.com",
        "overstock.com", "nordstrom.com", "gap.com", "adidas.com", "underarmour.com", "rei.com",
        "staples.com", "petco.com", "michaels.com", "dickssportinggoods.com", "carvana.com",
        "autozone.com", "advanceautoparts.com", "sharkninja.com", "dyson.com", "samsung.com",
    ],
    "saas": [
        "salesforce.com", "hubspot.com", "atlassian.com", "slack.com", "zoom.us", "notion.so",
        "figma.com", "asana.com", "monday.com", "airtable.com", "dropbox.com", "box.com",
        "zendesk.com", "intercom.com", "twilio.com", "stripe.com", "shopify.com", "squarespace.com",
        "wix.com", "webflow.com", "mailchimp.com", "klaviyo.com", "segment.com", "datadoghq.com",
        "newrelic.com", "pagerduty.com", "okta.com", "auth0.com", "cloudflare.com", "digitalocean.com",
        "heroku.com", "vercel.com", "netlify.com", "gitlab.com", "bitbucket.org", "docker.com",
        "jetbrains.com", "postman.com", "snowflake.com", "databricks.com",
    ],
    "news": [
        "nytimes.com", "washingtonpost.com", "wsj.com", "cnn.com", "bbc.com", "reuters.com",
        "apnews.com", "bloomberg.com", "ft.com", "theguardian.com", "forbes.com", "cnbc.com",
        "usatoday.com", "npr.org", "nbcnews.com", "cbsnews.com", "abcnews.go.com", "foxnews.com",
        "latimes.com", "politico.com", "axios.com", "thehill.com", "newsweek.com", "time.com",
        "theatlantic.com", "vox.com", "businessinsider.com", "techcrunch.com", "theverge.com",
        "arstechnica.com", "wired.com", "engadget.com", "zdnet.com", "venturebeat.com",
        "espn.com", "sbnation.com", "variety.com", "hollywoodreporter.com", "rollingstone.com",
        "economist.com",
    ],
    "marketplaces": [
        "airbnb.com", "booking.com", "expedia.com", "vrbo.com", "tripadvisor.com", "hotels.com",
        "kayak.com", "priceline.com", "opentable.com", "doordash.com", "ubereats.com", "grubhub.com",
        "instacart.com", "fiverr.com", "upwork.com", "freelancer.com", "zillow.com", "redfin.com",
        "realtor.com", "trulia.com", "apartments.com", "cars.com", "cargurus.com", "truecar.com",
        "carmax.com", "craigslist.org", "offerup.com", "mercari.com", "poshmark.com", "stubhub.com",
        "ticketmaster.com", "seatgeek.com", "vivid seats.com".replace(" ", ""), "gumtree.com",
        "yelp.com", "angi.com", "thumbtack.com", "taskrabbit.com", "rover.com", "care.com",
    ],
    "jobs": [
        "indeed.com", "linkedin.com", "glassdoor.com", "monster.com", "ziprecruiter.com",
        "careerbuilder.com", "simplyhired.com", "dice.com", "flexjobs.com", "snagajob.com",
        "usajobs.gov", "idealist.org", "themuse.com", "wellfound.com", "builtin.com",
        "lever.co", "greenhouse.io", "workable.com", "smartrecruiters.com", "jobvite.com",
        "adzuna.com", "jooble.org", "talent.com", "neuvoo.com", "seek.com.au", "reed.co.uk",
        "totaljobs.com", "cv-library.co.uk", "jobsite.co.uk", "stepstone.de", "xing.com",
        "workday.com", "icims.com", "bamboohr.com", "gusto.com", "rippling.com", "deel.com",
        "remote.com", "remoteok.com", "weworkremotely.com",
    ],
}

# ---- the AI Overview's script, verbatim from the served answer -------------
AI_HEADERS = {
    "User-Agent": "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/120.0.0.0 Safari/537.36"
}


def ai_audit(target_url):
    """The AI Overview's run_seo_audit, returning the findings instead of printing."""
    out = {"http": None, "error": None, "title": None, "desc": None, "h1_count": None,
           "images": None, "missing_alt": None, "links": None}
    try:
        response = requests.get(target_url, headers=AI_HEADERS, timeout=10)
        out["http"] = response.status_code
        if response.status_code != 200:
            return out
    except Exception as e:
        out["error"] = type(e).__name__
        return out

    soup = BeautifulSoup(response.text, "html.parser")
    domain = urlparse(target_url).netloc

    title_tag = soup.find("title")
    out["title"] = title_tag.string.strip() if title_tag and title_tag.string else None

    meta_desc = soup.find("meta", attrs={"name": "description"})
    out["desc"] = meta_desc.get("content").strip() if meta_desc and meta_desc.get("content") else None

    h1_tags = soup.find_all("h1")
    out["h1_count"] = len(h1_tags)

    images = soup.find_all("img")
    out["images"] = len(images)
    out["missing_alt"] = sum(1 for img in images if not img.get("alt") or img.get("alt").strip() == "")

    links = soup.find_all("a", href=True)
    out["links"] = len(links)
    return out
# ---------------------------------------------------------------------------


def api_audit(target_url, tries=3):
    """The same fields, but from a rendered page fetched through the API."""
    for i in range(tries):
        r = requests.post("https://api.hasdata.com/scrape/web", headers=HD,
                          data=json.dumps({"url": target_url, "proxyType": "datacenter",
                                           "jsRendering": True, "outputFormat": ["html"]}),
                          timeout=180)
        if r.status_code != 429:
            break
        time.sleep(6 * (i + 1))
    if r.status_code != 200 or not r.text:
        return {"http": r.status_code, "title": None, "desc": None, "h1_count": None}
    soup = BeautifulSoup(r.text, "html.parser")
    t = soup.find("title")
    m = soup.find("meta", attrs={"name": "description"})
    return {"http": 200,
            "title": t.string.strip() if t and t.string else (t.get_text(strip=True) if t else None),
            "desc": m.get("content").strip() if m and m.get("content") else None,
            "h1_count": len(soup.find_all("h1"))}


ranks = {}
for line in (S / "tranco.csv").read_text(encoding="utf-8", errors="replace").splitlines():
    parts = line.split(",")
    if len(parts) == 2:
        ranks[parts[1].strip()] = int(parts[0])

rows = []
for cat, domains in CATEGORIES.items():
    for dom in domains:
        url = f"https://{dom}/"
        rec = {"category": cat, "domain": dom, "tranco_rank": ranks.get(dom), "url": url}
        rec["ai"] = ai_audit(url)
        rows.append(rec)
        time.sleep(0.7)
    done = sum(1 for r in rows if r["category"] == cat)
    print(f"{cat}: probed {done}")

# classify the local leg
for r in rows:
    a = r["ai"]
    if a["error"] or (a["http"] and a["http"] != 200):
        r["local"] = "blocked"
    elif a["title"]:
        r["local"] = "data"
    else:
        r["local"] = "no_title"

need_api = [r for r in rows if r["local"] != "data" or not r["ai"]["desc"] or r["ai"]["h1_count"] == 0]
print(f"API leg on {len(need_api)} of {len(rows)} URLs (every non-clean local result)")
for i, r in enumerate(need_api, 1):
    r["api"] = api_audit(r["url"])
    if i % 20 == 0:
        print(f"  api {i}/{len(need_api)}")
    time.sleep(0.5)

# final classification: a silent blank is a local 200 whose missing field exists on the rendered page
for r in rows:
    api = r.get("api")
    a = r["ai"]
    r["silent_fields"] = []
    if r["local"] in ("data", "no_title") and api and api.get("http") == 200:
        if not a["title"] and api.get("title"):
            r["silent_fields"].append("title")
        if not a["desc"] and api.get("desc"):
            r["silent_fields"].append("description")
        if not a["h1_count"] and api.get("h1_count"):
            r["silent_fields"].append("h1")
    if r["local"] == "blocked":
        r["outcome"] = "blocked"
    elif r["silent_fields"]:
        # a field the script reported missing that the rendered page actually has
        r["outcome"] = "silent_blank"
    else:
        # includes pages that really carry no title or no h1: the API leg agreed
        r["outcome"] = "data"

agg = {}
for cat in CATEGORIES:
    sub = [r for r in rows if r["category"] == cat]
    agg[cat] = {
        "n": len(sub),
        "data": sum(1 for r in sub if r["outcome"] == "data"),
        "blocked": sum(1 for r in sub if r["outcome"] == "blocked"),
        "silent_blank": sum(1 for r in sub if r["outcome"] == "silent_blank"),
        "api_data": sum(1 for r in sub if r.get("api", {}).get("title")),
        "api_attempted": sum(1 for r in sub if r.get("api")),
        "wrong_fields": sum(len(r["silent_fields"]) for r in sub),
    }
totals = {k: sum(v[k] for v in agg.values()) for k in ("n", "data", "blocked", "silent_blank", "api_data", "api_attempted", "wrong_fields")}

(S / "ai_script_probe.json").write_text(json.dumps(
    {"tranco_list": "ZJQ6G (2026-09-02)", "per_category": agg, "totals": totals, "rows": rows},
    ensure_ascii=False, indent=1), encoding="utf-8")
print(json.dumps(agg, indent=1))
print(json.dumps(totals, indent=1))
print("saved ai_script_probe.json")
