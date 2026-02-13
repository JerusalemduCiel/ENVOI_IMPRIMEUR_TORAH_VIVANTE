import fitz  # PyMuPDF
import os
from pathlib import Path
import natsort

# --- Configuration ---
INPUT_DIR = Path(os.getcwd())
OUTPUT_FILE = INPUT_DIR.parent / "LUMIERES_DISRAEL_LA_TORAH_VIVANTE_296p.pdf"

print("="*80)
print("ASSEMBLAGE FINAL - LIVRE 'LUMIERES D'ISRAEL - LA TORAH VIVANTE'")
print("="*80)
print(f"Dossier source: {INPUT_DIR}")
print(f"Fichier de sortie: {OUTPUT_FILE}\n")

# --- Collecter et trier les fichiers ---
pdf_files = natsort.natsorted(INPUT_DIR.glob("P*.pdf"))

print(f"Fichiers trouves: {len(pdf_files)}")
if len(pdf_files) != 296:
    print(f"ATTENTION: {len(pdf_files)} fichiers au lieu de 296!")
    # Lister les fichiers trouves pour debug
    print("\nFichiers trouves:")
    for i, f in enumerate(pdf_files[:10]):
        print(f"  {i+1}. {f.name}")
    if len(pdf_files) > 10:
        print(f"  ... et {len(pdf_files) - 10} autres")
else:
    print("Nombre de fichiers correct: 296")

# Vérifier l'ordre
print("\n--- Ordre d'assemblage (5 premiers / 5 derniers) ---")
for f in pdf_files[:5]:
    print(f"  {f.name}")
print("  ...")
for f in pdf_files[-5:]:
    print(f"  {f.name}")

# --- Assemblage ---
print("\nAssemblage en cours...")
output = fitz.open()

fichiers_ignores = []
fichiers_assembles = 0

for i, pdf_path in enumerate(pdf_files):
    fname = pdf_path.name
    try:
        doc = fitz.open(str(pdf_path))
        
        # Vérification dimensions
        page = doc[0]
        w, h = round(page.rect.width, 2), round(page.rect.height, 2)
        if abs(w - 453.54) > 1 or abs(h - 623.62) > 1:
            print(f"  [ERREUR] dimensions {fname}: {w:.1f} x {h:.1f} - IGNORE")
            fichiers_ignores.append((fname, w, h))
            doc.close()
            continue
        
        output.insert_pdf(doc)
        doc.close()
        fichiers_assembles += 1
        
        if (i + 1) % 50 == 0:
            print(f"  {i + 1}/{len(pdf_files)} fichiers traites, {fichiers_assembles} pages assemblees...")
    except Exception as e:
        print(f"  [ERREUR] {fname}: {e} - IGNORE")
        fichiers_ignores.append((fname, "ERREUR", str(e)))

print(f"\nTotal pages dans le PDF: {len(output)}")
if fichiers_ignores:
    print(f"Fichiers ignores: {len(fichiers_ignores)}")
    for fname, w, h in fichiers_ignores[:5]:
        print(f"  - {fname}: {w} x {h}")

# --- Metadonnees ---
output.set_metadata({
    "title": "Lumieres d'Israel — La Torah Vivante",
    "author": "Michael Lumbroso",
    "subject": "118 figures fondatrices du judaisme — 4000 ans de sagesse",
    "creator": "Ora Shel Torah",
    "producer": "PyMuPDF",
    "keywords": "Torah, judaisme, sages, histoire juive, Lumieres d'Israel"
})

# --- Sauvegarde ---
print(f"\nSauvegarde: {OUTPUT_FILE}")
output.save(str(OUTPUT_FILE), garbage=4, deflate=True, deflate_images=True, deflate_fonts=True)
output.close()

# --- Verification finale ---
print("\n" + "="*80)
print("VERIFICATION FINALE")
print("="*80)

check = fitz.open(str(OUTPUT_FILE))
size_mb = os.path.getsize(OUTPUT_FILE) / (1024 * 1024)

