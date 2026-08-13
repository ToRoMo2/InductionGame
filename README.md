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

Limites détaillées en tête de `lex/validator.py`.
