"""La manche : phases A (enquete), B (pari), C (resolution).

Logique pure, aucune entree/sortie. La boucle terminal est dans cli.py, ce qui
permet de rejouer une manche entiere en tete sans passer par le clavier.

Decisions de cadrage retenues pour la phase 0 :
  - Pool fixe et visible en phase A : le joueur nomme n'importe quelle carte.
    La testabilite devient une propriete statique, verifiable exactement. La
    main tiree viendra plus tard, une fois la grammaire reglee.
  - Budget d'essais FIXE (§16.1), mais chaque sonde a son PRIX : le joueur
    decrit l'experience qu'il veut et paie sa precision (voir probe.py).
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
from .probe import Sonde
from .validator import contre_exemple, equivalentes

# Plancher mesure : un solveur parfait depense ~15 essais. On garde environ
# le double pour l'inefficacite humaine, comme avant le changement de sonde.
ESSAIS = 30
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
    essais_restants: int = 0
    multiplicateur: float = 1.0
    divergence: tuple | None = None  # (contexte, carte, verdict vrai)

    @property
    def base(self) -> int:
        return self.points_suite + self.points_loi

    @property
    def points(self) -> int:
        return round(self.base * self.multiplicateur)


@dataclass
class Partie:
    donne: Donne
    essais: int = ESSAIS
    taille_main: int = MAIN_PARI

    phase: Phase = Phase.ENQUETE
    ligne: list[Carte] = field(default_factory=list)
    # Toutes les sondes DANS L'ORDRE : (acceptee, carte). L'ordre n'est pas
    # decoratif. Un refus reste vrai pour toujours DANS SON CONTEXTE, et le
    # contexte change a chaque acceptation ; affiche chronologiquement en
    # regard de la ligne, le refus montre de lui-meme quand il a eu lieu et
    # apres quelle carte. C'est la « lisibilite ligne principale / lignes
    # d'erreur » qu'Eleusis nous apprend (§12).
    #
    # Signaler qu'une carte refusee passerait MAINTENANT serait tout autre
    # chose : une information sur le contexte courant que le joueur n'a pas
    # payee, donc interdite par le §6.
    journal: list[tuple[bool, Carte]] = field(default_factory=list)
    essais_restants: int = 0
    sondes: int = 0
    main: tuple[Carte, ...] = ()
    resolution: Resolution | None = None

    def __post_init__(self) -> None:
        if not self.ligne:
            self.ligne = [self.donne.demarrage]
        self.essais_restants = self.essais

    # --- phase A ---

    def jouer(self, sonde: Sonde) -> bool:
        """Le cout de la sonde est preleve sur le budget, pas 1 par coup.

        C'est la mecanique centrale : une carte au hasard ne coute presque rien
        et n'apprend presque rien, une jumelle coute cher et tranche. Le joueur
        arbitre a chaque tour entre la pelle et le scalpel.
        """
        if self.phase is not Phase.ENQUETE:
            raise RuntimeError("la phase d'enquete est terminee")
        if sonde.cout > self.essais_restants:
            raise ValueError("budget insuffisant pour cette sonde")
        self.essais_restants -= sonde.cout
        self.sondes += 1
        accepte = self.donne.loi.accepte(self.ligne, sonde.carte)
        self.journal.append((accepte, sonde.carte))
        if accepte:
            self.ligne.append(sonde.carte)
        return accepte

    # --- phase B ---

    def multiplicateur(self) -> float:
        """Les essais economises MULTIPLIENT le score, ils ne s'y ajoutent pas.

        L'addition serait une faute : elle ferait COUTER des points a l'enquete,
        et permettrait d'empocher le budget entier en declarant n'importe quoi
        au premier tour. Un multiplicateur sur zero fait zero, donc la mise en
        friche ne rapporte rien.

        Il s'applique aux pertes autant qu'aux gains. Sans cela, se precipiter
        serait du gain gratuit — gros si j'ai raison, petit si j'ai tort. Des
        deux cotes, la vitesse cesse d'etre un bonus et devient un
        multiplicateur de risque : c'est le §9 sans la boule de neige du §4.
        """
        if self.essais <= 0:
            return 1.0
        return 1.0 + self.essais_restants / self.essais

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
        # La suite prolonge la carte de depart : elle n'est pas une ligne neuve.
        i = self.donne.loi.valide_suite(suite, (self.donne.demarrage,))
        n = len(suite)
        res = Resolution(i < 0, n, n * n if i < 0 else -(n * n), i)
        res.essais_restants = self.essais_restants
        res.multiplicateur = self.multiplicateur()

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
            if not res.loi_juste:
                res.divergence = contre_exemple(
                    self.donne.loi, loi_declaree, self.donne.pool, self.ligne,
                    random.Random(self.donne.seed ^ 0x102), self.donne.demarrage,
                )

        self.resolution = res
        self.phase = Phase.FINI
        return res


def nouvelle_partie(
    seed: int | None = None,
    n_clauses: int = 2,
    essais: int = ESSAIS,
) -> Partie:
    return Partie(generer(seed=seed, n_clauses=n_clauses), essais=essais)
