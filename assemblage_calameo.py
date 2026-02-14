"""
ASSEMBLAGE COMPLET — Lumières d'Israël
=======================================
Assemble : couverture1.pdf + INT rogné + couverture4.pdf

Usage :
  python assemblage_calameo.py

Produit :
  LIVRE_COMPLET_CALAMEO.pdf

Nécessite : pip install pymupdf
"""

import fitz  # PyMuPDF
import os
import sys

# === FICHIERS ===
COUV1 = "couverture1.pdf"
INTERIEUR = "INT_La Torah Vivante_OK_ROGNE.pdf"
COUV4 = "couverture4.pdf"
OUTPUT = "LIVRE_COMPLET_CALAMEO.pdf"

# === VÉRIFICATION ===
for f in [COUV1, INTERIEUR, COUV4]:
    if not os.path.exists(f):
        print(f"❌ Fichier manquant : {f}")
        sys.exit(1)

print("📖 Assemblage en cours...\n")

# Ouvrir les 3 PDF
doc_couv1 = fitz.open(COUV1)
doc_int = fitz.open(INTERIEUR)
doc_couv4 = fitz.open(COUV4)

print(f"   📕 {COUV1} : {doc_couv1.page_count} page(s)")
print(f"   📖 {INTERIEUR} : {doc_int.page_count} pages")
print(f"   📗 {COUV4} : {doc_couv4.page_count} page(s)")

# Créer le document final
doc_final = fitz.open()

# 1. Ajouter couverture 1
doc_final.insert_pdf(doc_couv1)

# 2. Ajouter intérieur rogné
doc_final.insert_pdf(doc_int)

# 3. Ajouter couverture 4
doc_final.insert_pdf(doc_couv4)

total = doc_final.page_count
print(f"\n   📚 Total : {total} pages")

# Sauvegarder
print(f"\n💾 Sauvegarde : {OUTPUT}")
doc_final.save(OUTPUT)

# Fermer
doc_couv1.close()
doc_int.close()
doc_couv4.close()
doc_final.close()

size_mb = os.path.getsize(OUTPUT) / (1024 * 1024)
print(f"   Taille : {size_mb:.1f} Mo")
print(f"\n✅ {OUTPUT} prêt pour Calameo !")
