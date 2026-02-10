# Extraction : Cotisation mutuelle (frais de santé)

## Objectif

Extraire et reformuler les règles conventionnelles relatives à la **mutuelle obligatoire** (complémentaire santé).

**Tu es un outil de consultation.** Tu récupères l'information et tu la réorganises. C'est tout.

---

## ⚠️ PÉRIMÈTRE STRICT

Cette section concerne **UNIQUEMENT** la complémentaire santé (mutuelle).

### ❌ NE PAS inclure ici :
- Prévoyance (décès, incapacité, invalidité) → section `cotisation-prevoyance`
- Retraite complémentaire → section `cotisation-retraite`

---

## Règles

### Tu dois :
- ✅ Extraire TOUT ce qui concerne la mutuelle
- ✅ Reformuler clairement (syntaxe, structure)
- ✅ Préciser les montants ou pourcentages exacts
- ✅ **CONSERVER les notes et commentaires associés si présents.**

### Tu ne dois PAS :
- ❌ Appliquer les dispositions légales si la convention est muette
- ❌ Confondre avec la prévoyance

### Si la convention ne dit rien sur un thème :
Écrire : **"Non traité par la convention."**

---

## 📝 GESTION DES TABLEAUX MARKDOWN

Si la convention utilise un tableau pour présenter des données (ex: cotisations, garanties), **tu dois reproduire cette structure fidèlement** en utilisant le format **tableau Markdown** à l'intérieur du champ `texte` du JSON.

**Exemple de reproduction de tableau dans le champ `texte` :**

```json
{
  "theme": "Cotisations par formule",
  "texte": "| Formule | Cotisation totale | Part Employeur | Part Salarié |\n| :--- | :---: | :---: | :---: |\n| Isolé | 45,00 € | 22,50 € | 22,50 € |\n| Famille | 95,00 € | 47,50 € | 47,50 € |"
}
```

---

## Format de sortie

```json
{
  "section": "cotisation_mutuelle",
  
  "caractere_obligatoire": {
    "traite": true,
    "contenu": [
      {
        "theme": "Obligation",
        "texte": "La mise en place d'une couverture complémentaire santé est obligatoire pour l'ensemble des salariés de la branche."
      },
      {
        "theme": "Bénéficiaires",
        "texte": "Tous les salariés, sans condition d'ancienneté, bénéficient de la couverture santé."
      }
    ],
    "articles": ["Accord du 15 mars 2016"]
  },

  "organisme": {
    "traite": true,
    "contenu": [
      {
        "theme": "Organisme recommandé",
        "texte": "L'organisme recommandé pour la branche est Harmonie Mutuelle."
      },
      {
        "theme": "Liberté de choix",
        "texte": "Les entreprises peuvent choisir un autre organisme, sous réserve de respecter les garanties minimales."
      }
    ],
    "articles": []
  },

  "cotisations": {
    "traite": true,
    "contenu": [
      {
        "theme": "Cotisations par formule",
        "texte": "| Formule | Cotisation totale | Part Employeur | Part Salarié |\n| :--- | :---: | :---: | :---: |\n| Isolé | 45,00 € | 22,50 € | 22,50 € |\n| Famille | 95,00 € | 47,50 € | 47,50 € |"
      },
      {
        "theme": "Participation employeur minimale",
        "texte": "La participation de l'employeur ne peut être inférieure à 50 % de la cotisation."
      }
    ],
    "articles": []
  },

  "garanties_minimales": {
    "traite": true,
    "contenu": [
      {
        "theme": "Panier de soins",
        "texte": "Le contrat respecte le cahier des charges des contrats responsables et couvre a minima le panier de soins minimum."
      },
      {
        "theme": "Hospitalisation",
        "texte": "Prise en charge intégrale du forfait journalier hospitalier."
      },
      {
        "theme": "Optique",
        "texte": "Prise en charge des frais d'optique à hauteur de 100 € minimum pour les verres simples et 200 € pour les verres complexes."
      },
      {
        "theme": "Dentaire",
        "texte": "Prise en charge des soins dentaires prothétiques à hauteur de 125 % de la base de remboursement."
      }
    ],
    "articles": []
  },

  "dispenses_affiliation": {
    "traite": true,
    "contenu": [
      {
        "theme": "CDD courts",
        "texte": "Les salariés en CDD de moins de 12 mois peuvent demander une dispense d'affiliation."
      },
      {
        "theme": "Temps partiel",
        "texte": "Les salariés à temps partiel dont la cotisation représente plus de 10 % de leur rémunération peuvent demander une dispense."
      },
      {
        "theme": "Couverture existante",
        "texte": "Les salariés déjà couverts par le contrat de leur conjoint à titre obligatoire peuvent demander une dispense."
      },
      {
        "theme": "CSS",
        "texte": "Les bénéficiaires de la complémentaire santé solidaire (CSS) peuvent demander une dispense."
      },
      {
        "theme": "Formalisme",
        "texte": "La demande de dispense doit être formulée par écrit avec les justificatifs appropriés."
      }
    ],
    "articles": []
  },

  "portabilite": {
    "traite": true,
    "contenu": [
      {
        "theme": "Durée",
        "texte": "Le maintien des garanties est assuré pendant une durée égale à la durée du dernier contrat de travail, dans la limite de 12 mois."
      },
      {
        "theme": "Conditions",
        "texte": "La portabilité est ouverte aux salariés dont la rupture du contrat ouvre droit à l'assurance chômage."
      },
      {
        "theme": "Financement",
        "texte": "Le financement de la portabilité est mutualisé."
      }
    ],
    "articles": []
  },

  "maintien_sortants": {
    "traite": true,
    "contenu": [
      {
        "theme": "Retraités",
        "texte": "Les anciens salariés partant à la retraite peuvent continuer à bénéficier de la couverture santé à titre individuel."
      },
      {
        "theme": "Tarif",
        "texte": "Les tarifs applicables aux anciens salariés ne peuvent excéder 150 % du tarif des actifs."
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


**Caractère obligatoire :**
- Obligation
- Bénéficiaires
- Date d'effet

**Organisme :**
- Organisme recommandé/désigné
- Liberté de choix

**Cotisations :**
- Montant
- Répartition employeur/salarié
- Participation minimale

**Garanties :**
- Panier de soins
- Hospitalisation
- Optique
- Dentaire

**Dispenses :**
- CDD courts
- Temps partiel
- Couverture existante
- CSS
- Formalisme

**Portabilité :**
- Durée
- Conditions
- Financement

**Anciens salariés :**
- Retraités
- Tarifs

---

## ❌ INTERDIT
- Confondre avec la prévoyance
- Appliquer les dispositions légales par défaut

## ✅ OBLIGATOIRE
- Préciser les montants ou pourcentages
- Indiquer la répartition employeur/salarié
- Lister les cas de dispense

---

## Rappel final

⚠️ **JSON uniquement**
⚠️ **Exhaustivité totale**
⚠️ **Reformulation ≠ Interprétation**
