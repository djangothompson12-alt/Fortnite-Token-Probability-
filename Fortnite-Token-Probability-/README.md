# Loot or Love?

Are we more likely to find the Fortnite Pirate Shop Token or a girlfriend? I'm 19 and have neither, so I wrote a paper about it. [Here it is](loot-or-love.pdf).

## Short version

- The token is 1 in 137,500 per chest. By my maths, a cold DM is about 1 in 3,500 and meeting someone new is about 1 in 33,600. So love wins per try. We just open a lot more chests than we send DMs.
- The median solo player needs about 3,240 hours to find the token, which is 135 days with no sleep.
- If anyone in your squad finds it, you all get it, so squads are 2.6x faster (about 1,250 hours). Turns out you do need friends. A lot of you don't have any, so you're cooked.
- After about 800 games, around half your Fortnite time is lobby and loading screens.
- The best time to die is 5 min 49 s. There's a proof in the paper with a Lambert W function in it, which is the most effort I've put into anything this year.
- If you're actually looking, a girlfriend is more likely by 5 Dec as long as you play under about 23 hours a week. Past that the token wins, mostly because we stop going outside.
- An average guy who actually tries has about an 8.5% chance by Christmas. Going all out gets you to about 16%, and if you're top 10% for looks and personality it's about 46%. Half of single guys aren't trying at all, which is why the average looks so grim.
- Dating apps push the line out to about 49 hours. A swipe is roughly 1 in 47,000, which is only about 3x better than a chest.

## Run it yourself

```bash
pip install -r requirements.txt
python run_all.py      # token results + all-men figures
python noapp.py        # main paper results: guys who are looking, no apps, personal odds
python extras.py       # optimal-death proof check + error bars
python lobby_dms.py    # DM from every lobby: how to chase both
python psa.py 400      # 400 random versions of the model (~8 min)
python psa_report.py   # uncertainty + which assumptions matter
```

Every number is in `lootorlove/params.py`. [S] means it came from a real source and [A] means I guessed it (and then tested how much the guess matters).

## Disclaimer

The maths is real. The advice is not. Touch grass.

*Built with help from AI tools for the code and typesetting. The idea, model choices and jokes are mine.*
