import requests
from bs4 import BeautifulSoup
from urllib.parse import quote


SEARCHES = [
    "SOC Analyst Israel",
    "Security Analyst Israel",
    "MDR Analyst Israel",
    "Cybersecurity Analyst Israel",
    "SecOps Israel",
    "Incident Response Israel",
    "DFIR Israel",
    "Threat Intelligence Israel"
]


HEADERS = {
    "User-Agent": "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 Chrome/151.0 Safari/537.36",
    "Accept-Language": "en-US,en;q=0.9"
}


def search_google(query):

    url = (
        "https://www.google.com/search?q="
        + quote(query)
    )

    response = requests.get(
        url,
        headers=HEADERS,
        timeout=20
    )

    print(
        f"\nSearch: {query}"
    )

    print(
        f"Status: {response.status_code}"
    )

    soup = BeautifulSoup(
        response.text,
        "html.parser"
    )

    links = soup.find_all("a")

    results = []

    for link in links:

        href = link.get("href")

        text = link.get_text(
            " ",
            strip=True
        )

        if not href or not text:
            continue

        if "linkedin.com/jobs" in href:

            results.append({
                "title": text,
                "link": href
            })

    return results


all_results = []


for query in SEARCHES:

    results = search_google(query)

    print(
        f"Found LinkedIn results: {len(results)}"
    )

    all_results.extend(results)


print()
print("================================")
print("TOTAL RESULTS:", len(all_results))
print("================================")


for number, result in enumerate(
    all_results[:20],
    start=1
):

    print()
    print(
        f"{number}. {result['title']}"
    )

    print(
        result["link"]
    )