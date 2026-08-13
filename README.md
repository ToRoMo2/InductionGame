# InductionGame

Prototype console du jeu d'induction **LEX**. Voir
`cahier-des-charges-jeu-induction (1).md` pour la spec complète.

Périmètre actuel : **§13 uniquement** — phase 0. Une manche isolée, terminal,
texte brut, stdlib seule. Pas de run, pas d'objets, pas de méta-progression,
pas d'escalade de difficulté.

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
| `cards.py` | cartes, registre d'attributs, saisie |
| `bricks.py` | les 3 familles de briques → catalogue de clauses |
| `law.py` | la loi (conjonction) et son évaluateur |
| `generator.py` | propose-and-test ; rend la loi **et** le pool validé avec elle |
| `validator.py` | permissivité, anti-impasse, anti-masquage, identifiabilité |
| `game.py` | la manche (phases A/B/C), logique pure |
| `cli.py` | terminal |

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
formulation que rien d'observable ne distingue de la vraie loi compte juste.

Le constructeur n'apparaît qu'en phase B, une fois l'enquête close — disponible
plus tôt, il permettrait l'élimination mécanique que le §6 interdit.

Le nombre de briques n'est jamais annoncé pendant la manche.

Les cartes refusées sont listées avec le **numéro d'essai** et la **position de
la ligne** au moment du refus. Un refus reste vrai pour toujours dans son
contexte, et le contexte change à chaque acceptation. Comme la ligne ne fait que
croître, la position reste valable et pointe sans ambiguïté vers la carte qui
précédait — ce qu'il faut pour vérifier une hypothèse relationnelle. Le jeu ne signale jamais qu'une
carte refusée passerait maintenant — ce serait une information sur le contexte
courant que le joueur n'a pas payée (§6).

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
