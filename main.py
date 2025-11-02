import requests
import pandas as pd
import os
import google.generativeai as genai
from google_auth_oauthlib.flow import InstalledAppFlow
from googleapiclient.discovery import build
from google.auth.transport.requests import Request
import pickle

if not os.path.exists("credentials.json"):
    raise FileNotFoundError("⚠️ credentials.json not found. Please place it in the same folder as this script.")
else:
    print("✅ credentials.json found. Proceeding...")

genai.configure(api_key=os.getenv("GEMINI_API_KEY"))  # Replace with your Gemini key
model = genai.GenerativeModel("models/gemini-2.5-flash")

SCOPES = ['https://www.googleapis.com/auth/blogger']
BLOG_ID = os.getenv("BLOG_ID")  # Replace with your blog ID

def get_blogger_service():
    creds = None
    if os.path.exists("token.pickle"):
        with open("token.pickle", "rb") as token:
            creds = pickle.load(token)
    if not creds or not creds.valid:
        if creds and creds.expired and creds.refresh_token:
            creds.refresh(Request())
        else:
            flow = InstalledAppFlow.from_client_secrets_file("credentials.json", SCOPES)
            creds = flow.run_local_server(port=0)
        with open("token.pickle", "wb") as token:
            pickle.dump(creds, token)
    service = build("blogger", "v3", credentials=creds)
    return service



def get_today_birthdays():
    query = """
    SELECT ?person ?personLabel ?dob (SAMPLE(?desc) AS ?occupation) (SAMPLE(?wikiLink) AS ?wikiLink)
       (COUNT(DISTINCT ?wp) AS ?languageCount)
       (COUNT(DISTINCT ?award) AS ?awardCount)
    WHERE {
      ?person wdt:P31 wd:Q5;
              wdt:P569 ?dob;
              wdt:P27 wd:Q668.
      FILTER(MONTH(?dob) = MONTH(NOW()) && DAY(?dob) = DAY(NOW())).
      OPTIONAL { ?person wdt:P106 ?desc. }
      OPTIONAL {
        ?sitelink schema:about ?person;
                  schema:isPartOf <https://en.wikipedia.org/>.
        BIND(?sitelink AS ?wikiLink)
      }
      OPTIONAL {
        ?wp schema:about ?person;
            schema:isPartOf ?langwiki.
        FILTER(CONTAINS(STR(?langwiki), "wikipedia.org"))
      }
      OPTIONAL { ?person wdt:P166 ?award. }
      SERVICE wikibase:label { bd:serviceParam wikibase:language "en". }
    }
    GROUP BY ?person ?personLabel ?dob
    ORDER BY DESC(?languageCount) DESC(?awardCount)
    """
    url = "https://query.wikidata.org/sparql"
    headers = {"Accept": "application/sparql-results+json"}
    r = requests.get(url, params={'query': query}, headers=headers)
    data = r.json()
    results = data['results']['bindings']

    records = []
    for res in results:
        records.append({
            "name": res.get("personLabel", {}).get("value", ""),
            "dob": res.get("dob", {}).get("value", ""),
            "desc": res.get("desc", {}).get("value", ""),
            "wikiLink": res.get("wikiLink", {}).get("value", ""),
            "languageCount": int(res.get("languageCount", {}).get("value", 0)),
            "awardCount": int(res.get("awardCount", {}).get("value", 0))
        })
    return pd.DataFrame(records)


def get_wikipedia_page_length(title):
    url = "https://en.wikipedia.org/w/api.php"
    params = {"action": "query", "titles": title, "prop": "info", "format": "json"}
    headers = {"User-Agent": "IndiChroniclesBot/1.0 (mailto:arpityadavphn@gmail.com)"}
    r = requests.get(url, params=params, headers=headers)
    if r.status_code != 200:
        return 0
    data = r.json()
    pages = data.get("query", {}).get("pages", {})
    for _, page_info in pages.items():
        return page_info.get("length", 0)
    return 0


def compute_importance(df):
    df['pageLength'] = [
        get_wikipedia_page_length(link.split("/wiki/")[-1]) if link else 0
        for link in df['wikiLink']
    ]
    df['importanceScore'] = (
        df['languageCount'] * 3 +
        df['awardCount'] * 2 +
        df['pageLength'] / 10000
    )
    return df.sort_values(by='importanceScore', ascending=False)


def generate_article(person):
    prompt = f"""
    Write a detailed, fact-based, magazine-style 600-word article about {person['name']},
    who was born on {person['dob']}. The person is known for {person['desc']}.
    Include introduction, major achievements, impact, and legacy. Use warm tone.
    """
    try:
        response = model.generate_content(prompt)
        return response.text
    except Exception as e:
        print(f"❌ Error generating article for {person['name']}: {e}")
        return ""


# ---- 5️⃣ Publish to Blogger ----
def publish_to_blogger(service, title, content):
    try:
        post = {
            "kind": "blogger#post",
            "title": title,
            "content": content,
        }
        result = service.posts().insert(blogId=BLOG_ID, body=post).execute()
        print(f"✅ Published: {result['url']}")
    except Exception as e:
        print(f"❌ Failed to publish {title}: {e}")



if __name__ == "__main__":
    print("Fetching today's Indian birthdays...")
    df = get_today_birthdays()
    df = compute_importance(df)
    top5 = df.head(5)

    print("\n Top 5 Influential Indians Born Today:")
    print(top5[['name', 'desc', 'importanceScore']])

    blogger_service = get_blogger_service()

    for _, row in top5.iterrows():
        print(f"\n🧠 Generating article for {row['name']}...")
        article = generate_article(row)
        if article:
            publish_to_blogger(blogger_service, row['name'], article)
