#!/usr/bin/env python3
"""
═══════════════════════════════════════════════════════════════════════
LUMIÈRES D'ISRAËL — LA TORAH VIVANTE
Étape 3 : Conversion RGB → CMJN (FOGRA 39) via Ghostscript
═══════════════════════════════════════════════════════════════════════

Ne modifie RIEN au contenu. Convertit uniquement l'espace colorimétrique.

PRÉREQUIS :
  - Ghostscript (gs) installé
  - Profil FOGRA39 (.icc) disponible

USAGE :
  python 3_convertir_cmjn.py --input La_Torah_Vivante.pdf
"""

import argparse, os, subprocess, sys, shutil

def find_fogra39():
    """Cherche le profil FOGRA39 sur le système."""
    search_paths = [
        # Windows (chemins courants)
        r"C:\Windows\System32\spool\drivers\color",
        r"C:\Program Files\Common Files\Adobe\Color\Profiles",
        r"C:\Program Files (x86)\Common Files\Adobe\Color\Profiles",
        # Linux
        "/usr/share/color/icc",
        "/usr/share/texlive/texmf-dist/tex/generic/colorprofiles",
        "/usr/share/ghostscript",
        # Relatif (à côté du script)
        ".",
        "..",
    ]
    
    fogra_names = [
        "FOGRA39L_coated.icc",
        "FOGRA39.icc", 
        "CoatedFOGRA39.icc",
        "Coated_Fogra39L_VIGC_300.icc",
    ]
    
    for base in search_paths:
        if not os.path.exists(base):
            continue
        for root, dirs, files in os.walk(base):
            for f in files:
                if any(name.lower() in f.lower() for name in ["fogra39", "fogra 39"]):
                    return os.path.join(root, f)
    
    return None


def main():
    parser = argparse.ArgumentParser()
    parser.add_argument('--input', default='./La_Torah_Vivante.pdf')
    parser.add_argument('--output', default=None,
                        help='Fichier de sortie (défaut: ajout _CMJN)')
    parser.add_argument('--fogra', default=None,
                        help='Chemin vers le profil FOGRA39 .icc')
    args = parser.parse_args()
    
    if not os.path.exists(args.input):
        print(f"❌ Fichier introuvable : {args.input}")
        sys.exit(1)
    
    if not shutil.which('gs') and not shutil.which('gswin64c'):
        print("❌ Ghostscript non trouvé ! Installer depuis https://ghostscript.com/")
        sys.exit(1)
    
    gs_cmd = 'gswin64c' if shutil.which('gswin64c') else 'gs'
    
    # Déterminer le fichier de sortie
    if args.output is None:
        base, ext = os.path.splitext(args.input)
        args.output = f"{base}_CMJN{ext}"
    
    # Chercher FOGRA39
    fogra_path = args.fogra or find_fogra39()
    
    size_in = os.path.getsize(args.input) / 1024 / 1024
    print(f"📄 Entrée  : {args.input} ({size_in:.1f} Mo)")
    print(f"📄 Sortie  : {args.output}")
    
    # Construire la commande Ghostscript
    cmd = [
        gs_cmd,
        '-dNOPAUSE', '-dBATCH', '-dSAFER',
        '-sDEVICE=pdfwrite',
        '-sColorConversionStrategy=CMYK',
        '-dProcessColorModel=/DeviceCMYK',
        '-dCompatibilityLevel=1.5',
        '-dAutoRotatePages=/None',
        '-dDownsampleColorImages=false',
        '-dDownsampleGrayImages=false',
        '-dDownsampleMonoImages=false',
        '-dColorImageResolution=300',
        '-dGrayImageResolution=300',
        '-dEmbedAllFonts=true',
        '-dSubsetFonts=true',
        '-dCompressFonts=true',
        '-dPreserveAnnots=true',
        '-dHaveTransparency=true',
    ]
    
    if fogra_path and os.path.exists(fogra_path):
        print(f"🎨 Profil  : {fogra_path}")
        cmd.extend([
            f'-sDefaultRGBProfile=srgb.icc',
            f'-sOutputICCProfile={fogra_path}',
            '-dRenderIntent=1',
            '-dOverrideICC=true',
        ])
    else:
        print(f"⚠️  Profil FOGRA39 non trouvé — conversion CMJN standard")
        print(f"   (Pour un profil FOGRA39 : --fogra chemin/vers/FOGRA39.icc)")
    
    cmd.extend([
        f'-sOutputFile={args.output}',
        args.input,
    ])
    
    print(f"\n🔄 Conversion en cours...\n")
    
    result = subprocess.run(cmd, capture_output=True, text=True)
    
    if result.returncode != 0:
        print(f"❌ Erreur Ghostscript :")
        print(result.stderr[-500:] if result.stderr else "Pas de détails")
        sys.exit(1)
    
    if not os.path.exists(args.output):
        print(f"❌ Fichier de sortie non créé")
        sys.exit(1)
    
    size_out = os.path.getsize(args.output) / 1024 / 1024
    print(f"✅ Conversion terminée !")
    print(f"   Entrée  : {size_in:.1f} Mo (RGB)")
    print(f"   Sortie  : {size_out:.1f} Mo (CMJN)")
    print(f"   Fichier : {args.output}")
    
    # Vérification rapide
    try:
        with open(args.output, 'rb') as f:
            content = f.read().decode('latin-1')
        cmyk = content.count('DeviceCMYK')
        rgb = content.count('DeviceRGB')
        print(f"\n   Vérification :")
        print(f"   DeviceCMYK : {cmyk} occurrences")
        print(f"   DeviceRGB  : {rgb} occurrences")
        if rgb == 0:
            print(f"   🎉 100% CMJN — prêt pour l'imprimeur !")
        else:
            print(f"   ⚠️  RGB résiduel détecté — vérifier avec l'imprimeur")
    except:
        pass

if __name__ == '__main__':
    main()
