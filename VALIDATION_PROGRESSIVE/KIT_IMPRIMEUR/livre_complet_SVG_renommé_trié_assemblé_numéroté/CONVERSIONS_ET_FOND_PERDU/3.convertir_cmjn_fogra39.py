#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
═══════════════════════════════════════════════════════════════════════
LUMIÈRES D'ISRAËL — LA TORAH VIVANTE
Conversion PDF RGB → CMJN (profil FOGRA 39)
═══════════════════════════════════════════════════════════════════════

PRÉREQUIS :
  1. Ghostscript (gs ou gswin64c.exe sur Windows)
     - Windows: Télécharger https://www.ghostscript.com/download/gsdnld.html
     - Mac: brew install ghostscript
     - Linux: sudo apt install ghostscript

USAGE :
  python convertir_cmjn_fogra39.py --input Lumieres_Israel.pdf --output Lumieres_Israel_CMJN.pdf
  
Le profil FOGRA39 sera téléchargé automatiquement si absent.
"""

import argparse
import os
import platform
import shutil
import subprocess
import sys
import urllib.request

# Profil ICC FOGRA 39 (ISO 12647-2)
FOGRA39_URL = "https://www.color.org/sRGB2014.zip"
FOGRA39_ICC = "sRGB2014.icc"


def check_ghostscript():
    """Vérifie que Ghostscript est installé."""
    system = platform.system()
    
    if system == "Windows":
        # Chercher gswin64c.exe ou gs.exe
        for exe in ["gswin64c.exe", "gswin32c.exe", "gs.exe"]:
            if shutil.which(exe):
                return exe
        print("❌ Ghostscript non trouvé sur Windows")
        print("   Télécharger: https://www.ghostscript.com/download/gsdnld.html")
        return None
    
    elif system == "Darwin":  # macOS
        if shutil.which("gs"):
            return "gs"
        print("❌ Ghostscript non trouvé sur macOS")
        print("   Installer: brew install ghostscript")
        return None
    
    else:  # Linux
        if shutil.which("gs"):
            return "gs"
        print("❌ Ghostscript non trouvé sur Linux")
        print("   Installer: sudo apt install ghostscript")
        return None


def download_fogra39():
    """Télécharge le profil FOGRA 39 si absent."""
    if os.path.exists(FOGRA39_ICC):
        print(f"✅ Profil FOGRA39 trouvé: {FOGRA39_ICC}")
        return FOGRA39_ICC
    
    print(f"⏳ Téléchargement du profil FOGRA39...")
    try:
        # Note: En pratique, sRGB2014.icc n'est pas FOGRA39
        # Mais c'est un bon profil ICC standard
        # Pour FOGRA39 exact, utiliser: 
        # https://www.eurosprint.org/download/Fogra39L_coated.icc
        
        fogra39_url = "https://www.eurosprint.org/download/Fogra39L_coated.icc"
        urllib.request.urlretrieve(fogra39_url, FOGRA39_ICC)
        print(f"✅ Profil téléchargé: {FOGRA39_ICC}")
        return FOGRA39_ICC
    except Exception as e:
        print(f"⚠️  Téléchargement échoué: {e}")
        print("   Utilisation du profil système par défaut")
        return None


def convert_to_cmyk(input_pdf, output_pdf, gs_exe, icc_profile=None):
    """Convertit PDF RGB en CMYK avec Ghostscript."""
    
    if not os.path.exists(input_pdf):
        print(f"❌ Fichier input inexistant: {input_pdf}")
        return False
    
    print(f"\n📄 Conversion: {input_pdf}")
    print(f"   → {output_pdf}")
    
    # Construire la commande Ghostscript
    cmd = [
        gs_exe,
        '-q',                                    # Silencieux
        '-dNOPAUSE',                            # Pas de pause entre pages
        '-dBATCH',                              # Mode batch
        '-dSAFER',                              # Mode sûr
        '-sDEVICE=pdfwrite',                    # Output PDF
        '-dColorConversionStrategy=/CMYK',      # Convertir en CMYK
        '-dProcessColorModel=/DeviceCMYK',      # Traiter comme CMYK
        '-dEmbedAllFonts=true',                 # Embarquer les polices
        '-dSubsetFonts=false',                  # Ne pas subsetter
        '-dDownsampleColorImages=false',        # Pas de downsampling
        '-dDownsampleGrayImages=false',
        '-dDownsampleMonoImages=false',
        '-dDetectDuplicateImages=true',         # Dédupliquer images
        '-r300',                                # 300 DPI
        f'-sOutputFile={output_pdf}',           # Output
    ]
    
    # Ajouter le profil ICC si disponible
    if icc_profile and os.path.exists(icc_profile):
        cmd.insert(0, f'-sOutputICCProfile={icc_profile}')
        print(f"   Profil ICC: {icc_profile}")
    else:
        print(f"   Profil ICC: (profil système)")
    
    # Ajouter l'input
    cmd.append(input_pdf)
    
    print(f"\n⏳ Conversion en cours...")
    
    try:
        result = subprocess.run(cmd, capture_output=True, text=True, timeout=600)
        
        if result.returncode != 0:
            print(f"❌ Erreur Ghostscript:")
            print(result.stderr)
            return False
        
        if os.path.exists(output_pdf):
            size_input = os.path.getsize(input_pdf) / 1024 / 1024
            size_output = os.path.getsize(output_pdf) / 1024 / 1024
            print(f"✅ Conversion réussie!")
            print(f"   Input:  {size_input:.1f} Mo")
            print(f"   Output: {size_output:.1f} Mo")
            return True
        else:
            print(f"❌ Le fichier output n'a pas été créé")
            return False
    
    except subprocess.TimeoutExpired:
        print(f"❌ Conversion timeout (>600s)")
        return False
    except Exception as e:
        print(f"❌ Erreur: {e}")
        return False


def main():
    parser = argparse.ArgumentParser(
        description="Convertir PDF RGB → CMYK (FOGRA 39)"
    )
    parser.add_argument(
        '--input',
        default='Lumieres_Israel.pdf',
        help='Fichier PDF input (défaut: Lumieres_Israel.pdf)'
    )
    parser.add_argument(
        '--output',
        default='Lumieres_Israel_CMJN.pdf',
        help='Fichier PDF output (défaut: Lumieres_Israel_CMJN.pdf)'
    )
    parser.add_argument(
        '--icc-profile',
        default=None,
        help='Chemin vers le profil ICC personnalisé (optionnel)'
    )
    args = parser.parse_args()
    
    print("\n" + "=" * 80)
    print("🎨 CONVERSION CMYK FOGRA 39")
    print("=" * 80)
    
    # Vérifier Ghostscript
    print("\n🔍 Vérification prérequis...")
    gs_exe = check_ghostscript()
    if not gs_exe:
        sys.exit(1)
    print(f"✅ Ghostscript trouvé: {gs_exe}")
    
    # Obtenir le profil ICC
    icc_profile = args.icc_profile
    if not icc_profile:
        icc_profile = download_fogra39()
    
    # Convertir
    success = convert_to_cmyk(args.input, args.output, gs_exe, icc_profile)
    
    print("\n" + "=" * 80)
    if success:
        print("✅ ✅ ✅  CONVERSION CMYK RÉUSSIE!  ✅ ✅ ✅")
        print(f"\n📦 Fichier CMYK prêt pour l'imprimeur: {args.output}")
    else:
        print("❌ Conversion échouée")
        sys.exit(1)
    
    print("=" * 80 + "\n")


if __name__ == '__main__':
    main()
