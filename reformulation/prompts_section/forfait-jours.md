# Extraction : Forfait jours

## Objectif

Extraire et reformuler les règles conventionnelles relatives au **forfait annuel en jours**.

**Tu es un outil de consultation.** Tu récupères l'information et tu la réorganises. C'est tout.

---

## ⚠️ PÉRIMÈTRE STRICT

Cette section concerne **UNIQUEMENT** le forfait annuel en jours.

### ❌ NE PAS inclure ici :
- Durées du travail (hors forfait) → section `durees-travail`
- Heures supplémentaires → section `heures-supplementaires`
- Forfait heures → à traiter distinctement si présent

---

## Règles

### Tu dois :
- ✅ Extraire TOUT ce qui concerne le forfait jours
- ✅ Reformuler clairement (syntaxe, structure)
- ✅ **Présenter uniquement les modalités en vigueur.**
- ✅ **Utiliser la terminologie exacte de la convention.**

### Tu ne dois PAS :
- ❌ Appliquer le Code du travail si la convention est muette
- ❌ Faire d'analyse, de projection ou mentionner des règles non écrites.

### Si la convention ne dit rien sur un thème :
Écrire : **"Non traité par la convention."**

---

## 📝 Utilisation des Tableaux Markdown

Si l'information extraite est présentée sous forme de tableau (ex: barème de majoration, grille de classification, etc.), tu dois la retranscrire en utilisant le format **Markdown Table** à l'intérieur du champ `texte`.

### Exemple de Tableau Markdown (à utiliser dans le champ "texte") :

| Ancienneté | Taux de Majoration |
| :--- | :--- |
| 0 à 5 ans | 10% |
| 5 à 10 ans | 15% |
| > 10 ans | 20% |

---

## Format de sortie

```json
{
  "section": "forfait_jours",
  
  "salaries_eligibles": {
    "traite": true,
    "contenu": [
      {
        "theme": "Catégories concernées",
        "texte": "Peuvent conclure une convention de forfait en jours les cadres disposant d'une autonomie dans l'organisation de leur emploi du temps et dont la nature des fonctions ne les conduit pas à suivre l'horaire collectif."
      },
      {
        "theme": "Conditions d'autonomie",
        "texte": "Sont concernés les cadres à partir du niveau VII de la classification."
      },
      {
        "theme": "Non-cadres autonomes",
        "texte": "Les salariés non-cadres dont la durée du temps de travail ne peut être prédéterminée et qui disposent d'une réelle autonomie peuvent également bénéficier du forfait jours."
      }
    ],
    "articles": ["Art. 22"]
  },

  "nombre_jours": {
    "traite": true,
    "contenu": [
      {
        "theme": "Plafond annuel",
        "texte": "Le nombre de jours travaillés est fixé à 218 jours par an, journée de solidarité incluse."
      },
      {
        "theme": "Période de référence",
        "texte": "La période de référence est l'année civile, du 1er janvier au 31 décembre."
      },
      {
        "theme": "Forfait réduit",
        "texte": "Un forfait en jours réduit peut être convenu pour un nombre de jours inférieur à 218."
      }
    ],
    "articles": []
  },

  "jours_repos": {
    "traite": true,
    "contenu": [
      {
        "theme": "Calcul des JRS",
        "texte": "Le nombre de jours de repos supplémentaires (JRS) résulte du calcul : 365 jours - 218 jours travaillés - jours fériés chômés - 25 jours de CP - 104 jours de week-end."
      },
      {
        "theme": "Modalités de prise",
        "texte": "Les JRS sont pris par journées ou demi-journées, à l'initiative du salarié pour moitié et à l'initiative de l'employeur pour l'autre moitié."
      }
    ],
    "articles": []
  },

  "renonciation_jours_repos": {
    "traite": true,
    "contenu": [
      {
        "theme": "Possibilité",
        "texte": "Le salarié peut, avec l'accord de l'employeur, renoncer à une partie de ses jours de repos en contrepartie d'une majoration de salaire."
      },
      {
        "theme": "Plafond",
        "texte": "Le nombre maximal de jours travaillés ne peut excéder 235 jours."
      },
      {
        "theme": "Majoration",
        "texte": "Les jours travaillés au-delà de 218 jours sont majorés de 10 %."
      }
    ],
    "articles": []
  },

  "convention_individuelle": {
    "traite": true,
    "contenu": [
      {
        "theme": "Formalisme",
        "texte": "La mise en place du forfait jours nécessite la conclusion d'une convention individuelle écrite avec le salarié."
      },
      {
        "theme": "Mentions obligatoires",
        "texte": "La convention précise le nombre de jours travaillés, la rémunération forfaitaire et les modalités de suivi."
      }
    ],
    "articles": []
  },

  "suivi_charge_travail": {
    "traite": true,
    "contenu": [
      {
        "theme": "Entretien annuel",
        "texte": "Le salarié bénéficie d'un entretien annuel portant sur sa charge de travail, l'organisation du travail, l'articulation vie professionnelle/vie personnelle et sa rémunération."
      },
      {
        "theme": "Décompte des jours",
        "texte": "Un document de contrôle faisant apparaître le nombre et la date des journées travaillées est établi."
      },
      {
        "theme": "Droit d'alerte",
        "texte": "Le salarié peut alerter son employeur s'il estime que sa charge de travail est incompatible avec le respect des temps de repos."
      }
    ],
    "articles": []
  },

  "temps_repos": {
    "traite": true,
    "contenu": [
      {
        "theme": "Repos quotidien",
        "texte": "Le salarié en forfait jours bénéficie du repos quotidien de 11 heures consécutives."
      },
      {
        "theme": "Repos hebdomadaire",
        "texte": "Le salarié bénéficie du repos hebdomadaire de 35 heures consécutives."
      },
      {
        "theme": "Droit à la déconnexion",
        "texte": "Le salarié en forfait jours bénéficie d'un droit à la déconnexion en dehors de ses horaires de travail."
      }
    ],
    "articles": []
  },

  "remuneration": {
    "traite": true,
    "contenu": [
      {
        "theme": "Principe",
        "texte": "La rémunération est forfaitaire et indépendante du nombre d'heures de travail effectuées."
      },
      {
        "theme": "Minimum",
        "texte": "La rémunération annuelle ne peut être inférieure au minimum conventionnel majoré de 15 %."
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


**Éligibilité :**
- Catégories concernées
- Conditions d'autonomie
- Non-cadres autonomes

**Organisation :**
- Plafond annuel
- Période de référence
- Forfait réduit
- Jours de repos
- Modalités de prise

**Renonciation :**
- Possibilité
- Plafond
- Majoration

**Convention individuelle :**
- Formalisme
- Mentions obligatoires

**Suivi :**
- Entretien annuel
- Décompte des jours
- Droit d'alerte

**Garanties :**
- Repos quotidien
- Repos hebdomadaire
- Droit à la déconnexion

**Rémunération :**
- Principe
- Minimum conventionnel

---

## ❌ INTERDIT
- Inclure les heures supplémentaires
- Appliquer le Code du travail par défaut
- Faire d'analyse, de projection ou mentionner des règles non écrites.

## ✅ OBLIGATOIRE
- Préciser les catégories éligibles
- Indiquer le nombre de jours
- Détailler le suivi de la charge de travail
- **Présenter uniquement les modalités en vigueur.**
- **Utiliser la terminologie exacte de la convention.**

---

## Rappel final

⚠️ **JSON uniquement**
⚠️ **Exhaustivité totale**
⚠️ **Reformulation ≠ Interprétation**
