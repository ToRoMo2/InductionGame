# Cahier des charges — Jeu d'induction (nom de code : **LEX**)

> Document interne. Non destiné à la publication ni à la communication externe.
> Version 0.1 — sert de base de travail pour la phase console.

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

- Le système génère une **loi secrète** (voir §5).
- Le joueur dispose d'un **budget d'essais**.
- À son tour, il pose une carte. Le jeu répond **acceptée** ou **refusée**.
  - Acceptée → la carte rejoint la **ligne principale** ; le joueur gagne des essais supplémentaires.
  - Refusée → l'essai est consommé, la carte **retourne dans la pioche** (elle pourra ressortir ; c'est au joueur de retenir qu'il l'a déjà tentée).
- Le joueur peut à tout moment déclarer qu'il pense avoir compris → passage en phase B.

> **Risque identifié — effet boule de neige.** Récompenser un bon coup par des essais supplémentaires favorise celui qui a déjà compris et assèche celui qui cherche encore. Curseur à surveiller de très près au réglage. Alternative à tester : budget fixe par manche, l'acceptation rapportant des points plutôt que des essais.

### Phase B — Le pari

- Le joueur accède à une main élargie (**bornée** : longueur maximale ou main tirée — jamais l'accès total au paquet, sinon le problème devient un exercice de tableur).
- Il construit la **suite la plus rentable possible**, sans se tromper.
- Valeur de la suite = récompense potentielle **et** pénalité potentielle.

### Phase C — Résolution

- Si la suite est valide → le joueur encaisse les points.
- Si elle est invalide → la valeur de la suite **se retourne contre lui** (perte de points de vie / de score).
- **La loi est révélée**, quoi qu'il arrive. Le joueur apprend toujours quelque chose.
- Manche suivante : nouvelle loi.

**C'est le cœur du jeu** : le joueur peu sûr de lui joue une suite modeste et sûre ; le joueur confiant vise gros et risque de se prendre sa propre ambition en pleine figure. La compréhension devient une monnaie, pas une fin.

---

## 5. La grammaire de règles (moteur de rejouabilité)

### Principe

On ne code **pas** des règles. On code des **briques combinables** ; le système en compose une loi nouvelle à chaque manche. Dix briques donnent des centaines de lois sans écrire une ligne de contenu.

### Dimensions d'une carte

Deux familles, à distinguer clairement :

**Attributs classiques**
- rang (1–13)
- couleur (rouge / noir)
- enseigne (4)
- parité du rang

**Attributs cachés** — la signature du jeu
- couleur du dos
- carte légèrement pliée / non pliée
- marque, sceau, gravure (à définir)
- usure

Ces attributs cachés sont physiquement présents et manipulables : le joueur peut retourner une carte, l'inspecter, la manipuler.

### Types de briques

- **Absolue** : « pas de carte au dos jaune »
- **Relationnelle** : « rang supérieur au précédent », « enseigne différente »
- **Séquentielle** : « pas deux nombres impairs d'affilée »
- **Conditionnelle** (difficulté élevée) : « si la précédente est rouge, alors… »

Une loi = 1 à 3 briques combinées.

### Contraintes impératives du générateur

1. **Calibrage de permissivité.** Environ ¼ à ½ du paquet doit être jouable à tout instant (règle empirique héritée d'Eleusis). Trop restrictif = frustrant ; trop permissif = indétectable.
2. **Testabilité garantie.** Une clause portant sur un attribut qui n'apparaît qu'une fois toutes les trente cartes est indéductible. Le générateur doit **vérifier que chaque clause est apprenable dans le flux réellement disponible**. C'est la contrainte la plus difficile à coder, et celle qui décide de la qualité du jeu.
3. **Aucune exception, aucun joker.** Pas de « les figures sont toujours valides ».
4. **Toute carte doit être jouable après une certaine carte.**

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

---

## 7. Difficulté

Trois curseurs **indépendants**, à faire monter **en décalé** — jamais ensemble.

| Curseur | Progression |
|---|---|
| Nombre de dimensions actives | rang → rang + dos → rang + dos + pli → … |
| Complexité de la loi | 1 brique → 2 briques → conditionnelle |
| Budget d'essais | se resserre |

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

- Terminal, texte brut.
- **Aucun graphisme, aucun son, aucun asset, aucune interface.**
- 3 briques de règles maximum au départ.
- Une seule manche, pas de run, pas d'objets, pas de méta-progression.
- Attributs cachés simulés textuellement (`7♠ [dos:jaune] [plié]`).

### Fonctionnel minimal

1. Générateur de loi à partir de 3 briques.
2. Vérificateur de permissivité (¼–½ du paquet jouable).
3. Boucle : le joueur saisit une carte → réponse acceptée / refusée.
4. Affichage de la ligne principale et des cartes refusées.
5. Compteur d'essais.
6. Déclaration d'hypothèse → phase de pari → résolution → révélation de la loi.

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

| Étape | Contenu | Condition de passage |
|---|---|---|
| **0** | Jouer à Eleusis Express sur table | Test de sensation, 2 h |
| **1** | Générateur console, 3 briques | La boucle est grisante en texte brut |
| **2** | Élargissement de la grammaire + attributs cachés | La variété tient sur 10 manches |
| **3** | Couche run : objets, escalade, défaite | Un run donne envie d'en relancer un |
| **4** | Interface graphique + DA médiévale | Tout le reste est validé |

**Ne jamais sauter une étape.** Chaque passage se décide sur du ressenti mesuré, pas sur de l'enthousiasme.

---

## 15. Règles de conduite du projet

- **Arrêter dès que l'envie tombe**, sans culpabilité. Le prototype n°7 ne sera jamais atteint si on s'acharne six mois sur le n°2.
- Le jeu est un **pari parallèle à option** : coût faible, plafond immense, espérance mathématique mauvaise. Il ne remplace pas la piste principale et ne constitue pas un chemin fiable vers un revenu.
- Ne pas mesurer ce projet à l'aune du chiffre d'affaires. Le mesurer à l'aune de la question : **est-ce que ça m'anime ?**

---

## 16. Questions ouvertes

1. Budget d'essais : croissant (boule de neige) ou fixe par manche ?
2. Forme exacte de la phase de pari : longueur libre ? main imposée ? mise annoncée à l'avance ?
3. Structure du run : combien de manches, quelle condition de défaite ?
4. Faut-il un adversaire abstrait (points de vie) ou un simple score cible ? **Défaut retenu : score cible** — un ennemi coûte des assets et du design non nécessaires pour l'instant.
5. Méta-progression entre runs : déblocage de dimensions, de briques, ou rien ?
6. Nom du jeu.
