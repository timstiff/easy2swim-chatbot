from flask import Flask, jsonify
import requests
from bs4 import BeautifulSoup
from datetime import datetime, timedelta
import re

@app.route("/schedule", methods=["GET"])
def get_schedule():
    urls = {
        "2-4": "https://easy2swim.co.za/age-groups-classes/age-group-2-4-years/2-4-years-age-group-class-registration/",
        "5-7": "https://easy2swim.co.za/age-groups-classes/age-group-5-7-years/5-7-years-age-group-class-registration/",
        "8plus": "https://easy2swim.co.za/age-groups-classes/age-group-8-years/8-years-age-group-class-registration/"
    }

    def to_24h_format(time_str):
        dt = datetime.strptime(time_str.strip(), "%I:%M %p")
        return dt.strftime("%Hh%M")

    def get_abbr_day(day):
        days = {
            "Monday": "Mon", "Tuesday": "Tues", "Wednesday": "Wed",
            "Thursday": "Thurs", "Friday": "Fri", "Saturday": "Sat", "Sunday": "Sun"
        }
        return days.get(day, day[:3])

    results = {}

    for label, url in urls.items():
        try:
            page = requests.get(url)
            soup = BeautifulSoup(page.text, "html.parser")
            schedule = []

            # Extract term start and end dates
            term_info = soup.find(string=re.compile(r"Term Dates|Start Date"))
            date_text = term_info.find_parent().get_text() if term_info else ""
            dates = re.findall(r"(\d{1,2} \w+ \d{4})", date_text)

            if len(dates) >= 2:
                start_date = datetime.strptime(dates[0], "%d %B %Y")
                end_date = datetime.strptime(dates[1], "%d %B %Y")
            else:
                start_date = datetime.today()
                end_date = start_date + timedelta(weeks=10)

            today = datetime.today()
            weeks_left = max(0, ((end_date - today).days // 7) + 1)

            # Find total price from page (you can refine this if needed)
            price_match = re.search(r"R(\d{3,5})", page.text)
            total_price = int(price_match.group(1)) if price_match else 1650
            price_per_class = total_price / ((end_date - start_date).days // 7 + 1)
            pro_rata_price = int(round(price_per_class * weeks_left / 5.0) * 5)  # round to nearest 5

            rows = soup.select("table tr")
            for row in rows:
                cols = row.find_all("td")
                if len(cols) < 5:
                    continue

                day_time = cols[0].get_text(strip=True)
                size_text = cols[2].get_text(strip=True)

                if "/" not in size_text:
                    continue
                current, total = map(int, size_text.split("/"))
                if current >= total:
                    continue  # class full

                # Extract time and format it
                if "–" in day_time:
                    day_part, time_part = day_time.split(" ", 1)
                    start_time = time_part.split("–")[0].strip()
                else:
                    day_part, start_time = day_time.split(" ", 1)

                time_24 = to_24h_format(start_time)
                day_abbr = get_abbr_day(day_part)

                register_btn = cols[-1].find("a", href=True)
                if register_btn:
                    link = register_btn["href"]
                    label = f"[{day_abbr} {time_24}]({link}) • {weeks_left} Classes • R{pro_rata_price}"
                    schedule.append({"label": label})

            results[label] = schedule
        except Exception as e:
            results[label] = {"error": str(e)}

    return jsonify(results)
