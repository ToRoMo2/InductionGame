"""La manche : phases A (enquete), B (pari), C (resolution).

Logique pure, aucune entree/sortie. La boucle terminal est dans cli.py, ce qui
permet de rejouer une manche entiere en tete sans passer par le clavier.

Decisions de cadrage retenues pour la phase 0 :
  - Pool fixe et visible en phase A : le joueur nomme n'importe quelle carte.
    La testabilite devient une propriete statique, verifiable exactement. La
    main tiree viendra plus tard, une fois la grammaire reglee.
  - Budget d'essais FIXE (§16.1). Acceptations et refus consomment pareil.
  - Pari a longueur libre, tout ou rien (§16.2), depuis une main bornee
    (§4B interdit l'acces total au paquet).
"""

from __future__ import annotations

import random
from dataclasses import dataclass, field
from enum import Enum
from typing import Sequence

from .cards import Carte
from .generator import Donne, generer

ESSAIS = 20
MAIN_PARI = 12


class Phase(Enum):
    ENQUETE = "enquete"
    PARI = "pari"
    FINI = "fini"


@dataclass
class Resolution:
    valide: bool
    longueur: int
    points: int
    index_faute: int  # -1 si la suite est valide


@dataclass
class Partie:
    donne: Donne
    essais: int = ESSAIS
    taille_main: int = MAIN_PARI

    phase: Phase = Phase.ENQUETE
    ligne: list[Carte] = field(default_factory=list)
    refusees: list[Carte] = field(default_factory=list)
    essais_restants: int = 0
    main: tuple[Carte, ...] = ()
    resolution: Resolution | None = None

    def __post_init__(self) -> None:
        if not self.ligne:
            self.ligne = [self.donne.demarrage]
        self.essais_restants = self.essais

    # --- phase A ---

    def jouer(self, carte: Carte) -> bool:
        if self.phase is not Phase.ENQUETE:
            raise RuntimeError("la phase d'enquete est terminee")
        if self.essais_restants <= 0:
            raise RuntimeError("plus d'essais")
        self.essais_restants -= 1
        if self.donne.loi.accepte(self.ligne, carte):
            self.ligne.append(carte)
            return True
        self.refusees.append(carte)
        return False

    # --- phase B ---

    def passer_au_pari(self, rng: random.Random | None = None) -> tuple[Carte, ...]:
        if self.phase is not Phase.ENQUETE:
            raise RuntimeError("le pari a deja commence")
        rng = rng or random.Random(self.donne.seed ^ 0xBE7)
        self.main = tuple(sorted(rng.sample(self.donne.pool, self.taille_main)))
        self.phase = Phase.PARI
        return self.main

    # --- phase C ---

    def resoudre(self, suite: Sequence[Carte]) -> Resolution:
        if self.phase is not Phase.PARI:
            raise RuntimeError("il faut d'abord declarer le pari")
        i = self.donne.loi.valide_suite(suite)
        n = len(suite)
        points = n * n if i < 0 else -(n * n)
        self.resolution = Resolution(i < 0, n, points, i)
        self.phase = Phase.FINI
        return self.resolution


def nouvelle_partie(
    seed: int | None = None,
    n_clauses: int = 2,
    essais: int = ESSAIS,
) -> Partie:
    return Partie(generer(seed=seed, n_clauses=n_clauses), essais=essais)
