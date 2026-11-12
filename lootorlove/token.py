"""Per-player Monte Carlo of Pirate Shop Token hunting."""
import numpy as np
from . import params as P

def match_overhead(n):
    """Queue + loading + bus minutes. Queues get longer as SBMM moves you into thinner pools."""
    return P.OVERHEAD + P.QUEUE_GROWTH * (1 - np.exp(-n / P.TAU))

def _match_block(rng, n_idx, floor_i, share, surv_mult, extra_q, fatigue=True):
    mean = surv_mult * (floor_i[:, None] + (P.T0 - floor_i[:, None]) * np.exp(-n_idx[None, :] / P.TAU))
    over = match_overhead(n_idx)[None, :] + extra_q
    if fatigue:
        # position within the current session (sessions of SESSION_HOURS, approx. by expected match length)
        per_session = max(1, int(P.SESSION_HOURS * 60 / (mean.mean() + over.mean())))
        k = (n_idx % per_session)[None, :]
        mean = mean * (1 - P.FATIGUE_PER_MATCH) ** k     # survive less as you tire
        over = over + P.FATIGUE_IDLE * k                  # and drift between games
        loot_speed = (1 - P.FATIGUE_PER_MATCH) ** k       # and loot slower
    else:
        loot_speed = 1.0
    T = rng.gamma(P.SURV_SHAPE, mean / P.SURV_SHAPE)
    chests = rng.poisson(share * P.C_MAX * (1 - np.exp(-T * loot_speed / P.KAPPA)))
    minutes = T + over
    return chests, minutes, T

def time_to_token(n_players=4000, mode="Solo", region="NA-East", boost=1.0,
                  max_matches=150_000, block=2000, seed=3, fatigue=True):
    """Exact simulation: draw each player's chests-until-token (geometric), then play
    matches until they open that many. Returns hours (np.inf if censored)."""
    rng = np.random.default_rng(seed)
    share = P.MODE_SHARE[mode]; sm, q = P.REGIONS[region]
    need = rng.geometric(P.P_TOKEN * boost, n_players).astype(float)
    floor_i = P.T_FLOOR * np.exp(rng.normal(0, P.SKILL_SD, n_players))
    floor_i = np.minimum(floor_i, P.T0)
    cum_c = np.zeros(n_players); cum_h = np.zeros(n_players)
    out = np.full(n_players, np.inf); alive = np.ones(n_players, bool)
    for start in range(0, max_matches, block):
        idx = np.where(alive)[0]
        if idx.size == 0: break
        c, m, _ = _match_block(rng, np.arange(start, start + block), floor_i[idx], share, sm, q, fatigue)
        cc = cum_c[idx, None] + np.cumsum(c, 1); hh = cum_h[idx, None] + np.cumsum(m, 1) / 60
        hit = cc >= need[idx, None]; got = hit.any(1)
        first = hit.argmax(1)
        out[idx[got]] = hh[got, first[got]]
        alive[idx[got]] = False
        cum_c[idx] = cc[:, -1]; cum_h[idx] = hh[:, -1]
    return out

def season_probability(game_h_per_week, days=P.DAYS_LEFT, n_players=20000, mode="Solo",
                       seed=4, start_matches=300, fatigue=True, return_lobby=False):
    """P(find token before season end) for players who already have `start_matches`
    games of SBMM history. Uses exact per-player chest totals (Rao-Blackwellised)."""
    rng = np.random.default_rng(seed)
    budget = game_h_per_week * days / 7 * 60
    floor_i = np.minimum(P.T_FLOOR * np.exp(rng.normal(0, P.SKILL_SD, n_players)), P.T0)
    share = P.MODE_SHARE[mode]
    n_max = int(budget / (P.OVERHEAD + 1)) + 50
    c, m, T = _match_block(rng, np.arange(start_matches, start_matches + n_max), floor_i, share, 1.0, 0.0, fatigue)
    played = np.cumsum(m, 1) <= budget
    chests = (c * played).sum(1)
    p = np.mean(1 - np.exp(-P.P_TOKEN * chests))
    if return_lobby:
        lobby = 1 - (T * played).sum() / (m * played).sum()
        return p, chests, lobby
    return p, chests
