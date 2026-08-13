"""Controle qualite d'une loi. Module autonome, appelable sans la boucle de jeu.

Le cahier des charges (§5.2) formule la testabilite en frequence : « un attribut
qui n'apparait qu'une fois toutes les trente cartes est indeductible ». Ce n'est
pas le vrai danger.

Le vrai danger est le MASQUAGE. Dans une conjonction, un refus dit seulement
« au moins une clause a echoue ». Si la clause A refuse 80 % des cartes, presque
toute carte qui viole B viole aussi A : B devient invisible quelle que soit sa
frequence d'apparition. Une clause parfaitement frequente peut etre
parfaitement indeductible.

La bonne question n'est donc pas « l'attribut sort-il assez souvent » mais
« la loi est-elle separable de ses rivales dans le flux reellement atteignable ».

Methode : on echantillonne des contextes atteignables SOUS la loi (on ne
prolonge la ligne qu'avec des cartes acceptees), puis on encode le comportement
de chaque clause sur contextes x pool dans un entier Python utilise comme
masque de bits. Le masque d'une loi est le ET de ses clauses. Toute l'analyse
devient de l'arithmetique entiere, ce qui rend l'enumeration exacte de
l'espace d'hypotheses (~1700 lois) quasi gratuite.

Limites, explicitement :
  - identifiable != deductible par un humain. On garantit qu'aucune rivale de
    la grammaire ne survit aux observations, pas qu'un humain converge.
  - la garantie est relative a NOTRE grammaire. Un joueur entretient des
    hypotheses hors grammaire.
  - l'atteignabilite est echantillonnee, pas enumeree.
  - le compte de temoins pivots est un substitut bon marche a la lisibilite
    humaine. La verification complete (simulation d'un joueur-sonde a budget
    borne) n'est volontairement pas implementee : son seuil ne peut se regler
    que contre des parties reelles.
"""

from __future__ import annotations

import argparse
import random
from dataclasses import dataclass, field
from typing import Sequence

from .bricks import Clause, catalogue
from .cards import Carte
from .law import Loi

# --- seuils de calibrage (les boutons a tourner apres chaque partie) -------

PERM_MIN = 0.25          # §5.1 : un quart du paquet jouable
PERM_MAX = 0.50          # §5.1 : la moitie au plus
PERM_PLANCHER = 0.08     # §5.4 lu comme anti-impasse : jamais un contexte mort
TEMOINS_MIN = 12         # refus imputables a une seule clause
CONTEXTES_TEMOINS_MIN = 3
RIVALES_FRAGILES_MAX = 6  # rivales separees par <= 2 observations

N_CONTEXTES = 24
PROFONDEUR_MAX = 5


@dataclass
class Rapport:
    ok: bool = True
    motifs: list[str] = field(default_factory=list)
    perm_moy: float = 0.0
    perm_min: float = 0.0
    perm_max: float = 0.0
    temoins: dict[Clause, int] = field(default_factory=dict)
    temoins_contextes: dict[Clause, int] = field(default_factory=dict)
    n_contextes: int = 0
    classes: int = 0
    rivales_fragiles: int = 0
    separation_min: int = 0
    representant: Loi | None = None

    def rejeter(self, motif: str) -> None:
        self.ok = False
        self.motifs.append(motif)


# --- contextes atteignables ----------------------------------------------

def contextes(
    loi: Loi,
    pool: Sequence[Carte],
    rng: random.Random,
    n: int = N_CONTEXTES,
    profondeur_max: int = PROFONDEUR_MAX,
) -> tuple[tuple[Carte, ...], ...]:
    """Lignes que le joueur peut reellement rencontrer sous cette loi.

    La premiere carte est distribuee (elle n'a pas a etre acceptee), les
    suivantes doivent l'etre : la loi contraint ses propres contextes, et
    c'est precisement ce qui rend l'analyse honnete.
    """
    vus: set[tuple[Carte, ...]] = set()
    out: list[tuple[Carte, ...]] = []
    for _ in range(n * 20):
        if len(out) >= n:
            break
        ligne = [rng.choice(pool)]
        cible = rng.randint(1, profondeur_max)
        viable = True
        while len(ligne) < cible:
            cands = [c for c in pool if loi.accepte(ligne, c)]
            if not cands:
                viable = False
                break
            ligne.append(rng.choice(cands))
        cle = tuple(ligne)
        if viable and cle not in vus:
            vus.add(cle)
            out.append(cle)
    return tuple(out)


