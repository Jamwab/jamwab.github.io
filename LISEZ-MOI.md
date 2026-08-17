# Site de James Wabenga Yango

Site académique bilingue, en un seul fichier HTML autonome, avec mise à jour
automatique des publications et des comptes de citations.

## Ce que contient l'archive

| Fichier | Rôle |
|---|---|
| `index.html` | Le site complet. Photo, styles et scripts sont à l'intérieur. |
| `publications.json` | Vos travaux et vos comptes de citations. Le seul fichier que la synchronisation modifie. |
| `portrait.jpg` | Votre photo en fichier séparé, au cas où vous voudriez la remplacer. |
| `sync_publications.py` | Va chercher les nouveaux articles et les citations sur SSRN, Crossref, Semantic Scholar et Google Scholar. |
| `sync-publications.yml` | Fait tourner le script chaque nuit sur GitHub. À placer dans `.github/workflows/`. |
| `population-rdc-territoires-villes.xlsx` | La série de population des 145 territoires et des villes, feuille par feuille. |
| `data/prix-brut.json` | Les cours des matières premières, sous leur forme brute. C'est le seul fichier que l'actualisation nocturne des prix modifie. |
| `data/macro-rdc.json` | Les séries longues de la RD Congo : croissance, inflation, indice de volume, projections et tableau des agrégats annuels. |
| `data/bcc.json` | Les relevés de la Banque Centrale du Congo : taux directeur, réserves internationales, position monétaire. |
| `data/series.json` | Copie du registre des vingt et une séries, telle qu'elle est embarquée dans la page. |
| `data/csv/` | Une copie plate de chaque série, pour qui préfère le fichier au bouton. |
| `tools/mklib.py` | La bibliothèque de tracé : échelles, grilles, légendes, bilinguisme. |
| `tools/mkprix.py` | Le générateur des figures de prix, du tableau de bord et du bandeau d'indicateurs. |
| `tools/mkmacro.py` | Le générateur des figures macroéconomiques, du tableau des agrégats et des relevés de la banque centrale. |
| `tools/refresh_data.py` | Va chercher la feuille mensuelle et les séries longues de la Banque mondiale, puis réécrit les zones balisées de la page. |
| `tools/gg_prepare.py` | Met les séries en forme tabulaire pour R : un fichier CSV par planche et un plan de tracé. |
| `tools/figures.R` | Trace les planches avec ggplot2 et les écrit en SVG, une version anglaise et une version française. |
| `tools/gg_inject.py` | Vérifie chaque SVG, le dépose dans `figures/` et met à jour la zone balisée de la page. |
| `figures/` | Les planches ggplot2 publiées, en SVG. Le dossier se crée tout seul à la première exécution. |
| `refresh-data.yml` | Fait tourner l'actualisation de toutes les données et le tracé des planches chaque nuit. À placer dans `.github/workflows/`. |
| `tools/veille.py` | Relève la liste des bulletins d'épidémie que l'Organisation mondiale de la santé publie sur la RD Congo, et l'écrit dans `data/veille.json`. Ne touche à aucun tableau. |
| `data/veille.json` | Le dernier relevé des bulletins parus. Le filet du volet « Santé et épidémies » quand l'appel direct échoue. |
| `veille.yml` | Fait tourner la veille toutes les six heures. À placer dans `.github/workflows/`. |
| `tools/cv_maj.py` | Compare le curriculum vitae au relevé des travaux que le dépôt connaît, et dit ce qui manque de part et d'autre. Ne réécrit pas le CV ; pose seulement le mois du pied de page, sur demande. |
| `cv.yml` | Fait tourner ce contrôle chaque lundi et à chaque modification du CV. À placer dans `.github/workflows/`. |

---

## 1. Mettre le site en ligne sur GitHub

### Créer le dépôt

1. Allez sur https://github.com/Jamwab et cliquez sur **Repositories**, puis **New**.
2. Nommez le dépôt **`jamwab.github.io`**. Ce nom exact est important : il donne
   l'adresse `https://jamwab.github.io`, sans sous-dossier.
3. Cochez **Public**, puis **Create repository**.

### Déposer les fichiers

1. Sur la page du dépôt vide, cliquez **uploading an existing file**.
2. Ouvrez le dossier `sit_james_github` du Bureau et glissez son contenu dans
   la page. GitHub n'accepte qu'une centaine de fichiers à la fois : faites-le
   en deux fois.
   - **Premier dépôt** : les fichiers de la racine, puis les dossiers `cv`,
     `data` et `tools`.
   - **Second dépôt** : le dossier `figures` seul, qui en porte soixante-dix.
3. En bas, cliquez **Commit changes** après chaque dépôt.

Les fichiers `.yml` de la racine sont des copies de lecture : les vrais vont
dans `.github/workflows/`, comme il est dit plus bas.

### Activer la publication

1. Onglet **Settings**, puis **Pages** dans la colonne de gauche.
2. Sous *Source*, choisissez **Deploy from a branch**.
3. Branche **main**, dossier **/ (root)**, puis **Save**.
4. Attendez deux à trois minutes. Votre site est en ligne sur
   **https://jamwab.github.io**

### Mettre à jour le site

Le dépôt est déjà en ligne, et le dossier du Bureau porte une version plus
récente. Trois choses à savoir avant de commencer.

