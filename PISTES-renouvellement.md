# Pistes — le renouvellement du gameplay

> Notes de session, **non tranchées**. Rien ici n'est décidé.
> À lire avec `cahier-des-charges-jeu-induction.md` (le pourquoi) et `ETAT.md` (l'état).
> Répond à la question ouverte **§16.7 — le joueur est-il assez maître de sa partie ?**
> Ce fichier meurt quand ses idées sont soit intégrées au cahier des charges, soit rejetées par écrit.

---

## 1. Le diagnostic

**Rien ne persiste d'une manche à l'autre sauf un score.** La loi change, le paquet est réinitialisé, les sondes coûtent pareil, la main fait toujours 12. Le contenu se renouvelle ; le joueur, lui, est identique à la manche 6 et à la manche 1.

Balatro fait l'inverse : la loi (les mains de poker) ne change **jamais**, mais le deck et les jokers font qu'on ne joue pas de la même façon à l'ante 8 qu'à l'ante 1. Nous avons construit le jeu miroir — **contenu infini, joueur figé**. C'est le joueur figé qui use la rejouabilité, pas le contenu fini.

Le mot manquant : **build**.

### Les quatre emplacements d'une manche

| emplacement | état actuel | varie ? |
|---|---|---|
| ce qui est caché | une loi sur les attributs | contenu seulement |
| **comment on observe** | trois sondes, tarif fixe | **jamais** |
| **ce qu'on fait du savoir** | la plus longue suite valide | **jamais** |
| **la contrainte** | un budget d'essais | **jamais** |

Les 17 578 lois remplissent la première ligne. Les trois autres sont vides — c'est là qu'est le gisement.

### Filtre à appliquer à toute idée

> **Est-ce que ça change ce à quoi le joueur pense, ou seulement ce avec quoi il y pense ?**

Corollaire douloureux, à assumer : **la conquête, les rois, la carte, les territoires sont un habillage.** Un habillage ne répare jamais un verbe. Ils peuvent rester, mais ils ne répondent pas au §16.7 et ne doivent pas être comptés comme y répondant.

---

## 2. Le principe directeur — le plus important du fichier

> **Un build ne s'achète pas contre l'inconnu, il s'achète contre une hypothèse.**

Objection qui l'a fait naître : *quel intérêt de choisir un paquet riche en dos avant de savoir quelle loi on affronte ?* Aucun — c'est un pari aveugle, pas un choix. Balatro ne demande jamais de choisir son build au menu principal : il se construit **en réaction** à ce qu'on a déjà vu.

Reformulé : tout ce que le joueur achète doit être un pari sur **sa lecture** — de la loi, du roi, de la manche. Le jeu n'a alors plus qu'un seul verbe, et il est partout : *je crois avoir compris, et j'engage quelque chose là-dessus*. La phase B fait déjà exactement ça ; il s'agit de l'étendre au reste.

**Test à passer avant d'accepter toute idée de ce fichier :** au moment où le joueur paie, dispose-t-il d'une hypothèse à engager ? Si non, l'idée est mal placée dans le temps — la déplacer, pas la jeter.

---

## 3. Le paquet comme instrument (piste principale)

### Le mécanisme

Les sondes tirent dans le paquet. Donc **la composition du paquet détermine quelles expériences sont possibles et à quel prix**. Un paquet très varié sur le dos rend les jumelles-dos précises et bon marché ; un paquet appauvri sur le rang rend les lois de rang quasi indéductibles.

Modifier son paquet = choisir sa **spécialité d'enquêteur**. Le dilemme est natif : renforcer un axe affaiblit les autres. Le spécialiste des dos est aveugle sur les enseignes.

Avantage sur des jokers génériques : c'est **spécifique à l'induction**, donc non importable de Balatro, donc non concerné par le §11.

### Le piège du §16.7, requalifié

Le §16.7 notait qu'un paquet dégénéré rend une dimension intestable, donc le générateur ne peut plus produire de loi qui la touche, donc le joueur connaît la famille à l'avance.

**Ce n'est pas un bug, c'est le prix du build** : en se spécialisant, on apprend quelque chose sur ce que le roi pourra poser. À **borner**, pas à interdire — sinon ça devient un exploit. La composition libre reste refusée.

### Trois placements possibles dans le temps (le vrai sujet)

1. **En cours de manche, sur soupçon.** Trois sondes plus tard, on pense que la loi touche au dos ; on paie pour enrichir le paquet en dos. Observations plus tranchantes — mais si on s'est trompé, budget brûlé et autres axes appauvris. *C'est le placement le plus conforme au §2 : un pari sur sa propre lecture, au milieu de l'enquête.*
2. **Avant le duel, en connaissant le roi.** Un roi est déjà un profil de familles (fait). Si son style est partiellement visible avant, préparer son paquet devient de la préparation et non de la loterie. **Donne enfin une dépense au savoir de la phase d'étude (§8.B) : on n'étudie pas pour savoir, on étudie pour choisir son équipement.**
3. **Persistant sur tout le run.** Une manche est trop courte pour porter un build. Si les modifications restent : manche 1 générique et prudente, manches 2–6 typées. Le pari devient *je paie maintenant, ça me sert quatre fois — si j'ai bien lu*. Deux joueurs contre le même roi arrivent différemment équipés à la manche 5.

Les trois sont compatibles. Le 3 est probablement la fondation, le 1 le plus intéressant à jouer.

---

## 4. Les axes de build (grammaire, pas catalogue)

Même méthode que pour les lois : ne pas écrire cent jokers, écrire **trois ou quatre axes qui se combinent**. Quatre axes à trois niveaux = des dizaines de joueurs distincts sans contenu écrit.

| axe | ce qu'il modifie |
|---|---|
| **composition du paquet** | sur quelle dimension je suis riche, sur laquelle je suis pauvre |
| **instruments** | chaque sonde améliorable : moins chère, plus précise, un usage gratuit par manche |
| **tarif** | l'échange permanent budget ↔ précision |
| **format du pari** | main plus large mais suite plafonnée, ou l'inverse |

**Critère de réussite :** à la manche 5, deux joueurs face à la **même loi** ne l'abordent pas pareil — l'un fait trois jumelles chirurgicales, l'autre douze sondes larges.

### Pourquoi de simples objets ne suffiraient pas

Un joker de Balatro s'accroche à un choix riche (quelles 5 cartes parmi 8, que défausser, dans quel ordre, sur quatre mains). Notre verbe n'a que deux boutons : quelle sonde, quelle suite. **L'espace d'action est trop mince pour porter un build** — d'où l'impression, juste, qu'on n'aura jamais cent objets pertinents. Il faut épaissir l'espace d'action *avant* d'y accrocher des objets.

---

## 5. Le trou structurel

**Il ne se passe rien entre deux manches.** Or c'est là que le build se choisit dans tous les roguelikes. Il faut un **moment de décision inter-manche**.

> **Garde-fou §11.** Ce qu'on importe, ce n'est pas la boutique de Balatro, c'est le fait qu'un roguelike a des points de bifurcation. La version LEX doit être payée dans **notre** monnaie : **des essais, jamais de l'argent.** On sacrifie du budget d'enquête pour améliorer sa méthode.
>
> Pilier 1 préservé : savoir coûte quelque chose, **y compris savoir mieux**.

---

## 6. Les instruments — varier le canal d'observation

Un instrument ne donne **jamais d'information** (règle d'or du §8 intacte) ; il change la **forme de l'information achetable**.

