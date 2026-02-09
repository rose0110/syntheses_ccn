from bs4 import BeautifulSoup
import json
import logging
import re
from typing import Dict, List, Optional

logger = logging.getLogger(__name__)


class ConventionParser:
    def parse_convention_page(self, html: str, convention_id: int, metadata: Dict) -> Optional[Dict]:
        try:
            soup = BeautifulSoup(html, 'html.parser')
            
            # Extract header table metadata (IDCC, brochure, dates)
            header_metadata = self._extract_header_table(soup)
            metadata.update(header_metadata)
            
            sections = self._extract_sections(soup)
            toc = self._extract_toc(soup)
            
            result = {
                "id": convention_id,
                "metadata": metadata,
                "sections": sections,
                "toc": toc,
                "raw_html": html,
                "status": "success"
            }
            
            return result
            
        except Exception as e:
            logger.error(f"Failed to parse convention {convention_id}: {e}")
            return None
    
    def _extract_header_table(self, soup: BeautifulSoup) -> Dict:
        """Extract IDCC, brochure, dates from header table (same as original script)"""
        metadata = {
            "idcc": None,
            "brochure": None,
            "signature_date": None,
            "extension_date": None,
            "jo_date": None,
            "revision_date": None,
            "revision_extension": None,
            "revision_jo": None
        }
        
        # Find the header table
        info_table = soup.find('table', class_='TYPE0-1COL')
        if not info_table:
            return metadata
        
        rows = info_table.find_all('tr')
        for row in rows:
            cells = row.find_all('td')
            if len(cells) >= 9:
                # Helper to clean cell text (same as original script)
                def clean_cell(cell):
                    text = cell.get_text(strip=True).replace('\n', ' ')
                    # Keep only the first part before long text
                    text = text.split('Signalons')[0].strip()
                    text = text.split('(')[0].strip()
                    return text.strip('-').strip()
                
                def clean_idcc(cell):
                    text = cell.get_text(strip=True)
                    # Extract only digits at the beginning
                    match = re.match(r'^(\d+)', text)
                    return match.group(1) if match else (text.split()[0] if text else None)
                
                # Extract all metadata from cells (same order as original script)
                metadata["signature_date"] = clean_cell(cells[1])
                metadata["extension_date"] = clean_cell(cells[2])
                metadata["jo_date"] = clean_cell(cells[3])
                metadata["revision_date"] = clean_cell(cells[4])
                metadata["revision_extension"] = clean_cell(cells[5])
                metadata["revision_jo"] = clean_cell(cells[6])
                metadata["brochure"] = clean_idcc(cells[7])
                metadata["idcc"] = clean_idcc(cells[8])
                break
        
        return metadata
    
    def _extract_sections(self, soup: BeautifulSoup) -> List[Dict]:
        """Extract sections from ua-rows (same as original script)"""
        sections = []
        
        # Find document content
        doc_content = soup.find(id='docContent')
        if not doc_content:
            return sections
        
        # Find all ua-rows (same as original script)
        ua_rows = doc_content.find_all('tr', class_='ua-row')
        
        for ua_row in ua_rows:
            seq = ua_row.get('data-hulk-sequence-number', '0')
            ua_content = ua_row.find(class_='ua-content')
            
            if ua_content:
                html_content = str(ua_content)
                text_preview = ua_content.get_text(separator='\n', strip=True)[:500]
                
                is_preamble = int(seq) == 1
                
                section_data = {
                    "sequence": int(seq),
                    "is_preamble": is_preamble,
                    "html": html_content,
                    "text": text_preview
                }
                
                sections.append(section_data)
        
        return sections
    
    def _extract_toc(self, soup: BeautifulSoup) -> List[Dict]:
        """Extract TOC from navigation-book-toc (same as original script)"""
        toc = []
        
        # Find TOC container (same as original script)
        toc_container = soup.find('navigation-book-toc')
        if toc_container:
            for li in toc_container.find_all('li', attrs={'data-toc-entry-sgml-id': True}):
                label = li.find(class_='book-toc-item-label')
                if label:
                    toc.append({
                        "id": label.get('id', ''),
                        "sgml_id": li.get('data-toc-entry-sgml-id', ''),
                        "title": label.get_text(strip=True)
                    })
        
        return toc
