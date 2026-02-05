from typing import Dict, List

SECTIONS: List[str] = [
    "accident-travail",
    "amenagement-temps-travail",
    "apprenti",
    "cet",
    "classification",
    "conges-payes",
    "contrat-professionnalisation",
    "contributions-formation",
    "cotisation-mutuelle",
    "cotisation-prevoyance",
    "cotisation-retraite",
    "delai-prevenance",
    "durees-travail",
    "evenements-familiaux",
    "forfait-jours",
    "grille-remuneration",
    "heures-supplementaires",
    "indemnite-depart-retraite",
    "indemnite-licenciement",
    "indemnite-mise-retraite",
    "indemnite-precarite",
    "indemnite-rupture-conventionnelle",
    "informations-generales",
    "majoration-dimanche",
    "majoration-ferie",
    "majoration-nuit",
    "maladie",
    "maternite-paternite",
    "paritarisme-financement",
    "periode-essai",
    "preavis",
    "primes-indemnites-avantages",
    "stagiaire",
    "temps-partiel"
]

SECTION_TITLES: Dict[str, str] = {
    "accident-travail": "Accident de travail",
    "amenagement-temps-travail": "Aménagement du temps de travail",
    "apprenti": "Apprenti",
    "cet": "Compte épargne temps (CET)",
    "classification": "Classification",
    "conges-payes": "Congés payés",
    "contrat-professionnalisation": "Contrat de professionnalisation",
    "contributions-formation": "Contributions formation",
    "cotisation-mutuelle": "Cotisations mutuelle",
    "cotisation-prevoyance": "Cotisations prévoyance",
    "cotisation-retraite": "Cotisations retraite",
    "delai-prevenance": "Délai de prévenance",
    "durees-travail": "Durées du travail",
    "evenements-familiaux": "Événements familiaux",
    "forfait-jours": "Forfait jours",
    "grille-remuneration": "Grille de rémunération",
    "heures-supplementaires": "Heures supplémentaires",
    "indemnite-depart-retraite": "Indemnité de départ à la retraite",
    "indemnite-licenciement": "Indemnité de licenciement",
    "indemnite-mise-retraite": "Indemnité de mise à la retraite",
    "indemnite-precarite": "Indemnité de précarité",
    "indemnite-rupture-conventionnelle": "Indemnité de rupture conventionnelle",
    "informations-generales": "Informations générales",
    "majoration-dimanche": "Majoration dimanche",
    "majoration-ferie": "Majoration jours fériés",
    "majoration-nuit": "Majoration nuit",
    "maladie": "Maladie",
    "maternite-paternite": "Maternité, paternité, adoption",
    "paritarisme-financement": "Paritarisme et financement",
    "periode-essai": "Période d'essai",
    "preavis": "Préavis",
    "primes-indemnites-avantages": "Primes, indemnités et avantages divers",
    "stagiaire": "Stagiaire",
    "temps-partiel": "Temps partiel"
}


class SectionMapper:
    def get_all_sections(self) -> List[str]:
        return SECTIONS
    
    def get_section_title(self, section_id: str) -> str:
        return SECTION_TITLES.get(section_id, section_id)
    
    def create_empty_section(self, section_id: str) -> Dict[str, str]:
        return {
            "title": self.get_section_title(section_id),
            "content": "*Non traité par la convention.*"
        }
    
    def create_all_empty_sections(self) -> Dict[str, Dict[str, str]]:
        return {
            section_id: self.create_empty_section(section_id)
            for section_id in SECTIONS
        }
