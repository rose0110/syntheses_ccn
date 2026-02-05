import os
import json
import logging
import argparse
from pathlib import Path
from datetime import datetime
from dotenv import load_dotenv
from reformulation.reformulator import Reformulator

logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s - %(levelname)s - %(message)s'
)
logger = logging.getLogger(__name__)

load_dotenv()


def load_extractions(extractions_dir: str):
    """Charge toutes les extractions"""
    path = Path(extractions_dir)
    
    if not path.exists():
        logger.error(f"Directory not found: {extractions_dir}")
        return []
    
    json_files = sorted(path.glob("convention_*.json"))
    
    if not json_files:
        logger.warning(f"No convention files found")
        return []
    
    conventions = []
    
    for file_path in json_files:
        try:
            with open(file_path, 'r', encoding='utf-8') as f:
                data = json.load(f)
                conventions.append(data)
        except Exception as e:
            logger.error(f"Failed to load {file_path.name}: {e}")
    
    logger.info(f"Loaded {len(conventions)} conventions")
    return conventions


def load_existing_results(output_file: str):
    """Charge résultats existants pour reprise"""
    if not Path(output_file).exists():
        return []
    
    try:
        with open(output_file, 'r', encoding='utf-8') as f:
            data = json.load(f)
            logger.info(f"Found {len(data)} existing results")
            return data
    except Exception as e:
        logger.warning(f"Could not load existing results: {e}")
        return []


def save_results(results: list, output_file: str):
    """Sauvegarde résultats"""
    try:
        path = Path(output_file)
        path.parent.mkdir(parents=True, exist_ok=True)
        
        with open(path, 'w', encoding='utf-8') as f:
            json.dump(results, f, ensure_ascii=False, indent=2)
        
    except Exception as e:
        logger.error(f"Save failed: {e}")


def main():
    parser = argparse.ArgumentParser(description='Reformulation de conventions collectives')
    parser.add_argument('--id', type=int, help='Reformuler une seule convention par son indice')
    parser.add_argument('--start', type=int, help='Indice de début (inclus)')
    parser.add_argument('--end', type=int, help='Indice de fin (exclus)')
    parser.add_argument('--force', action='store_true', help='Reformuler même si déjà traité')
    
    args = parser.parse_args()
    
    api_key = os.getenv("DEEPSEEK_API_KEY")
    
    if not api_key:
        logger.error("DEEPSEEK_API_KEY not found in .env")
        return
    
    extractions_dir = "extractions"
    output_file = "data/reformulations.json"
    
    start_time = datetime.now()
    logger.info("=" * 60)
    logger.info("REFORMULATION - VERSION OPTIMISÉE")
    logger.info("=" * 60)
    
    # Charger extractions
    conventions = load_extractions(extractions_dir)
    
    if not conventions:
        logger.error("No conventions to process")
        return
    
    # Filtrer par indices
    if args.id is not None:
        if 0 <= args.id < len(conventions):
            conventions = [conventions[args.id]]
            logger.info(f"Mode: Convention unique (indice {args.id})")
        else:
            logger.error(f"Indice {args.id} hors limite (0-{len(conventions)-1})")
            return
    elif args.start is not None or args.end is not None:
        start_idx = args.start if args.start is not None else 0
        end_idx = args.end if args.end is not None else len(conventions)
        conventions = conventions[start_idx:end_idx]
        logger.info(f"Mode: Range [{start_idx}:{end_idx}]")
    else:
        logger.info("Mode: Toutes les conventions")
    
    # Charger résultats existants
    existing = load_existing_results(output_file)
    existing_ids = {r.get('id') for r in existing if r}
    
    # Filtrer déjà traités (sauf si --force)
    if args.force:
        to_process = conventions
        logger.info("Mode FORCE: reformulation même si déjà traité")
    else:
        to_process = [c for c in conventions if c.get('id') not in existing_ids]
    
    logger.info(f"Total conventions: {len(conventions)}")
    logger.info(f"Already processed: {len(conventions) - len(to_process)}")
    logger.info(f"Remaining: {len(to_process)}")
    
    if not to_process:
        logger.info("All conventions already processed! (use --force to reprocess)")
        return
    
    # Reformuler
    reformulator = Reformulator(api_key)
    results = existing.copy()
    success_count = 0
    error_count = 0
    
    for i, conv in enumerate(to_process, 1):
        conv_id = conv.get('id', '?')
        conv_name = conv.get('metadata', {}).get('name', 'Unknown')
        
        logger.info(f"\n[{i}/{len(to_process)}] Convention {conv_id}: {conv_name}")
        
        result = reformulator.process_convention(conv)
        
        if result:
            # Remove old version if exists
            if args.force:
                results = [r for r in results if r.get('id') != conv_id]
            
            results.append(result)
            success_count += 1
            logger.info(f"✓ Success ({success_count} total)")
        else:
            error_count += 1
            logger.warning(f"✗ Failed ({error_count} total)")
        
        # Sauvegarde tous les 3
        if i % 3 == 0:
            save_results(results, output_file)
            logger.info(f"💾 Saved checkpoint ({len(results)} conventions)")
    
    # Sauvegarde finale
    save_results(results, output_file)
    
    # Stats
    elapsed = datetime.now() - start_time
    logger.info("=" * 60)
    logger.info("TERMINÉ")
    logger.info("=" * 60)
    logger.info(f"Total traité: {len(to_process)}")
    logger.info(f"Succès: {success_count}")
    logger.info(f"Échecs: {error_count}")
    if len(to_process) > 0:
        logger.info(f"Taux succès: {success_count/(len(to_process))*100:.1f}%")
    logger.info(f"Temps écoulé: {elapsed}")
    logger.info(f"Résultats: {output_file}")


if __name__ == "__main__":
    main()


