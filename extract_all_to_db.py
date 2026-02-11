import os
import json
import hashlib
import logging
from pathlib import Path
from datetime import datetime
from dotenv import load_dotenv
from sqlalchemy.orm import Session
from extraction.extractor import ConventionExtractor
from api.database import init_db, SessionLocal, Convention

logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s - %(levelname)s - %(message)s'
)
logger = logging.getLogger(__name__)

load_dotenv()


def clean_html(html_content: str) -> str:
    """Nettoie le HTML en retirant scripts, styles et attributs inutiles"""
    if not html_content:
        return html_content
    
    try:
        from bs4 import BeautifulSoup
        
        soup = BeautifulSoup(html_content, 'html.parser')
        
        # Retirer toutes les balises script
        for script in soup.find_all('script'):
            script.decompose()
        
        # Retirer toutes les balises style
        for style in soup.find_all('style'):
            style.decompose()
        
        # Retirer tous les commentaires HTML
        for comment in soup.find_all(string=lambda text: isinstance(text, type(soup))):
            comment.extract()
        
        # Attributs à supprimer (événements JS et attributs inutiles)
        unwanted_attrs = [
            'onclick', 'onload', 'onmouseover', 'onmouseout', 
            'onfocus', 'onblur', 'onchange', 'onsubmit',
            'class', 'id', 'style'  # Optionnel : supprimer aussi les classes/IDs
        ]
        
        # Parcourir tous les éléments et retirer les attributs indésirables
        for tag in soup.find_all(True):
            for attr in unwanted_attrs:
                if attr in tag.attrs:
                    del tag.attrs[attr]
        
        return str(soup)
    
    except Exception as e:
        logger.warning(f"Erreur lors du nettoyage HTML: {e}")
        return html_content  # Retourner l'original en cas d'erreur



def compute_hash(sections):
    """Calcule un hash du contenu des sections"""
    content = json.dumps(sections, sort_keys=True)
    return hashlib.sha256(content.encode()).hexdigest()


def load_conventions_list(file_path: str):
    """Charge la liste des conventions"""
    with open(file_path, 'r', encoding='utf-8') as f:
        return json.load(f)


def populate_database(conventions_list: list):
    """Remplit la base de données"""
    db = SessionLocal()
    
    try:
        for i, conv in enumerate(conventions_list):
            existing = db.query(Convention).filter(Convention.id == i).first()
            
            if not existing:
                convention = Convention(
                    id=i,
                    name=conv.get('name', ''),
                    idcc=conv.get('idcc'),
                    brochure=conv.get('brochure'),
                    url=conv.get('url', ''),
                    pdf_url=conv.get('pdf_url'),
                    signature_date=conv.get('signature_date'),
                    extension_date=conv.get('extension_date'),
                    jo_date=conv.get('jo_date'),
                    status="pending"
                )
                db.add(convention)
        
        db.commit()
        logger.info(f"Database populated with {len(conventions_list)} conventions")
        
    finally:
        db.close()


def detect_changes():
    """Détecte les conventions qui ont changé depuis la dernière extraction"""
    db = SessionLocal()
    changed_conventions = []
    
    try:
        conventions = db.query(Convention).filter(
            Convention.status.in_(["extracted", "reformulated"])
        ).all()
        
        for conv in conventions:
            # Marquer pour ré-extraction
            conv.status = "pending"
        
        db.commit()
        logger.info(f"{len(conventions)} conventions marked for re-extraction")
        
    finally:
        db.close()
    
    return changed_conventions


