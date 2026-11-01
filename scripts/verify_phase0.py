import sys
import re

sys.stdout.reconfigure(encoding='utf-8')

# Read data_dictionary.md
with open('docs/data_dictionary.md', encoding='utf-8') as f:
    dd_content = f.read()

dd_headers = re.findall(r'### \d+\.\d+\s+([^\n]+)', dd_content)
dd_tables = []
for h in dd_headers:
    # Look for `table_name`
    m = re.search(r'`([a-z0-9_]+)`', h)
    if m:
        dd_tables.append(m.group(1))

# Read permissions.md
with open('docs/permissions.md', encoding='utf-8') as f:
    perm_content = f.read()

perm_section = perm_content.split('## 2. Comprehensive Entity CRUD Permissions Matrix')[1].split('## 3. Operational Action Permissions Matrix')[0]
perm_tables = []
for line in perm_section.splitlines():
    if line.startswith('| `'):
        t = line.split('|')[1].strip(' `')
        perm_tables.append(t)

# Read erd.md
with open('docs/erd.md', encoding='utf-8') as f:
    erd_content = f.read()

erd_blocks = re.findall(r'    ([A-Za-z0-9]+)\s*\{', erd_content)

print(f"Data Dictionary tables ({len(dd_tables)}):")
print(" ", sorted(dd_tables))
print(f"\nPermissions tables ({len(perm_tables)}):")
print(" ", sorted(perm_tables))
print(f"\nERD Entity Blocks ({len(erd_blocks)}):")
print(" ", sorted(erd_blocks))

assert len(dd_tables) == 26, f"Expected 26 tables in data_dictionary, got {len(dd_tables)}"
assert len(perm_tables) == 26, f"Expected 26 tables in permissions, got {len(perm_tables)}"
assert len(erd_blocks) == 26, f"Expected 26 entity blocks in ERD, got {len(erd_blocks)}"
assert set(dd_tables) == set(perm_tables), f"Mismatch between data dictionary and permissions: {set(dd_tables) ^ set(perm_tables)}"

print("\nSUCCESS: All 26 entities are identical and fully reconciled across ERD, Data Dictionary, and Permissions Matrix!")

