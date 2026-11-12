"""Probabilistic sensitivity analysis.

Every [A] parameter is drawn from a prior, the whole pipeline (calibration included)
is rerun, and the spread of the outputs gives uncertainty intervals.
First-order sensitivity indices S_i = Var(E[Y|X_i]) / Var(Y) are estimated by
quantile binning.   python psa.py [n_draws]   (about 10 minutes for 300 draws on 4 cores)
"""
import sys, json
import numpy as np
from multiprocessing import Pool

PRIORS = {  # name: (low, high), uniform
    # token
    "C_MAX": (8, 16), "KAPPA": (3, 10), "OVERHEAD": (2.5, 6), "QUEUE_GROWTH": (0, 3),
    "FATIGUE_PER_MATCH": (0, 0.02), "T_FLOOR": (4, 9), "T0": (11, 18), "SKILL_SD": (0.2, 0.5),
    # girlfriend
    "MU_BREAKUP": (0.25, 0.5), "RESIDUAL_SD": (0.25, 1.0), "DISPLACE": (0.1, 0.4), "BETA": (0.4, 1.6),
    "E_CONTEXT": (0.3, 1.0), "SWIPES_PER_DAY": (10, 100), "P_CONVO": (0.15, 0.5), "P_DATE": (0.08, 0.25),
    "DMS_PER_WEEK": (0, 10), "P_DM_REPLY": (0.03, 0.15), "LOOKS_RANGE": (4, 20),
    "OFFLINE_LOOKS_RANGE": (1.5, 6), "PASSIVE_FACTOR": (0.05, 0.4), "SINGLE_MEN": (0.53, 0.63), "ONLINE_SHARE": (0.30, 0.50),
}
HW = np.arange(0, 61, 4.0)

def one(args):
    k, theta = args
    from lootorlove import params as P, love, token
    for n, v in theta.items(): setattr(P, n, v)
    season = P.DAYS_LEFT / 365
    try:
        M, rho = love.calibrate(target_single=P.SINGLE_MEN, n=40000, seed=k)
    except ValueError:      # no (M, rho) can reproduce both survey targets: reject the draw
        return {"theta": theta, "rejected": True}
    tok = np.array([token.season_probability(h, n_players=1500, seed=1000 + k)[0] for h in HW])
    gf, lo, hi, na, na_lo, na_hi, ap = [], [], [], [], [], [], []
    for h in HW:
        t, pop = love.simulate(h, M, rho, n=30000, seed=2000 + k, return_pop=True)
        hit = t < season; off = ~pop.on_app & pop.looking
        gf.append(hit.mean()); lo.append(hit[pop.u < 0.2].mean()); hi.append(hit[pop.u >= 0.8].mean())
        na.append(hit[off].mean()); na_lo.append(hit[off & (pop.u < 0.2)].mean()); na_hi.append(hit[off & (pop.u >= 0.8)].mean())
        ap.append(hit[pop.on_app & pop.looking].mean())
    def cross(g):
        d = tok - np.array(g)
        return float(np.interp(0, d, HW)) if d[-1] > 0 and np.all(np.diff(d) > -1e-3) else float("nan")
    lob = token.season_probability(10, n_players=1500, start_matches=800, seed=3000 + k, return_lobby=True)[2]
    return {"theta": theta, "tok10": float(np.interp(10, HW, tok)), "gf10": float(np.interp(10, HW, gf)),
            "tok": tok.tolist(), "gf": gf, "cross": cross(gf), "cross_lo": cross(lo), "cross_hi": cross(hi),
            "lobby800": float(lob), "gf_noapp": na, "gf_app": ap, "cross_noapp": cross(na), "cross_noapp_lo": cross(na_lo),
            "cross_noapp_hi": cross(na_hi), "cross_app": cross(ap), "gf10_noapp": float(np.interp(10, HW, na)), "M": float(M), "rho": float(rho), "rejected": False}

if __name__ == "__main__":
    n = int(sys.argv[1]) if len(sys.argv) > 1 else 300
    rng = np.random.default_rng(42)
    draws = [(k, {p: float(rng.uniform(*b)) for p, b in PRIORS.items()}) for k in range(n)]
    with Pool(4) as pool:
        out = pool.map(one, draws, chunksize=4)
    json.dump({"HW": HW.tolist(), "priors": PRIORS, "draws": out}, open("psa.json", "w"))
    print("done", n)
