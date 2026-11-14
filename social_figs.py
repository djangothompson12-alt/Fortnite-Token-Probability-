"""9:16 images for TikTok, styled like the paper.   python social_figs.py"""
import json
import numpy as np
import matplotlib; matplotlib.use("Agg")
import matplotlib.pyplot as plt
plt.rcParams.update({"font.family": "serif", "font.serif": ["cmr10"], "mathtext.fontset": "cm",
                     "axes.formatter.use_mathtext": True, "axes.unicode_minus": False, "axes.linewidth": 1.0})
D = json.load(open("psa.json")); S = json.load(open("psa_summary.json")); E = json.load(open("extras.json"))
HW = np.array(D["HW"]); D["draws"] = [d for d in D["draws"] if not d["rejected"]]
tok = np.array([d["tok"] for d in D["draws"]]) * 100; gf = np.array([d["gf_noapp"] for d in D["draws"]]) * 100
BG = "#fbfaf6"

def frame(title, sub):
    fig = plt.figure(figsize=(5.4, 9.6), dpi=200, facecolor=BG)
    fig.text(0.5, 0.93, title, ha="center", fontsize=26, family="cmb10")
    fig.text(0.5, 0.895, sub, ha="center", fontsize=12, style="italic", color="0.3")
    return fig

# 1. the race
fig = frame("Loot or Love?", "Pr(before the season ends, 5 Dec 2026)")
ax = fig.add_axes([0.16, 0.40, 0.78, 0.43]); ax.set_facecolor(BG)
RR = json.load(open("results_noapp.json"))["rows"]; bh = np.array(sorted(map(int, RR)))
for arr, key, c, lab in ((tok, "token", "#1f5fa8", "Free item shop (token)"), (gf, "na", "#b3262b", "Girlfriend (average guy, no apps)")):
    ax.fill_between(HW, np.percentile(arr, 5, 0), np.percentile(arr, 95, 0), color=c, alpha=0.18, lw=0)
    ax.plot(bh, [100 * RR[str(h)][key] for h in bh], c=c, lw=2.4, label=lab)
base = json.load(open("results_noapp.json"))["cross"]["na"]; _c = np.array([d["cross_noapp"] for d in D["draws"]], float); cr = [0, np.nanpercentile(_c, 5), np.nanpercentile(_c, 95)]; ax.axvline(base, ls=":", c="k", lw=1.2)
ax.text(base + 1.2, ax.get_ylim()[1] * 0.06, f"crossover\n{base:.0f} h/week", fontsize=12)
ax.set_xlabel("Hours of Fortnite per week", fontsize=13); ax.set_ylabel("Probability (%)", fontsize=13)
ax.tick_params(labelsize=11); ax.legend(frameon=False, fontsize=11, loc="upper left", bbox_to_anchor=(0, 0.82))
fig.text(0.5, 0.165, f"Play more than about {base:.0f} hours a week and\nthe free item shop is more likely\nthan a girlfriend by December.\n(90% interval: {cr[1]:.0f} to {cr[2]:.0f} hours)",
         ha="center", fontsize=15, linespacing=1.5)
fig.text(0.5, 0.075, f"Lines: baseline. Shaded: 90% interval over {len(D['draws'])} sets of assumptions\n(each run: 1,500 simulated players and 30,000 simulated men)",
         ha="center", fontsize=9.5, color="0.35", linespacing=1.4)
fig.savefig("social/01_race.png", facecolor=BG); plt.close(fig)

# 2. odds per attempt
fig = frame("Odds per attempt", "probability of ending up with the thing")
rows = [("Fortnite chest", 137500, "#1f5fa8"), ("Tinder right swipe*", 47000, "#b3262b"),
        ("Meeting someone new", 33600, "#b3262b"), ("Cold DM*", 3500, "#b3262b")]
ax = fig.add_axes([0.08, 0.42, 0.84, 0.4]); ax.set_facecolor(BG); ax.axis("off")
for i, (lab, n, c) in enumerate(rows):
    y = 1 - i * 0.27
    ax.text(0, y, lab, fontsize=17, va="center"); ax.text(1, y, f"1 in {n:,}", fontsize=19, va="center", ha="right", color=c, family="cmb10")
ax.set_ylim(0.1, 1.1); ax.set_xlim(0, 1)
fig.text(0.5, 0.27, "Love wins every time per attempt.\nBut you open about 30 chests an hour,\nmeet about 1 new person a day\nand send about 3 DMs a week.",
         ha="center", fontsize=15, linespacing=1.5)
fig.text(0.5, 0.06, "*model estimates; chest odds are Epic's official rate", ha="center", fontsize=9.5, color="0.35")
fig.savefig("social/02_odds.png", facecolor=BG); plt.close(fig)

# 3. optimal time to die
ts = E["t_star"]["4"]; m, s = int(ts), int(round((ts - int(ts)) * 60))
fig = frame("The optimal time to die", "maximising chests per hour of real life")
fig.text(0.5, 0.72, f"{m} min {s} s", ha="center", fontsize=54, family="cmb10", color="#b3262b")
fig.text(0.5, 0.58, r"$T^{*} = -\kappa\left[W_{-1}\!\left(-e^{-(1+O/\kappa)}\right)+1\right] - O$", ha="center", fontsize=19)
fig.text(0.5, 0.40, "Chests are mostly opened early.\nAfter about 6 minutes, you loot more per hour\nby dying and queueing a fresh map.\n(Please don't actually do this.)",
         ha="center", fontsize=14, linespacing=1.5)
fig.savefig("social/03_optimal_death.png", facecolor=BG); plt.close(fig)
print("ok")
