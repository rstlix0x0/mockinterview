"""Interview loop templates and the seeded draw."""
import random

from .packs import LEVELS

TEMPLATES = {
    "junior": ["live-coding", "live-coding"],
    "mid": ["live-coding", "live-coding", "system-design"],
    "senior": ["live-coding", "live-coding", "system-design"],
    "staff": ["system-design", "system-design", "live-coding"],
}
RECENT_SESSIONS = 6


def adjacent_levels(level):
    i = LEVELS.index(level)
    return [LEVELS[j] for j in (i - 1, i + 1) if 0 <= j < len(LEVELS)]


def tag_deficits(history):
    """{tag: mean (100 - score) / 100} over past scored rounds."""
    acc = {}
    for entry in history:
        if entry.get("state") != "scored":
            continue
        for r in entry.get("rounds", []):
            if "score" not in r:
                continue
            for tag in r.get("tags", []):
                acc.setdefault(tag, []).append(max(0.0, 100.0 - r.get("score", 0.0)) / 100.0)
    return {t: sum(v) / len(v) for t, v in acc.items()}


def recent_ids(history):
    ids = set()
    for entry in history[-RECENT_SESSIONS:]:
        for r in entry.get("rounds", []):
            ids.add(r.get("problem"))
    return ids


def _weight(pack, deficits):
    ds = [deficits[t] for t in pack.tags if t in deficits]
    return 1.0 + (sum(ds) / len(ds) if ds else 0.0)


def build_loop(index, level, history, seed, forced_type=None, eligible=None):
    """Return (list of Pack, warnings). `eligible(pack)` filters (structure, trust)."""
    rnd = random.Random(seed)
    template = TEMPLATES[level]
    if forced_type:
        template = [forced_type] * len(template)
    deficits = tag_deficits(history)
    recent = recent_ids(history)
    chosen, warnings = [], []
    for ptype in template:
        used = {p.id for p in chosen}
        steps = [
            ("", [level], False),
            ("recently used problems were allowed because the pool was empty", [level], True),
            ("adjacent levels were allowed because the pool was empty", [level] + adjacent_levels(level), True),
        ]
        pick = None
        for message, levels, allow_recent in steps:
            pool = [p for p in index.packs.values()
                    if p.type == ptype and p.id not in used
                    and any(lv in levels for lv in p.levels)
                    and (allow_recent or p.id not in recent)
                    and (eligible is None or eligible(p))]
            if pool:
                pool.sort(key=lambda p: p.id)  # stable order for a reproducible draw
                pick = rnd.choices(pool, weights=[_weight(p, deficits) for p in pool])[0]
                if message:
                    warnings.append("%s round: %s" % (ptype, message))
                break
        if pick is None:
            warnings.append("no %s problem is available for level %s; round skipped" % (ptype, level))
            continue
        chosen.append(pick)
    return chosen, warnings
