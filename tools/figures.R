# figures.R -- les figures du site, tracees par ggplot2
#
# Lit build/gg/plan.json et les fichiers CSV prepares par tools/gg_prepare.py,
# puis ecrit une image SVG par figure et par langue dans build/gg/svg/.
#
# Le script est volontairement defensif : chaque figure est tracee dans un
# tryCatch, de sorte qu'une serie malformee ne fasse pas tomber les autres.
# Il se termine avec le code 0 des qu'au moins une figure a ete produite.
#
# Dependances : ggplot2, svglite, jsonlite, scales.

suppressPackageStartupMessages({
  library(ggplot2)
  library(svglite)
  library(jsonlite)
  library(scales)
  library(grid)
})

options(stringsAsFactors = FALSE, warn = 1)
try(Sys.setlocale("LC_ALL", "C.UTF-8"), silent = TRUE)

# Racine du depot : le dossier parent de celui qui contient ce script.
# Si l'appel ne passe pas par Rscript, on retombe sur le dossier courant.
arg <- grep("^--file=", commandArgs(trailingOnly = FALSE), value = TRUE)
racine <- if (length(arg))
  dirname(dirname(normalizePath(sub("^--file=", "", arg[1])))) else getwd()
dossier <- file.path(racine, "build", "gg")
sortie  <- file.path(dossier, "svg")
dir.create(sortie, showWarnings = FALSE, recursive = TRUE)

# Deux preparateurs alimentent ce script : gg_prepare.py, qui traite les
# series publiees par le site, et sf_prepare.py, qui construit les planches
# de faits stylises. Chacun ecrit son propre plan ; on les met bout a bout,
# et l'absence de l'un n'empeche pas de tracer l'autre.
plan <- list()
for (nom_plan in c("plan.json", "plan-sf.json")) {
  chemin <- file.path(dossier, nom_plan)
  if (file.exists(chemin))
    plan <- c(plan, fromJSON(chemin, simplifyDataFrame = FALSE,
                             simplifyMatrix = FALSE))
}
if (!length(plan)) {
  cat("aucun plan de figures dans", dossier, "\n")
  quit(status = 1)
}

# ---------------------------------------------------------------------------
# Palette et theme. On reprend le bleu d'Oxford du site, un filet discret et
# une typographie sans empattement, la meme que celle du corps de texte.
# ---------------------------------------------------------------------------
PINE   <- "#002147"
BRASS  <- "#8A6A18"
ENCRE  <- "#22201C"
MUET   <- "#6F6B62"
FILET  <- "#E3DFD4"

theme_wabenga <- function(base = 9.5) {
  theme_minimal(base_size = base, base_family = "sans") +
    theme(
      plot.title       = element_text(face = "bold", colour = PINE,
                                      size = base * 1.28, hjust = 0,
                                      margin = margin(b = 2)),
      plot.subtitle    = element_text(colour = MUET, size = base * 0.94,
                                      hjust = 0, margin = margin(b = 10)),
      plot.caption     = element_text(colour = MUET, size = base * 0.82,
                                      hjust = 0, margin = margin(t = 10)),
      plot.caption.position = "plot",
      plot.title.position   = "plot",
      axis.title.x     = element_text(colour = MUET, size = base * 0.88,
                                      margin = margin(t = 6)),
      axis.title.y     = element_text(colour = MUET, size = base * 0.88,
                                      margin = margin(r = 6)),
      axis.text        = element_text(colour = ENCRE, size = base * 0.86),
      panel.grid.major = element_line(colour = FILET, linewidth = 0.32),
      panel.grid.minor = element_blank(),
      panel.background = element_blank(),
      plot.background  = element_blank(),
      legend.position  = "top",
      legend.justification = "left",
      legend.title     = element_blank(),
      legend.key.height = unit(9, "pt"),
      legend.text      = element_text(colour = ENCRE, size = base * 0.86),
      legend.margin    = margin(b = -2),
      plot.margin      = margin(4, 8, 4, 4)
    )
}

# Un separateur de milliers discret, differencie par langue : espace fine
# insecable et virgule decimale en francais, virgule et point en anglais.
fmt_nombre <- function(fr) {
  scales::label_number(big.mark = if (fr) "\u202f" else ",",
                       decimal.mark = if (fr) "," else ".",
                       accuracy = NULL, drop0trailing = TRUE)
}