# --- masques --------------------------------------------------------------

def masque_clause(
    clause: Clause,
    ctxs: Sequence[Sequence[Carte]],
    pool: Sequence[Carte],
) -> int:
    """Bit (i * len(pool) + j) allume si la clause tient pour la carte j
    dans le contexte i."""
    m = 0
    largeur = len(pool)
    for i, ctx in enumerate(ctxs):
        base = i * largeur
        for j, carte in enumerate(pool):
            if clause.tient(ctx, carte):
                m |= 1 << (base + j)
    return m


def _popcount(x: int) -> int:
    return bin(x).count("1")


def _perm_par_contexte(m: int, n_ctx: int, largeur: int) -> list[float]:
    plein = (1 << largeur) - 1
    return [
        _popcount((m >> (i * largeur)) & plein) / largeur
        for i in range(n_ctx)
    ]


# --- analyse --------------------------------------------------------------

def analyser(
    loi: Loi,
    pool: Sequence[Carte],
    dims: Sequence[str],
    rng: random.Random,
    complet: bool = True,
) -> Rapport:
    """Verdict sur une loi. `complet=False` s'arrete apres les controles bon
    marche (permissivite, temoins) : c'est ce que fait le generateur pour ne
    pas payer l'enumeration de l'espace d'hypotheses sur des candidats qui
    echouent de toute facon au calibrage."""
    rap = Rapport()
    ctxs = contextes(loi, pool, rng)
    rap.n_contextes = len(ctxs)
    if not ctxs:
        rap.rejeter("aucun contexte atteignable")
        return rap

    largeur = len(pool)
    total_bits = len(ctxs) * largeur
    plein = (1 << total_bits) - 1

    masques = [masque_clause(c, ctxs, pool) for c in loi.clauses]
    m_loi = plein
    for m in masques:
        m_loi &= m

    # 1. calibrage de permissivite (§5.1) et anti-impasse (§5.4)
    perms = _perm_par_contexte(m_loi, len(ctxs), largeur)
    rap.perm_moy = sum(perms) / len(perms)
    rap.perm_min = min(perms)
    rap.perm_max = max(perms)
    if not (PERM_MIN <= rap.perm_moy <= PERM_MAX):
        rap.rejeter(f"permissivite moyenne hors cible ({rap.perm_moy:.0%})")
    if rap.perm_min < PERM_PLANCHER:
        rap.rejeter(f"contexte quasi-mort ({rap.perm_min:.0%} jouable)")

    # 2. temoins pivots : refus imputables a une seule clause.
    #    C'est le controle qui traite le masquage, et le plus important des
    #    controles bon marche.
    for i, ci in enumerate(loi.clauses):
        autres = plein
        for j, mj in enumerate(masques):
            if j != i:
                autres &= mj
        seul_fautif = (~masques[i]) & plein & autres
        rap.temoins[ci] = _popcount(seul_fautif)
        rap.temoins_contextes[ci] = sum(
            1
            for k in range(len(ctxs))
            if (seul_fautif >> (k * largeur)) & ((1 << largeur) - 1)
        )
        if rap.temoins[ci] < TEMOINS_MIN:
            rap.rejeter(f"clause masquee : « {ci.texte()} » ({rap.temoins[ci]} temoins)")
        elif rap.temoins_contextes[ci] < CONTEXTES_TEMOINS_MIN:
            rap.rejeter(f"clause observable dans trop peu de contextes : « {ci.texte()} »")

    if not complet or not rap.ok:
        return rap

    # 3. enumeration exacte de l'espace d'hypotheses.
    #    Regroupement par masque = canonicalisation extensionnelle : « rang
    #    pair » et « rang non impair » tombent dans la meme classe. Sans cette
    #    etape, l'identifiabilite echouerait pour une raison purement
    #    syntaxique.
    cat = catalogue(dims)
    m_cat = [masque_clause(c, ctxs, pool) for c in cat]

    classes: dict[int, Loi] = {}
    for i, ci in enumerate(cat):
        _retenir(classes, m_cat[i], Loi((ci,)))
    if len(loi.clauses) >= 2:
        for i in range(len(cat)):
            for j in range(i + 1, len(cat)):
                _retenir(classes, m_cat[i] & m_cat[j], Loi((cat[i], cat[j])))

    rap.classes = len(classes)
    rap.representant = classes.get(m_loi, loi)

    # Si le representant de la classe est plus court que la loi proposee, une
    # clause est redondante sur l'espace atteignable : on annoncerait au joueur
    # une loi dont il n'a jamais pu observer une partie. §3 pilier 3.
    if len(rap.representant) < len(loi):
        rap.rejeter("clause redondante : la loi se reduit a une loi plus courte")

    # 4. fragilite : combien de rivales ne sont separees que par une poignee
    #    d'observations ? Une rivale separee par 1 seule observation sur ~1200
    #    est une rivale que le joueur retiendra a tort et paiera au pari.
    fragiles = 0
    sep_min = total_bits
    for m in classes:
        if m == m_loi:
            continue
        d = _popcount(m ^ m_loi)
        sep_min = min(sep_min, d)
        if d <= 2:
            fragiles += 1
    rap.rivales_fragiles = fragiles
    rap.separation_min = sep_min
    if fragiles > RIVALES_FRAGILES_MAX:
        rap.rejeter(f"{fragiles} rivales quasi indistinguables")

    return rap


