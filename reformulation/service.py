import os
import json
import asyncio
import logging
from pathlib import Path
from typing import Dict, Optional
import re
import httpx
from google import generativeai as genai

logger = logging.getLogger(__name__)

BASE_DIR = Path(__file__).parent
PROMPTS_DIR = BASE_DIR / "prompts_section"
TEMP = 0.1
DELAY = 0.5

# Liste des 34 sections
SECTIONS = [
    "informations-generales",
    "periode-essai",
    "delai-prevenance",
    "preavis",
    "indemnite-licenciement",
    "indemnite-depart-retraite",
    "indemnite-mise-retraite",
    "indemnite-rupture-conventionnelle",
    "indemnite-precarite",
    "classification",
    "grille-remuneration",
    "durees-travail",
    "heures-supplementaires",
    "majoration-nuit",
    "majoration-dimanche",
    "majoration-ferie",
    "temps-partiel",
    "forfait-jours",
    "amenagement-temps-travail",
    "conges-payes",
    "evenements-familiaux",
    "maladie",
    "maternite-paternite",
    "accident-travail",
    "cet",
    "apprenti",
    "stagiaire",
    "contrat-professionnalisation",
    "cotisation-retraite",
    "cotisation-prevoyance",
    "cotisation-mutuelle",
    "paritarisme-financement",
    "contributions-formation",
    "primes-indemnites-avantages",
]

# System Prompt
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

## � FORMAT DE SORTIE

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



class ReformulationService:
    def __init__(self):
        self.gem_key = os.getenv("GEMINI_API_KEY")
        self.ds_key = os.getenv("DEEPSEEK_API_KEY")
        
        if not self.gem_key or not self.ds_key:
            raise ValueError("Missing API keys")
        
        genai.configure(api_key=self.gem_key)
        self.gem_model = genai.GenerativeModel(
            "gemini-2.5-flash",
            generation_config={"temperature": TEMP}
        )

    
    def clean_html(self, raw_html: str) -> str:
        """Nettoie le HTML (logique identique script original)"""
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
    
    def load_prompt(self, section: str) -> str:
        p_file = PROMPTS_DIR / f"{section}.md"
        if not p_file.exists():
            raise FileNotFoundError(f"No prompt for {section}")
        return p_file.read_text(encoding='utf-8')
    
    async def call_gemini(self, prompt: str, content: str) -> Optional[Dict]:
        try:
            full = f"{SYSTEM_PROMPT}\n\n{prompt}\n\n## CONTENU\n\n{content}"
            resp = self.gem_model.generate_content(full)
            txt = resp.text.strip()
            
            if txt.startswith("```"):
                txt = txt.split("```json")[1].split("```")[0].strip()
            
            return json.loads(txt)
        except Exception as e:
            logger.error(f"Gemini error: {e}")
            return None
    
    async def call_deepseek(self, prompt: str, content: str) -> Optional[Dict]:
        try:
            async with httpx.AsyncClient(timeout=60.0) as client:
                resp = await client.post(
                    "https://api.deepseek.com/v1/chat/completions",
                    headers={
                        "Authorization": f"Bearer {self.ds_key}",
                        "Content-Type": "application/json"
                    },
                    json={
                        "model": "deepseek-chat",
                        "messages": [
                            {"role": "system", "content": SYSTEM_PROMPT},
                            {"role": "user", "content": f"{prompt}\n\n## DO IT: \n\n{content}"}
                        ],
                        "temperature": TEMP
                    }
                )
                
                if resp.status_code != 200:
                    logger.error(f"DS Error: {resp.status_code}")
                    return None
                
                txt = resp.json()['choices'][0]['message']['content'].strip()
                if txt.startswith("```"):
                    txt = txt.split("```json")[1].split("```")[0].strip()
                
                return json.loads(txt)
        except Exception as e:
            logger.error(f"DS Exception: {e}")
            return None
    
    async def reformulate_convention(self, raw_html: str, status_cb=None) -> Dict[str, Dict]:
        content = self.clean_html(raw_html)
        if not content:
            raise ValueError("Empty content")
        
        res_gem, res_ds = {}, {}
        
        for i, section in enumerate(SECTIONS):
            logger.info(f">> {section}")
            if status_cb: status_cb(section, i + 1, len(SECTIONS))
            
            try:
                prompt = self.load_prompt(section)
                
                # Parallel execution
                task_g = self.call_gemini(prompt, content)
                task_d = self.call_deepseek(prompt, content)
                
                results = await asyncio.gather(task_g, task_d, return_exceptions=True)
                rg, rd = results
                
                if not isinstance(rg, Exception) and rg:
                    res_gem[section] = rg
                
                if not isinstance(rd, Exception) and rd:
                    res_ds[section] = rd
                
                await asyncio.sleep(DELAY)

            except Exception as e:
                logger.error(f"Fail {section}: {e}")
                continue
        
        return {"gemini": res_gem, "deepseek": res_ds}