lire <- function(fiche) {
  f <- file.path(dossier, fiche$csv)
  if (!file.exists(f)) stop("fichier absent : ", fiche$csv)
  d <- read.csv(f, fileEncoding = "UTF-8", check.names = FALSE)
  if (!nrow(d)) stop("serie vide : ", fiche$csv)
  d
}

champ <- function(fiche, base, fr) {
  v <- fiche[[paste0(base, if (fr) "_fr" else "_en")]]
  if (is.null(v)) "" else as.character(v)
}

# ---------------------------------------------------------------------------
# Les tracés, un par type de figure.
# ---------------------------------------------------------------------------

trace_colonnes_zero <- function(d, fiche, fr) {
  d$signe <- ifelse(d$y >= 0, "haut", "bas")
  ggplot(d, aes(x = x, y = y, fill = signe)) +
    geom_hline(yintercept = 0, colour = ENCRE, linewidth = 0.4) +
    geom_col(width = 0.72, show.legend = FALSE) +
    scale_fill_manual(values = c(haut = fiche$couleur, bas = fiche$couleur2)) +
    scale_x_continuous(breaks = pretty(d$x, n = 8)) +
    scale_y_continuous(labels = fmt_nombre(fr))
}

trace_ligne_log <- function(d, fiche, fr) {
  ggplot(d, aes(x = x, y = y)) +
    geom_line(colour = fiche$couleur, linewidth = 0.7) +
    geom_point(colour = fiche$couleur, size = 1.15) +
    scale_x_continuous(breaks = pretty(d$x, n = 8)) +
    scale_y_log10(labels = fmt_nombre(fr),
                  breaks = c(1, 10, 100, 1000, 10000, 100000, 1000000))
}

trace_aire <- function(d, fiche, fr) {
  ggplot(d, aes(x = x, y = y)) +
    geom_area(fill = fiche$couleur2, alpha = 0.55) +
    geom_line(colour = fiche$couleur, linewidth = 0.75) +
    scale_x_continuous(breaks = pretty(d$x, n = 8)) +
    scale_y_continuous(labels = fmt_nombre(fr))
}

trace_barres_h <- function(d, fiche, fr) {
  chiffres <- if (is.null(fiche$chiffres)) 2 else as.integer(fiche$chiffres)
  d$label <- factor(d$label, levels = unique(d$label[order(d$y)]))
  d$etiq <- formatC(d$y, format = "f", digits = chiffres,
                    big.mark = if (fr) "\u202f" else ",",
                    decimal.mark = if (fr) "," else ".")
  ggplot(d, aes(x = label, y = y)) +
    geom_col(fill = fiche$couleur, width = 0.68) +
    geom_text(aes(label = etiq), hjust = -0.16, size = 2.7, colour = ENCRE) +
    coord_flip(clip = "off") +
    scale_y_continuous(labels = fmt_nombre(fr),
                       expand = expansion(mult = c(0, 0.16)))
}

trace_courbe_cumul <- function(d, fiche, fr) {
  ggplot(d, aes(x = x, y = y)) +
    geom_hline(yintercept = c(50, 80), colour = FILET, linewidth = 0.5,
               linetype = "22") +
    geom_area(fill = fiche$couleur, alpha = 0.13) +
    geom_line(colour = fiche$couleur, linewidth = 0.8) +
    geom_point(colour = fiche$couleur, size = 1.05) +
    scale_x_continuous(breaks = pretty(d$x, n = 8)) +
    scale_y_continuous(labels = fmt_nombre(fr), breaks = seq(0, 100, 20)) +
    coord_cartesian(ylim = c(0, 100))
}

# Les abreviations de mois dependent de la langue du systeme ; on les pose
# nous-memes pour que la version francaise le soit vraiment.
MOIS_FR <- c("janv.", "f\u00e9vr.", "mars", "avr.", "mai", "juin",
             "juil.", "ao\u00fbt", "sept.", "oct.", "nov.", "d\u00e9c.")

etiq_date <- function(fr) {
  function(x) {
    if (!fr) return(format(x, "%b %Y"))
    m <- as.integer(format(x, "%m"))
    out <- paste(MOIS_FR[m], format(x, "%Y"))
    out[is.na(m)] <- ""
    out
  }
}

trace_marches <- function(d, fiche, fr) {
  d$x <- as.Date(d$x)
  # au-dela d'une dizaine de decisions, on laisse ggplot espacer les reperes
  reperes <- if (nrow(d) > 10) waiver() else sort(unique(d$x))
  ggplot(d, aes(x = x, y = y)) +
    geom_step(colour = fiche$couleur, linewidth = 0.8) +
    geom_point(colour = fiche$couleur2, size = 1.6) +
    scale_x_date(labels = etiq_date(fr), breaks = reperes) +
    scale_y_continuous(labels = fmt_nombre(fr))
}

