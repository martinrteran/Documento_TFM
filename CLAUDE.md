# CLAUDE.md

LaTeX source of a Master's thesis (TFM, Máster en Ingeniería de Sistemas y Control, UCM/UNED): **reactive map-less navigation of an AGV with deep reinforcement learning (PPO) on an occupancy grid, formulated as a POMDP**. The whole document is written in **Spanish academic register**; all prose you add must be in Spanish and match it.

This repo contains only the document. The Python training code (PPO agent, `TrainingManager.py`, `agent.py`, `rewards.py`, `curriculum.py`, …) lives in a separate repo, not here. Ask the user for its path before describing implementation details. Papers and other material sit in the parent folder (`../Articulos`, `../Libros`, `../Arquitectura`).

## Build

Toolchain: MiKTeX on Windows (pdflatex, bibtex, makeglossaries, latexmk all on PATH). Run from the repo root:

```
pdflatex Documento_maestro
bibtex Documento_maestro
makeglossaries Documento_maestro
pdflatex Documento_maestro
pdflatex Documento_maestro
```

- The bibliography uses **natbib + bibtex** (`unsrtnat`, `authoryear`), not biblatex. The biblatex lines in the preamble are commented out, and `Documento_maestro.run.xml` is a leftover.
- The glossary needs `makeglossaries`; `\makeglossaries` is called from `otros/glosario.tex`.
- A clean build currently produces only harmless warnings: `fancyhdr \headheight is too small` and `tracklang` for Spanish. Check the `.log` for `undefined` references or citations after editing.
- `Documento_maestro.pdf` is committed, because `.gitignore` lists `.pdf`, not `*.pdf`. Other build artefacts are ignored.

## Document structure

`Documento_maestro.tex` holds the preamble and the `\include` order. Only these files make up the thesis:

| Part | File |
|---|---|
| Front matter | `otros/portada.tex`, `agradecimientos.tex`, `resumen.tex`, `abstract.tex` (the summaries are still `\lipsum` placeholders) |
| Ch. 1 | `capitulos/1.introduccion.tex`: Motivación, Propuesta y objetivos, Estructura |
| Ch. 2 | `capitulos/fundamentos_teoricos.tex`: RL/MDP, PPO, kinematic models (differential, Ackermann, tricycle). It `\input`s the optional, self-contained `capitulos/fundamentos_redes_memoria.tex` (RNN/GRU); nothing else references it, so removing that one line is safe |
| Ch. 3 | `capitulos/2.estado_del_arte.tex` |
| Ch. 4 | `capitulos/3.materiales_y_metodos.tex`: POMDP formulation, observation/action/reward, architecture (`\label{cap:diseno-arquitectura}`) |
| Ch. 5 | `capitulos/4.resultados.tex`: experimental setup and results |
| Ch. 6 | `capitulos/5.conclusiones.tex`: conclusions by objective and future work (`\label{cap:conclusiones}`) |
| Appendices | `apendice_implementacion.tex` (training-infrastructure details), `apendice_ejemplo.tex` (LaTeX examples left over from the template) |

The file-name numbers do **not** match the chapter numbers, because `fundamentos_teoricos` was inserted as chapter 2.

**Legacy drafts, not compiled. Do not edit them unless asked:** `capitulos/introduccion.tex`, `estado_del_arte.tex`, `metodologia.tex`, `resultados.tex`, `conclusiones.tex`, `configuracion_experimental.tex`; `tesis_agv_nav-v4.tex` and `tesis_agv_nav-v5.tex`, older standalone versions; `references.bib` and `tesis_agv_nav.bib`. They use `\cite{Hu2020}`-style keys that are not in the active bibliography. `Plantilla_TFM.pdf` is the original university template.

## Writing conventions

- **Citations:** use `\citep{...}` for parenthetical citations and `\citet{...}` for narrative ones. Never use bare `\cite`. Keys follow the `authorYEARfirstword` pattern, for example `hu2020deep` or `sivashangaran2023deep`.
- **Bibliography:** only `bibliografia.bib` is active. It is split into commented blocks:
  1. Template entries.
  2. Real articles.
  3. Aliases named after PDF files, for example `state_art_RL.pdf`, kept for old citations in `fundamentos_teoricos.tex`.
  4. `@misc` entries for code files, for example `agent.py` or `rewards.py`, so the text can cite a specific implementation file.

  Add new papers to block 2. Never invent bibliographic data: check it against the source.
- **Cross-references:** use the custom macros `\fig{fig:x}`, which prints "la figura N", and `\eq{eq:x}`, which prints "la ecuación (N)". Elsewhere use `Figura~\ref{}`, `Capítulo~\ref{}` and so on.
- **Babel:** babel runs with `es-tabla`, so tables are captioned "Tabla".
- **Label prefixes:** `sec:`, `fig:`, `tab:`, `eq:`, `apendice:`. Chapter labels mix `chap:` (Ch. 1, Ch. 3) and `cap:` (Ch. 4, Ch. 5), so grep for the existing label before referencing it.
- **Figures and captions:** figures use `[htbp]` and `\centering`. Always give a short optional caption (`\caption[short]{long}`), because the list of figures and the list of tables use the short version.
- **Line wrapping:** match each file. Every chapter file except `fundamentos_teoricos.tex`, plus `apendice_implementacion.tex`, is hard-wrapped at about 75 characters; `fundamentos_teoricos.tex` uses one line per paragraph.
- **Code listings:** use `listings`, which defaults to the `estiloMUICD` style defined in the preamble.

## TikZ figures

Diagrams are TikZ sources in `imagenes/tikz/*.tex` and are `\input` directly inside a `figure` environment. They are not included as images. Notation inside each figure must match the chapter that uses it. The header comment of each figure file names that chapter.

`imagenes/tikz/generar_png.ps1` also exports them to 300-dpi PNGs in `imagenes/`, through the `png-standalone.tex` wrapper (pdflatex + `pdftoppm`):

```
powershell -File imagenes\tikz\generar_png.ps1
```

- Grid figures (`pomdp-escena`, `cinematica-sin-giro`, `cinematica-con-giro`) take axis names through `\ejeH`/`\ejeV`, with defaults set by `\providecommand`. Each one exports in two variants, `_cr` (column/row) and `_xy`.
- Continuous-plane figures (`cinematica-diferencial`, `cinematica-ackermann`) export a single version.
- To add a figure:
  1. Register it in the right hashtable in the script.
  2. Load any new TikZ library in **both** the master preamble and `png-standalone.tex`. The master loads `matrix,chains,positioning,arrows,babel`; the standalone wrapper loads only `arrows,babel`.

## Results figures

The plots of Ch. 5 are vector PDFs in `imagenes/resultados/`, generated from the training code repo's data
(`runs/Test/<N>/episodes.csv`, `plots/evals/eval_<N>_e1000_s0.json`, `maps/*.json`) by
`imagenes/resultados/generar_figuras.py`. Run it with the code repo's virtualenv, which has pandas and
matplotlib:

```
<repo>\.venv\Scripts\python.exe -I imagenes\resultados\generar_figuras.py <repo> . <cache_dir>
```

`<cache_dir>` holds one `.npz` per run so later runs are fast. All labels are in Spanish with decimal commas.

## Project skills

`.claude/skills/` holds thesis-specific skills. All of them write in Spanish.

- Writing chapters: introduction, state of the art, related work.
- Methodology from the RL code.
- Proposing methodology changes from data.
- Searching Scholar, summarising papers, and analysing paper figures.

Use them when a task matches.
