"""Boucle terminal. Texte brut, rien d'autre."""

from __future__ import annotations

import argparse
import random
import textwrap
from typing import Sequence

from .bricks import AVANCES, Clause
from .cards import ATTRIBUTS, CATEGORIELS, Carte, lire_description
from .game import ESSAIS, Partie, Phase, nouvelle_partie
from .law import Loi
from .probe import cout_jumelle, jumelle, tirer

LARGEUR = 68

# Mode etroit : pour jouer sur un ecran de telephone, ou en relais dans une
# conversation. Regle par --etroit.
ETROIT = False


def trait(c: str = "-") -> None:
    if c == "─":
        largeur = (sum(l for _, l, _ in _cols()) + 4 if ETROIT
                   else 2 * LARGEUR_COLS + 7)
    else:
        largeur = 34 if ETROIT else LARGEUR
    print(c * largeur)


# Colonnes resserrees : deux tableaux cote a cote doivent tenir dans 80.
COLONNES = (
    ("rang", 5, lambda c: c.nom_court[:-1]),
    ("parité", 7, lambda c: c.parite),
    ("ens", 4, lambda c: c.enseigne),
    ("couleur", 8, lambda c: c.couleur),
    ("dos", 7, lambda c: c.dos),
    ("pli", 6, lambda c: c.pli),
)
# Sur telephone, 80 colonnes se replient et detruisent l'alignement — qui est
# tout l'interet. En mode etroit on garde la meme idee (les refus decales pour
# que la colonne de gauche se lise d'une traite) mais sur une seule colonne,
# avec des largeurs resserrees : 30 caracteres au lieu de 80.
COLONNES_ETROITES = (
    ("rg", 3, lambda c: c.nom_court[:-1]),
    ("parité", 7, lambda c: c.parite),
    ("e", 2, lambda c: c.enseigne),
    ("coul", 6, lambda c: c.couleur),
    ("dos", 7, lambda c: c.dos),
    ("pli", 5, lambda c: c.pli),
)
LARGEUR_COLS = sum(l for _, l, _ in COLONNES)
SEP = " │ "


def _cols():
    return COLONNES_ETROITES if ETROIT else COLONNES


def _cellule(carte: Carte | None) -> str:
    cols = _cols()
    if carte is None:
        return " " * sum(l for _, l, _ in cols)
    return "".join(f"{f(carte):<{l}}" for _, l, f in cols)


def _entete_cols() -> str:
    return "".join(f"{nom:<{l}}" for nom, l, _ in _cols())


def afficher_ligne(p: Partie) -> None:
    """Deux colonnes : les acceptees a gauche, les refus a droite, dans l'ordre.

    Lire la colonne de gauche de haut en bas donne la suite valide sans qu'un
    refus vienne s'y melanger — c'est la lisibilite « ligne principale / lignes
    d'erreur » qu'Eleusis nous apprend (§12) et qu'on avait perdue.

    L'interet n'est pas que cosmetique : place chronologiquement en regard de
    la ligne, un refus montre de lui-meme APRES QUELLE CARTE il a eu lieu. Les
    annotations « (sonde 5, apres 1.) » qu'il fallait ajouter avant deviennent
    inutiles — la mise en page dit la meme chose sans un mot.
    """
    print()
    if ETROIT:
        print("LIGNE  (les refus sont décalés)")
        print(f"    {_entete_cols()}")
    else:
        gauche = f"{'LIGNE PRINCIPALE':<{LARGEUR_COLS + 4}}"
        print(f"{gauche}{SEP}REFUSÉES")
        print(f"    {_entete_cols()}{SEP}{_entete_cols()}")
    trait("─")

    def rangee(pos: int | None, carte: Carte, accepte: bool, suffixe: str = "") -> None:
        if ETROIT:
            print(f"{pos:>2}. {_cellule(carte)}" if accepte
                  else f"  x    {_cellule(carte)}")
        elif accepte:
            print(f"{pos:>2}. {_cellule(carte)}{SEP}")
        else:
            print(f"    {_cellule(None)}{SEP}{_cellule(carte)}{suffixe}")

    rangee(0, p.ligne[0], True)
    pos = 1
    for accepte, carte in p.journal:
        rangee(pos if accepte else None, carte, accepte)
        if accepte:
            pos += 1
    print()


