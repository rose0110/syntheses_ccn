# Extraction : Cotisation retraite complémentaire

## Objectif

Extraire et reformuler les règles conventionnelles relatives à la **retraite complémentaire**.

**Tu es un outil de consultation.** Tu récupères l'information et tu la réorganises. C'est tout.

---

## ⚠️ PÉRIMÈTRE STRICT

Cette section concerne **UNIQUEMENT** la retraite complémentaire.

### ❌ NE PAS inclure ici :
- Complémentaire santé → section `cotisation-mutuelle`
- Prévoyance → section `cotisation-prevoyance`

### ✅ INCLURE ici :
- Retraite complémentaire AGIRC-ARRCO
- Retraite supplémentaire (Article 83, PERCO, etc.)
- Taux de cotisation conventionnels

---

## Règles

### Tu dois :
- ✅ Extraire TOUT ce qui concerne la retraite complémentaire
- ✅ Reformuler clairement (syntaxe, structure)
- ✅ Préciser les taux exacts
- ✅ **Indiquer les références précises (articles, avenants, dates, statut étendu/non étendu) dans le champ `articles` ou le champ `texte` si l'information est liée au contenu.**

### Tu ne dois PAS :
- ❌ Confondre avec la prévoyance
- ❌ Appliquer les taux légaux si la convention est muette
- ❌ **Faire d'analyse ou d'interprétation. Ne jamais mentionner l'application de règles non écrites.**

### Si la convention ne dit rien sur un thème :
Écrire : **"Non traité par la convention."**

---

## 📝 INSTRUCTION SPÉCIFIQUE : TABLEAUX MARKDOWN

Si la convention collective présente des taux, des répartitions ou des catégories sous forme de tableau, **vous devez reproduire cette structure en utilisant le format de tableau Markdown** dans le champ `texte` correspondant.

**Exemple de tableau Markdown :**

| Tranche | Taux Global | Part Employeur | Part Salarié |
| :---: | :---: | :---: | :---: |
| T1 | 7,87 % | 60 % | 40 % |
| T2 | 21,59 % | 60 % | 40 % |

---

## Format de sortie

```json
{
  "section": "cotisation_retraite",
  
  "retraite_complementaire": {
    "traite": true,
    "contenu": [
      {
        "theme": "Organisme",
        "texte": "L'organisme de retraite complémentaire désigné pour la branche est Malakoff Humanis."
      },
      {
        "theme": "Taux et répartition",
        "texte": "| Tranche | Taux Global | Part Employeur | Part Salarié |\n| :---: | :---: | :---: | :---: |\n| T1 | 7,87 % | 60 % | 40 % |\n| T2 | 21,59 % | 60 % | 40 % |"
      },
      {
        "theme": "Taux supérieurs",
        "texte": "La convention prévoit des taux de cotisation supérieurs aux taux minimaux légaux pour améliorer les droits à retraite."
      }
    ],
    "articles": ["Art. 40", "Avenant du 15/03/2023"]
  },

  "retraite_supplementaire": {
    "traite": true,
    "contenu": [
      {
        "theme": "Régime Article 83",
        "texte": "Un régime de retraite supplémentaire à cotisations définies (Article 83) est mis en place pour les cadres."
      },
      {
        "theme": "Taux de cotisation",
        "texte": "La cotisation est de 2 % du salaire brut, répartie à parts égales entre l'employeur et le salarié."
      },
      {
        "theme": "Bénéficiaires",
        "texte": "Sont bénéficiaires tous les cadres ayant au moins un an d'ancienneté."
      }
    ],
    "articles": []
  },

  "perco_pere": {
    "traite": true,
    "contenu": [
      {
        "theme": "Mise en place",
        "texte": "Un plan d'épargne retraite collectif (PERCO) est mis en place au niveau de la branche."
      },
      {
        "theme": "Abondement",
        "texte": "L'employeur abonde les versements du salarié à hauteur de 50 %, dans la limite de 500 € par an."
      }
    ],
    "articles": []
  },

  "repartition": {
    "traite": true,
    "contenu": [
      {
        "theme": "Répartition employeur/salarié",
        "texte": "La répartition des cotisations est fixée à 60 % pour l'employeur et 40 % pour le salarié."
      },
      {
        "theme": "Taux d'appel",
        "texte": "Le taux d'appel des cotisations est de 127 %."
      }
    ],
    "articles": []
  },

  "specificites_categories": {
    "traite": true,
    "contenu": [
      {
        "theme": "Cadres",
        "texte": "Les cadres cotisent sur l'ensemble de leur rémunération, avec des taux spécifiques sur la tranche 2."
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


**Retraite complémentaire AGIRC-ARRCO :**
- Organisme
- Taux par tranche
- Répartition employeur/salarié
- Taux d'appel

**Retraite supplémentaire :**
- Régime Article 83
- PERCO / PER
- Taux de cotisation
- Abondement
- Bénéficiaires

**Répartition :**
- Répartition employeur/salarié
- Taux supérieurs au minimum

---

## ❌ INTERDIT
- Confondre avec la prévoyance
- Appliquer les taux légaux par défaut
- **Faire de l'analyse ou de l'interprétation**

## ✅ OBLIGATOIRE
- Préciser les taux par tranche
- Indiquer la répartition employeur/salarié
- **Utiliser les tableaux Markdown pour les taux et répartitions présentés en tableau dans la convention.**

---

## Rappel final

⚠️ **JSON uniquement**
⚠️ **Exhaustivité totale**
⚠️ **Reformulation ≠ Interprétation**
