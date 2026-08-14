# InductionGame

Prototype console du jeu d'induction **LEX**. Voir
`cahier-des-charges-jeu-induction.md` pour la spec complète.

Périmètre actuel : phase 0 livrée (§13), **étape 2 en cours** (§14) — la
grammaire s'élargit. Une manche isolée, terminal, texte brut, stdlib seule.
Pas de run, pas d'objets, pas de méta-progression, pas d'escalade.

## La grammaire

Quatre familles de briques, une loi en combine deux :

| famille | exemple |
|---|---|
| absolue | le dos n'est jamais « ivoire » |
| relationnelle | la couleur diffère de celle de la carte précédente |
| séquentielle | jamais deux « pair » d'affilée |
| conditionnelle | si la précédente a l'enseigne « ♣ », alors le pli est « lisse » |

**L'élargissement se fait par famille, jamais par attribut**, et c'est mesuré :
le joueur n'apprend pas les lois, il apprend les **formes**. Un attribut de plus
n'ajoute que 4 formes ; une famille multiplie. L'ajout de la conditionnelle a
fait passer la grammaire de 22 à 47 formes, et le plancher du solveur parfait
de 18 à 19 essais seulement — plus de variété sans plus de difficulté.

Le tirage est **équiprobable par famille**, pas par clause : la conditionnelle
représente 70 % du catalogue à elle seule, et un tirage uniforme sur les clauses
l'aurait laissée étouffer les trois autres.

## Jouer

```
python3 -m lex                    # une manche, loi à 2 briques
python3 -m lex --seed 44          # rejouer exactement la même manche
python3 -m lex --clauses 1        # loi à 1 brique
python3 -m lex --essais 30        # budget d'essais (fixe)
```

## Régler le générateur sans jouer

Le générateur et le validateur sont appelables indépendamment de la boucle.

```
python3 -m lex.generator --seed 42 --n 10     # 10 lois valides + leurs stats
python3 -m lex.validator --seed 44            # rapport détaillé sur une loi
python3 -m lex.validator --balayage 300       # pourquoi les lois sont rejetées
```

`--balayage` tire des lois **sans filtrage** et affiche la répartition des
motifs de rejet : c'est l'outil pour bouger les seuils de `lex/validator.py`.

## Modules

| Fichier | Rôle |
|---|---|
| `cards.py` | cartes, registre d'attributs, lecture des descriptions |
| `probe.py` | la sonde : description, jumelle, tarif |
| `bricks.py` | les 4 familles de briques → catalogue de clauses |
| `law.py` | la loi (conjonction) et son évaluateur |
| `generator.py` | propose-and-test ; rend la loi **et** le pool validé avec elle |
| `validator.py` | permissivité, anti-impasse, anti-masquage, identifiabilité |
| `game.py` | la manche (phases A/B/C), logique pure |
| `cli.py` | terminal |

## La sonde — le cœur du jeu

Le joueur ne choisit pas une carte, il **décrit l'expérience** qu'il veut mener
et paie sa précision.

```
> jaune plié            une carte au dos jaune et pliée, le reste au hasard   (3)
> jumelle 2 dos         identique à la carte en position 2, sauf le dos       (3)
> hasard                n'importe quelle carte                                (1)
```

Prix : 1 essai, +1 par attribut imposé. Budget 30.

**La jumelle est la raison d'être du dispositif.** C'est l'observation la plus
informative du jeu — le validateur l'appelle « témoin pivot » et compte ces
cas-là pour garantir qu'une loi est déductible — et le joueur n'avait aucun
moyen de la demander. Elle est vendue moins cher que sa précision ne le
justifie : un solveur glouton qui optimise l'information par essai ne la prend
jamais à plein tarif, parce que les sondes larges sont plus rentables par essai
dépensé. Mais ce solveur met à jour 1711 hypothèses bayésiennement ; un humain
non. La valeur d'une jumelle est **cognitive** — elle donne un fait directement
lisible — et à plein tarif le choix pelle-ou-scalpel n'existerait pas.

Le paquet est le **produit cartésien complet** : 13 × 4 × 2 × 2 = 208 cartes.
Ce n'est pas un paquet de 52 augmenté, c'est un changement de nature. Dans un
paquet classique, dos et pli sont des *fonctions* de (rang, enseigne) : il
n'existe qu'un seul 9♥, avec son dos et son pli figés, donc il est impossible
de faire varier une seule dimension. Sans produit complet, pas d'expérience
contrôlée — et sans expérience contrôlée, l'induction n'est qu'une collection
de coïncidences. Le paquet n'étant jamais affiché en entier, sa taille ne coûte
rien.

Étalonnage mesuré : un solveur parfait dépense une médiane de 18 essais sur 30.

## Le pari

Deux paris indépendants, de même mise `longueur²` :