def afficher_aide(dims: Sequence[str]) -> None:
    print()
    print("Une loi secrète décide si une carte peut suivre la ligne.")
    print("Tu ne choisis pas une carte : tu DÉCRIS l'expérience que tu veux,")
    print("et tu paies ta précision.")
    print()
    print("Dimensions en jeu (la loi ne porte que sur celles-ci) :")
    for d in dims:
        vals = " · ".join(str(v) for v in ATTRIBUTS[d].domaine)
        if d == "rang":
            vals = "1 à 13  (as valet dame roi)"
        print(f"  {ATTRIBUTS[d].libelle:20} {vals}")
    print()
    print("SONDES")
    print("  <valeurs>            une carte au hasard parmi celles qui collent")
    print("                       ex.  jaune plié   ·   9 coeur   ·   rouge")
    print("  jumelle <pos> <dim>  identique à la carte en position <pos>,")
    print("                       sauf sur <dim>.  ex.  jumelle 2 dos")
    print("  hasard               n'importe quelle carte")
    print()
    print("PRIX  1 essai, +1 par attribut que tu imposes.")
    print(f"      hasard = 1   ·   « jaune plié » = 3   ·   jumelle = {cout_jumelle()}")
    print()
    print("Commandes :  ligne | aide | pari | abandon")
    print()


def puce(texte: str, marge: str = "  · ") -> None:
    """Un texte de clause, replie proprement. Certaines montent a 96 caracteres
    (« le rang avance de 1 a 8 rangs... ») : sur telephone elles se replient
    n'importe ou, et c'est au moment de la revelation que la lisibilite compte
    le plus."""
    largeur = 38 if ETROIT else LARGEUR
    suite = " " * len(marge)
    for i, bout in enumerate(textwrap.wrap(texte, largeur - len(marge)) or [""]):
        print((marge if i == 0 else suite) + bout)


def demander(invite: str) -> str:
    try:
        return input(invite).strip()
    except (EOFError, KeyboardInterrupt):
        print()
        return "abandon"


# --- phase A --------------------------------------------------------------

def phase_enquete(p: Partie) -> bool:
    """Renvoie False si le joueur abandonne."""
    rng = random.Random(p.donne.seed ^ 0x50DE)
    trait("=")
    print("PHASE A — ENQUÊTE")
    trait("=")
    afficher_aide(p.donne.dims)
    afficher_ligne(p)

    while p.phase is Phase.ENQUETE:
        if p.essais_restants <= 0:
            print("Plus d'essais. Passage au pari.")
            return True
        saisie = demander(f"[{p.essais_restants} essais] > ").strip()
        bas = saisie.lower()
        if not bas:
            continue
        if bas in ("abandon", "quitter", "q"):
            return False
        if bas in ("pari", "declarer"):
            return True
        if bas in ("aide", "?", "h"):
            afficher_aide(p.donne.dims)
            continue
        if bas == "ligne":
            afficher_ligne(p)
            continue

        sonde = _lire_sonde(bas, p, rng)
        if sonde is None:
            continue
        if sonde.cout > p.essais_restants:
            print(f"  ? cette sonde coûte {sonde.cout}, il te reste "
                  f"{p.essais_restants}. Sois moins précis.")
            continue

        accepte = p.jouer(sonde)
        print(f"\n  {'ACCEPTÉE' if accepte else 'REFUSÉE'}   (-{sonde.cout})")
        afficher_ligne(p)
    return True


def _lire_sonde(saisie: str, p: Partie, rng: random.Random):
    """Traduit la saisie en sonde. Renvoie None si elle est incomprehensible."""
    mots = saisie.split()

    if mots[0] in ("jumelle", "j"):
        if len(mots) != 3 or not mots[1].isdigit():
            print("  ? forme attendue : jumelle <position> <dimension>")
            return None
        pos, dim = int(mots[1]), mots[2]
        if pos >= len(p.ligne):
            print(f"  ? la ligne s'arrête à la position {len(p.ligne) - 1}.")
            return None
        cible = next((d for d in p.donne.dims if d.startswith(dim[:3])), None)
        if cible is None:
            print(f"  ? dimension inconnue. « aide » pour la liste.")
            return None
        s = jumelle(p.donne.pool, p.ligne[pos], cible, rng)
        if s is None:
            print("  ? aucune jumelle disponible sur cette dimension.")
        return s

    if saisie in ("hasard", "au hasard"):
        return tirer(p.donne.pool, {}, rng)

    contraintes = lire_description(saisie)
    if contraintes is None:
        print("  ? description incomprise. « aide » pour le vocabulaire.")
        return None
    inconnues = [a for a in contraintes if a not in p.donne.dims]
    if inconnues:
        print(f"  ? dimension hors jeu : {', '.join(inconnues)}")
        return None
    s = tirer(p.donne.pool, contraintes, rng)
    if s is None:
        print("  ? aucune carte du paquet ne correspond.")
    return s


# --- phase B --------------------------------------------------------------

