"""Boucle terminal. Texte brut, rien d'autre."""

from __future__ import annotations

import argparse
import random
from typing import Sequence

from .bricks import AVANCES, Clause
from .cards import (ATTRIBUTS, CATEGORIELS, ENSEIGNES, NOM_RANG, RANGS, Carte,
                    parser_carte)
from .game import ESSAIS, Partie, Phase, nouvelle_partie
from .law import Loi

LARGEUR = 68

# Mode etroit : pour jouer sur un ecran de telephone, ou en relais dans une
# conversation. Regle par --etroit.
ETROIT = False


def trait(c: str = "-") -> None:
    print(c * (34 if ETROIT else LARGEUR))


def afficher_pool(pool: Sequence[Carte]) -> None:
    """Grille rang x enseigne. Tout est visible : en phase 0 il n'y a pas de
    geste de manipulation, donc les attributs caches sont ecrits en clair."""
    print()
    index = {(c.rang, c.enseigne): c for c in pool}
    if ETROIT:
        print("    (dos iv=ivoire ja=jaune · pli L=lisse P=plié)")
        print()
        print("     " + "".join(f"{e:<6}" for e in ENSEIGNES))
        for r in RANGS:
            cellules = [
                f"{index[(r, e)].dos[:2]}·{index[(r, e)].pli[0].upper():<3}"
                for e in ENSEIGNES
            ]
            print(f" {NOM_RANG.get(r, str(r)):<4}" + "".join(cellules))
        print()
        return
    print("    " + "".join(f"{e:<16}" for e in ENSEIGNES))
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
        print("REFUSÉES  (le refus vaut pour le contexte de ce tour-là)")
        for essai, c in p.refusees:
            print(f"  x  {c}   (essai {essai})")
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
            p.resoudre(suite, declarer_loi(p.donne.dims))
            return True

        carte = parser_carte(saisie, restantes)
        if carte is None:
            print("  ? carte absente de la main (ou syntaxe invalide).")
            continue
        restantes.remove(carte)
        suite.append(carte)
    return True


# --- declaration de la loi ------------------------------------------------

def _choisir(invite: str, options: Sequence[tuple[str, str]]) -> str | None:
    """Petit menu numerote. Renvoie None si le joueur renonce."""
    for i, (_, libelle) in enumerate(options, 1):
        print(f"    {i}. {libelle}")
    while True:
        s = demander(f"  {invite} > ").lower()
        if s in ("", "annuler", "retour", "abandon"):
            return None
        if s.isdigit() and 1 <= int(s) <= len(options):
            return options[int(s) - 1][0]
        for cle, libelle in options:
            if s == cle.lower() or s == libelle.lower():
                return cle
        print("  ? choix hors menu.")


def _choisir_multi(invite: str, options: Sequence[tuple[str, str]]) -> list[str] | None:
    for i, (_, libelle) in enumerate(options, 1):
        print(f"    {i}. {libelle}")
    while True:
        s = demander(f"  {invite} (numéros séparés par des virgules) > ").lower()
        if s in ("", "annuler", "retour", "abandon"):
            return None
        jetons = [j.strip() for j in s.replace(" ", ",").split(",") if j.strip()]
        if jetons and all(j.isdigit() and 1 <= int(j) <= len(options) for j in jetons):
            return [options[int(j) - 1][0] for j in jetons]
        print("  ? choix hors menu.")


