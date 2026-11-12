"""How many Pirate Shop tokens get found per day, worldwide?

Inputs:
  daily in-match peak players, 4-8 Nov 2026 (Endgame Tools, from Epic's Fortnite data API;
  FortCharts shows the same numbers)                                              [S]
  average/peak ratio for concurrent players                                        [A]
  share of in-match players who are in Battle Royale (FortCharts snapshot ~0.78)  [A]
  chests per in-match hour, from this model (squad 39 to solo 60)                  [model]
Writes finds_per_day.json.
"""
import json
import numpy as np

P_TOKEN = 1 / 137_500
P_GOLD = 1 / 1_562_500
PEAKS = [3_021_732, 2_971_977, 3_727_417, 6_053_079, 4_726_676]  # 4-8 Nov, in-match daily peaks

rng = np.random.default_rng(2026)
n = 200_000
peak = np.mean(PEAKS)
avg_ratio = rng.uniform(0.4, 0.7, n)
br_share = rng.uniform(0.6, 0.9, n)
chests_per_h = rng.uniform(39, 60, n)

chests_day = peak * avg_ratio * br_share * 24 * chests_per_h
finds = chests_day * P_TOKEN
gold = chests_day * P_GOLD
q = lambda x: [float(np.percentile(x, k)) for k in (5, 50, 95)]
out = {
    "mean_daily_peak_in_match": float(peak),
    "chests_per_day_5_50_95": q(chests_day),
    "token_finds_per_day_5_50_95": q(finds),
    "token_finds_season_33d_median": float(np.median(finds) * 33),
    "gold_outfit_per_day_5_50_95": q(gold),
    "player_hours_per_find_median": float(np.median(peak * avg_ratio * br_share * 24 / finds)),
}
json.dump(out, open("finds_per_day.json", "w"), indent=2)
print(json.dumps(out, indent=2))
