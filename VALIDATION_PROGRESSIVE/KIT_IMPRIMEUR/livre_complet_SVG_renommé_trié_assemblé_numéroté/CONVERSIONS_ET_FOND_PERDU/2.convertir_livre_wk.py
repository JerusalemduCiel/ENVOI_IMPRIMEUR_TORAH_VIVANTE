#!/usr/bin/env python3
"""
═══════════════════════════════════════════════════════════════════════
LUMIÈRES D'ISRAËL — LA TORAH VIVANTE
Conversion SVG → PDF via wkhtmltopdf (JUSTIFICATION PRÉSERVÉE)
═══════════════════════════════════════════════════════════════════════

PRÉREQUIS :
  1. Python 3.8+ avec pypdf (pip install pypdf)
  2. wkhtmltopdf (https://wkhtmltopdf.org/downloads.html)
     - Windows : installer le .exe et ajouter au PATH
     - Mac : brew install wkhtmltopdf
     - Linux : sudo apt install wkhtmltopdf
  3. Polices Georgia et Arial installées (natives Windows/Mac)

POURQUOI wkhtmltopdf ?
  - Utilise WebKit (moteur de Safari/Chrome) pour le rendu
  - Respecte textLength + lengthAdjust="spacing" = JUSTIFICATION
  - rsvg-convert et Inkscape ne gèrent PAS correctement textLength

USAGE :
  python convertir_livre_wk.py --svg-dir ./fiches --output livre.pdf
  python convertir_livre_wk.py --test  # 4 pages pour vérification
"""

import argparse, os, re, subprocess, sys, time, tempfile, shutil

def check_prerequisites():
    errors = []
    if not shutil.which('wkhtmltopdf'):
        errors.append("wkhtmltopdf non trouvé ! Installer depuis https://wkhtmltopdf.org/downloads.html")
    try:
        from pypdf import PdfWriter
    except ImportError:
        errors.append("pypdf non installé. Faire: pip install pypdf")
    if errors:
        for e in errors:
            print(f"❌ {e}")
        sys.exit(1)
    print("✅ Prérequis OK\n")


def svg_to_pdf_wk(svg_path, pdf_path, tmp_dir):
    """Convertit un SVG en PDF via wkhtmltopdf avec justification."""
    with open(svg_path, encoding='utf-8') as f:
        svg = f.read()

    # Ajouter width/height en mm pour dimensionnement correct dans WebKit
    svg = re.sub(r'<svg\s', '<svg width="150mm" height="210mm" ', svg, count=1)

    html = f'''<!DOCTYPE html>
<html><head><meta charset="UTF-8">
<style>
@page {{ size: 150mm 210mm; margin: 0; }}
* {{ margin: 0; padding: 0; }}
html, body {{ width: 150mm; height: 210mm; margin: 0; padding: 0; overflow: hidden; }}
svg {{ display: block; width: 150mm; height: 210mm; }}
</style>
</head><body>
{svg}
</body></html>'''

    html_path = os.path.join(tmp_dir, os.path.basename(svg_path).replace('.svg', '.html'))
    with open(html_path, 'w', encoding='utf-8') as f:
        f.write(html)

    result = subprocess.run([
        'wkhtmltopdf',
        '--page-width', '150mm', '--page-height', '210mm',
        '--margin-top', '0', '--margin-bottom', '0',
        '--margin-left', '0', '--margin-right', '0',
        '--dpi', '300', '--no-outline', '--disable-smart-shrinking',
        '--quiet', '--encoding', 'utf-8',
        html_path, pdf_path
    ], capture_output=True, text=True)

    return result.returncode == 0, result.stderr


def assemble_pdf(pdf_files, output_path):
    from pypdf import PdfWriter, PdfReader
    writer = PdfWriter()
    for p in pdf_files:
        for page in PdfReader(p).pages:
            writer.add_page(page)
    with open(output_path, 'wb') as f:
        writer.write(f)
    return len(writer.pages)


def main():
    parser = argparse.ArgumentParser()
    parser.add_argument('--svg-dir', default='./fiches')
    parser.add_argument('--inter-dir', default='./intercalaires')
    parser.add_argument('--output', default='./Lumieres_Israel.pdf')
    parser.add_argument('--test', action='store_true')
    parser.add_argument('--fiches-only', action='store_true')
    args = parser.parse_args()

    check_prerequisites()

    CHAPTERS = {
        1: list(range(1, 3)), 2: list(range(3, 11)), 3: list(range(11, 16)),
        4: list(range(16, 22)), 5: list(range(22, 30)), 6: list(range(30, 36)),
        7: list(range(36, 43)), 8: list(range(43, 54)), 9: list(range(54, 67)),
        10: list(range(67, 70)), 11: list(range(70, 75)), 12: list(range(75, 81)),
        13: list(range(81, 87)), 14: list(range(87, 91)), 15: list(range(91, 95)),
        16: list(range(95, 103)), 17: list(range(103, 107)), 18: list(range(107, 119)),
    }

    ordered = []
    for ch in range(1, 19):
        if not args.fiches_only:
            for side in ['gauche', 'droite']:
                p = os.path.join(args.inter_dir, f'intercalaire_ch{ch:02d}_{side}.svg')
                if os.path.exists(p):
                    ordered.append((p, f'Inter ch.{ch} {side}'))
        for n in CHAPTERS[ch]:
            for side in ['gauche', 'droite']:
                p = os.path.join(args.svg_dir, f'{n:03d}_{side}.svg')
                if os.path.exists(p):
                    ordered.append((p, f'Fiche {n:03d} {side}'))

    if args.test:
        ordered = ordered[:4]
        print(f"🧪 Mode test : {len(ordered)} pages\n")

    print(f"📄 {len(ordered)} SVG à convertir\n")

    timestamp = time.strftime('%Y%m%d_%H%M%S')
    work_dir = f'./conversion_wk_{timestamp}'
    tmp_dir = os.path.join(work_dir, 'html_tmp')
    pdf_dir = os.path.join(work_dir, 'pages_pdf')
    os.makedirs(tmp_dir, exist_ok=True)
    os.makedirs(pdf_dir, exist_ok=True)

    pdf_files = []
    errors = []
    start = time.time()

    for i, (svg, desc) in enumerate(ordered):
        pdf = os.path.join(pdf_dir, f'p{i+1:03d}_{os.path.basename(svg).replace(".svg", ".pdf")}')
        ok, err = svg_to_pdf_wk(svg, pdf, tmp_dir)
        if ok:
            pdf_files.append(pdf)
        else:
            errors.append(f'{desc}: {err}')
            print(f'\n  ❌ {desc}')
        pct = (i + 1) * 100 // len(ordered)
        bar = '█' * (pct // 2) + '░' * (50 - pct // 2)
        print(f'\r  [{bar}] {pct}% ({i+1}/{len(ordered)})', end='', flush=True)

    elapsed = time.time() - start
    print(f'\n\n  ✅ {len(pdf_files)} PDF en {elapsed:.1f}s')
    if errors:
        print(f'  ❌ {len(errors)} erreurs')
        for e in errors:
            print(f'    {e}')

    print(f'\n=== ASSEMBLAGE ===\n')
    n = assemble_pdf(pdf_files, args.output)
    size = os.path.getsize(args.output)
    print(f'  ✅ {n} pages → {args.output} ({size/1024/1024:.1f} Mo)')

    # Nettoyage
    shutil.rmtree(tmp_dir, ignore_errors=True)

    print(f'\n  ⚠️  OUVRIR LE PDF ET VÉRIFIER LA JUSTIFICATION !')


if __name__ == '__main__':
    main()
