#!/usr/bin/env python3
"""
═══════════════════════════════════════════════════════════════════════
LUMIÈRES D'ISRAËL — LA TORAH VIVANTE
Conversion SVG/HTML → PDF via wkhtmltopdf
═══════════════════════════════════════════════════════════════════════

v4 — Fix images manquantes :
  - Extrait les images base64 en fichiers temporaires
    (le vieux WebKit de wkhtmltopdf plante sur les grosses data URI)
  - href → xlink:href pour compatibilité WebKit
  - Injection @page CSS 160×220mm

USAGE :
  python 2_convertir_livre_wk_v4.py --input-dir ./AVEC_FOND_PERDU --output livre.pdf
  python 2_convertir_livre_wk_v4.py --input-dir ./AVEC_FOND_PERDU --test 15
"""

import argparse, base64, os, re, subprocess, sys, time, shutil, tempfile

PAGE_W_MM = 160
PAGE_H_MM = 220


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


def extract_base64_images(content, temp_dir):
    """
    Extrait toutes les images base64 en fichiers temporaires.
    Retourne le contenu modifié avec des chemins file:// locaux.
    
    C'est LE fix principal : le vieux WebKit de wkhtmltopdf ne gère
    pas bien les grosses data URI base64 intégrées dans les SVG.
    En les extrayant en fichiers locaux, tout passe correctement.
    """
    img_count = [0]

    def replace_data_uri(match):
        prefix = match.group(1)
        mime = match.group(2)
        b64data = match.group(3)
        img_count[0] += 1

        ext = 'png'
        if 'jpeg' in mime or 'jpg' in mime:
            ext = 'jpg'
        elif 'gif' in mime:
            ext = 'gif'

        img_path = os.path.join(temp_dir, f'img_{img_count[0]:03d}.{ext}')
        try:
            with open(img_path, 'wb') as f:
                f.write(base64.b64decode(b64data))
            abs_path = os.path.abspath(img_path).replace('\\', '/')
            if not abs_path.startswith('/'):
                abs_path = '/' + abs_path
            return f'{prefix}xlink:href="file://{abs_path}"'
        except Exception:
            return match.group(0)

    pattern = r'(<image\s[^>]*?)(?:xlink:)?href="data:(image/[^;]+);base64,([^"]*)"'
    result = re.sub(pattern, replace_data_uri, content)
    return result, img_count[0]


def fix_image_href(content):
    """Ajoute xmlns:xlink et convertit href → xlink:href pour <image>."""
    if 'xmlns:xlink' not in content:
        content = content.replace(
            'xmlns="http://www.w3.org/2000/svg"',
            'xmlns="http://www.w3.org/2000/svg" xmlns:xlink="http://www.w3.org/1999/xlink"'
        )
    content = re.sub(
        r'(<image\s[^>]*?)(?<!\bxlink:)\bhref=',
        r'\1xlink:href=',
        content
    )
    return content


def run_wkhtmltopdf(html_path, pdf_path):
    result = subprocess.run([
        'wkhtmltopdf',
        '--enable-local-file-access',
        '--page-width', f'{PAGE_W_MM}mm',
        '--page-height', f'{PAGE_H_MM}mm',
        '--margin-top', '0',
        '--margin-bottom', '0',
        '--margin-left', '0',
        '--margin-right', '0',
        '--dpi', '300',
        '--no-outline',
        '--disable-smart-shrinking',
        '--quiet',
        '--encoding', 'utf-8',
        html_path, pdf_path
    ], capture_output=True, text=True)
    return result.returncode == 0, result.stderr


def convert_svg(svg_path, pdf_path):
    """Convertit un SVG en PDF avec extraction des images base64."""
    with open(svg_path, encoding='utf-8') as f:
        svg = f.read()

    temp_dir = tempfile.mkdtemp(prefix='svg_conv_')

    try:
        svg = fix_image_href(svg)
        svg, _ = extract_base64_images(svg, temp_dir)

        svg = re.sub(
            r'<svg\s+xmlns',
            f'<svg width="{PAGE_W_MM}mm" height="{PAGE_H_MM}mm" xmlns',
            svg, count=1
        )

        html = f'''<!DOCTYPE html>
<html><head><meta charset="UTF-8">
<style>
@page {{ size: {PAGE_W_MM}mm {PAGE_H_MM}mm; margin: 0; }}
* {{ margin: 0; padding: 0; }}
html, body {{ width: {PAGE_W_MM}mm; height: {PAGE_H_MM}mm; margin: 0; padding: 0; overflow: hidden; }}
svg {{ display: block; width: {PAGE_W_MM}mm; height: {PAGE_H_MM}mm; }}
</style>
</head><body>
{svg}
</body></html>'''

        html_path = os.path.join(temp_dir, 'page.html')
        with open(html_path, 'w', encoding='utf-8') as f:
            f.write(html)

        return run_wkhtmltopdf(html_path, pdf_path)
    finally:
        shutil.rmtree(temp_dir, ignore_errors=True)


