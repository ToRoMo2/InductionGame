"""La sonde : le coup du joueur devient une experience concue.

Avant, le joueur nommait une carte et subissait ses attributs. Il voulait
tester le dos ? La carte nommee changeait aussi de rang, d'enseigne et de pli.
Il ne controlait rien, il observait des coincidences — et son talent
n'existait nulle part dans le systeme : taper au hasard ou reflechir cinq
minutes produisait le meme geste.

Ici il DECRIT ce qu'il veut, et le prix depend de sa precision :

    « jaune plié »        → une carte au dos jaune et pliee, le reste au hasard
    « jumelle 3 dos »     → identique a la carte en position 3, sauf le dos

La jumelle est le coeur. C'est l'observation la plus informative du jeu — le
validateur l'appelle « temoin pivot » et compte ces cas-la pour garantir qu'une
loi est deductible. Elle existait dans le moteur sans que le joueur puisse la
demander.

Le tarif est la mecanique centrale, pas un reglage : une carte au hasard ne
coute presque rien et n'apprend presque rien ; une jumelle coute cher et
tranche. Chaque tour pose donc la vraie question — pelle ou scalpel ? — et le
budget interdit de ne jouer qu'au scalpel.
"""

from __future__ import annotations

import random
from dataclasses import dataclass
from typing import Any, Sequence

from .cards import ATTRIBUTS, BASE, LIBRE, Carte, correspond

COUT_BASE = 1  # toute sonde coute au moins un essai


@dataclass(frozen=True)
class Sonde:
    carte: Carte
    cout: int
    intitule: str


def cout_description(contraintes: dict[str, Any]) -> int:
    return COUT_BASE + len(contraintes)


# La jumelle epingle 3 attributs, donc devrait couter 4. Elle est vendue moins
# cher a dessein. Mesure : un solveur glouton qui optimise l'information par
# essai ne la prend JAMAIS a 4 — les sondes larges sont plus rentables par
# essai depense. Mais ce solveur met a jour 1711 hypotheses bayesiennement ; un
# humain non. La valeur d'une jumelle est cognitive, pas informationnelle :
# elle donne un fait directement lisible (« changer le dos a inverse le
# verdict »). A plein tarif, le choix pelle-ou-scalpel n'existerait pas.
COUT_JUMELLE = 3


def cout_jumelle() -> int:
    return COUT_JUMELLE


def tirer(
    pool: Sequence[Carte],
    contraintes: dict[str, Any],
    rng: random.Random,
) -> Sonde | None:
    candidates = [c for c in pool if correspond(c, contraintes)]
    if not candidates:
        return None
    intitule = " ".join(str(v) for v in contraintes.values()) or "au hasard"
    return Sonde(rng.choice(candidates), cout_description(contraintes), intitule)


def jumelle(
    pool: Sequence[Carte],
    reference: Carte,
    attribut: str,
    rng: random.Random,
) -> Sonde | None:
    """Une carte identique a `reference` sauf sur `attribut`.

    couleur et parite ne sont pas independantes : demander une jumelle de
    couleur fait varier l'enseigne, une jumelle de parite fait varier le rang.
    Tous les autres attributs de base restent identiques.
    """
    libre = LIBRE.get(attribut)
    if libre is None:
        return None
    fixes = [a for a in BASE if a != libre]
    cible = ATTRIBUTS[attribut].get(reference)
    candidates = [
        c
        for c in pool
        if ATTRIBUTS[attribut].get(c) != cible
        and all(ATTRIBUTS[a].get(c) == ATTRIBUTS[a].get(reference) for a in fixes)
    ]
    if not candidates:
        return None
    return Sonde(
        rng.choice(candidates),
        cout_jumelle(),
        f"jumelle de {reference.nom_court} sur {ATTRIBUTS[attribut].court}",
    )
