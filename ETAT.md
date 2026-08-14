# État du projet — ce qui est fait, ce qui reste

> Fichier de suivi. À lire en premier pour reprendre le projet après une pause.
> Le **pourquoi** de chaque décision est dans `cahier-des-charges-jeu-induction.md` ;
> ici on ne garde que **l'état** et les **chiffres**.
>
> Règle de tenue : rien ne se décide sans être écrit ici. Une idée qui n'est pas
> dans ce fichier n'existe pas.

---

## 1. Où on en est

Feuille de route du §14, dans l'ordre strict :

| Étape | Contenu | État |
|---|---|---|
| 0 | Jouer à Eleusis Express sur table | non fait, non bloquant |
| 1 | Générateur console, 3 briques | **franchie** — validée par l'auteur et un testeur externe |
| 2 | Élargissement de la grammaire **par famille** | **franchie** — famille conditionnelle livrée |
| 3 | Couche run : objets, escalade, défaite | **en cours** — colonne vertébrale faite, reste objets et défaite |
| 4 | Interface graphique + DA médiévale | pas commencée, et ne doit pas l'être |

**Test externe (§13) — concluant.**

- 1re session : joueur non codeur, sans explication, trouve sa première loi et
  aime ça. Réserve : « sans plus », attribué au tout-texte.
- Correctif : affichage en colonnes (ligne principale à gauche, refus à droite).
- 2e session : **il confirme que c'est beaucoup plus lisible**, et surtout —
  **il a réinstallé le jeu sur son propre PC et l'a relancé de lui-même, en
  stream.**

Le §13 dit que le seul indicateur qui compte est comportemental, jamais
déclaratif. Il n'a pas *demandé* à rejouer : il est allé le chercher et l'a
joué en public, sur son matériel. C'est plus fort qu'une demande, et c'est le
signal que le §13 appelle décisif. **Il est positif.**

---

## 2. Les chiffres

Tous mesurés, aucun deviné. Entre parenthèses, où ils vivent dans le code.

### Le jeu

| | valeur | note |
|---|---|---|
| paquet | **208 cartes** | produit cartésien complet 13 × 4 × 2 × 2 (`cards.py`) |
| dimensions | 6 | 4 indépendantes (rang, enseigne, dos, pli) + 2 dérivées (couleur, parité) |
| catalogue | **187 clauses** | 18 absolues, 13 relationnelles, 24 séquentielles, 132 conditionnelles (`bricks.py`) |
| formes de règle | **48** | ce que le joueur apprend réellement — pas les 187 |
| lois à 1 ou 2 clauses | **17 578** | espace d'hypothèses |
| main du pari | 12 cartes (`MAIN_PARI`) | retirée jusqu'à permettre ≥ 3 cartes (`SUITE_MIN`) |
| budget, manche isolée | 30 (`ESSAIS`) | avec multiplicateur |
| budget, run | **120 partagés** (`BUDGET`) sur 6 manches (`MANCHES`) | sans multiplicateur |
| prix d'une sonde | 1 + nb d'attributs imposés | jumelle à 3 (`COUT_JUMELLE`) |

### Étalonnage

| mesure | valeur |
|---|---|
| plancher d'un solveur parfait | **~19 essais par manche** (médiane) |
| marge laissée à l'humain | ~1,6× en run (120 pour ~114 de plancher) |
| taux d'acceptation du générateur | ~40 % des lois tirées au hasard |
| temps de génération | médiane 0,6 s, pic 3,4 s |

### Seuils du validateur (`validator.py`)

| seuil | valeur | rôle |
|---|---|---|
| `PERM_MIN` / `PERM_MAX` | 25 % / 50 % | §5.1, moyenne **et** ouverture |
| `PERM_PLANCHER` | 8 % | anti-impasse, par contexte |
| `TEMOINS_FRAC` | 1 % | anti-masquage : refus imputables à une seule clause |
| `N_CONTEXTES` | 24 | contextes échantillonnés, tous depuis le départ réel |

---

## 3. FAIT

### Boucle de manche
- Phases A (enquête) / B (pari) / C (résolution), loi toujours révélée.
- **La sonde** : le joueur décrit l'expérience voulue et paie sa précision.
  Trois formes — description libre, **jumelle** (identique sauf une dimension),
  tirage au hasard.
- Budget d'essais **fixe**, coût **variable** par sonde.
- Pari à longueur libre, tout ou rien, prolongeant la carte de départ.
- **Déclaration de la loi** facultative, second pari de même mise, construite
  par menus (famille → attribut → paramètres).
- **Se coucher** est légal : suite vide, 0 point, aucun risque.

### Justice — chaque point vient d'un bug réel
- La loi est validée contre le **paquet réalisé** et la **carte de départ
  réelle**, jamais un départ tiré au hasard.
- La **carte de départ satisfait la loi** (24 % des manches la contredisaient).
- L'**ouverture** est calibrée, pas seulement la permissivité moyenne.
- La **main du pari est retirée** jusqu'à permettre 3 cartes (2 % des mains
  n'en permettaient aucune).
