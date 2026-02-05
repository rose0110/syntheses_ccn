import json
import logging
from pathlib import Path
from typing import Dict, List, Optional
from .html_to_markdown import HTMLToMarkdown
from .deepseek_client import DeepSeekClient
from .section_mapper import SectionMapper, SECTIONS

logger = logging.getLogger(__name__)

SYSTEM_PROMPT = """Tu es un assistant juridique qui reformule du contenu de conventions collectives.

IMPORTANT:
- Tu REFORMULES le contenu, tu ne synthétises pas
- Tu paraphrases pour éviter le plagiat tout en conservant TOUTES les informations
- Tu gardes la structure (titres, tableaux, listes)
- Tu utilises le format Markdown

INSTRUCTIONS:
1. Reformule tout le contenu en d'autres mots
2. Classe le contenu reformulé dans les sections appropriées
3. Si une section n'est pas mentionnée, écris: "*Non traité par la convention.*"
4. Garde les références d'articles si présentes

SECTIONS OBLIGATOIRES (34):
accident-travail, amenagement-temps-travail, apprenti, cet, classification, conges-payes,
contrat-professionnalisation, contributions-formation, cotisation-mutuelle, cotisation-prevoyance,
cotisation-retraite, delai-prevenance, durees-travail, evenements-familiaux, forfait-jours,
grille-remuneration, heures-supplementaires, indemnite-depart-retraite, indemnite-licenciement,
indemnite-mise-retraite, indemnite-precarite, indemnite-rupture-conventionnelle,
informations-generales, majoration-dimanche, majoration-ferie, majoration-nuit, maladie,
maternite-paternite, paritarisme-financement, periode-essai, preavis,
primes-indemnites-avantages, stagiaire, temps-partiel

FORMAT RÉPONSE (JSON):
{
  "accident-travail": {"title": "Accident de travail", "content": "..."},
  "amenagement-temps-travail": {"title": "Aménagement du temps de travail", "content": "..."},
  ...
}"""


class Reformulator:
    def __init__(self, api_key: str):
        self.client = DeepSeekClient(api_key)
        self.converter = HTMLToMarkdown()
        self.mapper = SectionMapper()
    
    def process_convention(self, convention_data: Dict) -> Optional[Dict]:
        logger.info(f"Processing convention {convention_data.get('id')}")
        
        try:
            markdown_content = self._extract_markdown(convention_data)
            
            if not markdown_content:
                logger.warning(f"No content found for convention {convention_data.get('id')}")
                return None
            
            reformulated = self.client.reformulate(markdown_content, SYSTEM_PROMPT)
            
            if not reformulated:
                logger.error(f"Reformulation failed for convention {convention_data.get('id')}")
                return None
            
            sections = self._validate_sections(reformulated)
            
            return {
                "id": convention_data.get("id"),
                "title": convention_data.get("metadata", {}).get("name", ""),
                "idcc": convention_data.get("metadata", {}).get("idcc"),
                "brochure": convention_data.get("metadata", {}).get("brochure"),
                "url": convention_data.get("metadata", {}).get("url"),
                "pdf_url": convention_data.get("metadata", {}).get("pdf_url"),
                "signature_date": convention_data.get("metadata", {}).get("signature_date"),
                "extension_date": convention_data.get("metadata", {}).get("extension_date"),
                "jo_date": convention_data.get("metadata", {}).get("jo_date"),
                "sections": sections
            }
            
        except Exception as e:
            logger.error(f"Error processing convention {convention_data.get('id')}: {e}")
            return None
    
    def _extract_markdown(self, convention_data: Dict) -> str:
        sections = convention_data.get("sections", [])
        
        if not sections:
            logger.warning("No sections found in convention data")
            return ""
        
        markdown_parts = []
        
        for section in sections:
            html = section.get("html", "")
            if html:
                md = self.converter.convert(html)
                if md:
                    markdown_parts.append(md)
        
        return "\n\n".join(markdown_parts)
    
    def _validate_sections(self, sections_data: Dict) -> Dict:
        result = {}
        
        for section_id in SECTIONS:
            if section_id in sections_data and sections_data[section_id]:
                result[section_id] = sections_data[section_id]
            else:
                result[section_id] = self.mapper.create_empty_section(section_id)
        
        return result
    
    def process_batch(self, conventions: List[Dict], output_path: str) -> List[Dict]:
        """DEPRECATED: Use individual processing instead"""
        logger.warning("process_batch is deprecated, processing individually")
        results = []
        
        for conv in conventions:
            result = self.process_convention(conv)
            if result:
                results.append(result)
        
        self._save_results(results, output_path)
        return results
    
    def _save_results(self, results: List[Dict], output_path: str):
        if not results:
            logger.warning("No results to save")
            return
        
        try:
            path = Path(output_path)
            path.parent.mkdir(parents=True, exist_ok=True)
            
            with open(path, 'w', encoding='utf-8') as f:
                json.dump(results, f, ensure_ascii=False, indent=2)
            
            logger.info(f"Saved {len(results)} conventions to {output_path}")
        except IOError as e:
            logger.error(f"Failed to save results: {e}")
            raise