1. **la suite** — elle **prolonge la carte de départ**, qui juge sa première
   carte ; valide, tu encaisses ; une seule carte fausse, la valeur se retourne
   contre toi. Évaluée sur une ligne neuve, la première carte n'aurait aucune
   carte précédente : sur les 17 % de lois sans clause absolue, n'importe
   quelle carte serait passée et un joueur n'ayant rien compris aurait encaissé
   des points garantis ;
2. **la loi** — facultatif. Tu la construis par menus (famille → attribut →
   paramètres), pas dans une liste de lois candidates. Juste, tu doubles ;
   faux, tu perds autant ; refuser ne coûte rien.

Le total est **multiplié** par `1 + essais_restants / budget` (plafond ×2),
gains comme pertes. Les essais économisés ne s'ajoutent jamais au score :
l'addition ferait *coûter* des points à l'enquête et permettrait d'empocher le
budget en déclarant n'importe quoi au premier tour. Un multiplicateur sur zéro
fait zéro. Appliqué aussi aux pertes, il fait de la vitesse un multiplicateur de
risque plutôt qu'un bonus — le §9 sans la boule de neige du §4.

La déclaration est jugée sur le **comportement**, jamais sur les mots : une
formulation que rien d'observable ne distingue de la vraie loi compte juste,
**y compris dans une autre famille**. « le dos diffère du précédent » est
reconnu identique à « jamais deux ivoire d'affilée ET jamais deux jaune
d'affilée ». C'est nécessaire : 190 clauses du catalogue ne produisent que
156 comportements distincts, et 54 clauses ont un jumeau exact.

Quand la déclaration est fausse, le jeu **montre où**. Il cherche un cas où les
deux lois divergent, en privilégiant celui dont la carte est la plus proche
d'une jumelle de la précédente : un contre-exemple qui change quatre attributs
ne prouve rien de lisible, un qui n'en change qu'un désigne la dimension du
malentendu. Sans ça, le joueur repart convaincu que sa loi disait la même
chose — et le §4C, qui promet qu'il apprend toujours quelque chose, n'est tenu
qu'à moitié.

La loi révélée est réécrite dans sa **formulation la plus courte** à
comportement égal.

Le constructeur n'apparaît qu'en phase B, une fois l'enquête close — disponible
plus tôt, il permettrait l'élimination mécanique que le §6 interdit.

Le nombre de briques n'est jamais annoncé pendant la manche.

La **carte de départ satisfait toujours la loi**. Sur une ligne vide seules les
clauses absolues mordent, donc la contrainte est légère — mais sans elle, la
position 0 de la ligne peut contredire la loi et le joueur rejette une
hypothèse correcte à cause de la carte qu'on lui a donnée (§3 pilier 3).

Le jeu ne signale jamais qu'une carte refusée passerait maintenant — ce serait
une information sur le contexte courant que le joueur n'a pas payée (§6).

## L'affichage

Deux colonnes : les acceptées à gauche, les refus à droite, **dans l'ordre
chronologique**.

```
LIGNE PRINCIPALE                          │ REFUSÉES
    rang parité ens couleur dos    pli    │ rang parité ens couleur dos    pli
──────────────────────────────────────────────────────────────────────────────
 0. V    impair ♣   noir    ivoire lisse  │
                                          │ 3    impair ♥   rouge   ivoire plié
 1. V    impair ♦   rouge   jaune  lisse  │
```

Lire la colonne de gauche de haut en bas donne la suite valide sans qu'un refus
s'y mélange — c'est la lisibilité « ligne principale / lignes d'erreur »
qu'Eleusis nous apprend (§12).

Ce n'est pas que cosmétique. Placé chronologiquement en regard de la ligne, un
refus montre **de lui-même** après quelle carte il a eu lieu : les annotations
« (sonde 5, après 1.) » qu'il fallait ajouter avant deviennent inutiles.

Les attributs dérivés (couleur, parité) ont leur colonne. Ils sont triviaux à
calculer mais coûteux à calculer *vite*, et les afficher ne révèle rien — ils
sont déjà annoncés comme dimensions.

## La testabilité (§5.2)

Le cahier des charges formule la contrainte en fréquence. Le vrai danger est le
**masquage** : dans une conjonction, un refus ne dit que « au moins une clause
a échoué », donc une clause très restrictive rend les autres invisibles quelle
que soit leur fréquence.

Le validateur encode le comportement de chaque clause sur
`contextes × pool` dans un masque de bits (un `int` Python), ce qui rend
l'énumération exacte des ~1700 lois de la grammaire quasi gratuite. Il vérifie
alors que chaque clause dispose d'assez de **témoins pivots** — des refus dont
elle est la seule responsable.

Tous les contextes partent de la **carte de départ réelle**. Une même loi peut
être déductible depuis un départ et partiellement inobservable depuis un autre :
« même couleur que la précédente » verrouille la ligne sur la couleur du départ,
ce qui peut rendre une seconde clause invisible pour toute la manche. La carte
de départ fait donc partie de ce que le générateur valide.

Limites détaillées en tête de `lex/validator.py`.