- La déclaration est jugée **extensionnellement**, y compris entre familles.
- Quand la déclaration est fausse, le jeu **montre un contre-exemple**, choisi
  parmi les plus proches d'une jumelle.
- La loi révélée est réécrite dans sa **formulation la plus courte**.

### Grammaire
- 4 familles : absolue, relationnelle, séquentielle, **conditionnelle**.
- Tirage **équiprobable par famille**, jamais par clause.
- Rang : `monte` / `descend` d'un pas cyclique de 1 à 6 — une seule amplitude.

### Run (étape 3)
- 6 manches reliées par **un seul budget d'essais**.
- Multiplicateur désactivé en run, conservé en manche isolée.
- Score cumulé, bilan de fin.

### Adversaires (prototype)
- Un roi est un **jeu de paramètres** : pondération des familles, budget,
  nombre de manches. `roi_engendre()` en produit à volonté.
- Trois témoins de test contrastés : le Sénéchal (52 % relationnel),
  l'Archiviste (60 % conditionnel), la Prévôte (4 manches, 70 essais).

### Outillage
- `python -m lex.generator` — engendre des lois et leurs stats.
- `python -m lex.validator` — rapport détaillé, `--balayage` pour les rejets.
- Mode `--etroit` (34 colonnes) pour téléphone.

---

## 4. DÉCIDÉ, PAS ENCORE CONSTRUIT

### 4.1 — Vocabulaire de formes (§16.5) — *conception complète*
Le constructeur de déclaration montre le catalogue entier : dès la deuxième
partie, plus aucune forme ne surprend. Le stock de surprise (48 formes) est
consommé en une soirée.

**Mécanisme retenu :** le joueur possède un vocabulaire de formes ; le
générateur tire dedans ; parfois une manche tire **hors** vocabulaire, et alors
**la déclaration n'est pas proposée** — son absence signale l'inédit. La
révélation ajoute la forme au vocabulaire.

**Règle de justice indissociable :** sur ces manches, le joueur ne perd rien sur
la déclaration — elle n'existe pas. Sinon il perdrait en ayant compris.

**Bénéfice mesuré :** le déblocage **est** la courbe de difficulté.

| vocabulaire | clauses | formes | lois |
|---|---|---|---|
| absolue | 18 | 5 | 171 |
| + relationnelle | 31 | 18 | 496 |
| + séquentielle | 55 | 23 | 1 540 |
| + conditionnelle | 187 | 48 | 17 578 |

**Note d'implémentation à ne pas oublier :** restreindre aussi les **rivales**
du validateur au vocabulaire du joueur. Sans ça le générateur rejetterait des
lois pour confusion avec des rivales que le joueur ne peut pas concevoir.

**Non tranché :** fréquence des manches à forme inconnue ; annoncé ou déduit
(préférence : déduit).

### 4.2 — Structure de conquête (§8) — *conception complète, prototype partiel*
Le joueur reprend des territoires ; à chaque étape il destitue le seigneur en
place en le battant à ce jeu. Justification : dans ce monde, tout se décide par
la capacité à déduire une règle — c'est ainsi qu'on juge qui est apte à régner.

**Cycle : étudier, puis affronter.** L'étude est une **seconde boucle
d'induction** à l'échelle du run.

> **La ligne à ne jamais franchir :** l'étude révèle la **distribution** dont la
> loi est tirée, jamais l'**instance**. Savoir qu'un roi affectionne les
> conditionnelles ne dit pas laquelle il a choisie. C'est ce qui la rend
> compatible avec la règle d'or du §8, et c'est la phrase qui permettra de
> refuser un jour « un objet qui révèle une clause ».

**Fait :** le roi comme profil de génération.
**À faire :** la phase d'étude, les PV, la carte.

### 4.3 — Duel en points de vie — *décidé, non construit*
Les points marqués infligent des dégâts ; les points perdus en encaissent.
Renverse le §16.4, qui avait écarté l'adversaire abstrait.

> **Facture chiffrée.** Un pari vaut `±longueur²`, la main fait 12 cartes, la
> déclaration double la mise : **une manche vaut de −288 à +288**. En dégâts
> bruts, soit une manche ratée tue, soit les PV sont si gros que les manches
> prudentes ne pèsent rien. Il faudra **plafonner la mise** ou **découpler
> dégâts et score**. C'est le vrai travail de cette idée.

**Question qui décide de tout : qu'est-ce que le roi *fait* ?** Un ennemi qui
n'a que des PV est un score cible déguisé. Leviers déjà disponibles : biaiser la
loi (fait), rogner le budget (fait), raccourcir les manches (fait). À ajouter :
interdire une dimension, imposer un format de pari.

### 4.4 — Succès masqués — *piste*
Chaque forme découverte débloque un succès ; la liste grandit, le joueur peut
viser le 100 %.

