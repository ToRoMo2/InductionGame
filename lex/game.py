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
from .law import Loi
from .validator import equivalentes

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
    points_suite: int
    index_faute: int  # -1 si la suite est valide
    loi_declaree: Loi | None = None
    loi_juste: bool = False
    points_loi: int = 0

    @property
    def points(self) -> int:
        return self.points_suite + self.points_loi


@dataclass
class Partie:
    donne: Donne
    essais: int = ESSAIS
    taille_main: int = MAIN_PARI

    phase: Phase = Phase.ENQUETE
    ligne: list[Carte] = field(default_factory=list)
    # (numero d'essai, carte refusee, position de la ligne a ce moment-la).
    # Rien de decoratif : un refus reste vrai pour toujours DANS SON CONTEXTE,
    # et le contexte change a chaque acceptation. Sans le numero d'essai ni la
    # position, verifier « est-ce que mon hypothese explique ce refus ? »
    # demande de reconstituer la ligne de tete. Comme la ligne ne fait que
    # croitre, la position reste valable pour toujours et pointe sans ambiguite
    # vers la carte qui precedait.
    #
    # Signaler qu'une carte refusee passerait MAINTENANT serait tout autre
    # chose : une information sur le contexte courant que le joueur n'a pas
    # payee, donc interdite par le §6.
    refusees: list[tuple[int, Carte, int]] = field(default_factory=list)
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
        self.refusees.append(
            (self.essais - self.essais_restants, carte, len(self.ligne) - 1)
        )
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

    def resoudre(
        self, suite: Sequence[Carte], loi_declaree: Loi | None = None
    ) -> Resolution:
        """La suite et la declaration sont deux paris independants, de meme
        mise. Enoncer la loi est facultatif : c'est un second risque assume,
        pas un bonus gratuit — sinon tout le monde tenterait sa chance.

        La declaration est jugee sur le COMPORTEMENT, pas sur les mots : une
        formulation differente mais indistinguable de la vraie loi compte
        juste.
        """
        if self.phase is not Phase.PARI:
            raise RuntimeError("il faut d'abord declarer le pari")
        i = self.donne.loi.valide_suite(suite)
        n = len(suite)
        res = Resolution(i < 0, n, n * n if i < 0 else -(n * n), i)

        if loi_declaree is not None:
            res.loi_declaree = loi_declaree
            res.loi_juste = equivalentes(
                self.donne.loi,
                loi_declaree,
                self.donne.pool,
                random.Random(self.donne.seed ^ 0x101),
                self.donne.demarrage,
            )
            res.points_loi = n * n if res.loi_juste else -(n * n)

        self.resolution = res
        self.phase = Phase.FINI
        return res


def nouvelle_partie(
    seed: int | None = None,
    n_clauses: int = 2,
    essais: int = ESSAIS,
) -> Partie:
    return Partie(generer(seed=seed, n_clauses=n_clauses), essais=essais)
