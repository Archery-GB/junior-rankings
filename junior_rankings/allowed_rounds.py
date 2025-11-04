from archeryutils import load_rounds
from archerydjango.fields import DbGender, DbAges, DbBowstyles


allowed_families = [
    "wa720",
    "metric720",
    "wa1440",
    "metric1440",
    "wa900",
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


def get_allowed_rounds(family, gender, age_group, bowstyle):
    if family not in allowed_families:
        return []
    if family in ["stgeorge_albion_windsor", "york_hereford_bristol"]:
        imperial_required_distances = {
            (DbGender.MALE, DbAges.AGE_UNDER_12): 30,
            (DbGender.MALE, DbAges.AGE_UNDER_14): 40,
            (DbGender.MALE, DbAges.AGE_UNDER_15): 50,
            (DbGender.MALE, DbAges.AGE_UNDER_16): 60,
            (DbGender.MALE, DbAges.AGE_UNDER_18): 80,
            (DbGender.MALE, DbAges.AGE_UNDER_21): 100,
            (DbGender.FEMALE, DbAges.AGE_UNDER_12): 30,
            (DbGender.FEMALE, DbAges.AGE_UNDER_14): 40,
            (DbGender.FEMALE, DbAges.AGE_UNDER_15): 50,
            (DbGender.FEMALE, DbAges.AGE_UNDER_16): 50,
            (DbGender.FEMALE, DbAges.AGE_UNDER_18): 60,
            (DbGender.FEMALE, DbAges.AGE_UNDER_21): 80,
        }
        rounds = []
        for r in all_available_rounds.values():
            if r.family != family:
                continue
            if r.max_distance().value >= imperial_required_distances[(gender, age_group)]:
                rounds.append(r)
    if family == "metric1440":
        wa_1440_required_distances = {
            (DbGender.MALE, DbAges.AGE_UNDER_12): 30,
            (DbGender.MALE, DbAges.AGE_UNDER_14): 40,
            (DbGender.MALE, DbAges.AGE_UNDER_15): 50,
            (DbGender.MALE, DbAges.AGE_UNDER_16): 60,
            (DbGender.MALE, DbAges.AGE_UNDER_18): 70,
            (DbGender.MALE, DbAges.AGE_UNDER_21): 90,
            (DbGender.FEMALE, DbAges.AGE_UNDER_12): 30,
            (DbGender.FEMALE, DbAges.AGE_UNDER_14): 40,
            (DbGender.FEMALE, DbAges.AGE_UNDER_15): 50,
            (DbGender.FEMALE, DbAges.AGE_UNDER_16): 50,
            (DbGender.FEMALE, DbAges.AGE_UNDER_18): 60,
            (DbGender.FEMALE, DbAges.AGE_UNDER_21): 70,
        }
        rounds = []
        for r in all_available_rounds.values():
            if r.family not in ["wa1440", "metric1440"]:
                continue
            if r.max_distance().value >= wa_1440_required_distances[(gender, age_group)]:
                rounds.append(r)
    if family == "agb900":
        agb_900_required_distances = {
            DbAges.AGE_UNDER_12: 30,
            DbAges.AGE_UNDER_14: 40,
            DbAges.AGE_UNDER_15: 50,
            DbAges.AGE_UNDER_16: 50,
            DbAges.AGE_UNDER_18: 60,
            DbAges.AGE_UNDER_21: 70,
        }
        rounds = []
        for r in all_available_rounds.values():
            if r.family != family:
                continue
            if r.max_distance().value >= agb_900_required_distances[age_group]:
                if r.codename == "agb900_60":
                    rounds.append(all_rounds["wa900"])
                else:
                    rounds.append(r)
    if family == "metric720":
        recurve_longbow_rounds = ["wa720_70", "wa720_60", "metric_122_50", "metric_122_40", "metric_122_30"]
        compound_rounds = ["wa720_50_c", "metric_80_40", "metric_80_30"]
        barebow_rounds = ["wa720_50_b", "metric_122_40", "metric_122_30"]
        recurve_longbow_distances = {
            DbAges.AGE_UNDER_12: 30,
            DbAges.AGE_UNDER_14: 40,
            DbAges.AGE_UNDER_15: 50,
            DbAges.AGE_UNDER_16: 50,
            DbAges.AGE_UNDER_18: 60,
            DbAges.AGE_UNDER_21: 70,
        }
        compound_barebow_distances = {
            DbAges.AGE_UNDER_12: 30,
            DbAges.AGE_UNDER_14: 40,
            DbAges.AGE_UNDER_15: 50,
            DbAges.AGE_UNDER_16: 50,
            DbAges.AGE_UNDER_18: 50,
            DbAges.AGE_UNDER_21: 50,
        }
        rounds = []
        for r in all_available_rounds.values():
            if r.family not in ["metric720", "wa720"]:
                continue
            if bowstyle in [DbBowstyles.RECURVE, DbBowstyles.LONGBOW] and r.codename not in recurve_longbow_rounds:
                continue
            if bowstyle == DbBowstyles.COMPOUND and r.codename not in compound_rounds:
                continue
            if bowstyle == DbBowstyles.BAREBOW and r.codename not in barebow_rounds:
                continue
            if bowstyle in [DbBowstyles.RECURVE, DbBowstyles.LONGBOW] and r.max_distance().value >= recurve_longbow_distances[age_group]:
                rounds.append(r)
            if bowstyle in [DbBowstyles.COMPOUND, DbBowstyles.BAREBOW] and r.max_distance().value >= compound_barebow_distances[age_group]:
                rounds.append(r)
    rounds.reverse()
    return rounds
