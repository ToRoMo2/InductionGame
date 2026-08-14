"""Le run : plusieurs manches reliees par UN SEUL budget d'essais.

C'est la colonne vertebrale choisie pour l'etape 3 (§14), et le choix est
deliberement etranger a Balatro. La structure evidente — un score cible qui
monte a chaque manche — est sa structure d'antes ; le §11 previent qu'importer
une solution concue pour un jeu d'optimisation a information connue abime la
boucle d'induction de facon invisible.

Ici la ressource partagee est **l'enquete elle-meme**. Fouiller a fond la
premiere manche laisse a sec la cinquieme. Chaque sonde chere devient un
arbitrage entre maintenant et plus tard, et la question « est-ce que je creuse
cette loi ou est-ce que je la lache » se pose a chaque manche. C'est natif au
genre : la rarete de l'information cree le sens (§3, pilier 1).

Deux consequences qu'on n'a pas eu a ecrire, elles tombent toutes seules :

  - le multiplicateur d'essais economises DISPARAIT. Il recompensait deja la
    vitesse ; le report de budget la recompense aussi. Garder les deux paierait
    deux fois la meme vertu et rendrait l'enquete trop chere. Le §9 tient
    toujours, en differe : comprendre vite, c'est avoir de quoi comprendre
    encore ensuite.
  - a la derniere manche, economiser ne sert plus a rien. Le run finit donc en
    tout-ou-rien sans qu'aucune regle ne le stipule.

Pas de defaite ni d'objets dans cette version : le §16.3 reste ouvert, et on
construit d'abord la colonne vertebrale pour la jouer avant d'y accrocher quoi
que ce soit.
"""

from __future__ import annotations

import random
from dataclasses import dataclass, field

from .boss import Roi
from .game import Partie
from .generator import generer

MANCHES = 6

# Plancher mesure : un solveur parfait depense ~19 essais par manche, soit ~114
# pour six. A 120, le joueur ne peut pas s'offrir six enquetes completes : il
# doit choisir lesquelles il creuse. C'est precisement la decision qu'on veut
# faire exister, et le chiffre est le premier a bouger si elle fait mal.
BUDGET = 120


@dataclass
class Bilan:
    manche: int
    points: int
    depense: int
    loi_juste: bool | None  # None si la loi n'a pas ete declaree


@dataclass
class Run:
    seed: int
    manches: int = MANCHES
    budget: int = BUDGET
    n_clauses: int = 2
    roi: Roi | None = None

    restant: int = 0
    score: int = 0
    numero: int = 0
    historique: list[Bilan] = field(default_factory=list)

    def __post_init__(self) -> None:
        self.restant = self.budget

    def manche_suivante(self) -> Partie | None:
        """La manche suivante, ou None si le run est fini."""
        if self.numero >= self.manches:
            return None
        self.numero += 1
        donne = generer(
            seed=self.seed + self.numero,
            n_clauses=self.n_clauses,
            poids=self.roi.poids if self.roi else None,
        )
        # Le budget de la manche EST le reliquat du run : c'est tout le
        # mecanisme. Le multiplicateur ne survit qu'en manche isolee, ou il n'y
        # a pas de suite a qui reporter les essais : sans lui, economiser n'y
        # servirait plus a rien.
        return Partie(
            donne, essais=self.restant, mult_actif=self.manches == 1
        )

    def cloturer(self, p: Partie) -> Bilan:
        depense = self.restant - p.essais_restants
        self.restant = p.essais_restants
        points = p.resolution.points if p.resolution else 0
        self.score += points
        bilan = Bilan(
            self.numero,
            points,
            depense,
            None if p.resolution is None or p.resolution.loi_declaree is None
            else p.resolution.loi_juste,
        )
        self.historique.append(bilan)
        return bilan


def nouveau_run(
    seed: int | None = None,
    manches: int = MANCHES,
    budget: int = BUDGET,
    n_clauses: int = 2,
    roi: Roi | None = None,
) -> Run:
    if seed is None:
        seed = random.randrange(1, 10**9)
    # Un roi fixe le format du duel : c'est lui qui dit combien de manches et
    # combien d'essais, pas les valeurs par defaut.
    if roi is not None:
        manches, budget = roi.manches, roi.budget
    return Run(seed=seed, manches=manches, budget=budget,
               n_clauses=n_clauses, roi=roi)