| instrument | effet | pourquoi c'est plus qu'un bonus |
|---|---|---|
| **lentille large** | poser 5 cartes d'un coup, le jeu dit seulement *combien* ont été acceptées | le retour agrégé rend la déduction **statistique** au lieu de logique — autre activité mentale |
| **scalpel** | jumelle moins chère, mais nombre de dimensions limité sur tout le run | force à choisir où être chirurgical |
| **mémoire** | remettre la ligne dans un état antérieur, donc retester un contexte passé | ouvre des expériences aujourd'hui impossibles |
| **brouillon** | voir le verdict avant de payer, une fois par manche | change la gestion du risque, pas l'information |

Un run « lentille » et un run « scalpel » ne se jouent pas pareil.

---

## 7. Varier la nature du secret

Aujourd'hui le secret est toujours *laquelle des 17 578 lois*. Varier le **type** de secret, pas son contenu. Un roi = un type de secret devient une différenciation **mécanique**, ce que le §8.D cherchait.

- **La loi bascule** en cours de manche, à un moment inconnu → la tâche n'est plus d'identifier mais de **détecter une rupture**.
- **La loi porte sur la ligne entière** et non sur les cartes adjacentes (« jamais plus de trois rouges au total ») → raisonnement **global** au lieu de local.

> **Écarté en discussion — « le roi ment une fois sur dix ».** Ajoute de la difficulté sans changer la manière de jouer. Ne passe pas le filtre du §1.