trace_lignes_multi <- function(d, fiche, fr) {
  d$x <- as.Date(d$x)
  noms <- fiche[[if (fr) "series_fr" else "series_en"]]
  if (!is.null(noms)) {
    cles <- names(noms)
    d$serie <- factor(d$serie, levels = cles,
                      labels = unlist(noms[cles], use.names = FALSE))
  }
  ggplot(d, aes(x = x, y = y, colour = serie)) +
    geom_line(linewidth = 0.65) +
    scale_colour_manual(values = c(fiche$couleur, fiche$couleur2, BRASS)) +
    scale_x_date(date_labels = "%Y", date_breaks = "5 years") +
    scale_y_continuous(labels = fmt_nombre(fr))
}

# ---------------------------------------------------------------------------
# Les planches de faits stylises. Elles reprennent la grammaire du dossier
# MODEL_DSGE_RDC : facettes a echelle libre, plages grisees sur les episodes
# de tension, trait de zero appuye sur les series centrees.
# ---------------------------------------------------------------------------

# Les dates arrivent au format aaaa-mm ; on les ramene au premier du mois.
en_date <- function(v) as.Date(paste0(as.character(v), "-01"))

# Les plages grisees, communes a toutes les planches mensuelles.
plages <- function(fiche) {
  b <- fiche$bandes
  if (is.null(b) || !length(b)) return(NULL)
  if (is.matrix(b)) {
    deb <- en_date(b[, 1]); fin <- en_date(b[, 2])
  } else {
    deb <- en_date(vapply(b, function(p) p[[1]], character(1)))
    fin <- en_date(vapply(b, function(p) p[[2]], character(1)))
  }
  annotate("rect", xmin = deb, xmax = fin, ymin = -Inf, ymax = Inf,
           fill = ENCRE, alpha = 0.055)
}

# L'intitule de facette depend de la langue ; on le pose une fois pour toutes
# et on garde l'ordre dans lequel le preparateur a range les panneaux.
panneau <- function(d, fr) {
  v <- if (fr) d$panneau_fr else d$panneau_en
  factor(v, levels = unique(v))
}

THEME_FACETTES <- function() {
  theme(strip.text = element_text(colour = PINE, size = 8.2, hjust = 0,
                                  margin = margin(b = 3)),
        panel.spacing.x = unit(13, "pt"),
        panel.spacing.y = unit(11, "pt"),
        axis.text.x = element_text(size = 7.4),
        axis.text.y = element_text(size = 7.4))
}

trace_facettes_niveaux <- function(d, fiche, fr) {
  d$x <- en_date(d$date)
  d$facette <- panneau(d, fr)
  # Les series positives sont portees en logarithme, comme dans le papier ;
  # l'intitule du panneau le signale deja.
  if (!is.null(d$log)) {
    q <- d$log == 1 & is.finite(d$y) & d$y > 0
    d$y[q] <- log(d$y[q])
    d <- d[!(d$log == 1 & !q), , drop = FALSE]
    d <- droplevels(d)
  }
  ncol <- if (is.null(fiche$colonnes)) 3 else as.integer(fiche$colonnes)
  ggplot(d, aes(x = x, y = y)) +
    plages(fiche) +
    geom_line(colour = PINE, linewidth = 0.52) +
    facet_wrap(~ facette, scales = "free_y", ncol = ncol) +
    scale_x_date(date_labels = "%Y", date_breaks = "3 years") +
    scale_y_continuous(labels = fmt_nombre(fr), n.breaks = 4)
}

trace_facettes_cycles <- function(d, fiche, fr) {
  d$x <- en_date(d$date)
  d$facette <- panneau(d, fr)
  ncol <- if (is.null(fiche$colonnes)) 3 else as.integer(fiche$colonnes)
  ggplot(d, aes(x = x, y = y)) +
    plages(fiche) +
    geom_hline(yintercept = 0, colour = MUET, linewidth = 0.36) +
    geom_area(fill = PINE, alpha = 0.13) +
    geom_line(colour = PINE, linewidth = 0.52) +
    facet_wrap(~ facette, scales = "free_y", ncol = ncol) +
    scale_x_date(date_labels = "%Y", date_breaks = "3 years") +
    scale_y_continuous(labels = fmt_nombre(fr), n.breaks = 4)
}

