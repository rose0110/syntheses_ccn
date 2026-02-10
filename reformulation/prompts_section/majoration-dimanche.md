# Extraction : Majoration pour travail du dimanche

## Objectif

Extraire et reformuler les règles conventionnelles relatives au **travail du dimanche** et à sa majoration.

**Tu es un outil de consultation.** Tu récupères l'information et tu la réorganises. C'est tout.

---

## ⚠️ PÉRIMÈTRE STRICT

Cette section concerne **UNIQUEMENT** le travail du dimanche.

### ❌ NE PAS inclure ici :
- Travail de nuit → section `majoration-nuit`
- Travail des jours fériés → section `majoration-ferie`
- Heures supplémentaires → section `heures-supplementaires`

---

## Règles

### Tu dois :
- ✅ Extraire TOUT ce qui concerne le travail du dimanche
- ✅ Reformuler clairement (syntaxe, structure)
- ✅ Distinguer travail occasionnel / habituel
- ✅ Indiquer la référence (article, avenant, date, statut) pour chaque disposition.

### Tu ne dois PAS :
- ❌ Convertir les pourcentages
- ❌ Appliquer le Code du travail si la convention est muette
- ❌ Faire d'analyse ou mentionner l'application de règles non écrites.

### Si la convention ne dit rien sur un thème :
Écrire : **"Non traité par la convention."**

### Si la convention ne contient aucune disposition spécifique sur compensation travail dimanche :
Mentionner **"RAS"** dans le champ `contenu` de la section `majorations`.

---

## Format de sortie

```json
{
  "section": "majoration_dimanche",
  
  "majorations": {
    "traite": true,
    "contenu": [
      {
        "theme": "Travail exceptionnel",
        "texte": "Le travail exceptionnel du dimanche est majoré de 100 %."
      },
      {
        "theme": "Travail habituel",
        "texte": "Pour les salariés travaillant habituellement le dimanche, la majoration est de 50 %."
      },
      {
        "theme": "Définition travail habituel",
        "texte": "Est considéré comme travail habituel le dimanche, le fait de travailler au moins 2 dimanches par mois."
      },
      {
        "theme": "Base de calcul",
        "texte": "La majoration est calculée sur le salaire horaire de base."
      }
    ],
    "articles": ["Art. 19"]
  },

  "repos_compensateur": {
    "traite": true,
    "contenu": [
      {
        "theme": "Repos de remplacement",
        "texte": "Le salarié ayant travaillé le dimanche bénéficie d'un jour de repos dans la semaine suivante."
      },
      {
        "theme": "Délai",
        "texte": "Ce repos doit être pris dans les 15 jours suivant le dimanche travaillé."
      }
    ],
    "articles": []
  },

  "volontariat": {
    "traite": true,
    "contenu": [
      {
        "theme": "Principe",
        "texte": "Le travail du dimanche repose sur le volontariat du salarié."
      },
      {
        "theme": "Refus",
        "texte": "Le refus de travailler le dimanche ne peut constituer une faute ou un motif de licenciement."
      }
    ],
    "articles": []
  },

  "cumul_majorations": {
    "traite": true,
    "contenu": [
      {
        "theme": "Règle de cumul",
        "texte": "La majoration pour travail du dimanche se cumule avec les majorations pour heures supplémentaires et travail de nuit."
      }
    ],
    "articles": []
  },

  "specificites_regionales": {
    "traite": false,
    "contenu": [],
    "articles": []
  }
}
```

---

## Thèmes possibles


**Majorations :**
- Travail exceptionnel
- Travail habituel
- Définition du travail habituel
- Base de calcul

**Repos :**
- Repos de remplacement
- Délai de prise

**Organisation :**
- Volontariat
- Refus
- Autorisation administrative

**Cumul :**
- Règle de cumul avec autres majorations

---

## 📝 Utilisation des tableaux Markdown

**Règle :** L'utilisation de tableaux Markdown dans les champs `texte` est **rarement justifiée** pour cette section.

**Exception :** Si l'information est intrinsèquement tabulaire (ex: taux de majoration différents selon 5 catégories de salariés ou 3 tranches horaires), un tableau peut être utilisé pour garantir l'exhaustivité et la clarté.

**Format d'exemple (si nécessaire) :**
```markdown
| Catégorie | Taux de Majoration |
| :--- | :--- |
| Cadres | 50 % |
| Employés | 25 % |
```

---

## ❌ INTERDIT
- Inclure les majorations nuit/fériés
- Convertir les pourcentages
- Appliquer le Code du travail par défaut

## ✅ OBLIGATOIRE
- Distinguer travail occasionnel / habituel
- Préciser le repos compensateur

---

## Rappel final

⚠️ **JSON uniquement**
⚠️ **Exhaustivité totale**
⚠️ **Reformulation ≠ Interprétation**
⚠️ **Terminologie exacte de la convention**
