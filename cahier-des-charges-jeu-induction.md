# Cahier des charges — Jeu d'induction (nom de code : **LEX**)

> Document interne. Non destiné à la publication ni à la communication externe.
> Version 0.2 — mis à jour après le prototype console jouable.
>
> **Ce qui a changé depuis la 0.1.** La v0.1 était spéculative ; la v0.2 décrit
> un jeu qui existe et qui a été joué. Tout ce qui a été tranché en jouant est
> signalé par un bloc **« Tranché en jouant »** avec la raison. Quand une
> décision contredit la v0.1, la v0.1 avait tort et on dit pourquoi — le
> document sert à penser, pas à avoir eu raison.
>
> Le changement le plus lourd : **le joueur ne pose plus une carte, il décrit
> une expérience** (§4). C'est une refonte du verbe central, décidée après avoir
> mesuré qu'une manche ne contenait qu'une dizaine de décisions toutes
> identiques.

---

## 1. Vision en une phrase

**Un roguelike de cartes où le joueur ignore la règle du jeu, la déduit en jouant, puis parie sa compréhension pour marquer des points.**

Formulation longue : chaque manche, le système génère une loi secrète. Le joueur pose des cartes, observe les acceptations et les refus, formule des hypothèses, puis engage sa compréhension dans une combinaison finale dont la valeur est proportionnelle au risque pris.

---

## 2. Ce que le jeu n'est pas

Cadrage négatif, à relire à chaque décision de design.

- **Pas un jeu d'exploration ni de survie.** Aucun monde, aucune carte, aucun inventaire.
- **Pas un jeu narratif.** Aucune histoire écrite à la main.
- **Pas un jeu d'énigmes.** Une énigme se consomme une fois ; ici la règle est régénérée à chaque manche.
- **Pas un jeu multijoueur.** Solo strict (cold start, netcode, serveurs = hors périmètre).
- **Pas un jeu d'optimisation à information connue** (c'est Balatro — voir §11).
- **Pas un jeu de dextérité.** Zéro réflexe, tour par tour, temps de réflexion illimité.

---

## 3. Piliers de design

1. **La rareté de l'information crée le sens.** Savoir doit coûter quelque chose.
2. **Le contenu émerge des règles, jamais de la production manuelle.** Une grammaire, pas un catalogue.
3. **Jamais injuste.** Tout ce qui est nécessaire à la déduction est observable dans le jeu.
4. **L'effort est une décision douloureuse, pas une difficulté d'exécution.**
5. **Basse fidélité, haute finition.** Peu d'assets, beaucoup d'itération sur le ressenti.

---

## 4. Boucle de jeu (une manche)

### Phase A — Enquête

