#!/usr/bin/env python3
# -*- coding: utf-8 -*-

"""
Renomme et "reclasse" (par tri alphabétique) les 296 pages selon
"Voici l'ordre complet des 296 pages.txt".

- Par défaut: DRY-RUN (n'écrit rien)
- Pour appliquer: --apply

Nommage final:
  {page:03d}__{slug}__{original_filename}

Ex:
  011__adam_harishon__001_gauche.svg
  010__titre_poeme_ch_1__intercalaire_ch01_droite.svg
  291__mentions_legales__annexe_mentions_legales.html

Le script travaille dans le dossier courant.
"""

from __future__ import annotations

import argparse
import os
import re
import sys
import unicodedata
from dataclasses import dataclass
from pathlib import Path
from typing import Dict, List, Tuple


ORDER_DEFAULT = "Voici l'ordre complet des 296 pages.txt"


@dataclass(frozen=True)
class Entry:
    page: int
    filename: str
    title: str


def slugify(s: str) -> str:
    s = s.strip().lower()
    # Remplace & et / etc.
    s = s.replace("&", " et ").replace("/", " ")
    # Normalise accents
    s = unicodedata.normalize("NFKD", s)
    s = "".join(ch for ch in s if not unicodedata.combining(ch))
    # Apostrophes -> rien
    s = s.replace("'", "").replace("’", "")
    # Tout ce qui n'est pas alphanum -> underscore
    s = re.sub(r"[^a-z0-9]+", "_", s)
    s = re.sub(r"_+", "_", s).strip("_")
    return s or "page"


def parse_order_file(text: str) -> List[Entry]:
    """
    Parse des tables Markdown type:
    | Page | Fichier | Contenu |
    | 11 | 001_gauche.svg | Adam HaRishon (gauche) |
    """
    entries: List[Entry] = []
    for line in text.splitlines():
        line = line.strip()
        if not line.startswith("|"):
            continue
        # ignore header separators
        if re.fullmatch(r"\|\s*-+\s*\|\s*-+\s*\|\s*-+\s*\|?", line):
            continue

        parts = [p.strip() for p in line.strip("|").split("|")]
        if len(parts) < 3:
            continue

        page_s, fname, title = parts[0], parts[1], parts[2]

        if not page_s.isdigit():
            continue

        page = int(page_s)
        # Nettoyage minimal
        fname = fname.strip()
        title = title.strip()
        entries.append(Entry(page=page, filename=fname, title=title))

    # Dédupe éventuelle
    # (si le fichier contient plusieurs tables, on garde l'ordre)
    # Tri par page
    entries.sort(key=lambda e: e.page)
    return entries


def build_plan(entries: List[Entry], base_dir: Path) -> Tuple[List[Tuple[Path, Path]], List[str]]:
    """
    Construit la liste (src -> dst). Retourne aussi les warnings.
    """
    warnings: List[str] = []
    seen_pages = set()
    renames: List[Tuple[Path, Path]] = []

    for e in entries:
        if e.page in seen_pages:
            warnings.append(f"Page dupliquée: {e.page}")
        seen_pages.add(e.page)

        src = base_dir / e.filename
        if not src.exists():
            warnings.append(f"Fichier manquant pour page {e.page}: {e.filename}")
            # On continue pour lister tous les manquants
            continue

        slug = slugify(e.title)
        dst_name = f"{e.page:03d}__{slug}__{e.filename}"
        dst = base_dir / dst_name

        renames.append((src, dst))

    # Vérifie nombre attendu
    if len(entries) != 296:
        warnings.append(f"Nombre d'entrées dans le fichier d'ordre = {len(entries)} (attendu 296)")
    # Vérifie pages 1..296
    missing_pages = [p for p in range(1, 297) if p not in seen_pages]
    if missing_pages:
        warnings.append(f"Pages absentes dans l'ordre: {missing_pages[:20]}{'...' if len(missing_pages)>20 else ''}")

    # Vérifie collisions de destination
    dst_counts: Dict[Path, int] = {}
    for _, dst in renames:
        dst_counts[dst] = dst_counts.get(dst, 0) + 1
    collisions = [str(p.name) for p, c in dst_counts.items() if c > 1]
    if collisions:
        warnings.append("Collisions de noms de destination (doublons) : " + ", ".join(collisions[:20]) +
                        ("..." if len(collisions) > 20 else ""))

    return renames, warnings


def two_pass_rename(renames: List[Tuple[Path, Path]], apply: bool) -> None:
    """
    Renommage en 2 passes pour éviter collisions :
    1) src -> src.__TMP__<pid>
    2) tmp -> dst
    """
    tmp_map: List[Tuple[Path, Path]] = []
    pid = os.getpid()

    # Pass 1: to temp
    for i, (src, dst) in enumerate(renames, start=1):
        tmp = src.with_name(src.name + f".__TMP__{pid}__{i}")
        tmp_map.append((tmp, dst))
        print(f"[1/2] {src.name}  ->  {tmp.name}")
        if apply:
            src.rename(tmp)

    # Pass 2: temp to final
    for i, (tmp, dst) in enumerate(tmp_map, start=1):
        print(f"[2/2] {tmp.name}  ->  {dst.name}")
        if apply:
            # sécurité: si dst existe déjà (ne devrait pas), on stop
            if dst.exists():
                raise RuntimeError(f"Destination existe déjà: {dst.name}")
            tmp.rename(dst)


def main() -> int:
    ap = argparse.ArgumentParser(description="Renommage des 296 pages selon un fichier d'ordre.")
    ap.add_argument("--order", default=ORDER_DEFAULT, help="Chemin vers le fichier d'ordre (.txt)")
    ap.add_argument("--apply", action="store_true", help="Appliquer réellement les renommages (sinon dry-run)")
    args = ap.parse_args()

    base_dir = Path.cwd()
    order_path = base_dir / args.order

    if not order_path.exists():
        print(f"ERREUR: fichier d'ordre introuvable: {order_path}", file=sys.stderr)
        return 2

    text = order_path.read_text(encoding="utf-8", errors="replace")
    entries = parse_order_file(text)

    renames, warnings = build_plan(entries, base_dir)

    # Affiche warnings
    if warnings:
        print("\n=== WARNINGS ===")
        for w in warnings:
            print(" - " + w)
        print("=== /WARNINGS ===\n")

    # Stop si trop de fichiers manquants
    missing = [w for w in warnings if w.startswith("Fichier manquant")]
    if missing:
        print("ERREUR: des fichiers sont manquants. Corrige ça puis relance.", file=sys.stderr)
        return 3

    # Affiche plan
    print(f"Plan de renommage: {len(renames)} fichiers.")
    if not args.apply:
        print("MODE DRY-RUN: aucun fichier ne sera modifié. Ajoute --apply pour exécuter.\n")

    # Exécute
    try:
        two_pass_rename(renames, apply=args.apply)
    except Exception as e:
        print(f"\nERREUR pendant le renommage: {e}", file=sys.stderr)
        return 4

    print("\nOK.")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())