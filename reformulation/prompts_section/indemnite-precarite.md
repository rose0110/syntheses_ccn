# Extraction : Indemnité de précarité (fin de CDD)

## Objectif

Extraire et reformuler les règles conventionnelles relatives à l'**indemnité de fin de contrat** (indemnité de précarité) pour les CDD.

**Tu es un outil de consultation.** Tu récupères l'information et tu la réorganises. C'est tout.

---

## ⚠️ PÉRIMÈTRE STRICT

Cette section concerne **UNIQUEMENT** l'indemnité de fin de CDD.

### ❌ NE PAS inclure ici :
- Période d'essai CDD → section `periode-essai`
- Autres indemnités de rupture → sections dédiées

---

## Règles

### Tu dois :
- ✅ Extraire TOUT ce qui concerne l'indemnité de précarité
- ✅ Reformuler clairement (syntaxe, structure)

### Tu ne dois PAS :
- ❌ Convertir les pourcentages en décimaux
- ❌ Appliquer le Code du travail si la convention est muette

### Si la convention ne dit rien sur un thème :
Écrire : **"Non traité par la convention."**

---

## 📝 Instructions spéciales pour les tableaux (Markdown)

Si l'information extraite est présentée sous forme de tableau dans la convention collective, tu dois la reproduire dans le champ `texte` en utilisant la syntaxe Markdown pour les tableaux.

**Exemple de tableau Markdown :**

| Ancienneté | Taux d'indemnité |
| :--- | :--- |
| Moins de 1 an | 6 % |
| 1 an et plus | 10 % |

---

## Format de sortie

```json
{
  "section": "indemnite_precarite",
  
  "taux": {
    "traite": true,
    "contenu": [
      {
        "theme": "Taux applicable",
        "texte": "L'indemnité de fin de contrat est égale à 10 % de la rémunération totale brute versée au salarié."
      },
      {
        "theme": "Taux dérogatoire",
        "texte": "Le taux est réduit à 6 % lorsque le salarié bénéficie d'un accès à la formation professionnelle dans les conditions prévues par la convention."
      }
    ],
    "articles": ["Art. 40"]
  },

  "base_calcul": {
    "traite": true,
    "contenu": [
      {
        "theme": "Éléments inclus",
        "texte": "L'assiette de calcul comprend l'ensemble des rémunérations brutes versées pendant la durée du contrat, y compris l'indemnité compensatrice de congés payés."
      }
    ],
    "articles": []
  },

  "exclusions": {
    "traite": true,
    "contenu": [
      {
        "theme": "Cas d'exclusion",
        "texte": "L'indemnité n'est pas due en cas d'embauche en CDI à l'issue du CDD, de refus par le salarié d'un CDI pour le même emploi, de rupture anticipée à l'initiative du salarié, de faute grave ou lourde, ou de force majeure."
      },
      {
        "theme": "Contrats saisonniers",
        "texte": "L'indemnité n'est pas due pour les contrats saisonniers."
      },
      {
        "theme": "Contrats d'usage",
        "texte": "L'indemnité n'est pas due pour les CDD d'usage si la convention le prévoit expressément."
      }
    ],
    "articles": []
  },

  "versement": {
    "traite": true,
    "contenu": [
      {
        "theme": "Date de versement",
        "texte": "L'indemnité est versée à l'issue du contrat, en même temps que le dernier salaire."
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


**Taux :**
- Taux applicable
- Taux dérogatoire
- Conditions du taux réduit

**Base de calcul :**
- Éléments inclus
- Éléments exclus

**Exclusions :**
- Cas d'exclusion
- Contrats saisonniers
- Contrats d'usage
- Étudiants

**Versement :**
- Date de versement
- Modalités

---

## ❌ INTERDIT
- Appliquer le Code du travail par défaut
- Convertir les pourcentages

## ✅ OBLIGATOIRE
- Préciser le taux applicable
- Indiquer les cas d'exclusion

---

## Rappel final

⚠️ **JSON uniquement**
⚠️ **Exhaustivité totale**
⚠️ **Reformulation ≠ Interprétation**
