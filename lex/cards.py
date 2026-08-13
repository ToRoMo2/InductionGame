"""Cartes et registre d'attributs.

Regle de construction : ce qui est stocke est independant, ce qui est derive est
calcule. Une carte incoherente (rouge et pique) est donc impossible a fabriquer.

Les briques ne connaissent jamais `rank` ou `suit` directement : elles passent
par ATTRIBUTS. Ajouter une dimension ajoute des lois sans toucher a bricks.py.
"""

from __future__ import annotations

import random
from dataclasses import dataclass
from typing import Any, Callable, Sequence

RANGS = tuple(range(1, 14))
ENSEIGNES = ("♠", "♥", "♦", "♣")  # pique coeur carreau trefle
ROUGES = frozenset({"♥", "♦"})
DOS = ("ivoire", "jaune")
PLIS = ("lisse", "plié")

NOM_RANG = {1: "A", 11: "V", 12: "D", 13: "R"}


@dataclass(frozen=True, order=True)
class Carte:
    rang: int
    enseigne: str
    dos: str
    pli: str

    @property
    def couleur(self) -> str:
        return "rouge" if self.enseigne in ROUGES else "noir"

    @property
    def parite(self) -> str:
        return "pair" if self.rang % 2 == 0 else "impair"

    @property
    def nom_court(self) -> str:
        return f"{NOM_RANG.get(self.rang, str(self.rang))}{self.enseigne}"

    def __str__(self) -> str:
        return f"{self.nom_court} [dos:{self.dos}] [{self.pli}]"


@dataclass(frozen=True)
class Attribut:
    nom: str
    get: Callable[[Carte], Any]
    domaine: tuple
    libelle: str  # avec article, pour les phrases : « le dos n'est jamais... »
    court: str    # sans article, pour les incises
    genre: str    # "m" / "f" — pour accorder « le même » / « la même »

    @property
    def meme(self) -> str:
        return "la même" if self.genre == "f" else "le même"

    @property
    def celui(self) -> str:
        return "celle" if self.genre == "f" else "celui"


ATTRIBUTS: dict[str, Attribut] = {
    "rang": Attribut("rang", lambda c: c.rang, RANGS, "le rang", "rang", "m"),
    "couleur": Attribut("couleur", lambda c: c.couleur, ("rouge", "noir"), "la couleur", "couleur", "f"),
    "enseigne": Attribut("enseigne", lambda c: c.enseigne, ENSEIGNES, "l'enseigne", "enseigne", "f"),
    "parite": Attribut("parite", lambda c: c.parite, ("pair", "impair"), "la parité du rang", "parité", "f"),
    "dos": Attribut("dos", lambda c: c.dos, DOS, "le dos", "dos", "m"),
    "pli": Attribut("pli", lambda c: c.pli, PLIS, "le pli", "pli", "m"),
}

# Attributs a domaine fini non ordonne : seuls ceux-la portent des clauses
# absolues et sequentielles. Le rang n'entre que par la relation (voir bricks).
CATEGORIELS = ("couleur", "enseigne", "parite", "dos", "pli")

DIMS_DEFAUT = ("rang", "couleur", "enseigne", "parite", "dos", "pli")


def construire_pool(rng: random.Random) -> tuple[Carte, ...]:
    """52 cartes. Dos et pli sont repartis de facon equilibree puis melanges.

    L'equilibre n'est pas cosmetique : il rend la permissivite d'une clause
    absolue previsible, donc le calibrage du generateur stable d'une graine
    a l'autre.
    """
    n = len(RANGS) * len(ENSEIGNES)
    dos = [DOS[0]] * (n // 2) + [DOS[1]] * (n - n // 2)
    plis = [PLIS[1]] * (n // 3) + [PLIS[0]] * (n - n // 3)
    rng.shuffle(dos)
    rng.shuffle(plis)
    cartes = []
    i = 0
    for enseigne in ENSEIGNES:
        for rang in RANGS:
            cartes.append(Carte(rang, enseigne, dos[i], plis[i]))
            i += 1
    return tuple(cartes)


# --- saisie ---------------------------------------------------------------

_RANGS_SAISIE = {
    "a": 1, "as": 1, "1": 1,
    "v": 11, "valet": 11, "j": 11,
    "d": 12, "dame": 12, "q": 12,
    "r": 13, "roi": 13, "k": 13,
}
for _n in range(2, 11):
    _RANGS_SAISIE[str(_n)] = _n

_ENSEIGNES_SAISIE = {
    "p": "♠", "pique": "♠", "♠": "♠", "s": "♠",
    "c": "♥", "coeur": "♥", "cœur": "♥", "♥": "♥", "h": "♥",
    "k": "♦", "car": "♦", "carreau": "♦", "♦": "♦", "d": "♦",
    "t": "♣", "tr": "♣", "trefle": "♣", "trèfle": "♣", "♣": "♣",
}


def parser_carte(texte: str, pool: Sequence[Carte]) -> Carte | None:
    """Tolerant : '7p', '7 pique', 'as coeur', 'R♥', '10 t'.

    Le rang et l'enseigne suffisent : dans un pool fixe de 52, ils identifient
    la carte, donc le joueur n'a jamais a saisir le dos ni le pli.
    """
    t = texte.strip().lower().replace("-", " ")
    if not t:
        return None

    morceaux = t.split()
    if len(morceaux) == 2:
        candidats = [(morceaux[0], morceaux[1])]
    else:
        s = "".join(morceaux)
        candidats = [(s[:i], s[i:]) for i in range(1, len(s))]

    for tr, te in candidats:
        rang = _RANGS_SAISIE.get(tr)
        enseigne = _ENSEIGNES_SAISIE.get(te)
        if rang is None or enseigne is None:
            continue
        for c in pool:
            if c.rang == rang and c.enseigne == enseigne:
                return c
    return None
