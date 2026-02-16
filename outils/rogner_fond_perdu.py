"""
ROGNER LE FOND PERDU — Lumières d'Israël
==========================================
Supprime 5mm de fond perdu sur les 4 côtés de chaque page du PDF imprimeur.

Format fini : 150 × 210 mm (15 × 21 cm)
Fond perdu  : 5 mm par côté
PDF imprimeur attendu : 160 × 220 mm par page

Usage :
  python rogner_fond_perdu.py "INT_La Torah Vivante_OK.pdf"

Produit :
  INT_La Torah Vivante_OK_ROGNE.pdf  (sans fond perdu, prêt pour flipbook)

Nécessite : pip install pymupdf
"""

import sys
import os

try:
    import fitz  # PyMuPDF
except ImportError:
    print("❌ PyMuPDF non installé. Lance : pip install pymupdf")
    sys.exit(1)

# === CONFIGURATION ===
BLEED_MM = 5.0  # Fond perdu en mm
MM_TO_PT = 72.0 / 25.4  # 1 mm = 2.8346 points
BLEED_PT = BLEED_MM * MM_TO_PT  # 5mm = 14.17 points

# Format fini attendu (pour vérification)
FINI_W_MM = 150  # largeur finie en mm
FINI_H_MM = 210  # hauteur finie en mm
FINI_W_PT = FINI_W_MM * MM_TO_PT  # ~425.2 pt
FINI_H_PT = FINI_H_MM * MM_TO_PT  # ~595.3 pt

# Tolérance pour la vérification (en points)
TOLERANCE_PT = 5.0


def rogner_pdf(input_path):
    if not os.path.exists(input_path):
        print(f"❌ Fichier introuvable : {input_path}")
        sys.exit(1)

    # Nom du fichier de sortie
    base, ext = os.path.splitext(input_path)
    output_path = f"{base}_ROGNE{ext}"

    print(f"📖 Ouverture de : {input_path}")
    doc = fitz.open(input_path)
    print(f"   {doc.page_count} pages détectées\n")

    # === VÉRIFICATION PAGE 1 ===
    page0 = doc[0]
    w_pt = page0.rect.width
    h_pt = page0.rect.height
    w_mm = w_pt / MM_TO_PT
    h_mm = h_pt / MM_TO_PT

    print(f"📐 Dimensions page 1 :")
    print(f"   {w_pt:.1f} × {h_pt:.1f} points")
    print(f"   {w_mm:.1f} × {h_mm:.1f} mm")
    print()

    # Vérifier que le fond perdu correspond
    expected_w = FINI_W_PT + 2 * BLEED_PT  # 150mm + 2×5mm = 160mm
    expected_h = FINI_H_PT + 2 * BLEED_PT  # 210mm + 2×5mm = 220mm

    w_ok = abs(w_pt - expected_w) < TOLERANCE_PT
    h_ok = abs(h_pt - expected_h) < TOLERANCE_PT

    if w_ok and h_ok:
        print(f"✅ Dimensions cohérentes avec fond perdu de {BLEED_MM}mm")
        print(f"   Attendu : {expected_w:.1f} × {expected_h:.1f} pt ({FINI_W_MM + 2*BLEED_MM:.0f} × {FINI_H_MM + 2*BLEED_MM:.0f} mm)")
        print(f"   Trouvé  : {w_pt:.1f} × {h_pt:.1f} pt ({w_mm:.1f} × {h_mm:.1f} mm)")
    else:
        print(f"⚠️  Dimensions NON standard !")
        print(f"   Attendu : {expected_w:.1f} × {expected_h:.1f} pt ({FINI_W_MM + 2*BLEED_MM:.0f} × {FINI_H_MM + 2*BLEED_MM:.0f} mm)")
        print(f"   Trouvé  : {w_pt:.1f} × {h_pt:.1f} pt ({w_mm:.1f} × {h_mm:.1f} mm)")
        print()

        # Calculer le fond perdu réel
        real_bleed_w = (w_pt - FINI_W_PT) / 2
        real_bleed_h = (h_pt - FINI_H_PT) / 2
        print(f"   Fond perdu réel estimé :")
        print(f"     Horizontal : {real_bleed_w:.1f} pt = {real_bleed_w/MM_TO_PT:.1f} mm")
        print(f"     Vertical   : {real_bleed_h:.1f} pt = {real_bleed_h/MM_TO_PT:.1f} mm")
        print()

        rep = input("   Continuer avec 5mm quand même ? (o/n) : ").strip().lower()
        if rep != 'o':
            print("   Annulé.")
            doc.close()
            sys.exit(0)

    print()
    print(f"✂️  Rognage de {BLEED_MM}mm ({BLEED_PT:.1f} pt) sur chaque côté...")

    # === ROGNAGE ===
    for i in range(doc.page_count):
        page = doc[i]
        rect = page.rect

        # Nouveau rectangle : on retire BLEED_PT de chaque côté
        new_rect = fitz.Rect(
            rect.x0 + BLEED_PT,  # gauche
            rect.y0 + BLEED_PT,  # haut
            rect.x1 - BLEED_PT,  # droite
            rect.y1 - BLEED_PT   # bas
        )
        page.set_cropbox(new_rect)

    # Vérification post-rognage
    page0_crop = doc[0]
    cw = page0_crop.rect.width
    ch = page0_crop.rect.height
    print(f"   Nouvelles dimensions : {cw:.1f} × {ch:.1f} pt = {cw/MM_TO_PT:.1f} × {ch/MM_TO_PT:.1f} mm")

    # === SAUVEGARDE ===
    print(f"\n💾 Sauvegarde : {output_path}")
    doc.save(output_path)
    doc.close()

    size_mb = os.path.getsize(output_path) / (1024 * 1024)
    print(f"   Taille : {size_mb:.1f} Mo")
    print(f"\n✅ Terminé ! {output_path} est prêt pour Calameo / flipbook.")


if __name__ == "__main__":
    if len(sys.argv) < 2:
        print("Usage : python rogner_fond_perdu.py <fichier.pdf>")
        print('Ex    : python rogner_fond_perdu.py "INT_La Torah Vivante_OK.pdf"')
        sys.exit(1)

    rogner_pdf(sys.argv[1])
