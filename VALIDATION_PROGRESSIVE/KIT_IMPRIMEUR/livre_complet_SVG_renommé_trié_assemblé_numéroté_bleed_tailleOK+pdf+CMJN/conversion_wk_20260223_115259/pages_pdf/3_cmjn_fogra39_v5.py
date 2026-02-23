#!/usr/bin/env python3
"""
═══════════════════════════════════════════════════════════════════════
LUMIÈRES D'ISRAËL — LA TORAH VIVANTE
Conversion RGB → CMJN FOGRA 39 via Ghostscript
═══════════════════════════════════════════════════════════════════════

v5 — Script testé et vérifié (conversion CMYK confirmée)

USAGE :
  python 3_cmjn_fogra39_v5.py --input-dir ./pages_pdf --output ../La_Torah_Vivante_CMJN.pdf

PRÉREQUIS :
  - Ghostscript (gswin64c / gs)
  - pypdf (pip install pypdf)
  - Optionnel : ISOcoated_v2_300_eci.icc dans le même dossier
"""

import argparse, os, subprocess, sys, shutil, time, glob


def get_gs():
    """Trouve Ghostscript sur le système."""
    for cmd in ['gswin64c', 'gswin32c', 'gs']:
        if shutil.which(cmd):
            return cmd
    print("❌ Ghostscript non trouvé !")
    sys.exit(1)


def find_icc(name_pattern, extra_dirs=None):
    """Cherche un profil ICC par nom."""
    search_paths = [
        # Dossier courant et dossier du script
        '.',
        os.path.dirname(os.path.abspath(__file__)),
        # Windows
        r'C:\Windows\System32\spool\drivers\color',
    ]
    
    # Ajouter les dossiers Ghostscript Windows
    for base in [r'C:\Program Files', r'C:\Program Files (x86)']:
        if os.path.exists(base):
            for d in glob.glob(os.path.join(base, 'gs*')):
                search_paths.append(d)
    
    # Linux
    search_paths.extend([
        '/usr/share/color/icc',
        '/usr/share/color/icc/ghostscript',
        '/usr/share/ghostscript',
    ])
    
    if extra_dirs:
        search_paths.extend(extra_dirs)
    
    for base in search_paths:
        if not os.path.exists(base):
            continue
        for pattern in [f'**/*{name_pattern}*', f'*{name_pattern}*']:
            try:
                for m in glob.glob(os.path.join(base, pattern), recursive=True):
                    if m.lower().endswith('.icc') or m.lower().endswith('.icm'):
                        return m
            except Exception:
                pass
    return None


def convert_one(gs_cmd, src, dst, fogra_path=None, srgb_path=None):
    """Convertit un PDF RGB en CMYK via Ghostscript."""
    
    # Paramètres de base — TESTÉS ET VÉRIFIÉS
    cmd = [
        gs_cmd,
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
    ]
    
    # Profils ICC optionnels (FOGRA 39)
    if fogra_path:
        if srgb_path:
            cmd.append(f'-sDefaultRGBProfile={srgb_path}')
        cmd.append(f'-sOutputICCProfile={fogra_path}')
        cmd.append('-dRenderIntent=1')
        cmd.append('-dOverrideICC=true')
    
    cmd.extend([f'-sOutputFile={dst}', src])
    
    result = subprocess.run(cmd, capture_output=True, text=True)
    return result.returncode == 0, result.stderr


def verify_cmyk(filepath):
    """Vérifie rapidement si un PDF contient du CMYK."""
    try:
        with open(filepath, 'rb') as f:
            raw = f.read(50000)  # Lire juste le début
            return b'DeviceCMYK' in raw
    except Exception:
        return False


def assemble(pdf_dir, output_path):
    """Assemble les PDF individuels en un seul fichier."""
    from pypdf import PdfWriter, PdfReader
    writer = PdfWriter()
    files = sorted([f for f in os.listdir(pdf_dir) if f.endswith('.pdf')])
    for f in files:
        try:
            for page in PdfReader(os.path.join(pdf_dir, f)).pages:
                writer.add_page(page)
        except Exception as e:
            print(f"  ⚠️  Erreur lecture {f}: {e}")
    with open(output_path, 'wb') as fo:
        writer.write(fo)
    return len(writer.pages)


