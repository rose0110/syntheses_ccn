import json
import logging
from pathlib import Path
from typing import Dict, List, Optional
from .elnet_connector import ElnetConnector
from .html_parser import ConventionParser

logger = logging.getLogger(__name__)


class ConventionExtractor:
    def __init__(self, username: str, password: str, headless: bool = True):
        self.connector = ElnetConnector(username, password, headless)
        self.parser = ConventionParser()
        self.conventions_data = []
    
    def load_conventions_list(self, file_path: str) -> List[Dict]:
        try:
            with open(file_path, 'r', encoding='utf-8') as f:
                data = json.load(f)
                logger.info(f"Loaded {len(data)} conventions from {file_path}")
                return data
        except FileNotFoundError:
            logger.error(f"File not found: {file_path}")
            return []
        except json.JSONDecodeError as e:
            logger.error(f"Invalid JSON in {file_path}: {e}")
            return []
    
    def generate_pdf_url(self, convention_url: str) -> Optional[str]:
        """Génère le lien PDF à partir du lien de la convention (logique script user)"""
        import re
        match = re.search(r'[?&]id=([A-Z0-9]+)', convention_url, re.IGNORECASE)
        if match:
            doc_id = match.group(1).upper()
            doc_id_lower = doc_id.lower()
            return f"https://www.elnet.fr/documentation/hulkStatic/EL/CD15/ETD/{doc_id}/sharp_/ANX/{doc_id_lower}.pdf"
        return None

    def extract_convention(self, convention_id: int, convention_info: Dict) -> Optional[Dict]:
        url = convention_info.get("url")
        
        if not url:
            logger.warning(f"No URL for convention {convention_id}")
            return None
        
        logger.info(f"Extracting convention {convention_id}: {convention_info.get('name', 'Unknown')}")
        
        html = self.connector.get_page(url)
        
        if not html:
            logger.error(f"Failed to retrieve page for convention {convention_id}")
            return None
        
        # Générer PDF URL dynamiquement si manquant
        pdf_url = convention_info.get("pdf_url")
        if not pdf_url and url:
            pdf_url = self.generate_pdf_url(url)

        metadata = {
            "name": convention_info.get("name", ""),
            "idcc": convention_info.get("idcc"),
            "brochure": convention_info.get("brochure"),
            "url": url,
            "pdf_url": pdf_url,
            "signature_date": convention_info.get("signature_date"),
            "extension_date": convention_info.get("extension_date"),
            "jo_date": convention_info.get("jo_date")
        }
        
        result = self.parser.parse_convention_page(html, convention_id, metadata)
        return result
    
    def extract_batch(self, conventions: List[Dict], output_dir: str):
        self.connector.setup_driver()
        
        if not self.connector.login():
            logger.error("Login failed, aborting extraction")
            self.connector.close()
            return
        
        results = []
        output_path = Path(output_dir)
        output_path.mkdir(parents=True, exist_ok=True)
        
        for i, conv in enumerate(conventions):
            conv_id = conv.get("id", i)
            
            result = self.extract_convention(conv_id, conv)
            
            if result:
                results.append(result)
                
                # Save individual file
                file_name = f"convention_{conv_id}.json"
                file_path = output_path / file_name
                
                try:
                    with open(file_path, 'w', encoding='utf-8') as f:
                        json.dump(result, f, ensure_ascii=False, indent=2)
                    logger.info(f"Saved {file_name}")
                except IOError as e:
                    logger.error(f"Failed to save {file_name}: {e}")
            
            # Small delay between requests
            if i < len(conventions) - 1:
                import time
                time.sleep(1)
        
        self.connector.close()
        
        logger.info(f"Extraction complete: {len(results)}/{len(conventions)} conventions")
        return results
    
    def extract_single(self, convention_id: int, conventions_list_path: str, output_dir: str):
        conventions = self.load_conventions_list(conventions_list_path)
        
        if not conventions:
            return None
        
        if convention_id >= len(conventions):
            logger.error(f"Convention ID {convention_id} out of range")
            return None
        
        target_conv = conventions[convention_id]
        target_conv['id'] = convention_id
        
        return self.extract_batch([target_conv], output_dir)
