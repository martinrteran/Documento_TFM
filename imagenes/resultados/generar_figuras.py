"""Figuras del capítulo de resultados del TFM (etiquetas en español).

Lee los datos del repositorio de código sin modificarlo:
  runs/Test/<N>/episodes.csv      (métricas por episodio, formato largo tag,step,value)
  plots/evals/eval_<N>_e1000_s0.json  (evaluación greedy / sampled)
  maps/*.json                     (mapas)
y guarda PDF vectoriales en <doc>/imagenes/resultados/.

Uso: python -I res_figs.py <repo> <doc> <cache_dir>
"""
import json
import sys
from pathlib import Path

import numpy as np
import pandas as pd
import matplotlib
matplotlib.use("Agg")
import matplotlib.pyplot as plt

REPO = Path(sys.argv[1])
DOC = Path(sys.argv[2])
CACHE = Path(sys.argv[3])
OUT = DOC / "imagenes" / "resultados"
OUT.mkdir(parents=True, exist_ok=True)
CACHE.mkdir(parents=True, exist_ok=True)

N_EP = 40000
TAGS = {
    "success": "Success/Episode",
    "hit": "Done/Hit Obstacle",
    "maxsteps": "Done/Max Steps Reached",
    "steps": "Steps/Episode",
    "ratio": "Steps/Ratio/Episode",
    "entropy": "Agent/Entropy",
    "qmean": "Agent/Q/Mean",
    "kl": "Agent/PPO/ApproxKL",
    "updates": "Agent/PPO/Updates",
    "map_simple": "Success/Map/simple_map",
    "map_free": "Success/Map/obstacle_free_map",
    "map_1": "Success/Map/1_obstacle",
    "map_4": "Success/Map/4_obstacles",
}

SEEDS = {
    "31": ["31", "311", "312", "313", "314"],
    "35": ["35", "351", "352", "353", "354"],
    "40": ["40", "401", "402", "403", "404"],
    "41": ["41", "411", "412", "413", "414"],
    "42": ["42", "421", "422", "423", "424"],
    "43": ["43", "431", "432", "433", "434"],
}

plt.rcParams.update({
    "font.size": 9, "axes.titlesize": 9.5, "axes.labelsize": 9, "legend.fontsize": 8,
    "xtick.labelsize": 8, "ytick.labelsize": 8, "axes.grid": True, "grid.alpha": 0.3,
    "pdf.fonttype": 42, "savefig.bbox": "tight", "savefig.pad_inches": 0.02,
    "axes.formatter.use_locale": False,
})
W = 6.5  # ancho de texto en pulgadas

COL = {
    "25": "#264653", "28": "#e76f51", "29": "#2a9d8f", "31": "#264653", "32": "#e9c46a",
    "35": "#e76f51", "36": "#8ab17d", "39": "#b5838d", "40": "#2a9d8f", "41": "#e9c46a",
    "42": "#7b5ea7", "43": "#8d99ae",
}
NAME = {
    "25": "25 PPOAgent", "28": "28 GRU", "29": "29 GRU corregida",
    "31": "31 PPOAgent + máscara", "32": "32 progreso con signo",
    "35": "35 PPOAgent + máscara + desplazamiento", "36": "36 Double DQN + máscara",
    "39": "39 Double DQN, lr $10^{-4}$", "40": "40 Double DQN + máscara + desplazamiento",
    "41": "41 PPO estándar", "42": "42 PPO estándar + KL objetivo", "43": "43 PPO estándar + KL + entropía 0,02",
}
SHORT = {
    "31": "31 PPOAgent", "35": "35 PPOAgent + desplaz.", "40": "40 DQN + desplaz.",
    "41": "41 PPO estándar", "42": "42 + KL objetivo", "43": "43 + entropía 0,02",
}


