"""
ASSEMBLAGE COMPLET AVEC ROGNAGE — Lumières d'Israël
=====================================================
1. Rogne le fond perdu de chaque fichier (couvertures + intérieur)
2. Assemble le tout en un seul PDF prêt pour Calameo/Heyzine

Usage :
  python assemblage_complet.py

Fichiers attendus dans le même dossier :
  - couverture1.pdf
  - INT_La Torah Vivante_OK.pdf  (ou déjà rogné : _ROGNE.pdf)
  - couverture4.pdf

Produit :
  LIVRE_COMPLET_CALAMEO.pdf

Nécessite : pip install pymupdf
"""

import fitz  # PyMuPDF
import os
import sys

# === CONFIGURATION ===
MM_TO_PT = 72.0 / 25.4

# Format fini du livre
FINI_W_MM = 150
FINI_H_MM = 210
FINI_W_PT = FINI_W_MM * MM_TO_PT
FINI_H_PT = FINI_H_MM * MM_TO_PT

OUTPUT = "LIVRE_COMPLET_CALAMEO.pdf"

# === FICHIERS SOURCE ===
COUV1 = "couverture1.pdf"
INTERIEUR = "INT_La Torah Vivante_OK.pdf"
INTERIEUR_ROGNE = "INT_La Torah Vivante_OK_ROGNE.pdf"
COUV4 = "couverture4.pdf"


def rogner_page(page):
    """Rogne une page pour obtenir le format fini 150×210mm, centré."""
    w = page.rect.width
    h = page.rect.height
    
    # Calculer le fond perdu réel (peut varier selon le fichier)
    bleed_x = (w - FINI_W_PT) / 2
    bleed_y = (h - FINI_H_PT) / 2
    
    if bleed_x < 0.5 and bleed_y < 0.5:
        # Déjà au bon format, pas besoin de rogner
        return False
    
    new_rect = fitz.Rect(
        page.rect.x0 + bleed_x,
        page.rect.y0 + bleed_y,
        page.rect.x1 - bleed_x,
        page.rect.y1 - bleed_y
    )
    page.set_cropbox(new_rect)
    return True


def info_page(doc, label):
    """Affiche les infos d'une page."""
    p = doc[0]
    w_mm = p.rect.width / MM_TO_PT
    h_mm = p.rect.height / MM_TO_PT
    bleed_x = (p.rect.width - FINI_W_PT) / 2 / MM_TO_PT
    bleed_y = (p.rect.height - FINI_H_PT) / 2 / MM_TO_PT
    print(f"   {label} : {doc.page_count} page(s), {w_mm:.1f} × {h_mm:.1f} mm", end="")
    if bleed_x > 0.3 or bleed_y > 0.3:
        print(f"  → fond perdu {bleed_x:.1f} × {bleed_y:.1f} mm à rogner")
    else:
        print(f"  ✅ déjà au format fini")
    return bleed_x > 0.3 or bleed_y > 0.3


# === VÉRIFICATION DES FICHIERS ===
print("=" * 60)
print("  ASSEMBLAGE COMPLET — Lumières d'Israël")
print("=" * 60)
print()

# Chercher l'intérieur (rogné ou non)
if os.path.exists(INTERIEUR_ROGNE):
    int_file = INTERIEUR_ROGNE
    print(f"📖 Intérieur déjà rogné trouvé : {INTERIEUR_ROGNE}")
elif os.path.exists(INTERIEUR):
    int_file = INTERIEUR
    print(f"📖 Intérieur original trouvé : {INTERIEUR}")
else:
    print(f"❌ Aucun fichier intérieur trouvé !")
    print(f"   Attendu : {INTERIEUR} ou {INTERIEUR_ROGNE}")
    sys.exit(1)

for f in [COUV1, COUV4]:
    if not os.path.exists(f):
        print(f"❌ Fichier manquant : {f}")
        sys.exit(1)

# === OUVRIR TOUS LES FICHIERS ===
print()
print("📐 Analyse des dimensions :")
print()

doc_couv1 = fitz.open(COUV1)
doc_int = fitz.open(int_file)
doc_couv4 = fitz.open(COUV4)

need_crop_c1 = info_page(doc_couv1, "Couverture 1")
need_crop_int = info_page(doc_int, "Intérieur   ")
need_crop_c4 = info_page(doc_couv4, "Couverture 4")

# === ROGNAGE ===
print()
print("✂️  Rognage en cours...")

count = 0
if need_crop_c1:
    for i in range(doc_couv1.page_count):
        rogner_page(doc_couv1[i])
    count += doc_couv1.page_count
    print(f"   ✅ Couverture 1 rognée")

if need_crop_int:
    for i in range(doc_int.page_count):
        rogner_page(doc_int[i])
    count += doc_int.page_count
    print(f"   ✅ Intérieur rogné ({doc_int.page_count} pages)")

if need_crop_c4:
    for i in range(doc_couv4.page_count):
        rogner_page(doc_couv4[i])
    count += doc_couv4.page_count
    print(f"   ✅ Couverture 4 rognée")

if count == 0:
    print("   Rien à rogner, tous les fichiers sont déjà au bon format.")

# === VÉRIFICATION POST-ROGNAGE ===
print()
print("📐 Vérification post-rognage :")
p = doc_couv1[0]
print(f"   Couverture 1 : {p.rect.width/MM_TO_PT:.1f} × {p.rect.height/MM_TO_PT:.1f} mm")
p = doc_int[0]
print(f"   Intérieur    : {p.rect.width/MM_TO_PT:.1f} × {p.rect.height/MM_TO_PT:.1f} mm")
p = doc_couv4[0]
print(f"   Couverture 4 : {p.rect.width/MM_TO_PT:.1f} × {p.rect.height/MM_TO_PT:.1f} mm")

# === ASSEMBLAGE ===
print()
print("📚 Assemblage...")

doc_final = fitz.open()
doc_final.insert_pdf(doc_couv1)
doc_final.insert_pdf(doc_int)
doc_final.insert_pdf(doc_couv4)

total = doc_final.page_count
print(f"   Total : {total} pages")

# === SAUVEGARDE ===
print(f"\n💾 Sauvegarde : {OUTPUT}")
doc_final.save(OUTPUT, deflate=True)

doc_couv1.close()
doc_int.close()
doc_couv4.close()
doc_final.close()

size_mb = os.path.getsize(OUTPUT) / (1024 * 1024)
print(f"   Taille : {size_mb:.1f} Mo")
print(f"\n{'=' * 60}")
print(f"  ✅ {OUTPUT} prêt pour Heyzine / Calameo !")
print(f"     {total} pages — format {FINI_W_MM} × {FINI_H_MM} mm")
print(f"{'=' * 60}")
