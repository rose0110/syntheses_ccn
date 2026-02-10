#!/usr/bin/env python3
"""
Script d'extraction des conventions collectives vers JSON structuré.
Utilise Gemini 2.5 Flash pour extraire et structurer les données.

PRÉREQUIS: Lancer generate_index.py pour créer l'index.json

Usage:
    python main.py                                # Mode interactif (menu)
    python main.py --list                         # Liste les CC disponibles
    python main.py --cc 16-transports-routiers    # Extrait par clé
    python main.py --cc-range 1-1500              # Plage d'IDCC
    python main.py --all                          # Extrait tout
    python main.py --dry-run                      # Simule sans appeler l'API
"""

import argparse
import json
import re
import time
from pathlib import Path
from datetime import datetime

import google.generativeai as genai
import inquirer
from rich.console import Console
from rich.table import Table

console = Console()

# ============================================================================
# CONFIGURATION
# ============================================================================

API_KEY = "AIzaSyBmUELyqEIXqpacEyB2WeMukp74jhOzYC0"

MODEL = "gemini-2.5-flash"
TEMPERATURE = 0.1

BASE_DIR = Path(__file__).parent
EXTRACTIONS_DIR = Path(r"C:\Users\roses\Downloads\Python\ELENET\output_conventions\extractions")
PROMPTS_DIR = BASE_DIR / "prompts_section"
RESULTATS_DIR = BASE_DIR / "resultats"

SECTIONS = [
    # Informations générales (1)
    "informations-generales",
    # Période d'essai et rupture (4)
    "periode-essai",
    "delai-prevenance",
    "preavis",
    # Indemnités de rupture (5)
    "indemnite-licenciement",
    "indemnite-depart-retraite",
    "indemnite-mise-retraite",
    "indemnite-precarite",
    "indemnite-rupture-conventionnelle",
    # Congés (2)
    "conges-payes",
    "evenements-familiaux",
    # Temps de travail (6)
    "durees-travail",
    "heures-supplementaires",
    "majoration-nuit",
    "majoration-dimanche",
    "majoration-ferie",
    "forfait-jours",
    # Aménagement du temps (3)
    "temps-partiel",
    "amenagement-temps-travail",
    "cet",
    # Maintien de salaire (3)
    "maladie",
    "accident-travail",
    "maternite-paternite",
    # Protection sociale (3)
    "cotisation-mutuelle",
    "cotisation-prevoyance",
    "cotisation-retraite",
    # Formation et paritarisme (2)
    "contributions-formation",
    "paritarisme-financement",
    # Alternance et stages (3)
    "apprenti",
    "contrat-professionnalisation",
    "stagiaire",
    # Classification et rémunération (3)
    "classification",
    "grille-remuneration",
    "primes-indemnites-avantages",
]

API_DELAY = 0.5

# ============================================================================
# SYSTEM PROMPT
# ============================================================================

SYSTEM_PROMPT = """
Tu es un assistant spécialisé dans l'extraction et la restructuration de données issues de conventions collectives françaises. Ces données sont destinées à être intégrées dans un logiciel de paie.

## ⚠️ RÈGLE ABSOLUE : NE RIEN OMETTRE

La source fournie est **déjà une synthèse**. Ton rôle n'est PAS d'analyser, trier ou sélectionner.

### Tu dois :
- ✅ **TOUT prendre** — chaque information, chaque nuance, chaque cas particulier
- ✅ **Réorganiser** dans la structure JSON demandée
- ✅ **Reformuler** si nécessaire pour clarifier
- ✅ **Conserver** toutes les valeurs, tous les seuils, toutes les conditions

### Tu ne dois PAS :
- ❌ Décider qu'une information est "moins importante"
- ❌ Résumer ou simplifier des règles complexes
- ❌ Omettre des cas particuliers, régionaux ou catégoriels
- ❌ Fusionner des tranches ou des seuils différents
- ❌ Appliquer le Code du travail si la convention est muette
- ❌ Inventer des informations qui ne sont pas dans la source

**Si c'est dans la source, c'est dans le JSON. Point final.**

## 📤 FORMAT DE SORTIE

### OBLIGATOIRE :
- Réponds **uniquement** avec un objet JSON valide
- **Aucun texte** avant le JSON
- **Aucun texte** après le JSON
- **Aucun bloc markdown** (pas de ```json```)
- Juste l'objet JSON brut

## 📊 TABLEAUX vs LISTES

### Format tableau :
```json
"tableau": {
  "colonnes": ["En-tête 1", "En-tête 2"],
  "lignes": [
    ["Valeur 1a", "Valeur 1b"],
    ["Valeur 2a *", "Valeur 2b"]
  ]
}
```

## ✳️ SYSTÈME D'ASTÉRISQUES

Pour les cas particuliers dans les tableaux :
- Dans la cellule : `"2 mois *"` ou `"3 mois **"`
- Dans précisions : `"* Explication..."`, `"** Autre explication..."`

## ⚠️ VALEURS NULLES

- Information absente de la source → `null`
- Catégorie sans élément → `[]`
- Bloc non applicable → `"applicable": false`
- Section non traitée par la CC → `"statut": "non_traite"`
""".strip()

