#!/usr/bin/env python
# Script to add section IDs and fix deprecation warnings
import re

with open('app.py', 'r', encoding='utf-8') as f:
    content = f.read()

# Replace deprecated use_container_width
content = content.replace('use_container_width=True', "width='stretch'")

print("Fixed deprecation warnings")

# Add section IDs before headers that don't have them yet
section_mapping = [
    ('Calendar Heatmap', 'calendar'),
    ('Performance Globale', 'performance'),
    ('LONG vs SHORT', 'direction'),
    ('Analyse Temporelle', 'temporal'),
    ('Classement des Actifs', 'assets'),
    ('Gestion du Risque', 'risk'),
    ('Trade Types', 'tradetypes'),
    ('Trade DNA', 'dna'),
    ('Clusters Comportementaux', 'clusters'),
    ('Patterns Comportementaux', 'behavior'),
    ('Temps en Position', 'duration'),
    ('Trades Probématiques', 'problems'),
    ('Analyse Avancée', 'montecarlo'),
]

for section_name, anchor_id in section_mapping:
    # Check if anchor already exists
    if f'id="{anchor_id}"' in content:
        print(f"  Anchor {anchor_id} already exists")
        continue
    
    # Find the header line
    pattern = rf"(st\.header\(['\"].*?{re.escape(section_name)}.*?['\"]\))"
    match = re.search(pattern, content)
    if match:
        header_line = match.group(1)
        anchor_div = f'st.markdown(\'<div id="{anchor_id}"></div>\', unsafe_allow_html=True)\n'
        content = content.replace(header_line, anchor_div + header_line, 1)
        print(f"  Added anchor {anchor_id}")
    else:
        print(f"  Header for {section_name} not found")

with open('app.py', 'w', encoding='utf-8') as f:
    f.write(content)

print("Done!")