trace_barres_xcorr <- function(d, fiche, fr) {
  d$facette <- panneau(d, fr)
  d$signe <- ifelse(d$r >= 0, "haut", "bas")
  ncol <- if (is.null(fiche$colonnes)) 4 else as.integer(fiche$colonnes)
  ggplot(d, aes(x = retard, y = r, fill = signe)) +
    geom_hline(yintercept = 0, colour = ENCRE, linewidth = 0.36) +
    geom_vline(xintercept = 0, colour = MUET, linewidth = 0.36,
               linetype = "22") +
    geom_col(width = 0.72, show.legend = FALSE) +
    scale_fill_manual(values = c(haut = PINE, bas = BRASS)) +
    facet_wrap(~ facette, ncol = ncol) +
    scale_x_continuous(breaks = seq(-12, 12, 6)) +
    scale_y_continuous(labels = fmt_nombre(fr), n.breaks = 5)
}

trace_facettes_aires <- function(d, fiche, fr) {
  d$x <- en_date(d$date)
  d$facette <- panneau(d, fr)
  ncol <- if (is.null(fiche$colonnes)) 2 else as.integer(fiche$colonnes)
  ggplot(d, aes(x = x, y = y, fill = couleur, colour = couleur)) +
    plages(fiche) +
    geom_hline(yintercept = 0, colour = MUET, linewidth = 0.36) +
    geom_area(alpha = 0.16, colour = NA) +
    geom_line(linewidth = 0.6) +
    scale_fill_identity() +
    scale_colour_identity() +
    facet_wrap(~ facette, scales = "free_y", ncol = ncol) +
    scale_x_date(date_labels = "%Y", date_breaks = "2 years") +
    scale_y_continuous(labels = fmt_nombre(fr), n.breaks = 4)
}

trace_colonnes_regimes <- function(d, fiche, fr) {
  d$periode <- if (fr) d$regime_fr else d$regime_en
  d$periode <- factor(d$periode, levels = unique(d$periode))
  teintes <- tapply(d$couleur, d$periode, function(v) v[1])
  # Le trait discontinu porte la croissance moyenne de chaque periode.
  moy <- data.frame(
    periode = names(tapply(d$y, d$periode, mean)),
    m       = as.numeric(tapply(d$y, d$periode, mean)),
    x1      = as.numeric(tapply(d$annee, d$periode, min)) - 0.45,
    x2      = as.numeric(tapply(d$annee, d$periode, max)) + 0.45,
    stringsAsFactors = FALSE)
  ggplot(d, aes(x = annee, y = y, fill = periode)) +
    geom_hline(yintercept = 0, colour = ENCRE, linewidth = 0.4) +
    geom_col(width = 0.74) +
    geom_segment(data = moy, inherit.aes = FALSE,
                 aes(x = x1, xend = x2, y = m, yend = m),
                 colour = ENCRE, linewidth = 0.5, linetype = "22") +
    scale_fill_manual(values = teintes) +
    scale_x_continuous(breaks = pretty(d$annee, n = 9)) +
    scale_y_continuous(labels = fmt_nombre(fr)) +
    guides(fill = guide_legend(nrow = 1))
}

trace_barres_h_couleur <- function(d, fiche, fr) {
  d$label <- factor(d$label, levels = unique(d$label[order(d$y)]))
  d$etiq <- formatC(d$y, format = "f", digits = 3,
                    decimal.mark = if (fr) "," else ".")
  ggplot(d, aes(x = label, y = y, fill = couleur)) +
    geom_col(width = 0.68) +
    geom_text(aes(label = etiq), hjust = -0.18, size = 2.55, colour = ENCRE) +
    scale_fill_identity() +
    coord_flip(clip = "off") +
    scale_y_continuous(labels = fmt_nombre(fr),
                       expand = expansion(mult = c(0, 0.18)))
}

trace_barres_v <- function(d, fiche, fr) {
  d$label <- if (fr) d$label_fr else d$label_en
  src <- if (fr) d$src_fr else d$src_en
  d$label <- paste0(d$label, "\n(", src, ")")
  d$label <- factor(d$label, levels = unique(d$label))
  d$etiq <- paste0(formatC(d$y, format = "f", digits = 1,
                           decimal.mark = if (fr) "," else "."), " %")
  ggplot(d, aes(x = label, y = y, fill = couleur)) +
    geom_col(width = 0.6) +
    geom_text(aes(label = etiq), vjust = -0.6, size = 2.9, colour = ENCRE) +
    scale_fill_identity() +
    scale_y_continuous(labels = fmt_nombre(fr),
                       expand = expansion(mult = c(0, 0.14)))
}

