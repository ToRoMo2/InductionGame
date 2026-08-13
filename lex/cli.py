"""Boucle terminal. Texte brut, rien d'autre."""

from __future__ import annotations

import argparse
import random
from typing import Sequence

from .cards import ATTRIBUTS, ENSEIGNES, NOM_RANG, RANGS, Carte, parser_carte
from .game import ESSAIS, MAIN_PARI, Partie, Phase, nouvelle_partie

LARGEUR = 68


def trait(c: str = "-") -> None:
    print(c * LARGEUR)


def afficher_pool(pool: Sequence[Carte]) -> None:
    """Grille rang x enseigne. Tout est visible : en phase 0 il n'y a pas de
    geste de manipulation, donc les attributs caches sont ecrits en clair."""
    print()
    print("    " + "".join(f"{e:<16}" for e in ENSEIGNES))
    index = {(c.rang, c.enseigne): c for c in pool}
    for r in RANGS:
        cellules = []
        for e in ENSEIGNES:
            c = index[(r, e)]
            cellules.append(f"{c.dos[:6]:<7}{c.pli:<9}")
        print(f" {NOM_RANG.get(r, str(r)):<3}" + "".join(cellules))
    print()


def afficher_ligne(p: Partie) -> None:
    print()
    print("LIGNE PRINCIPALE")
    for i, c in enumerate(p.ligne):
        marque = "(départ)" if i == 0 else ""
        print(f"  {i}. {c} {marque}")
    if p.refusees:
        print()
        print("REFUSÉES  (elles restent disponibles, à toi de les retenir)")
        for c in p.refusees:
            print(f"  x  {c}")
    print()


def afficher_aide(dims: Sequence[str]) -> None:
    print()
    print("Une loi secrète décide si une carte peut suivre la ligne.")
    print("Pose des cartes, observe, déduis. Puis parie.")
    print()
    print("Dimensions en jeu (la loi ne porte que sur celles-ci) :")
    for d in dims:
        print(f"  · {ATTRIBUTS[d].libelle}")
    print()
    print("Saisie d'une carte : rang + enseigne.  7p  ·  as coeur  ·  10 t  ·  R♥")
    print("  rangs     A 2..10 V D R          (ou 1..13)")
    print("  enseignes p=pique  c=cœur  k=carreau  t=trèfle")
    print()
    print("Commandes :  pool | ligne | aide | pari | abandon")
    print()


def demander(invite: str) -> str:
    try:
        return input(invite).strip()
    except (EOFError, KeyboardInterrupt):
        print()
        return "abandon"


# --- phase A --------------------------------------------------------------

def phase_enquete(p: Partie) -> bool:
    """Renvoie False si le joueur abandonne."""
    trait("=")
    print("PHASE A — ENQUÊTE")
    trait("=")
    afficher_aide(p.donne.dims)
    afficher_pool(p.donne.pool)
    afficher_ligne(p)

    while p.phase is Phase.ENQUETE:
        if p.essais_restants <= 0:
            print("Plus d'essais. Passage au pari.")
            return True
        saisie = demander(f"[{p.essais_restants} essais] > ").lower()
        if not saisie:
            continue
        if saisie in ("abandon", "quitter", "q"):
            return False
        if saisie in ("pari", "p!", "declarer"):
            return True
        if saisie in ("aide", "?", "h"):
            afficher_aide(p.donne.dims)
            continue
        if saisie == "pool":
            afficher_pool(p.donne.pool)
            continue
        if saisie == "ligne":
            afficher_ligne(p)
            continue

        carte = parser_carte(saisie, p.donne.pool)
        if carte is None:
            print("  ? carte non reconnue. « aide » pour la syntaxe.")
            continue

        accepte = p.jouer(carte)
        if accepte:
            print(f"  ACCEPTÉE   {carte}   → position {len(p.ligne) - 1}")
        else:
            print(f"  REFUSÉE    {carte}")
    return True


# --- phase B --------------------------------------------------------------