def extract_and_compare(start_idx: int = 0, end_idx: int = None, check_changes: bool = True):
    """Extrait et compare avec version précédente"""
    username = os.getenv("ELNET_USERNAME")
    password = os.getenv("ELNET_PASSWORD")
    
    if not username or not password:
        logger.error("ELNET credentials not found")
        return []
    
    init_db()
    
    # Load conventions list
    conventions_list = load_conventions_list("conventions_list.json")
    
    # Populate if empty
    db = SessionLocal()
    count = db.query(Convention).count()
    db.close()
    
    if count == 0:
        logger.info("Database empty, populating...")
        populate_database(conventions_list)
    
    # Get conventions to extract (all, not just pending - permet ré-extraction)
    db = SessionLocal()
    query = db.query(Convention)
    
    if end_idx:
        query = query.filter(Convention.id >= start_idx, Convention.id < end_idx)
    else:
        query = query.filter(Convention.id >= start_idx)
    
    conventions_to_extract = query.all()
    db.close()
    
    if not conventions_to_extract:
        logger.info("No conventions to extract")
        return []
    
    logger.info(f"Extracting {len(conventions_to_extract)} conventions")
    
    # Extract
    extractor = ConventionExtractor(username, password, headless=True)
    extractor.connector.setup_driver()
    
    if not extractor.connector.login():
        logger.error("Login failed")
        extractor.connector.close()
        return []
    
    changed_list = []
    
    for conv_db in conventions_to_extract:
        logger.info(f"[{conv_db.id}] {conv_db.name}")
        
        conv_data = {
            'id': conv_db.id,
            'name': conv_db.name,
            'idcc': conv_db.idcc,
            'url': conv_db.url,
            'pdf_url': conv_db.pdf_url,
            'brochure': conv_db.brochure,
            'signature_date': conv_db.signature_date,
            'extension_date': conv_db.extension_date,
            'jo_date': conv_db.jo_date
        }
        
        result = extractor.extract_convention(conv_db.id, conv_data)
        
        db = SessionLocal()
        try:
            conv = db.query(Convention).filter(Convention.id == conv_db.id).first()
            
            if result:
                new_hash = compute_hash(result.get('sections', []))
                old_hash = conv.version_hash
                
                # Détection de changement
                if check_changes and old_hash and old_hash != new_hash:
                    logger.info(f"✓ CHANGEMENT DÉTECTÉ pour {conv.name}")
                    conv.last_modified = datetime.utcnow()
                    
                    # Enregistrer dans table changes
                    from api.database import ConventionChange
                    change_record = ConventionChange(
                        convention_id=conv.id,
                        old_hash=old_hash,
                        new_hash=new_hash,
                        change_type="content_modified",
                        details={
                            'convention_name': conv.name,
                            'idcc': conv.idcc
                        },
                        processed=0
                    )
                    db.add(change_record)
                    
                    changed_list.append({
                        'id': conv.id,
                        'name': conv.name,
                        'idcc': conv.idcc,
                        'old_hash': old_hash,
                        'new_hash': new_hash,
                        'change_date': datetime.utcnow().isoformat()
                    })
                
                conv.sections = result.get('sections', [])
                conv.toc = result.get('toc', [])
                
                # Nettoyer le HTML avant stockage
                raw_html = result.get('raw_html', '')
                conv.raw_html = clean_html(raw_html) if raw_html else ''

                
                # Update metadata from extraction result
                metadata = result.get('metadata', {})
                if metadata.get('idcc'):
                    conv.idcc = metadata.get('idcc')
                if metadata.get('brochure'):
                    conv.brochure = metadata.get('brochure')
                if metadata.get('signature_date'):
                    conv.signature_date = metadata.get('signature_date')
                if metadata.get('extension_date'):
                    conv.extension_date = metadata.get('extension_date')
                if metadata.get('jo_date'):
                    conv.jo_date = metadata.get('jo_date')
                
                conv.status = "extracted"
                conv.extracted_at = datetime.utcnow()
                conv.version_hash = new_hash
                logger.info("✓ Success")
            else:
                conv.status = "error"
                logger.warning("✗ Failed")
            
            db.commit()
            
        finally:
            db.close()
    
    extractor.connector.close()
    
    # Sauvegarder la liste des changements
    if changed_list:
        timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
        changes_file = f"changes_{timestamp}.json"
        
        with open(changes_file, 'w', encoding='utf-8') as f:
            json.dump(changed_list, f, ensure_ascii=False, indent=2)
        
        logger.info(f"\n{'='*60}")
        logger.info(f"CHANGEMENTS DÉTECTÉS: {len(changed_list)}")
        logger.info(f"Sauvegardés dans: {changes_file}")
        logger.info(f"{'='*60}")
    
    return changed_list


def main():
    import argparse
    
    parser = argparse.ArgumentParser(description='Extract and track changes')
    parser.add_argument('--start', type=int, default=0)
    parser.add_argument('--end', type=int)
    parser.add_argument('--populate-only', action='store_true')
    parser.add_argument('--no-check-changes', action='store_true', 
                       help='Skip change detection')
    
    args = parser.parse_args()
    
    if args.populate_only:
        init_db()
        conventions_list = load_conventions_list("conventions_list.json")
        populate_database(conventions_list)
    else:
        changed = extract_and_compare(
            args.start, 
            args.end,
            check_changes=not args.no_check_changes
        )
        
        if changed:
            logger.info("\nConventions modifiées:")
            for c in changed:
                logger.info(f"  - {c['id']}: {c['name']}")


if __name__ == "__main__":
    main()
