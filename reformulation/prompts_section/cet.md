# Extraction : Compte épargne-temps (CET)

## Objectif

Extraire et reformuler les règles conventionnelles relatives au **compte épargne-temps**.

**Tu es un outil de consultation.** Tu récupères l'information et tu la réorganises. C'est tout.

---

## ⚠️ PÉRIMÈTRE STRICT

Cette section concerne **UNIQUEMENT** le compte épargne-temps.

### ❌ NE PAS inclure ici :
- Congés payés → section `conges-payes`
- RTT → section `amenagement-temps-travail`

---

## Règles

### Tu dois :
- ✅ Extraire TOUT ce qui concerne le CET
- ✅ Reformuler clairement (syntaxe, structure)
- ✅ Utiliser la **terminologie exacte** de la convention collective.
- ✅ N'ajouter des notes que si elles proviennent **directement** de la convention.

### Tu ne dois PAS :
- ❌ Appliquer le Code du travail si la convention est muette
- ❌ Faire d'analyse, de projection ou mentionner l'application de règles non écrites.

### Si la convention ne dit rien sur un thème :
Écrire : **"Non traité par la convention."** dans le champ `texte` correspondant.

### Si le CET n'est pas du tout prévu par la convention :
Retourner uniquement : `{"section": "cet", "ras": "RAS"}`

---

## Format de sortie

```json
{
  "section": "cet",
  
  "ouverture": {
    "traite": true,
    "contenu": [
      {
        "theme": "Conditions d'ouverture",
        "texte": "Tout salarié ayant au moins un an d'ancienneté peut ouvrir un compte épargne-temps."
      },
      {
        "theme": "Formalisme",
        "texte": "L'ouverture du compte fait l'objet d'une demande écrite du salarié."
      }
    ],
    "articles": ["Art. 30"]
  },

  "alimentation_temps": {
    "traite": true,
    "contenu": [
      {
        "theme": "Congés payés",
        "texte": "Le salarié peut affecter au CET les jours de congés payés excédant 24 jours ouvrables, dans la limite de 5 jours par an."
      },
      {
        "theme": "RTT",
        "texte": "Le salarié peut affecter au CET tout ou partie des jours de RTT, dans la limite de 10 jours par an."
      },
      {
        "theme": "Repos compensateur",
        "texte": "Le salarié peut affecter au CET les heures de repos compensateur de remplacement."
      },
      {
        "theme": "Heures supplémentaires",
        "texte": "Le salarié peut affecter au CET les heures supplémentaires et leurs majorations."
      }
    ],
    "articles": []
  },

  "alimentation_argent": {
    "traite": true,
    "contenu": [
      {
        "theme": "Éléments de rémunération",
        "texte": "Le salarié peut affecter au CET tout ou partie de sa prime d'intéressement et de sa participation."
      },
      {
        "theme": "Augmentation de salaire",
        "texte": "Le salarié peut affecter au CET tout ou partie d'une augmentation de salaire."
      }
    ],
    "articles": []
  },

  "plafond": {
    "traite": true,
    "contenu": [
      {
        "theme": "Plafond en jours",
        "texte": "Le nombre de jours épargnés ne peut excéder 60 jours."
      },
      {
        "theme": "Plafond monétaire",
        "texte": "Les droits épargnés ne peuvent excéder le plafond de garantie de l'AGS."
      }
    ],
    "articles": []
  },

  "utilisation_conges": {
    "traite": true,
    "contenu": [
      {
        "theme": "Congés de longue durée",
        "texte": "Le CET peut être utilisé pour financer un congé parental, un congé sabbatique, un congé pour création d'entreprise ou un congé de solidarité internationale."
      },
      {
        "theme": "Congé de fin de carrière",
        "texte": "Le CET peut être utilisé pour financer un congé de fin de carrière précédant le départ à la retraite."
      },
      {
        "theme": "Passage à temps partiel",
        "texte": "Le CET peut être utilisé pour compenser une réduction de salaire en cas de passage à temps partiel."
      },
      {
        "theme": "Délai de prévenance",
        "texte": "Le salarié doit informer l'employeur de sa volonté d'utiliser le CET au moins 3 mois à l'avance pour un congé supérieur à 2 mois."
      }
    ],
    "articles": []
  },

  "utilisation_monetaire": {
    "traite": true,
    "contenu": [
      {
        "theme": "Complément de rémunération",
        "texte": "Le salarié peut demander le déblocage de tout ou partie des droits épargnés sous forme de complément de rémunération."
      },
      {
        "theme": "Alimentation PEE/PERCO",
        "texte": "Les droits épargnés peuvent être transférés vers un plan d'épargne entreprise ou un plan d'épargne retraite."
      },
      {
        "theme": "Rachat de trimestres",
        "texte": "Le CET peut être utilisé pour racheter des trimestres de cotisation retraite."
      }
    ],
    "articles": []
  },

  "valorisation": {
    "traite": true,
    "contenu": [
      {
        "theme": "Valorisation des jours",
        "texte": "Les jours épargnés sont valorisés sur la base du salaire perçu au moment de leur utilisation."
      }
    ],
    "articles": []
  },

  "cloture": {
    "traite": true,
    "contenu": [
      {
        "theme": "Rupture du contrat",
        "texte": "En cas de rupture du contrat de travail, les droits épargnés sont liquidés sous forme d'indemnité compensatrice."
      },
      {
        "theme": "Transfert",
        "texte": "En cas de mobilité au sein du groupe, les droits peuvent être transférés vers le CET du nouvel employeur."
      },
      {
        "theme": "Renonciation",
        "texte": "Le salarié peut renoncer à l'utilisation du CET et demander la liquidation des droits sous forme d'indemnité."
      }
    ],
    "articles": []
  },

  "garantie": {
    "traite": true,
    "contenu": [
      {
        "theme": "Garantie des droits",
        "texte": "Les droits acquis sont garantis par l'AGS dans la limite du plafond légal."
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

## Utilisation des tableaux Markdown dans le champ `texte`

Dans le cas où l'information extraite est une liste de données structurées (ex: barème, liste de catégories avec des conditions associées), tu peux utiliser un tableau Markdown à l'intérieur du champ `texte`.

**Exemple de tableau dans le champ `texte` :**

```json
{
  "theme": "Catégories éligibles",
  "texte": "| Catégorie | Ancienneté requise |\n| :--- | :--- |\n| Ouvriers | 6 mois |\n| Cadres | 1 an |"
}
```

---

## Thèmes possibles


**Ouverture :**
- Conditions d'ouverture
- Formalisme
- Bénéficiaires

**Alimentation :**
- En temps (CP, RTT, repos)
- En argent (primes, intéressement)
- Plafonds

**Utilisation :**
- Congés de longue durée
- Fin de carrière
- Temps partiel
- Complément de rémunération
- Épargne retraite
- Délai de prévenance

**Valorisation :**
- Mode de valorisation

**Clôture :**
- Rupture du contrat
- Transfert
- Renonciation

**Garantie :**
- Garantie des droits

---

## ❌ INTERDIT
- Inclure les règles générales des congés payés
- Appliquer le Code du travail par défaut

## ✅ OBLIGATOIRE
- Préciser les sources d'alimentation
- Indiquer les plafonds
- Détailler les utilisations possibles

---

## Rappel final

⚠️ **JSON uniquement**
⚠️ **Exhaustivité totale**
⚠️ **Reformulation ≠ Interprétation**
⚠️ **Si CET non prévu :** `{"section": "cet", "ras": "RAS"}`