# ============================================================================
# FONCTIONS UTILITAIRES
# ============================================================================

def clean_html(raw_html: str) -> str:
    """Nettoie le HTML."""
    if not raw_html:
        return ""
    
    cleaned = raw_html
    cleaned = re.sub(r'<script[^>]*>.*?</script>', '', cleaned, flags=re.DOTALL)
    cleaned = re.sub(r'try\s*\{[^}]*\$\([^}]*\}[^}]*\}[^}]*catch\s*\([^)]*\)\s*\{\s*\}', '', cleaned, flags=re.DOTALL)
    cleaned = re.sub(r'<!--.*?-->', '', cleaned, flags=re.DOTALL)
    cleaned = re.sub(r'\s+(style|width|height|valign|align|border|cellpadding|cellspacing|id|name|src|alt|title)="[^"]*"', '', cleaned)
    cleaned = re.sub(r'\s+(ng-[a-z-]+|data-[a-z-]+|on\w+)="[^"]*"', '', cleaned)
    cleaned = re.sub(r'<table[^>]*class="contactredac-table"[^>]*>.*?</table>', '', cleaned, flags=re.DOTALL)
    cleaned = re.sub(r'<img[^>]*/?>', '', cleaned)
    cleaned = re.sub(r'<a[^>]*>\s*</a>', '', cleaned)
    cleaned = re.sub(r'\n\s*\n+', '\n', cleaned)
    cleaned = re.sub(r'  +', ' ', cleaned)
    
    return cleaned.strip()


def load_convention(filepath: Path) -> dict | None:
    """Charge un fichier JSON de convention."""
    try:
        with open(filepath, 'r', encoding='utf-8') as f:
            return json.load(f)
    except Exception as e:
        print(f"  ❌ Erreur lecture {filepath.name}: {e}")
        return None


def load_prompt(section: str) -> str | None:
    """Charge le prompt pour une section."""
    prompt_path = PROMPTS_DIR / f"{section}.md"
    if not prompt_path.exists():
        print(f"  ⚠️ Prompt non trouvé: {prompt_path}")
        return None
    
    try:
        return prompt_path.read_text(encoding='utf-8')
    except Exception as e:
        print(f"  ❌ Erreur lecture prompt {section}: {e}")
        return None


def load_index() -> dict:
    """Charge l'index des conventions."""
    index_path = BASE_DIR / "index.json"
    
    if not index_path.exists():
        console.print(f"[red]❌ Fichier index.json non trouvé[/red]")
        console.print("[dim]Lance d'abord: python generate_index.py[/dim]")
        return {}
    
    try:
        with open(index_path, 'r', encoding='utf-8') as f:
            return json.load(f)
    except Exception as e:
        console.print(f"[red]❌ Erreur lecture index.json: {e}[/red]")
        return {}


def list_conventions() -> list[dict]:
    """Liste toutes les conventions depuis l'index."""
    conventions = []
    index_data = load_index()
    
    for key, data in index_data.items():
        conventions.append({
            'key': key,
            'idcc': data.get('idcc') or '-',
            'nom': data.get('nom', 'N/A'),
            'brochure': data.get('brochure') or '-',
            'fichier': data.get('fichier', ''),
        })
    
    return conventions


