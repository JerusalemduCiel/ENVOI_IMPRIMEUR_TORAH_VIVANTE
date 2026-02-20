#!/usr/bin/env python3
"""
═══════════════════════════════════════════════════════════════════════
LUMIÈRES D'ISRAËL — LA TORAH VIVANTE
Intégration des portraits dans les fiches SVG (pages gauches)
═══════════════════════════════════════════════════════════════════════

USAGE :
  python integrer_images.py --svg-dir ./fiches --img-dir ./portraits --output-dir ./fiches_illustrees
  python integrer_images.py --test  # traite seulement les 3 premières fiches

STRUCTURE ATTENDUE DES IMAGES :
  ./portraits/001.jpg (ou .png)  → Adam HaRishon
  ./portraits/002.jpg            → 'Hava
  ...
  ./portraits/118.jpg            → Rabbi Jonathan Sacks

SPÉCIFICATIONS :
  - Position image : x=155, y=48
  - Dimensions : 115×115 pixels (dans le viewBox 425×595)
  - Recadrage : preserveAspectRatio="xMidYMid slice"
  - Coins arrondis : clip-path="inset(0 round 4px)"
  - Format : base64 embarqué dans le SVG
"""

import argparse, base64, os, re, sys, glob
from pathlib import Path

def find_image(img_dir, num):
    """Cherche l'image pour la fiche numéro num."""
    for ext in ['jpg', 'jpeg', 'png', 'webp']:
        for pattern in [f'{num:03d}.{ext}', f'{num:03d}_*.{ext}', f'{num}.{ext}']:
            matches = glob.glob(os.path.join(img_dir, pattern))
            if matches:
                return matches[0]
    return None

def image_to_base64(img_path):
    """Convertit une image en data URI base64."""
    ext = os.path.splitext(img_path)[1].lower()
    mime = {'jpg': 'image/jpeg', 'jpeg': 'image/jpeg', 'png': 'image/png', 'webp': 'image/webp'}
    mime_type = mime.get(ext.lstrip('.'), 'image/jpeg')
    
    with open(img_path, 'rb') as f:
        data = base64.b64encode(f.read()).decode('ascii')
    
    return f'data:{mime_type};base64,{data}'

def inject_image(svg_path, img_data_uri, output_path):
    """Injecte l'image dans le SVG de la fiche gauche."""
    with open(svg_path, encoding='utf-8') as f:
        svg = f.read()
    
    # Vérifier si une image est déjà présente
    if '<image ' in svg:
        # Remplacer l'image existante
        svg = re.sub(
            r'<image [^>]*/>',
            f'<image x="155" y="48" width="115" height="115" '
            f'preserveAspectRatio="xMidYMid slice" '
            f'clip-path="inset(0 round 4px)" '
            f'href="{img_data_uri}"/>',
            svg
        )
    else:
        # Insérer avant le premier <text> après le bandeau supérieur
        # Chercher le point d'insertion (après le bandeau haut, avant le nom hébreu)
        insert_point = svg.find('</g>') + len('</g>')
        if insert_point < 10:
            # Fallback : insérer avant le premier <text>
            insert_point = svg.find('<text')
        
        image_tag = (
            f'\n  <image x="155" y="48" width="115" height="115" '
            f'preserveAspectRatio="xMidYMid slice" '
            f'clip-path="inset(0 round 4px)" '
            f'href="{img_data_uri}"/>\n'
        )
        svg = svg[:insert_point] + image_tag + svg[insert_point:]
    
    with open(output_path, 'w', encoding='utf-8') as f:
        f.write(svg)
    
    return True

def main():
    parser = argparse.ArgumentParser()
    parser.add_argument('--svg-dir', default='./fiches', help='Dossier des SVG')
    parser.add_argument('--img-dir', default='./portraits', help='Dossier des images')
    parser.add_argument('--output-dir', default=None, help='Dossier de sortie (défaut: modifie en place)')
    parser.add_argument('--test', action='store_true', help='Traiter seulement 3 fiches')
    args = parser.parse_args()
    
    if args.output_dir:
        os.makedirs(args.output_dir, exist_ok=True)
    
    success = 0
    missing = 0
    errors = 0
    
    fiches = range(1, 4) if args.test else range(1, 119)
    
    for n in fiches:
        svg_path = os.path.join(args.svg_dir, f'{n:03d}_gauche.svg')
        if not os.path.exists(svg_path):
            continue
        
        img_path = find_image(args.img_dir, n)
        if not img_path:
            missing += 1
            print(f'  ⚠️  {n:03d} : pas d\'image trouvée')
            continue
        
        output_path = os.path.join(args.output_dir or args.svg_dir, f'{n:03d}_gauche.svg')
        
        try:
            data_uri = image_to_base64(img_path)
            inject_image(svg_path, data_uri, output_path)
            size_kb = os.path.getsize(img_path) / 1024
            success += 1
            print(f'  ✅ {n:03d} : {os.path.basename(img_path)} ({size_kb:.0f} Ko)')
        except Exception as e:
            errors += 1
            print(f'  ❌ {n:03d} : {e}')
    
    print(f'\n═══ RÉSULTAT ═══')
    print(f'  ✅ {success} images intégrées')
    print(f'  ⚠️  {missing} images manquantes')
    print(f'  ❌ {errors} erreurs')

if __name__ == '__main__':
    main()
