"""Height (dating side) and Fortnite skill (token side).   python height_skill.py

Height: NHANES Aug 2021-Aug 2023, men 20-29: mean 176.3 cm, 5th 162.0, 95th 188.1 [S]
        -> SD ~ 7.9 cm (from the 5th-95th spread).
        Hitsch, Hortacsu & Ariely (2006): men 6'3"-6'4" get 65% more first-contact
        e-mails than men 5'7"-5'8" [S] -> log-slope 0.0247 per cm.
        Hensley (1994): the advantage levels off above about 6 ft [S] -> flat above 188 cm [A].
Skill:  mean survival = T_FLOOR * exp(SKILL_SD * z); chests per hour of play from the
        model's loot curve with the long-run lobby time.
"""
import json, math
import numpy as np
from scipy.stats import norm
from lootorlove import params as P

H_MEAN, H_SD = 176.3, (188.1 - 162.0) / (2 * 1.645)
BETA = math.log(1.65) / ((6*12 + 3.5 - (5*12 + 7.5)) * 2.54)
CAP = 188.0
def height_mult(cm, beta=BETA):
    return math.exp(beta * (min(cm, CAP) - H_MEAN))

# calibrated hazards that reproduce the paper's headline numbers
LAM_ACTIVE = -math.log(1 - 0.085) / 46          # actively trying, average guy, 10 h/wk, by Christmas
LAM0 = 1.169e-3; K = 0.01823                    # casual, 0 h/wk; per-hour displacement (calculator)
RATE_SOLO = 30.3
def love_p(h, days, m): return 1 - math.exp(-LAM0 * math.exp(-K * h) * m * days)
def tok_p(h, days, rate=RATE_SOLO): return 1 - math.exp(-rate * h * days / 7 * P.P_TOKEN)
def crossover(m):
    for x in np.arange(0, 200.5, 0.5):
        if tok_p(x, 30) > love_p(x, 30, m): return float(x)
    return None

heights = [("5'5\"", 165.1), ("5'7\"", 170.2), ("5'9\"", 175.3), ("5'11\"", 180.3), ("6'1\"", 185.4), ("6'3\"", 190.5)]
H = []
for lab, cm in heights:
    m = height_mult(cm); m_lo = height_mult(cm, BETA / 2)
    H.append({"height": lab, "cm": cm, "pct": round(100 * norm.cdf((cm - H_MEAN) / H_SD)),
              "mult": round(m, 2), "p_xmas_active": 1 - math.exp(-LAM_ACTIVE * m * 46),
              "p_xmas_active_halfbeta": 1 - math.exp(-LAM_ACTIVE * m_lo * 46),
              "crossover_hpw": crossover(m)})

O = P.OVERHEAD + P.QUEUE_GROWTH          # long-run lobby time
def chests_per_hour(mean_T):
    th = mean_T / P.SURV_SHAPE
    frac = 1 - (1 + th / P.KAPPA) ** (-P.SURV_SHAPE)   # E[1 - exp(-T/kappa)], T ~ Gamma
    return 60 * P.C_MAX * frac / (mean_T + O)
S = []
for lab, z in [("Dies off spawn (mean 2 min)", None), ("Bottom 10%", -1.2816), ("Bottom 25%", -0.6745),
               ("Median", 0.0), ("Top 25%", 0.6745), ("Top 10%", 1.2816), ("Top 1%", 2.326)]:
    T = 2.0 if z is None else P.T_FLOOR * math.exp(P.SKILL_SD * z)
    r = chests_per_hour(T)
    S.append({"skill": lab, "mean_survival_min": round(T, 1), "chests_per_hour": round(r, 1),
              "median_hours_solo": round(math.log(2) / (r * P.P_TOKEN))})
best = max(np.arange(1, 30, 0.01), key=chests_per_hour)
out = {"height_mean_cm": H_MEAN, "height_sd_cm": round(H_SD, 2), "beta_per_cm": BETA,
       "height": H, "skill": S, "best_mean_survival_min": round(float(best), 2)}
json.dump(out, open("height_skill.json", "w"), indent=2)
print(json.dumps(out, indent=1))