def extract_content(data: dict) -> str:
    """Extrait le contenu textuel d'une convention."""
    raw_html = data.get('raw_html', '')
    
    if not raw_html:
        sections_text = []
        for section in data.get('sections', []):
            text = section.get('text', '') or section.get('html', '')
            if text:
                sections_text.append(text)
        return '\n\n'.join(sections_text)
    
    return clean_html(raw_html)


# ============================================================================
# API GEMINI
# ============================================================================

def init_gemini():
    """Initialise l'API Gemini."""
    genai.configure(api_key=API_KEY)


def call_gemini(prompt: str, max_retries: int = 3) -> str | None:
    """Appelle l'API Gemini."""
    model = genai.GenerativeModel(
        model_name=MODEL,
        generation_config={
            "response_mime_type": "application/json",
            "temperature": TEMPERATURE,
        }
    )
    
    for attempt in range(max_retries):
        try:
            response = model.generate_content(prompt)
            return response.text
        except Exception as e:
            print(f"    ⚠️ Tentative {attempt + 1}/{max_retries} échouée: {e}")
            if attempt < max_retries - 1:
                time.sleep(5)
    
    return None


def validate_json(response_text: str) -> tuple[bool, dict | str]:
    """Valide que la réponse est du JSON valide."""
    if not response_text:
        return False, "Réponse vide"
    
    try:
        data = json.loads(response_text)
        return True, data
    except json.JSONDecodeError as e:
        return False, f"JSON invalide: {e}"


# ============================================================================
# EXTRACTION
# ============================================================================

def extract_section(convention_data: dict, section: str, dry_run: bool = False) -> dict | None:
    """Extrait une section d'une convention."""
    section_prompt = load_prompt(section)
    if not section_prompt:
        return None
    
    content = extract_content(convention_data)
    if not content:
        print(f"    ⚠️ Contenu vide")
        return None
    
    meta = convention_data.get('metadata', {})
    idcc = meta.get('idcc', 'N/A')
    nom = meta.get('name', 'N/A')
    
    full_prompt = f"""
{SYSTEM_PROMPT}

---

## INSTRUCTIONS SPÉCIFIQUES À CETTE SECTION

{section_prompt}

---

## CONVENTION COLLECTIVE À ANALYSER

**IDCC** : {idcc}
**Nom** : {nom}

### CONTENU :

{content}
"""
    
    if dry_run:
        print(f"    [DRY-RUN] {len(full_prompt):,} chars (~{len(full_prompt)//4:,} tokens)")
        return {"dry_run": True, "prompt_length": len(full_prompt)}
    
    print(f"    📡 Appel API ({len(full_prompt):,} chars)...", end=" ", flush=True)
    response = call_gemini(full_prompt)
    
    if not response:
        print("❌ Pas de réponse")
        return None
    
    is_valid, result = validate_json(response)
    
    if not is_valid:
        print(f"❌ {result}")
        return None
    
    print("✅")
    return result


def extract_convention(filepath: Path, sections: list[str] | None = None, dry_run: bool = False) -> dict:
    """Extrait les sections d'une convention."""
    data = load_convention(filepath)
    if not data:
        return {}
    
    meta = data.get('metadata', {})
    idcc = meta.get('idcc', 'N/A')
    nom = meta.get('name', 'N/A')
    
    print(f"\n📖 IDCC {idcc} - {nom}")
    print(f"   Fichier: {filepath.name}")
    
    sections_to_extract = sections or SECTIONS
    
    results = {
        "metadata": meta,
        "extraction_date": datetime.now().isoformat(),
        "fichier_source": filepath.name,
        "sections": {}
    }
    
    for section in sections_to_extract:
        print(f"  📑 {section}...")
        
        result = extract_section(data, section, dry_run=dry_run)
        
        if result:
            results["sections"][section] = result
        else:
            results["sections"][section] = {"statut": "erreur"}
        
        if not dry_run and section != sections_to_extract[-1]:
            time.sleep(API_DELAY)
    
    return results


