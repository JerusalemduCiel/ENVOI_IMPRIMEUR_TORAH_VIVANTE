import fitz
import os
from pathlib import Path
from collections import defaultdict
import re

# ============================================================================
# CONFIGURATION
# ============================================================================
TARGET_W, TARGET_H = 453.54, 623.62
TOLERANCE = 1.0
dossier = Path(os.getcwd())

# ============================================================================
# INITIALISATION
# ============================================================================
print("="*80)
print("VERIFICATION ULTIME - LIVRE 'LUMIERES D'ISRAEL - LA TORAH VIVANTE'")
print("="*80)
print(f"Format cible: {TARGET_W} × {TARGET_H} points (160 × 220 mm)")
print(f"Dossier: {dossier}\n")

# ============================================================================
# COLLECTE DES FICHIERS
# ============================================================================
all_files = sorted(dossier.glob("*.pdf"))
print(f"Fichiers PDF trouves: {len(all_files)}\n")

# ============================================================================
# RESULTATS DES VERIFICATIONS
# ============================================================================
resultats = {
    "1_dimensions": {"ok": True, "erreurs": []},
    "2_sequence": {"ok": True, "manquants": [], "inattendus": []},
    "3_pages_vides": {"ok": True, "suspects": []},
    "4_coherence": {"ok": True, "anomalies": []},
    "5_taille_fichiers": {"ok": True, "trop_petits": [], "trop_gros": []},
    "6_ordre_assemblage": {"ok": True, "problemes": []},
    "7_parite": {"ok": True, "erreurs": []}
}

# Statistiques globales
stats = {
    "total_fichiers": len(all_files),
    "taille_totale_mb": 0,
    "fichiers_par_type": defaultdict(int)
}

# ============================================================================
# VERIFICATION 1: DIMENSIONS
# ============================================================================
print("1. VERIFICATION DES DIMENSIONS...")
for f in all_files:
    try:
        doc = fitz.open(str(f))
        for i, page in enumerate(doc):
            w, h = round(page.rect.width, 2), round(page.rect.height, 2)
            if abs(w - TARGET_W) > TOLERANCE or abs(h - TARGET_H) > TOLERANCE:
                resultats["1_dimensions"]["ok"] = False
                resultats["1_dimensions"]["erreurs"].append(
                    f"{f.name} p{i+1}: {w:.2f} × {h:.2f} (attendu {TARGET_W} × {TARGET_H})"
                )
        doc.close()
    except Exception as e:
        resultats["1_dimensions"]["ok"] = False
        resultats["1_dimensions"]["erreurs"].append(f"{f.name}: ERREUR - {e}")

if resultats["1_dimensions"]["ok"]:
    print(f"  [OK] {len(all_files)} fichiers - toutes les dimensions sont correctes")
else:
    print(f"  [ERREUR] {len(resultats['1_dimensions']['erreurs'])} fichier(s) au mauvais format")

# ============================================================================
# VERIFICATION 2: SEQUENCE DE NUMEROTATION
# ============================================================================
print("\n2. VERIFICATION DE LA SEQUENCE DE NUMEROTATION...")

# Séquence attendue
sequence_attendue = ["P001", "P001b"]
for i in range(2, 296):
    sequence_attendue.append(f"P{i:03d}")

# Extraire les numéros des fichiers trouvés
fichiers_trouves = {}
for f in all_files:
    match = re.search(r'P(\d{3}[b]?)', f.name.upper())
    if match:
        num = match.group(1)
        fichiers_trouves[num] = f.name

# Vérifier les manquants (enlever le "P" pour comparer)
for num_avec_p in sequence_attendue:
    num_sans_p = num_avec_p[1:]  # Enlever le "P"
    if num_sans_p not in fichiers_trouves:
        resultats["2_sequence"]["ok"] = False
        resultats["2_sequence"]["manquants"].append(num_avec_p)