def phase_pari(p: Partie) -> bool:
    main = p.passer_au_pari()
    print()
    trait("=")
    print("PHASE B — LE PARI")
    trait("=")
    print()
    print("Construis la suite la plus longue que tu oses.")
    print("Elle est évaluée SEULE, comme une ligne neuve — elle ne prolonge")
    print("pas la ligne principale.")
    print(f"Valide : +longueur².   Fausse d'une seule carte : -longueur².")
    print()
    print(f"MAIN ({len(main)} cartes, tirées du paquet) :")
    for c in main:
        print(f"  · {c}")
    print()
    print("Ajoute les cartes une par une. « retirer » annule la dernière,")
    print("« valider » résout, « ligne » rappelle l'enquête.")
    print()

    suite: list[Carte] = []
    restantes = list(main)
    while True:
        apercu = " → ".join(c.nom_court for c in suite) or "(vide)"
        saisie = demander(f"[suite: {apercu}] > ").lower()
        if not saisie:
            continue
        if saisie in ("abandon", "quitter", "q"):
            return False
        if saisie == "ligne":
            afficher_ligne(p)
            continue
        if saisie in ("retirer", "annuler"):
            if suite:
                restantes.append(suite.pop())
            continue
        if saisie in ("main", "pool"):
            for c in sorted(restantes):
                print(f"  · {c}")
            continue
        if saisie in ("valider", "ok"):
            if not suite:
                print("  ? une suite vide ne rapporte rien. Ajoute au moins une carte.")
                continue
            p.resoudre(suite)
            return True

        carte = parser_carte(saisie, restantes)
        if carte is None:
            print("  ? carte absente de la main (ou syntaxe invalide).")
            continue
        restantes.remove(carte)
        suite.append(carte)
    return True


# --- phase C --------------------------------------------------------------

def phase_resolution(p: Partie) -> None:
    r = p.resolution
    assert r is not None
    print()
    trait("=")
    print("PHASE C — RÉSOLUTION")
    trait("=")
    print()
    if r.valide:
        print(f"  SUITE VALIDE — {r.longueur} cartes.   {r.points:+d} points")
    else:
        print(f"  SUITE INVALIDE — elle casse en position {r.index_faute}.")
        print(f"  Ta propre ambition te revient dessus.   {r.points:+d} points")
    print()
    trait()
    print("LA LOI ÉTAIT :")
    for c in p.donne.loi.clauses:
        print(f"  · {c.texte()}")
    trait()
    print()
    rap = p.donne.rapport
    print(
        f"(diagnostic — permissivité {rap.perm_moy:.0%}, "
        f"{rap.classes} lois distinctes possibles dans la grammaire, "
        f"graine {p.donne.seed})"
    )
    print()


# --- entree ---------------------------------------------------------------

def jouer(seed: int | None = None, n_clauses: int = 2, essais: int = ESSAIS) -> int:
    print()
    trait("=")
    print("LEX — prototype console")
    trait("=")
    print("Génération d'une loi déductible…", flush=True)
    p = nouvelle_partie(seed=seed, n_clauses=n_clauses, essais=essais)
    print("prête.")

    if not phase_enquete(p):
        print("\nAbandon. La loi était :")
        for c in p.donne.loi.clauses:
            print(f"  · {c.texte()}")
        print()
        return 0
    if not phase_pari(p):
        print("\nAbandon. La loi était :")
        for c in p.donne.loi.clauses:
            print(f"  · {c.texte()}")
        print()
        return 0
    phase_resolution(p)
    return 0


def main(argv: Sequence[str] | None = None) -> int:
    p = argparse.ArgumentParser(prog="python -m lex", description="LEX, phase 0.")
    p.add_argument("--seed", type=int, default=None, help="rejouer la même manche")
    p.add_argument("--clauses", type=int, default=2, help="nombre de briques (1 ou 2)")
    p.add_argument("--essais", type=int, default=ESSAIS, help="budget d'essais (fixe)")
    args = p.parse_args(argv)
    return jouer(seed=args.seed, n_clauses=args.clauses, essais=args.essais)
