import requests
from bs4 import BeautifulSoup
import json


def get_monster_data():
    monster_names = [
        "Ajarakan", "Arkveld", "Balahara", "Blangonga", "Chatacabra", "Congalala", "Doshaguma",
        "Gore Magala", "Gravios", "Guardian Arkveld", "Guardian Doshaguma", "Guardian Ebony Odogaron",
        "Guardian Fulgur Anjanath", "Guardian Rathalos", "Gypceros", "Hirabami", "Jin Dahaad", "Lala Barina",
        "Nerscylla", "Nu Udra", "Quematrice", "Rathalos", "Rathian", "Rey Dau", "Rompopolo", "Uth Duna",
        "Xu Wu", "Yian Kut-Ku", "Zoh Shia"
    ]

    base_url = "https://monsterhunterwilds.wiki.fextralife.com/"
    monster_data = []

    for monster in monster_names:
        monster_url = base_url + monster.replace(" ", "+")
        monster_info = scrape_monster_page(monster_url)
        monster_info["name"] = monster
        monster_data.append(monster_info)
    return monster_data


def scrape_monster_page(url):
    response = requests.get(url)

    if response.status_code != 200:
        print(f"Failed to retrieve {url}")
        return {"url": url}

    soup = BeautifulSoup(response.text, "html.parser")

    info = {"url": url}
    tables = soup.find_all("table")

    if len(tables) >= 4:
        # Extract Monster Info
        info["basic_info"] = extract_basic_info(tables[0])

        # Extract Weaknesses Table
        info["Weapons"] = extract_star_table(tables[1], 3)

        # Extract Monster Drops Table
        info["Elements"] = extract_star_table(tables[2], 5)

        # Extract Fourth Table
        info["Ailments"] = extract_fourth_table(tables[3])

    return info


def extract_basic_info(table):
    data = {}

    # Find the image in the second row of the table (the first monster image)
    img_tag = table.find_all("tr")[1].find("img")  # The second row should contain the monster's image
    if img_tag:
        image_url = img_tag["src"]
        # Ensure the image URL is absolute (if it starts with '/')
        if image_url.startswith("/"):
            image_url = "https://monsterhunterwilds.wiki.fextralife.com" + image_url
        data["image"] = image_url

    # Now, process the rest of the table rows
    rows = table.find_all("tr")
    for row in rows:
        cells = row.find_all("td")
        if len(cells) == 2:
            key = cells[0].text.strip()
            value = cells[1].text.strip()

            if key == "Location(s)":
                # Find all <a> tags within the <td> for locations
                location_links = cells[1].find_all("a")
                data[key] = [location.text.strip() for location in location_links]
            elif key in ["Enemy Type", "Species", "Elements"]:
                data[key] = value

    return data


def extract_star_table(table, num_columns):
    data = []
    rows = table.find_all("tr")[1:]  # Skip header row
    for row in rows:
        columns = row.find_all("td")
        if len(columns) >= num_columns:
            entry = {
                "Monster Part": row.find("th").text.strip(),
                "Weaknesses": [identify_star_rating(col) for col in columns[:num_columns]]
            }
            data.append(entry)
    return data


def extract_fourth_table(table):
    data = []
    rows = table.find_all("tr")[1:]  # Skip header row
    for row in rows:
        columns = row.find_all("td")
        if len(columns) >= 3:
            data.append(identify_star_rating(columns[2]))
    return data


def identify_star_rating(td):
    img = td.find("img")
    if img:
        src = img["src"]
        if "1_star" in src:
            return "1_star"
        elif "2_star" in src:
            return "2_star"
        elif "3_star" in src:
            return "3_star"
        elif "4_star" in src:
            return "4_star"
        elif "uneffective" in src:
            return "uneffective"
    return "unknown"


if __name__ == "__main__":
    monsters = get_monster_data()
    with open("large_monsters.json", "w", encoding="utf-8") as f:
        json.dump(monsters, f, indent=4, ensure_ascii=False)
    print("Scraping complete. Data saved to large_monsters.json")

