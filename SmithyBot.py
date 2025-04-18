import os
import json

from dotenv import load_dotenv
import discord
from discord.ext import commands


monster_names = [
        "Ajarakan", "Arkveld", "Balahara", "Blangonga", "Chatacabra", "Congalala", "Doshaguma",
        "Gore Magala", "Gravios", "Guardian Arkveld", "Guardian Doshaguma", "Guardian Ebony Odogaron",
        "Guardian Fulgur Anjanath", "Guardian Rathalos", "Gypceros", "Hirabami", "Jin Dahaad", "Lala Barina",
        "Nerscylla", "Nu Udra", "Quematrice", "Rathalos", "Rathian", "Rey Dau", "Rompopolo", "Uth Duna",
        "Xu Wu", "Yian Kut-Ku", "Zoh Shia"
    ]


# Load the monster data from the JSON file
with open("large_monsters.json", "r", encoding="utf-8") as f:
    monster_data = json.load(f)

# Load material data from JSON
with open("materials.json", "r", encoding="utf-8") as file:
    materials = json.load(file)


# Function to search for a monster
def get_monster_info(name):
    for m in monster_data:
        if m["name"].lower() == name.lower():
            return m
    return None


def get_star_emoji(rating):
    star_map = {"1_star": "⭐", "2_star": "⭐⭐", "3_star": "⭐⭐⭐", "4_star": "⭐⭐⭐⭐", "uneffective": "❌"}
    return star_map.get(rating, "?")


def format_weaknesses(weaknesses, categories):
    if not weaknesses:
        return "N/A"

    # Create a list to hold the parts and their weaknesses, preserving order
    part_data = {category: [] for category in categories}
    part_names = []  # Using a list to preserve the order

    # Organize weaknesses by part and category
    for entry in weaknesses:
        part_name = entry["Monster Part"]
        if part_name not in part_names:
            part_names.append(part_name)  # Add part to preserve order
        for idx, rating in enumerate(entry["Weaknesses"]):
            category = categories[idx]
            part_data[category].append((part_name, get_star_emoji(rating)))

    # Prepare table-like format for weapon weaknesses
    table_header = "Part | " + " | ".join(categories)
    rows = []

    for part_name in part_names:
        row = [f"**{part_name}:**"]
        for category in categories:
            # Find the weakness for the given part and category
            weakness = next((rating for part, rating in part_data[category] if part == part_name), "N/A")
            row.append(weakness)
        rows.append(" | ".join(row))

    # Combine header, separator, and rows to form the final table
    output = f"**{table_header}**\n" + "\n".join(rows)
    return output


load_dotenv()
TOKEN = os.getenv('DISCORD_TOKEN')

intents = discord.Intents.default()
intents.message_content = True

bot = commands.Bot(command_prefix="!", intents=intents)


# To sync the commands with Discord's API
@bot.event
async def on_ready():
    # Sync the slash commands to ensure they are registered with Discord
    await bot.tree.sync()
    print(f'{bot.user.name} has connected to Discord!')


@bot.command(name='hello')
async def hello(ctx):
    await ctx.send('Hello User!')


@bot.hybrid_command(name='monster')
async def monster(ctx, *, name: str):
    if name.lower() == "help" or name.lower() == "h":
        output = "**Available Monsters:**\n"
        output += "```\n"
        output += "\n".join(monster_names)
        output += "\n```"
        await ctx.send(output)
        return
    m = next((m for m in monster_data if m["name"].lower() == name.lower()), None)

    if not m:
        await ctx.send("Monster not found!")
        return

    embed = discord.Embed(title=m["name"], url=m["url"], color=discord.Color.red())

    # Basic Info
    info = m.get("basic_info", {})

    # Append the image URL to the base URL
    embed.set_image(url=info["image"])

    for key, value in info.items():
        if key == "Location(s)":  # Special handling for locations
            # Display locations cleanly (e.g., as a comma-separated string or bullet list)
            locations = ", ".join(value) if isinstance(value, list) else value
            embed.add_field(name=key, value=locations, inline=True)
        elif key == "image":
            pass
        else:
            embed.add_field(name=key, value=value, inline=True)

    # Weapon Weaknesses (Table format)
    weapon_categories = ["Cut Damage", "Blunt Damage", "Ammo Damage"]
    weapon_weaknesses = format_weaknesses(m.get("Weapons", []), weapon_categories)
    if weapon_weaknesses != "N/A":
        embed.add_field(name="Weapon Weaknesses", value=weapon_weaknesses, inline=False)

    # Elemental Weaknesses
    element_categories = ["Fire", "Water", "Thunder", "Ice", "Dragon"]
    element_weaknesses = format_weaknesses(m.get("Elements", []), element_categories)
    if element_weaknesses != "N/A":
        embed.add_field(name="Elemental Weaknesses", value=element_weaknesses, inline=False)
    # Ailments Formatting (Simple List)
    ailment_categories = ["Poison", "Sleep", "Paralysis", "Blastblight", "Stun", "Exhaust"]
    ailments = "\n".join(f"**{ailment}:** {get_star_emoji(star)}" for ailment, star in
                         zip(ailment_categories, m.get("Ailments", [])))
    if ailments:
        embed.add_field(name="Ailments", value=ailments, inline=False)

    await ctx.send(embed=embed)


@bot.hybrid_command(name="material")
async def material(ctx, *, name: str):
    """Hybrid command to search materials by name."""
    material_info = next((m for m in materials if name.lower() in m["Name"].lower()), None)

    if material_info:
        # Create an embed
        embed = discord.Embed(
            title=material_info["Name"],
            description=f"**Rarity:** {material_info['Rarity']}\n"
                        f"**Source:** {material_info['Source']}",
            color=discord.Color.gold()
        )

        # Add material image if available
        if material_info.get("Image") and material_info["Image"] != "No Image":
            embed.set_thumbnail(url=f"https://monsterhunterwilds.wiki.fextralife.com{material_info['Image']}")

        await ctx.send(embed=embed)
    else:
        await ctx.send(f"❌ No material found with the name **{name}**.")

bot.run(TOKEN)