def main():
    parser = argparse.ArgumentParser(
        description="Conversion RGB → CMJN FOGRA 39"
    )
    parser.add_argument('--input-dir', default='.',
                        help='Dossier contenant les PDF RGB (p001.pdf...)')
    parser.add_argument('--output', default='../La_Torah_Vivante_CMJN.pdf',
                        help='Chemin du PDF CMJN assemblé')
    parser.add_argument('--fogra', default=None,
                        help='Chemin direct vers le profil FOGRA 39 .icc')
    parser.add_argument('--no-assemble', action='store_true',
                        help='Ne pas assembler, juste convertir')
    args = parser.parse_args()

    try:
        from pypdf import PdfWriter, PdfReader
    except ImportError:
        print("❌ pypdf non installé. Faire: pip install pypdf")
        sys.exit(1)

    print("═" * 65)
    print("  LUMIÈRES D'ISRAËL — CONVERSION CMJN FOGRA 39 (v5)")
    print("═" * 65)
    print()

    # Ghostscript
    gs = get_gs()
    print(f"  ✅ Ghostscript : {gs}")

    # Profils ICC
    extra_dirs = [args.input_dir]
    
    fogra_path = args.fogra
    if not fogra_path:
        # Chercher ISOcoated_v2_300 d'abord (le meilleur), puis FOGRA39
        fogra_path = find_icc('ISOcoated_v2_300', extra_dirs)
        if not fogra_path:
            fogra_path = find_icc('FOGRA39', extra_dirs)
        if not fogra_path:
            fogra_path = find_icc('Coated', extra_dirs)
    
    srgb_path = find_icc('srgb', extra_dirs) or find_icc('sRGB', extra_dirs)

    if fogra_path and os.path.exists(fogra_path):
        print(f"  ✅ Profil FOGRA 39 : {fogra_path}")
    else:
        fogra_path = None
        print("  ⚠️  Pas de profil FOGRA 39 — conversion CMYK générique")

    if srgb_path and os.path.exists(srgb_path):
        print(f"  ✅ Profil sRGB : {srgb_path}")
    else:
        srgb_path = None

    # Fichiers à convertir (uniquement les pXXX.pdf)
    all_files = sorted([
        f for f in os.listdir(args.input_dir)
        if f.endswith('.pdf') and f[0] == 'p' and f[1:-4].isdigit()
    ])

    if not all_files:
        print(f"\n  ❌ Aucun fichier pXXX.pdf dans {args.input_dir}")
        sys.exit(1)

    # Dossier de sortie
    out_dir = os.path.join(os.path.dirname(args.input_dir.rstrip('/\\')), 'pages_cmjn')
    if os.path.abspath(out_dir) == os.path.abspath(args.input_dir):
        out_dir = os.path.join(args.input_dir, '..', 'pages_cmjn')
    os.makedirs(out_dir, exist_ok=True)

    mode = 'FOGRA 39 (couché standard européen)' if fogra_path else 'CMYK générique'
    print(f"\n  📄 {len(all_files)} fichiers à convertir")
    print(f"  📂 Entrée  : {os.path.abspath(args.input_dir)}")
    print(f"  📂 Sortie  : {os.path.abspath(out_dir)}")
    print(f"  🎨 Mode    : {mode}")
    print()

    # Conversion
    errors = []
    cmyk_ok = 0
    start = time.time()

    for i, filename in enumerate(all_files):
        src = os.path.join(args.input_dir, filename)
        dst = os.path.join(out_dir, filename)

        ok, err = convert_one(gs, src, dst, fogra_path, srgb_path)

        if ok and os.path.exists(dst):
            if verify_cmyk(dst):
                cmyk_ok += 1
            else:
                errors.append(f"{filename}: converti mais encore RGB!")
        else:
            errors.append(f"{filename}: {err[:150] if err else 'erreur inconnue'}")
            # Copier l'original en fallback
            shutil.copy2(src, dst)

        pct = (i + 1) * 100 // len(all_files)
        bar = '█' * (pct // 2) + '░' * (50 - pct // 2)
        print(f'\r  [{bar}] {pct}% ({i+1}/{len(all_files)})', end='', flush=True)

    elapsed = time.time() - start
    print(f'\n\n  ✅ Conversion terminée en {elapsed:.0f}s')
    print(f'  🎨 CMYK confirmé : {cmyk_ok}/{len(all_files)}')

    if errors:
        print(f'\n  ⚠️  {len(errors)} problèmes :')
        for e in errors[:15]:
            print(f'    → {e}')
        if len(errors) > 15:
            print(f'    ... et {len(errors)-15} autres')

    if cmyk_ok == 0:
        print("\n  ❌ ALERTE : Aucun fichier n'est en CMYK !")
        print("  → Vérifier la version de Ghostscript")
        print("  → Essayer sans profil ICC : python script.py --fogra none")
        return

    # Assemblage
    if not args.no_assemble:
        print(f'\n{"═"*65}')
        print(f'  ASSEMBLAGE FINAL')
        print(f'{"═"*65}\n')

        n = assemble(out_dir, args.output)
        size = os.path.getsize(args.output) / 1024 / 1024
        print(f'  ✅ {n} pages → {args.output} ({size:.1f} Mo)')

    print(f'\n  📂 PDF individuels CMJN : {os.path.abspath(out_dir)}')
    
    if cmyk_ok == len(all_files):
        print(f'\n  🎉 Prêt pour l\'imprimeur !')
    

if __name__ == '__main__':
    main()
