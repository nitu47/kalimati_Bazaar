import requests
from bs4 import BeautifulSoup
import csv, datetime, os

URL = "https://kalimatimarket.gov.np/index.php/price"

def fetch_price_page():
    headers = {
        "User-Agent": "Mozilla/5.0 (Windows NT 10.0; Win64; x64)"
    }
    response = requests.get(URL, headers=headers)
    if response.status_code != 200:
        print(f" Failed to fetch page, status code: {response.status_code}")
        return None
    return response.text

def parse_prices(html):
    soup = BeautifulSoup(html, "html.parser")
    # Find the table by class, or fallback to first table
    table = soup.find("table", {"class": "table table-bordered"})
    if not table:
        table = soup.find("table")
    if not table:
        print(" Table not found")
        return []

    data = []
    today = datetime.date.today().isoformat()
    tbody = table.find("tbody")
    if not tbody:
        print(" No <tbody> in table")
        return []

    for row in tbody.find_all("tr"):
        cols = row.find_all("td")
        if len(cols) < 5:
            continue
        data.append({
            "date": today,
            "item": cols[0].get_text(strip=True),
            "unit": cols[1].get_text(strip=True),
            "min_price": cols[2].get_text(strip=True),
            "max_price": cols[3].get_text(strip=True),
            "avg_price": cols[4].get_text(strip=True)
        })
    return data

def save_to_csv(records, filename="kalimati_prices.csv"):
    file_exists = os.path.isfile(filename)
    with open(filename, "a", newline="", encoding="utf-8") as f:
        writer = csv.DictWriter(f, fieldnames=["date","item","unit","min_price","max_price","avg_price"])
        if not file_exists:
            writer.writeheader()
        writer.writerows(records)

def main():
    html = fetch_price_page()
    if not html:
        return

    prices = parse_prices(html)
    if prices:
        save_to_csv(prices)
        print(f" Saved {len(prices)} items for {datetime.date.today()}")
        for rec in prices[:10]:
            print(f"{rec['item']} ({rec['unit']}): min {rec['min_price']} / max {rec['max_price']} / avg {rec['avg_price']}")
    else:
        print(" No price records found.")

if __name__ == "__main__":
    main()
