# Extraction : Durées du travail

## Objectif

Extraire et reformuler les règles conventionnelles relatives aux **durées du travail**.

**Tu es un outil de consultation.** Tu récupères l'information et tu la réorganises. C'est tout.

---

## ⚠️ PÉRIMÈTRE STRICT

Cette section concerne **UNIQUEMENT** les durées du travail.

### ❌ NE PAS inclure ici :
- Heures supplémentaires → section `heures-supplementaires`
- Forfait jours → section `forfait-jours`
- Temps partiel → section `temps-partiel`
- Aménagement du temps de travail → section `amenagement-temps-travail`

### ✅ INCLURE ici :
- Durée légale et conventionnelle
- Durées maximales (quotidienne, hebdomadaire)
- Temps de pause
- Temps de repos
- Temps de trajet
- Temps d'habillage/déshabillage
- Astreintes (définition et compensation)

---

## Règles

### Tu dois :
- ✅ Extraire TOUT ce qui concerne les durées du travail
- ✅ Reformuler clairement (syntaxe, structure)
- ✅ Si l'information est un tableau, le formater en **Markdown** dans le champ "texte".

### Tu ne dois PAS :
- ❌ Appliquer le Code du travail si la convention est muette
- ❌ Interpréter ou synthétiser l'information au-delà de la reformulation

### Si la convention ne dit rien sur un thème :
Écrire : **"Non traité par la convention."**

---

## Format de sortie

```json
{
  "section": "durees_travail",
  
  "duree_reference": {
    "traite": true,
    "contenu": [
      {
        "theme": "Durée hebdomadaire",
        "texte": "La durée hebdomadaire de travail est fixée à 35 heures."
      },
      {
        "theme": "Durée annuelle",
        "texte": "La durée annuelle de travail est fixée à 1 607 heures."
      }
    ],
    "articles": ["Art. 10"]
  },

  "durees_maximales": {
    "traite": true,
    "contenu": [
      {
        "theme": "Durée quotidienne maximale",
        "texte": "La durée quotidienne de travail ne peut excéder 10 heures."
      },
      {
        "theme": "Durée quotidienne dérogatoire",
        "texte": "La durée quotidienne peut être portée à 12 heures en cas d'activité accrue ou pour des motifs liés à l'organisation de l'entreprise."
      },
      {
        "theme": "Durée hebdomadaire maximale (Exemple Tableau)",
        "texte": "| Catégorie | Durée Max. Hebdo. |\n|---|---|\n| Standard | 44 heures |\n| Travail continu | 48 heures |\n| Jeunes travailleurs | 40 heures |"
      },
      {
        "theme": "Durée hebdomadaire dérogatoire",
        "texte": "La moyenne sur 12 semaines peut être portée à 46 heures."
      }
    ],
    "articles": []
  },

  "temps_pause": {
    "traite": true,
    "contenu": [
      {
        "theme": "Durée minimale",
        "texte": "Le salarié bénéficie d'une pause d'au moins 20 minutes consécutives dès que le temps de travail quotidien atteint 6 heures."
      },
      {
        "theme": "Rémunération",
        "texte": "Le temps de pause n'est pas rémunéré sauf disposition contraire."
      }
    ],
    "articles": []
  },

  "repos_quotidien": {
    "traite": true,
    "contenu": [
      {
        "theme": "Durée",
        "texte": "Le salarié bénéficie d'un repos quotidien d'au moins 11 heures consécutives."
      },
      {
        "theme": "Dérogation",
        "texte": "Le repos quotidien peut être réduit à 9 heures pour les activités caractérisées par la nécessité d'assurer une continuité du service."
      }
    ],
    "articles": []
  },

  "repos_hebdomadaire": {
    "traite": true,
    "contenu": [
      {
        "theme": "Durée",
        "texte": "Le salarié bénéficie d'un repos hebdomadaire d'au moins 35 heures consécutives (24 heures + 11 heures de repos quotidien)."
      },
      {
        "theme": "Jour de repos",
        "texte": "Le repos hebdomadaire est donné le dimanche."
      }
    ],
    "articles": []
  },

  "temps_habillage": {
    "traite": true,
    "contenu": [
      {
        "theme": "Compensation",
        "texte": "Lorsque le port d'une tenue de travail est imposé et que l'habillage et le déshabillage doivent être réalisés sur le lieu de travail, le temps correspondant fait l'objet d'une contrepartie sous forme de repos ou de compensation financière."
      },
      {
        "theme": "Montant",
        "texte": "La compensation est fixée à 10 minutes par jour."
      }
    ],
    "articles": []
  },

  "temps_trajet": {
    "traite": true,
    "contenu": [
      {
        "theme": "Trajet domicile-travail",
        "texte": "Le temps de trajet entre le domicile et le lieu de travail n'est pas du temps de travail effectif."
      },
      {
        "theme": "Trajet inhabituel",
        "texte": "Lorsque le temps de trajet dépasse le temps normal de trajet entre le domicile et le lieu habituel de travail, ce dépassement fait l'objet d'une contrepartie sous forme de repos."
      }
    ],
    "articles": []
  },

  "astreintes": {
    "traite": true,
    "contenu": [
      {
        "theme": "Définition",
        "texte": "L'astreinte est une période pendant laquelle le salarié, sans être sur son lieu de travail, doit être en mesure d'intervenir pour accomplir un travail."
      },
      {
        "theme": "Compensation de l'astreinte",
        "texte": "L'astreinte fait l'objet d'une compensation sous forme financière ou en repos."
      },
      {
        "theme": "Temps d'intervention",
        "texte": "Le temps d'intervention pendant l'astreinte est du temps de travail effectif."
      },
      {
        "theme": "Délai de prévenance",
        "texte": "Le salarié est informé du programme d'astreinte au moins 15 jours à l'avance, sauf circonstances exceptionnelles avec un délai d'un jour franc."
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

**Durées de référence :**
- Durée hebdomadaire
- Durée annuelle
- Durée mensuelle

**Durées maximales :**
- Durée quotidienne maximale
- Durée hebdomadaire maximale
- Dérogations

**Repos et pauses :**
- Temps de pause
- Repos quotidien
- Repos hebdomadaire

**Temps annexes :**
- Temps d'habillage/déshabillage
- Temps de trajet
- Temps de douche

**Astreintes :**
- Définition
- Compensation
- Temps d'intervention
- Délai de prévenance

---

## ❌ INTERDIT
- Inclure les heures supplémentaires
- Inclure le forfait jours
- Appliquer le Code du travail par défaut

## ✅ OBLIGATOIRE
- Distinguer les durées de référence et les maximales
- Préciser les compensations

---

## Rappel final

⚠️ **JSON uniquement**
⚠️ **Exhaustivité totale**
⚠️ **Reformulation ≠ Interprétation**
