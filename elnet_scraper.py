import json
import logging
import os
import re
import time
from datetime import datetime
from typing import Optional, Tuple

from bs4 import BeautifulSoup

logger = logging.getLogger(__name__)

BASE_URL = "https://www.elnet.fr"

# Temps d'attente pour que AngularJS charge le contenu
ANGULAR_WAIT = 5       # secondes après navigation
SCROLL_WAIT = 0.4      # secondes entre chaque scroll
MAX_SCROLLS = 60       # scrolls maxi pour charger tout le lazy-load


class ElnetScraper:
    def __init__(self, connector, output_dir: str = "output"):
        self.connector = connector
        self.driver = connector.driver
        self.output_dir = output_dir
        os.makedirs(output_dir, exist_ok=True)

    # ──────────────────────────────────────────────────────────────
    # SCROLL (pour forcer le chargement lazy-load)
    # ──────────────────────────────────────────────────────────────

    def _scroll_page(self):
        """Scroll progressif jusqu'en bas pour charger toutes les sections."""
        last_height = self.driver.execute_script("return document.body.scrollHeight")
        scrolls = 0

        while scrolls < MAX_SCROLLS:
            self.driver.execute_script("window.scrollTo(0, document.body.scrollHeight);")
            time.sleep(SCROLL_WAIT)
            new_height = self.driver.execute_script("return document.body.scrollHeight")
            if new_height == last_height:
                break
            last_height = new_height
            scrolls += 1

        # Remonter en haut
        self.driver.execute_script("window.scrollTo(0, 0);")
        time.sleep(0.3)
        logger.debug(f"Scroll terminé après {scrolls} passes")

    # ──────────────────────────────────────────────────────────────
    # UTILITAIRES
    # ──────────────────────────────────────────────────────────────

    def _html_to_text(self, html: str) -> str:
        """Convertit du HTML en texte brut propre (preview ~500 chars)."""
        soup = BeautifulSoup(html, "html.parser")
        for tag in soup(["script", "style"]):
            tag.decompose()
        text = soup.get_text(separator="\n")
        lines = [line.strip() for line in text.splitlines()]
        cleaned = "\n".join(line for line in lines if line)
        return cleaned[:500] if len(cleaned) > 500 else cleaned

    def _output_path(self, elnet_id: str) -> str:
        return os.path.join(self.output_dir, f"{elnet_id}.json")

    def _clean_cell_value(self, cell) -> str:
        """Nettoie une cellule de tableau (garde les dates courtes)."""
        text = cell.get_text(separator=" ").strip()
        text = re.sub(r'\s+', ' ', text)
        # Supprimer les annotations longues entre parenthèses
        text = re.sub(r'\(.*\)', '', text).strip()
        # Nettoyer les tirets seuls
        if re.match(r'^[-\s]+$', text):
            return ""
        return text.strip()

    def _clean_numeric(self, cell) -> str:
        """Extrait uniquement les chiffres d'une cellule (IDCC, brochure)."""
        text = cell.get_text(strip=True)
        match = re.match(r'^(\d+)', text)
        return match.group(1) if match else ""

    # ──────────────────────────────────────────────────────────────
    # EXTRACTION DU TABLEAU MÉTADONNÉES (TYPE0-1COL)
    # ──────────────────────────────────────────────────────────────

    def _extract_header_table(self, soup: BeautifulSoup) -> Tuple[dict, str]:
        """Parse le tableau TYPE0-1COL : IDCC, brochure, dates."""
        meta = {
            "signature_date": "", "extension_date": "", "jo_date": "",
            "revision_date": "", "revision_extension": "", "revision_jo": "",
            "idcc": "", "brochure": "",
        }
        table = soup.find("table", class_="TYPE0-1COL")
        if not table:
            return meta, ""

        header_html = str(table)
        rows = table.find_all("tr")

        for row in rows:
            cells = row.find_all("td")
            if len(cells) >= 9:
                # Ordre: nom | signature | extension | JO | révision | ext_rév | JO_rév | brochure | IDCC
                meta["signature_date"] = self._clean_cell_value(cells[1])
                meta["extension_date"] = self._clean_cell_value(cells[2])
                meta["jo_date"] = self._clean_cell_value(cells[3])
                meta["revision_date"] = self._clean_cell_value(cells[4])
                meta["revision_extension"] = self._clean_cell_value(cells[5])
                meta["revision_jo"] = self._clean_cell_value(cells[6])
                meta["brochure"] = self._clean_numeric(cells[7])
                meta["idcc"] = self._clean_numeric(cells[8])
                break  # Première ligne de données suffisant

        return meta, header_html

    # ──────────────────────────────────────────────────────────────
    # EXTRACTION DU SOMMAIRE (navigation-book-toc)
    # ──────────────────────────────────────────────────────────────

    def _extract_toc(self, soup: BeautifulSoup) -> list:
        """Parse le composant navigation-book-toc pour construire le sommaire."""
        toc = []
        toc_container = soup.find("navigation-book-toc")
        if not toc_container:
            # Fallback : chercher les li avec data-toc-entry-sgml-id n'importe où
            toc_container = soup

        items = toc_container.find_all("li", attrs={"data-toc-entry-sgml-id": True})
        for item in items:
            sgml_id = item.get("data-toc-entry-sgml-id", "")
            label = item.find(class_="book-toc-item-label")
            if label:
                entry_id = label.get("id", sgml_id)
                title = label.get_text(strip=True)
                toc.append({
                    "id": entry_id,
                    "sgml_id": sgml_id,
                    "title": title,
                })

        return toc

    # ──────────────────────────────────────────────────────────────
    # EXTRACTION DES SECTIONS (tr.ua-row dans #docContent)
    # ──────────────────────────────────────────────────────────────

    def _extract_sections(self, soup: BeautifulSoup) -> Tuple[list, str]:
        """
        Extrait TOUTES les sections depuis #docContent.
        Chaque section = <tr class="ua-row" data-hulk-sequence-number="N">
                            <td><div class="ua-content">...</div></td>
                         </tr>
        Retourne (sections_list, preamble_html).
        """
        sections = []
        preamble_html = ""

        doc_content = soup.find(id="docContent")
        if not doc_content:
            logger.warning("❌ #docContent introuvable dans la page")
            return sections, preamble_html

        ua_rows = doc_content.find_all("tr", class_="ua-row")
        logger.info(f"  → {len(ua_rows)} ua-row trouvées dans #docContent")

        for row in ua_rows:
            seq_str = row.get("data-hulk-sequence-number", "0")
            try:
                seq = int(seq_str)
            except ValueError:
                seq = 0

            ua_content = row.find(class_="ua-content")
            if not ua_content:
                continue

            html_content = str(ua_content)
            text_preview = self._html_to_text(html_content)
            is_preamble = (seq == 1)

            if is_preamble:
                preamble_html = html_content

            sections.append({
                "sequence": seq,
                "is_preamble": is_preamble,
                "html": html_content,
                "text": text_preview,
            })

        # Trier par séquence
        sections.sort(key=lambda x: x["sequence"])
        return sections, preamble_html

    # ──────────────────────────────────────────────────────────────
    # CHARGEMENT DE LA PAGE CONVENTION (Selenium + scroll)
    # ──────────────────────────────────────────────────────────────

    def _load_convention_page(self, url: str) -> BeautifulSoup:
        """
        Charge une page convention via Selenium, attend le rendu Angular,
        scroll pour tout charger, puis retourne le BeautifulSoup.
        """
        self.driver.get(url)
        time.sleep(ANGULAR_WAIT)  # Attendre le rendu Angular

        # Scroll complet pour tout charger (sections lazy-loaded)
        self._scroll_page()

        # Attendre un peu après le scroll
        time.sleep(1)

        return BeautifulSoup(self.driver.page_source, "html.parser")

    # ──────────────────────────────────────────────────────────────
    # POINT D'ENTRÉE : scraper une convention complète
    # ──────────────────────────────────────────────────────────────

    def scrape_convention(self, convention: dict) -> Optional[dict]:
        """Scrape une convention et sauvegarde le JSON. Retourne None si déjà fait."""
        elnet_id = convention["id"]
        name = convention["name"]
        url = convention["url"]

        output_path = self._output_path(elnet_id)
        if os.path.exists(output_path):
            logger.info(f"⏭  {elnet_id} déjà extrait, on passe.")
            return None

        logger.info(f"\n{'='*60}")
        logger.info(f"📄 {name} ({elnet_id})")
        logger.info(f"{'='*60}")

        try:
            # 1. Charger la page et scroller
            soup = self._load_convention_page(url)

            # 2. Métadonnées depuis le tableau d'en-tête
            meta_dict, header_html = self._extract_header_table(soup)
            logger.info(f"  ✓ Métadonnées: IDCC={meta_dict['idcc']} | Brochure={meta_dict['brochure']}")

            # 3. TOC
            toc = self._extract_toc(soup)
            logger.info(f"  ✓ TOC: {len(toc)} entrées")

            # 4. Sections depuis les ua-row
            sections, preamble_html = self._extract_sections(soup)
            logger.info(f"  ✓ Sections: {len(sections)} extraites")

            if not sections:
                logger.warning(f"  ⚠ Aucune section trouvée pour {elnet_id} — le contenu n'est peut-être pas chargé")

            # 5. URL PDF
            pdf_url = (
                f"{BASE_URL}/documentation/hulkStatic/EL/CD15/ETD/"
                f"{elnet_id}/sharp_/ANX/{elnet_id.lower()}.pdf"
            )

            # 6. JSON final
            result = {
                "metadata": {
                    "name": name,
                    "url": url,
                    "pdf_url": pdf_url,
                    "elnet_id": elnet_id,
                    "extraction_date": datetime.now().isoformat(),
                    "idcc": meta_dict.get("idcc", ""),
                    "brochure": meta_dict.get("brochure", ""),
                    "signature_date": meta_dict.get("signature_date", ""),
                    "extension_date": meta_dict.get("extension_date", ""),
                    "jo_date": meta_dict.get("jo_date", ""),
                    "revision_date": meta_dict.get("revision_date", ""),
                    "revision_extension": meta_dict.get("revision_extension", ""),
                    "revision_jo": meta_dict.get("revision_jo", ""),
                },
                "header_table_html": header_html,
                "preamble_html": preamble_html,
                "toc": toc,
                "sections": sections,
            }

            # 7. Sauvegarde
            with open(output_path, "w", encoding="utf-8") as f:
                json.dump(result, f, ensure_ascii=False, indent=2)

            logger.info(f"  ✅ Sauvegardé → {output_path}")
            return result

        except Exception as e:
            logger.error(f"  ❌ Erreur {elnet_id}: {e}", exc_info=True)
            partial_path = output_path.replace(".json", "_partial.json")
            try:
                with open(partial_path, "w", encoding="utf-8") as f:
                    json.dump({"error": str(e), "convention": convention}, f, ensure_ascii=False)
            except Exception:
                pass
            return None
