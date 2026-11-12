"""Every number the model uses, with where it came from.

[S] = sourced (see paper references), [A] = assumption (see sensitivity analysis).
"""
from datetime import date

# ---------------- Token side ----------------
P_TOKEN = 1 / 137_500          # [S] per chest, Epic / Fortnite Status, 7 Nov 2026
TREASURE_BOOST = (1.5, 2.0)    # [S] Treasure Hours multiplier range
SEASON_END = date(2026, 12, 5) # [S] Treasure Hunters season end
TODAY = date(2026, 11, 9)
DAYS_LEFT = (SEASON_END - TODAY).days

C_MAX = 12.0     # [A] max chests a player opens in a long game
KAPPA = 6.0      # [A] looting time constant (min)
T0 = 14.0        # [A] mean survival (min) for a new account
T_FLOOR = 6.0    # [A] mean survival once SBMM has caught up (median player)
TAU = 150.0      # [A] SBMM catch-up scale (matches)
SKILL_SD = 0.35  # [A] log-sd of between-player skill (multiplies T_FLOOR)
OVERHEAD = 4.0   # [A] queue + lobby + bus (min)
SURV_SHAPE = 2.0 # [A] gamma shape for per-match survival (lots of early deaths)

MODE_SHARE = {"Solo": 1.00, "Duo": 0.85, "Trio": 0.75, "Squad": 0.65}  # [A] share of chests you open yourself
GROUP_SIZE = {"Solo": 1, "Duo": 2, "Trio": 3, "Squad": 4}  # [S] token is shared with the whole group
# region: (survival multiplier from bot density, extra queue minutes)       [A]
REGIONS = {"NA-East": (1.00, 0.0), "NA-West": (1.00, 0.0), "Europe": (0.95, 0.0),
           "Brazil": (0.90, 0.5), "Asia": (1.15, 1.0), "Oceania": (1.10, 1.5),
           "Middle East": (1.10, 2.0)}

# ---------------- Girlfriend side ----------------
# Offline "Drake" chain, per new person met
E_CONTEXT = 0.6    # [A] new people/day met through school/work regardless of free time
S0 = 0.51          # [S] ATUS 2025, ages 20-24: socializing & communicating, h/day
G0 = 1.08          # [S] ATUS 2025, ages 20-24: games & leisure computer use, h/day
BETA = 0.8         # [A] new people met per hour of socializing
DISPLACE = 0.20    # [A] hours of socializing lost per extra hour of gaming
PI_FEMALE = 0.50   # [A]
PI_AGE = 0.40      # [A] within a plausible age range
PI_SINGLE = 0.34   # [S] Pew 2023: share of women 18-29 who are single
PI_LOOKING = 0.35  # [S] Pew 2023: 35% of single women are looking
PI_ATTRACT = 0.05  # [S] Backus 2010: 1 in 20 find him attractive
PI_COMPAT = 0.10   # [S] Backus 2010: gets along with 1 in 10
PI_ASK = 0.50      # [A] he actually asks
PI_YES = 0.50      # [A] she says yes, conditional on everything above

ONLINE_SHARE = 0.39  # [S] HCMST 2017: share of het. couples who met online
FRIENDS_SHARE = 0.20 # [S] HCMST 2017: met through friends

SINGLE_MEN = 0.63    # [S] Pew 2023, men 18-29 (top-down calibration target)
SINGLE_MEN_GSS = 0.53# [A] lower value consistent with Wolfinger (2023) GSS reanalysis
MU_BREAKUP = 0.35    # [A] annual dissolution rate, young non-marital couples
ATTRACT_SD = 0.8     # [A] log-sd of between-man heterogeneity in success rate

# ---------------- v3: online channels, looks, location ----------------
APP_USE = 0.53        # [S] Pew 2023: share of under-30s who have ever used a dating app
APP_MATCH = 0.006     # [S] Tyson et al. 2016: share of men's right-swipes that match
LOOKS_RANGE = 11.0    # [S] OkCupid 2009: top-rated men get ~11x the messages of the lowest-rated
OFFLINE_LOOKS_RANGE = 4.0  # [A] looks matter less in person
SWIPES_PER_DAY = 40   # [A] for an active app user
P_CONVO = 0.30        # [A] a match turns into a real conversation
P_DATE = 0.15         # [A] a conversation turns into a date
# P_REL (relationship | date) is calibrated so apps supply 39% of new couples (HCMST)
DMS_PER_WEEK = 3      # [A] cold social-media DMs to people he doesn't know well
P_DM_REPLY = 0.08     # [A] reply rate on a cold DM (similar order to app matching)
DM_LOOKS = True       # looks multiplier applies to DMs too
RESIDUAL_SD = 0.5     # [A] log-sd of everything else (personality, confidence, luck)

# Location: eligible profiles within swiping distance
WOMEN_18_29 = 0.08    # [A] share of the population (approx. US/UK age structure)
ON_APP_NOW = 0.30     # [A] share of single young women currently active on an app
POOL_REFRESH_DAYS = 30# [A] you can get through your local pool about once a month
PLACES = {            # density per km^2 [A, typical values], search radius km [A]
    "City": (5000, 10), "Suburb": (1000, 10), "Small town": (150, 15), "Rural": (20, 25)}

# ---------------- v3: Fortnite fatigue and lobby time ----------------
QUEUE_GROWTH = 1.5    # [A] extra queue minutes once SBMM puts you in thinner, higher-rated pools
SESSION_HOURS = 3.0   # [A] typical session length
FATIGUE_PER_MATCH = 0.01  # [S-derived] ~10% decline over a ~10-match session (Sapienza et al. 2018)
FATIGUE_IDLE = 0.15   # [A] extra idle minutes per match into a session (snacks, staring, tilt)

# ---------------- v6: who is actually trying ----------------
MEN_LOOKING = 0.50     # [S] Pew 2023: half of single men are looking for a relationship or dates
PASSIVE_FACTOR = 0.2   # [A] guys not looking still sometimes fall into one, at 20% of the casual rate
EFFORT = {"Not looking": PASSIVE_FACTOR, "Casually looking": 1.0, "Actively trying": 2.5, "Going all out": 5.0}  # [A]
CHRISTMAS_DAYS = 46    # 9 Nov -> 25 Dec 2026
