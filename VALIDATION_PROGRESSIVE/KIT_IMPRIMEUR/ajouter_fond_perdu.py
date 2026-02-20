#!/usr/bin/env python3
"""
═══════════════════════════════════════════════════════════════════════
LUMIÈRES D'ISRAËL — LA TORAH VIVANTE
Ajout du fond perdu 5mm sur tous les SVG
═══════════════════════════════════════════════════════════════════════

Transforme les SVG de 150×210mm (425×595) en 160×220mm (453.5×623.6)
avec le fond ivoire #F5EEE1 étendu sur les 5mm de chaque côté.

USAGE :
  python ajouter_fond_perdu.py --svg-dir ./fiches --output-dir ./fiches_bleed
"""

import argparse, os, re

# 5mm de fond perdu en unités SVG (à 72dpi : 5mm = 14.17pt)
BLEED_PX = 14.17
OLD_W, OLD_H = 425, 595
NEW_W = OLD_W + 2 * BLEED_PX  # 453.34
NEW_H = OLD_H + 2 * BLEED_PX  # 623.34

def add_bleed(svg_path, output_path):
    with open(svg_path, encoding='utf-8') as f:
        svg = f.read()
    
    # 1. Modifier le viewBox et les dimensions
    svg = re.sub(
        r'width="425" height="595" viewBox="0 0 425 595"',
        f'width="{NEW_W:.1f}" height="{NEW_H:.1f}" viewBox="{-BLEED_PX:.2f} {-BLEED_PX:.2f} {NEW_W:.1f} {NEW_H:.1f}"',
        svg
    )
    
    # 2. Le rect de fond existant (<rect width="425" height="595" fill="#F5EEE1"/>)
    # couvre maintenant de (0,0) à (425,595). Il faut l'étendre au bleed.
    svg = svg.replace(
        '<rect width="425" height="595" fill="#F5EEE1"/>',
        f'<rect x="{-BLEED_PX:.2f}" y="{-BLEED_PX:.2f}" width="{NEW_W:.1f}" height="{NEW_H:.1f}" fill="#F5EEE1"/>'
    )
    
    with open(output_path, 'w', encoding='utf-8') as f:
        f.write(svg)
    
    return True

def main():
    parser = argparse.ArgumentParser()
    parser.add_argument('--svg-dir', default='./fiches')
    parser.add_argument('--output-dir', default='./fiches_bleed')
    parser.add_argument('--inter-dir', default=None, help='Dossier intercalaires (optionnel)')
    args = parser.parse_args()
    
    os.makedirs(args.output_dir, exist_ok=True)
    
    count = 0
    for f in sorted(os.listdir(args.svg_dir)):
        if f.endswith('.svg'):
            add_bleed(
                os.path.join(args.svg_dir, f),
                os.path.join(args.output_dir, f)
            )
            count += 1
    
    # Intercalaires si spécifié
    if args.inter_dir and os.path.exists(args.inter_dir):
        for f in sorted(os.listdir(args.inter_dir)):
            if f.endswith('.svg'):
                add_bleed(
                    os.path.join(args.inter_dir, f),
                    os.path.join(args.output_dir, f)
                )
                count += 1
    
    print(f'✅ {count} SVG avec fond perdu 5mm → {args.output_dir}')

if __name__ == '__main__':
    main()
