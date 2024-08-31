import pandas as pd
import json
import re

with open('file.json', 'r', encoding='utf-8') as f:
    data = json.load(f)

df = pd.DataFrame(data)


def convert_height(height):
    height_clean = re.sub(r'\(.*?\)', '', height).strip()
    height_clean = re.sub(r'[^\d.]+', '', height_clean)
    try:
        meters = float(height_clean)
    except ValueError:
        meters = 0
    centimeters = meters * 100
    return f"{centimeters:.1f} cm"


def convert_weight(weight):
    weight_clean = re.sub(r'\(.*?\)', '', weight).strip()
    weight_clean = weight_clean.replace('Â', '').replace('\u00a0', ' ')
    return weight_clean


def remove_duplicates(items):
    seen = set()
    result = []
    for item in items:
        item_tuple = tuple(item.items())
        if item_tuple not in seen:
            seen.add(item_tuple)
            result.append(item)
    return result


df['height_cm'] = df['height_cm'].apply(convert_height)
df['weight_kg'] = df['weight_kg'].apply(convert_weight)
df['abilities'] = df['abilities'].apply(remove_duplicates)
df['number'] = pd.to_numeric(df['number'])
df = df.sort_values(by='number')

print(df)

df.to_csv('clean_pokemon.csv', index=False)
data_list = df.to_dict(orient='records')

with open('clean_pokemon.json', 'w', encoding='utf-8') as f:
    json.dump(data_list, f, ensure_ascii=False, indent=4)
