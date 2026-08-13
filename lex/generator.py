"""Generateur de loi. Module autonome, appelable sans la boucle de jeu.

Le generateur ne « fabrique » pas une bonne loi : il en propose au hasard et
laisse le validateur les refuser (propose-and-test). C'est plus lent et
infiniment plus honnete qu'une heuristique de construction, parce que le
critere de qualite reste au meme endroit pour tout le monde.

Point d'architecture non negociable : la loi est validee CONTRE LE POOL
REALISE et rendue avec lui. Valider une loi contre un paquet abstrait puis
tirer les cartes independamment detruit la garantie de deductibilite.
"""

from __future__ import annotations

import argparse
import random
from dataclasses import dataclass
from typing import Sequence

from .bricks import catalogue
from .cards import DIMS_DEFAUT, Carte, construire_pool
from .law import Loi
from .validator import Rapport, analyser

TENTATIVES = 400
DEPARTS_ESSAYES = 6  # departs distincts testes par loi candidate


@dataclass(frozen=True)
class Donne:
    """Une manche prete a jouer : la loi ET le pool contre lequel elle a ete
    validee, plus la carte de depart."""
    loi: Loi
    pool: tuple[Carte, ...]
    demarrage: Carte
    rapport: Rapport
    seed: int
    dims: tuple[str, ...]


def generer(
    seed: int | None = None,
    n_clauses: int = 2,
    dims: Sequence[str] = DIMS_DEFAUT,
    tentatives: int = TENTATIVES,
) -> Donne:
    if seed is None:
        seed = random.randrange(1, 10**9)
    dims = tuple(dims)
    pool = construire_pool()
    rng = random.Random(seed ^ 0x5EED)
    cat = catalogue(dims)

    for taille in range(n_clauses, 0, -1):
        for _ in range(tentatives):
            clauses = tuple(rng.sample(cat, taille))
            loi = Loi(clauses)

            # La carte de depart fait partie de ce qu'on valide. Une meme loi
            # peut etre deductible depuis un depart et pas depuis un autre :
            # « meme couleur que la precedente » verrouille la ligne sur la
            # couleur du depart, ce qui peut rendre une autre clause
            # inobservable. On essaie donc plusieurs departs avant d'abandonner
            # la loi.
            # Le depart doit satisfaire la loi. Sur une ligne vide seules les
            # clauses absolues mordent, donc la contrainte est legere — mais
            # sans elle, la position 0 de la ligne peut contredire la loi et
            # le joueur rejette une hypothese correcte a cause de la carte
            # qu'on lui a donnee. §3 pilier 3. Mesure avant correction : 24 %
            # des manches. Le probleme s'aggrave depuis que la suite du pari
            # prolonge le depart : il serait la tete d'une sequence notee tout
            # en etant exempte de la regle qui note cette sequence.
            conformes = [c for c in pool if loi.accepte([], c)]
            if not conformes:
                continue
            for depart in rng.sample(
                conformes, min(DEPARTS_ESSAYES, len(conformes))
            ):
                # etage 1 : controles bon marche (permissivite, temoins). La
                # plupart des candidats meurent ici, et on evite ainsi de payer
                # l'enumeration de l'espace d'hypotheses pour rien.
                rap = analyser(loi, pool, dims, rng, depart, complet=False)
                if not rap.ok:
                    continue

                # etage 2 : identifiabilite exacte sur toute la grammaire.
                rap = analyser(loi, pool, dims, rng, depart, complet=True)
                if not rap.ok:
                    continue

                return Donne(rap.representant or loi, pool, depart, rap, seed, dims)

    raise RuntimeError(
        f"aucune loi valide trouvee en {tentatives} tentatives (graine {seed})"
    )


def _main(argv: Sequence[str] | None = None) -> int:
    p = argparse.ArgumentParser(
        prog="python -m lex.generator",
        description="Engendre des lois valides et les affiche.",
    )
    p.add_argument("--seed", type=int, default=None)
    p.add_argument("--clauses", type=int, default=2)
    p.add_argument("--n", type=int, default=1, help="nombre de lois a engendrer")
    args = p.parse_args(argv)

    for i in range(args.n):
        seed = args.seed if args.seed is not None else None
        if args.seed is not None and args.n > 1:
            seed = args.seed + i
        d = generer(seed=seed, n_clauses=args.clauses)
        r = d.rapport
        print(f"[graine {d.seed}] depart {d.demarrage}")
        for c in d.loi.clauses:
            print(f"    · {c.texte()}")
        print(
            f"    permissivité {r.perm_moy:.0%} (min {r.perm_min:.0%}) — "
            f"témoins {sorted(r.temoins.values())} — "
            f"{r.classes} classes, {r.rivales_fragiles} fragiles"
        )
        print()
    return 0


if __name__ == "__main__":
    raise SystemExit(_main())
