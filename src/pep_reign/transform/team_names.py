"""Canonical club names.

openfootball writes names like "Manchester City FC", "Sunderland AFC" in some
seasons and "Manchester City" in others. Each external source needs its own mapping,
so this module only removes the cosmetic differences. Add a source-specific alias
table here when you join a new source.
"""

import re

# Only a trailing club-type suffix. "AFC Bournemouth" keeps its prefix.
_CLUB_SUFFIX = re.compile(r"\s+(FC|AFC)$")


def canonical(name: str) -> str:
    """Return the club name without padding or a trailing ' FC' / ' AFC'."""
    cleaned = re.sub(r"\s+", " ", name).strip()
    return _CLUB_SUFFIX.sub("", cleaned)
