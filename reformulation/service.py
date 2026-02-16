"""
Service de reformulation utilisant 2 IA en parallèle (Gemini + DeepSeek)
"""
import os
import json
import time
import asyncio
import logging
from pathlib import Path
from typing import Dict, List, Optional
from bs4 import BeautifulSoup
import re
import httpx
from google import generativeai as genai

logger = logging.getLogger(__name__)

# Configuration
BASE_DIR = Path(__file__).parent
PROMPTS_DIR = BASE_DIR / "prompts_section"
TEMPERATURE = 0.1
API_DELAY = 0.5

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
    """Service pour reformuler les conventions avec 2 IA en parallèle"""
    
    def __init__(self):
        self.gemini_api_key = os.getenv("GEMINI_API_KEY")
        self.deepseek_api_key = os.getenv("DEEPSEEK_API_KEY")
        
        if not self.gemini_api_key:
            raise ValueError("GEMINI_API_KEY not found in environment")
        if not self.deepseek_api_key:
            raise ValueError("DEEPSEEK_API_KEY not found in environment")
        
        # Init Gemini
        genai.configure(api_key=self.gemini_api_key)
        self.gemini_model = genai.GenerativeModel(
            "gemini-2.5-flash",
            generation_config={"temperature": TEMPERATURE}
        )
        
        logger.info("ReformulationService initialized")
    
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
        """Charge le prompt d'une section"""
        prompt_file = PROMPTS_DIR / f"{section}.md"
        
        if not prompt_file.exists():
            raise FileNotFoundError(f"Prompt file not found: {prompt_file}")
        
        return prompt_file.read_text(encoding='utf-8')
    
    async def call_gemini(self, prompt: str, content: str) -> Optional[Dict]:
        """Appelle Gemini AI"""
        try:
            full_prompt = f"{SYSTEM_PROMPT}\n\n{prompt}\n\n## CONTENU À ANALYSER\n\n{content}"
            
            response = self.gemini_model.generate_content(full_prompt)
            response_text = response.text.strip()
            
            # Retirer markdown si présent
            if response_text.startswith("```"):
                response_text = response_text.split("```json")[1].split("```")[0].strip()
            
            return json.loads(response_text)
        
        except Exception as e:
            logger.error(f"Gemini API error: {e}")
            return None
    
    async def call_deepseek(self, prompt: str, content: str) -> Optional[Dict]:
        """Appelle DeepSeek AI"""
        try:
            full_prompt = f"{SYSTEM_PROMPT}\n\n{prompt}\n\n## CONTENU À ANALYSER\n\n{content}"
            
            async with httpx.AsyncClient(timeout=60.0) as client:
                response = await client.post(
                    "https://api.deepseek.com/v1/chat/completions",
                    headers={
                        "Authorization": f"Bearer {self.deepseek_api_key}",
                        "Content-Type": "application/json"
                    },
                    json={
                        "model": "deepseek-chat",
                        "messages": [
                            {"role": "system", "content": SYSTEM_PROMPT},
                            {"role": "user", "content": f"{prompt}\n\n## CONTENU À ANALYSER\n\n{content}"}
                        ],
                        "temperature": TEMPERATURE
                    }
                )
                
                if response.status_code != 200:
                    logger.error(f"DeepSeek API error: {response.status_code} - {response.text}")
                    return None
                
                result = response.json()
                response_text = result['choices'][0]['message']['content'].strip()
                
                # Retirer markdown si présent
                if response_text.startswith("```"):
                    response_text = response_text.split("```json")[1].split("```")[0].strip()
                
                return json.loads(response_text)
        
        except Exception as e:
            logger.error(f"DeepSeek API error: {e}")
            return None
    
    async def reformulate_convention(self, raw_html: str, status_callback=None) -> Dict[str, Dict]:
        """
        Reformule une convention avec les 2 IA en parallèle
        
        Returns:
            {
                "gemini": {...},
                "deepseek": {...}
            }
        """
        content = self.clean_html(raw_html)
        
        if not content:
            raise ValueError("No content to reformulate")
        
        results_gemini = {}
        results_deepseek = {}
        
        # Pour chaque section
        total_sections = len(SECTIONS)
        for i, section in enumerate(SECTIONS):
            logger.info(f"Processing section: {section}")
            
            if status_callback:
                status_callback(section, i + 1, total_sections)
            
            try:
                # Charger le prompt
                prompt = self.load_prompt(section)
                
                # Appeler les 2 IA en PARALLÈLE
                gemini_task = self.call_gemini(prompt, content)
                deepseek_task = self.call_deepseek(prompt, content)
                
                results_list = await asyncio.gather(gemini_task, deepseek_task, return_exceptions=True)
                
                gemini_result, deepseek_result = results_list
                
                # Check Gemini result
                if isinstance(gemini_result, Exception):
                    logger.error(f"Gemini error for section {section}: {gemini_result}")
                elif gemini_result:
                    results_gemini[section] = gemini_result
                
                # Check DeepSeek result
                if isinstance(deepseek_result, Exception):
                    logger.error(f"DeepSeek error for section {section}: {deepseek_result}")
                elif deepseek_result:
                    results_deepseek[section] = deepseek_result
                
                # Petit délai pour éviter rate limits même en parallèle
                await asyncio.sleep(API_DELAY)
            
            except Exception as e:
                logger.error(f"Error processing section {section}: {e}")
                continue
        
        return {
            "gemini": results_gemini,
            "deepseek": results_deepseek
        }