Un dépôt ne se met pas à jour tout seul : il faut redéposer les fichiers qui
ont changé. Un fichier redéposé sous le même nom remplace l'ancien, sans
question. Un fichier absent du dépôt s'ajoute. En revanche, **rien ne
s'efface** : un fichier que le site n'utilise plus reste dans le dépôt tant
que vous ne le supprimez pas à la main.

La marche à suivre :

1. Allez sur `https://github.com/Jamwab/jamwab.github.io`.
2. Cliquez **Add file**, puis **Upload files**.
3. Glissez le contenu du dossier `sit_james_github` du Bureau, en deux fois
   comme ci-dessus : la racine et les dossiers `cv`, `data`, `tools` d'abord,
   le dossier `figures` ensuite.
4. Sous *Commit changes*, écrivez ce que vous avez changé — « planches des
   cinq filtres », par exemple. Ce mot vous servira le jour où vous voudrez
   revenir en arrière.
5. Cliquez **Commit changes**.
6. Attendez deux à trois minutes. L'onglet **Actions** montre une pastille
   orange pendant la publication, verte quand elle est faite.
7. Ouvrez `https://jamwab.github.io` et forcez le rechargement :
   **Cmd + Maj + R**. Sans cela, le navigateur vous montre la page qu'il garde
   en mémoire, et vous croiriez que rien n'a bougé.

Si un fichier n'a pas à rester — une figure que la page ne cite plus, un outil
retiré —, ouvrez-le dans le dépôt, cliquez la corbeille en haut à droite, puis
**Commit changes**. C'est la seule façon de retirer quelque chose par le
navigateur.

Enfin, ne modifiez jamais `index.html` directement sur GitHub. Le fichier est
écrit par les outils du dossier ; une correction faite en ligne serait effacée
au dépôt suivant.

### Installer la mise à jour automatique

1. Dans le dépôt, cliquez **Add file**, puis **Create new file**.
2. Dans le champ du nom, tapez exactement : `.github/workflows/sync-publications.yml`
   Les barres obliques créent les dossiers toutes seules.
3. Collez le contenu de `sync-publications.yml`, puis **Commit changes**.
4. Onglet **Actions**, choisissez **Sync publications**, puis **Run workflow**
   pour un premier essai.

Ensuite, déposer un article sur SSRN suffit : il apparaîtra sur le site le
lendemain matin, avec ses citations.

### Votre ORCID

L'identifiant `0000-0002-4675-4583` est déjà inscrit dans le script et dans les
liens du site. Pour qu'il devienne votre source principale, allez sur orcid.org,
section **Works**, puis **Add works**, **Search & link**, et lancez Crossref puis
DataCite. Activez ensuite l'autorisation de mise à jour automatique. Tout travail
ajouté à votre ORCID apparaîtra sur le site le lendemain.

### Facultatif, les citations Google Scholar

Google Scholar n'a pas d'API et bloque les robots. Pour lire vos comptes Scholar
automatiquement, il faut passer par SerpApi, qui paie Google pour un accès légitime.

1. Créez un compte gratuit sur https://serpapi.com et copiez votre clé.
2. Dans le dépôt : **Settings**, **Secrets and variables**, **Actions**,
   **New repository secret**.
3. Nom : `SERPAPI_KEY`. Valeur : votre clé. Puis **Add secret**.

Sans cette clé, le script utilise Crossref et Semantic Scholar, et vos comptes
actuels restent en place. Un compte n'est jamais revu à la baisse.

---

## 2. Que faire du site Google Sites

Google Sites n'accepte pas de HTML complet : il n'est pas possible d'y installer
ce site tel quel. Trois options, de la meilleure à la plus rapide.

### Option A, recommandée : rediriger vers le nouveau site

Gardez l'adresse Google le temps que les liens existants basculent, et
transformez-la en panneau indicateur.

1. Ouvrez https://sites.google.com/view/jameswabengayango et cliquez **Modifier**.
2. Supprimez le contenu de la page d'accueil.
3. Insérez un texte court, par exemple : « Ce site a déménagé. Nouvelle adresse :
   jamwab.github.io », et faites du lien un bouton bien visible.
4. Cliquez **Publier**.

### Option B : intégrer le nouveau site dans l'ancien

1. Dans l'éditeur, menu **Insertion**, puis **Intégrer**.
2. Onglet **Par URL**, collez `https://jamwab.github.io`, puis **Insérer**.
3. Étirez le cadre sur toute la largeur et toute la hauteur de la page.
4. **Publier**.

Le site s'affiche alors dans un cadre, à l'intérieur de la page Google. Cela
fonctionne, mais le défilement se fait dans le cadre et la colonne latérale fixe
se comporte moins bien. À réserver au dépannage.

### Option C : supprimer le site Google

Une fois GitHub Pages en ligne et l'adresse diffusée, l'ancien site n'a plus
d'utilité. Dans Google Sites, menu à trois points à côté du site, puis
**Supprimer**. Faites-le seulement après avoir mis à jour votre CV, votre profil
RePEc, votre page CIRANO et votre signature de courriel.

---

## 3. Une adresse à votre nom, facultatif

Un domaine comme `jameswabengayango.com` coûte une quinzaine de dollars par an et
fait meilleure impression qu'une adresse en `.github.io` sur un dossier de
candidature.

1. Achetez le domaine chez un registraire, par exemple Namecheap ou Google Domains.
2. Chez le registraire, créez quatre enregistrements `A` pointant vers
   `185.199.108.153`, `185.199.109.153`, `185.199.110.153`, `185.199.111.153`.
