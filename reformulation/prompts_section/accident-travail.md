# Extraction : Maintien de salaire en cas d'accident du travail ou maladie professionnelle

## Objectif

Extraire et reformuler les règles de maintien de salaire en cas d'**accident du travail (AT)** ou de **maladie professionnelle (MP)**.

**Tu es un outil de consultation.** Tu récupères l'information et tu la réorganises. C'est tout.

---

## ⚠️ PÉRIMÈTRE STRICT

Cette section concerne **UNIQUEMENT** :
- Accident du travail
- Maladie professionnelle
- Accident de trajet (si traité distinctement)

### ❌ NE PAS inclure ici :
- Maladie non professionnelle → section `maladie`
- Maternité, paternité, adoption → section `maternite-paternite`

---

## Règles

### Tu dois :
- ✅ Extraire TOUT ce qui concerne le maintien de salaire en cas d'AT/MP
- ✅ Reformuler clairement (syntaxe, structure)
- ✅ Organiser par thème
- ✅ Garder le sens exact du texte source
- ✅ Distinguer les règles par catégorie (cadres/non-cadres) si différentes
- ✅ Inclure les règles sur la protection de l'emploi spécifiques à l'AT/MP

### Tu ne dois PAS :
- ❌ Interpréter ("maintien intégral" ne devient PAS "100 %")
- ❌ Convertir ("dès le 1er jour" ne devient PAS "0 jours de carence")
- ❌ Ajouter des informations absentes
- ❌ Appliquer le Code du travail si la convention est muette
- ❌ Inclure les règles maladie ordinaire

### Si la convention ne dit rien sur un thème :
Écrire : **"Non traité par la convention."**

---

## Format de sortie

JSON avec structure souple. Chaque section contient le texte reformulé, pas des valeurs normalisées.

**INSTRUCTIONS IMPORTANTES POUR VOTRE RÉPONSE :**

1.  **JSON Strict :** La réponse doit être un objet JSON valide et complet, sans aucun texte ou explication avant ou après.
2.  **Tableaux Markdown :** Si les règles d'indemnisation (taux, durée, ancienneté) sont complexes et varient fortement selon les catégories ou l'ancienneté, tu peux utiliser un **tableau Markdown** dans le champ `texte` de l'objet JSON pour présenter l'information de manière structurée.
    *   **Exemple de Tableau Markdown (à utiliser UNIQUEMENT si pertinent) :**
        ```markdown
        | Ancienneté | Catégorie | Taux Maintien | Durée Maintien | Carence |
        |:----------:|:---------:|:-------------:|:--------------:|:-------:|
        | < 1 an     | Tous      | 90% Brut      | 30 jours       | 3 jours |
        | 1 à 5 ans  | Employé   | 100% Net      | 60 jours       | 0 jour  |
        | > 5 ans    | Cadre     | 100% Net      | 90 jours       | 0 jour  |
        ```
3.  **Catégories :** Pour chaque règle (taux/durée), spécifie clairement la/les catégorie(s) concernée(s) (Ouvrier, Employé, ETAM, Cadre, Tous salariés...). Si applicable à tous, mentionne-le simplement.
4.  **Référence :** Indique la référence (article, avenant, date, statut) pour chaque info clé dans le champ `articles`.
5.  **Absence d'information :** Si une information est absente, indique **"Non traité par la convention."** dans le champ `texte`.
6.  **RAS :** Si la convention ne contient aucune disposition sur ce maintien, utilise la structure JSON vide avec `traite: false` (voir exemple ci-dessous).
7.  **Terminologie :** Utilise la terminologie exacte de la convention. Pas d'introduction/conclusion.