def convert_html(html_path, pdf_path):
    """Convertit un HTML en PDF avec extraction des images base64."""
    with open(html_path, encoding='utf-8') as f:
        content = f.read()

    temp_dir = tempfile.mkdtemp(prefix='html_conv_')

    try:
        content = fix_image_href(content)
        content, _ = extract_base64_images(content, temp_dir)

        css_inject = f'''
@page {{ size: {PAGE_W_MM}mm {PAGE_H_MM}mm; margin: 0; }}
* {{ margin: 0; padding: 0; }}
html, body {{ width: {PAGE_W_MM}mm; height: {PAGE_H_MM}mm; margin: 0; padding: 0; }}
.page {{ width: {PAGE_W_MM}mm !important; height: {PAGE_H_MM}mm !important; 
         box-shadow: none !important; border-radius: 0 !important; 
         overflow: visible !important; }}
svg {{ display: block; width: {PAGE_W_MM}mm; height: {PAGE_H_MM}mm; }}
'''

        if '</style>' in content:
            content = content.replace('</style>', css_inject + '</style>')
        else:
            content = content.replace('</head>', f'<style>{css_inject}</style></head>')

        content = re.sub(r'background:\s*#2C2C2C\s*;?', '', content)
        content = re.sub(r'display:\s*flex\s*;?', '', content)
        content = re.sub(r'justify-content:\s*center\s*;?', '', content)
        content = re.sub(r'padding:\s*30px\s*;?', '', content)

        tmp_path = os.path.join(temp_dir, 'page.html')
        with open(tmp_path, 'w', encoding='utf-8') as f:
            f.write(content)

        return run_wkhtmltopdf(tmp_path, pdf_path)
    finally:
        shutil.rmtree(temp_dir, ignore_errors=True)


def assemble_pdf(pdf_files, output_path):
    from pypdf import PdfWriter, PdfReader
    writer = PdfWriter()
    for p in pdf_files:
        try:
            for page in PdfReader(p).pages:
                writer.add_page(page)
        except Exception as e:
            print(f"  ⚠️  Erreur lecture {os.path.basename(p)}: {e}")
    with open(output_path, 'wb') as f:
        writer.write(f)
    return len(writer.pages)


def main():
    parser = argparse.ArgumentParser(
        description="Lumières d'Israël — Conversion SVG/HTML → PDF (v4 avec fix images)"
    )
    parser.add_argument('--input-dir', default='./AVEC_FOND_PERDU',
                        help='Dossier contenant les SVG/HTML triés')
    parser.add_argument('--output', default='./La_Torah_Vivante.pdf',
                        help='Chemin du PDF final assemblé')
    parser.add_argument('--test', type=int, default=0,
                        help='Nombre de pages à convertir (0 = toutes)')
    parser.add_argument('--pages-only', action='store_true',
                        help='Générer uniquement les PDF individuels, sans assembler')
    args = parser.parse_args()

    check_prerequisites()

    all_files = sorted([
        f for f in os.listdir(args.input_dir)
        if f.endswith(('.svg', '.html'))
    ])

    if not all_files:
        print(f"❌ Aucun fichier trouvé dans {args.input_dir}")
        sys.exit(1)

    if args.test > 0:
        all_files = all_files[:args.test]
        print(f"🧪 Mode test : {len(all_files)} pages\n")

    svg_count = sum(1 for f in all_files if f.endswith('.svg'))
    html_count = sum(1 for f in all_files if f.endswith('.html'))
    print(f"═══════════════════════════════════════════════════════════")
    print(f"  LUMIÈRES D'ISRAËL — CONVERSION v4 (fix images)")
    print(f"═══════════════════════════════════════════════════════════")
    print(f"  📄 {len(all_files)} fichiers ({svg_count} SVG + {html_count} HTML)")
    print(f"  📐 Format : {PAGE_W_MM}×{PAGE_H_MM}mm (fond perdu 5mm)")
    print(f"  🖼️  Fix : extraction images base64 → fichiers temporaires")
    print()

    timestamp = time.strftime('%Y%m%d_%H%M%S')
    work_dir = f'./conversion_wk_{timestamp}'
    pdf_dir = os.path.join(work_dir, 'pages_pdf')
    os.makedirs(pdf_dir, exist_ok=True)

    pdf_files = []
    errors = []
    start = time.time()

    for i, filename in enumerate(all_files):
        src = os.path.join(args.input_dir, filename)
        pdf = os.path.join(pdf_dir, f'p{i+1:03d}.pdf')

        if filename.endswith('.svg'):
            ok, err = convert_svg(src, pdf)
        else:
            ok, err = convert_html(src, pdf)

        if ok and os.path.exists(pdf):
            pdf_files.append(pdf)
        else:
            errors.append(f'{filename}: {err[:200] if err else "inconnu"}')

        pct = (i + 1) * 100 // len(all_files)
        bar = '█' * (pct // 2) + '░' * (50 - pct // 2)
        print(f'\r  [{bar}] {pct}% ({i+1}/{len(all_files)})', end='', flush=True)

    elapsed = time.time() - start
    print(f'\n\n  ✅ {len(pdf_files)} PDF convertis en {elapsed:.1f}s')

    if errors:
        print(f'  ❌ {len(errors)} erreurs :')
        for e in errors[:10]:
            print(f'    {e}')
        if len(errors) > 10:
            print(f'    ... et {len(errors)-10} autres')

    if args.pages_only:
        print(f'\n  📂 PDF individuels : {pdf_dir}')
        print(f'  (assemblage ignoré avec --pages-only)')
        return

    print(f'\n{"═"*60}')
    print(f'  ASSEMBLAGE FINAL')
    print(f'{"═"*60}\n')

    n = assemble_pdf(pdf_files, args.output)
    size = os.path.getsize(args.output)
    print(f'  ✅ {n} pages → {args.output} ({size/1024/1024:.1f} Mo)')
    print(f'\n  📂 PDF individuels : {pdf_dir}')
    print(f'  ⚠️  Puis lancer le script CMJN FOGRA 39 sur {pdf_dir}')


if __name__ == '__main__':
    main()