3. Dans GitHub : **Settings**, **Pages**, champ **Custom domain**, entrez votre
   domaine, puis cochez **Enforce HTTPS**.

---

## 4. Modifier le site à la main

Tout le texte est dans `index.html`. Chaque passage existe en deux versions :

```html
<span class="l-en">English text</span><span class="l-fr" lang="fr">Texte français</span>
```

Modifiez les deux, sinon une seule langue changera.

La mise en page comprend deux parties. À gauche, un panneau bleu fixe, large de
330 pixels, qui ne défile pas : il porte votre photo en médaillon (balise `<img class="side-mark">`, dont le diamètre se règle par la règle `.side-mark`), le nom, la ligne de
champs, le menu vertical, les fonctions, les coordonnées et le sélecteur de
langue. Cherchez `<aside class="sidebar">`. Sa largeur se règle par la variable
`--side` dans le bloc `:root`.

À droite, la colonne de lecture, `<div class="page">`. Elle s'ouvre sur un
bandeau, puis le nom centré, la ligne de champs, un filet et la photo ronde,
puis les sections.

Chaque rubrique du menu est une page à part entière. Les cinq sections
`<section class="view">` — présentation, recherche, enseignement, données
congolaises, contact — portent chacune un identifiant, et un petit routeur
n'affiche que celle dont l'adresse porte l'ancre. Cliquer sur *Research* ouvre
la page de recherche seule, remonte en haut et met à jour le titre de l'onglet ;
les boutons Précédent et Suivant du navigateur fonctionnent, et une adresse du
type `…/index.html#teaching` s'ouvre directement sur la bonne page. Deux
garde-fous : sans JavaScript le site redevient une page unique qui se déroule,
et à l'impression toutes les rubriques sont rendues visibles, de sorte qu'un
lecteur qui imprime obtient le document complet. Pour ajouter une rubrique,
ajoutez une `<section id="…" class="view">` dans `<main>` et le lien
correspondant dans `<nav class="sidenav">` ; le routeur la reprend sans autre
réglage.

Le bandeau est un nuage de mots vectoriel écrit directement dans le fichier,
cherchez `class="banner"`. Il contient deux groupes, `<g class="l-en">` et
`<g class="l-fr">`, un par langue, et suit donc le sélecteur EN/FR. Chaque terme
est une balise `<text>` avec ses coordonnées, sa taille et son opacité : plus le
terme est central dans vos travaux, plus il est grand et foncé. Pour en ajouter
un, copiez une ligne `<text>` et placez-la dans une zone libre, dans les deux
groupes. Pour remplacer tout le bandeau par une photographie, mettez une balise
`<img>` à la place du bloc `<svg>` ; gardez une image large et peu haute,
environ 1800 sur 300 pixels.

Le menu est dans `<nav class="sidenav">` ; chaque lien doit pointer vers
l'identifiant d'une section existante. La section en cours de lecture est
signalée par un tiret doré.

En dessous de 1040 pixels de large, le panneau cesse d'être une colonne et
devient une bande d'en-tête, le menu passe à l'horizontale et les encarts
Fonctions et Contact sont masqués. Ce seuil est dans la règle
`@media (max-width:1040px)`.

La section R.D. Congo, `<section id="drc">`, se place juste avant Contact et
réunit trois blocs. D'abord trois figures de séries longues, écrites en SVG
dans le fichier : cherchez `<div class="figs">`. Chacune couvre 1990-2026 :
la croissance du PIB réel en pourcentage, l'inflation des prix à la
consommation sur une échelle logarithmique, puis le PIB réel en indice
2015 = 100. Chaque figure est une `<figure class="fig">` avec un titre
`figcaption.fig-t`, un dessin de 720 sur 250 unités et une note de source
`p.fig-s`, le tout en deux langues.

Dans chaque dessin, la ligne bleue porte les années observées et chaque année
est marquée par un `<circle>`. Le dernier segment, de 2025 à 2026, est doré et
en pointillé : c'est la projection. Elle est rangée dans un `<g class="v-proj">`
et reste cachée tant que le lecteur n'a pas cliqué *Avec projections 2026*. Le
basculement se fait par la classe `is-proj` sur `<div id="macro">`, si bien que
la section reste lisible même sans JavaScript. Les valeurs annotées existent en
deux versions, `l-en` avec le point décimal et `l-fr` avec la virgule.

La zone de tracé va de 56 à 704 en largeur et de 20 à 194 en hauteur ; les
années sont écrites à `y="214"`. Ce dessin n'est pas à écrire à la main : il est
produit par `tools/mkmacro.py` à partir de `data/macro-rdc.json`, et réécrit
chaque nuit entre les balises `<!-- MACRO:FIGS:START -->` et
`<!-- MACRO:FIGS:END -->`. Les valeurs réalisées viennent de la Banque mondiale ;
la projection dorée se règle dans la rubrique `proj` du fichier.

Après ces trois figures vient un second bloc, sous le titre « Banque Centrale
du Congo, relevés courants », qui porte deux figures construites sur les
publications de la BCC : le taux directeur, tracé en escalier, et les réserves
internationales en milliards de dollars, relevés hebdomadaires. La géométrie est
la même que celle des figures longues. Ces deux dessins viennent de
`data/bcc.json` : pour enregistrer une décision de taux ou un nouveau relevé de
réserves, ajoutez un couple date-valeur dans la rubrique correspondante, et le
dessin se refait seul.