def save_results(key: str, results: dict):
    """Sauvegarde les résultats."""
    output_dir = RESULTATS_DIR / key
    output_dir.mkdir(parents=True, exist_ok=True)
    
    for section_name, section_data in results.get("sections", {}).items():
        output_path = output_dir / f"{section_name}.json"
        with open(output_path, 'w', encoding='utf-8') as f:
            json.dump(section_data, f, ensure_ascii=False, indent=2)
    
    meta_path = output_dir / "metadata.json"
    with open(meta_path, 'w', encoding='utf-8') as f:
        json.dump({
            "metadata": results.get("metadata", {}),
            "extraction_date": results.get("extraction_date"),
            "fichier_source": results.get("fichier_source", "")
        }, f, ensure_ascii=False, indent=2)
    
    print(f"  💾 Sauvegardé: {output_dir}")


def find_convention_file(cc_data: dict) -> Path | None:
    """Trouve le fichier d'une convention depuis l'index."""
    fichier = cc_data.get('fichier')
    if fichier:
        filepath = EXTRACTIONS_DIR / fichier
        if filepath.exists():
            return filepath
    return None


# ============================================================================
# COMMANDES CLI
# ============================================================================

def cmd_list():
    """Liste les conventions."""
    conventions = list_conventions()
    
    if not conventions:
        return
    
    table = Table(title="Conventions disponibles")
    table.add_column("IDCC", justify="right", style="cyan", width=6)
    table.add_column("Clé", style="yellow", width=40)
    table.add_column("Nom", style="green")
    
    for cc in conventions:
        table.add_row(cc['idcc'], cc['key'][:40], cc['nom'][:40])
    
    console.print(table)
    
    with_idcc = sum(1 for c in conventions if c['idcc'] != '-')
    without_idcc = len(conventions) - with_idcc
    console.print(f"\n[bold]Total: {len(conventions)}[/bold] | Avec IDCC: {with_idcc} | Sans IDCC: {without_idcc}")


def cmd_extract(keys: list[str], sections: list[str] | None, dry_run: bool):
    """Extrait par clé."""
    if not API_KEY:
        print("❌ Configure ta clé API")
        return
    
    init_gemini()
    index_data = load_index()
    
    for key in keys:
        if key not in index_data:
            print(f"❌ Clé non trouvée: {key}")
            continue
        
        cc_data = index_data[key]
        filepath = find_convention_file(cc_data)
        
        if not filepath:
            print(f"❌ Fichier non trouvé pour {key}")
            continue
        
        results = extract_convention(filepath, sections=sections, dry_run=dry_run)
        
        if results and not dry_run:
            save_results(key, results)


def cmd_extract_all(sections: list[str] | None, dry_run: bool, skip_confirm: bool = False):
    """Extrait tout."""
    if not API_KEY:
        print("❌ Configure ta clé API")
        return
    
    conventions = list_conventions()
    
    if not conventions:
        return
    
    print(f"\n📋 {len(conventions)} conventions × {len(sections or SECTIONS)} sections = {len(conventions) * len(sections or SECTIONS)} appels API")
    
    if not dry_run and not skip_confirm:
        confirm = input("\nContinuer ? (oui/non) : ")
        if confirm.lower() not in ['oui', 'o', 'yes', 'y']:
            print("Annulé.")
            return
    
    init_gemini()
    index_data = load_index()
    
    for cc in conventions:
        key = cc['key']
        cc_data = index_data.get(key, {})
        filepath = find_convention_file(cc_data)
        
        if filepath:
            results = extract_convention(filepath, sections=sections, dry_run=dry_run)
            if results and not dry_run:
                save_results(key, results)
        else:
            print(f"  ⚠️ Fichier non trouvé: {key}")


def cmd_extract_range(cc_range: str, sections: list[str] | None, dry_run: bool, skip_confirm: bool = False):
    """Extrait une plage d'IDCC."""
    if not API_KEY:
        print("❌ Configure ta clé API")
        return
    
    try:
        start, end = cc_range.split('-')
        start_idcc = int(start)
        end_idcc = int(end)
    except:
        print(f"❌ Format invalide: {cc_range} (attendu: DEBUT-FIN)")
        return
    
    conventions = list_conventions()
    
    filtered = []
    for cc in conventions:
        if cc['idcc'] != '-' and cc['idcc'].isdigit():
            idcc_num = int(cc['idcc'])
            if start_idcc <= idcc_num <= end_idcc:
                filtered.append(cc)
    
    if not filtered:
        print(f"❌ Aucune convention dans la plage {start_idcc}-{end_idcc}")
        return
    
    print(f"\n📋 Plage {start_idcc}-{end_idcc}: {len(filtered)} conventions")
    
    if not dry_run and not skip_confirm:
        confirm = input("\nContinuer ? (oui/non) : ")
        if confirm.lower() not in ['oui', 'o', 'yes', 'y']:
            print("Annulé.")
            return
    
    init_gemini()
    index_data = load_index()
    
    for cc in filtered:
        key = cc['key']
        cc_data = index_data.get(key, {})
        filepath = find_convention_file(cc_data)
        
        if filepath:
            results = extract_convention(filepath, sections=sections, dry_run=dry_run)
            if results and not dry_run:
                save_results(key, results)


