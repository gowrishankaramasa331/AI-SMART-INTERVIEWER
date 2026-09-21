import re
import glob

with open('templates/index.html', 'r', encoding='utf-8') as f:
    html = f.read()

html_ids = set(re.findall(r'id=["\']([a-zA-Z0-9_-]+)["\']', html))
print(f"Found {len(html_ids)} unique IDs in templates/index.html")

missing = {}
for js in sorted(glob.glob('static/js/*.js')):
    if 'three.min.js' in js:
        continue
    with open(js, 'r', encoding='utf-8') as f:
        js_code = f.read()
    js_ids = re.findall(r'getElementById\(["\']([a-zA-Z0-9_-]+)["\']\)', js_code)
    for jid in js_ids:
        if jid not in html_ids:
            missing.setdefault(js, set()).add(jid)

for file, ids in missing.items():
    print(f"{file} references missing IDs: {ids}")

if not missing:
    print("All getElementById references exist in HTML!")