Vient ensuite le tableau `table.macro-tab`, une ligne par indicateur, avec la
source en dernière colonne, puis le bloc `dl.macro-now` qui rassemble les
relevés récents de la Banque Centrale du Congo. Le premier se règle dans la
rubrique `tableau` de `data/macro-rdc.json`, le second dans la rubrique `kpi` de
`data/bcc.json`. Vous n'avez donc jamais à corriger une coordonnée : changez le
chiffre à sa source, et la figure, le tableau et le fichier téléchargeable
suivent ensemble. La marche à suivre complète est en section 7.

La section se termine par le volet démographique, sous le titre « Population par
territoire et par ville ». Il s'ouvre sur un bloc `dl.macro-now` qui donne les
grands agrégats — population totale, part rurale et part urbaine, territoire
médian, extrêmes — puis sur trois figures : la population des vingt-six provinces
en barres horizontales, les quinze entités les plus peuplées, où le bronze
distingue les villes du bleu des territoires, et la distribution des territoires
par classe de taille. Les barres horizontales suivent une géométrie simple : le
nom se termine à `x="130"`, la barre part de `x="138"` et la plus longue s'arrête
à `x="626"`, chaque ligne occupant vingt et un pixels. Pour ajouter une entité,
insérez un `<text>`, un `<rect>` et son étiquette chiffrée, puis augmentez la
hauteur du `viewBox` d'autant.

Le tableau intégral des cent quatre-vingt-neuf entités est replié dans un
`<details class="pop-details">` : le lecteur ne le déroule que s'il en a besoin,
et l'en-tête reste collé en haut pendant le défilement. Un tiret y signale une
entité urbaine dont la population est comptée dans l'entité voisine à la source,
afin qu'aucun habitant ne soit compté deux fois. Les chiffres proviennent des
statistiques infranationales publiées par OCHA et l'Institut national de la
statistique sur le Humanitarian Data Exchange ; comme aucun recensement général
n'a eu lieu depuis 1984, ce sont des projections démographiques. Le classeur
`population-rdc-territoires-villes.xlsx` livré à côté du site contient la même
série, feuille par feuille, avec sa mention de copyright.

Chaque publication porte une vignette à gauche, un carré de 96 pixels qui réunit
trois éléments : un emblème dessiné en SVG, le nom de la revue ou de l'archive en
deux langues, et l'année. L'emblème est un tracé au trait, en `currentColor`, si
bien qu'il prend la couleur donnée par la règle `.thumb .mark`. Cinq emblèmes
existent : un épi de blé pour l'*International Journal of Food and Agricultural
Economics*, une feuille réglée pour SSRN, trois nœuds reliés pour ResearchGate,
un tiroir d'archives pour MPRA, une feuille nue pour les documents de travail.

Ces vignettes existent en deux endroits, qu'il faut tenir accordés. Les
publications déjà écrites dans la page portent leur vignette en clair dans
`index.html` : cherchez `<div class="thumb"`. Les publications ajoutées par la
synchronisation sont fabriquées par le script, dans la fonction `buildPaper`. Le
choix de l'emblème se fait dans `venueKey`, qui lit le nom de la revue ; les
tracés sont dans le tableau `MARKS` et les noms bilingues dans `VENUE_NAMES`.
Pour ajouter une revue, complétez ces trois éléments.

Le nom de la revue est coupé à trois lignes par la règle `-webkit-line-clamp`.
Un titre plus long qu'*International Journal of Food and Agricultural Economics*
demande donc une abréviation, à écrire directement dans `VENUE_NAMES`.

Si vous obtenez un jour les fichiers officiels des logos, vous pouvez remplacer
le bloc `<svg class="mark">` par une balise `<img src="logos/ssrn.svg"
class="mark" alt="">` ; gardez une image carrée d'environ 26 pixels et déposez
les fichiers dans un dossier `logos/` du dépôt.

Les couleurs sont toutes déclarées dans le bloc `:root` en haut du fichier.
L'accent est le bleu d'Oxford (Pantone 282) sur un fond parchemin.

Pour changer la couleur de fond, cherchez `--paper:` :

- `#F4F2EA` parchemin chaud, réglage actuel
- `#FCFBF7` blanc chaud, plus lumineux
- `#F5F7FA` blanc bleuté, plus froid

Si vous éclaircissez `--paper`, éclaircissez aussi `--line` et `--line-soft`
pour que les filets restent visibles. Les contrastes actuels respectent tous
le niveau WCAG AA, vérifiez-les à nouveau après toute modification.

Pour ajouter un compte de citations à la main, ouvrez `publications.json` et
complétez la section `citations`, en associant le nombre au lien exact utilisé
sur la page.

---

## 5. Les réseaux d'échange et les prix des matières premières

La section « Données macroéconomiques de la R.D. Congo » se poursuit par deux
blocs d'analyse, chacun bâti sur le même principe : des figures, un tableau, un
commentaire macroéconomique, puis des mesures de politique économique numérotées.