def cmd_extract_sans_idcc(sections: list[str] | None, dry_run: bool, skip_confirm: bool = False):
    """Extrait les conventions sans IDCC."""
    if not API_KEY:
        print("❌ Configure ta clé API")
        return
    
    conventions = list_conventions()
    filtered = [cc for cc in conventions if cc['idcc'] == '-']
    
    if not filtered:
        print("❌ Aucune convention sans IDCC")
        return
    
    print(f"\n📋 Sans IDCC: {len(filtered)} conventions")
    
    if not dry_run and not skip_confirm:
        confirm = input("\nContinuer ? (oui/non) : ")
        if confirm.lower() not in ['oui', 'o', 'yes', 'y']:
            print("Annulé.")
            return
    
    init_gemini()
    index_data = load_index()
    
    for cc in filtered:
        key = cc['key']
        cc_data = index_data.get(key, {})
        filepath = find_convention_file(cc_data)
        
        if filepath:
            results = extract_convention(filepath, sections=sections, dry_run=dry_run)
            if results and not dry_run:
                save_results(key, results)


def cmd_extract_lot(lot: str, sections: list[str] | None, dry_run: bool, skip_confirm: bool = False):
    """Extrait un lot."""
    if not API_KEY:
        print("❌ Configure ta clé API")
        return
    
    try:
        num_lot, total_lots = lot.split('/')
        num_lot = int(num_lot)
        total_lots = int(total_lots)
        if num_lot < 1 or num_lot > total_lots:
            raise ValueError()
    except:
        print(f"❌ Format invalide: {lot} (attendu: N/TOTAL)")
        return
    
    conventions = list_conventions()
    total_cc = len(conventions)
    
    cc_par_lot = total_cc // total_lots
    reste = total_cc % total_lots
    
    if num_lot <= reste:
        start_idx = (num_lot - 1) * (cc_par_lot + 1)
        end_idx = start_idx + cc_par_lot + 1
    else:
        start_idx = reste * (cc_par_lot + 1) + (num_lot - 1 - reste) * cc_par_lot
        end_idx = start_idx + cc_par_lot
    
    filtered = conventions[start_idx:end_idx]
    
    if not filtered:
        print(f"❌ Lot {lot} vide")
        return
    
    print(f"\n📋 Lot {lot}: {len(filtered)} conventions (indices {start_idx+1}-{end_idx})")
    
    if not dry_run and not skip_confirm:
        confirm = input("\nContinuer ? (oui/non) : ")
        if confirm.lower() not in ['oui', 'o', 'yes', 'y']:
            print("Annulé.")
            return
    
    init_gemini()
    index_data = load_index()
    
    for cc in filtered:
        key = cc['key']
        cc_data = index_data.get(key, {})
        filepath = find_convention_file(cc_data)
        
        if filepath:
            results = extract_convention(filepath, sections=sections, dry_run=dry_run)
            if results and not dry_run:
                save_results(key, results)


# ============================================================================
# MODE INTERACTIF
# ============================================================================