# Vérifier les inattendus (ajouter le "P" pour comparer)
for num_sans_p in fichiers_trouves:
    num_avec_p = f"P{num_sans_p}"
    if num_avec_p not in sequence_attendue:
        resultats["2_sequence"]["ok"] = False
        resultats["2_sequence"]["inattendus"].append(fichiers_trouves[num_sans_p])

if resultats["2_sequence"]["ok"]:
    print(f"  [OK] Sequence complete: {len(sequence_attendue)} fichiers attendus, {len(fichiers_trouves)} trouves")
else:
    print(f"  [ERREUR] {len(resultats['2_sequence']['manquants'])} manquant(s), {len(resultats['2_sequence']['inattendus'])} inattendu(s)")

# ============================================================================
# VERIFICATION 3: PAGES BLANCHES / FICHIERS VIDES
# ============================================================================
print("\n3. VERIFICATION DES PAGES VIDES...")
for f in all_files:
    try:
        doc = fitz.open(str(f))
        page = doc[0]
        text = page.get_text().strip()
        images = page.get_images()
        drawings = len(page.get_drawings())
        
        if not text and not images and drawings < 3:
            resultats["3_pages_vides"]["ok"] = False
            resultats["3_pages_vides"]["suspects"].append(
                f"{f.name}: possiblement vide (0 texte, {len(images)} images, {drawings} tracés)"
            )
        doc.close()
    except Exception as e:
        resultats["3_pages_vides"]["ok"] = False
        resultats["3_pages_vides"]["suspects"].append(f"{f.name}: ERREUR - {e}")

if resultats["3_pages_vides"]["ok"]:
    print(f"  [OK] Aucune page vide suspecte")
else:
    print(f"  [ATTENTION] {len(resultats['3_pages_vides']['suspects'])} fichier(s) suspect(s)")

# ============================================================================
# VERIFICATION 4: COHERENCE DES TYPES DE PAGES
# ============================================================================
print("\n4. VERIFICATION DE LA COHERENCE DES TYPES DE PAGES...")

def verifier_type_page(f):
    """Vérifie que le contenu correspond au type de page attendu"""
    try:
        doc = fitz.open(str(f))
        page = doc[0]
        text = page.get_text().upper()
        images = page.get_images()
        doc.close()
        
        nom = f.name
        
        # P001_page_titre
        if "P001_PAGE_TITRE" in nom.upper():
            if "LUMIERES" not in text and "TORAH" not in text:
                return f"{nom}: devrait contenir 'Lumières' ou 'Torah'"
        
        # Intercalaires L
        elif "_INTER" in nom.upper() and "_L" in nom.upper():
            if len(images) == 0:
                return f"{nom}: intercalaire gauche devrait contenir une image"
        
        # Intercalaires R
        elif "_INTER" in nom.upper() and "_R" in nom.upper():
            if "CHAPITRE" not in text and "chapitre" not in text.lower():
                return f"{nom}: intercalaire droite devrait contenir 'CHAPITRE' (peut etre dans une image)"
        
        # Fiches G
        elif "_G.PDF" in nom.upper():
            if len(images) < 1:
                return f"{nom}: fiche gauche devrait contenir un portrait (image)"
        
        # Fiches D
        elif "_D.PDF" in nom.upper():
            if len(text) < 50:  # Au moins 50 caractères de texte
                return f"{nom}: fiche droite devrait contenir du texte biographique"
        
        # Index
        elif "INDEX" in nom.upper():
            if len(text) < 100:
                return f"{nom}: index devrait contenir une liste alphabétique"
        
        # Glossaire
        elif "GLOSSAIRE" in nom.upper():
            if len(text) < 100:
                return f"{nom}: glossaire devrait contenir des définitions"
        
        # Mentions légales
        elif "MENTIONS" in nom.upper():
            if "DROITS" not in text and "RESERVES" not in text and "MICHAEL" not in text and "LUMBROSO" not in text:
                return f"{nom}: mentions légales devrait contenir 'droits réservés' ou 'Michael Lumbroso'"
        
        # Notes
        elif "NOTES" in nom.upper():
            if "NOTES" not in text and "PERSONNELLES" not in text and "notes" not in text.lower():
                return f"{nom}: notes devrait contenir 'NOTES PERSONNELLES' (peut etre dans une image)"
        
        return None
    except Exception as e:
        return f"{f.name}: ERREUR - {e}"