Le premier, « Réseaux d'échange et propagation des chocs », repose sur la
matrice des comptes nationaux exploitée dans *Paper_Network_DRC*, quarante-sept
branches d'activité, et sur les statistiques de commerce extérieur de la Banque
Centrale du Congo. Il porte quatre figures : les débouchés à l'exportation, où
l'on distingue le pays de transit du pays de destination finale ; l'origine des
importations par produit, avec le taux de dépendance θ de chaque poste ;
l'influence des branches dans le réseau intersectoriel, mesurée par le vecteur
propre de la matrice des parts et par la distance moyenne à la demande finale ;
enfin la concentration, avec l'indice de Herfindahl, le nombre effectif de
branches et les parts cumulées. Le tableau des chocs simulés en fin de bloc donne
l'effet sur le PIB de dix scénarios, de la baisse du cours du cuivre et du cobalt
à la rupture du corridor sud.

Le second, « Cours des matières premières », suit les productions congolaises et
les principales importations. Six figures : cuivre, étain et zinc en indice
2023 = 100 avec le niveau en dollars annoté en fin de courbe ; le cobalt, ses
observations datées et les deux mesures de politique commerciale qui l'ont
gouverné depuis février 2025 ; l'or et le Brent sur deux axes ; les cinq
productions agricoles d'exportation en indice ; le coltan et le lithium en deux
panneaux ; enfin les indices d'ensemble des métaux et des métaux précieux. Le
tableau de bord qui suit donne, pour quinze produits, la moyenne 2025, le dernier
relevé, la variation et la date.

Les chiffres cités dans le texte d'analyse relèvent du jugement de l'auteur :
l'actualisation automatique décrite plus bas ne les touche jamais.

---

## 6. Télécharger une série

Sous chaque figure et chaque tableau, trois boutons, **CSV**, **XLSX** et
**TEX**, téléchargent la série exacte qui a servi à la dessiner. Le fichier
porte le nom de la série dans la langue affichée au moment du clic.

Le bouton **TEX** produit un document LaTeX complet et compilable, pas un
fragment : préambule, `booktabs` pour les filets, `longtable` au-delà de
trente-cinq lignes, légende et étiquette `\label{tab:…}` prêtes à être citées.
Les colonnes numériques sont alignées à droite et leurs milliers séparés par
une espace fine `\,` ; la ponctuation typographique — tirets cadratins,
apostrophes courbes, signes moins — est convertie en commandes que LaTeX
comprend. Quand un tableau est trop large pour la page, chaque colonne devient
un `p{}` proportionnel et le texte se replie au lieu de déborder. Un tableau
long est signalé par un commentaire en tête du fichier : compilez-le deux fois,
ou avec `latexmk`, pour que `longtable` cale ses colonnes.

La ligne de source est reprise sous le tableau, en petit corps. Le préambule
contient une ligne `\usepackage[french]{babel}` mise en commentaire : décommentez-la
si `babel-french` est installé sur votre machine, pour obtenir les espaces
insécables françaises devant les deux-points et les points-virgules.

### L'historique complet des cours

Sous le tableau de bord des prix, un encadré séparé propose l'historique
intégral du *Pink Sheet* : **toutes** les valeurs mensuelles publiées depuis
1960, les moyennes trimestrielles et les moyennes annuelles, chacune en série
téléchargeable à part. Rien n'est tronqué. Ces trois séries — `prix-hist-mensuel`,
`prix-hist-trimestriel`, `prix-hist-annuel` — n'apparaissent qu'après la première
exécution de l'actualisation nocturne, puisque c'est elle qui télécharge le
classeur mensuel. Tant que ce classeur n'a pas été lu, l'encadré reste absent et
la page demeure cohérente.

De la même façon, le tableau des agrégats macroéconomiques ne s'arrête plus à une
année plancher : il retient toutes les années que la Banque mondiale documente
simultanément pour la croissance, l'inflation et le niveau du PIB.

Rien n'est appelé à l'extérieur. Les vingt et une séries sont écrites dans la
page elle-même, dans une balise `<script type="application/json"
id="series-data">`, et le classeur Excel est fabriqué dans le navigateur : le
script assemble à la main les six pièces du format Office puis les enferme dans
une archive ZIP dont il calcule lui-même les sommes de contrôle. Aucune
bibliothèque externe, donc rien à installer et rien qui puisse tomber en panne.

Pour ajouter une série, complétez le JSON avec une entrée de la forme
`{"name_en": …, "name_fr": …, "source": …, "cols": [...], "rows": [[...]]}` puis
posez sous la figure :

```html
<div class="dlbar" data-series="ma-cle">
  <button type="button" class="dl" data-fmt="csv">CSV</button>
  <button type="button" class="dl" data-fmt="xlsx">XLSX</button>
</div>
```

---

## 7. L'actualisation nocturne des données

Toutes les données affichées sur la page se redessinent seules. Une action
GitHub s'exécute chaque nuit, vers trois heures du matin, et reconstruit la
section congolaise à partir des sources. Vous n'avez rien à faire : si une
figure change, c'est que la donnée a changé.

Le travail se fait en trois blocs indépendants.

**Le premier bloc, les prix des matières premières.** Il télécharge la feuille
mensuelle de la Banque mondiale, le *Pink Sheet*, en tire les moyennes
annuelles, les deux derniers trimestres complets et les trois derniers mois,
puis réécrit les six figures de prix, le tableau de bord, le bandeau
d'indicateurs et la date de dernier relevé.

**Le second bloc, la macroéconomie congolaise.** Il interroge l'interface
programmable de la Banque mondiale — croissance du PIB réel, inflation des prix
à la consommation, PIB en volume — pour la RD Congo, reconstruit l'indice de
volume sur la base 2015 = 100, puis redessine les trois figures longues, le
tableau des agrégats annuels, les deux figures de la banque centrale et la
position monétaire.

