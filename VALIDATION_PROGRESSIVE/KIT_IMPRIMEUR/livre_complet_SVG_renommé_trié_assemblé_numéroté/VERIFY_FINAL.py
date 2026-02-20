#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
🔍 VÉRIFICATION FINALE - Simple et rapide
Vérifie que les corrections ont marché
"""

from pathlib import Path

print("\n" + "=" * 80)
print("🔍 VÉRIFICATION FINALE")
print("=" * 80)

directory = Path('.')

# ════════════════════════════════════════════════════════════════
# VÉRIFIER LES 13 PAGES
# ════════════════════════════════════════════════════════════════

print("\n📄 VÉRIFICATION: 13 pages manquantes")
print("-" * 80)

PAGES_HTML = [
    ('001__page_de_titre__annexe_p1_titre.html', 1),
    ('002__a_propos__annexe_p2_apropos.html', 2),
    ('003__identite__annexe_p2_identite.html', 3),
    ('004__avant_propos__annexe_p3_avantpropos.html', 4),
    ('005__pourquoi_ce_livre_1__annexe_pourquoi_p1.html', 5),
    ('006__pourquoi_ce_livre_2__annexe_pourquoi_p2.html', 6),
    ('291__mentions_legales__annexe_mentions_legales.html', 291),
    ('292__notes_personnelles_1_5__annexe_notes_p1.html', 292),
    ('293__notes_personnelles_2_5__annexe_notes_p2.html', 293),
    ('294__notes_personnelles_3_5__annexe_notes_p3.html', 294),
    ('295__notes_personnelles_4_5__annexe_notes_p4.html', 295),
    ('296__notes_personnelles_5_5__annexe_notes_p5.html', 296),
]

PAGES_SVG = [
    ('079__osee_hoshea_gauche__030_gauche.svg', 79),
]

pages_ok = 0

for filename, page_num in PAGES_HTML:
    filepath = directory / filename
    if not filepath.exists():
        print(f"  ❌ {filename}: FICHIER MANQUANT")
        continue
    
    with open(filepath, 'r', encoding='utf-8') as f:
        content = f.read()
    
    if f'>{page_num}<' in content:
        print(f"  ✅ Page {page_num:3d}")
        pages_ok += 1
    else:
        print(f"  ❌ Page {page_num:3d}: NUMÉRO NON TROUVÉ")

for filename, page_num in PAGES_SVG:
    filepath = directory / filename
    if not filepath.exists():
        print(f"  ❌ {filename}: FICHIER MANQUANT")
        continue
    
    with open(filepath, 'r', encoding='utf-8') as f:
        content = f.read()
    
    if f'>{page_num}<' in content:
        print(f"  ✅ Page {page_num:3d}")
        pages_ok += 1
    else:
        print(f"  ❌ Page {page_num:3d}: NUMÉRO NON TROUVÉ")

print(f"\nRésultat: {pages_ok}/13 ✅")

# ════════════════════════════════════════════════════════════════
# VÉRIFIER LES 19 FICHES
# ════════════════════════════════════════════════════════════════

print("\n🏷️  VÉRIFICATION: 19 fiches décalées")
print("-" * 80)

FICHES_CORRECTIONS = [
    ('079__osee_hoshea_gauche__030_gauche.svg', 30, '30 / 118'),
    ('195__ralbag_gersonide_gauche__081_gauche.svg', 81, '81 / 118'),
    ('197__meiri_gauche__082_gauche.svg', 82, '82 / 118'),
    ('203__yossef_karo_gauche__085_gauche.svg', 85, '85 / 118'),
    ('205__rama_gauche__086_gauche.svg', 86, '86 / 118'),
    ('219__ramak_gauche__091_gauche.svg', 91, '91 / 118'),
    ('221__ari_zal_gauche__092_gauche.svg', 92, '92 / 118'),
    ('225__or_hahaim_hakadosh_gauche__094_gauche.svg', 94, '94 / 118'),
    ('239__nahman_de_breslev_gauche__100_gauche.svg', 100, '100 / 118'),
    ('241__shneur_zalman_de_liadi_gauche__101_gauche.svg', 101, '101 / 118'),
    ('243__le_rabbi_de_loubavitch_gauche__102_gauche.svg', 102, '102 / 118'),
    ('247__gaon_de_vilna_gauche__103_gauche.svg', 103, '103 / 118'),
    ('249__haim_de_volozhin_gauche__104_gauche.svg', 104, '104 / 118'),
    ('251__yisrael_salanter_gauche__105_gauche.svg', 105, '105 / 118'),
    ('253__hafets_haim_gauche__106_gauche.svg', 106, '106 / 118'),
    ('261__rav_a_y_kook_gauche__109_gauche.svg', 109, '109 / 118'),
    ('263__hazon_ish_gauche__110_gauche.svg', 110, '110 / 118'),
    ('265__sarah_schenirer_gauche__111_gauche.svg', 111, '111 / 118'),
    ('269__moshe_feinstein_gauche__113_gauche.svg', 113, '113 / 118'),
]

fiches_ok = 0

for filename, fiche_num, marker in FICHES_CORRECTIONS:
    filepath = directory / filename
    if not filepath.exists():
        print(f"  ❌ Fiche {fiche_num}: FICHIER MANQUANT")
        continue
    
    with open(filepath, 'r', encoding='utf-8') as f:
        content = f.read()
    
    if marker in content:
        print(f"  ✅ Fiche {fiche_num}/118")
        fiches_ok += 1
    else:
        print(f"  ❌ Fiche {fiche_num}/118: MARQUEUR NON TROUVÉ")

print(f"\nRésultat: {fiches_ok}/19 ✅")

# ════════════════════════════════════════════════════════════════
# RÉSUMÉ FINAL
# ════════════════════════════════════════════════════════════════

print("\n" + "=" * 80)
print("📊 RÉSUMÉ FINAL")
print("=" * 80)

print(f"\n✅ Pages: {pages_ok}/13")
print(f"✅ Fiches: {fiches_ok}/19")

print("\n" + "=" * 80)
if pages_ok == 13 and fiches_ok == 19:
    print("✅ ✅ ✅  VÉRIFICATION RÉUSSIE!  ✅ ✅ ✅")
    print("\n🎉 LE LIVRE EST 100% PRÊT POUR L'IMPRESSION!")
else:
    print(f"⚠️  Vérification partielle: {pages_ok + fiches_ok}/32")

print("=" * 80 + "\n")