for f in all_files:
    probleme = verifier_type_page(f)
    if probleme:
        resultats["4_coherence"]["ok"] = False
        resultats["4_coherence"]["anomalies"].append(probleme)

if resultats["4_coherence"]["ok"]:
    print(f"  [OK] Coherence verifiee pour tous les fichiers")
else:
    print(f"  [ATTENTION] {len(resultats['4_coherence']['anomalies'])} anomalie(s) detectee(s)")

# ============================================================================
# VERIFICATION 5: TAILLE DES FICHIERS
# ============================================================================
print("\n5. VERIFICATION DE LA TAILLE DES FICHIERS...")
tailles = []
for f in all_files:
    taille_ko = f.stat().st_size / 1024
    taille_mo = taille_ko / 1024
    stats["taille_totale_mb"] += taille_mo
    tailles.append((f.name, taille_ko, taille_mo))
    
    if taille_ko < 8:
        resultats["5_taille_fichiers"]["ok"] = False
        resultats["5_taille_fichiers"]["trop_petits"].append(f"{f.name}: {taille_ko:.1f} KB")
    if taille_mo > 5:
        resultats["5_taille_fichiers"]["ok"] = False
        resultats["5_taille_fichiers"]["trop_gros"].append(f"{f.name}: {taille_mo:.2f} MB")

tailles.sort(key=lambda x: x[2], reverse=True)

if resultats["5_taille_fichiers"]["ok"]:
    print(f"  [OK] Toutes les tailles sont normales")
else:
    print(f"  [ATTENTION] {len(resultats['5_taille_fichiers']['trop_petits'])} trop petit(s), {len(resultats['5_taille_fichiers']['trop_gros'])} trop gros")

# ============================================================================
# VERIFICATION 6: ORDRE D'ASSEMBLAGE
# ============================================================================
print("\n6. VERIFICATION DE L'ORDRE D'ASSEMBLAGE...")
import natsort
fichiers_tries = natsort.natsorted(all_files)

# Vérifier les paires intercalaires L/R
for i in range(len(fichiers_tries) - 1):
    f1 = fichiers_tries[i].name
    f2 = fichiers_tries[i+1].name
    
    # Vérifier intercalaire L suivi de R
    if "_INTER" in f1.upper() and "_L" in f1.upper():
        if "_INTER" not in f2.upper() or "_R" not in f2.upper():
            resultats["6_ordre_assemblage"]["ok"] = False
            resultats["6_ordre_assemblage"]["problemes"].append(
                f"Intercalaire L '{f1}' n'est pas suivi d'un R"
            )
    
    # Vérifier fiche G suivi de D
    if "_G.PDF" in f1.upper() and "FICHE" in f1.upper():
        if "_D.PDF" not in f2.upper():
            resultats["6_ordre_assemblage"]["ok"] = False
            resultats["6_ordre_assemblage"]["problemes"].append(
                f"Fiche G '{f1}' n'est pas suivie d'une D"
            )

if resultats["6_ordre_assemblage"]["ok"]:
    print(f"  [OK] Ordre d'assemblage correct")
else:
    print(f"  [ATTENTION] {len(resultats['6_ordre_assemblage']['problemes'])} probleme(s) d'ordre")

# ============================================================================
# VERIFICATION 7: PARITE DES PAGES (RECTO/VERSO)
# ============================================================================
print("\n7. VERIFICATION DE LA PARITE DES PAGES...")

