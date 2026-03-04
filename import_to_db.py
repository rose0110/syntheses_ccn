#!/usr/bin/env python3
"""
import_to_db.py — Importe les fichiers JSON du dossier output/ dans la base SQLite
====================================================================================
Usage:
    python import_to_db.py                  # importer tout le dossier output/
    python import_to_db.py --file Y5079     # importer une seule convention
    python import_to_db.py --reset          # réinitialiser la BD avant import
    python import_to_db.py --generate-integrales  # générer les intégrales HTML
"""

import argparse
import json
import logging
import os
import sys
from pathlib import Path
from sqlalchemy.orm import Session

# Doit être dans le même dossier que database.py / models.py
import database
import models
from database import SessionLocal, engine

logging.basicConfig(
    level=logging.INFO,
    format="%(asctime)s [%(levelname)s] %(message)s",
    handlers=[logging.StreamHandler(sys.stdout)]
)
logger = logging.getLogger(__name__)

OUTPUT_DIR = Path("output")


# ──────────────────────────────────────────────────────────────
# INITIALISATION DE LA BD
# ──────────────────────────────────────────────────────────────

def init_db():
    """Crée les tables si elles n'existent pas."""
    models.Base.metadata.create_all(bind=engine)
    logger.info("✓ Tables créées (ou déjà existantes)")


def reset_db():
    """Supprime et recrée toutes les tables."""
    models.Base.metadata.drop_all(bind=engine)
    models.Base.metadata.create_all(bind=engine)
    logger.info("✓ Base de données réinitialisée")


# ──────────────────────────────────────────────────────────────
# IMPORT D'UNE CONVENTION
# ──────────────────────────────────────────────────────────────

def import_convention(data: dict, db: Session) -> bool:
    """
    Importe une convention JSON dans la BD.
    Met à jour si elle existe déjà (upsert).
    Retourne True si succès.
    """
    meta = data.get("metadata", {})
    elnet_id = meta.get("elnet_id", "")

    if not elnet_id:
        logger.warning("⚠ elnet_id manquant, convention ignorée")
        return False

    # Vérifier si la convention existe déjà
    existing = db.query(models.Convention).filter(
        models.Convention.elnet_id == elnet_id
    ).first()

    if existing:
        # Mettre à jour
        conv = existing
        logger.info(f"  ↻ Mise à jour de {elnet_id}")
    else:
        # Créer
        conv = models.Convention(elnet_id=elnet_id)
        db.add(conv)
        logger.info(f"  + Import de {elnet_id}")

    # Remplir les champs
    conv.name = meta.get("name", "")
    conv.url = meta.get("url", "")
    conv.pdf_url = meta.get("pdf_url", "")
    conv.idcc = meta.get("idcc", "")
    conv.brochure = meta.get("brochure", "")
    conv.signature_date = meta.get("signature_date", "")
    conv.extension_date = meta.get("extension_date", "")
    conv.jo_date = meta.get("jo_date", "")
    conv.revision_date = meta.get("revision_date", "")
    conv.revision_extension = meta.get("revision_extension", "")
    conv.revision_jo = meta.get("revision_jo", "")
    conv.extraction_date = meta.get("extraction_date", "")
    conv.header_table_html = data.get("header_table_html", "")
    conv.preamble_html = data.get("preamble_html", "")

    # Flush pour obtenir l'ID
    db.flush()

    # ── TOC ──
    # Supprimer les anciennes entrées TOC
    db.query(models.TocEntry).filter(
        models.TocEntry.convention_id == conv.id
    ).delete()

    for position, toc_item in enumerate(data.get("toc", [])):
        entry = models.TocEntry(
            convention_id=conv.id,
            entry_id=toc_item.get("id", ""),
            sgml_id=toc_item.get("sgml_id", ""),
            title=toc_item.get("title", ""),
            position=position,
        )
        db.add(entry)

    # ── SECTIONS ──
    # Supprimer les anciennes sections
    db.query(models.Section).filter(
        models.Section.convention_id == conv.id
    ).delete()

    preamble_html = ""
    for section in data.get("sections", []):
        sec = models.Section(
            convention_id=conv.id,
            sequence=section.get("sequence", 0),
            is_preamble=section.get("is_preamble", False),
            html=section.get("html", ""),
            text=section.get("text", ""),
        )
        db.add(sec)
        if section.get("is_preamble"):
            preamble_html = section.get("html", "")

    # Mettre à jour le préambule si manquant
    if not conv.preamble_html and preamble_html:
        conv.preamble_html = preamble_html

    return True


