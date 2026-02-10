# Extraction : Indemnité de rupture conventionnelle

## Objectif

Extraire et reformuler les règles conventionnelles relatives à l'**indemnité de rupture conventionnelle**.

**Tu es un outil de consultation.** Tu récupères l'information et tu la réorganises. C'est tout.

---

## ⚠️ PÉRIMÈTRE STRICT

Cette section concerne **UNIQUEMENT** l'indemnité de rupture conventionnelle individuelle.

### ❌ NE PAS inclure ici :
- Indemnité de licenciement → section `indemnite-licenciement`
- Rupture conventionnelle collective → section distincte si applicable

---

## Règles

### Tu dois :
- ✅ Extraire TOUT ce qui concerne l'indemnité de rupture conventionnelle
- ✅ Reformuler clairement (syntaxe, structure)

### Tu ne dois PAS :
- ❌ Appliquer le Code du travail si la convention est muette
- ❌ Confondre avec l'indemnité de licenciement

### Si la convention ne dit rien sur un thème :
Écrire : **"Non traité par la convention."**

---

## 📝 Instructions de formatage spécifiques

### Tableaux Markdown dans les champs `texte`

Si l'information extraite est présentée sous forme de tableau dans la convention collective (par exemple, un barème d'ancienneté ou un tableau de montants), tu **DOIS** la retranscrire en utilisant la syntaxe de tableau Markdown à l'intérieur du champ `texte` correspondant.

**Exemple de tableau Markdown :**

| Ancienneté | Montant (en mois de salaire) |
| :--- | :--- |
| De 1 à 5 ans | 1/5ème |
| Au-delà de 5 ans | 1/5ème + 2/15ème par année supplémentaire |

---

## Format de sortie

```json
{
  "section": "indemnite_rupture_conventionnelle",
  
  "montant": {
    "traite": true,
    "contenu": [
      {
        "theme": "Règle de calcul",
        "texte": "L'indemnité de rupture conventionnelle ne peut être inférieure à l'indemnité conventionnelle de licenciement si celle-ci est plus favorable que l'indemnité légale."
      },
      {
        "theme": "Comparaison",
        "texte": "Le salarié bénéficie du montant le plus élevé entre l'indemnité légale de licenciement et l'indemnité conventionnelle de licenciement."
      }
    ],
    "articles": ["Art. 32"]
  },

  "salaire_reference": {
    "traite": true,
    "contenu": [
      {
        "theme": "Mode de calcul",
        "texte": "Le salaire de référence est calculé selon les mêmes modalités que l'indemnité de licenciement."
      }
    ],
    "articles": []
  },

  "anciennete": {
    "traite": true,
    "contenu": [
      {
        "theme": "Point de départ",
        "texte": "L'ancienneté s'apprécie à la date de rupture effective du contrat fixée dans la convention de rupture."
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


**Montant :**
- Règle de calcul
- Comparaison avec licenciement
- Minimum conventionnel

**Salaire de référence :**
- Mode de calcul
- Période de référence

**Ancienneté :**
- Point de départ
- Périodes prises en compte

---

## ❌ INTERDIT
- Appliquer le Code du travail par défaut
- Confondre avec l'indemnité de licenciement

## ✅ OBLIGATOIRE
- Préciser le minimum applicable
- Indiquer la référence au calcul de l'indemnité de licenciement

---

## Rappel final

⚠️ **JSON uniquement**
⚠️ **Exhaustivité totale**
⚠️ **Reformulation ≠ Interprétation**
