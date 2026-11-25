"""Canonical club names.

openfootball writes names like "Manchester City FC" in some seasons and
"Manchester City" in others. Each external source needs its own mapping, so
this module only removes the cosmetic differences. Add a source-specific
alias table here when you join a new source.
"""

import re

_FC_SUFFIX = re.compile(r"\s+FC$")


def canonical(name: str) -> str:
    """Return the club name without padding or a trailing ' FC'."""
    cleaned = re.sub(r"\s+", " ", name).strip()
    return _FC_SUFFIX.sub("", cleaned)