def comma(ax, axis="y", decimals=None):
    """Coma decimal en los ejes."""
    from matplotlib.ticker import FuncFormatter

    def f(v, _):
        if decimals is None:
            s = f"{v:g}"
        else:
            s = f"{v:.{decimals}f}"
        return s.replace(".", ",")
    fmt = FuncFormatter(f)
    if axis in ("y", "both"):
        ax.yaxis.set_major_formatter(fmt)
    if axis in ("x", "both"):
        ax.xaxis.set_major_formatter(fmt)


def thousands(ax):
    from matplotlib.ticker import FuncFormatter
    ax.xaxis.set_major_formatter(FuncFormatter(lambda v, _: f"{int(v):,}".replace(",", " ")))


def load(test: str) -> dict:
    """Series por episodio de una ejecución (con caché npz)."""
    cache = CACHE / f"{test}.npz"
    if cache.exists():
        z = np.load(cache)
        return {k: z[k] for k in z.files}
    df = pd.read_csv(REPO / "runs" / "Test" / test / "episodes.csv")
    out = {}
    for key, tag in TAGS.items():
        s = df[df.tag == tag]
        if s.empty:
            continue
        if key.startswith("map_"):
            out[key] = s.sort_values("step").value.to_numpy(dtype=float)  # episodios de ese mapa
            out[key + "_ep"] = s.sort_values("step").step.to_numpy(dtype=float)
        else:
            arr = np.full(N_EP, np.nan)
            st = s.step.to_numpy()
            ok = st < N_EP
            arr[st[ok]] = s.value.to_numpy(dtype=float)[ok]
            out[key] = arr
    np.savez_compressed(cache, **out)
    return out


