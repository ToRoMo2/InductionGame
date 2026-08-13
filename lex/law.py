"""La loi : une conjonction de clauses, et son evaluateur.

C'est le « verificateur » au sens etroit : dire si une carte passe. Les
controles de qualite d'une loi (permissivite, deductibilite) sont dans
validator.py, qui est un tout autre metier.

Le ET est le seul mode de combinaison en phase 0 (le cahier des charges dit
« 1 a 3 briques combinees » sans preciser lequel).
"""

from __future__ import annotations

from dataclasses import dataclass
from typing import Sequence

from .bricks import Clause
from .cards import Carte


@dataclass(frozen=True)
class Loi:
    clauses: tuple[Clause, ...]

    def accepte(self, ligne: Sequence[Carte], carte: Carte) -> bool:
        return all(c.tient(ligne, carte) for c in self.clauses)

    def clauses_fautives(self, ligne: Sequence[Carte], carte: Carte) -> tuple[Clause, ...]:
        """Diagnostic interne. N'est jamais montre au joueur : le §6 interdit
        de reveler l'attribut fautif, sans quoi la deduction devient de
        l'elimination mecanique."""
        return tuple(c for c in self.clauses if not c.tient(ligne, carte))

    def valide_suite(self, suite: Sequence[Carte]) -> int:
        """Renvoie l'index de la premiere carte invalide, ou -1 si tout passe.

        La suite est evaluee seule, comme une ligne neuve : elle ne prolonge
        pas la ligne principale.
        """
        for i in range(len(suite)):
            if not self.accepte(suite[:i], suite[i]):
                return i
        return -1

    def texte(self) -> str:
        if len(self.clauses) == 1:
            return self.clauses[0].texte()
        return "\n".join(f"  {i}. {c.texte()}" for i, c in enumerate(self.clauses, 1))

    def __len__(self) -> int:
        return len(self.clauses)

    def __str__(self) -> str:
        return " ET ".join(c.texte() for c in self.clauses)