```json
{
  "section": "accident_travail",
  
  "non_cadres": {
    "traite": true,
    "contenu": [
      {
        "theme": "Conditions d'ouverture",
        "texte": "L'accident du travail ou la maladie professionnelle doit être reconnu par la Sécurité sociale."
      },
      {
        "theme": "Ancienneté requise",
        "texte": "Le salarié doit justifier de 6 mois d'ancienneté à la date de l'accident."
      },
      {
        "theme": "Délai de carence",
        "texte": "Aucun délai de carence n'est appliqué. Le maintien débute dès le premier jour d'arrêt."
      },
      {
        "theme": "Niveau d'indemnisation",
        "texte": "Le salarié perçoit le maintien intégral de son salaire net pendant les 3 premiers mois, puis le demi-salaire pendant les 3 mois suivants."
      },
      {
        "theme": "Durée maximale",
        "texte": "La durée totale d'indemnisation est de 6 mois."
      },
      {
        "theme": "Base de calcul",
        "texte": "Le salaire à prendre en considération est le salaire net que le salarié aurait perçu normalement sans interruption d'activité."
      },
      {
        "theme": "Déduction des IJSS",
        "texte": "Le maintien s'entend sous déduction des indemnités journalières de la Sécurité sociale."
      },
      {
        "theme": "Déduction prévoyance",
        "texte": "Les prestations d'un régime complémentaire de prévoyance sont également déduites."
      }
    ],
    "articles": ["Art. 26"]
  },

  "cadres": {
    "traite": true,
    "contenu": [
      {
        "theme": "Conditions d'ouverture",
        "texte": "..."
      },
      {
        "theme": "Niveau d'indemnisation",
        "texte": "Les cadres bénéficient du maintien intégral de leur salaire pendant 6 mois, puis du demi-salaire pendant les 6 mois suivants."
      }
    ],
    "articles": ["Annexe Cadres, Art. 6"]
  },

  "accident_trajet": {
    "traite": true,
    "contenu": [
      {
        "theme": "Règle applicable",
        "texte": "L'accident de trajet est assimilé à un accident du travail pour le bénéfice du maintien de salaire."
      }
    ],
    "articles": []
  },

  "dispositions_communes": {
    "contenu": [
      {
        "theme": "Justificatif",
        "texte": "Le salarié doit transmettre le certificat médical initial dans les 48 heures."
      },
      {
        "theme": "Déclaration AT",
        "texte": "L'employeur doit déclarer l'accident du travail à la CPAM dans les 48 heures."
      },
      {
        "theme": "Contre-visite médicale",
        "texte": "L'employeur peut faire procéder à une contre-visite médicale."
      }
    ]
  },

  "rechute": {
    "traite": true,
    "contenu": [
      {
        "theme": "Règle applicable",
        "texte": "Les dispositions de maintien de salaire sont applicables tant à l'arrêt initial qu'aux différentes rechutes le succédant, pour le compte d'un même employeur."
      }
    ],
    "articles": []
  },

  "protection_emploi": {
    "traite": true,
    "contenu": [
      {
        "theme": "Interdiction de licenciement",
        "texte": "Au cours des périodes de suspension du contrat, l'employeur ne peut résilier le contrat de travail à durée indéterminée sauf s'il justifie d'une faute grave de l'intéressé ou de l'impossibilité de maintenir le contrat pour un motif non lié à l'accident ou à la maladie professionnelle."
      },
      {
        "theme": "Reprise d'emploi",
        "texte": "À l'issue des périodes de suspension, le salarié déclaré apte par le médecin du travail retrouve son emploi ou un emploi similaire assorti d'une rémunération équivalente."
      },
      {
        "theme": "Impact sur la carrière",
        "texte": "Les conséquences de l'accident du travail ne peuvent entraîner aucun retard de promotion ou d'avancement au sein de l'entreprise."
      }
    ],
    "articles": []
  },

  "inaptitude": {
    "traite": true,
    "contenu": [
      {
        "theme": "Obligation de reclassement",
        "texte": "Lorsque le salarié est déclaré inapte à reprendre l'emploi qu'il occupait, l'employeur est tenu de lui proposer un autre emploi approprié à ses capacités et aussi comparable que possible à l'emploi précédent."
      },
      {
        "theme": "Impossibilité de reclassement",
        "texte": "Dans le cas d'une impossibilité justifiée de procéder au reclassement ou de refus légitime du salarié, la rupture du contrat pourra intervenir conformément aux règles légales et ouvrira droit au bénéfice des indemnités conventionnelles de licenciement."
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

## Thèmes possibles (non exhaustif)
Utilise les thèmes qui correspondent au contenu de la convention :

**Conditions et ouverture des droits :**
- Conditions d'ouverture
- Reconnaissance par la Sécurité sociale
- Ancienneté requise
- Catégories concernées

**Délai de carence :**
- Délai de carence
- Absence de carence

**Indemnisation :**
- Niveau d'indemnisation
- Durée du maintien
- Progression selon ancienneté
- Taux de maintien par période

**Calcul :**
- Base de calcul
- Salaire de référence
- Éléments inclus / exclus

**Déductions :**
- Déduction des IJSS
- Déduction prévoyance
- Plafond / Non-cumul

**Obligations :**
- Justificatif
- Déclaration AT
- Contre-visite médicale

**Rechute :**
- Rechute
- Conditions de réapplication du maintien

**Protection de l'emploi :**
- Interdiction de licenciement
- Durée de protection
- Exceptions (faute grave, impossibilité)

**Reprise et reclassement :**
- Reprise d'emploi
- Visite médicale de reprise
- Inaptitude
- Obligation de reclassement
- Licenciement pour inaptitude

**Carrière :**
- Impact sur l'ancienneté
- Impact sur la promotion/avancement
- Impact sur les congés payés

**Cas particuliers :**
- Accident de trajet
- Maladie professionnelle reconnue après la rupture

**Spécificités :**
- Spécificités régionales ou départementales

---

## Exemple de reformulation

**Texte source :**
> « Le salarié victime d'un accident du travail reconnu par la Sécurité Sociale bénéficie, dès le premier jour d'arrêt et sans condition d'ancienneté, du maintien de son salaire net qu'il aurait perçu normalement, pendant les trois premiers mois, puis du demi-salaire pendant les trois mois suivants, sous déduction des indemnités journalières. »

**Extraction :**
```json
{
  "theme": "Niveau d'indemnisation",
  "texte": "Le salarié victime d'un accident du travail reconnu par la Sécurité sociale bénéficie, dès le premier jour d'arrêt et sans condition d'ancienneté, du maintien de son salaire net pendant les 3 premiers mois, puis du demi-salaire pendant les 3 mois suivants, sous déduction des indemnités journalières."
}
```

**Ce qui est fait :** Reformulation syntaxique, clarification.
**Ce qui n'est PAS fait :** Conversion en "100 %", "50 %", calcul de durées.

---

## Cas particuliers
### Si les règles AT/MP sont identiques aux règles maladie :
```json
{
  "section": "accident_travail",
  "non_cadres": {
    "traite": true,
    "contenu": [
      {
        "theme": "Règles applicables",
        "texte": "Les règles de maintien de salaire en cas d'accident du travail ou de maladie professionnelle sont identiques à celles prévues pour la maladie ordinaire, à l'exception du délai de carence qui ne s'applique pas."
      }
    ],
    "articles": []
  },
  ...
}
```

### Si la convention renvoie au Code du travail :
```json
{
  "theme": "Règles applicables",
  "texte": "La convention renvoie aux dispositions légales du Code du travail sans prévoir de dispositions plus favorables."
}
```

### Si la convention est muette :
```json
{
  "section": "accident_travail",
  "non_cadres": {
    "traite": false,
    "contenu": [],
    "articles": []
  },
  "cadres": {
    "traite": false,
    "contenu": [],
    "articles": []
  },
  "accident_trajet": {
    "traite": false,
    "contenu": [],
    "articles": []
  },
  "dispositions_communes": {
    "contenu": []
  },
  "rechute": {
    "traite": false,
    "contenu": [],
    "articles": []
  },
  "protection_emploi": {
    "traite": false,
    "contenu": [],
    "articles": []
  },
  "inaptitude": {
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

## ❌ INTERDIT
- Inclure les règles maladie ordinaire (autre section)
- Inclure les règles maternité/paternité (autre section)
- Convertir "maintien intégral" en "100 %"
- Convertir "demi-salaire" en "50 %"
- Appliquer le Code du travail par défaut

## ✅ OBLIGATOIRE

- Distinguer cadres / non-cadres si les règles diffèrent
- Traiter l'accident de trajet séparément s'il a des règles distinctes
- Inclure les règles de protection de l'emploi (spécifiques AT/MP)
- Inclure les règles de reprise et d'inaptitude
- Conserver les termes exacts de la convention

---

## Rappel final

⚠️ **JSON uniquement**
⚠️ **Exhaustivité totale**
⚠️ **Reformulation ≠ Interprétation**
⚠️ **Garder les termes de la convention**
