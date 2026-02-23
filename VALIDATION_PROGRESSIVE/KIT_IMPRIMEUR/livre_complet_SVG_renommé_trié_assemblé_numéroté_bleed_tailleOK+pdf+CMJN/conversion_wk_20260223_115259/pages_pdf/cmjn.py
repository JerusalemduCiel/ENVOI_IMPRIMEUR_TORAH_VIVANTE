#!/usr/bin/env python3
"""
Conversion CMJN fichier par fichier sur les PDF individuels existants.
Puis réassemblage en un seul PDF.

USAGE :
  python 3_convertir_cmjn_pages.py --input-dir ./pages_pdf --output ../La_Torah_Vivante_CMJN.pdf
"""

import argparse, os, subprocess, sys, shutil, time

def get_gs():
    for cmd in ['gswin64c', 'gswin32c', 'gs']:
        if shutil.which(cmd):
            return cmd
    print("❌ Ghostscript non trouvé !")
    sys.exit(1)

def main():
    parser = argparse.ArgumentParser()
    parser.add_argument('--input-dir', default='./pages_pdf')
    parser.add_argument('--output', default='./La_Torah_Vivante_CMJN.pdf')
    args = parser.parse_args()

    try:
        from pypdf import PdfWriter, PdfReader
    except ImportError:
        print("❌ pypdf non installé. Faire: pip install pypdf")
        sys.exit(1)

    gs = get_gs()

    files = sorted([f for f in os.listdir(args.input_dir) if f.endswith('.pdf')])
    if not files:
        print(f"❌ Aucun PDF dans {args.input_dir}")
        sys.exit(1)

    out_dir = os.path.join(args.input_dir, '..', 'pages_cmjn')
    os.makedirs(out_dir, exist_ok=True)

    print(f"📄 {len(files)} fichiers à convertir en CMJN")
    print(f"📂 Entrée  : {args.input_dir}")
    print(f"📂 Sortie  : {out_dir}\n")

    errors = []
    start = time.time()

    for i, f in enumerate(files):
        src = os.path.join(args.input_dir, f)
        dst = os.path.join(out_dir, f)

        result = subprocess.run([
            gs,
            '-dNOPAUSE', '-dBATCH', '-dSAFER', '-dQUIET',
            '-sDEVICE=pdfwrite',
            '-sColorConversionStrategy=CMYK',
            '-dProcessColorModel=/DeviceCMYK',
            '-dCompatibilityLevel=1.5',
            '-dAutoRotatePages=/None',
            '-dDownsampleColorImages=false',
            '-dDownsampleGrayImages=false',
            '-dDownsampleMonoImages=false',
            '-dEmbedAllFonts=true',
            '-dSubsetFonts=true',
            '-dHaveTransparency=true',
            f'-sOutputFile={dst}',
            src
        ], capture_output=True, text=True)

        if result.returncode != 0 or not os.path.exists(dst):
            errors.append(f)
            shutil.copy(src, dst)

        pct = (i + 1) * 100 // len(files)
        bar = '█' * (pct // 2) + '░' * (50 - pct // 2)
        print(f'\r  [{bar}] {pct}% ({i+1}/{len(files)})', end='', flush=True)

    elapsed = time.time() - start
    print(f'\n\n  ✅ Conversion terminée en {elapsed:.0f}s')
    if errors:
        print(f'  ⚠️  {len(errors)} erreurs : {errors[:10]}')

    # Assemblage
    print(f'\n  Assemblage...')
    writer = PdfWriter()
    for f in sorted(os.listdir(out_dir)):
        if f.endswith('.pdf'):
            for page in PdfReader(os.path.join(out_dir, f)).pages:
                writer.add_page(page)

    with open(args.output, 'wb') as fo:
        writer.write(fo)

    size = os.path.getsize(args.output) / 1024 / 1024
    print(f'  ✅ {len(writer.pages)} pages → {args.output} ({size:.1f} Mo)')
    print(f'\n  🎉 Prêt pour l\'imprimeur !')

if __name__ == '__main__':
    main()