print(f"\n=== RESULTAT FINAL ===")
print(f"  Fichier: {OUTPUT_FILE.name}")
print(f"  Pages: {len(check)}")
print(f"  Taille: {size_mb:.1f} MB")
print(f"  Format: {check[0].rect.width:.2f} x {check[0].rect.height:.2f} pt")

# Verifications detaillees
print(f"\n=== VERIFICATIONS POST-ASSEMBLAGE ===")

# 1. Nombre de pages
if len(check) == 296:
    print(f"  [OK] Nombre de pages: {len(check)} (attendu: 296)")
else:
    print(f"  [ERREUR] Nombre de pages: {len(check)} (attendu: 296)")

# 2. Taille du fichier
if 150 <= size_mb <= 300:
    print(f"  [OK] Taille du fichier: {size_mb:.1f} MB (normal: 150-300 MB)")
elif size_mb > 500:
    print(f"  [ATTENTION] Taille du fichier: {size_mb:.1f} MB (trop gros, images non compressees?)")
else:
    print(f"  [INFO] Taille du fichier: {size_mb:.1f} MB")

# 3. Premiere page
try:
    page1_text = check[0].get_text().upper()
    if "LUMIERES" in page1_text or "TORAH" in page1_text:
        print(f"  [OK] Premiere page: contient 'Lumieres' ou 'Torah'")
    else:
        print(f"  [ATTENTION] Premiere page: ne contient pas 'Lumieres' ou 'Torah'")
except:
    print(f"  [INFO] Premiere page: verification du texte impossible")

# 4. Derniere page
try:
    derniere_page = check[len(check)-1]
    derniere_text = derniere_page.get_text().upper()
    if "NOTES" in derniere_text or "PERSONNELLES" in derniere_text:
        print(f"  [OK] Derniere page: contient 'NOTES' ou 'PERSONNELLES'")
    else:
        print(f"  [ATTENTION] Derniere page: ne contient pas 'NOTES PERSONNELLES'")
except:
    print(f"  [INFO] Derniere page: verification du texte impossible")

# 5. Page 290 (mentions legales)
if len(check) >= 290:
    try:
        page290_text = check[289].get_text().upper()  # Index 0-based
        if "MENTIONS" in page290_text or "DROITS" in page290_text or "RESERVES" in page290_text:
            print(f"  [OK] Page 290: contient 'mentions legales' ou 'droits reserves'")
        else:
            print(f"  [ATTENTION] Page 290: ne contient pas 'mentions legales'")
    except:
        print(f"  [INFO] Page 290: verification du texte impossible")
else:
    print(f"  [INFO] Page 290: non disponible (seulement {len(check)} pages)")

# 6. Dimensions uniformes
dimensions_ok = True
for i in range(min(10, len(check))):  # Verifier les 10 premieres
    w, h = round(check[i].rect.width, 2), round(check[i].rect.height, 2)
    if abs(w - 453.54) > 1 or abs(h - 623.62) > 1:
        dimensions_ok = False
        print(f"  [ERREUR] Page {i+1}: {w} x {h} (attendu 453.54 x 623.62)")
        break

# Verifier aussi quelques pages du milieu et de la fin
if len(check) > 20:
    for i in [len(check)//2, len(check)-1]:
        w, h = round(check[i].rect.width, 2), round(check[i].rect.height, 2)
        if abs(w - 453.54) > 1 or abs(h - 623.62) > 1:
            dimensions_ok = False
            print(f"  [ERREUR] Page {i+1}: {w} x {h} (attendu 453.54 x 623.62)")
            break

if dimensions_ok:
    print(f"  [OK] Dimensions uniformes: toutes les pages verifiees sont a 453.54 x 623.62 pt")

print("\n" + "="*80)
if len(check) == 296 and dimensions_ok:
    print("ASSEMBLAGE REUSSI: Le PDF est pret pour l'envoi a l'imprimeur!")
else:
    print("ATTENTION: Des problemes ont ete detectes. Verifiez les erreurs ci-dessus.")
print("="*80)

check.close()