**Le troisième bloc, les planches ggplot2.** Il installe R et quatre paquets,
met les séries fraîchement écrites en forme tabulaire, trace les planches en
SVG dans les deux langues et les publie dans `figures/`. Il ajoute deux à trois
minutes à l'exécution ; la bibliothèque R est mise en cache d'une nuit sur
l'autre. Le détail est en section 10.

Les trois blocs sont étanches : si le *Pink Sheet* est déplacé, les figures
macroéconomiques se mettent quand même à jour ; si R tombe en panne, la page
garde ses planches de la veille et le reste s'actualise normalement. Le journal
de l'action indique à chaque exécution ce qui a été refait et ce qui a été laissé
en l'état.

### L'installer

1. Déposez dans le dépôt les dossiers `data/` et `tools/` tels qu'ils sont
   livrés.
2. **Add file**, **Create new file**, nom exact
   `.github/workflows/refresh-data.yml`, collez le contenu du fichier
   `refresh-data.yml`, puis **Commit changes**.
3. Onglet **Actions**, choisissez l'action d'actualisation, puis
   **Run workflow** pour un premier essai.

### Ce qu'elle modifie, et ce qu'elle ne modifie pas

Le script ne remplace que le contenu situé entre des balises de commentaire :

    <!-- PRIX:KPI:START -->    ...  <!-- PRIX:KPI:END -->
    <!-- PRIX:FIGS:START -->   ...  <!-- PRIX:FIGS:END -->
    <!-- PRIX:TAB:START -->    ...  <!-- PRIX:TAB:END -->
    <!-- PRIX:STAMP:START -->  ...  <!-- PRIX:STAMP:END -->
    <!-- MACRO:FIGS:START -->  ...  <!-- MACRO:FIGS:END -->
    <!-- MACRO:TAB:START -->   ...  <!-- MACRO:TAB:END -->
    <!-- BCC:FIGS:START -->    ...  <!-- BCC:FIGS:END -->
    <!-- BCC:KPI:START -->     ...  <!-- BCC:KPI:END -->
    <!-- GG:FIGS:START -->     ...  <!-- GG:FIGS:END -->
    <!-- SERIES:START -->      ...  <!-- SERIES:END -->

Ne les supprimez pas. Tout le reste — le texte d'analyse, les mesures de
politique économique, les figures de réseau, la population — reste sous votre
main : ces passages relèvent du jugement, pas d'une mise à jour mécanique.

### Les données qui n'ont pas de source automatique

Trois ensembles ne sont publiés par personne sous une forme lisible par une
machine. Ils vivent donc dans des fichiers du dépôt, et il suffit d'y changer un
chiffre pour que la page entière se redessine à la prochaine exécution.

`data/bcc.json` porte les relevés de la Banque Centrale du Congo. La rubrique
`taux_directeur` est une liste de couples date-valeur, une ligne par décision du
comité de politique monétaire ; la rubrique `reserves` fait de même pour les
relevés hebdomadaires des réserves internationales ; la rubrique `kpi` contient
les dix chiffres du bloc « position monétaire », chacun dans les deux langues.
Ajouter une décision de taux revient à ajouter une ligne :

```json
["2026-10-15", 12.0]
```

`data/macro-rdc.json` porte la projection de l'année en cours, dans la rubrique
`proj`, et le tableau des agrégats annuels, dans la rubrique `tableau`. Les
séries réalisées, elles, sont écrasées chaque nuit par la Banque mondiale : ne
les corrigez pas à la main, la correction serait perdue. La valeur `null` dans
une ligne du tableau produit un tiret cadratin sur la page.

`data/prix-brut.json`, section `hors_pink_sheet`, porte les cours que la Banque
mondiale ne publie pas : l'hydroxyde de cobalt, le tantalite, le carbonate de
lithium. Chaque relevé est accompagné de sa date.

### Essayer sans rien écrire

```bash
pip install openpyxl
python3 tools/refresh_data.py --dry-run
```

Et pour ne redessiner que les figures, sans toucher au réseau :

```bash
python3 tools/mkmacro.py
python3 tools/mkprix.py
```

Si la Banque mondiale déplace son classeur, relevez la nouvelle adresse sur
https://www.worldbank.org/en/research/commodity-markets et ajoutez-la en tête de
la liste `CANDIDATS`, dans `tools/refresh_data.py`.

---

## 8. Le compteur de visites

Le compteur est **GoatCounter** : gratuit pour un site personnel, sans cookie,
sans profilage, donc sans bandeau de consentement à afficher.

1. Créez un compte sur https://www.goatcounter.com et choisissez un code de
   site, par exemple `wabenga`. Votre tableau de bord sera alors à l'adresse
   `https://wabenga.goatcounter.com`.
2. Dans les réglages du site GoatCounter, section *Site settings*, cochez
   **Allow adding visitor counts to your website**. Sans cela, le nombre affiché
   dans la colonne de gauche resterait vide, même si le comptage fonctionne.
3. Ouvrez `index.html`, cherchez `var CODE = '';` tout en bas du fichier, et
   écrivez votre code entre les guillemets : `var CODE = 'wabenga';`.

Tant que cette ligne reste vide, aucun script extérieur n'est chargé et l'encart
reste masqué : le site fonctionne exactement comme avant. Une fois le code
renseigné, un bloc **Visites** apparaît dans la colonne de gauche, sous Contact,
avec le total depuis la mise en ligne et le nombre des trente derniers jours. Il
ne s'affiche que si la lecture réussit, de sorte qu'une panne du service ne
laisse jamais de case vide sur la page, et il ne s'imprime pas.

