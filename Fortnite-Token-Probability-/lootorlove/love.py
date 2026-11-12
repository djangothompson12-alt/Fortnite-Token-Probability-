"""The girlfriend equation: offline, dating apps and social media DMs."""
import numpy as np
from scipy.optimize import brentq
from . import params as P

# ---------- offline Drake chain ----------
def drake_per_person():
    return (P.PI_FEMALE * P.PI_AGE * P.PI_SINGLE * P.PI_LOOKING *
            P.PI_ATTRACT * P.PI_COMPAT * P.PI_ASK * P.PI_YES)

def encounters_per_day(game_h_per_day):
    social = np.maximum(0.0, P.S0 - P.DISPLACE * (game_h_per_day - P.G0))
    return P.E_CONTEXT + P.BETA * social

def offline_rate(game_h_per_day):
    """Naive single-encounter Drake hazard, per year (average man)."""
    return 365 * encounters_per_day(game_h_per_day) * drake_per_person()

# ---------- looks ----------
def looks_multiplier(u, rng_range):
    """u in [0,1] is looks percentile. Exponential in u, top/bottom = rng_range, mean 1."""
    k = np.log(rng_range)
    return np.exp(k * u) * k / (np.exp(k) - 1)

# ---------- location ----------
def app_pool(place):
    dens, r = P.PLACES[place]
    return dens * np.pi * r**2 * P.WOMEN_18_29 * P.PI_SINGLE * P.ON_APP_NOW

def swipes_per_day(place):
    return min(P.SWIPES_PER_DAY, app_pool(place) / P.POOL_REFRESH_DAYS)

# ---------- channel rates per year, before looks ----------
def app_rate(place, p_rel):
    return 365 * swipes_per_day(place) * P.APP_MATCH * P.P_CONVO * P.P_DATE * p_rel

def dm_rate(p_rel):
    return 52 * P.DMS_PER_WEEK * P.P_DM_REPLY * P.P_CONVO * P.P_DATE * p_rel

class Population:
    def __init__(self, n=200_000, seed=1, place="Suburb"):
        rng = np.random.default_rng(seed)
        self.u = rng.uniform(0, 1, n)
        self.res = np.exp(rng.normal(0, P.RESIDUAL_SD, n) - P.RESIDUAL_SD**2 / 2)
        self.on_app = rng.uniform(0, 1, n) < P.APP_USE
        self.looking = rng.uniform(0, 1, n) < getattr(P, "MEN_LOOKING", 1.0)
        self.effort = np.where(self.looking, 1.0, getattr(P, "PASSIVE_FACTOR", 1.0))
        self.place = place
        self.rng = rng

    def rates(self, game_h_per_week, M, p_rel, place=None, lobby_swipe_h=0.0):
        place = place or self.place
        g = game_h_per_week / 7
        off = M * offline_rate(g) * looks_multiplier(self.u, P.OFFLINE_LOOKS_RANGE)
        lm = looks_multiplier(self.u, P.LOOKS_RANGE)
        app = self.on_app * app_rate(place, p_rel) * lm
        # optional: swiping while in Fortnite lobbies (extra swipes, same pool cap)
        if lobby_swipe_h > 0:
            extra = min(lobby_swipe_h * 60 * 4, max(0, app_pool(place) / P.POOL_REFRESH_DAYS - swipes_per_day(place)))
            app = app + self.on_app * 365 * extra * P.APP_MATCH * P.P_CONVO * P.P_DATE * p_rel * lm
        dm = dm_rate(p_rel) * (lm if P.DM_LOOKS else 1)
        return off * self.res * self.effort, (app + dm) * self.res * self.effort

def calibrate(target_single=P.SINGLE_MEN, n=200_000, seed=1):
    """Two targets, two unknowns: overall single share (Pew/GSS) and online share of new couples (HCMST)."""
    pop = Population(n, seed)
    def solve(p_rel):
        def gap(M):
            off, onl = pop.rates(P.G0 * 7, M, p_rel)
            return np.mean(P.MU_BREAKUP / (off + onl + P.MU_BREAKUP)) - target_single
        if gap(1e-6) < 0:   # online alone already too effective
            return 0.0, 1.0
        M = brentq(gap, 1e-6, 1e4)
        off, onl = pop.rates(P.G0 * 7, M, p_rel)
        return M, onl.sum() / (off.sum() + onl.sum())
    p_rel = brentq(lambda pr: solve(pr)[1] - P.ONLINE_SHARE, 1e-6, 1.0)
    M, share = solve(p_rel)
    return M, p_rel

def simulate(game_h_per_week, M, p_rel, n=100_000, seed=2, place="Suburb", lobby_swipe_h=0.0, return_pop=False):
    pop = Population(n, seed, place)
    off, onl = pop.rates(game_h_per_week, M, p_rel, place, lobby_swipe_h)
    t = pop.rng.exponential(1 / (off + onl))
    return (t, pop) if return_pop else t


def personal_rate(game_h_per_week, M, p_rel, looks_pct, personality_pct, effort=1.0, apps=False, place="Suburb"):
    """Yearly rate for one specific guy: looks and personality as percentiles (0-1), effort multiplier."""
    from scipy.stats import norm
    g = game_h_per_week / 7
    r = np.exp(P.RESIDUAL_SD * norm.ppf(np.clip(personality_pct, 1e-3, 1 - 1e-3)) - P.RESIDUAL_SD**2 / 2)
    off = M * offline_rate(g) * looks_multiplier(looks_pct, P.OFFLINE_LOOKS_RANGE)
    onl = looks_multiplier(looks_pct, P.LOOKS_RANGE) * ((app_rate(place, p_rel) if apps else 0.0) + dm_rate(p_rel))
    return r * effort * (off + onl)