def phase_pari(p: Partie) -> bool:
    main = p.passer_au_pari()
    print()
    trait("=")
    print("PHASE B — LE PARI")
    trait("=")
    print()
    print("Construis la suite la plus longue que tu oses.")
    print("Elle PROLONGE la carte de départ, qui compte comme carte")
    print("précédente de ta première carte. Le reste de la ligne ne compte pas.")
    print()
    print(f"    {_entete_cols()}")
    print(f"dép.{_cellule(p.donne.demarrage)}")
    print(f"Valide : +longueur².   Fausse d'une seule carte : -longueur².")
    print()
    print(f"MULTIPLICATEUR ×{p.multiplicateur():.2f}"
          f"  ({p.essais_restants} essais économisés sur {p.essais})")
    print("Il s'applique au total, gains comme pertes.")
    print()
    print(f"MAIN ({len(main)} cartes, tirées du paquet) :")
    print(f"    {_entete_cols()}")
    for i, c in enumerate(main, 1):
        print(f"{i:2}. {_cellule(c)}")
    print()
    print("Ajoute les cartes par leur NUMÉRO — le paquet contient plusieurs")
    print("cartes de même rang et enseigne, seuls le dos et le pli changent.")
    print("« retirer » annule la dernière, « valider » résout, « main » réaffiche.")
    print()

    suite: list[Carte] = []
    restantes = list(main)
    while True:
        # Le depart est rappele en tete : c'est lui qui juge la premiere carte.
        apercu = " → ".join(
            [f"({p.donne.demarrage.nom_court})"] + [c.nom_court for c in suite]
        )
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
            print(f"    {_entete_cols()}")
            for i, c in enumerate(main, 1):
                etat = "posée" if c in suite else ""
                print(f"{i:2}. {_cellule(c)}{etat}")
            continue
        if saisie in ("valider", "ok"):
            if not suite:
                print("  ? une suite vide ne rapporte rien. Ajoute au moins une carte.")
                continue
            p.resoudre(suite, declarer_loi(p.donne.dims))
            return True

        if not saisie.isdigit() or not 1 <= int(saisie) <= len(main):
            print(f"  ? donne un numéro entre 1 et {len(main)}.")
            continue
        carte = main[int(saisie) - 1]
        if carte not in restantes:
            print("  ? carte déjà posée dans la suite.")
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
        ("absolue", "absolue        — porte sur la carte posée, seule"),
        ("relation", "relation       — compare à la carte précédente"),
        ("sequence", "séquence       — interdit une répétition sur la ligne"),
        ("conditionnelle", "conditionnelle — si la précédente est…, alors…"),
    ])
    if famille is None:
        return None

    if famille == "conditionnelle":
        a_si = _choisir("SI la précédente a…", cats)
        if a_si is None:
            return None
        v_si = _choisir(
            "…la valeur", [(str(v), str(v)) for v in ATTRIBUTS[a_si].domaine]
        )
        if v_si is None:
            return None
        a_alors = _choisir("ALORS la carte posée a…", cats)
        if a_alors is None:
            return None
        v_alors = _choisir(
            "…la valeur", [(str(v), str(v)) for v in ATTRIBUTS[a_alors].domaine]
        )
        if v_alors is None:
            return None
        return Clause("conditionnelle", (a_si, v_si, a_alors, v_alors))

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
    # Les options sont la phrase finale, pas un compte abstrait. « combien
    # d'affilee au maximum ? » avec « une seule / deux » a fait choisir 2 a un
    # joueur qui voulait « jamais deux d'affilee » : il pensait au nombre
    # INTERDIT, le menu demandait le nombre AUTORISE. Loi juste, declaration
    # fausse, 72 points perdus sur une tournure.
    maxi = _choisir("laquelle ?", [
        ("1", f"jamais deux « {valeur} » d'affilée"),
        ("2", f"jamais plus de deux « {valeur} » d'affilée"),
    ])
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
        puce(c.texte(), "    → ")
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
        puce(c.texte(), "    · ")
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
            puce(c.texte(), "    · ")
        if r.loi_juste:
            print(f"  LOI JUSTE — rien ne pouvait la distinguer.  {r.points_loi:+d}")
        else:
            print(f"  LOI FAUSSE.                                 {r.points_loi:+d}")
    else:
        print()
        print("  (loi non déclarée)")
    print()
    print(f"  base {r.base:+d}   ×{r.multiplicateur:.2f}"
          f"   ({r.essais_restants} essais économisés)")
    print(f"  TOTAL   {r.points:+d} points")
    print()
    trait()
    print("LA LOI ÉTAIT :")
    for c in p.donne.loi.clauses:
        puce(c.texte())
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
            puce(c.texte())
        print()
        return 0
    if not phase_pari(p):
        print("\nAbandon. La loi était :")
        for c in p.donne.loi.clauses:
            puce(c.texte())
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