---

## 8. Le run comme induction de second niveau

Ne pas **vendre** l'étude de l'adversaire : la rendre **déductible**. Les six manches d'un roi sont tirées d'une distribution cachée, au joueur de la deviner en jouant.

Effet : la manche 1 se joue à l'aveugle et large, la manche 5 avec des a priori forts et des sondes ciblées. **Le même verbe change de sens selon l'avancement du run** — c'est précisément ce qui manque.

Respecte le §8.B en mieux : distribution jamais instance, et **gratuite plutôt qu'achetée**.

---

## 9. Le renversement — je fais la loi

Certaines manches, le joueur **compose la loi** et le solveur doit la déduire. Score d'autant plus élevé qu'elle lui résiste — mais elle doit passer le validateur (permissive, testable, sans impasse). Fabriquer une loi *juste et difficile* est un problème entièrement différent de la déduire.

**Pour :** le code existe déjà presque en entier (constructeur par menus, validateur, solveur = l'adversaire). C'est le rôle du donneur d'Eleusis, dont le score dépend d'une règle ni trop facile ni trop dure — retour à la source. Thématiquement parfait : on ne prend pas seulement le territoire du roi, on prend sa place, donc on légifère.

**Contre, et c'est l'objection retenue :** ça ajoute **un second jeu à côté du premier**. Ça ne rend pas la déduction elle-même différente d'une manche à l'autre. Ne répond donc pas au §16.7.

**Statut : gardée, mais comme respiration ponctuelle — jamais comme réponse au problème de fond.** Bonne candidate pour les manches de contestation de territoire.

---

## 10. Ordre de test proposé

Ne rien construire en entier. La question à trancher est *« est-ce que changer de build change la sensation ? »*, et elle se teste petit.

1. **Trois compositions de paquet fixes** — équilibrée, riche en dos, riche en rang. Un run chacune, rien d'autre de changé.
   - Trois runs qui se sentent différents → le paquet est le bon axe, et on sait où mettre les six prochains mois.
   - Trois runs identiques → le paquet n'est pas l'axe, chercher ailleurs. **Deux jours pour le savoir.**
2. Si oui : ajouter le **moment de décision inter-manche** (payé en essais) et rendre le build **persistant sur le run**.
3. Puis un second axe (instruments), pour vérifier que les axes se **combinent** au lieu de s'additionner.
4. La nature du secret (§7) et l'induction de second niveau (§8) viennent après — elles supposent la structure de run stabilisée.

---

## 11. Rappels de discipline

- Ces pistes sont **postérieures** aux mesures en attente de `ETAT.md §7`. Elles ne les remplacent pas. En particulier : **le testeur externe a-t-il redemandé à jouer ?** — le §13 juge tout le reste spéculatif tant que c'est vide.
- `ETAT.md §2` : la marge du run est annoncée à **1,6×** alors que 120 sur ~114 fait **1,05×**. Le 1,6 vient de la manche isolée (30/19). À corriger **avant** de mesurer si le budget de 120 est bon, sinon on conclura que la structure de run est mauvaise alors que c'est le réglage.
- Toute idée retenue ici repasse par le **solveur** avant d'être jouée (règle 11 de `ETAT.md §8`).
- Rien de tout ceci ne justifie de toucher à l'étape 4 (§14).
