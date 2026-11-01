import os
import re

VIEWS_DIR = 'frontend/src/views'

def update_file(path, replacements):
    with open(path, 'r', encoding='utf-8') as f:
        content = f.read()
    orig = content
    for target, repl in replacements.items():
        content = content.replace(target, repl)
    if content != orig:
        with open(path, 'w', encoding='utf-8') as f:
            f.write(content)
        print(f"[+] Updated: {path}")
    else:
        print(f"[-] No changes needed: {path}")

# 1. Update SchedulingWorkspace.jsx
scheduling_replacements = {
    'bg-emerald-600/20 hover:bg-emerald-600/30 border border-emerald-500/40 text-emerald-400 font-semibold text-xs rounded transition-colors disabled:opacity-50':
        'bg-brand-accent hover:bg-brand-accent-hover border border-[#62626266]/40 text-black font-semibold text-xs rounded-[4px] transition-colors disabled:opacity-50',
    ": 'bg-emerald-500/15 border border-emerald-500/30 text-emerald-300'":
        ": 'bg-brand-accent/15 border border-brand-accent/30 text-brand-accent'",
    '<strong className="text-emerald-400 font-mono">{activeRun.scheduled_count}</strong>':
        '<strong className="text-brand-accent font-mono">{activeRun.scheduled_count}</strong>',
    '<div className="flex items-center gap-1.5 text-emerald-400 font-medium">':
        '<div className="flex items-center gap-1.5 text-brand-accent font-medium">',
    'Total Students Seated: <span className="text-emerald-400">':
        'Total Students Seated: <span className="text-brand-accent">'
}
update_file(os.path.join(VIEWS_DIR, 'SchedulingWorkspace.jsx'), scheduling_replacements)

# 2. Update AnalyticsReports.jsx
analytics_replacements = {
    "{ name: 'Lecture Halls', utilization: 88, fill: '#56D6C2' }":
        "{ name: 'Lecture Halls', utilization: 88, fill: '#B8EF43' }",
    "{ name: 'Computer Labs', utilization: 94, fill: '#57BE93' }":
        "{ name: 'Computer Labs', utilization: 94, fill: '#BEF264' }",
    "{ name: '1-3 Shifts', value: 45, fill: '#57BE93' }":
        "{ name: '1-3 Shifts', value: 45, fill: '#B8EF43' }",
    "{ name: '4-6 Shifts', value: 38, fill: '#56D6C2' }":
        "{ name: '4-6 Shifts', value: 38, fill: '#BEF264' }",
    'stroke="#9AAABA"':
        'stroke="#9CA3AF"',
    "contentStyle={{ backgroundColor: '#172330', borderColor: '#263442', color: '#E8EEF5', fontSize: '12px' }}":
        "contentStyle={{ backgroundColor: '#1C1C1C', borderColor: 'rgba(255, 255, 255, 0.20)', color: '#FFFFFF', borderRadius: '4px', fontSize: '12px' }}"
}
update_file(os.path.join(VIEWS_DIR, 'AnalyticsReports.jsx'), analytics_replacements)

# 3. Scan all views for any stray old teal/emerald
for f in os.listdir(VIEWS_DIR):
    if f.endswith('.jsx'):
        p = os.path.join(VIEWS_DIR, f)
        with open(p, 'r', encoding='utf-8') as fp:
            c = fp.read()
        
        orig = c
        c = re.sub(r'\btext-emerald-400\b', 'text-brand-accent', c)
        c = re.sub(r'\btext-emerald-300\b', 'text-brand-accent', c)
        c = re.sub(r'\btext-teal-400\b', 'text-brand-accent', c)
        c = re.sub(r'\btext-teal-300\b', 'text-brand-accent', c)
        c = re.sub(r'\bbg-emerald-500/15\b', 'bg-brand-accent/15', c)
        c = re.sub(r'\bborder-emerald-500/30\b', 'border-brand-accent/30', c)
        
        if c != orig:
            with open(p, 'w', encoding='utf-8') as fp:
                fp.write(c)
            print(f"[+] Cleaned stray tokens in: {f}")

