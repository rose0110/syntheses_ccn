# Extraction : Délai de prévenance

## Objectif

Extraire et reformuler les règles conventionnelles relatives aux **délais de prévenance** en cas de rupture de la période d'essai.

**Tu es un outil de consultation.** Tu récupères l'information et tu la réorganises. C'est tout.

---

## ⚠️ PÉRIMÈTRE STRICT

Cette section concerne **UNIQUEMENT** les délais de prévenance pendant la période d'essai.

### ❌ NE PAS inclure ici :
- Durée de la période d'essai → section `periode-essai`
- Préavis de démission/licenciement → section `preavis`

### ✅ INCLURE ici :
- Délai de prévenance à l'initiative de l'employeur
- Délai de prévenance à l'initiative du salarié
- Conséquences du non-respect

---

## Règles

### Tu dois :
- ✅ Extraire TOUT ce qui concerne les délais de prévenance
- ✅ Reformuler clairement (syntaxe, structure)
- ✅ Distinguer initiative employeur / initiative salarié
- ✅ Utiliser des **tableaux Markdown** pour structurer les informations complexes (ex: barèmes de délais de prévenance selon l'ancienneté) dans les champs `texte`.
- ✅ Le tableau doit être le **seul contenu** du champ `texte` s'il est utilisé.

### Tu ne dois PAS :
- ❌ Confondre avec le préavis de licenciement/démission
- ❌ Appliquer le Code du travail si la convention est muette

### Si la convention ne dit rien sur un thème :
Écrire : **"Non traité par la convention."**

---

## Format de sortie

```json
{
  "section": "delai_prevenance",
  
  "initiative_employeur": {
    "traite": true,
    "contenu": [
      {
        "theme": "Délais selon présence",
        "texte": "| Ancienneté | Délai de prévenance |\n|---|---|\n| Moins de 8 jours | 24 heures |\n| Entre 8 jours et 1 mois | 48 heures |\n| Après 1 mois | 2 semaines |\n| Après 3 mois | 1 mois |"
      },
      {
        "theme": "Point de départ",
        "texte": "Le délai court à compter de la notification de la rupture."
      }
    ],
    "articles": ["Art. 7"]
  },

  "initiative_salarie": {
    "traite": true,
    "contenu": [
      {
        "theme": "Délais selon présence",
        "texte": "Le salarié doit respecter un délai de prévenance de 24 heures si sa présence est inférieure à 8 jours, 48 heures au-delà."
      }
    ],
    "articles": []
  },

  "non_respect": {
    "traite": true,
    "contenu": [
      {
        "theme": "Indemnité compensatrice",
        "texte": "Le non-respect du délai de prévenance par l'employeur ouvre droit à une indemnité compensatrice égale au salaire correspondant à la durée du délai non effectué."
      },
      {
        "theme": "Prolongation interdite",
        "texte": "La période d'essai ne peut être prolongée du fait de la durée du délai de prévenance."
      }
    ],
    "articles": []
  },

  "specificites_cdd": {
    "traite": true,
    "contenu": [
      {
        "theme": "Règle applicable",
        "texte": "Les délais de prévenance s'appliquent également aux CDD comportant une période d'essai d'au moins une semaine."
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


- Délais selon présence
- Point de départ du délai
- Formalisme de la notification
- Indemnité compensatrice
- Prolongation interdite
- Spécificités CDD
- Spécificités par catégorie

---

## ❌ INTERDIT
- Confondre avec le préavis (hors période d'essai)
- Appliquer le Code du travail par défaut

## ✅ OBLIGATOIRE
- Distinguer initiative employeur / initiative salarié
- Préciser les conséquences du non-respect

---

## Rappel final

⚠️ **JSON uniquement**
⚠️ **Exhaustivité totale**
⚠️ **Reformulation ≠ Interprétation**