- Le système génère une **loi secrète** (voir §5) et distribue une **carte de départ**, qui satisfait toujours la loi.
- Le joueur dispose d'un **budget d'essais fixe** (30 aujourd'hui).
- À son tour, il ne choisit pas une carte : il **décrit l'expérience qu'il veut mener**, et paie sa précision. Le jeu tire une carte conforme à sa description et répond **acceptée** ou **refusée**.
  - Acceptée → la carte rejoint la **ligne principale**.
  - Refusée → elle rejoint la liste des refus, **datée** et **située** (numéro de sonde, position de la ligne à ce moment-là).
- Le joueur peut à tout moment déclarer qu'il pense avoir compris → passage en phase B.

#### La sonde — le verbe central

C'est le cœur du jeu, et il a été refondu après mesure.

| sonde | effet | prix |
|---|---|---|
| `jaune plié` | une carte au dos jaune et pliée, le reste au hasard | 3 |
| `jumelle 2 dos` | identique à la carte en position 2, **sauf le dos** | 3 |
| `hasard` | n'importe quelle carte | 1 |

Prix = 1 essai, +1 par attribut imposé.

**La jumelle est la raison d'être du dispositif.** C'est l'expérience contrôlée : une seule variable change, donc le verdict est directement interprétable. C'est aussi, formellement, l'observation dont le générateur a besoin pour garantir qu'une loi est déductible (§5) — et jusqu'à la refonte, le joueur n'avait aucun moyen de la demander.

> **Tranché en jouant.** La v0.1 faisait poser une carte nommée. Mesure : un solveur parfait épuisait l'information disponible en 10 coups pour un budget de 20. Une manche ne contenait donc qu'une dizaine de décisions, toutes de même nature. Pire, **l'intelligence du joueur n'avait aucune expression mécanique** : réfléchir cinq minutes ou taper au hasard produisait le même geste, et un système qui ne voit pas le talent ne peut ni le récompenser ni le faire varier. Décrire l'expérience rend le métier visible et tarifable.

> **Tranché en jouant — la jumelle est vendue sous son prix.** Elle épingle trois attributs, elle devrait coûter 4. Un solveur glouton qui optimise l'information par essai ne la prend jamais à ce tarif : les sondes larges rapportent plus par essai dépensé. Mais ce solveur met à jour 1711 hypothèses bayésiennement, un humain non. La valeur d'une jumelle est **cognitive**, pas informationnelle. À plein tarif, le choix pelle-ou-scalpel n'existerait pas.

> **Tranché en jouant — budget fixe, pas croissant.** Le risque de boule de neige identifié en v0.1 était réel ; on a retenu l'alternative qu'elle proposait. Les essais économisés ne rapportent pas de points, ils **multiplient le score** (§9).

### Phase B — Le pari

- Le joueur accède à une main **bornée** : 12 cartes tirées du paquet. Jamais l'accès total, sinon le problème devient un exercice de tableur.
- Il construit la **suite la plus rentable possible**, sans se tromper. Elle **prolonge la carte de départ**, qui juge sa première carte.
- Puis, **facultativement, il énonce la loi**. Second pari de même mise : juste, il double ; faux, il perd autant ; refuser ne coûte rien.

> **Tranché en jouant — la déclaration de la loi n'était pas dans la v0.1, et son absence était un trou.** Un joueur a encaissé le maximum de points avec un modèle faux : son hypothèse « uniquement du rouge » était plus restrictive que la vraie loi, donc toute suite qu'elle autorisait était sûre. **Une hypothèse fausse mais incluse dans la vérité gagne autant qu'une compréhension exacte.** Le pari ne testait que le comportement ; il fallait un endroit où la compréhension elle-même s'engage.

> **La déclaration est jugée sur le comportement, jamais sur les mots.** Une formulation que rien d'observable ne distingue de la vraie loi compte juste (§3, pilier 3). Elle se construit par menus — famille, attribut, paramètres — et non dans une liste de lois candidates : le joueur reçoit la grammaire, jamais l'espace des réponses. Le constructeur n'apparaît qu'en phase B, une fois l'enquête close ; disponible plus tôt, il permettrait l'élimination mécanique que le §6 interdit.

> **Effet secondaire observé, non anticipé.** La déclaration s'est révélée être un **déclencheur de compréhension** autant qu'un barème : un joueur n'a compris la seconde clause qu'au moment où le jeu lui a demandé de la formuler, en le forçant à relire sa propre ligne. Varier la *tâche* produit de l'expérience neuve sans contenu neuf. À retenir pour le §14.

### Phase C — Résolution

- Si la suite est valide → le joueur encaisse les points.
- Si elle est invalide → la valeur de la suite **se retourne contre lui**.
- Le total est **multiplié** par les essais économisés (§9), gains comme pertes.
- **La loi est révélée**, quoi qu'il arrive. Le joueur apprend toujours quelque chose.
- Manche suivante : nouvelle loi.

**C'est le cœur du jeu** : le joueur peu sûr de lui joue une suite modeste et sûre ; le joueur confiant vise gros et risque de se prendre sa propre ambition en pleine figure. La compréhension devient une monnaie, pas une fin.

---

## 5. La grammaire de règles (moteur de rejouabilité)

### Principe

On ne code **pas** des règles. On code des **briques combinables** ; le système en compose une loi nouvelle à chaque manche. Dix briques donnent des centaines de lois sans écrire une ligne de contenu.

### Dimensions d'une carte

La distinction qui compte n'est pas classique / caché, c'est **indépendant / dérivé**.

**Attributs indépendants** — ils définissent la carte
- rang (1–13)
- enseigne (4)
- dos (ivoire / jaune)
- pli (lisse / plié)

**Attributs dérivés** — calculés, jamais stockés
- couleur ← enseigne
- parité ← rang

**Attributs cachés restant à introduire** : marque, sceau, gravure, usure.

### Le paquet est le produit cartésien complet

13 × 4 × 2 × 2 = **208 cartes**, chaque combinaison exactement une fois.

> **Tranché en jouant, et c'est un changement de nature, pas une inflation.** Dans un paquet de 52, dos et pli sont des **fonctions** de (rang, enseigne) : il n'existe qu'un seul 9♥, avec son dos et son pli figés. Faire varier une dimension en gardant toutes les autres constantes est donc **impossible** — les jumelles n'existent pas, l'expérience contrôlée n'existe pas, et l'induction se réduit à une collecte de coïncidences. Avec le produit complet, toute carte a ses jumelles. Le paquet n'étant jamais affiché en entier (le joueur le décrit au lieu de le lire), sa taille ne coûte rien.

### Types de briques

- **Absolue** : « pas de carte au dos jaune »
- **Relationnelle** : « rang supérieur au précédent », « enseigne différente »
- **Séquentielle** : « pas deux nombres impairs d'affilée »
- **Conditionnelle** (difficulté élevée) : « si la précédente est rouge, alors… »

Une loi = 1 à 3 briques combinées.

### Contraintes impératives du générateur

1. **Calibrage de permissivité.** Environ ¼ à ½ du paquet jouable. Lu comme : moyenne sur les contextes atteignables dans la cible, **plus l'ouverture dans la cible elle aussi**. Un contexte ne descend jamais sous 8 %.

   > **Tranché en jouant.** Ne contrôler que la moyenne ne suffit pas : le joueur passe ses premiers coups dans un seul contexte, celui du départ. Une manche a distribué une ouverture à 17 % pour une moyenne à 33 % — cinq refus d'affilée en ouverture, 39 % de chances que ça arrive. La première impression se joue là.

2. **Testabilité garantie.** *La contrainte la plus difficile, et celle qui décide de la qualité du jeu.*

   > **Reformulée après implémentation.** La v0.1 posait le problème en **fréquence** — « un attribut qui n'apparaît qu'une fois toutes les trente cartes ». C'est le mauvais angle et il rate le vrai danger, qui est le **masquage** : dans une conjonction, un refus ne dit que « au moins une clause a échoué ». Si la clause A refuse 80 % des cartes, presque toute carte qui viole B viole aussi A, et B devient invisible **quelle que soit sa fréquence**. Une clause parfaitement fréquente peut être parfaitement indéductible.
   >
   > La bonne question n'est pas « l'attribut sort-il assez souvent » mais **« la loi est-elle séparable de ses rivales dans le flux réellement atteignable »**. Le générateur exige donc que chaque clause dispose d'assez de **témoins pivots** — des refus dont elle est la seule responsable.

3. **Aucune exception, aucun joker.** Pas de « les figures sont toujours valides ».

4. **Aucune impasse.** Depuis tout état de ligne, au moins une carte est jouable.

   > **Ambiguïté levée.** La v0.1 écrivait « toute carte doit être jouable après une certaine carte », ce qui **contredit son propre exemple de brique absolue** : une carte au dos jaune n'est jouable après aucune carte sous la règle « pas de dos jaune ». Lecture retenue : anti-impasse. Les briques absolues restent autorisées, des cartes peuvent être définitivement mortes, le jeu ne peut jamais se bloquer.

5. **La loi est validée contre le paquet réalisé ET la carte de départ réelle**, et rendue avec eux.

   > **Tranché en jouant, après un bug.** On échantillonnait les contextes depuis un départ tiré au hasard, ce qui mesurait « déductible depuis *un* départ » au lieu de « déductible depuis *ce* départ ». Cas réel : loi « jamais ♣ » **et** « même couleur que la précédente », départ rouge. La clause de couleur verrouille la ligne sur le rouge pour toujours, et sur une ligne rouge « jamais ♣ » est strictement inobservable. 91 témoins comptés en échantillonnage aléatoire, **0** depuis le départ réel. Le joueur a gagné le maximum avec un modèle faux sans jamais pouvoir voir la seconde clause.

6. **La carte de départ satisfait la loi.**

   > **Tranché en jouant.** 24 % des manches distribuaient un départ qui contredisait visiblement sa propre loi. Le joueur voit alors en position 0 une carte qui réfute une hypothèse correcte, et l'écarte pour cette raison : c'est le §3 pilier 3 violé par une observation que le jeu a lui-même fabriquée.

---

## 6. Vocabulaire du joueur (garde-fou anti-injustice)

Problème : si la loi porte sur le dos des cartes et que le joueur ignore que le dos est une variable, il n'y a pas déduction — il y a échec au hasard.

**Solution retenue :** le jeu mémorise l'ensemble des dimensions que le joueur a **effectivement manipulées au moins une fois**. Le générateur ne compose ses lois qu'à partir de ce vocabulaire acquis.

Conséquences :
- Le mystère porte sur **quelle loi**, jamais sur **quelles dimensions existent**.
- La découverte progressive du vocabulaire devient un moteur de progression roguelike naturel.
- Coût d'implémentation : trivial.

### Provoquer la découverte sans la forcer

- Rendre les cartes **manipulables dès la première seconde**, sans enjeu, pour que le geste soit connu avant d'être utile.
- Signaler qu'**un attribut inconnu est en jeu, sans dire lequel** (la carte tremble). Le joueur apprend qu'il lui manque du vocabulaire, sans gagner d'information gratuite sur la loi.
- **À ne pas faire hors tutoriel :** montrer l'attribut fautif. Le joueur éliminerait 2-3 attributs par carte posée et remplacerait la déduction par de l'élimination mécanique.

> **État en console.** Sans run ni méta-progression, le vocabulaire est **annoncé en entier au démarrage** : la liste des dimensions actives est affichée avant le premier coup. Le geste de manipulation n'existe donc pas, et le mécanisme d'acquisition progressive décrit ci-dessus non plus. Il reprendra son sens à l'étape 3.
>
> **Ce principe a servi deux fois à trancher, hors du cas prévu.**
>
> **1. La déclaration de la loi (§4).** Elle se construit par menus successifs — famille, puis attribut, puis paramètres — et non dans une liste de lois candidates. Le joueur reçoit la **grammaire** (les formes de règles existantes), jamais l'**espace des réponses**. Et le constructeur n'apparaît qu'en phase B : disponible pendant l'enquête, il aurait permis exactement l'élimination mécanique interdite ci-dessus.
>
> **2. Les refus périmés.** Une carte refusée puis devenue jouable apparaissait sans repère temporel. La correction naturelle — signaler qu'elle passerait maintenant — est **interdite** : ce serait révéler un fait sur le contexte courant que le joueur n'a pas payé. Retenu à la place : dater et situer le refus (numéro de sonde, position de la ligne). Le joueur reçoit son propre passé mieux rangé, aucune information neuve.

---

## 7. Difficulté

Trois curseurs **indépendants**, à faire monter **en décalé** — jamais ensemble.

| Curseur | Progression |
|---|---|
| Nombre de dimensions actives | rang → rang + dos → rang + dos + pli → … |
| Complexité de la loi | 1 brique → 2 briques → conditionnelle |
| Budget d'essais | se resserre |
| Tarif des sondes | la jumelle renchérit |

> **Ajouté après la refonte de la sonde.** Le tarif est un quatrième curseur, et probablement le plus fin des quatre : il ne change pas la difficulté de la loi, il change le **coût de la méthode**. Resserrer le budget punit le tâtonnement ; renchérir la jumelle punit le confort. Ce sont deux douleurs différentes, à ne pas confondre au réglage.

**Étalonnage mesuré.** Un solveur parfait — mémoire parfaite, aucun biais, gain d'information par essai optimisé — dépense une médiane de **18 essais sur 30**. C'est un plancher, pas une cible : un humain est très en dessous. Toute modification du tarif ou de la grammaire doit être repassée au solveur avant d'être jouée.

---

## 8. Couche roguelike

État actuel : boucle de manche solide, **structure de run encore à concevoir**. C'est le principal chantier de design restant.

### Règle d'or des objets

> Un objet donne du **confort** ou du **risque**. Jamais de l'**information**.

Un objet qui révèle une clause détruit la boucle. Le meilleur objet du jeu est celui qui pousse à **parier davantage**.

### Pistes d'objets

- essai supplémentaire
- rejouer une carte déjà posée
- multiplicateur de points contre réduction du budget d'essais
- consulter une carte retirée de la pioche
- pénalité d'échec réduite (permet de tenter des suites plus ambitieuses)

### À définir

- Structure du run : nombre de manches, condition de défaite, escalade.
- Économie inter-manches — **sans copier la boutique de Balatro**.
- Méta-progression entre runs (déblocage de dimensions ? de briques ?).

---

## 9. Récompense

Deux boucles concurrentes, à hiérarchiser :

- **Récompense intellectuelle** (comprendre) : très puissante, mais **s'éteint dès qu'elle est obtenue**.
- **Récompense mécanique** (points) : c'est elle qui doit porter le run.

**Liaison retenue :** comprendre vite → plus d'essais restants → suite plus ambitieuse possible → plus de points. La déduction alimente l'optimisation au lieu de la concurrencer.

### Mise en œuvre : les essais économisés MULTIPLIENT, ils ne s'ajoutent jamais

`score = (suite + loi) × (1 + essais_restants / budget)`, plafonné à ×2, **appliqué aux pertes autant qu'aux gains**.

> **Tranché en jouant, sur une objection du joueur.** L'idée naturelle — convertir les essais restants en points — est une faute de conception à deux titres. D'abord elle fait **coûter des points à l'enquête**, ce qui inverse exactement l'incitation que le §9 cherche. Ensuite elle s'exploite trivialement : on déclare n'importe quoi au premier tour et on empoche le budget entier. Un multiplicateur sur zéro fait zéro ; la mise en friche ne rapporte plus rien.
>
> **L'appliquer aux pertes est ce qui fait tenir l'ensemble.** Sinon se précipiter serait du gain gratuit — gros si j'ai raison, petit si j'ai tort. Des deux côtés, la vitesse cesse d'être un bonus et devient un **multiplicateur de risque** : comprendre vite paie, croire avoir compris vite coûte cher. C'est le §9 sans la boule de neige que le §4 redoutait.

---

## 10. Direction artistique (phase ultérieure — ne rien produire maintenant)

**Univers : manuscrit médiéval, enquête, artisanat.** Parchemin, encre, bois, bougie, sceaux, gravures, pliures.

Justification de design, pas décorative : le jeu n'est pas un jeu de cartes, c'est un jeu de **loi cachée**. Une coutume jamais écrite, un tribunal dont on ignore le code, un rituel dont on ne connaît pas les interdits — ça donne une raison narrative au secret, et transforme les « attributs cachés » en indices d'artisanat plutôt qu'en variables abstraites.

- Le pixel art est un choix assumé : il ne fait pas gagner du temps de production, il permet de **jeter et refaire dix fois**.
- Le médiéval-fantasy est saturé sur Steam : il doit être un **carburant personnel et un support logique**, jamais un argument de vente.
- **Si la mécanique demande quelque chose que le thème refuse, c'est le thème qui plie.**

---

## 11. Garde-fous Balatro

La ressemblance autorisée s'arrête à : *roguelike de cartes en pixel art*.

**À ne pas importer :**
- structure économique (boutique entre manches, jokers empilables, argent, mains/défausses)
- direction artistique (noir profond, néon, CRT, carte à jouer de casino)
- pitch (« Balatro mais… »)

**Risque principal — contamination du design.** En cas de blocage sur l'équilibrage, le réflexe « comment fait Balatro ? » importe des solutions conçues pour un jeu d'**optimisation à information connue** dans un jeu d'**induction**. Cela abîme la boucle de façon invisible.

**Réflexe correct :** aller voir les jeux du même genre — Mastermind, Zendo, Eleusis, The Witness, Chants of Sennaar.

Balatro fournit un **format** et un **modèle de vie de développeur**. Pas des solutions de design.

---

## 12. Inspirations

| Source | Ce qu'on en prend |
|---|---|
| **Eleusis** (Abbott, 1956) | La boucle d'induction elle-même, le calibrage de permissivité, la lisibilité ligne principale / lignes d'erreur |
| **Zendo**, 2-4-6 de Wason | L'induction comme jeu, le biais de confirmation comme ressort |
| **Mastermind** | Le retour quantitatif imprécis ; chaque coup est à la fois engagement et sonde |
| **Balatro** | Format roguelike de cartes, combinatoire plutôt que contenu écrit, modèle de dev solo |
| **Obra Dinn / Chants of Sennaar / Tunic / Animal Well** | La découverte diégétique : l'info est présente, le joueur la remarque |
| **Into the Breach** | Opposition systémique plutôt qu'adversaire symétrique |

**Divergence assumée avec Eleusis :** Eleusis est social et dépend de la qualité de l'humain qui invente la loi. Apport propre du projet : grammaire générative, optimisation en parallèle de la déduction, structure en runs.

---

## 13. Phase 0 — Prototype console (le seul livrable actuel)

**Objectif unique : déterminer si déduire une loi cachée procure du plaisir plus d'une fois.**
Tant que ce n'est pas répondu, tout le reste du document est spéculatif.

### Périmètre

- Terminal, texte brut. Python, bibliothèque standard seule.
- **Aucun graphisme, aucun son, aucun asset, aucune interface.**
- 3 familles de briques : absolue, relationnelle, séquentielle. Lois à 1 ou 2 clauses.
- Une seule manche, pas de run, pas d'objets, pas de méta-progression, pas d'escalade.
- Attributs cachés simulés textuellement (`7♠ [dos:jaune] [plié]`) et toujours visibles.
- **Générateur et validateur appelables indépendamment de la boucle de jeu**, pour régler sans jouer.

**Objectif de la phase 0, rappelé** : répondre à une seule question. Tout ce qui n'y sert pas est hors périmètre, y compris les bonnes idées.

### Fonctionnel minimal — **état : livré**

1. ~~Générateur de loi à partir de 3 briques.~~ **fait** — absolue, relationnelle, séquentielle ; catalogue engendré depuis le registre d'attributs, aucune règle écrite à la main.
2. ~~Vérificateur de permissivité.~~ **fait**, et étendu bien au-delà : anti-masquage, anti-impasse, identifiabilité exacte sur toute la grammaire, ouverture calibrée.
3. ~~Le joueur saisit une carte.~~ **remplacé** — le joueur décrit une expérience et paie sa précision (§4).
4. ~~Affichage ligne principale et refus.~~ **fait**, les refus étant datés et situés.
5. ~~Compteur d'essais.~~ **fait**, budget fixe, coût variable par sonde.
6. ~~Déclaration d'hypothèse → pari → résolution → révélation.~~ **fait**, plus la déclaration facultative de la loi, jugée sur le comportement.

**Au-delà du minimal, non prévu en v0.1 :** un solveur de référence qui mesure le plancher en essais, et un balayage qui affiche la répartition des motifs de rejet du générateur. Les deux servent à régler sans jouer.

### Ce qui reste ouvert dans la phase 0

- Le générateur peut encore habiller une règle d'un seul attribut en deux briques (« jamais noir » **et** « jamais ♥ » = « uniquement du carreau »). Inélégant ; plus injuste depuis que la déclaration est jugée extensionnellement.
- **Le test externe (ci-dessous) n'a pas encore eu lieu.** C'est la seule case décisive encore vide.

### Méthode de travail

Développement avec Claude Code, dans un repo git dédié. **Une partie jouée après chaque itération**, ajustement immédiat de ce qui coince. Cycle court, pas de planification longue.

### Critères d'évaluation (à noter après chaque partie)

- L'incertitude est-elle excitante ou seulement frustrante ?
- Le moment « ah, j'ai compris » existe-t-il, et est-il fort ?
- Au bout de trois manches : envie de continuer, ou soulagement d'arrêter ?
- **Le signal décisif : est-ce que je relance une partie sans y penser ?**

### Test externe

Mettre un ami devant, sans explication, et chronométrer. Observer où il coince, ce qu'il ne remarque pas. Le seul indicateur qui compte : **demande-t-il à rejouer ?**

> Précédent utile : le déclic de Balatro n'a pas été une intuition de marché, mais un ami disant avoir joué 30 ou 40 heures. Signal comportemental, jamais déclaratif.

---

## 14. Étapes suivantes (ordre strict)

| Étape | Contenu | Condition de passage | État |
|---|---|---|---|
| **0** | Jouer à Eleusis Express sur table | Test de sensation, 2 h | — |
| **1** | Générateur console, 3 briques | La boucle est grisante en texte brut | **franchie** (auteur) ; **test externe en attente** |
| **2** | Élargissement de la grammaire — **par famille, pas par attribut** | La reconnaissance ne remplace pas la découverte avant la manche N | à venir |
| **3** | Couche run : objets, escalade, défaite | Un run donne envie d'en relancer un | à venir |
| **4** | Interface graphique + DA médiévale | Tout le reste est validé | à venir |

**Ne jamais sauter une étape.** Chaque passage se décide sur du ressenti mesuré, pas sur de l'enthousiasme.

### Étape 2, reformulée après mesure

La v0.1 disait « élargissement de la grammaire **+ attributs cachés** ». C'est le mauvais levier, et le chiffre le montre :

```
lois à 2 clauses possibles     1 653
comportements distincts        ~1 200
FORMES de règle distinctes         22
```

**Le joueur n'apprend pas 1200 lois, il apprend 22 formes.** Et **un attribut de plus n'ajoute que 4 formes** — absolue, relation égal, relation différent, séquence. Passer de 6 à 7 dimensions, c'est +18 % de vocabulaire pour une explosion d'instances que personne ne ressent.

Ce qui multiplie les formes, c'est une **famille**. La conditionnelle du §5, jamais construite, en ajoute de l'ordre de 36 : elle triple le vocabulaire d'un coup.

**Coût technique mesuré** : le catalogue passerait de 58 à ~202 clauses, les lois à 2 clauses de 1 653 à ~20 300 (×12), et une analyse complète de 109 ms à ~380 ms plus l'énumération. L'astuce des masques de bits tient encore, mais la génération par rejet d'échantillonnage passerait sous la seconde à plusieurs dizaines. Il faudra élaguer.

### Condition de passage de l'étape 2, reformulée

« La variété tient sur 10 manches » n'est pas mesurable. La bonne question est :

> **À partir de quelle manche le joueur reconnaît-il la forme au lieu de la découvrir ?**

C'est ce nombre qui dit si la saturation est un problème urgent ou lointain, et c'est lui qui doit piloter la conception de la couche run.

---

## 15. Règles de conduite du projet

- **Arrêter dès que l'envie tombe**, sans culpabilité. Le prototype n°7 ne sera jamais atteint si on s'acharne six mois sur le n°2.
- Le jeu est un **pari parallèle à option** : coût faible, plafond immense, espérance mathématique mauvaise. Il ne remplace pas la piste principale et ne constitue pas un chemin fiable vers un revenu.
- Ne pas mesurer ce projet à l'aune du chiffre d'affaires. Le mesurer à l'aune de la question : **est-ce que ça m'anime ?**

---

## 16. Questions ouvertes

### Tranchées en jouant

1. ~~Budget d'essais : croissant ou fixe ?~~ → **fixe**, 30 essais, avec un **coût variable par sonde**. Les essais économisés multiplient le score (§9). La boule de neige redoutée par le §4 est évitée sans perdre la liaison du §9.
2. ~~Forme de la phase de pari ?~~ → **longueur libre, tout ou rien**, depuis une main tirée de 12, la suite prolongeant la carte de départ. **Plus une déclaration facultative de la loi**, de même mise, jugée sur le comportement.

### Encore ouvertes

3. **Structure du run** : combien de manches, quelle condition de défaite ? *C'est le principal chantier restant (§8).*
4. Adversaire abstrait ou score cible ? **Défaut retenu : score cible.** Non remis en cause.
5. **Méta-progression entre runs** : déblocage de dimensions, de briques, ou rien ? *Un argument nouveau en faveur du déblocage, apparu en jouant : la surprise vient de la découverte d'une **forme** de règle jamais vue, et ce stock s'épuise (22 formes, §14). Le débloquer progressivement étale une ressource rare au lieu de la brûler en dix manches.*
6. **Nom du jeu.**

### Ouverte, et la plus lourde — soulevée par un testeur

7. **Le joueur est-il assez maître de sa partie ?** Chaque manche propose le même verbe : j'observe, je teste, je déduis, je propose. La refonte de la sonde (§4) a beaucoup amélioré ça — le joueur compose désormais son expérience — mais la critique de fond tient : là où un roguelike de cartes renouvelle l'**espace d'action** à chaque run, nous ne renouvelons que l'**espace de contenu**, et le contenu sature au niveau des formes.

   Pistes envisagées, non tranchées :
   - **Plusieurs lois en parallèle, un seul budget.** Chaque tour devient une allocation : où est-ce que je creuse ? Spécialiste ou généraliste devient une identité de partie, et la combinaison des lois varie même à vocabulaire constant.
   - **Paquets pré-construits à caractère** (dos très variés / rangs uniformes, etc.). Attention : la composition **libre** est un piège — un paquet dégénéré rend une dimension intestable, donc le générateur ne peut plus produire de loi qui la touche, donc le joueur connaît la famille de la loi avant de commencer. Bornée uniquement.
   - **Engagement partiel façon Obra Dinn** : inscrire des faits isolés au fil de l'enquête, confirmés par lots. Répond aussi au tout-ou-rien du barème.
