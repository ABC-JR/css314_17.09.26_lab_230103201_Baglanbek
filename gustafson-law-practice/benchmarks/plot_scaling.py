#!/usr/bin/env python3
"""Task 24 - Publication-quality scaling plot.

Curves: (1) ideal S=P, (2) Gustafson with fitted alpha, (3) measured S with standard-error bars,
(4) Amdahl with the same serial fraction (s = alpha).
Usage: python3 plot_scaling.py [--csv results.csv] [--out ../plots/scaling_comparison] [--title TEXT]
Writes <out>.png and <out>.pdf (vector).
"""
import argparse, pathlib, numpy as np
import matplotlib
matplotlib.use("Agg")
import matplotlib.pyplot as plt
from fit_gustafson import load, summarize, fit_alpha


def main():
    here = pathlib.Path(__file__).parent
    ap = argparse.ArgumentParser()
    ap.add_argument("--csv", default=str(here / "results.csv"))
    ap.add_argument("--out", default=str(here.parent / "plots" / "scaling_comparison"))
    ap.add_argument("--title", default="Weak scaling: measured vs Gustafson vs Amdahl")
    a = ap.parse_args()
    summ = summarize(load(a.csv))
    fit = fit_alpha(summ)
    al = fit["alpha"]
    P = np.array([s["P"] for s in summ], float)
    S = np.array([s["S"] for s in summ])
    se = np.array([s["S_se"] for s in summ])
    Pc = np.linspace(1, P.max(), 400)
    plt.rcParams.update({"font.size": 11, "axes.grid": True, "grid.alpha": 0.3})
    fig, ax = plt.subplots(figsize=(6.4, 4.8))
    ax.plot(Pc, Pc, ":", color="k", label="Ideal  S = P")
    ax.plot(Pc, Pc - al * (Pc - 1), "-", color="tab:blue", label=f"Gustafson fit  (alpha = {al:.3f})")
    s_am = 1.0 / (max(al, 1e-9) + (1 - al) / Pc)
    ax.plot(Pc, s_am, "--", color="tab:red", label=f"Amdahl, same s = {al:.3f}")
    ax.errorbar(P, S, yerr=se, fmt="o", color="tab:green", capsize=3, label="Measured (mean +/- SE)")
    ax.set(xlabel="Workers P (problem size per worker constant)", ylabel="Scaled speedup S(P)", title=a.title)
    ax.legend(loc="upper left", fontsize=9)
    fig.tight_layout()
    out = pathlib.Path(a.out)
    out.parent.mkdir(parents=True, exist_ok=True)
    fig.savefig(out.with_suffix(".png"), dpi=300)
    fig.savefig(out.with_suffix(".pdf"))
    print(f"alpha={al:.4f}; wrote {out}.png / .pdf")


if __name__ == "__main__":
    main()
