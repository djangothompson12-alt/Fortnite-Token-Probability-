"""Summarise psa.json: intervals, sensitivity indices, uncertainty-band figure."""
import json
import numpy as np
import matplotlib; matplotlib.use("Agg")
import matplotlib.pyplot as plt
plt.rcParams.update({"font.family": "serif", "font.serif": ["cmr10"], "mathtext.fontset": "cm",
                     "axes.formatter.use_mathtext": True, "axes.unicode_minus": False,
                     "font.size": 9, "axes.linewidth": 0.6})
D = json.load(open("psa.json")); HW = np.array(D["HW"]); alld = D["draws"]; draws = [d for d in alld if not d["rejected"]]; names = list(D["priors"])
X = np.array([[d["theta"][n] for n in names] for d in draws])
def q(a): a = np.asarray(a, float); a = a[np.isfinite(a)]; return [float(np.median(a)), float(np.percentile(a, 5)), float(np.percentile(a, 95)), int(a.size)]
out = {k: q([d[k] for d in draws]) for k in ("tok10", "gf10", "cross", "cross_lo", "cross_hi", "lobby800", "M", "rho")}
out["p_gf_beats_tok_at_10"] = float(np.mean([d["gf10"] > d["tok10"] for d in draws]))
out["accepted"] = len(draws); out["total"] = len(alld)
out["p_cross_exists"] = float(np.mean([np.isfinite(d["cross"]) for d in draws]))

def S1(y, nb=10):
    """First-order index Var(E[Y|X_i])/Var(Y) by quantile binning."""
    ok = np.isfinite(y); y = y[ok]; res = {}
    for j, n in enumerate(names):
        x = X[ok, j]; edges = np.quantile(x, np.linspace(0, 1, nb + 1))
        b = np.clip(np.searchsorted(edges, x, side="right") - 1, 0, nb - 1)
        means = np.array([y[b == i].mean() for i in range(nb)]); w = np.array([(b == i).mean() for i in range(nb)])
        res[n] = float(np.sum(w * (means - y.mean())**2) / y.var())
    return dict(sorted(res.items(), key=lambda kv: -kv[1]))
cross = np.array([d["cross"] for d in draws], float)
out["S1_cross"] = S1(cross)
out["S1_tok10"] = S1(np.array([d["tok10"] for d in draws]))
out["S1_gf10"] = S1(np.array([d["gf10"] for d in draws]))
json.dump(out, open("psa_summary.json", "w"), indent=1)

# figure: season race with 90% bands
tok = np.array([d["tok"] for d in draws]) * 100; gf = np.array([d["gf"] for d in draws]) * 100
fig, ax = plt.subplots(figsize=(3.3, 2.3))
for arr, c, lab in ((tok, "C0", "Pirate Shop token"), (gf, "C3", "Girlfriend (average man)")):
    ax.fill_between(HW, np.percentile(arr, 5, 0), np.percentile(arr, 95, 0), color=c, alpha=0.18, lw=0)
    ax.plot(HW, np.median(arr, 0), c=c, lw=1.2, label=lab)
ax.set_xlabel("Hours of Fortnite per week"); ax.set_ylabel("Pr(before 5 Dec), %"); ax.legend(frameon=False, fontsize=6.5, loc="upper left")
fig.tight_layout(); fig.savefig("figures/fig_psa.pdf"); plt.close(fig)

# figure: sensitivity indices for the crossover
s = out["S1_cross"]; top = list(s.items())[:8]
labels = {"MU_BREAKUP": r"Breakup rate $\mu$", "C_MAX": r"Max chests $C$", "KAPPA": r"Looting time $\kappa$",
          "OVERHEAD": r"Overhead $O_0$", "SINGLE_MEN": "Single share target", "ONLINE_SHARE": "Online share target",
          "RESIDUAL_SD": "Residual spread", "QUEUE_GROWTH": r"Queue growth $\Delta_Q$", "DISPLACE": r"Displacement $\delta$",
          "T_FLOOR": "Survival floor", "T0": r"New-player survival $T_0$", "E_CONTEXT": r"Context meetings $E_{ctx}$",
          "BETA": r"Meeting rate $\beta$", "FATIGUE_PER_MATCH": r"Fatigue $\phi$", "SWIPES_PER_DAY": "Swipes per day",
          "P_CONVO": "Match to conversation", "P_DATE": "Conversation to date", "DMS_PER_WEEK": "DMs per week",
          "P_DM_REPLY": "DM reply rate", "LOOKS_RANGE": "Looks range (online)", "OFFLINE_LOOKS_RANGE": "Looks range (offline)",
          "SKILL_SD": "Skill spread"}
fig, ax = plt.subplots(figsize=(3.3, 2.2))
ax.barh(range(len(top))[::-1], [v for _, v in top], color="0.35", height=0.6)
ax.set_yticks(range(len(top))[::-1]); ax.set_yticklabels([labels.get(k, k) for k, _ in top], fontsize=7)
ax.set_xlabel(r"First-order index $S_i$ (crossover hours)")
fig.tight_layout(); fig.savefig("figures/fig_sobol.pdf"); plt.close(fig)
print(json.dumps(out, indent=1))
