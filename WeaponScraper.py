import requests
from bs4 import BeautifulSoup
import json

base_url = "https://monsterhunterwilds.wiki.fextralife.com/"
all_weapons = ["Great Sword", "Sword & Shield", "Dual Blades", "Long Sword", "Hammer", "Lance",
               "Switch Axe", "Insect Glaive", "Hunting Horn", "Gunlance", "Light Bowgun", "Heavy Bowgun",
               "Bow", "Charge Blade"]

weapon_types = ["Great Sword", "Sword & Shield", "Dual Blades", "Long Sword", "Hammer", "Lance"]
unique_weapon_types1 = ["Switch Axe", "Insect Glaive"]
unique_weapon_types2 = ["Hunting Horn", "Gunlance"]
unique_weapon_types3 = ["Light Bowgun", "Heavy Bowgun"]
unique_weapon_types4 = ["Bow", "Charge Blade"]


# Function to replace spaces with '+' and generate the URL
def generate_weapon_url(wt):
    return base_url + wt.replace(" ", "+")


# Initialize the list to store weapon data
weapons = []

# Loop through each weapon type and scrape data
for weapon_type in all_weapons:
    weapon_url = generate_weapon_url(weapon_type)
    print(f"Scraping data for {weapon_type} from {weapon_url}")

    response = requests.get(weapon_url)

    if response.status_code == 200:
        soup = BeautifulSoup(response.content, 'html.parser')

        tables = soup.find_all('table')
        if len(tables) < 2:
            print(f"Skipping {weapon_type} due to missing table.")
            continue

        table = tables[1]  # Assuming second table contains the data
        weapon_rows = table.find_all('tr')
        headers = table.find_all("th")
        header_names = []
        for th in headers:
            text = th.text.strip()
            if text:  # Use text if available
                header_names.append(text)
            else:  # Otherwise, extract from image filename
                img = th.find("img")
                if img and "src" in img.attrs:
                    filename = img["src"].rsplit("/", 1)[-1]  # Get filename without path
                    if filename.endswith(".png"):
                        words = filename[:-4].split("_")  # Remove .png and split by "_"
                        header_names.append(" ".join(words[:2]))  # Take first two words
        # print(header_names)
        for row in weapon_rows:
            weapon_data = {}
            cols = row.find_all('td')

            if len(cols) < 8:
                continue  # Skip incomplete rows

            # Extract the weapon name
            weapon_name_tag = cols[0].find('a')
            # Add weapon type
            weapon_data['Weapon Type'] = weapon_type
            weapon_data['Name'] = weapon_name_tag.get_text(strip=True) if weapon_name_tag else "Unknown"

            # Extract weapon image
            weapon_img_tag = cols[0].find('img')
            weapon_data['Image URL'] = weapon_img_tag['src'] if weapon_img_tag else "No Image Available"

            # Extract remaining fields
            weapon_data['Rarity'] = cols[1].get_text(strip=True)
            weapon_data['Attack'] = cols[2].get_text(strip=True)
            # Extract elemental damage
            element_text = cols[3].get_text(strip=True).split()
            weapon_data['Elemental Damage'] = " ".join(element_text[:2]) if len(element_text) > 1 else "None"
            weapon_data['Affinity'] = cols[4].get_text(strip=True)
            weapon_data['Defense'] = cols[5].get_text(strip=True)

            if weapon_type in weapon_types:

                # Extract decoration slots
                slots = [img['title'].lower().split('_')[0] + "_slot" for img in cols[6].find_all('img') if
                         'slot' in img['title'].lower()]
                weapon_data['Decoration Slots'] = ', '.join(slots) if slots else 'None'

                # Extract equipment skills
                skills = [link.get_text(strip=True) for link in cols[7].find_all('a')]
                weapon_data['Equipment Skills'] = ', '.join(skills) if skills else 'None'

                # Extract crafting materials
                crafting_materials = [li.get_text(strip=True) for li in cols[-1].find_all('li')]
                weapon_data['Crafting Materials'] = ', '.join(crafting_materials) if crafting_materials else 'None'

            elif weapon_type in unique_weapon_types1:

                # Extract uniques
                weapon_data[header_names[6]] = cols[6].get_text(strip=True)

                # Extract decoration slots
                slots = [img['title'].lower().split('_')[0] + "_slot" for img in cols[7].find_all('img') if
                         'slot' in img['title'].lower()]
                weapon_data['Decoration Slots'] = ', '.join(slots) if slots else 'None'

                # Extract equipment skills
                skills = [link.get_text(strip=True) for link in cols[8].find_all('a')]
                weapon_data['Equipment Skills'] = ', '.join(skills) if skills else 'None'

                # Extract crafting materials
                crafting_materials = [li.get_text(strip=True) for li in cols[-1].find_all('li')]
                weapon_data['Crafting Materials'] = ', '.join(crafting_materials) if crafting_materials else 'None'

            elif weapon_type in unique_weapon_types2:

                if weapon_type == "Hunting Horn":
                    td = cols[6]

                    # Extract the note names from the <img> alt attributes
                    note_names = ''
                    for img in td.find_all("img"):
                        alt_text = img.get("alt", "")
                        note_name = alt_text.split(" icon")[0]  # Get the first part before " icon"
                        note_names += ':' + note_name + ':'

                    weapon_data[header_names[6]] = note_names
                else:
                    weapon_data[header_names[6]] = cols[6].get_text(strip=True)

                weapon_data[header_names[7]] = cols[7].get_text(strip=True)

                # Extract decoration slots
                slots = [img['title'].lower().split('_')[0] + "_slot" for img in cols[8].find_all('img') if
                         'slot' in img['title'].lower()]
                weapon_data['Decoration Slots'] = ', '.join(slots) if slots else 'None'

                # Extract equipment skills
                skills = [link.get_text(strip=True) for link in cols[9].find_all('a')]
                weapon_data['Equipment Skills'] = ', '.join(skills) if skills else 'None'

                # Extract crafting materials
                crafting_materials = [li.get_text(strip=True) for li in cols[-1].find_all('li')]
                weapon_data['Crafting Materials'] = ', '.join(crafting_materials) if crafting_materials else 'None'

            elif weapon_type in unique_weapon_types3:

                weapon_data[header_names[6]] = cols[6].get_text(strip=True)
                weapon_data[header_names[7]] = cols[7].get_text(strip=True)
                weapon_data[header_names[8]] = cols[8].get_text(strip=True)
                if weapon_type == "Heavy Bowgun":
                    weapon_data[header_names[9]] = cols[9].get_text(strip=True)
                    weapon_data[header_names[10]] = cols[10].get_text(strip=True)

                # Extract decoration slots
                slots = [img['title'].lower().split('_')[0] + "_slot" for img in cols[-3].find_all('img') if
                         'slot' in img['title'].lower()]
                weapon_data['Decoration Slots'] = ', '.join(slots) if slots else 'None'

                # Extract equipment skills
                skills = [link.get_text(strip=True) for link in cols[-2].find_all('a')]
                weapon_data['Equipment Skills'] = ', '.join(skills) if skills else 'None'

                # Extract crafting materials
                crafting_materials = [li.get_text(strip=True) for li in cols[-1].find_all('li')]
                weapon_data['Crafting Materials'] = ', '.join(crafting_materials) if crafting_materials else 'None'

            elif weapon_type in unique_weapon_types4:

                if weapon_type == "Charge Blade":

                    weapon_data[header_names[8]] = cols[8].get_text(strip=True)

                    # Extract decoration slots
                    slots = [img['title'].lower().split('_')[0] + "_slot" for img in cols[6].find_all('img') if
                             'slot' in img['title'].lower()]
                    weapon_data['Decoration Slots'] = ', '.join(slots) if slots else 'None'

                    # Extract equipment skills
                    skills = [link.get_text(strip=True) for link in cols[7].find_all('a')]
                    weapon_data['Equipment Skills'] = ', '.join(skills) if skills else 'None'

                    # Extract crafting materials
                    crafting_materials = [li.get_text(strip=True) for li in cols[-1].find_all('li')]
                    weapon_data['Crafting Materials'] = ', '.join(crafting_materials) if crafting_materials else 'None'

                elif weapon_type == "Bow":

                    weapon_data['Rarity'] = cols[6].get_text(strip=True)
                    weapon_data['Attack'] = cols[1].get_text(strip=True)
                    # Extract elemental damage
                    element_text = cols[2].get_text(strip=True).split()
                    weapon_data['Elemental Damage'] = " ".join(element_text[:2]) if len(element_text) > 1 else "None"
                    weapon_data['Affinity'] = cols[3].get_text(strip=True)
                    weapon_data['Defense'] = cols[4].get_text(strip=True)

                    weapon_data[header_names[8]] = cols[8].get_text(strip=True)

                    # Extract decoration slots
                    slots = [img['title'].lower().split('_')[0] + "_slot" for img in cols[5].find_all('img') if
                             'slot' in img['title'].lower()]
                    weapon_data['Decoration Slots'] = ', '.join(slots) if slots else 'None'

                    # Extract equipment skills
                    skills = [link.get_text(strip=True) for link in cols[7].find_all('a')]
                    weapon_data['Equipment Skills'] = ', '.join(skills) if skills else 'None'

                    # Extract crafting materials
                    crafting_materials = [li.get_text(strip=True) for li in cols[-1].find_all('li')]
                    weapon_data['Crafting Materials'] = ', '.join(crafting_materials) if crafting_materials else 'None'

                    # Append to list
            if weapon_data['Name'] != "Unknown":
                weapons.append(weapon_data)

# Save the data to JSON
with open('weapon_data.json', 'w', encoding='utf-8') as outfile:
    json.dump(weapons, outfile, indent=4, ensure_ascii=False)

print("Scraping complete. Data saved to 'weapon_data.json'.")