"""Cartes et registre d'attributs.

Regle de construction : ce qui est stocke est independant, ce qui est derive est
calcule. Une carte incoherente (rouge et pique) est donc impossible a fabriquer.

Les briques ne connaissent jamais `rank` ou `suit` directement : elles passent
par ATTRIBUTS. Ajouter une dimension ajoute des lois sans toucher a bricks.py.
"""

from __future__ import annotations

import random
import unicodedata
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


def construire_pool() -> tuple[Carte, ...]:
    """Le produit cartesien complet : 13 x 4 x 2 x 2 = 208 cartes.

    Ce n'est pas un paquet de 52 augmente, c'est un changement de nature. Dans
    un paquet classique, dos et pli sont des FONCTIONS de (rang, enseigne) :
    il n'existe qu'un seul 9♥, avec son dos et son pli figes. Impossible donc
    de faire varier le dos en gardant tout le reste constant — c'est-a-dire
    impossible de mener une experience controlee, la seule chose qu'un joueur
    ait envie de faire.

    Avec le produit complet, toute carte a ses jumelles : une identique sauf
    sur le dos, une identique sauf sur le pli. Isoler une variable devient
    possible, donc l'induction devient un metier plutot qu'une collection de
    coincidences.

    Le paquet n'est jamais affiche en entier — le joueur decrit les cartes au
    lieu de les choisir dans une grille — donc sa taille ne coute rien.
    """
    return tuple(
        Carte(rang, enseigne, dos, pli)
        for enseigne in ENSEIGNES
        for rang in RANGS
        for dos in DOS
        for pli in PLIS
    )


# --- saisie ---------------------------------------------------------------

_RANGS_SAISIE = {
    "a": 1, "as": 1, "1": 1,
    "v": 11, "valet": 11, "j": 11,
    "d": 12, "dame": 12, "q": 12,
    "r": 13, "roi": 13, "k": 13,
}
for _n in range(2, 11):
    _RANGS_SAISIE[str(_n)] = _n

_NOMS_ENSEIGNE = {"pique": "♠", "coeur": "♥", "carreau": "♦", "trefle": "♣"}

# Lettres courtes, symboles, et les abreviations qui ne sont PAS des prefixes
# ("pic" n'est pas un debut de "pique"). Les cas ambigus ("c" pourrait etre
# coeur ou carreau) sont tranches ici une bonne fois ; tout le reste passe par
# le prefixe, donc "piq", "car", "tre", "co" marchent sans etre listes.
_ENSEIGNES_SAISIE = {
    "p": "♠", "s": "♠", "♠": "♠", "pic": "♠", "pik": "♠",
    "c": "♥", "h": "♥", "cœur": "♥", "♥": "♥",
    "k": "♦", "d": "♦", "♦": "♦", "kar": "♦",
    "t": "♣", "♣": "♣", "trefl": "♣",
}


def _sans_accents(s: str) -> str:
    return "".join(
        c for c in unicodedata.normalize("NFD", s) if not unicodedata.combining(c)
    )


def _lire_enseigne(jeton: str) -> str | None:
    """Accepte la lettre, le symbole, le nom complet, et toute abreviation non
    ambigue : « pic », « tre », « car ». Le pluriel est tolere."""
    for forme in (jeton, jeton.rstrip("s")):
        if not forme:
            continue
        if forme in _ENSEIGNES_SAISIE:
            return _ENSEIGNES_SAISIE[forme]
        nu = _sans_accents(forme).replace("œ", "oe")
        if nu in _ENSEIGNES_SAISIE:
            return _ENSEIGNES_SAISIE[nu]
        if len(nu) >= 2:
            trouves = {v for k, v in _NOMS_ENSEIGNE.items() if k.startswith(nu)}
            if len(trouves) == 1:
                return trouves.pop()
    return None


# Attributs reellement independants : ce sont eux qui definissent une carte.
# couleur et parite en decoulent (enseigne -> couleur, rang -> parite).
BASE = ("rang", "enseigne", "dos", "pli")

# Pour une jumelle « identique sauf X », quel attribut de base doit varier.
LIBRE = {
    "rang": "rang", "parite": "rang",
    "enseigne": "enseigne", "couleur": "enseigne",
    "dos": "dos", "pli": "pli",
}


def lire_valeur(jeton: str) -> tuple[str, Any] | None:
    """Un jeton de description → (attribut, valeur).

    Les valeurs sont globalement non ambigues d'un attribut a l'autre, donc le
    joueur enumere simplement ce qu'il veut : « jaune plié 9 » se lit tout seul
    comme dos=jaune, pli=plié, rang=9. Pas de prefixe « dos: » a taper.
    """
    j = _sans_accents(jeton.strip().lower())
    if not j:
        return None

    # 1. valeurs litterales des domaines (rouge, pair, ivoire, lisse...)
    for nom in ("couleur", "parite", "dos", "pli"):
        for v in ATTRIBUTS[nom].domaine:
            if _sans_accents(str(v)) == j:
                return (nom, v)

    # 2. rang. Les lettres seules (a, v, d, r) sont des rangs par convention ;
    #    les enseigne demandent au moins deux caracteres ou un symbole.
    if j in _RANGS_SAISIE:
        return ("rang", _RANGS_SAISIE[j])

    # 3. enseigne
    e = _lire_enseigne(j)
    if e is not None and (len(j) >= 2 or j in ENSEIGNES):
        return ("enseigne", e)
    return None


def lire_description(texte: str) -> dict[str, Any] | None:
    """« jaune plié 9 » → {dos: jaune, pli: plié, rang: 9}.

    Renvoie None si un jeton est incomprehensible ou si deux jetons portent sur
    le meme attribut (« rouge noir » n'a pas de sens).
    """
    jetons = [j for j in texte.replace(",", " ").split() if j]
    if not jetons:
        return {}
    out: dict[str, Any] = {}
    for j in jetons:
        lu = lire_valeur(j)
        if lu is None or lu[0] in out:
            return None
        out[lu[0]] = lu[1]
    return out


def correspond(carte: Carte, contraintes: dict[str, Any]) -> bool:
    return all(ATTRIBUTS[a].get(carte) == v for a, v in contraintes.items())


def parser_carte(texte: str, pool: Sequence[Carte]) -> Carte | None:
    """Tolerant : '7p', '7 pique', 'as coeur', 'R♥', '10 t', 'as pic'.

    Le rang et l'enseigne suffisent : dans un pool fixe de 52, ils identifient
    la carte, donc le joueur n'a jamais a saisir le dos ni le pli.
    """
    t = texte.strip().lower().replace("-", " ").replace("'", " ")
    if not t:
        return None

    # « 5 de coeur », « as de pique » : la liaison est la forme naturelle en
    # francais, elle ne porte aucune information.
    morceaux = [m for m in t.split() if m not in ("de", "d", "du", "des", "le", "la")]
    if not morceaux:
        return None
    if len(morceaux) == 2:
        candidats = [(morceaux[0], morceaux[1])]
    else:
        s = "".join(morceaux)
        candidats = [(s[:i], s[i:]) for i in range(1, len(s))]

    for tr, te in candidats:
        rang = _RANGS_SAISIE.get(tr)
        enseigne = _lire_enseigne(te)
        if rang is None or enseigne is None:
            continue
        for c in pool:
            if c.rang == rang and c.enseigne == enseigne:
                return c
    return None
