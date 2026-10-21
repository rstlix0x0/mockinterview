"""Rubrics, weights and score arithmetic."""
from .util import MiError

LC_DIMS = {"framing": 15, "approach": 15, "implementation": 25, "quality": 10,
           "testing": 15, "communication": 10, "adaptability": 10}
SD_DIMS = {"scoping": 15, "estimation": 10, "architecture": 25, "deep_dives": 30,
           "reliability": 10, "communication": 10}
DIMS = {"live-coding": LC_DIMS, "system-design": SD_DIMS}

READINGS = [
    (85, "Ready for senior rounds on this kind of problem."),
    (70, "Close. Repeat with a different problem of the same level."),
    (55, "Repeat in 3 days after reviewing the pattern or the matching building blocks."),
    (0, "Go back one level, or study the fundamentals first."),
]


def reading(total):
    for floor, text in READINGS:
        if total >= floor:
            return text
    return READINGS[-1][1]


def hint_penalty(ptype, hints):
    """Live coding: every rung used is deducted. System design: only the highest probe step is deducted."""
    costs = [h["cost"] for h in hints or []]
    if not costs:
        return 0
    return max(costs) if ptype == "system-design" else sum(costs)


def implementation_rating(last_run):
    """4 x the share of passing cases of the last run; 0 when nothing was run."""
    if not last_run or not last_run.get("total"):
        return 0.0
    return round(4.0 * last_run["passed"] / last_run["total"], 2)


def score_round(ptype, ratings, penalty, last_run, evidence=None):
    """Return the round scorecard entry. Raises MiError for unknown, missing or out-of-range ratings."""
    dims = DIMS[ptype]
    ratings = dict(ratings or {})
    if ptype == "live-coding":
        ratings.pop("implementation", None)
        ratings["implementation"] = implementation_rating(last_run)
    unknown = sorted(set(ratings) - set(dims))
    if unknown:
        raise MiError("unknown rating dimension(s) for %s: %s" % (ptype, ", ".join(unknown)), code="bad_ratings")
    missing = sorted(set(dims) - set(ratings))
    if missing:
        raise MiError("missing rating(s) for %s: %s" % (ptype, ", ".join(missing)), code="bad_ratings",
                      missing=missing)
    total = 0.0
    for name, weight in dims.items():
        value = ratings[name]
        if isinstance(value, bool) or not isinstance(value, (int, float)) or not 0 <= value <= 4:
            raise MiError("rating '%s' must be a number from 0 to 4" % name, code="bad_ratings")
        total += weight * value / 4.0
    score = round(max(total - penalty, 0.0), 1)
    return {"score": score, "ratings": ratings, "weights": dict(dims), "penalty": penalty,
            "evidence": dict(evidence or {})}