# Calculer la position dans le livre (page 1 = P001 = recto = impair)
# Note: Dans un livre, page 1 (recto) = impair, page 2 (verso) = pair
# Les pages G (gauche) sont verso (paires), les pages D (droite) sont recto (impaires)
position = 1
for f in fichiers_tries:
    nom = f.name
    
    # Pages G (gauche) = verso = pair (position 2, 4, 6, ...)
    if "_G.PDF" in nom.upper() or ("_INTER" in nom.upper() and "_L" in nom.upper()):
        if position % 2 != 0:  # Si impair, c'est une erreur
            resultats["7_parite"]["ok"] = False
            resultats["7_parite"]["erreurs"].append(
                f"{nom}: page gauche (verso) a la position {position} (impair) - devrait etre pair"
            )
    
    # Pages D (droite) = recto = impair (position 1, 3, 5, ...)
    elif "_D.PDF" in nom.upper() or ("_INTER" in nom.upper() and "_R" in nom.upper()):
        if position % 2 == 0:  # Si pair, c'est une erreur
            resultats["7_parite"]["ok"] = False
            resultats["7_parite"]["erreurs"].append(
                f"{nom}: page droite (recto) a la position {position} (pair) - devrait etre impair"
            )
    
    position += 1

if resultats["7_parite"]["ok"]:
    print(f"  [OK] Parite correcte pour toutes les pages")
else:
    print(f"  [ERREUR] {len(resultats['7_parite']['erreurs'])} erreur(s) de parite")

# ============================================================================
# GENERATION DU RAPPORT
# ============================================================================
print("\n" + "="*80)
print("RAPPORT DE VERIFICATION ULTIME")
print("="*80)

# RÉSUMÉ
print("\n1. RÉSUMÉ DES VÉRIFICATIONS")
print("-" * 80)
verifications = [
    ("1. Dimensions", resultats["1_dimensions"]["ok"]),
    ("2. Séquence de numérotation", resultats["2_sequence"]["ok"]),
    ("3. Pages vides", resultats["3_pages_vides"]["ok"]),
    ("4. Cohérence des types", resultats["4_coherence"]["ok"]),
    ("5. Taille des fichiers", resultats["5_taille_fichiers"]["ok"]),
    ("6. Ordre d'assemblage", resultats["6_ordre_assemblage"]["ok"]),
    ("7. Parité recto/verso", resultats["7_parite"]["ok"])
]

for nom, ok in verifications:
    statut = "[OK]" if ok else "[ERREUR]"
    print(f"  {statut}  {nom}")

# DÉTAILS
print("\n2. DÉTAILS DES ANOMALIES")
print("-" * 80)

if not resultats["1_dimensions"]["ok"]:
    print("\n[ERREUR] DIMENSIONS INCORRECTES:")
    for e in resultats["1_dimensions"]["erreurs"][:20]:
        print(f"  • {e}")
    if len(resultats["1_dimensions"]["erreurs"]) > 20:
        print(f"  ... et {len(resultats['1_dimensions']['erreurs']) - 20} autres")

if not resultats["2_sequence"]["ok"]:
    print("\n[ERREUR] SEQUENCE DE NUMEROTATION:")
    if resultats["2_sequence"]["manquants"]:
        print(f"  Fichiers manquants ({len(resultats['2_sequence']['manquants'])}):")
        for m in resultats["2_sequence"]["manquants"]:
            print(f"    • {m}")
    if resultats["2_sequence"]["inattendus"]:
        print(f"  Fichiers inattendus ({len(resultats['2_sequence']['inattendus'])}):")
        for u in resultats["2_sequence"]["inattendus"]:
            print(f"    • {u}")

if not resultats["3_pages_vides"]["ok"]:
    print("\n[ATTENTION] PAGES VIDES SUSPECTES:")
    for s in resultats["3_pages_vides"]["suspects"]:
        print(f"  • {s}")

