import sys
sys.stdout.reconfigure(encoding='utf-8')
from bs4 import BeautifulSoup
import re
from collections import Counter

# 1. Analyze Coodesh HTML
print("=== ANALYZING COODESH ===")
with open('.agents/teamwork_preview_explorer_scrapers_1/coodesh_test.html', 'r', encoding='utf-8') as f:
    html = f.read()

soup = BeautifulSoup(html, 'html.parser')
print("Total divs:", len(soup.find_all('div')))
print("Total links:", len(soup.find_all('a')))

# Check if __NEXT_DATA__ is in Coodesh HTML
if '__NEXT_DATA__' in html:
    print("Found __NEXT_DATA__ in Coodesh!")
    script = soup.find('script', id='__NEXT_DATA__')
    if script and script.string:
        print("Script length:", len(script.string))
        # Let's print first 300 characters of __NEXT_DATA__
        print("Snippet:", script.string[:300])
else:
    print("__NEXT_DATA__ NOT found in Coodesh")

# Find any links containing 'vagas/' or similar in href
links = soup.find_all('a', href=True)
job_links = [l['href'] for l in links if '/vaga/' in l['href'] or '/vagas/' in l['href'] or 'vagas-de-' in l['href']]
print("Job links found in raw HTML:", len(job_links))
if job_links:
    print("Job link samples:", job_links[:5])

# List common classes of links
link_classes = []
for a in soup.find_all('a', class_=True):
    link_classes.extend(a.get('class'))
print("Common link classes in Coodesh:", Counter(link_classes).most_common(10))


# 2. Analyze Geekhunter HTML
print("\n=== ANALYZING GEEKHUNTER ===")
with open('.agents/teamwork_preview_explorer_scrapers_1/geek_test.html', 'r', encoding='utf-8') as f:
    html_geek = f.read()

soup_geek = BeautifulSoup(html_geek, 'html.parser')
print("Total divs:", len(soup_geek.find_all('div')))
print("Total links:", len(soup_geek.find_all('a')))

# Check if __NEXT_DATA__ is in Geekhunter HTML
if '__NEXT_DATA__' in html_geek:
    print("Found __NEXT_DATA__ in Geekhunter!")
    script = soup_geek.find('script', id='__NEXT_DATA__')
    if script and script.string:
        print("Script length:", len(script.string))
        print("Snippet:", script.string[:300])
else:
    print("__NEXT_DATA__ NOT found in Geekhunter")

# Check if they have window.__INITIAL_STATE__ or similar
initial_state = re.findall(r'window\.__[A-Z_]+__\s*=\s*(.*?);', html_geek)
if initial_state:
    print("Found initial state variables:", len(initial_state))
    for i, state in enumerate(initial_state):
        print(f"State #{i} snippet: {state[:200]}")

# Find any links containing 'vagas/' or similar in href
links_geek = soup_geek.find_all('a', href=True)
job_links_geek = [l['href'] for l in links_geek if '/vaga/' in l['href'] or '/vagas/' in l['href'] or 'vaga-' in l['href']]
print("Job links found in raw HTML (Geekhunter):", len(job_links_geek))
if job_links_geek:
    print("Job link samples (Geekhunter):", job_links_geek[:5])

# List common classes of divs
div_classes = []
for div in soup_geek.find_all('div', class_=True):
    div_classes.extend(div.get('class'))
print("Common div classes in Geekhunter:", Counter(div_classes).most_common(15))
