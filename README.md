[![make.fun · the-passport-page-of-a-countr-2-20261121-0318](https://make.fun/badge/the-passport-page-of-a-countr-2-20261121-0318.svg)](https://make.fun/bounty/the-passport-page-of-a-countr-2-20261121-0318?utm_source=github&utm_medium=readme&utm_campaign=the-passport-page-of-a-countr-2-20261121-0318)
[![rank](https://make.fun/badge/the-passport-page-of-a-countr-2-20261121-0318/RavenMonedula/passport-page-qamar/rank.svg)](https://make.fun/bounty/the-passport-page-of-a-countr-2-20261121-0318/leaderboard?utm_source=github&utm_medium=readme&utm_campaign=the-passport-page-of-a-countr-2-20261121-0318)
[![reward](https://make.fun/badge/the-passport-page-of-a-countr-2-20261121-0318/RavenMonedula/passport-page-qamar/reward.svg)](https://make.fun/bounty/the-passport-page-of-a-countr-2-20261121-0318?utm_source=github&utm_medium=readme&utm_campaign=the-passport-page-of-a-countr-2-20261121-0318)

# The Passport Page of a Country That Isn't There — Republic of Qamar

A program that draws a two-page passport spread for the **Republic of Qamar**, a desert oasis republic that isn't there: an identity page for caravan guide Layla Noor Amrani (passport QMR 002914) and a visas page with a high-desert transit endorsement, a Sarq visitor visa, and eight entry/exit stamps in chronological order. The telling detail is the well-house rule: *the border is the water.* Built for the [make.fun bounty "The Passport Page of a Country That Isn't There"](https://make.fun/bounty/the-passport-page-of-a-countr-2-20261121-0318).

## Run

```sh
python3 main.py
```

Writes `/output/entry.png` (1024x1024 PNG, deterministic, no network, PIL only). The MRZ check digits are computed at runtime with the ICAO 9303 algorithm.

Referral: https://make.fun/r/ba6wp5re
