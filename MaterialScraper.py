import requests
from bs4 import BeautifulSoup
import json

# Base URL
base_url = "https://monsterhunterwilds.wiki.fextralife.com/Materials"

# Send request to the materials page
response = requests.get(base_url)

if response.status_code == 200:
    soup = BeautifulSoup(response.content, 'html.parser')

    # Find the first table on the page
    table = soup.find('table')

    if table:
        material_data = []

        # Extract rows from the table
        rows = table.find_all('tr')

        for row in rows[1:]:  # Skip header row
            cols = row.find_all('td')
            if len(cols) < 3:
                continue  # Skip if row does not have enough columns

            material = {}

            # Extract material name and image
            name_tag = cols[0].find('a')
            image_tag = cols[0].find('img')

            material["Name"] = name_tag.get_text(strip=True) if name_tag else "Unknown"
            material["Image"] = image_tag["src"] if image_tag else "No Image"

            # Extract rarity
            rarity_div = cols[1].find('div')
            material["Rarity"] = rarity_div.get_text(strip=True) if rarity_div else "Unknown"

            # Extract sources (monsters or locations)
            sources = [a.get_text(strip=True) for a in cols[2].find_all('a')]
            material["Source"] = ', '.join(sources) if sources else "Unknown"

            material_data.append(material)

        # Save data to JSON
        with open('materials.json', 'w', encoding='utf-8') as outfile:
            json.dump(material_data, outfile, indent=4, ensure_ascii=False)

        print("Scraping complete. Data saved to 'materials.json'.")

    else:
        print("No materials table found.")
else:
    print(f"Failed to fetch the page. Status code: {response.status_code}")