Le détail — pages consultées, provenance, navigateurs — se lit sur votre tableau
de bord GoatCounter, pas sur le site.

---

## 9. Vues et téléchargements par article

À côté du badge de citations, chaque article peut afficher son audience :
le nombre de consultations et de téléchargements, plateforme par plateforme,
suivi de la date du relevé. Six emplacements sont prévus : RePEc, SSRN,
ResearchGate, Google Scholar, Academia.edu et une case « Autres ».

La distinction est de méthode. **RePEc et SSRN publient leurs compteurs sous une
forme lisible par une machine** : le script `sync_publications.py` va les
chercher chaque nuit et met la page à jour tout seul. **ResearchGate, Google
Scholar et Academia.edu ne le font pas** — leurs pages sont protégées contre les
robots, et les relever automatiquement violerait leurs conditions d'usage. Ces
trois-là se saisissent donc à la main, et la page indique honnêtement la
plateforme et la date de lecture.

Pour saisir un chiffre, ouvrez `publications.json`, rubrique `access_manual`.
Elle est déjà préparée : une entrée par article, repérée par le lien exact utilisé
sur la page, et quatre cases par article.

```json
"access_manual": {
  "https://papers.ssrn.com/sol3/papers.cfm?abstract_id=5316606": {
    "researchgate": {"views": 412, "dl": 87, "on": "2026-08-15"},
    "scholar":      {"views": null, "dl": null, "on": null},
    "academia":     {"views": null, "dl": null, "on": null},
    "autres":       {"views": null, "dl": null, "on": null}
  }
}
```

Une case laissée à `null` n'affiche rien : mieux vaut un badge absent qu'un
chiffre inventé. La date `on` est celle de votre lecture, au format
année-mois-jour. Les chiffres saisis à la main portent un liseré en pointillé,
pour qu'on les distingue d'un coup d'œil de ceux qui viennent du réseau.

La rubrique voisine, `access`, est celle qu'écrit le script : n'y touchez pas,
elle est réécrite chaque nuit.

---

## 10. Les planches ggplot2 et les tableaux LaTeX

En bas de la section congolaise, sous le titre « Planches statistiques », une
série de figures est tracée par **R et ggplot2**, à partir des séries mêmes
qu'exportent les boutons de téléchargement. Sept planches sont prévues :
croissance du PIB en colonnes de part et d'autre de zéro, inflation en échelle
logarithmique, PIB en indice, taux directeur en escalier, indices de prix
mensuels, quinze entités les plus peuplées et quinze branches les plus
influentes, enfin la courbe de concentration de l'influence.

La chaîne compte quatre maillons, exécutés dans cet ordre par l'action nocturne :

1. `tools/gg_prepare.py` lit `data/series.json` et `data/prix-brut.json`, écrit
   un CSV par planche dans `build/gg/` et un `plan.json` qui décrit le type de
   graphique, les intitulés dans les deux langues, la source et le format.
2. `tools/figures.R` lit ce plan et trace chaque planche deux fois, en anglais
   et en français, au format SVG. Chaque tracé est isolé : une série malformée
   fait tomber sa planche, jamais les autres.
3. `tools/gg_inject.py` vérifie chaque SVG — document bien formé, `viewBox`
   présent, aucune dimension figée —, l'écrit dans `figures/` et met à jour la
   zone `<!-- GG:FIGS:START --> … <!-- GG:FIGS:END -->` de la page.
4. L'action publie le tout.

Trois garde-fous. Si R n'est pas disponible, si un paquet manque ou si le tracé
échoue, l'étape est signalée dans le journal et **la page conserve les figures de
la veille**. Si aucune planche valable n'est produite, `index.html` n'est pas
touché du tout. Enfin, aucune planche n'est publiée sans que les deux langues
existent, pour que le sélecteur EN/FR ne laisse jamais un cadre vide.

Les planches sont des fichiers séparés plutôt que du code inséré dans la page :
le lecteur peut les télécharger — deux liens **SVG EN** et **SVG FR** sous chaque
figure —, le navigateur les met en cache, et le dépôt ne reçoit chaque nuit que
les images réellement modifiées.

### L'essayer sur votre machine

```bash
python3 tools/gg_prepare.py
Rscript tools/figures.R
python3 tools/gg_inject.py
```

Il vous faut R et quatre paquets, que l'action installe elle-même sur le
serveur :

```r
install.packages(c("ggplot2", "svglite", "jsonlite", "scales"))
```

### Modifier une planche

Tout se règle dans `tools/gg_prepare.py`. Chaque figure y est une fonction courte
qui renvoie une fiche : la clé, le type de graphique, les intitulés, la source,
les couleurs et le format en pouces. Pour ajouter une planche, écrivez une
fonction du même modèle et inscrivez-la dans la liste `fabriques` de `main()`.
Pour en retirer une, effacez-la de cette liste : `gg_inject.py` supprime alors le
fichier SVG devenu inutile.

Les sept types de tracé disponibles — `colonnes_zero`, `ligne_log`, `aire`,
`barres_h`, `courbe_cumul`, `marches`, `lignes_multi` — sont définis dans
`tools/figures.R`, chacun en une dizaine de lignes. Les couleurs, la
typographie et les filets sont réunis dans la fonction `theme_wabenga()`, en
tête du fichier : c'est le seul endroit à modifier pour changer l'allure de
toutes les planches à la fois.

