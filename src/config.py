"""Central configuration and constants for Tweety's Twenty Questions."""

TURN_BUDGET = 20
HINT_UNLOCK_AT_TURNS_USED = 15  # Hint becomes available once this many turns have been used
FAME_BYTE_THRESHOLD = 50_000

# Model tiers.
# Research tier: Sonnet 5 + web_search, free-text output, grounded-only prompting.
# Structuring tier: Haiku 4.5, JSON-schema structured output, no tools.
RESEARCH_MODEL = "claude-sonnet-5"
LIGHT_MODEL = "claude-haiku-4-5"

WIKI_USER_AGENT = "Tweety20Questions/0.1 (contact: tanvee.rao@gmail.com)"
WIKI_REST_SUMMARY_URL = "https://en.wikipedia.org/api/rest_v1/page/summary/{title}"
WIKI_ACTION_API_URL = "https://en.wikipedia.org/w/api.php"

MAX_DISAMBIGUATION_CANDIDATES = 5
MAX_DISAMBIGUATION_LINKS_TO_CHECK = 15

CANDIDATE_POOL_SIZE = 10
MAX_POOL_REGENERATIONS = 1  # one fresh pool retry if the first pool fully exhausts

AGE_RANGES = [
    "Under 13", "13–17", "18–24", "25–34", "35–44",
    "45–54", "55–64", "65+",
]

REGIONS = [
    "North America", "UK & Ireland", "Continental Europe",
    "Latin America & Caribbean", "East Asia", "South Asia",
    "Southeast Asia", "Middle East & North Africa",
    "Sub-Saharan Africa", "Oceania", "Not sure / global mix",
]