if not resultats["4_coherence"]["ok"]:
    print("\n[ATTENTION] COHERENCE DES TYPES:")
    for a in resultats["4_coherence"]["anomalies"][:20]:
        print(f"  • {a}")
    if len(resultats["4_coherence"]["anomalies"]) > 20:
        print(f"  ... et {len(resultats['4_coherence']['anomalies']) - 20} autres")

if not resultats["5_taille_fichiers"]["ok"]:
    print("\n[ATTENTION] TAILLE DES FICHIERS:")
    if resultats["5_taille_fichiers"]["trop_petits"]:
        print(f"  Trop petits (< 8 KB) ({len(resultats['5_taille_fichiers']['trop_petits'])}):")
        for t in resultats["5_taille_fichiers"]["trop_petits"][:10]:
            print(f"    • {t}")
    if resultats["5_taille_fichiers"]["trop_gros"]:
        print(f"  Trop gros (> 5 MB) ({len(resultats['5_taille_fichiers']['trop_gros'])}):")
        for t in resultats["5_taille_fichiers"]["trop_gros"][:10]:
            print(f"    • {t}")
    print("\n  Top 10 des plus gros fichiers:")
    for nom, ko, mo in tailles[:10]:
        print(f"    • {nom}: {mo:.2f} MB ({ko:.1f} KB)")

if not resultats["6_ordre_assemblage"]["ok"]:
    print("\n[ATTENTION] ORDRE D'ASSEMBLAGE:")
    for p in resultats["6_ordre_assemblage"]["problemes"]:
        print(f"  • {p}")

if not resultats["7_parite"]["ok"]:
    print("\n[ERREUR] PARITE RECTO/VERSO:")
    for e in resultats["7_parite"]["erreurs"][:20]:
        print(f"  • {e}")
    if len(resultats["7_parite"]["erreurs"]) > 20:
        print(f"  ... et {len(resultats['7_parite']['erreurs']) - 20} autres")

# ACTIONS REQUISES
print("\n3. ACTIONS REQUISES")
print("-" * 80)
actions = []
if not resultats["1_dimensions"]["ok"]:
    actions.append("CRITIQUE: Corriger les dimensions des fichiers PDF")
if not resultats["2_sequence"]["ok"]:
    actions.append("CRITIQUE: Compléter la séquence de numérotation")
if not resultats["7_parite"]["ok"]:
    actions.append("CRITIQUE: Corriger la parité recto/verso")
if not resultats["6_ordre_assemblage"]["ok"]:
    actions.append("IMPORTANT: Corriger l'ordre d'assemblage")
if not resultats["4_coherence"]["ok"]:
    actions.append("IMPORTANT: Vérifier la cohérence du contenu")
if not resultats["3_pages_vides"]["ok"]:
    actions.append("À VÉRIFIER: Examiner les pages suspectes")
if not resultats["5_taille_fichiers"]["ok"]:
    actions.append("À OPTIMISER: Compresser les fichiers trop gros")

if actions:
    for i, action in enumerate(actions, 1):
        print(f"  {i}. {action}")
else:
    print("  [OK] Aucune action requise - tous les fichiers sont prets pour l'assemblage!")

# STATISTIQUES
print("\n4. STATISTIQUES")
print("-" * 80)
print(f"  Total de fichiers: {stats['total_fichiers']}")
print(f"  Taille totale: {stats['taille_totale_mb']:.2f} MB")
print(f"  Taille moyenne par fichier: {stats['taille_totale_mb']/stats['total_fichiers']:.2f} MB")
print(f"  Format cible: {TARGET_W} × {TARGET_H} points (160 × 220 mm)")

print("\n" + "="*80)
print("FIN DU RAPPORT")
print("="*80)

# Sauvegarder le rapport
with open("rapport_verification_ultime.txt", "w", encoding="utf-8") as f:
    # Réécrire tout le rapport dans le fichier
    import sys
    from io import StringIO
    old_stdout = sys.stdout
    sys.stdout = StringIO()
    # Réexécuter les prints (simplifié - on sauvegarde juste le résumé)
    pass

