"""'How to chase both': send one DM per lobby and leave at T* = 5:49. Numbers for Section 3.8."""
import json
import numpy as np
from lootorlove import params as P, token, love

rng = np.random.default_rng(1)
n = np.arange(300, 1300)                       # an established player
floor = np.minimum(P.T_FLOOR * np.exp(rng.normal(0, P.SKILL_SD, 4000)), P.T0)
c, m, T = token._match_block(rng, n, floor, 1.0, 1.0, 0.0, True)
mph, cph = 60 / m.mean(), c.sum() / m.sum() * 60
over = token.match_overhead(n).mean()
mph_opt = 60 / (5.82 + over)
cph_opt = P.C_MAX * (1 - np.exp(-5.82 / P.KAPPA)) * mph_opt

d = json.load(open("results_noapp.json")); M, rho = d["M"], d["rho"]
H = 10
for label, dms, cp in [("normal", 3, cph), ("DM every lobby", H * mph, cph), ("DM every lobby + leave at 5:49", H * mph_opt, cph_opt)]:
    P.DMS_PER_WEEK = dms
    lam = love.personal_rate(H, M, rho, 0.5, 0.5, 1.0)       # average guy, casually looking, no apps
    gf = 1 - np.exp(-lam * P.CHRISTMAS_DAYS / 365)
    tok = 1 - np.exp(-cp * H * P.DAYS_LEFT / 7 * P.P_TOKEN)
    print(f"{label:32s} DMs/wk {dms:5.1f}  gf by Christmas {gf:.3f}  token by 5 Dec {tok:.4f} (squad {1-np.exp(-2.6*cp*H*P.DAYS_LEFT/7*P.P_TOKEN):.4f})")
