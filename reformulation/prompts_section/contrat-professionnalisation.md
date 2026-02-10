# Extraction : Contrat de professionnalisation

## Objectif

Extraire et reformuler les règles conventionnelles relatives au **contrat de professionnalisation**.

**Tu es un outil de consultation.** Tu récupères l'information et tu la réorganises. C'est tout.

---

## ⚠️ PÉRIMÈTRE STRICT

Cette section concerne **UNIQUEMENT** le contrat de professionnalisation.

### ❌ NE PAS inclure ici :
- Contrat d'apprentissage → section `apprenti`
- Stagiaires → section `stagiaire`

---

## Règles

### Tu dois :
- ✅ Si une grille de rémunération est extraite, la formater en **tableau Markdown** dans le champ `texte` correspondant.
- ✅ Utiliser le format français pour les chiffres et pourcentages (ex: 12,5 %).
- ✅ Appliquer les règles générales : extraction infos en vigueur, terminologie exacte, pas d'introduction ni de conclusion.
- ✅ Extraire TOUT ce qui concerne le contrat de professionnalisation
- ✅ Reformuler clairement (syntaxe, structure)
- ✅ Préciser les taux de rémunération exacts

### Tu ne dois PAS :
- ❌ Recopier la grille légale si la convention ne prévoit pas de règle spécifique.
- ❌ Faire d'analyse ou mentionner l'application de règles non écrites.
- ❌ Appliquer les minimums légaux si la convention prévoit mieux
- ❌ Confondre avec le contrat d'apprentissage

### Si la convention ne dit rien sur un thème :
- Si le thème est abordé mais sans disposition spécifique, écrire : **"La convention ne prévoit rien à ce sujet."**
- Si le thème n'est pas abordé du tout, écrire : **"Non traité par la convention."**
- Si la convention ne mentionne absolument rien sur les contrats de professionnalisation, mettre `traite: false` et `contenu: []` pour la section.

---

## Format de sortie

```json
{
  "section": "contrat_professionnalisation",
  
  "remuneration": {
    "traite": true,
    "contenu": [
      {
        "theme": "Grille de rémunération spécifique",
        "texte": "Si une grille spécifique est prévue, elle doit être présentée sous forme de tableau Markdown. Exemple :
| Âge | Niveau Qualif. | % Base | Base |
| :--- | :--- | :--- | :--- |
| Moins de 21 ans | Inférieur Bac | 55 % | SMIC |
| Moins de 21 ans | Égal ou Supérieur Bac | 65 % | SMIC |
| 21 à 25 ans | Inférieur Bac | 70 % | SMIC |
| 21 à 25 ans | Égal ou Supérieur Bac | 80 % | SMIC |
| 26 ans et plus | Tous | 100 % | SMIC ou SMC (si plus favorable) |"
      },
      {
        "theme": "Majoration conventionnelle",
        "texte": "La convention prévoit une majoration de 5 points par rapport aux minima légaux."
      }
    ],
    "articles": ["Art. 52"]
  },

  "duree_contrat": {
    "traite": true,
    "contenu": [
      {
        "theme": "Type de contrat",
        "texte": "Le contrat de professionnalisation peut être conclu en CDD ou CDI."
      },
      {
        "theme": "Durée de l'action de professionnalisation",
        "texte": "La durée de l'action de professionnalisation est comprise entre 6 et 12 mois."
      },
      {
        "theme": "Durée étendue",
        "texte": "La durée peut être portée à 24 mois pour les publics prioritaires ou les qualifications spécifiques définies par la branche."
      }
    ],
    "articles": []
  },

  "formation": {
    "traite": true,
    "contenu": [
      {
        "theme": "Durée minimale",
        "texte": "La durée des actions de formation est comprise entre 15 % et 25 % de la durée du contrat ou de l'action de professionnalisation, sans pouvoir être inférieure à 150 heures."
      },
      {
        "theme": "Durée étendue",
        "texte": "La durée de formation peut être portée au-delà de 25 % pour les qualifications définies comme prioritaires par la branche."
      },
      {
        "theme": "Qualifications visées",
        "texte": "Le contrat vise l'obtention d'une qualification enregistrée au RNCP, d'un CQP ou d'une qualification reconnue par la branche."
      }
    ],
    "articles": []
  },

  "tuteur": {
    "traite": true,
    "contenu": [
      {
        "theme": "Désignation",
        "texte": "Un tuteur est désigné pour accompagner le salarié en contrat de professionnalisation."
      },
      {
        "theme": "Conditions",
        "texte": "Le tuteur doit justifier d'une expérience professionnelle de 2 ans minimum dans une qualification en rapport avec l'objectif visé."
      },
      {
        "theme": "Nombre de bénéficiaires",
        "texte": "Chaque tuteur peut accompagner au maximum 3 salariés."
      }
    ],
    "articles": []
  },

  "periode_essai": {
    "traite": true,
    "contenu": [
      {
        "theme": "Règles applicables",
        "texte": "La période d'essai du contrat de professionnalisation suit les règles de droit commun applicables au type de contrat (CDD ou CDI)."
      }
    ],
    "articles": []
  },

  "publics_prioritaires": {
    "traite": true,
    "contenu": [
      {
        "theme": "Liste des publics",
        "texte": "Sont considérés comme publics prioritaires les demandeurs d'emploi de longue durée, les bénéficiaires du RSA, de l'ASS ou de l'AAH, et les personnes ayant bénéficié d'un contrat unique d'insertion."
      },
      {
        "theme": "Avantages",
        "texte": "Les publics prioritaires bénéficient d'une durée d'action de professionnalisation pouvant aller jusqu'à 24 mois."
      }
    ],
    "articles": []
  },

  "financement": {
    "traite": true,
    "contenu": [
      {
        "theme": "Prise en charge OPCO",
        "texte": "Les coûts pédagogiques sont pris en charge par l'OPCO selon les niveaux définis par la branche."
      },
      {
        "theme": "Forfait horaire",
        "texte": "Le forfait de prise en charge est de 15 € par heure de formation."
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

**Rémunération :**
- Base de calcul
- Grille par âge
- Majoration conventionnelle

**Durée :**
- Type de contrat (CDD/CDI)
- Durée de l'action
- Durée étendue

**Formation :**
- Durée minimale
- Durée étendue
- Qualifications visées

**Tuteur :**
- Désignation
- Conditions
- Nombre de bénéficiaires

**Publics prioritaires :**
- Liste
- Avantages

**Financement :**
- Prise en charge OPCO
- Forfait horaire

---

## ❌ INTERDIT
- Confondre avec le contrat d'apprentissage
- Appliquer les minimums légaux si la convention prévoit mieux

## ✅ OBLIGATOIRE
- Préciser les taux de rémunération
- Distinguer par âge et niveau de qualification

---

## Rappel final

⚠️ **JSON uniquement**
⚠️ **Exhaustivité totale**
⚠️ **Reformulation ≠ Interprétation**
