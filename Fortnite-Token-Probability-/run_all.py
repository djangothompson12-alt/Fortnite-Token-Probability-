"""Reproduce every number and figure in the paper:  python run_all.py  (about 4 minutes)"""
import json
import numpy as np
import matplotlib; matplotlib.use("Agg")
import matplotlib.pyplot as plt
from lootorlove import params as P, love, token

plt.rcParams.update({"font.family": "serif", "font.serif": ["cmr10"], "mathtext.fontset": "cm",
                     "axes.formatter.use_mathtext": True, "axes.unicode_minus": False,
                     "font.size": 9, "axes.linewidth": 0.6})
FIG = "figures/"; R = {}; W = 3.3
SEASON = P.DAYS_LEFT / 365

# ---------------- calibration ----------------
M, p_rel = love.calibrate(); M_gss, p_rel_gss = love.calibrate(P.SINGLE_MEN_GSS)
per_swipe = P.APP_MATCH * P.P_CONVO * P.P_DATE * p_rel
R.update(drake_per_person=love.drake_per_person(), naive_rate=love.offline_rate(P.G0),
         naive_median_years=np.log(2) / love.offline_rate(P.G0), M=M, p_rel=p_rel, M_gss=M_gss,
         p_rel_gss=p_rel_gss, per_swipe=per_swipe, per_dm=P.P_DM_REPLY * P.P_CONVO * P.P_DATE * p_rel,
         pools={k: float(love.app_pool(k)) for k in P.PLACES}, swipes={k: float(love.swipes_per_day(k)) for k in P.PLACES})

# ---------------- Fig 1: two funnels ----------------
off = [("Met in person", 1), ("Woman", P.PI_FEMALE), ("Right age", P.PI_AGE), ("Single", P.PI_SINGLE),
       ("Looking", P.PI_LOOKING), ("Finds you attractive", P.PI_ATTRACT), ("You get along", P.PI_COMPAT),
       ("You ask", P.PI_ASK), ("She says yes", P.PI_YES)]
app = [("Right swipe", 1), ("Match", P.APP_MATCH), ("Conversation", P.P_CONVO), ("Date", P.P_DATE), ("Relationship", p_rel)]
fig, axs = plt.subplots(1, 2, figsize=(6.9, 2.4), gridspec_kw={"width_ratios": [1.4, 1]})
for ax, steps, title in ((axs[0], off, "In person (per new person met)"), (axs[1], app, "Dating app (per right swipe)")):
    v = np.cumprod([s[1] for s in steps]); y = np.arange(len(steps))[::-1]
    ax.barh(y, v, color="0.35", height=0.65); ax.set_xscale("log"); ax.set_xlim(3e-6, 4)
    ax.set_yticks(y); ax.set_yticklabels([s[0] for s in steps], fontsize=7)
    for yi, vi in zip(y, v):
        ax.text(vi * 1.4, yi, "1" if vi == 1 else f"1 in {1/vi:,.0f}", va="center", fontsize=6.5)
    ax.set_title(title, fontsize=8.5); ax.set_xlabel("Fraction remaining")
fig.tight_layout(); fig.savefig(FIG + "fig_funnel_allmen.pdf"); plt.close(fig)

# ---------------- token by mode ----------------
R["modes"] = {}
fig, ax = plt.subplots(figsize=(W, 2.3))
for mode in P.MODE_SHARE:
    # [S] if anyone in your group finds the token, the whole group gets it (GamesRadar, IBTimes, Nov 2026),
    # so the group pools its chests: equivalent to each player's chests counting group_size times.
    t = token.time_to_token(n_players=3000, mode=mode, boost=P.GROUP_SIZE[mode], seed=10)
    R["modes"][mode] = {"median_h": float(np.median(t)), "p10_h": float(np.percentile(t, 10)),
                        "p90_h": float(np.percentile(t, 90)), "censored": float(np.isinf(t).mean())}
    xs = np.sort(t[np.isfinite(t)]); ax.plot(xs, np.arange(1, len(xs) + 1) / len(t), lw=1, label=mode)
