import json
from datetime import datetime
from pathlib import Path

import matplotlib.pyplot as plt

script_dir = Path(__file__).resolve().parent

with open(script_dir / "eva-data.json", "r", encoding="utf-8") as file:
    eva_data = json.load(file)

records = []
country_totals = {}
longest_eva = None
category_counts = {"short": 0, "standard": 0, "long": 0}
missing_duration_count = 0

for eva in eva_data:
    date_text = eva.get("date")
    duration_text = eva.get("duration")
    
    if not duration_text:
        missing_duration_count += 1
        continue

    hours, minutes = map(int, duration_text.split(":"))
    duration_hours = hours + minutes/60
    if duration_hours < 4:
        category = "short"
    elif duration_hours < 7:
        category = "standard"
    else:
        category = "long"
    category_counts[category] += 1

    country = eva.get("country")
    if country:
        country_totals[country] = country_totals.get(country, 0) + duration_hours

    if longest_eva is None or duration_hours > longest_eva[2]:
        longest_eva = (date_text, country, duration_hours)

    if not date_text:
        continue

    date = datetime.fromisoformat(date_text)
    records.append((date, duration_hours))

selected_country = input("Enter a country: ").strip()
matching_country = next(
    (country for country in country_totals
     if country.casefold() == selected_country.casefold()),
    None,
)

if matching_country:
    print(
        f"Total EVA duration for {matching_country}: "
        f"{country_totals[matching_country]:.2f} hours"
    )
else:
    print(f"No EVA duration data found for {selected_country}.")

if longest_eva:
    longest_date, longest_country, longest_duration = longest_eva
    display_date = longest_date.split("T")[0] if longest_date else "unknown"
    print(
        f"Longest EVA: {display_date}, {longest_country}, "
        f"{longest_duration:.2f} hours"
    )

classified_count = sum(category_counts.values())
print(f"EVA duration categories ({classified_count} EVAs with recorded durations):")
for category, count in category_counts.items():
    percentage = count / classified_count * 100 if classified_count else 0
    print(f"{category.capitalize()}: {count} ({percentage:.2f}%)")
if missing_duration_count:
    print(f"EVAs without a recorded duration: {missing_duration_count} (excluded).")

records.sort(key=lambda record: record[0])

dates = []
cumulative_hours = []
total_hours = 0

for date, duration_hours in records:
        total_hours += duration_hours
        dates.append(date)
        cumulative_hours.append(total_hours)

plt.plot(dates, cumulative_hours)
plt.xlabel("Year")
plt.ylabel("Cumulative EVA duration(hours)")
plt.tight_layout()
plt.savefig(script_dir / "cumulative_duration.png")
plt.show()
