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

    def valide_suite(
        self, suite: Sequence[Carte], prefixe: Sequence[Carte] = ()
    ) -> int:
        """Renvoie l'index dans `suite` de la premiere carte invalide, ou -1.

        `prefixe` est la ligne deja posee sur laquelle la suite se greffe. En
        phase B c'est la carte de depart : sans elle, la premiere carte du pari
        n'aurait aucune carte precedente, donc les clauses relationnelles et
        sequentielles ne mordraient pas dessus. Sur les lois sans clause
        absolue — 17 % d'entre elles — n'importe quelle carte serait alors
        acceptee, et un joueur n'ayant rien compris empocherait des points
        garantis en posant une seule carte.
        """
        ligne = list(prefixe)
        for i, carte in enumerate(suite):
            if not self.accepte(ligne, carte):
                return i
            ligne.append(carte)
        return -1

    def plus_longue_suite(
        self,
        cartes: Sequence[Carte],
        prefixe: Sequence[Carte] = (),
        plafond: int = 8,
    ) -> int:
        """Longueur de la meilleure suite qu'on puisse tirer de `cartes`.

        Sert a garantir qu'une main de pari est jouable. Mesure avant
        correction : 2 % des mains tirees au hasard n'autorisaient AUCUNE carte,
        et 6 % plafonnaient a une seule. Le joueur pouvait donc avoir compris la
        loi parfaitement et etre force de perdre — le §3 pilier 3 viole par le
        tirage, pas par la regle.

        DFS avec plafond : les lois etant restrictives, l'arbre s'effondre vite
        et le plafond ne mord qu'en pratique sur les mains tres permissives, ou
        savoir « au moins 8 » suffit.
        """
        meilleur = 0

        def explorer(ligne: list[Carte], restantes: list[Carte], prof: int) -> None:
            nonlocal meilleur
            meilleur = max(meilleur, prof)
            if prof >= plafond:
                return
            for i, c in enumerate(restantes):
                if self.accepte(ligne, c):
                    explorer(ligne + [c], restantes[:i] + restantes[i + 1:], prof + 1)

        explorer(list(prefixe), list(cartes), 0)
        return meilleur

    def texte(self) -> str:
        if len(self.clauses) == 1:
            return self.clauses[0].texte()
        return "\n".join(f"  {i}. {c.texte()}" for i, c in enumerate(self.clauses, 1))

    def __len__(self) -> int:
        return len(self.clauses)

    def __str__(self) -> str:
        return " ET ".join(c.texte() for c in self.clauses)
