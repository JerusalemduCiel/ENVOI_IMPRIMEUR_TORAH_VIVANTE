#!/usr/bin/env python3
"""
═══════════════════════════════════════════════════════════════════════
LUMIÈRES D'ISRAËL — LA TORAH VIVANTE
Conversion RGB → CMJN FOGRA 39 via Ghostscript
═══════════════════════════════════════════════════════════════════════

v6 — Compatible Ghostscript 10.06+
  - Supprimé -dSAFER (bloque l'accès ICC en GS 10.06)
  - Supprimé -dProcessColorModel (déprécié en GS 10.x)
  - Utilise -dNOSAFER pour accès aux profils ICC

USAGE :
  python 3_cmjn_fogra39_v6.py --input-dir . --output ../La_Torah_Vivante_CMJN.pdf
"""

import argparse, os, subprocess, sys, shutil, time, glob


def get_gs():
    for cmd in ['gswin64c', 'gswin32c', 'gs']:
        if shutil.which(cmd):
            # Afficher la version
            r = subprocess.run([cmd, '--version'], capture_output=True, text=True)
            ver = r.stdout.strip() if r.returncode == 0 else '?'
            return cmd, ver
    print("❌ Ghostscript non trouvé !")
    sys.exit(1)


def find_icc(name_pattern, extra_dirs=None):
    search_paths = [
        '.',
        os.path.dirname(os.path.abspath(__file__)),
        r'C:\Windows\System32\spool\drivers\color',
        '/usr/share/color/icc/ghostscript',
    ]
    for base in [r'C:\Program Files', r'C:\Program Files (x86)']:
        if os.path.exists(base):
            for d in glob.glob(os.path.join(base, 'gs*')):
                search_paths.append(d)
    if extra_dirs:
        search_paths.extend(extra_dirs)

    for base in search_paths:
        if not os.path.exists(base):
            continue
        for pattern in [f'**/*{name_pattern}*', f'*{name_pattern}*']:
            try:
                for m in glob.glob(os.path.join(base, pattern), recursive=True):
                    if m.lower().endswith(('.icc', '.icm')):
                        return m
            except Exception:
                pass
    return None


def convert_one(gs_cmd, src, dst, fogra_path=None, srgb_path=None):
    """Convertit un PDF RGB en CMYK — compatible GS 10.06+"""

    cmd = [
        gs_cmd,
        '-dNOPAUSE', '-dBATCH', '-dQUIET',
        '-dNOSAFER',                          # ← CRUCIAL pour GS 10.06 (accès ICC)
        '-sDEVICE=pdfwrite',
        '-sColorConversionStrategy=CMYK',      # Conversion vers CMYK
        '-dCompatibilityLevel=1.5',
        '-dAutoRotatePages=/None',
        '-dDownsampleColorImages=false',
        '-dDownsampleGrayImages=false',
        '-dDownsampleMonoImages=false',
        '-dEmbedAllFonts=true',
        '-dSubsetFonts=true',
    ]

    # Profils ICC
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
    try:
        with open(filepath, 'rb') as f:
            raw = f.read(50000)
            return b'DeviceCMYK' in raw
    except Exception:
        return False


