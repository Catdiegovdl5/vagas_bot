import os
import datetime

files = [
    "bot.py",
    "scrapers/workana.py",
    "database.py",
    "tests/test_workana_settings.py"
]

print("--- FILE MODIFICATION TIMES ---")
for f in files:
    if os.path.exists(f):
        mtime = os.path.getmtime(f)
        dt = datetime.datetime.fromtimestamp(mtime, tz=datetime.timezone.utc)
        print(f"{f}: {dt.isoformat()}")
    else:
        print(f"{f}: DOES NOT EXIST")
