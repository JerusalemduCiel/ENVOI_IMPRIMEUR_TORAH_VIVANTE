#!/usr/bin/env python3
"""
═══════════════════════════════════════════════════════════════════════
LUMIÈRES D'ISRAËL — LA TORAH VIVANTE
Ajout du fond perdu 5mm sur tous les SVG et HTML
═══════════════════════════════════════════════════════════════════════

Transforme les fichiers de 150×210mm (425×595) en ~160×220mm (453.3×623.3)
avec le fond ivoire #F5EEE1 étendu sur les 5mm de chaque côté.

Pour les HTML : met à jour les dimensions CSS ET le overflow du conteneur .page

USAGE :
  python 1_ajouter_fond_perdu.py --svg-dir . --output-dir ./AVEC_FOND_PERDU
"""

import argparse, os, re

BLEED_PX = 14.17
OLD_W, OLD_H = 425, 595
NEW_W = OLD_W + 2 * BLEED_PX  # 453.34
NEW_H = OLD_H + 2 * BLEED_PX  # 623.34

def add_bleed(filepath, output_path):
    with open(filepath, encoding='utf-8') as f:
        content = f.read()
    
    # 1. SVG : modifier viewBox et dimensions
    content = re.sub(
        r'width="425"\s+height="595"\s+viewBox="0 0 425 595"',
        f'width="{NEW_W:.1f}" height="{NEW_H:.1f}" viewBox="{-BLEED_PX:.2f} {-BLEED_PX:.2f} {NEW_W:.1f} {NEW_H:.1f}"',
        content
    )
    
    # 2. SVG : étendre le rect de fond au bleed
    content = content.replace(
        '<rect width="425" height="595" fill="#F5EEE1"/>',
        f'<rect x="{-BLEED_PX:.2f}" y="{-BLEED_PX:.2f}" width="{NEW_W:.1f}" height="{NEW_H:.1f}" fill="#F5EEE1"/>'
    )
    
    # 3. HTML : mettre à jour le CSS .page (width, height, overflow)
    content = re.sub(
        r'\.page\{width:425px;height:595px;',
        f'.page{{width:{NEW_W:.1f}px;height:{NEW_H:.1f}px;',
        content
    )
    content = content.replace('overflow:hidden', 'overflow:visible')
    
    with open(output_path, 'w', encoding='utf-8') as f:
        f.write(content)

def main():
    parser = argparse.ArgumentParser()
    parser.add_argument('--svg-dir', default='.')
    parser.add_argument('--output-dir', default='./AVEC_FOND_PERDU')
    args = parser.parse_args()
    
    os.makedirs(args.output_dir, exist_ok=True)
    
    count_svg = 0
    count_html = 0
    
    for f in sorted(os.listdir(args.svg_dir)):
        if f.endswith('.svg') or f.endswith('.html'):
            add_bleed(
                os.path.join(args.svg_dir, f),
                os.path.join(args.output_dir, f)
            )
            if f.endswith('.svg'):
                count_svg += 1
            else:
                count_html += 1
    
    print(f'✅ {count_svg} SVG + {count_html} HTML avec fond perdu 5mm → {args.output_dir}')
    print(f'   Dimensions : {OLD_W}×{OLD_H} → {NEW_W:.1f}×{NEW_H:.1f} px')

if __name__ == '__main__':
    main()
