"""
Every player-facing string lives here so Tweety's voice stays consistent
in one place. All lines are original — written in the spirit of the
character, not quoted from any scripted source.
"""

LANDING_INSTRUCTIONS = [
    "Alright. Listen close, I'm only saying this once.",
    "Twenty turns. That's it. That's all the patience I've got.",
    "Yes or no. Full sentences bore me.",
    "Want to guess instead of asking? Go for it — but it costs you a turn, same as everything else.",
    "Guess right, you win. Guess wrong, you just burned a turn. Try again if you've got any left.",
    "Ask me something that's not yes or no? Doesn't count. Try again.",
    "Ask me something I genuinely don't know? Also doesn't count. I'm good, not psychic.",
    "Try to sweet-talk the answer out of me? Cute. Won't work — and don't waste a turn on it.",
    "Run out of turns with no right guess? I win. Don't @ me.",
    "Got all that? Good. Let's go.",
]

PATH_A_BUTTON = "I'll pick someone for a friend"
PATH_B_BUTTON = "Let Tweety pick"

PATH_A_PROMPT = "Type a name Tweety should look up."
PATH_A_SUBMIT = "Check"

FAME_CHECK_REJECTION = "Never heard of 'em. Pick someone real."
FAME_CHECK_LOADING = "Hold your horses."

DOSSIER_LOADING = "Doing my homework. Don't rush genius."
LIVE_SEARCH_LOADING = "Hold on, checking my sources."

DISAMBIGUATION_PROMPT = "More than one of those running around. Which one?"

HANDOFF_TITLE = "Tweety's ready. Pass the device to whoever's guessing — don't let them see this screen."
HANDOFF_BUTTON = "Start the grilling"

PATH_B_FRAMING = "So Tweety picks someone you'd actually recognize."
PATH_B_AGE_LABEL = "Age range"
PATH_B_REGION_LABEL = "Region"
PATH_B_SUBMIT = "Let Tweety pick"
PATH_B_THINKING = "Give me a second. Rifling through the rolodex."
POOL_EXHAUSTED_ERROR = "Struck out on that combo twice. Try a different age or region, chief."

GAME_TITLE = "TWEETY'S 20 QUESTIONS"
INPUT_PLACEHOLDER = "Ask Tweety something..."
ASK_BUTTON = "Ask"
GUESS_BUTTON = "Guess"
HINT_BUTTON = "Hint"
HINT_BUTTON_USED = "Hint used"
GIVE_UP_BUTTON = "Give Up"

RESULT_LABELS = {
    "YES": "YES",
    "NO": "NO",
    "DONT_KNOW": "DON'T KNOW",
    "ASK_AGAIN": "NOT YES/NO",
    "OFF_LIMITS": "NICE TRY",
    "GUESS_WRONG": "WRONG",
    "GUESS_RIGHT": "CORRECT",
}

HINT_TAG = "HINT"


def guess_confirm_text(guess_text: str) -> str:
    return f"Locking in '{guess_text}' as your guess — sure? That'll cost you a turn."


GIVE_UP_CONFIRM = "Give up? Tweety wins by default. Sure?"
CONFIRM_YES = "Yes"
CONFIRM_CANCEL = "Cancel"

ERROR_GENERIC = "Something's fritzing on my end. Give it another shot."


def win_text(name: str, turns_used: int, fact: str) -> str:
    return (
        f"Of course it was them. Took you long enough.\n\n"
        f"**{name}** — solved in {turns_used} turn{'s' if turns_used != 1 else ''}.\n\n"
        f"Oh, and: {fact}"
    )


def loss_turns_text(name: str, fact: str) -> str:
    return (
        f"Time's up. I win — obviously.\n\n"
        f"It was **{name}**. {fact}"
    )


def loss_giveup_text(name: str, fact: str) -> str:
    return (
        f"Giving up already? Typical.\n\n"
        f"It was **{name}**. {fact}"
    )


REPLAY_BUTTON = "One more round?"

PATH_A_ACK_GOOD = "Huh. Not bad. Good pick."
PATH_A_ACK_EASY = "That one? Too easy. Come on."
