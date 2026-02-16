from bs4 import BeautifulSoup
import json
import logging
import re
from typing import Dict, List, Optional

logger = logging.getLogger(__name__)


class ConventionParser:
    """Parser STRICTEMENT basé sur le script original qui fonctionne"""
    
    def parse_convention_page(self, html: str, convention_id: int, metadata: Dict) -> Optional[Dict]:
        try:
            soup = BeautifulSoup(html, 'html.parser')
            
            # EXACTEMENT comme le script original
            result = {
                "metadata": metadata.copy(),
                "header_table_html": "",
                "preamble_html": "",
                "toc": [],
                "sections": [],
                "raw_html": "",
            }
            
            # 1. Extraire le tableau d'en-tête (IDCC, Brochure, etc.) - COPIE EXACTE DU SCRIPT ORIGINAL
            info_table = soup.find('table', class_='TYPE0-1COL')
            if info_table:
                result["header_table_html"] = str(info_table)
                
                rows = info_table.find_all('tr')
                for row in rows:
                    cells = row.find_all('td')
                    if len(cells) >= 9:
                        # Extraire et nettoyer les valeurs (COPIE EXACTE DU SCRIPT ORIGINAL)
                        def clean_cell(cell):
                            text = cell.get_text(strip=True).replace('\n', ' ')
                            # Garder uniquement la première partie avant tout texte long
                            text = text.split('Signalons')[0].strip()
                            text = text.split('(')[0].strip()
                            return text.strip('-').strip()
                        
                        def clean_idcc(cell):
                            text = cell.get_text(strip=True)
                            # Extraire uniquement les chiffres au début
                            match = re.match(r'^(\d+)', text)
                            return match.group(1) if match else (text.split()[0] if text else '')
                        
                        result["metadata"]["signature_date"] = clean_cell(cells[1])
                        result["metadata"]["extension_date"] = clean_cell(cells[2])
                        result["metadata"]["jo_date"] = clean_cell(cells[3])
                        result["metadata"]["revision_date"] = clean_cell(cells[4])
                        result["metadata"]["revision_extension"] = clean_cell(cells[5])
                        result["metadata"]["revision_jo"] = clean_cell(cells[6])
                        result["metadata"]["brochure"] = clean_idcc(cells[7])
                        result["metadata"]["idcc"] = clean_idcc(cells[8])
                        logger.info(f"✓ Metadata extracted: IDCC={result['metadata']['idcc']}, Brochure={result['metadata']['brochure']}")
                        break
            
            # 2. Extraire le sommaire (TOC) - COPIE EXACTE DU SCRIPT ORIGINAL
            toc_container = soup.find('navigation-book-toc')
            if toc_container:
                for li in toc_container.find_all('li', attrs={'data-toc-entry-sgml-id': True}):
                    label = li.find(class_='book-toc-item-label')
                    if label:
                        result["toc"].append({
                            "id": label.get('id', ''),
                            "sgml_id": li.get('data-toc-entry-sgml-id', ''),
                            "title": label.get_text(strip=True),
                        })
            
            # 3. Extraire tout le contenu - COPIE EXACTE DU SCRIPT ORIGINAL
            doc_content = soup.find(id='docContent')
            if doc_content:
                result["raw_html"] = str(doc_content)
                
                ua_rows = doc_content.find_all('tr', class_='ua-row')
                
                for ua_row in ua_rows:
                    seq = ua_row.get('data-hulk-sequence-number', '0')
                    ua_content = ua_row.find(class_='ua-content')
                    
                    if ua_content:
                        html_content = str(ua_content)
                        text_preview = ua_content.get_text(separator='\n', strip=True)[:500]
                        
                        is_preamble = int(seq) == 1
                        
                        if is_preamble:
                            result["preamble_html"] = html_content
                        
                        # Tentative d'extraction du titre depuis le contenu
                        title = "Section sans titre"
                        soup_content = BeautifulSoup(html_content, 'html.parser')
                        
                        # Chercher les classes de titre habituelles sur ELNET
                        title_tag = soup_content.find(['div', 'p', 'h1', 'h2', 'h3'], class_=re.compile(r'A[0-9]-TITRE'))
                        if not title_tag:
                            title_tag = soup_content.find(['h1', 'h2', 'h3'])
                        
                        if title_tag:
                            title = title_tag.get_text(strip=True)

                        result["sections"].append({
                            "sequence": int(seq),
                            "is_preamble": is_preamble,
                            "title": title,
                            "html": html_content,
                            "text": text_preview,
                        })
            
            result["status"] = "success"
            return result
            
        except Exception as e:
            logger.error(f"Failed to parse convention {convention_id}: {e}")
            return None