ax.set_xscale("log"); ax.set_xlim(10, 3e4); ax.axhline(0.5, ls=":", c="k", lw=0.6)
ax.set_xlabel("Hours played"); ax.set_ylabel("Share of players with token"); ax.legend(frameon=False, fontsize=7)
fig.tight_layout(); fig.savefig(FIG + "fig_modes.pdf"); plt.close(fig)

R["regions"] = {reg: float(np.median(token.time_to_token(n_players=2000, region=reg, seed=20))) for reg in P.REGIONS}
R["treasure"] = {str(b): float(np.median(token.time_to_token(n_players=2000, boost=b, seed=30))) for b in P.TREASURE_BOOST}
R["squad_unshared_median_h"] = float(np.median(token.time_to_token(n_players=2000, mode="Squad", seed=40)))

# ---------------- lobby share and SBMM / fatigue decomposition ----------------
starts = [10, 25, 50, 100, 200, 400, 800, 1600, 3200]
lob = {f: [token.season_probability(10, n_players=3000, start_matches=s, fatigue=f, return_lobby=True)[2] for s in starts] for f in (False, True)}
R["lobby"] = {"starts": starts, "no_fatigue": lob[False], "fatigue": lob[True]}
fig, ax = plt.subplots(figsize=(W, 2.1))
ax.plot(starts, [100 * x for x in lob[False]], "o-", c="0.5", ms=3, lw=1, label="Fresh")
ax.plot(starts, [100 * x for x in lob[True]], "o-", c="k", ms=3, lw=1, label="With fatigue")
ax.axhline(50, ls=":", c="k", lw=0.6); ax.set_xscale("log"); ax.set_ylim(0, 70)
ax.set_xlabel("Matches already played"); ax.set_ylabel("Time not in a match, %"); ax.legend(frameon=False, fontsize=7)
fig.tight_layout(); fig.savefig(FIG + "fig_lobby.pdf"); plt.close(fig)

def with_params(changes, fn):
    old = {k: getattr(P, k) for k in changes}
    for k, v in changes.items(): setattr(P, k, v)
    try: return fn()
    finally:
        for k, v in old.items(): setattr(P, k, v)
sp = lambda **kw: token.season_probability(10, n_players=10000, **kw)[0]
R["decomp"] = {
    "full": sp(),
    "no_fatigue": sp(fatigue=False),
    "no_sbmm": with_params({"T_FLOOR": P.T0, "QUEUE_GROWTH": 0.0}, sp),
    "sbmm_survival_only": with_params({"QUEUE_GROWTH": 0.0}, sp),
}

# ---------------- season race, with looks ----------------
hw = np.arange(0, 61, 2.0)
tok = np.array([sp_h for sp_h in (token.season_probability(h, n_players=8000)[0] for h in hw)])
def gf_curve(Mx, prx, mask=None):
    out = []
    for h in hw:
        t, pop = love.simulate(h, Mx, prx, n=60000, return_pop=True)
        m = np.ones_like(t, bool) if mask is None else mask(pop.u)
        out.append(np.mean(t[m] < SEASON))
    return np.array(out)
gf = gf_curve(M, p_rel); gf2 = gf_curve(M_gss, p_rel_gss)
gf_lo = gf_curve(M, p_rel, lambda u: u < 0.2); gf_hi = gf_curve(M, p_rel, lambda u: u >= 0.8)
cross = lambda g: float(np.interp(0, tok - g, hw)) if (tok - g)[-1] > 0 else None
R["season"] = {"days_left": P.DAYS_LEFT, "cross_pew": cross(gf), "cross_gss": cross(gf2),
               "cross_bottom20": cross(gf_lo), "cross_top20": cross(gf_hi),
               "rows": {int(h): {"token": float(a), "gf": float(b), "gf_gss": float(c), "gf_lo": float(d), "gf_hi": float(e)}
                        for h, a, b, c, d, e in zip(hw, tok, gf, gf2, gf_lo, gf_hi)}}