# ──────────────────────────────────────────────────────────────
# GÉNÉRATION DES INTÉGRALES
# ──────────────────────────────────────────────────────────────

def generate_integrales(db: Session):
    """Génère l'intégrale HTML pour toutes les conventions qui n'en ont pas encore."""
    conventions = db.query(models.Convention).all()
    generated = 0

    for conv in conventions:
        # Vérifier si l'intégrale existe déjà
        existing = db.query(models.Integrale).filter(
            models.Integrale.convention_id == conv.id
        ).first()
        if existing:
            continue

        sections = db.query(models.Section).filter(
            models.Section.convention_id == conv.id
        ).order_by(models.Section.sequence).all()

        if not sections:
            continue

        full_html = "\n".join(s.html or "" for s in sections)
        full_text = "\n".join(s.text or "" for s in sections)

        integrale = models.Integrale(
            convention_id=conv.id,
            html=full_html,
            text=full_text,
        )
        db.add(integrale)
        generated += 1
        logger.info(f"  ✓ Intégrale générée pour {conv.elnet_id}")

    db.commit()
    logger.info(f"\n✅ {generated} intégrales générées")


# ──────────────────────────────────────────────────────────────
# POINT D'ENTRÉE
# ──────────────────────────────────────────────────────────────

def main():
    parser = argparse.ArgumentParser(
        description="Import des conventions JSON dans la base de données SQLite"
    )
    parser.add_argument(
        "--file", type=str, metavar="ELNET_ID",
        help="Importer uniquement cette convention (ex: Y5079)"
    )
    parser.add_argument(
        "--reset", action="store_true",
        help="Réinitialiser la BD avant l'import"
    )
    parser.add_argument(
        "--generate-integrales", action="store_true",
        help="Générer les intégrales HTML après l'import"
    )
    parser.add_argument(
        "--output-dir", type=str, default="output",
        help="Dossier contenant les fichiers JSON (défaut: output/)"
    )
    args = parser.parse_args()

    output_dir = Path(args.output_dir)
    if not output_dir.exists():
        logger.error(f"❌ Dossier introuvable: {output_dir}")
        sys.exit(1)

    # Init / reset BD
    if args.reset:
        logger.info("⚠ Réinitialisation de la base de données...")
        reset_db()
    else:
        init_db()

    # Sélectionner les fichiers à importer
    if args.file:
        files = [output_dir / f"{args.file}.json"]
        if not files[0].exists():
            logger.error(f"❌ Fichier introuvable: {files[0]}")
            sys.exit(1)
    else:
        files = sorted(output_dir.glob("*.json"))
        # Exclure les fichiers partiels et le résumé
        files = [f for f in files if not f.stem.endswith("_partial")
                 and not f.stem.startswith("_")]

    logger.info(f"\n{'='*60}")
    logger.info(f"📦 Import de {len(files)} convention(s)")
    logger.info(f"{'='*60}\n")

    db = SessionLocal()
    success = 0
    errors = 0

    try:
        for i, filepath in enumerate(files, 1):
            logger.info(f"[{i}/{len(files)}] {filepath.stem}")
            try:
                with open(filepath, "r", encoding="utf-8") as f:
                    data = json.load(f)

                ok = import_convention(data, db)
                if ok:
                    success += 1
                else:
                    errors += 1

                # Commit par lot de 10
                if i % 10 == 0:
                    db.commit()
                    logger.info(f"  → Commit intermédiaire ({i} conventions)")

            except Exception as e:
                logger.error(f"  ❌ Erreur sur {filepath.stem}: {e}")
                db.rollback()
                errors += 1

        # Commit final
        db.commit()

        logger.info(f"\n{'='*60}")
        logger.info(f"✅ Succès : {success}")
        logger.info(f"❌ Erreurs : {errors}")

        # Générer les intégrales si demandé
        if args.generate_integrales:
            logger.info(f"\n📄 Génération des intégrales...")
            generate_integrales(db)

        logger.info(f"{'='*60}")
        logger.info(f"\n🗄 Base de données : elnet.db")

    finally:
        db.close()


if __name__ == "__main__":
    main()