def construire_clause(dims: Sequence[str]) -> Clause | None:
    """Construit UNE clause par menus successifs.

    On donne au joueur la grammaire (les formes de regles), jamais la liste des
    lois candidates : le §6 veut que le mystere porte sur quelle loi, pas sur
    la forme du probleme. Et ce constructeur n'apparait qu'en phase B, une fois
    l'enquete close — sinon il permettrait l'elimination mecanique que le §6
    interdit explicitement.
    """
    cats = [(d, ATTRIBUTS[d].libelle) for d in CATEGORIELS if d in dims]

    famille = _choisir("famille", [
        ("absolue", "absolue    — porte sur la carte posée, seule"),
        ("relation", "relation   — compare à la carte précédente"),
        ("sequence", "séquence   — interdit une répétition sur la ligne"),
    ])
    if famille is None:
        return None

    if famille == "absolue":
        nom = _choisir("attribut", cats)
        if nom is None:
            return None
        dom = ATTRIBUTS[nom].domaine
        interdites = _choisir_multi(
            "quelles valeurs sont INTERDITES ?", [(v, str(v)) for v in dom]
        )
        if not interdites:
            return None
        autorisees = tuple(v for v in dom if v not in interdites)
        if not autorisees:
            print("  ? tout interdire ne laisse aucune carte jouable.")
            return None
        return Clause("absolue", (nom, autorisees))

    if famille == "relation":
        opts = list(cats) + ([("rang", "le rang")] if "rang" in dims else [])
        nom = _choisir("attribut", opts)
        if nom is None:
            return None
        if nom == "rang":
            mode = _choisir("relation", [
                ("different", "le rang diffère du précédent"),
                ("avance", "le rang avance de 1 à k rangs (l'as suit le roi)"),
            ])
            if mode is None:
                return None
            if mode == "avance":
                k = _choisir("k", [(str(v), f"de 1 à {v} rangs") for v in AVANCES])
                if k is None:
                    return None
                return Clause("relation", ("rang", "avance", int(k)))
            return Clause("relation", ("rang", "different", None))
        mode = _choisir("relation", [
            ("egal", f"{ATTRIBUTS[nom].libelle} est identique au précédent"),
            ("different", f"{ATTRIBUTS[nom].libelle} diffère du précédent"),
        ])
        if mode is None:
            return None
        return Clause("relation", (nom, mode, None))

    nom = _choisir("attribut", cats)
    if nom is None:
        return None
    valeur = _choisir(
        "quelle valeur ne doit pas se répéter ?",
        [(str(v), str(v)) for v in ATTRIBUTS[nom].domaine],
    )
    if valeur is None:
        return None
    maxi = _choisir("combien d'affilée au maximum ?", [("1", "une seule"), ("2", "deux")])
    if maxi is None:
        return None
    return Clause("sequence", (nom, valeur, int(maxi)))


def declarer_loi(dims: Sequence[str]) -> Loi | None:
    print()
    print("DÉCLARATION DE LA LOI  (facultative)")
    print("C'est un second pari, de même mise que la suite : juste, tu doubles ;")
    print("faux, tu perds autant. Refuser ne coûte rien.")
    print()
    if demander("  Déclarer la loi ? (o/n) > ").lower() not in ("o", "oui", "y", "yes"):
        return None

    clauses: list[Clause] = []
    while len(clauses) < 3:
        print()
        print(f"  — clause {len(clauses) + 1} —")
        c = construire_clause(dims)
        if c is None:
            if clauses:
                break
            print("  déclaration abandonnée.")
            return None
        clauses.append(c)
        print(f"    → {c.texte()}")
        if demander("  Ajouter une autre clause ? (o/n) > ").lower() not in (
            "o", "oui", "y", "yes"
        ):
            break
    if not clauses:
        return None
    loi = Loi(tuple(clauses))
    print()
    print("  Tu déclares :")
    for c in loi.clauses:
        print(f"    · {c.texte()}")
    return loi


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
        print(f"  SUITE VALIDE — {r.longueur} cartes.        {r.points_suite:+d}")
    else:
        print(f"  SUITE INVALIDE — casse en position {r.index_faute}.  {r.points_suite:+d}")
        print("  Ta propre ambition te revient dessus.")
    if r.loi_declaree is not None:
        print()
        print("  Tu avais déclaré :")
        for c in r.loi_declaree.clauses:
            print(f"    · {c.texte()}")
        if r.loi_juste:
            print(f"  LOI JUSTE — rien ne pouvait la distinguer.  {r.points_loi:+d}")
        else:
            print(f"  LOI FAUSSE.                                 {r.points_loi:+d}")
    else:
        print()
        print("  (loi non déclarée)")
    print()
    print(f"  TOTAL   {r.points:+d} points")
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
    p.add_argument(
        "--etroit",
        action="store_true",
        help="affichage compact, pour un ecran de telephone",
    )
    args = p.parse_args(argv)
    global ETROIT
    ETROIT = args.etroit
    return jouer(seed=args.seed, n_clauses=args.clauses, essais=args.essais)
