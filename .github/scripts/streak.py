import os, json, urllib.request
from datetime import date, timedelta

LOGIN = os.environ["GH_LOGIN"]
TOKEN = os.environ["GH_TOKEN"]

query = """query($login:String!){user(login:$login){contributionsCollection{
contributionCalendar{totalContributions weeks{contributionDays{date contributionCount}}}}}}"""

req = urllib.request.Request(
    "https://api.github.com/graphql",
    data=json.dumps({"query": query, "variables": {"login": LOGIN}}).encode(),
    headers={"Authorization": f"bearer {TOKEN}", "Content-Type": "application/json"},
)
cal = json.load(urllib.request.urlopen(req))["data"]["user"]["contributionsCollection"]["contributionCalendar"]

days = {d["date"]: d["contributionCount"]
        for w in cal["weeks"] for d in w["contributionDays"]}
total = cal["totalContributions"]

# current streak: today may still be empty, so start from yesterday in that case
today = date.today()
cur_end = today if days.get(today.isoformat(), 0) > 0 else today - timedelta(days=1)
cur, d = 0, cur_end
while days.get(d.isoformat(), 0) > 0:
    cur += 1
    d -= timedelta(days=1)
cur_start = d + timedelta(days=1)

# longest streak within the returned year
longest = run = 0
for k in sorted(days):
    run = run + 1 if days[k] > 0 else 0
    longest = max(longest, run)

rng = f"{cur_start:%b %d} - {cur_end:%b %d}" if cur else "No active streak"

svg = f'''<svg xmlns="http://www.w3.org/2000/svg" width="495" height="195" viewBox="0 0 495 195">
<rect width="495" height="195" rx="4.5" fill="#151515"/>
<g font-family="Segoe UI, Ubuntu, sans-serif" text-anchor="middle">
  <text x="82" y="85" font-size="28" font-weight="700" fill="#fff">{total}</text>
  <text x="82" y="115" font-size="14" fill="#FB8C00">Total Contributions</text>
  <circle cx="247" cy="80" r="40" fill="none" stroke="#FB8C00" stroke-width="5"/>
  <text x="247" y="90" font-size="28" font-weight="700" fill="#fff">{cur}</text>
  <text x="247" y="148" font-size="14" font-weight="700" fill="#FB8C00">Current Streak</text>
  <text x="247" y="170" font-size="12" fill="#9e9e9e">{rng}</text>
  <text x="412" y="85" font-size="28" font-weight="700" fill="#fff">{longest}</text>
  <text x="412" y="115" font-size="14" fill="#FB8C00">Longest Streak</text>
</g></svg>'''

os.makedirs("profile", exist_ok=True)
open("profile/streak.svg", "w").write(svg)
