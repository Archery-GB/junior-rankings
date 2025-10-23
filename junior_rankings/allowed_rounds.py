from archeryutils import load_rounds


allowed_families = [
    "metric720",
    "metric1440",
    "agb900",
    "york_hereford_bristol",
    "stgeorge_albion_windsor",
]


all_rounds = (
    load_rounds.WA_outdoor
    | load_rounds.AGB_outdoor_metric
    | load_rounds.AGB_outdoor_imperial
)

all_available_rounds = {k: r for (k, r) in all_rounds.items() if r.family in allowed_families}