def mode_interactif():
    """Mode interactif avec menus."""
    console.print("\n[bold blue]🔧 EXTRACTION CONVENTIONS COLLECTIVES[/bold blue]\n")
    
    if not API_KEY:
        console.print("[red]❌ Configure ta clé API[/red]")
        return
    
    conventions = list_conventions()
    
    if not conventions:
        console.print("[red]❌ Aucune convention. Lance: python generate_index.py[/red]")
        return
    
    console.print(f"[dim]{len(conventions)} conventions disponibles[/dim]\n")
    
    # Sélection conventions
    choices = ['Une convention', 'Plusieurs conventions', 'Toutes', 'Quitter']
    reponse = inquirer.prompt([inquirer.List('action', message="Que traiter ?", choices=choices)])
    
    if not reponse or reponse['action'] == 'Quitter':
        return
    
    selected = []
    
    if reponse['action'] == 'Toutes':
        selected = conventions
    else:
        options = [f"[{c['idcc']}] {c['key'][:35]}" for c in conventions]
        
        if reponse['action'] == 'Une convention':
            choix = inquirer.prompt([inquirer.List('selected', message="Sélectionne", choices=options)])
            if choix:
                idx = options.index(choix['selected'])
                selected = [conventions[idx]]
        else:
            choix = inquirer.prompt([inquirer.Checkbox('selected', message="Sélectionne (Espace puis Entrée)", choices=options)])
            if choix and choix['selected']:
                indices = [options.index(item) for item in choix['selected']]
                selected = [conventions[i] for i in indices]
    
    if not selected:
        console.print("[yellow]Annulé[/yellow]")
        return
    
    # Sélection sections
    section_choices = ['Toutes les sections', 'Sélectionner']
    reponse = inquirer.prompt([inquirer.List('action', message="Sections ?", choices=section_choices)])
    
    if reponse and reponse['action'] == 'Sélectionner':
        choix = inquirer.prompt([inquirer.Checkbox('selected', message="Sections", choices=SECTIONS)])
        selected_sections = choix['selected'] if choix and choix['selected'] else SECTIONS
    else:
        selected_sections = SECTIONS
    
    # Confirmation
    console.print(f"\n[bold]Récap:[/bold] {len(selected)} CC × {len(selected_sections)} sections = {len(selected) * len(selected_sections)} appels")
    
    confirm = inquirer.prompt([inquirer.Confirm('confirm', message="Lancer ?", default=True)])
    if not confirm or not confirm['confirm']:
        console.print("[yellow]Annulé[/yellow]")
        return
    
    # Extraction
    init_gemini()
    index_data = load_index()
    
    for cc in selected:
        key = cc['key']
        cc_data = index_data.get(key, {})
        filepath = find_convention_file(cc_data)
        
        if filepath:
            results = extract_convention(filepath, sections=selected_sections)
            if results:
                save_results(key, results)
        else:
            print(f"  ⚠️ Fichier non trouvé: {key}")
    
    console.print("\n[bold green]✅ Terminé ![/bold green]")


# ============================================================================
# MAIN
# ============================================================================

def main():
    parser = argparse.ArgumentParser(description="Extraction des conventions collectives")
    parser.add_argument('--list', '-l', action='store_true', help='Liste les conventions')
    parser.add_argument('--cc', type=str, help='Clé(s) (séparées par virgules)')
    parser.add_argument('--cc-range', type=str, help='Plage IDCC (ex: 1-1500)')
    parser.add_argument('--lot', type=str, help='Lot (ex: 1/30)')
    parser.add_argument('--section', '-s', type=str, help='Section(s)')
    parser.add_argument('--all', '-a', action='store_true', help='Tout extraire')
    parser.add_argument('--sans-idcc', action='store_true', help='Sans IDCC uniquement')
    parser.add_argument('--dry-run', '-n', action='store_true', help='Simulation')
    parser.add_argument('--yes', '-y', action='store_true', help='Skip confirmation')
    
    args = parser.parse_args()
    
    if args.list:
        cmd_list()
        return
    
    sections = None
    if args.section:
        sections = [s.strip() for s in args.section.split(',')]
        for s in sections:
            if s not in SECTIONS:
                console.print(f"[red]❌ Section inconnue: {s}[/red]")
                console.print(f"[dim]Valides: {', '.join(SECTIONS)}[/dim]")
                return
    
    if args.all:
        cmd_extract_all(sections, args.dry_run, args.yes)
    elif args.sans_idcc:
        cmd_extract_sans_idcc(sections, args.dry_run, args.yes)
    elif args.lot:
        cmd_extract_lot(args.lot, sections, args.dry_run, args.yes)
    elif args.cc_range:
        cmd_extract_range(args.cc_range, sections, args.dry_run, args.yes)
    elif args.cc:
        keys = [k.strip() for k in args.cc.split(',')]
        cmd_extract(keys, sections, args.dry_run)
    else:
        mode_interactif()


if __name__ == "__main__":
    main()