fig, ax = plt.subplots(figsize=(W, 2.5))
ax.plot(hw, 100 * tok, c="C0", lw=1.3, label="Pirate Shop token")
ax.plot(hw, 100 * gf_hi, c="C3", lw=0.8, ls="--", label="Girlfriend, top 20% looks")
ax.plot(hw, 100 * gf, c="C3", lw=1.3, label="Girlfriend, average")
ax.plot(hw, 100 * gf_lo, c="C3", lw=0.8, ls=":", label="Girlfriend, bottom 20% looks")
ax.set_ylim(0, 8); ax.set_xlabel("Hours of Fortnite per week"); ax.set_ylabel("Pr(before 5 Dec), %"); ax.legend(frameon=False, fontsize=6.5, loc="upper left")
fig.tight_layout(); fig.savefig(FIG + "fig_season_allmen.pdf"); plt.close(fig)

# ---------------- location and lobby swiping ----------------
R["places"] = {}
for pl in P.PLACES:
    t = love.simulate(10, M, p_rel, place=pl)
    R["places"][pl] = {"pool": float(love.app_pool(pl)), "swipes": float(love.swipes_per_day(pl)),
                       "median_y": float(np.median(t)), "season": float(np.mean(t < SEASON))}
t25 = love.simulate(25, M, p_rel); t25s = love.simulate(25, M, p_rel, lobby_swipe_h=1.0)
R["lobby_swipe"] = {"season_25": float(np.mean(t25 < SEASON)), "season_25_swipe": float(np.mean(t25s < SEASON)),
                    "season_10": float(R["season"]["rows"][10]["gf"])}
t_app, pop = love.simulate(10, M, p_rel, return_pop=True)
R["app_users"] = {"on_app": float(np.mean(t_app[pop.on_app] < SEASON)), "off_app": float(np.mean(t_app[~pop.on_app] < SEASON))}

# ---------------- long run ----------------
lr_h = [2, 5, 10, 15, 20, 30, 40, 56]; lr = {}
t_tok = token.time_to_token(n_players=3000, seed=50)
for h in lr_h:
    yt = t_tok / (h * 52); yg = love.simulate(h, M, p_rel, n=3000, seed=51)
    lr[h] = {"p_token_first": float(np.mean(yt < yg)), "median_token_y": float(np.median(yt)), "median_gf_y": float(np.median(yg))}
R["long_run"] = lr
fig, ax = plt.subplots(figsize=(W, 2.1))
ax.plot(lr_h, [100 * lr[h]["p_token_first"] for h in lr_h], "o-", c="k", ms=3, lw=1)
ax.axhline(50, ls=":", c="k", lw=0.6); ax.set_ylim(0, 100)
ax.set_xlabel("Hours of Fortnite per week"); ax.set_ylabel("Pr(token comes first), %")
fig.tight_layout(); fig.savefig(FIG + "fig_longrun.pdf"); plt.close(fig)

# ---------------- sensitivity (season probability at 10 h/week) ----------------
def gf_with():
    Mx, prx = love.calibrate(n=60000); return float(np.mean(love.simulate(10, Mx, prx, n=60000) < SEASON))
sens = {"base_tok": R["decomp"]["full"], "base_gf": float(R["season"]["rows"][10]["gf"])}
for name, lo, hi in [("C_MAX", 8, 16), ("KAPPA", 3, 10), ("OVERHEAD", 2, 7), ("QUEUE_GROWTH", 0, 4),
                     ("FATIGUE_PER_MATCH", 0.0, 0.03), ("T_FLOOR", 3, 10)]:
    sens[name] = [with_params({name: v}, sp) for v in (lo, hi)] + [lo, hi]
for name, lo, hi in [("MU_BREAKUP", 0.25, 0.5), ("RESIDUAL_SD", 0.25, 1.0), ("DISPLACE", 0.1, 0.4),
                     ("SWIPES_PER_DAY", 10, 100), ("DMS_PER_WEEK", 0, 15), ("LOOKS_RANGE", 4, 25)]:
    sens[name] = [with_params({name: v}, gf_with) for v in (lo, hi)] + [lo, hi]
R["sens"] = sens

json.dump(R, open("results.json", "w"), indent=1, default=float)
print(json.dumps(R, indent=1, default=float))
