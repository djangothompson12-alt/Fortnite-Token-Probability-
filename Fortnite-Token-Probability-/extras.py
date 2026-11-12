"""Closed-form optimum (Lambert W) check and Monte Carlo convergence.  python extras.py"""
import json
import numpy as np
from scipy.special import lambertw
import matplotlib; matplotlib.use("Agg")
import matplotlib.pyplot as plt
from lootorlove import params as P, token, love

plt.rcParams.update({"font.family": "serif", "font.serif": ["cmr10"], "mathtext.fontset": "cm",
                     "axes.formatter.use_mathtext": True, "axes.unicode_minus": False,
                     "font.size": 9, "axes.linewidth": 0.6})
W = 3.3; R = {}

def t_star(O, k):
    x = -lambertw(-np.exp(-(1 + O / k)), -1).real
    return k * (x - 1) - O

# --- Proposition 1 check: simulated chests/hour against fixed survival time
P.FATIGUE_PER_MATCH = 0.0; P.FATIGUE_IDLE = 0.0; P.QUEUE_GROWTH = 0.0; P.SKILL_SD = 1e-9; P.SURV_SHAPE = 1e6
Ts = np.arange(2, 16.01, 1.0); sim = []
for T in Ts:
    P.T0 = P.T_FLOOR = T
    _, c = token.season_probability(10, n_players=3000, seed=7)
    sim.append(c.mean() / (10 * P.DAYS_LEFT / 7))
Tg = np.linspace(0.5, 20, 400)
rate = lambda T, O: 60 * P.C_MAX * (1 - np.exp(-T / P.KAPPA)) / (T + O)
R["t_star"] = {str(O): t_star(O, P.KAPPA) for O in (2, 4, 5.5, 7)}
R["t_star_rate"] = rate(t_star(4, P.KAPPA), 4)
R["sim_peak_T"] = float(Ts[int(np.argmax(sim))])
fig, ax = plt.subplots(figsize=(W, 2.2))
for O, ls in ((2, ":"), (4, "-"), (7, "--")):
    ax.plot(Tg, rate(Tg, O), c="k", ls=ls, lw=0.9, label=f"$O={O}$ min")
    ts = t_star(O, P.KAPPA); ax.plot([ts], [rate(ts, O)], "o", c="k", ms=3)
ax.plot(Ts, sim, "x", c="C3", ms=4, label="Simulation ($O=4$)")
ax.set_xlabel("Survival time per match $T$ (min)"); ax.set_ylabel("Chests per hour"); ax.legend(frameon=False, fontsize=6.5)
fig.tight_layout(); fig.savefig("figures/fig_tstar.pdf"); plt.close(fig)

# --- Monte Carlo convergence (default parameters)
import importlib; importlib.reload(P); importlib.reload(token)
p, c = token.season_probability(10, n_players=20000, seed=8)
v = 1 - np.exp(-P.P_TOKEN * c)
n = np.arange(1, len(v) + 1); run = np.cumsum(v) / n
se = np.array([v[:k].std(ddof=1) / np.sqrt(k) if k > 1 else np.nan for k in n])
R["tok10_mean"] = float(v.mean()); R["tok10_se"] = float(v.std(ddof=1) / np.sqrt(len(v)))
M, rho = love.calibrate()
t = love.simulate(10, M, rho, n=100000)
hit = (t < P.DAYS_LEFT / 365).astype(float)
R["gf10_mean"] = float(hit.mean()); R["gf10_se"] = float(hit.std(ddof=1) / np.sqrt(len(hit)))
fig, ax = plt.subplots(figsize=(W, 2.0))
ax.plot(n, 100 * run, c="k", lw=0.8)
ax.fill_between(n, 100 * (run - 1.96 * se), 100 * (run + 1.96 * se), color="0.8", lw=0)
ax.set_xscale("log"); ax.set_xlim(10, len(v)); ax.set_ylim(0.6, 1.05)
ax.set_xlabel("Simulated players"); ax.set_ylabel("Pr(token), %")
fig.tight_layout(); fig.savefig("figures/fig_convergence.pdf"); plt.close(fig)

json.dump(R, open("extras.json", "w"), indent=1, default=float)
print(json.dumps(R, indent=1, default=float))
