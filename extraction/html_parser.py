from bs4 import BeautifulSoup
import json
import logging
from typing import Dict, List, Optional

logger = logging.getLogger(__name__)


class ConventionParser:
    def parse_convention_page(self, html: str, convention_id: int, metadata: Dict) -> Optional[Dict]:
        try:
            soup = BeautifulSoup(html, 'html.parser')
            
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
    
    def _extract_sections(self, soup: BeautifulSoup) -> List[Dict]:
        sections = []
        sequence = 0
        
        # Find all content sections
        content_divs = soup.find_all("div", class_="ua-content")
        
        for div in content_divs:
            sequence += 1
            
            section_data = {
                "sequence": sequence,
                "is_preamble": sequence == 1,
                "html": str(div),
                "text": div.get_text(separator='\n', strip=True)[:500]
            }
            
            sections.append(section_data)
        
        return sections
    
    def _extract_toc(self, soup: BeautifulSoup) -> List[Dict]:
        toc = []
        
        # Simple TOC extraction
        headers = soup.find_all(['h1', 'h2', 'h3'])
        
        for header in headers:
            entry = {
                "title": header.get_text(strip=True),
                "level": int(header.name[1])
            }
            toc.append(entry)
        
        return toc