def _retenir(classes: dict[int, Loi], m: int, candidate: Loi) -> None:
    """Garde comme representant d'une classe la formulation la plus courte,
    puis la plus breve a lire."""
    actuel = classes.get(m)
    if actuel is None:
        classes[m] = candidate
        return
    cle_a = (len(actuel), len(str(actuel)))
    cle_c = (len(candidate), len(str(candidate)))
    if cle_c < cle_a:
        classes[m] = candidate


# --- CLI ------------------------------------------------------------------

def _main(argv: Sequence[str] | None = None) -> int:
    from .generator import generer

    p = argparse.ArgumentParser(
        prog="python -m lex.validator",
        description="Rapport de diagnostic sur une loi engendrée.",
    )
    p.add_argument("--seed", type=int, default=None)
    p.add_argument("--clauses", type=int, default=2)
    p.add_argument(
        "--balayage",
        type=int,
        default=0,
        metavar="N",
        help="tire N lois AU HASARD (sans filtrage) et affiche pourquoi elles "
             "sont rejetees : c'est l'outil de reglage des seuils",
    )
    args = p.parse_args(argv)

    if args.balayage:
        return _balayage(args)

    donne = generer(seed=args.seed, n_clauses=args.clauses)
    rap = donne.rapport
    print(f"graine        : {donne.seed}")
    print(f"dimensions    : {', '.join(donne.dims)}")
    print(f"loi           :")
    print(donne.loi.texte() if len(donne.loi) > 1 else f"  {donne.loi.texte()}")
    print()
    print(f"contextes     : {rap.n_contextes}")
    print(f"permissivité  : moy {rap.perm_moy:.0%}  min {rap.perm_min:.0%}  max {rap.perm_max:.0%}")
    print(f"classes       : {rap.classes} comportements distincts dans la grammaire")
    print(f"séparation min: {rap.separation_min} observations")
    print(f"rivales fragiles : {rap.rivales_fragiles}")
    print("témoins pivots :")
    for c, n in rap.temoins.items():
        print(f"  {n:4d} sur {rap.temoins_contextes[c]} contextes — {c.texte()}")
    print(f"verdict       : {'OK' if rap.ok else 'REJET'}")
    for m in rap.motifs:
        print(f"  - {m}")
    return 0


def _balayage(args) -> int:
    import collections
    from .cards import DIMS_DEFAUT, construire_pool

    rng = random.Random(args.seed)
    pool = construire_pool(random.Random(args.seed))
    cat = catalogue(DIMS_DEFAUT)
    compte: collections.Counter = collections.Counter()
    reussites = 0
    for _ in range(args.balayage):
        clauses = tuple(rng.sample(cat, args.clauses))
        rap = analyser(Loi(clauses), pool, DIMS_DEFAUT, rng, complet=True)
        if rap.ok:
            reussites += 1
            compte["ACCEPTEE"] += 1
        else:
            compte[rap.motifs[0].split("(")[0].split(":")[0].strip()] += 1
    print(f"{reussites}/{args.balayage} lois acceptées ({reussites / args.balayage:.0%})")
    for motif, n in compte.most_common():
        print(f"  {n:5d}  {motif}")
    return 0


if __name__ == "__main__":
    raise SystemExit(_main())
