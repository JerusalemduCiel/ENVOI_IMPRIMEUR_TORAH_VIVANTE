#!/usr/bin/env python3
"""
Vérification des dimensions après ajout du fond perdu
Attendu : ~453.3 × 623.3 px (160×220mm)
Usage : python verifier_dimensions.py ./AVEC_FOND_PERDU
"""

import os, re, sys

EXPECTED_W = 453.3
EXPECTED_H = 623.3
TOLERANCE = 1.0  # marge de tolérance en px

def check_file(filepath):
    with open(filepath, encoding='utf-8') as f:
        content = f.read()
    
    # Chercher les dimensions SVG
    m = re.search(r'width="([^"]+)"\s+height="([^"]+)"', content)
    if not m:
        return None, None, "PAS DE SVG TROUVÉ"
    
    w, h = float(m.group(1)), float(m.group(2))
    
    if abs(w - EXPECTED_W) > TOLERANCE or abs(h - EXPECTED_H) > TOLERANCE:
        return w, h, "ERREUR"
    return w, h, "OK"

def main():
    dossier = sys.argv[1] if len(sys.argv) > 1 else './AVEC_FOND_PERDU'
    
    files = sorted(f for f in os.listdir(dossier) if f.endswith(('.svg', '.html')))
    
    ok = 0
    erreurs = []
    
    for f in files:
        w, h, status = check_file(os.path.join(dossier, f))
        if status == "OK":
            ok += 1
        else:
            erreurs.append((f, w, h, status))
    
    print(f"{'='*60}")
    print(f"VÉRIFICATION DIMENSIONS — Attendu : {EXPECTED_W} × {EXPECTED_H} px")
    print(f"{'='*60}")
    print(f"✅ Conformes : {ok}/{len(files)}")
    
    if erreurs:
        print(f"\n❌ PROBLÈMES ({len(erreurs)}) :")
        for f, w, h, status in erreurs:
            print(f"   {f}")
            print(f"   → {w} × {h} ({status})")
    else:
        print(f"\n🎉 Tous les {ok} fichiers sont aux bonnes dimensions !")

if __name__ == '__main__':
    main()
