#!/usr/bin/env python3
"""Task 23 - Summarize runs and fit the empirical serial fraction alpha.

Input  : CSV with columns P, run, t_parallel_s, t_serial_baseline_s   (from weak_scale_bench.py)
Output : summary table (mean, std, speedup, standard error) + fitted alpha

Method (least squares through the origin, exact linearization of Gustafson's law):
    S(P) = P - alpha (P - 1)   <=>   y = alpha * x   with  y = P - S,  x = P - 1
    alpha_hat = sum(x y) / sum(x^2),   SE = sqrt( SSE/(n-1) / sum(x^2) )
A free-intercept fit S = a + b P is also reported as a model check (Gustafson predicts a = alpha, b = 1 - alpha).

Usage: python3 fit_gustafson.py [--csv results.csv] [--summary summary.csv] [--json fit.json]
"""
import argparse, csv, json, math, pathlib
from collections import defaultdict
import numpy as np


def load(path):
    data = defaultdict(lambda: ([], []))
    with open(path) as f:
        for r in csv.DictReader(f):
            P = int(r["P"])
            data[P][0].append(float(r["t_parallel_s"]))
            data[P][1].append(float(r["t_serial_baseline_s"]))
    return data


def summarize(data):
    out = []
    for P in sorted(data):
        tp, ts = np.array(data[P][0]), np.array(data[P][1])
        n = len(tp)
        mp_, ms_ = tp.mean(), ts.mean()
        sp = tp.std(ddof=1) if n > 1 else 0.0
        ss = ts.std(ddof=1) if n > 1 else 0.0
        S = ms_ / mp_
        # delta-method standard error of a ratio of means
        se = S * math.sqrt((ss / (ms_ * math.sqrt(n))) ** 2 + (sp / (mp_ * math.sqrt(n))) ** 2)
        out.append(dict(P=P, n=n, t_par_mean=mp_, t_par_std=sp, t_ser_mean=ms_, t_ser_std=ss,
                        S=S, S_se=se, E=S / P))
    return out


def fit_alpha(summary):
    P = np.array([s["P"] for s in summary], float)
    S = np.array([s["S"] for s in summary], float)
    x, y = P - 1.0, P - S
    sxx = float(np.sum(x * x))
    if sxx == 0:
        raise SystemExit("need at least one configuration with P > 1")
    alpha = float(np.sum(x * y) / sxx)
    resid = y - alpha * x
    n = len(P)
    dof = max(n - 1, 1)
    se = math.sqrt(float(np.sum(resid ** 2)) / dof / sxx)
    sst = float(np.sum((y - y.mean()) ** 2))
    r2 = 1.0 - float(np.sum(resid ** 2)) / sst if sst > 0 else float("nan")
    res = dict(alpha=alpha, alpha_se=se, r2=r2, n_points=n)
    if n >= 3:
        b, a = np.polyfit(P, S, 1)
        res.update(free_intercept_a=float(a), free_slope_b=float(b), gustafson_pred_b=1 - alpha)
    return res


def main():
    here = pathlib.Path(__file__).parent
    ap = argparse.ArgumentParser()
    ap.add_argument("--csv", default=str(here / "results.csv"))
    ap.add_argument("--summary", default=str(here / "summary.csv"))
    ap.add_argument("--json", default=str(here / "fit.json"))
    a = ap.parse_args()
    summary = summarize(load(a.csv))
    fit = fit_alpha(summary)
    with open(a.summary, "w", newline="") as f:
        w = csv.DictWriter(f, fieldnames=list(summary[0].keys()))
        w.writeheader()
        for s in summary:
            w.writerow({k: (f"{v:.6g}" if isinstance(v, float) else v) for k, v in s.items()})
    json.dump(fit, open(a.json, "w"), indent=2)
    print(f"{'P':>4} {'n':>2} {'t_par mean':>11} {'std':>8} {'t_ser mean':>11} {'std':>8} {'S':>8} {'SE':>7} {'E':>6}")
    for s in summary:
        print(f"{s['P']:>4} {s['n']:>2} {s['t_par_mean']:>11.4f} {s['t_par_std']:>8.4f} {s['t_ser_mean']:>11.4f} "
              f"{s['t_ser_std']:>8.4f} {s['S']:>8.3f} {s['S_se']:>7.3f} {s['E']:>6.3f}")
    print(f"\nalpha_observed = {fit['alpha']:.4f} +/- {fit['alpha_se']:.4f}   (R^2 = {fit['r2']:.4f}, n = {fit['n_points']})")
    if "free_slope_b" in fit:
        print(f"free fit S = {fit['free_intercept_a']:.3f} + {fit['free_slope_b']:.3f} P   "
              f"(Gustafson with this alpha predicts slope {fit['gustafson_pred_b']:.3f})")


if __name__ == "__main__":
    main()
