#!/usr/bin/env python3
"""
main.py — Interface CLI pour le scraper de conventions collectives Elnet

Usage:
    python main.py --all                        # Scraper toutes les conventions
    python main.py --id Y5079                   # Scraper une seule convention
    python main.py --range 0 10                 # Scraper les conventions[0:10]
    python main.py --id Y5079 --no-headless     # Mode visible (débogage)
"""

import argparse
import json
import logging
import os
import sys
from dotenv import load_dotenv

from elnet_connector import ElnetConnector
from elnet_scraper import ElnetScraper

# ──────────────────────────────────────────────────────────────
# LOGGING
# ──────────────────────────────────────────────────────────────

logging.basicConfig(
    level=logging.INFO,
    format="%(asctime)s [%(levelname)s] %(message)s",
    handlers=[
        logging.StreamHandler(sys.stdout),
        logging.FileHandler("scraper.log", encoding="utf-8"),
    ],
)
logger = logging.getLogger(__name__)


# ──────────────────────────────────────────────────────────────
# CHARGEMENT DE LA LISTE DES CONVENTIONS
# ──────────────────────────────────────────────────────────────

def load_conventions(path: str = "conventions_list.json") -> list:
    with open(path, "r", encoding="utf-8") as f:
        return json.load(f)


# ──────────────────────────────────────────────────────────────
# POINT D'ENTRÉE
# ──────────────────────────────────────────────────────────────

def main():
    load_dotenv()

    parser = argparse.ArgumentParser(
        description="Scraper de conventions collectives Elnet"
    )
    group = parser.add_mutually_exclusive_group(required=True)
    group.add_argument(
        "--all",
        action="store_true",
        help="Scraper toutes les conventions",
    )
    group.add_argument(
        "--id",
        type=str,
        metavar="ELNET_ID",
        help="Scraper une convention par son ID (ex: Y5079)",
    )
    group.add_argument(
        "--range",
        nargs=2,
        type=int,
        metavar=("START", "END"),
        help="Scraper les conventions[START:END] (ex: --range 0 10)",
    )
    parser.add_argument(
        "--no-headless",
        action="store_true",
        default=False,
        help="Afficher le navigateur (mode debug)",
    )
    parser.add_argument(
        "--output",
        type=str,
        default="output",
        help="Dossier de sortie (défaut: output/)",
    )
    parser.add_argument(
        "--list",
        type=str,
        default="conventions_list.json",
        help="Chemin vers le fichier JSON de la liste (défaut: conventions_list.json)",
    )

    args = parser.parse_args()

    # Credentials depuis .env
    username = os.getenv("ELNET_USERNAME")
    password = os.getenv("ELNET_PASSWORD")

    if not username or not password:
        logger.error("❌ ELNET_USERNAME ou ELNET_PASSWORD manquant dans le fichier .env")
        sys.exit(1)

    # Chargement de la liste
    all_conventions = load_conventions(args.list)
    logger.info(f"✓ {len(all_conventions)} conventions chargées depuis {args.list}")

    # Sélection des conventions à scraper
    if args.all:
        to_scrape = all_conventions
        logger.info("Mode: TOUTES les conventions")
    elif args.id:
        to_scrape = [c for c in all_conventions if c["id"] == args.id]
        if not to_scrape:
            logger.error(f"❌ Aucune convention avec l'ID '{args.id}' trouvée dans {args.list}")
            sys.exit(1)
        logger.info(f"Mode: convention unique → {args.id}")
    elif args.range:
        start, end = args.range
        to_scrape = all_conventions[start:end]
        logger.info(f"Mode: plage [{start}:{end}] → {len(to_scrape)} conventions")

    logger.info(f"Conventions à traiter : {len(to_scrape)}")

    # Connexion
    headless = not args.no_headless
    connector = ElnetConnector(username=username, password=password, headless=headless)
    connector.setup_driver()

    try:
        logger.info("🔐 Connexion à Elnet...")
        if not connector.login():
            logger.error("❌ Échec de la connexion. Arrêt.")
            sys.exit(1)
        logger.info("✅ Connexion réussie !")

        scraper = ElnetScraper(connector=connector, output_dir=args.output)

        success = 0
        skipped = 0
        errors = 0

        for i, convention in enumerate(to_scrape, 1):
            logger.info(f"\n[{i}/{len(to_scrape)}] {convention['name']} ({convention['id']})")

            try:
                result = scraper.scrape_convention(convention)
                if result is None:
                    skipped += 1
                else:
                    success += 1
            except Exception as e:
                logger.error(f"❌ Erreur inattendue pour {convention['id']}: {e}")
                errors += 1

        logger.info(f"\n{'='*60}")
        logger.info(f"✅ Réussis : {success}")
        logger.info(f"⏭  Ignorés (déjà extraits) : {skipped}")
        logger.info(f"❌ Erreurs : {errors}")
        logger.info(f"{'='*60}")

    finally:
        connector.close()


if __name__ == "__main__":
    main()
