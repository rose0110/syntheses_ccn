# Extraction : Indemnité de mise à la retraite

## Objectif

Extraire et reformuler les règles conventionnelles relatives à l'**indemnité de mise à la retraite** (initiative de l'employeur).

**Tu es un outil de consultation.** Tu récupères l'information et tu la réorganises. C'est tout.

---

## ⚠️ PÉRIMÈTRE STRICT

Cette section concerne **UNIQUEMENT** la mise à la retraite (initiative de l'employeur).

### ❌ NE PAS inclure ici :
- Départ volontaire à la retraite (initiative salarié) → section `indemnite-depart-retraite`
- Indemnité de licenciement → section `indemnite-licenciement`
- Préavis → section `preavis`

---

## Règles

### Tu dois :
- ✅ Extraire TOUT ce qui concerne l'indemnité de mise à la retraite
- ✅ Reformuler clairement (syntaxe, structure)

### Tu ne dois PAS :
- ❌ Confondre avec le départ volontaire
- ❌ Appliquer le Code du travail si la convention est muette

### Si la convention ne dit rien sur un thème :
Écrire : **"Non traité par la convention."**

---

## 📝 Instruction Spécifique : Tableaux Markdown

Si l'information extraite (notamment pour le calcul ou les conditions) est naturellement structurée sous forme de tableau (ex: barème d'ancienneté, montants variables), **tu DOIS la retranscrire en utilisant la syntaxe de tableau Markdown** à l'intérieur du champ `texte` correspondant.

Exemple de format à utiliser dans le champ `texte` :

| Ancienneté | Montant (en mois de salaire) |
| :--- | :--- |
| De 1 à 5 ans | 1/10 de mois par année |
| Au-delà de 5 ans | 1/5 de mois par année |

---

## Format de sortie

```json
{
  "section": "indemnite_mise_retraite",
  
  "conditions_ouverture": {
    "traite": true,
    "contenu": [
      {
        "theme": "Âge requis",
        "texte": "L'employeur peut procéder à la mise à la retraite du salarié ayant atteint l'âge permettant de bénéficier d'une retraite à taux plein."
      },
      {
        "theme": "Procédure",
        "texte": "L'employeur doit interroger le salarié par écrit sur son intention de quitter l'entreprise, 3 mois avant son anniversaire."
      }
    ],
    "articles": ["Art. 36"]
  },

  "calcul": {
    "traite": true,
    "contenu": [
      {
        "theme": "Montant",
        "texte": "L'indemnité de mise à la retraite est calculée selon les mêmes modalités que l'indemnité de licenciement. **Si un barème d'ancienneté est présent, il doit être retranscrit en tableau Markdown.**"
      },
      {
        "theme": "Comparaison",
        "texte": "L'indemnité ne peut être inférieure à l'indemnité légale de licenciement."
      }
    ],
    "articles": []
  },

  "salaire_reference": {
    "traite": true,
    "contenu": [
      {
        "theme": "Mode de calcul",
        "texte": "Le salaire de référence est calculé selon la même méthode que l'indemnité de licenciement."
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
- Âge requis
- Procédure de mise à la retraite
- Délai de prévenance

**Calcul :**
- Montant
- Formule de calcul
- Comparaison avec licenciement

**Salaire de référence :**
- Mode de calcul

---

## ❌ INTERDIT
- Confondre avec le départ volontaire
- Appliquer le Code du travail par défaut

## ✅ OBLIGATOIRE
- Préciser les conditions de mise à la retraite
- Distinguer du départ volontaire

---

## Rappel final

⚠️ **JSON uniquement**
⚠️ **Exhaustivité totale**
⚠️ **Reformulation ≠ Interprétation**
⚠️ **Utiliser les tableaux Markdown pour les barèmes dans les champs `texte`**