Une planche ne suffit pas toujours : les figures écrites à la main en SVG, plus
haut dans la page, restent en place. Les deux séries de figures cohabitent, et
elles racontent les mêmes chiffres.

---

## 11. La veille des bulletins d'épidémie

Le volet « Santé et épidémies » est le seul de la page dont les chiffres
vieillissent en quelques jours : l'Organisation mondiale de la santé publie un
bulletin tous les dix à quinze jours, et chacun peut doubler un décompte.

Chaque tableau porte déjà, sous lui, le bulletin d'où il sort et la date d'arrêt
de ses chiffres : le lecteur sait donc toujours de quand date ce qu'il lit. Ce
qu'il ne peut pas savoir, c'est si l'Organisation a publié depuis. C'est à cela
que sert la veille.

### Ce qu'elle fait

Au chargement, la page demande à l'interface publique de l'Organisation la liste
des bulletins concernant la RD Congo, prend le plus récent, et le compare à celui
que ses propres tableaux citent. Si les deux concordent, rien ne paraît. Si le
bulletin paru est postérieur, une ligne s'ouvre en tête du volet, le nomme, le
date et renvoie à lui.

Le bulletin de référence n'est écrit nulle part à la main : `tools/rdc_themes.py`
le relève dans les sources des tableaux eux-mêmes. Le jour où vous ferez passer
un tableau au bulletin suivant, la veille suivra sans que vous ayez à y penser.

### Ce qu'elle ne fait pas

Elle ne recopie aucun chiffre et ne modifie aucun tableau. Relever qu'un bulletin
est paru est mécanique ; en tirer des chiffres ne l'est pas — il faut lire le
texte, distinguer un cas confirmé d'un cas suspect, repérer une réconciliation de
données. La page annonce donc la parution et renvoie à la source ; la mise à jour
des tableaux reste un acte de lecture, le vôtre.

Elle ne dit jamais non plus que la page est à jour. Si l'appel échoue et que le
fichier de secours manque, la ligne reste fermée : mieux vaut ne rien dire que
rassurer à tort.

### L'installer

1. Déposez `tools/veille.py` dans le dépôt, avec les autres outils.
2. **Add file**, **Create new file**, nom exact `.github/workflows/veille.yml`,
   collez le contenu du fichier `veille.yml`, puis **Commit changes**.
3. Onglet **Actions**, choisissez **Veille des bulletins d'épidémie**, puis
   **Run workflow** pour un premier essai.

L'action tourne toutes les six heures et ne sert que de filet : elle écrit
`data/veille.json`, que la page lit si l'appel direct échoue. Un échec de
l'action n'a aucun effet sur le site — le fichier garde son dernier relevé et
l'action se contente d'un avertissement dans son journal.

---

## 12. Le contrôle du curriculum vitae

Le relevé de vos travaux vit à trois endroits qui ne se parlent pas :
`publications.json`, que le dépôt refait chaque nuit ; la page, qui porte en
outre quelques travaux anciens que la synchronisation ne relève pas ; et le
curriculum vitae, composé à la main en LaTeX, dans les deux langues.

Les trois divergent lentement, et rien ne le signale — un CV à jour et un CV
périmé se ressemblent trait pour trait. C'est à cela que sert `cv_maj.py`.

### Ce qu'il fait

    python3 tools/cv_maj.py

Il rassemble ce que le dépôt sait de vos travaux, lit la rubrique des
publications des deux fichiers LaTeX, et imprime deux listes : les travaux
parus qui manquent au CV, et les entrées du CV que le dépôt ignore. La seconde
n'est pas une faute — un chapitre, un rapport de consultation n'ont pas à
figurer ailleurs —, mais elle mérite d'être vue une fois par an.

Il prévient aussi quand les deux langues portent un nombre différent d'entrées.
C'est la faute que rien d'autre ne rattrape, parce que chaque fichier pris seul
a l'air complet.

L'option `--orcid` interroge ORCID en plus ; si l'appel ne passe pas, le rapport
se fait sans lui et le dit.

### Ce qu'il ne fait pas

Il ne réécrit pas le CV. Un CV n'est pas un tableau : l'ordre des rubriques, la
façon de nommer un coauteur, la décision de retenir un travail ou de le laisser
de côté sont des actes d'écriture. Un script qui les prendrait à sa charge vous
ferait signer un document que vous n'auriez pas écrit. Le script relève l'écart
et s'arrête là ; la notice, c'est vous qui l'écrivez, dans les deux fichiers.

La seule chose qu'il écrit est le mois du pied de page :

    python3 tools/cv_maj.py --dater

À lancer après avoir modifié le CV, juste avant de recompiler — jamais tout
seul, sinon le document se vieillirait tout seul chaque mois sans qu'une ligne
ait bougé.

### L'installer

1. Déposez `tools/cv_maj.py` dans le dépôt, avec les autres outils.
2. **Add file**, **Create new file**, nom exact `.github/workflows/cv.yml`,
   collez le contenu du fichier `cv.yml`, puis **Commit changes**.

L'action tourne chaque lundi et à chaque modification d'un fichier du CV. Elle
ne pousse jamais rien : quand le CV est en retard, elle dépose un avertissement
dans son journal, et vous laisse écrire la notice.