trace_barres_empilees <- function(d, fiche, fr) {
  d$poste <- if (fr) d$poste_fr else d$poste_en
  d$poste <- factor(d$poste, levels = rev(unique(d$poste)))
  teintes <- tapply(d$couleur, d$poste, function(v) v[1])
  total <- sum(d$y)
  d$etiq <- paste0(formatC(100 * d$y / total, format = "f", digits = 1,
                           decimal.mark = if (fr) "," else "."), " %")
  ggplot(d, aes(x = factor(annee), y = y, fill = poste)) +
    geom_col(width = 0.46) +
    geom_text(aes(label = etiq), position = position_stack(vjust = 0.5),
              size = 2.7, colour = "white") +
    scale_fill_manual(values = teintes,
                      guide = guide_legend(reverse = TRUE, ncol = 1)) +
    scale_y_continuous(labels = fmt_nombre(fr),
                       expand = expansion(mult = c(0, 0.04)))
}

TRACES <- list(
  colonnes_zero = trace_colonnes_zero,
  ligne_log     = trace_ligne_log,
  aire          = trace_aire,
  barres_h      = trace_barres_h,
  courbe_cumul  = trace_courbe_cumul,
  marches       = trace_marches,
  lignes_multi  = trace_lignes_multi,
  # planches de faits stylises
  facettes_niveaux = trace_facettes_niveaux,
  facettes_cycles  = trace_facettes_cycles,
  barres_xcorr     = trace_barres_xcorr,
  facettes_aires   = trace_facettes_aires,
  colonnes_regimes = trace_colonnes_regimes,
  barres_h_couleur = trace_barres_h_couleur,
  barres_v         = trace_barres_v,
  barres_empilees  = trace_barres_empilees
)

# Retouches propres a certains types de planche. Elles sont posees apres
# theme_wabenga(), qui repose sur un theme complet et effacerait tout
# reglage anterieur.
THEMES <- list(
  facettes_niveaux = THEME_FACETTES(),
  facettes_cycles  = THEME_FACETTES(),
  barres_xcorr     = THEME_FACETTES(),
  facettes_aires   = THEME_FACETTES(),
  barres_v         = theme(axis.text.x = element_text(size = 7.4,
                                                      lineheight = 1.05)),
  barres_empilees  = theme(legend.position = "right",
                           legend.justification = "top",
                           panel.grid.major.x = element_blank())
)

# ---------------------------------------------------------------------------

produites <- 0L
for (fiche in plan) {
  for (fr in c(FALSE, TRUE)) {
    langue <- if (fr) "fr" else "en"
    nom <- file.path(sortie, paste0(fiche$cle, "-", langue, ".svg"))
    res <- tryCatch({
      d <- lire(fiche)
      f <- TRACES[[fiche$type]]
      if (is.null(f)) stop("type de figure inconnu : ", fiche$type)
      p <- f(d, fiche, fr) +
        labs(title    = champ(fiche, "titre", fr),
             subtitle = champ(fiche, "sous", fr),
             x        = champ(fiche, "x", fr),
             y        = champ(fiche, "y", fr),
             caption  = champ(fiche, "source", fr)) +
        theme_wabenga() +
        THEMES[[fiche$type]]
      largeur <- if (is.null(fiche$largeur)) 8.4 else as.numeric(fiche$largeur)
      hauteur <- if (is.null(fiche$hauteur)) 4.6 else as.numeric(fiche$hauteur)
      svglite(nom, width = largeur, height = hauteur,
              bg = "transparent", standalone = FALSE)
      print(p)
      grDevices::dev.off()
      TRUE
    }, error = function(e) {
      cat("  ", fiche$cle, "-", langue, ": abandon (",
          conditionMessage(e), ")\n", sep = "")
      while (grDevices::dev.cur() > 1) grDevices::dev.off()
      if (file.exists(nom)) unlink(nom)
      FALSE
    })
    if (isTRUE(res)) {
      produites <- produites + 1L
      cat("  ", fiche$cle, "-", langue, " : ",
          file.info(nom)$size, " octets\n", sep = "")
    }
  }
}

cat(produites, "images SVG ecrites dans", sortie, "\n")
quit(status = if (produites > 0L) 0 else 1)
