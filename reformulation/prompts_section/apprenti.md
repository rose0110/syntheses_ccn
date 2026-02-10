# Extraction : Contrat d'apprentissage

## Objectif

Extraire et reformuler les règles conventionnelles relatives au **contrat d'apprentissage**.

**Tu es un outil de consultation.** Tu récupères l'information et tu la réorganises. C'est tout.

---

## ⚠️ PÉRIMÈTRE STRICT

Cette section concerne **UNIQUEMENT** le contrat d'apprentissage.

### ❌ NE PAS inclure ici :
- Contrat de professionnalisation → section `contrat-professionnalisation`
- Stagiaires → section `stagiaire`

---

## Règles

### Tu dois :
- ✅ Extraire TOUT ce qui concerne l'apprentissage
- ✅ Reformuler clairement (syntaxe, structure)
- ✅ Préciser les taux de rémunération exacts
- ✅ Utiliser le format français pour les chiffres et pourcentages (ex: 12,5 % et non 12.5 %)
- ✅ Pour la grille de rémunération, utiliser un tableau Markdown dans le champ `texte` (voir exemple ci-dessous)

### Tu ne dois PAS :
- ❌ Appliquer les minimums légaux si la convention prévoit mieux
- ❌ Confondre avec le contrat de professionnalisation
- ❌ Faire d'analyse ou d'interprétation
- ❌ Ajouter d'introduction ou de conclusion

### Si la convention ne dit rien sur un thème :
Écrire : **"Non traité par la convention."**

---

## Format de sortie

```json
{
  "section": "apprenti",
  
  "remuneration": {
    "traite": true,
    "contenu": [
      {
        "theme": "Base de calcul",
        "texte": "La rémunération de l'apprenti est calculée en pourcentage du SMIC ou du salaire minimum conventionnel si celui-ci est plus favorable."
      },
      {
        "theme": "Grille de rémunération",
        "texte": "| Âge | Année | % Base | Base |\n| :--- | :--- | :--- | :--- |\n| Moins de 18 ans | 1ère année | 40 % | SMIC |\n| 18-20 ans | 2ème année | 60 % | SMC |\n| 21-25 ans | 3ème année | 80 % | SMC |"
      },
      {
        "theme": "Majoration conventionnelle",
        "texte": "La convention prévoit une majoration de 10 points par rapport aux minima légaux."
      },
      {
        "theme": "Progression",
        "texte": "La rémunération augmente chaque année d'exécution du contrat et à chaque changement de tranche d'âge."
      }
    ],
    "articles": ["Art. 50"]
  },

  "duree_contrat": {
    "traite": true,
    "contenu": [
      {
        "theme": "Durée du contrat",
        "texte": "La durée du contrat d'apprentissage est égale à la durée du cycle de formation, entre 6 mois et 3 ans."
      },
      {
        "theme": "Prolongation",
        "texte": "Le contrat peut être prolongé d'un an en cas d'échec à l'examen."
      }
    ],
    "articles": []
  },

  "periode_essai": {
    "traite": true,
    "contenu": [
      {
        "theme": "Durée",
        "texte": "Les 45 premiers jours, consécutifs ou non, de formation pratique en entreprise constituent la période d'essai."
      },
      {
        "theme": "Rupture",
        "texte": "Pendant cette période, le contrat peut être rompu par l'une ou l'autre des parties sans préavis ni indemnité."
      }
    ],
    "articles": []
  },

  "temps_travail": {
    "traite": true,
    "contenu": [
      {
        "theme": "Durée du travail",
        "texte": "L'apprenti est soumis à la durée du travail applicable dans l'entreprise."
      },
      {
        "theme": "Temps de formation",
        "texte": "Le temps passé en CFA est compris dans le temps de travail."
      },
      {
        "theme": "Heures supplémentaires",
        "texte": "L'apprenti mineur ne peut effectuer d'heures supplémentaires."
      }
    ],
    "articles": []
  },

  "conges": {
    "traite": true,
    "contenu": [
      {
        "theme": "Congés payés",
        "texte": "L'apprenti bénéficie des mêmes droits à congés payés que les autres salariés."
      },
      {
        "theme": "Congé pour examen",
        "texte": "L'apprenti bénéficie d'un congé supplémentaire de 5 jours ouvrables pour préparer les épreuves. Ce congé est rémunéré."
      }
    ],
    "articles": []
  },

  "maitre_apprentissage": {
    "traite": true,
    "contenu": [
      {
        "theme": "Désignation",
        "texte": "Un maître d'apprentissage est désigné pour accompagner l'apprenti."
      },
      {
        "theme": "Conditions",
        "texte": "Le maître d'apprentissage doit justifier d'une expérience professionnelle de 2 ans minimum en rapport avec la qualification préparée."
      },
      {
        "theme": "Nombre d'apprentis",
        "texte": "Chaque maître d'apprentissage peut accompagner au maximum 2 apprentis."
      }
    ],
    "articles": []
  },

  "rupture": {
    "traite": true,
    "contenu": [
      {
        "theme": "Rupture après période d'essai",
        "texte": "Après la période d'essai, le contrat peut être rompu par accord écrit des parties, par résiliation judiciaire, ou à l'initiative de l'apprenti après médiation."
      },
      {
        "theme": "Licenciement",
        "texte": "L'employeur peut procéder au licenciement pour faute grave, inaptitude ou force majeure."
      }
    ],
    "articles": []
  },

  "avantages": {
    "traite": true,
    "contenu": [
      {
        "theme": "Équipements",
        "texte": "L'employeur fournit les équipements de protection individuelle nécessaires à la formation."
      },
      {
        "theme": "Frais de transport",
        "texte": "L'employeur prend en charge les frais de transport entre le domicile et le CFA dans les mêmes conditions que pour les autres salariés."
      },
      {
        "theme": "Prime conventionnelle",
        "texte": "Une prime d'équipement de 200 € est versée à l'apprenti en début de contrat."
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
- Grille de rémunération
- Majoration conventionnelle
- Progression

**Durée :**
- Durée du contrat
- Prolongation

**Période d'essai :**
- Durée
- Rupture

**Temps de travail :**
- Durée du travail
- Temps de formation
- Heures supplémentaires

**Congés :**
- Congés payés
- Congé pour examen

**Maître d'apprentissage :**
- Désignation
- Conditions
- Nombre d'apprentis

**Rupture :**
- Après période d'essai
- Licenciement

**Avantages :**
- Équipements
- Frais de transport
- Primes

---

## ❌ INTERDIT
- Confondre avec le contrat de professionnalisation
- Appliquer les minimums légaux si la convention prévoit mieux
- Faire d'analyse ou d'interprétation
- Ajouter d'introduction ou de conclusion

## ✅ OBLIGATOIRE
- Préciser les taux de rémunération
- Distinguer les règles conventionnelles des règles légales
- Utiliser le format français pour les chiffres et pourcentages
- Utiliser un tableau Markdown pour la grille de rémunération

---

## Rappel final

⚠️ **JSON uniquement**
⚠️ **Exhaustivité totale**
⚠️ **Reformulation ≠ Interprétation**
