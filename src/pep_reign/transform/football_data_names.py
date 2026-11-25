"""Map Football-Data.co.uk team names to the canonical names used across the project.

Football-Data uses short names ("Man City", "Wolves"). Unknown names raise an error
rather than being guessed, so a new spelling cannot silently drop matches.
"""

FOOTBALL_DATA_TO_CANONICAL: dict[str, str] = {
    "Arsenal": "Arsenal",
    "Aston Villa": "Aston Villa",
    "Bournemouth": "AFC Bournemouth",
    "Brentford": "Brentford",
    "Brighton": "Brighton & Hove Albion",
    "Burnley": "Burnley",
    "Cardiff": "Cardiff City",
    "Chelsea": "Chelsea",
    "Crystal Palace": "Crystal Palace",
    "Everton": "Everton",
    "Fulham": "Fulham",
    "Huddersfield": "Huddersfield Town",
    "Hull": "Hull City",
    "Ipswich": "Ipswich Town",
    "Leeds": "Leeds United",
    "Leicester": "Leicester City",
    "Liverpool": "Liverpool",
    "Luton": "Luton Town",
    "Man City": "Manchester City",
    "Man United": "Manchester United",
    "Middlesbrough": "Middlesbrough",
    "Newcastle": "Newcastle United",
    "Nott'm Forest": "Nottingham Forest",
    "Norwich": "Norwich City",
    "Sheffield United": "Sheffield United",
    "Southampton": "Southampton",
    "Stoke": "Stoke City",
    "Sunderland": "Sunderland",
    "Swansea": "Swansea City",
    "Tottenham": "Tottenham Hotspur",
    "Watford": "Watford",
    "West Brom": "West Bromwich Albion",
    "West Ham": "West Ham United",
    "Wolves": "Wolverhampton Wanderers",
}


def to_canonical(name: str) -> str:
    """Return the canonical club name, or raise KeyError for an unmapped name."""
    try:
        return FOOTBALL_DATA_TO_CANONICAL[name.strip()]
    except KeyError as missing:
        raise KeyError(
            f"unmapped Football-Data team name {name!r}; add it to FOOTBALL_DATA_TO_CANONICAL"
        ) from missing
