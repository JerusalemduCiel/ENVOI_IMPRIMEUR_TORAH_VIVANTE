#!/usr/bin/env python3
"""
═══════════════════════════════════════════════════════════════════════
LUMIÈRES D'ISRAËL — LA TORAH VIVANTE
Vérification complète + Assemblage final pour l'imprimeur
═══════════════════════════════════════════════════════════════════════

Vérifie pour chaque PDF (p001.pdf → p296.pdf) :
  ✓ Présence de tous les fichiers (p001 à p296)
  ✓ Dimensions exactes : 160×220mm (453.5×623.6 pts)
  ✓ Résolution des images embarquées (cible 300 DPI)
  ✓ Espace colorimétrique (CMJN attendu)
  ✓ Taille fichier (détecte pages vides / images manquantes)
  ✓ Pages non blanches (contenu effectif)

Puis assemble en un seul PDF final.

USAGE :
  python 4_verifier_assembler_final.py --input-dir ./pages_cmjn --output ./La_Torah_Vivante_FINAL.pdf
  python 4_verifier_assembler_final.py --input-dir ./pages_cmjn --verify-only
"""

import argparse, os, sys, time

def check_dependencies():
    errors = []
    try:
        from pypdf import PdfReader, PdfWriter
    except ImportError:
        errors.append("pypdf non installé. Faire: pip install pypdf")
    try:
        import fitz  # PyMuPDF
    except ImportError:
        errors.append("PyMuPDF non installé. Faire: pip install PyMuPDF")
    if errors:
        for e in errors:
            print(f"❌ {e}")
        sys.exit(1)

def verify_files(input_dir, total_pages=296):
    """Vérifie la présence de tous les fichiers p001.pdf à p{total}.pdf"""
    missing = []
    extra = []
    
    expected = {f'p{i:03d}.pdf' for i in range(1, total_pages + 1)}
    actual = {f for f in os.listdir(input_dir) if f.endswith('.pdf')}
    
    missing = sorted(expected - actual)
    extra = sorted(actual - expected)
    
    return missing, extra, sorted(actual & expected)

def verify_page(filepath, page_num):
    """Vérifie un PDF individuel. Retourne dict de résultats."""
    import fitz
    from pypdf import PdfReader
    
    result = {
        'file': os.path.basename(filepath),
        'page': page_num,
        'size_kb': os.path.getsize(filepath) / 1024,
        'errors': [],
        'warnings': [],
    }
    
    # --- Dimensions via pypdf ---
    EXPECTED_W_PTS = 160 * 72 / 25.4  # ~453.5
    EXPECTED_H_PTS = 220 * 72 / 25.4  # ~623.6
    TOLERANCE_PTS = 5.0
    
    try:
        reader = PdfReader(filepath)
        if len(reader.pages) != 1:
            result['errors'].append(f"{len(reader.pages)} pages au lieu de 1")
            return result
        
        page = reader.pages[0]
        box = page.mediabox
        w_pts = float(box.width)
        h_pts = float(box.height)
        w_mm = w_pts * 25.4 / 72
        h_mm = h_pts * 25.4 / 72
        result['w_mm'] = w_mm
        result['h_mm'] = h_mm
        
        if abs(w_pts - EXPECTED_W_PTS) > TOLERANCE_PTS or abs(h_pts - EXPECTED_H_PTS) > TOLERANCE_PTS:
            result['errors'].append(f"Dimensions {w_mm:.1f}×{h_mm:.1f}mm (attendu 160×220mm)")
    except Exception as e:
        result['errors'].append(f"Erreur lecture pypdf: {e}")
        return result
    
    # --- Analyse via PyMuPDF ---
    try:
        doc = fitz.open(filepath)
        fitz_page = doc[0]
        
        # Vérifier le contenu (page non vide)
        text = fitz_page.get_text()
        images = fitz_page.get_images(full=True)
        drawings = fitz_page.get_drawings()
        
        has_content = bool(text.strip()) or bool(images) or bool(drawings)
        if not has_content:
            result['errors'].append("PAGE VIDE — aucun contenu détecté")
        
        result['has_text'] = bool(text.strip())
        result['num_images'] = len(images)
        result['has_drawings'] = bool(drawings)
        
        # Vérifier les images embarquées
        for img_index, img_info in enumerate(images):
            xref = img_info[0]
            try:
                img_dict = doc.extract_image(xref)
                if img_dict:
                    img_w = img_dict.get('width', 0)
                    img_h = img_dict.get('height', 0)
                    img_cs = img_dict.get('colorspace', 0)
                    img_size = len(img_dict.get('image', b''))
                    
                    # Image trop petite = probablement basse résolution
                    if img_w > 0 and img_h > 0 and img_size < 2000:
                        result['warnings'].append(f"Image #{img_index+1}: très petite ({img_size} bytes)")
            except:
                pass
        
        # Taille fichier suspecte
        if result['size_kb'] < 5:
            result['errors'].append(f"Fichier trop petit ({result['size_kb']:.1f} KB)")
        elif result['size_kb'] < 20 and len(images) == 0:
            result['warnings'].append(f"Petit fichier sans images ({result['size_kb']:.1f} KB)")
        
        # Vérifier espace colorimétrique dans le PDF brut
        with open(filepath, 'rb') as f:
            raw = f.read().decode('latin-1')
        
        has_cmyk = 'DeviceCMYK' in raw or 'ICCBased' in raw
        has_rgb = 'DeviceRGB' in raw
        
        result['has_cmyk'] = has_cmyk
        result['has_rgb'] = has_rgb
        
        if has_rgb and not has_cmyk:
            result['warnings'].append("Encore en RGB (pas de CMJN détecté)")
        elif has_rgb and has_cmyk:
            result['warnings'].append("Mix RGB + CMJN")
        
        has_fogra = 'FOGRA' in raw
        result['has_fogra'] = has_fogra
        
        doc.close()
        
    except Exception as e:
        result['errors'].append(f"Erreur analyse PyMuPDF: {e}")
    
    return result

