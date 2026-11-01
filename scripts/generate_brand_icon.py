# ExamOps Logo Design Generator

svg_icon_sidebar = '''<svg width="24" height="24" viewBox="0 0 32 32" fill="none" xmlns="http://www.w3.org/2000/svg">
  <!-- Calendar Binder Tabs -->
  <rect x="7" y="2" width="3.5" height="5" rx="1.75" fill="#B8EF43"/>
  <rect x="21.5" y="2" width="3.5" height="5" rx="1.75" fill="#B8EF43"/>
  
  <!-- Calendar / Timetable Outer Container -->
  <rect x="3" y="4.5" width="26" height="24.5" rx="5" fill="#141414" stroke="rgba(255, 255, 255, 0.22)" stroke-width="1.2"/>
  
  <!-- Calendar Header Line -->
  <line x1="3" y1="10.5" x2="29" y2="10.5" stroke="rgba(255, 255, 255, 0.14)" stroke-width="1"/>
  
  <!-- Timeline Vertical Track Spine (The 'E' Spine) -->
  <rect x="6.5" y="13" width="2.5" height="13" rx="1.25" fill="#FFFFFF"/>
  
  <!-- Morning Exam Slot (White) -->
  <rect x="11" y="13" width="9.5" height="3" rx="1.5" fill="#FFFFFF"/>
  <circle cx="23.5" cy="14.5" r="1.5" fill="#FCF7F3" fill-opacity="0.8"/>
  
  <!-- Midday Exam Slot (Electric Lime Signature Highlight - Optimized / Active) -->
  <rect x="11" y="18" width="14" height="3" rx="1.5" fill="#B8EF43"/>
  <circle cx="22" cy="19.5" r="0.75" fill="#000000"/>
  
  <!-- Afternoon Exam Slot (White / Secondary) -->
  <rect x="11" y="23" width="10.5" height="3" rx="1.5" fill="#FFFFFF" fill-opacity="0.85"/>
  <circle cx="24.5" cy="24.5" r="1.5" fill="#FCF7F3" fill-opacity="0.8"/>
</svg>'''

svg_favicon = '''<svg width="32" height="32" viewBox="0 0 32 32" fill="none" xmlns="http://www.w3.org/2000/svg">
  <!-- Favicon Container: Dark Obsidian with subtle border for high-contrast on light & dark browser tabs -->
  <rect width="32" height="32" rx="7" fill="#08090A"/>
  
  <!-- Calendar Binder Tabs -->
  <rect x="8" y="3" width="3" height="4.5" rx="1.5" fill="#B8EF43"/>
  <rect x="21" y="3" width="3" height="4.5" rx="1.5" fill="#B8EF43"/>
  
  <!-- Timetable Frame -->
  <rect x="4" y="5.5" width="24" height="23" rx="4.5" fill="#141414" stroke="rgba(255, 255, 255, 0.25)" stroke-width="1.2"/>
  <line x1="4" y1="11" x2="28" y2="11" stroke="rgba(255, 255, 255, 0.15)" stroke-width="1"/>
  
  <!-- Timeline Spine -->
  <rect x="7" y="13.5" width="2.5" height="12" rx="1.25" fill="#FFFFFF"/>
  
  <!-- Scheduled Exam Slots forming the iconic 'E' & Timetable -->
  <rect x="11.5" y="13.5" width="8" height="2.8" rx="1.4" fill="#FFFFFF"/>
  <rect x="11.5" y="18.1" width="13" height="2.8" rx="1.4" fill="#B8EF43"/>
  <rect x="11.5" y="22.7" width="9.5" height="2.8" rx="1.4" fill="#FFFFFF"/>
</svg>'''

with open('frontend/public/favicon.svg', 'w', encoding='utf-8') as f:
    f.write(svg_favicon)

print('Generated frontend/public/favicon.svg successfully!')

