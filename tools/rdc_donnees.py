#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""Les tableaux thematiques de la page « Donnees macroeconomiques de la RD Congo ».

Ce module ne contient que des donnees : chaque tableau reprend des chiffres
publies, dates et attribues. Aucune valeur n'est estimee ici. Lorsqu'une
serie n'existe pas dans une publication accessible, la case porte un tiret
et la note du tableau le dit.

Le rendu et l'injection dans index.html sont faits par rdc_themes.py.

Conventions d'ecriture d'une fiche :

  name_en / name_fr   la legende du tableau, dans les deux langues
  source              la ligne de source, en francais
  note_en / note_fr   la note de lecture, dans les deux langues
  cols                les en-tetes, chacun sous la forme [anglais, francais]
  chiffres            le nombre de decimales, colonne par colonne, en
                      commencant par la premiere colonne de donnees
  rows                les lignes ; la premiere case est l'intitule, sous la
                      forme [anglais, francais] ou sous forme de chaine

Bibliotheque standard seulement.
"""

# ----------------------------------------------------------------------
# Les sources, citees une fois et reprises par cle
# ----------------------------------------------------------------------
FMI = ("FMI, République démocratique du Congo : deuxième revue des accords "
       "FEC et FRD, rapport pays nº 26/2, janvier 2026.")
BM_MPO = ("Banque mondiale, Macro Poverty Outlook — République "
          "démocratique du Congo, avril 2026.")
WITS = ("Banque mondiale, World Integrated Trade Solution, d’après "
        "Comtrade, exercice 2023.")
ITIE = ("ITIE-RDC, rapport final 2023 (signé le 31 décembre 2025) et rapport "
        "de cadrage 2024.")
BM_PAUVRETE = ("Banque mondiale, Poverty and Equity Brief — Democratic "
               "Republic of Congo, octobre 2025.")
PNUD = "PNUD, Rapport sur le développement humain 2025, annexe statistique."
UIS = ("Institut de statistique de l’UNESCO, profil pays ODD 4, "
       "République démocratique du Congo, juin 2025.")
WDI = ("Banque mondiale, World Development Indicators, fiche pays consultée "
       "en août 2026.")
IPC = ("IPC, République démocratique du Congo, mise à jour de la projection "
       "d’insécurité alimentaire aiguë janvier-juin 2026, 12 mai 2026.")
OIM = ("OIM, Matrice de suivi des déplacements, aperçu des déplacements "
       "internes 2026 ; OCHA, relevés 2021-2026.")
HCR = "HCR, Global Appeal 2026, chapitre RD Congo, janvier 2026."
BCNUDH = ("Bureau conjoint des Nations unies aux droits de l’homme, "
          "rapport annuel 2025, présenté à Kinshasa le 12 mars 2026.")
OMS = ("OMS, bulletins d’épidémie 2025-DON589 et 2026-DON603 ; rapport "
       "de situation mpox nº 66, 31 mai 2026.")
OMS_DON614 = ("OMS, bulletin d’épidémie 2026-DON614, « Maladie à virus "
              "Bundibugyo — République démocratique du Congo », 1er août "
              "2026, révisé le 3 août 2026 ; source des données, Centre des "
              "opérations d’urgences de santé publique (COUSP-RDC), "
              "chiffres arrêtés au 30 juillet 2026.")
OMS_DON615 = ("OMS, bulletin d’épidémie 2026-DON615, « Maladie à virus "
              "Bundibugyo — République démocratique du Congo », 14 août "
              "2026 ; chiffres arrêtés au 12 août 2026, sauf le personnel "
              "de santé, arrêté au 9 août, et le suivi de la France, arrêté "
              "au 14 août.")
OMS_DONS = ("OMS, les dix bulletins d’épidémie de la série, 2026-DON602 du "
            "16 mai 2026 à 2026-DON615 du 14 août 2026. Chaque ligne est "
            "citée du bulletin qui la porte ; aucune n’est calculée à "
            "partir d’une autre.")
CDC_EBOLA = ("Centers for Disease Control and Prevention, « History of Ebola "
             "Outbreaks », page revue le 29 mai 2026, pour les seize "
             "premières épidémies ; OMS, bulletin d’épidémie 2026-DON615 du "
             "14 août 2026, pour la dix-septième.")
OMS_SURV = ("OMS, « Multi-country outbreak of mpox, external situation report "
            "nº 68 », 31 juillet 2026 ; « Multi-country outbreak of cholera, "
            "epidemiological update nº 38 », 30 juin 2026 ; déclaration de la "
            "quarante-quatrième réunion du comité d’urgence du Règlement "
            "sanitaire international sur la poliomyélite, 4 mars 2026.")
WPP = ("Nations unies, Département des affaires économiques et sociales, "
       "World Population Prospects, révision 2024.")
TI = "Transparency International, indice de perception de la corruption 2025."
TI_SERIE = ("Transparency International, indice de perception de la "
            "corruption, éditions 2019 à 2025 ; l’édition 2025 a paru le "
            "10 février 2026.")
WDI_VA = ("Banque mondiale, World Development Indicators, tableau 4.2 "
          "« Structure of value added », consulté le 16 août 2026.")
WDI_ENVOIS = ("Banque mondiale, World Development Indicators, séries "
              "BX.TRF.PWKR.CD.DT et BX.TRF.PWKR.DT.GD.ZS, d’après les "
              "statistiques de balance des paiements du FMI ; millésime de "
              "la base du 13 juillet 2026.")
USGS = ("United States Geological Survey, Mineral Commodity Summaries 2026, "
        "notices cuivre et cobalt, février 2026.")
OIT = ("Organisation internationale du travail, estimations modélisées "
       "ILOEST, reprises par la Banque mondiale, World Development "
       "Indicators, tableaux 2.3 et 2.4.")
DESA_MIG = ("Nations unies, Département des affaires économiques et "
            "sociales, International Migrant Stock 2024 "
            "(POP/DB/MIG/Stock/Rev.2024), publié en janvier 2025.")
HCR_ODP = ("HCR, portail des données opérationnelles, situation RD Congo, "
           "relevés du 31 mars et du 30 avril 2026.")
DIAL = ("Kankwanda, Makabu, Nilsson, Roubaud, Torelli et Wachsberger, "
        "« Le marché du travail en République démocratique du Congo en "
        "2012 : principaux résultats de la phase 1 de l’enquête 1-2-3 », "
        "DIAL-IRD, document de travail DT/2014-23, 2014, d’après "
        "l’enquête 1-2-3 de l’Institut national de la statistique.")
CPIA = ("Banque mondiale, Country Policy and Institutional Assessment, "
        "fiche République démocratique du Congo, exercice 2024.")
IIAG = ("Fondation Mo Ibrahim, indice Ibrahim de la gouvernance africaine, "
        "édition 2024, fiche RD Congo ; année de référence 2023.")
OBS = ("International Budget Partnership, Open Budget Survey 2025, fiche "
       "République démocratique du Congo ; situation arrêtée au "
       "31 décembre 2024.")
ITIE_VAL = ("Conseil d’administration de l’ITIE, décision 2022-50/BM-54 "
            "du 13 octobre 2022.")
BM_INGA = ("Banque mondiale, Inga 3 Development Program, Project "
           "Information Document, rapport nº PIDIA01263, 8 avril 2025.")
BM_ROUTES = ("Banque mondiale, DRC Transport and Connectivity Support "
             "Project SOP 2, Project Information Document, rapport "
             "nº PIDDC00863, 6 août 2024.")
BM_EAU = ("Banque mondiale, Scaling-Up Water Supply and Sanitation Access "
          "in Kinshasa, Project Information Document, rapport "
          "nº PIDDC01437, 18 décembre 2025, d’après OMS et UNICEF, "
          "Joint Monitoring Programme, édition 2025.")
WDI_INFRA = ("Banque mondiale, World Development Indicators, tableaux 3.7 "
             "« Electricity production, sources, and access » et 5.11 "
             "« The information society », consultés le 16 août 2026.")
AUTEUR_SERIES = ("Calculs de l’auteur sur les séries de croissance du PIB "
                 "réel et d’inflation publiées sur cette page (FMI, "
                 "Banque mondiale, BCC, BAD).")


# ----------------------------------------------------------------------
# 1. Comptes nationaux
# ----------------------------------------------------------------------
NAT_PIB = {
    "name_en": "Gross domestic product, levels and uses",
    "name_fr": "Produit intérieur brut, niveaux et emplois",
    "source": FMI + " " + BM_MPO,
    "cols": [["Year", "Année"],
             ["GDP, CDF bn", "PIB, milliards CDF"],
             ["GDP, $bn (IMF)", "PIB, milliards USD (FMI)"],
             ["GDP, $bn (World Bank)", "PIB, milliards USD (Banque mondiale)"],
             ["GDP per capita, $", "PIB par habitant, USD"],
             ["Total investment, % of GDP", "Investissement total, % du PIB"],
             ["Gross national saving, % of GDP",
              "Épargne nationale brute, % du PIB"]],
    "chiffres": [0, 1, 1, 1, 1, 1],
    "rows": [
        ["2023", 170711, 69.8, "—", "—", 15.5, 10.3],
        ["2024", 216585, 76.7, 77.7, 710.9, 13.8, 9.7],
        ["2025", 246893, 91.8, 87.6, 776.7, 13.3, 9.7],
        ["2026", 269331, 109.2, "—", "—", 13.9, 11.7],
    ],
    "note_en": ("2025 and 2026 are Fund projections, not outturns. The Fund "
                "and the Bank do not use the same nominal denominator: the "
                "gap reaches four billion dollars in 2025, so every ratio on "
                "this page names the denominator it rests on. The Fund "
                "publishes total investment and national saving but not "
                "gross fixed capital formation or household consumption "
                "separately, which is why those two lines are absent."),
    "note_fr": ("2025 et 2026 sont des projections du Fonds, non des "
                "réalisations. Le Fonds et la Banque ne retiennent pas le "
                "même dénominateur nominal : l’écart atteint quatre "
                "milliards de dollars en 2025, de sorte que chaque ratio de "
                "cette page nomme le dénominateur sur lequel il repose. Le "
                "Fonds publie l’investissement total et l’épargne "
                "nationale, mais ni la formation brute de capital fixe ni la "
                "consommation des ménages prises séparément : ces deux "
                "lignes manquent donc."),
}

NAT_COMPTES = {
    "name_en": "National accounts: what is published and what is not",
    "name_fr": "Comptes nationaux : ce qui est publié et ce qui ne l’est pas",
    "source": ("Institut national de la statistique (insrdc.cd, consulté le "
               "15 août 2026), Banque centrale du Congo, FMI, travaux de "
               "l’auteur."),
    "cols": [["Account", "Compte"],
             ["Status", "État"],
             ["Where", "Où"]],
    "chiffres": [],
    "rows": [
        [["Integrated economic accounts", "Comptes économiques intégrés"],
         ["Not published online", "Non publiés en ligne"],
         ["INS, site under construction", "INS, site en construction"]],
        [["Supply and use table",
          "Tableau des ressources et des emplois"],
         ["Not published online", "Non publié en ligne"],
         ["INS, site under construction", "INS, site en construction"]],
        [["National accounts, summary note",
          "Comptes nationaux, note de synthèse"],
         ["Referenced, file unreachable", "Référencée, fichier inaccessible"],
         ["Banque centrale du Congo", "Banque centrale du Congo"]],
        [["Social accounting matrix, 47 branches, 2018",
          "Matrice de comptabilité sociale, 47 branches, 2018"],
         ["Author’s work, not yet published",
          "Travaux de l’auteur, non encore publiés"],
         ["Working paper in preparation",
          "Document de travail en préparation"]],
        [["Expenditure side of GDP", "PIB par la dépense"],
         ["Investment and saving only",
          "Investissement et épargne seulement"],
         ["IMF country report 26/2", "FMI, rapport pays 26/2"]],
        [["Household consumption, share of GDP",
          "Consommation des ménages, part du PIB"],
         ["Not published", "Non publiée"],
         ["Growth rate only, World Bank",
          "Taux de croissance seulement, Banque mondiale"]],
        [["Gross fixed capital formation, share of GDP",
          "Formation brute de capital fixe, part du PIB"],
         ["Not published", "Non publiée"],
         ["Growth rate only, World Bank",
          "Taux de croissance seulement, Banque mondiale"]],
    ],
    "note_en": ("The DRC has produced a supply and use table and integrated "
                "economic accounts through the ERETES system, but neither is "
                "downloadable from a public source: the statistical "
                "institute’s portal announced its publication library as "
                "forthcoming when it was consulted in August 2026. The "
                "expenditure side is barely better served: the Fund "
                "publishes total investment and national saving, the Bank "
                "publishes growth rates for household consumption and for "
                "fixed capital formation, and nobody publishes either of "
                "those two as a share of output. This page therefore says "
                "nothing about the level of Congolese consumption, and the "
                "reason it says nothing is that no one has published it."),
    "note_fr": ("La RD Congo a produit un tableau des ressources et des "
                "emplois et des comptes économiques intégrés au moyen du "
                "système ERETES, mais ni l’un ni les autres ne sont "
                "téléchargeables depuis une source publique : le portail de "
                "l’institut national de la statistique annonçait sa "
                "bibliothèque de publications comme à venir lorsqu’il a "
                "été consulté en août 2026. Le PIB par la dépense n’est "
                "guère mieux servi : le Fonds publie l’investissement "
                "total et l’épargne nationale, la Banque publie des taux "
                "de croissance de la consommation des ménages et de la "
                "formation brute de capital fixe, et personne ne publie ni "
                "l’une ni l’autre en part de la production. Cette page ne "
                "dit donc rien du niveau de la consommation congolaise, et "
                "si elle n’en dit rien, c’est que personne ne l’a "
                "publié."),
}


# ----------------------------------------------------------------------
# 2. Comptes exterieurs
# ----------------------------------------------------------------------
EXT_PAIEMENTS = {
    "name_en": "Balance of payments, main balances",
    "name_fr": "Balance des paiements, principaux soldes",
    "source": FMI + " " + BM_MPO,
    "cols": [["Year", "Année"],
             ["Current account, % of GDP", "Solde courant, % du PIB"],
             ["Current account, $m", "Solde courant, millions USD"],
             ["Goods balance, $m", "Solde des biens, millions USD"],
             ["Services balance, $m", "Solde des services, millions USD"],
             ["Current account, % of GDP (World Bank)",
              "Solde courant, % du PIB (Banque mondiale)"]],
    "chiffres": [1, 0, 0, 0, 1],
    "rows": [
        ["2023", -5.3, -3678, 1601, -5094, -5.5],
        ["2024", -4.2, -3187, 4231, -5821, -4.2],
        ["2025", -3.6, -3340, 4562, -5906, -3.6],
        ["2026", -2.2, -2384, 6206, -6486, -3.4],
    ],
    "note_en": ("The external position of the DRC is the arithmetic of a "
                "mining surplus on goods offset by a structural deficit on "
                "services, freight and insurance above all, which the "
                "landlocked geography of the copper belt makes unavoidable. "
                "The two institutions agree on 2024 and 2025 and part "
                "company on 2026; both readings are given rather than "
                "reconciled."),
    "note_fr": ("La position extérieure de la RD Congo se ramène à "
                "l’arithmétique d’un excédent minier sur les biens "
                "compensé par un déficit structurel sur les services, fret "
                "et assurance au premier chef, que l’enclavement de la "
                "ceinture du cuivre rend inévitable. Les deux institutions "
                "s’accordent sur 2024 et 2025 et divergent sur 2026 ; "
                "les deux lectures sont données plutôt que réconciliées."),
}

EXT_COMMERCE = {
    "name_en": "Goods trade and the weight of the extractive sector",
    "name_fr": "Commerce de biens et poids du secteur extractif",
    "source": FMI,
    "cols": [["Year", "Année"],
             ["Exports, $m", "Exportations, millions USD"],
             ["of which extractive, $m",
              "dont secteur extractif, millions USD"],
             ["Extractive share, %", "Part extractive, %"],
             ["Imports, $m", "Importations, millions USD"],
             ["of which capital goods, $m",
              "dont biens d’équipement, millions USD"]],
    "chiffres": [0, 0, 1, 0, 0],
    "rows": [
        ["2023", 29601, 29427, 99.4, 28000, 12089],
        ["2024", 34927, 34357, 98.4, 30696, 12104],
        ["2025", 36406, 35717, 98.1, 31843, 13356],
        ["2026", 40153, 39460, 98.3, 33947, 14487],
    ],
    "note_en": ("The extractive share never falls below ninety-eight per "
                "cent over the period, which is the single fact from which "
                "most of the external vulnerability of the country follows. "
                "The share is computed from the two published Fund lines. "
                "The Fund projects exports to 2028, but not imports, so the "
                "table stops where both series stop."),
    "note_fr": ("La part extractive ne descend jamais sous quatre-vingt-dix-"
                "huit pour cent sur la période ; c’est le fait unique "
                "d’où découle l’essentiel de la vulnérabilité "
                "extérieure du pays. La part est calculée à partir des deux "
                "lignes publiées par le Fonds. Le Fonds projette les "
                "exportations jusqu’en 2028, mais non les importations : "
                "le tableau s’arrête là où les deux séries "
                "s’arrêtent."),
}

EXT_COMPOSITION = {
    "name_en": "Composition of external trade, 2023",
    "name_fr": "Composition du commerce extérieur, 2023",
    "source": WITS,
    "cols": [["Item", "Poste"],
             ["Flow", "Sens"],
             ["Value, $m", "Valeur, millions USD"],
             ["Share of flow, %", "Part du flux, %"]],
    "chiffres": [0, 1],
    "rows": [
        [["Refined copper cathodes", "Cathodes de cuivre affiné"],
         ["Export", "Exportation"], 16691.7, 60.2],
        [["Cobalt oxides and hydroxides", "Oxydes et hydroxydes de cobalt"],
         ["Export", "Exportation"], 4778.9, 17.2],
        [["Copper ores and concentrates", "Minerais et concentrés de cuivre"],
         ["Export", "Exportation"], 2158.1, 7.8],
        [["Unrefined copper", "Cuivre non affiné"],
         ["Export", "Exportation"], 1410.6, 5.1],
        [["Non-monetary gold", "Or non monétaire"],
         ["Export", "Exportation"], 1323.0, 4.8],
        [["Consumer goods", "Biens de consommation"],
         ["Import", "Importation"], 12413.0, 48.6],
        [["Capital goods", "Biens d’équipement"],
         ["Import", "Importation"], 6683.0, 26.2],
        [["Intermediate goods", "Biens intermédiaires"],
         ["Import", "Importation"], 3847.0, 15.1],
        [["Raw materials", "Matières premières"],
         ["Import", "Importation"], 2585.0, 10.1],
        [["of which refined petroleum oils",
          "dont huiles de pétrole raffinées"],
         ["Import", "Importation"], 9038.7, 35.4],
    ],
    "cle_tri": None,
    "note_en": ("Export shares are taken against declared exports of "
                "27,727 million dollars, import shares against declared "
                "imports of 25,529 million dollars, both free on board and "
                "cost-insurance-freight respectively as the source records "
                "them. Declared customs values fall short of the balance of "
                "payments figures in the table above, by about two and a "
                "half billion dollars on the export side: the gap is the "
                "usual one between mirror statistics and national accounts "
                "and should not be read as a measure of smuggling. Refined "
                "petroleum is listed separately because it crosses the "
                "consumer and intermediate categories in the source."),
    "note_fr": ("Les parts à l’exportation sont rapportées aux "
                "exportations déclarées, 27 727 millions de dollars, et les "
                "parts à l’importation aux importations déclarées, "
                "25 529 millions de dollars, respectivement franco à bord et "
                "coût-assurance-fret comme la source les enregistre. Les "
                "valeurs douanières déclarées restent en deçà des chiffres "
                "de balance des paiements du tableau précédent, de quelque "
                "deux milliards et demi de dollars à l’exportation : "
                "l’écart est celui, habituel, entre statistiques "
                "miroirs et comptes nationaux, et ne mesure pas la fraude. "
                "Le pétrole raffiné figure à part parce qu’il traverse "
                "les catégories consommation et intermédiaire dans la "
                "source."),
}

EXT_FINANCEMENT = {
    "name_en": "Financing of the external position and debt",
    "name_fr": "Financement de la position extérieure et dette",
    "source": FMI + " " + BM_MPO,
    "cols": [["Year", "Année"],
             ["Net FDI, $m", "IDE nets, millions USD"],
             ["External debt, % of GDP", "Dette extérieure, % du PIB"],
             ["Public debt, % of GDP (IMF)",
              "Dette publique, % du PIB (FMI)"],
             ["Public debt, % of GDP (World Bank)",
              "Dette publique, % du PIB (Banque mondiale)"],
             ["Reserves, $bn", "Réserves, milliards USD"]],
    "chiffres": [0, 1, 1, 1, 2],
    "rows": [
        ["2023", 1668, 17.2, 18.1, 27.4, 5.42],
        ["2024", 2915, 14.1, 20.9, 22.9, 6.73],
        ["2025", 2861, 11.8, 18.1, 21.1, 8.29],
        ["2026", 3401, 14.0, 20.5, 21.6, "—"],
    ],
    "note_en": ("The two debt ratios differ by up to nine points of GDP "
                "because they do not cover the same perimeter; the Fund "
                "figure excludes part of the certified domestic arrears, "
                "which stood at about five billion dollars in 2024 and 2025. "
                "Reserves reached 8.8 billion dollars at the end of March "
                "2026 and stood at 7.9 billion on 30 July 2026, that is "
                "three months of non-aid imports."),
    "note_fr": ("Les deux ratios de dette diffèrent de neuf points de PIB au "
                "plus parce qu’ils ne couvrent pas le même périmètre ; "
                "le chiffre du Fonds laisse de côté une partie des arriérés "
                "intérieurs certifiés, qui atteignaient environ cinq "
                "milliards de dollars en 2024 et en 2025. Les réserves ont "
                "culminé à 8,8 milliards de dollars fin mars 2026 et "
                "s’établissaient à 7,9 milliards le 30 juillet 2026, "
                "soit trois mois d’importations hors aide."),
}


# ----------------------------------------------------------------------
# 3. Finances publiques et monnaie
# ----------------------------------------------------------------------
FIN_PUBLIQUES = {
    "name_en": "Central government operations, per cent of GDP",
    "name_fr": "Opérations de l’État, en pourcentage du PIB",
    "source": (FMI + " Les années 2016 à 2018 proviennent du rapport pays "
               "nº 19/285 (article IV de 2019)."),
    "cols": [["Year", "Année"],
             ["Revenue and grants", "Recettes et dons"],
             ["Revenue excl. grants", "Recettes hors dons"],
             ["Expenditure", "Dépenses"],
             ["Current", "Courantes"],
             ["Capital", "Capital"],
             ["Overall balance", "Solde global"]],
    "chiffres": [1, 1, 1, 1, 1, 1],
    "rows": [
        ["2016", 14.0, 11.2, 14.5, "—", "—", -0.5],
        ["2017", 11.7, 9.8, 10.4, "—", "—", 1.4],
        ["2018", 11.6, 10.4, 11.2, "—", "—", 0.4],
        ["2023", 14.3, 13.2, 15.9, 9.4, 3.5, -1.6],
        ["2024", 14.8, 13.8, 16.4, 10.2, 3.8, -2.1],
        ["2025", 14.4, 13.5, 16.7, 9.8, 3.3, -2.4],
        ["2026", 14.8, 14.1, 17.1, 10.1, 3.9, -2.8],
    ],
    "note_en": ("The years 2019 to 2022 are missing because the Fund "
                "vintages consulted do not restate them on the revised "
                "national accounts; splicing them in from the old series "
                "would put non-comparable ratios side by side. Ratios up to "
                "2018 rest on the old GDP series and should be read as "
                "orders of magnitude. Expenditure carries an exceptional "
                "line, security and elections, which the Fund reports "
                "separately: 2.9 points of GDP in 2023, 2.3 in 2024 and 3.5 "
                "in 2025. Total revenue and expenditure in 2024 were 29,820 "
                "and 35,519 billion Congolese francs."),
    "note_fr": ("Les années 2019 à 2022 manquent parce que les millésimes du "
                "Fonds consultés ne les rétablissent pas sur les comptes "
                "nationaux révisés ; les reprendre de l’ancienne série "
                "reviendrait à juxtaposer des ratios non comparables. Les "
                "ratios antérieurs à 2019 reposent sur l’ancienne série "
                "de PIB et se lisent comme des ordres de grandeur. Les "
                "dépenses comportent une ligne exceptionnelle, sécurité et "
                "élections, que le Fonds isole : 2,9 points de PIB en 2023, "
                "2,3 en 2024 et 3,5 en 2025. Les recettes et les dépenses "
                "totales de 2024 se sont élevées à 29 820 et 35 519 "
                "milliards de francs congolais."),
}

FIN_EXTRACTIF = {
    "name_en": "Extractive revenue and the budget",
    "name_fr": "Recettes extractives et budget",
    "source": FMI + " " + ITIE,
    "cols": [["Year", "Année"],
             ["Extractive revenue, CDF bn",
              "Recettes extractives, milliards CDF"],
             ["Per cent of GDP", "En % du PIB"],
             ["Share of total revenue, %", "Part des recettes totales, %"],
             ["EITI extractive revenue, $bn",
              "Recettes extractives ITIE, milliards USD"]],
    "chiffres": [0, 1, 1, 3],
    "rows": [
        ["2023", 8836, 5.2, 39.1, 5.378],
        ["2024", 12325, 5.7, 41.3, 6.819],
        ["2025", 12600, 5.2, 37.7, "—"],
        ["2026", 13225, 4.9, 34.9, "—"],
    ],
    "note_en": ("The Fund’s extractive line covers mining and petroleum tax "
                "and non-tax revenue, royalties from the Sicomines "
                "agreement included. The share of total revenue is my own "
                "ratio of two published Fund lines, not a figure the Fund "
                "publishes. The EITI column is not the same aggregate: it "
                "reconciles company payments with government receipts, and "
                "mining alone accounted for 6.453 billion dollars of the "
                "2024 total. Two independent sources therefore say the same "
                "thing, that between a third and a half of what the "
                "Congolese state collects comes out of the ground."),
    "note_fr": ("La ligne extractive du Fonds couvre les recettes fiscales "
                "et non fiscales des mines et des hydrocarbures, redevances "
                "de la convention Sicomines comprises. La part des recettes "
                "totales est mon propre rapport de deux lignes publiées par "
                "le Fonds, non un chiffre que le Fonds publie. La colonne "
                "ITIE ne recouvre pas le même agrégat : elle rapproche les "
                "paiements des entreprises des encaissements de l’État, "
                "et les mines seules comptent pour 6,453 milliards de "
                "dollars du total de 2024. Deux sources indépendantes disent "
                "donc la même chose : entre le tiers et la moitié de ce que "
                "perçoit l’État congolais sort du sol."),
}

MON_PRIX_CHANGE = {
    "name_en": "Prices, exchange rate and money",
    "name_fr": "Prix, taux de change et monnaie",
    "source": (FMI + " Banque centrale du Congo, cours indicatif et cours "
               "parallèle ; Institut national de la statistique, relevé "
               "hebdomadaire des prix."),
    "cols": [["Year", "Année"],
             ["Inflation, period average, %", "Inflation, moyenne annuelle, %"],
             ["Inflation, end of period, %", "Inflation, fin de période, %"],
             ["CDF per USD, average", "CDF par USD, moyenne"],
             ["CDF per USD, end of period", "CDF par USD, fin de période"],
             ["Broad money growth, %", "Croissance de M2, %"],
             ["FX share of deposits, %", "Part des dépôts en devises, %"]],
    "chiffres": [1, 1, 0, 0, 1, 1],
    "rows": [
        ["2023", 19.9, 23.8, 2444, 2687, 40.3, 89.8],
        ["2024", 17.7, 11.7, 2823, 2856, 28.2, 91.6],
        ["2025", 7.7, 4.3, 2688, 2300, 4.0, 90.0],
        ["2026", 4.4, 6.1, "—", "—", 9.1, "—"],
    ],
    "note_en": ("Disinflation between 2023 and 2025 is the sharpest of the "
                "past decade and coincides with a franc that appreciated by "
                "about a fifth between August and October 2025, after the "
                "central bank revalued the franc-denominated reserve "
                "requirement on foreign currency deposits. The indicative "
                "rate stood near 2,250 francs to the dollar in July 2026 and "
                "the parallel rate at 2,266 in June, a spread narrow enough "
                "to be unremarkable. The dollarisation ratio is my own "
                "computation from the Fund’s monetary survey; no institution "
                "publishes it as such. The high-frequency price series "
                "published weekly by the statistical institute and by the "
                "central bank do not agree on the cumulative figure for "
                "2026, and the difference is material."),
    "note_fr": ("La désinflation de 2023 à 2025 est la plus vive de la "
                "décennie ; elle coïncide avec un franc apprécié d’un "
                "cinquième environ entre août et octobre 2025, après que la "
                "banque centrale eut réévalué la réserve obligatoire libellée "
                "en francs sur les dépôts en devises. Le cours indicatif "
                "avoisinait 2 250 francs pour un dollar en juillet 2026 et le "
                "cours parallèle 2 266 en juin, écart assez étroit pour ne "
                "rien signifier. Le taux de dollarisation est mon propre "
                "calcul à partir de la situation monétaire du Fonds ; aucune "
                "institution ne le publie tel quel. Les relevés de prix à "
                "haute fréquence publiés chaque semaine par l’institut "
                "de la statistique et par la banque centrale ne concordent "
                "pas sur le cumul de 2026, et l’écart n’est pas "
                "négligeable."),
}


# ----------------------------------------------------------------------
# 4. Pauvrete, inegalites, developpement
# ----------------------------------------------------------------------
DEV_PAUVRETE = {
    "name_en": "Poverty and inequality",
    "name_fr": "Pauvreté et inégalités",
    "source": BM_PAUVRETE + " " + PNUD,
    "cols": [["Indicator", "Indicateur"],
             ["Value", "Valeur"],
             ["Reference year", "Année de référence"]],
    "chiffres": [1],
    "rows": [
        [["Extreme poverty, $3.00 a day, 2021 PPP, %",
          "Pauvreté extrême, 3,00 USD par jour, PPA 2021, %"], 78.9, "2012"],
        [["Extreme poverty, $3.00 a day, 2021 PPP, %",
          "Pauvreté extrême, 3,00 USD par jour, PPA 2021, %"], 85.3, "2020"],
        [["People below $3.00 a day, millions",
          "Population sous 3,00 USD par jour, millions"], 81.9, "2020"],
        [["Poverty at the national line, %",
          "Pauvreté au seuil national, %"], 56.2, "2020"],
        [["Poverty at $4.20 a day, %", "Pauvreté à 4,20 USD par jour, %"],
         92.5, "2020"],
        [["Poverty at $8.30 a day, %", "Pauvreté à 8,30 USD par jour, %"],
         98.0, "2020"],
        [["Extreme poverty, urban, %", "Pauvreté extrême, urbain, %"],
         75.2, "2020"],
        [["Extreme poverty, rural, %", "Pauvreté extrême, rural, %"],
         93.9, "2020"],
        [["Gini index", "Indice de Gini"], 44.7, "2020"],
        [["Prosperity gap", "Écart de prospérité"], 26.1, "2020"],
        [["Income share of the poorest 40 per cent, %",
          "Part de revenu des 40 % les plus pauvres, %"], 15.1, "2010-2023"],
        [["Income share of the richest 10 per cent, %",
          "Part de revenu des 10 % les plus riches, %"], 35.7, "2010-2023"],
        [["Human development index adjusted for inequality",
          "Indice de développement humain ajusté aux inégalités"],
         0.341, "2023"],
    ],
    "note_en": ("Every poverty and inequality figure for the DRC rests on a "
                "household survey whose sampling frame is still the census "
                "of 1984, and the Bank states plainly that the 2005, 2012 "
                "and 2020 surveys are not fully comparable and that no "
                "consistent consumer price series exists to deflate them. A "
                "consumption survey completed in December 2024 was still "
                "being cleaned in late 2025. The right way to read the "
                "table is as an order of magnitude that has not moved: four "
                "Congolese in five live below three dollars a day, and the "
                "gap between the towns and the countryside is nearly twenty "
                "points. The Bank’s own October 2025 brief also carries a "
                "nowcast of nearly fifty million poor in 2024 which cannot "
                "be reconciled with the 2020 tabulation and appears to be "
                "left over from the earlier 2.15-dollar line."),
    "note_fr": ("Tout chiffre de pauvreté ou d’inégalité pour la RD "
                "Congo repose sur une enquête de ménages dont la base de "
                "sondage reste le recensement de 1984, et la Banque dit "
                "clairement que les enquêtes de 2005, 2012 et 2020 ne sont "
                "pas pleinement comparables et qu’aucune série de prix "
                "cohérente ne permet de les déflater. Une enquête de "
                "consommation achevée en décembre 2024 était encore en cours "
                "d’apurement fin 2025. Le tableau se lit donc comme un "
                "ordre de grandeur qui n’a pas bougé : quatre Congolais "
                "sur cinq vivent sous trois dollars par jour, et l’écart "
                "entre la ville et la campagne approche vingt points. La "
                "note de la Banque d’octobre 2025 avance par ailleurs "
                "une estimation de près de cinquante millions de pauvres en "
                "2024, inconciliable avec la tabulation de 2020 et qui "
                "semble héritée de l’ancien seuil de 2,15 dollars."),
}

DEV_HUMAIN = {
    "name_en": "Human development and governance",
    "name_fr": "Développement humain et gouvernance",
    "source": PNUD + " " + TI + " " + WDI,
    "cols": [["Indicator", "Indicateur"],
             ["Value", "Valeur"],
             ["Reference year", "Année de référence"],
             ["Source", "Source"]],
    "chiffres": [3],
    "rows": [
        [["Human development index", "Indice de développement humain"],
         0.522, "2023", ["UNDP", "PNUD"]],
        [["World rank, out of 193", "Rang mondial, sur 193"],
         171, "2023", ["UNDP", "PNUD"]],
        [["Life expectancy at birth, years",
          "Espérance de vie à la naissance, années"],
         61.9, "2023", ["UNDP", "PNUD"]],
        [["Expected years of schooling",
          "Durée attendue de scolarisation, années"],
         10.9, "2023", ["UNDP", "PNUD"]],
        [["Mean years of schooling", "Durée moyenne de scolarisation, années"],
         7.4, "2023", ["UNDP", "PNUD"]],
        [["Gross national income per capita, 2021 PPP $",
          "Revenu national brut par habitant, USD PPA 2021"],
         1431, "2023", ["UNDP", "PNUD"]],
        [["Corruption perceptions index, score out of 100",
          "Indice de perception de la corruption, note sur 100"],
         20, "2025", ["Transparency International",
                      "Transparency International"]],
        [["Corruption perceptions index, rank out of 182",
          "Indice de perception de la corruption, rang sur 182"],
         163, "2025", ["Transparency International",
                       "Transparency International"]],
        [["Human capital index", "Indice de capital humain"],
         0.366, "2020", ["World Bank", "Banque mondiale"]],
        [["Statistical performance indicator",
          "Indicateur de performance statistique"],
         46.3, "2024", ["World Bank", "Banque mondiale"]],
    ],
    "note_en": ("The corruption index moved by nothing at all over the "
                "years for which it is published, which is itself the "
                "finding: perceptions of governance in the DRC are stable "
                "and low. The statistical performance indicator is worth "
                "keeping in view on a page of this kind, since it measures "
                "the quality of the very apparatus that produces every other "
                "number here. The World Bank’s governance indicators were "
                "rebased in December 2025 onto an absolute scale and their "
                "percentile ranks are no longer the headline presentation, "
                "so they are left out rather than quoted from a superseded "
                "vintage."),
    "note_fr": ("L’indice de perception de la corruption n’a pas "
                "bougé sur les années publiées, et c’est là le résultat : "
                "la perception de la gouvernance en RD Congo est stable et "
                "basse. L’indicateur de performance statistique mérite "
                "de figurer sur une page de cette nature, puisqu’il "
                "mesure la qualité de l’appareil même qui produit tous "
                "les autres chiffres. Les indicateurs de gouvernance de la "
                "Banque mondiale ont été rebasés en décembre 2025 sur une "
                "échelle absolue et leurs rangs centiles ne sont plus la "
                "présentation de référence : ils sont laissés de côté plutôt "
                "que cités d’un millésime périmé."),
}

DEV_ACCES = {
    "name_en": "Access to basic services",
    "name_fr": "Accès aux services de base",
    "source": WDI + " " + UIS,
    "cols": [["Indicator", "Indicateur"],
             ["Per cent", "En pourcentage"],
             ["Reference year", "Année de référence"]],
    "chiffres": [1],
    "rows": [
        [["Population with access to electricity",
          "Population ayant accès à l’électricité"], 22.5, "2024"],
        [["Population with safely managed sanitation",
          "Population disposant d’un assainissement géré en sécurité"],
         13.0, "2024"],
        [["Individuals using the internet",
          "Personnes utilisant internet"], 20.0, "2024"],
        [["Population without at least limited drinking water",
          "Population sans eau de boisson au moins limitée"], 45.3, "2020"],
        [["Population without at least limited sanitation",
          "Population sans assainissement au moins limité"], 81.7, "2020"],
        [["Primary schools with electricity",
          "Écoles primaires raccordées à l’électricité"], 10.0, "2023"],
        [["Primary schools with basic drinking water",
          "Écoles primaires disposant d’eau de boisson"], 37.3, "2023"],
        [["Public spending on education, per cent of GDP",
          "Dépense publique d’éducation, en % du PIB"], 2.8, "2022"],
        [["Public spending on education, per cent of budget",
          "Dépense publique d’éducation, en % du budget"], 18.4, "2022"],
    ],
    "note_en": ("Electricity access is the binding constraint that the "
                "input-output table on this page cannot see: a country whose "
                "installed capacity is a fraction of its peak demand cannot "
                "move mining one step downstream, whatever the network "
                "multipliers say. Rural access, widely reported at around "
                "one per cent, is not tabulated in a source that could be "
                "verified and is therefore left out. The 2020 water and "
                "sanitation lines come from the household survey and use a "
                "different definition from the 2024 service indicators, so "
                "the two vintages are not to be differenced."),
    "note_fr": ("L’accès à l’électricité est la contrainte que le "
                "tableau entrées-sorties de cette page ne peut pas voir : un "
                "pays dont la capacité installée ne couvre qu’une "
                "fraction de la demande de pointe ne peut pas déplacer la "
                "mine d’un cran vers l’aval, quoi que disent les "
                "multiplicateurs de réseau. L’accès rural, souvent "
                "avancé autour de un pour cent, n’est tabulé dans "
                "aucune source vérifiable et reste donc absent. Les lignes "
                "eau et assainissement de 2020 viennent de l’enquête de "
                "ménages et n’emploient pas la définition des "
                "indicateurs de service de 2024 : on ne différencie pas les "
                "deux millésimes."),
}

DEV_EDUCATION = {
    "name_en": "School completion",
    "name_fr": "Achèvement scolaire",
    "source": UIS,
    "cols": [["Level", "Niveau"],
             ["2013, %", "2013, %"],
             ["2024, %", "2024, %"],
             ["Change, points", "Variation, points"]],
    "chiffres": [1, 1, 1],
    "rows": [
        [["Primary completion", "Achèvement du primaire"], 51.7, 61.3, 9.6],
        [["Lower secondary completion",
          "Achèvement du premier cycle du secondaire"], 41.5, 50.4, 8.9],
        [["Upper secondary completion",
          "Achèvement du second cycle du secondaire"], 17.5, 22.5, 5.0],
        [["Out of school, primary age",
          "Enfants non scolarisés, âge du primaire"], 24.0, 17.0, -7.0],
    ],
    "note_en": ("These are modelled estimates, not survey readings. The "
                "surveys of 2013 and 2018 put primary completion higher, at "
                "68.9 and 66.7 per cent, and lower secondary completion at "
                "53.5 and 54.4; the gap between the modelled and the "
                "surveyed series is a caution about both. The out-of-school "
                "line is for 2023, the last year the source models it. What "
                "survives the measurement problem is the shape: completion "
                "rises at every level, and falls by more than half between "
                "the start and the end of schooling."),
    "note_fr": ("Ce sont des estimations modélisées, non des relevés "
                "d’enquête. Les enquêtes de 2013 et de 2018 situent "
                "l’achèvement du primaire plus haut, à 68,9 et 66,7 "
                "pour cent, et celui du premier cycle du secondaire à 53,5 "
                "et 54,4 ; l’écart entre série modélisée et série "
                "enquêtée invite à la prudence sur les deux. La ligne des "
                "enfants non scolarisés porte sur 2023, dernière année "
                "modélisée par la source. Ce qui survit au problème de "
                "mesure, c’est la forme : l’achèvement progresse à "
                "tous les niveaux, et se réduit de plus de moitié entre le "
                "début et la fin de la scolarité."),
}

DEV_ALIMENTATION = {
    "name_en": "Acute food insecurity",
    "name_fr": "Insécurité alimentaire aiguë",
    "source": IPC,
    "cols": [["Period", "Période"],
             ["Phase 3 and above, millions", "Phase 3 et au-delà, millions"],
             ["Share of the population analysed, %",
              "Part de la population analysée, %"],
             ["Phase 4, millions", "Phase 4, millions"]],
    "chiffres": [1, 0, 1],
    "rows": [
        [["September to December 2025", "Septembre à décembre 2025"],
         24.8, 21, 3.2],
        [["January to June 2026", "Janvier à juin 2026"],
         26.5, 23, 3.6],
    ],
    "note_en": ("The analysis covers 117 million people, the population "
                "base drawn from the statistical institute’s 2026 "
                "estimates. Phase 3 is crisis, phase 4 emergency; the phase "
                "4 figures are floors, since the source gives them as more "
                "than. Nearly ten million of the twenty-six and a half are "
                "in the four eastern provinces alone, which is where the "
                "displacement figures in the next tab also concentrate."),
    "note_fr": ("L’analyse porte sur 117 millions de personnes, base de "
                "population tirée des estimations 2026 de l’institut de "
                "la statistique. La phase 3 désigne la crise, la phase 4 "
                "l’urgence ; les chiffres de phase 4 sont des planchers, "
                "la source les donnant comme des minima. Près de dix millions "
                "des vingt-six et demi se trouvent dans les quatre provinces "
                "de l’Est à elles seules, là où se concentrent aussi les "
                "déplacements de l’onglet suivant."),
}


# ----------------------------------------------------------------------
# 5. Securite, sante, demographie
# ----------------------------------------------------------------------
SEC_DEPLACEMENTS = {
    "name_en": "Internally displaced people",
    "name_fr": "Personnes déplacées internes",
    "source": OIM + " " + HCR,
    "cols": [["Reading date", "Date du relevé"],
             ["Displaced, millions", "Déplacés, millions"],
             ["Scope", "Périmètre"],
             ["Recording body", "Organisme"]],
    "chiffres": [2],
    "rows": [
        [["December 2021", "Décembre 2021"], 5.20,
         ["National", "National"], "OCHA"],
        [["December 2022", "Décembre 2022"], 5.50,
         ["National", "National"], "OCHA"],
        [["December 2024", "Décembre 2024"], 7.80,
         ["National", "National"], "OCHA"],
        [["April 2025", "Avril 2025"], 6.82,
         ["National", "National"], "OCHA"],
        [["September 2025", "Septembre 2025"], 5.00,
         ["National", "National"], ["UNHCR", "HCR"]],
        [["November 2025 to February 2026",
          "Novembre 2025 à février 2026"], 5.65,
         ["Four eastern provinces", "Quatre provinces de l’Est"],
         ["IOM displacement tracking matrix",
          "Matrice de suivi des déplacements de l’OIM"]],
        [["13 April 2026", "13 avril 2026"], 5.61,
         ["National", "National"], ["OCHA and IOM", "OCHA et OIM"]],
    ],
    "note_en": ("These readings are not a series and must not be "
                "differenced. Coverage, method and reporting body change "
                "between vintages, and the drop from 7.8 million at the end "
                "of 2024 to 5.6 million in 2026 reflects those changes as "
                "much as any return movement. The eastern reading of "
                "November 2025 to February 2026 covers four provinces only "
                "and counts 5,647,465 displaced alongside 3,525,590 "
                "returnees. Total forced displacement, internal and "
                "external together, was put at 8.2 million in September "
                "2025."),
    "note_fr": ("Ces relevés ne forment pas une série et ne se différencient "
                "pas. Le périmètre, la méthode et l’organisme changent "
                "d’un millésime à l’autre, et la baisse de 7,8 "
                "millions fin 2024 à 5,6 millions en 2026 tient à ces "
                "changements autant qu’à des retours. Le relevé oriental "
                "de novembre 2025 à février 2026 ne couvre que quatre "
                "provinces et dénombre 5 647 465 déplacés à côté de 3 525 590 "
                "retournés. Le déplacement forcé total, interne et externe "
                "confondus, était évalué à 8,2 millions en septembre 2025."),
}

SEC_PROVINCES = {
    "name_en": "Displacement by province, eastern DR Congo",
    "name_fr": "Déplacements par province, est de la RD Congo",
    "source": OIM,
    "cols": [["Province", "Province"],
             ["Displaced", "Déplacés"],
             ["Share of the four provinces, %",
              "Part des quatre provinces, %"]],
    "chiffres": [0, 0],
    "rows": [
        ["Nord-Kivu", 2561136, 45],
        ["Sud-Kivu", 1395604, 25],
        ["Ituri", 1360577, 24],
        ["Tanganyika", 330148, 6],
    ],
    "note_en": ("The reading covers November 2025 to February 2026 and "
                "counts displacement inside and between these four "
                "provinces; 3,525,590 returnees were recorded over the same "
                "round. Nearly half of the displaced are in North Kivu "
                "alone. Set against the population table in the Population "
                "tab, the displaced amount to a quarter of the inhabitants "
                "of North Kivu and a fifth of those of Ituri."),
    "note_fr": ("Le relevé porte sur novembre 2025 à février 2026 et "
                "dénombre les déplacements à l’intérieur de ces quatre "
                "provinces et entre elles ; 3 525 590 retournés ont été "
                "enregistrés sur le même tour. Près de la moitié des "
                "déplacés se trouvent dans le seul Nord-Kivu. Rapportés au "
                "tableau de population de l’onglet Population, les "
                "déplacés représentent le quart des habitants du Nord-Kivu "
                "et le cinquième de ceux de l’Ituri."),
}

SEC_REFUGIES = {
    "name_en": "Refugees and asylum seekers",
    "name_fr": "Réfugiés et demandeurs d’asile",
    "source": HCR,
    "cols": [["Population", "Population"],
             ["Number", "Effectif"],
             ["Reading date", "Date du relevé"]],
    "chiffres": [0],
    "rows": [
        [["Congolese refugees and asylum seekers abroad",
          "Réfugiés et demandeurs d’asile congolais à l’étranger"],
         1200000, ["30 November 2025", "30 novembre 2025"]],
        [["New arrivals in the five neighbouring countries since early 2025",
          "Arrivées nouvelles dans les cinq pays voisins depuis début 2025"],
         127000, "2025"],
        [["Refugees and asylum seekers hosted in the DR Congo",
          "Réfugiés et demandeurs d’asile accueillis en RD Congo"],
         529000, "2025"],
        [["Total forcibly displaced, internal and external",
          "Déplacement forcé total, interne et externe"],
         8200000, ["September 2025", "Septembre 2025"]],
    ],
    "note_en": ("Roughly half of the Congolese refugee population is in "
                "Uganda, and more than two fifths of those the DRC itself "
                "hosts are Rwandan. The agency’s own materials give the "
                "hosted caseload as both 529,000 and 490,000 in the same "
                "publication; the larger figure is used here and the "
                "discrepancy noted rather than resolved. The agency projects "
                "nine million forcibly displaced by the end of 2026."),
    "note_fr": ("La moitié environ des réfugiés congolais se trouve en "
                "Ouganda, et plus des deux cinquièmes de ceux que la RD "
                "Congo accueille elle-même sont rwandais. Les documents de "
                "l’agence donnent l’effectif accueilli à la fois à "
                "529 000 et à 490 000 dans la même publication ; le chiffre "
                "le plus élevé est retenu ici et la divergence signalée "
                "plutôt que tranchée. L’agence projette neuf millions de "
                "déplacés forcés à la fin de 2026."),
}

SEC_VIOLATIONS = {
    "name_en": "Documented human rights violations",
    "name_fr": "Violations documentées des droits de l’homme",
    "source": BCNUDH,
    "cols": [["Period", "Période"],
             ["Violations documented", "Violations documentées"],
             ["Victims documented", "Victimes documentées"],
             ["Scope", "Périmètre"]],
    "chiffres": [0, 0],
    "rows": [
        ["2022", 5091, "—",
         ["Five conflict-affected provinces",
          "Cinq provinces en conflit"]],
        ["2023", 5273, "—", ["National", "National"]],
        [["First half of 2024", "Premier semestre 2024"], 2355, 6309,
         ["National", "National"]],
        ["2025", 6169, 18000, ["National", "National"]],
    ],
    "note_en": ("Every figure here is a count of what the United Nations "
                "joint human rights office was able to document and verify, "
                "not an estimate of what occurred; the true figures are "
                "higher by an unknown margin, and the office says so. The "
                "2022 line covers five provinces and is not comparable with "
                "the national counts. The 2025 total is a floor: within it "
                "the office documented 1,479 victims of conflict-related "
                "sexual violence, up by three fifths on the previous year, "
                "and more than 3,900 victims of extrajudicial execution, of "
                "whom nearly three hundred were children. Armed groups were "
                "held responsible for 71 per cent of violations and state "
                "agents for 28 per cent."),
    "note_fr": ("Chaque chiffre est ici un décompte de ce que le bureau "
                "conjoint des Nations unies aux droits de l’homme a pu "
                "documenter et vérifier, non une estimation de ce qui est "
                "survenu ; les chiffres réels sont supérieurs d’une "
                "marge inconnue, et le bureau le dit. La ligne de 2022 porte "
                "sur cinq provinces et ne se compare pas aux décomptes "
                "nationaux. Le total de 2025 est un plancher : le bureau y a "
                "documenté 1 479 victimes de violences sexuelles liées au "
                "conflit, en hausse de trois cinquièmes sur l’année "
                "précédente, et plus de 3 900 victimes d’exécution "
                "extrajudiciaire, dont près de trois cents enfants. Les "
                "groupes armés ont été tenus pour responsables de 71 pour "
                "cent des violations et les agents de l’État de 28 pour "
                "cent."),
}

SANTE_EBOLA_BULLETINS = {
    "name_en": "The outbreak bulletin by bulletin, as the World Health "
               "Organization reported it",
    "name_fr": "L’épidémie bulletin par bulletin, telle que "
               "l’Organisation mondiale de la santé l’a rapportée",
    "source": OMS_DONS,
    "cols": [["Bulletin", "Bulletin"],
             ["Published", "Paru le"],
             ["Figures as of", "Chiffres arrêtés au"],
             ["Confirmed cases", "Cas confirmés"],
             ["Deaths", "Décès"],
             ["Case fatality ratio as printed, %",
              "Létalité telle qu’imprimée, %"],
             ["Recovered", "Guéris"]],
    "chiffres": [0, 0, 0, 0, 1, 0],
    "rows": [
        ["2026-DON602", ["16 May 2026", "16 mai 2026"],
         ["15 May 2026", "15 mai 2026"], "—", 4, "—", "—"],
        ["2026-DON603", ["21 May 2026", "21 mai 2026"],
         ["21 May 2026", "21 mai 2026"], 83, 9, 11, "—"],
        ["2026-DON605", ["29 May 2026", "29 mai 2026"],
         ["27 May 2026", "27 mai 2026"], 125, 17, 14, "—"],
        ["2026-DON606", ["8 June 2026", "8 juin 2026"],
         ["6 June 2026", "6 juin 2026"], 515, 91, 17.7, 12],
        ["2026-DON607", ["13 June 2026", "13 juin 2026"],
         ["10 June 2026", "10 juin 2026"], 676, 136, 20.1, 32],
        ["2026-DON608", ["19 June 2026", "19 juin 2026"],
         ["17 June 2026", "17 juin 2026"], 896, 232, 26, 78],
        ["2026-DON612", ["3 July 2026", "3 juillet 2026"],
         ["1 July 2026", "1er juillet 2026"], 1460, 452, 30.9, 213],
        ["2026-DON613", ["17 July 2026", "17 juillet 2026"],
         ["15 July 2026", "15 juillet 2026"], 2124, 828, 39, 390],
        ["2026-DON614", ["1 August 2026", "1er août 2026"],
         ["30 July 2026", "30 juillet 2026"], 3605, 1587, 44, 651],
        ["2026-DON615", ["14 August 2026", "14 août 2026"],
         ["12 August 2026", "12 août 2026"], 4665, 2184, 46.8, 965],
    ],
    "note_en": (
        "This is the table that makes the outbreak legible as a movement "
        "rather than a snapshot: one line per bulletin, each figure taken "
        "from the bulletin that carries it. Nothing here is carried over "
        "from a neighbouring issue and nothing is computed. The case "
        "fatality ratio is quoted exactly as the World Health Organization "
        "prints it, which is why it does not always follow from the two "
        "columns beside it; the Organization revises its denominator as "
        "investigations close. The figures are for the DR Congo alone. The "
        "first bulletin states no confirmed total — it reports suspected "
        "cases, and the four deaths shown are the four it attributes to "
        "confirmed cases — so that cell carries a dash. The bulletins of "
        "13 and 19 June both warn that their own ratio is probably an "
        "underestimate, because deaths that occurred before the outbreak "
        "was declared were still under investigation. The numbering has "
        "gaps because the Disease Outbreak News series is shared with "
        "other events; the ten bulletins listed here are the whole of the "
        "series for this outbreak. The bulletin of 1 August was revised on "
        "3 August, and it is the revised text that is quoted."),
    "note_fr": (
        "C’est ce tableau qui rend l’épidémie lisible comme un mouvement et "
        "non comme un instantané : une ligne par bulletin, chaque chiffre "
        "pris dans le bulletin qui le porte. Rien n’est repris d’un numéro "
        "voisin, rien n’est calculé. La létalité est citée exactement comme "
        "l’Organisation mondiale de la santé l’imprime, ce qui explique "
        "qu’elle ne découle pas toujours des deux colonnes qui la "
        "précèdent : l’Organisation révise son dénominateur à mesure que "
        "les enquêtes se closent. Les chiffres portent sur la seule RD "
        "Congo. Le premier bulletin ne donne aucun total de cas confirmés — "
        "il compte des cas suspects, et les quatre décès portés ici sont "
        "les quatre qu’il rattache à des cas confirmés —, d’où le tiret. "
        "Les bulletins des 13 et 19 juin avertissent l’un et l’autre que "
        "leur propre taux est vraisemblablement sous-estimé, des décès "
        "survenus avant la déclaration de l’épidémie restant à instruire. "
        "La numérotation présente des trous parce que la série des "
        "bulletins d’épidémie est partagée avec d’autres événements ; les "
        "dix bulletins recensés ici sont toute la série de cette épidémie. "
        "Le bulletin du 1er août a été révisé le 3 août, et c’est le texte "
        "révisé qui est cité."),
}

SANTE_EBOLA_SUIVI = {
    "name_en": "The seventeenth Ebola outbreak, latest reading",
    "name_fr": "La dix-septième épidémie d’Ebola, dernier relevé",
    "source": OMS_DON615,
    "cols": [["Reading", "Relevé"],
             ["Number", "Nombre"],
             ["Scope and date", "Périmètre et date"]],
    "chiffres": [0],
    "rows": [
        [["Confirmed cases, DR Congo", "Cas confirmés, RD Congo"], 4665,
         ["as of 12 August 2026", "au 12 août 2026"]],
        [["Deaths among confirmed cases, DR Congo",
          "Décès parmi les cas confirmés, RD Congo"], 2184,
         ["crude case fatality ratio of 46.8 per cent",
          "létalité brute de 46,8 pour cent"]],
        [["Patients recovered, DR Congo", "Patients guéris, RD Congo"], 965,
         ["as of 12 August 2026", "au 12 août 2026"]],
        [["Confirmed cases in the last twenty-four hours",
          "Cas confirmés des vingt-quatre dernières heures"], 100,
         ["from 22 health zones, in every affected province but South Kivu",
          "dans 22 zones de santé, dans toutes les provinces touchées sauf "
          "le Sud-Kivu"]],
        [["Confirmed cases, epidemiological week 32",
          "Cas confirmés, semaine épidémiologique 32"], 579,
         ["3 to 9 August 2026, heaviest week recorded to date",
          "du 3 au 9 août 2026, semaine la plus lourde enregistrée à ce "
          "jour"]],
        [["Deaths, epidemiological week 32",
          "Décès, semaine épidémiologique 32"], 304,
         ["3 to 9 August 2026, heaviest week recorded to date",
          "du 3 au 9 août 2026, semaine la plus lourde enregistrée à ce "
          "jour"]],
        [["Confirmed cases added since the bulletin of 1 August",
          "Cas confirmés ajoutés depuis le bulletin du 1er août"], 1060,
         ["thirteen days", "treize jours"]],
        [["Deaths added since the bulletin of 1 August",
          "Décès ajoutés depuis le bulletin du 1er août"], 597,
         ["thirteen days", "treize jours"]],
        [["Health workers infected", "Soignants infectés"], 155,
         ["at least, as of 9 August, case fatality ratio of 29 per cent",
          "au moins, au 9 août, létalité de 29 pour cent"]],
        [["Health workers dead", "Soignants décédés"], 45,
         ["as of 9 August 2026", "au 9 août 2026"]],
        [["Health workers recovered", "Soignants guéris"], 68,
         ["since the outbreak began", "depuis le début de l’épidémie"]],
        [["Contacts to be followed up",
          "Contacts à suivre"], 20740,
         ["in the twenty-four hours to 12 August",
          "dans les vingt-quatre heures au 12 août"]],
        [["Contacts actually seen", "Contacts effectivement vus"], 17460,
         ["84.2 per cent of those to be followed up",
          "84,2 pour cent des contacts à suivre"]],
        [["Provinces affected", "Provinces touchées"], 6,
         ["Ituri, North Kivu, South Kivu, Haut-Uélé, Tshopo, Bas-Uélé",
          "Ituri, Nord-Kivu, Sud-Kivu, Haut-Uélé, Tshopo, Bas-Uélé"]],
        [["Health zones affected", "Zones de santé touchées"], 54,
         ["the bulletin no longer says how many remain active",
          "le bulletin ne dit plus combien restent actives"]],
        [["Attacks on health care recorded",
          "Attaques contre les soins recensées"], 12,
         ["since 17 May 2026", "depuis le 17 mai 2026"]],
        [["Confirmed cases, Uganda", "Cas confirmés, Ouganda"], 20,
         ["18 recovered; enhanced monitoring ends 27 August 2026",
          "18 guéris ; la surveillance renforcée prend fin le 27 août 2026"]],
        [["Deaths, Uganda", "Décès, Ouganda"], 2,
         ["as of 12 August 2026", "au 12 août 2026"]],
        [["Confirmed cases, France", "Cas confirmés, France"], 1,
         ["imported 24 June, discharged 4 July, no secondary transmission; "
          "41 days without a further case at 14 August",
          "importé le 24 juin, sorti le 4 juillet, aucune transmission "
          "secondaire ; 41 jours sans autre cas au 14 août"]],
        [["Confirmed cases, all countries",
          "Cas confirmés, tous pays"], 4686,
         ["including two DR Congo cases treated in Germany",
          "dont deux cas congolais traités en Allemagne"]],
        [["Deaths, all countries", "Décès, tous pays"], 2186,
         ["including two in Uganda", "dont deux en Ouganda"]],
        [["Patients recovered, all countries",
          "Patients guéris, tous pays"], 986,
         ["at least, as of 12 August 2026", "au moins, au 12 août 2026"]],
    ],
    "note_en": (
        "This outbreak is the largest ever recorded in the country: it has "
        "passed the outbreak of 2018 to 2020, which the World Health "
        "Organization counts at 3 317 confirmed cases, and it is expanding "
        "faster than any previous Ebola outbreak there. It was declared on "
        "15 May 2026 by the Ministry of Public Health, Hygiene and Social "
        "Welfare and was determined a public health emergency of "
        "international concern on 17 May. Four cautions belong with the "
        "figures. The Organization attributes part of the increase to "
        "strengthened surveillance and laboratory capacity, but says that "
        "most of it reflects the expansion of the outbreak itself. The "
        "unusually large counts dated 22 July are the completion of a data "
        "reconciliation exercise covering cases and deaths that occurred "
        "earlier, not incidence on that day. There is still no licensed "
        "vaccine and no specific treatment for the Bundibugyo virus: Ervebo "
        "was recommended on 7 August for prioritisation within a randomised "
        "clinical trial, and the PARTNERS treatment trial has enrolled more "
        "than a hundred confirmed cases since 2 July, but neither is an "
        "approved product for this virus. And the twelve attacks on health "
        "care recorded since 17 May raise, in the Organization's own words, "
        "the risk of undetected transmission. In the two previous "
        "Bundibugyo outbreaks the published case fatality ratios were 30 "
        "per cent in Uganda in 2007 and 50 per cent in the DR Congo in "
        "2012. The readings above carry three different cut-offs, which the "
        "third column names line by line."),
    "note_fr": (
        "Cette épidémie est la plus étendue jamais enregistrée dans le "
        "pays : elle a dépassé celle de 2018 à 2020, que l’Organisation "
        "mondiale de la santé chiffre à 3 317 cas confirmés, et elle "
        "s’étend plus vite qu’aucune épidémie d’Ebola avant elle. Elle a "
        "été déclarée le 15 mai 2026 par le ministère de la Santé publique, "
        "de l’Hygiène et de la Prévoyance sociale, et qualifiée d’urgence "
        "de santé publique de portée internationale le 17 mai. Quatre "
        "précautions accompagnent les chiffres. L’Organisation attribue une "
        "partie de la hausse au renforcement de la surveillance et de la "
        "capacité de laboratoire, mais dit que l’essentiel tient à "
        "l’extension de l’épidémie elle-même. Les décomptes "
        "exceptionnellement élevés portés au 22 juillet sont "
        "l’aboutissement d’un travail de réconciliation des données, qui "
        "rattache à cette date des cas et des décès survenus plus tôt : ce "
        "n’est pas l’incidence du jour. Il n’existe toujours ni vaccin "
        "homologué ni traitement spécifique contre le virus Bundibugyo : le "
        "vaccin Ervebo a été recommandé le 7 août pour être administré en "
        "priorité dans le cadre d’un essai clinique randomisé, et l’essai "
        "thérapeutique PARTNERS a recruté plus de cent cas confirmés depuis "
        "le 2 juillet, mais aucun des deux n’est un produit homologué "
        "contre ce virus. Enfin, les douze attaques contre les soins "
        "recensées depuis le 17 mai élèvent, selon les termes mêmes de "
        "l’Organisation, le risque d’une transmission non détectée. Lors "
        "des deux épidémies Bundibugyo précédentes, les létalités publiées "
        "étaient de 30 pour cent en Ouganda en 2007 et de 50 pour cent en "
        "RD Congo en 2012. Les relevés ci-dessus portent trois dates "
        "d’arrêt différentes, que la troisième colonne nomme ligne à "
        "ligne."),
}

SANTE_EBOLA_PROVINCES = {
    "name_en": "The seventeenth outbreak by province",
    "name_fr": "La dix-septième épidémie par province",
    "source": OMS_DON615,
    "cols": [["Province", "Province"],
             ["Health zones affected", "Zones de santé touchées"],
             ["Health zones in the province",
              "Zones de santé de la province"],
             ["Confirmed cases", "Cas confirmés"],
             ["Deaths", "Décès"]],
    "chiffres": [0, 0, 0, 0],
    "rows": [
        ["Ituri", 28, 36, 3979, 1726],
        [["North Kivu", "Nord-Kivu"], 12, 34, "—", "—"],
        [["South Kivu", "Sud-Kivu"], 1, 34, "—", "—"],
        ["Haut-Uélé", 6, 13, "—", "—"],
        ["Tshopo", 6, 23, "—", "—"],
        ["Bas-Uélé", 1, 11, "—", "—"],
        [["The six provinces", "Les six provinces"],
         54, "—", 4665, 2184],
    ],
    "note_en": (
        "Ituri carries 85 per cent of the confirmed cases and 79 per cent of "
        "the deaths. The bulletin publishes the case and death counts "
        "province by province for Ituri only; for the other five the dash "
        "means that the figure is not in the source, not that it is zero. "
        "Bas-Uélé is the newest of the six: one confirmed case, in Buta "
        "health zone, in a person who had travelled from Haut-Uélé and fell "
        "ill on 4 August. The second column counts the health zones where a "
        "case has been confirmed, the third the health zones the province "
        "contains, so the two together say how far the outbreak has room to "
        "run. Contact follow-up is no longer broken down by province; the "
        "national figure, 17 460 contacts seen of 20 740 to be followed up, "
        "is in the first table. Of the hundred cases confirmed in the "
        "twenty-four hours to 12 August, sixty-seven were in Ituri and "
        "twenty-five in North Kivu."),
    "note_fr": (
        "L’Ituri porte 85 pour cent des cas confirmés et 79 pour cent des "
        "décès. Le bulletin ne publie le décompte des cas et des décès "
        "province par province que pour l’Ituri ; pour les cinq autres, le "
        "tiret signifie que le chiffre n’est pas dans la source, non qu’il "
        "est nul. Le Bas-Uélé est la dernière des six provinces atteintes : "
        "un cas confirmé, dans la zone de santé de Buta, chez une personne "
        "venue du Haut-Uélé et tombée malade le 4 août. La deuxième colonne "
        "compte les zones de santé où un cas a été confirmé, la troisième "
        "celles que la province compte : les deux ensemble disent ce qu’il "
        "reste d’espace à l’épidémie. Le suivi des contacts n’est plus "
        "ventilé par province ; le chiffre national, 17 460 contacts vus sur "
        "20 740 à suivre, figure au premier tableau. Sur les cent cas "
        "confirmés dans les vingt-quatre heures au 12 août, soixante-sept "
        "l’ont été en Ituri et vingt-cinq au Nord-Kivu."),
}

SANTE_EBOLA_ZONES = {
    "name_en": "Ituri, the health zones the bulletin names",
    "name_fr": "Ituri, les zones de santé que le bulletin nomme",
    "source": OMS_DON614,
    "cols": [["Health zone", "Zone de santé"],
             ["Confirmed cases", "Cas confirmés"]],
    "chiffres": [0],
    "rows": [
        ["Bunia", 880],
        ["Rwampara", 627],
        ["Mongbwalu", 541],
        ["Nizi", 377],
        ["Lita", 131],
        ["Nyankunde", 114],
    ],
    "note_en": (
        "This table stops on 30 July 2026, the cut-off of the bulletin "
        "named below it: no later bulletin has named a health zone, and "
        "the table is left at its own date rather than mixed with a more "
        "recent one. These are the six health zones of Ituri with the "
        "highest counts, and the only six the bulletin names. Ituri had "
        "3 176 confirmed cases at that date, spread over twenty-eight of "
        "its thirty-six health zones, so the remainder is distributed "
        "across the twenty-two others, which the source does not "
        "enumerate. Mongbwalu is where the outbreak began: it was "
        "confined to that single health zone before spreading to five "
        "provinces in two months, and to a sixth in three."),
    "note_fr": (
        "Ce tableau s’arrête au 30 juillet 2026, date d’arrêt du bulletin "
        "nommé au-dessous : aucun bulletin postérieur n’a nommé de zone de "
        "santé, et le tableau est laissé à sa propre date plutôt que mêlé "
        "à une plus récente. Ce sont les six zones de santé de l’Ituri aux "
        "décomptes les plus élevés, et les six seules que le bulletin "
        "nomme. L’Ituri comptait à cette date 3 176 cas confirmés répartis "
        "sur vingt-huit de ses trente-six zones de santé : le reste se "
        "distribue donc sur les vingt-deux autres, que la source n’énumère "
        "pas. Mongbwalu est le point de départ de l’épidémie : celle-ci y "
        "était confinée avant de gagner cinq provinces en deux mois, et "
        "une sixième en trois."),
}

SANTE_EBOLA_HISTOIRE = {
    "name_en": "The seventeen Ebola outbreaks, 1976 to 2026",
    "name_fr": "Les dix-sept épidémies d’Ebola, de 1976 à 2026",
    "source": CDC_EBOLA,
    "cols": [["Outbreak", "Épidémie"],
             ["Years", "Années"],
             ["Province and area", "Province et zone"],
             ["Virus", "Virus"],
             ["Cases", "Cas"],
             ["Deaths", "Décès"],
             ["Fatal cases, %", "Létalité, %"]],
    "chiffres": [0, 0, 0, 0, 0, 1],
    "rows": [
        [["1st", "1re"], "1976", ["Équateur, Yambuku", "Équateur, Yambuku"],
         "Zaire", 318, 280, 88],
        [["2nd", "2e"], "1977", ["Équateur, Tandala", "Équateur, Tandala"],
         "Zaire", 1, 1, 100],
        [["3rd", "3e"], "1995", "Kikwit", "Zaire", 315, 254, 81],
        [["4th", "4e"], "2007",
         ["Kasaï-Occidental, Luebo and Mweka",
          "Kasaï-Occidental, Luebo et Mweka"], "Zaire", 264, 187, 71],
        [["5th", "5e"], "2008-2009",
         ["Kasaï-Occidental, Mweka and Luebo",
          "Kasaï-Occidental, Mweka et Luebo"], "Zaire", 32, 15, 47],
        [["6th", "6e"], "2012", ["Orientale, Isiro", "Orientale, Isiro"],
         "Bundibugyo", 62, 34, 55],
        [["7th", "7e"], "2014", ["Équateur, Boende", "Équateur, Boende"],
         "Zaire", 69, 49, 71],
        [["8th", "8e"], "2017", "Likati", "Zaire", 8, 4, 50],
        [["9th", "9e"], "2018", ["Équateur, Bikoro", "Équateur, Bikoro"],
         "Zaire", 54, 33, 61],
        [["10th", "10e"], "2018-2020",
         ["North Kivu, Ituri and South Kivu",
          "Nord-Kivu, Ituri et Sud-Kivu"], "Zaire", 3470, 2287, 66],
        [["11th", "11e"], "2020", ["Équateur, Mbandaka",
                                   "Équateur, Mbandaka"], "Zaire",
         130, 55, 42.3],
        [["12th", "12e"], "2021", ["North Kivu, Biena", "Nord-Kivu, Biena"],
         "Zaire", 12, 6, 50],
        [["13th", "13e"], "2021", ["North Kivu, Beni", "Nord-Kivu, Beni"],
         "Zaire", 11, 9, 82],
        [["14th", "14e"], "2022", ["Équateur, Mbandaka",
                                   "Équateur, Mbandaka"], "Zaire", 5, 5, 100],
        [["15th", "15e"], "2022", ["North Kivu, Beni", "Nord-Kivu, Beni"],
         "Zaire", 1, 1, 100],
        [["16th", "16e"], "2025", ["Kasaï, Bulape", "Kasaï, Bulape"],
         "Zaire", 64, 45, 70],
        [["17th", "17e"], "2026",
         ["Ituri, North Kivu, South Kivu, Haut-Uélé, Tshopo, Bas-Uélé",
          "Ituri, Nord-Kivu, Sud-Kivu, Haut-Uélé, Tshopo, Bas-Uélé"],
         "Bundibugyo", 4665, 2184, 46.8],
    ],
    "note_en": (
        "Fifty years in one table. The case counts and the fatality ratios "
        "are those the source publishes; none is recomputed here, which is "
        "why the ratios do not always follow exactly from the two columns to "
        "their left. Two rows need a word. The tenth outbreak is given at "
        "3 470 cases because the American count includes probable and "
        "suspected cases; the World Health Organization counts 3 317 "
        "confirmed for the same episode, and it is against that confirmed "
        "figure that the outbreak now under way, at 4 665 confirmed, is "
        "described as the largest the country has known. The sixteenth is "
        "likewise given at 64 cases including probable ones. Fifteen of the "
        "seventeen outbreaks were caused by the Zaire virus; only the sixth "
        "and the seventeenth were caused by the Bundibugyo virus, for which "
        "no vaccine exists. The last column is worth reading on its own: an "
        "outbreak caught in one health zone kills a handful of people, one "
        "that reaches a city kills thousands."),
    "note_fr": (
        "Cinquante ans en un tableau. Les décomptes de cas et les létalités "
        "sont ceux que publie la source ; aucun n’est recalculé ici, ce qui "
        "explique que les taux ne se déduisent pas toujours exactement des "
        "deux colonnes qui les précèdent. Deux lignes appellent un mot. La "
        "dixième épidémie est portée à 3 470 cas parce que le décompte "
        "américain inclut les cas probables et suspects ; l’Organisation "
        "mondiale de la santé retient 3 317 cas confirmés pour le même "
        "épisode, et c’est à ce chiffre de cas confirmés que l’épidémie en "
        "cours, à 4 665 cas confirmés, est comparée lorsqu’on la dit la plus "
        "étendue que le pays ait connue. La seizième est de même portée à "
        "64 cas, cas probables inclus. Quinze des dix-sept épidémies sont "
        "dues au virus Zaïre ; seules la sixième et la dix-septième sont "
        "dues au virus Bundibugyo, contre lequel il n’existe pas de vaccin. "
        "La dernière colonne se lit pour elle-même : une épidémie arrêtée "
        "dans une seule zone de santé tue quelques personnes, une épidémie "
        "qui atteint une ville en tue des milliers."),
}

SANTE_EPIDEMIES = {
    "name_en": "Other diseases under surveillance",
    "name_fr": "Autres maladies sous surveillance",
    "source": OMS_SURV,
    "cols": [["Disease and scope", "Maladie et périmètre"],
             ["Period", "Période"],
             ["Cases", "Cas"],
             ["Deaths", "Décès"]],
    "chiffres": [0, 0],
    "rows": [
        [["Mpox, confirmed, DR Congo", "Mpox, confirmés, RD Congo"],
         ["June 2026", "Juin 2026"], 86, 0],
        [["Mpox, confirmed, DR Congo", "Mpox, confirmés, RD Congo"],
         ["8 June to 19 July 2026", "8 juin au 19 juillet 2026"], 30, 0],
        [["Mpox, confirmed, African region, 32 countries",
          "Mpox, confirmés, région africaine, 32 pays"],
         ["1 January 2025 to 19 July 2026",
          "1er janvier 2025 au 19 juillet 2026"], 51159, 235],
        [["Mpox, confirmed, world", "Mpox, confirmés, monde"],
         ["1 January 2025 to 30 June 2026",
          "1er janvier 2025 au 30 juin 2026"], 63692, 256],
        [["Cholera, suspected and confirmed, DR Congo",
          "Choléra, suspects et confirmés, RD Congo"],
         ["1 January to 31 May 2026", "1er janvier au 31 mai 2026"],
         28567, 815],
        [["Cholera, suspected and confirmed, DR Congo",
          "Choléra, suspects et confirmés, RD Congo"],
         ["May 2026", "Mai 2026"], 3651, 82],
        [["Circulating vaccine-derived poliovirus type 1, DR Congo",
          "Poliovirus circulant dérivé d’une souche vaccinale de type 1, "
          "RD Congo"], "2025", 1, "—"],
        [["Circulating vaccine-derived poliovirus type 2, DR Congo",
          "Poliovirus circulant dérivé d’une souche vaccinale de type 2, "
          "RD Congo"], "2025", "—", "—"],
        [["Measles, DR Congo", "Rougeole, RD Congo"], "—", "—", "—"],
    ],
    "note_en": (
        "Four diseases, four states of knowledge, and the table is built so "
        "that the difference shows. The mpox counts are confirmed cases, and "
        "the zeros in the death column are published zeros, not blanks; the "
        "World Health Organization attaches a warning to every Congolese "
        "mpox figure it prints, namely that reporting is delayed because "
        "national capacity is absorbed by the Bundibugyo response, so these "
        "are floors. The cholera counts mix suspected, rapid-test-positive "
        "and culture-confirmed cases, as the source does, and cannot be read "
        "as confirmed cases. For poliovirus the emergency committee names "
        "the DR Congo among the countries where both type 1 and type 2 "
        "circulate and gives one type 1 case for 2025, but publishes numeric "
        "type 2 counts only for Nigeria, Ethiopia and Yemen: the dash is the "
        "absence of a published figure, not the absence of the disease. "
        "Measles carries dashes throughout, and the reason is worth stating "
        "plainly. The organisation's measles surveillance figures are served "
        "from an interactive dashboard rather than published as a citable "
        "document, and this page prints nothing it cannot cite. The cells "
        "will be filled on the day a dated, attributable figure exists."),
    "note_fr": (
        "Quatre maladies, quatre états du savoir, et le tableau est bâti "
        "pour que la différence se voie. Les décomptes de mpox sont des cas "
        "confirmés, et les zéros de la colonne des décès sont des zéros "
        "publiés, non des cases vides ; l’Organisation mondiale de la santé "
        "assortit chaque chiffre congolais de mpox qu’elle imprime d’un "
        "avertissement, à savoir que la remontée d’information est retardée "
        "parce que la capacité nationale est absorbée par la riposte "
        "Bundibugyo : ce sont donc des planchers. Les décomptes de choléra "
        "mêlent cas suspects, cas positifs au test rapide et cas confirmés "
        "par culture, comme le fait la source, et ne se lisent pas comme des "
        "cas confirmés. Pour le poliovirus, le comité d’urgence nomme la RD "
        "Congo parmi les pays où circulent les types 1 et 2 et donne un cas "
        "de type 1 pour 2025, mais ne publie de décompte chiffré de type 2 "
        "que pour le Nigeria, l’Éthiopie et le Yémen : le tiret est "
        "l’absence d’un chiffre publié, non l’absence de la maladie. La "
        "rougeole porte des tirets partout, et la raison mérite d’être dite "
        "sans détour. Les chiffres de surveillance de la rougeole de "
        "l’Organisation sont servis par un tableau de bord interactif plutôt "
        "que publiés sous forme de document citable, et cette page "
        "n’imprime rien qu’elle ne puisse citer. Les cases seront remplies "
        "le jour où un chiffre daté et attribuable existera."),
}

DEMO_POPULATION = {
    "name_en": "Population",
    "name_fr": "Démographie",
    "source": WDI + " " + WPP,
    "cols": [["Indicator", "Indicateur"],
             ["Value", "Valeur"],
             ["Reference year", "Année de référence"],
             ["Source", "Source"]],
    "chiffres": [2],
    "rows": [
        [["Total population", "Population totale"],
         109276265, "2024", ["World Bank", "Banque mondiale"]],
        [["Total population", "Population totale"],
         112832473, "2025", ["World Bank", "Banque mondiale"]],
        [["Population growth, per cent a year",
          "Croissance démographique, % par an"],
         3.2, "2025", ["World Bank", "Banque mondiale"]],
        [["Crude birth rate, per thousand",
          "Taux brut de natalité, pour mille"],
         41.31, "2023", ["World Bank", "Banque mondiale"]],
        [["Crude birth rate, per thousand",
          "Taux brut de natalité, pour mille"],
         40.88, "2024", ["World Bank", "Banque mondiale"]],
        [["Net migration", "Solde migratoire"],
         -27309, "2025", ["World Bank", "Banque mondiale"]],
        [["Total fertility rate, children per woman",
          "Indice synthétique de fécondité, enfants par femme"],
         5.8, "2024", ["UN population division",
                       "Division de la population des Nations unies"]],
        [["Median age, years", "Âge médian, années"],
         15.9, "2024", ["UN population division",
                        "Division de la population des Nations unies"]],
        [["Urban share of the population, per cent",
          "Part urbaine de la population, %"],
         45.4, "2026", ["UN population division",
                        "Division de la population des Nations unies"]],
        [["GDP per capita, current $",
          "PIB par habitant, USD courants"],
         806.8, "2025", ["World Bank", "Banque mondiale"]],
    ],
    "note_en": ("A median age of sixteen and a fertility rate near six put "
                "the DRC among the youngest populations on earth, and this "
                "is the demographic transition my third line of research "
                "takes as its object. The arithmetic that follows is "
                "unforgiving: at three per cent a year the population "
                "doubles in twenty-three years, so output must grow by more "
                "than three per cent merely to hold income per head still. "
                "Growth of five to six per cent, which the DRC has recorded, "
                "leaves two to three points of genuine convergence a year, "
                "and no more. The net migration figure is small enough "
                "relative to natural increase to be immaterial to that "
                "arithmetic. The birth rate is the only demographic series "
                "the World Bank tabulates cleanly for the country; the death "
                "rate is not published in a form that could be verified and "
                "is therefore absent."),
    "note_fr": ("Un âge médian de seize ans et une fécondité proche de six "
                "placent la RD Congo parmi les populations les plus jeunes "
                "du monde, et c’est la transition démographique que "
                "prend pour objet mon troisième axe de recherche. "
                "L’arithmétique qui suit ne pardonne pas : à trois pour "
                "cent l’an, la population double en vingt-trois ans, de "
                "sorte que la production doit croître de plus de trois pour "
                "cent pour seulement maintenir le revenu par tête. Une "
                "croissance de cinq à six pour cent, celle qu’a "
                "enregistrée la RD Congo, laisse deux à trois points de "
                "convergence réelle par an, pas davantage. Le solde "
                "migratoire est assez faible au regard de "
                "l’accroissement naturel pour ne rien changer à ce "
                "calcul. Le taux de natalité est la seule série "
                "démographique que la Banque mondiale tabule proprement pour "
                "le pays ; le taux de mortalité n’est pas publié sous "
                "une forme vérifiable et manque donc."),
}


# ----------------------------------------------------------------------
# 8. Structure sectorielle, secteur cle et infrastructures
# ----------------------------------------------------------------------
STR_SECTEURS = {
    "name_en": "Structure of value added",
    "name_fr": "Structure de la valeur ajoutée",
    "source": WDI_VA,
    "cols": [["Sector", "Secteur"],
             ["2015, % of value added", "2015, % de la valeur ajoutée"],
             ["2024, % of value added", "2024, % de la valeur ajoutée"],
             ["Change, points", "Écart, points"]],
    "chiffres": [1, 1, 1],
    "rows": [
        [["Agriculture, forestry and fishing",
          "Agriculture, sylviculture et pêche"], 12.5, 9.6, -2.9],
        [["Industry", "Industrie"], 40.5, 39.9, -0.6],
        [["of which manufacturing", "dont industrie manufacturière"],
         16.8, 8.2, -8.6],
        [["Services", "Services"], 42.4, 46.6, 4.2],
    ],
    "note_en": ("The comparison year is 2015 because the World Bank table "
                "prints 2015 and 2024 and no 2010 column. Two readings "
                "matter here. Industry holds its share, but manufacturing "
                "inside it halves, from a sixth of value added to a "
                "twelfth: the industrial share is mining, and it is mining "
                "that has grown. Services take up the slack. The Bank does "
                "not publish a separate extractive-industries share of "
                "value added, so the key sector of the Congolese economy "
                "cannot be read directly off this table; it is read off "
                "the growth and export tables that follow, where the "
                "extractive figures are published in full. Nominal GDP "
                "went from 40.2 to 71.0 billion dollars over the same "
                "period."),
    "note_fr": ("L’année de comparaison est 2015 parce que le tableau de "
                "la Banque mondiale imprime 2015 et 2024, sans colonne "
                "2010. Deux lectures comptent ici. L’industrie tient sa "
                "part, mais la manufacture qu’elle contient est divisée "
                "par deux, d’un sixième à un douzième de la valeur "
                "ajoutée : la part industrielle, c’est la mine, et c’est "
                "la mine qui a crû. Les services prennent le reste. La "
                "Banque ne publie pas de part propre aux industries "
                "extractives dans la valeur ajoutée : le secteur clé de "
                "l’économie congolaise ne se lit donc pas directement sur "
                "ce tableau, mais sur ceux de la croissance et des "
                "exportations qui suivent, où les chiffres extractifs sont "
                "publiés en entier. Le PIB nominal est passé de 40,2 à "
                "71,0 milliards de dollars sur la même période."),
}

STR_CROISSANCE = {
    "name_en": "Growth by sector: the extractive economy and the rest",
    "name_fr": "Croissance par secteur : l’économie extractive et le reste",
    "source": FMI + " " + BM_MPO,
    "cols": [["Aggregate", "Agrégat"],
             ["2023", "2023"], ["2024", "2024"],
             ["2025", "2025"], ["2026", "2026"]],
    "chiffres": [1, 1, 1, 1],
    "rows": [
        [["Real GDP (IMF)", "PIB réel (FMI)"], 8.5, 6.1, 5.6, 5.3],
        [["Extractive GDP (IMF)", "PIB extractif (FMI)"],
         20.2, 11.9, 10.1, 5.0],
        [["Non-extractive GDP (IMF)", "PIB non extractif (FMI)"],
         3.4, 3.1, 3.1, 5.4],
        [["Agriculture (World Bank)", "Agriculture (Banque mondiale)"],
         "—", 2.2, 2.3, "—"],
        [["Industry (World Bank)", "Industrie (Banque mondiale)"],
         "—", 9.6, 8.6, "—"],
        [["Services (World Bank)", "Services (Banque mondiale)"],
         "—", 1.1, 1.6, "—"],
    ],
    "note_en": ("This is the table that names the key sector. Extractive "
                "activity grows three to six times faster than everything "
                "else, and the gap has been open every year since 2023. "
                "2025 and 2026 are projections, not outturns. The Fund’s "
                "real GDP line reads 5.6 and 5.3 for those two years where "
                "the headline series on this page reads 5.7 and 5.9: the "
                "vintages differ, and neither figure is corrected here to "
                "agree with the other. The Bank’s three lines are real "
                "growth at factor prices and cover 2024 and 2025 only, "
                "which is why the first and last columns carry a dash."),
    "note_fr": ("C’est le tableau qui nomme le secteur clé. L’activité "
                "extractive croît trois à six fois plus vite que tout le "
                "reste, et l’écart est ouvert chaque année depuis 2023. "
                "2025 et 2026 sont des projections, non des réalisations. "
                "La ligne de PIB réel du Fonds donne 5,6 et 5,3 pour ces "
                "deux années là où la série principale de cette page donne "
                "5,7 et 5,9 : les millésimes diffèrent, et aucun des deux "
                "chiffres n’est corrigé ici pour s’accorder à l’autre. Les "
                "trois lignes de la Banque sont des croissances réelles aux "
                "prix des facteurs et ne couvrent que 2024 et 2025, d’où le "
                "tiret dans la première et la dernière colonne."),
}

STR_MINES = {
    "name_en": "Mining output and the extractive share of exports",
    "name_fr": "Production minière et part extractive des exportations",
    "source": USGS + " " + FMI,
    "cols": [["Item", "Poste"], ["2024", "2024"], ["2025", "2025"]],
    "chiffres": [0, 0],
    "rows": [
        [["Copper, mine production, thousand tonnes",
          "Cuivre, production minière, milliers de tonnes"], 2990, 3200],
        [["Copper, refinery production, thousand tonnes",
          "Cuivre, production raffinée, milliers de tonnes"], 2560, 2800],
        [["Cobalt, mine production, tonnes",
          "Cobalt, production minière, tonnes"], 226000, 230000],
        [["Goods exports, $m", "Exportations de biens, millions USD"],
         34927, 36406],
        [["of which extractive, $m", "dont extractif, millions USD"],
         34357, 35717],
    ],
    "note_en": ("The 2025 column is an estimate in the Survey and a "
                "projection in the Fund report; 2024 is an outturn for "
                "mining and preliminary for trade. Two proportions carry "
                "the whole argument of this page. The Survey puts Congolese "
                "cobalt at about seventy-three per cent of world mine "
                "output. The Fund’s trade table puts the extractive share "
                "of goods exports at 98.4 per cent in 2024 and 98.1 per "
                "cent in 2025. Reserves are large enough that neither "
                "figure is about to fall for geological reasons: eighty "
                "million tonnes of copper and six million tonnes of "
                "cobalt."),
    "note_fr": ("La colonne 2025 est une estimation dans la publication du "
                "Survey et une projection dans le rapport du Fonds ; 2024 "
                "est une réalisation pour la mine et un chiffre "
                "provisoire pour le commerce. Deux proportions portent tout "
                "l’argument de cette page. Le Survey situe le cobalt "
                "congolais à environ soixante-treize pour cent de la "
                "production minière mondiale. Le tableau du commerce "
                "extérieur du Fonds situe la part extractive des "
                "exportations de biens à 98,4 pour cent en 2024 et à 98,1 "
                "pour cent en 2025. Les réserves sont assez larges pour "
                "qu’aucun de ces deux chiffres ne baisse pour des raisons "
                "géologiques : quatre-vingts millions de tonnes de cuivre "
                "et six millions de tonnes de cobalt."),
}

STR_EMPLOIS = {
    "name_en": "Employment by sector, modelled estimates",
    "name_fr": "Emploi par secteur, estimations modélisées",
    "source": OIT,
    "cols": [["Sector", "Secteur"],
             ["Men, 2015, %", "Hommes, 2015, %"],
             ["Men, 2019, %", "Hommes, 2019, %"],
             ["Women, 2015, %", "Femmes, 2015, %"],
             ["Women, 2019, %", "Femmes, 2019, %"]],
    "chiffres": [1, 1, 1, 1],
    "rows": [
        [["Agriculture", "Agriculture"], 52.4, 51.4, 68.5, 67.8],
        [["Industry", "Industrie"], 11.9, 11.7, 4.8, 4.8],
        [["Services", "Services"], 35.7, 36.9, 26.7, 27.5],
        [["Vulnerable employment", "Emploi vulnérable"],
         "—", 75.5, "—", 88.7],
    ],
    "note_en": ("These are modelled estimates, not survey readings: the "
                "Labour Organization fits them where a labour force survey "
                "is missing, and the DRC is such a case. They are printed "
                "because nothing better exists, and they should be read as "
                "orders of magnitude. Note the contrast with the value "
                "added table above: mining is the key sector for output "
                "and for exports, industry as a whole employs about one man "
                "in nine and one woman in twenty. Vulnerable employment is "
                "own-account and contributing family work; it is the "
                "nearest published proxy for informality, which is not "
                "published as such for the DRC. The Bank publishes no "
                "combined figure for both sexes."),
    "note_fr": ("Ce sont des estimations modélisées et non des relevés "
                "d’enquête : l’Organisation du travail les ajuste là où "
                "une enquête sur la population active manque, et la RD "
                "Congo est un tel cas. Elles figurent ici parce que rien de "
                "mieux n’existe et elles se lisent comme des ordres de "
                "grandeur. On notera le contraste avec le tableau de la "
                "valeur ajoutée : la mine est le secteur clé pour la "
                "production et pour les exportations, l’industrie tout "
                "entière emploie environ un homme sur neuf et une femme sur "
                "vingt. L’emploi vulnérable réunit les travailleurs à "
                "leur compte et les aides familiaux ; c’est le substitut "
                "publié le plus proche de l’informalité, qui n’est pas "
                "publiée comme telle pour la RD Congo. La Banque ne publie "
                "aucun chiffre réunissant les deux sexes."),
}

STR_INFRA = {
    "name_en": "Infrastructure and access",
    "name_fr": "Infrastructures et accès",
    "source": WDI_INFRA + " " + BM_INGA + " " + BM_ROUTES + " " + BM_EAU,
    "cols": [["Indicator", "Indicateur"],
             ["Value", "Valeur"],
             ["Year", "Année"]],
    "chiffres": [],
    "rows": [
        [["Access to electricity, % of population",
          "Accès à l’électricité, % de la population"], "20,8", "2021"],
        [["Access to electricity, rural, % of population",
          "Accès à l’électricité en milieu rural, % de la population"],
         "≈ 1", "2022"],
        [["Hydropower, % of electricity produced",
          "Hydroélectricité, % de l’électricité produite"],
         "99,6", "2015"],
        [["Inga 1 and 2, installed capacity, MW",
          "Inga 1 et 2, puissance installée, MW"], "1 775", "2025"],
        [["Total road network, km", "Réseau routier total, km"],
         "152 400", "2024"],
        [["Paved share of the national road network, %",
          "Part revêtue du réseau routier national, %"], "2", "2024"],
        [["Individuals using the internet, %",
          "Personnes utilisant internet, %"], "18,0", "2022"],
        [["Population without basic drinking water, %",
          "Population sans eau de boisson de base, %"], "64", "2024"],
        [["Population without basic sanitation, %",
          "Population sans assainissement de base, %"], "84", "2024"],
        [["Population without basic hygiene, %",
          "Population sans hygiène de base, %"], "81", "2024"],
    ],
    "note_en": ("The rural electricity figure is printed as an "
                "approximation because the source words it that way; it is "
                "not rounded here. The Inga line is the installed capacity "
                "of the two existing dams, against a site potential the "
                "Bank puts near forty-two thousand megawatts. Three "
                "quantities that a reader would reasonably expect are "
                "missing and are missing for the same reason: the national "
                "utility publishes no accessible report, so total installed "
                "generating capacity and actual Inga output do not appear; "
                "mobile penetration is no longer carried in the Bank table "
                "and the Telecommunication Union portal serves nothing a "
                "script can read; and the water and sanitation lines are "
                "basic service, not safely managed service, because the "
                "safely managed shares are not published for the DRC."),
    "note_fr": ("Le chiffre rural de l’électricité est imprimé comme une "
                "approximation parce que la source le formule ainsi ; il "
                "n’est pas arrondi ici. La ligne Inga donne la puissance "
                "installée des deux barrages existants, contre un "
                "potentiel du site que la Banque situe près de "
                "quarante-deux mille mégawatts. Trois grandeurs qu’un "
                "lecteur attendrait manquent, et manquent pour la même "
                "raison : la société nationale d’électricité ne publie "
                "aucun rapport accessible, de sorte que la puissance "
                "installée totale et la production effective d’Inga ne "
                "figurent pas ; la pénétration mobile n’est plus portée "
                "par le tableau de la Banque et le portail de l’Union des "
                "télécommunications ne sert rien qu’un programme puisse "
                "lire ; et les lignes d’eau et d’assainissement portent "
                "sur le service de base et non sur le service géré en "
                "toute sécurité, dont les parts ne sont pas publiées pour "
                "la RD Congo."),
}


# ----------------------------------------------------------------------
# 9. Migrations et envois de fonds
# ----------------------------------------------------------------------
MIG_TRANSFERTS = {
    "name_en": "Personal remittances received",
    "name_fr": "Envois de fonds des migrants reçus",
    "source": WDI_ENVOIS,
    "cols": [["Year", "Année"],
             ["$m", "Millions USD"],
             ["% of GDP", "% du PIB"]],
    "chiffres": [0, 1],
    "rows": [
        ["2018", 1823, 3.9],
        ["2019", 2076, 4.4],
        ["2020", 1196, 2.6],
        ["2021", 1348, 2.3],
        ["2022", 3262, 4.6],
        ["2023", 3298, 4.7],
        ["2024", 2001, 2.6],
    ],
    "note_en": ("Remittances are the second largest current inflow after "
                "mineral exports, and at their 2023 peak they were worth "
                "about half of foreign direct investment. The series is "
                "not smooth and this page does not smooth it: it falls by "
                "a third in 2020, roughly triples between 2021 and 2022, "
                "and falls by two fifths again in 2024. The Bank publishes "
                "no revision note that would let a reader say which of the "
                "flow or its measurement changed, so the jumps are printed "
                "as they stand. The figures are Fund balance of payments "
                "data completed by Bank staff estimates, which is to say "
                "that informal transfers, believed to be large in the DRC, "
                "are captured only to the extent that the estimate "
                "captures them."),
    "note_fr": ("Les envois de fonds sont la deuxième entrée courante "
                "après les exportations minières, et à leur sommet de "
                "2023 ils valaient environ la moitié de "
                "l’investissement direct étranger. La série n’est pas "
                "lisse et cette page ne la lisse pas : elle recule d’un "
                "tiers en 2020, à peu près triple entre 2021 et 2022, et "
                "retombe de deux cinquièmes en 2024. La Banque ne publie "
                "aucune note de révision qui permettrait de dire ce qui, "
                "du flux ou de sa mesure, a changé : les sauts sont donc "
                "imprimés tels quels. Les chiffres sont des données de "
                "balance des paiements du Fonds complétées par des "
                "estimations des services de la Banque, c’est-à-dire que "
                "les transferts informels, réputés importants en RD "
                "Congo, n’y sont saisis que dans la mesure où "
                "l’estimation les saisit."),
}

MIG_EMIGRES = {
    "name_en": "Congolese-born people living abroad, 2024",
    "name_fr": "Personnes nées en RD Congo vivant à l’étranger, 2024",
    "source": DESA_MIG,
    "cols": [["Country of residence", "Pays de résidence"],
             ["Number", "Effectif"]],
    "chiffres": [0],
    "rows": [
        [["Uganda", "Ouganda"], 637206],
        [["Rwanda", "Rwanda"], 236385],
        [["Burundi", "Burundi"], 224091],
        [["Congo, Rep.", "Congo (Rép.)"], 168387],
        [["France", "France"], 120178],
        [["South Sudan", "Soudan du Sud"], 97364],
        [["Angola", "Angola"], 93210],
        [["Belgium", "Belgique"], 88896],
        [["Tanzania", "Tanzanie"], 76772],
        [["Zambia", "Zambie"], 67171],
        [["South Africa", "Afrique du Sud"], 57519],
        [["Kenya", "Kenya"], 41186],
        [["Canada", "Canada"], 39790],
        [["All countries", "Tous pays"], 2097387],
    ],
    "note_en": ("The Congolese diaspora numbered 2.10 million in mid-2024, "
                "against 1.92 million in 2020. The thirteen countries "
                "listed hold about ninety-three per cent of it. The "
                "geography deserves a second look: eleven of the thirteen "
                "are African and the four largest are immediate "
                "neighbours, so most Congolese emigration is regional and "
                "much of it is displacement that has settled. France, "
                "Belgium and Canada together hold about a eighth of the "
                "total, which is the part of the diaspora that the "
                "remittance series above mostly reflects."),
    "note_fr": ("La diaspora congolaise comptait 2,10 millions de "
                "personnes à la mi-2024, contre 1,92 million en 2020. Les "
                "treize pays énumérés en portent environ "
                "quatre-vingt-treize pour cent. La géographie mérite un "
                "second regard : onze des treize sont africains et les "
                "quatre premiers sont des voisins immédiats, de sorte que "
                "l’essentiel de l’émigration congolaise est régional et "
                "qu’une bonne part en est un déplacement qui s’est "
                "installé. La France, la Belgique et le Canada réunis en "
                "portent environ un huitième, et c’est cette part de la "
                "diaspora que reflète surtout la série d’envois de fonds "
                "ci-dessus."),
}

MIG_ASILE = {
    "name_en": "Congolese refugees and asylum seekers, by country of asylum",
    "name_fr": "Réfugiés et demandeurs d’asile congolais, par pays d’asile",
    "source": HCR_ODP,
    "cols": [["Country of asylum", "Pays d’asile"],
             ["Number", "Effectif"]],
    "chiffres": [0],
    "rows": [
        [["Uganda", "Ouganda"], 657223],
        [["Burundi", "Burundi"], 109824],
        [["Rwanda", "Rwanda"], 79911],
        [["Tanzania", "Tanzanie"], 77137],
        [["Zambia", "Zambie"], 72258],
        [["Kenya", "Kenya"], 66236],
        [["Malawi", "Malawi"], 41071],
        [["South Africa", "Afrique du Sud"], 39261],
        [["Congo, Rep.", "Congo (Rép.)"], 30973],
        [["Angola", "Angola"], 23078],
        [["South Sudan", "Soudan du Sud"], 14808],
        [["Zimbabwe", "Zimbabwe"], 10419],
        [["All countries recorded", "Tous pays relevés"], 1238409],
    ],
    "note_en": ("Read this table against the one above it. Of the 2.10 "
                "million Congolese living abroad, 1.24 million are "
                "registered as refugees or asylum seekers, and 657 "
                "thousand of those are in Uganda alone: more than half of "
                "the Congolese refugee population is in one country, and "
                "the Ugandan figure comes from the government rather than "
                "from the agency. The portal covers African countries of "
                "asylum only, so the total is a floor and not a world "
                "count. Figures are dated 31 March 2026, except Malawi, "
                "South Sudan and the total, which are dated 30 April "
                "2026."),
    "note_fr": ("Ce tableau se lit contre celui qui le précède. Sur les "
                "2,10 millions de Congolais vivant à l’étranger, 1,24 "
                "million sont enregistrés comme réfugiés ou demandeurs "
                "d’asile, et 657 mille d’entre eux se trouvent en Ouganda "
                "seul : plus de la moitié de la population réfugiée "
                "congolaise tient dans un seul pays, et le chiffre "
                "ougandais provient du gouvernement et non de l’agence. Le "
                "portail ne couvre que les pays d’asile africains : le "
                "total est donc un plancher et non un décompte mondial. "
                "Les chiffres sont arrêtés au 31 mars 2026, sauf le "
                "Malawi, le Soudan du Sud et le total, arrêtés au 30 avril "
                "2026."),
}

MIG_IMMIGRES = {
    "name_en": "Foreign-born people living in the DRC, 2024",
    "name_fr": "Personnes nées à l’étranger vivant en RD Congo, 2024",
    "source": DESA_MIG,
    "cols": [["Country of birth", "Pays de naissance"],
             ["Number", "Effectif"]],
    "chiffres": [0],
    "rows": [
        [["Central African Republic", "République centrafricaine"], 368125],
        [["Rwanda", "Rwanda"], 286208],
        [["Angola", "Angola"], 201592],
        [["South Sudan", "Soudan du Sud"], 103594],
        [["Burundi", "Burundi"], 67352],
        [["Congo, Rep.", "Congo (Rép.)"], 7108],
        [["Uganda", "Ouganda"], 6776],
        [["Sudan", "Soudan"], 6115],
        [["All countries", "Tous pays"], 1085090],
    ],
    "note_en": ("The DRC receives as well as sends. One and a nine tenths "
                "million foreign-born residents is about one per cent of "
                "the population, and 51.8 per cent of them are women. The "
                "stock fell from 754 thousand in 1990 to 590 thousand in "
                "2010 before rising to its present level, which tracks the "
                "conflicts of the neighbours rather than any Congolese "
                "immigration policy. Against a diaspora of 2.10 million, "
                "the country is a net sender by roughly a million people."),
    "note_fr": ("La RD Congo reçoit autant qu’elle envoie. Un million "
                "quatre-vingt-cinq mille résidents nés à l’étranger, "
                "c’est environ un pour cent de la population, et 51,8 pour "
                "cent d’entre eux sont des femmes. Le stock est tombé de "
                "754 mille en 1990 à 590 mille en 2010 avant de remonter à "
                "son niveau actuel, ce qui suit les conflits des voisins "
                "plutôt qu’une quelconque politique congolaise "
                "d’immigration. Face à une diaspora de 2,10 millions, le "
                "pays est émetteur net d’environ un million de "
                "personnes."),
}

MIG_INTERNE = {
    "name_en": "Internal migration: what is published",
    "name_fr": "Migration interne : ce qui est publié",
    "source": DIAL,
    "cols": [["Item", "Élément"],
             ["Value", "Valeur"],
             ["Where", "Où"]],
    "chiffres": [],
    "rows": [
        [["Inter-provincial migration matrix",
          "Matrice des migrations interprovinciales"],
         ["Not published", "Non publiée"],
         ["No census since 1984", "Aucun recensement depuis 1984"]],
        [["Residents who have not always lived in their locality, 2012",
          "Résidents n’ayant pas toujours vécu dans leur localité, 2012"],
         ["18,4 %", "18,4 %"],
         ["Survey 1-2-3, phase 1", "Enquête 1-2-3, phase 1"]],
        [["of which women / men", "dont femmes / hommes"],
         ["19,4 % / 17,3 %", "19,4 % / 17,3 %"],
         ["Survey 1-2-3, phase 1", "Enquête 1-2-3, phase 1"]],
        [["Kinshasa", "Kinshasa"], ["14,8 %", "14,8 %"],
         ["Survey 1-2-3, phase 1", "Enquête 1-2-3, phase 1"]],
        [["Internal migrants of urban / rural origin",
          "Migrants internes d’origine urbaine / rurale"],
         ["47,9 % / 50,8 %", "47,9 % / 50,8 %"],
         ["Survey 1-2-3, phase 1", "Enquête 1-2-3, phase 1"]],
        [["Migrants who came from abroad",
          "Migrants venus de l’étranger"],
         ["1,3 %", "1,3 %"],
         ["Survey 1-2-3, phase 1", "Enquête 1-2-3, phase 1"]],
        [["Latest general population census",
          "Dernier recensement général de la population"],
         ["1984", "1984"],
         ["Institut national de la statistique",
          "Institut national de la statistique"]],
    ],
    "note_en": ("Inter-provincial and intra-provincial migration is the "
                "clearest gap on this page, and it is worth being explicit "
                "about why. A migration matrix needs a census, and the last "
                "scientific census in the DRC was taken in 1984. The "
                "statistical institute’s portal was still marked as under "
                "construction in August 2026 and publishes no library; the "
                "Organization for Migration counts conflict displacement, "
                "which is a different thing and is set out in the security "
                "tab. What survives is the 1-2-3 survey of 2012, which asks "
                "whether a person has always lived where they now live: "
                "about one Congolese in five had not. That is a lifetime "
                "migration rate, not a flow, and it is fourteen years old. "
                "No matrix is constructed here from it, because none can "
                "honestly be."),
    "note_fr": ("La migration interprovinciale et intraprovinciale est la "
                "lacune la plus nette de cette page, et il vaut la peine "
                "de dire pourquoi. Une matrice de migration demande un "
                "recensement, et le dernier recensement scientifique de la "
                "RD Congo date de 1984. Le portail de l’institut national "
                "de la statistique était encore annoncé comme en "
                "construction en août 2026 et ne publie aucune "
                "bibliothèque ; l’Organisation pour les migrations "
                "dénombre les déplacements liés au conflit, ce qui est "
                "autre chose et figure dans l’onglet sécurité. Il reste "
                "l’enquête 1-2-3 de 2012, qui demande si l’enquêté a "
                "toujours vécu là où il vit : environ un Congolais sur "
                "cinq n’y avait pas toujours vécu. C’est un taux de "
                "migration à vie, non un flux, et il a quatorze ans. "
                "Aucune matrice n’en est tirée ici, parce qu’aucune ne "
                "peut honnêtement l’être."),
}


# ----------------------------------------------------------------------
# 10. Corruption et gouvernance
# ----------------------------------------------------------------------
GOUV_CPI = {
    "name_en": "Corruption Perceptions Index, 2019 to 2025",
    "name_fr": "Indice de perception de la corruption, 2019 à 2025",
    "source": TI_SERIE,
    "cols": [["Edition", "Édition"],
             ["Score, out of 100", "Score, sur 100"],
             ["Rank", "Rang"],
             ["Countries ranked", "Pays classés"]],
    "chiffres": [0, 0, 0],
    "rows": [
        ["2019", 18, 168, 180],
        ["2020", 18, 170, 180],
        ["2021", 19, "—", 180],
        ["2022", 20, "—", 180],
        ["2023", 20, "—", 180],
        ["2024", 20, "—", 180],
        ["2025", 20, 163, 182],
    ],
    "note_en": ("The score has moved by two points in seven years and has "
                "not moved at all since 2022, which is the finding: on this "
                "measure nothing has changed. The rank improved from 170th "
                "to 163rd over the same period, but ranks are the weaker "
                "reading, because the number of countries ranked changed "
                "and because a country can rise in the ranking without "
                "improving. The four missing ranks are missing because "
                "Transparency International stopped printing a rank column "
                "in its report from the 2021 edition onward; the ranks "
                "survive only in a spreadsheet this page could not read, "
                "and no rank is reconstructed here."),
    "note_fr": ("Le score a bougé de deux points en sept ans et n’a plus "
                "bougé du tout depuis 2022 : c’est là le constat, rien "
                "n’a changé sur cette mesure. Le rang s’est amélioré de "
                "la 170ᵉ à la 163ᵉ place sur la même période, mais le "
                "rang est la lecture la plus faible, parce que le nombre de "
                "pays classés a changé et parce qu’un pays peut monter au "
                "classement sans s’améliorer. Les quatre rangs manquants "
                "manquent parce que Transparency International a cessé "
                "d’imprimer une colonne de rang dans son rapport à partir "
                "de l’édition 2021 ; les rangs ne subsistent que dans un "
                "classeur que cette page n’a pas pu lire, et aucun rang "
                "n’est reconstitué ici."),
}

GOUV_INDICES = {
    "name_en": "Governance, transparency and the public sector",
    "name_fr": "Gouvernance, transparence et secteur public",
    "source": (TI + " " + CPIA + " " + IIAG + " " + OBS + " " + ITIE_VAL),
    "cols": [["Indicator", "Indicateur"],
             ["Value", "Valeur"],
             ["Source and year", "Source et année"]],
    "chiffres": [],
    "rows": [
        [["Corruption Perceptions Index",
          "Indice de perception de la corruption"],
         ["20 / 100, 163rd of 182", "20 sur 100, 163ᵉ sur 182"],
         ["Transparency International, 2025",
          "Transparency International, 2025"]],
        [["CPIA, overall", "CPIA, note globale"],
         ["3,1 / 6", "3,1 sur 6"],
         ["World Bank, 2024", "Banque mondiale, 2024"]],
        [["CPIA, transparency, accountability and corruption",
          "CPIA, transparence, redevabilité et corruption"],
         ["2,5 / 6", "2,5 sur 6"],
         ["World Bank, 2024", "Banque mondiale, 2024"]],
        [["CPIA, public sector management and institutions",
          "CPIA, gestion et institutions du secteur public"],
         ["2,6 / 6", "2,6 sur 6"],
         ["World Bank, 2024", "Banque mondiale, 2024"]],
        [["Ibrahim index, overall governance",
          "Indice Ibrahim, gouvernance globale"],
         ["32,8 / 100, 48th of 54", "32,8 sur 100, 48ᵉ sur 54"],
         ["Mo Ibrahim Foundation, 2023",
          "Fondation Mo Ibrahim, 2023"]],
        [["Ibrahim index, anti-corruption",
          "Indice Ibrahim, lutte contre la corruption"],
         ["15,8 / 100, 51st", "15,8 sur 100, 51ᵉ"],
         ["Mo Ibrahim Foundation, 2023",
          "Fondation Mo Ibrahim, 2023"]],
        [["Ibrahim index, accountability and transparency",
          "Indice Ibrahim, redevabilité et transparence"],
         ["23,3 / 100, 39th", "23,3 sur 100, 39ᵉ"],
         ["Mo Ibrahim Foundation, 2023",
          "Fondation Mo Ibrahim, 2023"]],
        [["Open Budget Survey, budget transparency",
          "Open Budget Survey, transparence budgétaire"],
         ["41 / 100", "41 sur 100"],
         ["Budget Partnership, 2025",
          "International Budget Partnership, 2025"]],
        [["Open Budget Survey, public participation",
          "Open Budget Survey, participation du public"],
         ["31 / 100", "31 sur 100"],
         ["Budget Partnership, 2025",
          "International Budget Partnership, 2025"]],
        [["Open Budget Survey, budget oversight",
          "Open Budget Survey, contrôle budgétaire"],
         ["52 / 100", "52 sur 100"],
         ["Budget Partnership, 2025",
          "International Budget Partnership, 2025"]],
        [["EITI validation score", "Score de validation ITIE"],
         ["85,5 / 100", "85,5 sur 100"],
         ["EITI Board, October 2022",
          "Conseil de l’ITIE, octobre 2022"]],
        [["Worldwide Governance Indicators, percentile ranks",
          "Indicateurs mondiaux de gouvernance, rangs centiles"],
         ["Discontinued", "Abandonnés"],
         ["World Bank, 2025 revision",
          "Banque mondiale, révision 2025"]],
    ],
    "note_en": ("Four institutions measure roughly the same thing and "
                "agree: the DRC scores between a fifth and a half of the "
                "available marks on every scale in this table. The one "
                "exception is instructive. The country scores 85.5 on the "
                "extractive transparency initiative’s own validation, "
                "which is a high mark, and 41 on budget transparency at "
                "large. Publishing what the mines pay is a solved problem; "
                "publishing what the state does with it is not. The last "
                "line records a methodological loss rather than a "
                "Congolese one: the Bank discontinued percentile ranks in "
                "its 2025 revision of the governance indicators, so the six "
                "familiar percentiles cannot be shown for any country, and "
                "none is estimated here. The Ibrahim edition is dated 2024 "
                "but its reference year is 2023."),
    "note_fr": ("Quatre institutions mesurent à peu près la même chose et "
                "s’accordent : la RD Congo obtient entre un cinquième et "
                "la moitié des points disponibles sur chacune des échelles "
                "de ce tableau. L’unique exception est instructive. Le pays "
                "obtient 85,5 à la validation de l’initiative pour la "
                "transparence des industries extractives, ce qui est une "
                "note élevée, et 41 à la transparence budgétaire "
                "d’ensemble. Publier ce que les mines versent est un "
                "problème résolu ; publier ce que l’État en fait ne "
                "l’est pas. La dernière ligne enregistre une perte "
                "méthodologique et non une perte congolaise : la Banque a "
                "abandonné les rangs centiles dans sa révision 2025 des "
                "indicateurs de gouvernance, de sorte que les six centiles "
                "familiers ne peuvent plus être montrés pour aucun pays, "
                "et qu’aucun n’est estimé ici. L’édition Ibrahim est "
                "datée de 2024 mais son année de référence est 2023."),
}


# ----------------------------------------------------------------------
# 11. Regimes politiques, cycle reel et mesures annoncees
# ----------------------------------------------------------------------
CYCLE_REGIMES = {
    "name_en": "The real cycle by political period",
    "name_fr": "Le cycle réel par période politique",
    "source": AUTEUR_SERIES,
    "cols": [["Period", "Période"],
             ["Years", "Années"],
             ["Mean growth, %", "Croissance moyenne, %"],
             ["Std. dev., points", "Écart-type, points"],
             ["Years of contraction", "Années de recul"],
             ["Median inflation, %", "Inflation médiane, %"]],
    "chiffres": [0, 1, 1, 0, 1],
    "rows": [
        [["Late Mobutu years, 1990-1996",
          "Fin de la période Mobutu, 1990-1996"], 7, -6.3, 5.4, 6, 1987.0],
        [["War and transition, 1997-2000",
          "Guerre et transition, 1997-2000"], 4, -5.9, 2.4, 4, 242.5],
        [["Reconstruction, 2001-2018", "Reconstruction, 2001-2018"],
         18, 5.8, 3.4, 1, 15.8],
        [["Present administration, 2019-2026",
          "Administration actuelle, 2019-2026"], 8, 5.4, 3.2, 0, 9.2],
    ],
    "note_en": ("These are the author’s calculations on the two long "
                "series published on this page, real GDP growth and "
                "consumer price inflation, cut at the political breaks used "
                "by the figure « The real cycle, by political "
                "period » in the stylised facts tab. Three readings. "
                "The first two periods are one long contraction: the "
                "economy loses about six per cent a year for eleven years, "
                "and ten of those eleven years are years of decline. The "
                "turn comes in 2002, not with a change of head of state but "
                "with the end of the war and the resumption of external "
                "financing. Growth since has been of the same order under "
                "two administrations, 5.8 and 5.4 per cent, and the real "
                "difference between them is not the mean but the floor: one "
                "contraction in eighteen years, none in eight. The median "
                "is used for inflation rather than the mean, because a mean "
                "taken across a year at 23 863 per cent describes nothing. "
                "2025 and 2026 are projections."),
    "note_fr": ("Ce sont des calculs de l’auteur sur les deux longues "
                "séries publiées sur cette page, la croissance du PIB "
                "réel et l’inflation des prix à la consommation, "
                "découpées aux ruptures politiques retenues par la figure "
                "« Le cycle réel, par période politique » de "
                "l’onglet des faits stylisés. Trois lectures. Les deux "
                "premières périodes n’en font qu’une, celle d’une "
                "longue contraction : l’économie perd environ six pour "
                "cent par an pendant onze ans, et dix de ces onze années "
                "sont des années de recul. Le retournement vient en 2002, "
                "non avec un changement de chef de l’État mais avec la fin "
                "de la guerre et la reprise des financements extérieurs. "
                "La croissance est depuis du même ordre sous deux "
                "administrations, 5,8 et 5,4 pour cent, et la différence "
                "réelle entre elles n’est pas la moyenne mais le plancher : "
                "un recul en dix-huit ans, aucun en huit. La médiane sert "
                "pour l’inflation plutôt que la moyenne, parce qu’une "
                "moyenne prise sur une année à 23 863 pour cent ne décrit "
                "rien. 2025 et 2026 sont des projections."),
}

MESURES = {
    "name_en": "Measures set out for the authorities, with their deadlines",
    "name_fr": "Mesures énoncées à l’intention des autorités, avec leurs "
               "échéances",
    "source": FMI + " " + BM_MPO,
    "cols": [["Domain", "Domaine"],
             ["Measure as published", "Mesure telle que publiée"],
             ["Quantified target or date", "Cible chiffrée ou échéance"]],
    "chiffres": [],
    "rows": [
        [["Revenue", "Recettes"],
         ["The Fund calls for the revenue mobilisation plan to be "
          "accelerated: mining oversight, digitalisation, a standardised "
          "VAT invoice, a wider base",
          "Le Fonds demande d’accélérer le plan de mobilisation des "
          "recettes : contrôle minier, numérisation, facture normalisée "
          "de TVA, élargissement de l’assiette"],
         ["+0,7 % of GDP in 2026", "+0,7 % du PIB en 2026"]],
        [["Revenue", "Recettes"],
         ["The Fund calls for the tax codes to be completed and provincial "
          "taxation harmonised",
          "Le Fonds demande d’achever les codes fiscaux et d’harmoniser "
          "la fiscalité provinciale"],
         ["End-2026", "Fin 2026"]],
        [["Revenue", "Recettes"],
         ["The Fund calls for fuel pricing reform and the removal of "
          "industrial exemptions and subsidies",
          "Le Fonds demande la réforme du prix des carburants et la "
          "suppression des exonérations et subventions industrielles"],
         ["≈ 280 $m of tax expenditure in 2024",
          "≈ 280 M USD de dépense fiscale en 2024"]],
        [["Public finances", "Finances publiques"],
         ["The Fund calls for a public sector reform strategy and a "
          "national wage policy, urgently",
          "Le Fonds demande sans délai une stratégie de réforme du "
          "secteur public et une politique salariale nationale"],
         ["Wage bill above 50 % of tax revenue",
          "Masse salariale au-dessus de 50 % des recettes fiscales"]],
        [["Public finances", "Finances publiques"],
         ["The Fund calls for the treasury single account and for spending "
          "authorisation to be decentralised to pilot ministries",
          "Le Fonds demande le compte unique du Trésor et la "
          "décentralisation de l’ordonnancement vers des ministères "
          "pilotes"],
         ["February 2026", "Février 2026"]],
        [["Public finances", "Finances publiques"],
         ["The Fund calls for recurrent security spending to leave the "
          "emergency procedure and return to standard procedure",
          "Le Fonds demande que les dépenses de sécurité récurrentes "
          "quittent la procédure d’urgence pour la procédure normale"],
         ["17,4 % of spending under emergency procedure in 2025",
          "17,4 % des dépenses en procédure d’urgence en 2025"]],
        [["Public finances", "Finances publiques"],
         ["The Fund calls for domestic arrears to be certified and tracked "
          "more frequently",
          "Le Fonds demande une certification et un suivi plus fréquents "
          "des arriérés intérieurs"],
         ["4,98 $bn certified, 5,4 % of GDP",
          "4,98 Md USD certifiés, 5,4 % du PIB"]],
        [["Money and reserves", "Monnaie et réserves"],
         ["The Fund calls for a careful, data-dependent easing cycle, held "
          "if the currency depreciates sharply",
          "Le Fonds demande un assouplissement prudent et guidé par les "
          "données, suspendu en cas de forte dépréciation"],
         ["BCC target of 7 % inflation",
          "Cible de 7 % d’inflation de la BCC"]],
        [["Money and reserves", "Monnaie et réserves"],
         ["The Fund calls for faster conversion into dollars of the reserve "
          "requirements held in francs on foreign currency deposits",
          "Le Fonds demande une conversion plus rapide en dollars des "
          "réserves obligatoires détenues en francs sur les dépôts en "
          "devises"],
         ["Above the current 5 % a year",
          "Au-delà des 5 % par an actuels"]],
        [["Governance", "Gouvernance"],
         ["The Fund calls the law creating the economic and financial "
          "criminal court critical, and the anti-corruption bill to be "
          "tabled",
          "Le Fonds juge critique la loi créant la cour pénale économique "
          "et financière, et le dépôt du projet de loi anticorruption"],
         ["June 2026", "Juin 2026"]],
        [["Governance", "Gouvernance"],
         ["The Fund calls exit from the financial action task force grey "
          "list critical to correspondent banking",
          "Le Fonds juge la sortie de la liste grise du GAFI critique pour "
          "les relations de correspondance bancaire"],
         ["No date given", "Sans date"]],
        [["Business climate", "Climat des affaires"],
         ["The Fund calls for the strategic business climate plan, a VAT "
          "refund action plan, and a working tax mediation commission",
          "Le Fonds demande le plan stratégique du climat des affaires, un "
          "plan d’action sur les remboursements de TVA et une commission "
          "de médiation fiscale opérationnelle"],
         ["April, March and June 2026",
          "Avril, mars et juin 2026"]],
        [["Poverty", "Pauvreté"],
         ["The Bank sets out that resource revenue must be allocated more "
          "pro-poor, with more basic services, infrastructure and income "
          "opportunities",
          "La Banque énonce que la rente doit être affectée plus "
          "favorablement aux pauvres, avec davantage de services de base, "
          "d’infrastructures et de sources de revenu"],
         ["79,5 % poor at $3,00 a day by 2028",
          "79,5 % de pauvres à 3,00 USD par jour en 2028"]],
        [["Security", "Sécurité"],
         ["The Bank sets out that governance must be strengthened, conflict "
          "resolved, security restored and illicit resource flows curbed",
          "La Banque énonce qu’il faut renforcer la gouvernance, résoudre "
          "le conflit, rétablir la sécurité et endiguer les flux illicites "
          "de ressources"],
         ["No date given", "Sans date"]],
    ],
    "note_en": ("Nothing in this table is the author’s recommendation. "
                "Each line reports a measure that the Fund or the Bank has "
                "published, in the second review of the credit and "
                "sustainability arrangements of January 2026 and in the "
                "macro poverty outlook of April 2026, and the third column "
                "carries the target or the date the document itself "
                "attaches to it. The two institutions differ in a way worth "
                "seeing. The Fund writes a dated list of procedures; the "
                "Bank writes two sentences, both about who gets the money. "
                "They also differ on the facts: the Bank reads reserves at "
                "three months of imports and calls them stabilising, the "
                "Fund reads 11.7 weeks and calls them below adequate. Same "
                "country, same year, opposite verdict. Their deficit "
                "figures rest on different definitions and are not merged "
                "here."),
    "note_fr": ("Rien dans ce tableau n’est une recommandation de "
                "l’auteur. Chaque ligne rapporte une mesure que le Fonds "
                "ou la Banque a publiée, dans la deuxième revue des accords "
                "de crédit et de durabilité de janvier 2026 et dans les "
                "perspectives macroéconomiques et de pauvreté d’avril "
                "2026, et la troisième colonne porte la cible ou "
                "l’échéance que le document lui-même y attache. Les deux "
                "institutions diffèrent d’une manière qui mérite d’être "
                "vue. Le Fonds écrit une liste datée de procédures ; la "
                "Banque écrit deux phrases, toutes deux sur la question de "
                "savoir à qui va l’argent. Elles diffèrent aussi sur les "
                "faits : la Banque lit les réserves à trois mois "
                "d’importations et les juge stabilisantes, le Fonds lit "
                "11,7 semaines et les juge en deçà du niveau adéquat. Même "
                "pays, même année, verdict inverse. Leurs chiffres de "
                "déficit reposent sur des définitions différentes et ne "
                "sont pas fondus ici."),
}


# ----------------------------------------------------------------------
# L'ordre de lecture : onglets, puis tableaux dans chaque onglet
# ----------------------------------------------------------------------
ONGLETS = [
    {
        "cle": "comptes",
        "titre": ["National and external accounts",
                  "Comptes nationaux et extérieurs"],
        "intertitre": ["The accounts of an open, mineral-dependent economy",
                       "Les comptes d’une économie ouverte et minière"],
        "intro_en": (
            "What follows sets out the Congolese accounts in the order an "
            "open-economy macroeconomist reads them: the level of activity "
            "first, then the external constraint that acts on it. The two "
            "are tied together by a single mechanism. Mineral exports carry "
            "the trade balance; a structural deficit on services, freight "
            "above all, takes back a good part of what the mines bring in; "
            "and what remains, once foreign direct investment and debt "
            "service have passed through, is the room the country actually "
            "has. The tables give the published figures for each of those "
            "steps and state plainly where a published figure does not "
            "exist."),
        "intro_fr": (
            "Ce qui suit dispose les comptes congolais dans l’ordre où "
            "les lit un macroéconomiste de l’économie ouverte : le "
            "niveau d’activité d’abord, puis la contrainte "
            "extérieure qui s’exerce sur lui. Un seul mécanisme les "
            "relie. Les exportations minières portent la balance "
            "commerciale ; un déficit structurel sur les services, le fret "
            "au premier chef, reprend une bonne part de ce que les mines "
            "rapportent ; et ce qui subsiste, une fois passés "
            "l’investissement direct étranger et le service de la "
            "dette, constitue la marge dont le pays dispose réellement. Les "
            "tableaux donnent les chiffres publiés pour chacune de ces "
            "étapes et disent clairement là où aucun chiffre publié "
            "n’existe."),
        "tableaux": [("nat-pib", NAT_PIB),
                     ("ext-paiements", EXT_PAIEMENTS),
                     ("ext-commerce", EXT_COMMERCE),
                     ("ext-composition", EXT_COMPOSITION),
                     ("ext-financement", EXT_FINANCEMENT),
                     ("nat-comptes", NAT_COMPTES)],
    },
    {
        "cle": "budget",
        "titre": ["Public finances and money",
                  "Finances publiques et monnaie"],
        "intertitre": ["The state, the mine and the currency",
                       "L’État, la mine et la monnaie"],
        "intro_en": (
            "The Congolese budget collects about fourteen per cent of "
            "output and spends about seventeen, and between a third and a "
            "half of what it collects comes out of the ground. That single "
            "proportion is why the fiscal stance in the DRC is not chosen "
            "so much as received: it moves with the copper and cobalt "
            "cycle, and the deficit widens when the cycle turns. The "
            "monetary table alongside records the disinflation of 2023 to "
            "2025 and the exchange rate that accompanied it, together with "
            "a dollarisation ratio around ninety per cent which is what "
            "limits the transmission of any policy rate the central bank "
            "sets."),
        "intro_fr": (
            "Le budget congolais prélève quelque quatorze pour cent de la "
            "production et en dépense environ dix-sept, et entre le tiers "
            "et la moitié de ce qu’il prélève sort du sol. Cette seule "
            "proportion explique que l’orientation budgétaire en RD "
            "Congo soit moins choisie que subie : elle suit le cycle du "
            "cuivre et du cobalt, et le déficit se creuse quand le cycle se "
            "retourne. Le tableau monétaire qui l’accompagne enregistre "
            "la désinflation de 2023 à 2025 et le taux de change qui "
            "l’a accompagnée, avec un taux de dollarisation voisin de "
            "quatre-vingt-dix pour cent qui limite la transmission de tout "
            "taux directeur que fixe la banque centrale."),
        "tableaux": [("fin-publiques", FIN_PUBLIQUES),
                     ("fin-extractif", FIN_EXTRACTIF),
                     ("mon-prix-change", MON_PRIX_CHANGE)],
    },
    {
        "cle": "secteurs",
        "titre": ["Sectors, the key sector and infrastructure",
                  "Secteurs, secteur clé et infrastructures"],
        "intertitre": ["Where output comes from and where work is",
                       "D’où vient la production, où est le travail"],
        "intro_en": (
            "A single question runs through the four tables below: which "
            "sector actually drives the Congolese economy? The answer is not "
            "read off the value-added shares, because the national accounts "
            "publish no separate line for the extractive industries. It is "
            "read off the growth table, where the Fund splits extractive from "
            "non-extractive output and the first grows at two to four times "
            "the rate of the second, and off the export table, where minerals "
            "make up more than ninety-eight per cent of goods sold abroad. "
            "The employment table then shows the other half of the picture: "
            "the sector that carries the exports employs about one worker in "
            "nine, while agriculture, which carries almost none of them, "
            "employs one in two. Infrastructure closes the section because it "
            "is the binding constraint both of them run into."),
        "intro_fr": (
            "Une seule question traverse les quatre tableaux qui suivent : "
            "quel secteur entraîne réellement l’économie congolaise ? La "
            "réponse ne se lit pas dans les parts de valeur ajoutée, car les "
            "comptes nationaux ne publient aucune ligne distincte pour les "
            "industries extractives. Elle se lit dans le tableau de "
            "croissance, où le Fonds sépare la production extractive de la "
            "production non extractive et où la première croît deux à quatre "
            "fois plus vite que la seconde, et dans le tableau des "
            "exportations, où les minerais font plus de quatre-vingt-dix-huit "
            "pour cent des biens vendus à l’étranger. Le tableau de "
            "l’emploi montre alors l’autre moitié du tableau : le "
            "secteur qui porte les exportations occupe environ un "
            "travailleur sur neuf, tandis que l’agriculture, qui n’en "
            "porte presque aucune, en occupe un sur deux. Les "
            "infrastructures ferment la section parce qu’elles sont la "
            "contrainte que l’un et l’autre rencontrent."),
        "tableaux": [("str-croissance", STR_CROISSANCE),
                     ("str-secteurs", STR_SECTEURS),
                     ("str-mines", STR_MINES),
                     ("str-emplois", STR_EMPLOIS),
                     ("str-infra", STR_INFRA)],
    },
    {
        "cle": "migrations",
        "titre": ["Migration and remittances",
                  "Migrations et envois de fonds"],
        "intertitre": ["Two million abroad, one million within",
                       "Deux millions dehors, un million dedans"],
        "intro_en": (
            "Some two million Congolese live outside the country and about "
            "the same number of foreigners live inside it, which makes the "
            "DRC one of the few African states that is simultaneously a large "
            "sender, a large host and a large producer of refugees. The "
            "money that follows those people home is now worth two to three "
            "billion dollars a year, of the same order as the entire mining "
            "tax take, and it is counted with far less precision. Internal "
            "movement is the gap in this section, and it is a real one: "
            "there has been no census since 1984, so no inter-provincial "
            "migration matrix exists to be reproduced here."),
        "intro_fr": (
            "Quelque deux millions de Congolais vivent hors du pays et à peu "
            "près autant d’étrangers y vivent, ce qui fait de la RD Congo "
            "l’un des rares États africains à être en même temps un grand "
            "pays de départ, un grand pays d’accueil et un grand "
            "producteur de réfugiés. L’argent qui suit ces personnes "
            "jusqu’au pays vaut aujourd’hui deux à trois milliards de "
            "dollars l’an, du même ordre que la totalité des recettes "
            "minières, et il est compté avec bien moins de précision. Le "
            "mouvement interne est le manque de cette section, et c’est un "
            "manque réel : aucun recensement depuis 1984, donc aucune "
            "matrice de migration interprovinciale à reproduire ici."),
        "tableaux": [("mig-transferts", MIG_TRANSFERTS),
                     ("mig-emigres", MIG_EMIGRES),
                     ("mig-asile", MIG_ASILE),
                     ("mig-immigres", MIG_IMMIGRES),
                     ("mig-interne", MIG_INTERNE)],
    },
    {
        "cle": "social",
        "titre": ["Poverty, development and governance",
                  "Pauvreté, développement et gouvernance"],
        "intertitre": ["What growth has and has not done",
                       "Ce que la croissance a fait et ce qu’elle "
                       "n’a pas fait"],
        "intro_en": (
            "The DRC grew at five to nine per cent a year through most of "
            "the past decade, and four Congolese in five still live below "
            "three dollars a day. The tables below hold those two facts "
            "together, which is the whole difficulty. They also carry an "
            "unusual amount of methodological warning, and deliberately so: "
            "the household surveys behind every poverty figure rest on a "
            "sampling frame drawn from the census of 1984, and no reader "
            "should take a decimal point here as seriously as a decimal "
            "point in the fiscal tables. The last two tables turn to "
            "governance, which belongs here rather than in a section of its "
            "own: a state that scores twenty out of a hundred on perceived "
            "corruption and 2,5 out of 6 on the transparency of its own "
            "public accounts is a state whose spending on health and schools "
            "is worth reading with the same caution as its poverty rate."),
        "intro_fr": (
            "La RD Congo a cru de cinq à neuf pour cent l’an sur "
            "l’essentiel de la dernière décennie, et quatre Congolais "
            "sur cinq vivent toujours sous trois dollars par jour. Les "
            "tableaux qui suivent tiennent ensemble ces deux faits, et "
            "c’est là toute la difficulté. Ils portent aussi une somme "
            "inhabituelle d’avertissements de méthode, et à dessein : "
            "les enquêtes de ménages qui fondent tout chiffre de pauvreté "
            "reposent sur une base de sondage tirée du recensement de 1984, "
            "et nul ne devrait prendre ici une décimale aussi au sérieux "
            "qu’une décimale des tableaux budgétaires. Les deux derniers "
            "tableaux passent à la gouvernance, qui a sa place ici plutôt "
            "que dans une section à elle : un État qui obtient vingt sur "
            "cent en perception de la corruption et 2,5 sur 6 sur la "
            "transparence de ses propres comptes publics est un État dont "
            "la dépense de santé et d’école se lit avec la même prudence "
            "que son taux de pauvreté."),
        "tableaux": [("dev-pauvrete", DEV_PAUVRETE),
                     ("dev-humain", DEV_HUMAIN),
                     ("dev-acces", DEV_ACCES),
                     ("dev-education", DEV_EDUCATION),
                     ("dev-alimentation", DEV_ALIMENTATION),
                     ("gouv-cpi", GOUV_CPI),
                     ("gouv-indices", GOUV_INDICES)],
    },
    {
        "cle": "securite",
        "titre": ["Security and demography", "Sécurité et démographie"],
        "intertitre": ["Displacement, refuge and the age structure",
                       "Déplacements, refuge et structure par âge"],
        "intro_en": (
            "An economist has no business treating armed conflict as an "
            "exogenous shock in a country where it has been continuous for "
            "thirty years. It belongs in the accounts. Displacement removes "
            "labour from where it was productive and rarely returns it, and "
            "the age structure sets how fast output "
            "must grow before income per head moves at all. Every count "
            "below is what a named body was able to document, and none of "
            "them is a total. The distinction matters more here than "
            "anywhere else on this page."),
        "intro_fr": (
            "Un économiste n’a pas à traiter le conflit armé comme un "
            "choc exogène dans un pays où il dure depuis trente ans. Il "
            "relève des comptes. Le déplacement retire de la main-d’"
            "œuvre à l’endroit où elle était productive et l’y ramène "
            "rarement, et la "
            "structure par âge fixe la vitesse à laquelle la production doit "
            "croître avant que le revenu par tête ne bouge. Chaque décompte "
            "ci-dessous est ce qu’un organisme nommé a pu documenter, "
            "et aucun n’est un total. La distinction importe ici plus "
            "que partout ailleurs sur cette page."),
        "tableaux": [("sec-deplacements", SEC_DEPLACEMENTS),
                     ("sec-provinces", SEC_PROVINCES),
                     ("sec-refugies", SEC_REFUGIES),
                     ("sec-violations", SEC_VIOLATIONS),
                     ("demo-population", DEMO_POPULATION)],
    },
    {
        "cle": "sante",
        "titre": ["Health and epidemics", "Santé et épidémies"],
        # Les planches de ce volet sont tracees par tools/gg_inject.py et
        # deposees ici meme, entre l'introduction et les tableaux.
        "figures": "SANTE:FIGS",
        # Seul volet sous veille : ses chiffres vieillissent en dix a quinze
        # jours, au rythme des bulletins de l'Organisation. La page releve
        # d'elle-meme le dernier bulletin cite par ses tableaux et previent
        # le lecteur quand l'Organisation en a publie un plus recent.
        "veille": True,
        "intertitre": ["The seventeenth Ebola outbreak, and what stands "
                       "behind it",
                       "La dix-septième épidémie d’Ebola, et ce qui se "
                       "tient derrière"],
        "intro_en": (
            "An epidemic is an economic event before it is anything else to "
            "an economist: it closes markets, empties health zones of the "
            "people who staffed them, diverts a budget that was thin to "
            "begin with, and does all of this in provinces that were "
            "already the poorest and the least accessible. The outbreak of "
            "Bundibugyo virus disease that began in Mongbwalu in May 2026 "
            "is now the largest Ebola outbreak the country has recorded, "
            "and it is still growing as this is written. The five tables "
            "below hold the surveillance record as published: how the "
            "outbreak has moved from one bulletin to the next, where it "
            "stands today, where it is, where it started, and how it "
            "compares with the sixteen that came before. A sixth table "
            "carries the other diseases under surveillance. Nothing here is "
            "modelled, projected or filled in. Where a figure has not been "
            "published, the cell carries a dash and the note says why, "
            "because for a reader in a ministry or a field office the "
            "difference between a zero and a silence is the whole "
            "difference."),
        "intro_fr": (
            "Une épidémie est d’abord, pour un économiste, un événement "
            "économique : elle ferme des marchés, vide de leur personnel les "
            "zones de santé, détourne un budget qui était déjà mince, et "
            "fait tout cela dans les provinces les plus pauvres et les moins "
            "accessibles. L’épidémie de maladie à virus Bundibugyo partie de "
            "Mongbwalu en mai 2026 est aujourd’hui la plus étendue que le "
            "pays ait enregistrée, et elle croît encore à l’heure où ces "
            "lignes sont écrites. Les cinq tableaux ci-dessous portent le "
            "relevé de surveillance tel qu’il est publié : comment "
            "l’épidémie s’est déplacée d’un bulletin au suivant, où elle en "
            "est aujourd’hui, où elle se trouve, d’où elle est partie, et ce "
            "qu’elle vaut au regard des seize qui l’ont précédée. Un "
            "sixième tableau porte les autres maladies sous surveillance. "
            "Rien ici n’est modélisé, projeté ni comblé. Là où un chiffre "
            "n’a pas été publié, la case porte un tiret et la note dit "
            "pourquoi, car pour un lecteur en ministère ou en bureau de "
            "terrain la différence entre un zéro et un silence est toute la "
            "différence."),
        "tableaux": [("sante-ebola-bulletins", SANTE_EBOLA_BULLETINS),
                     ("sante-ebola-suivi", SANTE_EBOLA_SUIVI),
                     ("sante-ebola-provinces", SANTE_EBOLA_PROVINCES),
                     ("sante-ebola-zones", SANTE_EBOLA_ZONES),
                     ("sante-ebola-histoire", SANTE_EBOLA_HISTOIRE),
                     ("sante-epidemies", SANTE_EPIDEMIES)],
    },
    {
        "cle": "regimes",
        "titre": ["Political regimes and announced measures",
                  "Régimes politiques et mesures annoncées"],
        "intertitre": ["The real cycle, period by period",
                       "Le cycle réel, période par période"],
        "intro_en": (
            "The figure above this section plots real growth and inflation "
            "from 1990 to the present against the political periods; the "
            "first table below states the same thing in numbers. Four "
            "periods, four regimes of the real economy: contraction with "
            "moderate inflation at the end of the Mobutu years, contraction "
            "with hyperinflation through the war, a long reconstruction that "
            "grew at close to six per cent, and the present administration, "
            "which grows about as fast with half the volatility and the "
            "lowest median inflation of the four. The second table sets out "
            "what the authorities have said they will do, as published, with "
            "the figure or the date attached to each measure. It is a record "
            "of commitments, not a list of recommendations, and the "
            "distinction is kept deliberately."),
        "intro_fr": (
            "La figure placée au-dessus de cette section porte la croissance "
            "réelle et l’inflation de 1990 à aujourd’hui sur les "
            "périodes politiques ; le premier tableau ci-dessous dit la "
            "même chose en chiffres. Quatre périodes, quatre régimes de "
            "l’économie réelle : contraction et inflation modérée à la "
            "fin de la période Mobutu, contraction et hyperinflation pendant "
            "la guerre, une longue reconstruction proche de six pour cent, "
            "et l’administration actuelle, qui croît à peu près aussi "
            "vite avec la moitié de la volatilité et la plus faible "
            "inflation médiane des quatre. Le second tableau expose ce que "
            "les autorités ont annoncé, tel que publié, avec le chiffre ou "
            "la date attachés à chaque mesure. C’est un relevé "
            "d’engagements, non une liste de recommandations, et la "
            "distinction est tenue à dessein."),
        "tableaux": [("cycle-regimes", CYCLE_REGIMES),
                     ("mesures", MESURES)],
    },
]

# L'ordre final des onglets de la section, cles existantes comprises.
ORDRE_ONGLETS = [
    ("conjoncture", ["Current readings", "Conjoncture"]),
    ("comptes", ["National and external accounts",
                 "Comptes nationaux et extérieurs"]),
    ("budget", ["Public finances and money", "Finances publiques et monnaie"]),
    ("prix", ["Prices and commodities", "Prix et matières premières"]),
    ("secteurs", ["Sectors, the key sector and infrastructure",
                   "Secteurs, secteur clé et infrastructures"]),
    ("population", ["Population", "Population"]),
    ("migrations", ["Migration and remittances",
                    "Migrations et envois de fonds"]),
    ("social", ["Poverty, development and governance",
                "Pauvreté, développement et gouvernance"]),
    ("securite", ["Security and demography", "Sécurité et démographie"]),
    ("sante", ["Health and epidemics", "Santé et épidémies"]),
    ("regimes", ["Political regimes and announced measures",
                 "Régimes politiques et mesures annoncées"]),
    ("faits", ["Stylised facts", "Faits stylisés"]),
]