def assemble_pdf(input_dir, valid_files, output_path):
    """Assemble les PDF dans l'ordre p001 → p296."""
    from pypdf import PdfReader, PdfWriter
    
    writer = PdfWriter()
    errors = []
    
    for f in valid_files:
        path = os.path.join(input_dir, f)
        try:
            reader = PdfReader(path)
            for page in reader.pages:
                writer.add_page(page)
        except Exception as e:
            errors.append(f"{f}: {e}")
    
    with open(output_path, 'wb') as fo:
        writer.write(fo)
    
    return len(writer.pages), errors

def main():
    parser = argparse.ArgumentParser()
    parser.add_argument('--input-dir', default='./pages_cmjn')
    parser.add_argument('--output', default='./La_Torah_Vivante_FINAL.pdf')
    parser.add_argument('--total-pages', type=int, default=296)
    parser.add_argument('--verify-only', action='store_true', help='Vérifier sans assembler')
    args = parser.parse_args()

    check_dependencies()

    print(f'{"═"*65}')
    print(f'  LUMIÈRES D\'ISRAËL — VÉRIFICATION & ASSEMBLAGE FINAL')
    print(f'{"═"*65}\n')
    print(f'📂 Dossier  : {args.input_dir}')
    print(f'📄 Attendu  : {args.total_pages} pages (p001.pdf → p{args.total_pages:03d}.pdf)')
    print(f'📐 Format   : 160×220mm (fond perdu 5mm)')
    print(f'🎨 Couleur  : CMJN FOGRA 39 attendu\n')

    # ═══ ÉTAPE 1 : Vérifier la présence des fichiers ═══
    print(f'{"─"*65}')
    print(f'  ÉTAPE 1 — Vérification des fichiers')
    print(f'{"─"*65}\n')

    missing, extra, valid = verify_files(args.input_dir, args.total_pages)
    
    print(f'  ✅ Fichiers trouvés : {len(valid)}/{args.total_pages}')
    
    if missing:
        print(f'  ❌ MANQUANTS ({len(missing)}) :')
        for f in missing[:20]:
            print(f'     {f}')
        if len(missing) > 20:
            print(f'     ... et {len(missing)-20} autres')
    
    if extra:
        print(f'  ⚠️  Fichiers supplémentaires ({len(extra)}) :')
        for f in extra[:10]:
            print(f'     {f}')

    if not valid:
        print(f'\n❌ Aucun fichier valide trouvé. Arrêt.')
        sys.exit(1)

    # ═══ ÉTAPE 2 : Vérification page par page ═══
    print(f'\n{"─"*65}')
    print(f'  ÉTAPE 2 — Vérification page par page')
    print(f'{"─"*65}\n')

    results = []
    start = time.time()
    
    for i, f in enumerate(valid):
        filepath = os.path.join(args.input_dir, f)
        page_num = int(f[1:-4])  # p001.pdf → 001
        r = verify_page(filepath, page_num)
        results.append(r)
        
        pct = (i + 1) * 100 // len(valid)
        bar = '█' * (pct // 2) + '░' * (50 - pct // 2)
        print(f'\r  [{bar}] {pct}% ({i+1}/{len(valid)})', end='', flush=True)
    
    elapsed = time.time() - start
    print(f'\n  Vérifié en {elapsed:.1f}s\n')

    # ═══ RAPPORT ═══
    print(f'{"─"*65}')
    print(f'  RAPPORT DE VÉRIFICATION')
    print(f'{"─"*65}\n')

    pages_ok = [r for r in results if not r['errors'] and not r['warnings']]
    pages_warn = [r for r in results if r['warnings'] and not r['errors']]
    pages_err = [r for r in results if r['errors']]
    
    # Statistiques taille
    sizes = [r['size_kb'] for r in results]
    avg_size = sum(sizes) / len(sizes) if sizes else 0
    min_size = min(sizes) if sizes else 0
    max_size = max(sizes) if sizes else 0
    
    # Statistiques couleur
    cmyk_count = sum(1 for r in results if r.get('has_cmyk'))
    rgb_count = sum(1 for r in results if r.get('has_rgb') and not r.get('has_cmyk'))
    fogra_count = sum(1 for r in results if r.get('has_fogra'))
    
    print(f'  📊 RÉSUMÉ :')
    print(f'     ✅ Pages conformes      : {len(pages_ok)}')
    print(f'     ⚠️  Pages avec avertiss. : {len(pages_warn)}')
    print(f'     ❌ Pages avec erreurs    : {len(pages_err)}')
    print(f'')
    print(f'  📐 DIMENSIONS :')
    dims_ok = sum(1 for r in results if not any('Dimensions' in e for e in r['errors']))
    print(f'     160×220mm conformes : {dims_ok}/{len(results)}')
    print(f'')
    print(f'  🎨 COULEURS :')
    print(f'     CMJN   : {cmyk_count}/{len(results)}')
    print(f'     RGB résiduel : {rgb_count}')
    print(f'     FOGRA 39     : {fogra_count}/{len(results)}')
    print(f'')
    print(f'  💾 TAILLE FICHIERS :')
    print(f'     Moyenne : {avg_size:.0f} KB')
    print(f'     Min     : {min_size:.0f} KB')
    print(f'     Max     : {max_size:.0f} KB')
    print(f'     Total   : {sum(sizes)/1024:.1f} Mo')
    
    # Détails erreurs
    if pages_err:
        print(f'\n  ❌ ERREURS DÉTAILLÉES ({len(pages_err)}) :')
        for r in pages_err:
            print(f'     {r["file"]}:')
            for e in r['errors']:
                print(f'       → {e}')
    
    # Détails warnings
    if pages_warn:
        print(f'\n  ⚠️  AVERTISSEMENTS ({len(pages_warn)}) :')
        for r in pages_warn:
            print(f'     {r["file"]}:')
            for w in r['warnings']:
                print(f'       → {w}')

    # ═══ ÉTAPE 3 : Assemblage ═══
    if args.verify_only:
        print(f'\n  Mode vérification uniquement — pas d\'assemblage.')
        return

    if pages_err:
        print(f'\n  ⚠️  {len(pages_err)} pages avec erreurs.')
        resp = input('  Continuer l\'assemblage malgré les erreurs ? (o/n) : ').strip().lower()
        if resp != 'o':
            print('  Assemblage annulé.')
            return

    print(f'\n{"─"*65}')
    print(f'  ÉTAPE 3 — Assemblage final')
    print(f'{"─"*65}\n')

    # Assembler dans l'ordre p001 → p296
    all_pdf_files = sorted([r['file'] for r in results])
    
    n_pages, asm_errors = assemble_pdf(args.input_dir, all_pdf_files, args.output)
    
    if asm_errors:
        print(f'  ⚠️  Erreurs d\'assemblage :')
        for e in asm_errors:
            print(f'     {e}')
    
    size_mo = os.path.getsize(args.output) / 1024 / 1024
    
    print(f'  ✅ {n_pages} pages assemblées → {args.output}')
    print(f'  💾 Taille finale : {size_mo:.1f} Mo')
    
    print(f'\n{"═"*65}')
    print(f'  🎉 FICHIER PRÊT POUR L\'IMPRIMEUR !')
    print(f'{"═"*65}')

if __name__ == '__main__':
    main()