def assemble(pdf_dir, output_path):
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
    parser = argparse.ArgumentParser()
    parser.add_argument('--input-dir', default='.')
    parser.add_argument('--output', default='../La_Torah_Vivante_CMJN.pdf')
    parser.add_argument('--fogra', default=None)
    parser.add_argument('--no-assemble', action='store_true')
    args = parser.parse_args()

    try:
        from pypdf import PdfWriter, PdfReader
    except ImportError:
        print("❌ pypdf non installé. Faire: pip install pypdf")
        sys.exit(1)

    print("═" * 65)
    print("  LUMIÈRES D'ISRAËL — CONVERSION CMJN (v6 — GS 10.06+)")
    print("═" * 65)
    print()

    gs, gs_ver = get_gs()
    print(f"  ✅ Ghostscript : {gs} (version {gs_ver})")

    extra_dirs = [args.input_dir, os.path.abspath(args.input_dir)]

    fogra_path = args.fogra
    if not fogra_path:
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

    # ── Test rapide sur le premier fichier ──
    all_pdf = sorted([
        f for f in os.listdir(args.input_dir)
        if f.endswith('.pdf') and f[0] == 'p' and f[1:-4].isdigit()
    ])

    if not all_pdf:
        print(f"\n  ❌ Aucun fichier pXXX.pdf dans {args.input_dir}")
        sys.exit(1)

    print(f"\n  🧪 Test rapide sur {all_pdf[0]}...")
    test_src = os.path.join(args.input_dir, all_pdf[0])
    test_dst = os.path.join(args.input_dir, '_test_cmyk.pdf')
    ok, err = convert_one(gs, test_src, test_dst, fogra_path, srgb_path)

    if ok and os.path.exists(test_dst) and verify_cmyk(test_dst):
        print(f"  ✅ Test réussi — DeviceCMYK confirmé !")
        os.remove(test_dst)
    else:
        print(f"  ❌ Test échoué !")
        if err:
            print(f"     Erreur GS : {err[:300]}")
        # Essayer sans ICC
        print(f"\n  🔄 Nouvel essai SANS profil ICC...")
        ok2, err2 = convert_one(gs, test_src, test_dst, None, None)
        if ok2 and os.path.exists(test_dst) and verify_cmyk(test_dst):
            print(f"  ✅ Fonctionne SANS ICC — on continue en mode générique")
            fogra_path = None
            srgb_path = None
            os.remove(test_dst)
        else:
            print(f"  ❌ Échec total. Erreur Ghostscript :")
            print(f"     {err2[:500] if err2 else 'aucun message'}")
            if os.path.exists(test_dst):
                os.remove(test_dst)
            sys.exit(1)

    # ── Conversion complète ──
    out_dir = os.path.join(os.path.dirname(os.path.abspath(args.input_dir)), 'pages_cmjn')
    os.makedirs(out_dir, exist_ok=True)

    mode = 'FOGRA 39' if fogra_path else 'CMYK générique'
    print(f"\n  📄 {len(all_pdf)} fichiers à convertir")
    print(f"  📂 Entrée  : {os.path.abspath(args.input_dir)}")
    print(f"  📂 Sortie  : {os.path.abspath(out_dir)}")
    print(f"  🎨 Mode    : {mode}")
    print()

    errors = []
    cmyk_ok = 0
    start = time.time()

    for i, filename in enumerate(all_pdf):
        src = os.path.join(args.input_dir, filename)
        dst = os.path.join(out_dir, filename)

        ok, err = convert_one(gs, src, dst, fogra_path, srgb_path)

        if ok and os.path.exists(dst):
            if verify_cmyk(dst):
                cmyk_ok += 1
            else:
                errors.append(f"{filename}: converti mais encore RGB")
        else:
            errors.append(f"{filename}: {err[:150] if err else 'erreur'}")
            shutil.copy2(src, dst)

        pct = (i + 1) * 100 // len(all_pdf)
        bar = '█' * (pct // 2) + '░' * (50 - pct // 2)
        print(f'\r  [{bar}] {pct}% ({i+1}/{len(all_pdf)}) CMYK:{cmyk_ok}', end='', flush=True)

    elapsed = time.time() - start
    print(f'\n\n  ✅ Conversion terminée en {elapsed:.0f}s')
    print(f'  🎨 CMYK confirmé : {cmyk_ok}/{len(all_pdf)}')

    if errors:
        print(f'\n  ⚠️  {len(errors)} problèmes :')
        for e in errors[:15]:
            print(f'    → {e}')

    if not args.no_assemble:
        print(f'\n{"═"*65}')
        print(f'  ASSEMBLAGE FINAL')
        print(f'{"═"*65}\n')
        n = assemble(out_dir, args.output)
        size = os.path.getsize(args.output) / 1024 / 1024
        print(f'  ✅ {n} pages → {args.output} ({size:.1f} Mo)')

    print(f'\n  📂 PDF CMJN : {os.path.abspath(out_dir)}')
    if cmyk_ok == len(all_pdf):
        print(f'\n  🎉 100% CMYK — Prêt pour l\'imprimeur !')


if __name__ == '__main__':
    main()
