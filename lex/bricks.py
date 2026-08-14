"""Les quatre familles de briques.

Une *brique* est une famille ; une *clause* est une brique dont les parametres
sont lies. Le catalogue de clauses est engendre a partir du registre
d'attributs : il n'y a nulle part une liste de regles ecrite a la main.

Les clauses sont frozen (donc hachables) parce que le validateur les utilise
comme cles pour regrouper des lois par comportement.

    absolue        : porte sur la carte posee, seule.
    relation       : compare la carte posee a la derniere carte acceptee.
    sequence       : interdit une repetition sur la fin de la ligne.
    conditionnelle : « si la precedente a A = x, alors la carte a B = y ».
"""

from __future__ import annotations

from dataclasses import dataclass
from itertools import combinations
from typing import Sequence

from .cards import ATTRIBUTS, CATEGORIELS, Carte

# Amplitude du pas de rang. Six rangs sur treize = 46 % de permissivite,
# identique dans TOUS les contextes : la brique ne cree jamais d'impasse, ce
# qu'un « strictement superieur » ferait des qu'un roi est accepte (§5.4).
#
# Une seule amplitude, et non cinq comme avant. Remonte en jouant : la
# difficulte n'etait pas de deduire que le rang avance, elle etait de DECLARER
# — il fallait la borne exacte pour choisir la bonne entree du menu parmi cinq,
# soit une inference imbriquee dans une autre. Le sens (monte / descend) se
# repere en deux coups ; l'amplitude demandait dix tests qu'on ne fait que si
# on soupconne deja la reponse.
PAS = 6


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
            if mode == "monte":
                return (carte.rang - prec.rang) % 13 in range(1, PAS + 1)
            if mode == "descend":
                return (prec.rang - carte.rang) % 13 in range(1, PAS + 1)
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

        if self.famille == "conditionnelle":
            a_si, v_si, a_alors, v_alors = self.params
            if not ligne:
                return True
            if ATTRIBUTS[a_si].get(ligne[-1]) != v_si:
                return True  # la condition ne se declenche pas : la clause se tait
            return ATTRIBUTS[a_alors].get(carte) == v_alors

        raise ValueError(f"famille inconnue : {self.famille}")

    # --- lecture humaine ---

    @property
    def attrs(self) -> tuple[str, ...]:
        if self.famille == "relation" and self.params[1] in ("monte", "descend"):
            return ("rang",)
        if self.famille == "conditionnelle":
            return (self.params[0], self.params[2])
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
            if mode == "monte":
                return (
                    f"le rang monte de 1 à {PAS} rangs "
                    f"(après le roi on repart à l'as)"
                )
            if mode == "descend":
                return (
                    f"le rang descend de 1 à {PAS} rangs "
                    f"(avant l'as on repart au roi)"
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

        if self.famille == "conditionnelle":
            a_si, v_si, a_alors, v_alors = self.params
            return (
                f"si la précédente a {ATTRIBUTS[a_si].libelle} « {v_si} », "
                f"alors {ATTRIBUTS[a_alors].libelle} est « {v_alors} »"
            )

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
        out.append(Clause("relation", ("rang", "monte", None)))
        out.append(Clause("relation", ("rang", "descend", None)))

    # --- sequence ---
    for nom in CATEGORIELS:
        if nom not in dims:
            continue
        for valeur in ATTRIBUTS[nom].domaine:
            for maxi in (1, 2):
                out.append(Clause("sequence", (nom, valeur, maxi)))

    # --- conditionnelle ---
    # « si la precedente a A = x, alors la carte a B = y ». Quand la condition
    # ne se declenche pas, la clause se tait : elle est donc tres permissive et
    # ne survit jamais seule au calibrage. Elle vit en seconde clause, ce qui
    # est exactement sa place — le §5 la classe en difficulte elevee.
    #
    # C'est le levier de variete, et la raison est mesuree : la grammaire a
    # trois familles ne comptait que 23 FORMES de regle pour 1540 lois, et un
    # attribut de plus n'en ajoute que 4. Une famille, elle, multiplie.
    paires = [
        (nom, v)
        for nom in CATEGORIELS
        if nom in dims
        for v in ATTRIBUTS[nom].domaine
    ]
    for a_si, v_si in paires:
        for a_alors, v_alors in paires:
            if (a_si, v_si) == (a_alors, v_alors):
                continue  # « si X alors X » ne dit rien de neuf
            out.append(Clause("conditionnelle", (a_si, v_si, a_alors, v_alors)))

    return tuple(out)
