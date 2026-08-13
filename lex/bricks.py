"""Les trois familles de briques (phase 0).

Une *brique* est une famille ; une *clause* est une brique dont les parametres
sont lies. Le catalogue de clauses est engendre a partir du registre
d'attributs : il n'y a nulle part une liste de regles ecrite a la main.

Les clauses sont frozen (donc hachables) parce que le validateur les utilise
comme cles pour regrouper des lois par comportement.

    absolue    : porte sur la carte posee, seule.
    relation   : compare la carte posee a la derniere carte acceptee.
    sequence   : interdit une repetition sur la fin de la ligne.
"""

from __future__ import annotations

from dataclasses import dataclass
from itertools import combinations
from typing import Sequence

from .cards import ATTRIBUTS, CATEGORIELS, Carte

# Cadence de l'avance cyclique du rang. k=6 donne 6/13 = 46 % de permissivite,
# identique dans tous les contextes : cette brique ne cree jamais d'impasse.
AVANCES = (4, 5, 6, 7, 8)


@dataclass(frozen=True)
class Clause:
    famille: str
    params: tuple

    # --- evaluation ---

    def tient(self, ligne: Sequence[Carte], carte: Carte) -> bool:
        if self.famille == "absolue":
            nom, valeurs = self.params
            return ATTRIBUTS[nom].get(carte) in valeurs

        if self.famille == "relation":
            nom, mode, arg = self.params
            if not ligne:
                return True  # rien a comparer : la clause ne dit rien
            prec = ligne[-1]
            if mode == "avance":
                return (carte.rang - prec.rang) % 13 in range(1, arg + 1)
            a, b = ATTRIBUTS[nom].get(carte), ATTRIBUTS[nom].get(prec)
            return a == b if mode == "egal" else a != b

        if self.famille == "sequence":
            nom, valeur, maxi = self.params
            get = ATTRIBUTS[nom].get
            if get(carte) != valeur:
                return True
            suite = 0
            for c in reversed(ligne):
                if get(c) != valeur:
                    break
                suite += 1
            return suite < maxi

        raise ValueError(f"famille inconnue : {self.famille}")

    # --- lecture humaine ---

    @property
    def attrs(self) -> tuple[str, ...]:
        if self.famille == "relation" and self.params[1] == "avance":
            return ("rang",)
        return (self.params[0],)

    def texte(self) -> str:
        if self.famille == "absolue":
            nom, valeurs = self.params
            attr = ATTRIBUTS[nom]
            interdites = [v for v in attr.domaine if v not in valeurs]
            if len(interdites) == 1:
                return f"{attr.libelle} n'est jamais « {interdites[0]} »"
            autorisées = " ou ".join(f"« {v} »" for v in valeurs)
            return f"{attr.libelle} est toujours {autorisées}"

        if self.famille == "relation":
            nom, mode, arg = self.params
            if mode == "avance":
                return (
                    f"le rang avance de 1 à {arg} rangs par rapport à la carte "
                    f"précédente (après le roi on repart à l'as)"
                )
            attr = ATTRIBUTS[nom]
            if mode == "egal":
                return f"{attr.libelle} est {attr.meme} que {attr.celui} de la carte précédente"
            return f"{attr.libelle} diffère de {attr.celui} de la carte précédente"

        if self.famille == "sequence":
            nom, valeur, maxi = self.params
            attr = ATTRIBUTS[nom]
            if maxi == 1:
                return f"jamais deux « {valeur} » ({attr.court}) d'affilée"
            return f"jamais plus de {maxi} « {valeur} » ({attr.court}) d'affilée"

        raise ValueError(f"famille inconnue : {self.famille}")

    def __str__(self) -> str:
        return self.texte()


def catalogue(dims: Sequence[str]) -> tuple[Clause, ...]:
    """Toutes les clauses constructibles sur les dimensions actives.

    C'est a la fois l'espace de tirage du generateur et l'espace d'hypotheses
    du validateur. Les deux doivent rester la meme chose : si le generateur
    pouvait produire une loi que le validateur n'envisage pas comme rivale,
    la garantie de deductibilite serait fausse.
    """
    dims = tuple(dims)
    out: list[Clause] = []

    # --- absolue : sous-ensembles propres du domaine, categoriels seuls ---
    for nom in CATEGORIELS:
        if nom not in dims:
            continue
        dom = ATTRIBUTS[nom].domaine
        for taille in range(1, len(dom)):
            if taille * 2 < len(dom):
                continue  # trop restrictif pour tenir dans le calibrage
            for sous in combinations(dom, taille):
                out.append(Clause("absolue", (nom, sous)))

    # --- relation ---
    for nom in CATEGORIELS:
        if nom not in dims:
            continue
        out.append(Clause("relation", (nom, "egal", None)))
        out.append(Clause("relation", (nom, "different", None)))
    if "rang" in dims:
        out.append(Clause("relation", ("rang", "different", None)))
        for k in AVANCES:
            out.append(Clause("relation", ("rang", "avance", k)))

    # --- sequence ---
    for nom in CATEGORIELS:
        if nom not in dims:
            continue
        for valeur in ATTRIBUTS[nom].domaine:
            for maxi in (1, 2):
                out.append(Clause("sequence", (nom, valeur, maxi)))

    return tuple(out)
