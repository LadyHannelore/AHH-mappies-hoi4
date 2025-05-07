import csv
import os
import re

# Paths
base = os.path.dirname(__file__)
country_tags_path = os.path.join(base, "common", "country_tags", "00_mappies_countries.txt")
countries_dir = os.path.join(base, "common", "countries")
history_dir = os.path.join(base, "history", "countries")
localisation_path = os.path.join(base, "localisation", "english", "mappies_countries_l_english.yml")
war_csv = os.path.join(base, "Map game sheet - War.csv")
view_csv = os.path.join(base, "Map game sheet - View.csv")

# Ensure output dirs exist
os.makedirs(countries_dir, exist_ok=True)
os.makedirs(history_dir, exist_ok=True)

# Helper: make a 3-letter tag from Discord name
def make_tag(name, used_tags):
    tag = re.sub(r'\W+', '', name).upper()[:3]
    if len(tag) < 3:
        tag = (tag + "XXX")[:3]
    orig = tag
    i = 2
    while tag in used_tags:
        tag = (orig[:2] + str(i))[:3]
        i += 1
    used_tags.add(tag)
    return tag

# Read View CSV for nation info
nations = []
with open(view_csv, encoding="utf-8") as f:
    reader = csv.DictReader(f)
    for row in reader:
        nations.append({
            "discord": row["Discord name"],
            "nation": row["Nation name"],
            "capital": row["Capital"],
        })

# Read War CSV for army info
army_map = {}
with open(war_csv, encoding="utf-8") as f:
    reader = csv.DictReader(f)
    for row in reader:
        army_map[row["Discord name"]] = int(row["Army"]) if row["Army"].isdigit() else 0

# Generate tags and build mapping
used_tags = set()
tag_map = {}
for n in nations:
    tag = make_tag(n["discord"], used_tags)
    tag_map[n["discord"]] = tag
    n["tag"] = tag
    n["army"] = army_map.get(n["discord"], 0)

# Write country_tags file
with open(country_tags_path, "w", encoding="utf-8") as f:
    f.write("# Mappies mod country tags\n")
    for n in nations:
        f.write(f'{n["tag"]} = "countries/{n["tag"]}.txt"\n')

# Write countries files
for n in nations:
    country_file = os.path.join(countries_dir, f"{n['tag']}.txt")
    # Assign a color based on tag hash (for placeholder)
    color = [hash(n['tag'] + str(i)) % 256 for i in range(3)]
    with open(country_file, "w", encoding="utf-8") as f:
        f.write(f'graphical_culture = western_european_gfx\n')
        f.write(f'graphical_culture_2d = western_european_2d\n')
        f.write(f'color = {{ {color[0]} {color[1]} {color[2]} }}\n')

# Write history files
for n in nations:
    fname = f"{n['tag']} - {n['nation']}.txt"
    history_file = os.path.join(history_dir, fname.replace("/", "_"))
    with open(history_file, "w", encoding="utf-8") as f:
        f.write(f'capital = 1 # TODO: Replace with correct state ID for {n["capital"]}\n')
        f.write('oob = "{}_1936"\n'.format(n["tag"]))
        f.write('set_politics = {\n')
        f.write('    ruling_party = neutrality\n')
        f.write('    elections_allowed = yes\n')
        f.write('    last_election = "1935.1.1"\n')
        f.write('    election_frequency = 48\n')
        f.write('}\n')
        f.write(f'set_country_flag = {n["tag"]}_country_exists\n\n')
        for i in range(1, n["army"] + 1):
            f.write('create_unit = {\n')
            f.write(f'    division_name = "{i}th Infantry Division"\n')
            f.write('    division_template = "Infantry Division"\n')
            f.write('    start_experience_factor = 0.3\n')
            f.write(f'    owner = {n["tag"]}\n')
            f.write('    division = {\n')
            f.write('        infantry = 9\n')
            f.write('    }\n')
            f.write('}\n')

# Write localisation file
with open(localisation_path, "w", encoding="utf-8") as f:
    f.write("l_english:\n")
    for n in nations:
        f.write(f' {n["tag"]}:0 "{n["nation"]}"\n')

print("Done! Generated country tags, country files, history, and localisation.")
