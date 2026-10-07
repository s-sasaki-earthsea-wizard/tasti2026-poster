## TASTI 2026 poster build (A0 portrait, beamerposter)
#
# Requires: TeX Live (latexmk, beamerposter, qrcode), librsvg (rsvg-convert),
#           Python 3 with matplotlib, and poppler (pdftoppm / pdfinfo / pdffonts)
#           for the preview and check targets.

PDF      = poster.pdf
TEX      = poster.tex
THEME    = beamerthemetasti2026.sty

# Hand-drawn figures: every SVG directly under figures/src/ is converted to
# vector PDF. Untranslated Japanese originals live in figures/src/ja/ and are
# deliberately not part of the build.
SVG_SRC  = $(wildcard figures/src/*.svg)
SVG_FIGS = $(patsubst figures/src/%.svg,figures/%.pdf,$(SVG_SRC))

# Figures generated from benchmark numbers by scripts/.
PY_FIGS  = figures/fig2_speedup.pdf

FIGS     = $(SVG_FIGS) $(PY_FIGS)

# Rasterised preview (dpi is low on purpose: A0 at 30 dpi is ~1000 x 1400 px).
PREVIEW_DPI = 30
PREVIEW     = preview/poster.png

## all: Build poster.pdf with latexmk (figures first)
all: $(PDF)

$(PDF): $(TEX) $(THEME) $(FIGS)
	latexmk -pdf -interaction=nonstopmode $(TEX)

## figures: Convert the SVG sources and generate the plotted figures
figures: $(FIGS)

# pdfLaTeX cannot read SVG, so each hand-drawn figure is converted to vector PDF.
figures/%.pdf: figures/src/%.svg
	rsvg-convert -f pdf -o $@ $<

# Generated from the S3 benchmark series (see docs/results.md).
figures/fig2_speedup.pdf: scripts/plot_speedup.py
	python3 scripts/plot_speedup.py -o $@

## preview: Rasterise the poster to preview/poster.png for a quick look
preview: $(PREVIEW)

$(PREVIEW): $(PDF)
	mkdir -p preview
	pdftoppm -png -r $(PREVIEW_DPI) -singlefile $(PDF) preview/poster

## check: Verify page size (A0 = 2384 x 3370 pt) and that every font is embedded
check: $(PDF)
	@pdfinfo $(PDF) | grep -E '^(Pages|Page size)'
	@echo "--- fonts (every row must say 'yes' in the emb column) ---"
	@pdffonts $(PDF)
	@if pdffonts $(PDF) | tail -n +3 | awk '{print $$(NF-4)}' | grep -q no; then \
		echo "ERROR: unembedded font found"; exit 1; fi
	@pages=$$(pdfinfo $(PDF) | awk '/^Pages/{print $$2}'); \
	if [ "$$pages" != "1" ]; then echo "ERROR: poster has $$pages pages"; exit 1; fi
	@echo "OK"

## print: Copy the current PDF to print/poster_<date>.pdf (the one that goes to the printer)
print: check
	cp $(PDF) print/poster_$$(date +%Y-%m-%d).pdf
	@ls -la print/

## clean: Remove LaTeX build artifacts (generated figures are kept)
clean:
	latexmk -C $(TEX)
	rm -rf preview

## distclean: Also remove the generated figures
distclean: clean
	rm -f $(FIGS)

## help: Show this help
help:
	@grep -E '^## ' $(MAKEFILE_LIST) | sed 's/^## //'

.PHONY: all figures preview check print clean distclean help