def roll(x, w):
    return pd.Series(x).rolling(w, min_periods=max(1, w // 10)).mean().to_numpy()


def roll_median(x, w):
    return pd.Series(x).rolling(w, min_periods=max(1, w // 10)).median().to_numpy()


def group(tests, key, w=1000, median=False):
    rs = []
    for t in tests:
        d = load(t)
        if key not in d:
            return None
        rs.append(roll_median(d[key], w) if median else roll(d[key], w))
    m = np.vstack(rs)
    return np.nanmean(m, 0), np.nanmin(m, 0), np.nanmax(m, 0)


def map_curve(test, key, w=250):
    d = load(test)
    return d[key + "_ep"], roll(d[key], w)


def ev(test):
    return json.loads((REPO / "plots" / "evals" / f"eval_{test}_e1000_s0.json").read_text())


MAPS_EVAL = [("obstacle_free_map", "Sin obstáculos"), ("1_obstacle", "1 obstáculo"),
             ("4_obstacles", "4 obstáculos"), ("simple_map", "Simple")]


def eval_rates(test, mode):
    """Éxito (%) por mapa y total, y número de bucles."""
    e = ev(test)[mode]
    rates, tot_s, tot_n = {}, 0, 0
    for m, _ in MAPS_EVAL:
        c = e["per_map"].get(m, {})
        n = sum(c.values())
        s = c.get("success", 0)
        rates[m] = 100 * s / n
        tot_s += s
        tot_n += n
    rates["total"] = 100 * tot_s / tot_n
    return rates, e.get("timeout_loops", 0)


x_ep = np.arange(N_EP)

# ---------------------------------------------------------------------------
# Figura 1: mapas
# ---------------------------------------------------------------------------
sys.path.insert(0, str(REPO / "src"))
from tfm_control_ucm.core.grid_env.map import GridMap  # noqa: E402

fig, axes = plt.subplots(1, 4, figsize=(W, 2.45), gridspec_kw={"width_ratios": [40, 40, 60, 40]})
for ax, (f, title) in zip(axes, [("map_obstacle_free", "Sin obstáculos"), ("map_1_obstacle", "1 obstáculo"),
                                 ("map_4_square_obstacle", "4 obstáculos"), ("map_simple", "Simple")]):
    g = np.asarray(GridMap.load(str(REPO / "maps" / f"{f}.json")).grid) != 0
    ax.imshow(g, cmap="Greys", vmin=0, vmax=1.25, interpolation="nearest")
    ax.set_title(f"{title}\n{g.shape[1]}$\\times${g.shape[0]}, {int(g.sum())} celdas", fontsize=8.5)
    ax.set_xticks([]); ax.set_yticks([]); ax.grid(False)
    for s in ax.spines.values():
        s.set_linewidth(1.2)
fig.tight_layout(w_pad=0.6)
fig.savefig(OUT / "mapas.pdf"); plt.close(fig)

# ---------------------------------------------------------------------------
# Figura 2: test 25, finales de episodio y éxito por mapa
# ---------------------------------------------------------------------------
d = load("25")
fig, (a, b) = plt.subplots(1, 2, figsize=(W, 2.5))
a.plot(x_ep, 100 * roll(d["success"], 1000), color="#2a9d8f", label="Éxito")
a.plot(x_ep, 100 * roll(d["hit"], 1000), color="#e76f51", label="Choque")
a.plot(x_ep, 100 * roll(d["maxsteps"], 1000), color="#e9c46a", label="Límite de pasos")
a.set_xlabel("Episodio"); a.set_ylabel("Episodios (%)"); a.set_ylim(0, 100)
a.set_title("Final de los episodios (media móvil de 1000)"); a.legend(loc="center right"); thousands(a)
for key, lab, c in [("map_free", "Sin obstáculos", "#264653"), ("map_1", "1 obstáculo", "#2a9d8f"),
                    ("map_4", "4 obstáculos", "#e9c46a"), ("map_simple", "Simple", "#e76f51")]:
    ep, r = map_curve("25", key)
    b.plot(ep, 100 * r, color=c, label=lab)
b.set_xlabel("Episodio"); b.set_ylabel("Éxito (%)"); b.set_ylim(0, 100)
b.set_title("Éxito por mapa (media móvil de 250)"); b.legend(loc="lower right"); thousands(b)
fig.tight_layout(); fig.savefig(OUT / "test25_entrenamiento.pdf"); plt.close(fig)

# ---------------------------------------------------------------------------
# Figura 3: memoria recurrente (25, 28, 29)
# ---------------------------------------------------------------------------
fig, (a, b) = plt.subplots(1, 2, figsize=(W, 2.5))
for t in ["25", "28", "29"]:
    d = load(t)
    r = 100 * roll(d["success"], 1000)
    a.plot(x_ep, r, color=COL[t], label=NAME[t])
    b.plot(np.nancumsum(d["steps"]) / 1e6, r, color=COL[t], label=NAME[t])
a.set_xlabel("Episodio"); a.set_title("Éxito frente a episodios"); thousands(a)
b.set_xlabel("Pasos de entorno (millones)"); b.set_title("Éxito frente a pasos de entorno")
for ax in (a, b):
    ax.set_ylabel("Éxito (%)"); ax.set_ylim(0, 100)
comma(b, "x")
h, l = a.get_legend_handles_labels()
fig.legend(h, l, loc="lower center", ncol=3, bbox_to_anchor=(0.5, -0.01), frameon=False)
fig.tight_layout(rect=(0, 0.08, 1, 1)); fig.savefig(OUT / "gru_entrenamiento.pdf"); plt.close(fig)

# ---------------------------------------------------------------------------
# Figura 4: máscara (25, 31 con 5 semillas, 32)
# ---------------------------------------------------------------------------
fig, (a, b) = plt.subplots(1, 2, figsize=(W, 2.5))
d = load("25")
a.plot(x_ep, 100 * roll(d["success"], 1000), color=COL["25"], label="25 sin máscara")
m, lo, hi = group(SEEDS["31"], "success")
a.plot(x_ep, 100 * m, color="#e76f51", label="31 máscara (5 semillas)")
a.fill_between(x_ep, 100 * lo, 100 * hi, color="#e76f51", alpha=0.25, lw=0)
d = load("32")
a.plot(x_ep, 100 * roll(d["success"], 1000), color="#2a9d8f", label="32 máscara, progreso con signo", lw=1)
a.set_title("Éxito total (media móvil de 1000)")
ep, r = map_curve("25", "map_simple")
b.plot(ep, 100 * r, color=COL["25"], label="25 sin máscara")
curves = [map_curve(t, "map_simple") for t in SEEDS["31"]]
grid = np.arange(0, N_EP, 50)
interp = np.vstack([np.interp(grid, e, rr) for e, rr in curves])
b.plot(grid, 100 * interp.mean(0), color="#e76f51", label="31 máscara (5 semillas)")
b.fill_between(grid, 100 * interp.min(0), 100 * interp.max(0), color="#e76f51", alpha=0.25, lw=0)
ep, r = map_curve("32", "map_simple")
b.plot(ep, 100 * r, color="#2a9d8f", label="32 máscara, progreso con signo", lw=1)
b.set_title("Éxito en el mapa simple (media móvil de 250)")
for ax in (a, b):
    ax.set_xlabel("Episodio"); ax.set_ylabel("Éxito (%)"); ax.set_ylim(0, 100); ax.legend(loc="lower right")
    thousands(ax)
fig.tight_layout(); fig.savefig(OUT / "mascara_entrenamiento.pdf"); plt.close(fig)

# ---------------------------------------------------------------------------
# Figura 5: evaluación greedy / sampled de la secuencia de tests (semilla 0)
# ---------------------------------------------------------------------------
seq = ["25", "28", "29", "31", "32", "35", "36", "37", "38", "39", "40", "41", "42", "43"]
fig, (a, b) = plt.subplots(1, 2, figsize=(W, 2.6), gridspec_kw={"width_ratios": [1.2, 1]})
xs = np.arange(len(seq))
g = [eval_rates(t, "greedy") for t in seq]
s = [eval_rates(t, "sampled") for t in seq]
a.bar(xs - 0.2, [r["total"] for r, _ in g], 0.4, color="#264653", label="Greedy")
a.bar(xs + 0.2, [r["total"] for r, _ in s], 0.4, color="#e9c46a", label="Sampled")
a.set_ylim(50, 100); a.set_ylabel("Éxito total (%)"); a.set_title("Éxito en evaluación (semilla 0)")
b.bar(xs - 0.2, [l for _, l in g], 0.4, color="#264653", label="Greedy")
b.bar(xs + 0.2, [l for _, l in s], 0.4, color="#e9c46a", label="Sampled")
b.set_ylabel("Bucles por cada 1000 episodios"); b.set_title("Bucles en evaluación (semilla 0)")
for ax in (a, b):
    ax.set_xticks(xs); ax.set_xticklabels(seq, fontsize=7.5); ax.set_xlabel("Test")
    ax.axvspan(5.5, 10.5, color="0.88", zorder=0, lw=0)
h, l = a.get_legend_handles_labels()
from matplotlib.patches import Patch  # noqa: E402
h.append(Patch(color="0.88")); l.append("Tests DQN (36 a 40)")
fig.legend(h, l, loc="lower center", ncol=3, bbox_to_anchor=(0.5, -0.01), frameon=False)
fig.tight_layout(rect=(0, 0.08, 1, 1)); fig.savefig(OUT / "evaluacion_tests.pdf"); plt.close(fig)

# ---------------------------------------------------------------------------
# Figura 6: DQN frente a PPOAgent (entrenamiento y Q medio)
# ---------------------------------------------------------------------------
fig, (a, b) = plt.subplots(1, 2, figsize=(W, 2.5))
for key, lab in [("35", NAME["35"]), ("40", NAME["40"])]:
    m, lo, hi = group(SEEDS[key], "success")
    a.plot(x_ep, 100 * m, color=COL[key], label=key + (" PPOAgent (5 semillas)" if key == "35" else " Double DQN (5 semillas)"))
    a.fill_between(x_ep, 100 * lo, 100 * hi, color=COL[key], alpha=0.25, lw=0)
d = load("36")
a.plot(x_ep, 100 * roll(d["success"], 1000), color=COL["36"], lw=1, label="36 Double DQN sin desplaz.")
a.set_xlabel("Episodio"); a.set_ylabel("Éxito (%)"); a.set_ylim(0, 100); thousands(a)
a.set_title("Éxito en entrenamiento (media móvil de 1000)"); a.legend(loc="lower right")
lim = 5000
for t in ["36", "39", "40"]:
    d = load(t)
    b.plot(x_ep[:lim], roll(d["qmean"], 50)[:lim], color=COL[t], label=NAME[t].split(" + ")[0] if t != "40" else "40 Double DQN + desplaz.")
b.axhline(30, color="k", ls="--", lw=0.8)
b.text(lim * 0.98, 30.8, "cota aproximada del retorno", ha="right", va="bottom", fontsize=7.5)
b.set_xlabel("Episodio"); b.set_ylabel("Q medio del lote"); thousands(b)
b.set_title("Q medio en los primeros 5000 episodios"); b.legend(loc="lower right")
fig.tight_layout(); fig.savefig(OUT / "dqn_entrenamiento.pdf"); plt.close(fig)

# ---------------------------------------------------------------------------
# Figura 7: PPO estándar (entropía y KL aproximado)
# ---------------------------------------------------------------------------
fig, (a, b) = plt.subplots(1, 2, figsize=(W, 2.5))
for t in ["35", "41", "42", "43"]:
    m, lo, hi = group(SEEDS[t], "entropy", w=500)
    a.plot(x_ep, m, color=COL[t], label=SHORT[t])
    a.fill_between(x_ep, lo, hi, color=COL[t], alpha=0.2, lw=0)
a.set_xlabel("Episodio"); a.set_ylabel("Entropía (nats)"); a.set_ylim(0, 1.0); thousands(a)
a.set_title("Entropía de la política (5 semillas)"); a.legend(loc="upper right"); comma(a)
for t in ["41", "42", "43"]:
    rs = []
    for run in SEEDS[t]:
        d = load(run)
        kl = d["kl"].copy()
        upd = d["updates"]
        new = np.r_[False, np.diff(upd) > 0]  # episodios en los que hubo una actualización nueva
        kl[~new] = np.nan
        rs.append(pd.Series(kl).rolling(2000, min_periods=20).mean().to_numpy())
    b.plot(x_ep, np.nanmean(np.vstack(rs), 0), color=COL[t], label=SHORT[t])
b.axhline(0.015, color="k", ls="--", lw=0.8)
b.text(N_EP * 0.98, 0.0165, "KL objetivo 0,015", ha="right", va="bottom", fontsize=7.5)
b.set_xlabel("Episodio"); b.set_ylabel("KL aproximado por actualización"); thousands(b); comma(b)
b.set_ylim(0, None)
b.set_title("KL aproximado (5 semillas)"); b.legend(loc="upper right")
fig.tight_layout(); fig.savefig(OUT / "ppo_estandar_entropia_kl.pdf"); plt.close(fig)

# ---------------------------------------------------------------------------
# Figura 8: resumen de evaluación de los seis grupos de 5 semillas
# ---------------------------------------------------------------------------
groups = ["31", "35", "40", "41", "42", "43"]
gcol = {"31": "#264653", "35": "#e76f51", "40": "#2a9d8f", "41": "#e9c46a", "42": "#7b5ea7", "43": "#8d99ae"}
cats = [m for m, _ in MAPS_EVAL] + ["total"]
clab = [l for _, l in MAPS_EVAL] + ["Total"]
fig = plt.figure(figsize=(W, 4.6))
gs = fig.add_gridspec(2, 3, height_ratios=[1, 1], width_ratios=[1, 1, 0.75])
ax_g = fig.add_subplot(gs[0, :]); ax_s = fig.add_subplot(gs[1, :2]); ax_l = fig.add_subplot(gs[1, 2])
wbar = 0.13
for k, t in enumerate(groups):
    for mode, ax in [("greedy", ax_g), ("sampled", ax_s)]:
        vals = np.array([[eval_rates(r, mode)[0][c] for c in cats] for r in SEEDS[t]])
        xpos = np.arange(len(cats)) + (k - 2.5) * wbar
        ax.bar(xpos, vals.mean(0), wbar, yerr=vals.std(0, ddof=1), color=gcol[t], label=SHORT[t],
               error_kw={"lw": 0.7, "capsize": 1.5})
        for j in range(len(cats)):
            ax.scatter(np.full(len(vals), xpos[j]), vals[:, j], s=2, color="k", zorder=3)
    for j, mode in enumerate(["greedy", "sampled"]):
        loops = np.array([eval_rates(r, mode)[1] for r in SEEDS[t]])
        xpos = j + (k - 2.5) * wbar
        ax_l.bar(xpos, loops.mean(), wbar, yerr=loops.std(ddof=1), color=gcol[t], error_kw={"lw": 0.7, "capsize": 1.5})
        ax_l.scatter(np.full(len(loops), xpos), loops, s=2, color="k", zorder=3)
for ax, title in [(ax_g, "Evaluación greedy"), (ax_s, "Evaluación sampled")]:
    ax.set_xticks(np.arange(len(cats))); ax.set_xticklabels(clab); ax.set_ylim(50, 101)
    ax.set_ylabel("Éxito (%)"); ax.set_title(title)
ax_l.set_xticks([0, 1]); ax_l.set_xticklabels(["Greedy", "Sampled"]); ax_l.set_ylabel("Bucles por 1000 episodios")
ax_l.set_title("Bucles")
h, l = ax_g.get_legend_handles_labels()
fig.legend(h, l, loc="lower center", ncol=6, bbox_to_anchor=(0.5, -0.01), frameon=False, fontsize=7.5,
           handlelength=1.2, columnspacing=1.0)
fig.tight_layout(rect=(0, 0.05, 1, 1)); fig.savefig(OUT / "resumen_evaluacion.pdf"); plt.close(fig)

# ---------------------------------------------------------------------------
# Figura 9: resumen de entrenamiento de los seis grupos
# ---------------------------------------------------------------------------
fig, (a, b) = plt.subplots(1, 2, figsize=(W, 2.6))
for t in groups:
    m, lo, hi = group(SEEDS[t], "success")
    a.plot(x_ep, 100 * m, color=gcol[t], label=SHORT[t], lw=1.1)
    a.fill_between(x_ep, 100 * lo, 100 * hi, color=gcol[t], alpha=0.15, lw=0)
    m, lo, hi = group(SEEDS[t], "ratio", median=True)
    b.plot(x_ep, m, color=gcol[t], label=SHORT[t], lw=1.1)
a.set_ylim(0, 100); a.set_ylabel("Éxito (%)"); a.set_title("Éxito en entrenamiento (media móvil de 1000)")
a.legend(loc="lower right", fontsize=7)
b.set_ylim(0.95, 2.0); b.axhline(1.0, color="k", ls="--", lw=0.7); comma(b)
b.set_ylabel("Pasos / pasos óptimos"); b.set_title("Eficiencia de ruta (mediana móvil de 1000)")
for ax in (a, b):
    ax.set_xlabel("Episodio"); thousands(ax)
fig.tight_layout(); fig.savefig(OUT / "resumen_entrenamiento.pdf"); plt.close(fig)

print("figuras en", OUT)
for p in sorted(OUT.glob("*.pdf")):
    print(" ", p.name)
