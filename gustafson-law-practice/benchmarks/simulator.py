#!/usr/bin/env python3
"""Task 21 - Parametric Amdahl / Gustafson speedup simulator.

Models strong scaling (Amdahl, fixed size) and weak scaling (Gustafson, fixed time)
for core counts 1 <= P <= 65,536 and serial fractions 0.001 <= alpha <= 0.20.

Outputs
  * CSV  (one row per P, alpha): P, alpha, amdahl_speedup, gustafson_speedup,
         amdahl_efficiency, gustafson_efficiency, amdahl_ceiling, ratio_g_over_a
  * Overlay plots (PNG + PDF): speedup and efficiency vs P for several alphas.

Usage
  python3 benchmarks/simulator.py                       # defaults
  python3 benchmarks/simulator.py --alphas 0.01 0.05 0.1 --pmax 4096
  python3 benchmarks/simulator.py --csv out.csv --outdir plots --no-plot
"""
import argparse, csv, math, pathlib, sys

P_MIN, P_MAX_LIMIT = 1, 65536
A_MIN, A_MAX = 0.001, 0.20


def amdahl(P, s):
    return 1.0 / (s + (1.0 - s) / P)


def gustafson(P, a):
    return P - a * (P - 1)


def powers_of_two(pmax):
    p, out = 1, []
    while p <= pmax:
        out.append(p)
        p *= 2
    return out


def validate(Ps, alphas):
    for P in Ps:
        if not (P_MIN <= P <= P_MAX_LIMIT):
            sys.exit(f"P={P} outside [{P_MIN}, {P_MAX_LIMIT}]")
    for a in alphas:
        if not (A_MIN <= a <= A_MAX):
            sys.exit(f"alpha={a} outside [{A_MIN}, {A_MAX}]")


def simulate(Ps, alphas):
    rows = []
    for a in alphas:
        for P in Ps:
            sa, sg = amdahl(P, a), gustafson(P, a)
            rows.append(dict(P=P, alpha=a,
                             amdahl_speedup=sa, gustafson_speedup=sg,
                             amdahl_efficiency=sa / P, gustafson_efficiency=sg / P,
                             amdahl_ceiling=1.0 / a, ratio_g_over_a=sg / sa))
    return rows


def write_csv(rows, path):
    path = pathlib.Path(path)
    path.parent.mkdir(parents=True, exist_ok=True)
    with open(path, "w", newline="") as f:
        w = csv.DictWriter(f, fieldnames=list(rows[0].keys()))
        w.writeheader()
        for r in rows:
            w.writerow({k: (f"{v:.6g}" if isinstance(v, float) else v) for k, v in r.items()})


def plot(rows, alphas, outdir):
    import matplotlib
    matplotlib.use("Agg")
    import matplotlib.pyplot as plt
    outdir = pathlib.Path(outdir)
    outdir.mkdir(parents=True, exist_ok=True)
    cmap = plt.get_cmap("viridis")
    fig, axes = plt.subplots(1, 2, figsize=(12, 4.8))
    for i, a in enumerate(alphas):
        c = cmap(i / max(1, len(alphas) - 1) * 0.9)
        sel = [r for r in rows if r["alpha"] == a]
        P = [r["P"] for r in sel]
        axes[0].plot(P, [r["gustafson_speedup"] for r in sel], "-", color=c, label=f"Gustafson a={a:g}")
        axes[0].plot(P, [r["amdahl_speedup"] for r in sel], "--", color=c, label=f"Amdahl s={a:g}")
        axes[1].plot(P, [r["gustafson_efficiency"] for r in sel], "-", color=c, label=f"Gustafson a={a:g}")
        axes[1].plot(P, [r["amdahl_efficiency"] for r in sel], "--", color=c, label=f"Amdahl s={a:g}")
    Pall = sorted({r["P"] for r in rows})
    axes[0].plot(Pall, Pall, ":", color="k", label="Ideal (S=P)")
    axes[0].set(xscale="log", yscale="log", xlabel="Processors P", ylabel="Speedup S(P)",
                title="Speedup: weak (solid) vs strong (dashed) scaling")
    axes[1].set(xscale="log", ylim=(0, 1.05), xlabel="Processors P", ylabel="Efficiency S(P)/P",
                title="Efficiency: Gustafson plateaus at 1-a, Amdahl -> 0")
    for ax in axes:
        ax.grid(True, which="both", alpha=0.3)
    axes[0].legend(fontsize=6, ncol=2)
    fig.tight_layout()
    for ext in ("png", "pdf"):
        fig.savefig(outdir / f"simulator_overlay.{ext}", dpi=200)
    plt.close(fig)


def main():
    ap = argparse.ArgumentParser(description=__doc__, formatter_class=argparse.RawDescriptionHelpFormatter)
    ap.add_argument("--pmax", type=int, default=65536, help="largest P (powers of two from 1)")
    ap.add_argument("--procs", type=int, nargs="*", help="explicit list of P values (overrides --pmax)")
    ap.add_argument("--alphas", type=float, nargs="*", default=[0.001, 0.01, 0.05, 0.10, 0.20])
    ap.add_argument("--csv", default="benchmarks/simulator_output.csv")
    ap.add_argument("--outdir", default="plots")
    ap.add_argument("--no-plot", action="store_true")
    args = ap.parse_args()
    Ps = sorted(set(args.procs)) if args.procs else powers_of_two(args.pmax)
    validate(Ps, args.alphas)
    rows = simulate(Ps, args.alphas)
    write_csv(rows, args.csv)
    print(f"wrote {len(rows)} rows to {args.csv}")
    if not args.no_plot:
        plot(rows, args.alphas, args.outdir)
        print(f"wrote plots to {args.outdir}/simulator_overlay.(png|pdf)")


if __name__ == "__main__":
    main()
