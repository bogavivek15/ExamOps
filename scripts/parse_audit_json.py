import json
import sys
import re

sys.stdout.reconfigure(encoding='utf-8')

with open('docs/design/outskill_extracted_styles.json', 'r', encoding='utf-8') as f:
    data = json.load(f)

def rgb_to_hex(rgb_str):
    m = re.match(r'rgba?\((\d+),\s*(\d+),\s*(\d+)(?:,\s*([\d\.]+))?\)', rgb_str)
    if m:
        r, g, b = int(m.group(1)), int(m.group(2)), int(m.group(3))
        a = float(m.group(4)) if m.group(4) is not None else 1.0
        hex_val = f"#{r:02X}{g:02X}{b:02X}"
        if a < 0.999:
            hex_val += f" ({a*100:.0f}%)"
        return hex_val
    return rgb_str

print("=========================================")
print("OUTSKILL COMPREHENSIVE COLOR EXTRACTION")
print("=========================================\n")

for page_key in ['home', 'fellowship']:
    page = data['pages'][page_key]
    print(f"\n--- PAGE: {page_key.upper()} ({page.get('url')}) ---")
    print(f"Title: {page.get('title')}")
    
    print("\n[CSS VARIABLES]")
    for k, v in page.get('cssVariables', {}).items():
        print(f"  {k}: {v}")
        
    print("\n[TOP COMPUTED COLORS]")
    color_usage = page.get('colorUsage', {})
    for c, uses in sorted(color_usage.items(), key=lambda x: len(x[1]), reverse=True)[:35]:
        roles = sorted(list(set(u['role'] for u in uses)))
        samples = [u['elInfo'] for u in uses[:2]]
        hex_repr = rgb_to_hex(c)
        print(f"  {c:32} | {hex_repr:15} | Uses: {len(uses):3} | Roles: {roles}")
        for s in samples:
            print(f"      sample: {s[:75]}")

    print("\n[BUTTONS]")
    for el in page.get('elements', []):
        if el['type'] == 'button':
            bg_hex = rgb_to_hex(el['backgroundColor'])
            c_hex = rgb_to_hex(el['color'])
            b_hex = rgb_to_hex(el['borderColor'])
            print(f"  Button: '{el['text']}'")
            print(f"    bg: {el['backgroundColor']} ({bg_hex}) | text: {el['color']} ({c_hex}) | border: {el['borderColor']} ({b_hex})")
            print(f"    radius: {el['borderRadius']} | shadow: {el['boxShadow']} | font: {el['fontFamily']} weight: {el['fontWeight']}")
            print(f"    sel: {el['selector'][:80]}")

    print("\n[CARDS & SECTIONS]")
    for el in page.get('elements', []):
        if el['type'] in ['card', 'badge', 'nav', 'footer', 'body']:
            bg_hex = rgb_to_hex(el['backgroundColor'])
            c_hex = rgb_to_hex(el['color'])
            b_hex = rgb_to_hex(el['borderColor'])
            print(f"  [{el['type'].upper()}] text: '{el['text'][:30]}'")
            print(f"    bg: {el['backgroundColor']} ({bg_hex}) | text: {el['color']} ({c_hex}) | border: {b_hex} | radius: {el['borderRadius']}")
            print(f"    sel: {el['selector'][:80]}")

    print("\n[GRADIENTS]")
    for g in page.get('gradients', []):
        print(f"  sel: {g['selector'][:60]}")
        print(f"  val: {g['gradient']}")

    print("\n[SVGS]")
    for s in page.get('svgs', []):
        print(f"  SVG sel: {s['selector'][:60]} | fill: {s['fill']} | stroke: {s['stroke']} | color: {s['color']}")
