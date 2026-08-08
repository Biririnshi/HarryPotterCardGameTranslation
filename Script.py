import requests
import json
import time

BASE = "https://tcg.movic.jp/harrypotter/card-management/api/public/cards"

headers = {
    "Accept": "application/json",
    "Content-Type": "application/json",
}

session = requests.Session()

# Define the product IDs
product_ids = [1,2,3,4,5,6,7]
varients = ["false","true"]
combined_cards = []

# Search each product ID and combine the results
for product_id in product_ids:
    for varient in varients:
        response = session.post(
        f"{BASE}/search",
        json={"productIds":[product_id],"parallels":[varient]},
        headers=headers
        )
        # Check if the request was successful
        response.raise_for_status()
        cards = response.json().get("cards", [])
        combined_cards.extend(cards)
    
    # Print the number of card numbers for the current search
    print(f"Search for Product ID {product_id} contained {len(cards)} cards")

details = []
    
for card in combined_cards:
    number = card["cardNumber"]
    print(number)
    detail_response = session.post(
        f"{BASE}/detail",
        json={"cardNumber": number},
        headers=headers)
        # Check if the request was successful
    detail = detail_response.json()
    details.append(detail)
    time.sleep(0.5)


with open("harry_potter_cards.json", "w", encoding="utf-8") as f:
    json.dump(details, f, ensure_ascii=False, indent=2)
