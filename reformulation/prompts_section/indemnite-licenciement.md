# Extraction : Indemnité de licenciement

## Objectif

Extraire et reformuler les règles conventionnelles relatives à l'**indemnité de licenciement**.

**Tu es un outil de consultation.** Tu récupères l'information et tu la réorganises. C'est tout.

---

## ⚠️ PÉRIMÈTRE STRICT

Cette section concerne **UNIQUEMENT** l'indemnité de licenciement.

### ❌ NE PAS inclure ici :
- Indemnité de départ à la retraite → section `indemnite-depart-retraite`
- Indemnité de mise à la retraite → section `indemnite-mise-retraite`
- Indemnité de rupture conventionnelle → section `indemnite-rupture-conventionnelle`
- Préavis → section `preavis`

---

## Règles

### Tu dois :
- ✅ Extraire TOUT ce qui concerne l'indemnité de licenciement
- ✅ Reformuler clairement (syntaxe, structure)
- ✅ Distinguer par catégorie si les règles diffèrent

### Tu ne dois PAS :
- ❌ Convertir les formules (garder "1/4 de mois" et non "25%")
- ❌ Calculer des exemples
- ❌ Appliquer le Code du travail si la convention est muette

### Si la convention ne dit rien sur un thème :
Écrire : **"Non traité par la convention."**

---

## 💡 Gestion des Tableaux

Si la règle extraite est un barème ou un tableau (ex: montant de l'indemnité selon l'ancienneté), tu dois :
- Formater ce barème en **tableau Markdown** (avec `|` et `-`)
- Inclure ce tableau **intégralement** dans le champ `texte` de l'objet JSON correspondant.

**Exemple de tableau Markdown :**
| Ancienneté | Indemnité |
|---|---|
| < 5 ans | 1/5 mois/an |
| 5 à 10 ans | 1/4 mois/an |
| > 10 ans | 1/3 mois/an |

---

## Format de sortie

```json
{
  "section": "indemnite_licenciement",
  
  "conditions_ouverture": {
    "traite": true,
    "contenu": [
      {
        "theme": "Ancienneté minimale",
        "texte": "L'indemnité de licenciement est due au salarié justifiant d'au moins 8 mois d'ancienneté ininterrompue."
      },
      {
        "theme": "Exclusions",
        "texte": "L'indemnité n'est pas due en cas de licenciement pour faute grave ou lourde."
      }
    ],
    "articles": ["Art. 30"]
  },

  "calcul_non_cadres": {
    "traite": true,
    "contenu": [
      {
        "theme": "Formule de calcul",
        "texte": "L'indemnité est égale à 1/4 de mois de salaire par année d'ancienneté pour les 10 premières années, puis 1/3 de mois par année au-delà."
      },
      {
        "theme": "Années incomplètes",
        "texte": "L'indemnité est calculée proportionnellement au nombre de mois complets pour les années incomplètes."
      }
    ],
    "articles": ["Art. 31"]
  },

  "calcul_cadres": {
    "traite": true,
    "contenu": [
      {
        "theme": "Formule de calcul",
        "texte": "L'indemnité est égale à 1/3 de mois de salaire par année d'ancienneté, sans distinction selon les tranches."
      },
      {
        "theme": "Plafond",
        "texte": "L'indemnité est plafonnée à 12 mois de salaire."
      }
    ],
    "articles": ["Annexe Cadres"]
  },

  "salaire_reference": {
    "traite": true,
    "contenu": [
      {
        "theme": "Mode de calcul",
        "texte": "Le salaire de référence est calculé selon la formule la plus avantageuse pour le salarié : soit la moyenne des 12 derniers mois, soit la moyenne des 3 derniers mois (les primes annuelles étant prises en compte au prorata)."
      },
      {
        "theme": "Éléments inclus",
        "texte": "Sont pris en compte le salaire de base, les primes et avantages en nature."
      },
      {
        "theme": "Éléments exclus",
        "texte": "Sont exclus les remboursements de frais professionnels."
      }
    ],
    "articles": []
  },

  "anciennete": {
    "traite": true,
    "contenu": [
      {
        "theme": "Point de départ",
        "texte": "L'ancienneté s'apprécie à la date d'envoi de la lettre de licenciement."
      },
      {
        "theme": "Périodes prises en compte",
        "texte": "Les périodes de suspension du contrat pour maladie professionnelle ou accident du travail sont intégralement prises en compte."
      }
    ],
    "articles": []
  },

  "cas_particuliers": {
    "traite": true,
    "contenu": [
      {
        "theme": "Licenciement économique",
        "texte": "En cas de licenciement pour motif économique, une majoration de 20% de l'indemnité est accordée aux salariés de plus de 50 ans."
      },
      {
        "theme": "Inaptitude AT/MP",
        "texte": "En cas de licenciement pour inaptitude consécutive à un accident du travail ou une maladie professionnelle, l'indemnité est doublée."
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

**Conditions :**
- Ancienneté minimale
- Exclusions (faute grave, lourde)
- Catégories concernées

**Calcul :**
- Formule de calcul
- Années incomplètes
- Plafond
- Plancher

**Salaire de référence :**
- Mode de calcul
- Période de référence
- Éléments inclus
- Éléments exclus

**Ancienneté :**
- Point de départ
- Périodes prises en compte
- Périodes exclues

**Cas particuliers :**
- Licenciement économique
- Inaptitude AT/MP
- Temps partiel
- Salariés protégés

---

## ❌ INTERDIT
- Convertir les formules en pourcentages
- Calculer des exemples chiffrés
- Appliquer le Code du travail par défaut

## ✅ OBLIGATOIRE
- Distinguer cadres / non-cadres si règles différentes
- Préciser le salaire de référence
- Indiquer les cas particuliers

---

## Rappel final

⚠️ **JSON uniquement**
⚠️ **Exhaustivité totale**
⚠️ **Reformulation ≠ Interprétation**
