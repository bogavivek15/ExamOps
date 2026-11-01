import os
import re

FRONTEND_SRC = r'frontend/src'

hex_pattern = re.compile(r'#([0-9a-fA-F]{3,8})\b')
teal_pattern = re.compile(r'\b(teal|cyan|emerald)-[0-9]{2,3}\b')
brand_pattern = re.compile(r'brand-[a-zA-Z0-9-]+')

found_hexes = {}
found_teals = {}
found_brand_classes = {}

for root, dirs, files in os.walk(FRONTEND_SRC):
    for f in files:
        if f.endswith(('.jsx', '.js', '.css', '.html')):
            p = os.path.join(root, f)
            with open(p, 'r', encoding='utf-8', errors='ignore') as fp:
                content = fp.read()
                
                # Check hexes
                hexes = hex_pattern.findall(content)
                for h in hexes:
                    full = '#' + h.upper()
                    found_hexes[full] = found_hexes.get(full, 0) + 1
                    
                # Check teals
                teals = teal_pattern.findall(content)
                for t in teals:
                    found_teals[t] = found_teals.get(t, 0) + 1
                    
                # Check brand tokens
                brands = brand_pattern.findall(content)
                for b in brands:
                    found_brand_classes[b] = found_brand_classes.get(b, 0) + 1

print("=== FOUND HEX CODES IN FRONTEND/SRC ===")
for h, cnt in sorted(found_hexes.items(), key=lambda x: x[1], reverse=True):
    print(f"  {h:10}: {cnt:3} occurrences")

print("\n=== FOUND TEAL/CYAN/EMERALD CLASSES ===")
for t, cnt in sorted(found_teals.items(), key=lambda x: x[1], reverse=True):
    print(f"  {t:15}: {cnt:3} occurrences")

print("\n=== FOUND BRAND CLASSES ===")
for b, cnt in sorted(found_brand_classes.items(), key=lambda x: x[1], reverse=True):
    print(f"  {b:25}: {cnt:3} occurrences")