> **Contrainte impérative :** un succès non obtenu doit rester **entièrement
> masqué, nom compris**. Un succès qui annonce « découvrez la conditionnelle »
> réintroduit le spoiler que le 4.1 supprime.

---

## 5. QUESTIONS OUVERTES

| # | question | état |
|---|---|---|
| §16.3 | Condition de défaite d'un run | **ouverte** — aucune pour l'instant, le run va au bout |
| §16.6 | Nom du jeu | ouverte |
| §16.7 | Le joueur est-il assez maître de sa partie ? | **ouverte** — beaucoup améliorée par la sonde, pas close |
| §8 | Objets de run | ouverte — règle d'or : confort ou risque, **jamais** d'information |
| — | Escalade en cours de run | le budget qui s'épuise en tient lieu ; suffisant ? |

Pistes notées pour §16.7, non tranchées :
- **plusieurs lois en parallèle, un seul budget** — chaque tour devient une
  allocation ; spécialiste ou généraliste devient une identité de partie ;
- **paquets pré-construits à caractère** — attention, la composition **libre**
  est un piège : un paquet dégénéré rend une dimension intestable, donc le
  générateur ne peut plus produire de loi qui la touche, donc le joueur connaît
  la famille avant de commencer. **Bornée uniquement** ;
- **engagement partiel façon Obra Dinn** — inscrire des faits isolés au fil de
  l'enquête, confirmés par lots.

---

## 6. DETTES CONNUES

| dette | gravité | note |
|---|---|---|
| Le générateur peut habiller une règle d'un seul attribut en deux briques (« jamais noir » ET « jamais ♥ » = « uniquement du carreau ») | faible | inélégant, plus injuste depuis le jugement extensionnel |
| Le contrôle « rivales fragiles » n'a **jamais** tiré | faible | conservé, coût nul, pourrait servir si la grammaire grossit |
| Le raffinement « quasi-jumelles » des paires de contraste n'est pas implémenté | faible | seule la moitié bon marché (témoins pivots) existe |
| L'énumération des paires est réservée à l'analyse hors ligne | assumée | coût C(187,2) ; le contrôle de redondance, lui, reste actif en jeu |
| Le plancher du solveur est estimé sur 3 000 rivales échantillonnées | assumée | ordre de grandeur fiable, pas une borne exacte |
| Le joueur-sonde Monte-Carlo complet n'est pas construit | assumée | son seuil ne se règle que contre des parties réelles |

---

## 7. MESURES À FAIRE

1. **Le Sénéchal contre l'Archiviste.** Affronter le second se sent-il
   différent du premier ? *Si oui, toute la structure de conquête tient et le
   reste n'est qu'habillage. Si non, aucun pixel art ne la sauvera.*
2. **Le budget de 120 est-il le bon ?** Le bon réglage est celui où on lâche
   une ou deux manches **en le décidant**, pas en le subissant. Trop de budget
   restant à la fin → trop large ; à sec à la manche 4 → trop serré.
3. ~~Retester l'affichage en colonnes~~ — **fait, concluant.**
4. ~~A-t-il redemandé à jouer ?~~ — **fait : il a relancé de lui-même, en
   stream, sur son PC.** Signal décisif du §13, positif.
5. **À partir de quelle manche la reconnaissance remplace la découverte ?**
   Réponse partielle de l'auteur : pas encore arrivé, en connaissant pourtant
   toute la grammaire.

---

## 8. RÈGLES QU'ON S'EST DONNÉES

Invariants payés cher. Les rompre casserait quelque chose d'invisible.

1. **La loi est validée contre le paquet et le départ réels**, et rendue avec
   eux. Valider contre un paquet abstrait puis tirer indépendamment détruit la
   garantie de déductibilité.
2. **Le vrai danger de testabilité est le masquage, pas la fréquence.** Une
   clause parfaitement fréquente peut être parfaitement indéductible.
3. **Le tirage fait partie de ce qui doit être juste**, pas seulement la règle.
4. **Jamais d'information non payée.** Ne pas signaler qu'une carte refusée
   passerait maintenant ; ne pas montrer l'attribut fautif ; ne pas exposer le
   constructeur de déclaration pendant l'enquête.
5. **Étude = distribution, jamais instance.**
6. **Un adversaire est un jeu de paramètres, jamais un personnage.** Vingt rois
   écrits à la main, c'est le catalogue que le §3 pilier 2 refuse.
7. **Élargir la grammaire par famille, jamais par attribut.** Un attribut
   n'ajoute que 4 formes ; une famille multiplie.
8. **Tirer équiprobablement par famille**, jamais par clause.
9. **Ne pas importer les solutions de Balatro**, seulement son format. La
   structure d'antes est conçue pour un jeu d'optimisation à information connue.
10. **Ne jamais sauter une étape du §14.**
11. **Toute modification du tarif ou de la grammaire repasse au solveur** avant
    d'être jouée.
