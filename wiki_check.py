import requests

def wiki_check(name):
    S = requests.Session()
    S.headers.update({"User-Agent": "twenty-questions-wiki-check/1.0 (contact: tanveerao@gmail.com)"})
    r = S.get(f"https://en.wikipedia.org/api/rest_v1/page/summary/{name.replace(' ', '_')}")
    data = r.json()
    if data.get("type") == "disambiguation":
        return {"status": "AMBIGUOUS", "title": data.get("title")}
    if r.status_code == 404:
        return {"status": "NOT_FOUND"}
    title = data["title"]
    info = S.get("https://en.wikipedia.org/w/api.php", params={
        "action": "query", "titles": title, "prop": "info", "format": "json"
    }).json()
    page = next(iter(info["query"]["pages"].values()))
    return {"status": "OK", "title": title, "length_bytes": page.get("length", 0)}

if __name__ == "__main__":
    name = input("Enter a name to look up: ").strip()
    print(name, wiki_check(name))
