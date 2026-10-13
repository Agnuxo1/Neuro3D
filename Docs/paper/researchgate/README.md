# Neuro3D paper for ResearchGate (13 October 2026)

Manuscript: *Coherent optical learning from 3D scene geometry with certified numerics: a prospective wave test, capacity limits and reproducible evidence*. Sole author: Francisco Angulo de Lafuente (independent researcher). Preprint, not peer reviewed.

## Files

| File | Content |
|---|---|
| `neuro3d_paper.tex` | LaTeX source (article, 11 pt, A4) |
| `neuro3d_paper.bib` | Bibliography (30 entries, each checked against Crossref, DataCite or the arXiv API on 13 October 2026) |
| `neuro3d_paper.bbl` | BibTeX output used by the PDF |
| `neuro3d_paper.pdf` | Compiled paper, 16 pages |
| `figures/` | Copies of the repository data figures (sources below) |
| `logs/` | pdflatex and BibTeX logs of the final build (`pass1-3.out`, `bibtex.out`, `neuro3d_paper.log`, `neuro3d_paper.blg`) |

Figure sources: `Benchmarks/wave-confirmation-c1/results/wave-c1-confirmation.png`, `Benchmarks/wave-confirmation-c1/results/wave-c1-network-regime.png`, `Benchmarks/geometry-capacity-k1/results/ha-k1-capacity.png`, `Docs/closure-20261012/figures/wave-negative.png`, `Docs/closure-20261012/figures/paired-cost.png`, `Docs/closure-20261012/figures/eeg-paired.png`. Figure 1 is a data-free TikZ schematic drawn in the source.

## Build

MiKTeX (`C:/Program Files/MiKTeX/miktex/bin/x64`), standard packages only (lmodern, amsmath, amssymb, geometry, microtype, graphicx, booktabs, tabularx, array, caption, xcolor, siunitx, natbib, tikz, enumitem, hyperref). From this folder:

```sh
export PATH="/c/Program Files/MiKTeX/miktex/bin/x64:$PATH"
pdflatex --disable-installer -interaction=nonstopmode -halt-on-error neuro3d_paper
bibtex neuro3d_paper
pdflatex --disable-installer -interaction=nonstopmode -halt-on-error neuro3d_paper
pdflatex --disable-installer -interaction=nonstopmode -halt-on-error neuro3d_paper
```

`--disable-installer` keeps MiKTeX from opening its on-the-fly package dialog (newtx was not usable here because `xpatch` is not installed). Final build: 16 pages, 0 overfull or underfull boxes, 0 undefined references or citations, 0 BibTeX warnings.

SHA256 of `neuro3d_paper.pdf` (build of 13 October 2026, 04:46 local time):

```
a6fb69213d7830a9f35f7591b919aed53771ad10b21467b8a01946e180a2e9bf
```

A rebuild produces a PDF with a different hash because pdflatex embeds the creation date; the text and layout are unchanged.

## Evidence sources

All numbers come from `Docs/paper/optic_neuro_blender_reproducible_draft_2026-10-13_v3.md`, `Benchmarks/wave-confirmation-c1/RESULTS-WAVE-C1.md` (including its dated corrections), `Benchmarks/geometry-capacity-k1/RESULTS-HA-K1.md`, `Benchmarks/compiled-operator-g1/RESULTS-G1.md`, `Docs/closure-20261012/CLAIMS.md`, `Docs/closure-20261012/claude/RED-TEAM-WAVE-C1-LEAN.md`, `Docs/closure-20261012/claude/CLAUDE-CLOSURE-REPORT-20261013.md` and `Lean/closure-core/`. The EEGNet comparison (H2) is reported as pending: no `RESULTS-EEGNET-GPU-H2.md` existed when the PDF was built.

## Plain-language summary for the ResearchGate description field (150 words)

This preprint describes Neuro3D, a software experiment that turns a 3D scene built in Blender into a simulated optical classifier: light paths between mirrors and beam splitters carry the computation, and moving 16 pairs of mirrors trains it. Every number is checked: the geometry is captured exactly, interval arithmetic bounds the rounding errors, and the key lemmas are verified with the Lean theorem prover. The classifier answers 27 of 30 test flowers correctly on the classic Iris data, but it is not better than simple standard methods on wine data, and the graphics-card versions were not faster overall. A preregistered test with an independent wave solver confirmed when the simple light-path model is valid and showed that the captured scene lies far outside that range, so it is not a physical device design. The scene also limits what the classifier can learn. Code, protocols and negative results are public.
