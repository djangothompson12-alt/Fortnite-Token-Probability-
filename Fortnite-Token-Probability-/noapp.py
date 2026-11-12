"""Headline results for men who don't use dating apps (in person + social media only)."""
import json
import numpy as np
import matplotlib; matplotlib.use("Agg")
import matplotlib.pyplot as plt
from lootorlove import params as P, love, token
plt.rcParams.update({"font.family": "serif", "font.serif": ["cmr10"], "mathtext.fontset": "cm",
                     "axes.formatter.use_mathtext": True, "axes.unicode_minus": False, "font.size": 9, "axes.linewidth": 0.6})
SEASON = P.DAYS_LEFT / 365
M, rho = love.calibrate()
R0 = json.load(open("results.json"))["season"]["rows"]
hw = np.array(sorted(map(int, R0))); tok = np.array([R0[str(h)]["token"] for h in hw])
cur = {k: [] for k in ("na", "na_lo", "na_hi", "app")}
for h in hw:
    t, pop = love.simulate(h, M, rho, n=200000, return_pop=True)
    hit = t < SEASON; off = ~pop.on_app & pop.looking
    cur["na"].append(hit[off].mean()); cur["na_lo"].append(hit[off & (pop.u < .2)].mean())
    cur["na_hi"].append(hit[off & (pop.u >= .8)].mean()); cur["app"].append(hit[pop.on_app & pop.looking].mean())
cur = {k: np.array(v) for k, v in cur.items()}
def cross(g):
    d = tok - g
    return float(np.interp(0, d, hw)) if d[-1] > 0 else None
out = {"M": M, "rho": rho, "per_dm": P.P_DM_REPLY * P.P_CONVO * P.P_DATE * rho,
       "cross": {k: cross(v) for k, v in cur.items()},
       "rows": {int(h): {k: float(cur[k][i]) for k in cur} | {"token": float(tok[i])} for i, h in enumerate(hw)}}
# long run for non-app men
t_tok = token.time_to_token(n_players=3000, seed=50); lr = {}
for h in (5, 10, 15, 20, 30):
    t, pop = love.simulate(h, M, rho, n=40000, seed=51, return_pop=True); tg = t[~pop.on_app & pop.looking][:3000]
    lr[h] = {"p_token_first": float(np.mean(t_tok / (h * 52) < tg)), "median_gf_y": float(np.median(tg))}
out["long_run"] = lr
json.dump(out, open("results_noapp.json", "w"), indent=1)
print(json.dumps({k: v for k, v in out.items() if k != "rows"}, indent=1)); print({h: {k: round(100*v, 2) for k, v in out["rows"][h].items()} for h in (0, 10, 20, 30, 56)})

fig, ax = plt.subplots(figsize=(3.3, 2.5))
ax.plot(hw, 100 * tok, c="C0", lw=1.3, label="Pirate Shop token")
ax.plot(hw, 100 * cur["na_hi"], c="C3", lw=0.8, ls="--", label="Girlfriend, top 20% looks")
ax.plot(hw, 100 * cur["na"], c="C3", lw=1.3, label="Girlfriend, average")
ax.plot(hw, 100 * cur["na_lo"], c="C3", lw=0.8, ls=":", label="Girlfriend, bottom 20% looks")
ax.plot(hw, 100 * cur["app"], c="0.55", lw=0.9, ls="-.", label="Girlfriend, average + apps")
ax.set_ylim(0, 9); ax.set_xlabel("Hours of Fortnite per week"); ax.set_ylabel("Pr(before 5 Dec), %")
ax.legend(frameon=False, fontsize=6.3, loc="upper left")
fig.tight_layout(); fig.savefig("figures/fig_season.pdf"); plt.close(fig)

# funnels: in person vs cold DM
off = [("Met in person", 1), ("Woman", P.PI_FEMALE), ("Right age", P.PI_AGE), ("Single", P.PI_SINGLE),
       ("Looking", P.PI_LOOKING), ("Finds you attractive", P.PI_ATTRACT), ("You get along", P.PI_COMPAT),
       ("You ask", P.PI_ASK), ("She says yes", P.PI_YES)]
dm = [("Cold DM sent", 1), ("She replies", P.P_DM_REPLY), ("Real conversation", P.P_CONVO), ("Date", P.P_DATE), ("Relationship", rho)]
fig, axs = plt.subplots(1, 2, figsize=(6.9, 2.4), gridspec_kw={"width_ratios": [1.4, 1]})
for ax, steps, title in ((axs[0], off, "In person (per new person met)"), (axs[1], dm, "Social media (per cold DM)")):
    v = np.cumprod([s[1] for s in steps]); y = np.arange(len(steps))[::-1]
    ax.barh(y, v, color="0.35", height=0.65); ax.set_xscale("log"); ax.set_xlim(3e-6, 4)
    ax.set_yticks(y); ax.set_yticklabels([s[0] for s in steps], fontsize=7)
    for yi, vi in zip(y, v):
        ax.text(vi * 1.4, yi, "1" if vi == 1 else f"1 in {1/vi:,.0f}", va="center", fontsize=6.5)
    ax.set_title(title, fontsize=8.5); ax.set_xlabel("Fraction remaining")
fig.tight_layout(); fig.savefig("figures/fig_funnel.pdf"); plt.close(fig)

# ---- personal odds: looks x personality, actively trying, 10 h/wk, no apps, by Christmas
from matplotlib.colors import LinearSegmentedColormap
X = P.CHRISTMAS_DAYS / 365
g = np.linspace(0.02, 0.98, 49); L, Q = np.meshgrid(g, g)
lam = love.personal_rate(10, M, rho, L, Q, P.EFFORT["Actively trying"])
Z = 100 * (1 - np.exp(-lam * X))
fig, ax = plt.subplots(figsize=(3.3, 2.7))
cm = LinearSegmentedColormap.from_list("w2r", ["#f7f4ee", "#e8a3a0", "#b3262b", "#5c0f12"])
im = ax.pcolormesh(100 * g, 100 * g, Z, cmap=cm, shading="auto")
cs = ax.contour(100 * g, 100 * g, Z, levels=[2, 5, 10, 20, 30], colors="k", linewidths=0.5)
ax.clabel(cs, fmt="%d%%", fontsize=6.5)
ax.set_xlabel("Looks percentile"); ax.set_ylabel("Personality / social percentile")
fig.colorbar(im, ax=ax, label="Pr(girlfriend by Christmas), %")
fig.tight_layout(); fig.savefig("figures/fig_personal.pdf"); plt.close(fig)
tab = {}
for e, v in P.EFFORT.items():
    tab[e] = {}
    for name, (lk, pq) in {"bottom20": (0.1, 0.1), "average": (0.5, 0.5), "top20": (0.9, 0.9)}.items():
        l = love.personal_rate(10, M, rho, lk, pq, v)
        tab[e][name] = {"dec5": float(1 - np.exp(-l * P.DAYS_LEFT / 365)), "xmas": float(1 - np.exp(-l * X))}
    # crossover with token for an average guy at this effort
    hs = np.array(sorted(map(int, R0))); gfh = np.array([1 - np.exp(-love.personal_rate(h, M, rho, 0.5, 0.5, v) * P.DAYS_LEFT / 365) for h in hs])
    d = tok - gfh; tab[e]["cross"] = float(np.interp(0, d, hs)) if d[-1] > 0 else None
out["personal"] = tab
json.dump(out, open("results_noapp.json", "w"), indent=1)
print(json.dumps(tab, indent=1))
