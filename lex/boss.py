"""Les adversaires : un roi n'est pas un personnage, c'est un jeu de parametres.

C'est le point le plus important de ce module, et il protege le §3 pilier 2 —
« le contenu emerge des regles, jamais de la production manuelle. Une grammaire,
pas un catalogue. »

Ecrire vingt rois un par un serait un catalogue : produit lentement, consomme
une fois, impossible a etendre sans rediger. Un roi est donc ici une
**ponderation des familles de briques**, un budget et un nombre de manches. On
en engendre quarante d'un coup (`roi_engendre`), chacun se joue differemment, et
la difference est MECANIQUE — pas litteraire. C'est celle-la qui fait qu'on se
prepare contre un adversaire en particulier ; un nom et un blason n'y changent
rien.

Les trois rois nommes ci-dessous ne sont pas du contenu : ce sont des temoins de
test, choisis pour etre maximalement contrastes. La seule question a laquelle
ils servent a repondre est : **affronter le second se sent-il different du
premier ?** Si oui, toute la structure de conquete tient et le reste n'est
qu'habillage. Si non, aucun pixel art ne la sauvera.

Le champ `indice` est ce que la future phase d'etude revelerait. Il decrit une
DISTRIBUTION, jamais une INSTANCE : savoir que ce roi affectionne les
conditionnelles ne dit pas laquelle il a choisie ce soir. C'est ce qui distingue
l'etude d'un objet qui revelerait une clause, interdit par le §8.
"""

from __future__ import annotations

import random
from dataclasses import dataclass, field

FAMILLES = ("absolue", "relation", "sequence", "conditionnelle")


@dataclass(frozen=True)
class Roi:
    cle: str
    nom: str
    poids: dict[str, float] = field(default_factory=dict)
    manches: int = 6
    budget: int = 120
    indice: str = ""
    genre: str = "m"

    @property
    def contracte(self) -> str:
        """« face AU Sénéchal », « face À LA Prévôte », « face À L'Archiviste »."""
        if self.nom.startswith("le "):
            return "au " + self.nom[3:]
        if self.nom.startswith("la "):
            return "à la " + self.nom[3:]
        if self.nom.startswith("l'"):
            return "à l'" + self.nom[2:]
        return "à " + self.nom

    @property
    def pronom(self) -> str:
        return "elle" if self.genre == "f" else "il"

    def resume(self) -> str:
        return f"{self.nom} — {self.manches} manches, {self.budget} essais"


ROIS: tuple[Roi, ...] = (
    Roi(
        cle="senechal",
        nom="le Sénéchal",
        poids={"relation": 6, "conditionnelle": 0.3},
        manches=6,
        budget=130,
        indice="ne juge une carte que par rapport à celle qui la précède",
    ),
    Roi(
        cle="archiviste",
        nom="l'Archiviste",
        poids={"conditionnelle": 6, "absolue": 0.4},
        manches=6,
        budget=130,
        indice="ne pose de règle que sous condition",
    ),
    Roi(
        cle="prevote",
        nom="la Prévôte",
        poids={},
        manches=4,
        budget=70,
        indice="tranche vite et laisse peu de temps",
        genre="f",
    ),
)

PAR_CLE = {r.cle: r for r in ROIS}


def roi_engendre(rng: random.Random, numero: int = 0) -> Roi:
    """Un adversaire tire au sort. La preuve que le roster n'a pas besoin
    d'etre ecrit : une ponderation, un budget, un nombre de manches suffisent a
    produire un style qui se joue differemment."""
    favorite = rng.choice(FAMILLES)
    delaissee = rng.choice([f for f in FAMILLES if f != favorite])
    manches = rng.choice((4, 5, 6, 7))
    # ~20 essais par manche est le plancher d'un solveur parfait ; on tire
    # autour pour que certains adversaires etouffent et d'autres laissent
    # respirer.
    budget = manches * rng.choice((17, 20, 23, 26))
    return Roi(
        cle=f"inconnu-{numero}",
        nom=f"adversaire n°{numero}",
        poids={favorite: 6, delaissee: 0.3},
        manches=manches,
        budget=budget,
        indice=f"penche pour les lois de type « {favorite} »",
    )
