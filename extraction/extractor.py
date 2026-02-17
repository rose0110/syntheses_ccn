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
    
    def generate_pdf_url(self, url: str) -> Optional[str]:
        # Logique reverse-engineering pour trouver URL PDF
        import re
        m = re.search(r'[?&]id=([A-Z0-9]+)', url, re.IGNORECASE)
        if m:
            id_u = m.group(1).upper()
            return f"https://www.elnet.fr/documentation/hulkStatic/EL/CD15/ETD/{id_u}/sharp_/ANX/{id_u.lower()}.pdf"
        return None

    def extract_convention(self, id: int, info: Dict) -> Optional[Dict]:
        url = info.get("url")
        if not url:
            logger.warning(f"Skipping {id}: No URL")
            return None
        
        logger.info(f"Processing [{id}] {info.get('name', '???')}")
        
        html = self.connector.get_page(url)
        if not html:
            logger.error(f"Failed to load page {id}")
            return None
        
        # Fallback pour le PDF si non présent
        pdf = info.get("pdf_url") or self.generate_pdf_url(url)

        meta = {
            "name": info.get("name", ""),
            "idcc": info.get("idcc"),
            "brochure": info.get("brochure"),
            "url": url,
            "pdf_url": pdf,
            "signature_date": info.get("signature_date"),
            "extension_date": info.get("extension_date"),
            "jo_date": info.get("jo_date")
        }
        
        return self.parser.parse_convention_page(html, id, meta)
    
    def extract_batch(self, conv_list: List[Dict], out_dir: str):
        self.connector.setup_driver()
        
        if not self.connector.login():
            logger.error("Login failed. Check env vars.")
            self.connector.close()
            return
        
        res_list = []
        path = Path(out_dir)
        path.mkdir(parents=True, exist_ok=True)
        
        for i, c in enumerate(conv_list):
            cid = c.get("id", i)
            res = self.extract_convention(cid, c)
            
            if res:
                res_list.append(res)
                
                # Dump JSON direct
                fpath = path / f"convention_{cid}.json"
                try:
                    with open(fpath, 'w', encoding='utf-8') as f:
                        json.dump(res, f, ensure_ascii=False, indent=2)
                except Exception as e:
                    logger.error(f"Save error {cid}: {e}")
            
            # Anti-ban delay
            if i < len(conv_list) - 1:
                import time
                time.sleep(1)
        
        self.connector.close()
        logger.info(f"Done: {len(res_list)}/{len(conv_list)} OK")
        return res_list
    
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
