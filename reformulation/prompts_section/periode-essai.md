# Extraction : Période d'essai

## Objectif

Extraire et reformuler les règles conventionnelles relatives à la **période d'essai** pour les CDI et CDD.

**Tu es un outil de consultation.** Tu récupères l'information et tu la réorganises. C'est tout.

---

## ⚠️ PÉRIMÈTRE STRICT

Cette section concerne **UNIQUEMENT** la période d'essai.

### ❌ NE PAS inclure ici :
- Délai de prévenance en cas de rupture → section `delai-prevenance`
- Préavis de démission/licenciement → section `preavis`

### ✅ INCLURE ici :
- Durée initiale de la période d'essai
- Conditions et modalités de renouvellement
- Durée maximale totale
- Traitement des absences (prolongation)
- Spécificités CDD

---

## Règles

### Tu dois :
- ✅ Extraire TOUT ce qui concerne la période d'essai
- ✅ Reformuler clairement (syntaxe, structure)
- ✅ Organiser par thème
- ✅ Garder le sens exact du texte source
- ✅ Distinguer CDI / CDD si les règles diffèrent
- ✅ Distinguer par catégorie (ouvriers, employés, TAM, cadres)

### Tu ne dois PAS :
- ❌ Convertir les durées (ne pas transformer "1 mois" en "30 jours")
- ❌ Ajouter des informations absentes
- ❌ Appliquer le Code du travail si la convention est muette

### ⚠️ Gestion des tableaux
- Si l'information est présentée sous forme de tableau dans le texte source, tu dois la retranscrire en utilisant la syntaxe **Markdown pour les tableaux** dans le champ `texte`.
- **Exemple de tableau Markdown :**
  ```
  | Catégorie | Durée initiale | Renouvellement | Durée maximale |
  |---|---|---|---|
  | Ouvriers | 1 mois | 1 mois | 2 mois |
  | Cadres | 3 mois | 3 mois | 6 mois |
  ```

### Si la convention ne dit rien sur un thème :
Écrire : **"Non traité par la convention."**

---

## Format de sortie

```json
{
  "section": "periode_essai",
  
  "cdi": {
    "traite": true,
    "contenu": [
      {
        "theme": "Durées par catégorie",
        "texte": "La période d'essai est fixée à 1 mois pour les employés, 2 mois pour les agents de maîtrise et 3 mois pour les cadres."
      },
      {
        "theme": "Renouvellement",
        "texte": "La période d'essai peut être renouvelée une fois pour une durée identique à la période initiale, avec l'accord écrit du salarié."
      },
      {
        "theme": "Durée maximale totale",
        "texte": "La durée maximale, renouvellement compris, est de 2 mois pour les employés, 4 mois pour les agents de maîtrise et 6 mois pour les cadres."
      },
      {
        "theme": "Formalisme du renouvellement",
        "texte": "Le renouvellement doit faire l'objet d'un accord écrit du salarié, notifié avant l'expiration de la période initiale."
      },
      {
        "theme": "Conditions de renouvellement",
        "texte": "Le renouvellement n'est possible que si le contrat de travail le prévoit expressément."
      }
    ],
    "articles": ["Art. 5", "Art. 6"]
  },

  "cdd": {
    "traite": true,
    "contenu": [
      {
        "theme": "Calcul de la durée",
        "texte": "La période d'essai est calculée à raison d'un jour par semaine de travail, dans la limite de 2 semaines pour les contrats de 6 mois ou moins, et d'un mois pour les contrats de plus de 6 mois."
      },
      {
        "theme": "Renouvellement",
        "texte": "La convention ne prévoit pas de renouvellement pour les CDD."
      }
    ],
    "articles": []
  },

  "prolongation_absences": {
    "traite": true,
    "contenu": [
      {
        "theme": "Règle générale",
        "texte": "La période d'essai est prolongée de la durée des absences, quelle qu'en soit la cause."
      },
      {
        "theme": "Absences concernées",
        "texte": "Sont visées les absences pour maladie, accident, congés payés ou toute autre cause de suspension du contrat."
      }
    ],
    "articles": []
  },

  "rupture_pendant_essai": {
    "traite": true,
    "contenu": [
      {
        "theme": "Liberté de rupture",
        "texte": "Pendant la période d'essai, chacune des parties peut rompre le contrat librement, sans avoir à justifier d'un motif."
      },
      {
        "theme": "Indemnité",
        "texte": "Aucune indemnité n'est due en cas de rupture pendant la période d'essai."
      }
    ],
    "articles": []
  },

  "stage_prealable": {
    "traite": true,
    "contenu": [
      {
        "theme": "Réduction de la période d'essai",
        "texte": "La durée du stage effectué dans l'entreprise au cours des deux années précédant l'embauche est déduite de la période d'essai, sans pouvoir la réduire de plus de moitié."
      }
    ],
    "articles": []
  },

  "specificites_categories": {
    "traite": false,
    "contenu": [],
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

## Thèmes possibles (non exhaustif)


**Durées :**
- Durées par catégorie
- Durée initiale
- Durée pour les ouvriers/employés
- Durée pour les TAM/agents de maîtrise
- Durée pour les cadres

**Renouvellement :**
- Renouvellement
- Durée du renouvellement
- Durée maximale totale
- Formalisme du renouvellement
- Conditions de renouvellement

**Absences et prolongation :**
- Prolongation pour absences
- Absences concernées
- Calcul de la prolongation

**Rupture :**
- Liberté de rupture
- Indemnité
- Formalisme de la rupture

**CDD :**
- Calcul de la durée
- Renouvellement CDD
- Spécificités selon durée du contrat

**Autres :**
- Stage préalable (réduction)
- Embauche après intérim
- Spécificités par catégorie
- Spécificités régionales

---

## ❌ INTERDIT
- Inclure les délais de prévenance (autre section)
- Convertir les durées
- Appliquer le Code du travail par défaut

## ✅ OBLIGATOIRE
- Distinguer CDI / CDD
- Distinguer par catégorie professionnelle
- Préciser les conditions de renouvellement

---

## Rappel final

⚠️ **JSON uniquement**
⚠️ **Exhaustivité totale**
⚠️ **Reformulation ≠ Interprétation**
